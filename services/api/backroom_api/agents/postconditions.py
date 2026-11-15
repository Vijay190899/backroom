"""Postconditions: the code that decides whether a run succeeded.

`portal_state` asks the portal's admin endpoint, so a run can never "succeed" on looks
alone. `orders.last` only counts if the order list grew during the run (`baseline`), so an
order placed by an earlier run cannot satisfy a later one.
"""

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

from playwright.async_api import Page

from backroom_api.agents.portals_admin import PortalAdmin
from backroom_api.browser.executor import render
from backroom_api.skills.schema import Postcondition


@dataclass(frozen=True)
class PostResult:
    ok: bool
    detail: str


def _coerce(text: str) -> Any:
    try:
        return json.loads(text)
    except ValueError:
        return text


def _same(actual: Any, expected: Any) -> bool:
    if isinstance(actual, bool) or isinstance(expected, bool):
        return actual == expected
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return abs(float(actual) - float(expected)) < 1e-9
    return str(actual) == str(expected)


def walk(state: Mapping[str, Any], path: str, baseline_orders: int | None) -> Any:
    """Follow a dotted path. `last` is the final list element, and only valid if the list
    grew past `baseline_orders` (for `orders`)."""
    node: Any = state
    parts = path.split(".")
    for i, part in enumerate(parts):
        if isinstance(node, list):
            items: list[Any] = node  # type: ignore[assignment]
            if part == "last":
                if not items:
                    raise LookupError("the list is empty")
                grew = baseline_orders is None or len(items) > baseline_orders
                if parts[i - 1 : i] == ["orders"] and not grew:
                    raise LookupError("no new order appeared during this run")
                node = items[-1]
            else:
                node = items[int(part)]
        elif isinstance(node, dict):
            mapping: dict[str, Any] = node  # type: ignore[assignment]
            if part not in mapping:
                raise LookupError(f"no {part!r} in the portal state")
            node = mapping[part]
        else:
            raise LookupError(f"cannot read {part!r} from {node!r}")
    return node


async def check(
    post: Postcondition,
    params: Mapping[str, Any],
    *,
    page: Page,
    admin: PortalAdmin,
    portal: str,
    baseline_orders: int | None,
) -> PostResult:
    value = render(post.value, params)
    if post.kind == "url_matches":
        path = urlsplit(page.url).path
        ok = re.search(value, path) is not None
        return PostResult(ok, f"path {path!r} {'matches' if ok else 'does not match'} {value!r}")
    if post.kind == "text_visible":
        body = await page.inner_text("body")
        ok = value in body
        return PostResult(ok, f"text {value!r} {'is' if ok else 'is not'} on the page")
    expected = _coerce(render(post.equals, params)) if post.equals is not None else None
    try:
        actual = walk(await admin.state(portal), value, baseline_orders)
    except (LookupError, ValueError, IndexError) as exc:
        return PostResult(False, f"{value}: {exc}")
    ok = _same(actual, expected) if post.equals is not None else actual is not None
    return PostResult(ok, f"{value} = {actual!r}" + ("" if ok else f" (expected {expected!r})"))
