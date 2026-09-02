"""Structural validation of the generated jsPsych experiment (no browser needed)."""
import json
import re

import pandas as pd

from lexsync.counterbalancing import counterbalance
from lexsync.paradigms import referenced_fields, resolve_events
from lexsync.scripting import assign_triggers, export_jspsych


def validate_jspsych(text):
    assert text.lstrip().startswith("<!DOCTYPE html>")
    assert "</html>" in text
    assert "jspsych@" in text                      # the library is loaded
    assert "initJsPsych()" in text and "jsPsych.run(timeline)" in text
    # The embedded data parse as JSON (the HTML-safe < etc. are valid escapes).
    events = json.loads(re.search(r"const EVENTS = (.*?);\n", text, re.S).group(1))
    trials = json.loads(re.search(r"const TRIALS = (.*?);\n", text, re.S).group(1))
    assert events and trials
    return events, trials


def _stim():
    s = pd.DataFrame({
        "word": ["cat", "dog", "car", "cap"], "condition": ["a", "a", "b", "b"],
        "set": [1, 2, 1, 2], "trial": [1, 2, 3, 4], "length": 3, "frequency": 5,
        "n_density": 2, "old20": 1.5,
    })
    return assign_triggers(s)


def test_jspsych_is_structurally_valid(schema, tmp_path):
    design = {"name": "t", "language": "english", "timing": {}}
    path = export_jspsych(_stim(), design, schema, str(tmp_path))
    events, trials = validate_jspsych(open(path, encoding="utf-8").read())
    # every trial carries the fields the events reference and the trigger columns
    fields = referenced_fields(resolve_events(design))
    for trial in trials:
        for f in fields:
            assert f in trial
        assert "condition_trigger" in trial and 0 <= int(trial["condition_trigger"]) <= 255


def test_jspsych_maps_keys_to_browser_names(schema, tmp_path):
    design = {"name": "t", "language": "english", "timing": {}}
    events, _ = validate_jspsych(
        open(export_jspsych(_stim(), design, schema, str(tmp_path)), encoding="utf-8").read())
    response = [e for e in events if e["type"] == "response"][0]
    assert response["keys"] == ["arrowleft", "arrowright"]  # 'left'/'right' -> browser keys


def test_jspsych_escapes_html_in_data(schema, tmp_path):
    # A crafted stimulus cannot break out of the <script> block.
    stim = assign_triggers(pd.DataFrame({
        "word": ["</script><b>x"], "condition": ["a"], "set": [1], "trial": [1],
        "length": 3, "frequency": 5, "n_density": 2, "old20": 1.5,
    }))
    text = open(export_jspsych(stim, {"name": "t", "language": "english", "timing": {}},
                               schema, str(tmp_path)), encoding="utf-8").read()
    assert "</script><b>x" not in text          # the literal closing tag is escaped
    _, trials = validate_jspsych(text)
    assert trials[0]["word"] == "</script><b>x"  # but the value round-trips via JSON


def test_the_page_presents_one_counterbalancing_list(schema, tmp_path):
    # The trials are embedded whole, because one page serves every participant, and a
    # timeline built from all of them showed each target once per list: under a Latin
    # square, once in every condition. The page selects the participant's list from its
    # ?participant= query, the rule the other two targets follow. Pinned in
    # test-jspsych.R too.
    stim = pd.DataFrame({"prime": ["hot", "sky", "sun", "big"],
                         "target": ["cold", "cold", "moon", "moon"],
                         "condition": ["related", "unrelated"] * 2, "set": [1, 1, 2, 2],
                         "length": 4, "frequency": 5, "n_density": 2, "old20": 1.5})
    design = {"name": "t", "language": "english", "paradigm": "priming",
              "counterbalance": {"lists": 2}}
    stim = assign_triggers(counterbalance(stim, design, schema))
    text = open(export_jspsych(stim, design, schema, str(tmp_path)),
                encoding="utf-8").read()
    _, trials = validate_jspsych(text)
    # The embedded data stay complete; it is the timeline that takes one list.
    assert sorted({str(t["list"]) for t in trials}) == ["1", "2"]
    assert "const RUN_TRIALS = trialsForParticipant(TRIALS, PARTICIPANT);" in text
    assert "for (const trial of RUN_TRIALS) {" in text
    assert 'get("participant")' in text
