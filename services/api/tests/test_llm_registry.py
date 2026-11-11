import pytest

from backroom_api.config import Settings
from backroom_api.llm import registry


def make_settings(**overrides: object) -> Settings:
    return Settings(_env_file=None, **overrides)  # type: ignore[call-arg]


def test_openrouter_maps_canonical_ids() -> None:
    assert registry.wire_model_id("claude-haiku-5-5", "openrouter") == "anthropic/claude-haiku-5.5"
    assert (
        registry.wire_model_id("claude-sonnet-5-5", "openrouter") == "anthropic/claude-sonnet-5.5"
    )


def test_openrouter_passes_through_slash_ids() -> None:
    assert registry.wire_model_id("google/some-model", "openrouter") == "google/some-model"


def test_openrouter_rejects_unknown_canonical_id() -> None:
    with pytest.raises(ValueError, match="No OpenRouter mapping"):
        registry.wire_model_id("claude-nonexistent", "openrouter")


def test_anthropic_uses_canonical_ids_and_rejects_slash_ids() -> None:
    assert registry.wire_model_id("claude-haiku-5-5", "anthropic") == "claude-haiku-5-5"
    with pytest.raises(ValueError, match="OpenRouter model ID"):
        registry.wire_model_id("anthropic/claude-haiku-5.5", "anthropic")


def test_role_defaults() -> None:
    s = make_settings()
    worker = registry.role_config("worker", s)
    planner = registry.role_config("planner", s)
    assert (worker.model, worker.wire_model, worker.effort) == (
        "claude-haiku-5-5",
        "anthropic/claude-haiku-5.5",
        "low",
    )
    assert (planner.model, planner.effort) == ("claude-sonnet-5-5", "medium")
    for role in registry.ROLES:
        registry.role_config(role, s)  # every role resolves


def test_role_model_override_and_provider_switch() -> None:
    s = make_settings(llm_provider="anthropic", llm_planner_model="claude-opus-5-5")
    cfg = registry.role_config("planner", s)
    assert cfg.wire_model == "claude-opus-5-5"


def test_caps_defaults_and_overrides() -> None:
    assert registry.caps_for(make_settings()).server_fallbacks is False
    assert registry.caps_for(make_settings()).betas is False
    assert registry.caps_for(make_settings(llm_provider="anthropic")).server_fallbacks is True
    caps = registry.caps_for(make_settings(llm_caps_off="effort, strict_tools"))
    assert (caps.effort, caps.strict_tools, caps.prompt_cache) == (False, False, True)
    with pytest.raises(ValueError, match="unknown capabilities"):
        registry.caps_for(make_settings(llm_caps_off="telepathy"))


def test_cost_math() -> None:
    cost = registry.cost_usd(
        "claude-haiku-5-5",
        input_tokens=4_000,
        output_tokens=200,
        cache_read_tokens=10_000,
        cache_write_tokens=1_000,
    )
    expected = (4_000 * 0.10 + 200 * 0.50 + 10_000 * 0.01 + 1_000 * 0.125) / 1e6
    assert cost.priced and cost.usd == pytest.approx(expected)
    # OpenRouter IDs price the same as canonical IDs.
    via_or = registry.cost_usd(
        "anthropic/claude-sonnet-5.5", input_tokens=1_000_000, output_tokens=0
    )
    assert via_or.usd == pytest.approx(2.00)


def test_haiku_long_prompt_tier() -> None:
    cost = registry.cost_usd("claude-haiku-5-5", input_tokens=200_000, output_tokens=0)
    assert cost.usd == pytest.approx(200_000 * 0.50 / 1e6)


def test_unknown_model_is_unpriced() -> None:
    cost = registry.cost_usd("google/some-model", input_tokens=1_000, output_tokens=1_000)
    assert (cost.usd, cost.priced) == (0.0, False)


def test_client_requires_key() -> None:
    assert registry.is_configured(make_settings()) is False
    with pytest.raises(registry.LLMNotConfiguredError, match="OPENROUTER_API_KEY"):
        registry.build_async_client(make_settings())
    with pytest.raises(registry.LLMNotConfiguredError, match="ANTHROPIC_API_KEY"):
        registry.build_async_client(make_settings(llm_provider="anthropic"))


def test_openrouter_client_targets_openrouter(monkeypatch: pytest.MonkeyPatch) -> None:
    # A stray Anthropic key in the environment must not be sent to OpenRouter.
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-should-not-be-used")
    client = registry.build_async_client(make_settings(openrouter_api_key="sk-or-test"))
    assert str(client.base_url).rstrip("/") == "https://openrouter.ai/api"
    assert client.auth_token == "sk-or-test"
    assert client.api_key is None
    assert client.default_headers["X-Title"] == "Backroom"


def test_anthropic_client_uses_default_base_url() -> None:
    client = registry.build_async_client(
        make_settings(llm_provider="anthropic", anthropic_api_key="sk-ant-test")
    )
    assert "api.anthropic.com" in str(client.base_url)
    assert client.api_key == "sk-ant-test"
