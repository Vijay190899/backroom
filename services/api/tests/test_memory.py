"""L5: the memory layer on a real Postgres (Neon on the laptop, Docker on the PC).

Each test session gets its own schema, dropped at the end, so tests never touch real
data. Without a reachable database (as in CI) the tests skip.
"""

import uuid
from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, LiteralString, cast
from zoneinfo import ZoneInfo

import psycopg
import pytest
from psycopg import sql

from backroom_api.config import REPO_ROOT, Settings
from backroom_api.memory import packer, store, writers

TODAY = date(2026, 11, 13)
BONN = ZoneInfo("Europe/Berlin")
MIGRATION = REPO_ROOT / "services" / "api" / "migrations" / "0001_memory.sql"


def at(day: date) -> datetime:
    return datetime.combine(day, datetime.min.time(), tzinfo=BONN)


@pytest.fixture(scope="module")
def conn() -> Iterator[psycopg.Connection[Any]]:
    try:
        connection = psycopg.connect(Settings().database_url, connect_timeout=5)
    except psycopg.OperationalError:
        pytest.skip("no Postgres reachable (set DATABASE_URL, e.g. Neon)")
    schema = f"test_memory_{uuid.uuid4().hex[:10]}"
    name = sql.Identifier(schema)
    connection.execute(sql.SQL("create schema {}").format(name))
    connection.execute(sql.SQL("set search_path to {}, public").format(name))
    connection.execute(cast(LiteralString, MIGRATION.read_text()))
    connection.commit()
    try:
        yield connection
    finally:
        connection.rollback()
        connection.execute(sql.SQL("drop schema {} cascade").format(name))
        connection.commit()
        connection.close()


@pytest.fixture(scope="module")
def world(conn: psycopg.Connection[Any], tmp_path_factory: pytest.TempPathFactory) -> Path:
    from backroom_data import cli

    out = tmp_path_factory.mktemp("out")
    cli.build(TODAY, 44, out, tmp_path_factory.mktemp("raw"), offline=True)
    counts = writers.write_world(conn, out)
    conn.commit()
    assert counts["seed"] > 30 and counts["invoices"] > 0
    return out


def butter_prices(conn: psycopg.Connection[Any]) -> list[tuple[Any, ...]]:
    return conn.execute(
        "select id, value, valid_from, valid_to, superseded_by, invalidated_at from fact "
        "where subject_id = 'ingredient:butter' and predicate = 'unit_price_eur_per_kg' "
        "order by valid_from"
    ).fetchall()


def test_invoices_supersede_the_butter_price(conn: psycopg.Connection[Any], world: Path) -> None:
    rows = butter_prices(conn)
    assert [r[1] for r in rows] == [7.1, 8.24]
    (_, _, _, old_to, old_by, old_inv), (new_id, _, new_from, new_to, _, _) = rows
    assert old_to == new_from and old_by == new_id and old_inv is not None and new_to is None
    assert new_from.date() >= TODAY - timedelta(days=9)  # the first invoice after the rise


def test_writer_is_idempotent(conn: psycopg.Connection[Any], world: Path) -> None:
    before = conn.execute("select count(*) from fact").fetchone()
    assert writers.write_world(conn, world) == {"seed": 0, "invoices": 0}
    assert conn.execute("select count(*) from fact").fetchone() == before
    conn.commit()


def test_graph_as_of_shows_what_was_true_then(conn: psycopg.Connection[Any], world: Path) -> None:
    def butter(day: date) -> list[Any]:
        g = store.graph(conn, at(day))
        return [
            f.value
            for f in g.facts
            if f.subject_id == "ingredient:butter" and f.predicate == "unit_price_eur_per_kg"
        ]

    assert butter(TODAY - timedelta(days=20)) == [7.1]
    assert butter(TODAY) == [8.24]
    g = store.graph(conn, at(TODAY))
    node_ids = {n.id for n in g.nodes}
    assert {"business:hafer-und-bohne", "product:franzbroetchen", "ingredient:butter"} <= node_ids
    assert all(f.subject_id in node_ids for f in g.facts)


def test_known_at_hides_facts_recorded_later(conn: psycopg.Connection[Any], world: Path) -> None:
    long_ago = datetime(2020, 1, 1, tzinfo=UTC)  # before anything was recorded
    assert store.facts_as_of(conn, at(TODAY), known_at=long_ago) == []


def test_fact_detail_has_provenance_and_chain(conn: psycopg.Connection[Any], world: Path) -> None:
    old_id, new_id = (r[0] for r in butter_prices(conn))
    detail = store.fact_detail(conn, new_id)
    assert detail is not None and detail.supersedes == [old_id] and detail.superseded_by is None
    assert detail.source is not None and detail.source.kind == "invoice"
    assert detail.source.summary.startswith("Grainline invoice INV-")
    old = store.fact_detail(conn, old_id)
    assert old is not None and old.superseded_by == new_id and old.invalidated_at is not None
    assert store.fact_detail(conn, "f_missing") is None


def test_many_valued_facts_coexist(conn: psycopg.Connection[Any], world: Path) -> None:
    uses = conn.execute(
        "select count(*) from fact where subject_id = 'product:franzbroetchen' "
        "and predicate = 'uses_ingredient' and valid_to is null"
    ).fetchone()
    assert uses == (5,)  # butter, flour, sugar, cinnamon, milk


def test_learned_cap_is_a_preference_that_can_change(
    conn: psycopg.Connection[Any], world: Path
) -> None:
    episode = store.add_episode(conn, "rejection", {"summary": "too steep, max 8%"}, at(TODAY))
    first = writers.record_preference(
        conn,
        "max-price-increase",
        "Price rises of at most 8%",
        {"max_price_increase_pct": 8},
        valid_from=at(TODAY),
        source_episode=episode,
        confidence=0.9,
    )
    again = writers.record_preference(
        conn,
        "max-price-increase",
        "Price rises of at most 8%",
        {"max_price_increase_pct": 8},
        valid_from=at(TODAY),
        source_episode=episode,
        confidence=0.9,
    )
    assert again == first  # same rule: nothing new
    later = writers.record_preference(
        conn,
        "max-price-increase",
        "Price rises of at most 10%",
        {"max_price_increase_pct": 10},
        valid_from=at(TODAY + timedelta(days=2)),
    )
    prefs = {
        f.object_id: f.value
        for f in store.graph(conn, at(TODAY + timedelta(days=3))).facts
        if f.predicate == "has_preference"
    }
    assert prefs["preference:max-price-increase"] == {"max_price_increase_pct": 10}
    assert "preference:grainline-order-days" in prefs  # the seeded Tue/Fri rule still holds
    detail = store.fact_detail(conn, later)
    assert detail is not None and detail.supersedes == [first]
    conn.rollback()


def test_back_dated_fact_is_refused(conn: psycopg.Connection[Any], world: Path) -> None:
    with pytest.raises(store.OutOfOrderFactError):
        store.assert_fact(
            conn,
            "ingredient:butter",
            "unit_price_eur_per_kg",
            value=9.0,
            valid_from=at(TODAY - timedelta(days=30)),
        )
    conn.rollback()


def test_context_pack_is_ranked_and_within_budget(
    conn: psycopg.Connection[Any], world: Path
) -> None:
    full = packer.pack(conn, ["product:franzbroetchen"], at(TODAY))
    assert full.tokens <= full.budget_tokens == packer.DEFAULT_BUDGET_TOKENS
    lines = full.text.splitlines()
    head = lines[:6]  # hop 0: the business's standing rules and the seed's own facts
    assert any("has_preference preference:grainline-order-days" in line for line in head)
    assert any("has_rule preference:margin-target" in line for line in head)
    assert any(line.startswith("product:franzbroetchen menu_price_eur") for line in lines)
    butter = [line for line in lines if "ingredient:butter unit_price_eur_per_kg" in line]
    assert len(butter) == 1 and "8.24" in butter[0]
    assert not any("7.1" in line and "butter unit_price" in line for line in lines)
    small = packer.pack(conn, ["product:franzbroetchen"], at(TODAY), budget_tokens=60)
    assert small.tokens <= 60 and small.fact_ids == full.fact_ids[: len(small.fact_ids)]


# --- audit follow-ups ----------------------------------------------------------------------


def test_concurrent_writers_leave_one_open_fact(conn: psycopg.Connection[Any], world: Path) -> None:
    """Two connections race to set the same one-valued fact; the advisory lock makes the
    second wait, then supersede the first, so exactly one stays open."""
    import threading

    schema = conn.execute("select current_schema()").fetchone()
    assert schema is not None

    def connect() -> psycopg.Connection[Any]:
        other = psycopg.connect(Settings().database_url, connect_timeout=5)
        other.execute(sql.SQL("set search_path to {}, public").format(sql.Identifier(schema[0])))
        return other

    a, b = connect(), connect()
    store.upsert_entity(a, "ingredient:race", "ingredient", "Race")
    a.commit()
    store.assert_fact(a, "ingredient:race", "stock_on_hand", value=2.0, valid_from=at(TODAY))
    done = threading.Event()

    def second() -> None:  # blocks on the lock until `a` commits
        store.assert_fact(
            b,
            "ingredient:race",
            "stock_on_hand",
            value=3.0,
            valid_from=at(TODAY + timedelta(days=1)),
        )
        b.commit()
        done.set()

    worker = threading.Thread(target=second)
    worker.start()
    assert not done.wait(1.0)  # still waiting for `a`
    a.commit()
    worker.join(10)
    assert done.is_set()
    open_values = conn.execute(
        "select value from fact where subject_id = 'ingredient:race' and valid_to is null"
    ).fetchall()
    assert open_values == [(3.0,)]
    a.close()
    b.close()


def test_known_at_between_the_two_prices(conn: psycopg.Connection[Any], world: Path) -> None:
    store.upsert_entity(conn, "ingredient:clock", "ingredient", "Clock")
    store.assert_fact(
        conn, "ingredient:clock", "unit_price_eur_per_kg", value=1.0, valid_from=at(TODAY)
    )
    conn.commit()
    between = conn.execute("select now()").fetchone()
    conn.commit()
    assert between is not None
    store.assert_fact(
        conn,
        "ingredient:clock",
        "unit_price_eur_per_kg",
        value=2.0,
        valid_from=at(TODAY + timedelta(days=1)),
    )
    conn.commit()

    def price(known_at: datetime | None) -> list[Any]:
        return [
            f["value"]
            for f in store.facts_as_of(conn, at(TODAY + timedelta(days=2)), known_at)
            if f["subject_id"] == "ingredient:clock"
        ]

    assert price(between[0]) == [1.0]  # before we learned of the change
    assert price(None) == [2.0]
    old = conn.execute(
        "select f.invalidated_at, n.recorded_at from fact f join fact n on f.superseded_by = n.id "
        "where f.subject_id = 'ingredient:clock'"
    ).fetchone()
    assert old is not None and old[0] == old[1]  # one clock: invalidated when the new row landed


def test_held_back_invoice_supersedes_when_ingested(
    conn: psycopg.Connection[Any], tmp_path_factory: pytest.TempPathFactory
) -> None:
    """The demo path (PRD F4): hold the butter-rise invoice back, then ingest it."""
    import duckdb

    from backroom_data import cli

    out = tmp_path_factory.mktemp("held")
    cli.build(TODAY, 44, out, tmp_path_factory.mktemp("raw2"), offline=True)
    own = psycopg.connect(Settings().database_url, connect_timeout=5)
    name = sql.Identifier(f"test_memory_{uuid.uuid4().hex[:10]}")
    own.execute(sql.SQL("create schema {}").format(name))
    own.execute(sql.SQL("set search_path to {}, public").format(name))
    try:
        own.execute(cast(LiteralString, MIGRATION.read_text()))
        held = writers.invoices_from_price_change(out, "BUTTER-1KG")
        assert held
        invoice = held[0]
        writers.write_world(own, out, hold_back=set(held))
        assert [r[1] for r in butter_prices(own)] == [7.1]  # the rise isn't known yet
        lines = (
            duckdb.connect()
            .execute(
                "select order_id, order_date, sku, qty, unit_price_eur "
                "from read_parquet(?) where invoice_id = ?",
                [str(out / "grainline_orders.parquet"), invoice],
            )
            .fetchall()
        )
        result = writers.write_invoice(
            own,
            invoice_id=invoice,
            order_id=lines[0][0],
            day=lines[0][1],
            lines=[{"sku": r[2], "qty": r[3], "unit_price_eur": r[4]} for r in lines],
            sizes=writers.pack_sizes(out),
        )
        assert [r[1] for r in butter_prices(own)] == [7.1, 8.24]
        assert len(result.superseded_fact_ids) >= 1 and result.fact_ids
    finally:
        own.rollback()
        own.execute(sql.SQL("drop schema if exists {} cascade").format(name))
        own.commit()
        own.close()


def test_world_has_dated_nodes_and_contract_amounts(
    conn: psycopg.Connection[Any], world: Path
) -> None:
    types = dict(conn.execute("select type, count(*) from entity group by type").fetchall())
    assert types["weather_day"] >= 14 and types.get("holiday", 0) >= 0
    amount = conn.execute(
        "select value from fact where subject_id = 'product:franzbroetchen' "
        "and object_id = 'ingredient:butter'"
    ).fetchone()
    assert amount == ({"grams": 77.5},)


def test_seeds_come_from_the_task_text(conn: psycopg.Connection[Any], world: Path) -> None:
    seeds = packer.seeds_for(conn, "Fix the Franzbrötchen margin after the butter invoice")
    assert {"product:franzbroetchen", "ingredient:butter"} <= set(seeds)
