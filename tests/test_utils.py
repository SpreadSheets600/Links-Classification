from utils import extract_urls, get_domain, normalize_url


def test_extract_urls_strips_punctuation():
    text = "See https://example.com, and https://foo.bar/test)."
    assert extract_urls(text) == ["https://example.com", "https://foo.bar/test"]


def test_normalize_url_lowercases_scheme_and_host():
    assert (
        normalize_url("HTTPS://Example.COM/Path?Q=1") == "https://example.com/Path?Q=1"
    )


def test_get_domain():
    assert get_domain("https://sub.example.com/path") == "sub.example.com"
