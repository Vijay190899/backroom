"""Run a task from the terminal and watch the event stream.

    uv run python -m backroom_api.agents.cli run grainline.reorder_item [--seed 7] [--cold]
    uv run python -m backroom_api.agents.cli reset-skill grainline.reorder_item

Needs the portals service running (`pnpm dev:portals`), Chromium installed and, for any run
that explores or heals, an OpenRouter key. `--seed` sets the portal's chaos seed first.
"""

import argparse
import asyncio
import json
import sys
from typing import Any

from backroom_api.agents.portals_admin import PortalAdmin
from backroom_api.agents.runner import SkillRunner
from backroom_api.agents.tasks import TASKS
from backroom_api.browser import BrowserPool
from backroom_api.config import Settings
from backroom_api.contracts.events import RunEvent
from backroom_api.llm.client import LLM
from backroom_api.skills.store import SkillStore


async def _print(event: RunEvent) -> None:
    d: dict[str, Any] = event.model_dump(mode="json", exclude={"run_id", "ts"})
    kind = d.pop("type")
    seq = d.pop("seq")
    if kind == "cost.tick":
        t = d["totals"]
        print(f"{seq:>3} cost   ${t['usd']:.4f}  {t['llm_calls']} calls", flush=True)
        return
    if kind in ("step.started", "step.finished"):
        keep = {k: v for k, v in d.items() if v not in (None, "")}
        print(f"{seq:>3} {kind:<13} {json.dumps(keep, ensure_ascii=False)}", flush=True)
        return
    print(f"{seq:>3} {kind:<13} {json.dumps(d, ensure_ascii=False)[:300]}", flush=True)


async def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="backroom_api.agents.cli")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run")
    run.add_argument("task", choices=sorted(TASKS))
    run.add_argument("--seed", type=int, default=None, help="chaos seed to set first")
    run.add_argument("--cold", action="store_true", help="ignore the stored skill (explore)")
    run.add_argument("--param", action="append", default=[], help="name=value (JSON or text)")
    reset = sub.add_parser("reset-skill")
    reset.add_argument("task", choices=sorted(TASKS))
    args = parser.parse_args(argv)

    settings = Settings()
    store = SkillStore()
    if args.cmd == "reset-skill":
        store.delete(args.task)
        print(f"forgot {args.task}")
        return 0

    params: dict[str, Any] = {}
    for item in args.param:
        key, _, raw = item.partition("=")
        try:
            params[key] = json.loads(raw)
        except ValueError:
            params[key] = raw
    admin = PortalAdmin(settings)
    pool = BrowserPool()
    try:
        if args.seed is not None:
            await admin.set_chaos(TASKS[args.task].portal, args.seed)
        runner = SkillRunner(settings, LLM(settings), pool, store, admin)
        result = await runner.run(args.task, params, sink=_print, force_explore=args.cold)
    finally:
        await pool.close()
        await admin.close()
    t = result.totals
    print(
        f"\n{result.status.upper()}: {result.summary}\n"
        f"mode={result.mode} healed={result.healed} skill=v{result.skill_version} "
        f"steps={t.steps} llm_calls={t.llm_calls} tokens={t.tokens_in}/{t.tokens_out} "
        f"cache_read={t.cache_read_tokens} ${t.usd:.4f} {t.elapsed_ms / 1000:.1f}s"
    )
    for p in result.postconditions:
        print(f"  {'ok ' if p.ok else 'BAD'} {p.detail}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main(sys.argv[1:])))
