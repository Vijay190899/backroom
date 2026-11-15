"""Compiled skill format (PRD §8.2). Shared contract (L0): the PC's compiler, replay
and healer write and read it; the laptop's Skills page and diff view display it.

A skill is a parameterised, deterministic replay of a successful explore run.
Locator preference: `target` (ARIA role + accessible name), then the `fallbacks` in
order (label, text, css). `data-testid` is for our tests only and never appears in a
skill (docs/CONTRACTS.md §2).
"""

import re
from typing import Annotated, Any, Literal

from pydantic import AwareDatetime, Field, field_validator, model_validator

from backroom_api.contracts.common import Contract, Portal, SkillTask

StepAction = Literal[
    "click", "fill", "fill_secret", "select", "press", "goto", "wait_for", "extract", "totp"
]
# "{{qty}}" binds a param; "{{secret:grainline_password}}" binds a vault secret.
_TEMPLATE_RE = re.compile(r"\{\{(secret:)?([a-z][a-z0-9_]*)\}\}")
_SECRET_ONLY_RE = re.compile(r"\{\{secret:[a-z][a-z0-9_]*\}\}")
# Actions whose `target` is the element acted on.
_TARGETED: frozenset[str] = frozenset({"click", "fill", "fill_secret", "select", "totp"})


class Locator(Contract):
    role: str  # ARIA role, e.g. "button"
    name: str  # accessible name, e.g. "Add to cart"


class LabelFallback(Contract):
    label: str


class TextFallback(Contract):
    text: str


class CssFallback(Contract):
    css: str


Fallback = LabelFallback | TextFallback | CssFallback


class Expect(Contract):
    """What must be true after the step. Any field left out is not checked."""

    url_pattern: str | None = None  # regex matched against the path
    visible: Locator | None = None
    text: str | None = None


class Step(Contract):
    intent: str  # one line, shown in the timeline: "Add oat milk to the cart"
    action: StepAction
    target: Locator | None = None
    fallbacks: list[Fallback] = Field(default_factory=list[Fallback])
    value_template: str | None = None
    expect: Expect | None = None
    timeout_ms: Annotated[int, Field(gt=0, le=30_000)] = 5_000

    @model_validator(mode="after")
    def _check_shape(self) -> "Step":
        if self.action in _TARGETED and self.target is None and not self.fallbacks:
            raise ValueError(f"{self.action} needs a target or a fallback")
        if self.action in ("fill_secret", "totp"):
            if self.value_template is None or not _SECRET_ONLY_RE.fullmatch(self.value_template):
                raise ValueError(f"{self.action} needs a {{{{secret:key}}}} value_template")
        elif self.value_template and "secret:" in self.value_template:
            # A secret in a plain fill would be typed visibly and logged.
            raise ValueError("secrets may only be used by fill_secret or totp")
        if self.action in ("goto", "press") and not self.value_template:
            raise ValueError(f"{self.action} needs a value_template (path or key)")
        return self


class Postcondition(Contract):
    """Checked once the steps are done. `portal_state` asks the portal's admin state
    endpoint (docs/CONTRACTS.md §2), so a run can never "succeed" on looks alone.

    `equals` is rendered with the params, then parsed as JSON when it parses (so "3.6"
    is the number 3.6 and equals 3.60) and kept as a string otherwise ("placed")."""

    kind: Literal["url_matches", "text_visible", "portal_state"]
    value: str  # regex, text, or a dotted state path such as "orders.last.status"
    equals: str | None = None  # for portal_state: expected value (templated)


class SkillStats(Contract):
    runs: int = 0
    successes: int = 0
    mean_latency_ms: float | None = None
    mean_usd: float | None = None
    last_run_at: AwareDatetime | None = None


class Skill(Contract):
    id: str  # "<portal>.<verb>", same as the task, e.g. "grainline.reorder_item"
    task: SkillTask
    portal: Portal
    version: Annotated[int, Field(ge=1)]
    parent_version: int | None = None  # set on healed versions
    heal_note: str | None = None  # why this version exists ("Step 4 label changed")
    params_schema: dict[str, Any]  # JSON Schema for the params
    steps: list[Step]
    postconditions: list[Postcondition]
    stats: SkillStats = Field(default_factory=SkillStats)
    created_at: AwareDatetime

    @field_validator("steps")
    @classmethod
    def _non_empty(cls, steps: list[Step]) -> list[Step]:
        if not steps:
            raise ValueError("a skill needs at least one step")
        return steps

    @model_validator(mode="after")
    def _params_are_declared(self) -> "Skill":
        declared = set(self.params_schema.get("properties", {}))
        for i, step in enumerate(self.steps):
            for is_secret, name in _TEMPLATE_RE.findall(step.value_template or ""):
                if not is_secret and name not in declared:
                    raise ValueError(f"step {i} uses undeclared param {name!r}")
        if self.parent_version is not None and self.parent_version >= self.version:
            raise ValueError("parent_version must be lower than version")
        return self


class StepChange(Contract):
    """One change between two versions, rendered like a code review line.

    `update`: `field` of the step changed. `insert`: a new step (field "step", `before`
    null, `after` the Step). `delete`: a removed step (field "step", `after` null).
    `step_index` is the index in the newer version for update and insert, and in the
    older version for delete. Changes are listed in step order.
    """

    op: Literal["update", "insert", "delete"] = "update"
    step_index: int
    field: str  # "target", "fallbacks", "expect", ... or "step"
    before: Any
    after: Any

    @model_validator(mode="after")
    def _check_op(self) -> "StepChange":
        if self.op != "update" and self.field != "step":
            raise ValueError("insert and delete changes use field 'step'")
        if (self.op == "insert" and self.before is not None) or (
            self.op == "delete" and self.after is not None
        ):
            raise ValueError("insert has no before; delete has no after")
        return self


class SkillDiff(Contract):
    skill_id: str
    from_version: int
    to_version: int
    changes: list[StepChange]
