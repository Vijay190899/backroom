"""L4: the data pipeline, on tiny fixtures and fully offline."""

import io
import json
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from backroom_data import cli, parquet, sales, sources, world

TODAY = date(2026, 11, 13)  # a Friday
DATA = Path(cli.__file__).resolve().parents[1]


def tiny_xlsx(rows: list[list[str | float]]) -> io.BytesIO:
    """A one-sheet workbook with the Maven header, strings shared like Excel writes them."""
    header = [
        "transaction_id",
        "transaction_date",
        "transaction_time",
        "transaction_qty",
        "store_id",
        "store_location",
        "product_id",
        "unit_price",
        "product_category",
        "product_type",
        "product_detail",
    ]
    strings: list[str] = []

    def cell(col: int, row: int, value: str | float) -> str:
        ref = f"{'ABCDEFGHIJK'[col]}{row}"
        if isinstance(value, str):
            if value not in strings:
                strings.append(value)
            return f'<c r="{ref}" t="s"><v>{strings.index(value)}</v></c>'
        return f'<c r="{ref}"><v>{value}</v></c>'

    body = "".join(
        f'<row r="{r + 1}">' + "".join(cell(c, r + 1, v) for c, v in enumerate(values)) + "</row>"
        for r, values in enumerate([header, *rows])
    )
    ns = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
    shared = "".join(f"<si><t>{s}</t></si>" for s in strings)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(
            "xl/worksheets/sheet1.xml", f"<worksheet {ns}><sheetData>{body}</sheetData></worksheet>"
        )
        z.writestr("xl/sharedStrings.xml", f"<sst {ns}>{shared}</sst>")
    buf.seek(0)
    return buf


HK = "Hell's Kitchen"
ROWS: list[list[str | float]] = [
    # id, date serial (44927 = 2023-01-01, a Sunday), time, qty, store, location, pid, usd,
    [1, 44927, 0.5, 2, 8, HK, 32, 3.0, "Coffee", "Barista Espresso", "Latte Rg"],
    [2, 44927, 0.25, 1, 8, HK, 59, 3.5, "Bakery", "Scone", "Oatmeal Scone"],
    [3, 44928, 0.75, 1, 8, HK, 1, 2.5, "Tea", "Brewed Chai tea", "Spicy Eye Opener Chai"],
    [4, 44928, 0.75, 1, 5, "Astoria", 32, 3.0, "Coffee", "Drip coffee", "Our Old Time Diner"],
]


def test_xlsx_reader_streams_rows_with_shared_strings() -> None:
    from backroom_data import xlsx

    rows = list(xlsx.rows(tiny_xlsx(ROWS)))
    assert len(rows) == 4
    assert rows[0]["store_location"] == HK and rows[0]["transaction_date"] == "44927"


def test_maven_rows_are_filtered_mapped_and_converted() -> None:
    store, rules = sales.load_map(DATA / "seed" / "product_map.yaml")
    parsed = sales.parse_maven(tiny_xlsx(ROWS), store, rules)
    assert [(s.transaction_id, s.item_id, s.qty) for s in parsed] == [
        (1, "oat-latte", 2),
        (2, "franzbroetchen", 1),
    ]  # tea is not on the menu; Astoria is another store
    assert parsed[0].ts == datetime(2023, 1, 1, 12, 0)
    assert parsed[1].unit_price_eur == 3.20 and parsed[1].source_unit_price_usd == 3.5


def test_rebase_ends_yesterday_and_keeps_weekdays() -> None:
    days = [date(2023, 6, 20) + timedelta(days=i) for i in range(11)]  # ends Fri 30 Jun
    original = [
        sales.Sale(i, datetime.combine(d, datetime.min.time()), "espresso", 1, 2.4, "maven", 2.0)
        for i, d in enumerate(days)
    ]
    moved = sales.rebase(original, TODAY)
    assert max(s.ts.date() for s in moved) == TODAY - timedelta(days=1)
    by_id = {s.transaction_id: s for s in original}
    assert all(s.ts.weekday() == by_id[s.transaction_id].ts.weekday() for s in moved)
    assert len(moved) < len(original)  # the tail after the last Thursday was trimmed


def test_rainy_saturdays_are_calibrated_to_minus_14_percent() -> None:
    sats = [TODAY + timedelta(days=1) - timedelta(weeks=w) for w in range(1, 9)]
    rows, tx = [], 0
    for day in sats:
        for _ in range(100):
            tx += 1
            rows.append(
                sales.Sale(
                    tx, datetime.combine(day, datetime.min.time()), "espresso", 1, 2.4, "x", None
                )
            )
    rainy = set(sats[:3])
    kept = sales.apply_rainy_saturdays(rows, rainy, seed=1)
    count = {d: sum(1 for s in kept if s.ts.date() == d) for d in sats}
    assert all(count[d] == 86 for d in rainy) and all(count[d] == 100 for d in sats[3:])
    assert kept == sales.apply_rainy_saturdays(rows, rainy, seed=1)


def test_easter_and_computed_holidays() -> None:
    assert sources.easter(2026) == date(2026, 4, 5)
    assert sources.easter(2027) == date(2027, 3, 28)
    names = {h["name"] for h in sources.computed_nrw_holidays(2026)}
    assert {"Corpus Christi", "All Saints' Day", "Whit Monday"} <= names


def test_weather_json_parsing_drops_missing_days() -> None:
    body = json.dumps(
        {
            "daily": {
                "time": ["2026-11-01", "2026-11-02"],
                "precipitation_sum": [3.1, None],
                "temperature_2m_max": [10, 11],
                "temperature_2m_min": [3, 4],
            }
        }
    ).encode()
    parsed = sources._parse_daily(body, "archive")  # pyright: ignore[reportPrivateUsage]
    assert parsed[date(2026, 11, 1)]["precip_mm"] == 3.1
    assert parsed[date(2026, 11, 2)]["precip_mm"] is None


def test_franzbroetchen_unit_cost_tells_the_story() -> None:
    recipes = world.load_recipes(DATA / "recipes.yaml")
    before = world.unit_cost(recipes["franzbroetchen"], TODAY - timedelta(days=10), TODAY)
    after = world.unit_cost(recipes["franzbroetchen"], TODAY, TODAY)
    assert (round(before, 2), round(after, 2)) == (0.93, 1.02)
    assert round(0.0775 * 7.10, 2) == 0.55  # butter's share before the rise


# --- the whole build, offline -------------------------------------------------------------------


@pytest.fixture(scope="module")
def built(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict[str, object]]:
    out = tmp_path_factory.mktemp("out")
    raw = tmp_path_factory.mktemp("raw")  # empty: forces every fallback
    manifest = cli.build(TODAY, 44, out, raw, offline=True)
    return out, manifest


def test_offline_build_falls_back_to_synthetic_data(built: tuple[Path, dict[str, object]]) -> None:
    out, manifest = built
    assert manifest["sources"] == {
        "sales": "synthetic",
        "weather": ["synthetic", "synthetic+demo_override"],
        "holidays": ["computed"],
    }
    for name in ("sales", "weather", "inventory", "supplier_prices", "unit_costs", "rota"):
        assert (out / f"{name}.parquet").exists(), name


def test_build_is_idempotent(built: tuple[Path, dict[str, object]], tmp_path: Path) -> None:
    out, _ = built
    again = cli.build(TODAY, 44, tmp_path, tmp_path / "raw", offline=True)
    assert again == json.loads((out / "manifest.json").read_text())
    for name in ("sales", "inventory", "weather"):
        assert parquet.read(tmp_path / f"{name}.parquet") == parquet.read(out / f"{name}.parquet")


def test_story_numbers_come_out_of_the_built_data(built: tuple[Path, dict[str, object]]) -> None:
    import duckdb

    out, _ = built
    con = duckdb.connect()
    inv = str(out / "inventory.parquet")
    closing, velocity = con.execute(
        f"select (select closing from '{inv}' where sku = 'OAT-1L' order by date desc limit 1),"
        f" (select avg(used) from (select used from '{inv}' where sku = 'OAT-1L'"
        f" order by date desc limit 7))"
    ).fetchone() or (0, 1)
    assert round(closing / velocity, 2) == 2.0
    lowest = con.execute(f"select min(closing) from '{inv}'").fetchone()
    assert lowest is not None and lowest[0] >= 0
    saturday = cli.next_saturday(TODAY)
    rain = con.execute(
        f"select precip_mm from '{out / 'weather.parquet'}' where date = ?", [saturday]
    ).fetchone()
    assert rain == (9.0,)
    last = con.execute(f"select max(date) from '{out / 'sales.parquet'}'").fetchone()
    assert last == (TODAY - timedelta(days=1),)
    shift_hours = con.execute(
        f"select count(*) from '{out / 'rota.parquet'}' where date = ? and start = '14:00'",
        [saturday],
    ).fetchone()
    assert shift_hours == (3,)  # one of the three afternoon shifts can be trimmed


# --- audit follow-ups ------------------------------------------------------------------------


def maven_zip(raw: Path, rows: list[list[str | float]]) -> None:
    raw.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(raw / "coffee_shop_sales.zip", "w") as z:
        z.writestr("Coffee Shop Sales.xlsx", tiny_xlsx(rows).getvalue())


def cached_weather(raw: Path, start: date, end: date, precip: float = 0.0) -> None:
    """Archive + forecast fixture files with exactly the names the pipeline caches."""
    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    split = TODAY - timedelta(days=1)

    def body(ds: list[date]) -> str:
        return json.dumps(
            {
                "daily": {
                    "time": [d.isoformat() for d in ds],
                    "precipitation_sum": [precip] * len(ds),
                    "temperature_2m_max": [12.0] * len(ds),
                    "temperature_2m_min": [4.0] * len(ds),
                }
            }
        )

    (raw / f"weather_archive_{start}_{split}.json").write_text(
        body([d for d in days if d <= split])
    )
    fc_start = max(start, TODAY - timedelta(days=14))
    (raw / f"weather_forecast_{fc_start}_{end}.json").write_text(
        body([d for d in days if d >= fc_start])
    )


def test_maven_path_builds_with_honest_notes(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    # Two weeks of Thursdays and Fridays in June 2023 (serials 45097.. = 2023-06-19..)
    rows: list[list[str | float]] = [
        [i, 45097 + i, 0.4, 1, 8, HK, 32, 3.0, "Coffee", "Barista Espresso", "Latte"]
        for i in range(14)
    ]
    maven_zip(raw, rows)
    manifest = cli.build(TODAY, 44, tmp_path / "out", raw, offline=True)
    assert manifest["sources"]["sales"] == "maven"
    notes = " ".join(manifest["notes"])
    assert "Maven Analytics" in notes and "Weather: SYNTHETIC" in notes
    assert "computed NRW" in notes


def test_synthetic_build_says_so_in_its_notes(built: tuple[Path, dict[str, object]]) -> None:
    _, manifest = built
    notes = " ".join(manifest["notes"])  # type: ignore[arg-type]
    assert "Sales: SYNTHETIC" in notes and "Maven Analytics" not in notes


def test_corrupt_cached_download_falls_back_to_synthetic(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "coffee_shop_sales.zip").write_bytes(b"<html>rate limited</html>")
    (raw / "holidays_DE_2026.json").write_text("<html>oops</html>")
    manifest = cli.build(TODAY, 44, tmp_path / "out", raw, offline=True)
    assert manifest["sources"]["sales"] == "synthetic"
    assert manifest["sources"]["holidays"] == ["computed"]


def test_cached_weather_and_nager_holidays_are_used(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    start = TODAY - timedelta(days=sales.SYNTHETIC_DAYS)
    cached_weather(raw, start, TODAY + timedelta(days=cli.FORECAST_DAYS))
    (raw / "holidays_DE_2026.json").write_text(
        json.dumps(
            [
                {"date": "2026-11-01", "name": "All Saints' Day", "counties": ["DE-NW", "DE-BY"]},
                {"date": "2026-10-31", "name": "Reformation Day", "counties": ["DE-BB"]},
                {"date": "2026-10-03", "name": "German Unity Day", "counties": None},
            ]
        )
    )
    out = tmp_path / "out"
    manifest = cli.build(TODAY, 44, out, raw, offline=True)
    assert manifest["sources"]["weather"] == ["archive", "forecast", "forecast+demo_override"]
    assert manifest["sources"]["holidays"] == ["nager"]
    names = {row[1] for row in parquet.read(out / "holidays.parquet")}
    assert names == {"All Saints' Day", "German Unity Day"}  # Reformation Day isn't NRW


def test_one_missing_weather_day_switches_to_synthetic(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    start = TODAY - timedelta(days=sales.SYNTHETIC_DAYS)
    end = TODAY + timedelta(days=cli.FORECAST_DAYS)
    cached_weather(raw, start, end)
    forecast = next(raw.glob("weather_forecast_*.json"))
    data = json.loads(forecast.read_text())
    data["daily"]["precipitation_sum"][-1] = None  # the last forecast day is missing
    forecast.write_text(json.dumps(data))
    manifest = cli.build(TODAY, 44, tmp_path / "out", raw, offline=True)
    assert manifest["sources"]["weather"] == ["synthetic", "synthetic+demo_override"]


def test_build_is_idempotent_for_every_table(
    built: tuple[Path, dict[str, object]], tmp_path: Path
) -> None:
    out, _ = built
    cli.build(TODAY, 44, tmp_path, tmp_path / "raw", offline=True)
    for name in cli.SCHEMAS:
        assert (tmp_path / f"{name}.parquet").read_bytes() == (out / f"{name}.parquet").read_bytes()


def test_rain_effect_follows_the_local_trend() -> None:
    # Volume doubles over 12 weeks; the rainy Saturday is compared with its neighbours.
    sats = [TODAY + timedelta(days=1) - timedelta(weeks=w) for w in range(12, 0, -1)]
    rows, tx = [], 0
    for week, day in enumerate(sats):
        for _ in range(100 + 10 * week):
            tx += 1
            ts = datetime.combine(day, datetime.min.time())
            rows.append(sales.Sale(tx, ts, "espresso", 1, 2.4, "x", None))
    rainy = {sats[9]}
    kept = sales.apply_rainy_saturdays(rows, rainy, seed=1)
    neighbours = [100 + 10 * w for w in range(6, 12) if w != 9]  # within 3 weeks
    expected = round(0.86 * sum(neighbours) / len(neighbours))
    assert sum(1 for s in kept if s.ts.date() == sats[9]) == expected


def test_inventory_covers_only_the_order_window(built: tuple[Path, dict[str, object]]) -> None:
    out, _ = built
    days = {row[0] for row in parquet.read(out / "inventory.parquet")}
    assert min(days) == TODAY - timedelta(days=28) and max(days) == TODAY - timedelta(days=1)
