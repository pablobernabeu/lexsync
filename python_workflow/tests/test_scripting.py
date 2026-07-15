import pandas as pd

from lexsync.scripting import (_language_tag, assign_triggers, export_jspsych,
                               export_opensesame, export_psychopy)


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


def test_psychopy_export_is_frame_locked(schema, tmp_path):
    design = {"name": "t", "language": "english", "timing": {}}
    path = export_psychopy(_stim(), design, schema, str(tmp_path))
    text = open(path, encoding="utf-8").read()
    assert "win.callOnFlip(port.setData" in text
    assert "{{" not in text  # all placeholders substituted


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
