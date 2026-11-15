"""Secret vault: values live here and in the browser, never in prompts, events or logs.

A skill step names a secret as `{{secret:<key>}}`. Only `fill_secret` and `totp` steps may
use one (the skill schema enforces it); the executor asks the vault for the value at the
last moment and types it. Everything the executor reports goes through `redact`, which
replaces any secret value with `«secret:<key>»`, so even an error message that echoes an
input cannot leak one.
"""

import base64
import hashlib
import hmac
import re
import struct
import time
from collections.abc import Mapping

from backroom_api.config import Settings

_SECRET_RE = re.compile(r"\{\{secret:([a-z][a-z0-9_]*)\}\}")
_MIN_REDACT_LEN = 4  # shorter values would redact ordinary text; vault values are longer


class UnknownSecretError(KeyError):
    """The skill asks for a key the vault does not hold (the value itself is never named)."""


def default_totp_secret(data_seed: int) -> str:
    """Same rule as the portals (`backroom_portals.totp.default_secret`); a test pins the parity."""
    digest = hashlib.sha256(f"grainline-totp:{data_seed}".encode()).digest()
    return base64.b32encode(digest[:20]).decode()


def totp_code(secret: str, at: float | None = None) -> str:
    """RFC 6238: SHA-1, 30 s step, 6 digits."""
    key = base64.b32decode(secret.upper() + "=" * (-len(secret) % 8))
    counter = struct.pack(">Q", int((time.time() if at is None else at) // 30))
    mac = hmac.new(key, counter, hashlib.sha1).digest()
    offset = mac[-1] & 0x0F
    value = struct.unpack(">I", mac[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(value % 10**6).zfill(6)


class SecretVault:
    def __init__(self, secrets: Mapping[str, str]) -> None:
        self._secrets = {k: v for k, v in secrets.items() if v}

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> "SecretVault":
        s = settings or Settings()
        return cls(
            {
                "grainline_user": s.grainline_user,
                "grainline_password": s.grainline_password,
                "grainline_totp": s.grainline_totp_secret or default_totp_secret(s.data_seed),
                "tilldesk_user": s.tilldesk_user,
                "tilldesk_password": s.tilldesk_password,
            }
        )

    @staticmethod
    def key_of(template: str) -> str:
        """The key in `{{secret:key}}`; the whole template must be exactly one reference."""
        match = _SECRET_RE.fullmatch(template)
        if match is None:
            raise ValueError("expected a single {{secret:key}} reference")
        return match.group(1)

    def keys(self) -> list[str]:
        return sorted(self._secrets)

    def value(self, key: str) -> str:
        try:
            return self._secrets[key]
        except KeyError:
            raise UnknownSecretError(key) from None

    def resolve(self, template: str) -> str:
        """The text to type for a `fill_secret` template."""
        return self.value(self.key_of(template))

    def code(self, template: str) -> str:
        """The current one-time code for a `totp` template (the key holds the base32 secret)."""
        return totp_code(self.value(self.key_of(template)))

    def redact(self, text: str) -> str:
        """Replace every secret value (and any current one-time code) in `text`."""
        for key, secret in self._secrets.items():
            if len(secret) >= _MIN_REDACT_LEN:
                text = text.replace(secret, f"«secret:{key}»")
        totp_secret = self._secrets.get("grainline_totp")
        if totp_secret:
            for drift in (-30, 0, 30):
                text = text.replace(totp_code(totp_secret, time.time() + drift), "«totp»")
        return text
