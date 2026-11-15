"""TillDesk's in-memory state: the café's menu with draft and published prices.

Editing a price changes the draft; "Publish menu" makes every draft live on the till.
The change-price skill's postcondition reads `items.<id>.published_price_eur`.
"""

import re
import secrets
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime

from backroom_portals.contract import DEMO_PRICES_EUR, MenuItem, TillDeskState

# Menu items and their published prices at the start of the demo. The data pipeline
# (L4) maps the POS sales onto these ids and prices.
MENU: tuple[tuple[str, str, float], ...] = (
    ("franzbroetchen", "Franzbrötchen", DEMO_PRICES_EUR["franzbroetchen.menu"]),
    ("croissant", "Butter croissant", 2.60),
    ("flat-white", "Flat white", 3.80),
    ("oat-latte", "Oat latte", 4.20),
    ("cappuccino", "Cappuccino", 3.60),
    ("espresso", "Espresso", 2.40),
    ("filter-coffee", "Filter coffee", 2.90),
    ("banana-bread", "Banana bread", 3.40),
)
MIN_PRICE_EUR = 0.10
MAX_PRICE_EUR = 99.99
_PRICE_RE = re.compile(r"(\d{1,2})(?:[.,](\d{1,2}))?")


def parse_price(text: str) -> float | None:
    """'3.60', '3,60', '3,60 €', '€3.6' or '3' -> 3.6; anything else -> None."""
    text = text.strip().removeprefix("€").removesuffix("€").strip()
    match = _PRICE_RE.fullmatch(text) if text.isascii() else None
    if match is None:
        return None
    euros, cents = match.group(1), (match.group(2) or "0").ljust(2, "0")
    price = round(int(euros) + int(cents) / 100, 2)
    return price if MIN_PRICE_EUR <= price <= MAX_PRICE_EUR else None


@dataclass
class TillDeskStore:
    sessions: set[str] = field(default_factory=set[str])
    items: dict[str, MenuItem] = field(default_factory=dict[str, MenuItem])
    last_published_at: datetime | None = None
    lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        with self.lock:
            self.sessions.clear()
            self.items = {
                item_id: MenuItem(id=item_id, name=name, price_eur=price, published_price_eur=price)
                for item_id, name, price in MENU
            }
            self.last_published_at = None

    def new_session(self, replaces: str | None = None) -> str:
        """A fresh login also drops unpublished drafts, so a run that saved but never
        published cannot leak its draft into the next run's publish (like L-14)."""
        token = secrets.token_urlsafe(24)
        with self.lock:
            self.sessions.discard(replaces or "")
            self.sessions.add(token)
            self.items = {
                k: v.model_copy(update={"price_eur": v.published_price_eur})
                for k, v in self.items.items()
            }
        return token

    def end_session(self, token: str | None) -> None:
        with self.lock:
            self.sessions.discard(token or "")

    def authed(self, token: str | None) -> bool:
        return bool(token) and token in self.sessions

    def set_draft(self, item_id: str, price: float) -> MenuItem:
        with self.lock:
            item = self.items[item_id]
            self.items[item_id] = item.model_copy(update={"price_eur": price})
            return self.items[item_id]

    def has_unpublished(self) -> bool:
        return any(i.price_eur != i.published_price_eur for i in self.items.values())

    def publish(self) -> None:
        with self.lock:
            self.items = {
                k: v.model_copy(update={"published_price_eur": v.price_eur})
                for k, v in self.items.items()
            }
            self.last_published_at = datetime.now(UTC)

    def state(self) -> TillDeskState:
        return TillDeskState(items=dict(self.items), last_published_at=self.last_published_at)
