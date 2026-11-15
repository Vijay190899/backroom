import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, TypeAdapter, ValidationError

from backroom_api.contracts import api
from backroom_api.contracts.candidate import ProposedAction
from backroom_api.contracts.events import RunStarted, run_events_adapter, to_sse
from backroom_api.skills.schema import Locator, Skill, Step, StepChange

REPO = Path(__file__).resolve().parents[3]
FIXTURES = REPO / "apps" / "web" / "src" / "fixtures"
FIXTURE_TYPES: dict[str, Any] = {
    "brief.json": api.Brief,
    "brief-after-reject.json": api.Brief,
    "memory-graph.json": api.MemoryGraph,
    "run-events.json": run_events_adapter,
    "skill-versions.json": api.SkillVersions,
    "skills.json": TypeAdapter(list[api.SkillSummary]),
}


def load(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", sorted(FIXTURE_TYPES))
def test_shared_fixture_parses(name: str) -> None:
    kind = FIXTURE_TYPES[name]
    if isinstance(kind, TypeAdapter):
        kind.validate_python(load(name))  # type: ignore[reportUnknownMemberType]
    else:
        assert issubclass(kind, BaseModel)
        kind.model_validate(load(name))


def test_every_fixture_is_covered() -> None:
    assert {p.name for p in FIXTURES.glob("*.json")} == set(FIXTURE_TYPES)


def test_unknown_fields_are_rejected() -> None:
    with pytest.raises(ValidationError, match="Extra inputs"):
        api.Brief.model_validate({**load("brief.json"), "extra": 1})


def test_brief_has_at_most_three_cards() -> None:
    brief = load("brief.json")
    with pytest.raises(ValidationError):
        api.Brief.model_validate({**brief, "cards": [*brief["cards"], brief["cards"][0]]})


def test_run_event_seqs_count_up_from_one_and_secrets_are_redacted() -> None:
    events = run_events_adapter.validate_python(load("run-events.json"))
    assert [e.seq for e in events] == list(range(1, len(events) + 1))
    assert events[0].type == "run.started"
    assert events[-1].type == "run.finished"
    for e in events:
        if e.type == "step.started" and e.action in ("fill_secret", "totp"):
            assert e.value is None


def test_to_sse_uses_seq_as_event_id() -> None:
    event = RunStarted(
        seq=3,
        run_id="r1",
        ts=datetime(2026, 11, 13, tzinfo=UTC),
        action_id="a1",
        task="grainline.reorder_item",
        portal="grainline",
        mode="replay",
        skill_version=1,
        chaos_seed=0,
    )
    lines = to_sse(event).split("\n")
    assert lines[:2] == ["id: 3", "event: run.started"]
    assert json.loads(lines[2].removeprefix("data: "))["seq"] == 3
    assert to_sse(event).endswith("\n\n")


def test_margin_card_numbers_match_the_demo_story() -> None:
    card = next(c for c in load("brief.json")["cards"] if c["kind"] == "margin_erosion")
    n = {x["key"]: x["value"] for x in card["numbers"]}

    def margin(cost: str, price: str) -> int:
        return round((1 - n[cost] / n[price]) * 100)

    assert margin("unit_cost_before_eur", "price_now_eur") == n["margin_before_pct"]
    assert margin("unit_cost_after_eur", "price_now_eur") == n["margin_after_pct"]
    assert margin("unit_cost_after_eur", "price_new_eur") == n["margin_new_pct"]
    rise = (n["price_new_eur"] / n["price_now_eur"] - 1) * 100
    assert round(rise, 1) == n["price_increase_pct"]


# --- skill schema validators ---------------------------------------------------------


def make_skill(steps: list[dict[str, Any]], **overrides: Any) -> Skill:
    return Skill.model_validate(
        {
            "id": "grainline.reorder_item",
            "task": "grainline.reorder_item",
            "portal": "grainline",
            "version": 1,
            "params_schema": {"type": "object", "properties": {"qty": {"type": "integer"}}},
            "steps": steps,
            "postconditions": [],
            "created_at": "2026-11-13T07:00:00Z",
            **overrides,
        }
    )


QTY = {"intent": "qty", "action": "fill", "target": {"role": "spinbutton", "name": "Quantity"}}


def test_skill_accepts_declared_params_and_secrets() -> None:
    skill = make_skill(
        [
            {**QTY, "value_template": "{{qty}}"},
            {
                "intent": "pw",
                "action": "fill_secret",
                "target": {"role": "textbox", "name": "Password"},
                "value_template": "{{secret:grainline_password}}",
            },
        ]
    )
    assert skill.steps[1].target == Locator(role="textbox", name="Password")


@pytest.mark.parametrize(
    ("steps", "overrides", "error"),
    [
        ([{**QTY, "value_template": "{{sku}}"}], {}, "undeclared param 'sku'"),
        ([{**QTY, "value_template": "{{secret:pw}}"}], {}, "only be used by fill_secret"),
        ([{**QTY, "action": "fill_secret", "value_template": "x"}], {}, "needs a"),
        ([{"intent": "click", "action": "click"}], {}, "needs a target"),
        ([], {}, "at least one step"),
        ([QTY], {"version": 2, "parent_version": 2}, "parent_version"),
    ],
)
def test_skill_rejects_bad_shapes(
    steps: list[dict[str, Any]], overrides: dict[str, Any], error: str
) -> None:
    with pytest.raises(ValidationError, match=error):
        make_skill(steps, **overrides)


def test_step_fallback_forms_round_trip() -> None:
    step = Step.model_validate(
        {**QTY, "fallbacks": [{"label": "Quantity"}, {"text": "Qty"}, {"css": "#q"}]}
    )
    assert Step.model_validate(step.model_dump()) == step


# --- the api's chaos models must match the portals' --------------------------------------


def test_chaos_models_match_the_portals_contract() -> None:
    from backroom_portals import contract as portals

    assert (
        api.ChaosRequest.model_json_schema()["properties"]
        == (portals.ChaosRequest.model_json_schema()["properties"])
    )
    assert (
        api.ChaosState.model_json_schema()["properties"]
        == (portals.ChaosState.model_json_schema()["properties"])
    )


def test_memory_migration_defines_the_graph_tables() -> None:
    sql = (REPO / "services" / "api" / "migrations" / "0001_memory.sql").read_text()
    for table in ("entity", "episode", "fact"):
        assert f"create table {table} (" in sql
    # Entity types in SQL and in the API contract must be the same set.
    for entity_type in TypeAdapter(api.EntityType).json_schema()["enum"]:
        assert f"'{entity_type}'" in sql


def test_rejected_card_is_regenerated_under_the_learned_cap() -> None:
    card = next(
        c for c in load("brief-after-reject.json")["cards"] if c["kind"] == "margin_erosion"
    )
    n = {x["key"]: x["value"] for x in card["numbers"]}
    assert n["price_increase_pct"] < n["max_price_increase_pct"] == 8
    assert round((1 - n["unit_cost_after_eur"] / n["price_new_eur"]) * 100) == 70
    assert card["preference_note"] == "Kept under your 8% cap"


def test_naive_datetimes_are_rejected() -> None:
    with pytest.raises(ValidationError, match="timezone"):
        api.RunSummary.model_validate(
            {
                "id": "r",
                "action_id": "a",
                "task": "grainline.reorder_item",
                "portal": "grainline",
                "status": "queued",
                "mode": "replay",
                "skill_version": 1,
                "chaos_seed": 0,
                "started_at": "2026-11-13T07:30:00",
                "finished_at": None,
                "totals": {
                    "elapsed_ms": 0,
                    "steps": 0,
                    "llm_calls": 0,
                    "tokens_in": 0,
                    "tokens_out": 0,
                    "cache_read_tokens": 0,
                    "usd": 0,
                },
            }
        )


def test_heal_diff_can_insert_a_step() -> None:
    versions = api.SkillVersions.model_validate(load("skill-versions.json"))
    v1, v2 = versions.versions
    inserts = [c for c in versions.diffs[0].changes if c.op == "insert"]
    assert len(v2.steps) == len(v1.steps) + len(inserts)
    assert v2.steps[inserts[0].step_index].model_dump() == inserts[0].after
    with pytest.raises(ValidationError, match="field 'step'"):
        StepChange(op="insert", step_index=0, field="target", before=None, after={})


def test_goto_needs_a_path_and_secrets_need_the_exact_form() -> None:
    with pytest.raises(ValidationError, match="goto needs"):
        Step(intent="go", action="goto")
    with pytest.raises(ValidationError, match="needs a"):
        Step.model_validate(
            {**QTY, "action": "fill_secret", "value_template": "{{ secret:grainline_password }}"}
        )


def test_proposed_action_executable_iff_it_has_a_task() -> None:
    ProposedAction(task=None, portal=None, executable=False)
    ProposedAction(task="tilldesk.change_price", portal="tilldesk", executable=True)
    with pytest.raises(ValidationError, match="executable"):
        ProposedAction(task=None, portal=None, executable=True)
