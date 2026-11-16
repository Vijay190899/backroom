"""Read-mostly routes: skills, memory and the chaos switch."""

import itertools
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Request
from psycopg import Connection
from psycopg.rows import dict_row

from backroom_api.agents.portals_admin import PortalAdmin
from backroom_api.agents.tasks import TASKS
from backroom_api.contracts.api import (
    ChaosRequest,
    ChaosState,
    FactDetail,
    GraphFact,
    GraphNode,
    MemoryGraph,
    SkillSummary,
    SkillVersions,
)
from backroom_api.live.access import require_live
from backroom_api.live.runs import RunManager
from backroom_api.memory import store as memory
from backroom_api.routes.errors import ApiProblem
from backroom_api.skills.schema import SkillDiff
from backroom_api.skills.store import SkillStore

router = APIRouter()


def _skills(request: Request) -> SkillStore:
    return request.app.state.skills


# --- skills ---------------------------------------------------------------------------


@router.get("/skills", response_model=list[SkillSummary])
async def skills(request: Request) -> list[SkillSummary]:
    store = _skills(request)
    out: list[SkillSummary] = []
    for task in TASKS:
        versions = store.versions(task)
        if not versions:
            continue
        all_versions = [s for v in versions if (s := store.get(task, v)) is not None]
        latest = all_versions[-1]
        runs = sum(s.stats.runs for s in all_versions)
        successes = sum(s.stats.successes for s in all_versions)
        last_runs = [s.stats.last_run_at for s in all_versions if s.stats.last_run_at]
        out.append(
            SkillSummary(
                id=latest.id,
                task=latest.task,
                portal=latest.portal,
                latest_version=latest.version,
                runs=runs,
                success_rate=successes / runs if runs else None,
                mean_latency_ms=latest.stats.mean_latency_ms,
                mean_usd=latest.stats.mean_usd,
                updated_at=max([latest.created_at, *last_runs]),
            )
        )
    return out


@router.get("/skills/{skill_id}/versions", response_model=SkillVersions)
async def skill_versions(skill_id: str, request: Request) -> SkillVersions:
    store = _skills(request)
    if skill_id not in TASKS:
        raise ApiProblem(404, "not_found", f"no skill {skill_id}")
    numbers = store.versions(skill_id)
    if not numbers:
        raise ApiProblem(404, "not_found", f"{skill_id} has not been learned yet")
    versions = [s for v in numbers if (s := store.get(skill_id, v)) is not None]
    diffs: list[SkillDiff] = []
    for older, newer in itertools.pairwise(versions):
        diff = store.get_diff(skill_id, newer.version)
        diffs.append(
            diff
            if diff is not None and diff.from_version == older.version
            else SkillDiff(
                skill_id=skill_id,
                from_version=older.version,
                to_version=newer.version,
                changes=[],
            )
        )
    return SkillVersions(skill_id=skill_id, versions=versions, diffs=diffs)


# --- memory ---------------------------------------------------------------------------


def _history(conn: Connection[Any], as_of: datetime) -> MemoryGraph:
    """Every fact recorded so far, superseded ones included, so the time slider can show
    any moment without another request (the client filters by validity)."""
    with conn.cursor(row_factory=dict_row) as cur:
        facts = cur.execute(
            "select id, subject_id, predicate, object_id, value, valid_from, valid_to, "
            "confidence from fact where recorded_at <= now() "
            "order by subject_id, predicate, valid_from"
        ).fetchall()
        ids = sorted(
            {f["subject_id"] for f in facts} | {f["object_id"] for f in facts if f["object_id"]}
        )
        nodes = cur.execute(
            "select id, type, name from entity where id = any(%s) order by id", [ids]
        ).fetchall()
    return MemoryGraph(
        as_of=as_of,
        nodes=[GraphNode(**n) for n in nodes],
        facts=[GraphFact(**f) for f in facts],
    )


@router.get("/memory/graph", response_model=MemoryGraph)
async def memory_graph(request: Request, as_of: datetime | None = None) -> MemoryGraph:
    runs: RunManager = request.app.state.runs
    when = as_of or datetime.now(UTC)
    if when.tzinfo is None:
        raise ApiProblem(400, "bad_request", "as_of needs a time zone (e.g. ...Z)")
    return await runs.db(_history, when)


@router.get("/memory/facts/{fact_id}", response_model=FactDetail)
async def memory_fact(fact_id: str, request: Request) -> FactDetail:
    runs: RunManager = request.app.state.runs
    detail = await runs.db(memory.fact_detail, fact_id)
    if detail is None:
        raise ApiProblem(404, "not_found", f"no fact {fact_id}")
    return detail


# --- chaos (dev/demo) -----------------------------------------------------------------


@router.get("/chaos", response_model=list[ChaosState])
async def chaos_state(request: Request) -> list[ChaosState]:
    admin: PortalAdmin = request.app.state.admin
    return [ChaosState.model_validate(s) for s in await admin.chaos()]


@router.post("/chaos", response_model=ChaosState)
async def set_chaos(body: ChaosRequest, request: Request) -> ChaosState:
    require_live(request)  # re-skins the portal for every visitor
    admin: PortalAdmin = request.app.state.admin
    try:
        state = await admin.set_chaos(body.portal, body.seed)
    except Exception as exc:
        raise ApiProblem(503, "portals_unavailable", f"the portals did not answer: {exc}") from exc
    return ChaosState.model_validate(state)
