"""Run manager: starts runs in the background and fans their events out to clients.

Every event a run emits is written to Postgres first (so `Last-Event-ID` resumes exactly,
even after a restart) and then handed to the run's in-memory channel, which wakes every
open SSE stream. Screen frames are not stored: each WebSocket gets the latest frame and the
ones after it, and a slow client skips frames instead of slowing the browser down.
"""

import asyncio
import logging
import uuid
from collections import OrderedDict
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

from fastapi.concurrency import run_in_threadpool
from psycopg_pool import ConnectionPool

from backroom_api.agents.runner import SkillRunner
from backroom_api.agents.tasks import TASKS
from backroom_api.browser.screencast import Frame
from backroom_api.contracts.events import Cursor, FrameMeta, RunEvent
from backroom_api.live import repo

log = logging.getLogger(__name__)
HUMAN_WAIT_S = 15 * 60  # an unanswered ask_human ends the run as needs_human
KEEP_CHANNELS = 50  # finished runs kept in memory; older ones replay from Postgres
ScreenMessage = tuple[FrameMeta, bytes] | Cursor | None  # None: the run is over


@dataclass
class Channel:
    events: list[RunEvent] = field(default_factory=list[RunEvent])
    changed: asyncio.Condition = field(default_factory=asyncio.Condition)
    finished: bool = False
    step_index: int | None = None
    last_frame: tuple[FrameMeta, bytes] | None = None
    screens: set[asyncio.Queue[ScreenMessage]] = field(
        default_factory=set[asyncio.Queue[ScreenMessage]]
    )
    human: asyncio.Future[str] | None = None


class RunManager:
    def __init__(self, runner: SkillRunner, pool: ConnectionPool) -> None:
        self.runner = runner
        self.pool = pool
        self._channels: OrderedDict[str, Channel] = OrderedDict()
        self._tasks: set[asyncio.Task[None]] = set()

    # --- database helpers -------------------------------------------------------------

    async def db[T](self, fn: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        def call() -> T:
            with self.pool.connection() as conn:
                return fn(conn, *args, **kwargs)

        return await run_in_threadpool(call)

    # --- starting runs ----------------------------------------------------------------

    async def start(
        self,
        *,
        action_id: str,
        task: str,
        params: dict[str, Any],
        idempotency_key: str | None,
        undo_of: str | None = None,
    ) -> tuple[str, bool]:
        """Start a run (or return the one this idempotency key already started).
        Returns (run id, deduplicated)."""
        if idempotency_key:
            existing = await self.db(repo.run_for_key, idempotency_key)
            if existing:
                return existing, True
        spec = TASKS[task]
        undo_params = await self._undo_params(task, params)
        run_id = f"run_{uuid.uuid4().hex[:10]}"
        created = await self.db(
            repo.create_run,
            run_id=run_id,
            action_id=action_id,
            task=task,
            portal=spec.portal,
            params=params,
            idempotency_key=idempotency_key,
            undo_of=undo_of,
            undo_params=undo_params,
        )
        if not created:  # another request with the same key won the race
            existing = await self.db(repo.run_for_key, idempotency_key or "")
            return existing or run_id, True
        self._channel(run_id)  # exists before the first event, so streams can attach
        job = asyncio.create_task(self._execute(run_id, action_id, task, params, undo_params))
        self._tasks.add(job)
        job.add_done_callback(self._tasks.discard)
        return run_id, False

    async def _undo_params(self, task: str, params: dict[str, Any]) -> dict[str, Any] | None:
        """The inverse action, as {"task", "params"}, or None. A price change is undone by
        setting the price that is live now; a reorder by cancelling the order it places
        (its id is only known when the run ends, so `params` is filled in then)."""
        if task == "grainline.reorder_item":
            return {"task": "grainline.cancel_order", "params": None}
        if task != "tilldesk.change_price":
            return None
        try:
            state = await self.runner.admin.state("tilldesk")
            item = state["items"][params["item_id"]]
        except Exception:  # no undo is better than a wrong one
            return None
        return {
            "task": task,
            "params": {"item_id": params["item_id"], "price_eur": item["published_price_eur"]},
        }

    async def _execute(
        self,
        run_id: str,
        action_id: str,
        task: str,
        params: dict[str, Any],
        undo_params: dict[str, Any] | None,
    ) -> None:
        channel = self._channel(run_id)

        async def sink(event: RunEvent) -> None:
            if (
                event.type == "run.finished"
                and undo_params is not None
                and undo_params["params"] is None
                and event.result.get("order")
            ):
                # The order exists now: record how to cancel it before anyone can see
                # the run finish (and press Undo).
                undo = {**undo_params, "params": {"order_id": event.result["order"]}}
                await self.db(repo.set_undo, run_id, undo)
            await self.db(repo.add_event, event)
            if event.type == "step.started":
                channel.step_index = event.index
            async with channel.changed:
                channel.events.append(event)
                channel.finished = event.type == "run.finished"
                channel.changed.notify_all()

        async def on_frame(frame: Frame) -> None:
            meta = FrameMeta(
                seq=frame.seq, width=frame.width, height=frame.height, ts=datetime.now(UTC)
            )
            channel.last_frame = (meta, frame.jpeg)
            self._fan_out(channel, (meta, frame.jpeg))

        async def on_cursor(x: float, y: float) -> None:
            self._fan_out(channel, Cursor(x=x, y=y, step_index=channel.step_index))

        async def ask_human(reason: str, index: int) -> str:
            loop = asyncio.get_running_loop()
            channel.human = loop.create_future()
            try:
                return await asyncio.wait_for(channel.human, HUMAN_WAIT_S)
            except TimeoutError:
                return "timeout"
            finally:
                channel.human = None

        status = "failed"
        try:
            result = await self.runner.run(
                task,
                params,
                run_id=run_id,
                action_id=action_id,
                sink=sink,
                on_frame=on_frame,
                on_cursor=on_cursor,
                ask_human=ask_human,
                undoable=undo_params is not None,
            )
            status = "done" if result.ok else "failed"
        except Exception:  # SkillRunner.run already turns crashes into run.finished
            log.exception("run %s", run_id)
        finally:
            self._fan_out(channel, None)
            await self.db(repo.set_action_status, action_id, status)

    # --- reading runs -----------------------------------------------------------------

    def _channel(self, run_id: str) -> Channel:
        channel = self._channels.get(run_id)
        if channel is None:
            channel = self._channels[run_id] = Channel()
            while len(self._channels) > KEEP_CHANNELS:
                oldest, old = next(iter(self._channels.items()))
                if not old.finished:
                    break
                del self._channels[oldest]
        return channel

    def live(self, run_id: str) -> Channel | None:
        return self._channels.get(run_id)

    async def events(
        self, run_id: str, after: int = 0, keepalive_s: float = 15.0
    ) -> AsyncIterator[RunEvent | None]:
        """Every event with seq > `after`, then live ones until `run.finished`. Yields
        None as a keep-alive when nothing happened for `keepalive_s`."""
        channel = self._channels.get(run_id)
        if channel is None:  # an older run, or a previous process: Postgres has it all
            for event in await self.db(repo.events_after, run_id, after):
                yield event
            return
        i = after  # seq n is events[n - 1]
        while True:
            while i < len(channel.events):
                event = channel.events[i]
                i += 1
                yield event
                if event.type == "run.finished":
                    return
            if channel.finished:
                return
            async with channel.changed:
                try:
                    await asyncio.wait_for(
                        channel.changed.wait_for(lambda n=i: len(channel.events) > n), keepalive_s
                    )
                except TimeoutError:
                    yield None

    def screen(self, run_id: str) -> asyncio.Queue[ScreenMessage] | None:
        channel = self._channels.get(run_id)
        if channel is None:
            return None
        queue: asyncio.Queue[ScreenMessage] = asyncio.Queue(maxsize=4)
        if channel.last_frame is not None:
            queue.put_nowait(channel.last_frame)
        if channel.finished:
            queue.put_nowait(None)
        else:
            channel.screens.add(queue)
        return queue

    def drop_screen(self, run_id: str, queue: asyncio.Queue[ScreenMessage]) -> None:
        channel = self._channels.get(run_id)
        if channel is not None:
            channel.screens.discard(queue)

    @staticmethod
    def _fan_out(channel: Channel, message: ScreenMessage) -> None:
        for queue in list(channel.screens):
            if message is not None and queue.full():
                continue  # a slow client skips frames; it never blocks the run
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                # The end-of-run marker must get through: make room for it.
                queue.get_nowait()
                queue.put_nowait(message)

    # --- human in the loop ------------------------------------------------------------

    def answer(self, run_id: str, action: Literal["resume", "cancel"]) -> bool:
        channel = self._channels.get(run_id)
        if channel is None or channel.human is None or channel.human.done():
            return False
        channel.human.set_result(action)
        return True

    async def shutdown(self) -> None:
        for job in list(self._tasks):
            job.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
