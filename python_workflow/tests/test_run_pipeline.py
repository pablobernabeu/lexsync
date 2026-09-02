"""Pipeline-level guards. Twinned with test-run-pipeline.R: every fixture,
expectation and message here must stay in step with the R suite."""
import os
import re

import pandas as pd
import pytest
from conftest import _pkg_data

from lexsync.querying import add_neighbourhood
from lexsync.run_pipeline import run_all, run_pipeline


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


@pytest.mark.parametrize("n", ["0", ".inf"])
def test_a_zero_or_infinite_n_per_condition_is_an_error(tmp_path, n):
    """Both values used to slip past this guard in one engine only.

    A configured 0 is falsy, so `or` read it as absent, fell through to the
    matcher's default of twenty and ran; R's %||% falls back on NULL alone and
    refused. An infinite request went the other way: trunc(Inf) is Inf, so R took it
    as a whole number and selected the whole pool, while int() raised OverflowError
    here. Pinned identically in test-run-pipeline.R.
    """
    design = _corpus_design(str(tmp_path), n=n)
    with pytest.raises(ValueError, match="positive whole number"):
        _run(design, tmp_path)


def test_a_single_condition_design_writes_a_header_only_comparisons_file(tmp_path):
    """A design with one condition has nothing to compare against the anchor, and the
    engines used to part company there: this one finished and wrote a comparisons CSV
    with no header, while R died inside the reporting loop on seq_len(nrow(NULL)).
    Both now write this header and no rows. Pinned identically in
    test-run-pipeline.R."""
    design = _write_design(str(tmp_path), [
        "name: onecond",
        "language: english",
        "lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "n_per_condition: 5",
        "pool_filters: {length: [3, 7], frequency: [3.8, 7]}",
        "conditions:",
        "  - {name: only, define_by: {frequency: [4.0, 7.0]}}",
        "match_on: [length]",
    ])

    res = _run(design, tmp_path)

    with open(res["comparisons"], encoding="utf-8") as handle:
        assert handle.read().splitlines() == [
            "condition,reference,dimension,cohens_d,d_ci_low,d_ci_high,"
            "var_ratio,tost_p,equivalent"]


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


def test_a_condition_without_define_by_reaches_the_datasheet(tmp_path):
    # The candidate-pool record used to index c["define_by"] directly, so a
    # design the R engine ran to completion crashed this engine with a bare
    # KeyError after selection had already succeeded.
    import json
    design = _write_design(str(tmp_path), [
        "name: guard_bare",
        "language: english",
        "lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "n_per_condition: 3",
        "pool_filters: {length: [3, 7], frequency: [3.8, 7]}",
        "conditions:",
        "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
        "  - {name: rest}",
        "match_on: [length]",
    ])
    res = _run(design, tmp_path)
    import pandas as pd
    stim = pd.read_csv(res["stimuli"])
    assert sorted(stim["condition"].unique()) == ["high", "rest"]
    ds = json.load(open(os.path.join(str(tmp_path), "reports",
                                     "guard_bare_english_datasheet_py.json"),
                        encoding="utf-8"))
    entries = {e["condition"]: e["n_candidates"]
               for e in ds["selection"]["candidate_pool"]}
    assert set(entries) == {"high", "rest"}
    # The bare condition's candidates are the whole filtered pool.
    assert entries["rest"] >= entries["high"] > 0


def test_a_pair_designs_window_relaxation_reaches_the_datasheet(tmp_path):
    # The pair path dropped the selector's audit on re-expansion, so a tolerance
    # relaxation never reached the run log or the datasheet. tolerance_k 0 pins
    # a zero-width window that no pair satisfies, forcing the relaxation.
    import json
    items = os.path.join(str(tmp_path), "pairs.csv")
    with open(items, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("item,condition,prime,target\n"
                     "1,related,aaa,flat\n1,unrelated,abba,flat\n"
                     "2,related,acne,glass\n2,unrelated,aaron,glass\n"
                     "3,related,alarm,across\n3,unrelated,abrams,across\n"
                     "4,related,aha,house\n4,unrelated,abdel,house\n")
    design = _write_design(str(tmp_path), [
        "name: guard_pair_relax",
        "language: english",
        "paradigm: priming",
        "items:",
        "  source: table",
        "  path: " + _yaml_path(items),
        "  members: [prime, target]",
        "  lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "  anchor_condition: related",
        "n_per_condition: 3",
        "continuous:",
        "  predictor: target.frequency",
        "  controls: [target.length]",
        "match_on: [target.length]",
        "matching: {tolerance_k: {target.length: 0}}",
    ])
    res = _run(design, tmp_path)
    ds = json.load(open(os.path.join(str(tmp_path), "reports",
                                     "guard_pair_relax_english_datasheet_py.json"),
                        encoding="utf-8"))
    rx = ds["selection"]["window_relaxations"]
    assert len(rx) == 1
    assert rx[0]["condition"] == "continuous"
    assert rx[0]["n_needed"] == 3
    log = open(res["log"], encoding="utf-8").read()
    assert "tolerance window relaxed" in log


def test_verbose_false_keeps_the_console_silent(tmp_path, capsys):
    # log_step used to print unconditionally, so run_pipeline(verbose=False)
    # narrated every step; the Streamlit app embeds the pipeline and expects the
    # silence the R engine's options(lexsync.verbose) gate already provides.
    from lexsync import logging as runlog
    items = os.path.join(str(tmp_path), "pairs.csv")
    with open(items, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("item,condition,prime,target\n"
                     "1,related,nurse,doctor\n1,unrelated,window,doctor\n"
                     "2,related,dog,cat\n2,unrelated,table,cat\n")
    design = _write_design(str(tmp_path), [
        "name: guard_quiet",
        "language: english",
        "paradigm: priming",
        "items:",
        "  source: table",
        "  path: " + _yaml_path(items),
    ])
    _run(design, tmp_path)
    assert capsys.readouterr().out == ""
    run_pipeline(design, _pkg_data("schema.yaml"),
                 outdir=os.path.join(str(tmp_path), "loud"), verbose=True)
    assert "[lexsync]" in capsys.readouterr().out
    # The gate is module state, and run_pipeline puts it back on the way out, so
    # a quiet run cannot silence whatever runs after it.
    assert runlog.get_verbose() is True


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


def _bare_lexicon(tmp_path, n=600):
    """The example lexicon, shortened, without the columns lexsync derives itself.

    `load_lexicon` requires `word` and `freq_zipf` alone, so this is a lexicon a user
    may legitimately point lexsync at.
    """
    lex = pd.read_csv(_pkg_data("en_example.csv")).head(n)
    path = os.path.join(tmp_path, "bare.csv")
    lex.drop(columns=["n_density", "old20"]).to_csv(path, index=False)
    return path


def _derived_here(path, words, dim):
    """The dimension as add_neighbourhood computes it, over the same reference list."""
    lex = pd.read_csv(path)
    ref = lex["word"].astype(str).tolist()
    got = add_neighbourhood(pd.DataFrame({"word": words}), reference=ref)
    return got[dim].tolist()


def test_a_condition_defined_by_a_derived_dimension_computes_it(tmp_path):
    # The derivation used to be triggered by `match_on` alone, so a design that
    # defined its conditions by n_density -- the shape of the shipped
    # design_en_ndensity.yaml -- stopped on any lexicon that did not ship the column.
    # Twinned in test-run-pipeline.R.
    lexicon = _bare_lexicon(str(tmp_path))
    design = _write_design(str(tmp_path), [
        "name: derived_define", "language: english",
        "lexicon: " + _yaml_path(lexicon), "n_per_condition: 3",
        "pool_filters: {length: [3, 7]}",
        "conditions:",
        "  - {name: dense, define_by: {n_density: [5, 100]}}",
        "  - {name: sparse, define_by: {n_density: [0, 1]}}",
        "match_on: [length, frequency]",
    ])
    stim = pd.read_csv(_run(design, tmp_path)["stimuli"])
    assert len(stim) == 6
    assert stim["n_density"].tolist() == _derived_here(lexicon, stim["word"], "n_density")
    dense = stim[stim["condition"] == "dense"]["n_density"]
    assert (dense >= 5).all()


def test_a_pool_filter_on_a_derived_dimension_computes_it(tmp_path):
    # The filter names a column the lexicon does not have, and the guard on unknown
    # filter names used to reject the design before anything could derive it.
    lexicon = _bare_lexicon(str(tmp_path))
    design = _write_design(str(tmp_path), [
        "name: derived_filter", "language: english",
        "lexicon: " + _yaml_path(lexicon), "n_per_condition: 3",
        "pool_filters: {length: [3, 7], old20: [1.0, 2.0]}",
        "conditions:",
        "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
        "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
        "match_on: [length]",
    ])
    stim = pd.read_csv(_run(design, tmp_path)["stimuli"])
    assert len(stim) == 6
    assert stim["old20"].between(1.0, 2.0).all()
    assert stim["old20"].tolist() == _derived_here(lexicon, stim["word"], "old20")


def test_a_continuous_predictor_on_a_derived_dimension_computes_it(tmp_path):
    lexicon = _bare_lexicon(str(tmp_path))
    design = _write_design(str(tmp_path), [
        "name: derived_continuous", "language: english",
        "lexicon: " + _yaml_path(lexicon), "n_per_condition: 6",
        "pool_filters: {length: [3, 7]}",
        "continuous: {predictor: old20, controls: [length, frequency]}",
        "match_on: [length, frequency]",
    ])
    stim = pd.read_csv(_run(design, tmp_path)["stimuli"])
    assert len(stim) == 6
    assert stim["old20"].tolist() == _derived_here(lexicon, stim["word"], "old20")


def test_a_misspelt_filter_is_still_refused_beside_a_derived_one(tmp_path):
    lexicon = _bare_lexicon(str(tmp_path))
    design = _write_design(str(tmp_path), [
        "name: derived_typo", "language: english",
        "lexicon: " + _yaml_path(lexicon), "n_per_condition: 3",
        "pool_filters: {old20: [1.0, 2.0], frequncy: [3.8, 7]}",
        "conditions:",
        "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
        "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
        "match_on: [length]",
    ])
    with pytest.raises(ValueError, match="pool_filters name column"):
        _run(design, tmp_path)


def _constant_pool_design(tmp_path):
    """Two conditions each constant on the one matched dimension, at different
    constants, so Cohen's d and its interval are undefined for every comparison."""
    pool = os.path.join(tmp_path, "pool.csv")
    words = ["abcd", "efgh", "ijkl", "mnop", "qrst", "uvwx",
             "abcdef", "ghijkl", "mnopqr", "stuvwx", "yzabcd", "efghij"]
    pd.DataFrame({"word": words}).to_csv(pool, index=False)
    return _write_design(tmp_path, [
        "name: undefined_d", "language: english",
        "items:", "  source: pool", "  path: " + _yaml_path(pool),
        "n_per_condition: 3",
        "conditions:",
        "  - {name: four, define_by: {length: [4, 4]}}",
        "  - {name: six, define_by: {length: [6, 6]}}",
        "match_on: [length]",
    ])


def test_an_undefined_cohens_d_on_every_comparison_still_runs(tmp_path):
    """The whole column stays object dtype when no comparison is numeric, so the
    stored None reached the format string and stopped the run here while the R
    engine wrote 'NA' and finished. Mirrored in test-run-pipeline.R."""
    res = _run(_constant_pool_design(str(tmp_path)), tmp_path)
    comparisons = pd.read_csv(res["comparisons"])
    assert comparisons["cohens_d"].isna().all()
    with open(res["log"], encoding="utf-8") as handle:
        log = handle.read()
    assert "equivalence six vs four on 'length': d = NA," in log


# The two engines' run logs quoted different numbers for the same statistic: the
# stored value is at four places and Python printed all of them while R rounded to
# three, so 0.0016 was also written 0.002 and 1.0 was also written 1.000. The R
# suite pins the same two lines, fixture for fixture.
def _fractional_tost_design(tmp_path):
    pool = os.path.join(tmp_path, "pool.csv")
    letters = "abcdefghijklmnopqrstuvwxyz"
    rows = []
    i = 0
    for a in letters[:10]:
        for b in "aeiou":
            for c in letters[:6]:
                word = a + b + c if i % 3 else a + b + c + "z"
                rows.append({"word": word, "frequency": 1.0 + (i % 19) / 4.5})
                i += 1
    pd.DataFrame(rows).drop_duplicates("word").to_csv(pool, index=False)
    return _write_design(tmp_path, [
        "name: tost_format", "language: english",
        "items:", "  source: pool", "  path: " + _yaml_path(pool),
        "n_per_condition: 25",
        "conditions:",
        "  - {name: low, define_by: {frequency: [1.0, 2.0]}}",
        "  - {name: high, define_by: {frequency: [3.5, 5.5]}}",
        "match_on: [length]",
    ])


def test_the_run_log_writes_the_tost_p_at_four_places(tmp_path):
    res = _run(_fractional_tost_design(str(tmp_path)), tmp_path)
    with open(res["log"], encoding="utf-8") as handle:
        log = handle.read()
    assert "on 'length': d = 0.00 [-0.47, 0.47], TOST p = 0.0417 (equivalent)" in log
    assert "TOST p = 1.0000 (not shown equivalent)" in log


def _malformed(tmp_path, name, text):
    p = os.path.join(tmp_path, name)
    with open(p, "w", encoding="utf-8") as handle:
        handle.write(text)
    return p


@pytest.mark.parametrize("text", ["", "- a\n- b\n"])
def test_a_design_that_is_not_a_mapping_names_the_file(tmp_path, text):
    """An empty or list-shaped design used to report a Python type and not the file.
    Mirrored in test-run-pipeline.R."""
    design = _malformed(str(tmp_path), "design_bad.yaml", text)
    with pytest.raises(ValueError, match=re.escape(
            f"lexsync: design '{design}' did not parse to a mapping of keys")):
        _run(design, tmp_path)


@pytest.mark.parametrize(("lines", "key"), [
    (["language: english"], "name"),
    (["name: nameless"], "language"),
    (["name: ' '", "language: english"], "name"),
])
def test_a_design_without_a_name_or_a_language_is_refused(tmp_path, lines, key):
    """The base name for every artefact is built from both, so a nameless design
    used to write its files under the language alone in the R engine."""
    design = _write_design(str(tmp_path), lines)
    with pytest.raises(ValueError, match=re.escape(
            f"is missing the required key(s) '{key}'.")):
        _run(design, tmp_path)


def test_a_schema_without_its_structural_blocks_is_refused(tmp_path):
    schema = _malformed(str(tmp_path), "schema.yaml", "seed: 2026\n")
    design = _corpus_design(str(tmp_path))
    with pytest.raises(ValueError, match=re.escape(
            f"lexsync: schema '{schema}' is missing the required key(s) "
            "'lexicon_schema', 'matching'.")):
        run_pipeline(design, schema, outdir=str(tmp_path), verbose=False)


def test_run_all_names_the_design_that_failed(tmp_path):
    """A quiet sweep reported the bare failure of an unnamed one of twenty designs."""
    _malformed(str(tmp_path), "design_b_bad.yaml", "")
    with pytest.raises(RuntimeError, match=re.escape(
            "lexsync: design 'design_b_bad.yaml' failed: ")):
        run_all(str(tmp_path), _pkg_data("schema.yaml"), str(tmp_path), verbose=False)
