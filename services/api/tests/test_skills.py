"""H3 unit tests that need no browser: compiler, diff, store, postconditions."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from backroom_api.agents.postconditions import walk
from backroom_api.agents.tasks import TASKS
from backroom_api.replay.engine import replacement_changes
from backroom_api.skills.compiler import Action, compile_action, compile_skill, template_value
from backroom_api.skills.diff import diff_skills
from backroom_api.skills.schema import (
    LabelFallback,
    Locator,
    Skill,
    SkillDiff,
    Step,
    TextFallback,
)
from backroom_api.skills.store import SkillStore

PARAMS = {"sku": "OAT-1L", "qty": 24, "price_eur": 3.45, "item_id": "franzbroetchen"}


def test_values_become_params_only_when_they_match() -> None:
    assert template_value("fill", "OAT-1L", PARAMS) == "{{sku}}"
    assert template_value("fill", "24", PARAMS) == "{{qty}}"
    assert template_value("fill", "3.45", PARAMS) == "{{price_eur}}"
    assert template_value("fill", "3,45", PARAMS) == "{{price_eur}}"  # German decimal comma
    assert template_value("fill", "oat", PARAMS) == "oat"  # not an exact match: stays literal
    assert template_value("press", "24", PARAMS) == "24"  # only fill and select are templated
    assert (
        template_value("goto", "/tilldesk/menu/franzbroetchen/edit", PARAMS)
        == "/tilldesk/menu/{{item_id}}/edit"
    )


def test_compile_action_builds_a_replayable_step() -> None:
    click = compile_action(
        Action(
            intent="Open checkout",
            action="click",
            role="link",
            name="Checkout",
            url_before="http://x/grainline/cart",
            url_after="http://x/grainline/checkout",
        ),
        PARAMS,
    )
    assert click.target == Locator(role="link", name="Checkout")
    assert click.fallbacks == [TextFallback(text="Checkout")]
    assert click.expect is not None and click.expect.url_pattern == r"^/grainline/checkout$"

    field = compile_action(
        Action(intent="Qty", action="fill", role="spinbutton", name="Quantity", value="24"), PARAMS
    )
    assert field.value_template == "{{qty}}" and field.fallbacks == [
        LabelFallback(label="Quantity")
    ]

    secret = compile_action(
        Action(
            intent="Password",
            action="fill_secret",
            role="textbox",
            name="Password",
            secret="grainline_password",
        ),
        PARAMS,
    )
    assert secret.value_template == "{{secret:grainline_password}}"


def test_run_specific_ids_are_not_baked_into_expectations() -> None:
    step = compile_action(
        Action(
            intent="Place order",
            action="click",
            role="button",
            name="Place order",
            url_before="http://x/grainline/checkout",
            url_after="http://x/grainline/orders/GW-10482",
        ),
        PARAMS,
    )
    assert step.expect is not None and step.expect.url_pattern == r"^/grainline/orders/GW\-\d+$"


def test_compile_skill_validates_against_the_contract() -> None:
    spec = TASKS["grainline.reorder_item"]
    skill = compile_skill(
        task=spec.task,
        portal=spec.portal,
        start_path=spec.start_path,
        actions=[
            Action(intent="Search", action="fill", role="textbox", name="Search", value="OAT-1L")
        ],
        params=PARAMS,
        params_schema=spec.params_schema,
        postconditions=spec.postconditions,
    )
    assert skill.version == 1 and skill.steps[0].action == "goto"
    assert skill.steps[1].value_template == "{{sku}}"


def _skill(version: int, steps: list[Step]) -> Skill:
    return Skill(
        id="grainline.reorder_item",
        task="grainline.reorder_item",
        portal="grainline",
        version=version,
        parent_version=version - 1 if version > 1 else None,
        params_schema={"type": "object", "properties": {"qty": {}}},
        steps=steps,
        postconditions=[],
        created_at=datetime.now(UTC),
    )


def _click(name: str, intent: str = "Click") -> Step:
    return Step(intent=intent, action="click", target=Locator(role="button", name=name))


def test_diff_reports_updates_inserts_and_deletes() -> None:
    old = _skill(1, [_click("Sign in", "Sign in"), _click("Verify", "Verify")])
    banner = _click("Accept all", "Dismiss the cookie banner")
    new = _skill(2, [banner, _click("Anmelden", "Sign in")])
    changes = {(c.op, c.step_index, c.field) for c in diff_skills(old, new).changes}
    assert ("update", 1, "target") in changes or ("insert", 0, "step") in changes
    same = diff_skills(old, old)
    assert same.changes == []


def test_replacement_changes_label_the_obstacle_as_an_insert() -> None:
    old = _click("Sign in", "Sign in")
    banner = _click("Accept all", "Dismiss the cookie banner")
    renamed = _click("Anmelden", "Sign in")
    changes = replacement_changes(old, [banner, renamed], at=3, old_index=3)
    assert [(c.op, c.step_index, c.field) for c in changes] == [
        ("insert", 3, "step"),
        ("update", 4, "target"),
    ]
    assert changes[0].after["intent"] == "Dismiss the cookie banner"
    # No step of the same action: the old one is deleted at its old position.
    fill = Step(
        intent="Type", action="fill", target=Locator(role="textbox", name="X"), value_template="1"
    )
    gone = replacement_changes(fill, [banner], at=2, old_index=1)
    assert [c.op for c in gone] == ["insert", "delete"] and gone[1].step_index == 1


def test_store_versions_are_immutable_and_diffs_round_trip(tmp_path: Path) -> None:
    store = SkillStore(tmp_path)
    v1 = _skill(1, [_click("Sign in")])
    assert store.latest(v1.id) is None
    store.save(v1)
    with pytest.raises(FileExistsError):
        store.save(v1)
    v2 = _skill(2, [_click("Anmelden")])
    store.save(v2)
    store.save_diff(SkillDiff(skill_id=v2.id, from_version=1, to_version=2, changes=[]))
    assert store.versions(v1.id) == [1, 2]  # the .diff.json file is not a version
    assert store.latest(v1.id) == v2
    assert store.get_diff(v1.id, 2) is not None
    store.record_run(v1.id, 2, ok=True, wall_ms=1000, usd=0.002)
    store.record_run(v1.id, 2, ok=False, wall_ms=3000, usd=0.0)
    stats = store.latest(v1.id).stats  # type: ignore[union-attr]
    assert (stats.runs, stats.successes, stats.mean_latency_ms) == (2, 1, 2000)
    store.delete(v1.id)
    assert store.latest(v1.id) is None
    with pytest.raises(ValueError):
        store.versions("../escape")


STATE: dict[str, Any] = {
    "orders": [
        {"id": "GW-1", "status": "placed", "lines": [{"sku": "OAT-1L", "qty": 24}]},
        {"id": "GW-2", "status": "cancelled", "lines": [{"sku": "MILK-1L", "qty": 6}]},
    ],
    "items": {"franzbroetchen": {"published_price_eur": 3.45}},
}


def test_walk_reads_dotted_paths() -> None:
    assert walk(STATE, "items.franzbroetchen.published_price_eur", None) == 3.45
    assert walk(STATE, "orders.last.status", None) == "cancelled"
    assert walk(STATE, "orders.0.lines.0.sku", None) == "OAT-1L"
    with pytest.raises(LookupError):
        walk(STATE, "items.nothing.price", None)


def test_orders_last_needs_a_new_order_since_the_baseline() -> None:
    assert walk(STATE, "orders.last.id", 1) == "GW-2"  # the list grew from 1 to 2
    with pytest.raises(LookupError, match="no new order"):
        walk(STATE, "orders.last.id", 2)  # nothing new: an old order cannot count


def test_an_obstacle_action_compiles_to_an_optional_step() -> None:
    banner = compile_action(
        Action(
            intent="Accept cookies", action="click", role="button", name="Accept all", obstacle=True
        ),
        PARAMS,
    )
    assert banner.optional
    assert not compile_action(
        Action(intent="Go", action="click", role="link", name="Cart"), PARAMS
    ).optional


async def test_a_crashing_run_still_finishes_visibly(tmp_path: Path) -> None:

    from typing import cast

    from backroom_api.agents.portals_admin import PortalAdmin
    from backroom_api.agents.runner import SkillRunner
    from backroom_api.browser import BrowserPool, SecretVault
    from backroom_api.config import Settings
    from backroom_api.contracts.events import RunFinished

    class DownAdmin:
        async def state(self, portal: str) -> dict[str, Any]:
            raise ConnectionError("portals are down")

    events: list[Any] = []

    async def sink(event: Any) -> None:
        events.append(event)

    runner = SkillRunner(
        Settings(),
        None,
        BrowserPool(),
        SkillStore(tmp_path),
        cast(PortalAdmin, DownAdmin()),
        SecretVault({}),
    )
    result = await runner.run("grainline.reorder_item", sink=sink)
    assert not result.ok and result.status == "failed"
    assert isinstance(events[-1], RunFinished) and events[-1].status == "failed"
    assert "portals are down" in events[-1].summary


def test_param_values_in_descriptions_are_templated_and_rendered_per_run() -> None:
    from backroom_api.skills.compiler import render_text, template_text

    text = template_text("Set quantity to 24 for the OAT-1L row, not 240 or 2.4", PARAMS)
    assert text == "Set quantity to {{qty}} for the {{sku}} row, not 240 or 2.4"
    assert render_text(text, {"qty": 28, "sku": "MILK-1L"}) == (
        "Set quantity to 28 for the MILK-1L row, not 240 or 2.4"
    )
    assert render_text("Open {{unknown}}", {}) == "Open {{unknown}}"
    step = compile_action(
        Action(intent="Type 24", action="fill", role="spinbutton", name="Quantity", value="24"),
        PARAMS,
    )
    assert step.intent == "Type {{qty}}"


def test_heal_summary_is_short_and_never_cut_mid_word() -> None:
    from backroom_api.replay.engine import heal_summary
    from backroom_api.skills.schema import StepChange

    names = [("Email", "E-Mail"), ("Password", "Passwort"), ("Sign in", "Anmelden"),
             ("Verify", "Bestätigen"), ("Catalog", "Katalog"), ("Search", "Suchen")]  # fmt: skip
    changes = [
        StepChange(op="insert", step_index=1, field="step", before=None,
                   after={"intent": "Accept the cookie banner to clear the dialog over the page"}),
        *[StepChange(step_index=i, field="target", before={"role": "x", "name": a},
                     after={"role": "x", "name": b}) for i, (a, b) in enumerate(names, 2)],
    ]  # fmt: skip
    note = heal_summary(changes)
    assert note.startswith("Added 1 step: 'Accept the cookie banner to clear the dialog…'.")
    assert "6 labels changed: 'Email' → 'E-Mail', 'Password' → 'Passwort'" in note
    assert note.endswith("and 2 more.") and len(note) < 260
