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
table does not cover gets a missing value, and the tolerance windows then drop it
from the pool without saying so.

No norm data is bundled. These tests write their own tiny lexicon and norm table, so
the feature is covered end to end without shipping a norm dataset.

test-norms.R asserts the same properties.
"""
import json
import os

import pandas as pd
import pytest
import yaml

from lexsync.querying import apply_norms, load_lexicon
from lexsync.run_pipeline import run_pipeline

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

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


@pytest.fixture()
def schema():
    with open(os.path.join(REPO, "config", "schema.yaml"), encoding="utf-8") as handle:
        return yaml.safe_load(handle)


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
    run_pipeline(str(design_path), os.path.join(REPO, "config", "schema.yaml"),
                 str(outdir), verbose=False)

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
