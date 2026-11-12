"""Server-side rendering shared by every portal.

Templates never hard-code a visible control label: they call `t("add_to_cart")`, which
resolves the label for the portal's current chaos variants (contract.Label). Test ids
come from `tid("add_to_cart", row)` and never vary.
"""

from functools import partial
from pathlib import Path
from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from backroom_portals import chaos
from backroom_portals.contract import (
    GRAINLINE_LABELS,
    INTERSTITIAL_LABELS,
    TILLDESK_LABELS,
    Label,
    PortalName,
    testid,
)

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

_LABELS: dict[PortalName, dict[str, Label]] = {
    "grainline": GRAINLINE_LABELS,
    "tilldesk": TILLDESK_LABELS,
    "localboard": {},
}


class ChaosSeeds:
    """The current chaos seed per portal (default 0). L2 adds the admin endpoint."""

    def __init__(self) -> None:
        self.seeds: dict[PortalName, int] = {}

    def seed(self, portal: PortalName) -> int:
        return self.seeds.get(portal, 0)

    def variants(self, portal: PortalName) -> dict[str, str]:
        return chaos.pick_variants(portal, self.seed(portal))


def label(portal: PortalName, key: str, variants: dict[str, str]) -> str:
    entry = _LABELS[portal].get(key) or INTERSTITIAL_LABELS[key]
    return getattr(entry, variants["language"])


def page(request: Request, portal: PortalName, name: str, **context: Any) -> HTMLResponse:
    seeds: ChaosSeeds = request.app.state.chaos
    variants = seeds.variants(portal)
    return templates.TemplateResponse(
        request,
        name,
        {
            "portal": portal,
            "variants": variants,
            "t": partial(label, portal, variants=variants),
            "tid": partial(testid, portal),
            **context,
        },
    )
