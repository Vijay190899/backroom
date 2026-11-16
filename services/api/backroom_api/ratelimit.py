"""Per-client rate limits: sliding one-minute windows, kept in memory.

The API is public. Reads are cheap but not free (most read Postgres), and a write can start a
run, write run events or guess the demo access code. Limits are per client IP, which uvicorn
takes from Caddy's `X-Forwarded-For` (`--proxy-headers --forwarded-allow-ips '*'`: the API
port is reachable only from Caddy, and Caddy replaces any forwarded-for header a client sends).
The defaults leave room for an office sharing one IP. IPs are held for one window and never
logged.
"""

import logging
import time
from collections import deque
from collections.abc import Callable

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from backroom_api.routes.errors import body

log = logging.getLogger(__name__)

WRITE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
EXEMPT_PATHS = frozenset({"/health"})  # uptime checks and the web app's status pill


class RateLimiter:
    """ASGI middleware. Install it inside CORS, so a 429 still carries CORS headers."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        read_per_min: int,
        write_per_min: int,
        window_s: float = 60.0,
        max_clients: int = 10_000,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.app = app
        self.limits = {"read": read_per_min, "write": write_per_min}
        self.window_s = window_s
        self.max_clients = max_clients
        self.clock = clock
        self._hits: dict[tuple[str, str], deque[float]] = {}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket") or scope["path"] in EXEMPT_PATHS:
            await self.app(scope, receive, send)
            return
        method = scope.get("method", "GET")
        if method == "OPTIONS":  # CORS preflight: answered by the CORS middleware
            await self.app(scope, receive, send)
            return
        kind = "write" if method in WRITE_METHODS else "read"
        limit = self.limits[kind]
        if limit <= 0:  # 0 switches a limit off
            await self.app(scope, receive, send)
            return
        client = scope.get("client")
        ip = client[0] if client else "unknown"
        now = self.clock()
        hits = self._hits.setdefault((ip, kind), deque())
        while hits and now - hits[0] >= self.window_s:
            hits.popleft()
        if len(hits) >= limit:
            retry = max(1, int(self.window_s - (now - hits[0])) + 1)
            log.warning("rate limit: a client sent over %d %s requests a minute", limit, kind)
            if scope["type"] == "websocket":
                await send({"type": "websocket.close", "code": 1008})
                return
            response = JSONResponse(
                body("rate_limited", f"Too many requests. Try again in {retry} s."),
                status_code=429,
                headers={"Retry-After": str(retry)},
            )
            await response(scope, receive, send)
            return
        hits.append(now)
        if len(self._hits) > self.max_clients:
            self._prune(now)
        await self.app(scope, receive, send)

    def _prune(self, now: float) -> None:
        """Forget clients idle for a whole window; if still too many, the longest idle."""
        for key in [k for k, q in self._hits.items() if not q or now - q[-1] >= self.window_s]:
            del self._hits[key]
        if len(self._hits) > self.max_clients:
            by_last = sorted(self._hits, key=lambda k: self._hits[k][-1])
            for key in by_last[: len(self._hits) - self.max_clients]:
                del self._hits[key]

    @property
    def tracked_clients(self) -> int:
        return len(self._hits)
