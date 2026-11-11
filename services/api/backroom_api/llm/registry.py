"""Single source of truth for LLM providers, models, capabilities and prices.

Nothing outside this module may construct an SDK client or name a model ID.
See docs/ARCHITECTURE.md §5.
"""

from dataclasses import dataclass, fields, replace
from typing import Literal, get_args

import anthropic

from backroom_api.config import Effort, Provider, Settings

Role = Literal["planner", "worker", "verifier", "heal", "escalation", "ask"]
ROLES: tuple[Role, ...] = get_args(Role)

OPENROUTER_BASE_URL = "https://openrouter.ai/api"

# Canonical model ID -> OpenRouter model ID.
OPENROUTER_MODEL_IDS: dict[str, str] = {
    "claude-haiku-5-5": "anthropic/claude-haiku-5.5",
    "claude-sonnet-5-5": "anthropic/claude-sonnet-5.5",
    "claude-opus-5-5": "anthropic/claude-opus-5.5",
    "claude-fable-5-2": "anthropic/claude-fable-5.2",
}
_CANONICAL_BY_OPENROUTER_ID = {v: k for k, v in OPENROUTER_MODEL_IDS.items()}


class LLMNotConfiguredError(RuntimeError):
    """The active provider has no API key."""


@dataclass(frozen=True)
class Price:
    """USD per 1M tokens."""

    input: float
    output: float
    cache_read: float
    cache_write: float


# Anthropic first-party rates (cached 2026-11-03); OpenRouter lists the same rates
# (checked 2026-11-11). Cache writes are 1.25x input (5-minute TTL).
PRICES: dict[str, Price] = {
    "claude-haiku-5-5": Price(0.10, 0.50, 0.01, 0.125),
    "claude-sonnet-5-5": Price(2.00, 10.00, 0.10, 2.50),
    "claude-opus-5-5": Price(4.00, 20.00, 0.20, 5.00),
    "claude-fable-5-2": Price(8.00, 40.00, 0.20, 10.00),
}
# Haiku 5.5 charges a higher tier for prompts above 100K tokens.
_HAIKU_LONG_PROMPT_TOKENS = 100_000
_HAIKU_LONG_PROMPT_MULTIPLIER = 5.0


@dataclass(frozen=True)
class Caps:
    """What the active provider supports. Call sites check these flags; they never
    branch on the provider name."""

    effort: bool
    strict_tools: bool
    structured_outputs: bool
    prompt_cache: bool
    streaming: bool
    server_fallbacks: bool
    betas: bool


_DEFAULT_CAPS: dict[Provider, Caps] = {
    "anthropic": Caps(
        effort=True,
        strict_tools=True,
        structured_outputs=True,
        prompt_cache=True,
        streaming=True,
        server_fallbacks=True,
        betas=True,
    ),
    # OpenRouter's Anthropic-compatible endpoint. Beta headers are off; the other
    # flags are confirmed (or switched off via LLM_CAPS_OFF) by `pnpm probe:llm`.
    "openrouter": Caps(
        effort=True,
        strict_tools=True,
        structured_outputs=True,
        prompt_cache=True,
        streaming=True,
        server_fallbacks=False,
        betas=False,
    ),
}
CAP_NAMES = tuple(f.name for f in fields(Caps))


def caps_for(settings: Settings) -> Caps:
    caps = _DEFAULT_CAPS[settings.llm_provider]
    off = {name.strip() for name in settings.llm_caps_off.split(",") if name.strip()}
    unknown = off - set(CAP_NAMES)
    if unknown:
        raise ValueError(f"LLM_CAPS_OFF names unknown capabilities: {sorted(unknown)}")
    return replace(caps, **{name: False for name in off})


def wire_model_id(model: str, provider: Provider) -> str:
    """Map a canonical model ID to the ID the provider expects."""
    if provider == "anthropic":
        if "/" in model:
            raise ValueError(f"{model!r} is an OpenRouter model ID; LLM_PROVIDER is 'anthropic'")
        return model
    if "/" in model:  # already an OpenRouter ID (e.g. a non-Claude model for B4)
        return model
    try:
        return OPENROUTER_MODEL_IDS[model]
    except KeyError:
        raise ValueError(f"No OpenRouter mapping for model {model!r}") from None


def canonical_model_id(model: str) -> str:
    return _CANONICAL_BY_OPENROUTER_ID.get(model, model)


@dataclass(frozen=True)
class RoleConfig:
    role: Role
    model: str  # canonical
    wire_model: str  # what is sent to the provider
    effort: Effort


def role_config(role: Role, settings: Settings) -> RoleConfig:
    model: str = getattr(settings, f"llm_{role}_model")
    effort: Effort = getattr(settings, f"llm_{role}_effort")
    return RoleConfig(
        role=role,
        model=canonical_model_id(model),
        wire_model=wire_model_id(model, settings.llm_provider),
        effort=effort,
    )


def is_configured(settings: Settings) -> bool:
    if settings.llm_provider == "openrouter":
        return bool(settings.openrouter_api_key)
    return bool(settings.anthropic_api_key)


def build_async_client(settings: Settings) -> anthropic.AsyncAnthropic:
    """The only place an SDK client is constructed."""
    if not is_configured(settings):
        key_name = (
            "OPENROUTER_API_KEY" if settings.llm_provider == "openrouter" else "ANTHROPIC_API_KEY"
        )
        raise LLMNotConfiguredError(
            f"LLM_PROVIDER={settings.llm_provider} but {key_name} is not set (see .env.example)"
        )
    if settings.llm_provider == "openrouter":
        # Passing auth_token explicitly means the SDK ignores ANTHROPIC_* env credentials.
        return anthropic.AsyncAnthropic(
            base_url=OPENROUTER_BASE_URL,
            auth_token=settings.openrouter_api_key,
            default_headers={
                "X-Title": settings.openrouter_app_name,
                "HTTP-Referer": settings.openrouter_site_url,
            },
        )
    return anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


@dataclass(frozen=True)
class Cost:
    usd: float
    priced: bool  # False when the model has no entry in PRICES


def cost_usd(
    model: str,
    *,
    input_tokens: int,
    output_tokens: int,
    cache_read_tokens: int = 0,
    cache_write_tokens: int = 0,
) -> Cost:
    """Cost of one call. `input_tokens` excludes cached tokens, as in the API's usage."""
    price = PRICES.get(canonical_model_id(model))
    if price is None:
        return Cost(usd=0.0, priced=False)
    prompt_tokens = input_tokens + cache_read_tokens + cache_write_tokens
    multiplier = (
        _HAIKU_LONG_PROMPT_MULTIPLIER
        if canonical_model_id(model) == "claude-haiku-5-5"
        and prompt_tokens > _HAIKU_LONG_PROMPT_TOKENS
        else 1.0
    )
    usd = (
        input_tokens * price.input
        + output_tokens * price.output
        + cache_read_tokens * price.cache_read
        + cache_write_tokens * price.cache_write
    ) * multiplier / 1_000_000
    return Cost(usd=usd, priced=True)
