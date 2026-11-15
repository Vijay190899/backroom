"""Admin API (contract.ADMIN_ROUTES): chaos seeds, portal state for postconditions,
and reset. Every route needs the `X-Admin-Token` header."""

import hmac
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from backroom_portals import chaos
from backroom_portals.contract import (
    ADMIN_TOKEN_HEADER,
    PORTALS,
    ChaosRequest,
    ChaosState,
    GrainlineState,
    PortalName,
    TillDeskState,
)
from backroom_portals.rendering import ChaosSeeds


def require_admin(
    request: Request, token: Annotated[str | None, Header(alias=ADMIN_TOKEN_HEADER)] = None
) -> None:
    expected: str = request.app.state.settings.portals_admin_token
    if token is None or not hmac.compare_digest(token.encode(), expected.encode()):
        raise HTTPException(401, "admin token required")


router = APIRouter(prefix="/_admin", dependencies=[Depends(require_admin)])


def _chaos_state(seeds: ChaosSeeds, portal: PortalName) -> ChaosState:
    seed = seeds.seed(portal)
    return ChaosState(portal=portal, seed=seed, variants=chaos.pick_variants(portal, seed))


@router.get("/chaos")
def chaos_get(request: Request) -> list[ChaosState]:
    return [_chaos_state(request.app.state.chaos, p) for p in PORTALS]


@router.post("/chaos")
def chaos_set(request: Request, body: ChaosRequest) -> ChaosState:
    seeds: ChaosSeeds = request.app.state.chaos
    seeds.seeds[body.portal] = body.seed
    return _chaos_state(seeds, body.portal)


@router.get("/state/{portal}")
def state(request: Request, portal: PortalName) -> GrainlineState | TillDeskState:
    if portal == "grainline":
        return request.app.state.grainline.state()
    if portal == "tilldesk":
        return request.app.state.tilldesk.state()
    raise HTTPException(404, f"{portal} has no state yet")


@router.post("/reset", status_code=204)
def reset(request: Request) -> None:
    request.app.state.grainline.reset()
    request.app.state.tilldesk.reset()
    request.app.state.chaos.seeds.clear()
