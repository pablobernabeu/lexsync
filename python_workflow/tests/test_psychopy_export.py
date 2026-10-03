"""Validate the generated PsychoPy script without installing PsychoPy.

A fake ``psychopy`` package emulates the slice of the API the script uses, with a
Window that runs ``callOnFlip`` callbacks on the next ``flip`` (as real PsychoPy
does) and a port that records the flip on which each trigger is written. The tests
assert that the onset trigger is written on the very flip the word first appears,
and run the script's ``main()`` to see which trials a participant is presented.
"""
import csv
import glob
import importlib.util
import json
import os
import sys
import types

import pandas as pd
import pytest
from helper_repo import repo_path

from lexsync.counterbalancing import counterbalance
from lexsync.scripting import assign_triggers, export_psychopy


class FakeWin:
    def __init__(self, *args, **kwargs):
        self.flip_count = 0
        self._queue = []

    def callOnFlip(self, fn, *args, **kwargs):
        self._queue.append((fn, args, kwargs))

    def flip(self):
        self.flip_count += 1
        queue, self._queue = self._queue, []
        for fn, args, kwargs in queue:
            fn(*args, **kwargs)

    def getActualFrameRate(self, *args, **kwargs):
        return 60.0

    def close(self):
        pass


class FakePort:
    def __init__(self, win):
        self.win = win
        self.events = []

    def setData(self, data):
        self.events.append((self.win.flip_count, int(data)))


def _install_fake_psychopy(dialog=None):
    """Install the fake package. ``dialog`` holds what the start-up dialog returns
    when OK is pressed; None stands for Cancel."""
    psychopy = types.ModuleType("psychopy")
    visual = types.ModuleType("psychopy.visual")
    core = types.ModuleType("psychopy.core")
    event = types.ModuleType("psychopy.event")
    parallel = types.ModuleType("psychopy.parallel")
    gui = types.ModuleType("psychopy.gui")

    class TextStim:
        def __init__(self, *a, **k):
            self.text = ""

        def draw(self):
            pass

    visual.Window = FakeWin
    visual.TextStim = TextStim
    core.wait = lambda *_a, **_k: None
    core.quit = lambda *_a, **_k: None
    event.getKeys = lambda *_a, **_k: []
    event.waitKeys = lambda *_a, **_k: None

    class DlgFromDict:
        """Writes the answers into the dictionary it was given, as PsychoPy's does."""

        def __init__(self, dictionary, *args, **kwargs):
            self.OK = dialog is not None
            if dialog is not None:
                dictionary.update(dialog)

    gui.DlgFromDict = DlgFromDict

    class ParallelPort:
        def __init__(self, *a, **k):
            raise NotImplementedError

    parallel.ParallelPort = ParallelPort
    psychopy.visual, psychopy.core, psychopy.event, psychopy.parallel = visual, core, event, parallel
    psychopy.gui = gui
    for name, module in [("psychopy", psychopy), ("psychopy.visual", visual),
                         ("psychopy.core", core), ("psychopy.event", event),
                         ("psychopy.parallel", parallel), ("psychopy.gui", gui)]:
        sys.modules[name] = module


def _load_generated(path):
    spec = importlib.util.spec_from_file_location("lexsync_generated_psychopy", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_main(module, argv, monkeypatch):
    """Run the generated script's main() as if launched with `argv`, and return the
    trials it presented, in order."""
    presented = []
    run_event = module.run_event

    def recording(win, port, text_stim, ev, trial):
        # Every event of a trial receives the same row, so a new row is a new trial.
        if not presented or presented[-1] is not trial:
            presented.append(trial)
        return run_event(win, port, text_stim, ev, trial)

    monkeypatch.setattr(module, "run_event", recording)
    monkeypatch.setattr(sys, "argv", ["experiment.py", *argv])
    module.main()
    return presented


def _whole(cell):
    """A replicate or list cell as a number. A table without the column is one
    replicate, or one list, numbered 1."""
    return 1 if cell is None or str(cell).strip() == "" else int(float(cell))


def _two_list_stimuli(schema):
    """Two targets, each related in one list and unrelated in the other."""
    stim = pd.DataFrame({"prime": ["hot", "sky", "sun", "big"],
                         "target": ["cold", "cold", "moon", "moon"],
                         "condition": ["related", "unrelated"] * 2, "set": [1, 1, 2, 2]})
    design = {"name": "t", "language": "english", "paradigm": "priming",
              "counterbalance": {"lists": 2}}
    return assign_triggers(counterbalance(stim, design, schema)), design


def _replicated_stimuli(schema):
    """Two disjoint item samples (replicates), each dealt into one list."""
    stim = pd.DataFrame({"word": ["ant", "bee", "cat", "dog", "eel", "fox", "gnu", "hen"],
                         "condition": ["hi", "lo"] * 4, "set": [1, 1, 2, 2] * 2,
                         "replicate": [1, 1, 1, 1, 2, 2, 2, 2]})
    design = {"name": "r", "language": "english", "counterbalance": {"lists": 1}}
    return assign_triggers(counterbalance(stim, design, schema)), design


def test_onset_trigger_is_flip_locked(schema, tmp_path):
    _install_fake_psychopy()
    stim = assign_triggers(pd.DataFrame({
        "word": ["cat", "dog"], "condition": ["a", "b"], "set": [1, 2], "trial": [1, 2],
        "length": 3, "frequency": 5, "n_density": 2, "old20": 1.5,
    }))
    design = {"name": "t", "language": "english",
              "timing": {"fixation_frames": 3, "word_frames": 4, "isi_frames": 2}}
    path = export_psychopy(stim, design, schema, str(tmp_path))

    module = _load_generated(path)
    # The factorial event sequence: fixation, the critical word (onset-locked
    # condition marker), response, blank.
    types = [ev["type"] for ev in module.EVENTS]
    assert types == ["fixation", "text", "response", "blank"]

    win = FakeWin()
    port = FakePort(win)
    text_stim = module.visual.TextStim()
    trial = {"word": "cat", "condition_trigger": 101, "item_trigger": 40}
    for ev in module.EVENTS:
        module.run_event(win, port, text_stim, ev, trial)

    onset_flip = 3 + 1                                 # first flip showing the word
    assert (onset_flip, 101) in port.events            # condition marker bound to onset
    assert text_stim.text == "cat"


def test_mock_port_fallback_runs(schema, tmp_path):
    _install_fake_psychopy()
    stim = assign_triggers(pd.DataFrame({
        "word": ["cat"], "condition": ["a"], "set": [1], "trial": [1],
        "length": 3, "frequency": 5, "n_density": 2, "old20": 1.5,
    }))
    path = export_psychopy(stim, {"name": "t", "language": "english", "timing": {}}, schema, str(tmp_path))
    module = _load_generated(path)
    port = module.open_port(0x0378)          # ParallelPort raises -> MockPort
    assert type(port).__name__ == "MockPort"


# ---- One counterbalancing version per participant ------------------------------------
#
# A presentation version is one (replicate, list) pair of the presented trials. The
# conditions file holds every version, because one script serves every participant, and
# the script used to present it whole: in a Latin-square design each target appeared in
# both conditions, and in a resampled design every participant saw every replicate.
# test-scripting.R holds the R engine to the same generated script.

def _shipped_scripts():
    """Each shipped PsychoPy script with its conditions file and its versions, the
    (replicate, list) pairs of that file in order, and the design's recipe."""
    folder = repo_path("output", "experiments")
    out = []
    for script in sorted(glob.glob(os.path.join(folder, "*_psychopy.py"))):
        with open(script[:-len(".py")] + ".csv", newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        keys = sorted({(_whole(r.get("replicate")), _whole(r.get("list"))) for r in rows})
        base = os.path.basename(script)[:-len("_psychopy.py")]
        record = repo_path("output", "reports", f"{base}_datasheet_py.json")
        with open(record, encoding="utf-8") as handle:
            recipe = json.load(handle)["counterbalancing"]["recipe"]
        out.append((script, rows, keys, recipe))
    return out


def test_every_multi_version_design_presents_one_version_per_run(monkeypatch):
    _install_fake_psychopy()
    shipped = [s for s in _shipped_scripts() if len(s[2]) > 1]
    names = {os.path.basename(s[0]) for s in shipped}
    # The multi-list demonstrations and the three replicates of en_resample.
    assert {"en_priming_english_psychopy.py", "en_balanced_lists_english_psychopy.py",
            "en_resample_english_psychopy.py"} <= names
    for script, rows, keys, recipe in shipped:
        module = _load_generated(script)
        for k, key in enumerate(keys, start=1):
            what = f"{os.path.basename(script)}, version {k}"
            presented = _run_main(module, ["--participant", str(k), "--version", str(k)],
                                  monkeypatch)
            # That version's rows, each once and in the file's order, and no other row.
            assert presented == [r for r in rows
                                 if (_whole(r.get("replicate")), _whole(r.get("list"))) == key], what
            main = [r for r in presented if r.get("block", "main") == "main"]
            cells = [(r["set"], r["condition"]) for r in main]
            assert len(cells) == len(set(cells)), what
            if recipe == "latin_square_target":
                # Each target once, in one condition: the rotation as designed.
                assert len({r["set"] for r in main}) == len(main), what


def test_the_participant_number_chooses_the_version(schema, tmp_path, monkeypatch):
    _install_fake_psychopy()
    stim, design = _two_list_stimuli(schema)
    module = _load_generated(export_psychopy(stim, design, schema, str(tmp_path)))
    assert module.VERSIONS == [{"version": 1, "replicate": 1, "list": 1, "n_trials": 2},
                               {"version": 2, "replicate": 1, "list": 2, "n_trials": 2}]
    # Participant p runs version ((p - 1) mod 2) + 1, the rule participant_table() uses.
    for participant, wanted in ((1, "1"), (2, "2"), (3, "1"), (4, "2")):
        shown = _run_main(module, ["--participant", str(participant)], monkeypatch)
        assert {t["list"] for t in shown} == {wanted}
        assert sorted(t["target"] for t in shown) == ["cold", "moon"]
    # A version given at launch wins over the rule, and without replicates a list
    # names its version.
    for argv in (["--participant", "1", "--version", "2"], ["--list", "2"], ["--version=2"]):
        assert {t["list"] for t in _run_main(module, argv, monkeypatch)} == {"2"}


def test_the_runner_refuses_a_version_it_does_not_have(schema, tmp_path, monkeypatch):
    _install_fake_psychopy()
    stim, design = _two_list_stimuli(schema)
    module = _load_generated(export_psychopy(stim, design, schema, str(tmp_path)))
    refusals = {
        ("--version", "3"): "lexsync: version 3 was asked for, but this experiment has "
                            "versions 1 to 2.",
        ("--version", "two"): "lexsync: the version must be a whole number from 1, not 'two'.",
        ("--participant", "0"): "lexsync: the participant number must be a whole number "
                                "from 1, not '0'.",
        ("--list", "3"): "lexsync: there is no list 3. This experiment has lists 1, 2.",
        ("--version",): "lexsync: --version needs a value.",
    }
    for argv, message in refusals.items():
        with pytest.raises(SystemExit) as stop:
            _run_main(module, list(argv), monkeypatch)
        assert stop.value.code == message


def test_the_runner_asks_for_the_participant_when_launched_without_arguments(
        schema, tmp_path, monkeypatch):
    stim, design = _two_list_stimuli(schema)
    path = export_psychopy(stim, design, schema, str(tmp_path))
    # A blank version takes the participant's version by the rule.
    _install_fake_psychopy(dialog={"participant": "2", "version": ""})
    assert {t["list"] for t in _run_main(_load_generated(path), [], monkeypatch)} == {"2"}
    _install_fake_psychopy(dialog={"participant": "", "version": "1"})
    assert {t["list"] for t in _run_main(_load_generated(path), [], monkeypatch)} == {"1"}
    # Neither answer leaves no version to run, and Cancel ends the run.
    _install_fake_psychopy(dialog={"participant": "", "version": ""})
    with pytest.raises(SystemExit) as stop:
        _run_main(_load_generated(path), [], monkeypatch)
    assert stop.value.code == ("lexsync: give a participant number, or a version from "
                               "1 to 2.")
    _install_fake_psychopy(dialog=None)
    with pytest.raises(SystemExit) as stop:
        _run_main(_load_generated(path), [], monkeypatch)
    assert stop.value.code == 0


def test_replicates_are_versions_that_a_list_cannot_name(schema, tmp_path, monkeypatch):
    _install_fake_psychopy()
    stim, design = _replicated_stimuli(schema)
    module = _load_generated(export_psychopy(stim, design, schema, str(tmp_path)))
    assert [(v["replicate"], v["list"]) for v in module.VERSIONS] == [(1, 1), (2, 1)]
    shown = _run_main(module, ["--version", "2"], monkeypatch)
    assert sorted(t["word"] for t in shown) == ["eel", "fox", "gnu", "hen"]
    assert {t["replicate"] for t in shown} == {"2"}
    with pytest.raises(SystemExit) as stop:
        _run_main(module, ["--list", "1"], monkeypatch)
    assert stop.value.code == ("lexsync: this experiment's versions span several "
                               "replicates, so a list does not name one. Give --version "
                               "(1 to 2) instead.")


def test_a_single_version_design_presents_every_trial(schema, tmp_path, monkeypatch):
    _install_fake_psychopy()
    stim = assign_triggers(pd.DataFrame({
        "word": ["cat", "dog"], "condition": ["a", "b"], "set": [1, 2], "trial": [1, 2],
        "list": [1, 1], "length": 3, "frequency": 5, "n_density": 2, "old20": 1.5,
    }))
    module = _load_generated(export_psychopy(
        stim, {"name": "t", "language": "english", "timing": {}}, schema, str(tmp_path)))
    assert len(module.VERSIONS) == 1
    # Any participant runs the one version, and no version need be given.
    for argv in (["--participant", "3"], ["--version", "1"]):
        assert [t["word"] for t in _run_main(module, argv, monkeypatch)] == ["cat", "dog"]
    _install_fake_psychopy(dialog={"participant": "", "version": ""})
    module = _load_generated(module.__file__)
    assert [t["word"] for t in _run_main(module, [], monkeypatch)] == ["cat", "dog"]
