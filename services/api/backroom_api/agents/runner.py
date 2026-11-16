"""The skill runner: one task, start to finish.

    no skill yet  ->  EXPLORE (model operates the portal)  ->  compile  ->  store v1
    skill exists  ->  REPLAY (code only)  ->  heal ladder if the site changed  ->  store v+1

Either way a run is a success only if every postcondition passes against the portal's own
state. A skill is stored only after such a run, so a wrong guess can never become a skill.
"""

import asyncio
import logging
import uuid
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from typing import Any

from backroom_api.agents.explore import ExploreResult, explore, finish_step
from backroom_api.agents.portals_admin import PortalAdmin
from backroom_api.agents.postconditions import PostResult, check
from backroom_api.agents.recorder import EventSink, RunRecorder
from backroom_api.agents.tasks import TASKS, TaskSpec
from backroom_api.browser import Allowlist, BrowserPool, Executor, SecretVault
from backroom_api.browser.executor import CursorCallback
from backroom_api.browser.screencast import FrameCallback, Screencast
from backroom_api.config import Settings
from backroom_api.contracts.common import Mode
from backroom_api.contracts.events import RunEvent, RunFinished, RunStarted, RunTotals, StepStarted
from backroom_api.llm.client import LLM
from backroom_api.replay.engine import AskHumanHook, ReplayResult, heal_summary, replay
from backroom_api.skills.compiler import compile_skill
from backroom_api.skills.schema import Skill, SkillDiff, SkillStats, Step
from backroom_api.skills.store import SkillStore

log = logging.getLogger(__name__)


@dataclass
class RunResult:
    run_id: str
    ok: bool
    status: str  # succeeded | failed | needs_human
    summary: str
    mode: Mode  # how the run started: explore or replay
    healed: bool
    escalated: bool
    skill_version: int | None  # the version stored by (or used for) this run
    totals: RunTotals
    postconditions: list[PostResult] = field(default_factory=list[PostResult])
    failure: str | None = None
    events: list[RunEvent] = field(default_factory=list[RunEvent])
    result: dict[str, Any] = field(default_factory=dict[str, Any])  # as in run.finished


@dataclass(frozen=True)
class _Hooks:
    on_cursor: CursorCallback | None = None
    ask_human: AskHumanHook | None = None
    undoable: bool = False


class SkillRunner:
    def __init__(
        self,
        settings: Settings,
        llm: LLM | None,
        pool: BrowserPool,
        store: SkillStore,
        admin: PortalAdmin,
        vault: SecretVault | None = None,
    ) -> None:
        self.settings = settings
        self.llm = llm
        self.pool = pool
        self.store = store
        self.admin = admin
        self.vault = vault or SecretVault.from_settings(settings)
        self._locks: dict[str, asyncio.Lock] = {}

    async def run(
        self,
        task: str,
        params: Mapping[str, Any] | None = None,
        *,
        run_id: str | None = None,
        action_id: str = "act_manual",
        sink: EventSink | None = None,
        on_frame: FrameCallback | None = None,
        force_explore: bool = False,
        on_cursor: CursorCallback | None = None,
        ask_human: AskHumanHook | None = None,
        undoable: bool = False,
    ) -> RunResult:
        """Run one task. Never raises for a run that went wrong: every run ends with a
        `run.finished` event, so a live client is never left waiting."""
        spec = TASKS[task]
        merged = {**spec.default_params, **(params or {})}
        rec = RunRecorder(run_id or f"run_{uuid.uuid4().hex[:8]}", self.llm, sink)
        # One run per task at a time: two runs healing the same skill would both try to
        # store the same new version.
        async with self._locks.setdefault(task, asyncio.Lock()):
            try:
                return await self._run(
                    spec,
                    merged,
                    rec,
                    action_id,
                    on_frame,
                    force_explore,
                    _Hooks(on_cursor=on_cursor, ask_human=ask_human, undoable=undoable),
                )
            except Exception as exc:  # the run must still finish visibly
                log.exception("run %s crashed", rec.run_id)
                reason = self.vault.redact(f"{type(exc).__name__}: {exc}")[:300]
                await rec.emit(
                    RunFinished,
                    status="failed",
                    summary=f"Did not finish: internal error ({reason})",
                    result={},
                    undo_available=False,
                    skill_version=rec.skill_version,
                    totals=rec.totals(),
                )
                return RunResult(
                    run_id=rec.run_id,
                    ok=False,
                    status="failed",
                    summary="internal error",
                    mode="explore",
                    healed=False,
                    escalated=False,
                    skill_version=rec.skill_version,
                    totals=rec.totals(),
                    failure=reason,
                    events=rec.events,
                )

    async def _run(
        self,
        spec: TaskSpec,
        merged: dict[str, Any],
        rec: RunRecorder,
        action_id: str,
        on_frame: FrameCallback | None,
        force_explore: bool,
        hooks: "_Hooks",
    ) -> RunResult:
        task = spec.task
        run_id = rec.run_id
        baseline = await self._orders_before(spec)
        skill = None if force_explore else self.store.latest(task)
        mode: Mode = "replay" if skill else "explore"
        rec.skill_version = skill.version if skill else None
        await rec.emit(
            RunStarted,
            action_id=action_id,
            task=spec.task,
            portal=spec.portal,
            mode=mode,
            skill_version=rec.skill_version,
            chaos_seed=await self.admin.seed_of(spec.portal),
        )

        allow = Allowlist.for_portal(self.settings.portals_base_url, spec.portal)
        replayed: ReplayResult | None = None
        explored: ExploreResult | None = None
        posts: list[PostResult] = []
        failure: str | None = None
        async with self.pool.session(allow) as page:
            executor = Executor(page, self.vault, allow, on_cursor=hooks.on_cursor)
            cast = Screencast(page, on_frame) if on_frame else None
            if cast:
                await cast.start()
            try:
                if skill is not None:
                    replayed = await replay(
                        page=page,
                        executor=executor,
                        rec=rec,
                        vault=self.vault,
                        skill=skill,
                        params=merged,
                        portal=spec.portal,
                        can_heal=self.llm is not None,
                        max_usd=self.settings.run_max_usd,
                        ask_human=hooks.ask_human,
                    )
                    failure = replayed.failure
                    proceed = replayed.ok
                else:
                    explored = await self._explore(spec, merged, page, executor, rec)
                    failure = explored.reason
                    proceed = explored.ok
                if proceed:
                    posts = [
                        await check(
                            p,
                            merged,
                            page=page,
                            admin=self.admin,
                            portal=spec.portal,
                            baseline_orders=baseline,
                        )
                        for p in spec.postconditions
                    ]
                    if not all(p.ok for p in posts):
                        failure = "; ".join(p.detail for p in posts if not p.ok)
            finally:
                if cast:
                    await cast.stop()

        verified = bool(posts) and all(p.ok for p in posts)
        used_version = rec.skill_version
        if verified:
            used_version = self._store(skill, explored, replayed, spec, merged)
            rec.skill_version = used_version
        wall_ms = rec.totals().elapsed_ms
        # A version's stats count the runs that used it: a heal belongs to the version that
        # broke (not the one it created), and a first explore used no version at all.
        if skill is not None:
            self.store.record_run(
                task, skill.version, ok=verified, wall_ms=wall_ms, usd=round(rec.usd, 6)
            )
        needs_human = bool(replayed and replayed.needs_human)
        cancelled = bool(replayed and replayed.cancelled)
        status = (
            "succeeded"
            if verified
            else "cancelled"
            if cancelled
            else "needs_human"
            if needs_human
            else "failed"
        )
        summary, result = await self._outcome(spec, merged, verified, failure, posts)
        await rec.emit(
            RunFinished,
            status=status,
            summary=summary,
            result=result,
            undo_available=verified and hooks.undoable,
            skill_version=used_version,
            totals=rec.totals(),
        )
        return RunResult(
            run_id=run_id,
            ok=verified,
            status=status,
            summary=summary,
            mode=mode,
            healed=bool(replayed and replayed.healed),
            escalated=bool(replayed and replayed.escalated),
            skill_version=used_version,
            totals=rec.totals(),
            postconditions=posts,
            failure=None if verified else failure,
            events=rec.events,
            result=result,
        )

    # --- pieces ---------------------------------------------------------------------------

    async def _orders_before(self, spec: TaskSpec) -> int | None:
        if spec.portal != "grainline":
            return None
        return len((await self.admin.state("grainline")).get("orders", []))

    async def _explore(
        self,
        spec: TaskSpec,
        params: Mapping[str, Any],
        page: Any,
        executor: Executor,
        rec: RunRecorder,
    ) -> ExploreResult:
        opening = Step(intent="Open the portal", action="goto", value_template=spec.start_path)
        await rec.emit(
            StepStarted,
            index=0,
            intent=opening.intent,
            action="goto",
            target=None,
            value=spec.start_path,
            mode="explore",
        )
        outcome = await executor.run(opening, {})
        await finish_step(rec, 0, outcome, page.url)
        if not outcome.ok:
            return ExploreResult(ok=False, reason=outcome.error)
        return await explore(
            page=page,
            executor=executor,
            rec=rec,
            vault=self.vault,
            goal=spec.goal_for(dict(params)),
            params=params,
            portal=spec.portal,
            role="worker",
            mode="explore",
            max_steps=self.settings.explore_max_steps,
            max_usd=self.settings.explore_max_usd,
            first_index=1,
        )

    def _store(
        self,
        skill: Skill | None,
        explored: ExploreResult | None,
        replayed: ReplayResult | None,
        spec: TaskSpec,
        params: Mapping[str, Any],
    ) -> int | None:
        """Persist what a verified run learned. Returns (version used, newly stored skill)."""
        if skill is None and explored is not None:
            compiled = compile_skill(
                task=spec.task,
                portal=spec.portal,
                start_path=spec.start_path,
                actions=explored.actions,
                params=params,
                params_schema=spec.params_schema,
                postconditions=spec.postconditions,
            )
            self.store.save(compiled)
            return compiled.version
        if skill is not None and replayed is not None and replayed.healed and replayed.changes:
            healed = Skill.model_validate(
                skill.model_copy(
                    update={
                        "version": skill.version + 1,
                        "parent_version": skill.version,
                        "heal_note": heal_summary(replayed.changes),
                        "steps": replayed.steps,
                        "stats": SkillStats(),
                        "created_at": datetime.now(UTC),
                    }
                ).model_dump()
            )
            self.store.save(healed)
            self.store.save_diff(
                SkillDiff(
                    skill_id=healed.id,
                    from_version=skill.version,
                    to_version=healed.version,
                    changes=replayed.changes,
                )
            )
            return healed.version
        return skill.version if skill else None

    async def _outcome(
        self,
        spec: TaskSpec,
        params: Mapping[str, Any],
        ok: bool,
        failure: str | None,
        posts: list[PostResult],
    ) -> tuple[str, dict[str, Any]]:
        """The run's one-line summary and the result fields an owner reads (the theater
        formats `*_eur` as money). Checks are counted, their details stay in the log."""
        checks = f"{sum(p.ok for p in posts)} of {len(posts)} passed" if posts else "not run"
        if not ok:
            return f"Did not finish: {failure or 'unknown reason'}", {"checks": checks}
        state = await self.admin.state(spec.portal)
        if spec.task == "grainline.cancel_order":
            order_id = str(params["order_id"])
            return f"Order {order_id} cancelled", {
                "order": order_id,
                "status": "cancelled",
                "checks": checks,
            }
        if spec.portal == "grainline":
            order = state["orders"][-1]
            summary = (
                f"Order {order['id']} placed: {params.get('qty')} x {params.get('sku')}, "
                f"€{order['total_eur']:.2f}"
            )
            # Grainline cancels until the day before delivery: the undo's deadline.
            last_day = date.fromisoformat(order["delivery_date"]) - timedelta(days=1)
            return summary, {
                "order": order["id"],
                "total_eur": order["total_eur"],
                "delivery": order["delivery_date"],
                "undo_until": last_day.isoformat(),
                "checks": checks,
            }
        price = float(params["price_eur"])
        summary = f"{params.get('item_id')} is now €{price:.2f} on the till"
        return summary, {"item": params.get("item_id"), "price_eur": price, "checks": checks}
