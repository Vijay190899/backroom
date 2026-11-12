"""L2: the chaos engine renders deterministically and every variant really changes the DOM."""

import hashlib
import re
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from backroom_portals import chaos, rendering
from backroom_portals.contract import ADMIN_TOKEN_HEADER

from .test_grainline import ADMIN, SECRET, login, make_settings

PAGES = (
    "/grainline/",
    "/grainline/orders",
    "/grainline/catalog",
    "/grainline/catalog?q=oat",
    "/grainline/cart",
    "/grainline/checkout",
    "/grainline/orders/GW-10481",
    "/grainline/invoices",
)


def fresh_client(seed: int) -> TestClient:
    from backroom_portals.main import create_app

    client = TestClient(create_app(make_settings()))
    client.post("/_admin/chaos", json={"portal": "grainline", "seed": seed}, headers=ADMIN)
    return client


def signed_in(seed: int) -> TestClient:
    client = fresh_client(seed)
    login(client)
    client.post("/grainline/cart/add", data={"sku": "OAT-1L", "qty": "24"})
    return client


def skill_path_pages(seed: int) -> list[tuple[str, str]]:
    """(path, html) for every page a skill touches at this seed, login and TOTP included."""
    from backroom_portals import totp

    client = fresh_client(seed)
    out = [("/grainline/login", client.get("/grainline/login").text)]
    client.post("/grainline/login", data={"email": "lena@haferundbohne.example", "password": "pw"})
    out.append(("/grainline/login/totp", client.get("/grainline/login/totp").text))
    client.post("/grainline/login/totp", data={"code": totp.now_code(SECRET)})
    client.post("/grainline/cart/add", data={"sku": "OAT-1L", "qty": "24"})
    out += [(path, client.get(path).text) for path in PAGES]
    return out


def dom_hash(seed: int) -> str:
    """Hash of every page a skill touches, rendered at this seed."""
    digest = hashlib.sha256()
    for _, html in skill_path_pages(seed):
        digest.update(html.encode())
    return digest.hexdigest()


def test_same_seed_gives_the_same_dom() -> None:
    for seed in (0, 7, 13):
        assert dom_hash(seed) == dom_hash(seed), seed


def test_different_seeds_give_different_doms() -> None:
    hashes = [dom_hash(seed) for seed in range(20)]
    assert len(set(hashes)) == 20


# --- every variant of every family changes the DOM as specified ---------------------------


@pytest.fixture
def forced(monkeypatch: pytest.MonkeyPatch) -> Iterator[dict[str, str]]:
    """Render with CANONICAL plus whatever the test puts in this dict."""
    overrides: dict[str, str] = {}
    monkeypatch.setattr(rendering.chaos, "pick_variants", lambda p, s: chaos.CANONICAL | overrides)
    yield overrides


def catalog_html(overrides: dict[str, str], forced: dict[str, str], q: str = "oat") -> str:
    forced.update(overrides)
    client = fresh_client(0)
    login(client)
    return client.get("/grainline/catalog", params={"q": q}).text


# One marker per non-canonical variant: text that appears only when that variant is on.
# section_order is structural and has its own test below.
MARKERS: dict[tuple[str, str], str] = {
    ("language", "en_alt"): ">Add to basket<",
    ("language", "de"): ">In den Warenkorb<",
    ("nav_position", "topbar"): '<nav class="top"',
    ("nav_position", "hamburger"): "<summary>Open menu</summary>",
    ("wrapper_depth", "1"): '<div class="w"><label',
    ("wrapper_depth", "3"): '<div class="w"><div class="w"><div class="w">',
    ("id_class_salt", "salted"): 'class="btn-',
    ("interstitial", "cookie_banner"): 'data-testid="chaos-cookie-banner"',
    ("interstitial", "whats_new_modal"): ">What's new</h2>",
    ("interstitial", "survey"): ">No thanks</button>",
    ("delayed_render", "300"): 'hidden data-reveal="300"',
    ("delayed_render", "800"): 'hidden data-reveal="800"',
    ("delayed_render", "1500"): 'hidden data-reveal="1500"',
    ("control_kind", "link"): 'data-submit data-testid="gl-add-to-cart-OAT-1L"',
    ("list_layout", "cards"): '<ul class="cards" data-testid="gl-catalog"',
}


def test_every_non_canonical_variant_has_a_marker() -> None:
    expected = {
        (family, variant)
        for family, variants in chaos.CATALOG.items()
        if family != "section_order"
        for variant in variants[1:]
    }
    assert set(MARKERS) == expected


@pytest.mark.parametrize(("family", "variant"), sorted(MARKERS))
def test_variant_changes_the_dom(forced: dict[str, str], family: str, variant: str) -> None:
    marker = MARKERS[(family, variant)]
    canonical = catalog_html({}, forced)
    html = catalog_html({family: variant}, forced)
    assert marker in html and marker not in canonical


def test_variants_apply_beyond_the_catalog(forced: dict[str, str]) -> None:
    forced.update({"list_layout": "cards", "control_kind": "link"})
    client = fresh_client(0)
    login_page = client.get("/grainline/login").text
    # The link variant keeps a hidden real submit button, so Enter still submits.
    assert 'data-submit data-testid="gl-sign-in"' in login_page
    assert '<button type="submit" tabindex="-1" aria-hidden="true"' in login_page
    login(client)
    assert '<ul class="cards" data-testid="gl-invoices"' in client.get("/grainline/invoices").text


@pytest.mark.parametrize("order", ["reversed", "shuffled"])
def test_section_order_moves_sections(forced: dict[str, str], order: str) -> None:
    def positions(html: str) -> list[int]:
        return [
            html.index(f'data-testid="gl-{k}"') for k in ("search-form", "catalog", "pagination")
        ]

    canonical = positions(catalog_html({}, forced, q=""))
    moved = positions(catalog_html({"section_order": order}, forced, q=""))
    assert canonical == sorted(canonical) and moved != sorted(moved)


def test_dismissed_interstitial_stays_away(forced: dict[str, str]) -> None:
    forced["interstitial"] = "cookie_banner"
    client = fresh_client(0)
    login(client)
    assert "chaos-cookie-banner" in client.get("/grainline/catalog").text
    client.cookies.set("grainline_dismissed_0_cookie_banner", "1")
    assert "chaos-cookie-banner" not in client.get("/grainline/catalog").text


# --- what must hold at every seed ----------------------------------------------------------


@pytest.mark.parametrize("seed", range(20))
def test_every_seed_keeps_labels_ids_and_test_ids_sound(seed: int) -> None:
    client = signed_in(seed)
    for path, html in skill_path_pages(seed):
        ids = re.findall(r'\sid="([^"]+)"', html)
        assert len(ids) == len(set(ids)), (seed, path, "duplicate id")
        for target in re.findall(r'<label for="([^"]+)"', html):
            assert target in ids, (seed, path, target)
    catalog = client.get("/grainline/catalog", params={"q": "oat"}).text
    for testid in ("gl-add-to-cart-OAT-1L", "gl-quantity-OAT-1L", "gl-nav-cart", "gl-sign-out"):
        assert f'data-testid="{testid}"' in catalog, (seed, testid)


@pytest.mark.parametrize("seed", [3, 7, 11])
def test_reorder_still_works_under_chaos(seed: int) -> None:
    client = signed_in(seed)
    resp = client.post("/grainline/checkout", data={"delivery_date": "2026-11-16"})
    assert resp.url.path == "/grainline/orders/GW-10482"


def test_demo_seed_7_page() -> None:
    html = signed_in(7).get("/grainline/catalog", params={"q": "oat"}).text
    assert 'lang="de"' in html and ">In den Warenkorb<" in html
    assert '<nav class="top"' in html
    assert 'data-testid="chaos-cookie-banner"' in html and ">Alle akzeptieren<" in html


# --- admin chaos API -------------------------------------------------------------------------


def test_admin_chaos_sets_reads_and_resets_seeds() -> None:
    client = fresh_client(0)
    state = client.post("/_admin/chaos", json={"portal": "grainline", "seed": 7}, headers=ADMIN)
    assert state.json() == {
        "portal": "grainline",
        "seed": 7,
        "variants": chaos.pick_variants("grainline", 7),
    }
    seeds = {s["portal"]: s["seed"] for s in client.get("/_admin/chaos", headers=ADMIN).json()}
    assert seeds == {"grainline": 7, "tilldesk": 0, "localboard": 0}
    client.post("/_admin/reset", headers=ADMIN)
    assert client.get("/_admin/chaos", headers=ADMIN).json()[0]["seed"] == 0


def test_admin_chaos_validates_and_needs_the_token() -> None:
    client = fresh_client(0)
    bad = client.post("/_admin/chaos", json={"portal": "grainline", "seed": -1}, headers=ADMIN)
    assert bad.status_code == 422
    assert client.post("/_admin/chaos", json={"portal": "grainline", "seed": 1}).status_code == 401
    wrong = {ADMIN_TOKEN_HEADER.encode(): "w\u00f6rong".encode()}  # non-ASCII must not 500
    assert client.get("/_admin/chaos", headers=wrong).status_code == 401
