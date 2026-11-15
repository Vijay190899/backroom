"""Server-side rendering shared by every portal, with the chaos engine applied.

Templates never hard-code what chaos varies. They call into the per-request `Look`:
`t("add_to_cart")` for visible control labels (contract.Label), `look.id()` and
`look.cls()` for ids and classes (salted), `look.arrange()` for section order, and the
macros in `templates/macros.html` for controls, fields, wrappers, nav and interstitials.
Test ids come from `tid(key, row)` and never vary.
"""

import hashlib
import random
from collections.abc import Sequence
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
    """The current chaos seed per portal (default 0), set via POST /_admin/chaos."""

    def __init__(self) -> None:
        self.seeds: dict[PortalName, int] = {}

    def seed(self, portal: PortalName) -> int:
        return self.seeds.get(portal, 0)

    def variants(self, portal: PortalName) -> dict[str, str]:
        return chaos.pick_variants(portal, self.seed(portal))


def label(portal: PortalName, key: str, variants: dict[str, str]) -> str:
    entry = _LABELS[portal].get(key) or INTERSTITIAL_LABELS[key]
    return getattr(entry, variants["language"])


class Look:
    """How this portal looks at its current seed. Pure function of (portal, seed), so
    the same seed always renders the same DOM."""

    def __init__(self, portal: PortalName, seed: int, variants: dict[str, str]) -> None:
        self.portal = portal
        self.seed = seed
        self.variants = variants
        digest = hashlib.sha256(f"{portal}:{seed}".encode()).hexdigest()
        self._salt = digest[:5] if variants["id_class_salt"] == "salted" else ""
        self.depth = int(variants["wrapper_depth"])
        self.delay_ms = int(variants["delayed_render"])
        self.as_link = variants["control_kind"] == "link"
        self.cards = variants["list_layout"] == "cards"
        self.nav = variants["nav_position"]
        self.interstitial = variants["interstitial"]

    def id(self, name: str) -> str:
        return f"{name}-{self._salt}" if self._salt else name

    def cls(self, name: str) -> str:
        return f"{name}-{self._salt}" if self._salt else name

    def arrange(self, page: str, sections: Sequence[Any]) -> list[Any]:
        """The page's sections in this seed's order."""
        order = self.variants["section_order"]
        if order == "reversed":
            return list(reversed(sections))
        if order == "shuffled":
            shuffled = list(sections)
            random.Random(f"{self.portal}:{self.seed}:{page}").shuffle(shuffled)
            if shuffled == list(sections) and len(sections) > 1:
                shuffled = shuffled[1:] + shuffled[:1]  # a shuffle must move something
            return shuffled
        return list(sections)


def page(request: Request, portal: PortalName, name: str, **context: Any) -> HTMLResponse:
    seeds: ChaosSeeds = request.app.state.chaos
    seed = seeds.seed(portal)
    variants = chaos.pick_variants(portal, seed)
    look = Look(portal, seed, variants)
    dismissed = request.cookies.get(f"{portal}_dismissed_{seed}_{look.interstitial}") == "1"
    return templates.TemplateResponse(
        request,
        name,
        {
            "portal": portal,
            "variants": variants,
            "look": look,
            "show_interstitial": look.interstitial != "none" and not dismissed,
            "t": partial(label, portal, variants=variants),
            "tid": partial(testid, portal),
            **context,
        },
    )
