"""Run recorder: numbers events, keeps the running totals, and meters every LLM call.

Every agent action in a run goes through one `RunRecorder`, so the event stream
(`contracts/events.py`) and the cost ticker always agree: the ticker is computed from the
same records the cost meter wrote. `sink` is where events go (the SSE route in H4, a list
in tests and benches); `events` keeps them all for golden-run recording (H6).
"""

import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, TypeVar

from backroom_api.config import Settings
from backroom_api.contracts.events import CostTick, RunEvent, RunTotals
from backroom_api.llm.client import LLM, LLMResult
from backroom_api.llm.registry import Role

EventSink = Callable[[RunEvent], Awaitable[None]]
E = TypeVar("E", bound=RunEvent)


@dataclass
class _Counters:
    calls: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
    cache_read: int = 0
    usd: float = 0.0


class RunRecorder:
    def __init__(self, run_id: str, llm: LLM | None, sink: EventSink | None = None) -> None:
        self.run_id = run_id
        self.events: list[RunEvent] = []
        self._llm = llm
        self._sink = sink
        self._seq = 0
        self._started = time.monotonic()
        self._total = _Counters()
        self._pending = _Counters()  # LLM work since the last finished step
        self.steps = 0
        self.skill_version: int | None = None

    async def emit(self, cls: type[E], **fields: Any) -> E:
        self._seq += 1
        event = cls(seq=self._seq, run_id=self.run_id, ts=datetime.now(UTC), **fields)  # type: ignore[call-arg]
        self.events.append(event)
        if self._sink is not None:
            await self._sink(event)
        return event

    def totals(self) -> RunTotals:
        t = self._total
        return RunTotals(
            elapsed_ms=int((time.monotonic() - self._started) * 1000),
            steps=self.steps,
            llm_calls=t.calls,
            tokens_in=t.tokens_in,
            tokens_out=t.tokens_out,
            cache_read_tokens=t.cache_read,
            usd=round(t.usd, 6),
        )

    @property
    def settings(self) -> Settings:
        if self._llm is None:
            raise RuntimeError("this run has no LLM")
        return self._llm.settings

    @property
    def usd(self) -> float:
        return self._total.usd

    def take_pending(self) -> tuple[int, int, int, float]:
        """LLM calls, tokens in, tokens out and $ since the last step finished."""
        p, self._pending = self._pending, _Counters()
        return p.calls, p.tokens_in, p.tokens_out, round(p.usd, 6)

    def step_done(self) -> None:
        self.steps += 1

    async def call(self, role: Role, **kwargs: Any) -> LLMResult:
        """One metered LLM call (the cost meter and budget guard run inside `LLM.create`)."""
        if self._llm is None:
            raise RuntimeError("this run has no LLM (replay-only)")
        result = await self._llm.create(role, run_id=self.run_id, **kwargs)
        u = result.message.usage
        for c in (self._total, self._pending):
            c.calls += 1
            c.tokens_in += u.input_tokens
            c.tokens_out += u.output_tokens
            c.cache_read += u.cache_read_input_tokens or 0
            c.usd += result.cost.usd
        await self.emit(CostTick, totals=self.totals(), skill_version=self.skill_version)
        return result
