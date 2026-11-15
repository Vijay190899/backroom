"""L7: number guard, templates, the brief pipeline with fake models, and the F4 loop
(reject -> preference -> regenerated brief) on a real Postgres."""

import json
import uuid
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, LiteralString, cast
from zoneinfo import ZoneInfo

import psycopg
import pytest
from psycopg import sql

from backroom_api.analytics.detectors import run_all
from backroom_api.brief import guard, pipeline, templates
from backroom_api.brief.agents import (
    PLANNER_SYSTEM,
    BriefLLMError,
    CardCopy,
    Draft,
    LLMPlanner,
    LLMVerifier,
    Verdict,
    candidate_view,
)
from backroom_api.brief.rules import Preference, Rules, rules_from_memory, weekday_index
from backroom_api.config import REPO_ROOT, Settings
from backroom_api.contracts.api import BriefCardEvent, BriefDone, BriefSkeleton
from backroom_api.contracts.candidate import Candidate, EvidenceNumber
from backroom_api.memory import extractor, writers

TODAY = date(2026, 11, 13)  # a Friday
NOW = datetime(2026, 11, 13, 6, 30, tzinfo=ZoneInfo("Europe/Berlin"))
TUE_FRI = Preference(
    "preference:grainline-order-days",
    "Lena orders from Grainline only on Tuesdays and Fridays.",
    {"supplier": "grainline", "weekdays": ["tue", "fri"]},
)
CAP_8 = Preference(
    "preference:max-price-increase", "Price rises of at most 8%", {"max_price_increase_pct": 8}
)
MARGIN_70 = Preference("preference:margin-target", "Keep a 70% margin", {"margin_target_pct": 70})


def n(key: str, value: float, unit: str) -> EvidenceNumber:
    return EvidenceNumber(key=key, value=value, unit=unit, label=key)  # type: ignore[arg-type]


NUMBERS = [
    n("price_now_eur", 3.2, "eur"),
    n("price_new_eur", 3.6, "eur"),
    n("order_total_eur", 13.08, "eur"),
    n("labour_eur", 58.0, "eur"),
    n("price_increase_pct", 12.5, "pct"),
    n("butter_eur_per_kg", 8.24, "eur_per_kg"),
    n("days_left", 2.0, "days"),
    n("shift_hours", 4.0, "hours"),
    n("footfall_change_pct", -14, "pct"),
    n("units", 1200, "count"),
    n("cartons", 12, "count"),
]


# --- the guard ----------------------------------------------------------------------------


@pytest.mark.parametrize(
    "copy",
    [
        "€3.20 → €3.60 (+12.5%) in 2 days",
        "Prices go from 3.20 € to 3.60 €.",
        "Sales drop 14% on rainy days.",
        "Sales fall \u221214% when it rains.",  # a written sign that agrees
        "About 1,200 sold.",
        "Raise it by 13%.",  # 12.5 rounds half-up to 13
        "Order OAT-1L now; see GW-10482 and INV-204107.",  # ids are not quantities
        "Butter now costs €8.24/kg.",
        "Save €58 or €58.00 on a 4-hour shift.",  # whole euros may drop the cents
        "A dozen cartons arrive Monday.",  # number words are numbers
    ],
)
def test_guard_accepts_numbers_from_the_evidence(copy: str) -> None:
    assert guard.unmatched([copy], NUMBERS) == []


@pytest.mark.parametrize(
    ("copy", "bad"),
    [
        ("Raise it to €3.99.", ["€3.99"]),  # made up
        ("Raise it by 12%.", ["12%"]),  # half-up gives 13, not 12
        ("Butter is up 8%.", ["8%"]),  # 8 only exists as €8.24/kg: units must agree
        ("Costs 3.20 per item.", ["3.20"]),  # a bare number never matches a euro value
        ("Reprice at 14:00 on Saturday.", ["14:00"]),  # clock times are never evidence
        ("Since 2026, prices rose.", ["2026"]),
        ("The order is about €13.", ["€13"]),  # money keeps its cents: 13.08
        ("Butter costs €8.24.", ["€8.24"]),  # a per-kg price needs its /kg
        ("Only 4 days of stock.", ["4 days"]),  # 4 exists only as hours
        ("Sales rise +14% in rain.", ["+14%"]),  # the sign disagrees with -14
        ("Order three cartons.", ["three"]),
        ("Cut half the shifts.", ["half"]),  # fractions in words never match
        ("Pay €3." + "1" * 40 + ".", ["€3." + "1" * 40]),  # absurd decimals don't crash
    ],
)
def test_guard_rejects_unbacked_numbers(copy: str, bad: list[str]) -> None:
    assert guard.unmatched([copy], NUMBERS) == bad


def test_guard_skips_protected_names_in_any_case() -> None:
    copy = "WHEAT FLOUR TYPE 550 is fine; 2 days left."
    assert guard.unmatched([copy], NUMBERS) == ["550"]
    assert guard.unmatched([copy], NUMBERS, protected=["Wheat flour type 550"]) == []


def test_display_strings_always_pass() -> None:
    for number in [*NUMBERS, n("big", 1_234_567.891, "count"), n("eur_big", 1234.5, "eur")]:
        assert guard.unmatched([guard.display(number)], [number]) == [], number


def test_weekday_names_are_normalised() -> None:
    assert [weekday_index(d) for d in ("Tue", "tuesday", "TUE", "fri", "x")] == [1, 1, 1, 4, None]


# --- candidates from the real detectors (offline synthetic build) ---------------------------


@pytest.fixture(scope="module")
def data_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from backroom_data import cli

    out = tmp_path_factory.mktemp("out")
    cli.build(TODAY, 44, out, tmp_path_factory.mktemp("raw"), offline=True)
    return out


@pytest.fixture(scope="module")
def candidates(data_dir: Path) -> list[Candidate]:
    return run_all(data_dir, now=NOW)


def test_template_copy_passes_the_guard_for_every_candidate(
    candidates: list[Candidate], data_dir: Path
) -> None:
    protected = pipeline.protected_names(data_dir)
    for c in [*candidates, *run_all(data_dir, now=NOW, max_price_increase_pct=8)]:
        title, why = templates.copy_for(c)
        assert guard.unmatched([title, why], c.numbers, protected) == [], (c.kind, why)


# --- fakes -----------------------------------------------------------------------------------


def good_copy(c: Candidate) -> CardCopy:
    title, why = templates.copy_for(c)
    return CardCopy(candidate_id=c.id, title=title, why="Today: " + why)


@dataclass
class FakePlanner:
    """Writes template-like copy; `lie` adds a made-up number; `fix_on_rewrite` repairs it."""

    lie: bool = False
    fix_on_rewrite: bool = False
    fail: Exception | None = None
    fail_rewrite: Exception | None = None
    extra: list[CardCopy] = field(default_factory=list[CardCopy])
    rewrites: list[list[str]] = field(default_factory=list[list[str]])

    async def plan(self, candidates: list[Candidate], context: str) -> list[CardCopy]:
        if self.fail is not None:
            raise self.fail
        out = [good_copy(c) for c in candidates[:3]] + self.extra
        if self.lie:
            out[0] = out[0].model_copy(update={"why": out[0].why + " That's €999.99 a year."})
        return out

    async def rewrite(
        self, candidate: Candidate, previous: CardCopy, unmatched: list[str]
    ) -> CardCopy:
        self.rewrites.append(unmatched)
        if self.fail_rewrite is not None:
            raise self.fail_rewrite
        if self.fix_on_rewrite:
            return good_copy(candidate)
        return previous.model_copy(update={"why": previous.why + " Or 77%."})


@dataclass
class FakeVerifier:
    veto: str | None = None  # a candidate kind to veto
    cite: str = TUE_FRI.id  # the preference the veto rests on
    fail: Exception | None = None
    seen: list[str] = field(default_factory=list[str])
    drafts: list[Draft] = field(default_factory=list[Draft])
    calls: int = 0

    async def verify(
        self, drafts: list[Draft], preferences: list[Preference], today: date
    ) -> list[Verdict]:
        self.calls += 1
        if self.fail is not None:
            raise self.fail
        self.seen = [p.id for p in preferences]
        self.drafts = drafts
        return [
            Verdict(
                candidate_id=d.candidate.id,
                verdict="veto" if d.candidate.kind == self.veto else "keep",
                preference_id=self.cite if d.candidate.kind == self.veto else "",
                reason="conflicts" if d.candidate.kind == self.veto else "fine",
            )
            for d in drafts
        ]


WITH_RULES = Rules(preferences=[TUE_FRI], business_rules=[MARGIN_70])


async def brief(
    data_dir: Path, planner: Any, verifier: Any, rules: Rules | None = None
) -> pipeline.BriefResult:
    return await pipeline.brief_for_today(
        data_dir, planner=planner, verifier=verifier, rules=rules or WITH_RULES, now=NOW
    )


# --- the round trip --------------------------------------------------------------------------


async def test_round_trip_with_a_good_planner(data_dir: Path) -> None:
    result = await brief(data_dir, FakePlanner(), FakeVerifier())
    cards = result.brief.cards
    assert [c.rank for c in cards] == [1, 2, 3]
    assert {c.kind for c in cards} == {"stockout", "margin_erosion", "weather_demand"}
    assert all(
        c.copy_source == "llm" and c.guard.passed and c.guard.regenerations == 0 for c in cards
    )
    margin = next(c for c in cards if c.kind == "margin_erosion")
    assert margin.params == {"item_id": "franzbroetchen", "price_eur": 3.6}
    assert margin.preference_note is None  # no cap learned yet
    weather = next(c for c in cards if c.kind == "weather_demand")
    assert not weather.executable and weather.task is None


async def test_made_up_number_is_rejected_then_templated(data_dir: Path) -> None:
    planner = FakePlanner(lie=True)
    result = await brief(data_dir, planner, FakeVerifier())
    first = result.brief.cards[0]
    assert planner.rewrites == [["€999.99"]]  # one regeneration, told what was wrong
    assert first.copy_source == "template"
    assert not first.guard.passed and first.guard.regenerations == 1
    assert "77%" in first.guard.unmatched
    assert "999" not in first.why and "77%" not in first.why


async def test_rewrite_that_fixes_the_number_is_kept(data_dir: Path) -> None:
    result = await brief(data_dir, FakePlanner(lie=True, fix_on_rewrite=True), FakeVerifier())
    first = result.brief.cards[0]
    assert first.copy_source == "llm" and first.guard.passed and first.guard.regenerations == 1
    assert first.guard.unmatched == []


@pytest.mark.parametrize(
    "error", [BriefLLMError("refusal"), TimeoutError(), RuntimeError("budget spent")]
)
async def test_any_planner_failure_falls_back_to_templates(
    data_dir: Path, error: Exception
) -> None:
    result = await brief(data_dir, FakePlanner(fail=error), FakeVerifier())
    cards = result.brief.cards
    assert len(cards) == 3
    assert all(c.copy_source == "template" and c.guard.passed for c in cards)
    impacts = [c.impact_eur_weekly for c in cards]
    assert impacts == sorted(impacts, reverse=True)


async def test_rewrite_failure_falls_back_to_the_template(data_dir: Path) -> None:
    planner = FakePlanner(lie=True, fail_rewrite=TimeoutError())
    result = await brief(data_dir, planner, FakeVerifier())
    assert result.brief.cards[0].copy_source == "template"
    assert any(d.step == "rewrite" and "TimeoutError" in d.detail for d in result.decisions)


async def test_extra_unknown_and_duplicate_cards_are_dropped(
    data_dir: Path, candidates: list[Candidate]
) -> None:
    top = max(candidates, key=lambda c: c.impact_eur_weekly)
    extra = [CardCopy(candidate_id="nope", title="x", why="y"), good_copy(top)]
    result = await brief(data_dir, FakePlanner(extra=extra), FakeVerifier())
    assert len(result.brief.cards) == 3
    assert sum(d.detail == "unknown or duplicate id" for d in result.decisions) == 2


async def test_verifier_veto_removes_the_card(data_dir: Path) -> None:
    verifier = FakeVerifier(veto="weather_demand", cite=MARGIN_70.id)
    result = await brief(data_dir, FakePlanner(), verifier)
    assert [c.kind for c in result.brief.cards if c.kind == "weather_demand"] == []
    assert [c.rank for c in result.brief.cards] == [1, 2]
    assert len(result.vetoed) == 1
    assert {TUE_FRI.id, MARGIN_70.id} <= set(verifier.seen)  # business rules too


@pytest.mark.parametrize("error", [BriefLLMError("max_tokens"), TimeoutError(), OSError()])
async def test_any_verifier_failure_keeps_the_cards(data_dir: Path, error: Exception) -> None:
    result = await brief(data_dir, FakePlanner(), FakeVerifier(fail=error))
    assert len(result.brief.cards) == 3
    assert any(d.step == "verifier" and "unavailable" in d.detail for d in result.decisions)


async def test_no_rules_means_no_verifier_call(data_dir: Path) -> None:
    verifier = FakeVerifier(veto="stockout")
    result = await brief(data_dir, FakePlanner(), verifier, Rules())
    assert verifier.calls == 0 and len(result.brief.cards) == 3


async def test_veto_citing_an_unknown_rule_is_ignored(data_dir: Path) -> None:
    result = await brief(data_dir, FakePlanner(), FakeVerifier(veto="stockout", cite="made-up"))
    assert len(result.brief.cards) == 3
    assert any("cites no known rule" in d.detail for d in result.decisions)


async def test_veto_of_a_rule_code_already_satisfies_is_overruled(
    candidates: list[Candidate],
) -> None:
    """The real Haiku verifier once vetoed a Friday reorder under the Tue/Fri rule."""
    stock = [c for c in candidates if c.kind == "stockout"]
    verifier = FakeVerifier(veto="stockout", cite=TUE_FRI.id)
    result = await pipeline.generate(
        stock, planner=FakePlanner(), verifier=verifier, rules=WITH_RULES, today=TODAY, now=NOW
    )
    assert len(result.brief.cards) == 1 and result.vetoed == []
    assert any("overruled" in d.detail for d in result.decisions)
    assert verifier.drafts[0].note is not None and verifier.drafts[0].params["order_on"]


async def test_veto_of_a_rule_code_cannot_check_stands(candidates: list[Candidate]) -> None:
    stock = [c for c in candidates if c.kind == "stockout"]
    result = await pipeline.generate(
        stock,
        planner=FakePlanner(),
        verifier=FakeVerifier(veto="stockout", cite=MARGIN_70.id),
        rules=WITH_RULES,
        today=TODAY,
        now=NOW,
    )
    assert result.brief.cards == []


async def test_order_day_rule_is_per_supplier(candidates: list[Candidate]) -> None:
    stock = [c for c in candidates if c.kind == "stockout"]
    other = Preference("preference:x", "Other supplier", {"supplier": "acme", "weekdays": ["mon"]})
    result = await pipeline.generate(
        stock,
        planner=FakePlanner(),
        verifier=FakeVerifier(),
        rules=Rules(preferences=[other]),
        today=TODAY,
        now=NOW,
    )
    assert "order_on" not in result.brief.cards[0].params


async def test_learned_cap_reproposes_within_it_with_a_new_id(data_dir: Path) -> None:
    before = await brief(data_dir, FakePlanner(), FakeVerifier())
    capped_rules = Rules(preferences=[CAP_8, TUE_FRI], business_rules=[MARGIN_70])
    after = await brief(data_dir, FakePlanner(), FakeVerifier(), capped_rules)
    old = next(c for c in before.brief.cards if c.kind == "margin_erosion")
    new = next(c for c in after.brief.cards if c.kind == "margin_erosion")
    assert (old.params["price_eur"], new.params["price_eur"]) == (3.6, 3.45)
    assert new.preference_note == "Kept under your 8% cap"
    assert new.id != old.id  # approve/reject can't hit the stale €3.60 action


async def test_order_days_schedule_the_reorder(candidates: list[Candidate]) -> None:
    stock = [c for c in candidates if c.kind == "stockout"]
    for today, expected in [
        (date(2026, 11, 13), "Ordering today, Friday"),
        (date(2026, 11, 12), "Scheduled for Friday"),
    ]:
        result = await pipeline.generate(
            stock,
            planner=FakePlanner(),
            verifier=FakeVerifier(),
            rules=Rules(preferences=[TUE_FRI]),
            today=today,
            now=NOW,
        )
        card = result.brief.cards[0]
        assert card.preference_note is not None and card.preference_note.startswith(expected)
        assert card.params["order_on"] == "2026-11-13"


async def test_stream_sends_the_skeleton_before_any_model_call(data_dir: Path) -> None:
    calls: list[str] = []

    class Recording(FakePlanner):
        async def plan(self, candidates: list[Candidate], context: str) -> list[CardCopy]:
            calls.append("plan")
            return await super().plan(candidates, context)

    events: list[Any] = []
    async for e in pipeline.stream_today(
        data_dir, planner=Recording(), verifier=FakeVerifier(), rules=WITH_RULES, now=NOW
    ):
        events.append(e)
        if isinstance(e, BriefSkeleton):
            assert calls == []  # placeholders go out before the planner runs
    assert isinstance(events[0], BriefSkeleton) and events[0].cards == 3
    assert all(isinstance(e, BriefCardEvent) for e in events[1:4])
    assert isinstance(events[4], BriefDone) and isinstance(events[5], pipeline.BriefResult)


async def test_stream_of_a_finished_brief(data_dir: Path) -> None:
    result = await brief(data_dir, FakePlanner(), FakeVerifier())
    events = [e async for e in pipeline.stream(result)]
    assert isinstance(events[0], BriefSkeleton) and isinstance(events[-1], BriefDone)


def test_action_ids_follow_the_proposal() -> None:
    a = pipeline.action_id("x", {"price_eur": 3.6})
    assert a == pipeline.action_id("x", {"price_eur": 3.6})
    assert a != pipeline.action_id("x", {"price_eur": 3.45})


# --- the real agents against a stub client ---------------------------------------------------


@dataclass
class _Message:
    stop_reason: str


@dataclass
class _Result:
    message: _Message
    text: str


@dataclass
class StubLLM:
    stop_reason: str = "end_turn"
    text: str = '{"cards": []}'
    calls: list[dict[str, Any]] = field(default_factory=list[dict[str, Any]])

    async def create(self, role: str, **kwargs: Any) -> _Result:
        self.calls.append({"role": role, **kwargs})
        return _Result(_Message(self.stop_reason), self.text)


async def test_llm_planner_sends_a_cached_structured_request(
    candidates: list[Candidate],
) -> None:
    stub = StubLLM(
        text=json.dumps({"cards": [{"candidate_id": candidates[0].id, "title": "T", "why": "W"}]})
    )
    cards = await LLMPlanner(stub, run_id="r1").plan(candidates, "ctx")  # type: ignore[arg-type]
    assert cards == [CardCopy(candidate_id=candidates[0].id, title="T", why="W")]
    call = stub.calls[0]
    assert call["role"] == "planner" and call["json_schema"]["required"] == ["cards"]
    assert call["system"][0]["text"] == PLANNER_SYSTEM
    assert call["system"][0]["cache_control"] == {"type": "ephemeral"}
    sent = json.loads(call["messages"][0]["content"].split("\n\nWhat memory")[0])
    numbers = sent["candidates"][0]["numbers"]
    assert all(set(num) == {"key", "label", "display"} for num in numbers)


async def test_llm_rewrite_ends_on_a_user_turn(candidates: list[Candidate]) -> None:
    previous = CardCopy(candidate_id=candidates[0].id, title="T", why="W €9.99")
    stub = StubLLM(text=json.dumps({"cards": [previous.model_dump()]}))
    await LLMPlanner(stub).rewrite(candidates[0], previous, ["€9.99"])  # type: ignore[arg-type]
    roles = [m["role"] for m in stub.calls[0]["messages"]]
    assert roles == ["user", "assistant", "user"]  # never an assistant prefill
    assert "€9.99" in stub.calls[0]["messages"][-1]["content"]


async def test_llm_verifier_sees_what_the_owner_sees(candidates: list[Candidate]) -> None:
    c = candidates[0]
    stub = StubLLM(
        text=json.dumps(
            {
                "verdicts": [
                    {"candidate_id": c.id, "verdict": "keep", "preference_id": "", "reason": "ok"}
                ]
            }
        )
    )
    draft = Draft(c, good_copy(c), "Ordering today, Friday", {"order_on": "2026-11-13"})
    verdicts = await LLMVerifier(stub).verify([draft], [TUE_FRI], TODAY)  # type: ignore[arg-type]
    assert verdicts[0].verdict == "keep"
    sent = json.loads(stub.calls[0]["messages"][0]["content"])
    assert stub.calls[0]["role"] == "verifier" and sent["today"] == "2026-11-13 (Friday)"
    assert sent["cards"][0]["note"] == "Ordering today, Friday"
    assert sent["cards"][0]["action"]["params"] == {"order_on": "2026-11-13"}


@pytest.mark.parametrize(
    ("stop", "text"), [("refusal", ""), ("max_tokens", '{"cards": ['), ("end_turn", "not json")]
)
async def test_llm_planner_raises_on_unusable_answers(
    candidates: list[Candidate], stop: str, text: str
) -> None:
    with pytest.raises(BriefLLMError):
        await LLMPlanner(StubLLM(stop, text)).plan(candidates, "")  # type: ignore[arg-type]


def test_candidate_view_has_no_raw_values(candidates: list[Candidate]) -> None:
    for c in candidates:
        assert all(set(num) == {"key", "label", "display"} for num in candidate_view(c)["numbers"])


# --- the preference extractor ------------------------------------------------------------------


def rule(kind: str, value: float = 0, weekdays: list[str] | None = None) -> extractor.ExtractedRule:
    return extractor.ExtractedRule(
        kind=kind,  # type: ignore[arg-type]
        value=value,
        weekdays=weekdays or [],
        text="t",
    )


@pytest.mark.parametrize(
    ("proposed", "reason", "kept"),
    [
        (rule("max_price_increase_pct", 8), "too steep, max 8%", True),
        (rule("max_price_increase_pct", 10), "too steep, max 8%", False),  # not her number
        (rule("max_price_increase_pct", 8.5), "keep it under 8,5 %", True),
        (rule("order_weekdays", weekdays=["Tue", "FRI"]), "only order tue and fri", True),
        (rule("order_weekdays", weekdays=["mon"]), "only order tue and fri", False),
        (rule("none"), "not today", False),
        (None, "anything", False),
    ],
)
def test_extracted_rules_need_the_owners_words(
    proposed: extractor.ExtractedRule | None, reason: str, kept: bool
) -> None:
    assert (extractor.checked(proposed, reason) is not None) == kept


async def test_extract_uses_the_worker_role(data_dir: Path) -> None:
    result = await brief(data_dir, FakePlanner(), FakeVerifier())
    card = next(c for c in result.brief.cards if c.kind == "margin_erosion")
    stub = StubLLM(text=rule("max_price_increase_pct", 8).model_dump_json())
    got = await extractor.extract(stub, "too steep, max 8%", card)  # type: ignore[arg-type]
    assert got is not None and got.value == 8 and stub.calls[0]["role"] == "worker"
    refused = await extractor.extract(StubLLM("refusal", ""), "x", card)  # type: ignore[arg-type]
    assert refused is None


# --- F4 end to end on Postgres (Neon locally; skipped without a database) --------------------


MIGRATION = REPO_ROOT / "services" / "api" / "migrations" / "0001_memory.sql"


@pytest.fixture(scope="module")
def conn(data_dir: Path) -> Iterator[psycopg.Connection[Any]]:
    try:
        connection = psycopg.connect(Settings().database_url, connect_timeout=5)
    except psycopg.OperationalError:
        pytest.skip("no Postgres reachable (set DATABASE_URL, e.g. Neon)")
    name = sql.Identifier(f"test_brief_{uuid.uuid4().hex[:10]}")
    connection.execute(sql.SQL("create schema {}").format(name))
    connection.execute(sql.SQL("set search_path to {}, public").format(name))
    connection.execute(cast(LiteralString, MIGRATION.read_text()))
    writers.write_world(connection, data_dir)
    connection.commit()
    try:
        yield connection
    finally:
        connection.rollback()
        connection.execute(sql.SQL("drop schema {} cascade").format(name))
        connection.commit()
        connection.close()


async def test_reject_with_a_cap_then_regenerate(
    conn: psycopg.Connection[Any], data_dir: Path
) -> None:
    """PRD F4: reject +12.5% with "too steep, max 8%" -> Preference -> €3.45 card."""
    rules = rules_from_memory(conn, NOW)
    assert {p.id for p in rules.preferences} == {TUE_FRI.id}
    assert {p.id for p in rules.business_rules} == {MARGIN_70.id}
    first = await brief(data_dir, FakePlanner(), FakeVerifier(), rules)
    card = next(c for c in first.brief.cards if c.kind == "margin_erosion")
    assert card.params["price_eur"] == 3.6

    stub = StubLLM(text=rule("max_price_increase_pct", 8).model_dump_json())
    extracted = await extractor.extract(stub, "too steep, max 8%", card)  # type: ignore[arg-type]
    response = extractor.record_rejection(
        conn, card=card, reason="too steep, max 8%", rule=extracted, at=NOW
    )
    conn.commit()
    assert response.action_id == card.id and len(response.preference_fact_ids) == 1

    rules = rules_from_memory(conn, NOW)
    assert rules.max_price_increase_pct == 8
    second = await brief(data_dir, FakePlanner(), FakeVerifier(), rules)
    capped = next(c for c in second.brief.cards if c.kind == "margin_erosion")
    numbers = {x.key: x.value for x in capped.numbers}
    assert (capped.params["price_eur"], numbers["price_increase_pct"]) == (3.45, 7.8)
    assert numbers["margin_new_pct"] == 70
    assert capped.preference_note == "Kept under your 8% cap" and capped.id != card.id


async def test_a_reason_without_a_rule_records_only_the_episode(
    conn: psycopg.Connection[Any], data_dir: Path
) -> None:
    result = await brief(data_dir, FakePlanner(), FakeVerifier())
    card = result.brief.cards[0]
    response = extractor.record_rejection(
        conn, card=card, reason="not today", rule=rule("none"), at=NOW
    )
    assert response.preference_fact_ids == []
    kind = conn.execute("select kind from episode where id = %s", [response.episode_id]).fetchone()
    assert kind == ("rejection",)
    conn.rollback()
