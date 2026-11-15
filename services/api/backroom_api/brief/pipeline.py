"""The brief pipeline (PRD §8.4): detectors -> planner -> number guard -> rules ->
verifier -> Brief. "Agents for judgment, code for math."

1. Candidates come from the detectors, already re-proposed within the owner's cap.
2. The planner picks at most three and writes their copy (words only).
3. The number guard checks every number; one regeneration, then template copy.
4. Code applies the rules it can compute (order days) and writes the preference notes.
5. The verifier may veto a card that goes against a cited preference or rule; a veto of
   a rule code already enforces and the card satisfies is overruled.

Any model failure (refusal, invalid answer, timeout, API error, spent budget) degrades
to deterministic copy or an unverified-but-kept card; it never fails the brief.
"""

import hashlib
import json
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

from backroom_api.brief import guard, templates
from backroom_api.brief.agents import CardCopy, Draft, Planner, Verdict, Verifier
from backroom_api.brief.guard import display
from backroom_api.brief.rules import Rules
from backroom_api.contracts.api import (
    ActionCard,
    Brief,
    BriefCardEvent,
    BriefDone,
    BriefSkeleton,
    GuardResult,
)
from backroom_api.contracts.candidate import Candidate

BONN = ZoneInfo("Europe/Berlin")
MAX_CARDS = 3
WEEKDAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


@dataclass
class Decision:
    candidate_id: str
    step: str  # "planner", "guard", "rewrite", "template", "rules", "verifier", "dropped"
    detail: str


@dataclass
class BriefResult:
    brief: Brief
    decisions: list[Decision] = field(default_factory=list[Decision])
    vetoed: list[str] = field(default_factory=list[str])


@dataclass
class _Drafted:
    candidate: Candidate
    copy: CardCopy
    source: str  # "llm" or "template"
    guard: GuardResult
    note: str | None
    params: dict[str, Any]


def action_id(candidate_id: str, params: dict[str, Any]) -> str:
    """Stable for the same proposal, new when the proposal changes (e.g. a re-proposal
    under a learned cap), so approve/reject never hit a stale action."""
    key = json.dumps([candidate_id, params], sort_keys=True, default=str)
    return "act_" + hashlib.sha256(key.encode()).hexdigest()[:12]


def _failure(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}"


def _guarded(copy: CardCopy, candidate: Candidate, protected: Sequence[str]) -> list[str]:
    return guard.unmatched([copy.title, copy.why], candidate.numbers, protected)


async def _copy_for(
    candidate: Candidate,
    planned: CardCopy | None,
    planner: Planner,
    protected: Sequence[str],
    decisions: list[Decision],
) -> tuple[CardCopy, str, GuardResult] | None:
    """Copy that passes the guard: the planner's, its one rewrite, or the template.
    `GuardResult.passed` says whether the model's copy passed; the copy returned always
    does. None when even the template can't be verified (the card is then dropped)."""
    unmatched: list[str] = []
    regenerations = 0
    if planned is not None:
        bad = _guarded(planned, candidate, protected)
        if not bad:
            return planned, "llm", GuardResult(passed=True, regenerations=0)
        decisions.append(Decision(candidate.id, "guard", f"rejected {bad}"))
        regenerations, unmatched = 1, bad
        try:
            rewritten = await planner.rewrite(candidate, planned, bad)
        except Exception as exc:  # any model failure: fall back to the template
            decisions.append(Decision(candidate.id, "rewrite", f"failed: {_failure(exc)}"))
        else:
            rewritten = rewritten.model_copy(update={"candidate_id": candidate.id})
            again = _guarded(rewritten, candidate, protected)
            if not again:
                decisions.append(Decision(candidate.id, "rewrite", "passed the guard"))
                return rewritten, "llm", GuardResult(passed=True, regenerations=1)
            decisions.append(Decision(candidate.id, "guard", f"rewrite rejected {again}"))
            unmatched = again
    title, why = templates.copy_for(candidate)
    template = CardCopy(candidate_id=candidate.id, title=title, why=why)
    leftover = _guarded(template, candidate, protected)
    if leftover:  # never show an unverified number: drop the card instead
        decisions.append(Decision(candidate.id, "dropped", f"template failed {leftover}"))
        return None
    decisions.append(Decision(candidate.id, "template", "template copy"))
    return (
        template,
        "template",
        GuardResult(passed=planned is None, regenerations=regenerations, unmatched=unmatched),
    )


def _rules_note(
    candidate: Candidate, rules: Rules, today: date
) -> tuple[str | None, dict[str, Any]]:
    """The preference note and any params code adds for the rules it can apply."""
    action = candidate.proposed_action
    params = dict(action.params) if action else {}
    numbers = {n.key: n for n in candidate.numbers}
    if candidate.kind == "margin_erosion" and "max_price_increase_pct" in numbers:
        return f"Kept under your {display(numbers['max_price_increase_pct'])} cap", params
    days = rules.order_weekdays(action.portal) if action and action.portal else None
    if candidate.kind == "stockout" and days:
        day = rules.next_order_day(today, days)
        weekday = WEEKDAY_NAMES[day.weekday()]
        params["order_on"] = day.isoformat()
        if day == today:
            return f"Ordering today, {weekday}, a Grainline order day", params
        return f"Scheduled for {weekday}, your next Grainline order day", params
    return None, params


async def _plan(
    planner: Planner, ranked: list[Candidate], context: str, decisions: list[Decision]
) -> tuple[list[str], dict[str, CardCopy]]:
    by_id = {c.id: c for c in ranked}
    planned: dict[str, CardCopy] = {}
    order: list[str] = []
    try:
        for copy in await planner.plan(ranked, context):
            if copy.candidate_id in by_id and copy.candidate_id not in planned:
                planned[copy.candidate_id] = copy
                order.append(copy.candidate_id)
            else:
                decisions.append(Decision(copy.candidate_id, "planner", "unknown or duplicate id"))
    except Exception as exc:  # any model failure: the top candidates in template copy
        decisions.append(Decision("*", "planner", f"failed: {_failure(exc)}"))
    if len(order) > MAX_CARDS:
        decisions.append(Decision("*", "planner", f"returned {len(order)} cards; kept 3"))
    if not order:
        order = [c.id for c in ranked]
    return order[:MAX_CARDS], planned


async def _verify(
    verifier: Verifier,
    drafted: list[_Drafted],
    rules: Rules,
    today: date,
    decisions: list[Decision],
) -> list[str]:
    """Candidate ids the verifier vetoed, after code's checks."""
    citable = {p.id for p in rules.all_rules}
    if not citable or not drafted:
        return []  # nothing to check the cards against
    try:
        verdicts: list[Verdict] = await verifier.verify(
            [Draft(d.candidate, d.copy, d.note, d.params) for d in drafted],
            rules.all_rules,
            today,
        )
    except Exception as exc:  # unverified cards stay: the rules code applies still hold
        decisions.append(Decision("*", "verifier", f"unavailable, cards kept: {_failure(exc)}"))
        return []
    by_id = {d.candidate.id: d for d in drafted}
    vetoed: list[str] = []
    for v in verdicts:
        decisions.append(Decision(v.candidate_id, "verifier", f"{v.verdict}: {v.reason}"))
        if v.verdict != "veto" or v.candidate_id not in by_id:
            continue
        if v.preference_id not in citable:
            decisions.append(
                Decision(
                    v.candidate_id,
                    "verifier",
                    f"veto ignored: cites no known rule ({v.preference_id!r})",
                )
            )
            continue
        d = by_id[v.candidate_id]
        numbers = {n.key: n.value for n in d.candidate.numbers}
        portal = d.candidate.proposed_action.portal if d.candidate.proposed_action else None
        if rules.enforced_by_code(v.preference_id, d.params, numbers, portal):
            decisions.append(
                Decision(
                    v.candidate_id,
                    "verifier",
                    f"veto overruled: code already applies {v.preference_id}",
                )
            )
            continue
        vetoed.append(v.candidate_id)
    return vetoed


async def generate(
    candidates: list[Candidate],
    *,
    planner: Planner,
    verifier: Verifier,
    rules: Rules,
    today: date,
    now: datetime,
    context: str = "",
    protected: Sequence[str] = (),
) -> BriefResult:
    """Build the brief. `protected` are names whose digits the guard must skip (product
    and ingredient names such as "Wheat flour type 550")."""
    decisions: list[Decision] = []
    by_id = {c.id: c for c in candidates}
    ranked = sorted(candidates, key=lambda c: c.impact_eur_weekly, reverse=True)
    order, planned = await _plan(planner, ranked, context, decisions)

    drafted: list[_Drafted] = []
    for cid in order:
        candidate = by_id[cid]
        copied = await _copy_for(candidate, planned.get(cid), planner, protected, decisions)
        if copied is None:
            continue
        copy, source, result = copied
        note, params = _rules_note(candidate, rules, today)
        if note is not None:
            leftover = guard.unmatched([note], candidate.numbers, protected)
            if leftover:
                decisions.append(Decision(cid, "dropped", f"note failed the guard {leftover}"))
                continue
            decisions.append(Decision(cid, "rules", note))
        drafted.append(_Drafted(candidate, copy, source, result, note, params))

    vetoed = await _verify(verifier, drafted, rules, today, decisions)
    cards: list[ActionCard] = []
    for d in drafted:
        if d.candidate.id in vetoed:
            continue
        action = d.candidate.proposed_action
        cards.append(
            ActionCard(
                id=action_id(d.candidate.id, d.params),
                candidate_id=d.candidate.id,
                kind=d.candidate.kind,
                rank=len(cards) + 1,
                title=d.copy.title,
                impact_eur_weekly=d.candidate.impact_eur_weekly,
                why=d.copy.why,
                evidence=d.candidate.evidence,
                numbers=d.candidate.numbers,
                task=action.task if action else None,
                portal=action.portal if action else None,
                params=d.params,
                executable=bool(action and action.executable),
                status="proposed",
                preference_note=d.note,
                copy_source="llm" if d.source == "llm" else "template",
                guard=d.guard,
            )
        )
    stamp = hashlib.sha256(now.isoformat().encode()).hexdigest()[:6]
    brief = Brief(
        id=f"brief_{today.isoformat()}_{stamp}",
        generated_at=now,
        as_of=datetime.combine(today, datetime.min.time(), tzinfo=BONN),
        cards=cards,
        cached=False,
    )
    return BriefResult(brief=brief, decisions=decisions, vetoed=vetoed)


async def stream(
    result: BriefResult,
) -> AsyncIterator[BriefSkeleton | BriefCardEvent | BriefDone]:
    """The SSE events of a finished brief (CONTRACTS §7): skeleton, cards, whole brief."""
    yield BriefSkeleton(cards=len(result.brief.cards))
    for card in result.brief.cards:
        yield BriefCardEvent(card=card)
    yield BriefDone(brief=result.brief)


def protected_names(data_dir: Any) -> list[str]:
    """Names whose digits are part of the name, not quantities: menu items and
    ingredients (e.g. "Wheat flour type 550")."""
    import duckdb

    from backroom_api.analytics.detectors import INGREDIENT

    con = duckdb.connect()
    menu = [
        r[0]
        for r in con.execute(
            "select name from read_parquet(?)", [str(data_dir / "menu.parquet")]
        ).fetchall()
    ]
    con.close()
    return sorted({*menu, *(name for _, name, _ in INGREDIENT.values())})


async def stream_today(
    data_dir: Any,
    *,
    planner: Planner,
    verifier: Verifier,
    rules: Rules,
    now: datetime,
    context: str = "",
) -> AsyncIterator[BriefSkeleton | BriefCardEvent | BriefDone | BriefResult]:
    """GET /brief/today?regenerate=1: the skeleton goes out before any model call (the
    UI shows placeholders at once), then each verified card, then the whole brief. The
    last item is the BriefResult, for the caller to persist (not sent to the client)."""
    from backroom_api.analytics.detectors import run_all

    candidates = run_all(data_dir, now=now, max_price_increase_pct=rules.max_price_increase_pct)
    yield BriefSkeleton(cards=min(MAX_CARDS, len(candidates)))
    today = candidates[0].as_of.date() if candidates else now.astimezone(BONN).date()
    result = await generate(
        candidates,
        planner=planner,
        verifier=verifier,
        rules=rules,
        today=today,
        now=now,
        context=context,
        protected=protected_names(data_dir),
    )
    for card in result.brief.cards:
        yield BriefCardEvent(card=card)
    yield BriefDone(brief=result.brief)
    yield result


async def brief_for_today(
    data_dir: Any,
    *,
    planner: Planner,
    verifier: Verifier,
    rules: Rules,
    now: datetime,
    context: str = "",
) -> BriefResult:
    """The brief for the day the data was built for (stream_today without streaming)."""
    async for event in stream_today(
        data_dir, planner=planner, verifier=verifier, rules=rules, now=now, context=context
    ):
        if isinstance(event, BriefResult):
            return event
    raise AssertionError("stream_today ended without a result")
