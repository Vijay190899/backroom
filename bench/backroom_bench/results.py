"""Bench results: one JSON per benchmark under bench/results/ (PRD §9).

Every file carries what makes it reproducible: model ids, seeds, n, the date and the git
SHA. Numbers are measured, never estimated; a run that did not happen is not written.
"""

import json
import math
import subprocess
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backroom_api.config import Settings
from backroom_api.llm import registry

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"


def percentile(values: Sequence[float], q: float) -> float | None:
    """Nearest-rank percentile (q in 0..100); None for no values."""
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, math.ceil(q / 100 * len(ordered)))
    return ordered[rank - 1]


def rate(hits: int, n: int) -> float | None:
    return round(hits / n, 4) if n else None


def git_sha() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True
        )
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def models(settings: Settings) -> dict[str, str]:
    """The canonical model id per role, as the registry resolves them for this run."""
    roles = ("planner", "worker", "verifier", "heal", "escalation", "ask")
    return {r: registry.role_config(r, settings).model for r in roles}  # type: ignore[arg-type]


def with_fee(usd: float, settings: Settings) -> dict[str, float]:
    """Model spend plus OpenRouter's credit fee as its own line (ARCHITECTURE §5)."""
    fee = usd * settings.openrouter_fee_pct / 100 if settings.llm_provider == "openrouter" else 0.0
    return {
        "model_usd": round(usd, 6),
        "provider_fee_usd": round(fee, 6),
        "total_usd": round(usd + fee, 6),
    }


def write(
    bench_id: str,
    body: dict[str, Any],
    *,
    settings: Settings,
    seeds: Sequence[int] = (),
    n: int,
    fake: bool = False,
    out_dir: Path = RESULTS_DIR,
) -> Path:
    """Write `<out_dir>/<bench_id>.json` with the reproducibility header first."""
    payload = {
        "id": bench_id,
        "ran_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "git_sha": git_sha(),
        "provider": settings.llm_provider,
        "models": models(settings),
        "seeds": list(seeds),
        "n": n,
        # A fake run exercises the harness only; the bench page must never show it.
        "fake": fake,
        **body,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{bench_id.lower()}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
