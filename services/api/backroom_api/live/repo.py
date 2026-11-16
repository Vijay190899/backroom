"""Postgres access for briefs, actions, runs and run events (migration 0002).

Plain synchronous functions over one connection: the API calls them from worker threads
(ADR-10). Each function that writes commits, so one call is one transaction.
"""

from datetime import date, datetime
from typing import Any

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from backroom_api.contracts.api import ActionCard, Brief, RunSummary
from backroom_api.contracts.events import RunEvent, RunTotals, run_event_adapter

ZERO_TOTALS = RunTotals(
    elapsed_ms=0, steps=0, llm_calls=0, tokens_in=0, tokens_out=0, cache_read_tokens=0, usd=0
)

# --- briefs and actions ---------------------------------------------------------------


def save_brief(conn: Connection[Any], brief: Brief) -> None:
    """Store a brief and upsert its actions. An action keeps its status when the same
    proposal comes back in a regenerated brief."""
    conn.execute(
        "insert into brief (id, day, generated_at, body) values (%s, %s, %s, %s)",
        [brief.id, brief.as_of.date(), brief.generated_at, Jsonb(brief.model_dump(mode="json"))],
    )
    for card in brief.cards:
        conn.execute(
            "insert into action (id, brief_id, card) values (%s, %s, %s) "
            "on conflict (id) do update set brief_id = excluded.brief_id, card = excluded.card",
            [card.id, brief.id, Jsonb(card.model_dump(mode="json"))],
        )
    conn.commit()


def current_brief(conn: Connection[Any], day: date) -> Brief | None:
    """The newest brief for `day` that no rejection has made stale, with live statuses."""
    row = conn.execute(
        "select body from brief where day = %s and not stale order by generated_at desc limit 1",
        [day],
    ).fetchone()
    if row is None:
        return None
    brief = with_statuses(conn, Brief.model_validate(row[0]))
    return brief.model_copy(update={"cached": True})


def action_statuses(conn: Connection[Any], ids: list[str]) -> dict[str, str]:
    return dict(conn.execute("select id, status from action where id = any(%s)", [ids]).fetchall())


def with_statuses(conn: Connection[Any], brief: Brief) -> Brief:
    """Cards carry their action's real status: a proposal that comes back unchanged in a
    regenerated brief is the same action, already done (it must not be offered twice)."""
    statuses = action_statuses(conn, [c.id for c in brief.cards])
    cards = [c.model_copy(update={"status": statuses.get(c.id, c.status)}) for c in brief.cards]
    return brief.model_copy(update={"cards": cards})


def mark_briefs_stale(conn: Connection[Any], day: date) -> None:
    conn.execute("update brief set stale = true where day = %s", [day])
    conn.commit()


def get_action(conn: Connection[Any], action_id: str) -> tuple[ActionCard, str] | None:
    row = conn.execute("select card, status from action where id = %s", [action_id]).fetchone()
    return (ActionCard.model_validate(row[0]), row[1]) if row else None


def set_action_status(conn: Connection[Any], action_id: str, status: str) -> None:
    conn.execute(
        "update action set status = %s, updated_at = now() where id = %s", [status, action_id]
    )
    conn.commit()


# --- runs -----------------------------------------------------------------------------


def run_for_key(conn: Connection[Any], key: str) -> str | None:
    row = conn.execute("select id from run where idempotency_key = %s", [key]).fetchone()
    return row[0] if row else None


def create_run(
    conn: Connection[Any],
    *,
    run_id: str,
    action_id: str,
    task: str,
    portal: str,
    params: dict[str, Any],
    idempotency_key: str | None,
    undo_of: str | None = None,
    undo_params: dict[str, Any] | None = None,
) -> bool:
    """Insert a queued run. False if the idempotency key already has one (a race)."""
    cur = conn.execute(
        "insert into run (id, action_id, task, portal, params, idempotency_key, status, "
        "totals, undo_of, undo_params) values (%s, %s, %s, %s, %s, %s, 'queued', %s, %s, %s) "
        "on conflict (idempotency_key) do nothing",
        [
            run_id,
            action_id,
            task,
            portal,
            Jsonb(params),
            idempotency_key,
            Jsonb(ZERO_TOTALS.model_dump()),
            undo_of,
            Jsonb(undo_params) if undo_params is not None else None,
        ],
    )
    conn.commit()
    return cur.rowcount == 1


def add_event(conn: Connection[Any], event: RunEvent) -> None:
    """Store one event and keep the run row's summary fields in step with it."""
    body = event.model_dump(mode="json")
    conn.execute(
        "insert into run_event (run_id, seq, type, body) values (%s, %s, %s, %s) "
        "on conflict do nothing",
        [event.run_id, event.seq, event.type, Jsonb(body)],
    )
    if event.type == "run.started":
        conn.execute(
            "update run set status = 'running', mode = %s, skill_version = %s, chaos_seed = %s "
            "where id = %s",
            [event.mode, event.skill_version, event.chaos_seed, event.run_id],
        )
    elif event.type == "cost.tick":
        conn.execute(
            "update run set totals = %s where id = %s",
            [Jsonb(event.totals.model_dump()), event.run_id],
        )
    elif event.type == "ask_human":
        conn.execute("update run set status = 'needs_human' where id = %s", [event.run_id])
    elif event.type == "step.started":
        conn.execute(
            "update run set status = 'running' where id = %s and status = 'needs_human'",
            [event.run_id],
        )
    elif event.type == "run.finished":
        conn.execute(
            "update run set status = %s, finished_at = %s, totals = %s, summary = %s, "
            "skill_version = %s, undo_available = %s where id = %s",
            [
                event.status,
                event.ts,
                Jsonb(event.totals.model_dump()),
                event.summary,
                event.skill_version,
                event.undo_available,
                event.run_id,
            ],
        )
    conn.commit()


def set_undo(conn: Connection[Any], run_id: str, undo: dict[str, Any]) -> None:
    conn.execute("update run set undo_params = %s where id = %s", [Jsonb(undo), run_id])
    conn.commit()


def events_after(conn: Connection[Any], run_id: str, after: int) -> list[RunEvent]:
    rows = conn.execute(
        "select body from run_event where run_id = %s and seq > %s order by seq", [run_id, after]
    ).fetchall()
    return [run_event_adapter.validate_python(r[0]) for r in rows]


def get_run(conn: Connection[Any], run_id: str) -> dict[str, Any] | None:
    with conn.cursor(row_factory=dict_row) as cur:
        return cur.execute("select * from run where id = %s", [run_id]).fetchone()


def run_summary(row: dict[str, Any]) -> RunSummary:
    return RunSummary(
        id=row["id"],
        action_id=row["action_id"],
        task=row["task"],
        portal=row["portal"],
        status=row["status"],
        mode=row["mode"],
        skill_version=row["skill_version"],
        chaos_seed=row["chaos_seed"],
        started_at=row["started_at"],
        finished_at=row["finished_at"],
        totals=RunTotals.model_validate(row["totals"]),
        summary=row["summary"],
    )


def fail_unfinished(conn: Connection[Any], now: datetime) -> int:
    """At start-up: runs a previous process left queued or running can never finish."""
    cur = conn.execute(
        "update run set status = 'failed', finished_at = %s, "
        "summary = coalesce(summary, 'Interrupted: the API restarted during this run') "
        "where status in ('queued', 'running', 'needs_human')",
        [now],
    )
    conn.commit()
    return cur.rowcount
