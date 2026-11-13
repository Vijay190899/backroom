"""Context packer (PRD §8.3): the compact, token-budgeted facts an agent run sees.

task -> seed entities (`seeds_for`) -> facts valid at `as_of` within 2 hops -> ranked
by (hop, recency, confidence) -> one compact triple per line, until the token budget is
spent. The business's standing preferences and rules always come first, so a learned
cap ("max 8%") reaches every brief. The pack ships with the run (ContextPack).
"""

import json
import math
import re
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from psycopg import Connection

from backroom_api.contracts.api import ContextPack
from backroom_api.memory.store import facts_as_of

DEFAULT_BUDGET_TOKENS = 1200
MAX_HOPS = 2
BUSINESS = "business:hafer-und-bohne"
STANDING = ("has_preference", "has_rule")  # the business's rules: always in the pack
# Estimate, not a tokenizer call per pack. Ids, JSON and digits run at about 3 characters
# per token for Claude models, so this errs on the high side and the budget holds.
CHARS_PER_TOKEN = 3
BONN = ZoneInfo("Europe/Berlin")


def estimate_tokens(text: str) -> int:
    return math.ceil(len(text) / CHARS_PER_TOKEN)


def seeds_for(conn: Connection[Any], task: str) -> list[str]:
    """Entities the task mentions, by id slug or name (case-insensitive), in id order."""
    text = task.lower()
    found: list[str] = []
    for entity_id, name in conn.execute("select id, name from entity order by id").fetchall():
        slug = entity_id.split(":", 1)[1].replace("-", " ")
        names = {name.lower(), slug, entity_id.lower()}
        if any(re.search(rf"\b{re.escape(n)}\b", text) for n in names if len(n) > 2):
            found.append(entity_id)
    return found


def _triple(fact: dict[str, Any]) -> str:
    obj = fact["object_id"] or ""
    if fact["value"] is not None:
        value = json.dumps(fact["value"], separators=(",", ":"), sort_keys=True)
        obj = f"{obj} {value}".strip()
    since = fact["valid_from"].astimezone(BONN).date().isoformat()
    confidence = "" if fact["confidence"] >= 1 else f" conf={fact['confidence']:.2f}"
    return f"{fact['subject_id']} {fact['predicate']} {obj} (since {since}{confidence})"


def pack(
    conn: Connection[Any],
    seeds: list[str],
    as_of: datetime,
    budget_tokens: int = DEFAULT_BUDGET_TOKENS,
    known_at: datetime | None = None,
) -> ContextPack:
    facts = facts_as_of(conn, as_of, known_at)
    picked: dict[str, tuple[int, dict[str, Any]]] = {}
    for f in facts:  # standing rules rank first, ahead of everything the seeds reach
        if f["subject_id"] == BUSINESS and f["predicate"] in STANDING:
            picked[f["id"]] = (-1, f)
    seen = set(seeds)
    frontier = set(seeds)
    for distance in range(MAX_HOPS):
        reached: set[str] = set()
        for f in facts:
            ends = {f["subject_id"], f["object_id"]} - {None}
            if ends & frontier and f["id"] not in picked:
                picked[f["id"]] = (distance, f)
                reached |= ends - seen
        seen |= reached
        frontier = reached
    ranked = sorted(
        picked.values(),
        key=lambda item: (
            item[0],
            -item[1]["valid_from"].timestamp(),
            -item[1]["confidence"],
            item[1]["id"],
        ),
    )
    lines: list[str] = []
    fact_ids: list[str] = []
    for _, f in ranked:
        line = _triple(f)
        if estimate_tokens("\n".join([*lines, line])) > budget_tokens:
            break
        lines.append(line)
        fact_ids.append(f["id"])
    text = "\n".join(lines)
    return ContextPack(
        as_of=as_of,
        fact_ids=fact_ids,
        text=text,
        tokens=estimate_tokens(text),
        budget_tokens=budget_tokens,
    )
