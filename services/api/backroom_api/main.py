import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from psycopg_pool import ConnectionPool

from backroom_api import db
from backroom_api.agents.portals_admin import PortalAdmin
from backroom_api.agents.runner import SkillRunner
from backroom_api.browser import BrowserPool
from backroom_api.config import Settings, get_settings
from backroom_api.live import repo
from backroom_api.live.briefs import BriefService
from backroom_api.live.runs import RunManager
from backroom_api.llm.client import LLM
from backroom_api.llm.registry import is_configured
from backroom_api.routes import brief, catalog, errors, health, runs
from backroom_api.seed_db import migrate
from backroom_api.skills.store import SkillStore

log = logging.getLogger(__name__)


def _prepare_database(pool: ConnectionPool) -> None:
    """Apply pending migrations and close out runs a previous process left open. Skipped
    (and logged) when Postgres is down: the API still starts and reports "degraded"."""
    try:
        with pool.connection(timeout=3.0) as conn:
            applied = migrate(conn)
            if applied:
                log.info("migrations applied: %s", applied)
            stale = repo.fail_unfinished(conn, datetime.now(UTC))
            if stale:
                log.warning("marked %d interrupted run(s) as failed", stale)
    except Exception as exc:
        log.warning("database not prepared (%s); runs and briefs need Postgres", exc)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        pool = db.make_pool(settings)
        # Open without waiting: the API must start (and report "degraded") even when
        # Postgres is down.
        await run_in_threadpool(pool.open, False)
        await run_in_threadpool(_prepare_database, pool)
        llm = LLM(settings) if is_configured(settings) else None
        browsers = BrowserPool(max_contexts=2)
        admin = PortalAdmin(settings)
        skills = SkillStore()
        runner = SkillRunner(settings, llm, browsers, skills, admin)
        app.state.pool = pool
        app.state.ledger = llm.ledger if llm else None  # today's model spend (replay when spent)
        app.state.admin = admin
        app.state.skills = skills
        app.state.runs = RunManager(runner, pool)
        app.state.briefs = BriefService(pool, llm, settings.data_dir)
        try:
            yield
        finally:
            await app.state.runs.shutdown()
            await browsers.close()
            await admin.close()
            await run_in_threadpool(pool.close)

    app = FastAPI(title="Backroom API", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.web_origin],
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Last-Event-ID"],
    )
    errors.install(app)
    app.include_router(health.router)
    app.include_router(brief.router)
    app.include_router(runs.router)
    app.include_router(catalog.router)
    return app


# The ASGI target of `pnpm dev:api` and infra/Dockerfile.api (`backroom_api.main:app`).
# Cheap at import: the pool, browsers and model client are built in `lifespan`.
app = create_app()
