"""The one path every LLM call takes: budget check -> provider call -> cost record."""

from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import anthropic
from anthropic.types import Message

from backroom_api.config import Settings
from backroom_api.llm import registry
from backroom_api.llm.meter import CallRecord, SpendLedger
from backroom_api.llm.registry import Caps, Cost, Role, RoleConfig

DEFAULT_MAX_TOKENS = 16_000


@dataclass(frozen=True)
class LLMResult:
    message: Message
    cost: Cost
    role: RoleConfig

    @property
    def text(self) -> str:
        return "".join(b.text for b in self.message.content if b.type == "text")


class LLM:
    def __init__(
        self,
        settings: Settings,
        *,
        client: anthropic.AsyncAnthropic | None = None,
        ledger: SpendLedger | None = None,
    ) -> None:
        self._settings = settings
        self._client = client or registry.build_async_client(settings)
        self.caps: Caps = registry.caps_for(settings)
        self.ledger = ledger or SpendLedger(
            settings.llm_ledger_path, settings.llm_daily_budget_usd
        )

    def _request(
        self,
        role: Role,
        *,
        messages: list[dict[str, Any]],
        system: str | list[dict[str, Any]] | None,
        tools: list[dict[str, Any]] | None,
        json_schema: dict[str, Any] | None,
        max_tokens: int,
    ) -> tuple[RoleConfig, dict[str, Any]]:
        cfg = registry.role_config(role, self._settings)
        kwargs: dict[str, Any] = {
            "model": cfg.wire_model,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if system is not None:
            kwargs["system"] = system
        if tools:
            if not self.caps.strict_tools:
                tools = [{k: v for k, v in t.items() if k != "strict"} for t in tools]
            kwargs["tools"] = tools
        output_config: dict[str, Any] = {}
        if self.caps.effort:
            output_config["effort"] = cfg.effort
        if json_schema is not None:
            if not self.caps.structured_outputs:
                raise RuntimeError(
                    "structured_outputs is switched off for this provider; "
                    "use a strict tool or prompt for JSON instead"
                )
            output_config["format"] = {"type": "json_schema", "schema": json_schema}
        if output_config:
            kwargs["output_config"] = output_config
        return cfg, kwargs

    def _record(self, cfg: RoleConfig, message: Message, run_id: str | None) -> Cost:
        usage = message.usage
        cost = registry.cost_usd(
            cfg.model,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cache_read_tokens=usage.cache_read_input_tokens or 0,
            cache_write_tokens=usage.cache_creation_input_tokens or 0,
        )
        self.ledger.record(
            CallRecord(
                ts=datetime.now(UTC).isoformat(),
                provider=self._settings.llm_provider,
                role=cfg.role,
                model=cfg.model,
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                cache_read_tokens=usage.cache_read_input_tokens or 0,
                cache_write_tokens=usage.cache_creation_input_tokens or 0,
                usd=cost.usd,
                priced=cost.priced,
                stop_reason=message.stop_reason,
                run_id=run_id,
            )
        )
        return cost

    async def create(
        self,
        role: Role,
        *,
        messages: list[dict[str, Any]],
        system: str | list[dict[str, Any]] | None = None,
        tools: list[dict[str, Any]] | None = None,
        json_schema: dict[str, Any] | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        run_id: str | None = None,
    ) -> LLMResult:
        """One non-streaming call. Callers must check `message.stop_reason`."""
        self.ledger.check_budget()
        cfg, kwargs = self._request(
            role,
            messages=messages,
            system=system,
            tools=tools,
            json_schema=json_schema,
            max_tokens=max_tokens,
        )
        message = await self._client.messages.create(**kwargs)
        return LLMResult(message=message, cost=self._record(cfg, message, run_id), role=cfg)

    async def stream(
        self,
        role: Role,
        *,
        messages: list[dict[str, Any]],
        system: str | list[dict[str, Any]] | None = None,
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        run_id: str | None = None,
        on_text: Callable[[str], None] | None = None,
    ) -> LLMResult:
        """One streaming call; `on_text` receives text deltas as they arrive."""
        self.ledger.check_budget()
        cfg, kwargs = self._request(
            role,
            messages=messages,
            system=system,
            tools=tools,
            json_schema=None,
            max_tokens=max_tokens,
        )
        async with self._client.messages.stream(**kwargs) as stream:
            deltas: AsyncIterator[str] = stream.text_stream
            async for delta in deltas:
                if on_text is not None:
                    on_text(delta)
            message = await stream.get_final_message()
        return LLMResult(message=message, cost=self._record(cfg, message, run_id), role=cfg)
