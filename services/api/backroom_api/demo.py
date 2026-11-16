"""Put the demo back to its starting point (DEMO_SCRIPT "Setup before the call").

    uv run python -m backroom_api.demo reset [--relearn]      (pnpm demo:reset)

- Postgres: runs, briefs and actions are deleted; memory goes back to the seeded world, so
  no preference has been learned yet (the 8% cap is learned live, PRD F4).
- Portals: orders, carts and price edits are wiped and every chaos seed is back to 0.
- `--relearn`: every skill is forgotten and learned again by a cold explore at seed 0
  (reorder, then cancelling that order, then a price change; about $0.008 with the
  default models; needs the portals running and a model key).
  The portals are reset again afterwards, so the learning runs leave no trace.
"""

import argparse
import asyncio
import sys
from typing import Any

import psycopg

from backroom_api.agents.portals_admin import PortalAdmin
from backroom_api.agents.runner import SkillRunner
from backroom_api.agents.tasks import TASKS
from backroom_api.browser import BrowserPool
from backroom_api.config import Settings
from backroom_api.llm.client import LLM
from backroom_api.llm.registry import is_configured
from backroom_api.memory.writers import write_world
from backroom_api.seed_db import migrate
from backroom_api.skills.store import SkillStore

TABLES = "run_event, run, action, brief, fact, episode, entity"


def reset_database(settings: Settings) -> dict[str, int]:
    with psycopg.connect(settings.database_url) as conn:
        migrate(conn)
        conn.execute(f"truncate {TABLES} restart identity cascade")  # type: ignore[arg-type]
        created = write_world(conn, settings.data_dir)
        conn.commit()
    return created


async def relearn(settings: Settings, admin: PortalAdmin) -> list[str]:
    store = SkillStore()
    pool = BrowserPool(max_contexts=1)
    runner = SkillRunner(settings, LLM(settings), pool, store, admin)
    lines: list[str] = []
    last_order: str | None = None
    try:
        for task, spec in TASKS.items():
            store.delete(task)
            await admin.set_chaos(spec.portal, 0)
            # Cancelling needs an order: the one the reorder just placed.
            params = {"order_id": last_order} if task == "grainline.cancel_order" else None
            result = await runner.run(task, params, action_id="act_demo_setup")
            if not result.ok:  # a cold explore can stumble; one more try before failing
                result = await runner.run(task, params, action_id="act_demo_setup")
            if task == "grainline.reorder_item":
                last_order = result.result.get("order")
            t = result.totals
            lines.append(
                f"{task}: {result.status}, skill v{result.skill_version}, "
                f"{t.llm_calls} calls, ${t.usd:.4f}, {t.elapsed_ms / 1000:.1f} s"
            )
            if not result.ok:
                raise RuntimeError(f"{task} could not be learned: {result.summary}")
    finally:
        await pool.close()
    return lines


async def reset(relearn_skills: bool) -> int:
    settings = Settings()
    created = await asyncio.to_thread(reset_database, settings)
    print(f"database: runs and briefs cleared; memory re-seeded {created}")
    admin = PortalAdmin(settings)
    try:
        if relearn_skills:
            if not is_configured(settings):
                print("--relearn needs a model key (OPENROUTER_API_KEY)", file=sys.stderr)
                return 2
            await admin.reset()
            for line in await relearn(settings, admin):
                print(f"skill   {line}")
        await admin.reset()
        print("portals: orders, carts and edits wiped; chaos seeds back to 0")
    finally:
        await admin.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="backroom_api.demo")
    sub = parser.add_subparsers(dest="cmd", required=True)
    cmd = sub.add_parser("reset", help="back to the demo's starting point")
    cmd.add_argument("--relearn", action="store_true", help="learn both skills again at seed 0")
    args: Any = parser.parse_args(argv)
    return asyncio.run(reset(args.relearn))


if __name__ == "__main__":
    sys.exit(main())
