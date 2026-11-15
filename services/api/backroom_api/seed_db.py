"""H1: apply the SQL migrations and load the demo world into Postgres.

    uv run python -m backroom_api.seed_db [--data-dir data/out]

Migrations in `services/api/migrations/*.sql` run once each, in file-name order, one
transaction per file; applied names are recorded in `schema_migrations`. The world load
(`memory.writers.write_world`) is idempotent: a second run creates no new facts.
"""

import argparse
import sys
from pathlib import Path

import psycopg

from backroom_api.config import REPO_ROOT, Settings
from backroom_api.memory.writers import write_world

MIGRATIONS = Path(__file__).resolve().parents[1] / "migrations"


def migrate(conn: psycopg.Connection) -> list[str]:
    """Apply pending migrations; returns the names applied in this call."""
    conn.execute(
        "create table if not exists schema_migrations ("
        "name text primary key, applied_at timestamptz not null default now())"
    )
    conn.commit()
    done = {r[0] for r in conn.execute("select name from schema_migrations")}
    applied: list[str] = []
    for path in sorted(MIGRATIONS.glob("*.sql")):
        if path.name in done:
            continue
        with conn.transaction():
            conn.execute(path.read_text(encoding="utf-8"))  # type: ignore[arg-type]
            conn.execute("insert into schema_migrations (name) values (%s)", (path.name,))
        applied.append(path.name)
    return applied


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="backroom_api.seed_db")
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data" / "out")
    args = parser.parse_args(argv)
    if not (args.data_dir / "manifest.json").exists():
        print(f"seed_db: {args.data_dir} has no manifest.json; run `backroom-data all` first")
        return 2
    with psycopg.connect(Settings().database_url) as conn:
        applied = migrate(conn)
        print(f"seed_db: migrations applied: {applied or 'none (up to date)'}")
        with conn.transaction():
            created = write_world(conn, args.data_dir)
        print(f"seed_db: facts created {created}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
