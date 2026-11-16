"""B1 (browser robustness) and B2 (learning curve): orchestration and metrics.

The runs themselves need Chromium and the mock portals, so they happen on the PC (H7).
This module drives any `TaskRunner`: the PC's in-process skill runner, or `FakeRunner`
in tests. It sets the chaos seed, runs, and aggregates exactly what PRD §9 asks for.
"""

from collections.abc import Sequence
from dataclasses import asdict, dataclass
from statistics import fmean
from typing import Any, Literal, Protocol

from backroom_bench.results import percentile, rate, wilson

TASKS = ("grainline.reorder_item", "tilldesk.change_price", "grainline.download_invoice")
PORTAL = {
    "grainline.reorder_item": "grainline",
    "tilldesk.change_price": "tilldesk",
    "grainline.download_invoice": "grainline",
}
Start = Literal["cold", "warm"]
B2_SEEDS = (0, 7, 13)  # the starting look, then the redesigns at runs 8 and 15


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
    failure: str | None = None  # why it did not succeed (for the failure table)


class TaskRunner(Protocol):
    async def set_chaos(self, portal: str, seed: int) -> None: ...
    async def reset_skill(self, task: str) -> None:
        """Forget the compiled skill, so the next run is cold (EXPLORE)."""
        ...

    async def save_baseline(self, task: str) -> None:
        """Keep the current skill as the warm baseline (learned at seed 0)."""
        ...

    async def restore_baseline(self, task: str) -> None:
        """Put the baseline skill back, dropping versions a heal created since."""
        ...

    async def run(self, task: str) -> RunOutcome: ...


def summarize(outcomes: Sequence[RunOutcome]) -> dict[str, Any]:
    walls = [o.wall_ms for o in outcomes]
    hits = sum(o.ok for o in outcomes)
    return {
        "n": len(outcomes),
        "success": rate(hits, len(outcomes)),
        "success_ci95": wilson(hits, len(outcomes)),
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
    runner: TaskRunner,
    seeds: Sequence[int],
    tasks: Sequence[str] = TASKS,
    seed0_repeats: int = 5,
) -> dict[str, Any]:
    """Browser robustness, in two phases per task (PRD §9).

    - **Cold**: no skill; the agent explores. Seed 0 (the canonical design) is repeated
      `seed0_repeats` times, so "cold at seed 0" is a rate, not one run; every other seed
      runs once.
    - **Warm**: the skill learned at seed 0 replays on every seed. On a redesigned seed it
      has to heal; each warm run starts from that same seed-0 skill again.
    """
    rows: list[dict[str, Any]] = []
    done: list[tuple[str, int, Start, RunOutcome]] = []

    def keep(task: str, seed: int, start: Start, o: RunOutcome) -> None:
        done.append((task, seed, start, o))
        rows.append({"task": task, "seed": seed, "start": start, **asdict(o)})

    for task in tasks:
        portal = PORTAL[task]
        baseline = False
        for seed in [0] * seed0_repeats + [s for s in seeds if s != 0]:
            await runner.set_chaos(portal, seed)
            await runner.reset_skill(task)
            o = await runner.run(task)
            keep(task, seed, "cold", o)
            if seed == 0 and o.ok and not baseline:
                await runner.save_baseline(task)  # the first seed-0 skill is the baseline
                baseline = True
        for seed in seeds:
            if not baseline:  # nothing learned at seed 0: every warm run is a failure
                keep(
                    task,
                    seed,
                    "warm",
                    RunOutcome(False, 0, 0, 0, 0, 0.0, failure="no seed-0 skill"),
                )
                continue
            await runner.restore_baseline(task)
            await runner.set_chaos(portal, seed)
            keep(task, seed, "warm", await runner.run(task))
        await runner.set_chaos(portal, 0)

    def pick(
        start: Start, *, seed0: bool | None = None, task: str | None = None
    ) -> list[RunOutcome]:
        return [
            o
            for (t, s, st, o) in done
            if st == start and (task is None or t == task) and (seed0 is None or (s == 0) == seed0)
        ]

    groups = {f"{t}/{st}": summarize(pick(st, task=t)) for t in tasks for st in ("cold", "warm")}
    cold0, cold_all, warm_all = pick("cold", seed0=True), pick("cold"), pick("warm")
    warm_redesigned = pick("warm", seed0=False)
    return {
        "design": {
            "tasks": list(tasks),
            "seed0_repeats": seed0_repeats,
            "cold": "no skill; explore. Seed 0 repeated, other seeds once.",
            "warm": "the skill learned at seed 0, replayed on each seed (heals when redesigned).",
        },
        "groups": groups,
        "headline": {
            "cold_success_at_seed0": summarize(cold0)["success"],
            "cold_success_at_seed0_ci95": summarize(cold0)["success_ci95"],
            "cold_success_across_seeds": summarize(cold_all)["success"],
            "warm_success_across_seeds": summarize(warm_all)["success"],
            "warm_success_across_seeds_ci95": summarize(warm_all)["success_ci95"],
            "warm_success_on_redesigned_seeds": summarize(warm_redesigned)["success"],
            "warm_p50_ms_at_seed0": summarize(pick("warm", seed0=True))["p50_ms"],
            "targets": {"cold_success_at_seed0": 0.9, "warm_success_across_seeds": 0.85},
        },
        "failures": [r for r in rows if not r["ok"]],
        "runs": rows,
    }


async def b2(
    runner: TaskRunner,
    task: str = TASKS[0],
    runs: int = 20,
    redesign_at: Sequence[int] = (8, 15),
    seeds: Sequence[int] = B2_SEEDS,
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
    await runner.set_chaos(PORTAL[task], seeds[0])
    warm = [s for s in series if s["run"] not in (1, *redesign_at)]
    return {
        "task": task,
        "redesign_at": list(redesign_at),
        "series": series,
        "headline": {
            "warm_p50_ms": percentile([int(s["wall_ms"]) for s in warm], 50),
            "warm_usd": round(sum(float(s["usd"]) for s in warm), 6),
            # Fast failures must not pass for fast replays: report success alongside.
            "warm_success": rate(sum(bool(s["ok"]) for s in warm), len(warm)),
            "all_ok": all(bool(s["ok"]) for s in series),
            "redesigns_healed": [s["run"] for s in series if s["redesign"] and s["healed"]],
            "targets": {"warm_p50_ms": 5000, "warm_usd": 0.0},
        },
    }
