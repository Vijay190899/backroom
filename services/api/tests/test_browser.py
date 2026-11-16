"""H2 browser tests: real Chromium against a local fixture page (PC only).

The laptop has no Chromium, so every test here skips when the browser is not installed.
"""

import asyncio
import logging
from typing import Any

import pytest
from playwright.async_api import Page

from backroom_api.browser import (
    Allowlist,
    BrowserPool,
    Executor,
    Frame,
    Screencast,
    SecretVault,
    observe,
)
from backroom_api.browser.vault import default_totp_secret
from backroom_api.skills.schema import Expect, Locator, Step
from backroom_portals import totp as portal_totp

PASSWORD = "hunter2-Secret!"


@pytest.fixture
def vault() -> SecretVault:
    return SecretVault(
        {
            "grainline_user": "lena@example.test",
            "grainline_password": PASSWORD,
            "grainline_totp": default_totp_secret(44),
        }
    )


def make_exec(page: Page, vault: SecretVault, base_url: str, **kw: Any) -> Executor:
    return Executor(page, vault, Allowlist(base_url, ["/shop.html"]), **kw)


def loc(role: str, name: str) -> Locator:
    return Locator(role=role, name=name)


def step(action: str, role: str | None = None, name: str | None = None, **kw: Any) -> Step:
    target = loc(role, name) if role and name else None
    return Step(intent=f"{action} {name or ''}".strip(), action=action, target=target, **kw)  # type: ignore[arg-type]


async def test_click_and_extract(page: Page, vault: SecretVault, base_url: str) -> None:
    ex = make_exec(page, vault, base_url)
    for _ in range(2):
        out = await ex.run(step("click", "button", "Add to cart"), {})
        assert out.ok and out.resolved_via == "target"
    read = await ex.run(step("extract", "status", "Item count"), {})
    assert read.ok and read.extracted == "2"


async def test_fill_select_and_press(page: Page, vault: SecretVault, base_url: str) -> None:
    ex = make_exec(page, vault, base_url)
    assert (
        await ex.run(
            step("fill", "textbox", "Username", value_template="{{user}}"), {"user": "lena"}
        )
    ).ok
    assert (await ex.run(step("select", "combobox", "Size", value_template="Large"), {})).ok
    assert await page.get_by_role("combobox", name="Size").input_value() == "l"
    secret = step(
        "fill_secret", "textbox", "Password", value_template="{{secret:grainline_password}}"
    )
    assert (await ex.run(secret, {})).ok
    submitted = await ex.run(step("press", "textbox", "Password", value_template="Enter"), {})
    assert submitted.ok
    assert f"signed in as lena (pw length {len(PASSWORD)})" in await page.inner_text("#status")


async def test_totp_fills_a_valid_code(page: Page, vault: SecretVault, base_url: str) -> None:
    ex = make_exec(page, vault, base_url)
    totp_step = step("totp", "textbox", "Username", value_template="{{secret:grainline_totp}}")
    assert (await ex.run(totp_step, {})).ok
    code = await page.get_by_role("textbox", name="Username").input_value()
    assert portal_totp.verify(default_totp_secret(44), code)


async def test_secrets_never_reach_outcomes_or_logs(
    page: Page, vault: SecretVault, base_url: str, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)
    ex = make_exec(page, vault, base_url)
    ok = await ex.run(
        step("fill_secret", "textbox", "Password", value_template="{{secret:grainline_password}}"),
        {},
    )
    assert PASSWORD not in repr(ok) and ok.extracted is None
    # A failure that would echo the secret (it equals the element name) is redacted.
    tricky = SecretVault({"grainline_password": "Nonexistent"})
    ex2 = make_exec(page, tricky, base_url)
    bad = await ex2.run(step("click", "button", "Nonexistent", timeout_ms=200), {})
    assert not bad.ok and bad.error is not None
    assert "Nonexistent" not in bad.error and "«hidden»" in bad.error
    assert PASSWORD not in caplog.text and "Nonexistent" not in caplog.text


async def test_fallback_and_not_found_and_ambiguous(
    page: Page, vault: SecretVault, base_url: str
) -> None:
    ex = make_exec(page, vault, base_url)
    via_fallback = step(
        "fill",
        "textbox",
        "Renamed field",
        value_template="x",
        fallbacks=[{"label": "Username"}],  # type: ignore[list-item]
    )
    out = await ex.run(via_fallback, {})
    assert out.ok and out.resolved_via == "fallback[0]"

    missing = await ex.run(step("click", "button", "Add to basket", timeout_ms=300), {})
    assert not missing.ok and missing.error_kind == "locator_not_found"
    assert "button 'Add to basket'" in (missing.error or "")

    twice = await ex.run(step("click", "link", "Cart", timeout_ms=300), {})  # nav and footer
    assert not twice.ok and twice.error_kind == "locator_ambiguous"


async def test_expect_passes_and_fails(page: Page, vault: SecretVault, base_url: str) -> None:
    ex = make_exec(page, vault, base_url)
    good = step("click", "button", "Add to cart", expect=Expect(text="Items: 1"))
    assert (await ex.run(good, {})).ok
    bad = step("click", "button", "Add to cart", timeout_ms=300, expect=Expect(text="Items: 9"))
    out = await ex.run(bad, {})
    assert not out.ok and out.error_kind == "expect_failed"
    url_ok = step("wait_for", "button", "Add to cart", expect=Expect(url_pattern=r"^/shop\.html$"))
    assert (await ex.run(url_ok, {})).ok


async def test_wait_for_follows_aria_busy(page: Page, vault: SecretVault, base_url: str) -> None:
    ex = make_exec(page, vault, base_url)
    assert (await ex.run(step("click", "button", "Load later"), {})).ok
    waited = await ex.run(step("wait_for", value_template="Loaded"), {})
    assert waited.ok


async def test_allowlist_blocks_goto_and_link_navigation(
    page: Page, vault: SecretVault, base_url: str
) -> None:
    ex = make_exec(page, vault, base_url)
    out = await ex.run(step("goto", value_template="/forbidden.html"), {})
    assert not out.ok and out.error_kind == "blocked"
    # A click on an out-of-scope link is stopped at the request level and reported.
    clicked = await ex.run(step("click", "link", "Forbidden"), {})
    assert not clicked.ok and clicked.error_kind == "blocked"
    assert "forbidden.html" not in await page.content()


async def test_cursor_callback_reports_element_centres(
    page: Page, vault: SecretVault, base_url: str
) -> None:
    seen: list[tuple[float, float]] = []

    async def on_cursor(x: float, y: float) -> None:
        seen.append((x, y))

    ex = make_exec(page, vault, base_url, on_cursor=on_cursor)
    await ex.run(step("click", "button", "Add to cart"), {})
    assert len(seen) == 1 and 0 < seen[0][0] < 1280 and 0 < seen[0][1] < 800


async def test_observe_gives_refs_the_page_accepts(page: Page) -> None:
    obs = await observe(page)
    buttons = obs.find("button", "Add to cart")
    assert len(buttons) == 1 and not obs.truncated
    await page.locator(f"aria-ref={buttons[0].ref}").click()
    assert await page.inner_text("#count") == "1"
    short = await observe(page, max_chars=80)
    assert short.truncated and "truncated:" in short.text and "use `find`" in short.text
    assert "Add to cart" in short.full and len(short.full) > len(short.text)  # find searches it


async def test_contexts_are_isolated_and_limited(pool: BrowserPool, base_url: str) -> None:
    allow = Allowlist(base_url, ["/shop.html"])
    async with pool.session(allow) as a:
        await a.goto(f"{base_url}/shop.html")
        await a.evaluate("document.cookie = 'seen=1'")
    async with pool.session(allow) as b:
        await b.goto(f"{base_url}/shop.html")
        assert await b.evaluate("document.cookie") == ""

    small = BrowserPool(max_contexts=1)
    running = peak = 0

    async def work() -> None:
        nonlocal running, peak
        async with small.session(allow) as p:
            running += 1
            peak = max(peak, running)
            await p.goto(f"{base_url}/shop.html")
            await asyncio.sleep(0.15)
            running -= 1

    try:
        await asyncio.gather(work(), work())
    finally:
        await small.close()
    assert peak == 1


async def test_screencast_delivers_jpeg_frames(page: Page) -> None:
    frames: list[Frame] = []
    got = asyncio.Event()

    async def on_frame(frame: Frame) -> None:
        frames.append(frame)
        got.set()

    cast = Screencast(page, on_frame)
    await cast.start()
    await page.get_by_role("button", name="Add to cart").click()
    await asyncio.wait_for(got.wait(), timeout=5)
    await cast.stop()
    assert frames[0].jpeg[:2] == b"\xff\xd8" and frames[0].width > 0
    assert [f.seq for f in frames] == list(range(1, len(frames) + 1))
