"""Cost meter and daily budget guard. Every LLM call is recorded here.

The ledger is shared by every process that calls a model: the API, a benchmark, a golden
recording, `pnpm demo:reset`. Each one may append while another reads, so both take an
exclusive lock on a sidecar `.lock` file. Without it, Windows' append mode (seek to the end,
then write: two steps) let two writers land on the same offset, and one record overwrote
the other, leaving a torn line that broke every budget check after it.
"""

import contextlib
import json
import logging
import os
import sys
import threading
import time
from collections.abc import Generator
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

log = logging.getLogger(__name__)

LOCK_TIMEOUT_S = 30.0  # a reader or writer holds the lock for milliseconds


class BudgetExceededError(RuntimeError):
    """Today's LLM spend has reached LLM_DAILY_BUDGET_USD."""


@dataclass(frozen=True)
class CallRecord:
    ts: str  # ISO 8601, UTC
    provider: str
    role: str
    model: str  # canonical
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    usd: float
    priced: bool
    stop_reason: str | None
    run_id: str | None = None


@contextlib.contextmanager
def file_lock(path: Path, timeout_s: float = LOCK_TIMEOUT_S) -> Generator[None]:
    """An exclusive lock across processes, held on the first byte of `path`."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        deadline = time.monotonic() + timeout_s
        if sys.platform == "win32":
            import msvcrt

            while True:
                try:
                    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    if time.monotonic() > deadline:
                        raise TimeoutError(f"could not lock {path} in {timeout_s:.0f} s") from None
                    time.sleep(0.01)
            try:
                yield
            finally:
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() > deadline:
                        raise TimeoutError(f"could not lock {path} in {timeout_s:.0f} s") from None
                    time.sleep(0.01)
            try:
                yield
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


class SpendLedger:
    """Append-only JSONL ledger of LLM calls, with a per-day spend total."""

    def __init__(self, path: Path, daily_budget_usd: float) -> None:
        self._path = path
        self._lock_path = path.with_name(path.name + ".lock")
        self._budget = daily_budget_usd
        self._lock = threading.Lock()
        self._warned_damaged = False

    @staticmethod
    def _today() -> str:
        return datetime.now(UTC).date().isoformat()

    def spent_today(self) -> float:
        if not self._path.exists():
            return 0.0
        today = self._today()
        total = 0.0
        damaged = 0
        with self._lock, file_lock(self._lock_path):
            data = self._path.read_bytes()
        for line in data.splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                ts, usd = row["ts"], float(row["usd"])
            except (ValueError, KeyError, TypeError):
                damaged += 1  # a line torn before the lock existed: skip it, don't stop runs
                continue
            if ts.startswith(today):
                total += usd
        if damaged and not self._warned_damaged:
            self._warned_damaged = True
            log.warning("LLM ledger %s has %d unreadable line(s), skipped", self._path, damaged)
        return total

    def check_budget(self) -> None:
        spent = self.spent_today()
        if spent >= self._budget:
            raise BudgetExceededError(
                f"Daily LLM budget reached: ${spent:.4f} of ${self._budget:.2f} spent today"
            )

    def record(self, record: CallRecord) -> None:
        line = (json.dumps(asdict(record)) + "\n").encode("utf-8")
        with self._lock, file_lock(self._lock_path), self._path.open("ab") as f:
            f.write(line)  # one write of one whole line, under the lock
