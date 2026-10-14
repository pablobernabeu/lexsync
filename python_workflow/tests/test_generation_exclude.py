"""Known-form lists for generated pseudowords, and the eligible-candidate count.

The generators checked a candidate only against the reference lexicon, whose English
and Spanish forms stop at Zipf 2.95 and 3.11, so genuine low-frequency words (crier,
pall; in Spanish renos, esteras) passed as pseudowords. `items.generation.exclude`
names further word forms no pseudoword may equal. R_workflow/tests/testthat/
test-generation-exclude.R holds the R engine to the same tests, by the same names.
"""
import csv
import hashlib
import json
import os

import pandas as pd
import pytest
import yaml

import lexsync
from lexsync import corpora
from lexsync.datasheet import methods_paragraph
from lexsync.generation import (
    _lexdec_eligible,
    _read_known_forms,
    build_lexdec_stimuli,
    generate_pseudowords,
    generate_pseudowords_subsyllabic,
)
from lexsync.querying import build_pool, load_lexicon
from lexsync.run_pipeline import run_pipeline

LEX = ["cat", "cap", "car", "can", "cab", "bat", "bad", "bag", "ban",
       "rat", "ran", "ram", "rag", "tan", "tap", "tar", "mat", "map", "man"]
REF = ["planet", "bridge", "strength", "brake", "grape", "plane", "clip", "drum",
       "garden", "market", "basket", "winter", "silver", "butter", "letter", "better",
       "bitter", "banner", "dinner", "manner"]
BAND = {"length": [4, 7], "frequency": [3.5, 6.0]}


def _data(name):
    return os.path.join(os.path.dirname(lexsync.__file__), "data", name)


def _sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _posix(path):
    return str(path).replace("\\", "/")


def test_an_exclusion_forces_the_next_best_candidate():
    # Without the list, 'cat' becomes 'cag'. Excluding it, written as a user might
    # (padded, upper case), leaves the next-best candidate, and 'man' keeps its own.
    before = generate_pseudowords(["cat", "man"], LEX)
    assert before["pseudoword"].tolist() == ["cag", "mag"]
    after = generate_pseudowords(["cat", "man"], LEX, exclude=[" CAG "])
    assert after["pseudoword"].tolist() == ["tat", "mag"]
    # An excluded form that was never chosen changes nothing.
    assert generate_pseudowords(["cat", "man"], LEX, exclude=["zzz"]).equals(before)


def test_an_exclusion_reaches_the_subsyllabic_generator():
    before = generate_pseudowords_subsyllabic(["garden", "winter"], REF)
    assert before["pseudoword"].tolist() == ["gerder", "wittet"]
    after = generate_pseudowords_subsyllabic(["garden", "winter"], REF, exclude=["gerder"])
    assert after["pseudoword"].tolist() == ["garder", "wittet"]


def test_build_lexdec_stimuli_passes_the_exclusion_on():
    pool = pd.DataFrame({"word": ["cat", "man"], "length": [3, 3]})
    base = build_lexdec_stimuli(pool, 2, reference_words=LEX)
    assert base.loc[base["condition"] == "pseudoword", "target"].tolist() == ["cag", "mag"]
    out = build_lexdec_stimuli(pool, 2, reference_words=LEX, exclude=["cag"])
    assert out.loc[out["condition"] == "pseudoword", "target"].tolist() == ["tat", "mag"]


def test_known_forms_are_read_from_text_and_csv_files(tmp_path):
    txt = tmp_path / "known.txt"
    # A byte-order mark, CRLF line ends, a comment, a blank line, padding, upper case
    # and a decomposed accent, all of which the reader normalises as a lexicon is read.
    txt.write_bytes("\ufeff# known forms\r\nCrier\r\n\r\n  pall \r\nrene\u0301\r\npall\r\n"
                    .encode())
    table = tmp_path / "extra.csv"
    table.write_text("word,freq\ntiter,1.2\nCrier,2\n", encoding="utf-8")
    got = _read_known_forms([str(txt), str(table)])
    assert got["forms"] == ["crier", "pall", "ren\u00e9", "titer"]
    assert got["records"] == [
        {"source": _posix(txt), "sha256": _sha256(txt), "n_forms": 3},
        {"source": _posix(table), "sha256": _sha256(table), "n_forms": 2}]
    # A single path is a list of one.
    assert _read_known_forms(str(table))["forms"] == ["crier", "titer"]


def test_a_known_form_csv_without_a_word_column_is_refused(tmp_path):
    table = tmp_path / "bad.csv"
    table.write_text("form\ncrier\n", encoding="utf-8")
    with pytest.raises(ValueError, match="has no 'word' column"):
        _read_known_forms([str(table)])


def test_a_known_form_list_that_is_a_table_or_not_utf8_is_refused(tmp_path):
    # A tab-separated .txt (SUBTLEX-US's layout) was read whole, one row per form, so
    # it excluded nothing while the datasheet counted its rows. A comment may hold a
    # comma; a form may not.
    table = tmp_path / "subtlex.txt"
    table.write_bytes(b"# rows, as served\nWord\tFREQcount\ncrier\t17\n")
    with pytest.raises(ValueError, match="line 2 of the known-form list .* holds a tab"):
        _read_known_forms([str(table)])
    (tmp_path / "commas.txt").write_bytes(b"crier\npall,23\n")
    with pytest.raises(ValueError, match="line 2 of the known-form list"):
        _read_known_forms([str(tmp_path / "commas.txt")])
    # A Latin-1 file was misread in one engine and read as no forms in the other.
    latin = tmp_path / "latin.txt"
    latin.write_bytes("café\n".encode("latin-1"))
    with pytest.raises(ValueError, match="is not UTF-8 text"):
        _read_known_forms([str(latin)])


def test_a_known_form_entry_that_names_nothing_is_refused(tmp_path):
    with pytest.raises(ValueError, match="neither a readable file nor a corpus in the registry"):
        _read_known_forms([str(tmp_path / "missing.txt")])
    with pytest.raises(ValueError, match="must list file paths or registry corpus names"):
        _read_known_forms([3])


def test_a_registry_name_without_a_cached_corpus_is_refused_with_the_fetch_hint(
        tmp_path, monkeypatch):
    monkeypatch.setattr(corpora, "cache_dir", lambda: str(tmp_path / "cache"))
    with pytest.raises(ValueError, match=r"fetch_corpus\('subtlex_us'\)"):
        _read_known_forms(["subtlex_us"])
    # Once fetched, the corpus's registered word column is read: SUBTLEX-US names it
    # 'Word', and openlexicon serves it tab-separated.
    (tmp_path / "cache").mkdir()
    cached = tmp_path / "cache" / "subtlex_us.csv"
    cached.write_bytes(b"Word\tFREQcount\nCrier\t17\npall\t23\n")
    got = _read_known_forms(["subtlex_us"])
    assert got["forms"] == ["crier", "pall"]
    assert got["records"] == [{"source": "subtlex_us", "sha256": _sha256(cached),
                               "n_forms": 2}]


def _in_letters(words):
    """How many of the words are written wholly in letters, by Python's own str."""
    return sum(isinstance(w, str) and w.isalpha() for w in words)


def test_a_band_counts_the_words_written_in_attested_letters_as_eligible(schema):
    # Every word of the Spanish band is written in letters the lexicon attests, its
    # accented words included, which the a-z filter left out.
    lex = load_lexicon(_data("es_example.csv"), schema, "spanish")
    band = build_pool(lex, BAND)
    eligible = _lexdec_eligible(band, lex["word"].tolist())
    assert eligible["word"].tolist() == band["word"].tolist()
    assert _in_letters(band["word"]) == len(band)
    assert any(not w.isascii() for w in eligible["word"])
    # A hyphen, a digit or a letter the reference lacks still leaves a word out.
    pool = pd.DataFrame({"word": ["año", "e-mail", "mar2", "über", "casa"]})
    got = _lexdec_eligible(pool, ["año", "casa", "mar", "email"])
    assert got["word"].tolist() == ["año", "casa"]


def _write_generate_design(tmp_path, exclude=None):
    design = {"name": "es_lexdec_count", "language": "spanish",
              "paradigm": "lexical_decision",
              "items": {"source": "generate", "lexicon": _posix(_data("es_example.csv"))},
              "n_per_condition": 6, "pool_filters": BAND}
    if exclude is not None:
        design["items"]["generation"] = {"exclude": exclude}
    path = tmp_path / "design.yaml"
    path.write_text(yaml.safe_dump(design, allow_unicode=True), encoding="utf-8")
    return str(path)


def _datasheet(outdir):
    with open(os.path.join(outdir, "reports", "es_lexdec_count_spanish_datasheet_py.json"),
              encoding="utf-8") as handle:
        return json.load(handle)


def _pseudowords(outdir):
    with open(os.path.join(outdir, "stimuli", "es_lexdec_count_spanish_stimuli_py.csv"),
              encoding="utf-8", newline="") as handle:
        return sorted(r["target"] for r in csv.DictReader(handle)
                      if r["condition"] == "pseudoword")


def test_a_generated_design_reports_the_words_the_generator_could_use(tmp_path, schema):
    # The record counted the band before the letter filter. It now counts the words
    # written in letters the lexicon attests, which in this band, accents and all, is
    # every word. parity/twin_edge/generation_exclude holds both engines to a band with
    # a hyphenated word, which the filter leaves out.
    band = build_pool(load_lexicon(_data("es_example.csv"), schema, "spanish"), BAND)
    out = str(tmp_path / "out")
    run_pipeline(_write_generate_design(tmp_path), _data("schema.yaml"), out, verbose=False)
    ds = _datasheet(out)
    assert ds["selection"]["candidate_pool"] == [
        {"condition": "words in band", "n_candidates": _in_letters(band["word"])}]
    assert _in_letters(band["word"]) > int(band["word"].str.fullmatch(r"[a-z]+").sum())
    assert "generation_exclude" not in ds["selection"]


def test_a_generated_design_records_its_known_form_lists(tmp_path):
    plain = str(tmp_path / "plain")
    run_pipeline(_write_generate_design(tmp_path), _data("schema.yaml"), plain, verbose=False)
    first = _pseudowords(plain)[0]
    known = tmp_path / "known.txt"
    known.write_bytes((first + "\n").encode("utf-8"))
    out = str(tmp_path / "out")
    run_pipeline(_write_generate_design(tmp_path, [_posix(known)]), _data("schema.yaml"),
                 out, verbose=False)
    ds = _datasheet(out)
    assert ds["selection"]["generation_exclude"] == [
        {"source": _posix(known), "sha256": _sha256(known), "n_forms": 1}]
    assert first not in _pseudowords(out)
    assert ds["selection"]["candidate_pool"] == _datasheet(plain)["selection"]["candidate_pool"]
    assert ("Besides the lexicon, pseudowords were checked against 1 known word form "
            "(known.txt).") in methods_paragraph(ds)
    assert "known word form" not in methods_paragraph(_datasheet(plain))
