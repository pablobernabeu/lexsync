"""The English demonstrations select from the screened lexicon and leave out unsuitable words.

The demonstrations read corpora/derived/en.csv, which keeps every form wordfreq returns,
and broke exact ties by spelling. Their low-frequency conditions filled with names,
acronyms and early-alphabet words, and their selections held taboo words (bitch, boobs
and fuck). They now read en_v2.csv with `nonstandard: [0, 0]`, leave out the words of
config/exclude_en_demo.txt, check generated pseudowords against wordfreq's fuller list of
English forms, and break ties by the keyed hash. These tests hold the committed outputs to
that. They read the repository's designs, lexica and outputs, so they skip outside a
checkout. R_workflow/tests/testthat/test-demonstrations.R holds the R engine's outputs to
the same tests, by the same names.
"""
import json

import pandas as pd
import pytest
from helper_repo import REPO

from lexsync.io_utils import read_config, sha256_file

pytestmark = pytest.mark.skipif(REPO is None,
                                reason="the demonstrations live in the repository")

V2 = "corpora/derived/en_v2.csv"
EXCLUSIONS = "config/exclude_en_demo.txt"
KNOWN_FORMS = "corpora/derived/en_known_forms.txt"
# The corpus and generated designs, which filter on `nonstandard` and name the exclusions.
SCREENED = ["en_freqcontrast", "en_ndensity", "en_freqcontinuous", "en_balanced_lists",
            "en_resample", "en_richdim", "en_andrews_repro", "en_lexdec", "en_lexdec_blocks",
            "en_lexdec_wuggy"]
GENERATED = ["en_lexdec", "en_lexdec_blocks", "en_lexdec_wuggy"]
# A supplied pool and a pair table, which read en_v2.csv for their dimensions.
SUPPLIED = ["en_supplied_pool", "en_priming_continuous"]


def _design(name):
    return read_config(str(REPO / "config" / f"design_{name}.yaml"))


def _stimuli(name):
    return pd.read_csv(REPO / "output" / "stimuli" / f"{name}_english_stimuli_py.csv",
                       dtype=str, keep_default_na=False, encoding="utf-8")


def _report(name, kind):
    return pd.read_csv(REPO / "output" / "reports" / f"{name}_english_{kind}_py.csv",
                       dtype=str, keep_default_na=False, encoding="utf-8")


def _datasheet(name):
    path = REPO / "output" / "reports" / f"{name}_english_datasheet_py.json"
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _v2():
    return pd.read_csv(REPO / V2, dtype=str, keep_default_na=False, encoding="utf-8")


def _excluded():
    # Read here and not through the package, as the file states: one word per line,
    # blank lines and lines beginning '#' skipped.
    with open(REPO / EXCLUSIONS, encoding="utf-8") as handle:
        lines = [line.strip().lower() for line in handle]
    return [w for w in lines if w and not w.startswith("#")]


def _presented_words(name):
    """The real words a design presents: every selected word, the pseudowords of a
    lexical decision left out, and both members of every pair."""
    s = _stimuli(name)
    if "word" not in s.columns:
        return list(s["prime"]) + list(s["target"])
    return list(s.loc[s["condition"] != "pseudoword", "word"])


def _candidates(design, condition):
    """en_v2's rows that the design's pool filters, its exclusions and the condition's
    window admit, computed from the files and not through the package."""
    v2 = _v2()
    rows = v2[~v2["word"].isin(_excluded())]
    windows = dict(design.get("pool_filters") or {})
    windows.update(next(c for c in design["conditions"]
                        if c["name"] == condition)["define_by"])
    for dim, (lo, hi) in windows.items():
        values = (rows["word"].str.len() if dim == "length"
                  else pd.to_numeric(rows["freq_zipf" if dim == "frequency" else dim]))
        rows = rows[values.between(lo, hi)]
    return rows


def _initial_share(words):
    words = list(words)
    return sum(w[:1] in ("a", "b") for w in words) / len(words)


def test_the_english_demonstrations_read_the_screened_lexicon():
    for name in SCREENED:
        design = _design(name)
        lexicon = design["items"]["lexicon"] if name in GENERATED else design["lexicon"]
        assert lexicon == V2, name
        assert design["pool_filters"]["nonstandard"] == [0, 0], name
        assert design["exclude_words"] == {"path": EXCLUSIONS}, name
    for name in GENERATED:
        assert _design(name)["items"]["generation"]["exclude"] == [KNOWN_FORMS], name
    for name in SUPPLIED:
        assert _design(name)["items"]["lexicon"] == V2, name


def test_the_exclusion_list_holds_only_forms_the_screen_keeps():
    # A listed word that en_v2 lacks, or already marks, would exclude nothing.
    words = _excluded()
    assert words, "the exclusion list is empty"
    assert len(words) == len(set(words))
    v2 = _v2().set_index("word")
    assert set(words) <= set(v2.index)
    assert (v2.loc[words, "nonstandard"] == "0").all()
    with open(REPO / EXCLUSIONS, encoding="utf-8") as handle:
        assert handle.readline().startswith("#"), "the list opens with its criteria"


def test_no_english_demonstration_selects_a_marked_or_excluded_word():
    marked = set(_v2().query("nonstandard == '1'")["word"])
    excluded = set(_excluded())
    known = set(_v2()["word"])
    for name in SCREENED + SUPPLIED:
        words = set(_presented_words(name))
        assert words <= known, (name, sorted(words - known))
        assert not words & marked, (name, sorted(words & marked))
        assert not words & excluded, (name, sorted(words & excluded))


def test_no_andrews_cell_holds_a_marked_or_excluded_form():
    # In lexsync 0.1, 24 of the 36 low-frequency items were forms the screen marks (aclu,
    # adhd, bbq and bmx among them), against none of the 36 high-frequency items.
    flagged = set(_v2().query("nonstandard == '1'")["word"]) | set(_excluded())
    s = _stimuli("en_andrews_repro")
    for cell in ("HF_largeN", "HF_smallN", "LF_largeN", "LF_smallN"):
        words = s.loc[s["condition"] == cell, "word"]
        assert len(words) == 18, cell
        assert not set(words) & flagged, (cell, sorted(set(words) & flagged))


def test_freqcontrast_initials_follow_their_candidates():
    # Spelling broke the ties in lexsync 0.1, and 61% of the low-frequency words began
    # with a or b, against 13% of the candidates.
    design = _design("en_freqcontrast")
    s = _stimuli("en_freqcontrast")
    for condition in ("high_frequency", "low_frequency"):
        share = _initial_share(s.loc[s["condition"] == condition, "word"])
        assert share <= _initial_share(_candidates(design, condition)["word"]) + 0.1, condition


def test_no_english_pseudoword_is_a_known_form():
    with open(REPO / KNOWN_FORMS, encoding="utf-8") as handle:
        known = set(handle.read().split("\n"))
    for name in GENERATED:
        s = _stimuli(name)
        pseudowords = set(s.loc[s["condition"] == "pseudoword", "word"])
        assert pseudowords, name
        assert not pseudowords & known, (name, sorted(pseudowords & known))


def test_freqcontrast_matched_dimensions_remain_equivalent():
    design = _design("en_freqcontrast")
    rows = _report("en_freqcontrast", "comparisons").query("role == 'controlled'")
    assert sorted(rows["dimension"]) == sorted(design["match_on"])
    assert (rows["equivalent"] == "TRUE").all()
    assert (pd.to_numeric(rows["cohens_d"]).abs() < 0.1).all()


def test_the_demonstration_datasheets_record_the_screen():
    sha = sha256_file(str(REPO / EXCLUSIONS))
    known_sha = sha256_file(str(REPO / KNOWN_FORMS))
    for name in SCREENED:
        ds = _datasheet(name)
        source = ds["materials_source"]
        assert "screened against SUBTLEX-US" in source["provenance"], name
        exclusions = source["exclusions"]
        assert exclusions["path"] == EXCLUSIONS and exclusions["sha256"] == sha, name
        assert exclusions["n_listed"] == len(_excluded()), name
        if name in GENERATED:
            assert ds["selection"]["generation_exclude"] == [
                {"source": KNOWN_FORMS, "sha256": known_sha, "n_forms": 289023}], name
        elif "continuous" not in _design(name):
            assert ds["selection"]["tie_break"] == {"rule": "hash", "salt": "lexsync-tie-v1"}
