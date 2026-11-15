"""Browser agent core (H2): pool, observation, executor, vault, allowlist, live view."""

from backroom_api.browser.allowlist import Allowlist, NavigationBlockedError
from backroom_api.browser.executor import Executor, StepOutcome, display_value
from backroom_api.browser.pool import BrowserPool
from backroom_api.browser.screencast import Frame, Screencast
from backroom_api.browser.snapshot import Element, Observation, observe, parse_snapshot
from backroom_api.browser.vault import SecretVault

__all__ = [
    "Allowlist",
    "BrowserPool",
    "Element",
    "Executor",
    "Frame",
    "NavigationBlockedError",
    "Observation",
    "Screencast",
    "SecretVault",
    "StepOutcome",
    "display_value",
    "observe",
    "parse_snapshot",
]
