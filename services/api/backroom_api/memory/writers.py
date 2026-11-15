"""Deterministic writers: structured data -> episodes + facts, with no LLM (PRD §8.3).

`write_world` loads the L4 data (data/out) into the graph: the business, its menu,
recipes, supplier, staff, seeded preferences and rules, recent and forecast weather,
holidays, plus one `invoice` episode per Grainline invoice whose prices supersede each
other (butter EUR 7.10 -> 8.24/kg). It is idempotent: running it twice adds nothing.

`write_invoice` is the same invoice path on its own, for ingesting one invoice later
(POST /memory/ingest/invoice). `write_world(hold_back=...)` leaves chosen invoices out,
so the demo can ingest one live and watch its prices supersede (PRD F4).
"""

import json
from collections.abc import Collection
from datetime import date, datetime, time, timedelta
from itertools import pairwise
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import duckdb
from psycopg import Connection

from backroom_api.analytics.detectors import INGREDIENT
from backroom_api.contracts.api import InvoiceIngestResponse
from backroom_api.memory.store import add_episode, assert_fact, upsert_entity

BONN = ZoneInfo("Europe/Berlin")
BUSINESS = "business:hafer-und-bohne"
SUPPLIER = "supplier:grainline"
PRICE_PREDICATE = {
    "kg": "unit_price_eur_per_kg",
    "l": "unit_price_eur_per_l",
    "pcs": "unit_price_eur_each",
}
# Recipe amounts in the units CONTRACTS §8 names: grams, millilitres, pieces.
AMOUNT_KEY = {"kg": ("grams", 1000), "l": ("ml", 1000), "pcs": ("pcs", 1)}
WEATHER_PAST_DAYS = 14

PackSizes = dict[str, tuple[float, str]]  # sku -> (contents of one pack, unit)


def _at(day: date) -> datetime:
    return datetime.combine(day, time(), tzinfo=BONN)


def ingredient_id(sku: str) -> str:
    return f"ingredient:{INGREDIENT.get(sku, (sku.lower(),))[0]}"


def _rows(
    con: duckdb.DuckDBPyConnection, sql: str, path: Path, *params: Any
) -> list[dict[str, Any]]:
    """Rows of one Parquet file; the path is a parameter, never pasted into the SQL."""
    cur = con.execute(sql.replace("{table}", "read_parquet(?)"), [str(path), *params])
    cols = [d[0] for d in cur.description or []]
    return [dict(zip(cols, r, strict=True)) for r in cur.fetchall()]


def pack_sizes(data_dir: Path) -> PackSizes:
    con = duckdb.connect()
    rows = _rows(
        con,
        "select distinct on (sku) sku, unit_price_eur / price_per_unit_eur as size, unit "
        "from {table} order by sku, date desc",
        data_dir / "supplier_prices.parquet",
    )
    con.close()
    return {r["sku"]: (r["size"], r["unit"]) for r in rows}


def write_invoice(
    conn: Connection[Any],
    *,
    invoice_id: str,
    order_id: str,
    day: date,
    lines: list[dict[str, Any]],
    sizes: PackSizes,
) -> InvoiceIngestResponse:
    """One Grainline invoice -> an `invoice` episode + a price fact per line. A new
    price supersedes the old one; a known price changes nothing."""
    episode = add_episode(
        conn,
        "invoice",
        {
            "summary": f"Grainline invoice {invoice_id}",
            "invoice_id": invoice_id,
            "order_id": order_id,
            "lines": [
                {"sku": i["sku"], "qty": i["qty"], "unit_price_eur": i["unit_price_eur"]}
                for i in lines
            ],
        },
        _at(day),
    )
    created: list[str] = []
    superseded: list[str] = []
    for i in lines:
        size, unit = sizes[i["sku"]]
        result = assert_fact(
            conn,
            ingredient_id(i["sku"]),
            PRICE_PREDICATE[unit],
            value=round(i["unit_price_eur"] / size, 4),
            valid_from=_at(day),
            source_episode=episode,
        )
        if result.created:
            created.append(result.fact_id)
        if result.superseded:
            superseded.append(result.superseded)
    return InvoiceIngestResponse(
        episode_id=episode, fact_ids=created, superseded_fact_ids=superseded
    )


def write_world(
    conn: Connection[Any], data_dir: Path, hold_back: Collection[str] = ()
) -> dict[str, int]:
    """Load the L4 world; returns how many facts were created per source. Invoices whose
    id is in `hold_back` are left out (to be ingested later)."""
    manifest = json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))
    prefs = json.loads((data_dir / "preferences.json").read_text(encoding="utf-8"))
    start = _at(date.fromisoformat(manifest["window"]["start"]))
    today = date.fromisoformat(manifest["today"])
    con = duckdb.connect()

    def table(name: str, sql: str) -> list[dict[str, Any]]:
        return _rows(con, sql, data_dir / f"{name}.parquet")

    created = {"seed": 0, "invoices": 0}
    seed = add_episode(
        conn,
        "seed",
        {
            "summary": "Demo world from backroom-data",
            "today": manifest["today"],
            "seed": manifest["seed"],
        },
        start,
    )

    def fact(*args: Any, **kwargs: Any) -> None:
        if assert_fact(conn, *args, source_episode=seed, **kwargs).created:
            created["seed"] += 1

    upsert_entity(conn, BUSINESS, "business", "Hafer & Bohne", city="Bonn")
    upsert_entity(conn, SUPPLIER, "supplier", "Grainline Wholesale")
    upsert_entity(conn, "portal:grainline", "portal", "Grainline")
    upsert_entity(conn, "portal:tilldesk", "portal", "TillDesk")
    fact(SUPPLIER, "orders_via", object_id="portal:grainline", valid_from=start)
    fact(BUSINESS, "sells_via", object_id="portal:tilldesk", valid_from=start)

    for m in table("menu", "select * from {table} order by item_id"):
        product = f"product:{m['item_id']}"
        upsert_entity(conn, product, "product", m["name"])
        fact(product, "menu_price_eur", value=m["price_eur"], valid_from=start)
    sizes = pack_sizes(data_dir)
    for sku, (_, unit) in sizes.items():
        ingredient = ingredient_id(sku)
        name = INGREDIENT.get(sku, (sku, sku))[1]
        upsert_entity(conn, ingredient, "ingredient", name, sku=sku, unit=unit)
        fact(ingredient, "supplied_by", object_id=SUPPLIER, valid_from=start)
    for r in table("recipes", "select * from {table} order by item_id, sku"):
        key, factor = AMOUNT_KEY[r["unit"]]
        fact(
            f"product:{r['item_id']}",
            "uses_ingredient",
            object_id=ingredient_id(r["sku"]),
            value={key: round(r["amount"] * factor, 1)},
            valid_from=start,
        )
    for s in table("staff", "select * from {table} order by id"):
        staff = f"staff:{s['id']}"
        upsert_entity(conn, staff, "staff", s["name"], role=s["role"])
        fact(staff, "works_at", object_id=BUSINESS, value={"role": s["role"]}, valid_from=start)
    for p in prefs.get("preferences", []):
        since = _at(today - timedelta(days=int(p.get("since_days_ago", 0))))
        record_preference(
            conn, p["id"], p["text"], p["rule"], valid_from=since, source_episode=seed
        )
    for rule in prefs.get("business_rules", []):
        entity = f"preference:{rule['id']}"
        upsert_entity(conn, entity, "preference", rule["text"])
        fact(BUSINESS, "has_rule", object_id=entity, value=rule["rule"], valid_from=start)

    # Recent and forecast weather, and holidays, as dated nodes (memory's time context).
    weather_sql = "select * from {table} where date >= ? order by date"
    weather = _rows(
        con, weather_sql, data_dir / "weather.parquet", today - timedelta(days=WEATHER_PAST_DAYS)
    )
    for w in weather:
        node = f"weather_day:{w['date'].isoformat()}"
        upsert_entity(conn, node, "weather_day", w["date"].isoformat())
        fact(
            node,
            "weather",
            value={"precip_mm": w["precip_mm"], "tmax_c": w["tmax_c"], "source": w["source"]},
            valid_from=_at(w["date"]),
        )
    for h in table("holidays", "select * from {table} order by date"):
        node = f"holiday:{h['date'].isoformat()}"
        upsert_entity(conn, node, "holiday", h["name"])
        fact(
            node,
            "observed_in",
            object_id=BUSINESS,
            value={"date": h["date"].isoformat()},
            valid_from=_at(h["date"]),
        )

    # One episode per invoice, in date order, so a price change supersedes the previous
    # price (that is how the butter rise lands in memory).
    by_invoice: dict[str, list[dict[str, Any]]] = {}
    for line in table(
        "grainline_orders", "select * from {table} order by order_date, invoice_id, sku"
    ):
        by_invoice.setdefault(line["invoice_id"], []).append(line)
    for invoice_id, items in by_invoice.items():
        if invoice_id in hold_back:
            continue
        result = write_invoice(
            conn,
            invoice_id=invoice_id,
            order_id=items[0]["order_id"],
            day=items[0]["order_date"],
            lines=items,
            sizes=sizes,
        )
        created["invoices"] += len(result.fact_ids)
    con.close()
    return created


def invoices_from_price_change(data_dir: Path, sku: str) -> list[str]:
    """Every invoice from the first one that carries a new price for `sku` on, oldest
    first. The demo holds these back (write_world(hold_back=...)) and then ingests the
    first of them live, so its price supersedes the old one in front of the audience."""
    con = duckdb.connect()
    rows = _rows(
        con,
        "select invoice_id, unit_price_eur from {table} where sku = ? order by order_date",
        data_dir / "grainline_orders.parquet",
        sku,
    )
    con.close()
    for k, (previous, current) in enumerate(pairwise(rows), start=1):
        if current["unit_price_eur"] != previous["unit_price_eur"]:
            return list(dict.fromkeys(r["invoice_id"] for r in rows[k:]))
    return []


def record_preference(
    conn: Connection[Any],
    preference_id: str,
    text: str,
    rule: dict[str, Any],
    *,
    valid_from: datetime,
    source_episode: str | None = None,
    confidence: float = 1.0,
) -> str:
    """The business has this preference from `valid_from` on. A later assertion with a
    different rule (e.g. a new cap) supersedes the earlier one. Returns the fact id."""
    entity = f"preference:{preference_id}"
    upsert_entity(conn, entity, "preference", text)
    return assert_fact(
        conn,
        BUSINESS,
        "has_preference",
        object_id=entity,
        value=rule,
        valid_from=valid_from,
        source_episode=source_episode,
        confidence=confidence,
    ).fact_id
