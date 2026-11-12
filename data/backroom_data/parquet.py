"""Write lists of dicts to Parquet with DuckDB (typed columns, stable row order)."""

import csv
import tempfile
from pathlib import Path
from typing import Any

import duckdb


def write(path: Path, rows: list[dict[str, Any]], schema: dict[str, str]) -> int:
    """Write rows to `path` with the given {column: DuckDB type}; returns the row count.

    Rows are staged through CSV (quoted by the csv module), with NULL written as an
    empty field; no table here has empty-string values, so nothing is lost."""
    if rows and set(rows[0]) != set(schema):
        raise ValueError(f"{path.name}: columns {sorted(rows[0])} != schema {sorted(schema)}")
    columns = list(schema)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        staging = Path(tmp) / "rows.csv"
        with staging.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            for r in rows:
                writer.writerow(["" if r[c] is None else r[c] for c in columns])
        spec = ", ".join(f"'{c}': '{t}'" for c, t in schema.items())
        con = duckdb.connect()
        con.execute("SET threads = 1")  # stable row order and byte-identical output
        con.execute(
            f"COPY (SELECT * FROM read_csv('{staging}', header = true, nullstr = '', "
            f"columns = {{{spec}}})) TO '{path}' (FORMAT parquet)"
        )
        con.close()
    return len(rows)


def read(path: Path) -> list[tuple[Any, ...]]:
    con = duckdb.connect()
    out = con.execute(f"SELECT * FROM '{path}'").fetchall()
    con.close()
    return out
