"""Rejection -> preference (PRD F4): "too steep, max 8%" becomes a Preference fact the
next brief obeys.

The worker model reads the owner's reason and proposes a rule in a fixed shape. Code
then checks it against the reason itself: a number is accepted only if the owner wrote
it, and weekdays only if she named them. So the model can understand the sentence, but
can't originate a number (CLAUDE.md non-negotiable). The rejection is always recorded as
an episode, with or without a rule.
"""

import asyncio
import json
import re
from datetime import datetime
from typing import Any, Literal

from psycopg import Connection
from pydantic import BaseModel, ConfigDict, ValidationError

from backroom_api.contracts.api import ActionCard, RejectResponse
from backroom_api.llm.client import LLM
from backroom_api.memory.store import add_episode
from backroom_api.memory.writers import record_preference

EXTRACT_TIMEOUT_S = 15.0
_WEEKDAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
_NUMBERS = re.compile(r"\d+(?:[.,]\d+)?")


class ExtractedRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["max_price_increase_pct", "order_weekdays", "none"]
    value: float  # the cap in percent; 0 when not a cap
    weekdays: list[str]  # three-letter lowercase days; empty when not order days
    text: str  # the rule in one short sentence, in the owner's terms


EXTRACT_SYSTEM = """The owner of a café rejected a suggestion and said why. Read her \
reason and say whether it states a lasting rule of one of these shapes:
- "max_price_increase_pct": the largest price rise she accepts, in percent (value = that \
number as she wrote it);
- "order_weekdays": the only weekdays she orders from the supplier on (weekdays as \
three-letter lowercase names, e.g. "tue");
- "none": no lasting rule (a one-off objection, a mood, a question).
Use only numbers and days she actually wrote. text is the rule as one short sentence. \
Return JSON matching the schema."""

_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "kind": {"type": "string", "enum": ["max_price_increase_pct", "order_weekdays", "none"]},
        "value": {"type": "number"},
        "weekdays": {"type": "array", "items": {"type": "string"}},
        "text": {"type": "string"},
    },
    "required": ["kind", "value", "weekdays", "text"],
    "additionalProperties": False,
}


async def extract(llm: LLM, reason: str, card: ActionCard) -> ExtractedRule | None:
    """The model's reading of the reason, or None when the call fails."""
    payload = {"card": {"title": card.title, "text": card.why, "kind": card.kind}, "reason": reason}
    try:
        result = await asyncio.wait_for(
            llm.create(
                "worker",
                system=[
                    {"type": "text", "text": EXTRACT_SYSTEM, "cache_control": {"type": "ephemeral"}}
                ],
                messages=[{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
                json_schema=_SCHEMA,
                max_tokens=1000,
            ),
            EXTRACT_TIMEOUT_S,
        )
    except Exception:  # the rejection is still recorded, just without a rule
        return None
    if result.message.stop_reason != "end_turn":
        return None
    try:
        return ExtractedRule.model_validate(json.loads(result.text))
    except (ValueError, ValidationError):
        return None


def checked(rule: ExtractedRule | None, reason: str) -> ExtractedRule | None:
    """Keep the rule only if the owner's own words back it."""
    if rule is None or rule.kind == "none":
        return None
    if rule.kind == "max_price_increase_pct":
        written = {float(n.replace(",", ".")) for n in _NUMBERS.findall(reason)}
        if rule.value not in written or not 0 < rule.value < 100:
            return None
        return rule
    days = [d.strip().lower()[:3] for d in rule.weekdays]
    lowered = reason.lower()
    if not days or any(d not in _WEEKDAYS or d not in lowered for d in days):
        return None
    return rule.model_copy(update={"weekdays": days})


def record_rejection(
    conn: Connection[Any],
    *,
    card: ActionCard,
    reason: str,
    rule: ExtractedRule | None,
    at: datetime,
) -> RejectResponse:
    """POST /actions/{id}/reject: a `rejection` episode, plus a preference when the
    reason states a checked rule. The caller commits."""
    episode = add_episode(
        conn,
        "rejection",
        {
            "summary": f"Rejected: {card.title}",
            "action_id": card.id,
            "candidate_id": card.candidate_id,
            "reason": reason,
        },
        at,
    )
    facts: list[str] = []
    rule = checked(rule, reason)
    if rule is not None and rule.kind == "max_price_increase_pct":
        cap = rule.value
        facts.append(
            record_preference(
                conn,
                "max-price-increase",
                f"Price rises of at most {cap:g}%",
                {"max_price_increase_pct": cap},
                valid_from=at,
                source_episode=episode,
                confidence=0.9,
            )
        )
    elif rule is not None and rule.kind == "order_weekdays":
        days = sorted(set(rule.weekdays), key=_WEEKDAYS.index)
        facts.append(
            record_preference(
                conn,
                "grainline-order-days",
                rule.text or "Grainline order days",
                {"supplier": "grainline", "weekdays": days},
                valid_from=at,
                source_episode=episode,
                confidence=0.9,
            )
        )
    return RejectResponse(action_id=card.id, episode_id=episode, preference_fact_ids=facts)
