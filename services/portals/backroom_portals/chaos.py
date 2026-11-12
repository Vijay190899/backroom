"""Chaos variant catalog (L0 contract; the renderer that applies it is L2).

Each portal has one current seed (default 0). A seed picks one variant per family:
seed 0 is the canonical design, seed 7 is the pinned demo seed, and every other seed
draws from a RNG keyed on (portal, seed). Same (portal, seed) => same variants => same
DOM; that is what the DOM-hash tests prove.
"""

import random

from backroom_portals.contract import PortalName

# Family -> variants. The first variant of each family is canonical.
CATALOG: dict[str, tuple[str, ...]] = {
    # Visible labels: canonical English, English synonym, German (contract.Label).
    "language": ("en", "en_alt", "de"),
    # Where the main navigation lives.
    "nav_position": ("sidebar", "topbar", "hamburger"),
    # Order of the page's main sections (header blocks, filters, results).
    "section_order": ("canonical", "reversed", "shuffled"),
    # Extra wrapper <div>s around interactive elements.
    "wrapper_depth": ("0", "1", "3"),
    # Random suffixes on element ids and CSS classes (test ids never change).
    "id_class_salt": ("none", "salted"),
    # A layer that must be dismissed before the page can be used.
    "interstitial": ("none", "cookie_banner", "whats_new_modal", "survey"),
    # Skeleton first, real content after a delay.
    "delayed_render": ("0", "300", "800", "1500"),
    # Primary actions rendered as <button> or as a styled <a href="#"> that submits via JS.
    "control_kind": ("button", "link"),
    # Product and menu lists as a table or as cards.
    "list_layout": ("table", "cards"),
}
FAMILIES: tuple[str, ...] = tuple(CATALOG)
CANONICAL: dict[str, str] = {family: variants[0] for family, variants in CATALOG.items()}

DEMO_SEED = 7
# The demo seed changes exactly these, so the demo heal is predictable (DEMO_SCRIPT 1:40):
# German labels, moved navigation and a cookie modal.
_PINNED: dict[int, dict[str, str]] = {
    0: {},
    DEMO_SEED: {"language": "de", "nav_position": "topbar", "interstitial": "cookie_banner"},
}


def pick_variants(portal: PortalName, seed: int) -> dict[str, str]:
    """The variant chosen for each family, for this portal at this seed."""
    if seed < 0:
        raise ValueError("seed must be >= 0")
    if seed in _PINNED:
        return CANONICAL | _PINNED[seed]
    rng = random.Random(f"{portal}:{seed}")
    variants = {family: rng.choice(options) for family, options in CATALOG.items()}
    if variants == CANONICAL:
        # A chaos seed must change something; force a visible change.
        variants["language"] = "de"
    return variants
