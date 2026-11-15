"""H4 route tests: brief, approve/reject, run events (SSE + resume), screen, human, undo,
skills and memory, against real Postgres in a schema of their own.

The browser runner is replaced by a scripted fake (the agent itself is covered by
test_agents.py), and no model key is set, so the brief uses its template fallback.
Skips without Postgres.
"""

import asyncio
import json
import uuid
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from urllib.parse import quote
from zoneinfo import ZoneInfo

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg import sql

from backroom_api.agents.recorder import RunRecorder
from backroom_api.agents.tasks import TASKS
from backroom_api.browser.screencast import Frame
from backroom_api.config import Settings
from backroom_api.contracts.events import (
    AskHuman,
    RunFinished,
    RunStarted,
    StepFinished,
    StepStarted,
)
from backroom_api.main import create_app
from backroom_api.memory import writers
from backroom_api.skills.schema import Locator, Skill, Step
from backroom_api.skills.store import SkillStore

BONN = ZoneInfo("Europe/Berlin")


@pytest.fixture(scope="module")
def data_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from backroom_data import cli

    out = tmp_path_factory.mktemp("out")
    cli.build(datetime.now(BONN).date(), 44, out, tmp_path_factory.mktemp("raw"), offline=True)
    return out


@pytest.fixture(scope="module")
def database_url() -> Iterator[str]:
    base = Settings().database_url
    try:
        admin = psycopg.connect(base, connect_timeout=5, autocommit=True)
    except psycopg.OperationalError:
        pytest.skip("no Postgres reachable (set DATABASE_URL, e.g. Neon)")
    schema = f"test_api_{uuid.uuid4().hex[:10]}"
    admin.execute(sql.SQL("create schema {}").format(sql.Identifier(schema)))
    sep = "&" if "?" in base else "?"
    yield f"{base}{sep}options={quote(f'-c search_path={schema},public')}"
    admin.execute(sql.SQL("drop schema {} cascade").format(sql.Identifier(schema)))
    admin.close()


class FakeAdmin:
    async def state(self, portal: str) -> dict[str, Any]:
        return {"items": {"franzbroetchen": {"published_price_eur": 3.20}}, "orders": []}

    async def chaos(self) -> list[dict[str, Any]]:
        return [{"portal": "grainline", "seed": 0, "variants": {"language": "en"}}]

    async def set_chaos(self, portal: str, seed: int) -> dict[str, Any]:
        return {"portal": portal, "seed": seed, "variants": {"language": "de"}}

    async def close(self) -> None:
        pass


class FakeRunner:
    """Emits a short, realistic event stream. With `ask=True` it pauses on ask_human."""

    def __init__(self) -> None:
        self.admin = FakeAdmin()
        self.ask = False
        self.params: list[dict[str, Any]] = []

    async def run(self, task: str, params: dict[str, Any], **kw: Any) -> Any:
        self.params.append(dict(params))
        rec = RunRecorder(kw["run_id"], None, kw["sink"])
        spec = TASKS[task]
        await rec.emit(
            RunStarted,
            action_id=kw["action_id"],
            task=spec.task,
            portal=spec.portal,
            mode="replay",
            skill_version=1,
            chaos_seed=0,
        )
        await rec.emit(
            StepStarted,
            index=0,
            intent="Open",
            action="goto",
            target=None,
            value="/",
            mode="replay",
        )
        await kw["on_frame"](Frame(seq=1, jpeg=b"\xff\xd8fake-jpeg", width=1280, height=800))
        await kw["on_cursor"](10.0, 20.0)
        status = "succeeded"
        if self.ask:
            await rec.emit(AskHuman, reason="stuck at step 1", step_index=0)
            answer = await kw["ask_human"]("stuck", 0)
            status = "succeeded" if answer == "resume" else "cancelled"
        rec.step_done()
        await rec.emit(
            StepFinished,
            index=0,
            ok=True,
            duration_ms=5,
            llm_calls=0,
            tokens_in=0,
            tokens_out=0,
            usd=0.0,
        )
        await rec.emit(
            RunFinished,
            status=status,
            summary=f"{task} done",
            result={},
            undo_available=status == "succeeded" and kw["undoable"],
            skill_version=1,
            totals=rec.totals(),
        )
        return SimpleNamespace(ok=status == "succeeded")


@pytest.fixture(scope="module")
def client(
    database_url: str, data_dir: Path, tmp_path_factory: pytest.TempPathFactory
) -> Iterator[TestClient]:
    settings = Settings(
        database_url=database_url,
        data_dir=data_dir,
        openrouter_api_key="",
        anthropic_api_key="",
    )
    app = create_app(settings)
    with TestClient(app) as c:  # runs the lifespan: migrations into the test schema
        with psycopg.connect(database_url) as conn:
            writers.write_world(conn, data_dir)
            conn.commit()
        fake = FakeRunner()
        app.state.runs.runner = fake
        app.state.admin = fake.admin
        app.state.skills = SkillStore(tmp_path_factory.mktemp("skills"))
        app.state.fake = fake
        yield c


def card(c: TestClient, kind: str) -> dict[str, Any]:
    return next(x for x in c.get("/brief/today").json()["cards"] if x["kind"] == kind)


def wait_finished(c: TestClient, run_id: str) -> dict[str, Any]:
    for _ in range(100):
        summary = c.get(f"/runs/{run_id}").json()
        if summary["finished_at"]:
            return summary
        asyncio.run(asyncio.sleep(0.05))
    raise AssertionError("run did not finish")


def sse(text: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for block in text.split("\n\n"):
        fields = dict(
            line.split(": ", 1) for line in block.splitlines() if ": " in line and line[0] != ":"
        )
        if "data" in fields:
            out.append(
                {"id": fields.get("id"), "event": fields.get("event"), **json.loads(fields["data"])}
            )
    return out


def test_brief_is_generated_once_then_served_from_postgres(client: TestClient) -> None:
    first = client.get("/brief/today")
    assert first.status_code == 200
    body = first.json()
    assert 1 <= len(body["cards"]) <= 3
    assert all(c["copy_source"] == "template" for c in body["cards"])  # no model key
    again = client.get("/brief/today").json()
    assert again["cached"] is True and again["id"] == body["id"]


def test_regenerate_streams_skeleton_cards_then_the_brief(client: TestClient) -> None:
    text = client.get("/brief/today?regenerate=1").text
    kinds = [b.split("\n")[0] for b in text.strip().split("\n\n")]
    assert kinds[0] == "event: brief.skeleton" and kinds[-1] == "event: brief.done"
    assert kinds.count("event: brief.card") >= 1


def test_approve_runs_once_per_idempotency_key_and_streams_its_events(client: TestClient) -> None:
    reorder = card(client, "stockout")
    first = client.post(f"/actions/{reorder['id']}/approve", headers={"Idempotency-Key": "k-1"})
    assert first.status_code == 200 and first.json()["deduplicated"] is False
    run_id = first.json()["run_id"]
    repeat = client.post(f"/actions/{reorder['id']}/approve", headers={"Idempotency-Key": "k-1"})
    assert repeat.json() == {"run_id": run_id, "action_id": reorder["id"], "deduplicated": True}

    summary = wait_finished(client, run_id)
    assert summary["status"] == "succeeded" and summary["summary"] == "grainline.reorder_item done"
    events = sse(client.get(f"/runs/{run_id}/events").text)
    assert [e["seq"] for e in events] == list(range(1, len(events) + 1))
    assert events[0]["event"] == "run.started" and events[-1]["event"] == "run.finished"
    assert [e["id"] for e in events] == [str(e["seq"]) for e in events]
    resumed = sse(client.get(f"/runs/{run_id}/events", headers={"Last-Event-ID": "2"}).text)
    assert [e["seq"] for e in resumed] == list(range(3, len(events) + 1))
    assert card(client, "stockout")["status"] == "done"
    assert client.app.state.fake.params[-1]["sku"] == reorder["params"]["sku"]  # type: ignore[attr-defined]


def test_a_recommendation_cannot_be_approved(client: TestClient) -> None:
    advice = card(client, "weather_demand")
    response = client.post(f"/actions/{advice['id']}/approve")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "not_executable"


def test_the_screen_socket_sends_the_frame_header_then_the_jpeg(client: TestClient) -> None:
    reorder = card(client, "stockout")
    run_id = client.post(
        f"/actions/{reorder['id']}/approve", headers={"Idempotency-Key": "k-screen"}
    ).json()["run_id"]
    wait_finished(client, run_id)
    with client.websocket_connect(f"/runs/{run_id}/screen") as ws:
        header = json.loads(ws.receive_text())
        jpeg = ws.receive_bytes()
    assert header["type"] == "frame" and (header["width"], header["height"]) == (1280, 800)
    assert jpeg.startswith(b"\xff\xd8")


def test_ask_human_pauses_the_run_until_the_owner_answers(client: TestClient) -> None:
    fake = cast(FakeRunner, client.app.state.fake)  # type: ignore[attr-defined]
    fake.ask = True
    try:
        reorder = card(client, "stockout")
        run_id = client.post(
            f"/actions/{reorder['id']}/approve", headers={"Idempotency-Key": "k-human"}
        ).json()["run_id"]
        for _ in range(100):
            if client.get(f"/runs/{run_id}").json()["status"] == "needs_human":
                break
            asyncio.run(asyncio.sleep(0.05))
        reply = client.post(f"/runs/{run_id}/human", json={"action": "resume"})
        assert reply.status_code == 200
        assert wait_finished(client, run_id)["status"] == "succeeded"
        late = client.post(f"/runs/{run_id}/human", json={"action": "cancel"})
        assert late.status_code == 409 and late.json()["error"]["code"] == "not_waiting"
    finally:
        fake.ask = False


def test_a_price_change_can_be_undone_once(client: TestClient) -> None:
    price = card(client, "margin_erosion")
    run_id = client.post(
        f"/actions/{price['id']}/approve", headers={"Idempotency-Key": "k-price"}
    ).json()["run_id"]
    wait_finished(client, run_id)
    undo = client.post(f"/runs/{run_id}/undo")
    assert undo.status_code == 200 and undo.json()["undo_of"] == run_id
    assert client.post(f"/runs/{run_id}/undo").json() == undo.json()  # one undo run only
    wait_finished(client, undo.json()["run_id"])
    fake = cast(FakeRunner, client.app.state.fake)  # type: ignore[attr-defined]
    assert fake.params[-1] == {"item_id": "franzbroetchen", "price_eur": 3.20}  # the old price
    order = card(client, "stockout")
    order_run = client.post(
        f"/actions/{order['id']}/approve", headers={"Idempotency-Key": "k-no-undo"}
    ).json()["run_id"]
    wait_finished(client, order_run)
    no_undo = client.post(f"/runs/{order_run}/undo")
    assert no_undo.status_code == 409 and no_undo.json()["error"]["code"] == "no_undo"


def test_reject_records_the_reason_and_the_brief_regenerates(client: TestClient) -> None:
    price = card(client, "margin_erosion")
    before = client.get("/brief/today").json()["id"]
    response = client.post(f"/actions/{price['id']}/reject", json={"reason": "not this week"})
    assert response.status_code == 200
    body = response.json()
    assert body["action_id"] == price["id"] and body["episode_id"].startswith("ep_")
    assert body["preference_fact_ids"] == []  # no model key: the episode only
    after = client.get("/brief/today").json()
    assert after["id"] != before and after["cached"] is False
    again = next(c for c in after["cards"] if c["id"] == price["id"])
    assert again["status"] == "rejected"  # the same proposal keeps its decision


def test_skills_and_memory_routes(client: TestClient) -> None:
    store: SkillStore = client.app.state.skills  # type: ignore[attr-defined]
    store.save(
        Skill(
            id="grainline.reorder_item",
            task="grainline.reorder_item",
            portal="grainline",
            version=1,
            params_schema={"type": "object", "properties": {}},
            steps=[Step(intent="Go", action="click", target=Locator(role="link", name="Cart"))],
            postconditions=[],
            created_at=datetime.now(UTC),
        )
    )
    listed = client.get("/skills").json()
    assert [(s["id"], s["latest_version"], s["success_rate"]) for s in listed] == [
        ("grainline.reorder_item", 1, None)
    ]
    versions = client.get("/skills/grainline.reorder_item/versions").json()
    assert [v["version"] for v in versions["versions"]] == [1] and versions["diffs"] == []
    assert client.get("/skills/tilldesk.change_price/versions").status_code == 404

    graph = client.get("/memory/graph").json()
    assert graph["nodes"] and graph["facts"]
    assert any(f["valid_to"] for f in graph["facts"])  # superseded facts are included
    fact = graph["facts"][0]["id"]
    assert client.get(f"/memory/facts/{fact}").json()["fact"]["id"] == fact
    assert client.get("/memory/facts/f_nope").json()["error"]["code"] == "not_found"


def test_chaos_and_error_shapes(client: TestClient) -> None:
    state = client.post("/chaos", json={"portal": "grainline", "seed": 7}).json()
    assert state == {"portal": "grainline", "seed": 7, "variants": {"language": "de"}}
    invalid = client.post("/chaos", json={"portal": "grainline", "seed": 5000})
    assert invalid.status_code == 422 and invalid.json()["error"]["code"] == "invalid_request"
    missing = client.get("/runs/run_nope")
    assert missing.status_code == 404 and missing.json()["error"]["code"] == "not_found"
