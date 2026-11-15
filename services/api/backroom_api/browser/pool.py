"""Browser pool: one Chromium process, a fresh isolated context per run.

- **One browser, few contexts.** The 2 GB Lightsail box fits one Chromium with two contexts,
  not two browsers (ARCHITECTURE §8). `max_contexts` is a semaphore: a third run waits.
- **A fresh context per run** is a portal rule (CONTRACTS §3): a dismissed interstitial is
  remembered in a cookie that `/_admin/reset` cannot clear, and cookies never leak between
  runs this way.
- **The allowlist is enforced on every request**, not only on `goto`, so a link, a redirect
  or a script cannot take a run off the portal it was approved for.
"""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    Route,
    ViewportSize,
    async_playwright,
)

from backroom_api.browser.allowlist import Allowlist

VIEWPORT: ViewportSize = {"width": 1280, "height": 800}


class BrowserPool:
    def __init__(self, max_contexts: int = 2, headless: bool = True) -> None:
        self._headless = headless
        self._slots = asyncio.Semaphore(max_contexts)
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._start_lock = asyncio.Lock()

    async def start(self) -> None:
        async with self._start_lock:
            if self._browser is not None and self._browser.is_connected():
                return
            if self._playwright is None:
                self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=self._headless)

    async def close(self) -> None:
        async with self._start_lock:
            if self._browser is not None:
                await self._browser.close()
                self._browser = None
            if self._playwright is not None:
                await self._playwright.stop()
                self._playwright = None

    @property
    def running(self) -> bool:
        return self._browser is not None and self._browser.is_connected()

    @asynccontextmanager
    async def session(self, allowlist: Allowlist) -> AsyncIterator[Page]:
        """A fresh page in a fresh context, closed on exit (even on error)."""
        async with self._slots:
            await self.start()
            assert self._browser is not None
            context = await self._browser.new_context(
                viewport=VIEWPORT,
                locale="en-US",
                timezone_id="Europe/Berlin",
                accept_downloads=True,
            )
            try:
                await _guard(context, allowlist)
                yield await context.new_page()
            finally:
                await context.close()


async def _guard(context: BrowserContext, allowlist: Allowlist) -> None:
    async def handler(route: Route) -> None:
        request = route.request
        is_document = request.resource_type == "document"
        allowed = (
            allowlist.allows_document(request.url)
            if is_document
            else allowlist.allows_resource(request.url)
        )
        if allowed:
            await route.continue_()
        else:
            await route.abort("blockedbyclient")

    await context.route("**/*", handler)
