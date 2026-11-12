from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from backroom_portals import admin
from backroom_portals.config import Settings, get_settings
from backroom_portals.grainline import routes as grainline
from backroom_portals.grainline.store import GrainlineStore
from backroom_portals.rendering import ChaosSeeds
from backroom_portals.tilldesk import routes as tilldesk
from backroom_portals.tilldesk.store import TillDeskStore


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(title="Backroom mock portals", version="0.1.0", docs_url=None, redoc_url=None)
    app.state.settings = settings
    app.state.chaos = ChaosSeeds()
    app.state.grainline = GrainlineStore(
        today_fn=lambda: settings.today, data_seed=settings.data_seed
    )
    app.state.tilldesk = TillDeskStore()
    app.include_router(grainline.router)
    app.include_router(tilldesk.router)
    app.include_router(admin.router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/", include_in_schema=False)
    async def index() -> RedirectResponse:
        return RedirectResponse("/grainline/login")

    return app


app = create_app()
