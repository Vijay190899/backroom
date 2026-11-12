"""Request and response bodies of the HTTP API (ARCHITECTURE §3, "Key API").

Mirrored in zod in `apps/web/src/lib/contracts.ts`. `/health` is already defined by
`routes/health.py` and is not repeated here.
"""

from typing import Any, Literal

from pydantic import AwareDatetime, Field

from backroom_api.contracts.candidate import Evidence, EvidenceNumber
from backroom_api.contracts.common import CandidateKind, Contract, Mode, Portal, SkillTask
from backroom_api.contracts.events import RunStatus, RunTotals
from backroom_api.skills.schema import Skill, SkillDiff


class ApiError(Contract):
    """Body of every 4xx/5xx except `/health`: `{"error": {...}}`."""

    code: str  # "not_found", "budget_exceeded", "live_mode_locked", ...
    message: str


class ErrorResponse(Contract):
    error: ApiError


# --- Brief: GET /brief/today ---------------------------------------------------


class GuardResult(Contract):
    passed: bool
    regenerations: int  # 0 or 1; after that the card falls back to template copy
    unmatched: list[str] = Field(default_factory=list[str])  # numbers that had no evidence


class ActionCard(Contract):
    id: str  # action id, used by approve/reject
    candidate_id: str
    kind: CandidateKind
    rank: int  # 1..3, by impact
    title: str
    impact_eur_weekly: float
    why: str  # one sentence, owner voice
    evidence: list[Evidence]
    numbers: list[EvidenceNumber]  # what the guard checked the copy against
    task: SkillTask | None  # None for a recommendation only
    portal: Portal | None
    params: dict[str, Any] = Field(default_factory=dict[str, Any])
    executable: bool
    status: Literal["proposed", "approved", "rejected", "running", "done", "failed"]
    # Set when the verifier adjusted the card for a preference: "Kept under your 8% cap".
    preference_note: str | None = None
    copy_source: Literal["llm", "template"]
    guard: GuardResult


class Brief(Contract):
    id: str
    generated_at: AwareDatetime
    as_of: AwareDatetime
    cards: list[ActionCard] = Field(max_length=3)
    cached: bool


# GET /brief/today?regenerate=1 streams SSE: `brief.skeleton` (how many cards are
# coming), one `brief.card` per card as it passes the guard, then `brief.done` with the
# full brief (the same body a cached GET returns).


class BriefSkeleton(Contract):
    type: Literal["brief.skeleton"] = "brief.skeleton"
    cards: int = Field(ge=0, le=3)


class BriefCardEvent(Contract):
    type: Literal["brief.card"] = "brief.card"
    card: ActionCard


class BriefDone(Contract):
    type: Literal["brief.done"] = "brief.done"
    brief: Brief


# --- Actions ---------------------------------------------------------------------


class ApproveResponse(Contract):
    """POST /actions/{id}/approve, header `Idempotency-Key`. A repeat with the same
    key returns the same run with `deduplicated: true` and starts nothing."""

    run_id: str
    action_id: str
    deduplicated: bool


class RejectRequest(Contract):
    reason: str = Field(min_length=1, max_length=500)


class RejectResponse(Contract):
    action_id: str
    episode_id: str
    # Preference facts the extractor wrote from the reason (may be empty).
    preference_fact_ids: list[str]


# --- Runs ---------------------------------------------------------------------------


class ContextPack(Contract):
    """Shipped with each run for display (PRD §F4)."""

    as_of: AwareDatetime
    fact_ids: list[str]
    text: str  # the compact triples the agent saw
    tokens: int
    budget_tokens: int


class RunSummary(Contract):
    """GET /runs/{id}; the live detail streams from GET /runs/{id}/events."""

    id: str
    action_id: str
    task: SkillTask
    portal: Portal
    status: RunStatus
    mode: Mode
    skill_version: int | None
    chaos_seed: int
    started_at: AwareDatetime
    finished_at: AwareDatetime | None
    totals: RunTotals
    summary: str | None = None
    context_pack: ContextPack | None = None  # None for a replay (no LLM, no pack)


class UndoResponse(Contract):
    """POST /runs/{id}/undo: starts a run of the inverse action (cancel the order,
    restore the old price). 409 when the run has `undo_available: false`."""

    run_id: str  # the new undo run
    undo_of: str


class HumanReply(Contract):
    """POST /runs/{id}/human, answering an `ask_human` event. The run resumes (the
    human did the step, e.g. solved a CAPTCHA) or is cancelled. Returns RunSummary."""

    action: Literal["resume", "cancel"]
    note: str | None = Field(default=None, max_length=500)


# --- Skills: GET /skills, GET /skills/{id}/versions -----------------------------------


class SkillSummary(Contract):
    id: str
    task: SkillTask
    portal: Portal
    latest_version: int
    runs: int
    success_rate: float | None = Field(ge=0, le=1)  # None before the first run
    mean_latency_ms: float | None
    mean_usd: float | None
    updated_at: AwareDatetime


class SkillVersions(Contract):
    skill_id: str
    versions: list[Skill]  # oldest first
    diffs: list[SkillDiff]  # diffs[i] goes from versions[i] to versions[i + 1]


# --- Memory: GET /memory/graph?as_of=, GET /memory/facts/{id} ----------------------------

EntityType = Literal[
    "business",
    "product",
    "ingredient",
    "supplier",
    "staff",
    "shift",
    "portal",
    "skill",
    "preference",
    "weather_day",
    "holiday",
    "insight",
    "action",
]
EpisodeKind = Literal["invoice", "approval", "rejection", "chat", "run", "seed"]


class GraphNode(Contract):
    id: str  # "<type>:<slug>", e.g. "ingredient:butter"
    type: EntityType
    name: str


class GraphFact(Contract):
    """A fact valid at `as_of`. With `object_id` it is an edge; with `value` it is an
    attribute of the subject node."""

    id: str
    subject_id: str
    predicate: str  # snake_case, e.g. "unit_price_eur_per_kg"
    object_id: str | None
    value: Any = None
    valid_from: AwareDatetime
    valid_to: AwareDatetime | None
    confidence: float = Field(ge=0, le=1)


class MemoryGraph(Contract):
    as_of: AwareDatetime
    nodes: list[GraphNode]
    facts: list[GraphFact]


class EpisodeRef(Contract):
    id: str
    kind: EpisodeKind
    occurred_at: AwareDatetime
    summary: str


class FactDetail(Contract):
    fact: GraphFact
    recorded_at: AwareDatetime
    source: EpisodeRef | None
    supersedes: list[str]  # earlier fact ids on the same (subject, predicate)
    superseded_by: str | None
    invalidated_at: AwareDatetime | None  # when superseded_by was recorded


class InvoiceIngestResponse(Contract):
    """POST /memory/ingest/invoice."""

    episode_id: str
    fact_ids: list[str]
    superseded_fact_ids: list[str]


# --- Chaos: POST /chaos (dev/demo; forwards to the portals' /_admin/chaos) -----------------


class ChaosRequest(Contract):
    portal: Portal
    seed: int = Field(ge=0, le=999)


class ChaosState(Contract):
    portal: Portal
    seed: int
    # Family -> chosen variant, e.g. {"language": "de", "nav_position": "topbar"}.
    variants: dict[str, str]
