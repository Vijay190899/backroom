"""`backroom-data`: builds the Hafer & Bohne demo world from open data (milestone M1).

    uv run backroom-data all [--offline] [--today YYYY-MM-DD] [--seed N] [--out DIR]

Writes data/out/*.parquet plus manifest.json. Idempotent: downloads are cached under
data/raw/, and the same (today, seed, cache) always gives the same files. `today` and
the seed default to the portals' settings (PORTALS_TODAY, DATA_SEED, from .env), so the
data and the Grainline history agree. Loading Postgres is the PC's part of `pnpm seed`.
"""

import argparse
import json
import sys
import zipfile
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from backroom_data import parquet, sales, sources, world
from backroom_portals.config import Settings
from backroom_portals.grainline.catalog import HISTORY_DAYS, seeded_orders
from backroom_portals.tilldesk.store import MENU

DATA_DIR = Path(__file__).resolve().parents[1]
FORECAST_DAYS = 7
DEMO_FORECAST_RAIN_MM = 9.0  # PRD F1 card 3: "the forecast is 9 mm of rain"

# Explicit column types, so a table's schema never depends on which source built it.
SCHEMAS: dict[str, dict[str, str]] = {
    "sales": {
        "transaction_id": "BIGINT",
        "ts": "TIMESTAMP",
        "date": "DATE",
        "hour": "BIGINT",
        "weekday": "BIGINT",
        "item_id": "VARCHAR",
        "qty": "BIGINT",
        "unit_price_eur": "DOUBLE",
        "revenue_eur": "DOUBLE",
        "source": "VARCHAR",
        "source_unit_price_usd": "DOUBLE",
    },
    "weather": {
        "date": "DATE",
        "precip_mm": "DOUBLE",
        "tmax_c": "DOUBLE",
        "tmin_c": "DOUBLE",
        "source": "VARCHAR",
    },
    "holidays": {"date": "DATE", "name": "VARCHAR", "source": "VARCHAR"},
    "menu": {"item_id": "VARCHAR", "name": "VARCHAR", "price_eur": "DOUBLE"},
    "recipes": {"item_id": "VARCHAR", "sku": "VARCHAR", "amount": "DOUBLE", "unit": "VARCHAR"},
    "unit_costs": {"date": "DATE", "item_id": "VARCHAR", "unit_cost_eur": "DOUBLE"},
    "supplier_prices": {
        "date": "DATE",
        "sku": "VARCHAR",
        "unit_price_eur": "DOUBLE",
        "price_per_unit_eur": "DOUBLE",
        "unit": "VARCHAR",
    },
    "grainline_orders": {
        "order_id": "VARCHAR",
        "invoice_id": "VARCHAR",
        "order_date": "DATE",
        "delivery_date": "DATE",
        "sku": "VARCHAR",
        "qty": "BIGINT",
        "unit_price_eur": "DOUBLE",
    },
    "inventory": {
        "date": "DATE",
        "sku": "VARCHAR",
        "opening": "DOUBLE",
        "delivered": "DOUBLE",
        "used": "DOUBLE",
        "closing": "DOUBLE",
        "unit": "VARCHAR",
    },
    "staff": {"id": "VARCHAR", "name": "VARCHAR", "role": "VARCHAR", "hourly_wage_eur": "DOUBLE"},
    "rota": {
        "date": "DATE",
        "staff_id": "VARCHAR",
        "start": "VARCHAR",
        "end": "VARCHAR",
        "hours": "DOUBLE",
        "cost_eur": "DOUBLE",
    },
}


def next_saturday(today: date) -> date:
    return today + timedelta(days=(5 - today.weekday()) % 7 or 7)


def _maven_sales(raw: Path, today: date, *, offline: bool) -> list[sales.Sale]:
    """The re-based Maven sales, or [] when the source is missing or unreadable."""
    zip_path = sources.maven_zip(raw, offline=offline)
    if zip_path is None:
        return []
    store, rules = sales.load_map(DATA_DIR / "seed" / "product_map.yaml")
    try:
        with zipfile.ZipFile(zip_path) as z:
            name = next(n for n in z.namelist() if n.endswith(".xlsx") and "__MACOSX" not in n)
            with z.open(name) as workbook:
                parsed = sales.parse_maven(workbook, store, rules)
    except (zipfile.BadZipFile, StopIteration, KeyError, ValueError, OSError):
        return []  # a corrupt or unexpected download falls back to synthetic data
    return sales.rebase(parsed, today) if parsed else []


def build(today: date, seed: int, out: Path, raw: Path, *, offline: bool) -> dict[str, Any]:
    """Build every table; returns the manifest."""
    recipes = world.load_recipes(DATA_DIR / "recipes.yaml")
    lines = _maven_sales(raw, today, offline=offline)
    sales_source = "maven" if lines else "synthetic"
    if not lines:
        lines = sales.synthetic(today, seed)
    start = min(s.ts.date() for s in lines)
    end = today + timedelta(days=FORECAST_DAYS)

    weather = sources.weather(raw, start, end, today, offline=offline)
    if len({w["date"] for w in weather}) < (end - start).days + 1:  # any gap: all synthetic
        weather = sources.synthetic_weather(start, end, seed)
    saturday = next_saturday(today)
    for w in weather:
        if w["date"] == saturday:
            w.update(precip_mm=DEMO_FORECAST_RAIN_MM, source=f"{w['source']}+demo_override")
    rainy = {w["date"] for w in weather if w["precip_mm"] >= sales.RAIN_MM}
    lines = sales.apply_rainy_saturdays(lines, rainy, seed)
    sale_rows = [s.row() for s in lines]

    hols = sources.holidays(raw, sorted({start.year, end.year}), offline=offline)
    staff_spec: dict[str, Any] = world.yaml.safe_load(
        (DATA_DIR / "seed" / "staff.yaml").read_text(encoding="utf-8")
    )
    prefs: dict[str, Any] = world.yaml.safe_load(
        (DATA_DIR / "seed" / "preferences.yaml").read_text(encoding="utf-8")
    )
    orders = seeded_orders(today, seed)
    days = [start + timedelta(days=i) for i in range((today - start).days + 1)]
    wage = staff_spec["hourly_wage_eur"]

    tables: dict[str, list[dict[str, Any]]] = {
        "sales": sale_rows,
        "weather": weather,
        "holidays": [h for h in hols if start <= h["date"] <= end],
        "menu": [{"item_id": i, "name": n, "price_eur": p} for i, n, p in MENU],
        "recipes": world.recipe_rows(recipes),
        "unit_costs": [
            {"date": d, "item_id": item, "unit_cost_eur": round(world.unit_cost(r, d, today), 4)}
            for d in days
            for item, r in recipes.items()
        ],
        "supplier_prices": world.supplier_prices(start, today),
        "grainline_orders": [
            {
                "order_id": o.order_id,
                "invoice_id": o.invoice_id,
                "order_date": o.order_day,
                "delivery_date": o.delivery_day,
                "sku": line.sku,
                "qty": line.qty,
                "unit_price_eur": line.unit_price_eur,
            }
            for o in orders
            for line in o.lines
        ],
        # Only the window Grainline has orders for, so every delivery is a real order.
        "inventory": world.inventory(
            sale_rows, recipes, today - timedelta(days=HISTORY_DAYS), today, seed
        ),
        "staff": [{**s, "hourly_wage_eur": wage} for s in staff_spec["staff"]],
        "rota": world.rota(staff_spec, start, end),
    }
    out.mkdir(parents=True, exist_ok=True)
    counts = {
        name: parquet.write(out / f"{name}.parquet", rows, SCHEMAS[name])
        for name, rows in tables.items()
    }
    (out / "preferences.json").write_text(json.dumps(prefs, indent=2) + "\n", encoding="utf-8")
    weather_sources = sorted({w["source"] for w in weather})
    holiday_sources = sorted({h["source"] for h in hols})
    manifest: dict[str, Any] = {
        "today": today.isoformat(),
        "seed": seed,
        "window": {"start": start.isoformat(), "end": (today - timedelta(days=1)).isoformat()},
        "sources": {"sales": sales_source, "weather": weather_sources, "holidays": holiday_sources},
        "rows": counts,
        "notes": _notes(sales_source, weather_sources, holiday_sources, saturday),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def _notes(sales_source: str, weather: list[str], holidays: list[str], saturday: date) -> list[str]:
    """Honest provenance (docs/DATA.md): says what each table really came from."""
    notes = [
        "Sales: Maven Analytics 'Coffee Shop Sales' (NYC), one store, re-based to Bonn dates "
        "(weekdays kept) and mapped onto the TillDesk menu at its EUR prices."
        if sales_source == "maven"
        else "Sales: SYNTHETIC, seeded transactions (the Maven download was unavailable).",
        "Rainy-Saturday effect is synthesised: rainy Saturdays are thinned to 86% of nearby "
        "dry Saturdays.",
    ]
    if any(s.startswith("synthetic") for s in weather):
        notes.append("Weather: SYNTHETIC, seeded (Open-Meteo was unavailable).")
    else:
        notes.append("Weather: Open-Meteo archive and forecast for Bonn (CC BY 4.0).")
    notes.append(
        "Holidays: Nager.Date (DE-NW)."
        if holidays == ["nager"]
        else "Holidays: computed NRW public holidays (Nager.Date was unavailable)."
    )
    notes.append(
        f"Next Saturday ({saturday}) is set to {DEMO_FORECAST_RAIN_MM} mm of rain for the demo "
        "card (source marked demo_override)."
    )
    return notes


def main() -> None:
    settings = Settings()
    parser = argparse.ArgumentParser(
        prog="backroom-data", description=(__doc__ or "").split("\n")[0]
    )
    parser.add_argument("command", choices=["all"], help="build every table")
    parser.add_argument("--offline", action="store_true", help="no downloads; cache or synthetic")
    parser.add_argument("--today", type=date.fromisoformat, default=settings.today)
    parser.add_argument("--seed", type=int, default=settings.data_seed)
    parser.add_argument("--out", type=Path, default=DATA_DIR / "out")
    parser.add_argument("--raw", type=Path, default=DATA_DIR / "raw")
    args = parser.parse_args()
    manifest = build(args.today, args.seed, args.out, args.raw, offline=args.offline)
    rows = ", ".join(f"{k} {v}" for k, v in manifest["rows"].items())
    print(f"backroom-data: wrote {args.out} ({rows})", file=sys.stderr)
    print(f"backroom-data: sources {manifest['sources']}", file=sys.stderr)
