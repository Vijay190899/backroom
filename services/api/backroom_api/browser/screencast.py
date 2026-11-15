"""Live view: Chromium's CDP screencast, forwarded frame by frame.

`Page.startScreencast` pushes JPEG frames only when the page changes, so an idle page costs
nothing. Each frame must be acknowledged or Chromium stops sending; we ack before handing
the frame on, so a slow consumer drops frames instead of stalling the browser.
"""

import asyncio
import base64
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from playwright.async_api import CDPSession, Page

FrameCallback = Callable[["Frame"], Awaitable[None]]


@dataclass(frozen=True)
class Frame:
    seq: int
    jpeg: bytes
    width: int
    height: int


class Screencast:
    def __init__(self, page: Page, on_frame: FrameCallback, quality: int = 60) -> None:
        self._page = page
        self._on_frame = on_frame
        self._quality = quality
        self._cdp: CDPSession | None = None
        self._seq = 0
        self._pending: set[asyncio.Future[None]] = set()

    async def start(self) -> None:
        cdp = await self._page.context.new_cdp_session(self._page)
        self._cdp = cdp
        cdp.on("Page.screencastFrame", self._handle)
        await cdp.send(
            "Page.startScreencast",
            {"format": "jpeg", "quality": self._quality, "maxWidth": 1280, "maxHeight": 800},
        )

    async def stop(self) -> None:
        cdp, self._cdp = self._cdp, None
        if cdp is None:
            return
        try:
            await cdp.send("Page.stopScreencast")
            await cdp.detach()
        except Exception:  # the page may already be closed
            pass

    def _handle(self, params: dict[str, object]) -> None:
        task = asyncio.ensure_future(self._deliver(params))
        self._pending.add(task)  # a task nobody references can be garbage-collected mid-flight
        task.add_done_callback(self._pending.discard)

    async def _deliver(self, params: dict[str, object]) -> None:
        cdp = self._cdp
        if cdp is None:
            return
        try:
            await cdp.send("Page.screencastFrameAck", {"sessionId": params["sessionId"]})
        except Exception:
            return
        meta = params.get("metadata")
        meta = meta if isinstance(meta, dict) else {}
        self._seq += 1
        await self._on_frame(
            Frame(
                seq=self._seq,
                jpeg=base64.b64decode(str(params["data"])),
                width=int(meta.get("deviceWidth", 1280)),
                height=int(meta.get("deviceHeight", 800)),
            )
        )
