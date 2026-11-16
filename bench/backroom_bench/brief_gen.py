"""Generate the briefs B5 grades, with the real pipeline and the real models (PC, H7).

    uv run backroom-bench briefs [--n 10]

Half the briefs use the owner's rules as memory holds them; the other half add an 8% price
cap, so the code-written "Kept under your 8% cap" note is in the sample too. Every call goes
through the shared LLM client (cost meter, budget guard). Written to var/bench/briefs/.
"""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import psycopg

from backroom_api.brief import pipeline
from backroom_api.brief.agents import LLMPlanner, LLMVerifier
from backroom_api.brief.rules import Preference, Rules, rules_from_memory
from backroom_api.config import Settings
from backroom_api.llm.client import LLM

BONN = ZoneInfo("Europe/Berlin")
CAP = Preference(
    "preference:bench-price-cap", "Price rises of at most 8%", {"max_price_increase_pct": 8}
)


async def generate(n: int, out_dir: Path, settings: Settings) -> tuple[list[Path], float]:
    """Returns the files written and the model spend (from the cost ledger)."""
    llm = LLM(settings)
    now = datetime.now(BONN)
    with psycopg.connect(settings.database_url) as conn:
        base = rules_from_memory(conn, now)
    capped = Rules(preferences=[*base.preferences, CAP], business_rules=base.business_rules)
    _clear(out_dir)
    spent_before = llm.ledger.spent_today()
    written: list[Path] = []
    for i in range(n):
        rules = base if i % 2 == 0 else capped
        result = await pipeline.brief_for_today(
            settings.data_dir,
            planner=LLMPlanner(llm, run_id=f"bench-brief-{i:02d}"),
            verifier=LLMVerifier(llm, run_id=f"bench-brief-{i:02d}"),
            rules=rules,
            now=now,
        )
        written.append(
            _write(out_dir / f"brief-{i:02d}.json", result.brief.model_dump(mode="json"))
        )
    return written, round(llm.ledger.spent_today() - spent_before, 6)


def _clear(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("brief*.json"):
        old.unlink()


def _write(path: Path, body: dict[str, object]) -> Path:
    path.write_text(json.dumps(body, ensure_ascii=False, indent=1), encoding="utf-8")
    return path
