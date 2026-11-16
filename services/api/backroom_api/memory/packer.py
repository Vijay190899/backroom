"""Context packer (PRD §8.3): the compact, token-budgeted facts an agent run sees.

task -> seed entities (`seeds_for`) -> facts valid at `as_of` within 2 hops -> ranked
by (hop, recency, confidence) -> taken in rank order until the token budget is spent.
The business's standing preferences and rules always come first, so a learned cap
("max 8%") reaches every brief. The pack ships with the run (ContextPack).

The text is grouped by entity: a header with the entity's id and its name, then one
indented line per fact. Names are information ("holiday:2026-05-25" is "Whit Monday"), and
a group is easy to count ("how many items are on the menu?") and repeats no ids:

    product:croissant "Butter croissant"
      menu_price_eur 2.6 (since 2026-05-24)
      uses_ingredient ingredient:butter {"grams":30.0} (since 2026-05-24)

Two more sources, both ranked behind what the task names directly:
- **History** of the named entities: facts a newer one replaced, marked "from ... until
  ...", so "what did butter cost before?" has an answer (the memory is bitemporal; the
  pack used to show only the present).
- **Kinds** the task mentions ("the menu", "holidays", "staff"): the entities of that kind,
  so a question about a kind of thing, not a named one, still reaches its facts.
"""

import json
import math
import re
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from psycopg import Connection
from psycopg.rows import dict_row

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


# Words that mean "entities of this kind" (whole words, case-insensitive).
KIND_WORDS: dict[str, tuple[str, ...]] = {
    "product": ("menu", "menu items", "products"),
    "holiday": ("holiday", "holidays"),
    "staff": ("staff", "employees", "team", "people"),
    "ingredient": ("ingredient", "ingredients"),
    "supplier": ("supplier", "suppliers"),
    "weather_day": ("weather", "forecast"),
}


def kinds_for(task: str) -> list[str]:
    """Entity kinds the task talks about as a whole ("how many items on the menu")."""
    text = task.lower()
    return [
        kind
        for kind, words in KIND_WORDS.items()
        if any(re.search(rf"\b{re.escape(w)}\b", text) for w in words)
    ]


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


def _fact_line(fact: dict[str, Any]) -> str:
    """A fact without its subject (the group's header names it)."""
    obj = fact["object_id"] or ""
    if fact["value"] is not None:
        value = json.dumps(fact["value"], separators=(",", ":"), sort_keys=True)
        obj = f"{obj} {value}".strip()
    start = fact["valid_from"].astimezone(BONN).date().isoformat()
    confidence = "" if fact["confidence"] >= 1 else f" conf={fact['confidence']:.2f}"
    if fact.get("ended"):  # history: replaced by a newer fact
        end = fact["valid_to"].astimezone(BONN).date().isoformat()
        when = f"from {start} until {end}"
    else:
        when = f"since {start}"
    return f"{fact['predicate']} {obj} ({when}{confidence})"


def _header(entity_id: str, names: dict[str, str]) -> str:
    name = names.get(entity_id)
    return f"{entity_id} {json.dumps(name, ensure_ascii=False)}" if name else entity_id


def render(
    ranked: list[dict[str, Any]], names: dict[str, str], budget_tokens: int
) -> tuple[str, list[str]]:
    """The grouped text of the longest rank-order prefix of `ranked` that fits the budget,
    and the ids of the facts in it. A fact that does not fit ends the pack, so a smaller
    budget always keeps a prefix of a larger one."""
    groups: dict[str, list[str]] = {}
    fact_ids: list[str] = []
    chars = -1  # the newlines between lines: one fewer than the lines
    for f in ranked:
        subject, line = f["subject_id"], "  " + _fact_line(f)
        cost = len(line) + 1 + (len(_header(subject, names)) + 1 if subject not in groups else 0)
        if math.ceil((chars + cost) / CHARS_PER_TOKEN) > budget_tokens:
            break
        chars += cost
        groups.setdefault(subject, []).append(line)
        fact_ids.append(f["id"])
    # Groups appear in rank order; inside one, facts sort by predicate (stable, so rank
    # order holds within a predicate), which keeps a product's price lines together.
    text = "\n".join(
        "\n".join([_header(subject, names), *sorted(lines, key=_predicate)])
        for subject, lines in groups.items()
    )
    return text, fact_ids


def _predicate(line: str) -> str:
    return line.lstrip().split(" ", 1)[0]


HISTORY_SQL = """
select * from fact
where subject_id = any(%(ids)s)
  and valid_to is not null and valid_to <= %(t)s
  and recorded_at <= coalesce(%(r)s::timestamptz, now())
order by subject_id, predicate, valid_from
"""


def _history(
    conn: Connection[Any], ids: list[str], as_of: datetime, known_at: datetime | None
) -> list[dict[str, Any]]:
    if not ids:
        return []
    with conn.cursor(row_factory=dict_row) as cur:
        rows = cur.execute(HISTORY_SQL, {"ids": ids, "t": as_of, "r": known_at}).fetchall()
    return [{**r, "ended": True} for r in rows]


def pack(
    conn: Connection[Any],
    seeds: list[str],
    as_of: datetime,
    budget_tokens: int = DEFAULT_BUDGET_TOKENS,
    known_at: datetime | None = None,
    task: str = "",
) -> ContextPack:
    """The pack for `seeds` (named entities) and, if given, the kinds `task` mentions."""
    facts = facts_as_of(conn, as_of, known_at)
    picked: dict[str, tuple[float, dict[str, Any]]] = {}  # fact id -> (rank, fact)
    for f in facts:  # standing rules rank first, ahead of everything the seeds reach
        if f["subject_id"] == BUSINESS and f["predicate"] in STANDING:
            picked[f["id"]] = (-1, f)
    # What the task names directly: its current facts (hop 0), then their history.
    for f in _history(conn, seeds, as_of, known_at):
        picked[f["id"]] = (0.5, f)
    # Kinds it mentions: every entity of that kind, ranked after the named ones.
    kinds = kinds_for(task) if task else []
    if kinds:
        kind_ids = {
            r[0] for r in conn.execute("select id from entity where type = any(%s)", [kinds])
        } - set(seeds)
        for f in facts:
            if f["subject_id"] in kind_ids and f["id"] not in picked:
                picked[f["id"]] = (1.5, f)
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
    names = {
        r[0]: r[1]
        for r in conn.execute(
            "select id, name from entity where id = any(%s)",
            [sorted({f["subject_id"] for _, f in ranked})],
        )
    }
    text, fact_ids = render([f for _, f in ranked], names, budget_tokens)
    return ContextPack(
        as_of=as_of,
        fact_ids=fact_ids,
        text=text,
        tokens=estimate_tokens(text),
        budget_tokens=budget_tokens,
    )
