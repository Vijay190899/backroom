"""Portal settings, read from the environment and the repo-root `.env`."""

from datetime import date
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from backroom_portals.totp import default_secret

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    portals_admin_token: str = "change-me"
    grainline_user: str = "lena@haferundbohne.example"
    grainline_password: str = "change-me"
    # Empty: derived from DATA_SEED (totp.default_secret), the same rule the agent's vault
    # uses until `pnpm seed` writes a generated secret to .env.
    grainline_totp_secret: str = ""
    tilldesk_user: str = "lena"
    tilldesk_password: str = "change-me"
    data_seed: int = 44
    # "Today" for prices, seeded history and delivery dates. None = the real date; tests pin it.
    portals_today: date | None = None

    @property
    def totp_secret(self) -> str:
        return self.grainline_totp_secret or default_secret(self.data_seed)

    @property
    def today(self) -> date:
        return self.portals_today or date.today()


@lru_cache
def get_settings() -> Settings:
    return Settings()
