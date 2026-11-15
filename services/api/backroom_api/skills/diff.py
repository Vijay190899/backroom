"""Diff two versions of a skill, as the review-style list the Skills page shows.

Steps are aligned by (action, value_template), which a re-skin does not change (a button
is renamed, not turned into a fill). Within an aligned pair, every differing field is one
`update`; steps only in the newer version are `insert`s (e.g. dismissing a cookie banner);
steps only in the older one are `delete`s.
"""

from difflib import SequenceMatcher
from typing import Any

from backroom_api.skills.schema import Skill, SkillDiff, Step, StepChange

_FIELDS = ("intent", "target", "fallbacks", "value_template", "expect", "timeout_ms", "optional")


def _key(step: Step) -> tuple[str, str | None]:
    return step.action, step.value_template


def _dump(step: Step, field: str) -> Any:
    value = getattr(step, field)
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, list):
        return [v.model_dump(exclude_none=True) for v in value]  # type: ignore[union-attr]
    return value.model_dump(exclude_none=True)


def field_changes(before: Step, after: Step, index: int) -> list[StepChange]:
    """One `update` per field that differs between two versions of the same step."""
    return [
        StepChange(step_index=index, field=f, before=_dump(before, f), after=_dump(after, f))
        for f in _FIELDS
        if _dump(before, f) != _dump(after, f)
    ]


def diff_skills(old: Skill, new: Skill) -> SkillDiff:
    matcher = SequenceMatcher(
        a=[_key(s) for s in old.steps], b=[_key(s) for s in new.steps], autojunk=False
    )
    changes: list[StepChange] = []
    for tag, a0, a1, b0, b1 in matcher.get_opcodes():
        if tag == "equal":
            for offset in range(a1 - a0):
                before, after = old.steps[a0 + offset], new.steps[b0 + offset]
                for field in _FIELDS:
                    if _dump(before, field) != _dump(after, field):
                        changes.append(
                            StepChange(
                                step_index=b0 + offset,
                                field=field,
                                before=_dump(before, field),
                                after=_dump(after, field),
                            )
                        )
        else:
            paired = min(a1 - a0, b1 - b0) if tag == "replace" else 0
            # In a replaced block, pair the leftover newer steps with the older ones from the
            # end (the real action is last; what comes before it is an inserted obstacle step).
            extra_new = (b1 - b0) - paired
            for i in range(extra_new):
                step = new.steps[b0 + i]
                changes.append(
                    StepChange(
                        op="insert",
                        step_index=b0 + i,
                        field="step",
                        before=None,
                        after=step.model_dump(exclude_none=True),
                    )
                )
            for i in range(paired):
                before, after = old.steps[a1 - paired + i], new.steps[b1 - paired + i]
                for field in _FIELDS:
                    if _dump(before, field) != _dump(after, field):
                        changes.append(
                            StepChange(
                                step_index=b1 - paired + i,
                                field=field,
                                before=_dump(before, field),
                                after=_dump(after, field),
                            )
                        )
            for i in range((a1 - a0) - paired):
                step = old.steps[a0 + i]
                changes.append(
                    StepChange(
                        op="delete",
                        step_index=a0 + i,
                        field="step",
                        before=step.model_dump(exclude_none=True),
                        after=None,
                    )
                )
    return SkillDiff(
        skill_id=new.id, from_version=old.version, to_version=new.version, changes=changes
    )
