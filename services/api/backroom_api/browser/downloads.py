"""Files a run's browser downloaded, kept in memory for the postconditions.

A download is proof by itself: `file_downloaded` passes only if the browser received a file
with the expected name whose bytes really are that kind of file (a PDF starts `%PDF-`).
The bytes are read while the run's context is still open (its temp files go with it).
"""

import asyncio
from dataclasses import dataclass
from pathlib import Path

from playwright.async_api import Download, Page


@dataclass(frozen=True)
class DownloadedFile:
    name: str  # the server's suggested file name
    data: bytes


class DownloadLog:
    def __init__(self, page: Page) -> None:
        self.files: list[DownloadedFile] = []
        self._pending: set[asyncio.Future[None]] = set()
        page.on("download", self._on_download)

    def _on_download(self, download: Download) -> None:
        task = asyncio.ensure_future(self._save(download))
        self._pending.add(task)
        task.add_done_callback(self._pending.discard)

    async def _save(self, download: Download) -> None:
        path = await download.path()  # waits until the download is complete
        data = await asyncio.to_thread(Path(path).read_bytes)
        self.files.append(DownloadedFile(download.suggested_filename, data))

    async def settle(self, timeout_s: float = 10.0) -> None:
        """Wait for downloads still in flight (a click right before the check)."""
        if self._pending:
            await asyncio.wait(list(self._pending), timeout=timeout_s)
