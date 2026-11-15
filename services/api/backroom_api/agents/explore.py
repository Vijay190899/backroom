"""Explore loop: a model operates a portal one action at a time (mode `explore`/`heal`).

Each turn the model sees the goal, the actions so far and the current ARIA snapshot, and
answers with exactly one tool call: `act` (click, fill, ...) or `finish`. The loop owns
everything that must not depend on the model: it resolves the element ref to role + name,
refuses elements that are not unique on the page (a skill could not replay them), runs the
action through the same `Executor` that replays use, and records what worked.

The model never types a secret: it names a vault key (`secret`) and the executor types the
value. The model never decides that the task succeeded; the caller checks postconditions.
"""

import asyncio
import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import anthropic
from playwright.async_api import Page

from backroom_api.agents.recorder import RunRecorder
from backroom_api.browser.executor import Executor, StepOutcome
from backroom_api.browser.snapshot import Observation, observe
from backroom_api.browser.vault import SecretVault
from backroom_api.contracts.common import Mode
from backroom_api.contracts.events import StepFinished, StepStarted
from backroom_api.llm.meter import BudgetExceededError
from backroom_api.llm.registry import Role
from backroom_api.skills.compiler import Action
from backroom_api.skills.schema import Locator, Step, StepAction

ACTIONS: tuple[StepAction, ...] = (
    "click",
    "fill",
    "fill_secret",
    "select",
    "press",
    "goto",
    "totp",
    "wait_for",
)
LLM_TIMEOUT_S = 30  # one step decision; the SDK default would wait minutes
_NEEDS_REF = {"click", "fill", "fill_secret", "select", "totp"}

SYSTEM = """You operate a web portal on behalf of a café owner, through tool calls. \
One tool call per turn: `act` to do one thing, or `finish` when you are done.

How to work:
- Each turn you get the goal, the actions already done, and the current page as an ARIA \
snapshot. Refer to elements by their `ref` (like f3e38). Never invent a ref.
- Only act on elements that have a name. If several elements on the page share a name \
(for example one "Add to cart" button per product row), narrow the page first, for \
example with the search box, so exactly one is left. The system rejects ambiguous clicks.
- Sign-in: never type credentials yourself. Use action `fill_secret` with the `secret` key \
that fits the field (listed in the task), and `totp` for a one-time code field.
- Pop-ups, cookie banners and "what's new" dialogs block the page: dismiss them first. \
If navigation links are hidden behind a menu button, open the menu first.
- Fields you fill with a secret look empty in the snapshot (the value is hidden on purpose). \
Do not re-fill them: once a field is filled, go on to the next field or the submit button.
- Prefer the visible controls over guessing URLs. Use `goto` only for a path given in the task.
- Do exactly what the goal says. Do not buy, change or delete anything else.
- Call `finish` with success=true only when the page shows the goal is done (for example an \
order confirmation). If you are stuck, call `finish` with success=false and say why.
- Keep each `intent` short and plain, e.g. "Add oat milk to the cart"."""


def tools(secret_keys: list[str], healing: bool = False) -> list[dict[str, Any]]:
    completes: dict[str, Any] = {
        "completes_step": {
            "type": "boolean",
            "description": "true ONLY for the action that performs the stuck step itself; "
            "false for clearing a pop-up or opening a menu first.",
        }
    }
    return [
        {
            "name": "act",
            "description": "Perform one action on the current page.",
            "strict": True,
            "input_schema": {
                "type": "object",
                "properties": {
                    "intent": {"type": "string", "description": "Short plain sentence."},
                    "action": {"type": "string", "enum": list(ACTIONS)},
                    "ref": {
                        "type": "string",
                        "description": "Element ref from the snapshot (not goto/press/wait_for).",
                    },
                    "value": {
                        "type": "string",
                        "description": "Text to type, option to pick, key to press, path to open, "
                        "or text to wait for.",
                    },
                    "secret": {
                        "type": "string",
                        "enum": secret_keys,
                        "description": "Vault key for fill_secret / totp.",
                    },
                    "obstacle": {
                        "type": "boolean",
                        "description": "true if this action only clears a pop-up, cookie banner "
                        "or dialog, or opens a menu, i.e. something that may not be there next "
                        "time.",
                    },
                    **(completes if healing else {}),
                },
                "required": ["intent", "action"],
                "additionalProperties": False,
            },
        },
        {
            "name": "finish",
            "description": "End the task.",
            "strict": True,
            "input_schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "summary": {"type": "string", "description": "One sentence, plain English."},
                },
                "required": ["success", "summary"],
                "additionalProperties": False,
            },
        },
    ]


@dataclass
class ExploreResult:
    ok: bool  # the agent called `finish` with success=true
    actions: list[Action] = field(default_factory=list[Action])
    summary: str = ""
    reason: str | None = None  # why it stopped when not ok: "budget", "max_steps", "stuck", ...
    finished: bool = False  # the agent called `finish`


def _turn_text(
    goal: str,
    params: Mapping[str, Any],
    secret_keys: list[str],
    history: list[str],
    obs: Observation,
) -> str:
    done = "\n".join(f"{i}. {h}" for i, h in enumerate(history, 1)) or "(nothing yet)"
    return (
        f"GOAL: {goal}\n"
        f"PARAMS: {json.dumps(dict(params))}\n"
        f"SECRET KEYS you may use: {', '.join(secret_keys)}\n\n"
        f"ACTIONS SO FAR:\n{done}\n\n"
        f"CURRENT PAGE: {obs.url}  (title: {obs.title})\n{obs.text}"
    )


async def _unique(page: Page, role: str, name: str) -> int:
    return await page.get_by_role(role, name=name, exact=True).count()  # type: ignore[arg-type]


async def explore(
    *,
    page: Page,
    executor: Executor,
    rec: RunRecorder,
    vault: SecretVault,
    goal: str,
    params: Mapping[str, Any],
    portal: str,
    role: Role = "worker",
    mode: Mode = "explore",
    max_steps: int = 25,
    max_usd: float = 0.05,
    first_index: int = 0,
) -> ExploreResult:
    """Run the loop until the agent finishes, runs out of steps, or exceeds `max_usd`."""
    secret_keys = [k for k in vault.keys() if k.startswith(portal + "_")]  # noqa: SIM118
    system = [{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}]
    result = ExploreResult(ok=False)
    history: list[str] = []
    usd0 = rec.usd
    bad_turns = 0
    repeated: dict[str, int] = {}
    done_here: set[tuple[Any, ...]] = set()  # actions already done on the current page
    last_url = page.url

    for _ in range(max_steps):
        if rec.usd - usd0 > max_usd:
            result.reason = "budget"
            return result
        obs = await observe(page)
        refs = {e.ref: e for e in obs.elements}
        try:
            reply = await asyncio.wait_for(
                rec.call(
                    role,
                    system=system,
                    tools=tools(secret_keys, healing=mode == "heal"),
                    messages=[
                        {
                            "role": "user",
                            # The snapshot shows typed values (a username, a one-time
                            # code): redact, so secrets never reach a prompt (CLAUDE.md).
                            "content": vault.redact(
                                _turn_text(goal, params, secret_keys, history, obs)
                            ),
                        }
                    ],
                    max_tokens=1024,
                ),
                timeout=LLM_TIMEOUT_S,
            )
        except (anthropic.APIError, TimeoutError, BudgetExceededError) as exc:
            # A failed model call ends this attempt cleanly; the caller climbs the ladder
            # or reports the run as failed instead of crashing it.
            result.reason = f"model call failed: {type(exc).__name__}"
            return result
        message = reply.message
        call = next((b for b in message.content if b.type == "tool_use"), None)
        if message.stop_reason != "tool_use" or call is None:
            bad_turns += 1
            history.append("(no tool call was made; call `act` or `finish`)")
            if bad_turns >= 3:
                result.reason = f"no tool call (stop_reason={message.stop_reason})"
                return result
            continue
        args: dict[str, Any] = dict(call.input) if isinstance(call.input, dict) else {}

        if call.name == "finish":
            result.finished = True
            result.summary = str(args.get("summary", ""))
            result.ok = bool(args.get("success"))
            if not result.ok:
                result.reason = "agent gave up"
            return result

        action = str(args.get("action", ""))
        intent = str(args.get("intent") or action)
        problem = _validate(action, args, refs, secret_keys)
        element = refs.get(str(args.get("ref", "")))
        if page.url != last_url:
            done_here.clear()
            last_url = page.url
        signature = (
            action,
            element.role if element else None,
            element.name if element else None,
            args.get("value"),
            args.get("secret"),
        )
        if problem is None and action != "wait_for" and signature in done_here:
            problem = (
                "you already did exactly this on this page. Its effect may not be visible "
                "(secret fields look empty). Continue with the next step of the goal"
            )
        if problem is None and element is not None and action in _NEEDS_REF:
            count = await _unique(page, element.role, element.name)
            if count > 1:
                problem = (
                    f"{count} elements are named {element.role} {element.name!r}; narrow the page "
                    "first (for example search) so only one is left"
                )
            elif count == 0:
                problem = f"{element.role} {element.name!r} is not visible right now"
        if problem is not None:
            history.append(f"{intent} -> REJECTED: {problem}")
            repeated[problem] = repeated.get(problem, 0) + 1
            if repeated[problem] >= 3:
                result.reason = f"stuck: {problem}"
                return result
            continue
        assert action in ACTIONS

        value = str(args["value"]) if args.get("value") is not None else None
        secret = str(args["secret"]) if args.get("secret") else None
        step = Step(
            intent=intent,
            action=action,  # type: ignore[arg-type]
            target=Locator(role=element.role, name=element.name) if element else None,
            value_template=(
                "{{secret:" + (secret or "") + "}}" if action in ("fill_secret", "totp") else value
            ),
        )
        index = first_index + len(result.actions)
        await rec.emit(
            StepStarted,
            index=index,
            intent=intent,
            action=step.action,
            target=step.target,
            value=None if action in ("fill_secret", "totp") else value,
            mode=mode,
        )
        url_before = page.url
        outcome = await executor.run(step, {})
        await finish_step(rec, index, outcome)
        if not outcome.ok:
            history.append(f"{intent} -> FAILED ({outcome.error_kind}): {outcome.error}")
            repeated[intent] = repeated.get(intent, 0) + 1
            if repeated[intent] >= 3:
                result.reason = f"stuck: {intent} keeps failing"
                return result
            continue
        recorded = Action(
            intent=intent,
            action=step.action,
            role=element.role if element else None,
            name=element.name if element else None,
            value=None if action in ("fill_secret", "totp") else value,
            secret=secret,
            url_before=url_before,
            url_after=page.url,
            obstacle=args.get("obstacle") is True,
        )
        result.actions.append(recorded)
        if mode == "heal" and args.get("completes_step") is True:
            result.ok = True  # the stuck step is done: no extra `finish` round trip
            return result
        done_here.add(signature)
        hidden = " (the value is hidden on the page)" if secret else ""
        history.append(f"{intent} -> ok{hidden}")

    result.reason = "max_steps"
    return result


def _validate(
    action: str, args: Mapping[str, Any], refs: Mapping[str, Any], secret_keys: list[str]
) -> str | None:
    if action not in ACTIONS:
        return f"unknown action {action!r}"
    if action in _NEEDS_REF:
        ref = str(args.get("ref", ""))
        element = refs.get(ref)
        if element is None:
            return f"ref {ref!r} is not on the current page"
        if not element.name:
            return f"ref {ref!r} has no accessible name, so it cannot be targeted; pick another"
    if action in ("fill", "select", "press", "goto") and args.get("value") is None:
        return f"{action} needs a value"
    if action in ("fill_secret", "totp") and args.get("secret") not in secret_keys:
        return f"{action} needs a `secret` key from: {', '.join(secret_keys)}"
    return None


async def finish_step(rec: RunRecorder, index: int, outcome: StepOutcome) -> None:
    calls, tin, tout, usd = rec.take_pending()
    rec.step_done()
    await rec.emit(
        StepFinished,
        index=index,
        ok=outcome.ok,
        duration_ms=outcome.duration_ms,
        llm_calls=calls,
        tokens_in=tin,
        tokens_out=tout,
        usd=usd,
        error=outcome.error,
    )
