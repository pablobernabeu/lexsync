"""Structural and referential validation of the generated OpenSesame .osexp, and an
emulation of what OpenSesame 3.3 and 4.x do with the cells of its loop table."""
import contextlib
import csv
import ctypes
import glob
import itertools
import math
import os
import re
import sys
import types
from unittest import mock

import pandas as pd
import pytest
from helper_repo import repo_path

from lexsync.scripting import assign_triggers, export_opensesame, loop_table


def validate_osexp(text):
    lines = text.splitlines()
    assert lines[0] == "---" and any(l == "API: 2.1" for l in lines[:5])

    starts = [l.split("set start ", 1)[1].strip() for l in lines if l.startswith("set start ")]
    assert starts, "no 'set start' entry point"

    defines = {}
    for line in lines:
        m = re.match(r"^define\s+(\S+)\s+(\S+)", line)
        if m:
            defines[m.group(2)] = m.group(1)
    assert starts[0] in defines, "entry point is not defined"

    for line in lines:
        m = re.match(r"^\trun\s+(\S+)", line)
        if m:
            assert m.group(1) in defines, f"'run {m.group(1)}' has no matching define"
    return True


def _stim():
    return assign_triggers(pd.DataFrame({
        "word": ["cat", "dog"], "condition": ["a", "b"], "set": [1, 1], "trial": [1, 2],
        "length": 3, "frequency": 5, "n_density": 2, "old20": 1.5,
    }))


def test_osexp_structurally_valid(schema, tmp_path):
    path = export_opensesame(_stim(), {"name": "t", "language": "english"}, schema, str(tmp_path))
    text = open(path, encoding="utf-8").read()
    assert validate_osexp(text)

    source = [l.split('"')[1] for l in text.splitlines() if "set source_file" in l][0]
    assert os.path.exists(os.path.join(str(tmp_path), source))


def test_loop_table_triggers_in_byte_range():
    lt = loop_table(_stim())
    assert lt["item_trigger"].between(0, 255).all()
    assert lt["condition_trigger"].between(0, 255).all()


# ---- What OpenSesame does with a loop cell ----------------------------------------------
#
# The rules below are transcribed from the sources of the two versions the generated
# experiments were checked against, opensesame-core 4.1.20 and python-opensesame 3.3.14
# (libopensesame/loop.py, syntax.py, var_store.py and response_store.py). OpenSesame reads
# the loop table through datamatrix, which may already have turned a numeric cell into a
# number. Each cell is fed in here as text, the case in which OpenSesame's own rules reach
# furthest.

class Altered(Exception):
    """A cell or value that OpenSesame would execute, substitute or rewrite."""


_FSTRING = re.compile(r"(?<!{){(?!{)")                                  # 4.1.20 only
_VARIABLE = re.compile(r"(?<!\\)(\\\\)*(\[[_a-zA-Z]+[_a-zA-Z0-9]*\])")  # both versions
_INLINE_PYTHON = re.compile(r"(?<!\\)(\\\\)*(\[=.*?[^\\]\])")           # both versions
PLAIN_NUMBER = re.compile(r"\A-?[0-9]+(\.[0-9]+)?\Z")


def _eval_text(val, fstrings):
    """syntax.eval_text: an f-string (4.x), a [variable] or an inline [=python]."""
    if not isinstance(val, str):
        return val
    if fstrings and _FSTRING.search(val):
        raise Altered(f"runs as an f-string: {val!r}")
    if _VARIABLE.search(val):
        raise Altered(f"substitutes a variable: {val!r}")
    if _INLINE_PYTHON.search(val):
        raise Altered(f"runs inline Python: {val!r}")
    return val.replace("\\[", "[").replace("\\]", "]")


def _auto_type(val, allow_bool=False, allow_none=False):
    """syntax.auto_type in 4.1.20. int() raises on nan and inf, as it does there."""
    if allow_bool and val in ("True", "False"):
        return val == "True"
    if allow_none and val == "None":
        return None
    try:
        f = float(val)
    except (TypeError, ValueError):
        return "None" if val is None else str(val)
    return int(f) if int(f) == f else f


def _store_4x(val):
    """var_store.set in 4.1.20: anything float() accepts is stored as a number."""
    if isinstance(val, bool):
        return val
    try:
        val = float(val)
    except (TypeError, ValueError):
        pass
    try:
        ival = int(val)
    except (TypeError, ValueError, ArithmeticError):
        return val
    return ival if ival == val else val


def loop_value(version, cell):
    """What the loop stores for one cell (loop.run, 4.1.20 lines 333-345 and 3.3.14
    lines 365-377)."""
    if cell.startswith("="):
        # 3.3 runs the rest as Python. 4.x drops the '=' and evaluates the rest as text.
        raise Altered(f"starts with '=': {cell!r}")
    if version == "3.3":
        return cell
    try:
        val = _auto_type(cell, allow_bool=True, allow_none=True)
    except (ValueError, OverflowError):
        val = cell                       # the loop logs an unusual type and goes on
    return _store_4x(_eval_text(val, fstrings=True))


def read_value(version, val, evaluate=True):
    """var.get(name, _eval=evaluate): 4.1.20 var_store.py lines 185-223, 3.3.14 lines
    232-291. 3.3 converts to a number whether or not it evaluates."""
    if version == "4.x":
        return _auto_type(_eval_text(val, fstrings=True)) if evaluate else val
    if evaluate:
        val = _eval_text(val, fstrings=False)
    if isinstance(val, bool):
        return "yes" if val else "no"
    try:
        val = float(val)
    except (TypeError, ValueError):
        return val
    try:
        return int(val) if int(val) == val else val
    except (ValueError, ArithmeticError):
        return val


def _assert_inert(path):
    """Every cell is an empty cell or a plain number that both versions store and read
    back as that number, with or without evaluation."""
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    assert len(rows) > 1, f"{path}: no trials"
    for row in rows[1:]:
        for cell in row:
            assert cell == "" or PLAIN_NUMBER.match(cell), f"{path}: {cell!r}"
            for version in ("3.3", "4.x"):
                stored = loop_value(version, cell)
                for evaluate in (True, False):
                    got = read_value(version, stored, evaluate)
                    if cell == "":
                        assert got == "", f"{path}: an empty cell read back as {got!r}"
                    else:
                        assert type(got) in (int, float) and got == float(cell), (
                            f"{path}: {cell!r} read back as {got!r} in {version}")


def test_the_emulation_flags_what_opensesame_alters():
    # The emulation must see what the verification of OpenSesame's own classes saw, or
    # a test that relies on it proves nothing.
    for cell in ("{__import__('os').getpid()}", "The report {was} detailed."):
        with pytest.raises(Altered):
            loop_value("4.x", cell)
        assert read_value("3.3", loop_value("3.3", cell)) == cell   # braces are inert in 3.3
    for cell in ("=1+1", "[=1+1]"):
        for version in ("3.3", "4.x"):
            with pytest.raises(Altered):
                read_value(version, loop_value(version, cell))
    with pytest.raises(Altered):
        read_value("3.3", loop_value("3.3", "[name]"))
    assert read_value("4.x", loop_value("4.x", "007")) == 7
    assert read_value("4.x", loop_value("4.x", "True")) == 1
    with pytest.raises(ValueError):
        read_value("4.x", loop_value("4.x", "nan"))           # stops a 4.x session
    with pytest.raises(OverflowError):
        read_value("4.x", loop_value("4.x", "infinity"))
    # A timeout: 4.x stores None, which an evaluated read turns into 'None', and 3.3
    # stores the string 'None' (response_store.add in both versions).
    assert read_value("4.x", None) == "None"
    assert read_value("4.x", None, evaluate=False) is None
    assert read_value("3.3", "None", evaluate=False) == "None"


def test_every_shipped_loop_table_is_inert_in_both_opensesame_versions():
    folder = repo_path("output", "experiments")
    paths = sorted(glob.glob(os.path.join(folder, "*_opensesame.csv")))
    assert paths, f"no OpenSesame loop tables under {folder}"
    for path in paths:
        _assert_inert(path)


# ---- Running the generated scripts under each version's rules --------------------------

# Presented text OpenSesame would run or retype if it reached a loop cell.
HOSTILE = ["{__import__('os').getpid()}", "[=1+1]", "=1+1", "[name]", "infinity", "nan",
           "True", "007", "The report {was} detailed."]


def _hostile_stim():
    n = len(HOSTILE)
    return assign_triggers(pd.DataFrame({
        "word": HOSTILE,
        "sentence": ["The|report|{was}|detailed."] + [f"Region|{w}|ends." for w in HOSTILE[1:]],
        "question": [f"Was it {w}?" for w in HOSTILE],
        "condition": ["a", "b"] * 4 + ["a"], "set": list(range(1, n + 1)), "list": [1] * n,
        "trial": list(range(1, n + 1)), "critical_region": [2] * n,
        "answer": ["f", "j"] * 4 + ["f"], "iti_ms": [400 + 25 * i for i in range(n)],
    }))


def _hostile_design():
    return {"name": "hostile", "language": "english", "events": [
        {"type": "fixation", "content": "+", "duration_ms": 500},
        {"type": "text", "content": "{word}", "duration_ms": 300, "trigger": "condition"},
        {"type": "response", "keys": ["f", "j"], "timeout_ms": 2000},
        {"type": "feedback", "answer": "answer", "duration_ms": 600},
        {"type": "region_by_region", "content": "{sentence}", "critical_region_trigger": "item"},
        {"type": "question", "content": "{question}", "keys": ["f", "j"], "timeout_ms": 4000},
        {"type": "blank", "duration": {"from_column": "iti_ms"}},
    ]}


def _items(osexp):
    """The .osexp's items by name: type, inline-script code by phase, other lines."""
    items, name, phase = {}, None, None
    for line in osexp.splitlines():
        m = re.match(r"define (\S+) (\S+)$", line)
        if m:
            name, phase = m.group(2), None
            items[name] = {"type": m.group(1), "___prepare__": [], "___run__": [], "lines": []}
        elif name is not None and line.startswith("\t"):
            body = line[1:]
            if body in ("___prepare__", "___run__"):
                phase = body
            elif body == "__end__":
                phase = None
            else:
                items[name][phase or "lines"].append(body)
    return items


def _sequence(items, name):
    """The items a sequence runs, in order."""
    return [line.split()[1] for line in items[name]["lines"] if line.startswith("run ")]


# A keyword left out of a call, as opposed to one given as None.
_OWN = object()


def _run(osexp_path, version, responses, hz=None):
    """Run a generated experiment's scripts against stand-ins for OpenSesame's runtime,
    with `version`'s variable store, and return what each item showed, sent, slept and
    logged.

    The experiment runs as OpenSesame runs it (libopensesame/sequence.py and loop.py in
    3.3.14 and 4.1.20): a sequence prepares every item it holds before it runs any, and
    each cycle of the loop sets the trial's variables and then prepares and runs the
    trial sequence. Of the items around the loop, the trigger setup and the two session
    markers run. A check or a screen that waits for a key at start-up is left out,
    since this run sets no subject number and presses no key before the trials.
    OpenSesame 4 runs inline scripts in the variable store itself, so every loop column
    is also a global there; 3.3 keeps a separate workspace.

    Time is kept in milliseconds. Without `hz`, show() returns the time at once, and
    the clock advances only with each sleep and each wait for a key. With `hz`, the
    display refreshes every 1000 / hz ms: show() takes half a millisecond to draw and
    then waits for the next refresh, as the xpyriment backend's blocking flip does, and
    the clock reads and sleeps in whole milliseconds, as the legacy clock the generated
    experiment selects does (pygame's get_ticks() and delay(int(ms))). Building a
    canvas and drawing text on it each take a millisecond, so a canvas built while a
    sequence runs delays what follows it. The trigger device is the setup's test-mode
    printer, whose time.sleep() advances the clock.

    `responses` gives the participant's press in each response window, in order: a
    (key, ms) pair, the key pressed that many milliseconds after the window opened, or
    None for no press. A window opens when a script flushes its keyboard or first asks
    it for a key, and at each keyboard_response. The self-paced reading regions take no
    entry: each is advanced with the space bar 300 ms after it appears.

    Returns (shown, sent, slept, logged). `shown` holds (item, text, time) for each text
    on each canvas shown, text None for a blank canvas, and `sent` holds (item, code,
    time) for each code written to the port, at the time of the display. `slept` holds
    (item, ms) for each sleep. Each logger run adds a copy of the variable store to
    `logged`, read as the CSV logger reads it, without evaluation, and without the
    names beginning with an underscore that OpenSesame 4's logger leaves out."""
    folder = os.path.dirname(osexp_path)
    with open(osexp_path, encoding="utf-8") as handle:
        items = _items(handle.read())
    store, shown, sent, slept, logged = {}, [], [], [], []
    responses = iter(responses)
    current = [None]
    now = [0.0]

    def ticks():
        return now[0] if hz is None else float(math.floor(now[0] + 1e-9))

    def cost(ms):
        if hz is not None:
            now[0] += ms

    class Var:
        def __getattr__(self, name):
            return self.get(name)

        def __setattr__(self, name, value):
            store[name] = value

        def get(self, name, default=None, _eval=True):
            if name in store:
                val = store[name]
            elif default is not None:
                val = default
            else:
                raise KeyError(f"OpenSesame has no variable '{name}'")
            return read_value(version, val, _eval)

    class Canvas:
        def __init__(self, *args, **kwargs):
            self.texts = []
            cost(1.0)

        def text(self, text, *args, **kwargs):
            self.texts.append(text)
            cost(1.0)

        def show(self):
            if hz is not None:
                frame = 1000.0 / hz
                now[0] = (math.floor((now[0] + 0.5) / frame - 1e-9) + 1) * frame
            for text in self.texts or [None]:
                shown.append((current[0], text, now[0]))
            return ticks()

    class Keyboard:
        def __init__(self, keylist=None, timeout=None):
            self.keylist, self.timeout, self.opened = keylist, timeout, None

        def flush(self):
            # A response window opens, with the participant's press in it, if any.
            self.press = (("space", 300.0) if self.keylist == ["space"]
                          else next(responses))
            self.opened = now[0]

        def get_key(self, timeout=_OWN, **kwargs):
            # A timeout given in the call holds for that call, None included, and the
            # keyboard's own applies when none is given (openexp.backend.configurable).
            if self.opened is None:
                self.flush()
            timeout = self.timeout if timeout is _OWN else timeout
            # The legacy keyboard polls pygame's whole-millisecond ticks from the call.
            start = ticks()
            limit = float("inf") if timeout is None else (
                start + (timeout if hz is None else math.ceil(timeout)))
            if self.press is not None and self.opened + self.press[1] <= limit:
                now[0] = max(now[0], self.opened + self.press[1])
                key, self.press = self.press[0], None
                return key, ticks()
            now[0] = max(now[0], limit)
            return None, ticks()

    class Clock:
        def time(self):
            return ticks()

        def sleep(self, ms):
            slept.append((current[0], ms))
            now[0] += float(ms) if hz is None else float(max(0, int(ms)))

    def time_sleep(seconds):
        now[0] += seconds * 1000.0

    workspace = store if version == "4.x" else {}
    workspace.update(var=Var(), pool={f: os.path.join(folder, f) for f in os.listdir(folder)},
                     Canvas=Canvas, Keyboard=Keyboard, clock=Clock())
    source = re.search(r'set source_file "(.+)"', "\n".join(items["lexsync_loop"]["lines"]))
    with open(os.path.join(folder, source.group(1)), newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    top = [name for name in _sequence(items, "lexsync_experiment")
           if name in ("lexsync_trigger_setup", "lexsync_session_start", "lexsync_loop",
                       "lexsync_session_end")]

    def prepare(names):
        for name in names:
            current[0] = name
            if items[name]["type"] == "inline_script":
                exec("\n".join(items[name]["___prepare__"]), workspace)

    def run(names):
        for name in names:
            current[0] = name
            kind = items[name]["type"]
            if kind == "inline_script":
                exec("\n".join(items[name]["___run__"]), workspace)
            elif kind == "loop":
                for row in rows:
                    for column, cell in row.items():
                        store[column] = loop_value(version, cell)
                    prepare(_sequence(items, "lexsync_trial"))
                    run(_sequence(items, "lexsync_trial"))
            elif kind == "logger":
                assert "set auto_log yes" in items[name]["lines"]
                logged.append({k: read_value(version, v, False) for k, v in store.items()
                               if not k.startswith("_")})
            else:
                # keyboard_response: response_store.add stores syntax.sanitize(key),
                # which 4.x then auto-types, so a timeout is None there and 'None' in 3.3.
                # The item times its response from its own onset.
                assert kind == "keyboard_response"
                press = next(responses)
                key = None if press is None else press[0]
                raw = "None" if key is None else key
                store["response"] = (_auto_type(raw, allow_bool=True, allow_none=True)
                                     if version == "4.x" else raw)
                timeout = float(next(line.split()[2] for line in items[name]["lines"]
                                     if line.startswith("set timeout ")))
                store["response_time"] = timeout if press is None else press[1]
                now[0] += store["response_time"]

    with (mock.patch("time.sleep", time_sleep) if hz is not None
          else contextlib.nullcontext()):
        prepare(top)
        # The setup has opened the trigger device. Each write to it is recorded with
        # the time of the display, and still made, so that a write that blocks shows.
        device = workspace["send_trigger"]

        def send_trigger(code):
            sent.append((current[0], code, now[0]))
            device(code)

        workspace["send_trigger"] = send_trigger
        run(top)
    return shown, sent, slept, logged


def _pulses(sent):
    """Each code written to the port, as (item, code, onset, width, truncated).

    A code lasts until the next write. It is truncated when that write is a 0 that the
    next code follows at the same moment, which is how a new onset ends a code still
    held. A write of 0 starts no pulse."""
    out = []
    for i, (item, code, t) in enumerate(sent):
        if code == 0:
            continue
        end = next(((c, s) for _, c, s in sent[i + 1:]), None)
        assert end is not None, f"code {code} from {item} was never reset"
        truncated = (end[0] == 0 and i + 2 < len(sent) and sent[i + 2][1] != 0
                     and sent[i + 2][2] == end[1])
        out.append((item, code, t, end[1] - t, truncated))
    return out


@pytest.mark.parametrize("version", ["3.3", "4.x"])
def test_the_scripts_present_the_text_verbatim_and_score_a_timeout(version, schema,
                                                                    tmp_path, monkeypatch):
    # No port driver: the setup's parallel-port branch fails and it falls back to test
    # mode on any machine, as it does on one without the hardware.
    monkeypatch.setattr(ctypes, "windll", None, raising=False)
    stim = _hostile_stim()
    path = export_opensesame(stim, _hostile_design(), schema, str(tmp_path))
    _assert_inert(tmp_path / "hostile_english_opensesame.csv")
    n = len(stim)
    # Per trial: the response window, opened by the word, then the question. Trial 1
    # times out, trial 2 presses the wrong key and the rest press the right one, each
    # 600 ms after the word appears, which is while the 300 ms word is shown or after.
    pressed = [None, "f"] + list(stim["answer"])[2:]
    responses = [w for key in pressed for w in (None if key is None else (key, 600.0),
                                                  ("f", 400.0))]
    shown, sent, slept, logged = _run(path, version, responses)

    def by(item):
        return [text for name, text, _ in shown if name == item and text is not None]

    # The word and its response window are one item, so the events after it moved up.
    assert by("lexsync_e1") == HOSTILE
    assert by("lexsync_e3") == [r for s in stim["sentence"] for r in s.split("|") if r]
    assert by("lexsync_e4") == list(stim["question"])
    assert by("lexsync_e2") == ["Too slow", "Incorrect"] + ["Correct"] * (n - 2)
    codes = [code for _, code, _ in sent]
    assert codes and all(type(code) is int for code in codes)
    # The interval read from the items is timed from its own onset, and ends half a
    # frame early so that the next display lands on the refresh that ends it. A display
    # that cannot be measured, as this one, is taken to run at the assumed 60 Hz.
    waits = [sum(ms for _, ms in group)
             for name, group in itertools.groupby(slept, key=lambda s: s[0])
             if name == "lexsync_e5"]
    assert waits == pytest.approx([ms - 1000.0 / 60 / 2 for ms in stim["iti_ms"]])
    # The logger wrote a row per trial: the response, timed from the word's onset, with
    # the timeout and the accuracy, each region's reading time and the question.
    assert len(logged) == n
    assert [row["response"] for row in logged] == pressed
    assert [row["response_time"] for row in logged] == [""] + [pytest.approx(600.0)] * (n - 1)
    assert [row["timed_out"] for row in logged] == [1] + [0] * (n - 1)
    assert [row["correct"] for row in logged] == [0, 0] + [1] * (n - 2)
    assert [row["lexsync_region_rts"] for row in logged] == [
        "|".join("300.0" for r in s.split("|") if r) for s in stim["sentence"]]
    assert [(row["question_response"], row["question_rt"]) for row in logged] == [
        ("f", pytest.approx(400.0))] * n
    # The labels the text table holds are copied in for the logger.
    assert [row["lexsync_condition"] for row in logged] == list(stim["condition"])
    assert [row["lexsync_answer"] for row in logged] == list(stim["answer"])
    assert {row["lexsync_block"] for row in logged} == {""}


@pytest.mark.parametrize("version", ["3.3", "4.x"])
def test_the_scripts_show_each_text_in_the_case_its_event_asks_for(version, schema,
                                                                   tmp_path, monkeypatch):
    # A text event's `case` is applied by the script that shows the text, with Python's
    # own case mapping, not by lexsync, whose two engines upper-case 'ß' differently.
    # The forward mask is as many hash marks as the longest string has characters.
    monkeypatch.setattr(ctypes, "windll", None, raising=False)
    stim = assign_triggers(pd.DataFrame({
        "prime": ["Naïveté", "cat"], "target": ["straße", "moon"],
        "condition": ["related", "unrelated"], "set": [1, 2], "trial": [1, 2], "list": 1}))
    design = {"name": "t", "language": "english", "paradigm": "masked_priming"}
    path = export_opensesame(stim, design, schema, str(tmp_path))
    shown, _, _, logged = _run(path, version, [("left", 600.0), None])
    assert [(name, text) for name, text, _ in shown if text is not None] == [
        ("lexsync_e0", "#######"), ("lexsync_e1", "naïveté"), ("lexsync_e2", "STRASSE"),
        ("lexsync_e0", "#######"), ("lexsync_e1", "cat"), ("lexsync_e2", "MOON")]
    # The target stays on until the key or for its whole window: the first trial's key
    # ends it at 600 ms, and the second trial's runs out at 2,000 ms.
    assert [(row["response"], row["timed_out"]) for row in logged] == [("left", 0), (None, 1)]


def _delayed_design():
    return {"name": "delayed", "language": "english", "events": [
        {"type": "fixation", "content": "+", "duration_ms": 500},
        {"type": "text", "content": "{word}", "duration_ms": 300, "trigger": "condition"},
        {"type": "blank", "duration_ms": 200},
        {"type": "response", "keys": ["f", "j"], "timeout_ms": 2000},
        {"type": "feedback", "answer": "answer", "duration_ms": 600},
        {"type": "blank", "duration_ms": 250}]}


@pytest.mark.parametrize("version", ["3.3", "4.x"])
def test_a_delayed_response_is_scored_and_logged(version, schema, tmp_path, monkeypatch):
    # A response after a blank keeps its own window, opened when the stimulus has gone,
    # and a keyboard_response collects it. The script after it records the timeout and
    # the accuracy, which a keyboard_response cannot compute from an answer column.
    monkeypatch.setattr(ctypes, "windll", None, raising=False)
    stim = _hostile_stim()
    path = export_opensesame(stim, _delayed_design(), schema, str(tmp_path))
    n = len(stim)
    pressed = [None, "f"] + list(stim["answer"])[2:]
    shown, _, _, logged = _run(path, version,
                               [None if key is None else (key, 300.0) for key in pressed])
    assert ([text for name, text, _ in shown if name == "lexsync_e4"]
            == ["Too slow", "Incorrect"] + ["Correct"] * (n - 2))
    assert [row["timed_out"] for row in logged] == [1] + [0] * (n - 1)
    assert [row["correct"] for row in logged] == [0, 0] + [1] * (n - 2)
    assert [row["response_time"] for row in logged] == [""] + [300.0] * (n - 1)


def _trial_runs(lines):
    """The items the trial sequence runs, in order."""
    at = lines.index("define sequence lexsync_trial")
    runs = []
    for line in lines[at + 1:]:
        if not line:
            break
        if line.startswith("\trun "):
            runs.append(line.split()[1])
    return runs


def test_an_onset_locked_response_runs_in_its_stimulus_script(schema, tmp_path):
    # The target and its response window are one inline script, which shows the
    # target, sends its trigger and polls the keyboard through it and then a blank. A
    # keyboard_response flushed every key pressed while the target was on screen and
    # timed the response from the blank that followed it.
    design = {"name": "t", "language": "english", "paradigm": "lexical_decision"}
    lines = open(export_opensesame(_stim().rename(columns={"word": "target"}), design,
                                   schema, str(tmp_path)), encoding="utf-8").read().splitlines()
    assert not any(line.startswith("define keyboard_response") for line in lines)
    assert _trial_runs(lines) == ["lexsync_trial_start", "lexsync_e0", "lexsync_e1",
                                  "lexsync_e2", "lexsync_record", "lexsync_logger"]
    item = _items("\n".join(lines))["lexsync_e1"]
    # The target and the blank after it are built before the trial runs.
    assert item["___prepare__"] == [
        "_lexsync_c_e1 = Canvas()",
        "_lexsync_c_e1.text(_lexsync_row()[u'target'])",
        "_lexsync_c_e1_blank = Canvas()",
    ]
    # The window is timed from the target's onset: the keyboard is polled until half a
    # frame before the target's 800 ms are up, so that the blank lands on the refresh
    # that ends them, and then until 2,000 ms after that.
    assert item["___run__"] == [
        "_t0 = _lexsync_c_e1.show()",
        "var.onset_time = _t0",
        "_lexsync_onset(int(var.get(u'condition_trigger', _eval=False)), _t0)",
        "_kb = Keyboard(keylist=[u'left', u'right'])",
        "_kb.flush()",
        "_key, _t = _lexsync_key(_kb, _t0 + 800 - _LEXSYNC_HALF_FRAME)",
        "if _key is None:",
        "    _lexsync_c_e1_blank.show()",
        "    _key, _t = _lexsync_key(_kb, _t0 + 800 + 2000)",
        "var.response = _key",
        "var.response_time = u'' if _key is None else _t - _t0",
        "var.timed_out = 1 if _key is None else 0",
        "_want = str(_lexsync_row().get(u'answer', u'')).strip()",
        "_got = u'' if _key is None else str(_key).strip()",
        "var.correct = (1 if _got == _want else 0) if _want else u''",
    ]


def _run_instructions(osexp_path, key):
    """Run an experiment's instructions script with `key` pressed, and return the texts it
    showed and the (keylist, timeout) of each keyboard it opened. The script reads no
    variable, so it runs alike in both versions."""
    with open(osexp_path, encoding="utf-8") as handle:
        items = _items(handle.read())
    shown, keyboards = [], []

    class Canvas:
        def text(self, text, *args, **kwargs):
            shown.append(text)

        def show(self):
            return 0.0

    class Keyboard:
        def __init__(self, keylist=None, timeout=None):
            keyboards.append((keylist, timeout))

        def get_key(self, **kwargs):
            return key, 0.0

    exec("\n".join(items["lexsync_instructions"]["___run__"]),
         {"Canvas": Canvas, "Keyboard": Keyboard})
    return shown, keyboards


def test_the_instructions_wait_for_the_space_bar_before_the_loop(schema, tmp_path):
    # The experiment went straight from the trigger setup into the loop. A script now
    # shows the instructions, as text written into it and escaped for OpenSesame's
    # canvas, which reads a subset of HTML, and waits for the space bar.
    design = {"name": "t", "language": "english", "instructions": "Read & press <f>.\nThen j."}
    path = export_opensesame(_stim(), design, schema, str(tmp_path))
    text = open(path, encoding="utf-8").read()
    assert validate_osexp(text)
    runs = [line for line in text.splitlines() if line.startswith("\trun lexsync_")]
    assert runs[-6:] == ["\trun lexsync_trigger_setup always",
                         "\trun lexsync_trigger_notice always",
                         "\trun lexsync_instructions always",
                         "\trun lexsync_session_start always", "\trun lexsync_loop always",
                         "\trun lexsync_session_end always"]
    shown, keyboards = _run_instructions(path, "space")
    assert shown == ["Read &amp; press &lt;f&gt;.<br />Then j.<br /><br />Press the space "
                     "bar to begin."]
    assert keyboards == [(["space", "escape"], None)]
    with pytest.raises(RuntimeError, match="lexsync: stopped at the instructions"):
        _run_instructions(path, "escape")


def test_every_shipped_experiment_shows_its_instructions_before_the_loop():
    folder = repo_path("output", "experiments")
    paths = sorted(glob.glob(os.path.join(folder, "*.osexp")))
    assert paths, f"no OpenSesame experiments under {folder}"
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
        at = lines.index("define sequence lexsync_experiment")
        runs = [line.split()[1] for line in lines[at:] if line.startswith("\trun ")]
        assert runs[-4:] == ["lexsync_instructions", "lexsync_session_start",
                             "lexsync_loop", "lexsync_session_end"], path
        shown, keyboards = _run_instructions(path, "space")
        assert len(shown) == 1 and shown[0].endswith("Press the space bar to begin."), path
        assert keyboards == [(["space", "escape"], None)], path


def test_opensesame_timeouts_are_written_in_whole_milliseconds_as_declared(schema, tmp_path):
    # 1.001 s times 1000 is 1000.9999999999999 in binary floating point, so int() wrote
    # a declared 1,001 ms as 1,000: 95 of the whole-millisecond timeouts from 1 to 10,000
    # came out one short. test-scripting.R pins the same lines.
    delayed = {"name": "d", "language": "english", "events": [
        {"type": "text", "content": "{word}", "duration_ms": 300},
        {"type": "blank", "duration_ms": 100},
        {"type": "response", "keys": ["f", "j"], "timeout_ms": 1001},
        {"type": "question", "content": "{word}", "keys": ["f", "j"], "timeout_ms": 1003}]}
    lines = open(export_opensesame(_stim(), delayed, schema, str(tmp_path)),
                 encoding="utf-8").read().splitlines()
    assert "\tset timeout 1001" in lines
    assert "\t_key, _t = _lexsync_key(_kb, _t0 + 1003)" in lines
    onset = {"name": "o", "language": "english", "events": [
        {"type": "text", "content": "{word}", "duration_ms": 300},
        {"type": "response", "keys": ["f", "j"], "timeout_ms": 1001}]}
    lines = open(export_opensesame(_stim(), onset, schema, str(tmp_path)),
                 encoding="utf-8").read().splitlines()
    assert "\t    _key, _t = _lexsync_key(_kb, _t0 + 300 + 1001)" in lines


def test_every_shipped_experiment_logs_each_trial():
    # OpenSesame logs nothing without a logger item, and no generated experiment had one.
    folder = repo_path("output", "experiments")
    paths = sorted(glob.glob(os.path.join(folder, "*.osexp")))
    assert paths, f"no OpenSesame experiments under {folder}"
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        items = _items(text)
        assert items["lexsync_logger"]["type"] == "logger", path
        assert "set auto_log yes" in items["lexsync_logger"]["lines"], path
        runs = _trial_runs(text.splitlines())
        assert runs[0] == "lexsync_trial_start", path
        assert runs[-2:] == ["lexsync_record", "lexsync_logger"], path
        # Every shipped response follows its target, so none waits for the target to go.
        assert not [name for name, item in items.items()
                    if item["type"] == "keyboard_response"], path


# ---- When each display appears and how long each code is held --------------------------
#
# OpenSesame prepares every item of a sequence before it runs any, and its inline scripts
# share one workspace (libopensesame/sequence.py and inline_script.py, 3.3.14 and 4.1.20).
# The generated scripts built each canvas while the trial ran and slept each event's full
# duration after a blocking 10 ms pulse, the pattern OpenSesame's timing manual shows as
# the way not to time a display. Every event overran: at 60 Hz the 50 ms prime lasted
# about 67 ms and the 83 ms prime-target SOA about 117 ms. The experiment also ignored
# triggers.trigger_hold_ms and sent neither session marker. test-scripting.R pins the
# same generated structure, and the timing itself is run here, on a simulated display.

def _every_event_design():
    """One event of every type: a triggered prime and mask, a target with its response,
    feedback, a sentence region by region, a question, a delayed response and a
    per-trial interval."""
    return {"name": "every", "language": "english", "events": [
        {"type": "fixation", "content": "+", "duration_ms": 500},
        {"type": "text", "content": "{word}", "duration_ms": 50, "trigger": 20},
        {"type": "mask", "content": "#####", "duration_ms": 33},
        {"type": "text", "content": "{word}", "duration_ms": 300, "trigger": "condition"},
        {"type": "response", "keys": ["f", "j"], "timeout_ms": 2000},
        {"type": "feedback", "answer": "answer", "duration_ms": 600},
        {"type": "region_by_region", "content": "{sentence}", "critical_region_trigger": "item"},
        {"type": "question", "content": "{question}", "keys": ["f", "j"], "timeout_ms": 4000},
        {"type": "blank", "duration_ms": 200},
        {"type": "response", "keys": ["f", "j"], "timeout_ms": 1000},
        {"type": "blank", "duration": {"from_column": "iti_ms"}},
    ]}


def _every_event_experiment(schema, tmp_path):
    path = export_opensesame(_hostile_stim(), _every_event_design(), schema, str(tmp_path))
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    return path, _items(text), _trial_runs(text.splitlines())


def test_each_canvas_is_prepared_under_its_own_name(schema, tmp_path):
    _, items, trial = _every_event_experiment(schema, tmp_path)
    prepared = {}
    for name in trial:
        item = items[name]
        if item["type"] != "inline_script":
            continue
        run = "\n".join(item["___run__"])
        # Nothing is built while the trial runs: every canvas a script shows was
        # built in its prepare phase, before the sequence ran its first item.
        assert "Canvas(" not in run, name
        own = {m.group(1) for line in item["___prepare__"]
               for m in [re.match(r"(_lexsync_c_\w+) = ", line)] if m}
        assert set(re.findall(r"\b(_lexsync_c_\w+)\b", run)) <= own, name
        # The workspace is shared, so a canvas is named after its item. A shared name
        # would show, in every item, the canvas the sequence prepared last.
        suffix = "_lexsync_c_" + name[len("lexsync_"):]
        assert all(n == suffix or n.startswith(suffix + "_") for n in own), name
        prepared[name] = own
    names = [n for own in prepared.values() for n in own]
    assert len(names) == len(set(names))
    assert sorted(name for name, own in prepared.items() if own) == [
        "lexsync_e0", "lexsync_e1", "lexsync_e2", "lexsync_e3", "lexsync_e4", "lexsync_e5",
        "lexsync_e6", "lexsync_e7", "lexsync_e8_blank", "lexsync_e9"]


def test_no_event_sleeps_its_full_duration_after_a_trigger(schema, tmp_path):
    _, items, trial = _every_event_experiment(schema, tmp_path)
    for name in trial:
        run = items[name]["___run__"]
        # Every wait is timed from an onset through the setup's helpers, which also
        # reset the code when its hold is up. No script sleeps or writes to the port.
        assert not any("clock.sleep" in line or "send_trigger(" in line for line in run), name
    # A timed event shows its canvas, sends its code and waits until half a frame
    # before its end, measured from its onset, so that the next display lands on the
    # refresh that ends it.
    assert items["lexsync_e1"]["___run__"] == [
        "_t0 = _lexsync_c_e1.show()", "var.onset_time = _t0", "_lexsync_onset(20, _t0)",
        "_lexsync_wait(_t0 + 50 - _LEXSYNC_HALF_FRAME)"]
    assert items["lexsync_e2"]["___run__"] == [
        "_t0 = _lexsync_c_e2.show()", "var.onset_time = _t0",
        "_lexsync_wait(_t0 + 33 - _LEXSYNC_HALF_FRAME)"]
    assert items["lexsync_e9"]["___run__"][-1] == (
        "_lexsync_wait(_t0 + int(float(var.get(u'iti_ms', _eval=False))) "
        "- _LEXSYNC_HALF_FRAME)")
    # The trigger device writes a code and returns.
    setup = items["lexsync_trigger_setup"]["___prepare__"]
    assert not any("time.sleep" in line for line in setup)


def test_the_session_markers_are_sent_and_held(schema, tmp_path):
    _, items, _ = _every_event_experiment(schema, tmp_path)
    # The setup runs first, and the markers enclose the loop: 254 just before it and 255
    # just after it, whatever the experiment shows before the trials.
    sequence = _sequence(items, "lexsync_experiment")
    loop = sequence.index("lexsync_loop")
    assert sequence[0] == "lexsync_trigger_setup"
    assert sequence[loop - 1:] == ["lexsync_session_start", "lexsync_loop",
                                   "lexsync_session_end"]
    assert items["lexsync_session_start"]["___run__"] == ["_lexsync_marker(254)"]
    assert items["lexsync_session_end"]["___run__"] == ["_lexsync_marker(255)"]
    setup = items["lexsync_trigger_setup"]["___prepare__"]
    # The hold is the schema's, and the frame period falls back to the assumed rate.
    assert "_LEXSYNC_HOLD = 50" in setup
    assert "    _LEXSYNC_FRAME = 1000.0 / 60" in setup
    # A hold below the 10 ms most recorders need is raised to it.
    short = dict(schema, triggers=dict(schema.get("triggers") or {}, trigger_hold_ms=4),
                 presentation=dict(schema.get("presentation") or {}, assumed_refresh_hz=144))
    path = export_opensesame(_stim(), {"name": "s", "language": "english"}, short,
                             str(tmp_path))
    with open(path, encoding="utf-8") as handle:
        setup = _items(handle.read())["lexsync_trigger_setup"]["___prepare__"]
    assert "_LEXSYNC_HOLD = 10" in setup
    assert "    _LEXSYNC_FRAME = 1000.0 / 144" in setup


@pytest.mark.parametrize("hz", [60, 120, 144])
def test_the_priming_soa_holds_at_60_120_and_144_hz(hz, monkeypatch):
    # The shipped priming experiment, run on a display that refreshes at `hz`: the prime
    # and the mask last the flips the PsychoPy script gives them, so the SOA is 83.3 ms
    # at all three rates, and every code is held for the schema's 50 ms. It used to be
    # 116.7 ms at 60 Hz and 108.3 ms at 120 Hz.
    monkeypatch.setattr(ctypes, "windll", None, raising=False)
    path = repo_path("output", "experiments", "en_priming_english_list1.osexp")
    with open(str(path)[:-len(".osexp")] + "_opensesame.csv", encoding="utf-8") as handle:
        n = len(handle.read().splitlines()) - 1
    shown, sent, _, logged = _run(str(path), "4.x", [("left", 600.0)] * n, hz=hz)
    frame = 1000.0 / hz
    onsets = {name: [t for item, _, t in shown if item == name]
              for name in ("lexsync_e1", "lexsync_e2", "lexsync_e3")}
    assert len(onsets["lexsync_e1"]) == n
    for prime, mask, target in zip(*onsets.values(), strict=True):
        assert mask - prime == pytest.approx(round(50 * hz / 1000) * frame, abs=1e-6)
        assert target - mask == pytest.approx(round(33 * hz / 1000) * frame, abs=1e-6)
        assert abs(target - prime - 250.0 / 3) < frame
    pulses = _pulses(sent)
    assert pulses[0][1] == 254 and pulses[-1][1] == 255
    assert [code for _, code, *_ in pulses[1:-1]] == [
        c for row in logged for c in (20, int(row["condition_trigger"]))]
    for item, code, _, width, truncated in pulses:
        # To the millisecond the legacy clock counts.
        assert not truncated and abs(width - 50.0) <= 1.0, (item, code, width)
    # The experiment logs the frame period it measured: the median of 20 intervals in
    # the legacy clock's whole milliseconds, 17 at 60 Hz, 8 at 120 and 7 at 144.
    assert {row["lexsync_frame_ms"] for row in logged} == {float(round(frame))}


def test_a_code_is_held_past_a_short_event_and_an_early_key(schema, tmp_path, monkeypatch):
    # A 17 ms prime is one flip at 60 Hz, and its code is held for the 50 ms hold
    # through the mask after it, where the old script cleared it after 10 ms whatever
    # the hold. A key 20 ms into the target ends the target, and its code is still held
    # for the hold, through the blank that follows.
    monkeypatch.setattr(ctypes, "windll", None, raising=False)
    design = {"name": "short", "language": "english", "events": [
        {"type": "fixation", "content": "+", "duration_ms": 500},
        {"type": "text", "content": "{word}", "duration_ms": 17, "trigger": 20},
        {"type": "mask", "content": "#####", "duration_ms": 100},
        {"type": "text", "content": "{word}", "duration_ms": 800, "trigger": "condition"},
        {"type": "response", "keys": ["f", "j"], "timeout_ms": 2000},
        {"type": "blank", "duration_ms": 250}]}
    stim = _hostile_stim().head(3)
    path = export_opensesame(stim, design, schema, str(tmp_path))
    shown, sent, _, logged = _run(path, "4.x", [("f", 20.0)] * len(stim), hz=60)
    pulses = _pulses(sent)
    trial_codes = pulses[1:-1]
    assert [code for _, code, *_ in trial_codes] == [
        c for row in logged for c in (20, int(row["condition_trigger"]))]
    for item, code, _, width, truncated in trial_codes:
        assert not truncated and abs(width - 50.0) <= 1.0, (item, code, width)
    # Each code is reset in the event after the one that sent it.
    resets = [item for item, code, _ in sent if code == 0]
    assert resets == ["lexsync_session_start"] + ["lexsync_e2", "lexsync_e4"] * len(stim) + [
        "lexsync_session_end"]
    # The prime still lasted its one flip and the mask its six.
    for prime, mask in zip([t for item, _, t in shown if item == "lexsync_e1"],
                           [t for item, _, t in shown if item == "lexsync_e2"], strict=True):
        assert mask - prime == pytest.approx(1000.0 / 60)


def test_a_key_window_resets_a_code_whose_hold_ends_with_it(schema, tmp_path, monkeypatch):
    # At 120 Hz the legacy clock measures the frame as 8 ms, so a 54 ms target that
    # collects its own response polls the keyboard until 50 ms after its onset, the
    # moment its 50 ms hold ends. _lexsync_wait() resets a code whose hold ends with its
    # wait, and _lexsync_key() must do the same. It reset the code only once its hold had
    # ended before the window did, so here the code stayed on the port until the blank
    # appeared, 58.3 ms after the onset. test-scripting.R pins the same comparison.
    monkeypatch.setattr(ctypes, "windll", None, raising=False)
    design = {"name": "edge", "language": "english", "events": [
        {"type": "fixation", "content": "+", "duration_ms": 500},
        {"type": "text", "content": "{word}", "duration_ms": 54, "trigger": "condition"},
        {"type": "response", "keys": ["f", "j"], "timeout_ms": 2000},
        {"type": "blank", "duration_ms": 250}]}
    stim = _hostile_stim().head(3)
    path = export_opensesame(stim, design, schema, str(tmp_path))
    with open(path, encoding="utf-8") as handle:
        setup = _items(handle.read())["lexsync_trigger_setup"]["___prepare__"]
    assert ("    if _lexsync_due[0] is not None and (t is None or _lexsync_due[0] <= t):"
            in setup)
    _, sent, _, logged = _run(path, "4.x", [("f", 600.0)] * len(stim), hz=120)
    assert {row["lexsync_frame_ms"] for row in logged} == {8.0}
    trial_codes = _pulses(sent)[1:-1]
    assert [code for _, code, *_ in trial_codes] == [
        int(row["condition_trigger"]) for row in logged]
    for item, code, _, width, truncated in trial_codes:
        assert not truncated and abs(width - 50.0) <= 1.0, (item, code, width)


# ---- The trigger device, and what happens without it ----------------------------------
#
# The setup set var.trigger_backend to parallel on the line before the branch that would
# have opened a serial device, so that branch ran only once the script was edited by
# hand. It then took the first serial port it found. When the port could not be
# opened, the experiment printed one line and ran on without a single code. The schema's
# triggers.mode now decides, the trial log records the outcome as lexsync_trigger_mode,
# and a notice tells the experimenter before the trials. test-scripting.R pins the same
# lines.

def _with(schema, section, **settings):
    """The schema with `settings` added to its `section`."""
    return dict(schema, **{section: dict(schema.get(section) or {}, **settings)})


def _driver(monkeypatch):
    """A stand-in for the dlportio driver, which records each write as (address, code)."""
    writes = []
    port = types.SimpleNamespace(
        DlPortWritePortUchar=lambda address, code: writes.append((address, code)))
    monkeypatch.setattr(ctypes, "windll", types.SimpleNamespace(dlportio=port),
                        raising=False)
    return writes


def _setup(path):
    with open(path, encoding="utf-8") as handle:
        return _items(handle.read())["lexsync_trigger_setup"]["___prepare__"]


@pytest.mark.parametrize("version", ["3.3", "4.x"])
def test_the_trigger_mode_is_logged_with_every_trial(version, schema, tmp_path, monkeypatch):
    # Without the driver, the default mode, auto, prints the codes instead, and every row
    # of the log says so.
    monkeypatch.setattr(ctypes, "windll", None, raising=False)
    path = export_opensesame(_stim(), {"name": "t", "language": "english"}, schema,
                             str(tmp_path))
    _, sent, _, logged = _run(path, version, [None, None])
    assert sent
    assert [(row["lexsync_trigger_mode"], row["test_mode"]) for row in logged] == [
        ("mock", "yes")] * 2
    # With the driver, the codes go to the port at the schema's address, which opens
    # with a 0.
    writes = _driver(monkeypatch)
    _, sent, _, logged = _run(path, version, [None, None])
    assert [(row["lexsync_trigger_mode"], row["test_mode"]) for row in logged] == [
        ("hardware", "no")] * 2
    assert writes[0] == (0x0378, 0)
    assert writes[1:] == [(0x0378, code) for _, code, _ in sent]


def test_hardware_mode_stops_at_the_setup_without_the_port(schema, tmp_path, monkeypatch):
    monkeypatch.setattr(ctypes, "windll", None, raising=False)
    path = export_opensesame(_stim(), {"name": "t", "language": "english"},
                             _with(schema, "triggers", mode="hardware"), str(tmp_path))
    with pytest.raises(RuntimeError) as stop:
        _run(path, "4.x", [None, None])
    message = str(stop.value)
    assert message.startswith("lexsync: the parallel port at 0x0378 could not be opened "
                              "(AttributeError: ")
    assert message.endswith("). triggers.mode is hardware, so the experiment does not run "
                            "without it.")
    writes = _driver(monkeypatch)
    _, _, _, logged = _run(path, "4.x", [None, None])
    assert writes and {row["lexsync_trigger_mode"] for row in logged} == {"hardware"}


def test_mock_mode_never_touches_the_port(schema, tmp_path, monkeypatch):
    writes = _driver(monkeypatch)
    path = export_opensesame(_stim(), {"name": "t", "language": "english"},
                             _with(schema, "triggers", mode="mock"), str(tmp_path))
    _, sent, _, logged = _run(path, "4.x", [None, None])
    assert sent and writes == []
    assert {row["lexsync_trigger_mode"] for row in logged} == {"mock"}


def test_a_serial_backend_opens_the_port_the_schema_names(schema, tmp_path, monkeypatch):
    opened, writes = [], []
    serial = types.ModuleType("serial")

    class Serial:
        def __init__(self, port=None, baudrate=9600, **kwargs):
            opened.append((port, baudrate))

        def write(self, data):
            writes.append(bytes(data))

    serial.Serial = Serial
    monkeypatch.setitem(sys.modules, "serial", serial)
    path = export_opensesame(_stim(), {"name": "t", "language": "english"},
                             _with(schema, "triggers", backend="serial", serial_port="COM7",
                                   baudrate=57600), str(tmp_path))
    setup = _setup(path)
    # The named port, never the first one found, and no parallel-port code.
    assert "        _sp = serial.Serial(u'COM7', 57600)" in setup
    assert not any("comports" in line or "dlportio" in line for line in setup)
    _, sent, _, logged = _run(path, "4.x", [None, None])
    assert opened == [("COM7", 57600)]
    assert writes == [b"\x00"] + [bytes([code]) for _, code, _ in sent]
    assert {(row["lexsync_trigger_mode"], row["trigger_backend"]) for row in logged} == {
        ("hardware", "serial")}


def _run_notice(osexp_path, no_codes, key):
    """Run an experiment's trigger notice after a setup that found `no_codes`, the reason
    no codes will be sent or None, with `key` pressed, and return the texts it showed and
    the (keylist, timeout) of each keyboard it opened."""
    with open(osexp_path, encoding="utf-8") as handle:
        items = _items(handle.read())
    shown, keyboards = [], []

    class Canvas:
        def text(self, text, *args, **kwargs):
            shown.append(text)

        def show(self):
            return 0.0

    class Keyboard:
        def __init__(self, keylist=None, timeout=None):
            keyboards.append((keylist, timeout))

        def get_key(self, **kwargs):
            return key, 0.0

    exec("\n".join(items["lexsync_trigger_notice"]["___run__"]),
         {"Canvas": Canvas, "Keyboard": Keyboard, "_lexsync_no_codes": no_codes})
    return shown, keyboards


def test_the_experimenter_is_told_when_no_codes_will_be_sent(schema, tmp_path):
    path = export_opensesame(_stim(), {"name": "t", "language": "english"}, schema,
                             str(tmp_path))
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    assert validate_osexp(text)
    # Right after the setup, before any screen the participant sees.
    assert _sequence(_items(text), "lexsync_experiment")[:2] == [
        "lexsync_trigger_setup", "lexsync_trigger_notice"]
    why = "the parallel port at 0x0378 could not be opened"
    shown, keyboards = _run_notice(path, why, "c")
    assert shown == [f"No trigger codes will be sent, because {why}. Each code is printed in "
                     "the console instead.<br /><br />Press C to continue without triggers, "
                     "or escape to stop."]
    assert keyboards == [(["c", "escape"], None)]
    with pytest.raises(RuntimeError, match="lexsync: stopped at the trigger notice"):
        _run_notice(path, why, "escape")
    # Nothing is shown when the codes go to the port.
    assert _run_notice(path, None, "c") == ([], [])


# ---- One experiment per counterbalancing version ---------------------------------------

def _two_list_design(schema):
    from lexsync.counterbalancing import counterbalance
    stim = pd.DataFrame({"prime": ["hot", "sky", "sun", "big"],
                         "target": ["cold", "cold", "moon", "moon"],
                         "condition": ["related", "unrelated"] * 2, "set": [1, 1, 2, 2]})
    design = {"name": "t", "language": "english", "paradigm": "priming",
              "counterbalance": {"lists": 2}}
    return assign_triggers(counterbalance(stim, design, schema)), design


def _run_version_check(osexp_path, version, subject_nr, key):
    """Run an experiment's version check under `version`'s variable store, with
    OpenSesame's subject number set and `key` pressed at any prompt, and return the
    texts it showed."""
    with open(osexp_path, encoding="utf-8") as handle:
        items = _items(handle.read())
    store, shown = {"subject_nr": subject_nr}, []

    class Var:
        def __getattr__(self, name):
            return self.get(name)

        def get(self, name, default=None, _eval=True):
            if name in store:
                return read_value(version, store[name], _eval)
            if default is None:
                raise KeyError(f"OpenSesame has no variable '{name}'")
            return default

    class Canvas:
        def text(self, text, *args, **kwargs):
            shown.append(text)

        def show(self):
            return 0.0

    class Keyboard:
        def __init__(self, keylist=None, timeout=None):
            assert key in keylist

        def get_key(self, **kwargs):
            return key, 0.0

    exec("\n".join(items["lexsync_version_check"]["___run__"]),
         {"var": Var(), "Canvas": Canvas, "Keyboard": Keyboard})
    return shown


@pytest.mark.parametrize("version", ["3.3", "4.x"])
def test_each_experiment_warns_when_the_subject_number_belongs_to_another_version(
        version, schema, tmp_path):
    stim, design = _two_list_design(schema)
    export_opensesame(stim, design, schema, str(tmp_path))
    for k in (1, 2):
        path = tmp_path / f"t_english_list{k}.osexp"
        assert validate_osexp(path.read_text(encoding="utf-8"))
        _assert_inert(tmp_path / f"t_english_list{k}_opensesame.csv")
        for subject in (1, 2, 3, 4):
            expected = (subject - 1) % 2 + 1
            shown = _run_version_check(path, version, subject, "space")
            if expected == k:
                assert shown == [], (k, subject)
            else:
                assert shown == [
                    f"Participant {subject} would normally run version {expected}, and "
                    f"this file runs version {k}. Press space to continue with this one "
                    "or escape to stop."], (k, subject)
        # Escape at the warning stops the session.
        with pytest.raises(RuntimeError, match="lexsync: stopped at the version check"):
            _run_version_check(path, version, 3 - k, "escape")
