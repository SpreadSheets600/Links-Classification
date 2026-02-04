from __future__ import annotations

import re
from urllib.parse import urlparse, urlunparse

_URL_RE = re.compile(r"https?://[^\s<>\]]+")
_TRAILING_PUNCT = '.,;:!?)"]}'


def extract_urls(text: str) -> list[str]:
    urls: list[str] = []
    for match in _URL_RE.findall(text):
        cleaned = match.strip().strip("<>").rstrip(_TRAILING_PUNCT)
        if cleaned:
            urls.append(cleaned)
    return list(dict.fromkeys(urls))


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return url
    return urlunparse(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path or "",
            parsed.params or "",
            parsed.query or "",
            "",
        )
    )


def get_domain(url: str) -> str:
    return urlparse(url).netloc.lower()
