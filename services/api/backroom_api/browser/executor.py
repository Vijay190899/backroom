"""Step executor: performs one skill `Step` on a page.

It is the only code that touches the page for a replay, and the one the explore loop calls
for each model-chosen action, so both modes behave identically. It never raises for an
expected failure (missing element, failed expectation, blocked URL): it returns a
`StepOutcome` whose `error_kind` tells the heal ladder what went wrong. Anything it reports
goes through the vault's `redact`.

Locator order is the skill contract: `target` (ARIA role + exact accessible name), then the
`fallbacks` in order. A step that only worked through a fallback says so in `resolved_via`;
the healer promotes it into the target (heal rung 1).
"""

import asyncio
import re
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Literal
from urllib.parse import urlsplit

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Locator, Page

from backroom_api.browser.allowlist import Allowlist, NavigationBlockedError
from backroom_api.browser.snapshot import wait_until_idle
from backroom_api.browser.vault import SecretVault, UnknownSecretError
from backroom_api.skills.schema import (
    CssFallback,
    Expect,
    Fallback,
    LabelFallback,
    Step,
    TextFallback,
)
from backroom_api.skills.schema import (
    Locator as SkillLocator,
)

ErrorKind = Literal[
    "locator_not_found",  # nothing matched: the heal ladder's main trigger
    "locator_ambiguous",  # several matched and no fallback was unique
    "expect_failed",  # the action ran but the page is not where the step said it would be
    "blocked",  # the allowlist refused a URL
    "action_failed",  # Playwright could not perform the action (timeout, not actionable)
    "bad_step",  # the step cannot be run (missing param or secret)
]
CursorCallback = Callable[[float, float], Awaitable[None]]
_PARAM_RE = re.compile(r"\{\{([a-z][a-z0-9_]*)\}\}")
_POLL_S = 0.1


class StepError(Exception):
    def __init__(self, kind: ErrorKind, message: str) -> None:
        super().__init__(message)
        self.kind: ErrorKind = kind


@dataclass(frozen=True)
class StepOutcome:
    ok: bool
    duration_ms: int
    error_kind: ErrorKind | None = None
    error: str | None = None
    resolved_via: str | None = None  # "target", "fallback[0]", ...; None if no locator was used
    extracted: str | None = None
    detail: dict[str, Any] = field(default_factory=dict[str, Any])


def render(template: str, params: Mapping[str, Any]) -> str:
    """Fill `{{param}}` placeholders. Secret references are not handled here."""

    def sub(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in params:
            raise StepError("bad_step", f"missing param {name!r}")
        return str(params[name])

    return _PARAM_RE.sub(sub, template)


def display_value(step: Step, params: Mapping[str, Any]) -> str | None:
    """The `value` for a `step.started` event: never a secret, `None` instead."""
    if step.action in ("fill_secret", "totp") or step.value_template is None:
        return None
    return render(step.value_template, params)


def describe(target: SkillLocator | None, fallbacks: list[Fallback]) -> str:
    if target is not None:
        return f"{target.role} {target.name!r}"
    if fallbacks:
        first = fallbacks[0]
        return f"fallback {first.model_dump(exclude_none=True)}"
    return "page"


class Executor:
    def __init__(
        self,
        page: Page,
        vault: SecretVault,
        allowlist: Allowlist,
        on_cursor: CursorCallback | None = None,
    ) -> None:
        self.page = page
        self.vault = vault
        self.allowlist = allowlist
        self._on_cursor = on_cursor

    # --- locating -------------------------------------------------------------------------

    def _candidates(
        self, target: SkillLocator | None, fallbacks: list[Fallback]
    ) -> list[tuple[str, Locator]]:
        found: list[tuple[str, Locator]] = []
        if target is not None:
            found.append(
                ("target", self.page.get_by_role(target.role, name=target.name, exact=True))  # type: ignore[arg-type]
            )
        for i, fb in enumerate(fallbacks):
            if isinstance(fb, LabelFallback):
                loc = self.page.get_by_label(fb.label, exact=True)
            elif isinstance(fb, TextFallback):
                loc = self.page.get_by_text(fb.text, exact=True)
            elif isinstance(fb, CssFallback):
                loc = self.page.locator(fb.css)
            else:  # pragma: no cover - the union is closed
                continue
            found.append((f"fallback[{i}]", loc))
        return found

    async def resolve(
        self, target: SkillLocator | None, fallbacks: list[Fallback], timeout_ms: int
    ) -> tuple[Locator, str]:
        """The first candidate that matches exactly one element, waiting up to `timeout_ms`
        for a slow page. Raises `StepError` (not found / ambiguous)."""
        candidates = self._candidates(target, fallbacks)
        deadline = time.monotonic() + timeout_ms / 1000
        await wait_until_idle(self.page, timeout_ms=min(timeout_ms, 3_000))
        ambiguous: str | None = None
        while True:
            for via, loc in candidates:
                try:
                    count = await loc.count()
                except PlaywrightError:
                    continue  # the page navigated under us; look again
                if count == 1:
                    return loc, via
                if count > 1:
                    ambiguous = via
            if time.monotonic() >= deadline:
                break
            await asyncio.sleep(_POLL_S)
        what = describe(target, fallbacks)
        if ambiguous is not None:
            raise StepError("locator_ambiguous", f"several elements match {what} ({ambiguous})")
        raise StepError("locator_not_found", f"locator not found: {what}")

    async def _move_cursor(self, loc: Locator) -> None:
        if self._on_cursor is None:
            return
        try:
            box = await loc.bounding_box(timeout=500)
        except PlaywrightError:
            return
        if box is not None:
            await self._on_cursor(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)

    # --- running a step -------------------------------------------------------------------

    async def run(self, step: Step, params: Mapping[str, Any]) -> StepOutcome:
        started = time.monotonic()
        via: str | None = None
        extracted: str | None = None
        try:
            via, extracted = await self._perform(step, params)
            await wait_until_idle(self.page, timeout_ms=min(step.timeout_ms, 3_000))
            if self.page.url.startswith("chrome-error://"):
                # The request guard aborted a navigation (or the portal is unreachable).
                raise StepError(
                    "blocked", "navigation failed: blocked by the allowlist or unreachable"
                )
            if step.expect is not None:
                await self._check_expect(step.expect, step.timeout_ms)
        except StepError as exc:
            return self._fail(started, exc.kind, str(exc), via)
        except NavigationBlockedError as exc:
            return self._fail(started, "blocked", str(exc), via)
        except UnknownSecretError as exc:
            return self._fail(started, "bad_step", f"unknown secret {exc.args[0]!r}", via)
        except PlaywrightError as exc:
            first_line = (
                str(exc).strip().splitlines()[0] if str(exc).strip() else "playwright error"
            )
            return self._fail(started, "action_failed", first_line, via)
        return StepOutcome(
            ok=True,
            duration_ms=int((time.monotonic() - started) * 1000),
            resolved_via=via,
            extracted=extracted,
        )

    def _fail(self, started: float, kind: ErrorKind, message: str, via: str | None) -> StepOutcome:
        return StepOutcome(
            ok=False,
            duration_ms=int((time.monotonic() - started) * 1000),
            error_kind=kind,
            error=self.vault.redact(message),
            resolved_via=via,
        )

    async def _perform(
        self, step: Step, params: Mapping[str, Any]
    ) -> tuple[str | None, str | None]:
        action = step.action
        timeout = step.timeout_ms
        if action == "goto":
            assert step.value_template is not None
            url = self.allowlist.check_document(
                self.allowlist.absolute(render(step.value_template, params))
            )
            await self.page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            return None, None
        if action == "press" and step.target is None and not step.fallbacks:
            assert step.value_template is not None
            await self.page.keyboard.press(render(step.value_template, params))
            return None, None
        if action == "wait_for" and step.target is None and not step.fallbacks:
            if step.value_template:
                text = render(step.value_template, params)
                await self.page.get_by_text(text).first.wait_for(state="visible", timeout=timeout)
            return None, None
        if action == "extract" and step.target is None and not step.fallbacks:
            return None, await self.page.inner_text("body", timeout=timeout)

        loc, via = await self.resolve(step.target, step.fallbacks, timeout)
        if action == "wait_for":
            await loc.wait_for(state="visible", timeout=timeout)
            return via, None
        if action == "extract":
            return via, await loc.inner_text(timeout=timeout)
        await self._move_cursor(loc)
        if action == "click":
            await loc.click(timeout=timeout)
        elif action == "fill":
            assert step.value_template is not None
            await loc.fill(render(step.value_template, params), timeout=timeout)
        elif action == "fill_secret":
            assert step.value_template is not None
            await loc.fill(self.vault.resolve(step.value_template), timeout=timeout)
        elif action == "totp":
            assert step.value_template is not None
            await loc.fill(self.vault.code(step.value_template), timeout=timeout)
        elif action == "select":
            assert step.value_template is not None
            choice = render(step.value_template, params)
            try:
                await loc.select_option(label=choice, timeout=timeout)
            except PlaywrightError:
                await loc.select_option(value=choice, timeout=timeout)
        elif action == "press":
            assert step.value_template is not None
            await loc.press(render(step.value_template, params), timeout=timeout)
        return via, None

    # --- expectations ---------------------------------------------------------------------

    async def _check_expect(self, expect: Expect, timeout_ms: int) -> None:
        deadline = time.monotonic() + timeout_ms / 1000
        last = "expectation not met"
        while True:
            last = await self._first_unmet(expect) or ""
            if not last:
                return
            if time.monotonic() >= deadline:
                raise StepError("expect_failed", last)
            await asyncio.sleep(_POLL_S)

    async def _first_unmet(self, expect: Expect) -> str | None:
        if expect.url_pattern is not None:
            path = urlsplit(self.page.url).path
            if re.search(expect.url_pattern, path) is None:
                return f"expected the path to match {expect.url_pattern!r}, got {path!r}"
        if expect.visible is not None:
            loc = self.page.get_by_role(
                expect.visible.role,  # type: ignore[arg-type]
                name=expect.visible.name,
                exact=True,
            )
            try:
                if await loc.count() < 1 or not await loc.first.is_visible():
                    return f"expected {expect.visible.role} {expect.visible.name!r} to be visible"
            except PlaywrightError:
                return "the page changed while checking"
        if expect.text is not None:
            try:
                body = await self.page.inner_text("body", timeout=500)
            except PlaywrightError:
                return "the page changed while checking"
            if expect.text not in body:
                return f"expected the text {expect.text!r} on the page"
        return None
