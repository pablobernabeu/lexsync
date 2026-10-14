"""Validate the generated PsychoPy script without installing PsychoPy.

A fake ``psychopy`` package emulates the slice of the API the script uses, with a
Window that runs ``callOnFlip`` callbacks on the next ``flip`` (as real PsychoPy
does) and a port that records the flip on which each trigger is written. The tests
assert that the onset trigger is written on the very flip the word first appears,
and run the script's ``main()`` to see which trials a participant is presented and
what the data file records.

Each flip advances a simulated clock to the display's next refresh, 60 Hz unless a
test asks for another rate, and core.wait() advances it by the time waited. The fake
keyboard (``psychopy.hardware.keyboard.Keyboard``) presses keys on a schedule against
that clock: a response window opens whenever the script resets the keyboard clock,
which it queues on the flip that opens the window, and the schedule says which key is
pressed how many seconds later. Like the real keyboard, a key's ``rt`` is the time
of the press on that clock, not the time the script polled for it.
"""
import csv
import glob
import importlib.util
import json
import math
import os
import re
import sys
import types

import pandas as pd
import pytest
from helper_repo import repo_path

from lexsync.counterbalancing import counterbalance
from lexsync.scripting import assign_triggers, export_psychopy

FRAME_S = 1.0 / 60.0


class FakeTime:
    """The simulated time, in seconds, that the fake display has reached, and the
    display's refresh rate."""

    now = 0.0
    hz = 60.0


# The text of every TextStim drawn, in order, so a test can see what was on screen when
# the script waited for a key. Cleared by _install_fake_psychopy.
DRAWN = []
# The keyword arguments of every window opened and every TextStim created, in order.
# Cleared by _install_fake_psychopy.
WINDOWS = []
TEXT_STIMS = []


class FakeWin:
    def __init__(self, *args, **kwargs):
        self.flip_count = 0
        self._queue = []
        WINDOWS.append(kwargs)

    def callOnFlip(self, fn, *args, **kwargs):
        self._queue.append((fn, args, kwargs))

    def flip(self):
        # A flip lands on the display's next refresh, and the callbacks queued for it
        # run then, as in PsychoPy's Window.flip(). Real PsychoPy returns the time of
        # the flip, and so does this one.
        self.flip_count += 1
        FakeTime.now = (math.floor(FakeTime.now * FakeTime.hz + 1e-6) + 1) / FakeTime.hz
        queue, self._queue = self._queue, []
        for fn, args, kwargs in queue:
            fn(*args, **kwargs)
        return FakeTime.now

    def getActualFrameRate(self, *args, **kwargs):
        return FakeTime.hz

    def close(self):
        pass


class FakeKey:
    def __init__(self, name, rt):
        self.name = name
        self.rt = rt


def press_first_key_after(seconds):
    """A schedule that presses the first key a window accepts, `seconds` after it
    opens."""
    def press(window, keys):
        return next(k for k in keys if k != "escape"), seconds
    return press


class FakeKeyboard:
    """psychopy.hardware.keyboard.Keyboard, pressing keys on a schedule.

    ``press(window, keys)`` gives the key pressed in the ``window``-th response window
    (counted from 1) and the seconds after the window opened at which it is pressed,
    or None for no press. A window opens at each reset of the keyboard clock."""

    def __init__(self, press, gate="space", notice="c"):
        self.press = press
        self.gate = gate
        self.notice = notice
        self.window = 0
        self.planned = None
        self.reset_at = 0.0
        self.windows = []        # the keys each window accepted, in order
        # Each wait for a key: the keys it accepted, the text last drawn and how many
        # response windows had opened before it.
        self.waits = []
        keyboard = self

        class Clock:
            def reset(self):
                keyboard.window += 1
                keyboard.planned = "unasked"
                keyboard.reset_at = FakeTime.now

            def getTime(self):
                return FakeTime.now - keyboard.reset_at

        self.clock = Clock()

    def clearEvents(self, *args, **kwargs):
        pass

    def getKeys(self, keyList=None, waitRelease=True, **kwargs):
        if self.planned == "unasked":
            self.windows.append(list(keyList))
            self.planned = self.press(self.window, list(keyList))
        if self.planned is None or self.planned == "unasked":
            return []
        name, at = self.planned
        if self.clock.getTime() < at:
            return []
        self.planned = None
        return [FakeKey(name, at)]

    def waitKeys(self, keyList=None, **kwargs):
        # The notice that no trigger codes will be sent, the one wait that takes C, where
        # the experimenter presses `notice`. Then the start gate, where the participant
        # presses `gate`, and the pauses between blocks, where the participant goes on
        # at once.
        self.waits.append((list(keyList), DRAWN[-1] if DRAWN else None, self.window))
        if "c" in keyList:
            return [FakeKey(self.notice, 0.0)]
        others = [keys for keys, _, _ in self.waits if "c" not in keys]
        return [FakeKey(self.gate if len(others) == 1 else "space", 0.0)]


class FakePort:
    def __init__(self, win):
        self.win = win
        self.events = []      # (flip, code)
        self.writes = []      # (seconds, code)

    def setData(self, data):
        self.events.append((self.win.flip_count, int(data)))
        self.writes.append((FakeTime.now, int(data)))


def _install_fake_psychopy(dialog=None, press=None, gate="space", hz=60.0,
                           port_writes=None, notice="c"):
    """Install the fake package and return its keyboard. ``dialog`` holds what the
    start-up dialog returns when OK is pressed; None stands for Cancel. ``press`` is
    the keyboard's schedule, by default the first key 600 ms into each window, and
    ``gate`` the key pressed at the instructions. The display refreshes at ``hz``.
    Without ``port_writes`` no parallel port opens, so the script falls back to its
    mock, and ``notice`` is the key pressed at the notice that says so. With a list, a
    port opens and each write to it is appended there as (seconds, code)."""
    FakeTime.now = 0.0
    FakeTime.hz = float(hz)
    DRAWN.clear()
    WINDOWS.clear()
    TEXT_STIMS.clear()
    kb = FakeKeyboard(press or press_first_key_after(0.6), gate, notice)
    psychopy = types.ModuleType("psychopy")
    visual = types.ModuleType("psychopy.visual")
    core = types.ModuleType("psychopy.core")
    event = types.ModuleType("psychopy.event")
    parallel = types.ModuleType("psychopy.parallel")
    gui = types.ModuleType("psychopy.gui")
    hardware = types.ModuleType("psychopy.hardware")
    keyboard = types.ModuleType("psychopy.hardware.keyboard")
    keyboard.Keyboard = lambda *_a, **_k: kb
    hardware.keyboard = keyboard

    class TextStim:
        def __init__(self, *a, text="", **k):
            self.text = text
            self.height = k.get("height")
            TEXT_STIMS.append(self)

        def draw(self):
            DRAWN.append(self.text)

    def wait(secs, *args, **kwargs):
        FakeTime.now += float(secs)

    visual.Window = FakeWin
    visual.TextStim = TextStim
    core.wait = wait
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
            if port_writes is None:
                raise NotImplementedError

        def setData(self, data):
            port_writes.append((FakeTime.now, int(data)))

    parallel.ParallelPort = ParallelPort
    psychopy.visual, psychopy.core, psychopy.event, psychopy.parallel = visual, core, event, parallel
    psychopy.gui, psychopy.hardware = gui, hardware
    for name, module in [("psychopy", psychopy), ("psychopy.visual", visual),
                         ("psychopy.core", core), ("psychopy.event", event),
                         ("psychopy.parallel", parallel), ("psychopy.gui", gui),
                         ("psychopy.hardware", hardware),
                         ("psychopy.hardware.keyboard", keyboard)]:
        sys.modules[name] = module
    return kb


def _install_fake_serial(monkeypatch, opened, writes, fails=False):
    """Install a fake pyserial for the test. Each serial line opened is appended to
    ``opened`` as (device, baud rate), and each write to it to ``writes`` as (seconds,
    bytes). With ``fails``, opening a line raises, as pyserial does for a device that
    is not there."""
    serial = types.ModuleType("serial")

    class Serial:
        def __init__(self, port=None, baudrate=9600, **kwargs):
            if fails:
                raise OSError("could not open port %s" % port)
            opened.append((port, baudrate))

        def write(self, data):
            writes.append((FakeTime.now, bytes(data)))
            return len(data)

    serial.Serial = Serial
    monkeypatch.setitem(sys.modules, "serial", serial)


def _load_generated(path):
    spec = importlib.util.spec_from_file_location("lexsync_generated_psychopy", path)
    module = importlib.util.module_from_spec(spec)
    # Compiled from the source on every load. The import system would reuse the bytecode it
    # cached in __pycache__ while the source's size and whole-second modification time are
    # unchanged, so a script regenerated within the same second with a same-length edit (a text
    # height of 48 becoming 60) would run as the previous script.
    with open(path, encoding="utf-8") as fh:
        exec(compile(fh.read(), path, "exec"), module.__dict__)
    return module


def _run_main(module, argv, monkeypatch, data_dir):
    """Run the generated script's main() as if launched with `argv`, and return the
    trials it presented, in order. The data file goes to `data_dir`, so a run of a
    committed script never writes into the repository."""
    presented = []
    run_event = module.run_event

    def recording(win, port, text_stim, ev, trial):
        # Every event of a trial receives the same row, so a new row is a new trial.
        if not presented or presented[-1] is not trial:
            presented.append(trial)
        return run_event(win, port, text_stim, ev, trial)

    monkeypatch.setattr(module, "run_event", recording)
    monkeypatch.setattr(module, "DATA_DIR", str(data_dir), raising=False)
    monkeypatch.setattr(sys, "argv", ["experiment.py", *argv])
    module.main()
    return presented


def _data_files(data_dir):
    return sorted(glob.glob(os.path.join(str(data_dir), "*.csv")))


def _read_data(path):
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


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
    kb = _install_fake_psychopy(press=lambda window, keys: None)
    stim = assign_triggers(pd.DataFrame({
        "word": ["cat", "dog"], "condition": ["a", "b"], "set": [1, 2], "trial": [1, 2],
        "length": 3, "frequency": 5, "n_density": 2, "old20": 1.5,
    }))
    design = {"name": "t", "language": "english",
              "timing": {"fixation_frames": 3, "word_frames": 4, "isi_frames": 2}}
    path = export_psychopy(stim, design, schema, str(tmp_path))

    module = _load_generated(path)
    # The factorial event sequence: fixation, the critical word (onset-locked
    # condition marker) collecting the response from its onset, blank.
    assert [ev["type"] for ev in module.EVENTS] == ["fixation", "text", "blank"]
    assert module.EVENTS[1]["respond"] == {"keys": ["left", "right"], "timeout": 2}

    win = FakeWin()
    port = FakePort(win)
    text_stim = module.visual.TextStim()
    module.KEYBOARD = kb
    trial = {"word": "cat", "condition_trigger": 101, "item_trigger": 40}
    for ev in module.EVENTS:
        module.run_event(win, port, text_stim, ev, trial)

    onset_flip = 3 + 1                                 # first flip showing the word
    assert (onset_flip, 101) in port.events            # condition marker bound to onset
    assert text_stim.text == "cat"
    # The response window opened on that same flip: the keyboard clock was reset
    # there, so a reaction time is timed from the word's onset.
    assert kb.window == 1 and kb.windows == [["left", "right", "escape"]]
    assert kb.reset_at == pytest.approx(onset_flip * FRAME_S)


def test_mock_port_fallback_runs(schema, tmp_path):
    _install_fake_psychopy()
    stim = assign_triggers(pd.DataFrame({
        "word": ["cat"], "condition": ["a"], "set": [1], "trial": [1],
        "length": 3, "frequency": 5, "n_density": 2, "old20": 1.5,
    }))
    path = export_psychopy(stim, {"name": "t", "language": "english", "timing": {}}, schema, str(tmp_path))
    module = _load_generated(path)
    port, why = module.open_port()           # ParallelPort raises -> MockPort
    assert type(port).__name__ == "MockPort"
    assert why == "the parallel port at 0x0378 could not be opened"


# ---- What a run records ----------------------------------------------------------------
#
# The response window used to open only when the target had gone, event.waitKeys
# discarded every key pressed while the target was on screen, and the script wrote no
# file at all. A response is now collected from the onset of the stimulus it answers,
# and each trial is written to a data file under data/ beside the script, one row per
# trial, flushed as the run goes.

RUN_COLUMNS = ["participant", "version", "replicate", "list", "block", "trial", "set",
               "condition"]
MEASURES = ["response", "rt_ms", "timed_out", "correct", "region_rts_ms",
            "question_response", "question_rt_ms", "refresh_hz", "trigger_mode",
            "event_flips", "event_onsets_ms"]


def _lexdec():
    """Two words and two pseudowords in one list, each naming its correct key."""
    stim = assign_triggers(pd.DataFrame({
        "target": ["cat", "dog", "cag", "dop"],
        "condition": ["word", "word", "pseudoword", "pseudoword"],
        "set": [1, 2, 1, 2], "trial": [1, 2, 3, 4], "list": 1,
        "answer": ["left", "left", "right", "right"]}))
    return stim, {"name": "t", "language": "english", "paradigm": "lexical_decision"}


def test_a_keypress_during_the_target_is_recorded_from_its_onset(schema, tmp_path,
                                                                 monkeypatch):
    _install_fake_psychopy(press=press_first_key_after(0.6))
    stim, design = _lexdec()
    module = _load_generated(export_psychopy(stim, design, schema, str(tmp_path)))
    _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / "data")
    files = _data_files(tmp_path / "data")
    assert len(files) == 1
    assert re.fullmatch(r"t_english_p1_v1_[0-9]{8}-[0-9]{6}\.csv", os.path.basename(files[0]))
    header, rows = _read_data(files[0])
    assert header == (RUN_COLUMNS + ["target", "condition_trigger", "item_trigger", "answer"]
                      + MEASURES)
    assert [r["target"] for r in rows] == ["cat", "dog", "cag", "dop"]
    for row in rows:
        # 600 ms after onset, while the 800 ms target was still on screen. waitKeys
        # discarded that press and timed nothing.
        assert row["response"] == "left"
        assert abs(float(row["rt_ms"]) - 600.0) <= 1000.0 / 60
        assert row["timed_out"] == "0"
        assert (row["participant"], row["version"], row["replicate"], row["list"]) == (
            "1", "1", "1", "1")
        assert row["refresh_hz"] == "60.00"
        # The fixation's 30 flips, the target until the press, the 15-flip blank, each
        # event's onset timed from the trial's first flip.
        flips = [int(n) for n in row["event_flips"].split("|")]
        assert flips[0] == 30 and 36 <= flips[1] <= 38 and flips[2] == 15
        assert row["event_onsets_ms"].split("|")[:2] == ["0.0", "500.0"]
    assert [r["correct"] for r in rows] == ["1", "1", "0", "0"]


def test_a_keypress_after_the_window_closes_is_a_timeout(schema, tmp_path, monkeypatch):
    # The window runs from target onset for the target's 800 ms and the 2,000 ms
    # timeout, the total it had before, so a press at 2,900 ms comes too late.
    _install_fake_psychopy(press=press_first_key_after(2.9))
    stim, design = _lexdec()
    module = _load_generated(export_psychopy(stim, design, schema, str(tmp_path)))
    _run_main(module, ["--version", "1"], monkeypatch, tmp_path / "data")
    files = _data_files(tmp_path / "data")
    # No participant number was given, so none is in the name or the rows.
    assert re.fullmatch(r"t_english_v1_[0-9]{8}-[0-9]{6}\.csv", os.path.basename(files[0]))
    _, rows = _read_data(files[0])
    assert len(rows) == 4
    for row in rows:
        assert (row["response"], row["rt_ms"], row["timed_out"]) == ("", "", "1")
        assert row["correct"] == "0" and row["participant"] == ""
        # The target's 48 flips, then blank flips until 2,800 ms have passed on the
        # keyboard clock, give or take a flip of the simulated clock's rounding.
        assert 168 <= int(row["event_flips"].split("|")[1]) <= 170


def test_a_delayed_response_is_timed_from_its_own_window(schema, tmp_path, monkeypatch):
    # from: offset keeps a response window that opens after the stimulus, for designs
    # that ask the participant to wait. Its reaction time runs from that window.
    _install_fake_psychopy(press=press_first_key_after(0.3))
    stim, _ = _lexdec()
    design = {"name": "t", "language": "english", "events": [
        {"type": "fixation", "content": "+", "duration_ms": 500},
        {"type": "text", "content": "{target}", "duration_ms": 800, "trigger": "condition"},
        {"type": "response", "keys": ["left", "right"], "timeout_ms": 2000, "from": "offset"},
        {"type": "blank", "duration_ms": 250}]}
    module = _load_generated(export_psychopy(stim, design, schema, str(tmp_path)))
    assert [ev["type"] for ev in module.EVENTS] == ["fixation", "text", "response", "blank"]
    _run_main(module, ["--participant", "2"], monkeypatch, tmp_path / "data")
    _, rows = _read_data(_data_files(tmp_path / "data")[0])
    assert [(r["response"], r["rt_ms"], r["timed_out"]) for r in rows] == [
        ("left", "300.0", "0")] * 4
    # The target ran its full 48 flips, since no key was accepted while it was shown.
    assert {r["event_flips"].split("|")[1] for r in rows} == {"48"}


def test_a_delayed_window_opens_on_every_trial(schema, tmp_path, monkeypatch):
    # A window is timed on the keyboard clock, which is reset on the window's first
    # flip. The deadline was read before that flip, against the clock of the window
    # before, so from the second trial on, when more than the 2,000 ms timeout had passed
    # since the last key, the window closed before it opened and every later trial
    # recorded a timeout.
    _install_fake_psychopy(press=press_first_key_after(1.5))
    stim, _ = _lexdec()
    design = {"name": "t", "language": "english", "events": [
        {"type": "fixation", "content": "+", "duration_ms": 500},
        {"type": "text", "content": "{target}", "duration_ms": 800, "trigger": "condition"},
        {"type": "response", "keys": ["left", "right"], "timeout_ms": 2000, "from": "offset"},
        {"type": "blank", "duration_ms": 250}]}
    module = _load_generated(export_psychopy(stim, design, schema, str(tmp_path)))
    _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / "data")
    _, rows = _read_data(_data_files(tmp_path / "data")[0])
    assert [(r["response"], r["rt_ms"], r["timed_out"]) for r in rows] == [
        ("left", "1500.0", "0")] * 4


def test_a_question_after_a_slow_region_still_opens_its_window(schema, tmp_path,
                                                                monkeypatch):
    # The same clock: a question asked more than its 5,000 ms timeout after the last
    # region's key closed at once, unanswered.
    _install_fake_psychopy(
        press=lambda window, keys: ("space", 5.5) if keys[0] == "space" else ("f", 0.4))
    stim = assign_triggers(pd.DataFrame({
        "sentence": ["The|cat|sat.", "A|dog|ran|off."], "question": ["Sat?", "Ran?"],
        "condition": ["a", "b"], "set": [1, 2], "trial": [1, 2], "list": 1,
        "critical_region": [2, 3], "answer": ["f", "j"]}))
    design = {"name": "s", "language": "english", "paradigm": "self_paced_reading"}
    module = _load_generated(export_psychopy(stim, design, schema, str(tmp_path)))
    _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / "data")
    _, rows = _read_data(_data_files(tmp_path / "data")[0])
    assert [r["region_rts_ms"] for r in rows] == ["5500.0|5500.0|5500.0",
                                                   "5500.0|5500.0|5500.0|5500.0"]
    assert [(r["question_response"], r["question_rt_ms"]) for r in rows] == [
        ("f", "400.0"), ("f", "400.0")]


def test_reading_times_and_the_question_are_recorded(schema, tmp_path, monkeypatch):
    _install_fake_psychopy(press=press_first_key_after(0.4))
    stim = assign_triggers(pd.DataFrame({
        "sentence": ["The|cat|sat.", "A|dog|ran|off."], "question": ["Sat?", "Ran?"],
        "condition": ["a", "b"], "set": [1, 2], "trial": [1, 2], "list": 1,
        "critical_region": [2, 3], "answer": ["f", "j"]}))
    design = {"name": "s", "language": "english", "paradigm": "self_paced_reading"}
    module = _load_generated(export_psychopy(stim, design, schema, str(tmp_path)))
    _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / "data")
    header, rows = _read_data(_data_files(tmp_path / "data")[0])
    assert header == (RUN_COLUMNS + ["sentence", "question", "critical_region",
                                     "condition_trigger", "item_trigger", "answer"] + MEASURES)
    # Each region's reading time from its own flip, "|"-joined.
    assert [r["region_rts_ms"] for r in rows] == ["400.0|400.0|400.0",
                                                   "400.0|400.0|400.0|400.0"]
    assert [(r["question_response"], r["question_rt_ms"]) for r in rows] == [
        ("f", "400.0"), ("f", "400.0")]
    # No response event, so accuracy scores the question.
    assert [r["correct"] for r in rows] == ["1", "0"]
    assert {(r["response"], r["rt_ms"], r["timed_out"]) for r in rows} == {("", "", "")}


def test_an_escape_leaves_a_valid_data_file(schema, tmp_path, monkeypatch):
    # Escape in the third response window stops the run, and the file then holds the
    # two trials completed before it.
    _install_fake_psychopy(
        press=lambda window, keys: ("escape", 0.2) if window == 3 else ("left", 0.5))
    stim, design = _lexdec()
    module = _load_generated(export_psychopy(stim, design, schema, str(tmp_path)))
    _run_main(module, ["--participant", "4"], monkeypatch, tmp_path / "data")
    header, rows = _read_data(_data_files(tmp_path / "data")[0])
    assert header[-len(MEASURES):] == MEASURES
    assert [(r["target"], r["response"]) for r in rows] == [("cat", "left"), ("dog", "left")]


LEXDEC_TEXT = ("You will see a string of letters. Press %s if it is a real English word and "
               "%s if it is not. Respond as quickly and accurately as you can.")
START = "\n\nPress the space bar to begin."


def test_the_runner_shows_the_instructions_and_waits_for_space(schema, tmp_path,
                                                                monkeypatch):
    # The script started the trials at once, so nothing told the participant which key
    # meant what. It now shows the instructions and waits for the space bar, which also
    # lets the experimenter start the run, before the first trial. A port opens, so no
    # notice about missing trigger codes comes first.
    kb = _install_fake_psychopy(port_writes=[])
    stim, design = _lexdec()
    module = _load_generated(export_psychopy(stim, design, schema, str(tmp_path)))
    text = LEXDEC_TEXT % ("the left arrow key", "the right arrow key")
    assert module.INSTRUCTIONS == [text]
    presented = _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / "data")
    # The first wait for a key came before any response window opened.
    assert kb.waits[0] == (["space", "escape"], text + START, 0)
    assert len(presented) == 4
    assert len(_read_data(_data_files(tmp_path / "data")[0])[1]) == 4
    # A mapping rotated across lists gives each version its own keys.
    kb = _install_fake_psychopy(port_writes=[])
    rotated = dict(design, rotate_mapping_by_list=True)
    two = pd.concat([stim, stim.assign(list=2)], ignore_index=True)
    module = _load_generated(export_psychopy(two, rotated, schema, str(tmp_path)))
    assert module.INSTRUCTIONS == [text, LEXDEC_TEXT % ("the right arrow key",
                                                        "the left arrow key")]
    _run_main(module, ["--participant", "2"], monkeypatch, tmp_path / "data")
    assert kb.waits[0][1] == module.INSTRUCTIONS[1] + START


def _practice_and_fillers():
    """Two practice trials, then main trials with two fillers interleaved, as add_blocks
    orders them."""
    stim = assign_triggers(pd.DataFrame({
        "target": ["tree", "trel", "cat", "sun", "cag", "map", "dop"],
        "condition": ["word", "pseudoword", "word", "word", "pseudoword", "word",
                      "pseudoword"],
        "block": ["practice", "practice", "main", "filler", "main", "filler", "main"],
        "set": [10, 11, 1, 20, 1, 21, 2], "trial": list(range(1, 8)), "list": 1,
        "answer": ["left", "right", "left", "left", "right", "left", "right"]}))
    return stim, {"name": "t", "language": "english", "paradigm": "lexical_decision"}


def test_fillers_run_with_the_main_trials_and_only_the_practice_ends_in_a_pause(
        schema, tmp_path, monkeypatch):
    # The script paused wherever the block changed, and fillers are interleaved with the
    # main trials, so a pause came before and after every filler, set it apart and, after
    # each one, said that the practice trials had ended. Fillers now run with the main
    # trials, and the one pause comes where the practice trials end.
    kb = _install_fake_psychopy(port_writes=[])
    stim, design = _practice_and_fillers()
    module = _load_generated(export_psychopy(stim, design, schema, str(tmp_path)))
    presented = _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / "data")
    assert [t["target"] for t in presented] == ["tree", "trel", "cat", "sun", "cag", "map",
                                                "dop"]
    # The start gate, then the end of the practice, after its two response windows.
    assert [(text.split("\n")[0], opened) for _, text, opened in kb.waits] == [
        ("You will see a string of letters. Press the left arrow key if it is a real "
         "English word and the right arrow key if it is not. Respond as quickly and "
         "accurately as you can.", 0),
        ("End of the practice trials.", 2)]


def test_escape_at_the_instructions_stops_before_any_trial(schema, tmp_path, monkeypatch):
    _install_fake_psychopy(gate="escape")
    stim, design = _lexdec()
    module = _load_generated(export_psychopy(stim, design, schema, str(tmp_path)))
    assert _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / "data") == []
    # Nothing ran, so no data file was opened.
    assert _data_files(tmp_path / "data") == []


def test_a_second_run_never_overwrites_the_first(schema, tmp_path, monkeypatch):
    _install_fake_psychopy()
    stim, design = _lexdec()
    module = _load_generated(export_psychopy(stim, design, schema, str(tmp_path)))
    for _ in range(2):
        _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / "data")
    files = _data_files(tmp_path / "data")
    assert len(files) == 2
    assert all(len(_read_data(f)[1]) == 4 for f in files)


def test_every_shipped_script_writes_one_row_per_trial(tmp_path, monkeypatch):
    shipped = _shipped_scripts()
    assert len(shipped) == 21
    for script, _rows, _keys, _recipe in shipped:
        _install_fake_psychopy()
        module = _load_generated(script)
        out = tmp_path / os.path.basename(script)
        _run_main(module, ["--participant", "1"], monkeypatch, out)
        files = _data_files(out)
        assert len(files) == 1, script
        header, recorded = _read_data(files[0])
        assert header[:len(RUN_COLUMNS)] == RUN_COLUMNS, script
        assert header[-len(MEASURES):] == MEASURES, script
        assert len(recorded) == module.VERSIONS[0]["n_trials"], script
        # Every trial collected what its events ask for, 600 ms into each window.
        for row in recorded:
            if any(ev["type"] == "response" or "respond" in ev for ev in module.EVENTS):
                assert (row["rt_ms"], row["timed_out"]) == ("600.0", "0"), script
            if any(ev["type"] == "question" for ev in module.EVENTS):
                assert row["question_rt_ms"] == "600.0", script


# ---- How long each code is held -------------------------------------------------------
#
# The 254 and 255 session markers were set on a flip and cleared by the next statement.
# A code on an event shorter than the hold was cleared as soon as the event's last flip
# returned, so a one-flip event's pulse lasted no time at all. And the hold, floored at
# 10 ms before it was rounded to flips, fell to 6.9 ms at 144 Hz and 8.3 ms at 240 Hz.
# Recorders that sample the port every 0.5 to 2 ms miss such pulses. Every code now
# lasts the hold, in whole flips at the measured refresh and never under 10 ms. A code
# that outlasts its event is reset in the events after it, unless the next onset's code
# replaces it first.

def _pulses(writes):
    """Each code written to the port, as (code, onset, width, truncated), in seconds.

    A code lasts until the next write. It is truncated when that write is a 0 that the
    next code follows at the same moment, which is how a new onset ends a code still
    held. A write of 0 to a port at 0, such as the one that opens it, is not a pulse."""
    out = []
    for i, (t, code) in enumerate(writes):
        if code == 0:
            continue
        assert i + 1 < len(writes), f"code {code} was never reset"
        end_t, end_code = writes[i + 1]
        truncated = (end_code == 0 and i + 2 < len(writes) and writes[i + 2][1] != 0
                     and writes[i + 2][0] == end_t)
        out.append((code, t, end_t - t, truncated))
    return out


@pytest.mark.parametrize("hz", [60, 144, 240])
def test_every_code_lasts_the_hold_in_every_shipped_script(hz, tmp_path, monkeypatch):
    shipped = _shipped_scripts()
    assert len(shipped) == 21
    for script, _rows, _keys, _recipe in shipped:
        name = os.path.basename(script)
        writes = []
        _install_fake_psychopy(hz=hz, port_writes=writes)
        module = _load_generated(script)
        _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / name)
        hold = float(module.TRIGGER_HOLD_MS) / 1000.0
        pulses = _pulses(writes)
        assert pulses[0][0] == 254 and pulses[-1][0] == 255, name
        assert writes[-1][1] == 0, name
        for code, onset, width, truncated in pulses:
            # At least 10 ms, and within half a flip of the hold unless the next onset
            # ended it.
            assert width >= 0.010 - 1e-9, (name, code, onset, width)
            if not truncated:
                assert abs(width - hold) <= 0.5 / hz + 1e-9, (name, code, onset, width)


def test_the_hold_is_rounded_to_flips_and_never_below_10_ms(schema, tmp_path):
    _install_fake_psychopy()
    stim, design = _lexdec()
    module = _load_generated(export_psychopy(stim, design, schema, str(tmp_path)))
    # The default 50 ms hold keeps the flips it had, the nearest whole number of them.
    assert [module.trigger_hold_frames(hz) for hz in (60, 144, 240)] == [3, 7, 12]
    # A 10 ms hold is rounded up where the nearest whole number of flips falls short of
    # 10 ms: 6.9 ms (one flip) at 144 Hz, and 8.3 ms (two) at 240 Hz.
    module.TRIGGER_HOLD_MS = 10
    assert [module.trigger_hold_frames(hz) for hz in (60, 144, 240)] == [1, 2, 3]


def _one_trial(schema, tmp_path, events, press):
    """Run one trial of a design with these events at 60 Hz, and return what each
    event recorded and what was written to the port."""
    kb = _install_fake_psychopy(press=press)
    stim = assign_triggers(pd.DataFrame({"word": ["cat"], "condition": ["a"], "set": [1],
                                         "trial": [1]}))
    module = _load_generated(export_psychopy(stim, {"name": "t", "language": "english",
                                                    "events": events},
                                             schema, str(tmp_path)))
    module.KEYBOARD = kb
    module.TRIGGER_HOLD_FRAMES = module.trigger_hold_frames(60)
    win = FakeWin()
    port = FakePort(win)
    records = module.run_trial(win, port, module.visual.TextStim(),
                               {"word": "cat", "condition_trigger": "101",
                                "item_trigger": "40"})
    return records, port.writes


def test_a_code_outlasts_an_event_shorter_than_the_hold(schema, tmp_path):
    # A 17 ms prime is one flip at 60 Hz, and its code is held for the three flips of the
    # 50 ms hold, through the mask after it. A key 20 ms into the target ends the target,
    # and its code is still held for the hold, through the blank that follows.
    fixation = {"type": "fixation", "content": "+", "duration_ms": 500}
    prime = {"type": "text", "content": "{word}", "duration_ms": 17, "trigger": 20}
    target = {"type": "text", "content": "{word}", "duration_ms": 800,
              "trigger": "condition"}
    response = {"type": "response", "keys": ["left", "right"], "timeout_ms": 2000}
    blank = {"type": "blank", "duration_ms": 250}
    records, writes = _one_trial(
        schema, tmp_path, [fixation, prime, {"type": "mask", "content": "#####",
                                             "duration_ms": 100}, target, response, blank],
        press_first_key_after(0.02))
    assert [(code, round(width * 1000, 1), truncated)
            for code, _, width, truncated in _pulses(writes)] == [
        (20, 50.0, False), (101, 50.0, False)]
    # The prime still lasted its one flip and the mask its six; the key ended the
    # target on its third flip.
    assert [r["flips"] for r in records] == [30, 1, 6, 3, 15]
    # A code still held when the next onset comes ends on that onset's flip, with a 0
    # written just before the new code.
    _, writes = _one_trial(schema, tmp_path, [fixation, prime, target, response, blank],
                           press_first_key_after(0.6))
    assert [(code, round(width * 1000, 1), truncated)
            for code, _, width, truncated in _pulses(writes)] == [
        (20, 16.7, True), (101, 50.0, False)]


# ---- The window, the text and the trigger device --------------------------------------
#
# The script always opened a 1280 x 1024 window, though PsychoPy's advice for reducing
# dropped frames is to run full screen. It drew its text at 48 px, where the OpenSesame
# experiment used 32. When the parallel port could not be opened, it fell back to
# printing the codes and said nothing more, so a session could run to its end without a
# single code reaching the amplifier. It had no way to send codes over a serial line.
# test-scripting.R checks the constants the R engine writes into the same script.

NOTICE = ("No trigger codes will be sent, because %s. Each code is printed in the console "
          "instead.\n\nPress C to continue without triggers, or escape to stop.")


def _with(schema, section, **settings):
    """The schema with `settings` added to its `section`."""
    return dict(schema, **{section: dict(schema.get(section) or {}, **settings)})


def test_the_window_is_full_screen_unless_the_schema_says_otherwise(schema, tmp_path,
                                                                     monkeypatch):
    _install_fake_psychopy(port_writes=[])
    stim, design = _lexdec()
    module = _load_generated(export_psychopy(stim, design, schema, str(tmp_path)))
    assert module.FULLSCREEN is True
    _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / "data")
    assert WINDOWS[-1]["fullscr"] is True
    windowed = _with(schema, "presentation", fullscreen=False)
    module = _load_generated(export_psychopy(stim, design, windowed, str(tmp_path)))
    assert module.FULLSCREEN is False
    _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / "data")
    assert (WINDOWS[-1]["fullscr"], WINDOWS[-1]["size"]) == (False, (1280, 1024))


def test_the_text_height_reaches_the_stimulus(schema, tmp_path, monkeypatch):
    for settings, height in (({}, 48), ({"text_height_px": 60}, 60)):
        _install_fake_psychopy(port_writes=[])
        stim, design = _lexdec()
        module = _load_generated(export_psychopy(
            stim, design, _with(schema, "presentation", **settings), str(tmp_path)))
        assert module.TEXT_HEIGHT_PX == height
        _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / "data")
        # The stimulus that showed the targets. The instructions keep their own size.
        assert [s.height for s in TEXT_STIMS if s.text == "dop"] == [height]


def test_without_a_port_the_experimenter_is_told_before_the_first_trial(
        schema, tmp_path, monkeypatch, capsys):
    kb = _install_fake_psychopy()
    stim, design = _lexdec()
    module = _load_generated(export_psychopy(stim, design, schema, str(tmp_path)))
    assert module.TRIGGER_MODE == "auto"
    _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / "data")
    # A notice the experimenter dismisses with C comes before the instructions, and the
    # console says the same.
    why = "the parallel port at 0x0378 could not be opened"
    assert kb.waits[0] == (["c", "escape"], NOTICE % why, 0)
    assert kb.waits[1][0] == ["space", "escape"]
    out = capsys.readouterr().out
    assert f"[lexsync] {why} (NotImplementedError)." in out
    assert f"[lexsync] NO TRIGGER CODES WILL BE SENT, because {why}." in out
    # Every row of the data file says the codes were printed, not sent.
    _, rows = _read_data(_data_files(tmp_path / "data")[0])
    assert [r["trigger_mode"] for r in rows] == ["mock"] * 4
    # With the port, no notice comes before the instructions, and the rows say so.
    kb = _install_fake_psychopy(port_writes=[])
    module = _load_generated(module.__file__)
    _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / "hardware")
    assert kb.waits[0][0] == ["space", "escape"]
    _, rows = _read_data(_data_files(tmp_path / "hardware")[0])
    assert {r["trigger_mode"] for r in rows} == {"hardware"}


def test_hardware_mode_stops_before_any_window_without_the_port(schema, tmp_path,
                                                                 monkeypatch):
    _install_fake_psychopy()
    stim, design = _lexdec()
    module = _load_generated(export_psychopy(
        stim, design, _with(schema, "triggers", mode="hardware"), str(tmp_path)))
    with pytest.raises(SystemExit) as stop:
        _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / "data")
    assert stop.value.code == (
        "lexsync: the parallel port at 0x0378 could not be opened (NotImplementedError). "
        "triggers.mode is hardware, so the experiment does not run without it.")
    assert WINDOWS == []
    assert _data_files(tmp_path / "data") == []
    # With the port, the run goes ahead.
    writes = []
    _install_fake_psychopy(port_writes=writes)
    module = _load_generated(module.__file__)
    _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / "data")
    assert 254 in [code for _, code in writes]
    _, rows = _read_data(_data_files(tmp_path / "data")[0])
    assert {r["trigger_mode"] for r in rows} == {"hardware"}


def test_mock_mode_prints_the_codes_without_trying_the_port(schema, tmp_path, monkeypatch,
                                                            capsys):
    writes = []
    kb = _install_fake_psychopy(port_writes=writes)
    stim, design = _lexdec()
    module = _load_generated(export_psychopy(
        stim, design, _with(schema, "triggers", mode="mock"), str(tmp_path)))
    _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / "data")
    # The port was there, and the script never wrote to it.
    assert writes == []
    assert kb.waits[0] == (["c", "escape"], NOTICE % "triggers.mode is mock", 0)
    assert "[lexsync mock trigger] 254" in capsys.readouterr().out
    _, rows = _read_data(_data_files(tmp_path / "data")[0])
    assert {r["trigger_mode"] for r in rows} == {"mock"}


def test_escape_at_the_trigger_notice_stops_before_any_trial(schema, tmp_path, monkeypatch):
    _install_fake_psychopy(notice="escape")
    stim, design = _lexdec()
    module = _load_generated(export_psychopy(stim, design, schema, str(tmp_path)))
    assert _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / "data") == []
    assert _data_files(tmp_path / "data") == []


def test_a_serial_backend_writes_each_code_as_one_byte(schema, tmp_path, monkeypatch):
    # The codes go to the serial line the schema names, never to the first port found,
    # and each is one byte, held and reset as on a parallel port.
    _install_fake_psychopy()
    opened, writes = [], []
    _install_fake_serial(monkeypatch, opened, writes)
    stim, design = _lexdec()
    serial = _with(schema, "triggers", backend="serial", serial_port="COM7", baudrate=57600)
    module = _load_generated(export_psychopy(stim, design, serial, str(tmp_path)))
    assert (module.TRIGGER_BACKEND, module.SERIAL_PORT, module.SERIAL_BAUDRATE) == (
        "serial", "COM7", 57600)
    _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / "data")
    assert opened == [("COM7", 57600)]
    assert {len(data) for _, data in writes} == {1}
    codes = [(t, data[0]) for t, data in writes]
    assert codes[0][1] == 0 and codes[-1][1] == 0
    pulses = _pulses(codes)
    assert pulses[0][0] == 254 and pulses[-1][0] == 255
    for code, onset, width, truncated in pulses:
        assert truncated or abs(width - 0.050) <= 0.5 / 60 + 1e-9, (code, onset, width)
    _, rows = _read_data(_data_files(tmp_path / "data")[0])
    assert {r["trigger_mode"] for r in rows} == {"hardware"}
    # A serial device that is not there is handled as a missing parallel port is.
    kb = _install_fake_psychopy()
    _install_fake_serial(monkeypatch, [], [], fails=True)
    module = _load_generated(module.__file__)
    _run_main(module, ["--participant", "1"], monkeypatch, tmp_path / "missing")
    assert kb.waits[0][1] == NOTICE % "the serial port COM7 could not be opened"


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


def test_every_multi_version_design_presents_one_version_per_run(tmp_path, monkeypatch):
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
                                  monkeypatch, tmp_path / "data")
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
    data = tmp_path / "data"
    for participant, wanted in ((1, "1"), (2, "2"), (3, "1"), (4, "2")):
        shown = _run_main(module, ["--participant", str(participant)], monkeypatch, data)
        assert {t["list"] for t in shown} == {wanted}
        assert sorted(t["target"] for t in shown) == ["cold", "moon"]
    # A version given at launch wins over the rule, and without replicates a list
    # names its version.
    for argv in (["--participant", "1", "--version", "2"], ["--list", "2"], ["--version=2"]):
        assert {t["list"] for t in _run_main(module, argv, monkeypatch, data)} == {"2"}


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
            _run_main(module, list(argv), monkeypatch, tmp_path / "data")
        assert stop.value.code == message
    # A run refused before it starts leaves no data file.
    assert _data_files(tmp_path / "data") == []


def test_the_runner_asks_for_the_participant_when_launched_without_arguments(
        schema, tmp_path, monkeypatch):
    stim, design = _two_list_stimuli(schema)
    path = export_psychopy(stim, design, schema, str(tmp_path))
    data = tmp_path / "data"
    # A blank version takes the participant's version by the rule.
    _install_fake_psychopy(dialog={"participant": "2", "version": ""})
    assert {t["list"] for t in _run_main(_load_generated(path), [], monkeypatch, data)} == {"2"}
    _install_fake_psychopy(dialog={"participant": "", "version": "1"})
    assert {t["list"] for t in _run_main(_load_generated(path), [], monkeypatch, data)} == {"1"}
    # Neither answer leaves no version to run, and Cancel ends the run.
    _install_fake_psychopy(dialog={"participant": "", "version": ""})
    with pytest.raises(SystemExit) as stop:
        _run_main(_load_generated(path), [], monkeypatch, data)
    assert stop.value.code == ("lexsync: give a participant number, or a version from "
                               "1 to 2.")
    _install_fake_psychopy(dialog=None)
    with pytest.raises(SystemExit) as stop:
        _run_main(_load_generated(path), [], monkeypatch, data)
    assert stop.value.code == 0


def test_replicates_are_versions_that_a_list_cannot_name(schema, tmp_path, monkeypatch):
    _install_fake_psychopy()
    stim, design = _replicated_stimuli(schema)
    module = _load_generated(export_psychopy(stim, design, schema, str(tmp_path)))
    assert [(v["replicate"], v["list"]) for v in module.VERSIONS] == [(1, 1), (2, 1)]
    shown = _run_main(module, ["--version", "2"], monkeypatch, tmp_path / "data")
    assert sorted(t["word"] for t in shown) == ["eel", "fox", "gnu", "hen"]
    assert {t["replicate"] for t in shown} == {"2"}
    # The data rows name the replicate and the list the run presented.
    _, rows = _read_data(_data_files(tmp_path / "data")[0])
    assert {(r["version"], r["replicate"], r["list"]) for r in rows} == {("2", "2", "1")}
    with pytest.raises(SystemExit) as stop:
        _run_main(module, ["--list", "1"], monkeypatch, tmp_path / "data")
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
    data = tmp_path / "data"
    # Any participant runs the one version, and no version need be given.
    for argv in (["--participant", "3"], ["--version", "1"]):
        assert [t["word"] for t in _run_main(module, argv, monkeypatch, data)] == ["cat", "dog"]
    _install_fake_psychopy(dialog={"participant": "", "version": ""})
    module = _load_generated(module.__file__)
    assert [t["word"] for t in _run_main(module, [], monkeypatch, data)] == ["cat", "dog"]
