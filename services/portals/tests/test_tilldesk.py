"""L3: TillDesk (login, menu list, edit price, publish), with chaos applied."""

import hashlib
import re

import pytest
from fastapi.testclient import TestClient

from backroom_portals.contract import TILLDESK_ITEM_IDS, TillDeskState
from backroom_portals.main import create_app
from backroom_portals.tilldesk.store import parse_price

from .test_grainline import ADMIN, make_settings


def fresh(seed: int = 0) -> TestClient:
    client = TestClient(create_app(make_settings()))
    client.post("/_admin/chaos", json={"portal": "tilldesk", "seed": seed}, headers=ADMIN)
    return client


def login(client: TestClient) -> None:
    resp = client.post("/tilldesk/login", data={"username": "lena", "password": "change-me"})
    assert resp.url.path == "/tilldesk/menu"


def state(client: TestClient) -> TillDeskState:
    return TillDeskState.model_validate(client.get("/_admin/state/tilldesk", headers=ADMIN).json())


def change_price(client: TestClient, item_id: str, price: str) -> None:
    client.post(f"/tilldesk/menu/{item_id}", data={"price_eur": price})
    client.post("/tilldesk/menu/publish")


# --- login -------------------------------------------------------------------------------


def test_pages_need_a_login() -> None:
    client = fresh()
    for path in ("/tilldesk/menu", "/tilldesk/menu/franzbroetchen/edit", "/tilldesk/"):
        assert client.get(path).url.path == "/tilldesk/login", path
    assert client.post("/tilldesk/menu/publish").url.path == "/tilldesk/login"


@pytest.mark.parametrize(("user", "password"), [("lena", "nope"), ("léna", "change-me")])
def test_wrong_credentials_show_an_error(user: str, password: str) -> None:
    client = fresh()
    resp = client.post("/tilldesk/login", data={"username": user, "password": password})
    assert resp.status_code == 200 and 'data-testid="td-login-error"' in resp.text


def test_logout_ends_the_session() -> None:
    client = fresh()
    login(client)
    client.post("/tilldesk/logout")
    assert client.get("/tilldesk/menu").url.path == "/tilldesk/login"


# --- menu, edit, publish -------------------------------------------------------------------


def test_menu_lists_every_item_at_its_published_price() -> None:
    client = fresh()
    login(client)
    html = client.get("/tilldesk/menu").text
    for item_id in TILLDESK_ITEM_IDS:
        assert f'data-testid="td-row-{item_id}"' in html
        assert f'data-testid="td-edit-{item_id}"' in html
    assert 'aria-label="Edit Franzbrötchen"' in html
    assert re.search(r'td-price-franzbroetchen">€3.20<', html)
    assert 'data-testid="td-all-live"' in html


def test_change_price_drafts_then_publishes() -> None:
    client = fresh()
    login(client)
    edit = client.get("/tilldesk/menu/franzbroetchen/edit").text
    assert 'value="3.20"' in edit and ">Save</button>" in edit

    resp = client.post("/tilldesk/menu/franzbroetchen", data={"price_eur": "3.60"})
    assert resp.url.path == "/tilldesk/menu"
    assert 'data-testid="td-saved-notice"' in resp.text
    assert 'data-testid="td-draft-franzbroetchen"' in resp.text
    item = state(client).items["franzbroetchen"]
    assert (item.price_eur, item.published_price_eur) == (3.6, 3.2)  # not on the till yet

    resp = client.post("/tilldesk/menu/publish")
    assert 'data-testid="td-published-notice"' in resp.text
    s = state(client)
    assert s.items["franzbroetchen"].published_price_eur == 3.6
    assert s.last_published_at is not None
    assert 'data-testid="td-all-live"' in resp.text


def test_undo_restores_the_old_price() -> None:
    client = fresh()
    login(client)
    change_price(client, "franzbroetchen", "3.60")
    change_price(client, "franzbroetchen", "3.20")
    assert state(client).items["franzbroetchen"].published_price_eur == 3.2


def test_postcondition_path_is_addressable() -> None:
    client = fresh()
    login(client)
    change_price(client, "franzbroetchen", "3,45")
    raw = client.get("/_admin/state/tilldesk", headers=ADMIN).json()
    assert raw["items"]["franzbroetchen"]["published_price_eur"] == 3.45


@pytest.mark.parametrize("bad", ["abc", "0", "100", "3.999", "-1", "", "\uff13.60", "3.60.1"])
def test_bad_prices_show_an_error_and_change_nothing(bad: str) -> None:
    client = fresh()
    login(client)
    resp = client.post("/tilldesk/menu/franzbroetchen", data={"price_eur": bad})
    assert resp.status_code == 200 and 'data-testid="td-price-error"' in resp.text
    assert state(client).items["franzbroetchen"].price_eur == 3.2


@pytest.mark.parametrize(
    ("text", "price"), [("3.60", 3.6), ("3,60", 3.6), ("3.6", 3.6), ("3", 3.0), ("€ 3.45", 3.45)]
)
def test_price_parsing(text: str, price: float) -> None:
    assert parse_price(text) == price


def test_unknown_item_is_404() -> None:
    client = fresh()
    login(client)
    assert client.get("/tilldesk/menu/nope/edit").status_code == 404
    assert client.post("/tilldesk/menu/nope", data={"price_eur": "1"}).status_code == 404


def test_reset_restores_the_menu() -> None:
    client = fresh()
    login(client)
    change_price(client, "espresso", "2.80")
    client.post("/_admin/reset", headers=ADMIN)
    assert state(client).items["espresso"].published_price_eur == 2.4
    assert client.get("/tilldesk/menu").url.path == "/tilldesk/login"


# --- chaos ------------------------------------------------------------------------------------


def pages(seed: int) -> list[str]:
    client = fresh(seed)
    out = [client.get("/tilldesk/login").text]
    login(client)
    client.post("/tilldesk/menu/franzbroetchen", data={"price_eur": "3.60"})
    out += [client.get(p).text for p in ("/tilldesk/menu", "/tilldesk/menu/franzbroetchen/edit")]
    return out


def dom_hash(seed: int) -> str:
    return hashlib.sha256("".join(pages(seed)).encode()).hexdigest()


def test_same_seed_same_dom_and_seeds_differ() -> None:
    assert dom_hash(7) == dom_hash(7)
    assert len({dom_hash(seed) for seed in range(20)}) == 20


@pytest.mark.parametrize("seed", range(20))
def test_every_seed_keeps_labels_ids_and_test_ids_sound(seed: int) -> None:
    for html in pages(seed):
        ids = re.findall(r'\sid="([^"]+)"', html)
        assert len(ids) == len(set(ids)), seed
        for target in re.findall(r'<label for="([^"]+)"', html):
            assert target in ids, (seed, target)
    menu = pages(seed)[1]
    for testid in ("td-edit-franzbroetchen", "td-publish-menu", "td-nav-menu", "td-sign-out"):
        assert f'data-testid="{testid}"' in menu, (seed, testid)


def test_demo_seed_7_is_german_with_moved_nav_and_cookie_banner() -> None:
    login_page, menu, edit = pages(7)
    assert ">Anmelden<" in login_page and 'lang="de"' in menu
    assert '<nav class="top"' in menu and 'data-testid="chaos-cookie-banner"' in menu
    assert ">Speisekarte veröffentlichen<" in menu and ">Speichern<" in edit


@pytest.mark.parametrize("seed", [3, 7, 11])
def test_change_price_still_works_under_chaos(seed: int) -> None:
    client = fresh(seed)
    login(client)
    change_price(client, "franzbroetchen", "3.45")
    assert state(client).items["franzbroetchen"].published_price_eur == 3.45


# --- audit follow-ups -------------------------------------------------------------------------


def test_publish_is_offered_even_when_the_saved_price_is_already_live() -> None:
    client = fresh()
    login(client)
    resp = client.post("/tilldesk/menu/franzbroetchen", data={"price_eur": "3.20"})
    assert 'data-testid="td-publish-menu"' in resp.text
    assert client.post("/tilldesk/menu/publish").status_code == 200


def test_a_fresh_login_drops_leftover_drafts() -> None:
    client = fresh()
    login(client)
    client.post("/tilldesk/menu/espresso", data={"price_eur": "9.99"})  # saved, never published
    login(client)
    change_price(client, "franzbroetchen", "3.60")
    items = state(client).items
    assert items["espresso"].published_price_eur == 2.4 and items["espresso"].price_eur == 2.4
    assert items["franzbroetchen"].published_price_eur == 3.6


def test_edit_links_have_translated_row_names() -> None:
    menu = pages(7)[1]
    assert 'aria-label="Bearbeiten Franzbrötchen"' in menu


def test_saving_needs_a_login_and_reset_clears_the_publish_time() -> None:
    client = fresh()
    assert client.post("/tilldesk/menu/espresso", data={"price_eur": "2"}).url.path == (
        "/tilldesk/login"
    )
    login(client)
    change_price(client, "espresso", "2.50")
    assert state(client).last_published_at is not None
    client.post("/_admin/reset", headers=ADMIN)
    assert state(client).last_published_at is None


def test_routes_and_menu_ids_match_the_contract() -> None:
    from backroom_portals.contract import TILLDESK_ROUTES
    from backroom_portals.tilldesk.routes import router
    from backroom_portals.tilldesk.store import MENU

    served: set[tuple[str, str]] = set()
    for route in router.routes:
        path: str = getattr(route, "path", "")
        methods: set[str] = getattr(route, "methods", None) or set()
        served |= {(method, path) for method in methods}
    assert served == set(TILLDESK_ROUTES.values())
    assert tuple(item_id for item_id, _, _ in MENU) == TILLDESK_ITEM_IDS


def test_suffix_euro_prices_parse() -> None:
    assert parse_price("3,60 €") == 3.6
