"""The screened English lexicon must stay what `fetch_corpora.py --screen-en` writes.

corpora/derived/en_v2.csv holds the 30,000 forms of en.csv with columns from SUBTLEX-US
(Brysbaert & New, 2009) that mark the forms absent from it or rarely written in lower
case, mostly names and acronyms. Its N and OLD20 are computed against the unmarked
forms only. en.csv keeps its bytes, so designs written for
lexsync 0.1 select what they selected. These tests hold both files to that, check
en_v2's N and OLD20 against lexsync's own add_neighbourhood, and rebuild en_v2 byte
for byte when SUBTLEX-US is cached under corpora/raw/. Data checks on repository files,
so the R suite has no twin of them.
"""
import hashlib
import importlib.util
import re
import sys

import numpy as np
import pandas as pd
import pytest
from helper_repo import REPO

from lexsync.querying import add_neighbourhood

DERIVED = REPO / "corpora" / "derived" if REPO else None
# en.csv as git stores it, LF line ends. A CRLF copy hashes differently, so the
# line ends are normalised first.
EN_LF_SHA256 = "575833489e04d6a4001fda56a56e3daa383811dece1f819c44060ee79ca56976"
COLUMNS = ["word", "freq_zipf", "language", "source", "n_density", "old20",
           "in_subtlex_us", "lowercase_share", "nonstandard", "reference_member",
           "n_density_raw", "old20_raw"]

pytestmark = pytest.mark.skipif(REPO is None,
                                reason="repository-only data; absent from an installed copy")


def _text(name):
    """A derived lexicon as the text of its cells, as written."""
    path = DERIVED / name
    if not path.exists():
        pytest.fail(f"{name} is missing; run python corpora/fetch_corpora.py --screen-en")
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")


def _builder():
    pytest.importorskip("wordfreq")
    pytest.importorskip("rapidfuzz")
    spec = importlib.util.spec_from_file_location(
        "fetch_corpora", REPO / "corpora" / "fetch_corpora.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_en_csv_keeps_its_bytes():
    data = (DERIVED / "en.csv").read_bytes()
    assert hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest() == EN_LF_SHA256


def test_en_v2_holds_the_forms_of_en_in_order():
    en, v2 = _text("en.csv"), _text("en_v2.csv")
    assert list(v2.columns) == COLUMNS
    assert len(v2) == 30000
    for col in ("word", "freq_zipf", "language", "source"):
        assert v2[col].tolist() == en[col].tolist(), col


def test_en_v2_keeps_the_neighbourhood_of_en_as_raw_columns():
    en, v2 = _text("en.csv"), _text("en_v2.csv")
    assert v2["n_density_raw"].tolist() == en["n_density"].tolist()
    assert v2["old20_raw"].tolist() == en["old20"].tolist()


def test_the_screening_columns_follow_the_rule():
    v2 = _text("en_v2.csv")
    for col in ("in_subtlex_us", "nonstandard", "reference_member"):
        assert set(v2[col]) == {"0", "1"}, col
    assert ((v2["nonstandard"].astype(int) + v2["reference_member"].astype(int)) == 1).all()
    present = v2["in_subtlex_us"] == "1"
    share = pd.to_numeric(v2["lowercase_share"].replace("", np.nan))
    # A share for every SUBTLEX-US form and none for the others, in [0, 1].
    assert share[present].between(0, 1).all()
    assert share[~present].isna().all()
    allow = _builder().SCREEN_ALLOW
    rule = (~present | (share < 0.1)) & ~v2["word"].isin(allow)
    assert (v2["nonstandard"] == "1").tolist() == rule.tolist()
    # Never a share of 0.5: sentence-initial capitals put these below it.
    by_word = v2.set_index("word")
    kept = by_word.loc[["what", "how", "why", "maybe", "okay", "yes"]]
    assert (kept["nonstandard"] == "0").all()
    # What the guides and ATTRIBUTION.md say the rule marks, and the two months it keeps.
    marked = by_word.loc[["monday", "january", "american", "god", "ok", "tv",
                          "selfie", "emoji", "covid"]]
    assert (marked["nonstandard"] == "1").all()
    assert (by_word.loc[["march", "may"], "nonstandard"] == "0").all()


def test_en_v2_counts_neighbours_among_the_unmarked_forms_only():
    v2 = _text("en_v2.csv")
    members = v2.loc[v2["reference_member"] == "1", "word"].tolist()
    sample = v2.iloc[::250]
    got = add_neighbourhood(pd.DataFrame({"word": sample["word"].tolist()}), reference=members)
    assert got["n_density"].tolist() == sample["n_density"].astype(int).tolist()
    assert np.round(got["old20"], 3).tolist() == sample["old20"].astype(float).tolist()
    # cat counted caa, cbt, cdt and crt among its 32 neighbours, and the guides name them
    # as forms the screen takes out of the reference.
    by_word = v2.set_index("word")
    cat = by_word.loc["cat"]
    assert int(cat["n_density_raw"]) == 32
    assert int(cat["n_density"]) == 21
    assert (by_word.loc[["caa", "cbt", "cdt", "crt"], "reference_member"] == "0").all()


def test_en_v2_is_lf_and_recorded_in_attribution():
    data = (DERIVED / "en_v2.csv").read_bytes()
    assert b"\r" not in data and data.endswith(b"\n")
    v2 = _text("en_v2.csv")
    text = (REPO / "corpora" / "ATTRIBUTION.md").read_text(encoding="utf-8")
    entry = re.search(r"\('en_v2'\)\*\*, (\d+) words, .* (\d+) forms marked `nonstandard`, "
                      r"and N and OLD20 computed by lexsync against the other (\d+)\.", text)
    assert entry, "ATTRIBUTION.md has no entry for en_v2.csv"
    assert int(entry.group(1)) == len(v2)
    assert int(entry.group(2)) == int((v2["nonstandard"] == "1").sum())
    assert int(entry.group(3)) == int((v2["reference_member"] == "1").sum())


def test_en_v2_rebuilds_byte_for_byte_from_the_cached_subtlex_us():
    builder = _builder()
    tsv = builder.RAW / builder.SUBTLEX_US_FILE
    if not tsv.exists():
        pytest.skip("SUBTLEX-US is not cached in corpora/raw/; "
                    "python corpora/fetch_corpora.py --screen-en fetches it")
    assert builder.screen_en(tsv) == (DERIVED / "en_v2.csv").read_bytes(), (
        "rebuild with python corpora/fetch_corpora.py --screen-en")


def test_the_english_example_slices_rebuild_byte_for_byte(tmp_path, monkeypatch):
    # Both packages bundle the slice that `fetch_corpora.py --slice-en` writes from the
    # forms en_v2.csv keeps, with LF line ends on every platform.
    builder = _builder()
    monkeypatch.setattr(builder, "PACKAGE_DATA_DIRS", (tmp_path,))
    assert builder.write_screened_slice() == 3000
    rebuilt = (tmp_path / "en_example.csv").read_bytes()
    assert b"\r" not in rebuilt
    for package in (REPO / "R_workflow" / "inst" / "extdata",
                    REPO / "python_workflow" / "src" / "lexsync" / "data"):
        assert (package / "en_example.csv").read_bytes() == rebuilt, (
            f"{package}: rebuild with python corpora/fetch_corpora.py --slice-en")


def test_a_subtlex_us_copy_with_other_bytes_is_refused(tmp_path):
    builder = _builder()
    other = tmp_path / builder.SUBTLEX_US_FILE
    other.write_bytes(b"Word\tFREQcount\tCDcount\tFREQlow\nthe\t1\t1\t1\n")
    with pytest.raises(SystemExit, match="SHA-256"):
        builder.subtlex_us(other)
