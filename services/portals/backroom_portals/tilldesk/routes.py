"""TillDesk: the café's till back office. Login, menu list, edit price, publish.

Routes follow contract.TILLDESK_ROUTES. Forms post and redirect with 303; bad input
redirects back with `?error=` and the page shows it.
"""

import hmac
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from backroom_portals.config import Settings
from backroom_portals.rendering import page as render
from backroom_portals.tilldesk.store import TillDeskStore, parse_price

router = APIRouter(prefix="/tilldesk")
COOKIE = "td_session"


def _store(request: Request) -> TillDeskStore:
    return request.app.state.tilldesk


def _settings(request: Request) -> Settings:
    return request.app.state.settings


def _redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url, status_code=303)


def _authed(request: Request) -> bool:
    return _store(request).authed(request.cookies.get(COOKIE))


def _same(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode(), b.encode())


@router.get("/", include_in_schema=False)
def home() -> Response:
    return _redirect("/tilldesk/menu")


@router.get("/login", response_class=HTMLResponse)
def login(request: Request, error: str | None = None) -> Response:
    return render(request, "tilldesk", "tilldesk/login.html", error=error)


@router.post("/login")
def login_submit(
    request: Request, username: Annotated[str, Form()], password: Annotated[str, Form()]
) -> Response:
    settings = _settings(request)
    ok_user = _same(username.strip().lower(), settings.tilldesk_user.lower())
    ok_pass = _same(password, settings.tilldesk_password)
    if not (ok_user and ok_pass):
        return _redirect("/tilldesk/login?error=credentials")
    token = _store(request).new_session(replaces=request.cookies.get(COOKIE))
    response = _redirect("/tilldesk/menu")
    response.set_cookie(COOKIE, token, httponly=True, samesite="lax")
    return response


@router.post("/logout")
def logout(request: Request) -> Response:
    _store(request).end_session(request.cookies.get(COOKIE))
    response = _redirect("/tilldesk/login")
    response.delete_cookie(COOKIE)
    return response


@router.get("/menu", response_class=HTMLResponse)
def menu(request: Request, saved: str = "", published: str = "") -> Response:
    if not _authed(request):
        return _redirect("/tilldesk/login")
    store = _store(request)
    return render(
        request,
        "tilldesk",
        "tilldesk/menu.html",
        items=list(store.items.values()),
        saved=store.items.get(saved),
        published=published == "1",
        unpublished=store.has_unpublished(),
    )


@router.get("/menu/{item_id}/edit", response_class=HTMLResponse)
def item_edit(request: Request, item_id: str, error: str | None = None) -> Response:
    if not _authed(request):
        return _redirect("/tilldesk/login")
    item = _store(request).items.get(item_id)
    if item is None:
        raise HTTPException(404, "menu item not found")
    return render(request, "tilldesk", "tilldesk/edit.html", item=item, error=error)


@router.post("/menu/publish")
def publish(request: Request) -> Response:
    if not _authed(request):
        return _redirect("/tilldesk/login")
    _store(request).publish()
    return _redirect("/tilldesk/menu?published=1")


@router.post("/menu/{item_id}")
def item_save(request: Request, item_id: str, price_eur: Annotated[str, Form()] = "") -> Response:
    if not _authed(request):
        return _redirect("/tilldesk/login")
    store = _store(request)
    if item_id not in store.items:
        raise HTTPException(404, "menu item not found")
    price = parse_price(price_eur)
    if price is None:
        return _redirect(f"/tilldesk/menu/{item_id}/edit?error=price")
    store.set_draft(item_id, price)
    return _redirect(f"/tilldesk/menu?saved={item_id}")
