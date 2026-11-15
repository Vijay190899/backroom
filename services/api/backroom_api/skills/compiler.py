"""Compile a successful explore run into a skill (PRD §8.2).

The explore agent acts on whatever it sees; the compiler keeps only what replays:
role + accessible name as the locator, the typed value turned back into `{{param}}`
wherever it equals a task parameter, a text/label fallback for rung-1 healing, and a path
expectation after every step that navigated.
"""

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlsplit

from backroom_api.contracts.common import Portal, SkillTask
from backroom_api.skills.schema import (
    Expect,
    Fallback,
    LabelFallback,
    Locator,
    Postcondition,
    Skill,
    Step,
    StepAction,
    TextFallback,
)

_FIELD_ROLES = {"textbox", "spinbutton", "combobox", "searchbox", "checkbox", "radio", "slider"}


@dataclass(frozen=True)
class Action:
    """One action the explore agent performed successfully."""

    intent: str
    action: StepAction
    role: str | None = None
    name: str | None = None
    value: str | None = None  # what was typed/selected/pressed/opened; never a secret
    secret: str | None = None  # vault key for fill_secret / totp
    url_before: str = ""
    url_after: str = ""
    obstacle: bool = False  # it only cleared a pop-up/banner/menu that may not come back


def _number(text: str) -> float | None:
    try:
        return float(text.replace(",", "."))
    except ValueError:
        return None


def template_value(action: str, value: str, params: Mapping[str, Any]) -> str:
    """Turn a typed value back into `{{param}}` where it equals a parameter."""
    if action == "goto":
        # a path that contains a parameter (e.g. an item id) is parameterised in place
        for key, param in params.items():
            if isinstance(param, str) and len(param) >= 3 and param in value:
                value = value.replace(param, "{{" + key + "}}")
        return value
    if action not in ("fill", "select"):
        return value
    for key, param in sorted(params.items(), key=lambda kv: -len(str(kv[1]))):
        if value == str(param):
            return "{{" + key + "}}"
        if isinstance(param, (int, float)) and not isinstance(param, bool):
            typed = _number(value)
            if typed is not None and abs(typed - float(param)) < 1e-9:
                return "{{" + key + "}}"
    return value


def template_text(text: str, params: Mapping[str, Any]) -> str:
    """Parameter values inside a step's description ("Set quantity to 24") become
    `{{qty}}`, so a replay with other params never shows the explore run's values."""
    for key, param in sorted(params.items(), key=lambda kv: -len(str(kv[1]))):
        if isinstance(param, bool):
            continue
        if isinstance(param, str) and len(param) >= 3:
            text = text.replace(param, "{{" + key + "}}")
        elif isinstance(param, (int, float)):
            text = re.sub(rf"(?<![\w.]){re.escape(str(param))}(?![\w.])", "{{" + key + "}}", text)
    return text


def render_text(text: str, params: Mapping[str, Any]) -> str:
    """The display form of a templated description (unknown names stay as they are)."""
    return re.sub(
        r"\{\{([a-z][a-z0-9_]*)\}\}",
        lambda m: str(params.get(m.group(1), m.group(0))),
        text,
    )


def fallbacks_for(role: str | None, name: str | None) -> list[Fallback]:
    if not role or not name:
        return []
    if role in _FIELD_ROLES:
        return [LabelFallback(label=name)]
    return [TextFallback(text=name)]


def _path_expect(before: str, after: str) -> Expect | None:
    new_path = urlsplit(after).path
    if not after or new_path == urlsplit(before).path:
        return None
    # ids that change per run (order GW-10483) must not be baked into the expectation
    pattern = re.sub(r"\d+", r"\\d+", re.escape(new_path))
    return Expect(url_pattern=f"^{pattern}$")


def compile_action(act: Action, params: Mapping[str, Any]) -> Step:
    target = Locator(role=act.role, name=act.name) if act.role and act.name else None
    if act.action in ("fill_secret", "totp"):
        template: str | None = "{{secret:" + str(act.secret) + "}}"
    elif act.value is not None:
        template = template_value(act.action, act.value, params)
    else:
        template = None
    return Step(
        intent=template_text(act.intent, params),
        action=act.action,
        target=target,
        fallbacks=fallbacks_for(act.role, act.name) if act.action != "goto" else [],
        value_template=template,
        expect=_path_expect(act.url_before, act.url_after) if act.action != "goto" else None,
        optional=act.obstacle,
    )


def compile_skill(
    *,
    task: SkillTask,
    portal: Portal,
    start_path: str,
    actions: Sequence[Action],
    params: Mapping[str, Any],
    params_schema: dict[str, Any],
    postconditions: list[Postcondition],
) -> Skill:
    steps = [Step(intent="Open the portal", action="goto", value_template=start_path)]
    steps += [compile_action(a, params) for a in actions]
    return Skill(
        id=task,
        task=task,
        portal=portal,
        version=1,
        params_schema=params_schema,
        steps=steps,
        postconditions=postconditions,
        created_at=datetime.now(UTC),
    )
