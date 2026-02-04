from models import LinkData
from storage import LinkStore


def test_save_and_dedupe(tmp_path):
    store = LinkStore(str(tmp_path / "links.json"))

    link = LinkData(url="https://example.com", title="Example", category="article")
    result1 = store.save(link)
    result2 = store.save(link)

    assert result1 is not None
    assert result2 is None
    assert len(store.get_all()) == 1


def test_exists(tmp_path):
    store = LinkStore(str(tmp_path / "links.json"))

    link = LinkData(url="https://example.com", title="Example")
    assert store.exists("https://example.com") is False

    store.save(link)
    assert store.exists("https://example.com") is True
