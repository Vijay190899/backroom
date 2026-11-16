"""The bench harness end to end on fakes: every benchmark aggregates and writes its JSON."""

import json
from pathlib import Path

import pytest

from backroom_api.config import Settings
from backroom_bench import browser, fakes, memory_bench, results
from backroom_bench.questions import QUESTIONS, Question

DATA = Path(__file__).resolve().parents[2] / "data" / "out"


def test_percentile_and_rate() -> None:
    assert results.percentile([5, 1, 3, 2, 4], 50) == 3
    assert results.percentile([5, 1, 3, 2, 4], 95) == 5
    assert results.percentile([], 50) is None
    assert results.rate(17, 20) == 0.85


def test_fee_line_only_on_openrouter() -> None:
    assert results.with_fee(1.0, Settings(llm_provider="openrouter"))["provider_fee_usd"] == 0.055
    assert results.with_fee(1.0, Settings(llm_provider="anthropic"))["provider_fee_usd"] == 0.0


async def test_b1_cold_repeats_and_warm_from_the_seed0_skill() -> None:
    body = await browser.b1(fakes.FakeRunner(), seeds=[0, 1, 2], seed0_repeats=4)
    # per task: 4 cold at seed 0 + 2 cold at other seeds + 3 warm
    assert len(body["runs"]) == 3 * (4 + 2 + 3)
    head = body["headline"]
    assert head["cold_success_at_seed0"] == 1.0 and head["warm_success_across_seeds"] == 1.0
    assert (
        head["cold_success_at_seed0_ci95"][1] == 1.0 and head["cold_success_at_seed0_ci95"][0] < 1
    )
    warm = [r for r in body["runs"] if r["start"] == "warm"]
    # Warm starts from the seed-0 skill: free at seed 0, a heal on every redesigned seed.
    assert all(not r["healed"] and r["usd"] == 0 for r in warm if r["seed"] == 0)
    assert all(r["healed"] for r in warm if r["seed"] != 0)
    assert body["failures"] == []


async def test_b1_without_a_seed0_skill_counts_every_warm_run_as_failed() -> None:
    class NeverLearns(fakes.FakeRunner):
        async def run(self, task: str) -> browser.RunOutcome:
            return browser.RunOutcome(False, 30_000, 25, 1, 1, 0.05, failure="max_steps")

    body = await browser.b1(NeverLearns(), seeds=[0, 1], tasks=[browser.TASKS[0]], seed0_repeats=2)
    warm = [r for r in body["runs"] if r["start"] == "warm"]
    assert [r["failure"] for r in warm] == ["no seed-0 skill", "no seed-0 skill"]
    assert body["headline"]["cold_success_at_seed0"] == 0.0 and len(body["failures"]) == 5


def test_wilson_interval() -> None:
    assert results.wilson(0, 0) is None
    low, high = results.wilson(15, 15)  # type: ignore[misc]
    assert high == 1.0 and 0.79 < low < 0.80  # 15/15 is not proof of 100%
    low, high = results.wilson(17, 20)  # type: ignore[misc]
    assert 0.63 < low < 0.65 and 0.94 < high < 0.96


async def test_b2_spikes_at_redesigns_then_recovers() -> None:
    body = await browser.b2(fakes.FakeRunner())
    series = body["series"]
    healed = [s["run"] for s in series if s["healed"]]
    assert healed == [8, 15]
    assert body["headline"]["redesigns_healed"] == [8, 15] and body["headline"]["all_ok"] is True
    assert body["headline"]["warm_usd"] == 0.0


def test_grading() -> None:
    num, cnt, txt = (
        Question("a", "", "", "number"),
        Question("b", "", "", "count"),
        Question("c", "", "", "text"),
    )
    assert memory_bench.correct(num, 100.0, "100.9") and not memory_bench.correct(
        num, 100.0, "101.5"
    )
    assert memory_bench.correct(num, 3.2, "€3.20") and not memory_bench.correct(num, 3.2, None)
    assert memory_bench.correct(num, 8.24, "8,24") and memory_bench.correct(num, -5.0, "\u22125")
    assert memory_bench.correct(cnt, 49, "49") and not memory_bench.correct(cnt, 49, "49.4")
    assert memory_bench.correct(txt, "Whit Monday", "whit monday ") and not memory_bench.correct(
        txt, "Tuesday", "Monday"
    )


@pytest.mark.skipif(
    not (DATA / "sales.parquet").exists(), reason="seeded data not built (pnpm seed)"
)
async def test_b3_on_real_ground_truth(tmp_path: Path) -> None:
    con = memory_bench.connect(DATA)
    truth = memory_bench.ground_truth(con)
    assert len(truth) == len(QUESTIONS) == 30
    assert truth["q07"] == 8.24 and truth["q08"] == 7.1  # the butter story
    arms = [
        memory_bench.PackArm(fakes.fake_pack),
        memory_bench.RawDump(con),
        memory_bench.NoMemory(),
    ]
    body = await memory_bench.b3(fakes.FakeAnswerer(truth), arms, truth)
    acc = {k: v["accuracy"] for k, v in body["arms"].items()}
    assert acc == {"context_pack": 1.0, "raw_dump": 1.0, "none": 0.0}
    assert body["headline"]["pack_tokens_vs_dump"] < 0.2
    path = results.write("B3", body, settings=Settings(), n=30, fake=True, out_dir=tmp_path)
    saved = json.loads(path.read_text())
    assert saved["fake"] is True and saved["n"] == 30 and saved["git_sha"]
