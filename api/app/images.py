"""Fetch a NASA GIBS picture for a browser that cannot read GIBS itself.

This is not an open proxy. The host and the path have to be GIBS map
service. A request for any other address is rejected before we connect.
"""

from __future__ import annotations

from urllib.parse import unquote, urlsplit

import httpx

GIBS_HOST = "gibs.earthdata.nasa.gov"
MAX_BYTES = 8_000_000
_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}


class GibsUrlError(ValueError):
    """The caller asked for something other than a GIBS map picture."""


class ImageFetchError(RuntimeError):
    """GIBS did not return a picture we can pass on."""


def require_gibs_url(url: str) -> str:
    """Return the URL when it is an https GIBS WMS or WMTS picture."""

    candidate = url.strip()
    parsed = urlsplit(candidate)
    if parsed.scheme == "" and "%" in candidate:
        candidate = unquote(candidate)
        parsed = urlsplit(candidate)
    host = (parsed.hostname or "").lower()
    path = parsed.path or ""
    if (
        parsed.scheme != "https"
        or parsed.username
        or parsed.password
        or parsed.port not in (None, 443)
        or host != GIBS_HOST
        or not (path.startswith("/wms/") or path.startswith("/wmts/"))
    ):
        raise GibsUrlError("Only NASA GIBS map pictures can be loaded through this API.")
    return candidate


async def fetch_gibs_image(url: str) -> tuple[bytes, str]:
    """Download one allowed GIBS picture. Redirects are not followed."""

    safe = require_gibs_url(url)
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
            async with client.stream("GET", safe) as response:
                if response.status_code != 200:
                    raise ImageFetchError("NASA GIBS did not return the picture.")
                content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
                if content_type not in _IMAGE_TYPES:
                    raise ImageFetchError("NASA GIBS did not return a picture.")
                chunks: list[bytes] = []
                total = 0
                async for chunk in response.aiter_bytes():
                    total += len(chunk)
                    if total > MAX_BYTES:
                        raise ImageFetchError("The picture is too large to pass through.")
                    chunks.append(chunk)
    except httpx.HTTPError as exc:
        raise ImageFetchError("NASA GIBS did not return the picture.") from exc
    return b"".join(chunks), content_type
