"""Postgres access.

The pool is synchronous and used from worker threads. psycopg's async mode needs a
selector event loop on Windows, while Playwright needs the proactor loop, so the
async API never touches the database driver directly (see docs/DECISIONS.md, ADR-10).
"""

from psycopg_pool import ConnectionPool

from backroom_api.config import Settings


def make_pool(settings: Settings) -> ConnectionPool:
    return ConnectionPool(
        settings.database_url,
        min_size=1,
        max_size=5,
        open=False,
        timeout=5.0,
        kwargs={"connect_timeout": 3},
    )


def ping(pool: ConnectionPool) -> bool:
    with pool.connection() as conn:
        row = conn.execute("select 1").fetchone()
    return row is not None and row[0] == 1
