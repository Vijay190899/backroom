"""The rest of the demo world: recipe costs, supplier prices, inventory, rota.

All pure functions of (sales, today, seed) plus the seed YAML files.
"""

from collections import defaultdict
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any

import yaml

from backroom_portals.grainline.catalog import BY_SKU, price_on, seeded_orders

# Stock-out story (PRD F1 card 1): oat milk has 2 days left at current velocity.
STORY_DAYS_LEFT = {"OAT-1L": 2.0}
VELOCITY_DAYS = 7
SAFETY_STOCK_DAYS = 4.0  # every other ingredient never runs below this many days


def load_recipes(path: Path) -> dict[str, dict[str, Any]]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def unit_cost(recipe: dict[str, Any], day: date, today: date) -> float:
    """EUR to make one item on `day`, at that day's Grainline prices."""
    cost = float(recipe.get("other_eur", 0.0))
    for sku, amount in recipe["uses"].items():
        cost += amount / BY_SKU[sku].size_qty * price_on(sku, day, today)
    return cost


def recipe_rows(recipes: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item_id, recipe in recipes.items():
        for sku, amount in recipe["uses"].items():
            rows.append(
                {"item_id": item_id, "sku": sku, "amount": amount, "unit": BY_SKU[sku].size_unit}
            )
    return rows


def supplier_prices(start: date, today: date) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    day = start
    while day <= today:
        for sku, product in BY_SKU.items():
            price = price_on(sku, day, today)
            rows.append(
                {
                    "date": day,
                    "sku": sku,
                    "unit_price_eur": price,
                    "price_per_unit_eur": round(price / product.size_qty, 4),
                    "unit": product.size_unit,
                }
            )
        day += timedelta(days=1)
    return rows


def daily_usage(
    sales: list[dict[str, Any]], recipes: dict[str, dict[str, Any]]
) -> dict[tuple[date, str], float]:
    """Ingredient used per (day, sku), in the SKU's size unit."""
    used: dict[tuple[date, str], float] = defaultdict(float)
    for s in sales:
        for sku, amount in recipes[s["item_id"]]["uses"].items():
            used[(s["date"], sku)] += amount * s["qty"]
    return used


def inventory(
    sales: list[dict[str, Any]],
    recipes: dict[str, dict[str, Any]],
    start: date,
    today: date,
    seed: int,
) -> list[dict[str, Any]]:
    """Daily stock per SKU: opening + Grainline deliveries - usage (sales x recipes).

    The opening stock is solved, not guessed: oat milk ends yesterday with exactly
    STORY_DAYS_LEFT of its 7-day velocity; every other SKU never drops below
    SAFETY_STOCK_DAYS."""
    used = daily_usage(sales, recipes)
    delivered: dict[tuple[date, str], float] = defaultdict(float)
    for order in seeded_orders(today, seed):
        for line in order.lines:
            delivered[(order.delivery_day, line.sku)] += line.qty * BY_SKU[line.sku].size_qty
    days = [start + timedelta(days=i) for i in range((today - start).days)]
    rows: list[dict[str, Any]] = []
    for sku in BY_SKU:
        net, cumulative = 0.0, []
        for day in days:
            net += delivered[(day, sku)] - used[(day, sku)]
            cumulative.append(net)
        velocity = sum(used[(d, sku)] for d in days[-VELOCITY_DAYS:]) / VELOCITY_DAYS
        if sku in STORY_DAYS_LEFT:
            opening = STORY_DAYS_LEFT[sku] * velocity - cumulative[-1]
        else:
            opening = SAFETY_STOCK_DAYS * velocity - min(cumulative)
        opening = max(opening, 0.0)
        stock = opening
        for day in days:
            start_stock = stock
            stock += delivered[(day, sku)] - used[(day, sku)]
            rows.append(
                {
                    "date": day,
                    "sku": sku,
                    "opening": round(start_stock, 4),
                    "delivered": round(delivered[(day, sku)], 4),
                    "used": round(used[(day, sku)], 4),
                    "closing": round(stock, 4),
                    "unit": BY_SKU[sku].size_unit,
                }
            )
    return rows


def rota(staff_spec: dict[str, Any], start: date, end: date) -> list[dict[str, Any]]:
    """Deterministic shift plan: staff rotate through the weekday's shift templates."""
    staff = [s["id"] for s in staff_spec["staff"] if s["role"] != "owner"]
    wage = float(staff_spec["hourly_wage_eur"])
    rows: list[dict[str, Any]] = []
    day, turn = start, 0
    while day <= end:
        key = "saturday" if day.weekday() == 5 else "sunday" if day.weekday() == 6 else "weekday"
        for shift in staff_spec["shifts"][key]:
            begin = time.fromisoformat(shift["start"])
            finish = time.fromisoformat(shift["end"])
            hours = (datetime.combine(day, finish) - datetime.combine(day, begin)).seconds / 3600
            for _ in range(shift["staff"]):
                rows.append(
                    {
                        "date": day,
                        "staff_id": staff[turn % len(staff)],
                        "start": shift["start"],
                        "end": shift["end"],
                        "hours": hours,
                        "cost_eur": round(hours * wage, 2),
                    }
                )
                turn += 1
        day += timedelta(days=1)
    return rows
