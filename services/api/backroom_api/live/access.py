"""Live or replay, per request (PRD §8.6, F7).

A request is **live** (real browser runs, model calls, changes to the shared memory) only if
the server runs in live mode, today's model budget is not spent, and the visitor sent the
demo access code. Everyone else gets **replay**: approving a card plays a recorded golden run,
and anything that would change what every visitor sees is refused with `live_mode_locked`.

The web app sends the code as an `X-Demo-Code` header (it is on another domain, so a
cookie would need cross-site credentials). While the code is unset or still the default
`change-me` (local development), every request is live.
"""

import hmac
from dataclasses import dataclass
from typing import Literal

from fastapi import Request

from backroom_api.config import Settings
from backroom_api.routes.errors import ApiProblem

DEFAULT_CODES = {"", "change-me"}
Mode = Literal["live", "replay"]


@dataclass(frozen=True)
class Access:
    mode: Mode
    reason: str  # shown to the visitor: why this is (or isn't) live


def access_for(request: Request) -> Access:
    settings: Settings = request.app.state.settings
    if settings.demo_mode == "replay":
        return Access("replay", "This demo is serving recorded runs.")
    ledger = getattr(request.app.state, "ledger", None)  # None without a model key
    if ledger is not None and ledger.spent_today() >= settings.llm_daily_budget_usd:
        return Access("replay", "Today's model budget is spent, so recorded runs are served.")
    if settings.demo_access_code in DEFAULT_CODES:
        return Access("live", "Local development: live mode is open.")
    code = request.headers.get("X-Demo-Code", "")
    if code and hmac.compare_digest(code.encode(), settings.demo_access_code.encode()):
        return Access("live", "Live: the agent works on the real portals.")
    return Access("replay", "Recorded runs. Live mode needs the demo access code.")


def require_live(request: Request) -> None:
    """For routes that change what every visitor sees (reject, regenerate, chaos, undo)."""
    access = access_for(request)
    if access.mode != "live":
        raise ApiProblem(403, "live_mode_locked", access.reason)
