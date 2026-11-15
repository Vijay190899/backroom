"""The real `TaskRunner` for the bench harness (B1, B2; H7).

    uv run backroom-bench b1 --runner backroom_api.agents.bench_runner:factory

It drives the in-process `SkillRunner` against the live portals. `change_price` alternates
between two prices so that every run really changes something: a postcondition that is
already true before the run would prove nothing.
"""

from typing import Any

from backroom_api.agents.portals_admin import PortalAdmin
from backroom_api.agents.runner import SkillRunner
from backroom_api.agents.tasks import TASKS
from backroom_api.browser import BrowserPool
from backroom_api.config import Settings
from backroom_api.llm.client import LLM
from backroom_api.skills.store import SkillStore

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
        )


def factory() -> BenchRunner:
    return BenchRunner()
