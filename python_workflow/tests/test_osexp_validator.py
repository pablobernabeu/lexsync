"""Structural and referential validation of the generated OpenSesame .osexp, and an
emulation of what OpenSesame 3.3 and 4.x do with the cells of its loop table."""
import csv
import ctypes
import glob
import os
import re

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


def _run(osexp_path, version, responses):
    """Run a generated experiment's scripts against stand-ins for OpenSesame's runtime,
    with `version`'s variable store, and return what each item showed and sent.

    OpenSesame 4 runs inline scripts in the variable store itself, so every loop column
    is also a global there; 3.3 keeps a separate workspace. `responses` gives the key
    pressed (None for a timeout) at each keyboard_response and question, in order."""
    folder = os.path.dirname(osexp_path)
    with open(osexp_path, encoding="utf-8") as handle:
        items = _items(handle.read())
    store, shown, sent, slept = {}, [], [], []
    responses = iter(responses)
    current = [None]

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
        def text(self, text, *args, **kwargs):
            shown.append((current[0], text))

        def show(self):
            return 0.0

    class Keyboard:
        def __init__(self, keylist=None, timeout=None):
            self.keylist = keylist

        def get_key(self, **kwargs):
            return ("space" if self.keylist == ["space"] else next(responses)), 0.0

    class Clock:
        def sleep(self, ms):
            slept.append((current[0], ms))

    workspace = store if version == "4.x" else {}
    workspace.update(var=Var(), pool={f: os.path.join(folder, f) for f in os.listdir(folder)},
                     Canvas=Canvas, Keyboard=Keyboard, clock=Clock())
    exec("\n".join(items["lexsync_trigger_setup"]["___prepare__"]), workspace)
    workspace["send_trigger"] = lambda code: sent.append((current[0], code))
    source = re.search(r'set source_file "(.+)"', "\n".join(items["lexsync_loop"]["lines"]))
    order = [l.split()[1] for l in items["lexsync_trial"]["lines"] if l.startswith("run ")]
    with open(os.path.join(folder, source.group(1)), newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for name, cell in row.items():
            store[name] = loop_value(version, cell)
        for name in order:
            current[0] = name
            if items[name]["type"] == "inline_script":
                exec("\n".join(items[name]["___run__"]), workspace)
            else:
                # keyboard_response: response_store.add stores syntax.sanitize(key),
                # which 4.x then auto-types, so a timeout is None there and 'None' in 3.3.
                key = next(responses)
                raw = "None" if key is None else key
                store["response"] = (_auto_type(raw, allow_bool=True, allow_none=True)
                                     if version == "4.x" else raw)
    return shown, sent, slept


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
    # Per trial: the keyboard_response, then the question. Trial 1 times out, trial 2
    # presses the wrong key and the rest press the right one.
    pressed = [None, "f"] + list(stim["answer"])[2:]
    responses = [k for key in pressed for k in (key, "f")]
    shown, sent, slept = _run(path, version, responses)

    def by(item):
        return [text for name, text in shown if name == item]

    assert by("lexsync_e1") == HOSTILE
    assert by("lexsync_e4") == [r for s in stim["sentence"] for r in s.split("|") if r]
    assert by("lexsync_e5") == list(stim["question"])
    assert by("lexsync_e3") == ["Too slow", "Incorrect"] + ["Correct"] * (n - 2)
    codes = [code for _, code in sent]
    assert codes and all(type(code) is int for code in codes)
    assert [ms for name, ms in slept if name == "lexsync_e6"] == list(stim["iti_ms"])
