"""H3 tests: explore, replay and the heal ladder on the fixture page (PC only).

The model is scripted: each turn gets the prompt text (with the live ARIA snapshot) and
answers with a tool call, so these run offline and fast. They skip without Chromium.
"""

import re
from collections.abc import Callable
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any, cast

from playwright.async_api import Page

from backroom_api.agents.explore import explore
from backroom_api.agents.recorder import RunRecorder
from backroom_api.browser import Allowlist, Executor, SecretVault
from backroom_api.config import Settings
from backroom_api.contracts.events import (
    AskHuman,
    HealAttempt,
    HealFailed,
    HealStarted,
    HealSucceeded,
    RunEvent,
)
from backroom_api.llm.client import LLM
from backroom_api.replay.engine import replay
from backroom_api.skills.schema import Fallback, Locator, Skill, Step, TextFallback

Turn = Callable[[str], dict[str, Any]]


def ref_of(prompt: str, role: str, name: str) -> str:
    match = re.search(rf'{role} "{re.escape(name)}"[^\n]*\[ref=([A-Za-z0-9]+)\]', prompt)
    assert match, f"{role} {name!r} not in the prompt"
    return match.group(1)


def act(prompt: str, role: str, name: str, **kw: Any) -> dict[str, Any]:
    return {"name": "act", "input": {"ref": ref_of(prompt, role, name), **kw}}


class FakeLLM:
    """Stands in for `LLM`: replies from a script of turns, one per call."""

    def __init__(self, turns: list[Turn]) -> None:
        self.settings = Settings()
        self.turns = list(turns)
        self.calls: list[str] = []

    async def create(self, role: str, **kwargs: Any) -> Any:
        prompt = kwargs["messages"][0]["content"]
        self.calls.append(role)
        call = (
            self.turns.pop(0)(prompt)
            if self.turns
            else {"name": "finish", "input": {"success": False, "summary": "script ended"}}
        )
        block = SimpleNamespace(type="tool_use", name=call["name"], input=call["input"])
        usage = SimpleNamespace(input_tokens=100, output_tokens=20, cache_read_input_tokens=0)
        message = SimpleNamespace(content=[block], stop_reason="tool_use", usage=usage)
        return SimpleNamespace(message=message, cost=SimpleNamespace(usd=0.001))


def finish(success: bool) -> Turn:
    return lambda _p: {"name": "finish", "input": {"success": success, "summary": "done"}}


def build(page: Page, base_url: str, turns: list[Turn]) -> tuple[Executor, RunRecorder, FakeLLM]:
    llm = FakeLLM(turns)
    rec = RunRecorder("run_test", cast(LLM, llm))
    executor = Executor(page, SecretVault({}), Allowlist(base_url, ["/shop.html"]))
    return executor, rec, llm


def skill_with(steps: list[Step]) -> Skill:
    return Skill(
        id="grainline.reorder_item",
        task="grainline.reorder_item",
        portal="grainline",
        version=1,
        params_schema={"type": "object", "properties": {}},
        steps=steps,
        postconditions=[],
        created_at=datetime.now(UTC),
    )


def click(name: str, fallbacks: list[Fallback] | None = None) -> Step:
    return Step(
        intent=f"Click {name}",
        action="click",
        target=Locator(role="button", name=name),
        fallbacks=fallbacks or [],
    )


def kinds(events: list[RunEvent], cls: type) -> list[Any]:
    return [e for e in events if isinstance(e, cls)]


async def item_count(page: Page) -> str:
    return await page.inner_text("#count")


async def test_explore_records_actions_and_rejects_ambiguous_elements(
    page: Page, base_url: str
) -> None:
    executor, rec, llm = build(
        page,
        base_url,
        [
            lambda p: act(p, "link", "Cart", intent="Open cart", action="click"),  # nav + footer
            lambda p: act(p, "button", "Add to cart", intent="Add it", action="click"),
            finish(True),
        ],
    )
    result = await explore(
        page=page, executor=executor, rec=rec, vault=SecretVault({}), goal="Add one item",
        params={}, portal="fixture",
    )  # fmt: skip
    assert result.ok and result.finished
    assert [(a.action, a.name) for a in result.actions] == [("click", "Add to cart")]
    assert await item_count(page) == "1"
    assert len(llm.calls) == 3 and rec.totals().llm_calls == 3


async def test_explore_stops_at_the_cost_budget(page: Page, base_url: str) -> None:
    executor, rec, _ = build(
        page,
        base_url,
        [lambda p: act(p, "button", "Add to cart", intent="Add", action="click")] * 5,
    )
    result = await explore(
        page=page, executor=executor, rec=rec, vault=SecretVault({}), goal="x", params={},
        portal="fixture", max_usd=0.0015,
    )  # fmt: skip
    assert not result.ok and result.reason == "budget" and len(result.actions) < 5


async def test_a_fallback_hit_is_promoted_without_any_model_call(page: Page, base_url: str) -> None:
    executor, rec, llm = build(page, base_url, [])
    # The recorded name is gone, but the visible text still finds the button (rung 1).
    old = click("Add to bag", fallbacks=[TextFallback(text="Add to cart")])
    result = await replay(
        page=page, executor=executor, rec=rec, vault=SecretVault({}),
        skill=skill_with([old]), params={}, portal="fixture",
    )  # fmt: skip
    assert result.ok and result.healed and llm.calls == []
    assert result.steps[0].target == Locator(role="button", name="Add to cart")
    assert await item_count(page) == "1"
    # The old name is kept, so switching back to the old design is also a free rung-1 hit.
    assert TextFallback(text="Add to bag") in result.steps[0].fallbacks
    attempt = kinds(rec.events, HealAttempt)[0]
    assert (attempt.rung, attempt.ok, attempt.model) == ("fallback", True, None)


async def test_the_healer_replaces_a_stale_step_and_keeps_its_intent(
    page: Page, base_url: str
) -> None:
    executor, rec, llm = build(
        page,
        base_url,
        [
            lambda p: act(
                p, "button", "Add to cart", intent="Press the add button", action="click",
                completes_step=True,
            )
        ],
    )  # fmt: skip
    steps = [click("Add to cart"), click("Add to basket")]  # the second name no longer exists
    result = await replay(
        page=page, executor=executor, rec=rec, vault=SecretVault({}),
        skill=skill_with(steps), params={}, portal="fixture",
    )  # fmt: skip
    assert result.ok and result.healed and llm.calls == ["heal"]
    assert result.steps[1].target == Locator(role="button", name="Add to cart")
    assert result.steps[1].intent == "Click Add to basket"  # what the step is for is unchanged
    assert await item_count(page) == "2"
    started, succeeded = kinds(rec.events, HealStarted)[0], kinds(rec.events, HealSucceeded)[0]
    assert started.step_index == 1 and succeeded.new_version == 2
    assert [(c.op, c.field) for c in succeeded.changes] == [
        ("update", "target"),
        ("update", "fallbacks"),  # regenerated for the new name
    ]


async def test_an_obstacle_is_inserted_as_its_own_step(page: Page, base_url: str) -> None:
    executor, rec, _ = build(
        page,
        base_url,
        [
            lambda p: act(p, "button", "Load later", intent="Dismiss the popup", action="click"),
            lambda p: act(
                p, "button", "Add to cart", intent="Add", action="click", completes_step=True
            ),
        ],
    )  # fmt: skip
    result = await replay(
        page=page, executor=executor, rec=rec, vault=SecretVault({}),
        skill=skill_with([click("Add to basket")]), params={}, portal="fixture",
    )  # fmt: skip
    assert result.ok and [s.target.name for s in result.steps if s.target] == [
        "Load later",
        "Add to cart",
    ]
    ops = [(c.op, c.step_index) for c in result.changes]
    assert ops[0] == ("insert", 0) and ("update", 1) in ops
    # The pop-up may not be there next time: the inserted step is optional, the real one not.
    assert [s.optional for s in result.steps] == [True, False]


async def test_when_the_ladder_is_exhausted_the_run_hands_over_to_a_human(
    page: Page, base_url: str
) -> None:
    executor, rec, llm = build(page, base_url, [finish(False), finish(False)])
    result = await replay(
        page=page, executor=executor, rec=rec, vault=SecretVault({}),
        skill=skill_with([click("Add to basket")]), params={}, portal="fixture",
    )  # fmt: skip
    assert not result.ok and result.needs_human and result.escalated
    assert llm.calls == ["heal", "escalation"]
    rungs = [(a.rung, a.ok) for a in kinds(rec.events, HealAttempt)]
    assert rungs == [("healer", False), ("escalation", False)]
    assert kinds(rec.events, HealFailed) and kinds(rec.events, AskHuman)
    assert await item_count(page) == "0"  # nothing was guessed


async def test_events_are_numbered_without_gaps(page: Page, base_url: str) -> None:
    executor, rec, _ = build(page, base_url, [])
    await replay(
        page=page, executor=executor, rec=rec, vault=SecretVault({}),
        skill=skill_with([click("Add to cart")]), params={}, portal="fixture",
    )  # fmt: skip
    assert [e.seq for e in rec.events] == list(range(1, len(rec.events) + 1))
    assert rec.totals().steps == 1 and rec.totals().llm_calls == 0


async def test_an_absent_optional_step_is_skipped_without_healing(
    page: Page, base_url: str
) -> None:
    executor, rec, llm = build(page, base_url, [])
    banner = Step(
        intent="Dismiss the cookie banner",
        action="click",
        target=Locator(role="button", name="Alle akzeptieren"),
        optional=True,
    )
    result = await replay(
        page=page, executor=executor, rec=rec, vault=SecretVault({}),
        skill=skill_with([banner, click("Add to cart")]), params={}, portal="fixture",
    )  # fmt: skip
    assert result.ok and not result.healed and result.changes == []
    assert llm.calls == [] and not kinds(rec.events, HealStarted)
    assert await item_count(page) == "1"
