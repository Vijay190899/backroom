"""The temporal knowledge graph (PRD §8.3) on the `0001_memory.sql` schema.

Facts are only ever inserted. A new fact supersedes the open fact on the same
(subject, predicate) - or (subject, predicate, object) for many-valued predicates - by
closing it: `valid_to` = the new fact's `valid_from`, `invalidated_at` = the new row's
`recorded_at` and `superseded_by` = the new id, in the same transaction, under a
per-key advisory lock (CONTRACTS §8).

All functions take a sync psycopg connection (ADR-10) and leave commit to the caller.
"""

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from backroom_api.contracts.api import (
    EntityType,
    EpisodeKind,
    EpisodeRef,
    FactDetail,
    GraphFact,
    GraphNode,
    MemoryGraph,
)

# Predicates where one subject holds several facts at once (one per object).
MANY_VALUED = frozenset({"uses_ingredient", "has_preference", "has_rule", "works_at"})


class OutOfOrderFactError(ValueError):
    """A fact must start after the open fact it supersedes (no back-dated corrections)."""


def _id(prefix: str, *parts: object) -> str:
    digest = hashlib.sha256(json.dumps(parts, default=str, sort_keys=True).encode()).hexdigest()
    return f"{prefix}_{digest[:16]}"


def upsert_entity(
    conn: Connection[Any], entity_id: str, type_: EntityType, name: str, **attrs: Any
) -> str:
    conn.execute(
        "insert into entity (id, type, name, attrs) values (%s, %s, %s, %s) "
        "on conflict (id) do update set name = excluded.name, attrs = excluded.attrs",
        [entity_id, type_, name, Jsonb(attrs)],
    )
    return entity_id


def add_episode(
    conn: Connection[Any], kind: EpisodeKind, payload: dict[str, Any], occurred_at: datetime
) -> str:
    """Record a raw input. The id is a hash of its content, so writers are idempotent."""
    episode_id = _id("ep", kind, payload, occurred_at.isoformat())
    conn.execute(
        "insert into episode (id, kind, payload, occurred_at) values (%s, %s, %s, %s) "
        "on conflict (id) do nothing",
        [episode_id, kind, Jsonb(payload), occurred_at],
    )
    return episode_id


@dataclass(frozen=True)
class Assertion:
    fact_id: str
    created: bool  # False when an identical fact was already open
    superseded: str | None  # the fact this one closed


def assert_fact(
    conn: Connection[Any],
    subject_id: str,
    predicate: str,
    *,
    valid_from: datetime,
    value: Any = None,
    object_id: str | None = None,
    source_episode: str | None = None,
    confidence: float = 1.0,
) -> Assertion:
    """Insert a fact, superseding the open one it replaces. Idempotent: asserting the
    same value again (same subject/predicate/object, same value) changes nothing."""
    many = predicate in MANY_VALUED
    key_sql = "subject_id = %s and predicate = %s and valid_to is null"
    params: list[Any] = [subject_id, predicate]
    if many:
        key_sql += " and object_id is not distinct from %s"
        params.append(object_id)
    fact_id = _id("f", subject_id, predicate, object_id, value, valid_from.isoformat())
    # Serialise writers of the same key for the rest of the transaction. A row lock is
    # not enough: with no open row there is nothing to lock, and under READ COMMITTED a
    # blocked writer would re-read and insert a second open fact.
    lock_key = "|".join([subject_id, predicate, (object_id or "") if many else ""])
    conn.execute("select pg_advisory_xact_lock(hashtextextended(%s, 0))", [lock_key])
    # Already known: a fact with this subject, predicate, object and value that covers
    # valid_from (open, or superseded since). Replaying history then changes nothing.
    known = conn.execute(
        "select id from fact where subject_id = %s and predicate = %s "
        "and object_id is not distinct from %s and value is not distinct from %s "
        "and valid_from <= %s and (valid_to is null or valid_to > %s)",
        [
            subject_id,
            predicate,
            object_id,
            None if value is None else Jsonb(value),
            valid_from,
            valid_from,
        ],
    ).fetchone()
    if known is not None:
        return Assertion(known[0], created=False, superseded=None)
    with conn.cursor(row_factory=dict_row) as cur:
        open_facts = cur.execute(
            f"select id, value, object_id, valid_from from fact where {key_sql}",
            params,
        ).fetchall()
        superseded = None
        for old in open_facts:
            if old["valid_from"] >= valid_from:
                raise OutOfOrderFactError(
                    f"{subject_id}.{predicate}: new fact starts {valid_from}, "
                    f"open fact {old['id']} started {old['valid_from']}"
                )
        cur.execute(
            "insert into fact (id, subject_id, predicate, object_id, value, valid_from, "
            "source_episode, confidence) values (%s, %s, %s, %s, %s, %s, %s, %s)",
            [
                fact_id,
                subject_id,
                predicate,
                object_id,
                None if value is None else Jsonb(value),
                valid_from,
                source_episode,
                confidence,
            ],
        )
        for old in open_facts:
            # The DB clock, so invalidated_at equals the new row's recorded_at exactly.
            cur.execute(
                "update fact set valid_to = %s, invalidated_at = now(), superseded_by = %s "
                "where id = %s",
                [valid_from, fact_id, old["id"]],
            )
            superseded = old["id"]
    return Assertion(fact_id, created=True, superseded=superseded)


# --- reads ----------------------------------------------------------------------------------

# Valid at %(t)s, as we knew it at %(r)s (the migration header explains the clause).
AS_OF_SQL = """
select * from fact
where recorded_at <= coalesce(%(r)s::timestamptz, now()) and valid_from <= %(t)s
  and (valid_to is null or valid_to > %(t)s
       or (invalidated_at is not null
           and invalidated_at > coalesce(%(r)s::timestamptz, now())))
"""


def facts_as_of(
    conn: Connection[Any], t: datetime, known_at: datetime | None = None
) -> list[dict[str, Any]]:
    with conn.cursor(row_factory=dict_row) as cur:
        return cur.execute(
            AS_OF_SQL + " order by subject_id, predicate, valid_from",
            {"t": t, "r": known_at},  # None: as known now (DB clock)
        ).fetchall()


def _graph_fact(row: dict[str, Any]) -> GraphFact:
    return GraphFact(
        id=row["id"],
        subject_id=row["subject_id"],
        predicate=row["predicate"],
        object_id=row["object_id"],
        value=row["value"],
        valid_from=row["valid_from"],
        valid_to=row["valid_to"],
        confidence=row["confidence"],
    )


def graph(conn: Connection[Any], as_of: datetime, known_at: datetime | None = None) -> MemoryGraph:
    """GET /memory/graph?as_of=: the facts valid at `as_of` and the entities they touch."""
    facts = facts_as_of(conn, as_of, known_at)
    ids = sorted(
        {f["subject_id"] for f in facts} | {f["object_id"] for f in facts if f["object_id"]}
    )
    with conn.cursor(row_factory=dict_row) as cur:
        nodes = cur.execute(
            "select id, type, name from entity where id = any(%s) order by id", [ids]
        ).fetchall()
    return MemoryGraph(
        as_of=as_of,
        nodes=[GraphNode(**n) for n in nodes],
        facts=[_graph_fact(f) for f in facts],
    )


def fact_detail(conn: Connection[Any], fact_id: str) -> FactDetail | None:
    """GET /memory/facts/{id}: the fact, its source episode and its supersession chain."""
    with conn.cursor(row_factory=dict_row) as cur:
        row = cur.execute("select * from fact where id = %s", [fact_id]).fetchone()
        if row is None:
            return None
        episode = None
        if row["source_episode"]:
            ep = cur.execute(
                "select id, kind, occurred_at, payload from episode where id = %s",
                [row["source_episode"]],
            ).fetchone()
            if ep is not None:
                episode = EpisodeRef(
                    id=ep["id"],
                    kind=ep["kind"],
                    occurred_at=ep["occurred_at"],
                    summary=str(ep["payload"].get("summary", ep["kind"])),
                )
        earlier = cur.execute(
            "with recursive chain(id, depth) as ("
            "  select id, 1 from fact where superseded_by = %s"
            "  union all select f.id, c.depth + 1 from fact f join chain c"
            "  on f.superseded_by = c.id"
            ") select id from chain order by depth",
            [fact_id],
        ).fetchall()
    return FactDetail(
        fact=_graph_fact(row),
        recorded_at=row["recorded_at"],
        source=episode,
        supersedes=[e["id"] for e in earlier],
        superseded_by=row["superseded_by"],
        invalidated_at=row["invalidated_at"],
    )
