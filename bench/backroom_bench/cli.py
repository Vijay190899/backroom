"""`backroom-bench`: the benchmark harness (B1-B3, B5) and the provider capability probe.

    backroom-bench probe                      provider capability probe (M0)
    backroom-bench all|b1|b2|b3|b5 [--fake]   benchmarks -> bench/results/<id>.json

The browser benchmarks need a runner (Chromium + portals, on the PC): pass
`--runner module:factory`. B3's context-pack arm needs the memory store: pass
`--pack module:callable` (question text -> ContextPack.text). `--fake` runs everything on
deterministic fakes into var/bench-fake/, marked fake, never into bench/results/.
"""

import argparse
import asyncio
import importlib
import json
import sys
from pathlib import Path
from typing import Any

from backroom_api.config import get_settings
from backroom_api.contracts.api import Brief
from backroom_bench import browser, fakes, guard_bench, memory_bench, probe, results

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_BRIEFS = ROOT / "apps" / "web" / "src" / "fixtures"
BENCH_BRIEFS = ROOT / "var" / "bench" / "briefs"
FAKE_OUT = ROOT / "var" / "bench-fake"


def _load(spec: str) -> Any:
    module, _, name = spec.partition(":")
    return getattr(importlib.import_module(module), name)


def _briefs(directory: Path) -> list[Brief]:
    return [
        Brief.model_validate(json.loads(p.read_text(encoding="utf-8")))
        for p in sorted(directory.glob("brief*.json"))
    ]


async def _browser_benches(
    args: argparse.Namespace,
    runner: Any,
    which: set[str],
    seeds: list[int],
    settings: Any,
    out: Path,
    written: list[Path],
) -> None:
    if "b1" in which:
        body = await browser.b1(runner, seeds, seed0_repeats=args.seed0_repeats)
        written.append(
            results.write(
                "B1",
                body,
                settings=settings,
                seeds=seeds,
                n=len(body["runs"]),
                fake=args.fake,
                out_dir=out,
            )
        )
    if "b2" in which:
        body = await browser.b2(runner)
        written.append(
            results.write(
                "B2",
                body,
                settings=settings,
                seeds=list(browser.B2_SEEDS),
                n=len(body["series"]),
                fake=args.fake,
                out_dir=out,
            )
        )


async def _briefs_cmd(n: int) -> int:
    from backroom_bench import brief_gen

    written, usd = await brief_gen.generate(n, BENCH_BRIEFS, get_settings())
    print(f"wrote {len(written)} briefs to {BENCH_BRIEFS.relative_to(ROOT)} (${usd:.4f})")
    return 0


async def _run(args: argparse.Namespace) -> int:
    settings = get_settings()
    out = FAKE_OUT if args.fake else Path(args.out)
    which = {"b1", "b2", "b3", "b5"} if args.command == "all" else {args.command}
    seeds = list(range(args.seeds))
    written: list[Path] = []
    skipped: list[str] = []  # asked for but not run: the exit code says so

    if which & {"b1", "b2"}:
        runner = (
            fakes.FakeRunner() if args.fake else (_load(args.runner)() if args.runner else None)
        )
        if runner is None:
            print(
                "B1/B2 need a browser runner: --runner module:factory (runs on the PC).",
                file=sys.stderr,
            )
            skipped += sorted(which & {"b1", "b2"})
            which -= {"b1", "b2"}
        else:
            try:
                await _browser_benches(args, runner, which, seeds, settings, out, written)
            finally:
                close = getattr(runner, "close", None)
                if close is not None:  # the real runner restores the demo's skills
                    await close()

    if "b3" in which:
        con = memory_bench.connect()
        truth = memory_bench.ground_truth(con)
        if args.fake:
            answerer: memory_bench.Answerer = fakes.FakeAnswerer(truth)
            pack_for = fakes.fake_pack
        else:
            from backroom_api.llm.client import LLM

            answerer = memory_bench.LlmAnswerer(LLM(settings))
            pack_for = _load(args.pack) if args.pack else None
        if pack_for is None:
            # Without the arm under test, B3 would publish a result with no headline.
            print(
                "B3 needs the context pack: --pack module:callable (runs on the PC).",
                file=sys.stderr,
            )
            skipped.append("b3")
        else:
            arms: list[memory_bench.ContextArm] = [
                memory_bench.PackArm(pack_for),
                memory_bench.RawDump(con),
                memory_bench.NoMemory(),
            ]
            body = await memory_bench.b3(answerer, arms, truth)
            usd = sum(float(a["usd"]) for a in body["arms"].values())
            body["cost"] = results.with_fee(usd, settings)
            written.append(
                results.write(
                    "B3",
                    body,
                    settings=settings,
                    n=len(memory_bench.QUESTIONS),
                    fake=args.fake,
                    out_dir=out,
                )
            )

    if "b5" in which:
        # Real runs grade the briefs generated during the bench; only --fake may fall
        # back to the committed sample briefs.
        source = (
            Path(args.briefs) if args.briefs else (FIXTURE_BRIEFS if args.fake else BENCH_BRIEFS)
        )
        briefs = [b for b in _briefs(source) if b.cards] if source.exists() else []
        if not briefs:
            print(f"B5: no briefs in {source} (save the bench's briefs there).", file=sys.stderr)
            skipped.append("b5")
        else:
            body = {
                "guard": guard_bench.summarize(briefs),
                "verification": guard_bench.verify(briefs),
            }
            written.append(
                results.write(
                    "B5", body, settings=settings, n=len(briefs), fake=args.fake, out_dir=out
                )
            )

    for p in written:
        print(f"wrote {p.relative_to(ROOT) if p.is_relative_to(ROOT) else p}")
    if skipped:
        print(f"skipped: {', '.join(skipped)}", file=sys.stderr)
    return 0 if written and not skipped else 2


def main() -> None:
    parser = argparse.ArgumentParser(prog="backroom-bench")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("probe", help="check which LLM features the active provider supports")
    gen = sub.add_parser("briefs", help="generate the briefs B5 grades (real models, PC)")
    gen.add_argument("--n", type=int, default=10)
    for name in ("all", "b1", "b2", "b3", "b5"):
        p = sub.add_parser(name, help=f"run {'B1-B3 and B5' if name == 'all' else name.upper()}")
        p.add_argument(
            "--fake", action="store_true", help="deterministic fakes, written to var/bench-fake/"
        )
        p.add_argument("--out", default=str(results.RESULTS_DIR))
        p.add_argument("--seeds", type=int, default=20, help="B1 chaos seeds 0..N-1")
        p.add_argument("--seed0-repeats", type=int, default=5, help="B1 cold runs at seed 0")
        p.add_argument("--runner", help="B1/B2 runner factory, module:callable")
        p.add_argument("--pack", help="B3 context pack, module:callable (question -> text)")
        p.add_argument("--briefs", help="B5: a directory of brief JSONs generated during the bench")
    args = parser.parse_args()
    if args.command == "probe":
        raise SystemExit(probe.main())
    if args.command == "briefs":
        raise SystemExit(asyncio.run(_briefs_cmd(args.n)))
    raise SystemExit(asyncio.run(_run(args)))
