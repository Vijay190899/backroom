"""The owner's preferences and business rules, as the brief pipeline uses them.

They live in memory (L5): preferences as `has_preference` facts and business rules
(the 70% margin target) as `has_rule` facts on the business. Rules with a known shape
are applied by code (a price cap re-proposes prices; order days schedule the reorder);
every preference and rule also goes to the verifier model, which can veto a card that
goes against one it cites.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

from psycopg import Connection

from backroom_api.memory.store import facts_as_of

BUSINESS = "business:hafer-und-bohne"
WEEKDAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


def weekday_index(name: str) -> int | None:
    """ "Tue", "tuesday", "TUE" -> 1; anything else -> None."""
    key = str(name).strip().lower()[:3]
    return WEEKDAYS.index(key) if key in WEEKDAYS else None


def _weekdays(rule: dict[str, Any]) -> set[int]:
    return {i for i in (weekday_index(d) for d in rule.get("weekdays", [])) if i is not None}


@dataclass(frozen=True)
class Preference:
    id: str  # the preference entity, e.g. "preference:max-price-increase"
    text: str
    rule: dict[str, Any]


@dataclass(frozen=True)
class Rules:
    preferences: list[Preference] = field(default_factory=list[Preference])
    business_rules: list[Preference] = field(default_factory=list[Preference])

    @property
    def all_rules(self) -> list[Preference]:
        """Everything the verifier may cite."""
        return [*self.preferences, *self.business_rules]

    @property
    def max_price_increase_pct(self) -> float | None:
        caps = [
            float(p.rule["max_price_increase_pct"])
            for p in self.preferences
            if "max_price_increase_pct" in p.rule
        ]
        return min(caps) if caps else None

    def order_weekdays(self, supplier: str) -> set[int] | None:
        """The weekdays the owner orders from `supplier` on, if she set any."""
        for p in self.preferences:
            if p.rule.get("supplier") == supplier and _weekdays(p.rule):
                return _weekdays(p.rule)
        return None

    @staticmethod
    def next_order_day(today: date, allowed: set[int]) -> date:
        day = today
        while day.weekday() not in allowed:
            day += timedelta(days=1)
        return day

    def enforced_by_code(
        self,
        preference_id: str,
        params: dict[str, Any],
        numbers: dict[str, float],
        portal: str | None,
    ) -> bool:
        """True when `preference_id` is a rule code applies and this card satisfies it.
        A model's veto citing such a rule is overruled: judgment can't override
        arithmetic that was already checked."""
        pref = next((p for p in self.preferences if p.id == preference_id), None)
        if pref is None:
            return False
        if "max_price_increase_pct" in pref.rule and "price_increase_pct" in numbers:
            return numbers["price_increase_pct"] <= float(pref.rule["max_price_increase_pct"])
        days = _weekdays(pref.rule)
        if days and "order_on" in params and pref.rule.get("supplier") == portal:
            return date.fromisoformat(params["order_on"]).weekday() in days
        return False


def rules_from_memory(conn: Connection[Any], as_of: datetime) -> Rules:
    """The business's preferences and rules valid at `as_of`."""
    facts = [
        f
        for f in facts_as_of(conn, as_of)
        if f["subject_id"] == BUSINESS and f["predicate"] in ("has_preference", "has_rule")
    ]
    names = dict(
        conn.execute(
            "select id, name from entity where id = any(%s)", [[f["object_id"] for f in facts]]
        ).fetchall()
    )
    prefs: list[Preference] = []
    business: list[Preference] = []
    for f in sorted(facts, key=lambda f: f["object_id"]):
        item = Preference(f["object_id"], names.get(f["object_id"], ""), f["value"] or {})
        (prefs if f["predicate"] == "has_preference" else business).append(item)
    return Rules(preferences=prefs, business_rules=business)
