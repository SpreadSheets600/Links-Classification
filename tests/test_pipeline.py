import pytest

import pipeline
from config import Settings
from models import LinkData
from storage import LinkStore


@pytest.mark.asyncio
async def test_process_links_saves_and_errors(monkeypatch, tmp_path):
    class DummyClassifier:
        def __init__(self, settings):
            pass

        async def analyze(self, url, domain):
            if "bad" in url:
                raise RuntimeError("boom")
            return LinkData(
                url=url,
                title="Title",
                description="Desc",
                site_name="Site",
                category="article",
                context="Context",
            )

    monkeypatch.setattr(pipeline, "Classifier", DummyClassifier)

    store = LinkStore(str(tmp_path / "links.json"))
    settings = Settings.from_env()

    result = await pipeline.process_links(
        urls=["https://example.com", "https://bad.example.com"],
        store=store,
        settings=settings,
    )

    assert result.total == 2
    assert result.saved == 1
    assert len(result.errors) == 1
    assert len(store.get_all()) == 1


@pytest.mark.asyncio
async def test_process_links_skips_duplicates(monkeypatch, tmp_path):
    class DummyClassifier:
        def __init__(self, settings):
            pass

        async def analyze(self, url, domain):
            return LinkData(
                url=url,
                title="Title",
                description="Desc",
                site_name="Site",
                category="code",
                context="Context",
            )

    monkeypatch.setattr(pipeline, "Classifier", DummyClassifier)

    store = LinkStore(str(tmp_path / "links.json"))
    settings = Settings.from_env()

    result1 = await pipeline.process_links(
        urls=["https://example.com"],
        store=store,
        settings=settings,
    )
    result2 = await pipeline.process_links(
        urls=["https://example.com"],
        store=store,
        settings=settings,
    )

    assert result1.saved == 1
    assert result2.skipped == 1
    assert len(store.get_all()) == 1


@pytest.mark.asyncio
async def test_process_links_empty_list(tmp_path):
    store = LinkStore(str(tmp_path / "links.json"))
    settings = Settings.from_env()

    result = await pipeline.process_links(urls=[], store=store, settings=settings)

    assert result.total == 0
    assert result.saved == 0
    assert result.errors == []
