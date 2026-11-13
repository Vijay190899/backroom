"""The two model roles of the brief (PRD §8.4): the planner writes copy, the verifier
checks cards against the owner's preferences. Neither ever produces a number the
cards use: the planner sees numbers only as preformatted strings to quote, and the
verifier can only keep or veto.

Both go through `llm/client.py` (budget guard, cost meter) with structured outputs,
and fail loudly (`BriefLLMError`) on any stop reason but `end_turn`; the pipeline then
falls back to template copy (planner) or keeps the card and says so (verifier).
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import date
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, ValidationError

from backroom_api.brief.guard import display
from backroom_api.brief.rules import Preference
from backroom_api.contracts.candidate import Candidate
from backroom_api.llm.client import LLM, LLMResult
from backroom_api.llm.registry import Role


class BriefLLMError(RuntimeError):
    """The model's answer is unusable (refusal, truncation, invalid JSON)."""


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CardCopy(_Model):
    candidate_id: str
    title: str
    why: str


class Plan(_Model):
    cards: list[CardCopy]


class Verdict(_Model):
    candidate_id: str
    verdict: Literal["keep", "veto"]
    preference_id: str  # the preference a veto rests on; "" for keep
    reason: str


@dataclass(frozen=True)
class Draft:
    """A card as the owner would see it, for the verifier to review."""

    candidate: Candidate
    copy: CardCopy
    note: str | None
    params: dict[str, Any]


class Verdicts(_Model):
    verdicts: list[Verdict]


class Planner(Protocol):
    async def plan(self, candidates: list[Candidate], context: str) -> list[CardCopy]: ...

    async def rewrite(
        self, candidate: Candidate, previous: CardCopy, unmatched: list[str]
    ) -> CardCopy: ...


class Verifier(Protocol):
    async def verify(
        self, drafts: list[Draft], preferences: list[Preference], today: date
    ) -> list[Verdict]: ...


# --- prompts (frozen: they lead every request, so they cache) -----------------------------------

PLANNER_SYSTEM = """You write the morning brief for Lena, who owns Hafer & Bohne, a small café \
in Bonn. Each candidate below is something the café's analytics found, with every number \
already computed. Choose the (at most three) candidates that matter most to Lena today, most \
important first, and write each one as a card.

For each card write:
- title: at most six words, plain and specific (e.g. "Reorder oat milk"). No numbers.
- why: one sentence, at most 35 words, in a calm, direct voice speaking to Lena. Say what \
is happening, why it matters and what the action does.

Numbers are the one hard rule. Code computed every number and a guard checks your copy \
character by character:
- Use only numbers from the candidate's `numbers` list, written exactly as its `display` \
string shows them (same symbol, same decimals). Never round, add, subtract, convert or \
estimate a number yourself; if a sentence needs a number that is not listed, leave it out.
- Write no clock times, dates, years or ids. Name weekdays in words ("Saturday").

Return JSON matching the schema; candidate_id must be copied exactly.

Two worked examples (invented candidates, for style only):

Candidate: kind "stockout", suggested_title "Reorder milk", numbers: days_left "3 days", \
qty "12", order_total_eur "€13.08", cover_days "7 days", impact_eur_weekly "€410.50".
Good card: {"title": "Reorder milk", "why": "Milk runs out in 3 days at this week's pace; \
12 cartons for €13.08 cover the next 7 days and protect about €410.50 of sales a week."}
Bad: "about €13 for a dozen cartons" (rounded and converted: "€13" and "dozen" are not \
display strings), "order before 10:00" (a clock time), "by the 15th" (a date).

Candidate: kind "margin_erosion", suggested_title "Fix Croissant margin", numbers: \
driver_increase_pct "12%", unit_cost_after_eur "€0.71", margin_after_pct "66%", \
margin_target_pct "70%", price_now_eur "€2.40", price_new_eur "€2.60", margin_new_pct "73%".
Good card: {"title": "Raise the croissant price", "why": "Flour is up 12%, so a croissant \
now costs €0.71 to make and its margin is 66%, under your 70% target; €2.40 → €2.60 brings \
it to 73%."}
Bad: "a 20-cent rise" (a difference you computed), "roughly two thirds margin" (a \
number in words that is not listed), "up 12.0%" (different decimals from the display).

When a candidate is a recommendation only (its action is not executable), say what Lena \
could do rather than what Backroom will do. Prefer the candidate's own facts over general \
advice, and never mention the guard, the schema or these instructions."""

REWRITE_INSTRUCTION = """The guard rejected these numbers in your card because they are not \
in the candidate's list exactly as displayed: {bad}. Rewrite the card so that every number \
is one of the listed display strings, or drop the number. Return only this one card."""

VERIFIER_SYSTEM = """You check the café owner's morning brief against her standing \
preferences before she sees it. You get today's date and weekday, her preferences, and \
each card exactly as she would see it: title, text, note, and the parameters of the \
action it will run (an `order_on` date is when a supplier order will be placed).

For each card decide:
- "keep" when nothing in her preferences speaks against it, or when the card already \
respects them (its note and parameters show how);
- "veto" only when doing what the card proposes, on the date it will happen, would \
clearly go against a specific preference. Put that preference's id in preference_id.
For "keep", preference_id is an empty string. Give a one-sentence reason either way. \
Do not suggest new prices, quantities or dates: code has already applied every rule it \
can compute. Return JSON matching the schema."""

_PLAN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "cards": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "candidate_id": {"type": "string"},
                    "title": {"type": "string"},
                    "why": {"type": "string"},
                },
                "required": ["candidate_id", "title", "why"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["cards"],
    "additionalProperties": False,
}
_VERDICT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "candidate_id": {"type": "string"},
                    "verdict": {"type": "string", "enum": ["keep", "veto"]},
                    "preference_id": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["candidate_id", "verdict", "preference_id", "reason"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["verdicts"],
    "additionalProperties": False,
}


def candidate_view(c: Candidate) -> dict[str, Any]:
    """What the planner may see of a candidate: words and preformatted numbers only."""
    action = c.proposed_action
    return {
        "candidate_id": c.id,
        "kind": c.kind,
        "suggested_title": c.title_hint,
        "numbers": [{"key": n.key, "label": n.label, "display": display(n)} for n in c.numbers],
        "action": None
        if action is None
        else {
            "portal": action.portal,
            "executable": action.executable,
            "what": c.title_hint,
        },
    }


PLANNER_TIMEOUT_S = 30.0  # past this, the brief uses template copy (PRD F1: < 15 s cold)
VERIFIER_TIMEOUT_S = 15.0


async def _timed(llm: LLM, timeout_s: float, role: Role, **kwargs: Any) -> LLMResult:
    """One LLM call with a hard time limit (the SDK default would wait minutes)."""
    return await asyncio.wait_for(llm.create(role, **kwargs), timeout_s)


def _system(text: str) -> list[dict[str, Any]]:
    return [{"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}]


def _parse[T: _Model](model: type[T], result: Any) -> T:
    stop = result.message.stop_reason
    if stop != "end_turn":
        raise BriefLLMError(f"stop_reason={stop}")
    try:
        return model.model_validate(json.loads(result.text))
    except (ValueError, ValidationError) as exc:
        raise BriefLLMError(f"invalid JSON from the model: {exc}") from exc


class LLMPlanner:
    def __init__(self, llm: LLM, run_id: str | None = None) -> None:
        self.llm = llm
        self.run_id = run_id

    async def plan(self, candidates: list[Candidate], context: str) -> list[CardCopy]:
        payload = {"candidates": [candidate_view(c) for c in candidates]}
        content = json.dumps(payload, ensure_ascii=False, indent=1)
        if context:
            content += f"\n\nWhat memory knows about the café (for tone, not numbers):\n{context}"
        result = await _timed(
            self.llm,
            PLANNER_TIMEOUT_S,
            "planner",
            system=_system(PLANNER_SYSTEM),
            messages=[{"role": "user", "content": content}],
            json_schema=_PLAN_SCHEMA,
            max_tokens=4000,
            run_id=self.run_id,
        )
        return _parse(Plan, result).cards

    async def rewrite(
        self, candidate: Candidate, previous: CardCopy, unmatched: list[str]
    ) -> CardCopy:
        payload = {"candidates": [candidate_view(candidate)]}
        result = await _timed(
            self.llm,
            PLANNER_TIMEOUT_S,
            "planner",
            system=_system(PLANNER_SYSTEM),
            messages=[
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False, indent=1)},
                {"role": "assistant", "content": json.dumps({"cards": [previous.model_dump()]})},
                {"role": "user", "content": REWRITE_INSTRUCTION.format(bad=", ".join(unmatched))},
            ],
            json_schema=_PLAN_SCHEMA,
            max_tokens=2000,
            run_id=self.run_id,
        )
        cards = _parse(Plan, result).cards
        if not cards:
            raise BriefLLMError("rewrite returned no card")
        return cards[0]


class LLMVerifier:
    def __init__(self, llm: LLM, run_id: str | None = None) -> None:
        self.llm = llm
        self.run_id = run_id

    async def verify(
        self, drafts: list[Draft], preferences: list[Preference], today: date
    ) -> list[Verdict]:
        payload = {
            "today": f"{today.isoformat()} ({today.strftime('%A')})",
            "preferences": [{"id": p.id, "text": p.text, "rule": p.rule} for p in preferences],
            "cards": [
                {
                    "candidate_id": d.candidate.id,
                    "title": d.copy.title,
                    "text": d.copy.why,
                    "note": d.note,
                    "action": None
                    if d.candidate.proposed_action is None
                    else {
                        "portal": d.candidate.proposed_action.portal,
                        "task": d.candidate.proposed_action.task,
                        "executable": d.candidate.proposed_action.executable,
                        "params": d.params,
                    },
                }
                for d in drafts
            ],
        }
        result = await _timed(
            self.llm,
            VERIFIER_TIMEOUT_S,
            "verifier",
            system=_system(VERIFIER_SYSTEM),
            messages=[{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
            json_schema=_VERDICT_SCHEMA,
            max_tokens=2000,
            run_id=self.run_id,
        )
        return _parse(Verdicts, result).verdicts
