"""The design's `norms:` block: a semantic dimension joined before the pool is built.

The join itself is merge_norms, tested in test_dimensions.py. What is tested here is
the part that makes it usable and honest: the orchestrator applies the block before
build_pool, so a norm column can be filtered on, matched on and spanned; and every
table it joined is recorded in the materials datasheet with its checksum and its
per-column coverage.

That record is not decoration. A norm table can supply the very variable a design
manipulates, so a run whose datasheet did not name the file would describe a
selection over columns of unstated origin -- unreproducible from the record that
exists to make it reproducible. Coverage is recorded for the same reason: a word the
table does not cover gets a missing value, which takes it out of any selection that
filters, matches or spans on the column.

No norm data is bundled. These tests write their own tiny lexicon and norm table, so
the feature is covered end to end without shipping a norm dataset.

test-norms.R asserts the same properties.
"""
import json
import os
import re

import pandas as pd
import pytest
import yaml

import lexsync
from lexsync.io_utils import read_config
from lexsync.querying import apply_norms, load_lexicon
from lexsync.run_pipeline import run_pipeline

# The bundled schema, as test-norms.R reads, and conftest.py's `schema` fixture with
# it: with their own lexicon and norm table these tests need nothing from the
# repository, so they run from an sdist as well.
BUNDLED_SCHEMA = os.path.join(os.path.dirname(lexsync.__file__), "data", "schema.yaml")

WORDS = ["cat", "dog", "car", "cap", "bat", "bag", "cot", "cog", "rat", "rag",
         "hat", "hag", "pot", "peg", "man", "map"]


def _lexicon(tmp_path, upper=False):
    """A tiny lexicon. `upper` writes the forms in capitals, which load_lexicon folds."""
    path = tmp_path / "lex.csv"
    pd.DataFrame({
        "word": [w.upper() if upper else w for w in WORDS],
        "freq_zipf": [3.0 + 0.2 * i for i in range(len(WORDS))],
    }).to_csv(path, index=False, lineterminator="\n")
    return path


def _norms(tmp_path, covered=None, name="conc.csv"):
    """A norm table covering `covered` of the lexicon (all of it by default)."""
    words = WORDS if covered is None else WORDS[:covered]
    path = tmp_path / name
    pd.DataFrame({
        "word": words,
        # Deliberately not monotonic in frequency, so a filter on concreteness selects
        # a set that a filter on frequency could not have produced by accident.
        "concreteness": [2.0 + (i % 4) for i in range(len(words))],
    }).to_csv(path, index=False, lineterminator="\n")
    return path


def test_apply_norms_joins_and_records_provenance(schema, tmp_path):
    lex = load_lexicon(str(_lexicon(tmp_path)), schema)
    norms_path = _norms(tmp_path)
    out = apply_norms(lex, {"norms": [{"path": str(norms_path)}]})
    assert "concreteness" in out["lexicon"].columns
    rec = out["provenance"][0]
    assert rec["path"] == str(norms_path)
    assert len(rec["sha256"]) == 64
    assert rec["on"] == "word"
    assert rec["columns"] == [{"column": "concreteness", "n_matched": len(WORDS),
                              "n_total": len(WORDS)}]


def test_apply_norms_records_partial_coverage(schema, tmp_path):
    # The uncovered rows carry NaN, which the tolerance windows drop from the pool, so
    # coverage is part of how the pool was defined and belongs in the record.
    lex = load_lexicon(str(_lexicon(tmp_path)), schema)
    out = apply_norms(lex, {"norms": [{"path": str(_norms(tmp_path, covered=10))}]})
    assert out["provenance"][0]["columns"][0] == {
        "column": "concreteness", "n_matched": 10, "n_total": len(WORDS)}


def test_apply_norms_accepts_a_single_bare_mapping(schema, tmp_path):
    # Writing one table as a bare mapping rather than a one-element list is the obvious
    # thing to do in YAML, so it must not be silently ignored.
    lex = load_lexicon(str(_lexicon(tmp_path)), schema)
    out = apply_norms(lex, {"norms": {"path": str(_norms(tmp_path))}})
    assert "concreteness" in out["lexicon"].columns
    assert len(out["provenance"]) == 1


def test_apply_norms_is_a_no_op_without_the_block(schema, tmp_path):
    # Every shipped design lacks a `norms:` block, so this path must not touch the
    # lexicon at all -- otherwise adding the feature would move existing artefacts.
    lex = load_lexicon(str(_lexicon(tmp_path)), schema)
    out = apply_norms(lex, {"name": "x"})
    assert out["provenance"] == []
    assert list(out["lexicon"].columns) == list(lex.columns)
    assert out["lexicon"].equals(lex)


def test_apply_norms_rejects_a_traversing_path(schema, tmp_path):
    lex = load_lexicon(str(_lexicon(tmp_path)), schema)
    with pytest.raises(ValueError, match=r"must not contain '\.\.'"):
        apply_norms(lex, {"norms": [{"path": "../secrets/x.csv"}]})
    with pytest.raises(ValueError, match="needs a `path`"):
        apply_norms(lex, {"norms": [{"columns": ["concreteness"]}]})


def test_apply_norms_folds_the_lexicon_key(schema, tmp_path):
    # load_lexicon case-folds `word`, so an upper-case source still joins. This is the
    # regression guard for the half-folded key: only the norm table's side used to be
    # normalised, and both engines then agreed on an all-NaN dimension.
    lex = load_lexicon(str(_lexicon(tmp_path, upper=True)), schema)
    out = apply_norms(lex, {"norms": [{"path": str(_norms(tmp_path))}]})
    assert out["lexicon"]["concreteness"].notna().all()


# ---- The join key of a norms entry --------------------------------------------
# YAML 1.1 reads a bare `on` as the boolean true in both engines, so the documented
# `on: lemma` reached the join as a key True (named TRUE in R) and every join silently
# used `word`. The key is now written `join_on`. These tests write their entries as
# YAML and read them with read_config, as run_pipeline does, because the defect lived
# in the reading.

ON_NOTE = ("lexsync: read `on:` in a norms entry as the join key; YAML reads a bare `on` "
           "as true, so write `join_on:`.")
FORMS = ["cat", "cats", "dog", "dogs", "mice", "mouse"]
LEMMAS = ["cat", "cat", "dog", "dog", "mouse", "mouse"]


def _lemma_lexicon(tmp_path):
    """Word forms with their lemmas, in byte order, so the lexicon keeps this order."""
    path = tmp_path / "lemma_lex.csv"
    pd.DataFrame({"word": FORMS, "freq_zipf": [4.0 + 0.1 * i for i in range(len(FORMS))],
                  "lemma": LEMMAS}).to_csv(path, index=False, lineterminator="\n")
    return path


def _lemma_norms(tmp_path, with_word=True):
    """A lemma-level norm table. With `with_word`, it also lists each lemma's citation
    form under `word`. A join on `word` then matches only the forms that are their own
    lemma, so the key a join used can be read off its coverage."""
    path = tmp_path / "lemma_norms.csv"
    table = {"lemma": ["cat", "dog", "mouse"], "concreteness": [4.9, 4.8, 4.7]}
    if with_word:
        table = {"word": ["cat", "dog", "mouse"], **table}
    pd.DataFrame(table).to_csv(path, index=False, lineterminator="\n")
    return path


def _norms_entry(tmp_path, entry, norms_path):
    """A design whose single norms entry is the YAML mapping `{path: ..., <entry>}`."""
    path = tmp_path / "norms_entry.yaml"
    path.write_text("norms:\n  - {path: %s, %s}\n" % (str(norms_path).replace("\\", "/"), entry),
                    encoding="utf-8")
    return read_config(str(path))


BY_LEMMA = [4.9, 4.9, 4.8, 4.8, 4.7, 4.7]


def _joined(out):
    return [None if v != v else v for v in out["lexicon"]["concreteness"].tolist()]


def test_a_bare_on_key_is_read_as_the_join_key(schema, tmp_path):
    """Pinned identically in test-norms.R."""
    lex = load_lexicon(str(_lemma_lexicon(tmp_path)), schema)
    design = _norms_entry(tmp_path, "on: lemma, columns: [concreteness]", _lemma_norms(tmp_path))
    out = apply_norms(lex, design)
    assert _joined(out) == BY_LEMMA
    assert out["provenance"][0]["on"] == "lemma"
    assert out["notes"] == [ON_NOTE]


def test_join_on_names_the_join_key_and_wins_over_on(schema, tmp_path):
    """`join_on` joins with no note, and so does a quoted 'on'. Given both, `join_on`
    wins. Without either, the join uses `word`, which covers only the forms that are
    their own lemma. Pinned identically in test-norms.R."""
    lex = load_lexicon(str(_lemma_lexicon(tmp_path)), schema)
    norms_path = _lemma_norms(tmp_path)
    for entry in ("join_on: lemma", "'on': lemma", "join_on: lemma, on: word",
                  "join_on: lemma, 'on': word"):
        out = apply_norms(lex, _norms_entry(tmp_path, entry + ", columns: [concreteness]",
                                            norms_path))
        assert _joined(out) == BY_LEMMA, entry
        assert out["provenance"][0]["on"] == "lemma", entry
        assert out["notes"] == [], entry
    out = apply_norms(lex, _norms_entry(tmp_path, "columns: [concreteness]", norms_path))
    assert _joined(out) == [4.9, None, 4.8, None, None, 4.7]
    assert out["provenance"][0]["on"] == "word"


def test_an_unknown_key_in_a_norms_entry_is_refused(schema, tmp_path):
    """A misspelt `join_on` fell back to `word` as silently as the bare `on` did. A key
    YAML reads as false is named as R names it. Pinned identically in test-norms.R."""
    lex = load_lexicon(str(_lemma_lexicon(tmp_path)), schema)
    norms_path = _lemma_norms(tmp_path)
    for entry, key in (("joinon: lemma", "joinon"), ("off: lemma", "FALSE")):
        with pytest.raises(ValueError, match=re.escape(
                "lexsync: unknown key '%s' in a norms entry; known keys: path, join_on, "
                "columns." % key)):
            apply_norms(lex, _norms_entry(tmp_path, entry, norms_path))
    # A single entry written as a bare mapping is checked in the same way. The R engine
    # took a bare mapping without `path` for a list of entries, so it reported the
    # missing path where this engine named the misspelt key.
    bare = tmp_path / "bare_entry.yaml"
    bare.write_text("norms: {joinon: lemma, columns: [concreteness]}\n", encoding="utf-8")
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: unknown key 'joinon' in a norms entry; known keys: path, join_on, "
            "columns.")):
        apply_norms(lex, read_config(str(bare)))
    # A mapping of named entries is checked as one entry whose keys are the names. The R
    # engine joined each entry, and this engine refused the block.
    bare.write_text("norms:\n  conc: {path: %s}\n" % str(norms_path).replace("\\", "/"),
                    encoding="utf-8")
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: unknown key 'conc' in a norms entry; known keys: path, join_on, "
            "columns.")):
        apply_norms(lex, read_config(str(bare)))
    # An empty mapping holds no entry at all, in both engines.
    bare.write_text("norms: {}\n", encoding="utf-8")
    assert apply_norms(lex, read_config(str(bare)))["provenance"] == []
    # An entry that is not a mapping has no path to read.
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: every entry under `norms:` needs a `path`.")):
        apply_norms(lex, {"norms": [str(norms_path)]})


def test_the_pipeline_joins_on_a_bare_on_and_notes_it(tmp_path):
    """End to end, from a hand-written design: the table has no `word` column, so the
    join on `word` that the bare `on` used to give stopped the run. Pinned identically
    in test-norms.R."""
    lexicon = tmp_path / "lex_lemma.csv"
    pd.DataFrame({"word": WORDS, "freq_zipf": [3.0 + 0.2 * i for i in range(len(WORDS))],
                  "lemma": WORDS}).to_csv(lexicon, index=False, lineterminator="\n")
    norms_path = tmp_path / "conc_lemma.csv"
    pd.DataFrame({"lemma": WORDS, "concreteness": [2.0 + (i % 4) for i in range(len(WORDS))]}
                 ).to_csv(norms_path, index=False, lineterminator="\n")
    design_path = tmp_path / "design_lemmatest.yaml"
    design_path.write_text("\n".join([
        "name: lemmatest",
        "language: english",
        "lexicon: " + str(lexicon).replace("\\", "/"),
        "n_per_condition: 3",
        "norms:",
        "  - path: " + str(norms_path).replace("\\", "/"),
        "    on: lemma",
        "    columns: [concreteness]",
        "conditions:",
        "  - {name: high, define_by: {frequency: [4.2, 7.0]}}",
        "  - {name: low, define_by: {frequency: [3.0, 3.8]}}",
        "match_on: [length, concreteness]",
    ]) + "\n", encoding="utf-8")
    outdir = tmp_path / "out"
    run_pipeline(str(design_path), BUNDLED_SCHEMA, str(outdir), verbose=False)
    stim = pd.read_csv(outdir / "stimuli" / "lemmatest_english_stimuli_py.csv")
    assert stim["concreteness"].notna().all()
    ds = json.load(open(outdir / "reports" / "lemmatest_english_datasheet_py.json",
                        encoding="utf-8"))
    assert ds["materials_source"]["norms"][0]["on"] == "lemma"
    with open(outdir / "reports" / "lemmatest_english_run_log_py.jsonl",
              encoding="utf-8") as handle:
        messages = [json.loads(line)["message"] for line in handle]
    assert ON_NOTE in messages


def _norm_design(tmp_path, lexicon, norms_path):
    """A two-condition design whose pool filter and matched dimension are norm columns."""
    return {
        "name": "normtest", "language": "english", "lexicon": str(lexicon),
        "description": "A design whose control dimension comes from a norm table.",
        "n_per_condition": 3,
        "norms": [{"path": str(norms_path), "columns": ["concreteness"]}],
        "pool_filters": {"concreteness": [2.0, 5.0]},
        "conditions": [
            {"name": "high", "define_by": {"frequency": [4.2, 7.0]}},
            {"name": "low", "define_by": {"frequency": [3.0, 3.8]}},
        ],
        "match_on": ["length", "concreteness"],
        "counterbalance": {"lists": 1},
        "timing": {"fixation_ms": 500, "word_ms": 500, "isi_ms": 250},
    }


def test_the_pipeline_matches_on_a_norm_column_and_records_it(tmp_path):
    """End to end: the block is applied before the pool, so a norm column is matchable.

    This is what the wiring buys. Before it, merge_norms existed but nothing called
    it, so a semantic dimension could not reach `match_on` at all.
    """
    lexicon = _lexicon(tmp_path)
    norms_path = _norms(tmp_path)
    design_path = tmp_path / "design_normtest.yaml"
    with open(design_path, "w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(_norm_design(tmp_path, lexicon, norms_path), handle)

    outdir = tmp_path / "out"
    run_pipeline(str(design_path), BUNDLED_SCHEMA, str(outdir), verbose=False)

    stim = pd.read_csv(outdir / "stimuli" / "normtest_english_stimuli_py.csv")
    # The norm column reached the stimuli table, and the pool filter held.
    assert "concreteness" in stim.columns
    assert stim["concreteness"].notna().all()
    assert stim["concreteness"].between(2.0, 5.0).all()

    ds = json.load(open(outdir / "reports" / "normtest_english_datasheet_py.json",
                        encoding="utf-8"))
    recorded = ds["materials_source"]["norms"]
    assert len(recorded) == 1
    assert recorded[0]["path"] == str(norms_path)
    assert recorded[0]["columns"][0]["column"] == "concreteness"
    # The matched dimension is named as controlled, and the norm file is named in the
    # Methods prose a user pastes into a paper.
    assert "concreteness" in ds["selection"]["match_on"]
    md = open(outdir / "reports" / "normtest_english_datasheet_py.md",
              encoding="utf-8").read()
    assert "## Joined norms" in md and "conc.csv" in md
    assert "Norm dimensions were joined from conc.csv" in md
