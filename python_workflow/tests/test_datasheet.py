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
    assert ds["lexsync_datasheet_version"] == "1.1"
    assert ds["design"]["name"] == "t"
    assert ds["reproducibility"]["seed"] == 2026
    assert "python" in ds["reproducibility"]["versions"]
    roles = {r["dimension"]: r["role"] for r in ds["realised_control"]}
    assert roles["length"] == "controlled"
    assert roles["frequency"] == "manipulated/free"


def test_methods_paragraph_reads_naturally(schema):
    stim = _stim()
    report = match_report(stim, ["length", "frequency", "n_density", "old20"], schema)
    ds = build_datasheet(_design(), schema, report, stim, "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    m = methods_paragraph(ds)
    assert "matched item by item" in m
    assert "0.5-SD equivalence bound" in m
    assert "deterministic and reproducible" in m


def test_write_datasheet_emits_json_and_prereg(schema, tmp_path):
    stim = _stim()
    report = match_report(stim, ["length", "frequency"], schema)
    ds = build_datasheet(_design(), schema, report, stim, "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    jp, mp = write_datasheet(ds, str(tmp_path / "d.json"), str(tmp_path / "d.md"))
    loaded = json.load(open(jp, encoding="utf-8"))
    assert loaded["lexsync_datasheet_version"] == "1.1"
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
    # missing value and are then dropped from the pool by the tolerance windows.
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
    assert "within the 0.4-SD equivalence bound" in methods_paragraph(ds)


def test_an_undefined_d_forces_the_non_affirmative_methods_sentence(schema):
    # A controlled dimension constant at a different value in each condition has an
    # undefined d: the worst possible failure of the matching, not an excludable row.
    stim = _stim()
    stim["length"] = [3, 3, 4, 4]
    report = match_report(stim, ["length", "frequency"], schema)
    ds = build_datasheet(_design(), schema, report, stim, "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    m = methods_paragraph(ds)
    assert "Equivalence was not confirmed on every matched dimension" in m
    assert "realised-control table" in m
    assert "equivalence bound" not in m
    # The undefined cells render as the ASCII placeholder, matching the R engine.
    md = render_datasheet_md(ds)
    assert "| length | controlled | -- | -- |" in md


def test_a_failed_tost_on_a_controlled_dimension_blocks_the_affirmative_sentence(schema):
    stim = _stim()
    stim["length"] = [3, 9, 3, 4]  # defined d, but far too few items to pass a TOST
    report = match_report(stim, ["length", "frequency"], schema)
    ds = build_datasheet(_design(), schema, report, stim, "x.csv",
                         {"stimuli": None, "experiments": {}}, 2026)
    m = methods_paragraph(ds)
    assert "Equivalence was not confirmed on every matched dimension" in m
    assert "The realised control was close" not in m


def test_affirmative_sentence_prints_the_signed_d_beside_its_signed_ci(schema):
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
    assert "was -0.12 (90% CI [" in m
    assert "within the 0.5-SD equivalence bound" in m


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
