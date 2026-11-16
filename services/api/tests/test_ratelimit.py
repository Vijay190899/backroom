"""Rate limits per client IP (backroom_api/ratelimit.py) and the cached budget read."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
from starlette.types import Message, Receive, Scope, Send

from backroom_api.config import Settings
from backroom_api.llm.meter import CallRecord, SpendLedger
from backroom_api.main import create_app
from backroom_api.ratelimit import RateLimiter


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


async def ok_app(scope: Scope, receive: Receive, send: Send) -> None:
    if scope["type"] == "websocket":
        await send({"type": "websocket.accept"})
        return
    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": b"ok"})


async def call(
    limiter: RateLimiter, method: str = "GET", path: str = "/x", ip: str = "1.2.3.4"
) -> tuple[int | None, dict[str, str], list[Message]]:
    sent: list[Message] = []

    async def receive() -> Message:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: Message) -> None:
        sent.append(message)

    kind = "websocket" if method == "WS" else "http"
    scope: dict[str, Any] = {"type": kind, "path": path, "client": (ip, 5000), "headers": []}
    if kind == "http":
        scope["method"] = method
    await limiter(scope, receive, send)
    start = next((m for m in sent if m["type"] == "http.response.start"), None)
    headers = {k.decode(): v.decode() for k, v in (start or {}).get("headers", [])}
    return (start["status"] if start else None), headers, sent


def limiter(clock: Clock, read: int = 3, write: int = 2, **kw: Any) -> RateLimiter:
    return RateLimiter(ok_app, read_per_min=read, write_per_min=write, clock=clock, **kw)


async def test_reads_and_writes_have_their_own_windows() -> None:
    clock = Clock()
    rl = limiter(clock)
    assert [(await call(rl))[0] for _ in range(3)] == [200, 200, 200]
    status, headers, sent = await call(rl)
    assert status == 429 and int(headers["retry-after"]) >= 1
    body = json.loads(next(m for m in sent if m["type"] == "http.response.body")["body"])
    assert body["error"]["code"] == "rate_limited"
    # Writes are counted apart from reads.
    assert [(await call(rl, "POST"))[0] for _ in range(3)] == [200, 200, 429]
    # The window slides: a minute later both are open again.
    clock.now += 60
    assert (await call(rl))[0] == 200 and (await call(rl, "POST"))[0] == 200


async def test_health_preflight_and_other_clients_are_not_limited() -> None:
    rl = limiter(Clock(), read=1)
    assert (await call(rl))[0] == 200 and (await call(rl))[0] == 429
    assert (await call(rl, path="/health"))[0] == 200
    assert (await call(rl, "OPTIONS"))[0] == 200
    assert (await call(rl, ip="5.6.7.8"))[0] == 200  # another client has its own window


async def test_a_limited_websocket_is_refused_before_it_opens() -> None:
    rl = limiter(Clock(), read=1)
    _, _, first = await call(rl, "WS", "/runs/r/screen")
    _, _, second = await call(rl, "WS", "/runs/r/screen")
    assert first[0]["type"] == "websocket.accept"
    assert second == [{"type": "websocket.close", "code": 1008}]


async def test_memory_stays_bounded_with_many_clients() -> None:
    clock = Clock()
    rl = limiter(clock, max_clients=50)
    for i in range(500):
        await call(rl, ip=f"10.0.{i // 256}.{i % 256}")
        clock.now += 0.01
    assert rl.tracked_clients <= 50


def test_a_429_from_the_app_carries_cors_headers() -> None:
    settings = Settings(
        _env_file=None,  # type: ignore[call-arg]
        web_origin="https://web.example",
        rate_limit_read_per_min=2,
    )
    client = TestClient(create_app(settings))  # no lifespan: /mode needs no database
    origin = {"Origin": "https://web.example"}
    codes = [client.get("/mode", headers=origin).status_code for _ in range(3)]
    last = client.get("/mode", headers=origin)
    assert codes[:2] == [200, 200] and last.status_code == 429
    assert last.headers["access-control-allow-origin"] == "https://web.example"
    assert last.json()["error"]["code"] == "rate_limited"


def test_the_budget_read_is_cached_for_the_mode_check(tmp_path: Path) -> None:
    path = tmp_path / "ledger.jsonl"
    ledger = SpendLedger(path, daily_budget_usd=1.0)
    assert ledger.spent_today(max_age_s=5) == 0.0
    now = datetime.now(UTC).isoformat()
    # Another process writes: the cached total is reused, a fresh read sees it.
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": now, "usd": 0.5}) + "\n")
    assert ledger.spent_today(max_age_s=5) == 0.0
    assert ledger.spent_today() == 0.5
    # This process's own spend is added to the cached total at once.
    ledger.record(
        CallRecord(
            ts=now, provider="openrouter", role="worker", model="claude-haiku-5-5",
            input_tokens=1, output_tokens=1, cache_read_tokens=0, cache_write_tokens=0,
            usd=0.25, priced=True, stop_reason="end_turn",
        )
    )  # fmt: skip
    assert ledger.spent_today(max_age_s=5) == 0.75
