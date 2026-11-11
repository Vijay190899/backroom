import json
from pathlib import Path
from typing import Any

import pytest
from anthropic.types import Message

from backroom_api.config import Settings
from backroom_api.llm.client import LLM
from backroom_api.llm.meter import BudgetExceededError, SpendLedger


def fake_message(**usage: int) -> Message:
    return Message.model_validate(
        {
            "id": "msg_test",
            "type": "message",
            "role": "assistant",
            "model": "anthropic/claude-haiku-5.5",
            "content": [{"type": "text", "text": "ok"}],
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {"input_tokens": 1000, "output_tokens": 100, **usage},
        }
    )


class FakeMessages:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def create(self, **kwargs: Any) -> Message:
        self.calls.append(kwargs)
        return fake_message(cache_read_input_tokens=5000)


class FakeClient:
    def __init__(self) -> None:
        self.messages = FakeMessages()


def make_llm(tmp_path: Path, **overrides: Any) -> tuple[LLM, FakeClient, Path]:
    ledger_path = tmp_path / "ledger.jsonl"
    settings = Settings(
        _env_file=None,  # type: ignore[call-arg]
        openrouter_api_key="sk-or-test",
        llm_ledger_path=ledger_path,
        **overrides,
    )
    client = FakeClient()
    return LLM(settings, client=client), client, ledger_path  # type: ignore[arg-type]


STRICT_TOOL = {
    "name": "record_order",
    "description": "Record an order",
    "strict": True,
    "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
}


async def test_create_sends_wire_model_and_effort_and_records_cost(tmp_path: Path) -> None:
    llm, client, ledger_path = make_llm(tmp_path)
    result = await llm.create("worker", messages=[{"role": "user", "content": "hi"}])

    sent = client.messages.calls[0]
    assert sent["model"] == "anthropic/claude-haiku-5.5"
    assert sent["output_config"] == {"effort": "low"}
    assert "temperature" not in sent and "thinking" not in sent and "tool_choice" not in sent

    expected = (1000 * 0.10 + 100 * 0.50 + 5000 * 0.01) / 1e6
    assert result.text == "ok"
    assert result.cost.usd == pytest.approx(expected)
    row = json.loads(ledger_path.read_text(encoding="utf-8").strip())
    assert row["role"] == "worker" and row["model"] == "claude-haiku-5-5"
    assert row["provider"] == "openrouter" and row["cache_read_tokens"] == 5000
    assert row["usd"] == pytest.approx(expected)


async def test_json_schema_goes_into_output_config(tmp_path: Path) -> None:
    llm, client, _ = make_llm(tmp_path)
    schema = {"type": "object", "properties": {}, "additionalProperties": False}
    await llm.create("planner", messages=[{"role": "user", "content": "hi"}], json_schema=schema)
    sent = client.messages.calls[0]
    assert sent["model"] == "anthropic/claude-sonnet-5.5"
    assert sent["output_config"] == {
        "effort": "medium",
        "format": {"type": "json_schema", "schema": schema},
    }


async def test_caps_off_strips_effort_and_strict(tmp_path: Path) -> None:
    llm, client, _ = make_llm(tmp_path, llm_caps_off="effort,strict_tools,structured_outputs")
    await llm.create("worker", messages=[{"role": "user", "content": "hi"}], tools=[STRICT_TOOL])
    sent = client.messages.calls[0]
    assert "output_config" not in sent
    assert "strict" not in sent["tools"][0]
    assert "strict" in STRICT_TOOL  # caller's tool definition is not mutated
    with pytest.raises(RuntimeError, match="structured_outputs is switched off"):
        await llm.create("worker", messages=[{"role": "user", "content": "x"}], json_schema={})


async def test_budget_guard_blocks_before_calling(tmp_path: Path) -> None:
    llm, client, _ = make_llm(tmp_path, llm_daily_budget_usd=0.0001)
    await llm.create("worker", messages=[{"role": "user", "content": "hi"}])  # spends > budget
    with pytest.raises(BudgetExceededError):
        await llm.create("worker", messages=[{"role": "user", "content": "again"}])
    assert len(client.messages.calls) == 1


def test_ledger_only_counts_today(tmp_path: Path) -> None:
    path = tmp_path / "ledger.jsonl"
    path.write_text(json.dumps({"ts": "2020-01-01T00:00:00+00:00", "usd": 99.0}) + "\n")
    ledger = SpendLedger(path, daily_budget_usd=1.0)
    assert ledger.spent_today() == 0.0
    ledger.check_budget()  # does not raise
