"""The datasheet credits the lexicon a design selected from for what it is.

The datasheet and the Methods paragraph credited wordfreq (Speer, 2022) for every lexicon
a corpus or generated design read, whatever file the design named. A study selecting from
SUBTLEX-US, or from a lexicon of its own, would have cited the wrong corpus. A lexicon
lexsync ships is now recognised by the checksum of its bytes with CRLF line ends read as
LF. A corpus fetched into the cache is credited by the registry's citation, and any other
file is named by its file name and checksum. R_workflow/tests/testthat/
test-lexicon-provenance.R holds the R engine to the same tests, by the same names.
"""
import hashlib
import json
import os
import re
from pathlib import Path

import pandas as pd
import pytest
import yaml
from helper_repo import repo_path

import lexsync
from lexsync import corpora
from lexsync.datasheet import _BUNDLED_LEXICA, _lexicon_provenance, methods_paragraph
from lexsync.run_pipeline import run_pipeline

WORDFREQ = ("wordfreq (Speer, 2022), data CC BY-SA 4.0; full corpus licence and citation "
            "at https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md")
# The screened lexicon's credit states its rule, since the datasheet records it.
SCREENED = ("wordfreq (Speer, 2022) screened against SUBTLEX-US (Brysbaert & New, 2009), "
            "data CC BY-SA 4.0; forms absent from SUBTLEX-US or beginning with a lower-case "
            "letter in under 10% of their uses are marked nonstandard, and N and OLD20 "
            "count only the unmarked forms; full corpus licence and citation at "
            "https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md")
# The English example slice holds only forms the screen keeps, so it marks none.
SCREENED_SLICE = ("wordfreq (Speer, 2022) screened against SUBTLEX-US (Brysbaert & New, "
                  "2009), data CC BY-SA 4.0; forms absent from SUBTLEX-US or beginning with "
                  "a lower-case letter in under 10% of their uses are left out, and N and "
                  "OLD20 count neighbours only among the forms the screen keeps; full corpus "
                  "licence and citation at "
                  "https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md")
SLICES = {"en_example.csv": SCREENED_SLICE, "es_example.csv": WORDFREQ,
          "zh_example.csv": WORDFREQ}
DERIVED = {"en.csv": WORDFREQ, "en_v2.csv": SCREENED, "es.csv": WORDFREQ,
           "es_gender.csv": WORDFREQ, "zh.csv": WORDFREQ}


def _data(name):
    return os.path.join(os.path.dirname(lexsync.__file__), "data", name)


def _posix(path):
    return str(path).replace("\\", "/")


def _lf_sha256(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def _registry():
    with open(corpora._registry_path(None), encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def test_a_user_lexicon_is_named_by_file_and_checksum(tmp_path):
    # The example slice less its last row: the same columns, but not a file lexsync ships.
    data = Path(_data("en_example.csv")).read_bytes()
    lexicon = tmp_path / "my_lexicon.csv"
    lexicon.write_bytes(data[:data.rstrip(b"\n").rfind(b"\n") + 1])
    design = {"name": "en_own", "language": "english", "lexicon": _posix(lexicon),
              "n_per_condition": 4, "pool_filters": {"length": [4, 7]},
              "conditions": [{"name": "high", "define_by": {"frequency": [5.0, 7.0]}},
                             {"name": "low", "define_by": {"frequency": [3.0, 4.0]}}],
              "match_on": ["length"]}
    path = tmp_path / "design.yaml"
    path.write_text(yaml.safe_dump(design), encoding="utf-8")
    out = tmp_path / "out"
    run_pipeline(str(path), _data("schema.yaml"), str(out), verbose=False)
    with open(out / "reports" / "en_own_english_datasheet_py.json", encoding="utf-8") as handle:
        ds = json.load(handle)
    own = ("a user-supplied lexicon (my_lexicon.csv, sha256 %s)"
           % hashlib.sha256(lexicon.read_bytes()).hexdigest()[:12])
    assert ds["materials_source"]["provenance"] == own
    text = methods_paragraph(ds)
    assert f"selected from the English lexicon ({own})" in text
    assert "wordfreq" not in text


def test_a_bundled_lexicon_is_recognised_whatever_its_line_endings(tmp_path):
    for name, provenance in SLICES.items():
        data = Path(_data(name)).read_bytes()
        assert b"\r" not in data
        crlf = tmp_path / ("crlf_" + name)
        crlf.write_bytes(data.replace(b"\n", b"\r\n"))
        renamed = tmp_path / ("renamed_" + name)
        renamed.write_bytes(data)
        assert _lexicon_provenance(_data(name)) == provenance, name
        assert _lexicon_provenance(str(crlf)) == provenance, name
        assert _lexicon_provenance(str(renamed)) == provenance, name
    # One byte more and the file is the user's own.
    changed = tmp_path / "changed.csv"
    changed.write_bytes(Path(_data("en_example.csv")).read_bytes() + b"zzzz,1.0,en,mine,0,1.0\n")
    assert _lexicon_provenance(str(changed)) == (
        "a user-supplied lexicon (changed.csv, sha256 %s)"
        % hashlib.sha256(changed.read_bytes()).hexdigest()[:12])


def test_the_repository_lexica_are_recognised_with_crlf_line_endings(tmp_path):
    # This OneDrive checkout once held en.csv and es.csv with CRLF line ends, which a
    # key on the raw bytes would not have recognised.
    for name, provenance in DERIVED.items():
        path = repo_path("corpora", "derived", name)
        data = path.read_bytes()
        crlf = tmp_path / name
        crlf.write_bytes(data.replace(b"\n", b"\r\n"))
        assert _lexicon_provenance(str(path)) == provenance, name
        assert _lexicon_provenance(str(crlf)) == provenance, name


def test_every_bundled_lexicon_is_in_the_provenance_table():
    named = {entry[0]: digest for digest, entry in _BUNDLED_LEXICA.items()}
    assert sorted(named) == sorted(["corpora/derived/" + n for n in DERIVED] + list(SLICES))
    for name in SLICES:
        assert named[name] == _lf_sha256(Path(_data(name)).read_bytes()), name
    for name in DERIVED:
        data = repo_path("corpora", "derived", name).read_bytes()
        assert named["corpora/derived/" + name] == _lf_sha256(data), name


def test_the_english_example_slice_holds_unmarked_rows_of_en_v2():
    # The slice both packages bundle is 3,000 of the forms the screened lexicon keeps,
    # each with the cells en_v2.csv gives it, N and OLD20 among them. It used to be a
    # slice of en.csv, a quarter of it names, acronyms and other marked forms.
    v2 = pd.read_csv(repo_path("corpora", "derived", "en_v2.csv"), dtype=str,
                     keep_default_na=False, encoding="utf-8").set_index("word")
    sl = pd.read_csv(_data("en_example.csv"), dtype=str, keep_default_na=False,
                     encoding="utf-8")
    assert list(sl.columns) == ["word", "freq_zipf", "language", "source", "n_density",
                                "old20"]
    assert len(sl) == 3000 and sl["word"].is_unique
    rows = v2.loc[sl["word"]]
    assert (rows["nonstandard"] == "0").all()
    for col in sl.columns[1:]:
        assert rows[col].tolist() == sl[col].tolist(), col


def test_a_registry_corpus_in_the_cache_is_credited_by_its_citation(tmp_path, monkeypatch):
    cache = tmp_path / "cache"
    cache.mkdir()
    monkeypatch.setattr(corpora, "cache_dir", lambda: str(cache))
    reg = _registry()
    body = b"word,freq_zipf\ncat,4.5\ndog,4.6\n"
    cached = cache / "subtlex_us.csv"
    cached.write_bytes(body)
    assert _lexicon_provenance(str(cached)) == reg["corpora"]["subtlex_us"]["citation"]
    # A lexicon the wordfreq connector built is credited to wordfreq.
    built = cache / "fr_wordfreq.csv"
    built.write_bytes(body)
    assert _lexicon_provenance(str(built)) == reg["wordfreq_connector"]["citation"]
    # The same file outside the cache, or a cached file no registry entry names, is the
    # user's own.
    sha = hashlib.sha256(body).hexdigest()[:12]
    elsewhere = tmp_path / "subtlex_us.csv"
    elsewhere.write_bytes(body)
    assert _lexicon_provenance(str(elsewhere)) == (
        f"a user-supplied lexicon (subtlex_us.csv, sha256 {sha})")
    mine = cache / "mine.csv"
    mine.write_bytes(body)
    assert _lexicon_provenance(str(mine)) == f"a user-supplied lexicon (mine.csv, sha256 {sha})"


def test_a_cached_corpus_with_a_missing_registry_setting_is_refused(tmp_path, monkeypatch):
    # A LEXSYNC_REGISTRY that names a missing file is refused by name, and the corpus
    # is not credited as the user's own.
    cache = tmp_path / "cache"
    cache.mkdir()
    monkeypatch.setattr(corpora, "cache_dir", lambda: str(cache))
    cached = cache / "subtlex_esp.csv"
    cached.write_bytes(b"word,freq_zipf\nhola,5\n")
    missing = str(tmp_path / "no_such_registry.yaml")
    monkeypatch.setenv("LEXSYNC_REGISTRY", missing)
    message = re.escape(
        f"lexsync: registry not found: '{missing}' (the LEXSYNC_REGISTRY environment variable).")
    with pytest.raises(FileNotFoundError, match=message):
        _lexicon_provenance(str(cached))


def test_a_lexicon_that_cannot_be_read_is_still_the_users_own(tmp_path):
    missing = tmp_path / "missing.csv"
    assert _lexicon_provenance(str(missing)) == "a user-supplied lexicon (missing.csv)"
    assert _lexicon_provenance(None) == "a user-supplied lexicon"
