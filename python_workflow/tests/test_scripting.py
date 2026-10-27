import json
import os
import re

import pandas as pd
import pytest

from lexsync.counterbalancing import counterbalance
from lexsync.design import validate_design
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


def test_onset_locked_false_is_accepted_and_noted(schema):
    # Every event's trigger is written on its onset flip. test-scripting.R asserts the same.
    design = {"name": "t", "language": "english",
              "events": [{"type": "fixation", "onset_locked": False}]}
    assert validate_design(design, schema) == [
        "lexsync: events[].onset_locked: false changes nothing, since every event's trigger "
        "is written on its onset flip."]
    design["events"][0]["onset_locked"] = True
    assert validate_design(design, schema) == []


def test_inter_trigger_ms_is_accepted_and_no_longer_used(schema, tmp_path):
    # The self-paced reading critical-region code was held for inter_trigger_ms, 10 ms,
    # where every other code is held for trigger_hold_ms, and nothing else read the key.
    # A schema that still sets it is accepted, and the run log says the key is not used.
    # test-scripting.R asserts the same.
    design = {"name": "t", "language": "english", "timing": {}}
    old = dict(schema, triggers=dict(schema.get("triggers") or {}, inter_trigger_ms=16.65))
    text = open(export_psychopy(_stim(), design, old, str(tmp_path)),
                encoding="utf-8").read()
    assert "INTER_TRIGGER" not in text
    assert validate_design(design, old) == [
        "lexsync: triggers.inter_trigger_ms is no longer used; the self-paced reading "
        "critical-region code is held for triggers.trigger_hold_ms, as every other code is."]
    # The shipped schema no longer sets it.
    assert "inter_trigger_ms" not in (schema.get("triggers") or {})
    assert validate_design(design, schema) == []


def test_opensesame_export_is_consistent(schema, tmp_path):
    design = {"name": "t", "language": "english"}
    path = export_opensesame(_stim(), design, schema, str(tmp_path))
    lines = open(path, encoding="utf-8").read().splitlines()
    assert any("set start lexsync_experiment" in line for line in lines)
    assert any("dlportio" in line for line in lines)       # parallel backend
    # The serial branch is written only for a schema that names a serial device.
    assert not any("import serial" in line or "serial.Serial" in line for line in lines)


# ---- Presentation and trigger settings ------------------------------------------------
#
# The PsychoPy script always opened a 1280 x 1024 window, and the OpenSesame experiment
# drew its text at 32 px where the other two targets used 48. The OpenSesame setup set
# its trigger backend to parallel on the line before the branch that would have opened a
# serial device, and that branch took the first serial port it found. Neither laboratory
# target said when its port could not be opened. The schema now sets all of this, and a
# value the experiments cannot use is refused before anything is written.
# test-scripting.R pins the same lines and messages.

def _with(schema, section, **settings):
    """The schema with `settings` added to its `section`."""
    return dict(schema, **{section: dict(schema.get(section) or {}, **settings)})


def _three_targets(schema, tmp_path):
    """The PsychoPy script's lines, the .osexp's lines and the page's text."""
    design = {"name": "t", "language": "english"}

    def read(path):
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    return (read(export_psychopy(_stim(), design, schema, str(tmp_path))).splitlines(),
            read(export_opensesame(_stim(), design, schema, str(tmp_path))).splitlines(),
            read(export_jspsych(_stim(), design, schema, str(tmp_path))))


def test_the_schema_sets_the_window_the_text_height_and_the_trigger_device(schema, tmp_path):
    py, osexp, html = _three_targets(schema, tmp_path)
    for line in ("FULLSCREEN = True", "TEXT_HEIGHT_PX = 48", 'TRIGGER_MODE = "auto"',
                 'TRIGGER_BACKEND = "parallel"', "TRIGGER_ADDRESS = 0x0378", 'SERIAL_PORT = ""',
                 "SERIAL_BAUDRATE = 115200",
                 'TRIGGER_DEVICE = "the parallel port at 0x0378"'):
        assert line in py, line
    assert "set font_size 48" in osexp
    assert ('.lexsync-stim { font-family: "Courier New", monospace; font-size: 48px; '
            'color: #fff; }') in html
    # jsPsych and its stylesheet are checked against their hashes.
    assert len(re.findall(r'integrity="sha384-[A-Za-z0-9+/]{64}"\s+crossorigin="anonymous"',
                          html)) == 3
    custom = _with(_with(schema, "presentation", fullscreen=False, text_height_px=36),
                   "triggers", mode="hardware", backend="serial",
                   serial_port="/dev/ttyUSB0", baudrate=9600)
    py, osexp, html = _three_targets(custom, tmp_path)
    for line in ("FULLSCREEN = False", "TEXT_HEIGHT_PX = 36", 'TRIGGER_MODE = "hardware"',
                 'TRIGGER_BACKEND = "serial"', 'SERIAL_PORT = "/dev/ttyUSB0"',
                 "SERIAL_BAUDRATE = 9600", 'TRIGGER_DEVICE = "the serial port /dev/ttyUSB0"'):
        assert line in py, line
    assert "set font_size 36" in osexp
    assert "font-size: 36px; color: #fff; }" in html


_HEIGHT = "lexsync: presentation.text_height_px must be a whole number of pixels from 8 to 400."
_BAUD = "lexsync: triggers.baudrate must be a whole number of bits per second, such as 115200."
_PORT_SHAPE = ("lexsync: triggers.serial_port must name a serial device such as COM3 or "
               "/dev/ttyUSB0, not '%s'. Only letters, digits and . _ - : / are allowed, "
               "since the name is written into the generated experiments.")


def test_presentation_and_trigger_settings_are_checked_before_anything_is_written():
    design = {"name": "t", "language": "english"}
    refusals = [
        ({"presentation": {"fullscreen": "yes"}},
         "lexsync: presentation.fullscreen must be true or false."),
        ({"presentation": {"text_height_px": 7}}, _HEIGHT),
        ({"presentation": {"text_height_px": 401}}, _HEIGHT),
        ({"presentation": {"text_height_px": 48.5}}, _HEIGHT),
        ({"presentation": {"text_height_px": "48"}}, _HEIGHT),
        ({"presentation": {"text_height_px": True}}, _HEIGHT),
        ({"triggers": {"mode": "on"}},
         "lexsync: triggers.mode must be auto, hardware or mock, not 'on'."),
        ({"triggers": {"mode": True}},
         "lexsync: triggers.mode must be auto, hardware or mock, not 'true'."),
        ({"triggers": {"backend": "usb"}},
         "lexsync: triggers.backend must be parallel or serial, not 'usb'."),
        ({"triggers": {"backend": "serial"}},
         "lexsync: triggers.backend is serial, so triggers.serial_port must name the serial "
         "device, such as COM3 or /dev/ttyUSB0."),
        ({"triggers": {"backend": "serial", "serial_port": 3}},
         "lexsync: triggers.serial_port must be text naming a serial device such as COM3 "
         "or /dev/ttyUSB0."),
        ({"triggers": {"backend": "serial", "serial_port": "COM3'; import os"}},
         _PORT_SHAPE % "COM3'; import os"),
        # Checked whatever the backend, since the script carries it either way.
        ({"triggers": {"serial_port": "COM3\n"}}, _PORT_SHAPE % "COM3\n"),
        ({"triggers": {"baudrate": 0}}, _BAUD),
        ({"triggers": {"baudrate": 9600.5}}, _BAUD),
        ({"triggers": {"baudrate": "fast"}}, _BAUD),
        ({"triggers": {"baudrate": True}}, _BAUD),
    ]
    for schema, message in refusals:
        with pytest.raises(ValueError) as err:
            validate_design(design, schema)
        assert str(err.value) == message, schema
    # A full set of valid settings passes, a whole number written as 36.0 included, and
    # none of the keys is noted as unknown.
    assert validate_design(design, {
        "presentation": {"fullscreen": False, "text_height_px": 36.0},
        "triggers": {"mode": "hardware", "backend": "serial", "baudrate": 115200,
                     "serial_port": "/dev/serial/by-path/pci-0000:00:14.0-usb-0:1:1.0-port0"},
    }) == []


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


def _events_from_yaml(tmp_path, keys):
    """The events of a design whose response keys are written `keys` in YAML, read as
    run_pipeline reads them, so the test covers the YAML reader as well."""
    from lexsync.io_utils import read_config
    path = tmp_path / "keys.yaml"
    path.write_text("events:\n"
                    "  - {type: text, content: '{target}', duration_ms: 800}\n"
                    "  - {type: response, keys: %s}\n" % keys, encoding="utf-8")
    return read_config(str(path))["events"]


def test_unquoted_y_and_n_are_response_keys_y_and_n(tmp_path):
    """The R engine's YAML reader took an unquoted y and n for TRUE and FALSE, so
    `keys: [y, n]` gave it experiments waiting for keys named TRUE and FALSE, which no
    participant can press. Pinned identically in test-scripting.R."""
    for keys, want in (("[y, n]", ["y", "n"]), ("[Y, N]", ["Y", "N"])):
        rendered = render_events(_events_from_yaml(tmp_path, keys), {}, 60)
        assert rendered[0]["respond"]["keys"] == want


def test_a_yaml_boolean_response_key_is_refused(tmp_path):
    """YAML 1.1 reads an unquoted yes, no, on, off, true or false as a boolean in both
    engines. The R engine rendered it as the key TRUE and this engine as True, two
    different experiments that no participant could answer. Pinned identically in
    test-scripting.R."""
    refusal = "lexsync: response key %s is a YAML boolean; quote it ('%s') or choose another key."
    for keys, shown in (("[yes, no]", ("TRUE", "yes")), ("[f, off]", ("FALSE", "no")),
                        ("on", ("TRUE", "yes"))):
        with pytest.raises(ValueError, match=re.escape(refusal % shown)):
            render_events(_events_from_yaml(tmp_path, keys), {}, 60)
    question = {"type": "question", "content": "{target}", "keys": [False, "j"]}
    with pytest.raises(ValueError, match=re.escape(refusal % ("FALSE", "no"))):
        render_events([question], {}, 60)


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
        # the loop, then shows its instructions, and no run line carries a condition.
        # The session markers come after the instructions, just before and after the
        # loop. The notice for missing trigger codes comes first, for the experimenter.
        assert "define inline_script lexsync_version_check" in lines
        assert f"\t_version = {k}" in lines and "\t_versions = 2" in lines
        runs = [line for line in lines if line.startswith("\trun ")]
        assert runs[-7:] == ["\trun lexsync_trigger_setup always",
                             "\trun lexsync_trigger_notice always",
                             "\trun lexsync_version_check always",
                             "\trun lexsync_instructions always",
                             "\trun lexsync_session_start always",
                             "\trun lexsync_loop always",
                             "\trun lexsync_session_end always"]
        assert not any('"' in line for line in runs)


def _two_list_three_orders(schema, lists=2, orders=3):
    """Eight item sets dealt into `lists` lists, each list in `orders` trial orders."""
    stim = pd.DataFrame({"word": ["w%02d" % i for i in range(1, 17)],
                         "condition": ["hi", "lo"] * 8,
                         "set": [s for s in range(1, 9) for _ in (0, 1)]})
    design = {"name": "o", "language": "english", "timing": {},
              "counterbalance": {"lists": lists, "orders": orders}}
    return assign_triggers(counterbalance(stim, design, schema)), design


def test_one_opensesame_experiment_per_version_and_order(schema, tmp_path):
    # OpenSesame's loop presents its table in file order, so each trial order of each
    # version is an experiment of its own, its tables sorted by that order. The loop
    # table numbers the trials as presented. test-scripting.R pins the same files.
    stim, design = _two_list_three_orders(schema)
    out = export_experiments(stim, design, schema, str(tmp_path))
    stems = ["o_english_list%d_order%d" % (k, j) for k in (1, 2) for j in (1, 2, 3)]
    assert [os.path.basename(p) for p in out["files"] if p.endswith(".osexp")] == [
        s + ".osexp" for s in stems]
    assert out["opensesame"] == out["files"][1]
    for k in (1, 2):
        for j in (1, 2, 3):
            stem = "o_english_list%d_order%d" % (k, j)
            numbers = pd.read_csv(tmp_path / f"{stem}_opensesame.csv")
            text = pd.read_csv(tmp_path / f"{stem}_opensesame_text.csv")
            want = stim[stim["list"] == k].sort_values("order_%d" % j)
            assert list(text["word"]) == list(want["word"]), stem
            assert list(numbers["lexsync_trial"]) == list(range(1, 9)), stem
            assert list(text["order_%d" % j]) == list(range(1, 9)), stem
            lines = (tmp_path / f"{stem}.osexp").read_text(encoding="utf-8").splitlines()
            assert f"set lexsync_order {j}" in lines
            assert f"\t_version = {k}" in lines and "\t_versions = 2" in lines
            assert f"\t_order = {j}" in lines and "\t_orders = 3" in lines
    # The loop table of the PsychoPy script and the page holds every order.
    loop = pd.read_csv(tmp_path / "o_english_psychopy.csv")
    assert [c for c in loop.columns if c.startswith("order_")] == [
        "order_1", "order_2", "order_3"]
    # The script and the page are told how many orders the trials carry.
    py = open(out["psychopy"], encoding="utf-8").read().splitlines()
    assert "ORDERS = 3" in py
    html = open(out["jspsych"], encoding="utf-8").read().splitlines()
    assert "  const ORDERS = 3;" in html


def test_one_version_in_several_orders_names_each_order(schema, tmp_path):
    stim, design = _two_list_three_orders(schema, lists=1, orders=2)
    out = export_experiments(stim, design, schema, str(tmp_path))
    assert [os.path.basename(p) for p in out["files"] if p.endswith(".osexp")] == [
        "o_english_order1.osexp", "o_english_order2.osexp"]
    osexp = (tmp_path / "o_english_order2.osexp").read_text(encoding="utf-8")
    assert "lexsync_version_check" in osexp


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


# ---- Trigger codes are checked when the experiment is generated -------------------
#
# A literal code was never range-checked: 300 reached the parallel port, which keeps
# only the low byte, and the serial port's to_bytes(1) raised during the session. A
# misspelt token such as `conditon` stopped this engine with int()'s own error, while
# the R engine wrote send_trigger(NA) into the OpenSesame experiment. test-scripting.R
# pins the same rules, codes and messages.

def _word(trigger):
    return {"type": "text", "content": "{word}", "duration_ms": 800, "trigger": trigger}


_REGION_ITEM = {"type": "region_by_region", "content": "{sentence}",
                "critical_region_trigger": "item"}


def _sets(n):
    """Two conditions crossed with sets 1 to n."""
    return pd.DataFrame({"condition": ["a", "b"] * n,
                         "set": [s for s in range(1, n + 1) for _ in (1, 2)]})


def _item_codes(stim):
    return dict(zip(stim["set"], stim["item_trigger"], strict=True))


def test_a_trigger_is_condition_item_or_a_code_from_1_to_255():
    def spec(trigger):
        return render_events([_FIX, _word(trigger)], {}, 60)[1]["trigger"]

    assert spec("condition") == "@condition_trigger"
    assert spec("item") == "@item_trigger"
    # A whole number, written as a number or as a string of digits.
    assert [spec(t) for t in (1, 255, "20", 20.0)] == [1, 255, 20, 20]
    for bad, shown in ((300, "300"), (0, "0"), (-5, "-5"), ("conditon", "conditon"),
                       (20.5, "20.5"), (True, "true"), ("20 ", "20 ")):
        with pytest.raises(ValueError, match=re.escape(
                "lexsync: event 2 has trigger '%s'; use 'condition', 'item' or a code from "
                "1 to 255." % shown)):
            render_events([_FIX, _word(bad)], {}, 60)
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: event 1 has critical_region_trigger '256'; use 'condition', 'item' or "
            "a code from 1 to 255.")):
        render_events([dict(_REGION_ITEM, critical_region_trigger=256)], {}, 60)


def test_a_literal_trigger_of_254_or_255_is_logged(schema, tmp_path, capsys):
    stim = _sets(2)
    assign_triggers(stim, events=[dict(_FIX, trigger=254), _word("condition")])
    assert capsys.readouterr().out == (
        "lexsync: event 1 sends code 254, which the PsychoPy and OpenSesame experiments also "
        "send when the session starts.\n")
    assign_triggers(stim, events=[_FIX, _word(255)])
    assert capsys.readouterr().out == (
        "lexsync: event 2 sends code 255, which the PsychoPy and OpenSesame experiments also "
        "send when the session ends.\n")
    # export_experiments hands the design's events to assign_triggers.
    design = {"name": "t", "language": "english",
              "events": [dict(_FIX, trigger=254), _word("condition")]}
    export_experiments(stim.assign(word="cat", trial=[1, 2, 3, 4]), design, schema,
                       str(tmp_path))
    assert "lexsync: event 1 sends code 254" in capsys.readouterr().out


def test_a_literal_trigger_that_shares_a_code_in_use_is_logged(capsys):
    # A code equal to a condition code the design sends.
    out = assign_triggers(_sets(2), events=[dict(_FIX, trigger=102), _word("condition")])
    assert capsys.readouterr().out == (
        "lexsync: event 1 sends code 102, which is also the condition code of 'b'.\n")
    assert set(_item_codes(out).values()) == {40, 41}
    # A code among the item codes the design sends: no item takes it, but a reader who
    # decoded item codes by their range would.
    out = assign_triggers(_sets(10), events=[dict(_FIX, trigger=45), _REGION_ITEM])
    assert capsys.readouterr().out == (
        "lexsync: event 1 sends code 45, which lies inside the range of the item codes "
        "(40 to 50); decode item codes through the loop table.\n")
    assert 45 not in _item_codes(out).values()
    # A design that sends neither kind of code hears nothing about them.
    assign_triggers(_sets(10), events=[dict(_FIX, trigger=45), _word(102)])
    assert capsys.readouterr().out == ""


def test_a_70_set_design_sending_both_code_kinds_has_no_overlap(capsys):
    out = assign_triggers(_sets(70), events=[_word("condition"), _REGION_ITEM])
    codes = _item_codes(out)
    assert set(codes.values()).isdisjoint({101, 102})
    assert len(set(codes.values())) == 70
    # Item codes follow the code-point order of the set labels, so set 10 is 41 and set 2
    # is 51. Sets 65 and 66, which took 101 and 102, take the next free codes.
    assert [codes[s] for s in (10, 2, 64, 65, 66)] == [41, 51, 100, 103, 104]
    assert capsys.readouterr().out == ""


def test_item_codes_are_allocated_as_before_unless_both_kinds_are_sent():
    for events in (None, [_word("condition")], [_REGION_ITEM], [dict(_FIX, trigger=20),
                                                                  _REGION_ITEM]):
        codes = _item_codes(assign_triggers(_sets(70), events=events))
        assert [codes[s] for s in (10, 2, 65, 66)] == [41, 51, 101, 102]


def test_item_codes_beyond_the_free_codes_are_refused_unless_overlap_is_allowed(capsys):
    events = [_word("condition"), _REGION_ITEM]
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: 199 item sets need 199 item codes, but only 198 of the codes from 40 "
            "to 239 are free of the condition codes and the design's own codes; send fewer "
            "kinds of code, or set triggers.allow_code_overlap: true to let item codes "
            "repeat.")):
        assign_triggers(_sets(199), events=events)
    assert len(set(_item_codes(assign_triggers(_sets(198), events=events)).values())) == 198
    out = assign_triggers(_sets(199), events=events,
                          schema={"triggers": {"allow_code_overlap": True}})
    assert capsys.readouterr().out == (
        "lexsync: 199 item sets exceed the 198 free item codes; item codes wrap and repeat.\n")
    codes = list(_item_codes(out).values())
    assert set(codes).isdisjoint({101, 102})
    # The first set's code is the one used twice.
    assert sorted(codes).count(40) == 2 and len(set(codes)) == 198
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: triggers.allow_code_overlap must be true or false.")):
        assign_triggers(_sets(2), events=events,
                        schema={"triggers": {"allow_code_overlap": "yes"}})


def test_the_trials_json_carries_15_significant_digits(schema, tmp_path):
    # R's jsonlite wrote four decimal places of a fractional number and this engine every
    # digit, so the page differed between the engines. Both now write 15 significant
    # digits. test-scripting.R pins the same line.
    stim = pd.DataFrame({"word": ["cat", "dog"], "condition": ["a", "b"], "set": [1, 1],
                         "trial": [1, 2], "word_ms": [33.333333, 1000 / 30]})
    design = {"name": "t", "language": "english", "events": [
        {"type": "text", "content": "{word}", "duration": {"from_column": "word_ms"}}]}
    html = open(export_jspsych(assign_triggers(stim), design, schema, str(tmp_path)),
                encoding="utf-8").read()
    assert ('const TRIALS = [{"trial":1,"set":1,"condition":"a","word":"cat",'
            '"word_ms":33.333333,"condition_trigger":101,"item_trigger":40},'
            '{"trial":2,"set":1,"condition":"b","word":"dog","word_ms":33.3333333333333,'
            '"condition_trigger":102,"item_trigger":40}];') in html
