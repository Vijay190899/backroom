"""Golden runs (PRD F7): real runs recorded as events plus JPEG frames, played back when
the API is unreachable or the demo is in replay mode.

    uv run python -m backroom_api.replay.golden record [--only reorder]

A golden run is a directory (CONTRACTS §5): `events.json` (the run's events, with
`run.started.recorded = true`), `frames.json` (`GoldenFrame` index) and `frames/*.jpg`, plus
`meta.json`. They live in `apps/web/public/golden/<name>/`, so the web app can play them
with no API at all, and the API serves the same files in replay mode.

Recording drives the real stack (portals, Chromium, model calls for the heal), so it needs
`pnpm dev:portals` and a model key. The skills on disk are snapshotted first and restored
afterwards, and the portals are reset: recording leaves the demo where it was.
"""

import argparse
import asyncio
import json
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backroom_api.agents.portals_admin import PortalAdmin
from backroom_api.agents.runner import RunResult, SkillRunner
from backroom_api.agents.tasks import TASKS
from backroom_api.browser import BrowserPool
from backroom_api.browser.screencast import Frame
from backroom_api.config import REPO_ROOT, Settings
from backroom_api.contracts.events import GoldenFrame, RunEvent
from backroom_api.llm.client import LLM
from backroom_api.skills.store import DEFAULT_ROOT as SKILLS_ROOT
from backroom_api.skills.store import SkillStore

GOLDEN_ROOT = REPO_ROOT / "apps" / "web" / "public" / "golden"
# Which recording plays for an approved task in replay mode.
GOLDEN_FOR_TASK = {
    "grainline.reorder_item": "reorder",
    "grainline.cancel_order": "cancel",
    "tilldesk.change_price": "price",
}
MIN_FRAME_GAP_MS = 350  # within one step, keep at most ~3 frames a second (size)


@dataclass(frozen=True)
class Scenario:
    name: str
    title: str
    task: str
    seed: int
    params: dict[str, Any]


# The demo's runs (DEMO_SCRIPT): the reorder replay, the same reorder healing after the
# seed-7 redesign, the price change, and the undo of an order.
SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        "reorder", "Reorder oat milk", "grainline.reorder_item", 0, {"sku": "OAT-1L", "qty": 28}
    ),
    Scenario(
        "reorder-heal",
        "Reorder after a redesign",
        "grainline.reorder_item",
        7,
        {"sku": "OAT-1L", "qty": 28},
    ),
    Scenario(
        "price",
        "Raise the Franzbrötchen price",
        "tilldesk.change_price",
        0,
        {"item_id": "franzbroetchen", "price_eur": 3.45},
    ),
    Scenario("cancel", "Cancel the order (undo)", "grainline.cancel_order", 0, {}),
)


class GoldenRecorder:
    """Collects one run's events and frames, then writes the golden directory."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.run_id = f"golden-{name}"
        self.events: list[RunEvent] = []
        self.frames: list[GoldenFrame] = []
        self.jpegs: list[bytes] = []
        self._t0 = time.monotonic()
        self._cursor: tuple[float, float] | None = None
        self._last_kept_ms = -10_000

    async def sink(self, event: RunEvent) -> None:
        self.events.append(event)

    async def on_cursor(self, x: float, y: float) -> None:
        self._cursor = (x, y)

    async def on_frame(self, frame: Frame) -> None:
        offset = int((time.monotonic() - self._t0) * 1000)
        after = self.events[-1].seq if self.events else 0
        same_step = bool(self.frames) and self.frames[-1].after_seq == after
        if same_step and offset - self._last_kept_ms < MIN_FRAME_GAP_MS:
            # Replace the step's last frame instead of adding one: the newest view wins.
            self.jpegs[-1] = frame.jpeg
            return
        self._last_kept_ms = offset
        self.jpegs.append(frame.jpeg)
        self.frames.append(
            GoldenFrame(
                file=f"{len(self.jpegs):04d}.jpg",
                after_seq=after,
                offset_ms=offset,
                width=frame.width,
                height=frame.height,
                cursor_x=self._cursor[0] if self._cursor else None,
                cursor_y=self._cursor[1] if self._cursor else None,
            )
        )

    def write(self, root: Path, scenario: Scenario, result: RunResult) -> Path:
        out = root / self.name
        if out.exists():
            shutil.rmtree(out)
        (out / "frames").mkdir(parents=True)
        events: list[dict[str, Any]] = []
        for event in self.events:
            body = event.model_dump(mode="json")
            body["run_id"] = self.run_id
            if body["type"] == "run.started":
                body["recorded"] = True  # the Replay badge: never presented as live
            if body["type"] == "run.finished":
                body["undo_available"] = False  # a recording cannot undo anything
            events.append(body)
        (out / "events.json").write_text(json.dumps(events, ensure_ascii=False), "utf-8")
        frames = [f.model_dump(mode="json") for f in self.frames]
        (out / "frames.json").write_text(json.dumps(frames), "utf-8")
        for frame, jpeg in zip(self.frames, self.jpegs, strict=True):
            (out / "frames" / frame.file).write_bytes(jpeg)
        meta = {
            "name": self.name,
            "title": scenario.title,
            "task": scenario.task,
            "chaos_seed": scenario.seed,
            "status": result.status,
            "summary": result.summary,
            "recorded_at": datetime.now(UTC).isoformat(),
            "git_sha": _git_sha(),
            "totals": result.totals.model_dump(),
            "frames": len(self.frames),
            "bytes": sum(len(j) for j in self.jpegs),
        }
        (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), "utf-8")
        return out


def _git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


async def record(only: str | None, root: Path) -> int:
    settings = Settings()
    store = SkillStore()
    missing = [t for t in TASKS if store.latest(t) is None]
    if missing:
        print(
            f"skills missing ({', '.join(missing)}): run `pnpm demo:reset` first", file=sys.stderr
        )
        return 2
    snapshot = Path(tempfile.mkdtemp(prefix="backroom-skills-"))
    shutil.copytree(SKILLS_ROOT, snapshot / "skills")
    admin = PortalAdmin(settings)
    pool = BrowserPool(max_contexts=1)
    runner = SkillRunner(settings, LLM(settings), pool, store, admin)
    last_order: str | None = None
    try:
        await admin.reset()
        for scenario in SCENARIOS:
            if (
                only
                and scenario.name != only
                and not (only == "cancel" and scenario.name == "reorder")
            ):
                continue
            params = dict(scenario.params)
            if scenario.task == "grainline.cancel_order":
                if last_order is None:
                    print(
                        "cancel needs an order: record `reorder` in the same session",
                        file=sys.stderr,
                    )
                    return 2
                params["order_id"] = last_order
            await admin.set_chaos(TASKS[scenario.task].portal, scenario.seed)
            rec = GoldenRecorder(scenario.name)
            result = await runner.run(
                scenario.task,
                params,
                run_id=rec.run_id,
                action_id="act_golden",
                sink=rec.sink,
                on_frame=rec.on_frame,
                on_cursor=rec.on_cursor,
            )
            if not result.ok:
                print(f"{scenario.name}: {result.status}: {result.summary}", file=sys.stderr)
                return 1
            if scenario.task == "grainline.reorder_item":
                last_order = result.result.get("order")
            out = rec.write(root, scenario, result)
            t = result.totals
            print(
                f"{scenario.name:<13} {result.status}, {len(rec.events)} events, "
                f"{len(rec.frames)} frames ({sum(map(len, rec.jpegs)) // 1024} KB), "
                f"{t.elapsed_ms / 1000:.1f} s, {t.llm_calls} calls, ${t.usd:.4f} "
                f"-> {out.relative_to(REPO_ROOT)}"
            )
    finally:
        await pool.close()
        # Recording changed skills (the heal made v2) and portal state: put both back.
        shutil.rmtree(SKILLS_ROOT)
        shutil.copytree(snapshot / "skills", SKILLS_ROOT)
        shutil.rmtree(snapshot, ignore_errors=True)
        await admin.reset()
        await admin.close()
    write_index(root)
    return 0


def write_index(root: Path) -> None:
    """`index.json`: the golden runs the web app can offer."""
    index = sorted(p.name for p in root.iterdir() if (p / "events.json").exists())
    (root / "index.json").write_text(json.dumps(index), "utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="backroom_api.replay.golden")
    sub = parser.add_subparsers(dest="cmd", required=True)
    rec = sub.add_parser("record", help="record the demo's golden runs on the live stack")
    rec.add_argument("--only", choices=[s.name for s in SCENARIOS])
    args = parser.parse_args(argv)
    return asyncio.run(record(args.only, GOLDEN_ROOT))


if __name__ == "__main__":
    sys.exit(main())
