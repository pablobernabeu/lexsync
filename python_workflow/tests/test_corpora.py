import hashlib
import os
import re
import sys
import time
import types
import unicodedata
import urllib.error
import urllib.request

import pandas as pd
import pytest
import yaml
from helper_corpus_files import SUBTLEX_US, SUBTLEX_US_LEXICON
from helper_repo import REPO

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


def _temp_registry(tmp_path, url, sha256=None):
    """A one-entry registry pointing at `url`, so no test touches the network."""
    entry = {
        "language": {"name": "Test", "iso": "xx"}, "connector": "openlexicon",
        "status": "supported", "openlexicon": url, "citation": "Test (2026).",
    }
    if sha256:
        entry["sha256"] = sha256
    reg = {"corpora": {"fake": entry}}
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump(reg), encoding="utf-8")
    return str(path)


class _FakeResponse:
    """Minimal stand-in for urlopen()'s response: the chunked reads and the
    context management fetch_corpus() uses, and nothing else."""

    def __init__(self, body):
        self._body = body

    def read(self, n):
        chunk, self._body = self._body[:n], self._body[n:]
        return chunk

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _mock_transport(monkeypatch, body):
    """Serve `body` in place of the network; returns the recorded call."""
    calls = {}

    def fake_urlopen(url, timeout=None):
        calls["url"], calls["timeout"] = url, timeout
        return _FakeResponse(body)

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    return calls


def _local_cache(tmp_path, monkeypatch):
    cache = tmp_path / "cache"
    cache.mkdir()
    monkeypatch.setattr(corpora, "cache_dir", lambda: str(cache))
    return cache


def _absent_cache(tmp_path, monkeypatch):
    """Point cache_dir() at a directory that does not exist yet."""
    cache = tmp_path / "cache"
    monkeypatch.setattr(corpora, "cache_dir", lambda: str(cache))
    return cache


def _seed_cache(cache, names):
    """Fill the (temporary) cache with empty files of the given names."""
    cache.mkdir(exist_ok=True)
    for name in names:
        (cache / name).write_bytes(b"")


def _listing(cache):
    return sorted(p.name for p in cache.iterdir())


def _age(cache, names):
    """Backdate cache files by two days, past the day after which the sweep
    treats a sidecar as abandoned."""
    then = time.time() - 2 * 24 * 60 * 60
    for name in names:
        os.utime(cache / name, (then, then))


def _wordfreq_registry(tmp_path):
    """A registry whose wordfreq connector covers the one language 'xx'."""
    reg = {"wordfreq_connector": {"languages": ["xx"], "citation": "Test (2026)."},
           "corpora": {}}
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


# Pins the same contract as "fetch_corpus refuses a name that is a path" in the R
# engine's test-corpora.R. The name becomes the cached file's name, so an edited
# registry with an entry named '../../../escaped' made fetch_corpus write three levels
# above the cache, where cache_clear() then refused to look. The rule is
# cache_clear()'s, and it is applied before the registry is read.
@pytest.mark.parametrize("bad", ["../../../escaped", "..\\escaped", "a/b", "C:escaped", "",
                                 ["a", "b"], 1])
def test_fetch_corpus_refuses_a_name_that_is_a_path(tmp_path, monkeypatch, bad):
    cache = _absent_cache(tmp_path, monkeypatch)
    entry = {"language": {"name": "Test", "iso": "xx"}, "status": "supported",
             "openlexicon": "https://example.invalid/escaped.csv", "citation": "Test (2026)."}
    reg = tmp_path / "registry.yaml"
    reg.write_text(yaml.safe_dump({"corpora": {"../../../escaped": entry, "a/b": entry}}),
                   encoding="utf-8")
    _mock_transport(monkeypatch, b"word,freq_zipf\ndog,4.5\n")
    with pytest.raises(ValueError, match="'name' must be a single corpus name, not a path"):
        fetch_corpus(bad, registry_path=str(reg))
    assert not cache.exists()
    assert sorted(p.name for p in tmp_path.iterdir()) == ["registry.yaml"]


# Pins the same contract as "fetch_corpus refusals name the registry they read" in the
# R engine's test-corpora.R. The refusals cited corpora/registry.yaml, a path that an
# installed package does not have, and called an entry with no URL at all a landing page.
def test_fetch_corpus_refusals_name_the_registry_they_read(tmp_path):
    shipped = _registry_path()
    with pytest.raises(ValueError, match="registers only a landing page .* in '%s'"
                                         % re.escape(shipped)):
        fetch_corpus("subtlex_uk", registry_path=shipped)
    with pytest.raises(ValueError, match="not in the registry '%s'" % re.escape(shipped)):
        fetch_corpus("subtlex_klingon", registry_path=shipped)
    # subtlex_nl registers neither a landing page nor a file.
    with pytest.raises(ValueError, match="registers no download URL in '%s'"
                                         % re.escape(shipped)):
        fetch_corpus("subtlex_nl", registry_path=shipped)
    path = _temp_registry(tmp_path, "file:///etc/passwd")
    with pytest.raises(ValueError, match="non-http.* in '%s'" % re.escape(path)):
        fetch_corpus("fake", registry_path=path)


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
# honour through an 'openlexicon' key or a 'derived' file; conversely an entry carrying
# either advertises a download, so it may not claim a status that denies one. Pinning
# the equivalence keeps a rotted URL from being demoted in status alone.
def _download_url(entry):
    return (entry.get("derived") or {}).get("url") or entry.get("openlexicon")


def test_openlexicon_key_and_supported_status_agree(registry):
    for name, entry in registry["corpora"].items():
        assert bool(_download_url(entry)) == (entry.get("status") == "supported"), name


# Pins the same contract as "every supported entry has a download URL and a SHA-256"
# in the R engine's test-corpora.R. A download is cached only once it matches the
# registry's digest, and an entry without one would cache whatever the server sent.
def test_every_supported_entry_has_a_download_url_and_a_sha256():
    supported = []
    for path in _registry_copies():
        with open(path, encoding="utf-8") as handle:
            entries = yaml.safe_load(handle)["corpora"]
        for name, entry in entries.items():
            if entry.get("status") != "supported":
                continue
            supported.append(name)
            derived = entry.get("derived")
            sha = derived.get("sha256") if derived else entry.get("sha256")
            assert _download_url(entry).startswith("https://"), (path, name)
            assert re.fullmatch(r"[0-9a-f]{64}", sha or ""), (path, name)
    assert "subtlex_us" in supported


# SUBTLEX-US's Lg10WF and SUBTLEX-DE's lgSUBTLEX are log10 word counts, which read
# about 1.3 and 1.6 below Zipf, and SUBTLEX-CH publishes no WCpmw column. A user
# who renamed columns as the registry said would filter and match on the wrong
# scale. Pins the same contract as the test of this name in test-corpora.R, and
# reads every copy of the registry that is around: all three in a checkout, the
# bundled one otherwise.
def _registry_copies():
    paths = [_registry_path()]
    if REPO is not None:
        paths += [str(REPO / "corpora" / "registry.yaml"),
                  str(REPO / "R_workflow" / "inst" / "extdata" / "registry.yaml")]
    return paths


def test_registry_column_maps_are_not_log_counts():
    for path in _registry_copies():
        with open(path, encoding="utf-8") as handle:
            entries = yaml.safe_load(handle)["corpora"]
        for name, entry in entries.items():
            columns = entry.get("columns") or {}
            assert columns.get("freq_zipf") not in {"Lg10WF", "lgSUBTLEX", "WCpmw"}, (path, name)
        assert entries["subtlex_us"]["columns"].get("freq_permillion") == "SUBTLWF", path


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
# an unintelligible schema error. Pins the same contract as "an HTML body is
# refused and leaves nothing behind" in the R engine's test-corpora.R: the sniff
# now runs on the sidecar, so not even a '.part' file may remain.
def test_fetch_corpus_rejects_an_html_body_and_caches_nothing(tmp_path, monkeypatch):
    path = _temp_registry(tmp_path, "https://example.invalid/rotted.csv")
    cache = _local_cache(tmp_path, monkeypatch)
    _mock_transport(monkeypatch, b"<!DOCTYPE html>\n<html><body>Not Found</body></html>\n")
    with pytest.raises(ValueError, match="HTML page, not a delimited file"):
        fetch_corpus("fake", registry_path=path)
    assert list(cache.iterdir()) == []


def test_fetch_corpus_brands_a_failed_download(tmp_path, monkeypatch):
    path = _temp_registry(tmp_path, "https://example.invalid/gone.csv")
    cache = _local_cache(tmp_path, monkeypatch)

    def fake_urlopen(url, timeout=None):
        raise urllib.error.HTTPError(url, 404, "Not Found", None, None)

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(RuntimeError, match="could not download corpus 'fake'"):
        fetch_corpus("fake", registry_path=path)
    assert list(cache.iterdir()) == []


# Pins the same contract as "a transfer that dies mid-stream leaves nothing
# behind" in the R engine's test-corpora.R: the pre-sidecar implementation
# cached exactly such truncated bodies, to resurface later as schema errors.
def test_fetch_corpus_removes_the_sidecar_when_the_transfer_dies(tmp_path, monkeypatch):
    path = _temp_registry(tmp_path, "https://example.invalid/flaky.csv")
    cache = _local_cache(tmp_path, monkeypatch)

    class _DyingResponse(_FakeResponse):
        def read(self, n):
            if self._body:
                return _FakeResponse.read(self, n)
            raise OSError("connection reset")

    monkeypatch.setattr(urllib.request, "urlopen",
                        lambda url, timeout=None: _DyingResponse(b"word,freq_zipf\ndog,4"))
    with pytest.raises(RuntimeError, match="could not download corpus 'fake'"):
        fetch_corpus("fake", registry_path=path)
    assert list(cache.iterdir()) == []


# Pins the same contract as "fetch_corpus promotes a verified download and
# removes the sidecar" in the R engine's test-corpora.R: the transfer lands in
# '<dest>.part' and is renamed into place only after every check has passed.
def test_fetch_corpus_promotes_a_verified_download(tmp_path, monkeypatch):
    path = _temp_registry(tmp_path, "https://example.invalid/good.csv")
    cache = _local_cache(tmp_path, monkeypatch)
    calls = _mock_transport(monkeypatch, b"word,freq_zipf\ndog,4.5\n")
    dest = fetch_corpus("fake", registry_path=path)
    assert os.path.basename(dest) == "fake.csv"
    assert [p.name for p in cache.iterdir()] == ["fake.csv"]
    with open(dest, "rb") as handle:
        assert handle.read() == b"word,freq_zipf\ndog,4.5\n"
    # The R engine's download.file() honours options(timeout); this engine has
    # no such ambient setting, so the transport must be given its own.
    assert calls["timeout"] == 60


# Pins the same contract as "an oversized download is aborted and leaves nothing
# behind" in the R engine's test-corpora.R. The cap is lowered through its seam
# because a genuine 200 MB fixture has no place in a test suite; the message
# names the real limit regardless.
def test_fetch_corpus_aborts_an_oversized_download(tmp_path, monkeypatch):
    path = _temp_registry(tmp_path, "https://example.invalid/big.csv")
    cache = _local_cache(tmp_path, monkeypatch)
    monkeypatch.setattr(corpora, "_max_download_bytes", lambda: 16)
    _mock_transport(monkeypatch, b"x" * 64)
    with pytest.raises(ValueError, match="exceeded the 200 MB size limit"):
        fetch_corpus("fake", registry_path=path)
    assert list(cache.iterdir()) == []


# Pins the same contract as "a checksum mismatch is refused and leaves nothing
# behind" in the R engine's test-corpora.R. The field is optional in the code, so the
# contract is exercised through a temporary registry.
def test_fetch_corpus_refuses_a_checksum_mismatch(tmp_path, monkeypatch):
    path = _temp_registry(tmp_path, "https://example.invalid/good.csv", sha256="0" * 64)
    cache = _local_cache(tmp_path, monkeypatch)
    _mock_transport(monkeypatch, b"word,freq_zipf\ndog,4.5\n")
    with pytest.raises(ValueError, match="checksum mismatch for corpus 'fake'"):
        fetch_corpus("fake", registry_path=path)
    assert list(cache.iterdir()) == []


# Pins the same contract as "a matching checksum is accepted" in the R engine's
# test-corpora.R: both engines must derive the same digest from the same bytes.
def test_fetch_corpus_accepts_a_matching_checksum(tmp_path, monkeypatch):
    body = b"word,freq_zipf\ndog,4.5\n"
    path = _temp_registry(tmp_path, "https://example.invalid/good.csv",
                          sha256=hashlib.sha256(body).hexdigest())
    cache = _local_cache(tmp_path, monkeypatch)
    _mock_transport(monkeypatch, body)
    dest = fetch_corpus("fake", registry_path=path)
    assert [p.name for p in cache.iterdir()] == ["fake.csv"]
    assert os.path.basename(dest) == "fake.csv"


# Pins the same contract as "a mocked fetch of subtlex_us normalises into the cache"
# in the R engine's test-corpora.R. The shipped entry names openlexicon's TSV and its
# SHA-256, which a fixture cannot match, so the fixture is first refused against the
# shipped entry and then served to a copy of the entry that carries its own digest.
def test_a_mocked_fetch_of_subtlex_us_normalises_into_the_cache(tmp_path, monkeypatch,
                                                                registry, capsys):
    body = SUBTLEX_US.encode("utf-8")
    entry = dict(registry["corpora"]["subtlex_us"])
    cache = _absent_cache(tmp_path, monkeypatch)
    calls = _mock_transport(monkeypatch, body)
    with pytest.raises(ValueError, match="checksum mismatch for corpus 'subtlex_us'"):
        fetch_corpus("subtlex_us", registry_path=_registry_path())
    assert calls["url"] == entry["openlexicon"]
    assert _listing(cache) == []
    entry["sha256"] = hashlib.sha256(body).hexdigest()
    reg = tmp_path / "registry.yaml"
    reg.write_text(yaml.safe_dump({"corpora": {"subtlex_us": entry}}), encoding="utf-8")
    capsys.readouterr()
    dest = fetch_corpus("subtlex_us", registry_path=str(reg))
    assert dest == str(cache / "subtlex_us.csv")
    assert _listing(cache) == ["subtlex_us.csv"]
    with open(dest, "rb") as handle:
        assert handle.read().decode("utf-8") == SUBTLEX_US_LEXICON
    out = capsys.readouterr().out
    assert "normalised 5 forms from 'SUBTLEXus74286wordstextversion.tsv'" in out
    assert "downloaded 'subtlex_us'. Please cite: Brysbaert & New (2009)" in out


# Pins the same contract as "a download that cannot be normalised leaves nothing
# behind" in the R engine's test-corpora.R: the normalisation is one more check the
# sidecar must pass before it may enter the cache.
def test_a_download_that_cannot_be_normalised_leaves_nothing_behind(tmp_path, monkeypatch):
    entry = {"language": {"name": "Test", "iso": "xx"}, "status": "supported",
             "openlexicon": "https://example.invalid/raw.tsv",
             "columns": {"word": "Word", "freq_permillion": "SUBTLWF"},
             "citation": "Test (2026)."}
    reg = tmp_path / "registry.yaml"
    reg.write_text(yaml.safe_dump({"corpora": {"fake": entry}}), encoding="utf-8")
    cache = _absent_cache(tmp_path, monkeypatch)
    _mock_transport(monkeypatch, b"Word\tFREQcount\ndog\t9831\n")
    with pytest.raises(ValueError, match="has no column 'SUBTLWF'"):
        fetch_corpus("fake", registry_path=str(reg))
    assert _listing(cache) == []


# Pins the same contract as "a derived file is fetched in place of the openlexicon
# file" in the R engine's test-corpora.R. A 'derived' file is a lexicon already
# normalised, which both engines then read byte for byte, so it is preferred and
# cached as it arrives.
def test_a_derived_file_is_fetched_in_place_of_the_openlexicon_file(tmp_path, monkeypatch):
    body = b"word,freq_zipf,freq_permillion\ncat,4.848,70.41\n"
    entry = {"language": {"name": "Test", "iso": "xx"}, "status": "supported",
             "openlexicon": "https://example.invalid/raw.tsv",
             "derived": {"url": "https://example.invalid/derived.csv",
                         "sha256": hashlib.sha256(body).hexdigest()},
             "columns": {"word": "Word", "freq_permillion": "SUBTLWF"},
             "citation": "Test (2026)."}
    reg = tmp_path / "registry.yaml"
    reg.write_text(yaml.safe_dump({"corpora": {"fake": entry}}), encoding="utf-8")
    cache = _absent_cache(tmp_path, monkeypatch)
    calls = _mock_transport(monkeypatch, body)
    dest = fetch_corpus("fake", registry_path=str(reg))
    assert calls["url"] == "https://example.invalid/derived.csv"
    assert _listing(cache) == ["fake.csv"]
    with open(dest, "rb") as handle:
        assert handle.read() == body


# Pins the same contract as "lexsync_cache_dir reports the path without creating
# it" in the R engine's test-corpora.R: asking where the cache is must not bring
# it into being.
def test_cache_dir_only_reports_the_path(tmp_path, monkeypatch):
    # expanduser() reads USERPROFILE on Windows and HOME elsewhere.
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    path = corpora.cache_dir()
    assert path == os.path.join(str(tmp_path), ".lexsync", "cache")
    assert not os.path.exists(path)
    assert not (tmp_path / ".lexsync").exists()


# Pins the same contract as "a refused fetch leaves the cache uncreated" in the R
# engine's test-corpora.R: every refusal comes before the cache is created, so a
# call that fetches nothing writes nothing.
def test_a_refused_fetch_leaves_the_cache_uncreated(tmp_path, monkeypatch):
    cache = _absent_cache(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="not in the registry"):
        fetch_corpus("subtlex_klingon", registry_path=_registry_path())
    with pytest.raises(ValueError, match="landing page"):
        fetch_corpus("subtlex_esp", registry_path=_registry_path())
    with pytest.raises(ValueError, match="non-http"):
        fetch_corpus("fake", registry_path=_temp_registry(tmp_path, "file:///etc/passwd"))
    assert not cache.exists()


# The wordfreq connector has no R twin; its refusal, a missing [corpora] extra,
# must write nothing either.
def test_a_wordfreq_fetch_without_the_extra_leaves_the_cache_uncreated(tmp_path, monkeypatch):
    cache = _absent_cache(tmp_path, monkeypatch)

    def missing(language, n_words, **options):
        raise ModuleNotFoundError("lexsync: ... needs the wordfreq connector")

    monkeypatch.setattr(corpora, "build_wordfreq_lexicon", missing)
    with pytest.raises(ModuleNotFoundError, match="wordfreq connector"):
        fetch_corpus("xx", registry_path=_wordfreq_registry(tmp_path))
    assert not cache.exists()


# Pins the same contract as "a default-destination fetch creates the cache and
# sweeps stale sidecars" in the R engine's test-corpora.R. An interrupt or a dead
# process leaves a '.part' that no handler removed; the next fetch into the cache
# deletes every such sidecar a day old or more, and nothing else. A younger one
# may be a download still running in another process, so it is left alone.
def test_fetch_corpus_creates_the_cache_and_sweeps_stale_sidecars(tmp_path, monkeypatch):
    path = _temp_registry(tmp_path, "https://example.invalid/good.csv")
    cache = _absent_cache(tmp_path, monkeypatch)
    _mock_transport(monkeypatch, b"word,freq_zipf\ndog,4.5\n")
    assert fetch_corpus("fake", registry_path=path) == str(cache / "fake.csv")
    assert _listing(cache) == ["fake.csv"]

    _seed_cache(cache, ["fake.csv.part", "other.csv.part", "other.csv", "busy.csv.part"])
    _age(cache, ["fake.csv.part", "other.csv.part"])
    fetch_corpus("fake", registry_path=path)
    assert _listing(cache) == ["busy.csv.part", "fake.csv", "other.csv"]


# Pins the same contract as "stale sidecars are swept even when the download then
# fails" in the R engine's test-corpora.R: the sweep happens as the fetch starts.
def test_stale_sidecars_are_swept_even_when_the_download_then_fails(tmp_path, monkeypatch):
    path = _temp_registry(tmp_path, "https://example.invalid/gone.csv")
    cache = _absent_cache(tmp_path, monkeypatch)
    _seed_cache(cache, ["other.csv.part", "other.csv"])
    _age(cache, ["other.csv.part"])

    def fake_urlopen(url, timeout=None):
        raise urllib.error.HTTPError(url, 404, "Not Found", None, None)

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(RuntimeError, match="could not download corpus 'fake'"):
        fetch_corpus("fake", registry_path=path)
    assert _listing(cache) == ["other.csv"]


# A wordfreq build is a fetch into the same cache, so it prepares it the same way.
def test_a_wordfreq_fetch_creates_the_cache_and_sweeps_stale_sidecars(tmp_path, monkeypatch):
    cache = _absent_cache(tmp_path, monkeypatch)
    lexicon = pd.DataFrame({"word": ["dog"], "freq_zipf": [4.5],
                            "language": ["xx"], "source": ["wordfreq"]})
    monkeypatch.setattr(corpora, "build_wordfreq_lexicon",
                        lambda language, n_words, **options: lexicon)
    registry_path = _wordfreq_registry(tmp_path)
    assert fetch_corpus("xx", registry_path=registry_path) == str(cache / "xx_wordfreq.csv")

    _seed_cache(cache, ["other.csv.part", "other.csv", "busy.csv.part"])
    _age(cache, ["other.csv.part"])
    fetch_corpus("xx", registry_path=registry_path)
    assert _listing(cache) == ["busy.csv.part", "other.csv", "xx_wordfreq.csv"]


# Pins the same contract as "lexsync_cache_clear removes one corpus and its
# sidecar" in the R engine's test-corpora.R. This engine alone builds wordfreq
# lexica, so it alone has a '<name>_wordfreq.csv' to remove.
def test_cache_clear_removes_one_corpus(tmp_path, monkeypatch):
    cache = _absent_cache(tmp_path, monkeypatch)
    _seed_cache(cache, ["fake.csv", "fake.csv.part", "fake_wordfreq.csv",
                        "other.csv", "fake_extra.csv"])
    removed = corpora.cache_clear("fake")
    assert removed == [str(cache / n) for n in ("fake.csv", "fake.csv.part", "fake_wordfreq.csv")]
    assert _listing(cache) == ["fake_extra.csv", "other.csv"]
    assert corpora.cache_clear("fake") == []


# Pins the same contract as "lexsync_cache_clear() removes the whole cache" in
# the R engine's test-corpora.R.
def test_cache_clear_removes_the_whole_cache(tmp_path, monkeypatch):
    cache = _absent_cache(tmp_path, monkeypatch)
    _seed_cache(cache, ["fake.csv", "other.csv", "other.csv.part"])
    removed = corpora.cache_clear()
    assert sorted(os.path.basename(p) for p in removed) == [
        "fake.csv", "other.csv", "other.csv.part"]
    assert not cache.exists()


# Pins the same contract as "lexsync_cache_clear on an absent cache removes and
# creates nothing" in the R engine's test-corpora.R.
def test_cache_clear_on_an_absent_cache_creates_nothing(tmp_path, monkeypatch):
    cache = _absent_cache(tmp_path, monkeypatch)
    assert corpora.cache_clear() == []
    assert corpora.cache_clear("fake") == []
    assert not cache.exists()


# Pins the same contract as "lexsync_cache_clear refuses a name that is not a
# single corpus name" in the R engine's test-corpora.R: the name is joined onto
# the cache directory, so a separator, or the colon of a Windows drive, would
# reach outside it.
@pytest.mark.parametrize("bad", ["../outside", "..\\outside", "a/b", "C:outside", "a:b", "",
                                 ["a", "b"], 1])
def test_cache_clear_refuses_a_path(tmp_path, monkeypatch, bad):
    cache = _absent_cache(tmp_path, monkeypatch)
    _seed_cache(cache, ["fake.csv"])
    # The file that "../outside" would reach, beside the cache directory.
    outside = tmp_path / "outside.csv"
    outside.write_bytes(b"")
    with pytest.raises(ValueError, match="not a path"):
        corpora.cache_clear(bad)
    assert outside.exists()
    assert _listing(cache) == ["fake.csv"]


def test_list_corpora_surfaces_registry_status():
    frame = list_corpora(_registry_path())
    status = dict(zip(frame["name"], frame["status"], strict=True))
    assert status["subtlex_uk"] == "manual"
    assert status["subtlex_esp"] == "listed"
    assert "validated" not in set(status.values())


# Pins the same contract as "lexsync_cache_clear takes a name literally" in the R
# engine's test-corpora.R, where unlink() once expanded "*" and emptied the
# cache. A name names one corpus's files, and a directory that happens to carry
# that name is not one of them.
def test_cache_clear_takes_a_name_literally(tmp_path, monkeypatch):
    cache = _absent_cache(tmp_path, monkeypatch)
    _seed_cache(cache, ["a.csv", "b.csv"])
    (cache / "d.csv").mkdir()
    for pattern in ("*", "?", "[ab]"):
        assert corpora.cache_clear(pattern) == []
    assert corpora.cache_clear("d") == []
    assert _listing(cache) == ["a.csv", "b.csv", "d.csv"]


# ~/.lexsync holds nothing but the cache, so emptying the cache must not leave an
# empty directory behind in the user's home. Anything else kept there stays.
def test_cache_clear_removes_the_emptied_lexsync_directory(tmp_path, monkeypatch):
    home_dir = tmp_path / ".lexsync"
    cache = home_dir / "cache"
    monkeypatch.setattr(corpora, "cache_dir", lambda: str(cache))
    home_dir.mkdir()
    _seed_cache(cache, ["fake.csv"])
    corpora.cache_clear()
    assert not home_dir.exists()

    home_dir.mkdir()
    _seed_cache(cache, ["fake.csv"])
    (home_dir / "notes.txt").write_bytes(b"")
    corpora.cache_clear()
    assert sorted(p.name for p in home_dir.iterdir()) == ["notes.txt"]


# Pins the same contract as lexsync_cache_clear()'s survivor check in
# R_workflow/R/corpora.R: a file that cannot be deleted (one held open on
# Windows, say) is named in a lexsync error, not left to a bare OSError raised
# partway through.
def test_cache_clear_names_a_file_it_could_not_remove(tmp_path, monkeypatch):
    cache = _absent_cache(tmp_path, monkeypatch)
    _seed_cache(cache, ["fake.csv", "other.csv"])
    monkeypatch.setattr(corpora.os, "remove", lambda path: None)
    with pytest.raises(OSError, match=r"lexsync: could not remove .*fake\.csv"):
        corpora.cache_clear("fake")
    monkeypatch.setattr(corpora.shutil, "rmtree", lambda path, ignore_errors=False: None)
    with pytest.raises(OSError, match="lexsync: could not remove"):
        corpora.cache_clear()


# The wordfreq connector's letter filter has no R twin, since the R engine reads what
# the connector builds as an ordinary lexicon. wordfreq ships in the optional [corpora]
# extra, which CI's dev install leaves out. A real word list would also tie the
# expected words to one wordfreq release, so these tests serve fixed tokens from a
# stand-in.
def _fake_wordfreq(monkeypatch, tokens, zipf=None):
    """Install a stand-in for wordfreq whose top list is `tokens`, most frequent first.

    top_n_list returns the first n tokens, as wordfreq's does, and zipf_frequency gives
    every word 4.0 unless `zipf` maps it to another value.
    """
    fake = types.ModuleType("wordfreq")
    fake.top_n_list = lambda language, n: list(tokens[:n])
    fake.zipf_frequency = lambda word, language: (zipf or {}).get(word, 4.0)
    monkeypatch.setitem(sys.modules, "wordfreq", fake)


def _wordfreq_words(monkeypatch, language, tokens, **options):
    """The words build_wordfreq_lexicon keeps from `tokens`, every token examined."""
    _fake_wordfreq(monkeypatch, tokens)
    lexicon = corpora.build_wordfreq_lexicon(language, n_words=len(tokens), **options)
    return lexicon["word"].tolist()


# Hindi and Bengali write most vowels, the virama and the nasal signs as combining
# marks, which Python's word class excludes. The filter built on that class kept 137 of
# the 500 Hindi forms requested, beginning 'aap', 'and' and 'at', without है or में,
# and 90 of 500 Bengali ones.
@pytest.mark.parametrize("language,tokens", [
    ("hi", ["के", "है", "में", "की", "से", "को", "क्या"]),
    ("bn", ["না", "করে", "এবং", "আমি", "প্রথম"]),
])
def test_wordfreq_keeps_words_written_with_combining_marks(monkeypatch, language, tokens):
    assert _wordfreq_words(monkeypatch, language, tokens) == sorted(tokens)


# Persian spells many words with a zero-width non-joiner (U+200C), and Devanagari
# can force a half form with a zero-width joiner (U+200D). Both are format characters
# that Python's word class excludes, so every Persian form spelt with a non-joiner was
# dropped. A token that opens with either is still refused.
@pytest.mark.parametrize("language,tokens,kept", [
    ("fa", ["می\u200cشود", "آن\u200cها", "\u200cها", "است"],
     ["می\u200cشود", "آن\u200cها", "است"]),
    ("hi", ["क्\u200dष", "\u200dक", "है"], ["क्\u200dष", "है"]),
])
def test_wordfreq_keeps_words_spelt_with_zero_width_joiners(monkeypatch, language, tokens,
                                                           kept):
    assert _wordfreq_words(monkeypatch, language, tokens) == sorted(kept)


# Ukrainian spells words such as п'ять and ім'я with an apostrophe between two letters,
# written U+0027, U+2019 or U+02BC, and Belarusian likewise. Catalan writes its
# geminate l as l·l (pel·lícula). The filter dropped all of them. Each joiner is
# allowed only between two letters, the middle dot only between two l's, and only in
# the languages that spell words with it. U+02BC is a modifier letter, so it counts as
# an apostrophe here and never as a letter.
@pytest.mark.parametrize("language,tokens,kept", [
    ("uk", ["п'ять", "п\u2019ять", "п\u02bcять", "ім'я", "'ять", "п'", "п''ять", "так"],
     ["п'ять", "п\u2019ять", "п\u02bcять", "ім'я", "так"]),
    ("be", ["сям'я", "\u02bcя", "так"], ["сям'я", "так"]),
    ("ca", ["pel·lícula", "col·lecció", "l·a", "a·l", "l·", "·l", "per"],
     ["pel·lícula", "col·lecció", "per"]),
    ("ru", ["п'ять", "п\u02bcять", "так"], ["так"]),
    ("es", ["pel·lícula", "por"], ["por"]),
])
def test_wordfreq_admits_word_internal_joiners_where_the_language_uses_them(
        monkeypatch, language, tokens, kept):
    assert _wordfreq_words(monkeypatch, language, tokens) == sorted(kept)


# Anywhere else an apostrophe joins a contraction, an elision or a clitic, two words in
# one token. Digits spell no word, and nor do underscores or other punctuation marks,
# so all of these stay out. A token that opens with a combining mark stays out as well.
@pytest.mark.parametrize("language,tokens,kept", [
    ("en", ["don't", "it\u2019s", "don\u02bct", "a1", "2nd", "e_mail", "u.s", "co-op",
            "\u0301a", "cat"], ["cat"]),
    ("fr", ["aujourd'hui", "l'homme", "chat"], ["chat"]),
    ("ca", ["se'n", "l'home", "gat"], ["gat"]),
    ("uk", ["5'ять", "п'5", "п_ять", "кіт"], ["кіт"]),
])
def test_wordfreq_still_excludes_contractions_digits_and_punctuation(
        monkeypatch, language, tokens, kept):
    assert _wordfreq_words(monkeypatch, language, tokens) == kept


# wordfreq gives some Greek forms decomposed (μαΐου as ι, U+0308 and U+0301), which
# the filter dropped for their combining marks. Each form is kept in NFC, the form the
# lexicon readers give every word, and a form two tokens share is kept once.
def test_wordfreq_keeps_each_form_once_in_nfc(monkeypatch):
    nfc = "\u03bc\u03b1\u0390\u03bf\u03c5"
    nfd = unicodedata.normalize("NFD", nfc)
    assert nfd != nfc
    assert _wordfreq_words(monkeypatch, "el", [nfd, "και"]) == ["και", nfc]
    assert _wordfreq_words(monkeypatch, "el", [nfd, nfc, "και", "να"]) == ["και", nfc, "να"]


# A fetch that yields fewer forms than requested says so, since a short lexicon
# changes every frequency band a design draws on. The count is of the forms the
# lexicon holds, after any that wordfreq gives no frequency are dropped.
def test_wordfreq_reports_a_shortfall(monkeypatch, capsys):
    _fake_wordfreq(monkeypatch, ["है", "में", "a1", "don't", "की", "से"], zipf={"से": 0.0})
    lexicon = corpora.build_wordfreq_lexicon("hi", n_words=6)
    assert lexicon["word"].tolist() == ["की", "में", "है"]
    assert capsys.readouterr().out == (
        "lexsync: wordfreq supplied only 3 forms for 'hi' that pass the letter filter "
        "(n_words was 6).\n")

    _fake_wordfreq(monkeypatch, ["है", "में", "a1"])
    assert len(corpora.build_wordfreq_lexicon("hi", n_words=2)) == 2
    assert capsys.readouterr().out == ""


def test_wordfreq_strict_refuses_a_shortfall(monkeypatch):
    _fake_wordfreq(monkeypatch, ["है", "में", "a1"])
    with pytest.raises(ValueError, match=r"^lexsync: wordfreq supplied only 2 forms for 'hi' "
                                         r"that pass the letter filter \(n_words was 3\)\.$"):
        corpora.build_wordfreq_lexicon("hi", n_words=3, strict=True)
    assert len(corpora.build_wordfreq_lexicon("hi", n_words=2, strict=True)) == 2


# exclude_latin drops every form holding a Latin letter, such as the English tokens of
# the Hindi list ('and', 'bjp'), fullwidth ones included. The option is off by default
# and is not a one-script rule, so a Japanese lexicon keeps its kana and kanji together.
@pytest.mark.parametrize("language,tokens,kept", [
    ("hi", ["है", "and", "abcनमस्ते", "में", "bjp", "café", "नमस्ते"], ["है", "में", "नमस्ते"]),
    ("ja", ["コーヒー", "twitter", "人々", "\uff54\uff56", "tシャツ"], ["コーヒー", "人々"]),
])
def test_wordfreq_exclude_latin_drops_forms_with_latin_letters(monkeypatch, language, tokens,
                                                               kept):
    assert _wordfreq_words(monkeypatch, language, tokens, exclude_latin=True) == sorted(kept)
    assert _wordfreq_words(monkeypatch, language, tokens) == sorted(tokens)


# fetch_corpus passes both options to the connector, and a shortfall refused under
# strict=True writes nothing, as every other refusal does.
def test_fetch_corpus_passes_the_filter_options_to_the_wordfreq_connector(tmp_path,
                                                                         monkeypatch):
    cache = _absent_cache(tmp_path, monkeypatch)
    _fake_wordfreq(monkeypatch, ["है", "and", "में"])
    registry_path = _wordfreq_registry(tmp_path)
    with pytest.raises(ValueError, match="supplied only 2 forms for 'xx'"):
        fetch_corpus("xx", registry_path=registry_path, n_words=3, strict=True,
                     exclude_latin=True)
    assert not cache.exists()
    dest = fetch_corpus("xx", registry_path=registry_path, n_words=2, exclude_latin=True)
    assert pd.read_csv(dest, encoding="utf-8")["word"].tolist() == ["में", "है"]
