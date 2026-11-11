from fastapi.testclient import TestClient

from backroom_api.config import Settings
from backroom_api.main import create_app


def test_health_reports_degraded_when_dependencies_are_down() -> None:
    settings = Settings(
        _env_file=None,  # type: ignore[call-arg]
        database_url="postgresql://nobody:nothing@127.0.0.1:1/none",
        portals_base_url="http://127.0.0.1:1",
    )
    with TestClient(create_app(settings)) as client:
        resp = client.get("/health")
    assert resp.status_code == 503
    body = resp.json()
    assert body["status"] == "degraded"
    assert body["checks"]["postgres"] == "down"
    assert body["checks"]["portals"] == "down"
    assert body["checks"]["llm"] == {"provider": "openrouter", "configured": False}
