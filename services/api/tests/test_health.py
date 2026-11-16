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


def test_every_server_command_names_an_app_that_exists() -> None:
    """`pnpm dev:*` and the deploy images start uvicorn on `module:attr`. H4 dropped the
    API's module-level `app`, and nothing failed until the server itself was started."""
    import importlib
    import json
    import re
    from pathlib import Path

    from fastapi import FastAPI

    root = Path(__file__).resolve().parents[3]
    scripts = json.loads((root / "package.json").read_text(encoding="utf-8"))["scripts"]
    commands = [scripts["dev:api"], scripts["dev:portals"]] + [
        (root / "infra" / f).read_text(encoding="utf-8")
        for f in ("Dockerfile.api", "Dockerfile.portals")
    ]
    targets = {m for c in commands for m in re.findall(r"(backroom_\w+\.main):(\w+)", c)}
    assert targets == {("backroom_api.main", "app"), ("backroom_portals.main", "app")}
    for module, attr in targets:
        assert isinstance(getattr(importlib.import_module(module), attr, None), FastAPI)
