import os
import urllib.error
import urllib.request

import pytest
import yaml

import lexsync
from lexsync import corpora
from lexsync.corpora import _starts_with_markup, fetch_corpus, list_corpora

# The vocabulary registry.yaml's header defines and list_corpora() surfaces.
STATUSES = {"validated", "supported", "manual", "listed"}


def _registry_path():
    return os.path.join(os.path.dirname(lexsync.__file__), "data", "registry.yaml")


@pytest.fixture
def registry():
    with open(_registry_path(), encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _temp_registry(tmp_path, url):
    """A one-entry registry pointing at `url`, so no test touches the network."""
    reg = {"corpora": {"fake": {
        "language": {"name": "Test", "iso": "xx"}, "connector": "openlexicon",
        "status": "supported", "openlexicon": url, "citation": "Test (2026).",
    }}}
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump(reg), encoding="utf-8")
    return str(path)


# Pins the same contract as "fetch_corpus refuses an entry that registers only a
# landing page" in the R engine's test-corpora.R: 'url' is the human-facing page
# and 'openlexicon' the delimited file, so falling back to 'url' would cache an
# HTML document as <name>.csv and fail later as a confusing schema error.
def test_fetch_corpus_refuses_landing_page_only_entry(tmp_path):
    with pytest.raises(ValueError, match="landing page"):
        fetch_corpus("subtlex_esp", registry_path=_registry_path())


def test_fetch_corpus_rejects_unregistered_corpus():
    with pytest.raises(ValueError, match="not in the registry"):
        fetch_corpus("subtlex_klingon", registry_path=_registry_path())


# The registry's own header defines 'validated' as a bundled example slice
# demonstrated end to end. Every bundled lexicon is wordfreq-derived, so no
# SUBTLEX entry may claim it; list_corpora() shows 'status' to users.
def test_registry_status_reflects_what_is_actually_shipped(registry):
    corpora_ = registry["corpora"]
    assert corpora_["subtlex_uk"]["status"] == "manual"
    assert corpora_["subtlex_esp"]["status"] == "listed"
    assert not any(entry.get("status") == "validated" for entry in corpora_.values())
    assert not any("bundled" in entry for entry in corpora_.values())


def test_registry_statuses_come_from_the_documented_vocabulary(registry):
    for name, entry in registry["corpora"].items():
        assert entry.get("status") in STATUSES, name


# SUBTLEX-UK's openlexicon path 404s, and openlexicon has never hosted the corpus;
# van Heuven's own distribution publishes it only as zip archives, which the
# delimited-file connector cannot ingest. The entry must therefore send a human to
# the landing page rather than advertise a download that fails.
def test_subtlex_uk_advertises_a_landing_page_not_a_dead_download(registry):
    entry = registry["corpora"]["subtlex_uk"]
    assert "openlexicon" not in entry
    assert entry["url"].startswith("https://")
    with pytest.raises(ValueError, match="landing page"):
        fetch_corpus("subtlex_uk", registry_path=_registry_path())


# 'supported' means fetchable into the user cache, which fetch_corpus() can only
# honour through an 'openlexicon' key; conversely an entry carrying that key
# advertises a download, so it may not claim a status that denies one. Pinning the
# equivalence keeps a rotted URL from being demoted in status alone.
def test_openlexicon_key_and_supported_status_agree(registry):
    for name, entry in registry["corpora"].items():
        assert bool(entry.get("openlexicon")) == (entry.get("status") == "supported"), name


# Pins the same contract as "fetch_corpus refuses a non-http(s) URL" in the R
# engine's test-corpora.R. A registry is editable and fetch_corpus() writes
# wherever it points, so 'file://' must not be read under the guise of a download.
@pytest.mark.parametrize("url", ["file:///etc/passwd", "ftp://example.invalid/x.csv",
                                 "corpora/local.csv"])
def test_fetch_corpus_refuses_a_non_http_url(tmp_path, url):
    with pytest.raises(ValueError, match="non-http"):
        fetch_corpus("fake", registry_path=_temp_registry(tmp_path, url))


# Pins the same decision table as .starts_with_markup() in the R engine's
# test-corpora.R: identical bytes must give an identical verdict in both engines.
@pytest.mark.parametrize("head,expected", [
    (b"<!DOCTYPE html>\n<html>404</html>", True),
    (b"\n\r\t <html>", True),                       # leading whitespace
    (b"\xef\xbb\xbf<html>", True),                  # a BOM ahead of the tag
    (b"word,freq_zipf\ndog,4.5\n", False),
    (b"\xef\xbb\xbfword,freq_zipf\n", False),       # a BOM ahead of real data
    (b"", False),
    (b"   ", False),
])
def test_starts_with_markup_decision_table(tmp_path, head, expected):
    path = tmp_path / "head.bin"
    path.write_bytes(head)
    assert _starts_with_markup(str(path)) is expected


# A URL answering 200 with an HTML page (a login wall, or a 404 page served with
# the wrong status) must not be cached as <name>.csv, where it would resurface as
# an unintelligible schema error. The R twin cannot be driven this far without a
# seam through utils::download.file, so it pins the same verdict on the sniff.
def test_fetch_corpus_rejects_an_html_body_and_caches_nothing(tmp_path, monkeypatch):
    path = _temp_registry(tmp_path, "https://example.invalid/rotted.csv")
    cache = tmp_path / "cache"
    cache.mkdir()
    monkeypatch.setattr(corpora, "cache_dir", lambda: str(cache))

    def fake_urlretrieve(url, dest):
        with open(dest, "wb") as handle:
            handle.write(b"<!DOCTYPE html>\n<html><body>Not Found</body></html>\n")
        return dest, None

    monkeypatch.setattr(urllib.request, "urlretrieve", fake_urlretrieve)
    with pytest.raises(ValueError, match="HTML page, not a delimited file"):
        fetch_corpus("fake", registry_path=path)
    assert list(cache.iterdir()) == []


def test_fetch_corpus_brands_a_failed_download(tmp_path, monkeypatch):
    path = _temp_registry(tmp_path, "https://example.invalid/gone.csv")
    monkeypatch.setattr(corpora, "cache_dir", lambda: str(tmp_path))

    def fake_urlretrieve(url, dest):
        raise urllib.error.HTTPError(url, 404, "Not Found", None, None)

    monkeypatch.setattr(urllib.request, "urlretrieve", fake_urlretrieve)
    with pytest.raises(RuntimeError, match="could not download corpus 'fake'"):
        fetch_corpus("fake", registry_path=path)


def test_fetch_corpus_keeps_a_delimited_body(tmp_path, monkeypatch):
    path = _temp_registry(tmp_path, "https://example.invalid/good.csv")
    cache = tmp_path / "cache"
    cache.mkdir()
    monkeypatch.setattr(corpora, "cache_dir", lambda: str(cache))

    def fake_urlretrieve(url, dest):
        with open(dest, "wb") as handle:
            handle.write(b"word,freq_zipf\ndog,4.5\n")
        return dest, None

    monkeypatch.setattr(urllib.request, "urlretrieve", fake_urlretrieve)
    dest = fetch_corpus("fake", registry_path=path)
    assert os.path.basename(dest) == "fake.csv"
    with open(dest, encoding="utf-8") as handle:
        assert handle.read().startswith("word,freq_zipf")


def test_list_corpora_surfaces_registry_status():
    frame = list_corpora(_registry_path())
    status = dict(zip(frame["name"], frame["status"]))
    assert status["subtlex_uk"] == "manual"
    assert status["subtlex_esp"] == "listed"
    assert "validated" not in set(status.values())
