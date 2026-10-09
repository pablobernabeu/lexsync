import json
import os
import re

import pandas as pd
import pytest

from lexsync.counterbalancing import counterbalance
from lexsync.io_utils import _round_dp
from lexsync.paradigms import resolve_events
from lexsync.scripting import (
    _design_condition_names,
    _json_r,
    _language_tag,
    assign_triggers,
    export_experiments,
    export_jspsych,
    export_opensesame,
    export_psychopy,
    loop_table,
    presentation_versions,
    render_events,
)


def _stim():
    s = pd.DataFrame({
        "word": ["cat", "dog", "car", "cap"], "condition": ["a", "a", "b", "b"],
        "set": [1, 2, 1, 2], "trial": [1, 2, 3, 4], "length": 3, "frequency": 5,
        "n_density": 2, "old20": 1.5,
    })
    return assign_triggers(s)


def test_triggers_in_range():
    s = _stim()
    assert s["item_trigger"].between(40, 239).all()
    assert set(s["condition_trigger"]) == {101, 102}


def _codes(s):
    return dict(zip(s["condition"], s["condition_trigger"], strict=True))


def test_condition_codes_follow_the_given_order_not_the_row_order():
    # After counterbalance() shuffles the trials, first appearance depends on the
    # seed, so it cannot be what fixes a condition's code. Pinned identically in
    # test-scripting.R.
    stim = pd.DataFrame({"condition": ["low", "high", "low", "high"], "set": [1, 1, 2, 2]})
    # The default keeps the 0.1.0 behaviour: order of first appearance.
    assert _codes(assign_triggers(stim)) == {"low": 101, "high": 102}
    assert _codes(assign_triggers(stim, conditions=["high", "low"])) == {"high": 101, "low": 102}
    assert _codes(assign_triggers(stim.iloc[::-1], conditions=["high", "low"])) == {
        "high": 101, "low": 102}
    # A listed condition absent from the rows keeps its code; an unlisted one takes
    # the next free code in code-point order of its label.
    sub = assign_triggers(stim[stim["condition"] == "low"], conditions=["high", "low"])
    assert set(sub["condition_trigger"]) == {102}
    extra = pd.concat([stim, pd.DataFrame({"condition": ["zeta", "Mid"], "set": [3, 3]})],
                      ignore_index=True)
    assert _codes(assign_triggers(extra.iloc[::-1], conditions="high")) == {
        "high": 101, "Mid": 102, "low": 103, "zeta": 104}


def test_export_experiments_numbers_conditions_in_the_design_order(schema, tmp_path):
    stim = pd.DataFrame({"word": ["cat", "dog", "car", "cap"],
                         "condition": ["a", "b", "a", "b"], "set": [1, 1, 2, 2],
                         "trial": [1, 2, 3, 4]})
    design = {"name": "t", "language": "english", "timing": {},
              "conditions": [{"name": "b"}, {"name": "a"}]}
    assert _design_condition_names(design) == ["b", "a"]
    assert _design_condition_names({"name": "t"}) is None
    export_experiments(stim, design, schema, str(tmp_path))
    loop = pd.read_csv(tmp_path / "t_english_psychopy.csv")
    assert _codes(loop) == {"b": 101, "a": 102}
    # An explicit order overrides the design's.
    export_experiments(stim, design, schema, str(tmp_path), conditions=["a", "b"])
    loop = pd.read_csv(tmp_path / "t_english_psychopy.csv")
    assert _codes(loop) == {"a": 101, "b": 102}


def test_more_than_200_item_sets_discloses_the_trigger_wrap(capsys):
    s = pd.DataFrame({"condition": ["a"] * 201, "set": list(range(1, 202))})
    out = assign_triggers(s)
    assert ("lexsync: 201 item sets exceed the 200-code trigger range; "
            "item codes wrap and repeat.") in capsys.readouterr().out
    assert out["item_trigger"].between(40, 239).all()
    # 201 sets into 200 codes: exactly one code is reused, and it is the first.
    assert int(out["item_trigger"].duplicated().sum()) == 1
    assert out.loc[out["item_trigger"].duplicated(), "item_trigger"].tolist() == [40]


def test_exactly_200_item_sets_stays_silent(capsys):
    out = assign_triggers(pd.DataFrame({"condition": ["a"] * 200,
                                        "set": list(range(1, 201))}))
    assert capsys.readouterr().out == ""
    assert int(out["item_trigger"].duplicated().sum()) == 0


def test_timeouts_round_through_the_shared_rule():
    # An integer timeout_ms divides to at most three decimals, so rounding is the
    # identity and no committed experiment byte moves.
    r = render_events([{"type": "response", "timeout_ms": 1500}], {}, 60)
    assert r[0]["timeout"] == 1.5
    # A fractional timeout goes through _round_dp, the rounder both engines share;
    # 7812.5 ms lands on a 3-dp halfway case where the engines' own rounders differ.
    r = render_events([{"type": "response", "timeout_ms": 1500.0005}], {}, 60)
    assert r[0]["timeout"] == _round_dp(1500.0005 / 1000.0, 3)
    r = render_events([{"type": "question", "timeout_ms": 7812.5}], {}, 60)
    assert r[0]["timeout"] == _round_dp(7812.5 / 1000.0, 3)
    assert r[0]["timeout"] != round(7812.5 / 1000.0, 3)


def test_psychopy_export_is_frame_locked(schema, tmp_path):
    design = {"name": "t", "language": "english", "timing": {}}
    path = export_psychopy(_stim(), design, schema, str(tmp_path))
    text = open(path, encoding="utf-8").read()
    assert "win.callOnFlip(port.setData" in text
    assert "{{" not in text  # all placeholders substituted


def test_inter_trigger_s_goes_through_17g_like_its_neighbours(schema, tmp_path):
    # str(16.65 / 1000) gives "0.016649999999999998" while R's as.character()
    # gives "0.01665", so the substitution is pinned through %.17g in both
    # engines. test-scripting.R asserts these same generated lines.
    design = {"name": "t", "language": "english", "timing": {}}
    fractional = dict(schema, triggers=dict(schema.get("triggers") or {},
                                            inter_trigger_ms=16.65))
    text = open(export_psychopy(_stim(), design, fractional, str(tmp_path)),
                encoding="utf-8").read()
    assert "INTER_TRIGGER_S = 0.016649999999999998\n" in text
    # The shipped default still renders as "0.01", so no committed experiment
    # byte moves.
    default = dict(schema, triggers={k: v for k, v in (schema.get("triggers") or {}).items()
                                     if k != "inter_trigger_ms"})
    text = open(export_psychopy(_stim(), design, default, str(tmp_path)),
                encoding="utf-8").read()
    assert "INTER_TRIGGER_S = 0.01\n" in text


def test_opensesame_export_is_consistent(schema, tmp_path):
    design = {"name": "t", "language": "english"}
    path = export_opensesame(_stim(), design, schema, str(tmp_path))
    lines = open(path, encoding="utf-8").read().splitlines()
    assert any("set start lexsync_experiment" in line for line in lines)
    assert any("dlportio" in line for line in lines)       # parallel backend
    assert any("serial.Serial" in line for line in lines)  # serial backend


def test_opensesame_loop_follows_the_computed_trial_order(schema, tmp_path):
    # The loop table is sorted on the seeded `trial` column, and all three targets
    # must present that order; OpenSesame's default (`order random`) would reshuffle.
    design = {"name": "t", "language": "english"}
    lines = open(export_opensesame(_stim(), design, schema, str(tmp_path)),
                 encoding="utf-8").read().splitlines()
    assert "\tset order sequential" in lines
    assert "\tset order random" not in lines


_FIX = {"type": "fixation", "content": "+", "duration_ms": 500}
_TEXT = {"type": "text", "content": "{target}", "duration_ms": 800, "trigger": "condition"}
_BLANK = {"type": "blank", "duration_ms": 200}
_RESP = {"type": "response", "keys": ["f", "j"], "timeout_ms": 2000}


def test_a_response_after_a_text_event_is_collected_from_its_onset():
    # The window used to open only when the target had gone. After a text event a
    # response is now collected from the text's onset, as one rendered event: the text
    # stays up for its 800 ms at most, and the window runs 2,800 ms, the total it had.
    # test-scripting.R pins the same rules and messages.
    assert render_events([_FIX, _TEXT, _RESP], {}, 60) == [
        {"type": "fixation", "text": "+", "ms": 500},
        {"type": "text", "field": "target", "ms": 800, "trigger": "@condition_trigger",
         "respond": {"keys": ["f", "j"], "timeout": 2.0}}]
    assert [r["type"] for r in render_events(resolve_events({"paradigm": "factorial"}),
                                             {}, 60)] == ["fixation", "text", "blank"]
    # After anything else, and with from: offset, the window opens after the stimulus,
    # as it did, for designs that delay the response.
    for events in ([_TEXT, _BLANK, _RESP], [_TEXT, dict(_RESP, **{"from": "offset"})],
                   [_TEXT, _BLANK, dict(_RESP, **{"from": "offset"})]):
        rendered = render_events(events, {}, 60)
        assert rendered[-1] == {"type": "response", "keys": ["f", "j"], "timeout": 2.0}
        assert "respond" not in rendered[0]
    # from: onset needs a text event before the response.
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: event 3 collects its response from the onset of the preceding "
            "stimulus, but event 2 is a blank; use from: offset.")):
        render_events([_TEXT, _BLANK, dict(_RESP, **{"from": "onset"})], {}, 60)
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: event 1 collects its response from the onset of the preceding "
            "stimulus, but no event precedes it; use from: offset.")):
        render_events([dict(_RESP, **{"from": "onset"})], {}, 60)
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: event 2 gives `from: start`, but a response event takes "
            "from: onset or from: offset.")):
        render_events([_TEXT, dict(_RESP, **{"from": "start"})], {}, 60)
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: event 2 gives `from: true`, but a response event takes "
            "from: onset or from: offset.")):
        render_events([_TEXT, dict(_RESP, **{"from": True})], {}, 60)
    # The merged event runs where the text runs, so the two must name the same blocks.
    practice = dict(_TEXT, blocks=["practice"])
    assert render_events([practice, dict(_RESP, blocks="practice")], {}, 60)[0] == dict(
        render_events([practice], {}, 60)[0], respond={"keys": ["f", "j"], "timeout": 2.0})
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: event 2 collects its response from the onset of event 1, so the two "
            "must run in the same blocks; give them the same `blocks`, or use from: offset.")):
        render_events([practice, _RESP], {}, 60)


def test_a_single_response_key_is_written_as_a_list(schema, tmp_path):
    # One key is still a list of keys in every generated experiment, as the runners
    # read it. test-scripting.R holds the R engine to the same EVENTS.
    events = [_TEXT, dict(_RESP, keys="space"), _BLANK, dict(_RESP, keys=["space"]),
              {"type": "question", "content": "{target}", "keys": "f"}]
    assert _json_r(render_events(events, {}, 60)) == (
        '[{"type":"text","field":"target","ms":800,"trigger":"@condition_trigger",'
        '"respond":{"keys":["space"],"timeout":2}},{"type":"blank","ms":200},'
        '{"type":"response","keys":["space"],"timeout":2},'
        '{"type":"question","field":"target","keys":["f"],"timeout":5}]')


def test_a_delayed_response_still_opens_after_the_stimulus(schema, tmp_path):
    # from: offset keeps the window that opens when the stimulus has gone. PsychoPy runs
    # it as its own event, and OpenSesame blanks the screen, collects the key with a
    # keyboard_response and then scores it.
    design = {"name": "t", "language": "english", "timing": {}, "events": [
        {"type": "fixation", "content": "+", "duration_frames": 30},
        {"type": "text", "content": "{word}", "duration_frames": 48, "trigger": "condition"},
        {"type": "response", "keys": ["left", "right"], "timeout_ms": 2000, "from": "offset"},
        {"type": "blank", "duration_frames": 15}]}
    py = open(export_psychopy(_stim(), design, schema, str(tmp_path)), encoding="utf-8").read()
    events = json.loads(re.search(r'EVENTS = json\.loads\(r"""(.*)"""\)', py).group(1))
    assert [e["type"] for e in events] == ["fixation", "text", "response", "blank"]
    lines = open(export_opensesame(_stim(), design, schema, str(tmp_path)),
                 encoding="utf-8").read().splitlines()
    assert "define inline_script lexsync_e2_blank" in lines
    assert "define keyboard_response lexsync_e2" in lines
    assert "define inline_script lexsync_e2_score" in lines
    runs = [l for l in lines if l.startswith("\trun lexsync_e")]
    assert runs == ["\trun lexsync_e0 always", "\trun lexsync_e1 always",
                    "\trun lexsync_e2_blank always", "\trun lexsync_e2 always",
                    "\trun lexsync_e2_score always", "\trun lexsync_e3 always"]


def test_jspsych_lang_attribute_is_a_valid_bcp47_tag(schema, tmp_path):
    for language, tag in (("english", "en"), ("spanish", "es"), ("chinese", "zh")):
        design = {"name": "t", "language": language, "timing": {}}
        html = open(export_jspsych(_stim(), design, schema, str(tmp_path), base=language),
                    encoding="utf-8").read()
        assert f'<html lang="{tag}">' in html


def test_language_tag_maps_labels_and_falls_back_to_undetermined():
    assert _language_tag({"language": "english"}) == "en"
    assert _language_tag({"language": "Chinese (Mandarin)"}) == "zh"
    assert _language_tag({"language": "en-GB"}) == "en-GB"          # already a tag
    assert _language_tag({"language": "english", "language_tag": "en-US"}) == "en-US"
    assert _language_tag({"language": "klingon"}) == "und"
    assert _language_tag({"language": ""}) == "und"


def _cjk_stim():
    # Two-character Chinese words, as in the logographic demonstration.
    s = pd.DataFrame({
        "word": ["自然", "回来", "三亚", "东盟"], "condition": ["a", "a", "b", "b"],
        "set": [1, 2, 1, 2], "trial": [1, 2, 3, 4], "length": 2, "frequency": 5,
        "n_density": 80, "old20": 1.0,
    })
    return assign_triggers(s)


def test_font_is_configurable_for_logographic_scripts(schema, tmp_path):
    # A per-design font overrides the Latin default in both presentation targets,
    # so non-alphabetic scripts (here Chinese) render with a glyph-complete font.
    design = {"name": "zh", "language": "chinese", "font": "SimHei", "timing": {}}
    py = open(export_psychopy(_cjk_stim(), design, schema, str(tmp_path)), encoding="utf-8").read()
    assert 'WORD_FONT = "SimHei"' in py
    assert "{{" not in py
    os_lines = open(export_opensesame(_cjk_stim(), design, schema, str(tmp_path)),
                    encoding="utf-8").read().splitlines()
    assert any(line == "set font_family SimHei" for line in os_lines)
    # The Chinese words survive the round-trip into the loop table.
    csv = open(export_psychopy(_cjk_stim(), design, schema, str(tmp_path)).replace(".py", ".csv"),
               encoding="utf-8").read()
    assert "自然" in csv and "东盟" in csv


def test_default_font_is_latin(schema, tmp_path):
    design = {"name": "t", "language": "english", "timing": {}}
    py = open(export_psychopy(_stim(), design, schema, str(tmp_path)), encoding="utf-8").read()
    assert 'WORD_FONT = "Courier New"' in py


# ---- One counterbalancing version per participant ------------------------------------
#
# A presentation version is one (replicate, list) pair of the presented trials, numbered
# from 1 in that order. test-scripting.R pins the same files, names and texts.

def _two_list_stimuli(schema):
    """Two targets, each related in one list and unrelated in the other."""
    stim = pd.DataFrame({"prime": ["hot", "sky", "sun", "big"],
                         "target": ["cold", "cold", "moon", "moon"],
                         "condition": ["related", "unrelated"] * 2, "set": [1, 1, 2, 2]})
    design = {"name": "t", "language": "english", "paradigm": "priming",
              "counterbalance": {"lists": 2}}
    return assign_triggers(counterbalance(stim, design, schema)), design


def _three_replicates(schema):
    """Three disjoint item samples, each dealt into one list, as en_resample is."""
    stim = pd.DataFrame({"word": ["w%02d" % i for i in range(12)],
                         "condition": ["hi", "lo"] * 6, "set": [1, 1, 2, 2] * 3,
                         "replicate": [1] * 4 + [2] * 4 + [3] * 4})
    design = {"name": "r", "language": "english", "counterbalance": {"lists": 1}}
    return assign_triggers(counterbalance(stim, design, schema)), design


def test_one_opensesame_experiment_per_version(schema, tmp_path):
    stim, design = _two_list_stimuli(schema)
    first = export_opensesame(stim, design, schema, str(tmp_path))
    assert os.path.basename(first) == "t_english_list1.osexp"
    assert sorted(os.listdir(tmp_path)) == [
        "t_english_list1.osexp", "t_english_list1_opensesame.csv",
        "t_english_list1_opensesame_text.csv", "t_english_list2.osexp",
        "t_english_list2_opensesame.csv", "t_english_list2_opensesame_text.csv"]
    for k in (1, 2):
        numbers = pd.read_csv(tmp_path / f"t_english_list{k}_opensesame.csv")
        assert set(numbers["lexsync_list"]) == {k}
        assert list(numbers["lexsync_row"]) == [1, 2]
        text = pd.read_csv(tmp_path / f"t_english_list{k}_opensesame_text.csv")
        assert sorted(text["target"]) == ["cold", "moon"]
        lines = (tmp_path / f"t_english_list{k}.osexp").read_text(encoding="utf-8").splitlines()
        assert f'\tset source_file "t_english_list{k}_opensesame.csv"' in lines
        assert ("\twith open(pool[u't_english_list%d_opensesame_text.csv'], "
                "encoding=u'utf-8-sig', newline=u'') as _f:" % k) in lines
        # Each experiment checks the subject number against its own version before
        # the loop, and no run line carries a condition.
        assert "define inline_script lexsync_version_check" in lines
        assert f"\t_version = {k}" in lines and "\t_versions = 2" in lines
        runs = [line for line in lines if line.startswith("\trun ")]
        assert runs[-3:] == ["\trun lexsync_trigger_setup always",
                             "\trun lexsync_version_check always",
                             "\trun lexsync_loop always"]
        assert not any('"' in line for line in runs)


def test_single_version_designs_keep_their_file_names(schema, tmp_path):
    design = {"name": "t", "language": "english", "timing": {}}
    out = export_experiments(_stim(), design, schema, str(tmp_path))
    # The three keys callers read are unchanged, and `files` lists every file written.
    assert list(out) == ["psychopy", "opensesame", "jspsych", "files"]
    assert [os.path.basename(p) for p in out["files"]] == [
        "t_english_psychopy.py", "t_english.osexp", "t_english.html",
        "t_english_psychopy.csv", "t_english_opensesame.csv",
        "t_english_opensesame_text.csv"]
    assert out["files"][:3] == [out["psychopy"], out["opensesame"], out["jspsych"]]
    assert sorted(os.listdir(tmp_path)) == sorted(os.path.basename(p) for p in out["files"])
    osexp = open(out["opensesame"], encoding="utf-8").read()
    assert "lexsync_version_check" not in osexp


def test_export_experiments_lists_every_version_file(schema, tmp_path):
    stim, design = _two_list_stimuli(schema)
    out = export_experiments(stim, design, schema, str(tmp_path))
    assert [os.path.basename(p) for p in out["files"]] == [
        "t_english_psychopy.py", "t_english_list1.osexp", "t_english_list2.osexp",
        "t_english.html", "t_english_psychopy.csv",
        "t_english_list1_opensesame.csv", "t_english_list1_opensesame_text.csv",
        "t_english_list2_opensesame.csv", "t_english_list2_opensesame_text.csv"]
    assert out["opensesame"] == out["files"][1]
    assert sorted(os.listdir(tmp_path)) == sorted(os.path.basename(p) for p in out["files"])


def test_resampled_replicates_are_separate_versions(schema, tmp_path):
    stim, design = _three_replicates(schema)
    assert presentation_versions(stim) == [
        {"version": v, "replicate": v, "list": 1, "n_trials": 4} for v in (1, 2, 3)]
    # The loop table carries the replicate and keeps each replicate's trials together,
    # in trial order. Trials are numbered within a replicate, so sorting on the trial
    # alone interleaved the replicates.
    loop = loop_table(stim)
    assert list(loop.columns[:3]) == ["trial", "list", "replicate"]
    assert list(zip(loop["replicate"], loop["trial"], strict=True)) == [
        (r, t) for r in (1, 2, 3) for t in (1, 2, 3, 4)]
    out = export_experiments(stim, design, schema, str(tmp_path))
    assert [os.path.basename(p) for p in out["files"] if p.endswith(".osexp")] == [
        "r_english_rep1_list1.osexp", "r_english_rep2_list1.osexp",
        "r_english_rep3_list1.osexp"]
    numbers = pd.read_csv(tmp_path / "r_english_rep2_list1_opensesame.csv")
    assert set(numbers["replicate"]) == {2}


def test_the_psychopy_script_and_the_page_carry_the_versions(schema, tmp_path):
    stim, design = _two_list_stimuli(schema)
    versions = ('[{"version":1,"replicate":1,"list":1,"n_trials":2},'
                '{"version":2,"replicate":1,"list":2,"n_trials":2}]')
    py = open(export_psychopy(stim, design, schema, str(tmp_path)), encoding="utf-8").read()
    assert f'VERSIONS = json.loads(r"""{versions}""")' in py
    html = open(export_jspsych(stim, design, schema, str(tmp_path)), encoding="utf-8").read()
    assert f"const VERSIONS = {versions};" in html
    for text in (py, html):
        assert "{{" not in text


def test_a_presentation_version_is_numbered_by_whole_number_lists():
    # A table without `list` or `replicate` is one list of one replicate.
    assert presentation_versions(pd.DataFrame({"word": ["a", "b"]})) == [
        {"version": 1, "replicate": 1, "list": 1, "n_trials": 2}]
    # Lists are put in numeric order, so list 10 follows list 9.
    lists = pd.DataFrame({"list": [10, 9, 10]})
    assert [(v["list"], v["n_trials"]) for v in presentation_versions(lists)] == [(9, 1), (10, 2)]
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: the trials' `list` column holds 'A', but a presentation version is "
            "numbered by whole-number lists and replicates.")):
        presentation_versions(pd.DataFrame({"list": [1, "A"]}))
    with pytest.raises(ValueError, match=re.escape("column holds '1.5'")):
        presentation_versions(pd.DataFrame({"replicate": [1.5]}))
    # Both engines read a list by one rule: a number by its value, and text as a plain
    # decimal number. float() alone took "1_0" and other scripts' digits, R's
    # as.numeric() took "0x10", and R's as.character() rounded 1.0000000000000002 to 1.
    for odd in ("1_0", "0x10", "１", "1e1", 1.0000000000000002):
        with pytest.raises(ValueError, match="presentation version is numbered"):
            presentation_versions(pd.DataFrame({"list": [odd]}))
    with pytest.raises(ValueError, match=re.escape("holds '1.0000000000000002'")):
        presentation_versions(pd.DataFrame({"list": [1.0000000000000002]}))
    mixed = pd.DataFrame({"list": [" 2 ", "2.0", "10", "3"]})
    assert [(v["list"], v["n_trials"]) for v in presentation_versions(mixed)] == [
        (2, 2), (3, 1), (10, 1)]
