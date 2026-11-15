"""GET /brief/today, POST /actions/{id}/approve, POST /actions/{id}/reject."""

from collections.abc import AsyncIterator

from fastapi import APIRouter, Header, Request
from fastapi.responses import StreamingResponse

from backroom_api.contracts.api import ApproveResponse, Brief, RejectRequest, RejectResponse
from backroom_api.live import repo
from backroom_api.live.briefs import BriefService
from backroom_api.live.runs import RunManager
from backroom_api.routes.errors import ApiProblem

router = APIRouter()
SSE_HEADERS = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}


def _briefs(request: Request) -> BriefService:
    return request.app.state.briefs


def _runs(request: Request) -> RunManager:
    return request.app.state.runs


@router.get("/brief/today", response_model=Brief)
async def brief_today(request: Request, regenerate: bool = False) -> Brief | StreamingResponse:
    briefs = _briefs(request)
    if not regenerate:
        return await briefs.today()

    async def stream() -> AsyncIterator[str]:
        async for event in briefs.regenerate():
            yield f"event: {event.type}\ndata: {event.model_dump_json()}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream", headers=SSE_HEADERS)


@router.post("/actions/{action_id}/approve", response_model=ApproveResponse)
async def approve(
    action_id: str,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> ApproveResponse:
    runs = _runs(request)
    found = await runs.db(repo.get_action, action_id)
    if found is None:
        raise ApiProblem(404, "not_found", f"no action {action_id}")
    card, status = found
    if not card.executable or card.task is None:
        raise ApiProblem(409, "not_executable", "this card is a recommendation, not an action")
    if idempotency_key:
        existing = await runs.db(repo.run_for_key, idempotency_key)
        if existing:
            return ApproveResponse(run_id=existing, action_id=action_id, deduplicated=True)
    if status == "running":
        raise ApiProblem(409, "already_running", "this action is already running")
    run_id, deduplicated = await runs.start(
        action_id=action_id,
        task=card.task,
        params=card.params,
        idempotency_key=idempotency_key,
    )
    if not deduplicated:
        await runs.db(repo.set_action_status, action_id, "running")
    return ApproveResponse(run_id=run_id, action_id=action_id, deduplicated=deduplicated)


@router.post("/actions/{action_id}/reject", response_model=RejectResponse)
async def reject(action_id: str, body: RejectRequest, request: Request) -> RejectResponse:
    briefs = _briefs(request)
    found = await briefs.db(repo.get_action, action_id)
    if found is None:
        raise ApiProblem(404, "not_found", f"no action {action_id}")
    card, status = found
    if status == "running":
        raise ApiProblem(409, "already_running", "this action is running; it can't be rejected")
    return await briefs.reject(card, body.reason)
