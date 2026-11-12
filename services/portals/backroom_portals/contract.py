"""Portal contract (L0): routes, visible labels, test ids and the admin API.

One FastAPI app serves every portal under its own path prefix (`/grainline`,
`/tilldesk`, `/localboard`), so a run's allowlist is origin + prefix.

Labels are what the browser agent and the compiled skills see, so chaos varies them
(`en` canonical, `en_alt` synonym, `de` German). Test ids (`data-testid`) never vary;
they exist for our own tests and postcondition checks, and the agent never sees or
uses them (they are not in the ARIA snapshot).
"""

from datetime import date
from typing import Literal, NamedTuple

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

PortalName = Literal["grainline", "tilldesk", "localboard"]
PORTALS: tuple[PortalName, ...] = ("grainline", "tilldesk", "localboard")
ADMIN_TOKEN_HEADER = "X-Admin-Token"


class Label(NamedTuple):
    en: str
    en_alt: str
    de: str


# --- Routes ------------------------------------------------------------------------
# Method + path. Form posts redirect (303) to the next page, like a classic SaaS app.

GRAINLINE_ROUTES: dict[str, tuple[str, str]] = {
    "login": ("GET", "/grainline/login"),
    "login_submit": ("POST", "/grainline/login"),
    "totp": ("GET", "/grainline/login/totp"),
    "totp_submit": ("POST", "/grainline/login/totp"),
    "dashboard": ("GET", "/grainline/"),
    "catalog": ("GET", "/grainline/catalog"),  # ?q=&page=
    "cart": ("GET", "/grainline/cart"),
    "cart_add": ("POST", "/grainline/cart/add"),  # form: sku, qty
    "cart_update": ("POST", "/grainline/cart/update"),  # form: sku, qty (0 removes)
    "checkout": ("GET", "/grainline/checkout"),
    "checkout_submit": ("POST", "/grainline/checkout"),  # form: delivery_date
    "orders": ("GET", "/grainline/orders"),
    "order": ("GET", "/grainline/orders/{order_id}"),
    "order_cancel": ("POST", "/grainline/orders/{order_id}/cancel"),  # the Undo
    "invoices": ("GET", "/grainline/invoices"),
    "invoice_pdf": ("GET", "/grainline/invoices/{invoice_id}.pdf"),
    "logout": ("POST", "/grainline/logout"),
}

TILLDESK_ROUTES: dict[str, tuple[str, str]] = {
    "login": ("GET", "/tilldesk/login"),
    "login_submit": ("POST", "/tilldesk/login"),
    "menu": ("GET", "/tilldesk/menu"),
    "item_edit": ("GET", "/tilldesk/menu/{item_id}/edit"),
    "item_save": ("POST", "/tilldesk/menu/{item_id}"),  # form: price_eur
    "publish": ("POST", "/tilldesk/menu/publish"),
    "logout": ("POST", "/tilldesk/logout"),
}

# P1: only if Localboard makes the Thu 19:00 cut.
LOCALBOARD_ROUTES: dict[str, tuple[str, str]] = {
    "login": ("GET", "/localboard/login"),
    "login_submit": ("POST", "/localboard/login"),
    "posts": ("GET", "/localboard/posts"),
    "post_new": ("GET", "/localboard/posts/new"),
    "post_submit": ("POST", "/localboard/posts"),  # form: title, body
}

ADMIN_ROUTES: dict[str, tuple[str, str]] = {
    "chaos_get": ("GET", "/_admin/chaos"),  # all portals' current seed + variants
    "chaos_set": ("POST", "/_admin/chaos"),  # body ChaosRequest -> ChaosState
    "state": ("GET", "/_admin/state/{portal}"),  # GrainlineState | TillDeskState
    "reset": ("POST", "/_admin/reset"),  # wipe orders/carts/edits, seeds back to 0
}

# --- Labels --------------------------------------------------------------------------

GRAINLINE_LABELS: dict[str, Label] = {
    "email": Label("Email", "Email address", "E-Mail"),
    "password": Label("Password", "Your password", "Passwort"),
    "sign_in": Label("Sign in", "Log in", "Anmelden"),
    "totp_code": Label("Authentication code", "6-digit code", "Bestätigungscode"),
    "verify": Label("Verify", "Continue", "Bestätigen"),
    "nav_catalog": Label("Catalog", "Products", "Katalog"),
    "nav_cart": Label("Cart", "Basket", "Warenkorb"),
    "nav_orders": Label("Orders", "Order history", "Bestellungen"),
    "nav_invoices": Label("Invoices", "Billing", "Rechnungen"),
    "search": Label("Search products", "Find products", "Produkte suchen"),
    "search_submit": Label("Search", "Find", "Suchen"),
    "quantity": Label("Quantity", "Qty", "Menge"),
    "add_to_cart": Label("Add to cart", "Add to basket", "In den Warenkorb"),
    "update_qty": Label("Update", "Save", "Aktualisieren"),
    "remove": Label("Remove", "Delete", "Entfernen"),
    "prev_page": Label("Previous", "Back", "Zurück"),
    "next_page": Label("Next", "More", "Weiter"),
    "checkout": Label("Checkout", "Proceed to checkout", "Zur Kasse"),
    "delivery_date": Label("Delivery date", "Deliver on", "Liefertermin"),
    "place_order": Label("Place order", "Confirm order", "Bestellung aufgeben"),
    "cancel_order": Label("Cancel order", "Cancel this order", "Bestellung stornieren"),
    "download_invoice": Label("Download PDF", "Download invoice", "PDF herunterladen"),
    "sign_out": Label("Sign out", "Log out", "Abmelden"),
}

TILLDESK_LABELS: dict[str, Label] = {
    "username": Label("Username", "User name", "Benutzername"),
    "password": Label("Password", "Your password", "Passwort"),
    "log_in": Label("Log in", "Sign in", "Anmelden"),
    "nav_menu": Label("Menu", "Menu items", "Speisekarte"),
    "edit": Label("Edit", "Change", "Bearbeiten"),
    "price": Label("Price (€)", "Sale price (€)", "Preis (€)"),
    "save": Label("Save", "Save changes", "Speichern"),
    "publish_menu": Label("Publish menu", "Go live", "Speisekarte veröffentlichen"),
    "sign_out": Label("Sign out", "Log out", "Abmelden"),
}

# Interstitials (chaos family "interstitial"); shared by every portal.
INTERSTITIAL_LABELS: dict[str, Label] = {
    "accept_cookies": Label("Accept all", "Accept", "Alle akzeptieren"),
    "close": Label("Close", "Dismiss", "Schließen"),
    "survey_skip": Label("No thanks", "Skip", "Nein danke"),
    "open_menu": Label(
        "Open menu", "Show navigation", "Menü öffnen"
    ),  # hamburger nav (nav_position)
}

# --- Test ids ---------------------------------------------------------------------------
# Static ids are "<prefix>-<label key>" with "_" -> "-", e.g. "gl-add-to-cart".
# Per-row ids add the row key: "gl-add-to-cart-OAT-1L", "td-edit-franzbroetchen",
# "gl-order-GW-10482". Interstitials: "chaos-cookie-banner", "chaos-modal".

TESTID_PREFIX: dict[PortalName, str] = {"grainline": "gl", "tilldesk": "td", "localboard": "lb"}


def testid(portal: PortalName, key: str, row: str | None = None) -> str:
    base = f"{TESTID_PREFIX[portal]}-{key.replace('_', '-')}"
    return f"{base}-{row}" if row else base


# --- Catalog keys the other packages rely on ------------------------------------------------
# Prices and history belong to the data pipeline (L4) and Grainline (L1); these ids and
# the demo-story prices are fixed here so skills, detectors and fixtures agree.

GRAINLINE_SKUS: dict[str, str] = {
    "OAT-1L": "Oat milk, barista, 1 L",
    "MILK-1L": "Whole milk, 1 L",
    "BEANS-1KG": "Espresso beans, 1 kg",
    "BUTTER-1KG": "Butter, 1 kg",
    "FLOUR-5KG": "Wheat flour type 550, 5 kg",
    "SUGAR-1KG": "Sugar, 1 kg",
    "CINNAMON-500G": "Cinnamon, ground, 500 g",
    "CUP-12OZ-50": "Paper cups 12 oz, 50 pcs",
}
DEMO_PRICES_EUR = {
    "OAT-1L": 1.59,  # 24 x 1.59 = 38.16 (PRD F2 summary)
    "BUTTER-1KG.before": 7.10,  # invoice before day -9
    "BUTTER-1KG": 8.24,  # +16% from day -9 (DATA.md)
    "franzbroetchen.menu": 3.20,  # TillDesk price before the demo
}
TILLDESK_ITEM_IDS: tuple[str, ...] = (
    "franzbroetchen",
    "croissant",
    "flat-white",
    "oat-latte",
    "cappuccino",
    "espresso",
    "filter-coffee",
    "banana-bread",
)
# Vault keys a skill may reference as {{secret:<key>}}; values come from .env.
SECRET_KEYS: dict[str, str] = {
    "grainline_user": "GRAINLINE_USER",
    "grainline_password": "GRAINLINE_PASSWORD",
    "grainline_totp": "GRAINLINE_TOTP_SECRET",
    "tilldesk_user": "TILLDESK_USER",
    "tilldesk_password": "TILLDESK_PASSWORD",
}
ORDER_ID_PATTERN = r"GW-\d{5}"
INVOICE_ID_PATTERN = r"INV-\d{6}"

# --- Admin API bodies -----------------------------------------------------------------------


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ChaosRequest(_Model):
    portal: PortalName
    seed: int = Field(ge=0, le=999)


class ChaosState(_Model):
    portal: PortalName
    seed: int
    variants: dict[str, str]


class OrderLine(_Model):
    sku: str
    qty: int
    unit_price_eur: float


class Order(_Model):
    id: str
    status: Literal["placed", "cancelled"]
    lines: list[OrderLine]
    total_eur: float
    delivery_date: date
    invoice_id: str | None


class GrainlineState(_Model):
    portal: Literal["grainline"] = "grainline"
    cart: list[OrderLine]
    orders: list[Order]  # newest last, so "orders.last" is the latest


class MenuItem(_Model):
    id: str
    name: str
    price_eur: float  # draft (edited) price
    published_price_eur: float  # what the till charges


class TillDeskState(_Model):
    portal: Literal["tilldesk"] = "tilldesk"
    items: dict[str, MenuItem]  # by item id: "items.franzbroetchen.published_price_eur"
    last_published_at: AwareDatetime | None
