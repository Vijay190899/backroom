"""Cost meter and daily budget guard. Every LLM call is recorded here."""

import json
import threading
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


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


class SpendLedger:
    """Append-only JSONL ledger of LLM calls, with a per-day spend total."""

    def __init__(self, path: Path, daily_budget_usd: float) -> None:
        self._path = path
        self._budget = daily_budget_usd
        self._lock = threading.Lock()

    @staticmethod
    def _today() -> str:
        return datetime.now(UTC).date().isoformat()

    def spent_today(self) -> float:
        if not self._path.exists():
            return 0.0
        today = self._today()
        total = 0.0
        with self._path.open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                if row["ts"].startswith(today):
                    total += row["usd"]
        return total

    def check_budget(self) -> None:
        spent = self.spent_today()
        if spent >= self._budget:
            raise BudgetExceededError(
                f"Daily LLM budget reached: ${spent:.4f} of ${self._budget:.2f} spent today"
            )

    def record(self, record: CallRecord) -> None:
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(record)) + "\n")
