import httpx
from fastapi import APIRouter, Request, Response
from fastapi.concurrency import run_in_threadpool

from backroom_api import db
from backroom_api.llm import registry

router = APIRouter()


async def _postgres_ok(request: Request) -> bool:
    try:
        return await run_in_threadpool(db.ping, request.app.state.pool)
    except Exception:
        return False


async def _portals_ok(base_url: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{base_url}/health")
        return resp.status_code == 200
    except httpx.HTTPError:
        return False


@router.get("/health")
async def health(request: Request, response: Response) -> dict[str, object]:
    """Liveness plus dependency checks. Postgres and portals are required; a missing
    LLM key is reported but does not fail the check (replay mode needs no LLM)."""
    settings = request.app.state.settings
    postgres = await _postgres_ok(request)
    portals = await _portals_ok(settings.portals_base_url)
    healthy = postgres and portals
    if not healthy:
        response.status_code = 503
    return {
        "status": "ok" if healthy else "degraded",
        "checks": {
            "postgres": "ok" if postgres else "down",
            "portals": "ok" if portals else "down",
            "llm": {
                "provider": settings.llm_provider,
                "configured": registry.is_configured(settings),
            },
        },
        "demo_mode": settings.demo_mode,
    }
