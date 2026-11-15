"""Deterministic stand-ins for the parts that need Chromium, Postgres or a model, so the
harness runs end to end anywhere (tests, `backroom-bench all --fake`). Never published."""

from typing import Any

from backroom_bench.browser import RunOutcome
from backroom_bench.memory_bench import Answer
from backroom_bench.questions import QUESTIONS


class FakeRunner:
    """Cold runs explore (model calls); warm runs replay for free; a redesigned portal
    (non-zero seed) costs one heal on the first warm run after it."""

    def __init__(self) -> None:
        self.seed: dict[str, int] = {}
        self.learned: dict[str, int | None] = {}

    async def set_chaos(self, portal: str, seed: int) -> None:
        self.seed[portal] = seed

    async def reset_skill(self, task: str) -> None:
        self.learned[task] = None

    async def run(self, task: str) -> RunOutcome:
        seed = self.seed.get(task.split(".")[0], 0)
        known = self.learned.get(task)
        self.learned[task] = seed
        if known is None:
            return RunOutcome(True, 21_000, 14, 56_000, 2_800, 0.0084)
        if known != seed:
            return RunOutcome(True, 8_400, 1, 4_200, 96, 0.0016, healed=True)
        return RunOutcome(True, 2_300, 0, 0, 0, 0.0)


class FakeAnswerer:
    """Right with the context pack or the raw dump, silent without memory; token counts
    scale with the context, like the real thing."""

    def __init__(self, truth: dict[str, Any]) -> None:
        self._truth = {q.text: truth[q.id] for q in QUESTIONS}

    async def answer(self, question: str, context: str) -> Answer:
        tokens = 120 + len(context) // 4
        value = None if not context else str(self._truth[question])
        return Answer(value, tokens, 8, 0, round(tokens * 1e-6, 6), 400 + tokens // 100)


def fake_pack(question: str) -> str:
    return f"(fake context pack for: {question})"
