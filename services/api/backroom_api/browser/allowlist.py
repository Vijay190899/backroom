"""Navigation allowlist: origin plus path prefix (docs/CONTRACTS.md §2).

One portals service serves three apps on one origin, so a run for Grainline may not wander
into `/tilldesk`. Documents are checked against origin and prefix. Sub-resources (images,
CSS, scripts) only need the origin. `data:`, `blob:` and `about:blank` are always allowed.
"""

from collections.abc import Iterable
from urllib.parse import urljoin, urlsplit

_ALWAYS = ("data:", "blob:", "about:blank")


class NavigationBlockedError(Exception):
    def __init__(self, url: str) -> None:
        super().__init__(f"navigation blocked by the allowlist: {url}")
        self.url = url


def _origin(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}".lower()


class Allowlist:
    def __init__(self, base_url: str, prefixes: Iterable[str]) -> None:
        self.base_url = base_url.rstrip("/")
        self._origin = _origin(self.base_url)
        self._prefixes = tuple(p.rstrip("/") or "/" for p in prefixes)

    @classmethod
    def for_portal(cls, base_url: str, portal: str) -> "Allowlist":
        return cls(base_url, [f"/{portal}"])

    def absolute(self, path_or_url: str) -> str:
        """Resolve a skill `goto` value (a path like `/grainline/cart`) against the base."""
        return urljoin(self.base_url + "/", path_or_url)

    def allows_document(self, url: str) -> bool:
        if url.startswith(_ALWAYS):
            return True
        if _origin(url) != self._origin:
            return False
        path = urlsplit(url).path
        return any(p == "/" or path == p or path.startswith(p + "/") for p in self._prefixes)

    def allows_resource(self, url: str) -> bool:
        return url.startswith(_ALWAYS) or _origin(url) == self._origin

    def check_document(self, url: str) -> str:
        if not self.allows_document(url):
            raise NavigationBlockedError(url)
        return url
