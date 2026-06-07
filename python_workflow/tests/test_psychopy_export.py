"""Validate the generated PsychoPy script without installing PsychoPy.

A fake ``psychopy`` package emulates the slice of the API the script uses, with a
Window that runs ``callOnFlip`` callbacks on the next ``flip`` (as real PsychoPy
does) and a port that records the flip on which each trigger is written. The test
asserts that the onset trigger is written on the very flip the word first appears.
"""
import importlib.util
import sys
import types

import pandas as pd

from lexsync.scripting import assign_triggers, export_psychopy


class FakeWin:
    def __init__(self):
        self.flip_count = 0
        self._queue = []

    def callOnFlip(self, fn, *args, **kwargs):
        self._queue.append((fn, args, kwargs))

    def flip(self):
        self.flip_count += 1
        queue, self._queue = self._queue, []
        for fn, args, kwargs in queue:
            fn(*args, **kwargs)

    def close(self):
        pass


class FakePort:
    def __init__(self, win):
        self.win = win
        self.events = []

    def setData(self, data):
        self.events.append((self.win.flip_count, int(data)))


def _install_fake_psychopy():
    psychopy = types.ModuleType("psychopy")
    visual = types.ModuleType("psychopy.visual")
    core = types.ModuleType("psychopy.core")
    event = types.ModuleType("psychopy.event")
    parallel = types.ModuleType("psychopy.parallel")

    class TextStim:
        def __init__(self, *a, **k):
            self.text = ""

        def draw(self):
            pass

    class Window:
        def __init__(self, *a, **k):
            pass

    visual.Window = Window
    visual.TextStim = TextStim
    core.wait = lambda *_a, **_k: None
    core.quit = lambda *_a, **_k: None
    event.getKeys = lambda *_a, **_k: []

    class ParallelPort:
        def __init__(self, *a, **k):
            raise NotImplementedError

    parallel.ParallelPort = ParallelPort
    psychopy.visual, psychopy.core, psychopy.event, psychopy.parallel = visual, core, event, parallel
    for name, module in [("psychopy", psychopy), ("psychopy.visual", visual),
                         ("psychopy.core", core), ("psychopy.event", event),
                         ("psychopy.parallel", parallel)]:
        sys.modules[name] = module


def _load_generated(path):
    spec = importlib.util.spec_from_file_location("lexsync_generated_psychopy", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_onset_trigger_is_flip_locked(schema, tmp_path):
    _install_fake_psychopy()
    stim = assign_triggers(pd.DataFrame({
        "word": ["cat", "dog"], "condition": ["a", "b"], "set": [1, 1], "trial": [1, 2],
        "length": 3, "frequency": 5, "n_density": 2, "old20": 1.5,
    }))
    design = {"name": "t", "language": "english",
              "timing": {"fixation_frames": 3, "word_frames": 4, "isi_frames": 2}}
    path = export_psychopy(stim, design, schema, str(tmp_path))

    module = _load_generated(path)
    assert module.FIXATION_FRAMES == 3 and module.WORD_DURATION_FRAMES == 4

    win = FakeWin()
    port = FakePort(win)
    fixation = module.visual.TextStim()
    word = module.visual.TextStim()
    module.present_trial(win, port, fixation, word,
                         {"word": "cat", "target_word_trigger": 40, "condition_trigger": 101})

    onset_flip = module.FIXATION_FRAMES + 1            # first flip showing the word
    assert (onset_flip, 40) in port.events            # onset trigger bound to that flip
    assert (onset_flip, 101) not in port.events       # condition marker is sent later
    assert word.text == "cat"


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
