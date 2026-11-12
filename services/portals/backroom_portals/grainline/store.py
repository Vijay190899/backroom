"""Grainline's in-memory state: one merchant account, its sessions, cart and orders.

The portals are a demo fixture, so state lives in memory and `reset()` (also
`POST /_admin/reset`) rebuilds it from the seeded history.
"""

import secrets
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from typing import Literal

from backroom_portals.contract import GrainlineState, Order, OrderLine
from backroom_portals.grainline.catalog import (
    BY_SKU,
    FIRST_INVOICE,
    FIRST_NEW_ORDER,
    next_weekday,
    price_on,
    seeded_orders,
)


@dataclass
class Invoice:
    id: str
    order_id: str
    issued_on: date
    lines: list[OrderLine]

    @property
    def net_eur(self) -> float:
        return round(sum(line.qty * line.unit_price_eur for line in self.lines), 2)

    def vat_eur(self) -> dict[int, float]:
        """VAT amount per rate (7 % food, 19 % other)."""
        out: dict[int, float] = {}
        for line in self.lines:
            rate = BY_SKU[line.sku].vat_pct
            out[rate] = out.get(rate, 0.0) + line.qty * line.unit_price_eur * rate / 100
        return {rate: round(v, 2) for rate, v in sorted(out.items())}

    @property
    def gross_eur(self) -> float:
        return round(self.net_eur + sum(self.vat_eur().values()), 2)


@dataclass
class Session:
    stage: Literal["password_ok", "authed"]


@dataclass
class GrainlineStore:
    today_fn: Callable[[], date]  # read per request, so a dev server survives midnight
    data_seed: int
    sessions: dict[str, Session] = field(default_factory=dict[str, Session])
    cart: dict[str, int] = field(default_factory=dict[str, int])  # sku -> qty, insertion order
    orders: list[Order] = field(default_factory=list[Order])  # oldest first
    invoices: dict[str, Invoice] = field(default_factory=dict[str, Invoice])
    lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self) -> None:
        self.reset()

    @property
    def today(self) -> date:
        return self.today_fn()

    def reset(self) -> None:
        with self.lock:
            self.sessions.clear()
            self.cart.clear()
            self.orders.clear()
            self.invoices.clear()
            for seed in seeded_orders(self.today, self.data_seed):
                lines = [
                    OrderLine(sku=line.sku, qty=line.qty, unit_price_eur=line.unit_price_eur)
                    for line in seed.lines
                ]
                self._add_order(int(seed.order_id[3:]), lines, seed.order_day, seed.delivery_day)

    # --- sessions -------------------------------------------------------------------------

    def new_session(self, replaces: str | None = None) -> str:
        """A fresh session after a correct password. The cart starts empty on every login,
        so nothing left over from an earlier run leaks into a new order."""
        token = secrets.token_urlsafe(24)
        with self.lock:
            self.sessions.pop(replaces or "", None)
            self.sessions[token] = Session(stage="password_ok")
            self.cart.clear()
        return token

    def end_session(self, token: str | None) -> None:
        with self.lock:
            self.sessions.pop(token or "", None)

    def session(self, token: str | None) -> Session | None:
        return self.sessions.get(token) if token else None

    # --- cart and orders -------------------------------------------------------------------

    def set_cart_qty(self, sku: str, qty: int, *, add: bool) -> None:
        if sku not in BY_SKU:
            raise KeyError(sku)
        with self.lock:
            new = (self.cart.get(sku, 0) if add else 0) + qty
            if new <= 0:
                self.cart.pop(sku, None)
            else:
                self.cart[sku] = min(new, 999)

    def cart_lines(self) -> list[OrderLine]:
        return [
            OrderLine(sku=sku, qty=qty, unit_price_eur=price_on(sku, self.today, self.today))
            for sku, qty in self.cart.items()
        ]

    def delivery_options(self) -> list[date]:
        """The next three weekdays, starting tomorrow."""
        days = [next_weekday(self.today)]
        while len(days) < 3:
            days.append(next_weekday(days[-1]))
        return days

    def place_order(self, delivery: date) -> Order:
        if delivery not in self.delivery_options():
            raise ValueError("delivery date not offered")
        with self.lock:
            lines = self.cart_lines()
            if not lines:
                raise ValueError("cart is empty")
            number = max([FIRST_NEW_ORDER, *(int(o.id[3:]) + 1 for o in self.orders)])
            order = self._add_order(number, lines, self.today, delivery)
            self.cart.clear()
            return order

    def cancel_order(self, order_id: str) -> Order:
        with self.lock:
            for i, order in enumerate(self.orders):
                if order.id == order_id:
                    if order.status != "placed" or order.delivery_date <= self.today:
                        raise ValueError("order can no longer be cancelled")
                    self.orders[i] = order.model_copy(update={"status": "cancelled"})
                    return self.orders[i]
        raise KeyError(order_id)

    def order(self, order_id: str) -> Order | None:
        return next((o for o in self.orders if o.id == order_id), None)

    def can_cancel(self, order: Order) -> bool:
        return order.status == "placed" and order.delivery_date > self.today

    def state(self) -> GrainlineState:
        return GrainlineState(cart=self.cart_lines(), orders=list(self.orders))

    def _add_order(
        self, number: int, lines: list[OrderLine], placed_on: date, delivery: date
    ) -> Order:
        invoice_id = f"INV-{FIRST_INVOICE + len(self.invoices)}"
        invoice = Invoice(id=invoice_id, order_id=f"GW-{number}", issued_on=placed_on, lines=lines)
        order = Order(
            id=f"GW-{number}",
            status="placed",
            lines=lines,
            total_eur=invoice.net_eur,
            delivery_date=delivery,
            invoice_id=invoice_id,
        )
        self.invoices[invoice_id] = invoice
        self.orders.append(order)
        return order
