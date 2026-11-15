"""B3, memory vs baseline: the same 30 questions answered three ways (PRD §9):
(a) with the temporal-memory context pack, (b) with a raw dump of the data in the prompt,
(c) with no memory at all. Graded against SQL ground truth: ±1% for amounts, exact for
counts and names. Tokens, $ and latency come from the API's usage, through the cost meter.
"""

import json
import time
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import fmean
from typing import Any, Protocol

import duckdb

from backroom_bench.questions import QUESTIONS, Question
from backroom_bench.results import percentile, rate

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "out"
TOLERANCE = 0.01


def connect(data_dir: Path = DATA_DIR) -> duckdb.DuckDBPyConnection:
    """Every table in the seeded data as a view, for the ground-truth SQL."""
    con = duckdb.connect()
    for path in sorted(data_dir.glob("*.parquet")):
        con.execute(f"CREATE VIEW {path.stem} AS SELECT * FROM '{path}'")
    return con


def ground_truth(
    con: duckdb.DuckDBPyConnection, questions: Sequence[Question] = QUESTIONS
) -> dict[str, Any]:
    truth: dict[str, Any] = {}
    for q in questions:
        rows = con.execute(q.sql).fetchall()
        if len(rows) != 1 or len(rows[0]) != 1 or rows[0][0] is None:
            raise ValueError(f"{q.id}: ground truth must be one value, got {rows!r}")
        truth[q.id] = rows[0][0]
    return truth


def correct(q: Question, truth: Any, answer: str | float | None) -> bool:
    if answer is None:
        return False
    if q.kind == "text":
        return str(answer).strip().casefold() == str(truth).strip().casefold()
    try:
        value = float(str(answer).replace(",", "").replace("€", "").replace("%", "").strip())
    except ValueError:
        return False
    if q.kind == "count":
        return round(value) == round(float(truth)) and abs(value - round(value)) < 1e-6
    t = float(truth)
    return abs(value - t) <= TOLERANCE * abs(t) if t else abs(value) < 1e-9


@dataclass(frozen=True)
class Answer:
    value: str | None
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    usd: float
    ms: int
    cache_write_tokens: int = 0

    @property
    def prompt_tokens(self) -> int:
        """Everything the model read: uncached input plus cache reads and writes, so a
        cached raw dump is still counted at its full size when the arms are compared."""
        return self.input_tokens + self.cache_read_tokens + self.cache_write_tokens


class Answerer(Protocol):
    async def answer(self, question: str, context: str) -> Answer: ...


class ContextArm(Protocol):
    name: str

    def context(self, question: Question) -> str: ...


class NoMemory:
    name = "none"

    def context(self, question: Question) -> str:
        return ""


DAILY_SALES = (
    "select date, weekday, item_id, sum(qty) qty, round(sum(revenue_eur), 2) revenue_eur,"
    " count(distinct transaction_id) transactions"
    " from sales group by all order by date, item_id"
)


class RawDump:
    """Arm (b): the data itself in the prompt. Sales go in as daily per-item rows (the
    raw transactions are ~27k lines, beyond any context window); every other table whole."""

    name = "raw_dump"

    def __init__(self, con: duckdb.DuckDBPyConnection) -> None:
        tables = [
            r[0]
            for r in con.execute(
                "select view_name from duckdb_views() where not internal"
            ).fetchall()
        ]
        parts: list[str] = []
        for t in sorted(tables):
            sql = DAILY_SALES if t == "sales" else f"select * from {t}"
            cur = con.execute(sql)
            cols = [d[0] for d in cur.description]
            lines = [",".join(cols)] + [
                ",".join("" if v is None else str(v) for v in row) for row in cur.fetchall()
            ]
            parts.append(f"## {t}\n" + "\n".join(lines))
        self._text = "\n\n".join(parts)

    def context(self, question: Question) -> str:
        return self._text


class PackArm:
    """Arm (a): the context pack the agents get (ContextPack.text), from a callable the
    PC wires to the memory store: `pack_for(question_text) -> str`."""

    name = "context_pack"

    def __init__(self, pack_for: Any) -> None:
        self._pack_for = pack_for

    def context(self, question: Question) -> str:
        return str(self._pack_for(question.text))


ANSWER_SCHEMA = {
    "type": "object",
    "properties": {"answer": {"type": ["string", "null"]}},
    "required": ["answer"],
    "additionalProperties": False,
}
SYSTEM = (
    "You answer questions about a café's business records. Use only the records given. "
    "Reply with the bare answer: a number without units or currency signs, or a name. "
    "If the records do not contain it, answer null."
)


class LlmAnswerer:
    """The real answerer: one structured-output call per question through the shared LLM
    client (registry, cost meter, budget guard). Role `ask`."""

    def __init__(self, llm: Any) -> None:
        self._llm = llm

    async def answer(self, question: str, context: str) -> Answer:
        # The records are the stable prefix (the same for every question in an arm), so
        # they are cached; only the question changes.
        records: dict[str, Any] = {"type": "text", "text": f"Records:\n{context or '(none)'}"}
        if context:
            records["cache_control"] = {"type": "ephemeral"}
        content = [records, {"type": "text", "text": f"Question: {question}"}]
        started = time.perf_counter()
        result = await self._llm.create(
            "ask",
            system=[{"type": "text", "text": SYSTEM}],
            messages=[{"role": "user", "content": content}],
            json_schema=ANSWER_SCHEMA,
            max_tokens=200,
        )
        ms = int((time.perf_counter() - started) * 1000)
        msg = result.message
        value: str | None = None
        if msg.stop_reason == "end_turn":
            try:
                raw = json.loads(result.text).get("answer")
                value = None if raw is None else str(raw)
            except (json.JSONDecodeError, AttributeError):
                value = None
        u = msg.usage
        return Answer(
            value,
            u.input_tokens,
            u.output_tokens,
            u.cache_read_input_tokens or 0,
            result.cost.usd,
            ms,
            u.cache_creation_input_tokens or 0,
        )


async def b3(
    answerer: Answerer,
    arms: Sequence[ContextArm],
    truth: dict[str, Any],
    questions: Sequence[Question] = QUESTIONS,
) -> dict[str, Any]:
    per_arm: dict[str, dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    for arm in arms:
        answers: list[tuple[Question, Answer, bool]] = []
        for q in questions:
            a = await answerer.answer(q.text, arm.context(q))
            ok = correct(q, truth[q.id], a.value)
            answers.append((q, a, ok))
            rows.append(
                {
                    "arm": arm.name,
                    "question": q.id,
                    "truth": str(truth[q.id]),
                    "ok": ok,
                    **asdict(a),
                }
            )
        per_arm[arm.name] = {
            "accuracy": rate(sum(ok for *_, ok in answers), len(answers)),
            "input_tokens": sum(a.prompt_tokens for _, a, _ in answers),
            "mean_input_tokens": round(fmean(a.prompt_tokens for _, a, _ in answers), 1),
            "cache_read_tokens": sum(a.cache_read_tokens for _, a, _ in answers),
            "usd": round(sum(a.usd for _, a, _ in answers), 6),
            "p50_ms": percentile([a.ms for _, a, _ in answers], 50),
        }
    pack, dump = per_arm.get("context_pack"), per_arm.get("raw_dump")
    ratio = (
        round(int(pack["input_tokens"]) / int(dump["input_tokens"]), 4)
        if pack and dump and dump["input_tokens"]
        else None
    )
    return {
        "arms": per_arm,
        "headline": {
            "pack_tokens_vs_dump": ratio,
            "targets": {"pack_accuracy": 0.9, "pack_tokens_vs_dump": 0.2},
        },
        "answers": rows,
    }
