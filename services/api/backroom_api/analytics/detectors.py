"""Detectors (PRD §8.4 step 1): DuckDB SQL over the L4 Parquet tables -> Candidates.

Every number a card can quote is computed here and listed in `Candidate.numbers`; the
planner only writes words around them and the number guard checks it (CONTRACTS §6).

Weekly impact, by kind (cards are ranked by it):
- stockout: sales of the last 7 days of every menu item that needs the ingredient
  (what running out puts at risk);
- margin_erosion: units sold in the last 7 days x the proposed price rise (margin
  recovered, assuming demand holds);
- weather_demand: the labour cost of the one shift the card proposes to trim.
"""

import json
import math
from collections.abc import Callable
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import duckdb

from backroom_api.analytics.pricing import propose_price, round_half_up
from backroom_api.contracts.candidate import Candidate, Evidence, EvidenceNumber, ProposedAction
from backroom_api.contracts.common import Unit

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[4] / "data" / "out"
BONN = ZoneInfo("Europe/Berlin")
TABLES = (
    "sales",
    "weather",
    "menu",
    "recipes",
    "unit_costs",
    "supplier_prices",
    "inventory",
    "rota",
)
STOCKOUT_DAYS = 3.0  # flag an ingredient with less than this many days of stock left
COVER_DAYS = 7  # a reorder covers one week of use
# Same rules as the data pipeline (backroom_data.sales); a test keeps them equal.
RAIN_MM = 2.0
NEIGHBOUR_DAYS = 21
MIN_RAIN_EFFECT_PCT = -5  # rain must cost at least this much before a card is worth it
MARGIN_LOOKBACK_DAYS = 28
LATE_SHIFT = ("14:00", "18:00")
INGREDIENT = {
    "OAT-1L": ("oat-milk", "Oat milk", "cartons"),
    "MILK-1L": ("milk", "Milk", "cartons"),
    "BEANS-1KG": ("espresso-beans", "Espresso beans", "bags"),
    "BUTTER-1KG": ("butter", "Butter", "blocks"),
    "FLOUR-5KG": ("flour", "Flour", "sacks"),
    "SUGAR-1KG": ("sugar", "Sugar", "bags"),
    "CINNAMON-500G": ("cinnamon", "Cinnamon", "tubs"),
    "CUP-12OZ-50": ("paper-cups", "Paper cups", "sleeves"),
}


def _ingredient(sku: str) -> tuple[str, str, str]:
    return INGREDIENT.get(sku, (sku.lower(), sku, "packs"))


def connect(data_dir: Path) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    for table in TABLES:
        con.execute(f"CREATE VIEW {table} AS SELECT * FROM '{data_dir / table}.parquet'")
    return con


def _n(key: str, value: float, unit: Unit, label: str) -> EvidenceNumber:
    return EvidenceNumber(key=key, value=value, unit=unit, label=label)


def _shown(sql: str, params: list[Any]) -> str:
    """The SQL as run, with its parameters inlined, for the evidence drawer."""
    for p in params:
        sql = sql.replace("?", f"'{p}'" if isinstance(p, date | str) else str(p), 1)
    return sql.strip()


class Context:
    def __init__(
        self,
        data_dir: Path,
        as_of: date,
        now: datetime,
        max_price_increase_pct: float | None = None,
    ) -> None:
        manifest = json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))
        if as_of.isoformat() != manifest["today"]:
            # The tables are built relative to one "today" (inventory ends the day before,
            # unit costs end on it); any other date would mix past and future rows.
            raise ValueError(f"data was built for {manifest['today']}, not {as_of}")
        self.con = connect(data_dir)
        self.as_of = as_of
        self.as_of_ts = datetime.combine(as_of, time(), tzinfo=BONN)
        self.week = (as_of - timedelta(days=7), as_of)  # the 7 full days before as_of
        self.now = now
        self.max_price_increase_pct = max_price_increase_pct
        self.synthetic_sales = manifest["sources"]["sales"] != "maven"
        prefs = json.loads((data_dir / "preferences.json").read_text(encoding="utf-8"))
        rules = [r["rule"] for r in prefs.get("business_rules", [])]
        self.margin_target = float(
            next((r["margin_target_pct"] for r in rules if "margin_target_pct" in r), 70)
        )

    def one(self, sql: str, params: list[Any] | None = None) -> tuple[Any, ...]:
        row = self.con.execute(sql, params or []).fetchone()
        if row is None:
            raise LookupError(sql)
        return row


# --- stock-out ---------------------------------------------------------------------------------

STOCKOUT_SQL = """
with last_day as (select max(date) as d from inventory where date < ?),
velocity as (
  select sku, avg(used) as per_day from inventory, last_day
  where date > last_day.d - interval 7 day and date <= last_day.d group by sku
),
pack as (
  select sku, unit_price_eur, unit_price_eur / price_per_unit_eur as size
  from supplier_prices where date = ?
)
select i.sku, round(i.closing, 2) as closing, round(v.per_day, 2) as per_day,
       round(i.closing / v.per_day, 2) as days_left, i.unit, p.size, p.unit_price_eur
from inventory i join velocity v using (sku) join pack p using (sku), last_day
where i.date = last_day.d and v.per_day > 0
order by days_left
"""
AT_RISK_SQL = """
select round(coalesce(sum(s.revenue_eur), 0), 2) from sales s
where s.item_id in (select item_id from recipes where sku = ?)
  and s.date >= ? and s.date < ?
"""


def stockout(ctx: Context) -> list[Candidate]:
    out: list[Candidate] = []
    rows = ctx.con.execute(STOCKOUT_SQL, [ctx.as_of, ctx.as_of]).fetchall()
    for sku, closing, per_day, days_left, unit, size, price in rows:
        if days_left >= STOCKOUT_DAYS or not size:
            continue
        slug, name, packs_word = _ingredient(sku)
        packs = max(1, math.ceil((COVER_DAYS * per_day - closing) / size - 1e-9))
        at_risk = float(ctx.one(AT_RISK_SQL, [sku, *ctx.week])[0])
        total = round(packs * price, 2)
        out.append(
            Candidate(
                id=f"stockout:ingredient:{slug}:{ctx.as_of}",
                kind="stockout",
                subject_id=f"ingredient:{slug}",
                title_hint=f"Reorder {name.lower()}",
                impact_eur_weekly=at_risk,
                numbers=[
                    _n("days_left", float(days_left), "days", "Days of stock left"),
                    _n(
                        "stock_left_packs",
                        round(closing / size, 1),
                        "count",
                        f"Stock left ({packs_word})",
                    ),
                    _n(
                        "use_per_day_packs",
                        round(per_day / size, 1),
                        "count",
                        f"Used per day ({packs_word})",
                    ),
                    _n("use_per_week", round(7 * per_day, 1), "count", f"Used per week ({unit})"),
                    _n("qty", float(packs), "count", f"{packs_word.capitalize()} to order"),
                    _n("cover_days", float(COVER_DAYS), "days", "Days the order covers"),
                    _n("unit_price_eur", float(price), "eur", "Grainline price per pack"),
                    _n("order_total_eur", total, "eur", "Order total"),
                    _n("impact_eur_weekly", at_risk, "eur", "Weekly sales of items that need it"),
                ],
                evidence=[
                    Evidence(
                        id=f"ev_stock_{slug}",
                        kind="sql",
                        label=f"{name}: stock and 7-day use",
                        sql=_shown(STOCKOUT_SQL, [ctx.as_of, ctx.as_of]),
                        columns=["sku", "closing", "per_day", "days_left", "unit"],
                        rows=[[sku, closing, per_day, days_left, unit]],
                        synthetic=True,  # inventory is simulated (docs/DATA.md)
                    ),
                    Evidence(
                        id=f"ev_sales_{slug}",
                        kind="sql",
                        label="Last 7 days of sales that need it",
                        sql=_shown(AT_RISK_SQL, [sku, *ctx.week]),
                        columns=["revenue_eur"],
                        rows=[[at_risk]],
                        synthetic=ctx.synthetic_sales,
                    ),
                ],
                proposed_action=ProposedAction(
                    task="grainline.reorder_item",
                    portal="grainline",
                    params={"sku": sku, "qty": packs},
                    executable=True,
                ),
                as_of=ctx.as_of_ts,
                computed_at=ctx.now,
            )
        )
    return out


# --- margin erosion ---------------------------------------------------------------------------

MARGIN_SQL = """
select m.item_id, m.name, m.price_eur, b.unit_cost_eur as cost_before, n.unit_cost_eur as cost_now
from menu m
join unit_costs b on b.item_id = m.item_id and b.date = ?
join unit_costs n on n.item_id = m.item_id and n.date = ?
order by m.item_id
"""
DRIVER_SQL = """
select r.sku, r.amount * b.price_per_unit_eur as cost_before,
       r.amount * n.price_per_unit_eur as cost_now,
       b.unit_price_eur as price_before, n.unit_price_eur as price_now
from recipes r
join supplier_prices b on b.sku = r.sku and b.date = ?
join supplier_prices n on n.sku = r.sku and n.date = ?
where r.item_id = ?
"""
UNITS_SQL = "select coalesce(sum(qty), 0) from sales where item_id = ? and date >= ? and date < ?"


def margin_erosion(ctx: Context) -> list[Candidate]:
    before_day = ctx.as_of - timedelta(days=MARGIN_LOOKBACK_DAYS)
    out: list[Candidate] = []
    for item_id, name, price, cost_before, cost_now in ctx.con.execute(
        MARGIN_SQL, [before_day, ctx.as_of]
    ).fetchall():
        if price <= 0 or cost_now <= cost_before:
            continue
        margin_before = (1 - cost_before / price) * 100
        margin_now = (1 - cost_now / price) * 100
        if margin_now >= ctx.margin_target:
            continue
        drivers = [
            d
            for d in ctx.con.execute(DRIVER_SQL, [before_day, ctx.as_of, item_id]).fetchall()
            if d[3] > 0
        ]
        if not drivers:
            continue
        sku, part_before, part_now, unit_before, unit_now = max(drivers, key=lambda d: d[2] - d[1])
        _, ingredient, _ = _ingredient(sku)
        proposal = propose_price(cost_now, price, ctx.margin_target, ctx.max_price_increase_pct)
        if not proposal.meets_target and proposal.price_eur <= price:
            continue  # the owner's cap leaves no price rise worth proposing
        units = float(ctx.one(UNITS_SQL, [item_id, *ctx.week])[0])
        impact = round(units * (proposal.price_eur - price), 2)
        numbers = [
            _n(
                "driver_increase_pct",
                round_half_up((unit_now / unit_before - 1) * 100, 1),
                "pct",
                f"{ingredient} price change",
            ),
            _n("driver_price_before_eur", unit_before, "eur", f"{ingredient} before"),
            _n("driver_price_now_eur", unit_now, "eur", f"{ingredient} now"),
            _n(
                "driver_cost_before_eur",
                round_half_up(part_before, 2),
                "eur",
                f"{ingredient} per {name}, before",
            ),
            _n(
                "driver_cost_now_eur",
                round_half_up(part_now, 2),
                "eur",
                f"{ingredient} per {name}, now",
            ),
            _n("unit_cost_before_eur", round_half_up(cost_before, 2), "eur", "Unit cost before"),
            _n("unit_cost_after_eur", round_half_up(cost_now, 2), "eur", "Unit cost now"),
            _n(
                "cost_rise_eur",
                round_half_up(cost_now - cost_before, 2),
                "eur",
                "Cost rise per item",
            ),
            _n("margin_before_pct", round_half_up(margin_before), "pct", "Margin before"),
            _n("margin_after_pct", round_half_up(margin_now), "pct", "Margin now"),
            _n("margin_target_pct", ctx.margin_target, "pct", "Target margin"),
            _n("price_now_eur", price, "eur", "Current price"),
            _n("price_new_eur", proposal.price_eur, "eur", "Proposed price"),
            _n("price_increase_pct", proposal.increase_pct, "pct", "Price change"),
            _n("margin_new_pct", round_half_up(proposal.margin_pct), "pct", "Margin at new price"),
            _n("units_weekly", units, "count", "Sold in the last 7 days"),
            _n("impact_eur_weekly", impact, "eur", "Weekly margin recovered"),
        ]
        if ctx.max_price_increase_pct is not None:
            numbers.append(
                _n(
                    "max_price_increase_pct",
                    ctx.max_price_increase_pct,
                    "pct",
                    "Your cap on price rises",
                )
            )
        out.append(
            Candidate(
                id=f"margin_erosion:product:{item_id}:{ctx.as_of}",
                kind="margin_erosion",
                subject_id=f"product:{item_id}",
                title_hint=f"Fix {name} margin",
                impact_eur_weekly=impact,
                numbers=numbers,
                evidence=[
                    Evidence(
                        id=f"ev_cost_{item_id}",
                        kind="sql",
                        label=f"{name} unit cost, {before_day} vs today",
                        sql=_shown(MARGIN_SQL, [before_day, ctx.as_of]),
                        columns=["item_id", "name", "price_eur", "cost_before", "cost_now"],
                        rows=[[item_id, name, price, round(cost_before, 4), round(cost_now, 4)]],
                    ),
                    Evidence(
                        id=f"ev_driver_{item_id}",
                        kind="sql",
                        label=f"{ingredient}: Grainline price and cost per {name}",
                        sql=_shown(DRIVER_SQL, [before_day, ctx.as_of, item_id]),
                        columns=["sku", "cost_before", "cost_now", "price_before", "price_now"],
                        rows=[
                            [sku, round(part_before, 4), round(part_now, 4), unit_before, unit_now]
                        ],
                        synthetic=True,  # supplier prices come from the mock Grainline portal
                    ),
                ],
                proposed_action=ProposedAction(
                    task="tilldesk.change_price",
                    portal="tilldesk",
                    params={"item_id": item_id, "price_eur": proposal.price_eur},
                    executable=True,
                ),
                as_of=ctx.as_of_ts,
                computed_at=ctx.now,
            )
        )
    return out


# --- weather demand ----------------------------------------------------------------------------

RAIN_EFFECT_SQL = f"""
with sat as (
  select s.date, count(distinct s.transaction_id) as tx, w.precip_mm >= {RAIN_MM} as rainy
  from sales s join weather w using (date)
  where dayofweek(s.date) = 6 and s.date < ? group by s.date, w.precip_mm
)
select r.date, r.tx,
       round((select avg(d.tx) from sat d
              where not d.rainy and abs(date_diff('day', d.date, r.date)) <= {NEIGHBOUR_DAYS}), 1)
         as nearby_dry_tx
from sat r where r.rainy order by r.date
"""
LATE_SHIFTS_SQL = (
    "select count(*), max(hours), max(cost_eur) from rota "
    'where date = ? and start = ? and "end" = ?'
)


def weather_demand(ctx: Context) -> list[Candidate]:
    saturday = ctx.as_of + timedelta(days=(5 - ctx.as_of.weekday()) % 7 or 7)
    forecast = ctx.con.execute(
        "select precip_mm, source from weather where date = ?", [saturday]
    ).fetchone()
    if forecast is None or forecast[0] < RAIN_MM:
        return []
    history = [r for r in ctx.con.execute(RAIN_EFFECT_SQL, [ctx.as_of]).fetchall() if r[2]]
    if not history:
        return []
    effect = round_half_up((sum(tx / dry for _, tx, dry in history) / len(history) - 1) * 100)
    if effect > MIN_RAIN_EFFECT_PCT:
        return []
    late = ctx.con.execute(LATE_SHIFTS_SQL, [saturday, *LATE_SHIFT]).fetchone()
    if late is None or late[0] < 2:
        return []  # keep at least one person on the afternoon
    shifts, hours, cost = late
    rows = [[d.isoformat(), tx, dry] for d, tx, dry in history]
    return [
        Candidate(
            id=f"weather_demand:business:hafer-und-bohne:{ctx.as_of}",
            kind="weather_demand",
            subject_id="business:hafer-und-bohne",
            title_hint="Rainy Saturday: trim one shift",
            impact_eur_weekly=float(cost),
            numbers=[
                _n("rain_mm", float(forecast[0]), "mm", "Forecast rain"),
                _n("footfall_change_pct", float(effect), "pct", "Sales on rainy Saturdays"),
                _n("rainy_saturdays", float(len(history)), "count", "Rainy Saturdays in history"),
                _n("late_shifts", float(shifts), "count", "Afternoon shifts planned"),
                _n("shift_hours", float(hours), "hours", "Shift length"),
                _n("impact_eur_weekly", float(cost), "eur", "Labour saved"),
            ],
            evidence=[
                Evidence(
                    id="ev_rain_saturdays",
                    kind="chart",
                    label="Rainy Saturdays vs nearby dry ones (transactions)",
                    sql=_shown(RAIN_EFFECT_SQL, [ctx.as_of]),
                    columns=["date", "transactions", "nearby_dry_avg"],
                    rows=rows,
                    synthetic=True,  # the rain effect is synthesised (docs/DATA.md)
                ),
                Evidence(
                    id="ev_forecast",
                    kind="sql",
                    label=f"Forecast for {saturday}",
                    sql=_shown("select precip_mm, source from weather where date = ?", [saturday]),
                    columns=["precip_mm", "source"],
                    rows=[[forecast[0], forecast[1]]],
                    synthetic="demo_override" in forecast[1] or "synthetic" in forecast[1],
                ),
            ],
            proposed_action=ProposedAction(
                task=None,
                portal=None,
                params={"date": saturday.isoformat(), "shift": "-".join(LATE_SHIFT)},
                executable=False,  # no portal trims shifts; a recommendation only (PRD F1)
            ),
            as_of=ctx.as_of_ts,
            computed_at=ctx.now,
        )
    ]


DETECTORS: tuple[Callable[[Context], list[Candidate]], ...] = (
    stockout,
    margin_erosion,
    weather_demand,
)


def run_all(
    data_dir: Path = DEFAULT_DATA_DIR,
    as_of: date | None = None,
    now: datetime | None = None,
    max_price_increase_pct: float | None = None,
) -> list[Candidate]:
    """Every detector's candidates, highest weekly impact first.

    `max_price_increase_pct` is the owner's learned cap (a Preference fact); with it the
    margin card is re-proposed within the cap (PRD F4)."""
    manifest = json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))
    ctx = Context(
        data_dir,
        as_of or date.fromisoformat(manifest["today"]),
        now or datetime.now(BONN),
        max_price_increase_pct,
    )
    try:
        found = [c for detect in DETECTORS for c in detect(ctx)]
    finally:
        ctx.con.close()
    return sorted(found, key=lambda c: c.impact_eur_weekly, reverse=True)
