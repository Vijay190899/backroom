import re
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from backroom_portals import totp
from backroom_portals.config import Settings
from backroom_portals.contract import ADMIN_TOKEN_HEADER, GrainlineState
from backroom_portals.contract import testid as make_testid
from backroom_portals.grainline.catalog import PRODUCTS, price_on, seeded_orders
from backroom_portals.main import create_app

TODAY = date(2026, 11, 13)  # a Friday
SECRET = totp.default_secret(44)
ADMIN = {ADMIN_TOKEN_HEADER: "admin-test"}
FULLWIDTH_CODE = "\uff11\uff12\uff13\uff14\uff15\uff16"  # looks like 123456


def make_settings() -> Settings:
    return Settings(
        _env_file=None,  # type: ignore[call-arg]
        grainline_password="pw",
        portals_admin_token="admin-test",
        portals_today=TODAY,
    )


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app(make_settings()))


def login(client: TestClient) -> None:
    resp = client.post(
        "/grainline/login", data={"email": "lena@haferundbohne.example", "password": "pw"}
    )
    assert resp.url.path == "/grainline/login/totp"
    resp = client.post("/grainline/login/totp", data={"code": totp.now_code(SECRET)})
    assert resp.url.path == "/grainline/"


def state(client: TestClient) -> GrainlineState:
    return GrainlineState.model_validate(
        client.get("/_admin/state/grainline", headers=ADMIN).json()
    )


def has_testid(html: str, key: str, row: str | None = None) -> bool:
    return f'data-testid="{make_testid("grainline", key, row)}"' in html


# --- TOTP ---------------------------------------------------------------------------------


def test_totp_matches_the_rfc_6238_vector() -> None:
    secret = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"  # "12345678901234567890"
    assert totp.code_at(secret, 59) == "287082"
    assert totp.verify(secret, "287082", at=59 + 30)  # one step of drift is fine
    assert not totp.verify(secret, "287082", at=59 + 90)


# --- login ----------------------------------------------------------------------------------


def test_pages_redirect_to_login_without_a_session(client: TestClient) -> None:
    for path in ("/grainline/", "/grainline/catalog", "/grainline/cart", "/grainline/orders"):
        assert client.get(path).url.path == "/grainline/login", path
    assert client.get("/grainline/login/totp").url.path == "/grainline/login"


def test_wrong_password_is_rejected(client: TestClient) -> None:
    resp = client.post(
        "/grainline/login", data={"email": "lena@haferundbohne.example", "password": "nope"}
    )
    assert resp.url.path == "/grainline/login"
    assert has_testid(resp.text, "login_error")
    assert client.get("/grainline/").url.path == "/grainline/login"


def test_password_alone_does_not_sign_in(client: TestClient) -> None:
    client.post("/grainline/login", data={"email": "lena@haferundbohne.example", "password": "pw"})
    assert client.get("/grainline/catalog").url.path == "/grainline/login"
    resp = client.post("/grainline/login/totp", data={"code": "000000"})
    assert has_testid(resp.text, "totp_error")


def test_login_with_totp_reaches_the_dashboard_and_logout_ends_it(client: TestClient) -> None:
    login(client)
    assert "Welcome back" in client.get("/grainline/").text
    client.post("/grainline/logout")
    assert client.get("/grainline/").url.path == "/grainline/login"


def test_login_form_has_labelled_controls(client: TestClient) -> None:
    html = client.get("/grainline/login").text
    assert '<label for="email">Email</label>' in html
    assert '<label for="password">Password</label>' in html
    assert has_testid(html, "sign_in") and ">Sign in</button>" in html


# --- catalog ---------------------------------------------------------------------------------


def test_search_finds_oat_milk_at_todays_price(client: TestClient) -> None:
    login(client)
    html = client.get("/grainline/catalog", params={"q": "oat"}).text
    assert has_testid(html, "row", "OAT-1L")
    assert "€1.59 / carton" in html
    assert len(re.findall(r'data-testid="gl-row-', html)) == 1
    assert has_testid(html, "add_to_cart", "OAT-1L") and ">Add to cart</button>" in html


def test_catalog_paginates(client: TestClient) -> None:
    login(client)
    first = client.get("/grainline/catalog").text
    second = client.get("/grainline/catalog", params={"page": 2}).text
    rows = len(re.findall(r'data-testid="gl-row-', first)) + len(
        re.findall(r'data-testid="gl-row-', second)
    )
    assert rows == len(PRODUCTS)
    assert has_testid(first, "next_page") and has_testid(second, "prev_page")


# --- cart, checkout, orders ---------------------------------------------------------------------


def test_reorder_oat_milk_end_to_end(client: TestClient) -> None:
    login(client)
    resp = client.post("/grainline/cart/add", data={"sku": "OAT-1L", "qty": "24"})
    assert resp.url.path == "/grainline/cart"
    assert has_testid(resp.text, "cart_line", "OAT-1L") and "€38.16" in resp.text

    checkout = client.get("/grainline/checkout").text
    options = re.findall(r'<option value="([0-9-]+)"', checkout)
    assert options[0] == (TODAY + timedelta(days=3)).isoformat()  # Friday -> Monday

    resp = client.post("/grainline/checkout", data={"delivery_date": options[0]})
    assert resp.url.path == "/grainline/orders/GW-10482"
    assert "Order GW-10482 placed" in resp.text
    assert has_testid(resp.text, "cancel_order")

    s = state(client)
    assert s.cart == []
    last = s.orders[-1]
    assert (last.id, last.status, last.total_eur) == ("GW-10482", "placed", 38.16)
    assert [(line.sku, line.qty) for line in last.lines] == [("OAT-1L", 24)]


def test_cart_update_and_remove(client: TestClient) -> None:
    login(client)
    client.post("/grainline/cart/add", data={"sku": "OAT-1L", "qty": "2"})
    client.post("/grainline/cart/add", data={"sku": "OAT-1L", "qty": "3"})
    client.post("/grainline/cart/add", data={"sku": "BUTTER-1KG", "qty": "1"})
    assert {line.sku: line.qty for line in state(client).cart} == {"OAT-1L": 5, "BUTTER-1KG": 1}
    client.post("/grainline/cart/update", data={"sku": "OAT-1L", "qty": "10"})
    client.post("/grainline/cart/update", data={"sku": "BUTTER-1KG", "qty": "0"})
    assert {line.sku: line.qty for line in state(client).cart} == {"OAT-1L": 10}


@pytest.mark.parametrize(
    ("sku", "qty"), [("NOPE", "1"), ("OAT-1L", "0"), ("OAT-1L", "abc"), ("OAT-1L", "\uff11\uff12")]
)
def test_bad_cart_input_shows_an_error_not_a_raw_4xx(
    client: TestClient, sku: str, qty: str
) -> None:
    login(client)
    resp = client.post("/grainline/cart/add", data={"sku": sku, "qty": qty})
    assert resp.status_code == 200 and has_testid(resp.text, "cart_error")
    assert state(client).cart == []


def test_checkout_refuses_an_empty_cart_and_unoffered_dates(client: TestClient) -> None:
    login(client)
    resp = client.post("/grainline/checkout", data={"delivery_date": "2026-11-16"})
    assert resp.url.query == b"error=empty" or "error=empty" in str(resp.url)
    client.post("/grainline/cart/add", data={"sku": "OAT-1L", "qty": "1"})
    resp = client.post("/grainline/checkout", data={"delivery_date": "2027-01-01"})
    assert "error=date" in str(resp.url)
    assert state(client).orders[-1].id != "GW-10482"


def test_cancel_is_the_undo_and_only_works_once(client: TestClient) -> None:
    login(client)
    client.post("/grainline/cart/add", data={"sku": "OAT-1L", "qty": "24"})
    client.post("/grainline/checkout", data={"delivery_date": "2026-11-16"})
    resp = client.post("/grainline/orders/GW-10482/cancel")
    assert "Order GW-10482 cancelled" in resp.text
    assert state(client).orders[-1].status == "cancelled"
    again = client.post("/grainline/orders/GW-10482/cancel")
    assert again.status_code == 200 and has_testid(again.text, "cancel_error")


def test_delivered_orders_cannot_be_cancelled(client: TestClient) -> None:
    login(client)
    html = client.get("/grainline/orders/GW-10474").text
    assert "Order GW-10474" in html and not has_testid(html, "cancel_order")
    resp = client.post("/grainline/orders/GW-10474/cancel")
    assert has_testid(resp.text, "cancel_error")
    assert state(client).orders[0].status == "placed"


def test_order_numbers_continue(client: TestClient) -> None:
    login(client)
    for _ in range(2):
        client.post("/grainline/cart/add", data={"sku": "MILK-1L", "qty": "1"})
        client.post("/grainline/checkout", data={"delivery_date": "2026-11-16"})
    assert [o.id for o in state(client).orders[-2:]] == ["GW-10482", "GW-10483"]


# --- seeded history and invoices ---------------------------------------------------------------


def test_seeded_history_is_tue_fri_and_carries_the_butter_rise() -> None:
    history = seeded_orders(TODAY, 44)
    assert history and all(o.order_day.weekday() in (1, 4) for o in history)
    assert history == seeded_orders(TODAY, 44)  # deterministic
    rise_day = TODAY - timedelta(days=9)
    assert price_on("BUTTER-1KG", rise_day - timedelta(days=1), TODAY) == 7.10
    assert price_on("BUTTER-1KG", rise_day, TODAY) == 8.24
    assert price_on("OAT-1L", TODAY - timedelta(days=4), TODAY) == 1.46
    assert price_on("OAT-1L", TODAY - timedelta(days=3), TODAY) == 1.59


def test_seeded_orders_end_just_below_the_demo_order_number(client: TestClient) -> None:
    ids = [o.id for o in state(client).orders]
    assert ids[-1] == "GW-10481"
    butter_prices = {
        line.unit_price_eur
        for o in state(client).orders
        for line in o.lines
        if line.sku == "BUTTER-1KG"
    }
    assert butter_prices == {7.10, 8.24}


def test_invoice_pdf_is_a_valid_deterministic_pdf(client: TestClient) -> None:
    login(client)
    client.post("/grainline/cart/add", data={"sku": "OAT-1L", "qty": "24"})
    client.post("/grainline/checkout", data={"delivery_date": "2026-11-16"})
    invoice_id = state(client).orders[-1].invoice_id
    assert invoice_id is not None
    resp = client.get(f"/grainline/invoices/{invoice_id}.pdf")
    assert resp.headers["content-type"] == "application/pdf"
    pdf = resp.content
    assert pdf.startswith(b"%PDF-1.4") and pdf.rstrip().endswith(b"%%EOF")
    assert b"(Order: GW-10482)" in pdf and b"\x8038.16" in pdf  # cp1252 euro sign
    # Every xref offset points at the start of its object.
    xref_at = int(pdf.rsplit(b"startxref\n", 1)[1].split(b"\n")[0])
    entries = pdf[xref_at:].split(b"\n")[3:9]
    for number, entry in enumerate(entries, start=1):
        offset = int(entry[:10])
        assert pdf[offset:].startswith(f"{number} 0 obj".encode())
    assert client.get(f"/grainline/invoices/{invoice_id}.pdf").content == pdf


def test_invoice_list_links_every_invoice(client: TestClient) -> None:
    login(client)
    html = client.get("/grainline/invoices").text
    ids = re.findall(r'data-testid="gl-invoice-(INV-\d{6})"', html)
    assert ids and all(has_testid(html, "download_invoice", i) for i in ids)
    assert client.get("/grainline/invoices/INV-999999.pdf").status_code == 404


# --- admin and labels -------------------------------------------------------------------


def test_admin_needs_the_token(client: TestClient) -> None:
    assert client.get("/_admin/state/grainline").status_code == 401
    assert (
        client.get("/_admin/state/grainline", headers={ADMIN_TOKEN_HEADER: "x"}).status_code == 401
    )


def test_reset_restores_the_seeded_state(client: TestClient) -> None:
    login(client)
    client.post("/grainline/cart/add", data={"sku": "OAT-1L", "qty": "24"})
    client.post("/grainline/checkout", data={"delivery_date": "2026-11-16"})
    assert client.post("/_admin/reset", headers=ADMIN).status_code == 204
    assert state(client).orders[-1].id == "GW-10481"
    assert client.get("/grainline/").url.path == "/grainline/login"  # sessions are gone


def test_labels_follow_the_chaos_language(client: TestClient) -> None:
    login(client)
    client.app.state.chaos.seeds["grainline"] = 7  # type: ignore[attr-defined]
    html = client.get("/grainline/catalog", params={"q": "oat"}).text
    assert ">In den Warenkorb</button>" in html and 'lang="de"' in html
    assert has_testid(html, "add_to_cart", "OAT-1L")  # test ids never change


# --- audit follow-ups -------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("email", "code"), [("l\u00ebn\u0430@haferundbohne.example", "123456"), ("x@y", FULLWIDTH_CODE)]
)
def test_non_ascii_input_never_crashes(client: TestClient, email: str, code: str) -> None:
    resp = client.post("/grainline/login", data={"email": email, "password": "pw"})
    assert resp.status_code == 200 and has_testid(resp.text, "login_error")
    client.post("/grainline/login", data={"email": "lena@haferundbohne.example", "password": "pw"})
    resp = client.post("/grainline/login/totp", data={"code": code})
    assert resp.status_code == 200 and has_testid(resp.text, "totp_error")
    assert not totp.verify(SECRET, FULLWIDTH_CODE)


def test_seeded_deliveries_are_on_weekdays(client: TestClient) -> None:
    assert all(o.delivery_date.weekday() < 5 for o in state(client).orders)
    ids = [o.order_id for o in seeded_orders(TODAY, 44)]
    invoices = [o.invoice_id for o in seeded_orders(TODAY, 44)]
    assert [o.id for o in state(client).orders] == ids
    assert [o.invoice_id for o in state(client).orders] == invoices


def test_each_login_starts_with_an_empty_cart(client: TestClient) -> None:
    login(client)
    client.post("/grainline/cart/add", data={"sku": "BUTTER-1KG", "qty": "3"})
    login(client)
    assert state(client).cart == []


def test_every_page_renders_for_a_signed_in_user(client: TestClient) -> None:
    login(client)
    pages = {
        "/grainline/": "Recent orders",
        "/grainline/orders": "Order history",
        "/grainline/orders/GW-10481": "Order GW-10481",
        "/grainline/invoices": "Invoices",
        "/grainline/cart": "Your cart is empty",
        "/grainline/checkout": "Your cart is empty",
        "/grainline/catalog?page=abc": "Catalog",
        "/grainline/catalog?page=99": "Page 2 of 2",
    }
    for path, text in pages.items():
        resp = client.get(path)
        assert resp.status_code == 200 and text in resp.text, path
    assert client.get("/grainline/orders/GW-1").status_code == 404


def test_invoice_pdf_shows_vat_per_rate(client: TestClient) -> None:
    login(client)
    client.post("/grainline/cart/add", data={"sku": "OAT-1L", "qty": "24"})  # 7 %
    client.post("/grainline/cart/add", data={"sku": "CUP-12OZ-50", "qty": "2"})  # 19 %
    client.post("/grainline/checkout", data={"delivery_date": "2026-11-16"})
    pdf = client.get(f"/grainline/invoices/{state(client).orders[-1].invoice_id}.pdf").content
    # net 38.16 + 9.80 = 47.96; VAT 2.67 + 1.86; gross 52.49
    for text in (b"Net total: \x8047.96", b"VAT 7%: \x802.67", b"VAT 19%: \x801.86", b"\x8052.49"):
        assert text in pdf, text


def test_totp_cli_prints_a_valid_code() -> None:
    import subprocess
    import sys

    out = subprocess.run(
        [sys.executable, "-m", "backroom_portals.totp"],
        capture_output=True,
        text=True,
        check=True,
        env={"DATA_SEED": "44", "GRAINLINE_TOTP_SECRET": "", "PATH": ""},
    ).stdout
    secret, code = (line.split()[1] for line in out.splitlines()[:2])
    assert secret == SECRET and totp.verify(SECRET, code)
