"""Run events, streamed over SSE from `GET /runs/{id}/events` (PRD §F2, §8.5).

Wire format, one event per SSE message:

    id: <seq>
    event: <type>
    data: <RunEvent as JSON>

`seq` starts at 1 and increases by 1 per run, so a client resumes with
`Last-Event-ID: <seq>` and gets every later event. Golden-run recordings (replay
mode, F7) are a JSON array of the same `RunEvent` objects.

Secrets never appear: a `fill_secret` or `totp` step carries `value: null`.
"""

from typing import Annotated, Any, Literal

from pydantic import AwareDatetime, Field, TypeAdapter

from backroom_api.contracts.common import Contract, Mode, Portal, SkillTask
from backroom_api.skills.schema import Locator, StepAction, StepChange

RunStatus = Literal["queued", "running", "succeeded", "failed", "needs_human", "cancelled"]
HealRung = Literal["fallback", "healer", "escalation", "human"]


class RunTotals(Contract):
    elapsed_ms: int
    steps: int
    llm_calls: int
    tokens_in: int
    tokens_out: int
    cache_read_tokens: int
    usd: float


class _Event(Contract):
    seq: Annotated[int, Field(ge=1)]
    run_id: str
    ts: AwareDatetime


class RunStarted(_Event):
    type: Literal["run.started"] = "run.started"
    action_id: str
    task: SkillTask
    portal: Portal
    mode: Mode
    skill_version: int | None  # None on a cold explore
    chaos_seed: int
    recorded: bool = False  # True when played back from a golden run (Replay badge)


class StepStarted(_Event):
    type: Literal["step.started"] = "step.started"
    index: int
    intent: str
    action: StepAction
    target: Locator | None = None
    value: str | None = None  # already redacted
    mode: Mode


class StepFinished(_Event):
    type: Literal["step.finished"] = "step.finished"
    index: int
    ok: bool
    duration_ms: int
    llm_calls: int
    tokens_in: int
    tokens_out: int
    usd: float
    error: str | None = None


class ModeChanged(_Event):
    type: Literal["mode.changed"] = "mode.changed"
    from_mode: Mode
    to_mode: Mode
    reason: str


class HealStarted(_Event):
    type: Literal["heal.started"] = "heal.started"
    step_index: int
    failure: str  # "locator not found: button 'Add to cart'"


class HealAttempt(_Event):
    type: Literal["heal.attempt"] = "heal.attempt"
    step_index: int
    rung: HealRung
    model: str | None = None  # canonical model ID for the healer/escalation rungs
    ok: bool


class HealSucceeded(_Event):
    """`new_version` is provisional: the replay continues on it, but it is stored only
    when the run finishes `succeeded` with every postcondition passing. Every heal in
    one run names the same `new_version`."""

    type: Literal["heal.succeeded"] = "heal.succeeded"
    step_index: int
    new_version: int
    changes: list[StepChange]


class HealFailed(_Event):
    type: Literal["heal.failed"] = "heal.failed"
    step_index: int
    reason: str


class CostTick(_Event):
    type: Literal["cost.tick"] = "cost.tick"
    totals: RunTotals
    skill_version: int | None


class AskHuman(_Event):
    type: Literal["ask_human"] = "ask_human"
    reason: str
    step_index: int | None = None


class RunFinished(_Event):
    type: Literal["run.finished"] = "run.finished"
    status: Literal["succeeded", "failed", "needs_human", "cancelled"]
    summary: str  # "Order GW-10482 placed, 24 x 1L oat milk, €38.16, arrives Thu"
    result: dict[str, Any] = Field(default_factory=dict[str, Any])
    undo_available: bool = False
    skill_version: int | None
    totals: RunTotals


RunEvent = Annotated[
    RunStarted
    | StepStarted
    | StepFinished
    | ModeChanged
    | HealStarted
    | HealAttempt
    | HealSucceeded
    | HealFailed
    | CostTick
    | AskHuman
    | RunFinished,
    Field(discriminator="type"),
]
run_event_adapter: TypeAdapter[RunEvent] = TypeAdapter(RunEvent)
run_events_adapter: TypeAdapter[list[RunEvent]] = TypeAdapter(list[RunEvent])


def to_sse(event: RunEvent) -> str:
    """Serialise one event as an SSE message."""
    return f"id: {event.seq}\nevent: {event.type}\ndata: {event.model_dump_json()}\n\n"


# --- WS /runs/{id}/screen -----------------------------------------------------
# Binary messages are JPEG frames. Each frame is preceded by a `FrameMeta` text
# message; `Cursor` text messages move the agent-cursor halo between frames.


class FrameMeta(Contract):
    type: Literal["frame"] = "frame"
    seq: int
    width: int
    height: int
    ts: AwareDatetime


class GoldenFrame(Contract):
    """Index entry of a recorded golden run (F7). A golden run is a directory:
    `events.json` (list[RunEvent]), `frames.json` (list[GoldenFrame]) and
    `frames/<file>`; the player shows each frame once `after_seq` has been played."""

    file: str  # "000123.jpg"
    after_seq: int  # the RunEvent seq this frame follows
    offset_ms: int  # time since run.started
    width: int
    height: int
    cursor_x: float | None = None
    cursor_y: float | None = None


class Cursor(Contract):
    type: Literal["cursor"] = "cursor"
    x: float  # CSS px in frame coordinates
    y: float
    step_index: int | None = None
