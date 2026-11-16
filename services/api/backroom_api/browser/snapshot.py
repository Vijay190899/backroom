"""Observation: what the agent sees of a page.

The agent never sees HTML. It sees Playwright's AI-mode ARIA snapshot, a compact outline of
roles and accessible names with a short `ref` per element (`button "Sign in" [ref=e12]`).
`data-testid`s are not in it (docs/CONTRACTS.md §2), so a skill can only be built from
role + name, which is exactly what survives a re-skin.

Before each snapshot we wait until no `[aria-busy]` element is left: a chaos-delayed page
shows a "Loading..." skeleton for up to 1.5 s (CONTRACTS §3, rule 2).
"""

import contextlib
import json
import re
from dataclasses import dataclass

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page

_LINE_RE = re.compile(
    r'^\s*- (?P<role>[a-z]+)(?: "(?P<name>(?:[^"\\]|\\.)*)")?(?P<attrs>(?: \[[^\]]+\])*)'
)
_REF_RE = re.compile(r"\[ref=([A-Za-z0-9]+)\]")  # "e12", or "f1e12" after a navigation
_NOT_BUSY_JS = "() => !document.querySelector('[aria-busy]:not([aria-busy=\"false\"])')"
DEFAULT_MAX_CHARS = 12_000  # about 3k tokens: enough for a portal page, cheap to repeat


@dataclass(frozen=True)
class Element:
    ref: str
    role: str
    name: str


@dataclass(frozen=True)
class Observation:
    url: str
    title: str
    text: str  # the snapshot, possibly truncated (what goes into a prompt)
    full: str  # the whole snapshot (for `find`)
    elements: tuple[Element, ...]
    truncated: bool

    def find(self, role: str, name: str) -> list[Element]:
        return [e for e in self.elements if e.role == role and e.name == name]


def parse_snapshot(snapshot: str) -> tuple[Element, ...]:
    """Every element that has a ref, in document order."""
    found: list[Element] = []
    for line in snapshot.splitlines():
        match = _LINE_RE.match(line)
        if match is None:
            continue
        ref = _REF_RE.search(match.group("attrs") or "")
        if ref is None:
            continue
        raw = match.group("name")
        name = json.loads(f'"{raw}"') if raw is not None else ""
        found.append(Element(ref=ref.group(1), role=match.group("role"), name=name))
    return tuple(found)


async def wait_until_idle(page: Page, timeout_ms: int = 3_000) -> None:
    """Wait for aria-busy to clear. A page that never settles is observed as it is."""
    with contextlib.suppress(PlaywrightError):
        await page.wait_for_function(_NOT_BUSY_JS, timeout=timeout_ms)


async def observe(page: Page, max_chars: int = DEFAULT_MAX_CHARS) -> Observation:
    await wait_until_idle(page)
    snapshot = await page.aria_snapshot(mode="ai")
    truncated = len(snapshot) > max_chars
    return Observation(
        url=page.url,
        title=await page.title(),
        text=snapshot[:max_chars]
        + (
            f"\n... (truncated: {len(snapshot) - max_chars:,} more characters; "
            "use `find` to search them)"
            if truncated
            else ""
        ),
        full=snapshot,
        elements=parse_snapshot(snapshot),
        truncated=truncated,
    )
