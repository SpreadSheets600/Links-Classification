from __future__ import annotations

import aiohttp

from config import Settings


async def fetch_html(
    url: str, settings: Settings, session: aiohttp.ClientSession
) -> str | None:
    async with session.get(url, allow_redirects=True) as resp:
        if resp.status >= 400:
            return None
        if "text/html" not in resp.headers.get("Content-Type", ""):
            return None
        raw = await resp.content.read(250_000)
        return raw.decode("utf-8", errors="ignore") if raw else None
