import pandas as pd
import pytest

from lexsync.io_utils import _round_dp
from lexsync.scripting import (
    _language_tag,
    _osexp_event_block,
    assign_triggers,
    export_jspsych,
    export_opensesame,
    export_psychopy,
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


def test_the_opensesame_timeout_matches_the_other_two_backends():
    """1.001 * 1000 is 1000.9999999999999, and int() truncated it, so a 1001 ms
    window reached OpenSesame as 1000 while PsychoPy used the seconds directly and
    jsPsych rounded. Mirrored in test-scripting.R."""
    r = render_events([{"type": "response", "timeout_ms": 1001},
                       {"type": "question", "content": "q", "timeout_ms": 1001}], {}, 60)
    assert [ev["timeout"] for ev in r] == [1.001, 1.001]
    resp, _ = _osexp_event_block("t", r[0])
    assert "\tset timeout 1001" in resp
    quest, _ = _osexp_event_block("q", r[1])
    assert any("timeout=1001)" in line for line in quest)


# An explicit `events:` list is the documented way to depart from a paradigm, so
# the message that refuses one has to say what a type may be. test-scripting.R pins
# the same three sentences.
_KNOWN_TYPES_SENTENCE = ("Known types: fixation, text, mask, blank, region_by_region, "
                         "response, question, feedback.")


def test_an_unknown_event_type_names_the_known_ones():
    with pytest.raises(ValueError) as excinfo:
        render_events([{"type": "fixaton", "content": "+", "duration_ms": 500}], {}, 60)
    assert str(excinfo.value) == ("lexsync: unknown event type 'fixaton'. "
                                  + _KNOWN_TYPES_SENTENCE)
    with pytest.raises(ValueError) as excinfo:
        _osexp_event_block("e1", {"type": "fixaton"})
    assert str(excinfo.value) == ("lexsync: unknown event type 'fixaton'. "
                                  + _KNOWN_TYPES_SENTENCE)


def test_an_event_with_no_type_is_refused_by_name():
    with pytest.raises(ValueError) as excinfo:
        render_events([{"content": "+", "duration_ms": 500}], {}, 60)
    assert str(excinfo.value) == "lexsync: unknown event type ''. " + _KNOWN_TYPES_SENTENCE


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


def test_all_targets_offset_the_stimulus_before_the_response_window(schema, tmp_path):
    # The stimulus offsets at its own duration, not at the participant's keypress:
    # PsychoPy flips an empty window and OpenSesame shows an empty canvas, both
    # before the response is collected, matching jsPsych's empty `response` stimulus.
    design = {"name": "t", "language": "english", "timing": {}}
    py = open(export_psychopy(_stim(), design, schema, str(tmp_path)), encoding="utf-8").read()
    assert "        win.flip()\n        keys = event.waitKeys(" in py

    lines = open(export_opensesame(_stim(), design, schema, str(tmp_path)),
                 encoding="utf-8").read().splitlines()
    assert "define inline_script lexsync_e2_blank" in lines
    assert "define keyboard_response lexsync_e2" in lines
    runs = [l for l in lines if l.startswith("\trun lexsync_e")]
    assert runs == ["\trun lexsync_e0 always", "\trun lexsync_e1 always",
                    "\trun lexsync_e2_blank always", "\trun lexsync_e2 always",
                    "\trun lexsync_e3 always"]


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


def test_the_osexp_list_gate_orders_labels_as_the_two_runners_do():
    """The gate sorted with str.isdigit(), which is true of characters int()
    refuses, so a superscript label raised a ValueError where the PsychoPy and
    jsPsych runners sort it as an ordinary label. The three read one experiment's
    lists, so they have to agree on the same input."""
    from lexsync.scripting import _list_sort_key

    assert sorted(["10", "9", "1"], key=_list_sort_key) == ["1", "9", "10"]
    # int() refuses it, so it sorts as a label rather than raising.
    assert _list_sort_key("\u00b2") == (1, 0, "\u00b2")
    assert sorted(["b", "2", "a", "10"], key=_list_sort_key) == ["2", "10", "a", "b"]
