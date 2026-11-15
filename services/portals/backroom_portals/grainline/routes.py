"""Grainline Wholesale: login + TOTP, catalog search, cart, checkout, orders, invoices.

Routes follow contract.GRAINLINE_ROUTES. Forms post and redirect with 303. Bad input
never answers with a raw 4xx: it redirects back with `?error=` and the page shows it.
"""

import hmac
from datetime import date
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from backroom_portals import totp
from backroom_portals.config import Settings
from backroom_portals.grainline.catalog import BY_SKU, PRODUCTS, price_on
from backroom_portals.grainline.pdf import invoice_pdf
from backroom_portals.grainline.store import GrainlineStore
from backroom_portals.rendering import page as render

router = APIRouter(prefix="/grainline")
COOKIE = "gl_session"
PAGE_SIZE = 6


def _store(request: Request) -> GrainlineStore:
    return request.app.state.grainline


def _settings(request: Request) -> Settings:
    return request.app.state.settings


def _redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url, status_code=303)


def _authed(request: Request) -> bool:
    session = _store(request).session(request.cookies.get(COOKIE))
    return session is not None and session.stage == "authed"


def _login_required() -> RedirectResponse:
    return _redirect("/grainline/login")


def _same(a: str, b: str) -> bool:
    """Constant-time compare that also accepts non-ASCII input."""
    return hmac.compare_digest(a.encode(), b.encode())


def _int(value: str, default: int) -> int | None:
    """Numbers arrive as text; None means "not a number" (shown as an error, not a 422)."""
    value = value.strip()
    if not value:
        return default
    digits = value.removeprefix("-")
    return int(value) if digits.isascii() and digits.isdigit() else None


# --- login + TOTP --------------------------------------------------------------------------


@router.get("/login", response_class=HTMLResponse)
def login(request: Request, error: str | None = None) -> Response:
    return render(request, "grainline", "grainline/login.html", error=error)


@router.post("/login")
def login_submit(
    request: Request, email: Annotated[str, Form()], password: Annotated[str, Form()]
) -> Response:
    settings = _settings(request)
    ok_user = _same(email.strip().lower(), settings.grainline_user.lower())
    ok_pass = _same(password, settings.grainline_password)
    if not (ok_user and ok_pass):
        return _redirect("/grainline/login?error=credentials")
    token = _store(request).new_session(replaces=request.cookies.get(COOKIE))
    response = _redirect("/grainline/login/totp")
    response.set_cookie(COOKIE, token, httponly=True, samesite="lax")
    return response


@router.get("/login/totp", response_class=HTMLResponse)
def totp_page(request: Request, error: str | None = None) -> Response:
    if _store(request).session(request.cookies.get(COOKIE)) is None:
        return _login_required()
    return render(request, "grainline", "grainline/totp.html", error=error)


@router.post("/login/totp")
def totp_submit(request: Request, code: Annotated[str, Form()]) -> Response:
    session = _store(request).session(request.cookies.get(COOKIE))
    if session is None:
        return _login_required()
    if not totp.verify(_settings(request).totp_secret, code):
        return _redirect("/grainline/login/totp?error=code")
    session.stage = "authed"
    return _redirect("/grainline/")


@router.post("/logout")
def logout(request: Request) -> Response:
    _store(request).end_session(request.cookies.get(COOKIE))
    response = _redirect("/grainline/login")
    response.delete_cookie(COOKIE)
    return response


# --- dashboard and catalog -----------------------------------------------------------------


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request) -> Response:
    if not _authed(request):
        return _login_required()
    recent = list(reversed(_store(request).orders))[:3]
    return render(request, "grainline", "grainline/dashboard.html", recent=recent)


@router.get("/catalog", response_class=HTMLResponse)
def catalog(request: Request, q: str = "", page: str = "1") -> Response:
    if not _authed(request):
        return _login_required()
    needle = q.strip().lower()
    matches = [p for p in PRODUCTS if needle in p.sku.lower() or needle in p.name.lower()]
    pages = max(1, -(-len(matches) // PAGE_SIZE))
    page_no = min(max(1, _int(page, 1) or 1), pages)
    store = _store(request)
    rows = [
        (p, price_on(p.sku, store.today, store.today))
        for p in matches[(page_no - 1) * PAGE_SIZE : page_no * PAGE_SIZE]
    ]
    return render(
        request,
        "grainline",
        "grainline/catalog.html",
        q=q,
        rows=rows,
        page_no=page_no,
        pages=pages,
        total=len(matches),
    )


# --- cart and checkout ----------------------------------------------------------------------


@router.get("/cart", response_class=HTMLResponse)
def cart(request: Request, added: str = "", error: str | None = None) -> Response:
    if not _authed(request):
        return _login_required()
    lines = _store(request).cart_lines()
    total = round(sum(line.qty * line.unit_price_eur for line in lines), 2)
    return render(
        request,
        "grainline",
        "grainline/cart.html",
        lines=lines,
        total=total,
        products=BY_SKU,
        added=BY_SKU.get(added),
        error=error,
    )


@router.post("/cart/add")
def cart_add(
    request: Request, sku: Annotated[str, Form()], qty: Annotated[str, Form()] = "1"
) -> Response:
    if not _authed(request):
        return _login_required()
    n = _int(qty, 1)
    if n is None or n < 1 or sku not in BY_SKU:
        return _redirect("/grainline/cart?error=quantity")
    _store(request).set_cart_qty(sku, n, add=True)
    return _redirect(f"/grainline/cart?added={quote(sku)}")


@router.post("/cart/update")
def cart_update(
    request: Request, sku: Annotated[str, Form()], qty: Annotated[str, Form()] = "0"
) -> Response:
    if not _authed(request):
        return _login_required()
    n = _int(qty, 0)
    if n is None or n < 0 or sku not in BY_SKU:
        return _redirect("/grainline/cart?error=quantity")
    _store(request).set_cart_qty(sku, n, add=False)
    return _redirect("/grainline/cart")


@router.get("/checkout", response_class=HTMLResponse)
def checkout(request: Request, error: str | None = None) -> Response:
    if not _authed(request):
        return _login_required()
    store = _store(request)
    lines = store.cart_lines()
    total = round(sum(line.qty * line.unit_price_eur for line in lines), 2)
    return render(
        request,
        "grainline",
        "grainline/checkout.html",
        lines=lines,
        total=total,
        products=BY_SKU,
        options=store.delivery_options(),
        error=error,
    )


@router.post("/checkout")
def checkout_submit(request: Request, delivery_date: Annotated[str, Form()] = "") -> Response:
    if not _authed(request):
        return _login_required()
    store = _store(request)
    if not store.cart:
        return _redirect("/grainline/checkout?error=empty")
    try:
        order = store.place_order(date.fromisoformat(delivery_date.strip()))
    except ValueError as exc:
        reason = "empty" if "empty" in str(exc) else "date"
        return _redirect(f"/grainline/checkout?error={reason}")
    return _redirect(f"/grainline/orders/{order.id}?placed=1")


# --- orders and invoices ---------------------------------------------------------------------


@router.get("/orders", response_class=HTMLResponse)
def orders(request: Request) -> Response:
    if not _authed(request):
        return _login_required()
    store = _store(request)
    return render(
        request,
        "grainline",
        "grainline/orders.html",
        orders=list(reversed(store.orders)),
        invoices=store.invoices,
    )


@router.get("/orders/{order_id}", response_class=HTMLResponse)
def order(
    request: Request,
    order_id: str,
    placed: str = "",
    cancelled: str = "",
    error: str | None = None,
) -> Response:
    if not _authed(request):
        return _login_required()
    store = _store(request)
    found = store.order(order_id)
    if found is None:
        raise HTTPException(404, "order not found")
    return render(
        request,
        "grainline",
        "grainline/order.html",
        order=found,
        products=BY_SKU,
        placed=placed == "1",
        cancelled=cancelled == "1",
        can_cancel=store.can_cancel(found),
        error=error,
    )


@router.post("/orders/{order_id}/cancel")
def order_cancel(request: Request, order_id: str) -> Response:
    if not _authed(request):
        return _login_required()
    try:
        _store(request).cancel_order(order_id)
    except KeyError as exc:
        raise HTTPException(404, "order not found") from exc
    except ValueError:
        return _redirect(f"/grainline/orders/{order_id}?error=cancel")
    return _redirect(f"/grainline/orders/{order_id}?cancelled=1")


@router.get("/invoices", response_class=HTMLResponse)
def invoices(request: Request) -> Response:
    if not _authed(request):
        return _login_required()
    listed = sorted(_store(request).invoices.values(), key=lambda i: i.id, reverse=True)
    return render(request, "grainline", "grainline/invoices.html", invoices=listed)


@router.get("/invoices/{invoice_id}.pdf")
def invoice_download(request: Request, invoice_id: str) -> Response:
    if not _authed(request):
        return _login_required()
    invoice = _store(request).invoices.get(invoice_id)
    if invoice is None:
        raise HTTPException(404, "invoice not found")
    return Response(
        invoice_pdf(invoice),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{invoice_id}.pdf"'},
    )
