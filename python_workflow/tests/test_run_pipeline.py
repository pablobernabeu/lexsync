# -*- coding: utf-8 -*-
"""Pipeline-level guards. Twinned with test-run-pipeline.R: every fixture,
expectation and message here must stay in step with the R suite."""
import os

import pytest

from lexsync.run_pipeline import run_pipeline

from conftest import _pkg_data


def _yaml_path(p):
    return p.replace("\\", "/")


def _write_design(tmp_path, lines):
    p = os.path.join(tmp_path, "design.yaml")
    with open(p, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    return p


def _corpus_design(tmp_path, extra=(), n="5"):
    return _write_design(tmp_path, [
        "name: guard_test",
        "language: english",
        "lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "n_per_condition: " + n,
        "pool_filters: {length: [3, 7], frequency: [3.8, 7]}",
        "conditions:",
        "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
        "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
        "match_on: [length]",
        *extra,
    ])


def _run(design, tmp_path):
    return run_pipeline(design, _pkg_data("schema.yaml"), outdir=str(tmp_path),
                        verbose=False)


def test_misspelt_pool_filter_is_an_error(tmp_path):
    design = _write_design(str(tmp_path), [
        "name: guard_test",
        "language: english",
        "lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "n_per_condition: 5",
        "pool_filters: {frequncy: [3.8, 7]}",
        "conditions:",
        "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
        "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
        "match_on: [length]",
    ])
    with pytest.raises(ValueError, match="pool_filters name column"):
        _run(design, tmp_path)


def test_non_integer_n_per_condition_is_an_error(tmp_path):
    design = _corpus_design(str(tmp_path), n="2.5")
    with pytest.raises(ValueError, match="positive whole number"):
        _run(design, tmp_path)


def test_continuous_table_without_members_is_an_error(tmp_path):
    items = os.path.join(str(tmp_path), "pairs.csv")
    with open(items, "w", encoding="utf-8") as handle:
        handle.write("item,condition,prime,target\n1,related,nurse,doctor\n")
    design = _write_design(str(tmp_path), [
        "name: guard_test",
        "language: english",
        "paradigm: priming",
        "items:",
        "  source: table",
        "  path: " + _yaml_path(items),
        "continuous:",
        "  predictor: target.frequency",
        "  controls: [target.length]",
        "match_on: [target.length]",
    ])
    with pytest.raises(ValueError, match="requires items.members"):
        _run(design, tmp_path)


def test_pool_filters_on_a_plain_table_are_an_error(tmp_path):
    items = os.path.join(str(tmp_path), "pairs.csv")
    with open(items, "w", encoding="utf-8") as handle:
        handle.write("item,condition,prime,target\n"
                     "1,related,nurse,doctor\n1,unrelated,window,doctor\n")
    design = _write_design(str(tmp_path), [
        "name: guard_test",
        "language: english",
        "paradigm: priming",
        "items:",
        "  source: table",
        "  path: " + _yaml_path(items),
        "pool_filters: {length: [3, 7]}",
    ])
    with pytest.raises(ValueError, match="pool_filters have no effect"):
        _run(design, tmp_path)


def test_generate_shortfall_errors_by_default_and_allow_accepts(tmp_path):
    base = [
        "name: guard_gen",
        "language: english",
        "paradigm: lexical_decision",
        "items:",
        "  source: generate",
        "  lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "n_per_condition: 2000",
        "pool_filters: {length: [4, 7], frequency: [3.5, 6.0]}",
    ]
    with pytest.raises(ValueError, match="could be generated"):
        _run(_write_design(str(tmp_path), base), tmp_path)
    out2 = os.path.join(str(tmp_path), "allow")
    os.makedirs(out2, exist_ok=True)
    design = _write_design(out2, base + ["matching: {shortfall: allow}"])
    res = run_pipeline(design, _pkg_data("schema.yaml"), outdir=out2, verbose=False)
    assert os.path.exists(res["stimuli"])


def test_continuous_over_a_supplied_pool_selects_continuously(tmp_path):
    # The predicate that gates the continuous selector must treat a supplied
    # pool like a corpus; before the fix this design fell through to the
    # conditions matcher and crashed differently in each engine.
    import pandas as pd
    lex = pd.read_csv(_pkg_data("en_example.csv"))
    words = lex["word"].head(60)
    pool_path = os.path.join(str(tmp_path), "pool.csv")
    words.to_frame().to_csv(pool_path, index=False)
    design = _write_design(str(tmp_path), [
        "name: guard_pool",
        "language: english",
        "items:",
        "  source: pool",
        "  path: " + _yaml_path(pool_path),
        "  lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "n_per_condition: 10",
        "continuous:",
        "  predictor: frequency",
        "  controls: [length]",
        "match_on: [length]",
    ])
    res = _run(design, tmp_path)
    stim = pd.read_csv(res["stimuli"])
    assert (stim["condition"] == "continuous").all()
    assert stim["set"].nunique() == 10
