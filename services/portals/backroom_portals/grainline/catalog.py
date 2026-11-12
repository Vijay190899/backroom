"""Grainline's catalog, price history and seeded order history.

Pure functions of (today, data_seed), so the portal, the data pipeline (L4) and the
detectors (L6) all see the same prices and invoices. Scripted events (docs/DATA.md):
butter +16% from day -9 (EUR 7.10 -> 8.24/kg), oat milk +9% from day -3.
"""

import random
from dataclasses import dataclass
from datetime import date, timedelta

from backroom_portals.contract import DEMO_PRICES_EUR, GRAINLINE_SKUS


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    unit: str  # what one quantity buys, shown next to the price
    vat_pct: int  # 7 for food, 19 for everything else
    size_qty: float  # contents of one unit, in size_unit (for EUR/kg, EUR/L)
    size_unit: str  # "kg", "l" or "pcs"


@dataclass(frozen=True)
class PriceEvent:
    sku: str
    day_offset: int  # relative to today; the new price applies from this day on
    before_eur: float
    after_eur: float


_UNITS: dict[str, tuple[str, int, float, str]] = {
    "OAT-1L": ("carton", 7, 1.0, "l"),
    "MILK-1L": ("carton", 7, 1.0, "l"),
    "BEANS-1KG": ("bag", 7, 1.0, "kg"),
    "BUTTER-1KG": ("block", 7, 1.0, "kg"),
    "FLOUR-5KG": ("sack", 7, 5.0, "kg"),
    "SUGAR-1KG": ("bag", 7, 1.0, "kg"),
    "CINNAMON-500G": ("tub", 7, 0.5, "kg"),
    "CUP-12OZ-50": ("sleeve", 19, 50.0, "pcs"),
}
PRODUCTS: tuple[Product, ...] = tuple(
    Product(sku, name, *_UNITS[sku]) for sku, name in GRAINLINE_SKUS.items()
)
BY_SKU = {p.sku: p for p in PRODUCTS}

# Prices that never change in the demo window.
STABLE_PRICES_EUR: dict[str, float] = {
    "MILK-1L": 1.09,
    "BEANS-1KG": 18.90,
    "FLOUR-5KG": 4.35,
    "SUGAR-1KG": 1.29,
    "CINNAMON-500G": 6.80,
    "CUP-12OZ-50": 4.90,
}
PRICE_EVENTS: tuple[PriceEvent, ...] = (
    PriceEvent(
        "BUTTER-1KG", -9, DEMO_PRICES_EUR["BUTTER-1KG.before"], DEMO_PRICES_EUR["BUTTER-1KG"]
    ),
    PriceEvent("OAT-1L", -3, 1.46, DEMO_PRICES_EUR["OAT-1L"]),
)
_EVENT_BY_SKU = {e.sku: e for e in PRICE_EVENTS}


def price_on(sku: str, day: date, today: date) -> float:
    """Net unit price in EUR on `day`."""
    event = _EVENT_BY_SKU.get(sku)
    if event is None:
        return STABLE_PRICES_EUR[sku]
    return event.after_eur if day >= today + timedelta(days=event.day_offset) else event.before_eur


@dataclass(frozen=True)
class SeedLine:
    sku: str
    qty: int
    unit_price_eur: float


@dataclass(frozen=True)
class SeedOrder:
    order_id: str
    invoice_id: str
    order_day: date
    delivery_day: date
    lines: tuple[SeedLine, ...]


# Lena's usual Tue/Fri order (the seeded preference); quantities vary a little per order.
# Oat milk is ordered well under what the café now uses (220 ml per oat latte, ~38 L a
# week vs ~20 L delivered), so stock falls steadily to the demo's stock-out with its
# lowest point at the end of the window (backroom_data.world.inventory). The agent's
# reorder of 24 cartons is the fix.
_USUAL_BASKET = {
    "OAT-1L": 10,
    "MILK-1L": 30,
    "BEANS-1KG": 6,
    "BUTTER-1KG": 4,
    "FLOUR-5KG": 2,
    "SUGAR-1KG": 3,
    "CUP-12OZ-50": 4,
}
HISTORY_DAYS = 28
ORDER_WEEKDAYS = (1, 4)  # Tue, Fri
FIRST_NEW_ORDER = 10482  # seeded history ends just below this (GW-10482 in the demo)
FIRST_INVOICE = 204100


def next_weekday(day: date) -> date:
    day += timedelta(days=1)
    while day.weekday() >= 5:
        day += timedelta(days=1)
    return day


def seeded_orders(today: date, data_seed: int) -> list[SeedOrder]:
    """Past orders on every Tue/Fri of the last four weeks, oldest first, with the ids,
    prices and invoice ids the portal shows (invoice i belongs to order i)."""
    days = [
        today - timedelta(days=back)
        for back in range(HISTORY_DAYS, 0, -1)
        if (today - timedelta(days=back)).weekday() in ORDER_WEEKDAYS
    ]
    orders: list[SeedOrder] = []
    for i, day in enumerate(days):
        rng = random.Random(f"{data_seed}:{day.isoformat()}")
        basket = [
            (sku, max(1, qty + rng.choice((-1, 0, 0, 1)) * max(1, qty // 6)))
            for sku, qty in _USUAL_BASKET.items()
        ]
        if rng.random() < 0.5:
            basket.append(("CINNAMON-500G", 1))
        lines = tuple(SeedLine(sku, qty, price_on(sku, day, today)) for sku, qty in basket)
        orders.append(
            SeedOrder(
                order_id=f"GW-{FIRST_NEW_ORDER - len(days) + i}",
                invoice_id=f"INV-{FIRST_INVOICE + i}",
                order_day=day,
                delivery_day=next_weekday(day),
                lines=lines,
            )
        )
    return orders
