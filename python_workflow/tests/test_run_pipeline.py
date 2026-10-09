"""Pipeline-level guards. Twinned with test-run-pipeline.R: every fixture,
expectation and message here must stay in step with the R suite."""
import os

import pytest
from conftest import _pkg_data

from lexsync.run_pipeline import run_pipeline


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
            "var_ratio,tost_p,equivalent,mean_diff,role"]


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
                     "1,related,aback,boat\n1,unrelated,abandon,boat\n"
                     "2,related,abdomen,apple\n2,unrelated,ability,apple\n"
                     "3,related,abnormal,bridge\n3,unrelated,abode,bridge\n"
                     "4,related,absurd,hotel\n4,unrelated,academy,hotel\n")
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


def _rated_lexicon(tmp_path):
    # Ten nouns and ten verbs. Two nouns and one verb have no rating, as words a norm
    # table does not cover would have none. The ratings are invented for this test.
    rows = [("anchor", 3.66, "noun", "2.1"), ("basket", 3.88, "noun", ""),
            ("bottle", 4.58, "noun", "3.0"), ("button", 4.29, "noun", "2.6"),
            ("candle", 3.79, "noun", "2.2"), ("carpet", 3.92, "noun", ""),
            ("forest", 4.62, "noun", "3.4"), ("garden", 4.83, "noun", "2.8"),
            ("ladder", 3.74, "noun", "2.4"), ("mirror", 4.33, "noun", "3.1"),
            ("arrive", 4.27, "verb", "2.0"), ("borrow", 3.95, "verb", "2.7"),
            ("decide", 4.88, "verb", ""), ("divide", 3.98, "verb", "2.3"),
            ("escape", 4.52, "verb", "3.3"), ("follow", 5.08, "verb", "2.9"),
            ("gather", 4.18, "verb", "2.5"), ("invite", 4.03, "verb", "3.2"),
            ("listen", 4.91, "verb", "2.2"), ("punish", 3.77, "verb", "3.0")]
    path = os.path.join(str(tmp_path), "lexicon.csv")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("word,freq_zipf,pos,rating\n")
        handle.writelines("%s,%s,%s,%s\n" % r for r in rows)
    return path


def test_an_exclusion_for_a_missing_matched_value_reaches_the_record(tmp_path):
    # Matching excludes a candidate missing a matched dimension, and the run log and
    # the datasheet say how many each condition lost. Twinned with
    # test-run-pipeline.R.
    import json
    design = _write_design(str(tmp_path), [
        "name: guard_incomplete",
        "language: english",
        "lexicon: " + _yaml_path(_rated_lexicon(tmp_path)),
        "n_per_condition: 4",
        "conditions:",
        "  - {name: noun, define_by: {pos: [noun]}}",
        "  - {name: verb, define_by: {pos: [verb]}}",
        "match_on: [length, rating]",
    ])
    res = _run(design, tmp_path)
    with open(os.path.join(str(tmp_path), "reports",
                           "guard_incomplete_english_datasheet_py.json"),
              encoding="utf-8") as handle:
        ds = json.load(handle)
    assert ds["selection"]["incomplete_dropped"] == [
        {"condition": "noun", "n": 2}, {"condition": "verb", "n": 1}]
    with open(res["log"], encoding="utf-8") as handle:
        log = handle.read()
    assert "dropped 2 candidate(s) of condition 'noun' missing a matched dimension" in log
    assert "dropped 1 candidate(s) of condition 'verb' missing a matched dimension" in log


def test_a_continuous_designs_exclusion_reaches_the_record(tmp_path):
    import json
    design = _write_design(str(tmp_path), [
        "name: guard_incomplete_cont",
        "language: english",
        "lexicon: " + _yaml_path(_rated_lexicon(tmp_path)),
        "n_per_condition: 6",
        "continuous: {predictor: rating, controls: [length]}",
        "match_on: [length]",
    ])
    res = _run(design, tmp_path)
    with open(os.path.join(str(tmp_path), "reports",
                           "guard_incomplete_cont_english_datasheet_py.json"),
              encoding="utf-8") as handle:
        ds = json.load(handle)
    assert ds["selection"]["incomplete_dropped"] == [{"condition": "continuous", "n": 3}]
    with open(res["log"], encoding="utf-8") as handle:
        log = handle.read()
    assert "dropped 3 candidate(s) missing the predictor or a control" in log


def test_a_pair_designs_exclusion_reaches_the_record(tmp_path):
    # The pair path selects over one row per set and copies the selector's audit onto
    # the re-expanded table. 'bridge' has no rating, so its set is excluded and the
    # count reaches the run log and the datasheet. Twinned with test-run-pipeline.R.
    import json
    items = os.path.join(str(tmp_path), "pairs.csv")
    with open(items, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("item,condition,prime,target\n"
                     "1,related,aback,boat\n1,unrelated,abandon,boat\n"
                     "2,related,abdomen,apple\n2,unrelated,ability,apple\n"
                     "3,related,abnormal,bridge\n3,unrelated,abode,bridge\n"
                     "4,related,absurd,hotel\n4,unrelated,academy,hotel\n")
    ratings = os.path.join(str(tmp_path), "ratings.csv")
    with open(ratings, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("word,rating\nboat,2.5\napple,3.1\nhotel,4.0\n")
    design = _write_design(str(tmp_path), [
        "name: guard_pair_incomplete",
        "language: english",
        "paradigm: priming",
        "norms:",
        "  - {path: " + _yaml_path(ratings) + ", columns: [rating]}",
        "items:",
        "  source: table",
        "  path: " + _yaml_path(items),
        "  members: [prime, target]",
        "  lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "  anchor_condition: related",
        "n_per_condition: 3",
        "continuous:",
        "  predictor: target.rating",
        "  controls: [target.length]",
        "match_on: [target.length]",
    ])
    res = _run(design, tmp_path)
    with open(os.path.join(str(tmp_path), "reports",
                           "guard_pair_incomplete_english_datasheet_py.json"),
              encoding="utf-8") as handle:
        ds = json.load(handle)
    assert ds["selection"]["incomplete_dropped"] == [{"condition": "continuous", "n": 1}]
    with open(res["log"], encoding="utf-8") as handle:
        log = handle.read()
    assert "dropped 1 candidate(s) missing the predictor or a control" in log
    with open(res["stimuli"], encoding="utf-8") as handle:
        assert "bridge" not in handle.read()


def test_a_resampled_designs_exclusion_reaches_the_record(tmp_path):
    # resample_stimuli records the first replicate's exclusions, which are the whole
    # pool's, and the pipeline used to discard its audit. Twinned with
    # test-run-pipeline.R.
    import json
    design = _write_design(str(tmp_path), [
        "name: guard_incomplete_resample",
        "language: english",
        "lexicon: " + _yaml_path(_rated_lexicon(tmp_path)),
        "n_per_condition: 3",
        "conditions:",
        "  - {name: noun, define_by: {pos: [noun]}}",
        "  - {name: verb, define_by: {pos: [verb]}}",
        "match_on: [length, rating]",
        "resample: {n_sets: 2}",
    ])
    res = _run(design, tmp_path)
    with open(os.path.join(str(tmp_path), "reports",
                           "guard_incomplete_resample_english_datasheet_py.json"),
              encoding="utf-8") as handle:
        ds = json.load(handle)
    assert ds["selection"]["incomplete_dropped"] == [
        {"condition": "noun", "n": 2}, {"condition": "verb", "n": 1}]
    with open(res["log"], encoding="utf-8") as handle:
        log = handle.read()
    assert "dropped 2 candidate(s) of condition 'noun' missing a matched dimension" in log
    assert "dropped 1 candidate(s) of condition 'verb' missing a matched dimension" in log


def test_a_key_that_only_begins_a_design_key_is_not_read(tmp_path):
    """R's `$` matched a list name partially, so `font_size: 40` stood in for the
    absent `font` and set every target's font to '40', while this engine ignored
    the key. Pinned identically in test-run-pipeline.R."""
    design = _write_design(str(tmp_path), [
        "name: prefix_test",
        "language: english",
        "lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "n_per_condition: 5",
        "pool_filters: {length: [3, 7], frequency: [3.8, 7]}",
        "conditions:",
        "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
        "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
        "match_on: [length]",
        "font_size: 40",
    ])
    res = _run(design, tmp_path)
    exps = res["experiments"]
    with open(exps["psychopy"], encoding="utf-8") as handle:
        assert 'WORD_FONT = "Courier New"' in handle.read().splitlines()
    with open(exps["opensesame"], encoding="utf-8") as handle:
        assert "set font_family mono" in handle.read().splitlines()
    with open(exps["jspsych"], encoding="utf-8") as handle:
        assert 'font-family: "Courier New"' in handle.read()


def test_an_annotation_key_does_not_make_a_design_continuous(tmp_path):
    """R read `continuous_notes` as `continuous` and failed on this factorial
    design. Pinned identically in test-run-pipeline.R."""
    import pandas as pd
    design = _write_design(str(tmp_path), [
        "name: annotated_test",
        "language: english",
        "lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "n_per_condition: 5",
        "pool_filters: {length: [3, 7], frequency: [3.8, 7]}",
        "conditions:",
        "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
        "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
        "match_on: [length]",
        "continuous_notes: frequency defines the two conditions",
    ])
    res = _run(design, tmp_path)
    stim = pd.read_csv(res["stimuli"])
    assert sorted(stim["condition"].unique()) == ["high", "low"]
    assert stim["condition"].value_counts().tolist() == [5, 5]


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


def test_an_incomplete_rotation_reaches_the_run_log_and_the_datasheet(tmp_path):
    """Three conditions in two lists run under the default counterbalance.incomplete:
    allow, and the run log, the datasheet and the Methods text say what the rotation
    leaves out. Pinned identically in test-run-pipeline.R."""
    import json
    items = os.path.join(str(tmp_path), "items.csv")
    rows = ["%d,%s,%s%d,t%d" % (s, c, c[:3], s, s)
            for s in range(1, 7) for c in ("identity", "related", "unrelated")]
    with open(items, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(["item,condition,prime,target"] + rows) + "\n")
    design = _write_design(str(tmp_path), [
        "name: guard_incomplete",
        "language: english",
        "paradigm: priming",
        "items:",
        "  source: table",
        "  path: " + _yaml_path(items),
        "counterbalance:",
        "  lists: 2",
    ])
    res = _run(design, tmp_path)
    issue = "With 2 lists and 3 conditions, each item appears in only 2 of its 3 conditions."
    with open(res["log"], encoding="utf-8") as handle:
        assert "counterbalancing: " + issue in handle.read()
    reports = os.path.join(str(tmp_path), "reports")
    with open(os.path.join(reports, "guard_incomplete_english_datasheet_py.json"),
              encoding="utf-8") as handle:
        record = json.load(handle)["counterbalancing"]
    assert record["complete"] is False
    assert record["issues"] == [issue]
    assert record["lists"] == 2
    with open(os.path.join(reports, "guard_incomplete_english_datasheet_py.md"),
              encoding="utf-8") as handle:
        assert "(an incomplete Latin-square rotation)" in handle.read()


def test_the_run_log_and_the_datasheet_name_every_experiment_file(tmp_path):
    """Two lists give two OpenSesame experiments, each with its own loop and text
    tables. The run log recorded the three experiment scripts only, and the datasheet
    listed no loop table, although the loop tables hold the trial order and the trigger
    codes. Pinned identically in test-run-pipeline.R."""
    import json
    items = os.path.join(str(tmp_path), "items.csv")
    rows = ["%d,%s,%s%d,t%d" % (s, c, c[:3], s, s)
            for s in range(1, 5) for c in ("related", "unrelated")]
    with open(items, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(["item,condition,prime,target"] + rows) + "\n")
    design = _write_design(str(tmp_path), [
        "name: guard_versions",
        "language: english",
        "paradigm: priming",
        "items:",
        "  source: table",
        "  path: " + _yaml_path(items),
        "counterbalance:",
        "  lists: 2",
    ])
    res = _run(design, tmp_path)
    files = res["experiments"]["files"]
    assert [os.path.basename(p) for p in files] == [
        "guard_versions_english_psychopy.py", "guard_versions_english_list1.osexp",
        "guard_versions_english_list2.osexp", "guard_versions_english.html",
        "guard_versions_english_psychopy.csv",
        "guard_versions_english_list1_opensesame.csv",
        "guard_versions_english_list1_opensesame_text.csv",
        "guard_versions_english_list2_opensesame.csv",
        "guard_versions_english_list2_opensesame_text.csv"]
    assert res["experiments"]["opensesame"] == files[1]
    with open(res["log"], encoding="utf-8") as handle:
        log = handle.read()
    for path in files:
        assert "wrote '%s'" % os.path.basename(path) in log
    reports = os.path.join(str(tmp_path), "reports")
    with open(os.path.join(reports, "guard_versions_english_datasheet_py.json"),
              encoding="utf-8") as handle:
        record = json.load(handle)
    recorded = [a["file"].rsplit("/", 1)[1] for a in record["artifacts"]]
    assert recorded[1:] == [os.path.basename(p) for p in files]
    assert record["counterbalancing"]["versions"] == 2


def test_a_condition_no_list_reaches_is_still_counted(tmp_path):
    """One item set in three conditions, dealt to two lists, never shows its third
    condition. The check counts the conditions of the table the pipeline dealt, not
    those the lists hold, so it reports three conditions and gives the condition left
    out an empty cell in each list. Pinned identically in test-run-pipeline.R."""
    import json
    items = os.path.join(str(tmp_path), "items.csv")
    with open(items, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("item,condition,prime,target\n1,identity,ide1,t1\n"
                     "1,related,rel1,t1\n1,unrelated,unr1,t1\n")
    design = _write_design(str(tmp_path), [
        "name: guard_unreached",
        "language: english",
        "paradigm: priming",
        "items:",
        "  source: table",
        "  path: " + _yaml_path(items),
        "counterbalance:",
        "  lists: 2",
    ])
    _run(design, tmp_path)
    with open(os.path.join(str(tmp_path), "reports", "guard_unreached_english_datasheet_py.json"),
              encoding="utf-8") as handle:
        record = json.load(handle)["counterbalancing"]
    assert record["issues"] == [
        "With 2 lists and 3 conditions, each item appears in only 2 of its 3 conditions.",
        "With 1 item set and 3 conditions, the item sets are not a multiple of the "
        "conditions, so the conditions within each list differ by one trial."]
    assert [(c["list"], c["condition"], c["n_trials"]) for c in record["cells"]] == [
        (1, "identity", 1), (1, "related", 0), (1, "unrelated", 0),
        (2, "identity", 0), (2, "related", 1), (2, "unrelated", 0)]


def _files_under(root):
    """Every file under `root`, relative to it, so a refusal can be shown to leave
    nothing behind."""
    out = []
    for d, _, files in os.walk(root):
        out += [os.path.relpath(os.path.join(d, f), root) for f in files]
    return sorted(out)


def _refused_before_writing(lines, tmp_path, message):
    """Run a design that must be refused, and check that nothing reached outdir."""
    import re
    design = _write_design(str(tmp_path), lines)
    outdir = os.path.join(str(tmp_path), "out")
    with pytest.raises(ValueError, match=re.escape(message)):
        run_pipeline(design, _pkg_data("schema.yaml"), outdir=outdir, verbose=False)
    assert _files_under(outdir) == []


def _corpus_lines(name="check_test", extra=(), n="5"):
    return [
        "name: " + name,
        "language: english",
        "lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "n_per_condition: " + n,
        "pool_filters: {length: [3, 7], frequency: [3.8, 7]}",
        "conditions:",
        "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
        "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
        "match_on: [length]",
        *extra,
    ]


def test_a_misspelt_design_key_is_refused_with_a_suggestion(tmp_path):
    """`n_per_conditon: 8` was ignored, so the design silently got the default twenty
    items per condition. Pinned identically in test-run-pipeline.R."""
    lines = [ln for ln in _corpus_lines() if not ln.startswith("n_per_condition")]
    _refused_before_writing(
        lines + ["n_per_conditon: 8"], tmp_path,
        "lexsync: unknown design key 'n_per_conditon' (did you mean 'n_per_condition'?)")
    _refused_before_writing(
        _corpus_lines(extra=["matching: {methd: joint}"]), tmp_path,
        "lexsync: unknown design key 'matching.methd' (did you mean 'matching.method'?)")


def test_an_unknown_design_key_is_reported_in_the_run_log(tmp_path):
    """A key far from every known one is not refused yet, but the run log says it was
    ignored. `description` and a key beginning `x_` are annotations and pass quietly.
    Pinned identically in test-run-pipeline.R."""
    design = _write_design(str(tmp_path), _corpus_lines(extra=[
        "notes: piloted in May",
        "description: two frequency bands",
        "x_reviewer: second author",
        "conditions_comment: high against low",
    ]))
    res = _run(design, tmp_path)
    with open(res["log"], encoding="utf-8") as handle:
        log = handle.read()
    for key in ("notes", "conditions_comment"):
        assert ("lexsync: design key '%s' is not read by lexsync and is ignored; a later "
                "release will refuse it. Put annotations in `description` or a key "
                "beginning `x_`." % key) in log
    assert "'description'" not in log
    assert "x_reviewer" not in log


def test_a_whole_float_n_per_condition_is_accepted(tmp_path):
    """YAML reads `4.0` as a float, which this engine refused with a TypeError deep
    in the matcher. Pinned identically in test-run-pipeline.R."""
    import pandas as pd
    res = _run(_write_design(str(tmp_path), _corpus_lines(n="4.0")), tmp_path)
    stim = pd.read_csv(res["stimuli"])
    assert stim["condition"].value_counts().tolist() == [4, 4]


def test_a_whole_float_n_reaches_the_generate_path(tmp_path):
    import pandas as pd
    design = _write_design(str(tmp_path), [
        "name: float_gen",
        "language: english",
        "paradigm: lexical_decision",
        "items:",
        "  source: generate",
        "  lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "n_per_condition: 4.0",
        "pool_filters: {length: [4, 7], frequency: [3.5, 6.0]}",
    ])
    res = _run(design, tmp_path)
    stim = pd.read_csv(res["stimuli"])
    assert stim["set"].nunique() == 4


def test_a_schema_of_seed_and_lexicon_schema_runs(tmp_path):
    """Every other schema block has a default, so a schema holding only these two
    runs. This engine raised KeyError 'matching'. Pinned identically in
    test-run-pipeline.R."""
    schema = os.path.join(str(tmp_path), "schema.yaml")
    with open(schema, "w", encoding="utf-8") as handle:
        handle.write("seed: 7\nlexicon_schema:\n  required: [word, freq_zipf]\n")
    design = _write_design(str(tmp_path), _corpus_lines())
    res = run_pipeline(design, schema, outdir=os.path.join(str(tmp_path), "out"),
                       verbose=False)
    assert os.path.exists(res["stimuli"])


def test_a_design_without_a_name_is_refused_before_anything_is_written(tmp_path):
    """The R engine wrote four files and then failed with 'argument is of length
    zero'; this one raised a bare KeyError. Pinned identically in
    test-run-pipeline.R."""
    lines = [ln for ln in _corpus_lines() if not ln.startswith("name:")]
    _refused_before_writing(lines, tmp_path, "lexsync: the design has no `name`.")


def test_language_tag_does_not_stand_in_for_language(tmp_path):
    lines = [ln if not ln.startswith("language:") else "language_tag: en-GB"
             for ln in _corpus_lines()]
    _refused_before_writing(lines, tmp_path, "lexsync: the design has no `language`.")


def test_a_language_that_yaml_reads_as_a_boolean_is_refused(tmp_path):
    lines = [ln if not ln.startswith("language:") else "language: no"
             for ln in _corpus_lines()]
    _refused_before_writing(
        lines, tmp_path,
        "lexsync: the design's `language` must be text; quote it if it is a code "
        "such as 'no'.")


def test_an_unsafe_name_is_refused_before_any_file_exists(tmp_path):
    """The name used to be checked only at export, after the stimuli, both reports
    and the PsychoPy loop table were on disk."""
    _refused_before_writing(_corpus_lines(name="\"bad'name\""), tmp_path,
                            "cannot be written safely")


def test_an_unsafe_font_or_port_is_refused_before_any_file_exists(tmp_path):
    _refused_before_writing(_corpus_lines(extra=["font: \"Arial'\""]), tmp_path,
                            "cannot be written safely")
    schema = os.path.join(str(tmp_path), "schema.yaml")
    with open(_pkg_data("schema.yaml"), encoding="utf-8") as handle:
        text = handle.read()
    with open(schema, "w", encoding="utf-8") as handle:
        handle.write(text.replace("parallel_address: '0x0378'", "parallel_address: 'LPT1'"))
    design = _write_design(str(tmp_path), _corpus_lines())
    outdir = os.path.join(str(tmp_path), "out_port")
    with pytest.raises(ValueError, match="must be a port address"):
        run_pipeline(design, schema, outdir=outdir, verbose=False)
    assert _files_under(outdir) == []


def test_a_bad_response_key_is_refused_before_any_file_exists(tmp_path):
    _refused_before_writing(_corpus_lines(extra=[
        "events:",
        "  - {type: text, content: '{word}', duration_ms: 500, trigger: condition}",
        "  - {type: response, keys: ['a;b']}",
    ]), tmp_path, "must be a key name")


def test_a_matched_design_without_match_on_is_refused(tmp_path):
    """Without match_on the R engine paired the byte-first words, and with an empty
    list both engines did. Pinned identically in test-run-pipeline.R."""
    message = "lexsync: a matched design needs `match_on` naming at least one dimension."
    lines = [ln for ln in _corpus_lines() if not ln.startswith("match_on")]
    _refused_before_writing(lines, tmp_path, message)
    _refused_before_writing(lines + ["match_on: []"], tmp_path, message)


def test_a_condition_name_that_is_not_text_is_refused(tmp_path):
    lines = [ln.replace("name: high", "name: 1") for ln in _corpus_lines()]
    _refused_before_writing(lines, tmp_path,
                            "lexsync: condition names must be text; quote '1'.")


def test_a_non_ascii_name_writes_under_a_checksummed_stem(tmp_path):
    """Designs named 词频 and 笔画 in Chinese both wrote chinese_*, so the second
    overwrote the first. Pinned identically in test-run-pipeline.R."""
    lines = [ln if not ln.startswith("language:") else "language: chinese"
             for ln in _corpus_lines(name="词频")]
    res = _run(_write_design(str(tmp_path), lines), tmp_path)
    assert os.path.basename(res["stimuli"]) == "chinese_14aadfa7_stimuli_py.csv"
    assert os.path.basename(res["experiments"]["opensesame"]) == "chinese_14aadfa7.osexp"


def test_run_all_refuses_designs_that_would_write_the_same_files(tmp_path):
    """`en-lexdec` and `en_lexdec` slugify alike, so the second design overwrote the
    first's files. Pinned identically in test-run-pipeline.R."""
    from lexsync.run_pipeline import run_all
    cfg = os.path.join(str(tmp_path), "config")
    os.makedirs(cfg)
    for fname, name in (("design_a.yaml", "en-lexdec"), ("design_b.yaml", "en_lexdec")):
        with open(os.path.join(cfg, fname), "w", encoding="utf-8") as handle:
            handle.write("\n".join(_corpus_lines(name=name)) + "\n")
    outdir = os.path.join(str(tmp_path), "out")
    with pytest.raises(ValueError, match=(
            "lexsync: 'design_a.yaml' and 'design_b.yaml' would write the same files "
            r"\('en_lexdec_english'\); give the designs distinct names.")):
        run_all(cfg, _pkg_data("schema.yaml"), outdir, verbose=False)
    assert _files_under(outdir) == []


# Pins the same contract as "the run log and datasheet record NFC normalisation" in
# test-run-pipeline.R. Each word appears in NFC and in NFD, the second spelling in
# the other condition. Before normalisation they were four words, and the matcher
# could put a word in both conditions of one set.
def test_the_run_log_and_datasheet_record_nfc_normalisation(tmp_path):
    import glob
    import json

    import pandas as pd
    avion, limon, cafe, papa = "avión", "limón", "café", "papá"
    avion_d, limon_d = "avio\u0301n", "limo\u0301n"
    cafe_d, papa_d = "cafe\u0301", "papa\u0301"
    pool_path = os.path.join(str(tmp_path), "pool.csv")
    with open(pool_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(f"word,grp\n{avion},a\n{avion_d},b\n{limon_d},b\n{limon},a\n"
                     f"{cafe},a\n{cafe_d},b\n{papa_d},b\n{papa},a\n")
    design = _write_design(str(tmp_path), [
        "name: nfc_record",
        "language: spanish",
        "items:",
        "  source: pool",
        "  path: " + _yaml_path(pool_path),
        "n_per_condition: 2",
        "conditions:",
        "  - {name: a, define_by: {grp: [a]}}",
        "  - {name: b, define_by: {grp: [b]}}",
        "match_on: [length]",
    ])
    res = run_pipeline(design, _pkg_data("schema.yaml"), outdir=str(tmp_path),
                       reference_words=[avion_d, limon_d], verbose=False)
    stim = pd.read_csv(res["stimuli"], encoding="utf-8")
    got = sorted(zip(stim["condition"], stim["word"], strict=True))
    assert got == sorted([("a", avion), ("a", cafe), ("b", limon), ("b", papa)])
    # Four pool rows and both reference words changed, and four pool rows were merged.
    with open(res["log"], encoding="utf-8") as handle:
        assert "normalised 6 word form(s) to NFC; 4 duplicate(s) removed" in handle.read()
    (ds_path,) = glob.glob(os.path.join(str(tmp_path), "reports", "*_datasheet_py.json"))
    with open(ds_path, encoding="utf-8") as handle:
        ds = json.load(handle)
    assert ds["materials_source"]["input_normalisation"] == {"changed": 6, "collapsed": 4}

    # Input already in NFC leaves no trace, so no shipped datasheet changes.
    clean = os.path.join(str(tmp_path), "clean")
    os.makedirs(clean)
    _run(_corpus_design(clean), clean)
    (ds_path,) = glob.glob(os.path.join(clean, "reports", "*_datasheet_py.json"))
    with open(ds_path, encoding="utf-8") as handle:
        assert "input_normalisation" not in json.load(handle)["materials_source"]


# Pins the same contract as "a practice table's NFC normalisation is recorded" in
# test-run-pipeline.R. A practice or filler table goes through load_items like the main
# one, so its text is put in NFC too, and the record used to leave that out.
def test_a_practice_tables_nfc_normalisation_is_recorded(tmp_path):
    import glob
    import json
    practice = os.path.join(str(tmp_path), "practice.csv")
    with open(practice, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("item,condition,word\n1,high,cafe\u0301\n2,low,dog\n")
    res = _run(_corpus_design(str(tmp_path), ["practice:", "  path: " + _yaml_path(practice)]),
               tmp_path)
    with open(res["log"], encoding="utf-8") as handle:
        assert "normalised 1 word form(s) to NFC; 0 duplicate(s) removed" in handle.read()
    (ds_path,) = glob.glob(os.path.join(str(tmp_path), "reports", "*_datasheet_py.json"))
    with open(ds_path, encoding="utf-8") as handle:
        ds = json.load(handle)
    assert ds["materials_source"]["input_normalisation"] == {"changed": 1, "collapsed": 0}


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


# ---- Derived dimensions (n_density, old20, bigram_freq) ---------------------------
# lexsync derived these only for dimensions named in match_on, and checked pool_filters
# against the lexicon before deriving anything, so a design that manipulated, filtered
# on or regressed on a derived dimension stopped with "absent from the pool". Each test
# below is pinned identically in test-run-pipeline.R.

def _read_json(path):
    import json
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _datasheet(tmp_path, stem):
    return _read_json(os.path.join(str(tmp_path), "reports", stem + "_datasheet_py.json"))


def _lexicon_without(tmp_path, source, drop, name="lexicon.csv"):
    """A copy of a bundled lexicon without the named columns, as `lexsync fetch`
    writes one (word, freq_zipf, language, source)."""
    import pandas as pd
    lex = pd.read_csv(_pkg_data(source), keep_default_na=False)
    path = os.path.join(str(tmp_path), name)
    lex.drop(columns=list(drop)).to_csv(path, index=False, lineterminator="\n")
    return path


def test_a_bigram_contrast_runs_on_a_lexicon_without_bigram_freq(tmp_path):
    import pandas as pd
    design = _write_design(str(tmp_path), [
        "name: bigram_contrast",
        "language: english",
        "lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "n_per_condition: 5",
        "pool_filters: {length: [4, 7], frequency: [3.8, 7]}",
        "conditions:",
        "  - {name: high_bigram, define_by: {bigram_freq: [0.009, 1]}}",
        "  - {name: low_bigram, define_by: {bigram_freq: [0, 0.004]}}",
        "match_on: [length, frequency]",
    ])
    res = _run(design, tmp_path)
    stim = pd.read_csv(res["stimuli"])
    assert stim["condition"].value_counts().tolist() == [5, 5]
    assert (stim.loc[stim["condition"] == "high_bigram", "bigram_freq"] >= 0.009).all()
    assert (stim.loc[stim["condition"] == "low_bigram", "bigram_freq"] <= 0.004).all()


def test_a_continuous_design_can_take_bigram_freq_as_its_predictor(tmp_path):
    import pandas as pd
    design = _write_design(str(tmp_path), [
        "name: bigram_continuous",
        "language: english",
        "lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "n_per_condition: 10",
        "pool_filters: {length: [4, 7], frequency: [3.8, 7]}",
        "continuous:",
        "  predictor: bigram_freq",
        "  controls: [length]",
        "match_on: [length]",
    ])
    res = _run(design, tmp_path)
    stim = pd.read_csv(res["stimuli"])
    assert stim["set"].nunique() == 10
    assert stim["bigram_freq"].notna().all()


def test_a_pool_filter_on_bigram_freq_runs(tmp_path):
    import pandas as pd
    design = _write_design(str(tmp_path), [
        "name: bigram_filter",
        "language: english",
        "lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "n_per_condition: 5",
        "pool_filters: {length: [3, 7], frequency: [3.8, 7], bigram_freq: [0.005, 0.02]}",
        "conditions:",
        "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
        "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
        "match_on: [length]",
    ])
    res = _run(design, tmp_path)
    stim = pd.read_csv(res["stimuli"])
    assert len(stim) == 10
    assert stim["bigram_freq"].between(0.005, 0.02).all()


def test_an_ndensity_design_runs_on_a_lexicon_without_n_and_old20(tmp_path):
    """design_es_ndensity on a lexicon such as `lexsync fetch es` writes. The measures
    are computed against the whole lexicon, not against the filtered pool."""
    import pandas as pd

    from lexsync.querying import add_neighbourhood
    lexicon = _lexicon_without(tmp_path, "es_example.csv", ["n_density", "old20"])
    design = _write_design(str(tmp_path), [
        "name: fetched_ndensity",
        "language: spanish",
        "lexicon: " + _yaml_path(lexicon),
        "n_per_condition: 5",
        "pool_filters: {length: [3, 6], frequency: [3.8, 7.0]}",
        "conditions:",
        "  - {name: dense_neighbourhood, define_by: {n_density: [3, 100]}}",
        "  - {name: sparse_neighbourhood, define_by: {n_density: [0, 1]}}",
        "match_on: [length, frequency]",
        "matching: {method: joint}",
    ])
    res = _run(design, tmp_path)
    stim = pd.read_csv(res["stimuli"], keep_default_na=False)
    assert stim["condition"].value_counts().tolist() == [5, 5]
    assert (stim.loc[stim["condition"] == "dense_neighbourhood", "n_density"] >= 3).all()
    words = pd.read_csv(lexicon, keep_default_na=False)["word"].tolist()
    want = add_neighbourhood(stim[["word"]], reference=words)
    assert stim["n_density"].tolist() == want["n_density"].tolist()
    assert stim["old20"].tolist() == want["old20"].tolist()


def test_reference_words_recomputes_n_and_old20_and_is_recorded(tmp_path):
    """Every bundled lexicon carries n_density and old20, so the override was ignored
    while the datasheet recorded it as applied."""
    import pandas as pd
    design = _corpus_design(str(tmp_path))
    res = run_pipeline(design, _pkg_data("schema.yaml"), outdir=str(tmp_path),
                       reference_words=["zzzz", "qqqq"], verbose=False)
    from lexsync.querying import add_neighbourhood
    stim = pd.read_csv(res["stimuli"])
    want = add_neighbourhood(stim[["word"]], reference=["zzzz", "qqqq"])
    assert (stim["n_density"] == 0).all()
    assert stim["old20"].tolist() == want["old20"].tolist()
    nref = _datasheet(tmp_path, "guard_test_english")["selection"]["neighbourhood_reference"]
    assert nref["applied_to"] == ["n_density", "old20"]
    assert nref["n_words"] == 2
    assert nref["source"] == "user-supplied"
    with open(res["log"], encoding="utf-8") as handle:
        assert ("recomputed n_density, old20 against a supplied reference of 2 words"
                in handle.read())


def test_reference_words_recomputes_bigram_freq_when_the_design_uses_it(tmp_path):
    design = _write_design(str(tmp_path), [
        "name: guard_test",
        "language: english",
        "lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "n_per_condition: 5",
        "pool_filters: {length: [3, 7], frequency: [3.8, 7]}",
        "conditions:",
        "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
        "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
        "match_on: [length, bigram_freq]",
    ])
    res = run_pipeline(design, _pkg_data("schema.yaml"), outdir=str(tmp_path),
                       reference_words=["zzzz", "qqqq"], verbose=False)
    nref = _datasheet(tmp_path, "guard_test_english")["selection"]["neighbourhood_reference"]
    assert nref["applied_to"] == ["n_density", "old20", "bigram_freq"]
    with open(res["log"], encoding="utf-8") as handle:
        assert ("recomputed n_density, old20, bigram_freq against a supplied reference "
                "of 2 words" in handle.read())


def test_reference_words_on_a_generate_design_is_ignored_and_not_recorded(tmp_path):
    design = _write_design(str(tmp_path), [
        "name: gen_ref",
        "language: english",
        "paradigm: lexical_decision",
        "items:",
        "  source: generate",
        "  lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "n_per_condition: 5",
        "pool_filters: {length: [4, 7], frequency: [3.5, 6.0]}",
    ])
    res = run_pipeline(design, _pkg_data("schema.yaml"), outdir=str(tmp_path),
                       reference_words=["zzzz", "qqqq"], verbose=False)
    assert "neighbourhood_reference" not in _datasheet(tmp_path, "gen_ref_english")["selection"]
    with open(res["log"], encoding="utf-8") as handle:
        assert ("reference_words is not used by items.source 'generate' and was ignored"
                in handle.read())


@pytest.mark.parametrize("words", [[], ["zzzz", None]])
def test_reference_words_must_hold_a_word_and_no_missing_value(tmp_path, words):
    """Once the override took effect, an empty list set every N to 0 and every OLD20
    to missing, and the selection went ahead on those values."""
    design = _corpus_design(str(tmp_path))
    with pytest.raises(ValueError, match="lexsync: reference_words must hold at least one "
                                         "word and no missing value."):
        run_pipeline(design, _pkg_data("schema.yaml"), outdir=str(tmp_path),
                     reference_words=words, verbose=False)
    assert not os.path.exists(os.path.join(str(tmp_path), "reports"))


def test_a_lone_reference_word_is_one_word(tmp_path):
    """R reads a character scalar as one word, so a Python string is one word too and
    is not split into its letters."""
    import pandas as pd

    from lexsync.querying import add_neighbourhood
    design = _corpus_design(str(tmp_path))
    res = run_pipeline(design, _pkg_data("schema.yaml"), outdir=str(tmp_path),
                       reference_words="zzzz", verbose=False)
    nref = _datasheet(tmp_path, "guard_test_english")["selection"]["neighbourhood_reference"]
    assert nref["n_words"] == 1
    stim = pd.read_csv(res["stimuli"])
    want = add_neighbourhood(stim[["word"]], reference=["zzzz"])
    assert stim["old20"].tolist() == want["old20"].tolist()


def test_a_reference_member_column_sets_the_neighbourhood_reference(tmp_path):
    """A lexicon may mark the forms that make up the neighbourhood reference. The
    measures it lacks are then computed against those rows alone."""
    import pandas as pd
    lexicon = os.path.join(str(tmp_path), "lexicon.csv")
    rows = [("cat", 5.0, 1), ("cot", 4.0, 1), ("cut", 4.1, 1), ("cap", 4.2, 0),
            ("car", 5.1, 0), ("dog", 5.2, 1), ("dig", 4.3, 1), ("dug", 4.0, 0)]
    pd.DataFrame(rows, columns=["word", "freq_zipf", "reference_member"]).to_csv(
        lexicon, index=False, lineterminator="\n")
    design = _write_design(str(tmp_path), [
        "name: member_ref",
        "language: english",
        "lexicon: " + _yaml_path(lexicon),
        "n_per_condition: 3",
        "conditions:",
        "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
        "  - {name: low, define_by: {frequency: [3.0, 4.5]}}",
        "match_on: [length, n_density]",
    ])
    res = _run(design, tmp_path)
    stim = pd.read_csv(res["stimuli"]).set_index("word")
    # Against the members cat, cot, cut, dog and dig: cat neighbours cot and cut but
    # not the non-members cap and car, and car and dog have one member neighbour each.
    assert stim.loc[["cat", "car", "dog"], "n_density"].tolist() == [2, 1, 1]


# ---- n_syllables outside Latin script (twinned with test-run-pipeline.R) --------
# count_syllables returned 0 for every Chinese, Russian or Greek word, so a design
# could match on n_syllables and report perfect balance. It now gives a missing value
# there, and a design that refers to the dimension while the pool holds such words is
# refused before anything is written.

_SYLLABLES_REFUSED = (
    "lexsync: n_syllables is not available for %d word(s) in the pool: it counts Latin "
    "vowel letters, so it is undefined for other scripts. Remove it from the design or "
    "filter those words out.")


def _zh_lines(extra):
    return [
        "name: zh_syllables",
        "language: chinese",
        "lexicon: " + _yaml_path(_pkg_data("zh_example.csv")),
        "n_per_condition: 5",
        "conditions:",
        "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
        "  - {name: low, define_by: {frequency: [3.5, 4.2]}}",
        *extra,
    ]


def test_a_design_matching_on_n_syllables_over_chinese_is_refused(tmp_path):
    _refused_before_writing(_zh_lines(["match_on: [length, n_syllables]"]), tmp_path,
                            _SYLLABLES_REFUSED % 3000)


def test_a_filter_on_n_syllables_over_chinese_is_refused_not_emptied(tmp_path):
    """A filter drops the rows missing its column, so without the check this design
    went on with an empty pool and failed far from the cause."""
    _refused_before_writing(
        _zh_lines(["pool_filters: {n_syllables: [1, 3]}", "match_on: [length]"]),
        tmp_path, _SYLLABLES_REFUSED % 3000)


def test_a_chinese_design_without_n_syllables_leaves_the_column_empty(tmp_path):
    import pandas as pd
    res = _run(_write_design(str(tmp_path), _zh_lines(["match_on: [length]"])), tmp_path)
    stim = pd.read_csv(res["stimuli"])
    assert stim["n_syllables"].isna().all()


@pytest.mark.parametrize("freq,refused", [(2.0, False), (5.0, True)])
def test_n_syllables_is_checked_on_the_filtered_pool(tmp_path, freq, refused):
    """A Cyrillic word that the design's other filters remove does not count against
    it; one they keep does."""
    lexicon = os.path.join(str(tmp_path), "lexicon.csv")
    with open(_pkg_data("en_example.csv"), encoding="utf-8") as handle:
        text = handle.read()
    with open(lexicon, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text + "\u043c\u043e\u043b\u043e\u043a\u043e,%s,en,test,0,1.0\n" % freq)
    lines = [ln.replace(_yaml_path(_pkg_data("en_example.csv")), _yaml_path(lexicon))
             for ln in _corpus_lines(name="mixed_syllables")]
    lines = [ln if not ln.startswith("match_on") else "match_on: [length, n_syllables]"
             for ln in lines]
    if refused:
        _refused_before_writing(lines, tmp_path, _SYLLABLES_REFUSED % 1)
    else:
        _run(_write_design(str(tmp_path), lines), tmp_path)


# ---- schema resolution -------------------------------------------------------
# Twinned with the same section of test-run-pipeline.R. Each test runs from a
# temporary working directory, as an installed package is run outside a clone.

def _write_schema(path, seed):
    """The bundled schema with its seed changed, so the record shows which file ran."""
    with open(_pkg_data("schema.yaml"), encoding="utf-8") as handle:
        text = handle.read()
    assert "\nseed: 2026\n" in text
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text.replace("\nseed: 2026\n", "\nseed: %d\n" % seed, 1))


def _reproducibility(outdir, name="guard_test"):
    import json
    with open(os.path.join(str(outdir), "reports", name + "_english_datasheet_py.json"),
              encoding="utf-8") as handle:
        return json.load(handle)["reproducibility"]


def _same_file(a, b):
    return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))


def test_run_pipeline_falls_back_to_the_bundled_schema_outside_a_checkout(
        tmp_path, monkeypatch, capsys):
    # The default used to be config/schema.yaml relative to the working directory,
    # so the one-call pipeline stopped with "configuration not found" anywhere but
    # the root of a clone, while the command line already fell back.
    monkeypatch.chdir(tmp_path)
    design = _corpus_design(str(tmp_path))
    out = tmp_path / "out"
    run_pipeline(design, outdir=str(out), verbose=False)
    err = capsys.readouterr().err.strip()
    assert err.startswith("lexsync: using the schema at '")
    used = err[len("lexsync: using the schema at '"):].split("'")[0]
    assert _same_file(used, _pkg_data("schema.yaml"))
    rep = _reproducibility(out)
    assert rep["seed"] == 2026
    assert "\\" not in rep["schema_path"]
    assert _same_file(rep["schema_path"], _pkg_data("schema.yaml"))
    with open(os.path.join(str(out), "reports", "guard_test_english_run_log_py.md"),
              encoding="utf-8") as handle:
        assert "- schema_path: " + rep["schema_path"] in handle.read()


def test_run_pipeline_reads_config_then_the_design_directory(tmp_path, monkeypatch, capsys):
    # With no schema named, ./config/schema.yaml comes first (the old default), then
    # the schema beside the design, and only then the bundled copy.
    monkeypatch.chdir(tmp_path)
    study = tmp_path / "study"
    study.mkdir()
    _write_schema(str(study / "schema.yaml"), 99)
    design = _corpus_design(str(study))
    run_pipeline(design, outdir=str(tmp_path / "beside"), verbose=False)
    rep = _reproducibility(tmp_path / "beside")
    assert rep["seed"] == 99
    assert _same_file(rep["schema_path"], str(study / "schema.yaml"))
    (tmp_path / "config").mkdir()
    _write_schema(str(tmp_path / "config" / "schema.yaml"), 7)
    run_pipeline(design, outdir=str(tmp_path / "config_first"), verbose=False)
    rep = _reproducibility(tmp_path / "config_first")
    assert rep["seed"] == 7
    assert rep["schema_path"] == "config/schema.yaml"
    assert "lexsync: using the schema at 'config" in capsys.readouterr().err


def test_an_explicit_missing_schema_is_an_error(tmp_path, monkeypatch):
    # A schema the caller named is never substituted: the error names the bundled
    # copy so the caller can pass it on purpose.
    monkeypatch.chdir(tmp_path)
    design = _corpus_design(str(tmp_path))
    with pytest.raises(FileNotFoundError, match="schema not found: 'missing.yaml'") as exc:
        run_pipeline(design, "missing.yaml", outdir=str(tmp_path), verbose=False)
    assert "importlib.resources" in str(exc.value)
    assert os.path.normcase(_pkg_data("schema.yaml")) in os.path.normcase(str(exc.value))


def test_run_all_falls_back_to_the_bundled_schema(tmp_path, monkeypatch, capsys):
    # run_all read config_dir/schema.yaml and nothing else, so a folder of designs
    # without a schema of its own stopped with "configuration not found".
    from lexsync.run_pipeline import run_all
    monkeypatch.chdir(tmp_path)
    cfg = tmp_path / "designs"
    cfg.mkdir()
    os.replace(_corpus_design(str(cfg)), str(cfg / "design_guard.yaml"))
    run_all(str(cfg), outdir=str(tmp_path / "out"), verbose=False)
    err = capsys.readouterr().err
    assert err.count("lexsync: using the schema at '") == 1
    assert _same_file(_reproducibility(tmp_path / "out")["schema_path"],
                      _pkg_data("schema.yaml"))


@pytest.mark.parametrize("config_dir", ["study", "study/"])
def test_the_schema_notice_names_the_path_as_the_record_does(
        tmp_path, monkeypatch, capsys, config_dir):
    # The notice and the record give the path in POSIX form in both engines, and a
    # folder named with a trailing separator gains no second one (R's file.path()
    # gave "study//schema.yaml" where os.path.join gives "study/schema.yaml").
    from lexsync.datasheet import _posix
    from lexsync.paths import resolve_schema
    monkeypatch.chdir(tmp_path)
    (tmp_path / "study").mkdir()
    _write_schema(str(tmp_path / "study" / "schema.yaml"), 99)
    path, origin = resolve_schema(config_dir=config_dir)
    assert origin == "config_dir"
    assert _posix(path) == "study/schema.yaml"
    assert capsys.readouterr().err == "lexsync: using the schema at 'study/schema.yaml'\n"


# ---- The realised-control report (twinned with test-run-pipeline.R) -------------
# It covered length, frequency, N, OLD20 and match_on, compared every condition with
# the first only, and called every unmatched row "manipulated/free", so real confounds
# went unreported while the Methods text called the control close.

def _comparisons(res):
    """A comparisons CSV as text, so an empty cell reads as '' and not NaN."""
    import pandas as pd
    return pd.read_csv(res["comparisons"], dtype=str, keep_default_na=False)


def _roles(cmp):
    return {(c, r, d): x for c, r, d, x in zip(cmp["condition"], cmp["reference"],
                                               cmp["dimension"], cmp["role"], strict=True)}


def test_one_item_per_condition_under_shortfall_allow_leaves_d_empty(tmp_path):
    """One item has no spread, so d is undefined. Both engines reported d = 0, a perfect
    balance, for a frequency contrast of 3.01 Zipf, and this engine then raised a
    TypeError formatting the missing interval for the run log."""
    lexicon = os.path.join(str(tmp_path), "lexicon.csv")
    with open(lexicon, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("word,freq_zipf\ntime,6.29\nzeal,3.28\n")
    res = _run(_write_design(str(tmp_path), [
        "name: shortfall_one",
        "language: english",
        "lexicon: " + _yaml_path(lexicon),
        "n_per_condition: 20",
        "conditions:",
        "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
        "  - {name: low, define_by: {frequency: [2.0, 4.0]}}",
        "match_on: [length]",
        "matching: {shortfall: allow}",
    ]), tmp_path)
    cmp = _comparisons(res)
    assert list(cmp["dimension"]) == ["length", "frequency", "n_syllables", "bigram_freq"]
    for col in ("cohens_d", "d_ci_low", "d_ci_high", "var_ratio", "tost_p", "equivalent"):
        assert set(cmp[col]) == {""}, col
    assert list(cmp["mean_diff"]) == ["0", "3.01", "1", "0"]
    assert list(cmp["role"]) == ["controlled", "manipulated", "uncontrolled", "uncontrolled"]
    with open(res["log"], encoding="utf-8") as handle:
        assert "on 'frequency': d = NA, TOST p = NA (not shown equivalent)" in handle.read()


def test_frequency_is_manipulated_only_between_cells_whose_windows_differ(tmp_path):
    """Every pair of a 2 x 2 design is compared, and a dimension is manipulated only in
    the rows whose define_by windows on it differ: two high-frequency cells share the
    window [5, 7]."""
    res = _run(_write_design(str(tmp_path), [
        "name: andrews_like",
        "language: english",
        "lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "n_per_condition: 5",
        "pool_filters: {length: [3, 7]}",
        "conditions:",
        "  - {name: HF_largeN, define_by: {frequency: [5.0, 7.0], n_density: [9, 100]}}",
        "  - {name: HF_smallN, define_by: {frequency: [5.0, 7.0], n_density: [0, 5]}}",
        "  - {name: LF_largeN, define_by: {frequency: [2.5, 4.2], n_density: [9, 100]}}",
        "  - {name: LF_smallN, define_by: {frequency: [2.5, 4.2], n_density: [0, 5]}}",
        "match_on: [length]",
    ]), tmp_path)
    role = _roles(_comparisons(res))
    assert role[("HF_smallN", "HF_largeN", "frequency")] == "uncontrolled"
    assert role[("LF_largeN", "HF_largeN", "frequency")] == "manipulated"
    assert role[("LF_smallN", "LF_largeN", "frequency")] == "uncontrolled"
    assert role[("LF_largeN", "HF_smallN", "frequency")] == "manipulated"
    assert role[("HF_smallN", "HF_largeN", "n_density")] == "manipulated"
    assert role[("LF_largeN", "HF_largeN", "n_density")] == "uncontrolled"
    assert {r for k, r in role.items() if k[2] == "length"} == {"controlled"}
    assert {(k[0], k[1]) for k in role} == {
        ("HF_smallN", "HF_largeN"), ("LF_largeN", "HF_largeN"), ("LF_smallN", "HF_largeN"),
        ("LF_largeN", "HF_smallN"), ("LF_smallN", "HF_smallN"), ("LF_smallN", "LF_largeN")}


def test_a_norm_named_only_in_define_by_is_reported_as_manipulated(tmp_path):
    """A joined norm column that defines the conditions is the manipulated variable, and
    it was absent from the report although the stimuli carried it."""
    import pandas as pd
    words = pd.read_csv(_pkg_data("en_example.csv"), keep_default_na=False)["word"]
    norms = os.path.join(str(tmp_path), "conc.csv")
    # Invented ratings, describing no norm.
    pd.DataFrame({"word": words,
                  "concreteness": [1 + (i % 50) / 10 for i in range(len(words))]}).to_csv(
        norms, index=False, lineterminator="\n")
    res = _run(_write_design(str(tmp_path), [
        "name: norm_define",
        "language: english",
        "lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "norms:",
        "  - {path: " + _yaml_path(norms) + ", columns: [concreteness]}",
        "n_per_condition: 5",
        "pool_filters: {length: [3, 7]}",
        "conditions:",
        "  - {name: concrete, define_by: {concreteness: [4.0, 6.0]}}",
        "  - {name: abstract, define_by: {concreteness: [1.0, 2.5]}}",
        "match_on: [length]",
    ]), tmp_path)
    cmp = _comparisons(res)
    assert _roles(cmp)[("abstract", "concrete", "concreteness")] == "manipulated"
    desc = pd.read_csv(res["descriptives"])
    assert "concreteness" in set(desc["dimension"])


def test_a_corpus_report_covers_every_dimension_without_changing_the_stimuli(tmp_path):
    """Syllables and bigram frequency are reported, the latter computed for the report
    only, so the stimuli file and the selection stay as they were."""
    import pandas as pd
    res = _run(_corpus_design(str(tmp_path)), tmp_path)
    cmp = _comparisons(res)
    assert list(cmp["dimension"]) == ["length", "frequency", "n_density", "old20",
                                      "n_syllables", "bigram_freq"]
    assert list(cmp["role"]) == ["controlled", "manipulated", "uncontrolled",
                                 "uncontrolled", "uncontrolled", "uncontrolled"]
    assert "bigram_freq" not in pd.read_csv(res["stimuli"]).columns


def test_a_chinese_design_reports_no_n_syllables_row(tmp_path):
    """A dimension every item lacks has nothing to compare: the syllable estimate is
    undefined for Chinese."""
    res = _run(_write_design(str(tmp_path), _zh_lines(["match_on: [length]"])), tmp_path)
    dims = list(_comparisons(res)["dimension"])
    assert "n_syllables" not in dims
    assert "bigram_freq" in dims


def test_a_generated_design_reports_the_dimensions_it_does_not_control(tmp_path):
    """Words and pseudowords were compared on length alone, which they share by
    construction, so the bigram typicality the generator maximises went unreported.
    The stimuli give each pseudoword its base word and edit distance."""
    import pandas as pd
    res = _run(_write_design(str(tmp_path), [
        "name: gen_report",
        "language: english",
        "paradigm: lexical_decision",
        "items:",
        "  source: generate",
        "  lexicon: " + _yaml_path(_pkg_data("en_example.csv")),
        "n_per_condition: 5",
        "pool_filters: {length: [4, 7], frequency: [3.5, 6.0]}",
    ]), tmp_path)
    cmp = _comparisons(res)
    assert list(cmp["dimension"]) == ["length", "bigram_freq", "n_density", "old20"]
    assert list(cmp["role"]) == ["controlled", "uncontrolled", "uncontrolled",
                                 "uncontrolled"]
    stim = pd.read_csv(res["stimuli"])
    assert not {"bigram_freq", "n_density", "old20"} & set(stim.columns)
    words = stim[stim["condition"] == "word"].set_index("set")
    pseudo = stim[stim["condition"] == "pseudoword"].set_index("set")
    assert (words["base"] == words["target"]).all()
    assert (words["edit_distance"] == 0).all()
    assert (pseudo["base"] == words.loc[pseudo.index, "target"]).all()
    assert pseudo["edit_distance"].between(1, 2).all()


def _golden(name):
    import pandas as pd
    from helper_repo import repo_path
    path = repo_path("output", "reports", name)
    return pd.read_csv(path)


def test_en_ndensity_reports_its_syllable_confound():
    """The dense words have fewer estimated syllables than the sparse ones, an
    uncontrolled difference the report did not show while the Methods text called the
    control close."""
    cmp = _golden("en_ndensity_english_comparisons_py.csv")
    row = cmp[cmp["dimension"] == "n_syllables"].iloc[0]
    assert row["role"] == "uncontrolled"
    assert not row["equivalent"]
    assert abs(row["cohens_d"] - -0.528) < 0.001


def test_en_freqcontinuous_reports_the_spread_of_its_predictor():
    """The selection follows the pool's skew, so its frequency SD is about 0.59 of that
    of 80 values spread evenly over the same range (0.53 against 0.90)."""
    cmp = _golden("en_freqcontinuous_english_comparisons_py.csv").set_index("dimension")
    assert abs(cmp.loc["frequency", "sd_ratio"] - 0.59) < 0.005
    assert cmp.loc["length", "window_low"] < cmp.loc["length", "window_high"]
