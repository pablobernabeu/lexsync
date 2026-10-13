"""Instructions, the response mapping and the answers it gives every trial.

No generated experiment said which key meant what. jsPsych named the keys and nothing
more, PsychoPy and OpenSesame started the trials at once, and a generated lexical
decision had no `answer` column, so its main trials could not be scored. The practice
table presented the word 'plank' as a pseudoword, and every categorisation item was a
'yes' trial, so pressing f on every trial scored 100%.

A design may now give `instructions`, `response_mapping` and `rotate_mapping_by_list`.
A lexical decision maps word to the response event's first key and pseudoword to its
second by default, and lexsync writes English instructions for the tasks it knows.
The loop tables carry each trial's correct key in `answer`, derived when the
experiments are exported, and the stimuli file does not change.
R_workflow/tests/testthat/test-instructions.R holds the R engine to the same tests, by
the same names. The runners' start gate is tested in test_psychopy_export.py,
test_jspsych_export.py and test_osexp_validator.py, since each template is one shared
file.
"""
import json
import os
import re

import pandas as pd
import pytest
import yaml
from helper_repo import repo_path

import lexsync
from lexsync.datasheet import _mapping_note, _response_mapping_record, methods_paragraph
from lexsync.design import validate_design
from lexsync.io_utils import read_config
from lexsync.run_pipeline import run_pipeline
from lexsync.scripting import (
    _assign_answers,
    _instruction_notes,
    _instruction_texts,
    _key_label,
    export_experiments,
    presentation_versions,
)

LEXDEC = {"name": "t", "language": "english", "paradigm": "lexical_decision"}
# The events of en_lexdec_blocks: keys f and j, and feedback during practice only.
BLOCKS_EVENTS = [
    {"type": "fixation", "content": "+", "duration_ms": 500},
    {"type": "text", "content": "{target}", "duration_ms": 800, "trigger": "condition"},
    {"type": "response", "keys": ["f", "j"], "timeout_ms": 2000},
    {"type": "feedback", "answer": "answer", "duration_ms": 600, "blocks": ["practice"]},
    {"type": "blank", "duration_ms": 250}]

LEXDEC_TEXT = ("You will see a string of letters. Press %s if it is a real English word and "
               "%s if it is not. Respond as quickly and accurately as you can.")
LANGUAGE_NOTE = ("lexsync: the design gives no `instructions` and its language is '%s', so "
                 "the experiments show lexsync's instructions in English; give `instructions` "
                 "in the participants' language.")
TASK_NOTE = ("lexsync: the design gives no `instructions`, and lexsync cannot tell what the "
             "response keys of a %s design mean, so the experiments only name the keys; give "
             "`instructions` that say what each key means.")


def _lexdec_stim():
    """Two words and two pseudowords in one list, with no answer of their own, as the
    generator writes them."""
    return pd.DataFrame({"target": ["cat", "dog", "cag", "dop"],
                         "condition": ["word", "word", "pseudoword", "pseudoword"],
                         "set": [1, 2, 1, 2], "trial": [1, 2, 3, 4], "list": [1, 1, 1, 1]})


def _blocks_stim(lists=(1,)):
    """Practice rows that name their answer, then main rows that do not, in each list."""
    rows = []
    for lst in lists:
        rows += [("clock", "word", "f", 3, "practice", lst), ("plang", "pseudoword", "j", 4,
                                                              "practice", lst),
                 ("cat", "word", None, 1, "main", lst), ("cag", "pseudoword", None, 1, "main", lst),
                 ("dog", "word", None, 2, "main", lst), ("dop", "pseudoword", None, 2, "main", lst)]
    stim = pd.DataFrame(rows, columns=["target", "condition", "answer", "set", "block", "list"])
    stim["trial"] = stim.groupby("list").cumcount() + 1
    return stim


def _read(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")


def _main_answers(stim):
    main = stim[stim["block"] == "main"]
    return {(int(lst), cond): set(main.loc[(main["list"] == lst) & (main["condition"] == cond),
                                           "answer"])
            for lst in sorted(set(main["list"])) for cond in ("word", "pseudoword")}


def test_a_lexical_decision_takes_its_answers_from_the_response_mapping(schema, tmp_path):
    # The paradigm's events allow left and right, so word takes left and pseudoword
    # right, and every main trial can be scored.
    export_experiments(_lexdec_stim(), LEXDEC, schema, str(tmp_path))
    loop = _read(tmp_path / "t_english_psychopy.csv")
    assert list(loop.columns) == ["trial", "list", "set", "condition", "target", "answer",
                                  "condition_trigger", "item_trigger"]
    assert list(zip(loop["condition"], loop["answer"], strict=True)) == [
        ("word", "left"), ("word", "left"), ("pseudoword", "right"), ("pseudoword", "right")]
    text = _read(tmp_path / "t_english_opensesame_text.csv")
    assert list(text["answer"]) == ["left", "left", "right", "right"]
    # The jsPsych page names them as the browser does (see the test below).
    html = (tmp_path / "t_english.html").read_text(encoding="utf-8")
    trials = json.loads(re.search(r"const TRIALS = (.*?);\n", html, re.S).group(1))
    assert [t["answer"] for t in trials] == ["arrowleft", "arrowleft", "arrowright",
                                             "arrowright"]
    # The answers are derived for the export, so the frame passed in is unchanged.
    stim = _lexdec_stim()
    export_experiments(stim, LEXDEC, schema, str(tmp_path))
    assert "answer" not in stim.columns


def test_main_trials_follow_the_keys_of_the_practice_table(schema, tmp_path):
    # en_lexdec_blocks's events allow f and j, and its practice table codes word as f,
    # so its main trials take f for a word and j for a pseudoword. Rows that name their
    # own answer keep it.
    design = dict(LEXDEC, events=BLOCKS_EVENTS)
    stim, notes = _assign_answers(_blocks_stim(), design)
    assert notes == []
    assert _main_answers(stim) == {(1, "word"): {"f"}, (1, "pseudoword"): {"j"}}
    practice = stim[stim["block"] == "practice"]
    assert list(practice["answer"]) == ["f", "j"]
    export_experiments(_blocks_stim(), design, schema, str(tmp_path))
    loop = _read(tmp_path / "t_english_psychopy.csv")
    assert all(loop["answer"] == loop["condition"].map({"word": "f", "pseudoword": "j"}))


def _page(path, name):
    """One of the JSON blobs a jsPsych page embeds, read back."""
    html = open(path, encoding="utf-8").read()
    return json.loads(re.search(r"const %s = (.*?);\n" % name, html, re.S).group(1))


def test_the_jspsych_page_names_each_answer_as_the_browser_does(schema, tmp_path):
    # jsPsych records a key by the browser's name for it, arrowleft for the left arrow,
    # and the page's events name the keys so, but its trials named each answer as the
    # other targets do, left. No correct response then equalled its trial's answer, and a
    # feedback screen called every correct response incorrect. The page now names an
    # answer as it names the keys, and the loop tables keep the other targets' names.
    out = export_experiments(_lexdec_stim(), LEXDEC, schema, str(tmp_path))
    keys = [ev["respond"]["keys"] for ev in _page(out["jspsych"], "EVENTS") if "respond" in ev]
    assert keys == [["arrowleft", "arrowright"]]
    assert [t["answer"] for t in _page(out["jspsych"], "TRIALS")] == [
        "arrowleft", "arrowleft", "arrowright", "arrowright"]
    assert list(_read(tmp_path / "t_english_psychopy.csv")["answer"]) == [
        "left", "left", "right", "right"]
    # A trial's own answer is mapped as well, around the spaces a runner ignores, and a
    # key the browser names as lexsync does is left alone.
    events = [dict(ev, keys=["space", "return"]) if ev["type"] == "response" else ev
              for ev in BLOCKS_EVENTS]
    stim = _blocks_stim()
    stim["answer"] = [" space", "j", None, None, None, None]
    out = export_experiments(stim, dict(LEXDEC, events=events), schema, str(tmp_path))
    assert {(t["block"], t["condition"], t["answer"])
            for t in _page(out["jspsych"], "TRIALS")} == {
        ("practice", "word", " "), ("practice", "pseudoword", "j"),
        ("main", "word", " "), ("main", "pseudoword", "enter")}


def test_an_answer_read_as_a_number_keeps_the_text_of_its_cell(schema, tmp_path):
    # A practice table that codes its answers as number keys is read with a numeric
    # answer column, which this engine holds as floats once the main trials' missing
    # answers join it. The answer 1.0 was compared with the key 1 as '1.0', so the run
    # log said that practice answers following the mapping contradicted it, and the page
    # wrote them as numbers beside the main trials' text, where the R engine wrote text.
    # Both engines now take such an answer as the text its loop-table cell holds.
    events = [dict(ev, keys=[1, 2]) if ev["type"] == "response" else ev
              for ev in BLOCKS_EVENTS]
    design = dict(LEXDEC, events=events)
    stim = _blocks_stim()
    stim["answer"] = [1.0, 2.0] + [float("nan")] * 4
    out, notes = _assign_answers(stim, design)
    assert notes == []
    assert list(out["answer"]) == ["1", "2", "1", "2", "1", "2"]
    page = export_experiments(stim, design, schema, str(tmp_path))["jspsych"]
    assert sorted({t["answer"] for t in _page(page, "TRIALS")}) == ["1", "2"]
    # The text is what both engines' CSV writers write: 100000, not R's 1e+05.
    texts = [lexsync.scripting._answer_text(v)
             for v in (100000.0, 2.5, True, None, float("nan"), " f ")]
    assert texts == ["100000", "2.5", "TRUE", None, None, " f "]


def test_a_mapping_naming_a_key_the_response_does_not_allow_is_refused(schema):
    design = dict(LEXDEC, events=BLOCKS_EVENTS)
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: response_mapping maps 'word' to 'k', but the response event allows "
            "only f and j.")):
        validate_design(dict(design, response_mapping={"word": "k", "pseudoword": "j"}), schema)
    for bad in ({}, ["f", "j"], {"word": ["f", "j"]}, {"word": None}, {"word": True}):
        with pytest.raises(ValueError, match=re.escape(
                "lexsync: response_mapping must map each condition to one response key, as "
                "in {word: f, pseudoword: j}.")):
            validate_design(dict(design, response_mapping=bad), schema)
    passive = {"name": "t", "language": "english", "events": BLOCKS_EVENTS[:2],
               "response_mapping": {"word": "f"}}
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: the design gives `response_mapping`, but none of its events is a "
            "response whose keys it could name.")):
        validate_design(passive, schema)
    # A key the response allows passes, and the default needs no key at all.
    assert validate_design(dict(design, response_mapping={"word": "j", "pseudoword": "f"}),
                           schema) == []
    assert validate_design(design, schema) == []


def test_a_declared_mapping_must_cover_the_trials_conditions(schema, tmp_path):
    design = dict(LEXDEC, events=BLOCKS_EVENTS)
    stim = _lexdec_stim().replace({"condition": {"pseudoword": "nonword"}})
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: response_mapping gives no key for condition 'nonword', and 2 "
            "trial(s) of it have no answer of their own.")):
        _assign_answers(stim, dict(design, response_mapping={"word": "f"}))
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: response_mapping names condition 'pseudowrod', which no trial has; "
            "the trials' conditions are word and pseudoword.")):
        export_experiments(_lexdec_stim(), dict(design, response_mapping={
            "word": "f", "pseudoword": "j", "pseudowrod": "j"}), schema, str(tmp_path))
    # The default maps word and pseudoword only, and says so for any other condition.
    out, notes = _assign_answers(stim, design)
    assert list(out["answer"].fillna("")) == ["f", "f", "", ""]
    assert notes == ["lexsync: 2 trial(s) of condition 'nonword' have no answer, since the "
                     "lexical-decision default maps only word and pseudoword; give "
                     "`response_mapping`."]


def test_rotation_swaps_the_keys_on_list_two():
    # List k moves each key k - 1 places along the response event's keys, a swap on
    # every even-numbered list when there are two.
    design = dict(LEXDEC, events=BLOCKS_EVENTS, rotate_mapping_by_list=True)
    stim, notes = _assign_answers(_blocks_stim(lists=(1, 2)), design)
    assert _main_answers(stim) == {(1, "word"): {"f"}, (1, "pseudoword"): {"j"},
                                   (2, "word"): {"j"}, (2, "pseudoword"): {"f"}}
    # The practice table keeps its answers, which list 2's mapping contradicts.
    assert notes == [
        "lexsync: 1 practice trial(s) of condition 'word' in list 2 keep their answer 'f', "
        "where the response mapping gives 'j'.",
        "lexsync: 1 practice trial(s) of condition 'pseudoword' in list 2 keep their answer "
        "'j', where the response mapping gives 'f'."]
    # Each version's instructions name its own keys.
    versions = presentation_versions(_blocks_stim(lists=(1, 2)))
    assert _instruction_texts(design, versions) == [LEXDEC_TEXT % ("F", "J"),
                                                    LEXDEC_TEXT % ("J", "F")]
    # A declared mapping rotates the same way.
    declared = dict(design, response_mapping={"word": "j", "pseudoword": "f"})
    stim, _ = _assign_answers(_blocks_stim(lists=(1, 2)), declared)
    assert _main_answers(stim) == {(1, "word"): {"j"}, (1, "pseudoword"): {"f"},
                                   (2, "word"): {"f"}, (2, "pseudoword"): {"j"}}


def test_rotate_mapping_by_list_takes_true_or_false(schema):
    design = dict(LEXDEC, events=BLOCKS_EVENTS)
    for bad in ("yes", 1, "true", [True]):
        with pytest.raises(ValueError, match=re.escape(
                "lexsync: rotate_mapping_by_list must be true or false.")):
            validate_design(dict(design, rotate_mapping_by_list=bad), schema)
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: rotate_mapping_by_list rotates a response mapping, and the design has "
            "none; give `response_mapping`.")):
        validate_design({"name": "t", "language": "english", "rotate_mapping_by_list": True},
                        schema)
    assert validate_design(dict(design, rotate_mapping_by_list=False), schema) == []


def test_the_instructions_reach_all_three_targets(schema, tmp_path):
    text = "Lies jedes Wort, é & \"<b>\".\nThen press f or j."
    design = dict(LEXDEC, events=BLOCKS_EVENTS, instructions=text + "\n")
    out = export_experiments(_lexdec_stim(), design, schema, str(tmp_path))
    py = open(out["psychopy"], encoding="utf-8").read()
    match = re.search(r'INSTRUCTIONS = json\.loads\(r"""(.*)"""\)', py)
    # Carried as JSON data, one text per version, the closing line break trimmed.
    assert json.loads(match.group(1)) == [text]
    html = open(out["jspsych"], encoding="utf-8").read()
    page = json.loads(re.search(r"const INSTRUCTIONS = (.*?);\n", html, re.S).group(1))
    assert page == [text]
    assert "<b>" not in html.split("const INSTRUCTIONS = ", 1)[1].split(";\n", 1)[0]
    lines = open(out["opensesame"], encoding="utf-8").read().splitlines()
    at = lines.index("define inline_script lexsync_instructions")
    assert lines[at:at + 12] == [
        "define inline_script lexsync_instructions",
        '\tset description "Show the instructions and wait for the space bar"',
        '\tset _prepare ""',
        "\t___run__",
        "\tc = Canvas()",
        "\tc.text(u'Lies jedes Wort, é &amp; \"&lt;b&gt;\".<br />Then press f or j."
        "<br /><br />Press the space bar to begin.')",
        "\tc.show()",
        "\t_key, _t = Keyboard(keylist=[u'space', u'escape'], timeout=None).get_key()",
        "\tif _key == u'escape':",
        "\t    raise RuntimeError(u'lexsync: stopped at the instructions.')",
        "\t__end__",
        ""]
    runs = [line for line in lines if line.startswith("\trun lexsync_")]
    assert runs[-5:] == ["\trun lexsync_trigger_setup always",
                         "\trun lexsync_instructions always",
                         "\trun lexsync_session_start always", "\trun lexsync_loop always",
                         "\trun lexsync_session_end always"]


def test_lexsync_writes_instructions_for_the_tasks_it_knows():
    one = [{"version": 1, "replicate": 1, "list": 1, "n_trials": 4}]
    assert _instruction_texts(LEXDEC, one) == [LEXDEC_TEXT % ("the left arrow key",
                                                              "the right arrow key")]
    assert _instruction_texts(dict(LEXDEC, events=BLOCKS_EVENTS), one) == [
        LEXDEC_TEXT % ("F", "J")]
    assert _instruction_texts({"name": "c", "language": "english",
                               "paradigm": "categorisation"}, one) == [
        "You will see a category and then a word. Press F for yes if the word belongs to "
        "the category and J for no if it does not. Respond as quickly and accurately as you "
        "can."]
    assert _instruction_texts({"name": "s", "language": "english",
                               "paradigm": "self_paced_reading"}, one) == [
        "You will read each sentence one part at a time. Press the space bar to see the "
        "next part. Answer each question by pressing F for yes and J for no."]
    for paradigm in ("factorial", "priming"):
        assert _instruction_texts({"name": "f", "language": "english",
                                   "paradigm": paradigm}, one) == [
            "When a response is needed, press the left arrow key or the right arrow key. "
            "Respond as quickly and accurately as you can."]
    passive = {"name": "p", "language": "english", "events": BLOCKS_EVENTS[:2]}
    assert _instruction_texts(passive, one) == [
        "You will see items presented one at a time on the screen."]
    # A design's own text wins, whatever the paradigm.
    assert _instruction_texts(dict(LEXDEC, instructions="Go."), one) == ["Go."]
    assert [_key_label(k) for k in ("f", "space", "left", "return", "1", "lshift")] == [
        "F", "the space bar", "the left arrow key", "the Enter key", "1", "the lshift key"]


def test_a_design_in_another_language_without_instructions_is_warned(tmp_path, monkeypatch):
    spanish = {"name": "e", "language": "spanish", "paradigm": "lexical_decision"}
    assert _instruction_notes(spanish) == [LANGUAGE_NOTE % "spanish"]
    assert _instruction_notes(dict(spanish, instructions="Pulse la tecla.")) == []
    for english in ("english", "English", "en-GB"):
        assert _instruction_notes(dict(spanish, language=english)) == []
    # The run log says so, before anything is selected.
    monkeypatch.chdir(tmp_path)
    (tmp_path / "items.csv").write_text("item,condition,word\n1,alta,casa\n1,baja,cosa\n"
                                        "2,alta,mesa\n2,baja,masa\n", encoding="utf-8")
    (tmp_path / "design.yaml").write_text(yaml.safe_dump({
        "name": "es_demo", "language": "spanish", "items": {"source": "table",
                                                            "path": "items.csv"},
        "counterbalance": {"lists": 1}}), encoding="utf-8")
    schema_path = os.path.join(os.path.dirname(lexsync.__file__), "data", "schema.yaml")
    res = run_pipeline("design.yaml", schema_path, str(tmp_path / "out"), verbose=False)
    log = open(res["log"], encoding="utf-8").read()
    assert LANGUAGE_NOTE % "spanish" in log
    assert TASK_NOTE % "factorial" in log


def test_a_factorial_design_without_instructions_is_warned():
    assert _instruction_notes({"name": "f", "language": "english"}) == [TASK_NOTE % "factorial"]
    assert _instruction_notes({"name": "p", "language": "english", "paradigm": "priming"}) == [
        TASK_NOTE % "priming"]
    # A task lexsync knows, a design with no response and a design's own text are not.
    for design in (LEXDEC, {"name": "c", "language": "english", "paradigm": "categorisation"},
                   {"name": "s", "language": "english", "paradigm": "self_paced_reading"},
                   {"name": "p", "language": "english", "events": BLOCKS_EVENTS[:2]},
                   {"name": "f", "language": "english", "instructions": "Press f."}):
        assert _instruction_notes(design) == []
    # A mapping rotated across lists is noted when the design's own text cannot follow it.
    rotated = dict(LEXDEC, events=BLOCKS_EVENTS, rotate_mapping_by_list=True)
    assert _instruction_notes(rotated) == []
    assert _instruction_notes(dict(rotated, instructions="Press the keys.")) == [
        "lexsync: the response keys rotate across lists, but the design's `instructions` "
        "are the same in every list, so they should not name the keys."]


def test_instructions_must_be_text_without_control_characters(schema):
    for bad in (42, ["Press f."], {"en": "Press f."}):
        with pytest.raises(ValueError, match=re.escape(
                "lexsync: the design's `instructions` must be text.")):
            validate_design(dict(LEXDEC, instructions=bad), schema)
    for text, code in (("Press\tf.", "0009"), ("Press\rf.", "000D"), ("Press\x7ff.", "007F"),
                       ("Press\x85f.", "0085"), ("Press f.", "2028")):
        with pytest.raises(ValueError, match=re.escape(
                "lexsync: the design's `instructions` contain the control character U+%s; "
                "only line breaks are allowed." % code)):
            validate_design(dict(LEXDEC, instructions=text), schema)
    for empty in ("", " \n "):
        with pytest.raises(ValueError, match=re.escape(
                "lexsync: the design's `instructions` are empty; write the text or leave the "
                "key out.")):
            validate_design(dict(LEXDEC, instructions=empty), schema)
    assert validate_design(dict(LEXDEC, instructions="Press f.\n\nPress j."), schema) == []


def test_the_methods_paragraph_states_the_response_mapping():
    rec = _response_mapping_record(LEXDEC)
    assert rec == {"conditions": {"word": "left", "pseudoword": "right"},
                   "keys": ["left", "right"], "rotate_by_list": False, "source": "default"}
    ds = {"presentation": {"response_mapping": rec}, "counterbalancing": {"lists": 1}}
    assert _mapping_note(ds) == (" Participants pressed the left arrow key for words and the "
                                 "right arrow key for pseudowords.")
    # This engine writes the record's JSON with sorted keys, and the record read back
    # renders the same text.
    read_back = dict(rec, conditions={"pseudoword": "right", "word": "left"})
    assert _mapping_note(dict(ds, presentation={"response_mapping": read_back})) == (
        _mapping_note(ds))
    rotated = _response_mapping_record(dict(LEXDEC, events=BLOCKS_EVENTS,
                                            rotate_mapping_by_list=True))
    assert rotated["rotate_by_list"] is True
    assert _mapping_note({"presentation": {"response_mapping": rotated},
                          "counterbalancing": {"lists": 2}}) == (
        " Participants pressed F for words and J for pseudowords in odd-numbered lists and "
        "the reverse in even-numbered lists.")
    # One list has nothing to rotate.
    assert _mapping_note({"presentation": {"response_mapping": rotated},
                          "counterbalancing": {"lists": 1}}) == (
        " Participants pressed F for words and J for pseudowords.")
    declared = _response_mapping_record({
        "name": "p", "language": "english", "paradigm": "priming",
        "response_mapping": {"related": "left", "unrelated": "left"}})
    assert declared["source"] == "design"
    assert _mapping_note({"presentation": {"response_mapping": declared},
                          "counterbalancing": {"lists": 2}}) == (
        " Participants pressed the left arrow key for related and unrelated trials.")
    # Without a mapping there is nothing to record or say.
    assert _response_mapping_record({"name": "f", "language": "english"}) is None
    assert _mapping_note({"presentation": {}}) == ""


# ---- The shipped demonstrations --------------------------------------------------------

def test_the_shipped_lexical_decisions_carry_an_answer_on_every_trial():
    folder = repo_path("output", "experiments")
    loop = _read(folder / "en_lexdec_english_psychopy.csv")
    assert len(loop) == 120
    assert all(loop["answer"] == loop["condition"].map({"word": "left", "pseudoword": "right"}))
    practice = _read(repo_path("items", "practice_en_lexdec.csv"))
    keys = dict(zip(practice["condition"], practice["answer"], strict=True))
    assert keys == {"word": "f", "pseudoword": "j"}
    blocks = _read(folder / "en_lexdec_blocks_english_psychopy.csv")
    main = blocks[blocks["block"] == "main"]
    assert len(main) == 40
    assert all(blocks["answer"] == blocks["condition"].map(keys))
    # The datasheet and its Methods text state the mapping.
    with open(repo_path("output", "reports", "en_lexdec_english_datasheet_py.json"),
              encoding="utf-8") as handle:
        ds = json.load(handle)
    assert ds["presentation"]["response_mapping"]["conditions"] == {"word": "left",
                                                                    "pseudoword": "right"}
    md = repo_path("output", "reports", "en_lexdec_english_datasheet_py.md").read_text(
        encoding="utf-8")
    sentence = ("Participants pressed the left arrow key for words and the right arrow key "
                "for pseudowords.")
    assert sentence in md
    # The record read back from its JSON, and the R engine's, render the same sentence.
    assert sentence in methods_paragraph(ds)
    with open(repo_path("output", "reports", "en_lexdec_english_datasheet_R.json"),
              encoding="utf-8") as handle:
        assert sentence in methods_paragraph(json.load(handle))


def test_no_practice_pseudoword_is_a_known_form():
    known = set(repo_path("corpora", "derived", "en_known_forms.txt").read_text(
        encoding="utf-8").split("\n"))
    practice = _read(repo_path("items", "practice_en_lexdec.csv"))
    pseudowords = set(practice.loc[practice["condition"] == "pseudoword", "target"])
    assert len(pseudowords) == 4
    assert not pseudowords & known, sorted(pseudowords & known)


def test_the_categorisation_experiment_presents_both_answers():
    design = read_config(str(repo_path("config", "design_en_categorisation.yaml")))
    assert design["fillers"] == {"path": "items/categorisation_foils_en.csv"}
    foils = _read(repo_path("items", "categorisation_foils_en.csv"))
    members = _read(repo_path("items", "categorisation_en.csv"))
    assert list(foils.columns) == list(members.columns)
    assert len(foils) == 16 and set(foils["answer"]) == {"j"}
    assert foils["condition"].value_counts().to_dict() == {"narrow": 8, "broad": 8}
    # Judged against the members' own cues, and no foil is a member target.
    assert set(foils["category"]) <= set(members["category"])
    assert not set(foils["target"]) & set(members["target"])
    loop = _read(repo_path("output", "experiments", "en_categorisation_english_psychopy.csv"))
    for lst in sorted(set(loop["list"])):
        rows = loop[loop["list"] == lst]
        assert rows["answer"].value_counts().to_dict() == {"f": 16, "j": 16}, lst
        # Neither cue type predicts the answer.
        for cue in ("narrow", "broad"):
            assert set(rows.loc[rows["condition"] == cue, "answer"]) == {"f", "j"}, (lst, cue)
