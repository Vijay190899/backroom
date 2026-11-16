"""Runtime settings, read from the environment and the repo-root `.env`."""

from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]

Provider = Literal["openrouter", "anthropic"]
Effort = Literal["low", "medium", "high", "xhigh", "max"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- LLM provider ---
    llm_provider: Provider = "openrouter"
    openrouter_api_key: str = ""
    openrouter_app_name: str = "Backroom"
    openrouter_site_url: str = "https://github.com/Vijay190899/backroom"
    openrouter_fee_pct: float = 5.5
    anthropic_api_key: str = ""
    # Comma-separated capability flags to switch off for the active provider
    # (set from the results of `pnpm probe:llm`), e.g. "effort,strict_tools".
    llm_caps_off: str = ""

    # --- Model roles (canonical IDs; mapped per provider by llm/registry.py) ---
    llm_planner_model: str = "claude-sonnet-5-5"
    llm_planner_effort: Effort = "medium"
    llm_worker_model: str = "claude-haiku-5-5"
    llm_worker_effort: Effort = "low"
    llm_verifier_model: str = "claude-haiku-5-5"
    llm_verifier_effort: Effort = "low"
    llm_heal_model: str = "claude-haiku-5-5"
    llm_heal_effort: Effort = "low"
    llm_escalation_model: str = "claude-sonnet-5-5"
    llm_escalation_effort: Effort = "medium"
    llm_ask_model: str = "claude-sonnet-5-5"
    llm_ask_effort: Effort = "low"

    # --- Guards ---
    llm_daily_budget_usd: float = 3.0
    llm_ledger_path: Path = REPO_ROOT / "var" / "llm_ledger.jsonl"
    explore_max_steps: int = 25
    explore_max_usd: float = 0.05
    run_max_usd: float = 0.25  # a run that heals stops (and asks a human) beyond this
    demo_access_code: str = "change-me"
    demo_mode: Literal["live", "replay"] = "live"
    # Requests per client IP per minute (backroom_api/ratelimit.py); 0 switches a limit off.
    rate_limit_read_per_min: int = 240
    rate_limit_write_per_min: int = 30

    # --- Infra ---
    database_url: str = "postgresql://backroom:backroom@localhost:5432/backroom"
    portals_base_url: str = "http://localhost:8001"
    portals_admin_token: str = "change-me"
    web_origin: str = "http://localhost:3000"
    data_dir: Path = REPO_ROOT / "data" / "out"
    golden_dir: Path = (
        REPO_ROOT / "apps" / "web" / "public" / "golden"
    )  # recorded runs (F7)  # what `pnpm seed` builds; the brief reads it

    # --- Portal credentials (the secret vault's source; same variables the portals read) ---
    grainline_user: str = "lena@haferundbohne.example"
    grainline_password: str = "change-me"
    grainline_totp_secret: str = ""  # empty: derived from DATA_SEED, as the portals do
    tilldesk_user: str = "lena"
    tilldesk_password: str = "change-me"
    data_seed: int = 44
    # The portals' "today" (same variable they read); None = the real date. Undo checks
    # Grainline's cancellation cutoff against it.
    portals_today: date | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
