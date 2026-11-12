"""Admin API (contract.ADMIN_ROUTES): portal state for postconditions, and reset.

Every route needs the `X-Admin-Token` header. The chaos routes arrive with L2.
"""

import hmac
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from backroom_portals.contract import ADMIN_TOKEN_HEADER, GrainlineState, PortalName


def require_admin(
    request: Request, token: Annotated[str | None, Header(alias=ADMIN_TOKEN_HEADER)] = None
) -> None:
    expected: str = request.app.state.settings.portals_admin_token
    if token is None or not hmac.compare_digest(token, expected):
        raise HTTPException(401, "admin token required")


router = APIRouter(prefix="/_admin", dependencies=[Depends(require_admin)])


@router.get("/state/{portal}")
def state(request: Request, portal: PortalName) -> GrainlineState:
    if portal == "grainline":
        return request.app.state.grainline.state()
    raise HTTPException(404, f"{portal} has no state yet")


@router.post("/reset", status_code=204)
def reset(request: Request) -> None:
    request.app.state.grainline.reset()
    request.app.state.chaos.seeds.clear()
