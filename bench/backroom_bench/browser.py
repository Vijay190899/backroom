"""B1 (browser robustness) and B2 (learning curve): orchestration and metrics.

The runs themselves need Chromium and the mock portals, so they happen on the PC (H7).
This module drives any `TaskRunner`: the PC's in-process skill runner, or `FakeRunner`
in tests. It sets the chaos seed, runs, and aggregates exactly what PRD §9 asks for.
"""

from collections.abc import Sequence
from dataclasses import asdict, dataclass
from statistics import fmean
from typing import Any, Literal, Protocol

from backroom_bench.results import percentile, rate

TASKS = ("grainline.reorder_item", "tilldesk.change_price", "grainline.download_invoice")
PORTAL = {
    "grainline.reorder_item": "grainline",
    "tilldesk.change_price": "tilldesk",
    "grainline.download_invoice": "grainline",
}
Start = Literal["cold", "warm"]


@dataclass(frozen=True)
class RunOutcome:
    ok: bool  # postconditions verified (never "looked done")
    wall_ms: int
    llm_calls: int
    tokens_in: int
    tokens_out: int
    usd: float
    healed: bool = False
    escalated: bool = False  # ended in a human handoff (counts as not ok)


class TaskRunner(Protocol):
    async def set_chaos(self, portal: str, seed: int) -> None: ...
    async def reset_skill(self, task: str) -> None:
        """Forget the compiled skill, so the next run is cold (EXPLORE)."""
        ...

    async def run(self, task: str) -> RunOutcome: ...


def summarize(outcomes: Sequence[RunOutcome]) -> dict[str, float | int | None]:
    walls = [o.wall_ms for o in outcomes]
    return {
        "n": len(outcomes),
        "success": rate(sum(o.ok for o in outcomes), len(outcomes)),
        "healed": sum(o.healed for o in outcomes),
        "escalated": sum(o.escalated for o in outcomes),
        "p50_ms": percentile(walls, 50),
        "p95_ms": percentile(walls, 95),
        "llm_calls": sum(o.llm_calls for o in outcomes),
        "tokens_in": sum(o.tokens_in for o in outcomes),
        "tokens_out": sum(o.tokens_out for o in outcomes),
        "usd": round(sum(o.usd for o in outcomes), 6),
        "mean_usd": round(fmean([o.usd for o in outcomes]), 6) if outcomes else None,
    }


async def b1(
    runner: TaskRunner, seeds: Sequence[int], tasks: Sequence[str] = TASKS
) -> dict[str, Any]:
    """Each task x chaos seed, cold (fresh EXPLORE) then warm (REPLAY, healing if needed)."""
    rows: list[dict[str, Any]] = []
    done: list[tuple[str, int, Start, RunOutcome]] = []
    for task in tasks:
        for seed in seeds:
            await runner.set_chaos(PORTAL[task], seed)
            await runner.reset_skill(task)
            for start in ("cold", "warm"):
                o = await runner.run(task)
                done.append((task, seed, start, o))
                rows.append({"task": task, "seed": seed, "start": start, **asdict(o)})
    groups = {
        f"{t}/{st}": summarize([o for (tt, _, ss, o) in done if tt == t and ss == st])
        for t in tasks
        for st in ("cold", "warm")
    }
    cold_seed0 = [o for (_, seed, st, o) in done if seed == 0 and st == "cold"]
    warm_all = [o for (_, _, st, o) in done if st == "warm"]
    return {
        "groups": groups,
        "headline": {
            "cold_success_at_seed0": rate(sum(o.ok for o in cold_seed0), len(cold_seed0)),
            "warm_success_across_seeds": rate(sum(o.ok for o in warm_all), len(warm_all)),
            "targets": {"cold_success_at_seed0": 0.9, "warm_success_across_seeds": 0.85},
        },
        "runs": rows,
    }


async def b2(
    runner: TaskRunner,
    task: str = TASKS[0],
    runs: int = 20,
    redesign_at: Sequence[int] = (8, 15),
    seeds: Sequence[int] = (0, 7, 13),
) -> dict[str, Any]:
    """The same task `runs` times in a row; the portal is redesigned (new chaos seed) at
    the given 1-based run numbers. Expect spikes there, then recovery to cheap replays."""
    await runner.reset_skill(task)
    await runner.set_chaos(PORTAL[task], seeds[0])
    series: list[dict[str, Any]] = []
    designs = iter(seeds[1:])
    for i in range(1, runs + 1):
        if i in redesign_at:
            await runner.set_chaos(PORTAL[task], next(designs))
        o = await runner.run(task)
        series.append({"run": i, "redesign": i in redesign_at, **asdict(o)})
    warm = [s for s in series if s["run"] not in (1, *redesign_at)]
    return {
        "task": task,
        "redesign_at": list(redesign_at),
        "series": series,
        "headline": {
            "warm_p50_ms": percentile([int(s["wall_ms"]) for s in warm], 50),
            "warm_usd": round(sum(float(s["usd"]) for s in warm), 6),
            "targets": {"warm_p50_ms": 5000, "warm_usd": 0.0},
        },
    }
