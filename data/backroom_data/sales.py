"""POS sales for Hafer & Bohne: Maven "Coffee Shop Sales", re-based to Bonn.

- One NYC store, its products mapped onto the café's menu (data/seed/product_map.yaml).
- Dates shifted by a multiple of 7 days so the window ends yesterday (weekdays kept).
- Prices are the TillDesk menu prices in EUR; the source USD price is kept for honesty.
- The weather effect is synthesised: a seeded 14% of transactions on rainy Saturdays
  are dropped, because the NYC sales never "saw" Bonn rain (docs/DATA.md).
"""

import random
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any

import yaml

from backroom_data import xlsx
from backroom_portals.tilldesk.store import MENU

_EXCEL_EPOCH = date(1899, 12, 30)
MENU_PRICE_EUR = {item_id: price for item_id, _, price in MENU}
RAIN_MM = 2.0  # a day with at least this much rain counts as rainy (detectors use the same)
RAINY_SATURDAY_DROP = 0.14  # PRD F1 card 3: -14% footfall on rainy Saturdays


@dataclass(frozen=True)
class Sale:
    transaction_id: int
    ts: datetime
    item_id: str
    qty: int
    unit_price_eur: float
    source: str  # "maven" or "synthetic"
    source_unit_price_usd: float | None

    def row(self) -> dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "ts": self.ts,
            "date": self.ts.date(),
            "hour": self.ts.hour,
            "weekday": self.ts.weekday(),
            "item_id": self.item_id,
            "qty": self.qty,
            "unit_price_eur": self.unit_price_eur,
            "revenue_eur": round(self.qty * self.unit_price_eur, 2),
            "source": self.source,
            "source_unit_price_usd": self.source_unit_price_usd,
        }


def load_map(path: Path) -> tuple[str, list[dict[str, str]]]:
    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    return spec["store"], spec["rules"]


def map_item(rules: list[dict[str, str]], product_type: str, detail: str) -> str | None:
    for rule in rules:
        if rule["type"] == product_type and detail.startswith(rule.get("detail", "")):
            return rule["item"]
    return None


def parse_maven(source: Any, store: str, rules: list[dict[str, str]]) -> list[Sale]:
    """The chosen store's mapped lines, in their original (NYC) dates."""
    out: list[Sale] = []
    for r in xlsx.rows(source):
        if r.get("store_location") != store:
            continue
        item = map_item(rules, r.get("product_type", ""), r.get("product_detail", "").strip())
        if item is None:
            continue
        day = _EXCEL_EPOCH + timedelta(days=int(float(r["transaction_date"])))
        seconds = round(float(r["transaction_time"]) * 86400)
        ts = datetime.combine(day, time()) + timedelta(seconds=seconds)
        out.append(
            Sale(
                transaction_id=int(float(r["transaction_id"])),
                ts=ts,
                item_id=item,
                qty=int(float(r["transaction_qty"])),
                unit_price_eur=MENU_PRICE_EUR[item],
                source="maven",
                source_unit_price_usd=float(r["unit_price"]),
            )
        )
    return out


def shift_days(last: date, today: date) -> int:
    """Days to add so `last` lands exactly on yesterday; a whole number of weeks when
    `last` has yesterday's weekday (rebase trims the source to make sure it does)."""
    return (today - timedelta(days=1) - last).days


def rebase(sales: Iterable[Sale], today: date) -> list[Sale]:
    """Shift the window to end yesterday with weekdays kept: first drop the source's
    last few days until it ends on yesterday's weekday (at most 6 days)."""
    sales = list(sales)
    yesterday_weekday = (today - timedelta(days=1)).weekday()
    last = max(s.ts.date() for s in sales)
    while last.weekday() != yesterday_weekday:
        last -= timedelta(days=1)
    sales = [s for s in sales if s.ts.date() <= last]
    shift = timedelta(days=shift_days(last, today))
    assert shift.days % 7 == 0
    return [
        Sale(
            s.transaction_id,
            s.ts + shift,
            s.item_id,
            s.qty,
            s.unit_price_eur,
            s.source,
            s.source_unit_price_usd,
        )
        for s in sales
    ]


NEIGHBOUR_WEEKS = 3


def apply_rainy_saturdays(sales: list[Sale], rainy_days: set[date], seed: int) -> list[Sale]:
    """Synthesise the rain effect: each rainy Saturday keeps a seeded sample of
    (1 - RAINY_SATURDAY_DROP) x the mean of the dry Saturdays within NEIGHBOUR_WEEKS.

    Calibrated against nearby dry Saturdays, not a flat per-day drop: the re-based sales
    trend upwards over the window, and with only a handful of rainy Saturdays the NYC
    noise would otherwise swamp (or reverse) the effect.
    """
    by_day: dict[date, set[int]] = {}
    for s in sales:
        by_day.setdefault(s.ts.date(), set()).add(s.transaction_id)
    saturdays = sorted(d for d in by_day if d.weekday() == 5)
    dry = {d: len(by_day[d]) for d in saturdays if d not in rainy_days}
    dropped: set[int] = set()
    for day in (d for d in saturdays if d in rainy_days):
        near = [n for d, n in dry.items() if abs((d - day).days) <= 7 * NEIGHBOUR_WEEKS]
        near = near or list(dry.values())
        if not near:
            continue
        target = round((1 - RAINY_SATURDAY_DROP) * sum(near) / len(near))
        ids = sorted(by_day[day])
        if len(ids) > target:
            keep = set(random.Random(f"{seed}:rain:{day}").sample(ids, target))
            dropped |= set(ids) - keep
    return [s for s in sales if s.transaction_id not in dropped]


# --- synthetic fallback ---------------------------------------------------------------------

_ITEM_SHARE = {
    "filter-coffee": 0.34,
    "oat-latte": 0.12,
    "cappuccino": 0.11,
    "espresso": 0.05,
    "flat-white": 0.05,
    "franzbroetchen": 0.14,
    "croissant": 0.10,
    "banana-bread": 0.09,
}
_HOUR_WEIGHT = {7: 9, 8: 14, 9: 13, 10: 12, 11: 9, 12: 8, 13: 7, 14: 6, 15: 6, 16: 5, 17: 4, 18: 2}
_WEEKDAY_TX = (240, 245, 250, 255, 265, 230, 200)  # Mon..Sun transactions per day
SYNTHETIC_DAYS = 182


def synthetic(today: date, seed: int) -> list[Sale]:
    """Seeded transactions with the Maven schema and similar hour/weekday shape."""
    rng = random.Random(f"sales:{seed}")
    items, weights = zip(*_ITEM_SHARE.items(), strict=True)
    hours, hour_w = zip(*_HOUR_WEIGHT.items(), strict=True)
    out: list[Sale] = []
    tx = 1
    for back in range(SYNTHETIC_DAYS, 0, -1):
        day = today - timedelta(days=back)
        for _ in range(_WEEKDAY_TX[day.weekday()] + rng.randint(-20, 20)):
            hour = rng.choices(hours, hour_w)[0]
            ts = datetime.combine(day, time(hour, rng.randrange(60), rng.randrange(60)))
            item = rng.choices(items, weights)[0]
            qty = 1 if rng.random() < 0.8 else 2
            out.append(Sale(tx, ts, item, qty, MENU_PRICE_EUR[item], "synthetic", None))
            tx += 1
    return out
