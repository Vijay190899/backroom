"""Today's brief: served from Postgres when one exists, generated when not.

Generation is the laptop's pipeline (detectors -> planner -> verifier -> number guard,
`brief/pipeline.py`) with the owner's rules read from memory. A rejection records the
reason (and any rule it states) and marks today's brief stale, so the next request
regenerates it under the new rule: "max 8%" turns the €3.60 card into €3.45.
"""

import asyncio
import json
import logging
from collections.abc import AsyncIterator, Callable
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from fastapi.concurrency import run_in_threadpool
from psycopg_pool import ConnectionPool

from backroom_api.brief import pipeline
from backroom_api.brief.agents import LLMPlanner, LLMVerifier
from backroom_api.brief.rules import rules_from_memory
from backroom_api.contracts.api import (
    ActionCard,
    Brief,
    BriefCardEvent,
    BriefDone,
    BriefSkeleton,
    RejectResponse,
)
from backroom_api.live import repo
from backroom_api.llm.client import LLM
from backroom_api.memory import extractor

log = logging.getLogger(__name__)
BONN = ZoneInfo("Europe/Berlin")
BriefEvent = BriefSkeleton | BriefCardEvent | BriefDone


class BriefService:
    def __init__(self, pool: ConnectionPool, llm: LLM | None, data_dir: Path) -> None:
        self.pool = pool
        self.llm = llm
        self.data_dir = data_dir
        self._lock = asyncio.Lock()  # one generation at a time; others wait for its result

    async def db[T](self, fn: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        def call() -> T:
            with self.pool.connection() as conn:
                return fn(conn, *args, **kwargs)

        return await run_in_threadpool(call)

    def _day(self, now: datetime) -> date:
        """The day the brief is for: the day the data was built for (`pnpm seed` writes it to
        manifest.json), not the clock's. Otherwise, after midnight, every request would miss
        the cache and pay for a new brief."""
        try:
            manifest = json.loads((self.data_dir / "manifest.json").read_text(encoding="utf-8"))
            return date.fromisoformat(manifest["today"])
        except (OSError, ValueError, KeyError):
            return now.astimezone(BONN).date()

    async def today(self) -> Brief:
        now = datetime.now(BONN)
        cached = await self.db(repo.current_brief, self._day(now))
        if cached is not None:
            return cached
        async with self._lock:
            cached = await self.db(repo.current_brief, self._day(now))  # built while we waited
            if cached is not None:
                return cached
            brief: Brief | None = None
            async for event in self._generate(now):
                if isinstance(event, BriefDone):
                    brief = event.brief
            assert brief is not None
            return brief

    async def regenerate(self) -> AsyncIterator[BriefEvent]:
        """GET /brief/today?regenerate=1: a fresh brief, streamed card by card."""
        async with self._lock:
            async for event in self._generate(datetime.now(BONN)):
                yield event

    async def _generate(self, now: datetime) -> AsyncIterator[BriefEvent]:
        rules = await self.db(rules_from_memory, now)
        planner = LLMPlanner(self.llm) if self.llm else _NoModel()
        verifier = LLMVerifier(self.llm) if self.llm else _NoModel()
        async for item in pipeline.stream_today(
            self.data_dir,
            planner=planner,  # type: ignore[arg-type]
            verifier=verifier,  # type: ignore[arg-type]
            rules=rules,
            now=now,
        ):
            if isinstance(item, pipeline.BriefResult):
                await self.db(repo.save_brief, item.brief)
                for d in item.decisions:
                    log.info("brief %s: %s %s %s", item.brief.id, d.candidate_id, d.step, d.detail)
            elif isinstance(item, BriefCardEvent):
                statuses = await self.db(repo.action_statuses, [item.card.id])
                status = statuses.get(item.card.id, item.card.status)
                yield item.model_copy(
                    update={"card": item.card.model_copy(update={"status": status})}
                )
            elif isinstance(item, BriefDone):
                yield BriefDone(brief=await self.db(repo.with_statuses, item.brief))
            else:
                yield item

    async def reject(self, card: ActionCard, reason: str) -> RejectResponse:
        rule = None
        if self.llm is not None:
            try:
                rule = await extractor.extract(self.llm, reason, card)
            except Exception:  # the episode is still recorded; only the rule is lost
                log.exception("preference extraction failed")
        now = datetime.now(BONN)

        def record(conn: Any) -> RejectResponse:
            response = extractor.record_rejection(conn, card=card, reason=reason, rule=rule, at=now)
            conn.commit()
            return response

        response = await self.db(record)
        await self.db(repo.set_action_status, card.id, "rejected")
        await self.db(repo.mark_briefs_stale, self._day(now))
        return response


class _NoModel:
    """Without a model key the pipeline still works: template copy, code-only checks."""

    async def plan(self, *_: Any, **__: Any) -> Any:
        from backroom_api.brief.agents import BriefLLMError

        raise BriefLLMError("no model configured")

    async def verify(self, *_: Any, **__: Any) -> Any:
        from backroom_api.brief.agents import BriefLLMError

        raise BriefLLMError("no model configured")
