import pandas as pd

from lexsync.scripting import assign_triggers, export_opensesame, export_psychopy


def _stim():
    s = pd.DataFrame({
        "word": ["cat", "dog", "car", "cap"], "condition": ["a", "a", "b", "b"],
        "set": [1, 2, 1, 2], "trial": [1, 2, 3, 4], "length": 3, "frequency": 5,
        "n_density": 2, "old20": 1.5,
    })
    return assign_triggers(s)


def test_triggers_in_range():
    s = _stim()
    assert s["target_word_trigger"].between(40, 239).all()
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
