"""Detector output (PRD §8.4 step 1). Detectors compute every number; the planner
only writes copy around them, and the number guard checks that copy against
`Candidate.numbers` (rules in docs/CONTRACTS.md §6)."""

from typing import Any, Literal

from pydantic import AwareDatetime, Field, model_validator

from backroom_api.contracts.common import CandidateKind, Contract, Portal, SkillTask, Unit


class EvidenceNumber(Contract):
    """One computed number the copy may quote."""

    key: str  # stable name, e.g. "margin_after_pct"
    value: float  # pct values are percent (71.0, not 0.71)
    unit: Unit
    label: str  # human label for the evidence drawer


class Evidence(Contract):
    """One item in the evidence drawer: a query result, a fact, a chart or an invoice."""

    id: str
    kind: Literal["sql", "fact", "chart", "invoice"]
    label: str
    sql: str | None = None
    columns: list[str] = Field(default_factory=list[str])
    rows: list[list[Any]] = Field(default_factory=list[list[Any]])
    fact_ids: list[str] = Field(default_factory=list[str])
    # Shows the "Synthetic" chip (docs/DATA.md).
    synthetic: bool = False


class ProposedAction(Contract):
    """What the card would do. A recommendation only (e.g. trimming a shift, which no
    portal does) has no task and `executable: false`."""

    task: SkillTask | None
    portal: Portal | None
    params: dict[str, Any] = Field(default_factory=dict[str, Any])
    executable: bool

    @model_validator(mode="after")
    def _executable_has_task(self) -> "ProposedAction":
        if self.executable != (self.task is not None and self.portal is not None):
            raise ValueError("executable actions need a task and a portal; others neither")
        return self


class Candidate(Contract):
    id: str  # deterministic: "<kind>:<subject_id>:<as_of date>"
    kind: CandidateKind
    subject_id: str  # memory entity id, e.g. "product:franzbroetchen"
    title_hint: str  # template title, used when the planner's copy fails the guard
    impact_eur_weekly: float
    numbers: list[EvidenceNumber]
    evidence: list[Evidence]
    proposed_action: ProposedAction | None
    as_of: AwareDatetime
    computed_at: AwareDatetime
