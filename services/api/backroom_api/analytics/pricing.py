"""Deterministic price proposals. The planner and verifier never compute prices: they pick
from what this module returns (PRD §8.4, "LLMs never originate numbers")."""

import math
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

TARGET_BUFFER_PTS = 1.5  # propose a little above the target, so one more cost bump doesn't sink it
GRID_EUR = 0.10  # menu prices move in 10-cent steps...
CAPPED_GRID_EUR = 0.05  # ...or 5-cent steps when an owner's cap forces a finer price


def round_half_up(value: float, digits: int = 0) -> float:
    """Rounding as people (and JS Math.round) do it: 70.5 -> 71, not Python's 70."""
    q = Decimal(1).scaleb(-digits)
    return float(Decimal(str(value)).quantize(q, rounding=ROUND_HALF_UP))


@dataclass(frozen=True)
class PriceProposal:
    price_eur: float
    increase_pct: float  # rounded half-up to 1 decimal
    margin_pct: float  # raw; round at the point of display
    meets_target: bool
    capped: bool


def margin_pct(cost_eur: float, price_eur: float) -> float:
    return (1 - cost_eur / price_eur) * 100


def propose_price(
    cost_eur: float,
    price_eur: float,
    target_pct: float,
    max_increase_pct: float | None = None,
) -> PriceProposal:
    """The lowest grid price whose margin reaches target + buffer.

    With an owner's cap (`max_increase_pct`, a learned Preference), the price is the
    highest 5-cent step within the cap, never below today's price; `meets_target` says
    whether that still reaches the plain target (the verifier keeps or drops the card)."""
    if price_eur <= 0 or cost_eur <= 0:
        raise ValueError("price and cost must be positive")
    want = target_pct + TARGET_BUFFER_PTS
    if want >= 100:
        raise ValueError("a margin target must be below 100%")
    # Smallest grid price p with 1 - cost/p >= want/100, i.e. p >= cost / (1 - want/100).
    floor_price = max(price_eur, cost_eur / (1 - want / 100))
    price = round(math.ceil(floor_price / GRID_EUR - 1e-9) * GRID_EUR, 2)
    capped = False
    if max_increase_pct is not None:
        ceiling = price_eur * (1 + max_increase_pct / 100)
        if price > ceiling:
            stepped = math.floor(ceiling / CAPPED_GRID_EUR + 1e-9) * CAPPED_GRID_EUR
            price = round(max(price_eur, stepped), 2)
            capped = True
    margin = margin_pct(cost_eur, price)
    return PriceProposal(
        price_eur=price,
        increase_pct=round_half_up((price / price_eur - 1) * 100, 1),
        margin_pct=margin,
        meets_target=margin >= target_pct,
        capped=capped,
    )
