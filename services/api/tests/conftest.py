"""Shared fixtures for the browser tests: a local fixture site and a Chromium pool.

Every browser test skips when Chromium is not installed (the laptop), so the rest of the
suite still runs there.
"""

import functools
import http.server
import threading
from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from typing import Any

import pytest
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page

from backroom_api.browser import Allowlist, BrowserPool

FIXTURES = Path(__file__).parent / "fixtures"


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        pass


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    handler = functools.partial(_Quiet, directory=str(FIXTURES))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


@pytest.fixture
async def pool() -> AsyncIterator[BrowserPool]:
    p = BrowserPool(max_contexts=2)
    try:
        await p.start()
    except PlaywrightError as exc:
        if "Executable doesn't exist" in str(exc):
            pytest.skip("Chromium is not installed (run `uv run playwright install chromium`)")
        raise
    yield p
    await p.close()


@pytest.fixture
async def page(pool: BrowserPool, base_url: str) -> AsyncIterator[Page]:
    async with pool.session(Allowlist(base_url, ["/shop.html"])) as p:
        await p.goto(f"{base_url}/shop.html")
        yield p
