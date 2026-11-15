"""Template copy: the fallback when the planner is unavailable or its copy fails the
number guard twice. Built only from the candidate's own numbers via `guard.display`, so
it passes the guard by construction (tested)."""

from backroom_api.brief.guard import display
from backroom_api.contracts.candidate import Candidate, EvidenceNumber


def _numbers(candidate: Candidate) -> dict[str, EvidenceNumber]:
    return {n.key: n for n in candidate.numbers}


def _pack_word(n: EvidenceNumber) -> str:
    # The qty label is "<Packs> to order", e.g. "Cartons to order".
    return n.label.split(" ")[0].lower()


def copy_for(candidate: Candidate) -> tuple[str, str]:
    """(title, why) for a candidate, in plain owner-facing English."""
    n = _numbers(candidate)
    d = {k: display(v) for k, v in n.items()}
    title = candidate.title_hint
    if candidate.kind == "stockout" and {"days_left", "qty", "order_total_eur"} <= n.keys():
        thing = title.removeprefix("Reorder ").strip()
        why = (
            f"{thing.capitalize()} runs out in {d['days_left']} at this week's pace; "
            f"{d['qty']} {_pack_word(n['qty'])} for {d['order_total_eur']}"
            + (f" cover {d['cover_days']}." if "cover_days" in d else ".")
        )
    elif candidate.kind == "margin_erosion" and {"price_now_eur", "price_new_eur"} <= n.keys():
        driver = n["driver_increase_pct"].label.removesuffix(" price change")
        why = (
            f"{driver} is up {d['driver_increase_pct']}, so each one costs "
            f"{d['unit_cost_after_eur']} to make and the margin fell from "
            f"{d['margin_before_pct']} to {d['margin_after_pct']}, under your "
            f"{d['margin_target_pct']} target; {d['price_now_eur']} → {d['price_new_eur']} "
            f"brings it to {d['margin_new_pct']}."
        )
    elif candidate.kind == "weather_demand" and {"rain_mm", "footfall_change_pct"} <= n.keys():
        why = (
            f"Saturday's forecast is {d['rain_mm']} of rain and rainy Saturdays sell "
            f"{d['footfall_change_pct']} less; trimming one afternoon shift "
            f"({d['shift_hours']}) saves {d['impact_eur_weekly']}."
        )
    else:
        why = f"Worth about {d['impact_eur_weekly']} a week."
    return title, why
