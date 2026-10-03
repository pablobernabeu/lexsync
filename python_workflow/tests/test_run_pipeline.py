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
