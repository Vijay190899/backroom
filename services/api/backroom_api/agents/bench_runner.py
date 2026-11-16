"""The real `TaskRunner` for the bench harness (B1, B2; H7).

    uv run backroom-bench b1 --runner backroom_api.agents.bench_runner:factory

It drives the in-process `SkillRunner` against the live portals. `change_price` alternates
between two prices so that every run really changes something: a postcondition that is
already true before the run would prove nothing.

The bench forgets and relearns skills constantly; the demo's skills are snapshotted when
the runner starts and put back by `close()`, and the portals are reset, so a bench run
leaves the demo exactly as it found it.
"""

import shutil
import tempfile
from pathlib import Path
from typing import Any

from backroom_api.agents.portals_admin import PortalAdmin
from backroom_api.agents.runner import SkillRunner
from backroom_api.agents.tasks import TASKS
from backroom_api.browser import BrowserPool
from backroom_api.config import Settings
from backroom_api.llm.client import LLM
from backroom_api.skills.store import DEFAULT_ROOT, SkillStore

_PRICES = (3.45, 3.60)


class BenchRunner:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.store = SkillStore()
        self.admin = PortalAdmin(self.settings)
        self.runner = SkillRunner(
            self.settings, LLM(self.settings), BrowserPool(max_contexts=1), self.store, self.admin
        )
        self._runs = 0
        self._tmp = Path(tempfile.mkdtemp(prefix="backroom-bench-"))
        self._baselines = self._tmp / "baselines"
        if DEFAULT_ROOT.exists():
            shutil.copytree(DEFAULT_ROOT, self._tmp / "demo-skills")

    async def save_baseline(self, task: str) -> None:
        target = self._baselines / task
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(self.store.root / task, target)

    async def restore_baseline(self, task: str) -> None:
        live = self.store.root / task
        if live.exists():
            shutil.rmtree(live)
        shutil.copytree(self._baselines / task, live)

    async def close(self) -> None:
        """Put the demo's skills back, reset the portals, close the browser."""
        try:
            await self.runner.pool.close()
            saved = self._tmp / "demo-skills"
            if saved.exists():
                shutil.rmtree(DEFAULT_ROOT, ignore_errors=True)
                shutil.copytree(saved, DEFAULT_ROOT)
            await self.admin.reset()
            await self.admin.close()
        finally:
            shutil.rmtree(self._tmp, ignore_errors=True)

    async def set_chaos(self, portal: str, seed: int) -> None:
        await self.admin.set_chaos(portal, seed)

    async def reset_skill(self, task: str) -> None:
        self.store.delete(task)

    def params_for(self, task: str) -> dict[str, Any]:
        params = dict(TASKS[task].default_params)
        if task == "tilldesk.change_price":
            params["price_eur"] = _PRICES[self._runs % 2]
        return params

    async def run(self, task: str) -> Any:
        from backroom_bench.browser import RunOutcome  # the harness owns the result type

        result = await self.runner.run(task, self.params_for(task), action_id="act_bench")
        self._runs += 1
        t = result.totals
        return RunOutcome(
            ok=result.ok,
            wall_ms=t.elapsed_ms,
            llm_calls=t.llm_calls,
            tokens_in=t.tokens_in,
            tokens_out=t.tokens_out,
            usd=t.usd,
            healed=result.healed,
            escalated=result.status == "needs_human",
            failure=None if result.ok else (result.failure or result.status),
        )


def factory() -> BenchRunner:
    return BenchRunner()


def pack_for(question: str) -> str:
    """B3's memory arm: the production context packer over the real memory, unchanged.
    Seeds are the entities the question names; facts are as of now."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    import psycopg

    from backroom_api.memory.packer import pack, seeds_for

    settings = Settings()
    with psycopg.connect(settings.database_url) as conn:
        return pack(conn, seeds_for(conn, question), datetime.now(ZoneInfo("Europe/Berlin"))).text
