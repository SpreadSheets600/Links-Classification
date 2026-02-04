from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from classifier import Classifier
from config import Settings
from storage import LinkStore
from utils import get_domain


@dataclass
class ProcessResult:
    total: int = 0
    saved: int = 0
    skipped: int = 0
    errors: list[dict[str, str]] = field(default_factory=list)


async def _process_url(
    url: str,
    classifier: Classifier,
    store: LinkStore,
    semaphore: asyncio.Semaphore,
    result: ProcessResult,
):
    async with semaphore:
        try:
            link_data = await classifier.analyze(url, get_domain(url))
            saved = store.save(link_data)
            if saved:
                result.saved += 1
            else:
                result.skipped += 1
        except Exception as e:
            result.errors.append({"url": url, "error": str(e)})


async def process_links(
    urls: list[str], store: LinkStore, settings: Settings
) -> ProcessResult:
    unique_urls = list(dict.fromkeys(url for url in urls if url))
    result = ProcessResult(total=len(unique_urls))

    if not unique_urls:
        return result

    classifier = Classifier(settings)
    semaphore = asyncio.Semaphore(settings.max_concurrency)

    tasks = [
        _process_url(url, classifier, store, semaphore, result) for url in unique_urls
    ]
    await asyncio.gather(*tasks)

    return result
