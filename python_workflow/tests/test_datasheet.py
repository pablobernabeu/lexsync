"""The materials datasheet and pre-registration template."""
import json

import pandas as pd

from lexsync.datasheet import build_datasheet, methods_paragraph, render_datasheet_md, write_datasheet
from lexsync.validation import match_report, match_report_continuous


def _stim():
    return pd.DataFrame({
        "word": ["cat", "dog", "car", "cap"], "condition": ["hi", "hi", "lo", "lo"],
        "set": [1, 2, 1, 2], "length": 3, "frequency": [6, 6, 3, 3],
        "n_density": 2, "old20": 1.5,
    })


def _design():
    return {"name": "t", "language": "english", "match_on": ["length", "n_density", "old20"],
            "n_per_condition": 2, "counterbalance": {"lists": 1}}


def _gen_stim():
    return pd.DataFrame({
        "word": ["cat", "dog", "cag", "dop"],
        "condition": ["word", "word", "pseudoword", "pseudoword"],
        "set": [1, 2, 1, 2], "length": 3,
    })


def _gen_design(method=None):
    items = {"source": "generate", "lexicon": "corpora/derived/en.csv"}
    if method is not None:
        items["generation"] = {"method": method}
    return {"name": "g", "language": "english", "paradigm": "lexical_decision",
            "items": items, "n_per_condition": 2, "counterbalance": {"lists": 1}}


def test_datasheet_structure_and_realised_control(schema):
    stim = _stim()
    report = match_report(stim, ["length", "frequency", "n_density", "old20"], schema)
    ds = build_datasheet(_design(), schema, report, stim, "corpora/derived/en.csv",
                         {"stimuli": None, "experiments": {}}, 2026, engine="python")
    assert ds["lexsync_datasheet_version"] == "1.2"
    assert ds["design"]["name"] == "t"
    assert ds["reproducibility"]["seed"] == 2026
    assert "python" in ds["reproducibility"]["versions"]
    roles = {r["dimension"]: r["role"] for r in ds["realised_control"]}
    assert roles["length"] == "controlled"
    # The design declares no conditions, so no window sets frequency apart.
    assert roles["frequency"] == "uncontrolled"


def test_realised_control_records_the_pair_the_role_and_the_raw_difference(schema):
    """Each entry names the two conditions it contrasts and gives the raw difference.
    A report without roles, as a direct call of match_report gives, takes them from the
    design: a dimension whose define_by windows differ is manipulated, one in match_on
    controlled and any other uncontrolled. Every unmatched dimension was
    "manipulated/free". Pinned identically in test-datasheet.R."""
    stim = _stim()
    design = dict(_design(), conditions=[
        {"name": "hi", "define_by": {"frequency": [5.0, 7.0]}},
        {"name": "lo", "define_by": {"frequency": [2.0, 4.0]}}])
    report = match_report(stim, ["length", "frequency", "n_density", "old20"], schema)
    ds = build_datasheet(design, schema, report, stim, "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    rc = {r["dimension"]: r for r in ds["realised_control"]}
    assert {d: r["role"] for d, r in rc.items()} == {
        "length": "controlled", "frequency": "manipulated", "n_density": "controlled",
        "old20": "controlled"}
    assert (rc["frequency"]["condition"], rc["frequency"]["reference"]) == ("lo", "hi")
    assert rc["frequency"]["mean_diff"] == 3.0
    # A role the report carries is kept.
    report["comparisons"]["role"] = "uncontrolled"
    kept = build_datasheet(design, schema, report, stim, "x.csv",
                           {"stimuli": None, "experiments": {}}, 2026)
    assert {r["role"] for r in kept["realised_control"]} == {"uncontrolled"}


def test_methods_paragraph_reads_naturally(schema):
    stim = _stim()
    report = match_report(stim, ["length", "frequency", "n_density", "old20"], schema)
    ds = build_datasheet(_design(), schema, report, stim, "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    m = methods_paragraph(ds)
    assert "matched item by item" in m
    assert ("Two one-sided tests at a bound of 0.5 SD (alpha 0.05) supported equivalence "
            "on 3 of 3 matched comparisons") in m
    assert "deterministic and reproducible" in m


def test_write_datasheet_emits_json_and_prereg(schema, tmp_path):
    stim = _stim()
    report = match_report(stim, ["length", "frequency"], schema)
    ds = build_datasheet(_design(), schema, report, stim, "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    jp, mp = write_datasheet(ds, str(tmp_path / "d.json"), str(tmp_path / "d.md"))
    loaded = json.load(open(jp, encoding="utf-8"))
    assert loaded["lexsync_datasheet_version"] == "1.2"
    md = open(mp, encoding="utf-8").read()
    assert "Pre-registration template" in md and "Materials (from the lexsync datasheet)" in md


def test_datasheet_continuous_model_and_rows(schema):
    stim = pd.DataFrame({
        "word": ["a", "b", "c", "d"], "condition": "continuous",
        "frequency": [2.0, 3.0, 4.0, 5.0], "length": [3, 4, 3, 4],
        "n_density": [1, 2, 1, 2], "old20": [1.5, 1.6, 1.5, 1.6],
    })
    design = {"name": "c", "language": "english",
              "continuous": {"predictor": "frequency",
                             "controls": ["length", "n_density", "old20"]},
              "match_on": ["length", "n_density", "old20"], "n_per_condition": 4,
              "matching": {"tolerance_k": {"length": 1.5}},
              "counterbalance": {"lists": 1}}
    rep = match_report_continuous(stim, "frequency", ["length", "n_density", "old20"], schema)
    ds = build_datasheet(design, schema, rep, stim, "corpora/derived/en.csv",
                         {"stimuli": None, "experiments": {}}, 2026, engine="python")
    assert ds["analysis"]["suggested_model"] == (
        "response ~ frequency + length + n_density + old20 "
        "+ (1 + frequency | subject) + (1 | item)")
    assert ds["realised_control"][0]["role"] == "predictor"
    assert "pearson_r" in ds["realised_control"][1]
    # The realised spreads and the control windows are part of the record. Frequency
    # 2, 3, 4, 5 is an even spread, so its ratio is 1.
    assert ds["realised_control"][0]["sd_ratio"] == 1.0
    assert {"sd", "sd_ratio", "window_low", "window_high"} <= set(ds["realised_control"][1])
    assert "predictor" in ds["selection"]
    # The control bands the matcher applied are part of the record.
    assert ds["selection"]["tolerance_k"]["length"] == 1.5
    assert ds["selection"]["tolerance_k"]["old20"] == 2.0
    assert "span frequency" in methods_paragraph(ds)
    assert "r with predictor" in render_datasheet_md(ds)


def test_datasheet_without_report_table_source(schema):
    # A table-sourced paradigm has no match report; the datasheet still builds.
    stim = pd.DataFrame({"prime": ["a", "b"], "target": ["x", "y"],
                         "condition": ["r", "u"], "set": [1, 1]})
    design = {"name": "p", "language": "english", "paradigm": "priming",
              "items": {"source": "table", "path": "items/p.csv"},
              "counterbalance": {"lists": 2}}
    ds = build_datasheet(design, schema, None, stim, "items/p.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    assert ds["realised_control"] == []
    assert ds["counterbalancing"]["recipe"] == "latin_square_target"
    assert "item table" in methods_paragraph(ds)
    assert ds["dimensions"] == {}


# --- Datasheet v1.2: the counterbalancing that ran ---------------------------
# test-datasheet.R asserts the same properties.

def _priming_table(conditions=("related", "unrelated"), n_sets=4):
    return pd.DataFrame([{"item": s, "set": s, "condition": c,
                          "prime": "%s%d" % (c[:3], s), "target": "t%d" % s}
                         for s in range(1, n_sets + 1) for c in conditions])


def _table_design(**extra):
    design = {"name": "p", "language": "english", "paradigm": "priming",
              "items": {"source": "table", "path": "items/p.csv"}}
    design.update(extra)
    return design


def test_the_datasheet_records_the_realised_lists(schema):
    # A Latin square without counterbalance.lists realises one list per condition,
    # but the record read counterbalance.lists with a default of 1, and the Methods
    # text said "1 list(s)". The latin_no_lists twin-edge case pins the same run.
    from lexsync.counterbalancing import counterbalance
    design = _table_design()
    out = counterbalance(_priming_table(), design, schema)
    ds = build_datasheet(design, schema, None, out, "items/p.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    record = ds["counterbalancing"]
    assert record["recipe"] == "latin_square_target"
    assert record["lists"] == 2
    assert record["complete"] is True and record["issues"] == []
    assert record["cells"] == [{"list": lst, "condition": c, "n_trials": 2}
                               for lst in (1, 2) for c in ("related", "unrelated")]
    assert "counterbalanced into 2 list(s) (a Latin-square rotation)" in methods_paragraph(ds)
    md = render_datasheet_md(ds)
    assert "## Counterbalanced lists" in md
    assert "| 2 | unrelated | 2 |" in md


def test_build_datasheet_accepts_a_frame_without_list(schema):
    # build_datasheet is exported, so it may be given a frame that was never
    # counterbalanced. The record then gives the lists counterbalance() would deal:
    # one per condition for a Latin square, else counterbalance.lists or 1.
    stim = _priming_table()
    files = {"stimuli": None, "experiments": {}}
    ds = build_datasheet(_table_design(), schema, None, stim, "items/p.csv", files, 2026)
    assert ds["counterbalancing"]["lists"] == 2
    assert ds["counterbalancing"]["cells"] == []
    four = build_datasheet(_table_design(counterbalance={"lists": 4}), schema, None, stim,
                           "items/p.csv", files, 2026)
    assert four["counterbalancing"]["lists"] == 4
    corpus = build_datasheet(_design(), schema, None, _stim(), "x.csv", files, 2026)
    assert corpus["counterbalancing"]["lists"] == 1
    unset = {k: v for k, v in _design().items() if k != "counterbalance"}
    assert build_datasheet(unset, schema, None, _stim(), "x.csv", files,
                           2026)["counterbalancing"]["lists"] == 1


def test_the_datasheet_records_the_recipe_counterbalance_applied(schema):
    # The record inferred the recipe from items.source while counterbalance()
    # dispatched on the paradigm, so a table-sourced lexical-decision design was
    # recorded as a Latin-square rotation it never had.
    stim = pd.DataFrame({"target": ["a", "b"], "condition": ["word", "pseudoword"],
                         "set": [1, 1]})
    files = {"stimuli": None, "experiments": {}}
    design = {"name": "t", "language": "english", "paradigm": "lexical_decision",
              "items": {"source": "table", "path": "items/t.csv"},
              "counterbalance": {"lists": 1}}
    ds = build_datasheet(design, schema, None, stim, "items/t.csv", files, 2026)
    assert ds["counterbalancing"]["recipe"] == "factorial"
    assert "Latin-square" not in methods_paragraph(ds)
    design["paradigm"] = "priming"
    design["events"] = [{"type": "text", "content": "{target}", "duration_ms": 800}]
    ds = build_datasheet(design, schema, None, stim, "items/t.csv", files, 2026)
    assert ds["counterbalancing"]["recipe"] == "latin_square_target"
    design["counterbalance"] = {"lists": 1, "recipe": "factorial"}
    ds = build_datasheet(design, schema, None, stim, "items/t.csv", files, 2026)
    assert ds["counterbalancing"]["recipe"] == "factorial"


def test_the_datasheet_lists_every_experiment_file(schema, tmp_path):
    # The record listed the three experiment scripts only, so it could not verify the
    # loop tables, which hold the trial order and the trigger codes those experiments
    # present. It now lists every file export_experiments wrote.
    from lexsync.counterbalancing import counterbalance
    from lexsync.scripting import export_experiments
    design = _table_design(counterbalance={"lists": 2})
    stim = counterbalance(_priming_table(), design, schema)
    out = export_experiments(stim, design, schema, str(tmp_path))
    ds = build_datasheet(design, schema, None, stim, "items/p.csv",
                         {"stimuli": None, "experiments": out}, 2026)
    assert [a["file"] for a in ds["artifacts"]] == [p.replace("\\", "/") for p in out["files"]]
    assert [a["file"].rsplit("/", 1)[1] for a in ds["artifacts"]][4:] == [
        "p_english_psychopy.csv", "p_english_list1_opensesame.csv",
        "p_english_list1_opensesame_text.csv", "p_english_list2_opensesame.csv",
        "p_english_list2_opensesame_text.csv"]
    assert all(len(a["sha256"]) == 64 for a in ds["artifacts"])


def test_the_datasheet_records_the_presentation_versions(schema):
    from lexsync.counterbalancing import counterbalance
    design = _table_design(counterbalance={"lists": 2})
    ds = build_datasheet(design, schema, None, counterbalance(_priming_table(), design, schema),
                         "items/p.csv", {"stimuli": None, "experiments": {}}, 2026)
    assert ds["counterbalancing"]["versions"] == 2
    assert ds["counterbalancing"]["assignment"] == (
        "version = ((participant - 1) mod 2) + 1 unless a version is given at launch")
    assert ("generated for PsychoPy, OpenSesame and jsPsych. Each participant was presented "
            "one of the 2 lists, assigned in rotation by participant number. Responses were "
            "collected" in methods_paragraph(ds))
    assert ("- **Presentation versions:** 2, assigned as version = ((participant - 1) mod "
            "2) + 1 unless a version is given at launch") in render_datasheet_md(ds)
    # One version: nothing to assign, and nothing said about it.
    single = build_datasheet(_design(), schema, None, _stim(), "x.csv",
                             {"stimuli": None, "experiments": {}}, 2026)
    assert single["counterbalancing"]["versions"] == 1
    assert "Each participant was presented" not in methods_paragraph(single)
    assert "Presentation versions" not in render_datasheet_md(single)
    # Replicates multiply the versions, and a frame without `list` counts the lists
    # counterbalance() would deal.
    reps = pd.concat([_priming_table().assign(replicate=r) for r in (1, 2, 3)],
                     ignore_index=True)
    resampled = dict(design, resample={"n_sets": 3})
    ds = build_datasheet(resampled, schema, None, counterbalance(reps, resampled, schema),
                         "items/p.csv", {"stimuli": None, "experiments": {}}, 2026)
    assert ds["counterbalancing"]["versions"] == 6
    assert ("Each participant was presented one of the 6 presentation versions (one list "
            "of one item set), assigned in rotation by participant number."
            in methods_paragraph(ds))
    unlisted = build_datasheet(resampled, schema, None, reps, "items/p.csv",
                               {"stimuli": None, "experiments": {}}, 2026)
    assert unlisted["counterbalancing"]["versions"] == 6


def test_the_datasheet_names_where_the_reaction_time_is_timed_from(schema):
    # The record called the outcome "reaction time or accuracy" without saying where a
    # reaction time starts, and the Methods text said nothing of the response window.
    # test-datasheet.R pins the same record and text.
    files = {"stimuli": None, "experiments": {}}
    ds = build_datasheet(_design(), schema, None, _stim(), "x.csv", files, 2026)
    assert ds["presentation"] == {"response_windows": [
        {"event": 3, "from": "onset", "window_ms": 2800}]}
    assert ds["analysis"]["response"] == (
        "reaction time from the onset of `{word}`; responses collected for 2800 ms; a "
        "response ends the trial")
    assert ("generated for PsychoPy, OpenSesame and jsPsych. Responses were collected from "
            "target onset until 2800 ms after it, and a response ended the trial. The "
            "selection" in methods_paragraph(ds))
    # A window that opens after the stimulus, for a design that delays the response.
    delayed = dict(_design(), events=[
        {"type": "text", "content": "{word}", "duration_ms": 800},
        {"type": "blank", "duration_ms": 200},
        {"type": "response", "keys": ["f", "j"], "timeout_ms": 1500}])
    ds = build_datasheet(delayed, schema, None, _stim(), "x.csv", files, 2026)
    assert ds["presentation"]["response_windows"] == [
        {"event": 3, "from": "offset", "window_ms": 1500}]
    assert ds["analysis"]["response"] == (
        "reaction time from the opening of a response window after the stimulus; "
        "responses collected for 1500 ms; a response ends the trial")
    assert (" Responses were collected in a 1500 ms window that opened after the stimulus, "
            "and a response ended the trial." in methods_paragraph(ds))
    # A target whose duration varies by trial ends its window a fixed time after it goes.
    varying = dict(_design(), events=[
        {"type": "text", "content": "{word}", "duration": {"from_column": "word_ms"}},
        {"type": "response", "keys": ["f", "j"], "timeout_ms": 2000}])
    ds = build_datasheet(varying, schema, None, _stim().assign(word_ms=[300, 400, 300, 400]),
                         "x.csv", files, 2026)
    assert ds["presentation"]["response_windows"] == [
        {"event": 2, "from": "onset", "window_ms": None, "duration_column": "word_ms",
         "timeout_ms": 2000}]
    assert ds["analysis"]["response"] == (
        "reaction time from the onset of `{word}`; responses collected until 2000 ms after "
        "its offset; a response ends the trial")
    assert (" Responses were collected from target onset until 2000 ms after its offset, "
            "and a response ended the trial." in methods_paragraph(ds))
    # Without a response event, as in self-paced reading, nothing is said, and a record
    # written before the field existed renders as it did.
    spr = _table_design(paradigm="self_paced_reading")
    ds = build_datasheet(spr, schema, None, _priming_table(), "items/p.csv", files, 2026)
    assert ds["presentation"] == {"response_windows": []}
    assert ds["analysis"]["response"] == "the trial outcome (e.g. reaction time or accuracy)"
    assert "Responses were collected" not in methods_paragraph(ds)
    old = {k: v for k, v in build_datasheet(_design(), schema, None, _stim(), "x.csv", files,
                                            2026).items() if k != "presentation"}
    assert "Responses were collected" not in methods_paragraph(old)


def test_an_incomplete_rotation_is_described_as_incomplete(schema):
    from lexsync.counterbalancing import counterbalance
    design = _table_design(counterbalance={"lists": 2})
    out = counterbalance(_priming_table(("identity", "related", "unrelated"), 6), design,
                         schema)
    ds = build_datasheet(design, schema, None, out, "items/p.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    issue = "With 2 lists and 3 conditions, each item appears in only 2 of its 3 conditions."
    assert ds["counterbalancing"]["complete"] is False
    assert ds["counterbalancing"]["issues"] == [issue]
    assert ("counterbalanced into 2 list(s) (an incomplete Latin-square rotation)"
            in methods_paragraph(ds))
    assert "- **Incomplete rotation:** " + issue in render_datasheet_md(ds)


def test_datasheet_records_the_tolerance_windows_the_matcher_applied(schema):
    # The design-level override is what match_stimuli applies, so it is what the
    # provenance record must state; the schema defaults survive for the rest.
    design = _design()
    design["matching"] = {"tolerance_k": {"frequency": 0.111}}
    ds = build_datasheet(design, schema, None, _stim(), "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    assert ds["selection"]["tolerance_k"]["frequency"] == 0.111
    assert ds["selection"]["tolerance_k"]["length"] == 2.0
    plain = build_datasheet(_design(), schema, None, _stim(), "x.csv",
                            {"stimuli": None, "experiments": {}}, 2026)
    assert plain["selection"]["tolerance_k"]["frequency"] == 1.0


def test_datasheet_names_the_generator_that_ran(schema):
    ds = build_datasheet(_gen_design("subsyllabic"), schema, None, _gen_stim(), "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    assert ds["selection"]["generation_method"] == "subsyllabic"
    assert ds["selection"]["method"] == (
        "subsyllabic constituent swap (Wuggy-style, deterministic pseudowords)")
    assert "subsyllabic constituent swap" in methods_paragraph(ds)
    default = build_datasheet(_gen_design(), schema, None, _gen_stim(), "x.csv",
                              {"stimuli": None, "experiments": {}}, 2026)
    assert default["selection"]["generation_method"] == "letter_substitution"
    assert default["selection"]["method"] == (
        "constrained letter substitution (deterministic pseudowords)")


def test_datasheet_dimensions_are_filtered_to_the_controlled_ones(schema):
    gen = build_datasheet(_gen_design("subsyllabic"), schema, None, _gen_stim(), "x.csv",
                          {"stimuli": None, "experiments": {}}, 2026)
    assert set(gen["dimensions"]) == {"length"}
    corpus = build_datasheet(_design(), schema, None, _stim(), "x.csv",
                             {"stimuli": None, "experiments": {}}, 2026)
    assert set(corpus["dimensions"]) == set(schema["dimensions"])


def test_datasheet_reads_the_lexsync_version_from_package_metadata(schema, monkeypatch):
    import importlib.metadata
    monkeypatch.setattr(importlib.metadata, "version", lambda name: "9.9.9")
    ds = build_datasheet(_design(), schema, None, _stim(), "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    assert ds["reproducibility"]["versions"]["lexsync"] == "9.9.9"


# --- Datasheet v1.1: joined norms, and honesty about the pair path -----------
# Both were required by the rule that anything affecting item selection is recorded
# in the datasheet. test-datasheet.R asserts the same properties.

def _pair_stim():
    return pd.DataFrame({
        "item": [1, 1, 2, 2], "set": [1, 1, 2, 2],
        "condition": ["related", "unrelated"] * 2,
        "prime": ["nurse", "window", "dog", "table"],
        "target": ["doctor", "doctor", "cat", "cat"],
        # join_member_norms gives every member the same dimensions.
        "prime.frequency": [4.4, 4.1, 5.1, 4.7],
        "prime.length": [5, 6, 3, 5],
        "target.frequency": [5.0, 5.0, 4.8, 4.8],
        "target.length": [6, 6, 3, 3],
        "pair.lev": [6, 5, 3, 4], "pair.overlap": [0.0, 0.16, 0.0, 0.2],
    })


def _pair_design():
    return {"name": "pc", "language": "english", "paradigm": "priming",
            "items": {"source": "table", "path": "items/p.csv",
                      "members": ["prime", "target"], "lexicon": "corpora/derived/en.csv"},
            "continuous": {"predictor": "target.frequency",
                           "controls": ["target.length", "pair.overlap"]},
            "n_per_condition": 2, "counterbalance": {"lists": 2}}


def test_datasheet_records_the_joined_norm_tables(schema, tmp_path):
    norms = [{"path": "norms/en_conc.csv", "sha256": "a" * 64, "on": "word",
              "columns": [{"column": "concreteness", "n_matched": 900, "n_total": 1000}]}]
    ds = build_datasheet(_design(), schema, None, _stim(), "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026, norms=norms)
    assert ds["materials_source"]["norms"] == norms
    # Coverage is rendered, because the rows a norm table does not cover carry a
    # missing value and drop out of any selection that uses the column.
    md = render_datasheet_md(ds)
    assert "## Joined norms" in md and "900 / 1000" in md
    assert "en_conc.csv" in methods_paragraph(ds)


def test_a_design_without_norms_has_no_norms_key(schema):
    # Not `"norms": null`: every datasheet would then carry a key for a feature the
    # design does not use.
    ds = build_datasheet(_design(), schema, None, _stim(), "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    assert "norms" not in ds["materials_source"]


def test_datasheet_is_honest_that_the_pair_path_selects(schema):
    # `_cross_engine` answered "n/a (user-supplied items)" for every table design.
    # That is true of a plain item table, but a pair-keyed continuous design performs
    # a real selection over it, and that selection is byte-identical across engines --
    # so the record understated the guarantee on the one path that most needs it.
    rep = match_report_continuous(_pair_stim().iloc[[0, 2]], "target.frequency",
                                  ["target.length", "pair.overlap"], schema)
    ds = build_datasheet(_pair_design(), schema, rep, _pair_stim(), "items/p.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    assert ds["selection"]["cross_engine"] == "byte-identical"

    # A plain table design still says n/a: nothing was selected.
    plain = {"name": "p", "language": "english", "paradigm": "priming",
             "items": {"source": "table", "path": "items/p.csv"},
             "counterbalance": {"lists": 2}}
    plain_ds = build_datasheet(plain, schema, None, _pair_stim(), "items/p.csv",
                               {"stimuli": None, "experiments": {}}, 2026)
    assert plain_ds["selection"]["cross_engine"] == "n/a (user-supplied items)"
    assert plain_ds["relational"] is None


def test_datasheet_separates_member_from_relational_dimensions(schema):
    ds = build_datasheet(_pair_design(), schema, None, _pair_stim(), "items/p.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    rel = ds["relational"]
    assert rel["members"] == ["prime", "target"]
    # n_pairs, because items.n_total counts ROWS -- one per pair per condition -- so a
    # reader comparing it against n_per_condition would find it doubled.
    assert rel["n_pairs"] == 2 and ds["items"]["n_total"] == 4
    # The member lexicon is where every member-level control came from, and nothing
    # else in the record names it: materials_source names the item table.
    assert rel["member_lexicon"] == "corpora/derived/en.csv"
    assert rel["member_dimensions"] == ["frequency", "length"]
    assert rel["relational_dimensions"] == ["pair.lev", "pair.overlap"]
    # A pair design joins every lexicon dimension onto each member, so the record
    # lists them all rather than the empty set a plain table design gets.
    assert set(ds["dimensions"]) == set(schema["dimensions"])
    md = render_datasheet_md(ds)
    assert "## Pair-keyed items" in md and "re-expanded" in md


def test_methods_paragraph_counts_pairs_not_items(schema):
    rep = match_report_continuous(_pair_stim().iloc[[0, 2]], "target.frequency",
                                  ["target.length", "pair.overlap"], schema)
    ds = build_datasheet(_pair_design(), schema, rep, _pair_stim(), "items/p.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    m = methods_paragraph(ds)
    assert "2 English prime-target pairs were selected" in m
    assert "items were selected" not in m


def test_artifact_paths_are_recorded_in_posix_form():
    # The datasheet travels with the materials, so it must not record the separator of
    # whichever machine built it, nor disagree with the R engine's record of the same
    # file. os.path.join gives backslashes on Windows; _posix normalises them.
    from lexsync.datasheet import _posix
    assert _posix(r"output\stimuli\x_R.csv") == "output/stimuli/x_R.csv"
    assert _posix("output/stimuli/x_R.csv") == "output/stimuli/x_R.csv"
    assert _posix(None) is None


# --- Truthful prose, audit honesty and provenance completeness ---------------
# test-datasheet.R asserts the same properties.

def test_datasheet_records_the_equivalence_settings_the_report_used(schema):
    ds = build_datasheet(_design(), schema, None, _stim(), "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    assert ds["equivalence"] == {"bound_d": 0.5, "alpha": 0.05}


def test_methods_prose_states_the_schemas_bound_not_a_literal(schema):
    schema = dict(schema, equivalence={"bound_d": 0.4, "alpha": 0.05})
    stim = _stim()
    report = match_report(stim, ["length", "frequency"], schema)
    ds = build_datasheet(_design(), schema, report, stim, "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    assert ds["equivalence"]["bound_d"] == 0.4
    assert "at a bound of 0.4 SD (alpha 0.05)" in methods_paragraph(ds)


def test_an_undefined_d_is_reported_as_undefined(schema):
    # A controlled dimension constant at a different value in each condition has an
    # undefined d: the worst possible failure of the matching, not an excludable row.
    stim = _stim()
    stim["length"] = [3, 3, 4, 4]
    report = match_report(stim, ["length", "frequency"], schema)
    ds = build_datasheet(_design(), schema, report, stim, "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    m = methods_paragraph(ds)
    assert ("Cohen's d is undefined for every matched comparison, and the realised-control "
            "table gives their raw differences") in m
    assert "supported equivalence on 0 of 1 matched comparisons" in m
    assert "The largest difference" not in m
    # The undefined cells render as the ASCII placeholder, matching the R engine.
    md = render_datasheet_md(ds)
    assert "| lo | hi | length | controlled | -1.000 | -- | -- |" in md


def test_a_failed_tost_is_counted_and_explained(schema):
    stim = _stim()
    stim["length"] = [3, 9, 3, 4]  # defined d, but far too few items to pass a TOST
    report = match_report(stim, ["length", "frequency"], schema)
    ds = build_datasheet(_design(), schema, report, stim, "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    m = methods_paragraph(ds)
    assert ("supported equivalence on 0 of 1 matched comparisons; with 2 items per condition "
            "no dimension that varies can pass this test, however well matched.") in m
    assert "The realised control was close" not in m


def test_the_largest_difference_prints_the_signed_d_beside_its_signed_ci(schema):
    stim = pd.DataFrame({
        "word": [f"w{i}" for i in range(120)],
        "condition": ["hi"] * 60 + ["lo"] * 60,
        "length": [4.0, 5.0, 6.0] * 20 + [4.1, 5.1, 6.1] * 20,
        "frequency": [6] * 60 + [3] * 60,
        "set": list(range(60)) * 2,
    })
    report = match_report(stim, ["length", "frequency"], schema)
    ds = build_datasheet(_design(), schema, report, stim, "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    m = methods_paragraph(ds)
    # The anchor's mean is below the comparison's, so the worst d is negative and
    # must be printed with its sign: |d| beside a signed CI misstated the direction.
    assert "was -0.100 characters in length (hi against lo; d = -0.12, 90% CI [" in m
    assert "supported equivalence on 1 of 1 matched comparisons." in m


def test_pairwise_method_records_the_candidate_cap_instead_of_tolerance_windows(schema):
    design = _design()
    design["matching"] = {"method": "joint"}
    cp = [{"condition": "hi", "n_candidates": 5000},
          {"condition": "lo", "n_candidates": 40}]
    ds = build_datasheet(design, schema, None, _stim(), "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026, candidate_pool=cp)
    assert "tolerance_k" not in ds["selection"]
    assert ds["selection"]["candidate_cap"] == {"cap": 1200,
                                                "applied": {"hi": True, "lo": False}}
    assert ("reduced to the 1200 candidates nearest the other condition's centroid "
            "before pairing") in methods_paragraph(ds)
    # The nearest-neighbour default keeps the windows it applies and takes no cap.
    plain = build_datasheet(_design(), schema, None, _stim(), "x.csv",
                            {"stimuli": None, "experiments": {}}, 2026)
    assert "tolerance_k" in plain["selection"]
    assert "candidate_cap" not in plain["selection"]


def test_an_uncapped_pairwise_run_says_nothing_about_the_cap_in_the_prose(schema):
    design = _design()
    design["matching"] = {"method": "optimal"}
    ds = build_datasheet(design, schema, None, _stim(), "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026,
                         candidate_pool=[{"condition": "hi", "n_candidates": 40},
                                         {"condition": "lo", "n_candidates": 40}])
    assert not any(ds["selection"]["candidate_cap"]["applied"].values())
    assert "nearest the other condition's centroid" not in methods_paragraph(ds)


def test_a_pool_designs_candidate_pool_is_recorded_like_a_corpus_designs(schema):
    design = _design()
    design["items"] = {"source": "pool", "path": "items/pool.csv"}
    cp = [{"condition": "hi", "n_candidates": 12}]
    ds = build_datasheet(design, schema, None, _stim(), "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026, candidate_pool=cp)
    assert ds["selection"]["candidate_pool"] == cp


def test_datasheet_records_design_and_schema_checksums_and_the_matcher_audit(schema, tmp_path):
    from lexsync.io_utils import sha256_file
    dpath = tmp_path / "design.yaml"
    dpath.write_text("name: t\n", encoding="utf-8")
    spath = tmp_path / "schema.yaml"
    spath.write_text("seed: 2026\n", encoding="utf-8")
    audit = {"window_relaxations": [{"condition": "lo",
                                     "n_within_tolerance": 1, "n_needed": 2}]}
    nref = {"source": "corpora/derived/en.csv", "n_words": 25000, "sha256": "b" * 64}
    ds = build_datasheet(_design(), schema, None, _stim(), "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026,
                         design_path=str(dpath), schema_path=str(spath),
                         selection_audit=audit, neighbourhood_reference=nref)
    assert ds["reproducibility"]["design_sha256"] == sha256_file(str(dpath))
    assert ds["reproducibility"]["schema_sha256"] == sha256_file(str(spath))
    assert ds["selection"]["window_relaxations"] == [
        {"condition": "lo", "n_within_tolerance": 1, "n_needed": 2}]
    assert ds["selection"]["neighbourhood_reference"] == nref
    # Existing call sites pass none of these, so nothing appears without them, and an
    # audit that recorded no relaxation leaves no key either.
    plain = build_datasheet(_design(), schema, None, _stim(), "x.csv",
                            {"stimuli": None, "experiments": {}}, 2026,
                            selection_audit={"window_relaxations": []})
    assert "design_sha256" not in plain["reproducibility"]
    assert "schema_sha256" not in plain["reproducibility"]
    assert "window_relaxations" not in plain["selection"]
    assert "neighbourhood_reference" not in plain["selection"]


def test_datasheet_records_the_candidates_excluded_for_a_missing_value(schema):
    # A candidate missing a matched dimension is excluded before anything is
    # selected, and the record says how many each condition lost. The field is absent
    # when nothing was excluded, so the datasheets of complete pools do not change.
    # Twinned with test-datasheet.R.
    audit = {"incomplete_dropped": [{"condition": "hi", "n": 3}, {"condition": "lo", "n": 1}]}
    ds = build_datasheet(_design(), schema, None, _stim(), "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026, selection_audit=audit)
    assert ds["selection"]["incomplete_dropped"] == [
        {"condition": "hi", "n": 3}, {"condition": "lo", "n": 1}]
    plain = build_datasheet(_design(), schema, None, _stim(), "x.csv",
                            {"stimuli": None, "experiments": {}}, 2026,
                            selection_audit={"window_relaxations": []})
    assert "incomplete_dropped" not in plain["selection"]
    # The excluded candidates never reach the pairwise cap, so a condition the
    # exclusion brings under it is recorded as uncapped.
    design = _design()
    design["matching"] = {"method": "joint"}
    capped = build_datasheet(design, schema, None, _stim(), "x.csv",
                             {"stimuli": None, "experiments": {}}, 2026,
                             candidate_pool=[{"condition": "hi", "n_candidates": 1250},
                                             {"condition": "lo", "n_candidates": 1300}],
                             selection_audit={"incomplete_dropped": [
                                 {"condition": "hi", "n": 100}]})
    assert capped["selection"]["candidate_cap"]["applied"] == {"hi": False, "lo": True}


def test_the_methods_text_counts_only_the_candidates_that_could_be_matched(schema, tmp_path):
    # The candidate pool counts every word in a condition's window, the ones excluded
    # for a missing matched value among them. Those were never eligible, so the Methods
    # text takes them off, and here the exclusion makes 'hi' the smaller condition.
    # Twinned with test-datasheet.R.
    ds = build_datasheet(_design(), schema, None, _stim(), "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026,
                         candidate_pool=[{"condition": "hi", "n_candidates": 30},
                                         {"condition": "lo", "n_candidates": 25}],
                         selection_audit={"incomplete_dropped": [
                             {"condition": "hi", "n": 14}]})
    m = methods_paragraph(ds)
    assert "The smallest condition was selected from 16 eligible candidates" in m
    # A record read back from its JSON renders the same text.
    jpath, mpath = str(tmp_path / "d.json"), str(tmp_path / "d.md")
    write_datasheet(ds, jpath, mpath)
    with open(jpath, encoding="utf-8") as handle:
        assert methods_paragraph(json.load(handle)) == m


def test_versions_block_records_the_os_and_the_parsing_packages():
    import platform

    from lexsync.datasheet import _versions
    v = _versions("python")
    assert v["os"] == platform.system() + " " + platform.machine()
    assert "rapidfuzz" in v and "pyyaml" in v


def test_analysis_note_is_truthful_about_python_mixed_model_tooling(schema):
    ds = build_datasheet(_design(), schema, None, _stim(), "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    assert "lme4 syntax" in ds["analysis"]["note"]
    assert "statsmodels MixedLM" in ds["analysis"]["note"]
    assert "pymer4/statsmodels" not in ds["analysis"]["note"]
    assert "post-selection diagnostics" in ds["analysis"]["note"]


def test_a_dotted_model_term_earns_the_patsy_quoting_note(schema):
    ds = build_datasheet(_pair_design(), schema, None, _pair_stim(), "items/p.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    assert 'Q("...")' in ds["analysis"]["note"]
    plain = build_datasheet({"name": "c", "language": "english",
                             "continuous": {"predictor": "frequency",
                                            "controls": ["length"]},
                             "n_per_condition": 4, "counterbalance": {"lists": 1}},
                            schema, None, _stim(), "x.csv",
                            {"stimuli": None, "experiments": {}}, 2026)
    assert "Patsy" not in plain["analysis"]["note"]


# ---- Numbers are printed by lexsync, not by each language's printf ----------
# Format specifications such as :.2f round correctly, so an exact tie such as -0.125
# goes to the even digit, while R's sprintf() hands ties to the platform's C library
# and printed 0.165 at two places as "0.16" on Windows. Every number in the Markdown
# and the Methods paragraph now goes through _fmt_dp, which rounds half away from
# zero by the package's own arithmetic. test-datasheet.R pins the same strings.

def _tie_rows():
    pair = {"condition": "lo", "reference": "hi"}
    return [
        dict(pair, dimension="length", role="controlled", cohens_d=0.165, ci_low=-0.125,
             ci_high=0.455, var_ratio=0.0825, tost_p=0.0009, equivalent=True,
             mean_diff=0.04),
        dict(pair, dimension="old20", role="controlled", cohens_d=0.1, ci_low=-0.2,
             ci_high=0.3, var_ratio=1.0, tost_p=0.0, equivalent=True, mean_diff=0.01),
        dict(pair, dimension="frequency", role="manipulated", cohens_d=5.27, ci_low=4.72,
             ci_high=5.83, var_ratio=0.21, tost_p=1.0, equivalent=False, mean_diff=1.5),
    ]


def test_decimal_ties_print_the_same_in_the_methods_paragraph_and_the_table(schema):
    ds = build_datasheet(_design(), schema, None, _stim(), "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    ds["realised_control"] = _tie_rows()
    assert ("was 0.040 characters in length (hi against lo; d = 0.17, 90% CI "
            "[-0.13, 0.46])") in methods_paragraph(ds)
    md = render_datasheet_md(ds)
    # The TOST p is printed to four places, and a stored 0 as a bound.
    assert "| lo | hi | length | controlled | 0.040 | 0.17 | [-0.13, 0.46] | 0.08 | 0.0009 |" in md
    assert "| lo | hi | old20 | controlled | 0.010 | 0.10 | [-0.20, 0.30] | 1.00 | < 0.0001 |" in md
    assert "| lo | hi | frequency | manipulated | 1.500 | 5.27 | [4.72, 5.83] | 0.21 | 1.0000 |" in md


def test_a_continuous_design_prints_its_span_and_correlations_through_the_formatter(schema):
    ds = build_datasheet({"name": "c", "language": "english",
                          "continuous": {"predictor": "frequency", "controls": ["length"]},
                          "n_per_condition": 4, "counterbalance": {"lists": 1}},
                         schema, None, _stim(), "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    ds["realised_control"] = [
        {"dimension": "frequency", "role": "predictor", "pearson_r": None,
         "predictor_span": 0.165},
        {"dimension": "length", "role": "control", "pearson_r": -0.0825,
         "predictor_span": 0.165},
    ]
    m = methods_paragraph(ds)
    assert "to span frequency (a span of 0.17), for analysis" in m
    assert "The largest predictor-control correlation was |r| = 0.083." in m
    md = render_datasheet_md(ds)
    assert "| frequency | predictor | -- | 0.165 |" in md
    assert "| length | control | -0.083 | 0.165 |" in md


def _files():
    return {"stimuli": None, "experiments": {}}


def test_the_datasheet_records_the_tie_break_rule(schema):
    # A matched design records the rule that broke exact ties, with its salt under
    # hash, the default. A design that runs no matcher records none. Twinned with
    # test-datasheet.R.
    ds = build_datasheet(_design(), schema, None, _stim(), "x.csv", _files(), 2026)
    assert ds["selection"]["tie_break"] == {"rule": "hash", "salt": "lexsync-tie-v1"}
    as_0_1 = dict(_design(), matching={"tie_break": "bytes"})
    ds = build_datasheet(as_0_1, schema, None, _stim(), "x.csv", _files(), 2026)
    assert ds["selection"]["tie_break"] == {"rule": "bytes"}
    schema_bytes = dict(schema, matching=dict(schema["matching"], tie_break="bytes"))
    joint = dict(_design(), matching={"method": "joint"})
    ds = build_datasheet(joint, schema_bytes, None, _stim(), "x.csv", _files(), 2026)
    assert ds["selection"]["tie_break"] == {"rule": "bytes"}
    gen = build_datasheet(_gen_design(), schema, None, _gen_stim(), "x.csv", _files(), 2026)
    assert "tie_break" not in gen["selection"]
    cont = build_datasheet({"name": "c", "language": "english",
                            "continuous": {"predictor": "frequency", "controls": ["length"]},
                            "n_per_condition": 4, "counterbalance": {"lists": 1}},
                           schema, None, _stim(), "x.csv", _files(), 2026)
    assert "tie_break" not in cont["selection"]


def test_selection_transparency_says_the_seed_does_not_select(schema):
    # The section said selection was deterministic given the seed, which plays no part
    # in it, and that it was free of item-selection bias. Twinned with test-datasheet.R.
    cp = [{"condition": "hi", "n_candidates": 40}, {"condition": "lo", "n_candidates": 30}]
    lead = ("- Selection is a deterministic function of the materials source, the design "
            "and the schema, blind to any outcome measure, and does not depend on the "
            "seed, which fixes the trial order.")
    tail = ("Automating the choice removes the experimenter's discretion that Forster "
            "(2000) showed can bias item selection.")
    md = render_datasheet_md(build_datasheet(_design(), schema, None, _stim(), "x.csv",
                                             _files(), 2026, candidate_pool=cp))
    assert "given the seed" not in md and "free of item-selection bias" not in md
    assert (lead + " Exact ties between equally close candidates are broken by a keyed "
            "hash of each word (salt lexsync-tie-v1), so no part of the alphabet is "
            "favoured. " + tail) in md
    as_0_1 = dict(_design(), matching={"tie_break": "bytes"})
    md = render_datasheet_md(build_datasheet(as_0_1, schema, None, _stim(), "x.csv",
                                             _files(), 2026, candidate_pool=cp))
    assert (lead + " Exact ties between equally close candidates are broken by spelling, "
            "in byte order, as lexsync 0.1 did, so every tie goes to the spelling that "
            "sorts first. " + tail) in md
    gen = render_datasheet_md(build_datasheet(
        _gen_design(), schema, None, _gen_stim(), "x.csv", _files(), 2026,
        candidate_pool=[{"condition": "words in band", "n_candidates": 100}]))
    assert (lead + " " + tail) in gen


def test_the_methods_paragraph_says_the_seed_fixes_the_trial_order(schema):
    # The seed plays no part in selection, so the Methods text no longer presents it as
    # what makes the selection reproducible. Twinned with test-datasheet.R.
    ds = build_datasheet(_design(), schema, None, _stim(), "x.csv", _files(), 2026)
    version = ds["reproducibility"]["versions"]["lexsync"]
    sentence = ("The selection is deterministic and reproducible (lexsync %s), and the "
                "seed (2026) fixes the trial order." % version)
    assert sentence in methods_paragraph(ds)
    cont = build_datasheet({"name": "c", "language": "english",
                            "continuous": {"predictor": "frequency", "controls": ["length"]},
                            "n_per_condition": 4, "counterbalance": {"lists": 1}},
                           schema, None, _stim(), "x.csv", _files(), 2026)
    assert sentence in methods_paragraph(cont)
    assert "(seed 2026;" not in methods_paragraph(ds) + methods_paragraph(cont)


def test_the_methods_paragraph_from_the_r_record_matches_the_r_rendering():
    # The Methods paragraph is the part of the datasheet meant to be identical across
    # engines; the rest of the Markdown names its engine and is excluded from the
    # cross-engine diff. This engine renders the paragraph from the R engine's
    # committed record of en_freqcontrast, read back from JSON as a reader would, and
    # it must match the paragraph the R engine wrote. test-datasheet.R does the same
    # from the Python record.
    from helper_repo import repo_path
    base = repo_path("output", "reports", "en_freqcontrast_english_datasheet_R",
                     reason="committed reports not available")
    with open(str(base) + ".json", encoding="utf-8") as fh:
        ds = json.load(fh)
    with open(str(base) + ".md", encoding="utf-8") as fh:
        md = fh.read().split("\n")
    at = md.index("## Methods paragraph")
    assert methods_paragraph(ds) == md[at + 2]


# ---- Realised control described before it is tested; a model that says what it is --
# The Methods text called the control close on the strength of equivalence tests that
# fewer than 23 items per condition can never pass, named no uncontrolled confound,
# stated the requested number of items and labelled every interval 90%. The suggested
# model left out the matched covariates, gave the Latin-square categorisation design no
# by-item slope and called its structure maximal whatever its slopes. The committed
# records below are read back as a reader would read them. test-datasheet.R pins the
# same strings.

def _committed_record(name):
    from helper_repo import repo_path
    base = repo_path("output", "reports", name, reason="committed reports not available")
    with open(str(base) + ".json", encoding="utf-8") as handle:
        return json.load(handle)


def _matched_stim(n):
    # Identical lengths in both conditions, so only the number of items decides the TOST.
    lengths = [4.0 + (i % 3) for i in range(n)]
    return pd.DataFrame({"word": ["w%d" % i for i in range(2 * n)],
                         "condition": ["hi"] * n + ["lo"] * n,
                         "set": list(range(1, n + 1)) * 2, "length": lengths * 2,
                         "frequency": [6.0 + (i % 2) / 10 for i in range(n)]
                         + [3.0 + (i % 2) / 10 for i in range(n)]})


def _frequency_conditions(design):
    return dict(design, conditions=[{"name": "hi", "define_by": {"frequency": [5.0, 7.0]}},
                                    {"name": "lo", "define_by": {"frequency": [2.0, 4.0]}}])


def test_the_methods_text_describes_the_realised_control_before_testing_it():
    m = methods_paragraph(_committed_record("en_freqcontrast_english_datasheet_py"))
    assert ("The largest difference on a matched dimension was 0.325 neighbours in "
            "n_density (high_frequency against low_frequency; d = 0.06, 90% CI "
            "[-0.21, 0.32]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) "
            "supported equivalence on 3 of 3 matched comparisons. No uncontrolled "
            "dimension differed by more than 0.5 SD.") in m
    assert "The realised control was close" not in m
    assert "equivalence bound" not in m


def test_with_too_few_items_the_methods_text_says_no_dimension_can_pass(schema):
    from lexsync.datasheet import _tost_min_n
    assert [_tost_min_n(0.5, 0.05), _tost_min_n(0.3, 0.05), _tost_min_n(0.5, 0.005)] == [
        23, 62, 56]

    def paragraph(n):
        stim = _matched_stim(n)
        report = match_report(stim, ["length", "frequency"], schema)
        design = _frequency_conditions(dict(_design(), n_per_condition=n))
        return methods_paragraph(build_datasheet(design, schema, report, stim, "x.csv",
                                                 _files(), 2026))

    assert ("supported equivalence on 0 of 1 matched comparisons; with 15 items per "
            "condition no dimension that varies can pass this test, however well "
            "matched.") in paragraph(15)
    m = paragraph(24)
    assert "supported equivalence on 1 of 1 matched comparisons." in m
    assert "no dimension that varies can pass" not in m


def test_a_bound_too_small_for_any_request_still_gets_the_caveat(schema):
    # Below a bound of about 5e-5 SD, no n_per_condition either engine accepts can pass.
    # R's search returned NA there, with a warning, and its Methods text then stopped
    # with an error, while this engine searched on. At smaller bounds R's search never
    # ended. Both now stop at the largest request and return infinity.
    from lexsync.datasheet import _tost_min_n
    assert _tost_min_n(1e-4, 0.05) == 541108692
    assert _tost_min_n(1e-5, 0.05) == float("inf")
    tiny = dict(schema, equivalence={"bound_d": 1e-5, "alpha": 0.05})
    stim = _matched_stim(30)
    report = match_report(stim, ["length", "frequency"], tiny)
    ds = build_datasheet(_frequency_conditions(_design()), tiny, report, stim, "x.csv",
                         _files(), 2026)
    assert ("Two one-sided tests at a bound of 1e-05 SD (alpha 0.05) supported equivalence "
            "on 0 of 1 matched comparisons; with 30 items per condition no dimension that "
            "varies can pass this test, however well matched.") in methods_paragraph(ds)


def test_the_methods_text_names_the_uncontrolled_dimensions_that_differ():
    m = methods_paragraph(_committed_record("en_ndensity_english_datasheet_py"))
    assert ("Dimensions the design did not control differed: old20 (dense_neighbourhood "
            "against sparse_neighbourhood: -0.536 mean Levenshtein distance; d = -2.39, "
            "90% CI [-2.73, -2.04]) and n_syllables (dense_neighbourhood against "
            "sparse_neighbourhood: -0.288 syllables; d = -0.53, 90% CI "
            "[-0.79, -0.26]).") in m


def test_a_lexical_decision_reports_what_its_pseudowords_were_not_matched_on():
    m = methods_paragraph(_committed_record("en_lexdec_english_datasheet_py"))
    assert ("Words and pseudowords were matched on length only, and the words differed "
            "from the pseudowords in bigram frequency (d = -0.97, 90% CI [-1.29, -0.65]), "
            "N (d = 0.01, 90% CI [-0.30, 0.31]) and OLD20 (d = -0.04, 90% CI "
            "[-0.34, 0.27]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) "
            "supported equivalence on 1 of 1 matched comparisons.") in m


def test_the_interval_is_labelled_by_the_configured_alpha(schema):
    strict = dict(schema, equivalence={"bound_d": 0.5, "alpha": 0.005})
    stim = _matched_stim(30)
    report = match_report(stim, ["length", "frequency"], strict)
    ds = build_datasheet(_frequency_conditions(_design()), strict, report, stim, "x.csv",
                         _files(), 2026)
    m = methods_paragraph(ds)
    assert "(hi against lo; d = 0.00, 99% CI [" in m
    assert "at a bound of 0.5 SD (alpha 0.005)" in m
    assert "90%" not in m
    md = render_datasheet_md(ds)
    assert "| Cohen's d | 99% CI | Var ratio |" in md
    assert "90% CI" not in md


def test_a_shortfall_states_the_items_selected_and_the_request(schema):
    # One item per condition under shortfall: allow. The text stated the 20 requested.
    stim = pd.DataFrame({"word": ["cat", "dog"], "condition": ["hi", "lo"], "set": [1, 1],
                         "length": [3, 3], "frequency": [6.0, 3.0]})
    design = dict(_frequency_conditions(_design()), n_per_condition=20,
                  matching={"shortfall": "allow"})
    report = match_report(stim, ["length", "frequency"], schema)
    ds = build_datasheet(design, schema, report, stim, "x.csv", _files(), 2026)
    assert ds["design"]["n_per_condition"] == 20
    assert ds["items"]["n_per_condition_realised"] == [{"condition": "hi", "n": 1},
                                                        {"condition": "lo", "n": 1}]
    m = methods_paragraph(ds)
    assert m.startswith("1 item per condition (of 20 requested) was selected from the "
                        "English lexicon")
    assert ("Cohen's d is undefined for every matched comparison, and the realised-control "
            "table gives their raw differences") in m
    assert "with 1 item per condition no dimension that varies can pass this test" in m
    # A single item has no TOST verdict either. The table printed Python's None there,
    # where the R renderer prints its placeholder.
    md = render_datasheet_md(ds)
    assert "| lo | hi | length | controlled | 0.000 | -- | -- | -- | -- | -- |" in md
    assert "None" not in md
    # A design that leaves n_per_condition to the matcher records the matcher's 20, and
    # that is the request the two items here fall short of.
    unset = {k: v for k, v in _design().items() if k != "n_per_condition"}
    plain = build_datasheet(unset, schema, None, _stim(), "x.csv", _files(), 2026)
    assert plain["design"]["n_per_condition"] == 20
    assert methods_paragraph(plain).startswith(
        "2 items per condition (of 20 requested) were selected")


def test_the_realised_counts_are_per_replicate_when_the_design_resamples(schema):
    reps = pd.concat([_stim().assign(replicate=r) for r in (2, 1)], ignore_index=True)
    ds = build_datasheet(dict(_design(), resample={"n_sets": 2}), schema, None, reps,
                         "x.csv", _files(), 2026)
    assert ds["items"]["n_per_condition_realised"] == [
        {"replicate": 1, "condition": "hi", "n": 2}, {"replicate": 1, "condition": "lo", "n": 2},
        {"replicate": 2, "condition": "hi", "n": 2}, {"replicate": 2, "condition": "lo", "n": 2}]
    assert methods_paragraph(ds).startswith("2 items per condition were selected")


def test_a_continuous_methods_text_gives_the_spreads_and_the_windows():
    m = methods_paragraph(_committed_record("en_freqcontinuous_english_datasheet_py"))
    assert ("80 English items were selected to span frequency (a span of 3.05 and an SD of "
            "0.53, 0.59 times that of an even spread over the span), for analysis by "
            "regression or a mixed model rather than a between-condition contrast (Kuperman, "
            "2015; Liben-Nowell et al., 2019). The controls were banded within windows of "
            "the mean \u00b1 1.5 SD of an initial selection spread over the ranks of "
            "frequency (length 3.99 to 8.13, n_density -2.52 to 7.54 and old20 1.29 to "
            "2.91), and their realised SDs were 0.76, 0.41 and 0.68 of the pool's. The "
            "largest predictor-control correlation was |r| = 0.301.") in m
    assert "near-constant" not in m
    # The first pass spreads over the predictor's ranks and follows the pool's skew, so
    # calling it an even spread contradicted the SD ratio given a sentence earlier.
    assert "initial even spread" not in m


def test_a_relaxed_continuous_selection_says_its_windows_were_widened(schema):
    design = {"name": "c", "language": "english", "n_per_condition": 4,
              "continuous": {"predictor": "frequency", "controls": ["length"]},
              "match_on": ["length"], "counterbalance": {"lists": 1}}
    stim = pd.DataFrame({"word": ["a", "b", "c", "d"], "condition": "continuous",
                         "frequency": [2.0, 3.0, 4.0, 5.0], "length": [3, 4, 3, 4]})
    audit = {"control_windows": [{"dimension": "length", "low": 3.2, "high": 3.8,
                                  "pool_sd": 1.0}]}
    report = match_report_continuous(stim, "frequency", ["length"], schema, audit=audit)
    banded = methods_paragraph(build_datasheet(design, schema, report, stim, "x.csv",
                                               _files(), 2026))
    assert (" The control was banded within a window of the mean \u00b1 2 SD of an initial "
            "selection spread over the ranks of frequency (length 3.20 to 3.80), and its "
            "realised SD was 0.58 of the pool's.") in banded
    relaxed = {"window_relaxations": [{"condition": "continuous", "n_within_tolerance": 0,
                                       "n_needed": 4}]}
    m = methods_paragraph(build_datasheet(design, schema, report, stim, "x.csv", _files(),
                                          2026, selection_audit=relaxed))
    assert (" The control window, the mean \u00b1 2 SD of an initial selection spread over "
            "the ranks of frequency (length 3.20 to 3.80), held too few items and was "
            "widened to the whole pool, and its realised SD was 0.58 of the pool's.") in m


def test_the_realised_control_table_names_the_pair_and_the_raw_difference(schema):
    stim = _stim()
    report = match_report(stim, ["length", "frequency"], schema)
    md = render_datasheet_md(build_datasheet(_design(), schema, report, stim, "x.csv",
                                             _files(), 2026))
    assert ("| Condition | Reference | Dimension | Role | Raw difference | Cohen's d | "
            "90% CI | Var ratio | TOST p | Equivalent |") in md
    assert ("The raw difference and Cohen's d are the reference mean minus the condition "
            "mean") in md
    assert "| lo | hi | length | controlled | 0.000 | 0.00 | [0.00, 0.00] | 1.00 | < 0.0001 |" in md
    assert "| lo | hi | frequency | uncontrolled | 3.000 | -- | -- | 1.00 | 1.0000 |" in md


def test_a_matched_design_adds_its_matched_dimensions_as_centred_covariates(schema):
    # Length is the same for every item here, so it is left out of the model.
    stim = _stim().assign(n_density=[1, 2, 3, 4], old20=[1.5, 1.6, 1.7, 1.8])
    a = build_datasheet(_design(), schema, None, stim, "x.csv", _files(), 2026)["analysis"]
    assert a["suggested_model"] == (
        "response ~ condition + scale(n_density, scale = FALSE) + scale(old20, scale = FALSE)"
        " + (1 + condition | subject) + (1 | item)")
    assert "(Sassenhagen & Alday, 2016)" in a["note"]
    assert ("The matched dimension length is constant among the selected items, so it is "
            "left out.") in a["note"]
    # The covariates take no random slopes, so the structure is described, not called
    # maximal.
    assert "maximal" not in a["note"]
    assert ("Begin with random slopes for condition, the manipulated factor, by subject and, "
            "where it varies within items, by item (Barr et al., 2013); the matched "
            "covariates enter as fixed effects only.") in a["note"]
    assert ("If the model is singular or fails to converge, simplify it as Matuschek et al. "
            "(2017) describe.") in a["note"]


def test_a_lexical_decision_models_the_condition_column(schema):
    a = build_datasheet(_gen_design(), schema, None, _gen_stim(), "x.csv", _files(),
                        2026)["analysis"]
    assert a["suggested_model"] == ("response ~ condition + (1 + condition | subject) + "
                                    "(1 | item)")
    assert "The condition column codes lexicality, word or pseudoword." in a["note"]
    assert "Begin with this maximal structure (Barr et al., 2013)." in a["note"]


def test_a_latin_square_gives_items_a_slope_for_condition(schema):
    categorisation = _table_design(paradigm="categorisation")
    a = build_datasheet(categorisation, schema, None, _priming_table(("narrow", "broad")),
                        "items/p.csv", _files(), 2026)["analysis"]
    assert a["suggested_model"] == ("response ~ condition + (1 + condition | subject) + "
                                    "(1 + condition | item)")
    assert "Begin with this maximal structure (Barr et al., 2013)." in a["note"]
    # The recipe that ran decides, not the item source: a factorial item table keeps the
    # intercept alone.
    factorial = _table_design(paradigm="factorial", counterbalance={"lists": 2})
    table = pd.DataFrame({"item": [1, 2, 3, 4], "set": [1, 1, 2, 2],
                          "condition": ["word", "pseudoword"] * 2,
                          "target": ["cat", "cag", "dog", "dop"]})
    a = build_datasheet(factorial, schema, None, table, "items/p.csv", _files(),
                        2026)["analysis"]
    assert a["suggested_model"] == ("response ~ condition + (1 + condition | subject) + "
                                    "(1 | item)")


def test_a_continuous_pair_design_models_the_condition_and_its_interaction(schema):
    a = build_datasheet(_pair_design(), schema, None, _pair_stim(), "items/p.csv", _files(),
                        2026)["analysis"]
    assert a["suggested_model"] == (
        "response ~ condition * target.frequency + target.length + pair.overlap + "
        "(1 + condition * target.frequency | subject) + (1 + condition | item)")
    # The controls take no random slopes, so the structure is described, not called
    # maximal.
    assert "maximal" not in a["note"]
    assert ("Begin with random slopes for condition, target.frequency and their interaction "
            "by subject and for condition by item (Barr et al., 2013); the controls enter "
            "as fixed effects only.") in a["note"]
    # A pair design with one condition has no condition term.
    related = _pair_stim()[lambda f: f["condition"] == "related"]
    a = build_datasheet(_pair_design(), schema, None, related, "items/p.csv", _files(),
                        2026)["analysis"]
    assert a["suggested_model"] == ("response ~ target.frequency + target.length + "
                                    "pair.overlap + (1 + target.frequency | subject) + "
                                    "(1 | item)")
    assert ("Begin with a random slope for target.frequency by subject (Barr et al., 2013); "
            "the controls enter as fixed effects only.") in a["note"]


def test_the_committed_records_suggest_the_models_their_designs_need():
    # The categorisation design rotates its cues over its targets by a Latin square, the
    # continuous priming design crosses its condition with target frequency, and the
    # frequency contrast adds its matched covariates, so only the first is maximal.
    categorisation = _committed_record("en_categorisation_english_datasheet_py")["analysis"]
    assert categorisation["suggested_model"].endswith("+ (1 + condition | item)")
    assert "Begin with this maximal structure" in categorisation["note"]
    priming = _committed_record("en_priming_continuous_english_datasheet_py")["analysis"]
    assert "(1 + condition * target.frequency | subject)" in priming["suggested_model"]
    assert priming["suggested_model"].endswith("+ (1 + condition | item)")
    contrast = _committed_record("en_freqcontrast_english_datasheet_py")["analysis"]
    assert "scale(n_density, scale = FALSE)" in contrast["suggested_model"]
    assert "maximal" not in contrast["note"] and "maximal" not in priming["note"]


def test_a_design_with_more_than_two_conditions_is_told_how_to_recode(schema):
    four = pd.DataFrame({"word": list("abcdefgh"),
                         "condition": ["HF_l", "HF_l", "HF_s", "HF_s",
                                       "LF_l", "LF_l", "LF_s", "LF_s"],
                         "set": [1, 2] * 4, "length": [3, 4] * 4,
                         "n_density": [1, 2] * 4, "old20": [1.5, 1.6] * 4})
    note = build_datasheet(_design(), schema, None, four, "x.csv", _files(),
                           2026)["analysis"]["note"]
    assert ("If the conditions cross two or more factors, recode condition into those "
            "factors (for example frequency * neighbourhood) with sum coding.") in note
    two = build_datasheet(_design(), schema, None, _stim(), "x.csv", _files(), 2026)
    assert "recode condition" not in two["analysis"]["note"]
