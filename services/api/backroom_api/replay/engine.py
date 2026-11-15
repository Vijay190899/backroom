"""Replay a compiled skill, and heal it when the site has changed (modes REPLAY / HEAL).

A warm replay is pure code: no LLM call, one `Executor.run` per step. When a step fails the
heal ladder runs, cheapest rung first (PRD §8.2):

1. **fallback**: the step's text/label fallback found the element; promote it to the target.
   Free, and already done inside the executor.
2. **healer**: the Haiku-class model gets the failing step and the live page, does that one
   step (dismissing a pop-up first if needed), then finishes. Its actions replace the step.
3. **escalation**: the same with the Sonnet-class model and more room.
4. **human**: the run pauses with `ask_human`; nothing is guessed.

A run that heals several steps produces one new version; it is stored by the caller only if
the run finishes with every postcondition passing (CONTRACTS §4).
"""

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from playwright.async_api import Page

from backroom_api.agents.explore import explore, finish_step
from backroom_api.agents.recorder import RunRecorder
from backroom_api.browser.executor import Executor, StepOutcome, display_value
from backroom_api.browser.vault import SecretVault
from backroom_api.contracts.events import (
    AskHuman,
    HealAttempt,
    HealFailed,
    HealRung,
    HealStarted,
    HealSucceeded,
    ModeChanged,
    StepStarted,
)
from backroom_api.llm import registry
from backroom_api.skills.compiler import compile_action, fallbacks_for, render_text
from backroom_api.skills.diff import field_changes
from backroom_api.skills.schema import Fallback, Locator, Skill, Step, StepChange

# Called on ask_human with (reason, step index); returns "resume", "cancel" or "timeout".
AskHumanHook = Callable[[str, int], Awaitable[str]]
REPLAY_TIMEOUT_MS = 2_500  # a step that is going to work does so well inside this
AFTER_HEAL_TIMEOUT_MS = 600  # the site has changed: do not wait long on each stale locator
OPTIONAL_TIMEOUT_MS = 800  # how long to look for a pop-up before deciding it is not there
MAX_FALLBACKS = 6  # labels remembered per step (each design the skill has seen)
MAX_HEALS = 15  # a full re-translation touches about a dozen steps
# (rung, role, max actions for that attempt)
LADDER: tuple[tuple[HealRung, registry.Role, int], ...] = (
    ("healer", "heal", 5),
    ("escalation", "escalation", 8),
)


@dataclass
class ReplayResult:
    ok: bool  # every step ran (postconditions are the caller's job)
    steps: list[Step]  # the effective steps; differs from the skill's if healed
    changes: list[StepChange] = field(default_factory=list[StepChange])
    healed: bool = False
    escalated: bool = False
    needs_human: bool = False
    cancelled: bool = False  # the owner answered ask_human with "cancel"
    failure: str | None = None
    notes: list[str] = field(default_factory=list[str])


def remembered_fallbacks(new: Locator, old: Step) -> list[Fallback]:
    """Fallbacks for a re-targeted step: the new name first, then every name the step had
    before. A portal that switches back to a design the skill has seen is then matched by
    rung 1 (free) instead of another model call."""
    out: list[Fallback] = []
    candidates = list(fallbacks_for(new.role, new.name))
    if old.target is not None:
        candidates += fallbacks_for(old.target.role, old.target.name)
    candidates += old.fallbacks
    seen: set[str] = set()
    for fb in candidates:
        key = fb.model_dump_json()
        if key not in seen:
            seen.add(key)
            out.append(fb)
    return out[:MAX_FALLBACKS]


def heal_goal(step: Step, index: int, error: str, params: Mapping[str, Any]) -> str:
    was = f"{step.target.role} {step.target.name!r}" if step.target else "the page"
    return (
        f"A saved automation is replaying a task and got stuck at step {index + 1}: "
        f"'{step.intent}' (action: {step.action}, it used to act on {was}). "
        f"What went wrong: {error}. The website may have been redesigned, translated or moved "
        "things around, or a pop-up may be in the way. Get past whatever is in the way, then "
        "perform exactly that step on the current page. Set completes_step=true on the one action "
        "that performs the step itself (false for dismissing a pop-up or opening a menu "
        "first). Do not do any later step. If the step turns out to be done already, call "
        "`finish`. "
        f"Values you may need: {dict(params)}."
    )


def replacement_changes(
    old: Step, new_steps: list[Step], at: int, old_index: int
) -> list[StepChange]:
    """What replacing `old` by `new_steps` changed: updates on the step that corresponds to
    it (the last new step with the same action), inserts for the others, or a delete if none
    corresponds."""
    main = next(
        (j for j in reversed(range(len(new_steps))) if new_steps[j].action == old.action), None
    )
    changes: list[StepChange] = []
    for j, step in enumerate(new_steps):
        if j == main:
            changes += field_changes(old, step, at + j)
        else:
            changes.append(
                StepChange(
                    op="insert",
                    step_index=at + j,
                    field="step",
                    before=None,
                    after=step.model_dump(exclude_none=True),
                )
            )
    if main is None:
        changes.append(
            StepChange(
                op="delete",
                step_index=old_index,
                field="step",
                before=old.model_dump(exclude_none=True),
                after=None,
            )
        )
    return changes


def _describe(old: Step, changes: list[StepChange]) -> str:
    parts: list[str] = []
    for c in changes:
        if c.op == "insert":
            parts.append(f"inserted '{c.after['intent']}'")
        elif c.op == "delete":
            parts.append(f"removed '{c.before['intent']}'")
        elif c.field == "target":
            was = c.before and c.before.get("name")
            now = c.after and c.after.get("name")
            parts.append(f"'{was}' is now '{now}'")
    return f"Step '{old.intent}': " + ("; ".join(parts) if parts else "updated")


async def replay(
    *,
    page: Page,
    executor: Executor,
    rec: RunRecorder,
    vault: SecretVault,
    skill: Skill,
    params: Mapping[str, Any],
    portal: str,
    can_heal: bool = True,
    max_usd: float = 0.25,
    ask_human: AskHumanHook | None = None,
) -> ReplayResult:
    """Replay `skill`. With `ask_human`, a step the ladder cannot fix pauses the run until
    the owner answers: "resume" retries the step (without another model heal), "cancel"
    ends the run. Without it, or on any other answer, the run ends `needs_human`."""
    steps = list(skill.steps)
    result = ReplayResult(ok=False, steps=steps)
    new_version = skill.version + 1
    timeout = REPLAY_TIMEOUT_MS
    heals = 0
    human_retry = False  # the owner said "resume": the next failure goes straight back
    i = 0
    while i < len(steps):
        step = steps[i]
        await rec.emit(
            StepStarted,
            index=i,
            intent=render_text(step.intent, params),
            action=step.action,
            target=step.target,
            value=display_value(step, params),
            mode="replay",
        )
        wait = min(timeout, OPTIONAL_TIMEOUT_MS) if step.optional else timeout
        outcome = await executor.run(step, params, timeout_ms=wait)
        if step.optional and outcome.error_kind == "locator_not_found":
            # The pop-up or banner is not there this time: nothing to do, nothing to heal.
            outcome = StepOutcome(ok=True, duration_ms=outcome.duration_ms)
        await finish_step(rec, i, outcome)

        if outcome.ok:
            if outcome.resolved_via not in (None, "target") and outcome.found is not None:
                found = Locator(role=outcome.found.role, name=outcome.found.name)
                promoted = step.model_copy(
                    update={"target": found, "fallbacks": remembered_fallbacks(found, step)}
                )
                changes = field_changes(step, promoted, i)
                await rec.emit(HealStarted, step_index=i, failure=_not_found(step))
                await rec.emit(HealAttempt, step_index=i, rung="fallback", model=None, ok=True)
                await rec.emit(
                    HealSucceeded, step_index=i, new_version=new_version, changes=changes
                )
                steps[i] = promoted
                result.changes += changes
                result.notes.append(_describe(step, changes))
                result.healed = True
                timeout = AFTER_HEAL_TIMEOUT_MS
            human_retry = False
            i += 1
            continue

        # --- the step failed: climb the heal ladder -----------------------------------
        failure = outcome.error or "step failed"
        if rec.usd >= max_usd:
            failure = f"{failure} (this run reached its ${max_usd:.2f} model budget)"
        if (
            outcome.error_kind == "blocked"
            or not can_heal
            or heals >= MAX_HEALS
            or rec.usd >= max_usd
            or human_retry
        ):
            answer = await _hand_over(rec, i, failure, ask_human, result)
            if answer != "resume":
                return result
            human_retry = True  # retry the step once as it is; no second model heal
            continue
        heals += 1
        result.healed = True
        timeout = AFTER_HEAL_TIMEOUT_MS
        replaced = await _heal_step(
            page=page,
            executor=executor,
            rec=rec,
            vault=vault,
            step=step,
            index=i,
            outcome=outcome,
            params=params,
            portal=portal,
            new_version=new_version,
            shift=len(steps) - len(skill.steps),
            result=result,
        )
        if replaced is None:
            answer = await _hand_over(rec, i, failure, ask_human, result)
            if answer != "resume":
                return result
            human_retry = True
            continue
        steps[i : i + 1] = replaced
        i += len(replaced)

    result.ok = True
    return result


def _not_found(step: Step) -> str:
    return (
        f"locator not found: {step.target.role} {step.target.name!r}" if step.target else "failed"
    )


async def _hand_over(
    rec: RunRecorder,
    index: int,
    failure: str,
    ask_human: "AskHumanHook | None",
    result: ReplayResult,
) -> str:
    """Pause for the owner (or give up without a hook). Returns the answer."""
    result.failure = failure
    await _give_up(rec, index, failure)
    answer = await ask_human(failure, index) if ask_human is not None else "timeout"
    if answer == "cancel":
        result.cancelled = True
    elif answer != "resume":
        result.needs_human = True
    return answer


async def _give_up(rec: RunRecorder, index: int, failure: str) -> None:
    await rec.emit(HealFailed, step_index=index, reason=failure)
    await rec.emit(
        AskHuman, reason=f"I could not get past step {index + 1}: {failure}", step_index=index
    )


async def _heal_step(
    *,
    page: Page,
    executor: Executor,
    rec: RunRecorder,
    vault: SecretVault,
    step: Step,
    index: int,
    outcome: StepOutcome,
    params: Mapping[str, Any],
    portal: str,
    new_version: int,
    shift: int,
    result: ReplayResult,
) -> list[Step] | None:
    error = outcome.error or "step failed"
    await rec.emit(HealStarted, step_index=index, failure=error)
    await rec.emit(
        ModeChanged, from_mode="replay", to_mode="heal", reason=f"step {index + 1} failed: {error}"
    )
    for rung, role, max_steps in LADDER:
        explored = await explore(
            page=page,
            executor=executor,
            rec=rec,
            vault=vault,
            goal=heal_goal(step, index, error, params),
            params=params,
            portal=portal,
            role=role,
            mode="heal",
            max_steps=max_steps,
            max_usd=0.05,
            first_index=index,
        )
        # No actions + a successful finish means the step had in fact already happened.
        done_already = explored.ok and not explored.actions
        ok = explored.ok
        model = registry.role_config(role, rec.settings).model
        await rec.emit(HealAttempt, step_index=index, rung=rung, model=model, ok=ok)
        if rung == "escalation":
            result.escalated = True
        if not ok:
            continue
        new_steps = (
            [step.model_copy(update={"expect": None})]
            if done_already
            else [compile_action(a, params) for a in explored.actions]
        )
        # What the step is for does not change when the site does; only how it is reached.
        # Every other action the healer needed (a pop-up, a menu) becomes an optional step.
        main = next(
            (j for j in range(len(new_steps) - 1, -1, -1) if new_steps[j].action == step.action),
            None,
        )
        new_steps = [
            s.model_copy(
                update={
                    "intent": step.intent,
                    "optional": step.optional,
                    "fallbacks": remembered_fallbacks(s.target, step) if s.target else s.fallbacks,
                }
            )
            if j == main
            else s.model_copy(update={"optional": True})
            for j, s in enumerate(new_steps)
        ]
        changes = replacement_changes(step, new_steps, at=index, old_index=index - shift)
        await rec.emit(HealSucceeded, step_index=index, new_version=new_version, changes=changes)
        await rec.emit(
            ModeChanged, from_mode="heal", to_mode="replay", reason=f"{rung} fixed step {index + 1}"
        )
        result.changes += changes
        result.notes.append(_describe(step, changes))
        return new_steps
    return None
