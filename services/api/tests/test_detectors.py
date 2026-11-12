"""L6: detectors on an offline (synthetic) build of the L4 data, plus pricing."""

from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import duckdb
import pytest

from backroom_api.analytics import detectors, pricing
from backroom_api.analytics.detectors import run_all
from backroom_api.contracts.candidate import Candidate

TODAY = date(2026, 11, 13)
NOW = datetime(2026, 11, 13, 6, 0, tzinfo=ZoneInfo("Europe/Berlin"))


@pytest.fixture(scope="module")
def data_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from backroom_data import cli

    out = tmp_path_factory.mktemp("out")
    cli.build(TODAY, 44, out, tmp_path_factory.mktemp("raw"), offline=True)
    return out


@pytest.fixture(scope="module")
def candidates(data_dir: Path) -> dict[str, Candidate]:
    found = run_all(data_dir, now=NOW)
    assert [c.impact_eur_weekly for c in found] == sorted(
        (c.impact_eur_weekly for c in found), reverse=True
    )
    return {c.kind: c for c in found}


def numbers(c: Candidate) -> dict[str, float]:
    return {n.key: n.value for n in c.numbers}


def test_all_three_detectors_fire(candidates: dict[str, Candidate]) -> None:
    assert set(candidates) == {"stockout", "margin_erosion", "weather_demand"}


def test_franzbroetchen_margin_story_comes_out_of_the_data(
    candidates: dict[str, Candidate],
) -> None:
    c = candidates["margin_erosion"]
    assert c.id == f"margin_erosion:product:franzbroetchen:{TODAY}"
    n = numbers(c)
    assert (round(n["driver_increase_pct"]), n["driver_cost_before_eur"]) == (16, 0.55)
    assert (n["driver_cost_now_eur"], n["cost_rise_eur"]) == (0.64, 0.09)
    assert (n["unit_cost_before_eur"], n["unit_cost_after_eur"]) == (0.93, 1.02)
    assert (n["margin_before_pct"], n["margin_after_pct"], n["margin_target_pct"]) == (71, 68, 70)
    assert (n["price_now_eur"], n["price_new_eur"], n["price_increase_pct"]) == (3.2, 3.6, 12.5)
    assert n["margin_new_pct"] == 72
    assert c.proposed_action is not None
    assert c.proposed_action.params == {"item_id": "franzbroetchen", "price_eur": 3.6}
    assert n["impact_eur_weekly"] == round(n["units_weekly"] * 0.40, 2)


def test_owner_cap_reproposes_within_it(data_dir: Path) -> None:
    capped = {c.kind: c for c in run_all(data_dir, now=NOW, max_price_increase_pct=8)}
    n = numbers(capped["margin_erosion"])
    assert (n["price_new_eur"], n["price_increase_pct"], n["margin_new_pct"]) == (3.45, 7.8, 70)
    assert n["max_price_increase_pct"] == 8


def test_only_eroded_items_get_a_card(candidates: dict[str, Candidate]) -> None:
    assert [c.subject_id for c in candidates.values() if c.kind == "margin_erosion"] == [
        "product:franzbroetchen"
    ]


def test_weekly_windows_are_seven_full_days(
    data_dir: Path, candidates: dict[str, Candidate]
) -> None:
    con = duckdb.connect()
    days, units = con.execute(
        f"select count(distinct date), sum(qty) from '{data_dir / 'sales.parquet'}' "
        "where item_id = 'franzbroetchen' and date >= ? and date < ?",
        [TODAY - timedelta(days=7), TODAY],
    ).fetchone() or (0, 0)
    assert days == 7
    assert numbers(candidates["margin_erosion"])["units_weekly"] == units


def test_oat_milk_stockout(candidates: dict[str, Candidate]) -> None:
    c = candidates["stockout"]
    n = numbers(c)
    assert c.subject_id == "ingredient:oat-milk" and n["days_left"] == 2.0
    assert n["order_total_eur"] == round(n["qty"] * n["unit_price_eur"], 2)
    assert n["qty"] >= 7 * n["use_per_day_packs"] - n["stock_left_packs"] - 0.5  # a week of cover
    assert c.proposed_action is not None and c.proposed_action.task == "grainline.reorder_item"
    assert c.evidence[0].synthetic  # inventory is simulated
    assert "?" not in (c.evidence[0].sql or "")  # parameters are shown inline


def test_rainy_saturday_is_a_recommendation(candidates: dict[str, Candidate]) -> None:
    c = candidates["weather_demand"]
    n = numbers(c)
    assert n["rain_mm"] == 9.0 and n["footfall_change_pct"] <= -10
    assert (n["late_shifts"], n["shift_hours"], n["impact_eur_weekly"]) == (3, 4.0, 58.0)
    assert c.proposed_action is not None and not c.proposed_action.executable


def test_every_card_lists_its_impact_and_ids_are_deterministic(
    candidates: dict[str, Candidate],
) -> None:
    for c in candidates.values():
        n = numbers(c)
        assert n["impact_eur_weekly"] == c.impact_eur_weekly
        assert len(n) == len(c.numbers)  # no duplicate keys
        assert c.id.endswith(str(TODAY)) and c.computed_at == NOW


def test_a_date_the_data_was_not_built_for_is_refused(data_dir: Path) -> None:
    with pytest.raises(ValueError, match="built for"):
        run_all(data_dir, as_of=TODAY - timedelta(days=3))


def test_rain_rules_match_the_data_pipeline() -> None:
    from backroom_data import sales

    assert detectors.RAIN_MM == sales.RAIN_MM
    assert detectors.NEIGHBOUR_DAYS == 7 * sales.NEIGHBOUR_WEEKS


# --- pricing ------------------------------------------------------------------------------


def test_price_proposal_reaches_target_plus_buffer() -> None:
    p = pricing.propose_price(cost_eur=1.0192, price_eur=3.20, target_pct=70)
    assert (p.price_eur, p.increase_pct, pricing.round_half_up(p.margin_pct)) == (3.60, 12.5, 72)
    assert p.meets_target and not p.capped


def test_owner_cap_gives_the_demo_price() -> None:
    p = pricing.propose_price(cost_eur=1.0192, price_eur=3.20, target_pct=70, max_increase_pct=8)
    assert (p.price_eur, p.increase_pct, pricing.round_half_up(p.margin_pct)) == (3.45, 7.8, 70)
    assert p.capped and p.meets_target


def test_cap_that_cannot_reach_the_target_says_so_and_never_cuts() -> None:
    p = pricing.propose_price(cost_eur=1.0192, price_eur=3.20, target_pct=70, max_increase_pct=3)
    assert p.price_eur == 3.25 and not p.meets_target
    off_grid = pricing.propose_price(
        cost_eur=1.5, price_eur=3.27, target_pct=70, max_increase_pct=0.5
    )
    assert off_grid.price_eur >= 3.27


def test_rounding_is_half_up_and_bad_inputs_raise() -> None:
    assert (pricing.round_half_up(70.5), pricing.round_half_up(12.5)) == (71, 13)
    with pytest.raises(ValueError):
        pricing.propose_price(cost_eur=1, price_eur=3, target_pct=99)
    with pytest.raises(ValueError):
        pricing.propose_price(cost_eur=1, price_eur=0, target_pct=70)
