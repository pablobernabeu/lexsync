"""A design's `exclude_words`: words taken out of the candidates before the pool filters.

A lexicon holds forms a study may not want, names and offensive words among them. No filter
on its columns can remove a word the researcher has simply decided against, since a range
filter on a norm table drops every word the table does not cover as well. `exclude_words`
lists such words in the design, or names a file of them, one per line. Both engines
remove them after the norms join and before the pool filters, from the candidates only:
the neighbourhood reference, and a generated design's list of real words, keep them. The
datasheet records the list with its checksum and the run log the removal.
R_workflow/tests/testthat/test-exclude-words.R holds the R engine to the same tests, by
the same names.
"""
import csv
import hashlib
import json
import os

import pandas as pd
import pytest
import yaml

import lexsync
from lexsync.datasheet import methods_paragraph, render_datasheet_md
from lexsync.design import validate_design
from lexsync.generation import build_lexdec_stimuli
from lexsync.querying import _read_exclude_words, add_neighbourhood, build_pool, load_lexicon
from lexsync.run_pipeline import run_pipeline

# The words of the letter-substitution tests in test_generation_exclude.py. Against these
# alone, 'cat' becomes the pseudoword 'cag'.
LEX = ["cat", "cap", "car", "can", "cab", "bat", "bad", "bag", "ban",
       "rat", "ran", "ram", "rag", "tan", "tap", "tar", "mat", "map", "man"]
NAME = "en_exclude"


def _data(name):
    return os.path.join(os.path.dirname(lexsync.__file__), "data", name)


def _posix(path):
    return str(path).replace("\\", "/")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _key(word):
    return word.encode("utf-8")


def _design(tmp_path, exclude=None, lexicon=None, match_on=("length",), tag="design"):
    design = {"name": NAME, "language": "english",
              "lexicon": _posix(lexicon or _data("en_example.csv")),
              "n_per_condition": 6,
              "pool_filters": {"length": [4, 7]},
              "conditions": [{"name": "high", "define_by": {"frequency": [5.0, 7.0]}},
                             {"name": "low", "define_by": {"frequency": [3.0, 4.0]}}],
              "match_on": list(match_on)}
    if exclude is not None:
        design["exclude_words"] = exclude
    path = tmp_path / f"{tag}.yaml"
    path.write_text(yaml.safe_dump(design, allow_unicode=True), encoding="utf-8")
    return str(path)


def _run(tmp_path, tag, **kwargs):
    out = str(tmp_path / tag)
    run_pipeline(_design(tmp_path, tag=tag, **kwargs), _data("schema.yaml"), out, verbose=False)
    return out


def _datasheet(outdir, name=NAME):
    with open(os.path.join(outdir, "reports", f"{name}_english_datasheet_py.json"),
              encoding="utf-8") as handle:
        return json.load(handle)


def _rows(outdir, name=NAME):
    with open(os.path.join(outdir, "stimuli", f"{name}_english_stimuli_py.csv"),
              encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _stimuli_bytes(outdir):
    with open(os.path.join(outdir, "stimuli", f"{NAME}_english_stimuli_py.csv"), "rb") as handle:
        return handle.read()


def _selected(outdir):
    """The selected words of each condition, in the order of the stimuli file."""
    out: dict = {}
    for r in _rows(outdir):
        out.setdefault(r["condition"], []).append(r["word"])
    return out


def _candidates(ds):
    return {c["condition"]: c["n_candidates"] for c in ds["selection"]["candidate_pool"]}


def _log(outdir):
    with open(os.path.join(outdir, "reports", f"{NAME}_english_run_log_py.md"),
              encoding="utf-8") as handle:
        return handle.read()


def test_exclude_words_as_a_list_removes_exactly_the_listed_words(tmp_path):
    plain = _run(tmp_path, "plain")
    chosen = _selected(plain)
    high, low = chosen["high"][0], chosen["low"][0]
    # Written as a user might: padded and in upper case, with a word the lexicon lacks.
    out = _run(tmp_path, "out", exclude=["  " + high.upper() + " ", low, "zzzz"])
    ds = _datasheet(out)
    listed = sorted([high, low, "zzzz"], key=_key)
    assert ds["materials_source"]["exclusions"] == {
        "path": "inline", "sha256": _sha256("\n".join(listed).encode("utf-8")),
        "n_listed": 3, "n_removed": 2}
    got = _selected(out)
    assert high not in got["high"] + got["low"]
    assert low not in got["high"] + got["low"]
    # Each word was a candidate of the condition it had been selected for, so each
    # condition lost one candidate and no other.
    before = _candidates(_datasheet(plain))
    assert _candidates(ds) == {"high": before["high"] - 1, "low": before["low"] - 1}
    assert ("exclude_words: removed 2 of the 3 listed word(s) from the candidates (inline)"
            in _log(out))
    # Excluding the words selects what a lexicon without them selects. The ids differ,
    # since they number the lexicon's rows, so the rows are compared without them.
    src = pd.read_csv(_data("en_example.csv"), dtype=str, keep_default_na=False)
    smaller = tmp_path / "smaller.csv"
    src[~src["word"].isin([high, low])].to_csv(smaller, index=False, lineterminator="\n")
    alone = _run(tmp_path, "alone", lexicon=smaller)

    def strip(rows):
        return [{k: v for k, v in r.items() if k != "id"} for r in rows]
    assert strip(_rows(out)) == strip(_rows(alone))


def test_exclude_words_from_a_file_selects_as_the_inline_list_does(tmp_path):
    plain = _run(tmp_path, "plain")
    chosen = _selected(plain)
    high, low = chosen["high"][0], chosen["low"][0]
    inline = _run(tmp_path, "inline", exclude=[high, low, "zzzz"])
    listing = tmp_path / "leave_out.txt"
    # A byte-order mark, CRLF line ends, a comment, a blank line, padding, upper case and
    # a repeat, all of which the reader normalises as a lexicon's words are read.
    listing.write_bytes(("\ufeff# words to leave out, one per line\r\n" + high.upper()
                         + "\r\n\r\n  " + low + " \r\nzzzz\r\n" + low + "\r\n").encode("utf-8"))
    out = _run(tmp_path, "file", exclude={"path": _posix(listing)})
    assert _stimuli_bytes(out) == _stimuli_bytes(inline)
    ds = _datasheet(out)
    assert ds["materials_source"]["exclusions"] == {
        "path": _posix(listing), "sha256": _sha256(listing.read_bytes()),
        "n_listed": 3, "n_removed": 2}
    assert ("An exclusion list (leave_out.txt) removed 2 words from the candidates before "
            "selection.") in methods_paragraph(ds)
    assert ("An exclusion list in the design removed 2 words from the candidates before "
            "selection.") in methods_paragraph(_datasheet(inline))
    assert "exclusion list" not in methods_paragraph(_datasheet(plain))
    assert "exclusions" not in _datasheet(plain)["materials_source"]
    assert ("- **Excluded words:** `%s` (3 words, 2 removed, sha256 `%s"
            % (_posix(listing), _sha256(listing.read_bytes())[:16])) in render_datasheet_md(ds)


def test_exclude_words_is_refused_for_an_item_table(schema):
    design = {"name": "t", "language": "english", "paradigm": "priming",
              "items": {"source": "table", "path": "items/priming_pairs_en.csv"},
              "exclude_words": ["dog"]}
    with pytest.raises(ValueError, match="exclude_words has no effect for items.source 'table'"):
        validate_design(design, schema)
    # A corpus design may name it.
    corpus = {"name": "c", "language": "english", "exclude_words": ["dog"]}
    assert validate_design(corpus, schema) == []


# {} is a mapping without a path in both engines' YAML readers, not an empty list.
@pytest.mark.parametrize("value", [["dog", True], [3], 5, {"file": "words.txt"},
                                   {"path": ["a.txt", "b.txt"]}, {"path": "  "}, {}])
def test_exclude_words_must_list_words_or_name_a_file(schema, value):
    design = {"name": "c", "language": "english", "exclude_words": value}
    with pytest.raises(ValueError, match="exclude_words must be a list of words"):
        validate_design(design, schema)


def test_exclude_words_refuses_a_path_it_must_not_follow(schema):
    design = {"name": "c", "language": "english", "exclude_words": {"path": "../words.txt"}}
    with pytest.raises(ValueError, match=r"exclude_words path must not contain '\.\.'"):
        validate_design(design, schema)
    design["exclude_words"] = {"paht": "words.txt"}
    with pytest.raises(ValueError, match=r"did you mean 'exclude_words\.path'"):
        validate_design(design, schema)


def test_an_exclude_words_file_must_be_readable_utf8_text_with_one_word_a_line(tmp_path):
    missing = _posix(tmp_path / "missing.txt")
    with pytest.raises(ValueError, match="exclude_words names '.*missing.txt', which is not a "
                                         "readable file"):
        _read_exclude_words({"path": missing})
    latin = tmp_path / "latin.txt"
    latin.write_bytes("café\n".encode("latin-1"))
    with pytest.raises(ValueError, match="the exclude_words file .* is not UTF-8 text"):
        _read_exclude_words({"path": _posix(latin)})
    # UTF-16 saved without a byte-order mark decodes as UTF-8 with a NUL after every
    # letter, so its words would match nothing while the datasheet counted them.
    utf16 = tmp_path / "utf16.txt"
    utf16.write_bytes("dog\ncat\n".encode("utf-16-le"))
    with pytest.raises(ValueError, match="the exclude_words file .* is not UTF-8 text"):
        _read_exclude_words({"path": _posix(utf16)})
    # A table read one row a word would exclude nothing while the datasheet counted its
    # rows. A comment may hold a comma, but a word may not.
    table = tmp_path / "table.txt"
    table.write_bytes(b"# word, reason\ndog\ncat,taboo\n")
    with pytest.raises(ValueError, match="line 3 of the exclude_words file .* holds a tab"):
        _read_exclude_words({"path": _posix(table)})


def test_a_lone_word_is_a_list_of_one():
    one = _read_exclude_words(" Dog ")
    assert one["words"] == ["dog"]
    assert one["record"] == {"path": "inline", "sha256": _sha256(b"dog"), "n_listed": 1}
    empty = _read_exclude_words([])
    assert empty == {"words": [], "record": {"path": "inline", "sha256": _sha256(b""),
                                             "n_listed": 0}}


def test_a_generated_design_keeps_excluded_words_out_of_its_pseudowords(tmp_path):
    # 'cag' is a word of this lexicon. Removed from the base words, it must still be one
    # the pseudowords avoid: against the other words alone, 'cat' would become 'cag'.
    words = LEX + ["cag"]
    freq = {"cat": "5.0", "man": "5.0", "cag": "5.0"}
    lexicon = tmp_path / "lexicon.csv"
    lexicon.write_text("word,freq_zipf\n" + "".join(f"{w},{freq.get(w, '3.0')}\n" for w in words),
                       encoding="utf-8")
    design = {"name": NAME, "language": "english", "paradigm": "lexical_decision",
              "items": {"source": "generate", "lexicon": _posix(lexicon)},
              "n_per_condition": 2, "pool_filters": {"frequency": [4.5, 6.0]},
              "exclude_words": ["cag"]}
    path = tmp_path / "design.yaml"
    path.write_text(yaml.safe_dump(design), encoding="utf-8")
    out = str(tmp_path / "out")
    run_pipeline(str(path), _data("schema.yaml"), out, verbose=False)
    rows = _rows(out)
    real = sorted(r["target"] for r in rows if r["condition"] == "word")
    pseudo = sorted(r["target"] for r in rows if r["condition"] == "pseudoword")
    assert real == ["cat", "man"]
    assert "cag" not in pseudo
    want = build_lexdec_stimuli(pd.DataFrame({"word": ["cat", "man"], "length": [3, 3]}), 2,
                                reference_words=words)
    assert pseudo == sorted(want.loc[want["condition"] == "pseudoword", "target"])
    ds = _datasheet(out)
    assert ds["materials_source"]["exclusions"]["n_removed"] == 1
    assert ds["selection"]["candidate_pool"] == [{"condition": "words in band",
                                                  "n_candidates": 2}]


def test_excluded_words_stay_in_the_neighbourhood_reference(tmp_path, schema):
    # A lexicon without N and OLD20, so the run derives OLD20 for the pool. Every word
    # beginning with b is excluded, and the selected words' OLD20 must still count them
    # among the neighbours.
    src = pd.read_csv(_data("en_example.csv"), dtype=str, keep_default_na=False)
    bare = tmp_path / "bare.csv"
    src[["word", "freq_zipf"]].to_csv(bare, index=False, lineterminator="\n")
    gone = sorted(w for w in src["word"] if w.startswith("b"))
    out = _run(tmp_path, "out", lexicon=bare, exclude=gone, match_on=("length", "old20"))
    rows = _rows(out)
    assert rows and not any(r["word"].startswith("b") for r in rows)
    lex = load_lexicon(str(bare), schema, language="english")
    chosen = pd.DataFrame({"word": [r["word"] for r in rows]})
    whole = add_neighbourhood(chosen, reference=lex["word"].tolist())
    without = add_neighbourhood(chosen, reference=[w for w in lex["word"] if w not in gone])
    got = [round(float(r["old20"]), 6) for r in rows]
    assert got == [round(v, 6) for v in whole["old20"]]
    # The check has teeth: against the reference without them, some OLD20 differs.
    assert got != [round(v, 6) for v in without["old20"]]
    # The candidates lost them all the same.
    pool = build_pool(lex[~lex["word"].isin(gone)], {"length": [4, 7]})
    assert _candidates(_datasheet(out)) == {
        "high": len(build_pool(pool, {"frequency": [5.0, 7.0]})),
        "low": len(build_pool(pool, {"frequency": [3.0, 4.0]}))}
