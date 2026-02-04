from __future__ import annotations

import asyncio
from pathlib import Path

from dotenv import load_dotenv

from config import Settings
from pipeline import process_links
from storage import LinkStore
from utils import extract_urls


async def run() -> int:
    load_dotenv()
    settings = Settings.from_env()

    if not settings.openrouter_api_key:
        print("OPENROUTER_API_KEY is required. Set it in .env or environment.")
        return 1

    links_file = Path(__file__).with_name("links.md")
    if not links_file.exists():
        print(f"Links file not found: {links_file}")
        return 1

    urls = extract_urls(links_file.read_text())
    if not urls:
        print("No URLs found in links.md")
        return 1

    store = LinkStore(settings.data_path)
    result = await process_links(urls, store, settings)

    print(
        f"Processed {result.total} URLs: {result.saved} saved, {result.skipped} skipped, {len(result.errors)} errors"
    )
    for err in result.errors:
        print(f"  Error: {err['url']} - {err['error']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
