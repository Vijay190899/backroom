"""Runs: summary, the SSE event stream, the live screen, human answers and undo."""

import asyncio
from collections.abc import AsyncIterator

from fastapi import APIRouter, Header, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from backroom_api.contracts.api import HumanReply, RunSummary, UndoResponse
from backroom_api.contracts.events import to_sse
from backroom_api.live import repo
from backroom_api.live.runs import RunManager
from backroom_api.routes.errors import ApiProblem

router = APIRouter()
SSE_HEADERS = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}


def _runs(request: Request) -> RunManager:
    return request.app.state.runs


async def _row(runs: RunManager, run_id: str) -> dict[str, object]:
    row = await runs.db(repo.get_run, run_id)
    if row is None:
        raise ApiProblem(404, "not_found", f"no run {run_id}")
    return row


@router.get("/runs/{run_id}", response_model=RunSummary)
async def run_summary(run_id: str, request: Request) -> RunSummary:
    return repo.run_summary(await _row(_runs(request), run_id))  # type: ignore[arg-type]


@router.get("/runs/{run_id}/events")
async def run_events(
    run_id: str,
    request: Request,
    after: int = 0,
    last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
) -> StreamingResponse:
    """`id: <seq>`, `event: <type>`, `data: <RunEvent>` (CONTRACTS §5). A reconnecting
    EventSource sends Last-Event-ID and gets exactly the events after it."""
    runs = _runs(request)
    await _row(runs, run_id)
    if last_event_id and last_event_id.isdigit():
        after = max(after, int(last_event_id))

    async def stream() -> AsyncIterator[str]:
        yield "retry: 2000\n\n"
        async for event in runs.events(run_id, after):
            if await request.is_disconnected():
                return
            yield ": keep-alive\n\n" if event is None else to_sse(event)

    return StreamingResponse(stream(), media_type="text/event-stream", headers=SSE_HEADERS)


@router.websocket("/runs/{run_id}/screen")
async def run_screen(websocket: WebSocket, run_id: str) -> None:
    """A `{"type":"frame",...}` text message, then that frame's JPEG; `{"type":"cursor"}`
    messages move the halo. Closes when the run ends (finished runs: last frame, if any)."""
    runs: RunManager = websocket.app.state.runs
    await websocket.accept()
    queue = runs.screen(run_id)
    if queue is None:
        await websocket.close(code=4404, reason="no live screen for this run")
        return
    try:
        while True:
            message = await queue.get()
            if message is None:
                break
            if isinstance(message, tuple):
                meta, jpeg = message
                await websocket.send_text(meta.model_dump_json())
                await websocket.send_bytes(jpeg)
            else:
                await websocket.send_text(message.model_dump_json())
        await websocket.close()
    except (WebSocketDisconnect, RuntimeError, asyncio.CancelledError):
        pass
    finally:
        runs.drop_screen(run_id, queue)


@router.post("/runs/{run_id}/human", response_model=RunSummary)
async def run_human(run_id: str, reply: HumanReply, request: Request) -> RunSummary:
    runs = _runs(request)
    await _row(runs, run_id)
    if not runs.answer(run_id, reply.action):
        raise ApiProblem(409, "not_waiting", "this run is not waiting for an answer")
    await asyncio.sleep(0.05)  # let the run record the answer before we report its state
    return repo.run_summary(await _row(runs, run_id))  # type: ignore[arg-type]


@router.post("/runs/{run_id}/undo", response_model=UndoResponse)
async def run_undo(run_id: str, request: Request) -> UndoResponse:
    runs = _runs(request)
    row = await _row(runs, run_id)
    if not row["undo_available"] or row["undo_params"] is None:
        raise ApiProblem(409, "no_undo", "this run cannot be undone")
    new_id, _ = await runs.start(
        action_id=str(row["action_id"]),
        task=str(row["task"]),
        params=dict(row["undo_params"]),  # type: ignore[arg-type]
        idempotency_key=f"undo:{run_id}",  # undoing twice starts one undo run
        undo_of=run_id,
    )
    return UndoResponse(run_id=new_id, undo_of=run_id)
