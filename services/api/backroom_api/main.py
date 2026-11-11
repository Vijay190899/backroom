from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

from backroom_api import db
from backroom_api.config import Settings, get_settings
from backroom_api.routes import health


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        pool = db.make_pool(settings)
        # Open without waiting: the API must start (and report "degraded") even when
        # Postgres is down.
        await run_in_threadpool(pool.open, False)
        app.state.pool = pool
        try:
            yield
        finally:
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
    app.include_router(health.router)
    return app


app = create_app()
