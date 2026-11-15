"""RFC 6238 TOTP (SHA-1, 30 s, 6 digits), the scheme authenticator apps use."""

import base64
import hashlib
import hmac
import re
import struct
import time

STEP_S = 30
DIGITS = 6


def default_secret(data_seed: int) -> str:
    """Deterministic base32 secret for local runs without a seeded GRAINLINE_TOTP_SECRET."""
    digest = hashlib.sha256(f"grainline-totp:{data_seed}".encode()).digest()
    return base64.b32encode(digest[:20]).decode()


def code_at(secret: str, at: float) -> str:
    key = base64.b32decode(secret.upper() + "=" * (-len(secret) % 8))
    counter = struct.pack(">Q", int(at // STEP_S))
    mac = hmac.new(key, counter, hashlib.sha1).digest()
    offset = mac[-1] & 0x0F
    value = struct.unpack(">I", mac[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(value % 10**DIGITS).zfill(DIGITS)


def now_code(secret: str) -> str:
    return code_at(secret, time.time())


def verify(secret: str, code: str, at: float | None = None, window: int = 1) -> bool:
    """True if `code` matches the current step or one step either side (clock drift)."""
    at = time.time() if at is None else at
    code = code.strip().replace(" ", "")
    if not re.fullmatch(r"[0-9]{6}", code, flags=re.ASCII):
        return False
    return any(
        hmac.compare_digest(code_at(secret, at + drift * STEP_S).encode(), code.encode())
        for drift in range(-window, window + 1)
    )


if __name__ == "__main__":
    # For signing in by hand: `uv run python -m backroom_portals.totp`
    from backroom_portals.config import get_settings

    secret = get_settings().totp_secret
    print(f"secret {secret}\ncode   {now_code(secret)}  (valid ~30 s)")
