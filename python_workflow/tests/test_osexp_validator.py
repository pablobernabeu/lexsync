"""Structural and referential validation of the generated OpenSesame .osexp."""
import os
import re

import pandas as pd

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
