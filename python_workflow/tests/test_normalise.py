"""normalise_lexicon(): a corpus file in its publisher's layout, made into a lexicon.

Neither engine could read a SUBTLEX-format file without renaming its columns, turning
tabs into commas and converting frequencies per million to Zipf by hand, although the
registry described every one of those steps. R_workflow/tests/testthat/test-normalise.R
holds the R engine to the same tests, by the same names, and to the same bytes, which
helper_corpus_files.py and its R twin pin.
"""
import json

import pandas as pd
import pytest
import yaml
from helper_corpus_files import (
    LEXIQUE,
    LEXIQUE_ENTRY,
    LEXIQUE_FIRST,
    LEXIQUE_SUM,
    NEAR_BOUNDARY,
    PER_MILLION,
    PER_MILLION_LEXICON,
    PER_MILLION_MAP,
    SUBTLEX_US,
    SUBTLEX_US_LEXICON,
    SUBTLEX_US_MAP,
    TAB_ZIPF,
    TAB_ZIPF_LEXICON,
)

from lexsync import load_lexicon, normalise_lexicon, run_pipeline


def _write(tmp_path, name, text):
    path = tmp_path / name
    path.write_bytes(text.encode("utf-8"))
    return str(path)


def _bytes(path):
    with open(path, "rb") as handle:
        return handle.read().decode("utf-8")


def test_normalise_lexicon_derives_zipf_from_a_subtlex_us_table(tmp_path, schema, capsys):
    src = _write(tmp_path, "SUBTLEXus.tsv", SUBTLEX_US)
    out = str(tmp_path / "subtlex_us.csv")
    lex = normalise_lexicon(src, columns=SUBTLEX_US_MAP, out=out)
    assert _bytes(out) == SUBTLEX_US_LEXICON
    assert lex.attrs["normalisation"] == {
        "n_read": 5, "n_forms": 5, "n_merged": 0, "duplicates": "first",
        "zipf_derived": True, "near_boundary": 0}
    assert capsys.readouterr().out == (
        "lexsync: normalised 5 forms from 'SUBTLEXus.tsv'; 0 of the Zipf values "
        "derived from frequencies per million lay within 1e-9 of a rounding boundary.\n")
    loaded = load_lexicon(out, schema)
    assert loaded["word"].tolist() == ["cat", "dog", "the", "you", "zebra"]


def test_normalise_lexicon_reads_a_per_million_csv(tmp_path):
    src = _write(tmp_path, "esp.csv", PER_MILLION)
    out = str(tmp_path / "esp_lexicon.csv")
    lex = normalise_lexicon(src, columns=PER_MILLION_MAP, out=out)
    assert _bytes(out) == PER_MILLION_LEXICON
    assert lex["word"].tolist() == ["café", "de", "niño", "árbol"]


def test_normalise_lexicon_detects_a_tab_separated_file(tmp_path, capsys):
    src = _write(tmp_path, "words.txt", TAB_ZIPF)
    out = str(tmp_path / "words.csv")
    lex = normalise_lexicon(src, out=out)
    assert _bytes(out) == TAB_ZIPF_LEXICON
    assert lex.attrs["normalisation"]["zipf_derived"] is False
    assert capsys.readouterr().out == "lexsync: normalised 2 forms from 'words.txt'.\n"


def test_normalise_lexicon_sums_duplicate_forms(tmp_path):
    src = _write(tmp_path, "Lexique383.tsv", LEXIQUE)
    out = str(tmp_path / "lexique.csv")
    lex = normalise_lexicon(src, entry=LEXIQUE_ENTRY, out=out)
    assert _bytes(out) == LEXIQUE_SUM
    assert lex.attrs["normalisation"]["n_merged"] == 1
    assert lex.attrs["normalisation"]["duplicates"] == "sum"
    # Without the entry's rule the first row of a repeated form is kept.
    normalise_lexicon(src, columns=LEXIQUE_ENTRY["columns"], out=out)
    assert _bytes(out) == LEXIQUE_FIRST


def test_normalise_lexicon_counts_values_near_a_rounding_boundary(tmp_path):
    # Only the count is pinned: the value itself is the one the engines may round apart.
    lex = normalise_lexicon(_write(tmp_path, "edge.csv", NEAR_BOUNDARY))
    assert lex.attrs["normalisation"]["near_boundary"] == 1


def test_normalise_lexicon_takes_a_registry_entry_by_name(tmp_path):
    src = _write(tmp_path, "SUBTLEXus.tsv", SUBTLEX_US)
    out = str(tmp_path / "subtlex_us.csv")
    normalise_lexicon(src, entry="subtlex_us", out=out)
    assert _bytes(out) == SUBTLEX_US_LEXICON


@pytest.mark.parametrize("value", ["0", "-1.5"])
def test_normalise_lexicon_refuses_non_positive_frequencies(tmp_path, value):
    src = _write(tmp_path, "zero.csv", "word,freq_permillion\ndog,12.5\ncat,%s\n" % value)
    with pytest.raises(ValueError, match=r"'freq_permillion' holds %s for 'cat'.*positive"
                                         % value.replace(".", r"\.")):
        normalise_lexicon(src)


def test_normalise_lexicon_refuses_an_unusable_map(tmp_path):
    src = _write(tmp_path, "SUBTLEXus.tsv", SUBTLEX_US)
    with pytest.raises(ValueError, match="has no column 'Zipf'"):
        normalise_lexicon(src, columns={"word": "Word", "freq_zipf": "Zipf"})
    with pytest.raises(ValueError, match="freq_zipf or freq_permillion, not both"):
        normalise_lexicon(src, columns={"word": "Word", "freq_zipf": "Lg10WF",
                                        "freq_permillion": "SUBTLWF"})
    with pytest.raises(ValueError, match="unknown key 'lemma'"):
        normalise_lexicon(src, columns={"word": "Word", "lemma": "Word",
                                        "freq_permillion": "SUBTLWF"})
    with pytest.raises(ValueError, match="duplicates: sum adds frequencies per million"):
        normalise_lexicon(src, entry={"columns": {"word": "Word", "freq_zipf": "Lg10WF"},
                                      "duplicates": "sum"})
    with pytest.raises(ValueError, match="duplicates must be 'first' or 'sum'"):
        normalise_lexicon(src, entry={"columns": SUBTLEX_US_MAP, "duplicates": "mean"})
    with pytest.raises(ValueError, match="no column named freq_zipf or freq_permillion"):
        normalise_lexicon(src, columns={"word": "Word"})


def test_a_run_over_a_lexicon_with_frequencies_per_million_records_the_boundary_count(
        tmp_path, en_lexicon_path):
    # The example slice with a rate per million on every row, as normalise_lexicon()
    # writes one. log10(1.5) + 3 is 3.176..., far from a rounding boundary.
    with open(en_lexicon_path, "rb") as handle:
        lines = handle.read().decode("utf-8").split("\n")
    body = [lines[0] + ",freq_permillion"] + [ln + ",1.5" for ln in lines[1:] if ln]
    lexicon = tmp_path / "per_million.csv"
    lexicon.write_bytes(("\n".join(body) + "\n").encode("utf-8"))
    design = {"name": "en_pm", "language": "english",
              "lexicon": str(lexicon).replace("\\", "/"),
              "n_per_condition": 4, "pool_filters": {"length": [4, 7]},
              "conditions": [{"name": "high", "define_by": {"frequency": [5.0, 7.0]}},
                             {"name": "low", "define_by": {"frequency": [3.0, 4.0]}}],
              "match_on": ["length"]}
    path = tmp_path / "design.yaml"
    path.write_text(yaml.safe_dump(design), encoding="utf-8")
    out = tmp_path / "out"
    from conftest import _pkg_data
    run_pipeline(str(path), _pkg_data("schema.yaml"), str(out), verbose=False)
    with open(out / "reports" / "en_pm_english_datasheet_py.json", encoding="utf-8") as handle:
        ds = json.load(handle)
    n = len(body) - 1
    assert ds["materials_source"]["zipf_derivation"] == {"n_values": n, "near_boundary": 0}
    log = (out / "reports" / "en_pm_english_run_log_py.md").read_text(encoding="utf-8")
    assert ("freq_permillion: 0 of %d value(s) put Zipf within 1e-9 of a rounding "
            "boundary" % n) in log
    md = (out / "reports" / "en_pm_english_datasheet_py.md").read_text(encoding="utf-8")
    assert ("- **Zipf from frequencies per million:** 0 of %d value(s) within 1e-9 of a "
            "rounding boundary" % n) in md
    # A lexicon without the column, every shipped one included, carries no record.
    design["lexicon"] = en_lexicon_path.replace("\\", "/")
    path.write_text(yaml.safe_dump(design), encoding="utf-8")
    run_pipeline(str(path), _pkg_data("schema.yaml"), str(out), verbose=False)
    with open(out / "reports" / "en_pm_english_datasheet_py.json", encoding="utf-8") as handle:
        assert "zipf_derivation" not in json.load(handle)["materials_source"]


def test_normalise_lexicon_without_out_writes_nothing(tmp_path):
    src = _write(tmp_path, "Lexique383.tsv", LEXIQUE)
    lex = normalise_lexicon(src, entry=LEXIQUE_ENTRY)
    assert isinstance(lex, pd.DataFrame)
    assert list(lex.columns) == ["word", "freq_zipf", "freq_permillion"]
    assert lex["freq_zipf"].tolist() == [4.756, 3.497, 3.722]
    assert sorted(p.name for p in tmp_path.iterdir()) == ["Lexique383.tsv"]
