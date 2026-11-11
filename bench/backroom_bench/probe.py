"""Provider capability probe: one cheap worker-model call per feature.

Confirms which capability flags hold for the active LLM provider and writes
bench/results/provider_probe.json. See docs/ARCHITECTURE.md §5.1.
"""

import asyncio
import json
import subprocess
import time
from collections.abc import Awaitable, Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

import anthropic

from backroom_api.config import REPO_ROOT, Settings, get_settings
from backroom_api.llm import registry
from backroom_api.llm.client import LLM

RESULTS_PATH = REPO_ROOT / "bench" / "results" / "provider_probe.json"
MAX_TOKENS = 2_000

ORDER_TOOL: dict[str, Any] = {
    "name": "record_order",
    "description": "Record a supplier order line.",
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {"sku": {"type": "string"}, "qty": {"type": "integer"}},
        "required": ["sku", "qty"],
        "additionalProperties": False,
    },
}
INVOICE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"item": {"type": "string"}, "price_eur_per_kg": {"type": "number"}},
    "required": ["item", "price_eur_per_kg"],
    "additionalProperties": False,
}
# A deterministic prefix comfortably above the minimum cacheable length.
CACHE_PREFIX = "Grainline Wholesale portal manual.\n" + "\n".join(
    f"Section {i}: catalogue row {i} lists pack size, unit price in EUR, and delivery days."
    for i in range(1, 401)
)


@dataclass
class Check:
    ok: bool
    detail: str
    ms: int = 0
    usd: float = 0.0


def _user(text: str) -> list[dict[str, Any]]:
    return [{"role": "user", "content": text}]


async def check_basic(llm: LLM) -> Check:
    r = await llm.create(
        "worker", messages=_user("Reply with the single word: ready"), max_tokens=MAX_TOKENS
    )
    ok = r.message.stop_reason == "end_turn" and bool(r.text.strip())
    return Check(ok, f"stop_reason={r.message.stop_reason} text={r.text.strip()[:40]!r}",
                 usd=r.cost.usd)


async def check_effort(llm: LLM) -> Check:
    r = await llm.create(
        "worker", messages=_user("Reply with the single word: ready"), max_tokens=MAX_TOKENS
    )
    ok = r.message.stop_reason == "end_turn"
    return Check(ok, f"output_config.effort={r.role.effort} accepted; "
                 f"stop_reason={r.message.stop_reason}", usd=r.cost.usd)


async def check_strict_tools(llm: LLM) -> Check:
    r = await llm.create(
        "worker",
        messages=_user("Use the record_order tool to record 24 units of SKU OAT-1L."),
        tools=[ORDER_TOOL],
        max_tokens=MAX_TOKENS,
    )
    calls = [b for b in r.message.content if b.type == "tool_use"]
    ok = (
        r.message.stop_reason == "tool_use"
        and len(calls) == 1
        and calls[0].input == {"sku": "OAT-1L", "qty": 24}
    )
    seen = calls[0].input if calls else None
    return Check(ok, f"stop_reason={r.message.stop_reason} input={seen}", usd=r.cost.usd)


async def check_structured_outputs(llm: LLM) -> Check:
    r = await llm.create(
        "worker",
        messages=_user("Extract from this invoice line: 'Butter, 10 kg at EUR 8.24 per kg'."),
        json_schema=INVOICE_SCHEMA,
        max_tokens=MAX_TOKENS,
    )
    try:
        data = json.loads(r.text)
    except json.JSONDecodeError:
        return Check(False, f"not JSON: {r.text[:80]!r}", usd=r.cost.usd)
    ok = (
        r.message.stop_reason == "end_turn"
        and set(data) == {"item", "price_eur_per_kg"}
        and data["price_eur_per_kg"] == 8.24
    )
    return Check(ok, f"parsed={data}", usd=r.cost.usd)


async def check_prompt_cache(llm: LLM) -> Check:
    system = [{"type": "text", "text": CACHE_PREFIX, "cache_control": {"type": "ephemeral"}}]
    first = await llm.create(
        "worker", system=system, messages=_user("How many sections are there? Number only."),
        max_tokens=MAX_TOKENS,
    )
    second = await llm.create(
        "worker", system=system, messages=_user("What does section 7 list? One sentence."),
        max_tokens=MAX_TOKENS,
    )
    written = first.message.usage.cache_creation_input_tokens or 0
    read = second.message.usage.cache_read_input_tokens or 0
    return Check(read > 0, f"first call cache_write={written}, second call cache_read={read}",
                 usd=first.cost.usd + second.cost.usd)


async def check_streaming(llm: LLM) -> Check:
    deltas: list[str] = []
    r = await llm.stream(
        "worker",
        messages=_user("Count from 1 to 20, separated by spaces."),
        max_tokens=MAX_TOKENS,
        on_text=deltas.append,
    )
    ok = r.message.stop_reason == "end_turn" and len(deltas) >= 1 and "20" in r.text
    return Check(ok, f"{len(deltas)} text deltas; stop_reason={r.message.stop_reason}",
                 usd=r.cost.usd)


async def _run(name: str, fn: Callable[[LLM], Awaitable[Check]], llm: LLM) -> Check:
    start = time.perf_counter()
    try:
        check = await fn(llm)
    except anthropic.APIStatusError as e:
        check = Check(False, f"HTTP {e.status_code}: {e.message[:300]}")
    except anthropic.APIConnectionError as e:
        check = Check(False, f"connection error: {e}")
    except Exception as e:  # report, don't crash the probe
        check = Check(False, f"{type(e).__name__}: {e}")
    check.ms = int((time.perf_counter() - start) * 1000)
    print(f"  {'PASS' if check.ok else 'FAIL'}  {name:<19} {check.ms:>6} ms  {check.detail}")
    return check


def _git_sha() -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.strip()


async def run_probe(settings: Settings) -> int:
    worker = registry.role_config("worker", settings)
    print(f"Provider: {settings.llm_provider} · worker model: {worker.wire_model}")

    # Each feature is probed in isolation: effort is off everywhere except its own check.
    plain = LLM(settings.model_copy(update={"llm_caps_off": "effort"}))
    with_effort = LLM(settings.model_copy(update={"llm_caps_off": ""}))

    checks: dict[str, Check] = {"basic": await _run("basic", check_basic, plain)}
    if checks["basic"].ok:
        checks["effort"] = await _run("effort", check_effort, with_effort)
        checks["strict_tools"] = await _run("strict_tools", check_strict_tools, plain)
        checks["structured_outputs"] = await _run(
            "structured_outputs", check_structured_outputs, plain
        )
        checks["prompt_cache"] = await _run("prompt_cache", check_prompt_cache, plain)
        checks["streaming"] = await _run("streaming", check_streaming, plain)
    else:
        print("  Basic call failed; skipping the feature checks.")

    failed = [name for name, c in checks.items() if not c.ok]
    caps_off = ",".join(n for n in failed if n in registry.CAP_NAMES)
    result = {
        "provider": settings.llm_provider,
        "model": worker.model,
        "wire_model": worker.wire_model,
        "sdk_version": anthropic.__version__,
        "ran_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "git_sha": _git_sha(),
        "checks": {name: asdict(c) for name, c in checks.items()},
        "total_usd": round(sum(c.usd for c in checks.values()), 6),
        "recommended_llm_caps_off": caps_off,
    }
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {RESULTS_PATH.relative_to(REPO_ROOT)} · total ${result['total_usd']:.4f}")
    if failed:
        print(f"FAILED: {', '.join(failed)}")
        if caps_off:
            print(f"Set LLM_CAPS_OFF={caps_off} in .env and record it in docs/DECISIONS.md.")
        return 1
    print("All capability checks passed.")
    return 0


def main() -> int:
    settings = get_settings()
    if not registry.is_configured(settings):
        key = "OPENROUTER_API_KEY" if settings.llm_provider == "openrouter" else "ANTHROPIC_API_KEY"
        print(f"NOT RUN: {key} is not set in .env (LLM_PROVIDER={settings.llm_provider}).")
        return 2
    return asyncio.run(run_probe(settings))
