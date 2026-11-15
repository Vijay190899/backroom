"""H2 unit tests: vault, allowlist and snapshot parsing. No browser needed."""

import pytest

from backroom_api.browser.allowlist import Allowlist, NavigationBlockedError
from backroom_api.browser.snapshot import parse_snapshot
from backroom_api.browser.vault import (
    SecretVault,
    UnknownSecretError,
    default_totp_secret,
    totp_code,
)
from backroom_api.skills.schema import LabelFallback, Step
from backroom_portals import totp as portal_totp

SNAPSHOT = """\
- generic [active] [ref=e1]:
  - navigation "Main" [ref=e3]:
    - link "Cart" [ref=e4] [cursor=pointer]:
      - /url: "#cart"
  - main [ref=e6]:
    - heading "Fixture shop" [level=1] [ref=e7]
    - textbox "Username" [ref=e9]
    - combobox "Size" [ref=e11]:
      - option "Small" [selected]
    - button "Say \\"hi\\"" [ref=e12]
    - status
"""


def test_totp_matches_the_portals_implementation() -> None:
    secret = default_totp_secret(44)
    assert secret == portal_totp.default_secret(44)
    for at in (0.0, 59.0, 1_700_000_000.0):
        assert totp_code(secret, at) == portal_totp.code_at(secret, at)


def test_vault_resolves_and_redacts() -> None:
    vault = SecretVault({"grainline_password": "hunter2-Secret!", "grainline_user": ""})
    assert vault.resolve("{{secret:grainline_password}}") == "hunter2-Secret!"
    assert vault.keys() == ["grainline_password"]  # empty values are not secrets
    redacted = vault.redact("typed hunter2-Secret! into the form")
    assert "hunter2" not in redacted and "«secret:grainline_password»" in redacted
    with pytest.raises(UnknownSecretError):
        vault.resolve("{{secret:tilldesk_password}}")
    with pytest.raises(ValueError):
        vault.resolve("prefix {{secret:grainline_password}}")


def test_vault_redacts_current_one_time_codes() -> None:
    secret = default_totp_secret(44)
    vault = SecretVault({"grainline_totp": secret})
    code = vault.code("{{secret:grainline_totp}}")
    assert portal_totp.verify(secret, code)
    assert code not in vault.redact(f"code was {code}")


def test_secret_steps_carry_no_value_in_events() -> None:
    from backroom_api.browser.executor import display_value

    secret_step = Step(
        intent="Type the password",
        action="fill_secret",
        fallbacks=[LabelFallback(label="Password")],
        value_template="{{secret:grainline_password}}",
    )
    assert display_value(secret_step, {}) is None
    plain = Step(
        intent="Type",
        action="fill",
        fallbacks=[LabelFallback(label="Qty")],
        value_template="{{qty}}",
    )  # type: ignore[list-item]
    assert display_value(plain, {"qty": 24}) == "24"


def test_allowlist_is_origin_plus_path_prefix() -> None:
    allow = Allowlist.for_portal("http://localhost:8001", "grainline")
    assert allow.allows_document("http://localhost:8001/grainline")
    assert allow.allows_document("http://localhost:8001/grainline/cart?x=1")
    assert not allow.allows_document(
        "http://localhost:8001/grainlinex"
    )  # not a prefix of a segment
    assert not allow.allows_document("http://localhost:8001/tilldesk/menu")
    assert not allow.allows_document("http://evil.example/grainline")
    assert not allow.allows_document("http://localhost:9999/grainline")
    assert allow.allows_document("about:blank")
    # sub-resources need only the origin (shared CSS and fonts live outside the prefix)
    assert allow.allows_resource("http://localhost:8001/static/app.css")
    assert not allow.allows_resource("https://cdn.example/x.js")
    assert allow.absolute("/grainline/cart") == "http://localhost:8001/grainline/cart"
    with pytest.raises(NavigationBlockedError):
        allow.check_document("http://localhost:8001/tilldesk")


def test_parse_snapshot_extracts_roles_names_and_refs() -> None:
    elements = parse_snapshot(SNAPSHOT)
    by_ref = {e.ref: (e.role, e.name) for e in elements}
    assert by_ref["e4"] == ("link", "Cart")
    assert by_ref["e7"] == ("heading", "Fixture shop")
    assert by_ref["e12"] == ("button", 'Say "hi"')  # escapes decode
    assert "e1" in by_ref and by_ref["e1"][1] == ""  # nameless containers still have refs
    assert all(e.ref.startswith("e") for e in elements)
    assert len(elements) == 8  # the url line, the option and the ref-less status are skipped


def test_parse_snapshot_accepts_frame_prefixed_refs() -> None:
    # After a navigation Playwright prefixes refs with the frame ("f1e4"); the real Grainline
    # login page showed this, and an `e\d+`-only pattern found no elements on any later page.
    page2 = (
        '- textbox "Authentication code" [ref=f1e8]\n'
        '- button "Verify" [ref=f12e10] [cursor=pointer]\n'
    )
    assert [(e.ref, e.name) for e in parse_snapshot(page2)] == [
        ("f1e8", "Authentication code"),
        ("f12e10", "Verify"),
    ]
