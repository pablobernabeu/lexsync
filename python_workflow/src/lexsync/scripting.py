# -*- coding: utf-8 -*-
"""Export finalised, hardware-timed experiment scripts (PsychoPy + OpenSesame).

Mirrors R_workflow/R/scripting.R. The OpenSesame .osexp is built line for line
identically to the R engine. Generation imports neither psychopy nor pyserial:
it only writes text.
"""
from __future__ import annotations

import os

import pandas as pd

from .io_utils import slugify, write_csv_utf8

_LOOP_COLS = ["trial", "list", "word", "condition", "set", "length", "frequency",
              "n_density", "old20", "target_word_trigger", "condition_trigger"]


def find_template(relpath: str) -> str:
    candidates = []
    env = os.environ.get("LEXSYNC_TEMPLATES")
    if env:
        candidates.append(os.path.join(env, relpath))
    candidates.append(os.path.join(os.path.dirname(__file__), "templates", relpath))
    candidates.append(os.path.join("templates", relpath))
    candidates.append(os.path.join("..", "templates", relpath))
    for cand in candidates:
        if cand and os.path.exists(cand):
            return cand
    raise FileNotFoundError(f"lexsync: template '{relpath}' not found.")


def assign_triggers(stimuli: pd.DataFrame) -> pd.DataFrame:
    stimuli = stimuli.copy()
    conds = list(dict.fromkeys(stimuli["condition"]))
    stimuli["condition_trigger"] = stimuli["condition"].map(lambda c: 100 + 1 + conds.index(c))
    uw = list(dict.fromkeys(stimuli["word"]))
    code = {w: 40 + (i % 200) for i, w in enumerate(uw)}
    stimuli["target_word_trigger"] = stimuli["word"].map(code)
    return stimuli


def loop_table(stimuli: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in _LOOP_COLS if c in stimuli.columns]
    tab = stimuli[cols].copy()
    if "trial" in tab.columns:
        tab = tab.sort_values("trial").reset_index(drop=True)
    return tab


def _write_text(text: str, path: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text + "\n")
    return path


def export_psychopy(stimuli, design, schema, outdir, base=None) -> str:
    base = base or slugify(design["name"], design["language"])
    csv_name = f"{base}_psychopy.csv"
    write_csv_utf8(loop_table(stimuli), os.path.join(outdir, csv_name))
    with open(find_template("psychopy/trial_runner_template.py"), encoding="utf-8") as handle:
        tmpl = handle.read()
    timing = design.get("timing") or {}
    triggers = schema.get("triggers") or {}
    subs = {
        "DESIGN": design["name"], "LANGUAGE": design["language"], "CONDITIONS_FILE": csv_name,
        "TRIGGER_ADDRESS": triggers.get("parallel_address", "0x0378"),
        "RESET_AFTER_FRAMES": triggers.get("reset_after_frames", 2),
        "WORD_DURATION_FRAMES": timing.get("word_frames", 30),
        "FIXATION_FRAMES": timing.get("fixation_frames", 30),
        "ISI_FRAMES": timing.get("isi_frames", 15),
        "INTER_TRIGGER_S": triggers.get("inter_trigger_ms", 10) / 1000,
        "FULLSCREEN": "False",
    }
    for key, value in subs.items():
        tmpl = tmpl.replace("{{" + key + "}}", str(value))
    out = os.path.join(outdir, f"{base}_psychopy.py")
    return _write_text(tmpl.rstrip("\n"), out)


def build_osexp(design_name: str, language: str, conditions_file: str, schema: dict) -> str:
    addr = (schema.get("triggers") or {}).get("parallel_address", "0x378")
    def tb(seq):
        if isinstance(seq, str):
            return "\t" + seq
        return ["\t" + s for s in seq]
    setup = [
        "var.trigger_backend = u'parallel'",
        f"var.parallel_port_address = {addr}",
        "var.test_mode = u'no'",
        "import time",
        "def _printer(code):",
        "    print(u'[lexsync test trigger] %d' % int(code))",
        "    time.sleep(0.01)",
        "    print(u'[lexsync test trigger] 0')",
        "send_trigger = _printer",
        "try:",
        "    if var.trigger_backend == u'serial':",
        "        import serial",
        "        import serial.tools.list_ports",
        "        _ports = serial.tools.list_ports.comports()",
        "        if _ports:",
        "            _sp = serial.Serial(_ports[0].device)",
        "            def send_trigger(code):",
        "                _sp.write(int(code).to_bytes(1, 'big'))",
        "                time.sleep(0.01)",
        "                _sp.write((0).to_bytes(1, 'big'))",
        "        else:",
        "            var.test_mode = u'yes'",
        "    else:",
        "        from ctypes import windll",
        "        _io = windll.dlportio",
        "        _addr = int(var.parallel_port_address)",
        "        def send_trigger(code):",
        "            _io.DlPortWritePortUchar(_addr, int(code))",
        "            time.sleep(0.01)",
        "            _io.DlPortWritePortUchar(_addr, 0)",
        "except Exception as _exc:",
        "    var.test_mode = u'yes'",
        "    print(u'lexsync: trigger device unavailable; test mode.')",
        "send_trigger(0)",
    ]
    send = ["send_trigger(var.target_word_trigger)", "send_trigger(var.condition_trigger)"]
    lines = [
        "---", "API: 2.1", "OpenSesame: 3.3.14", "Platform: nt", "---",
        "set width 1024", "set uniform_coordinates yes",
        f'set title "lexsync: {design_name} ({language})"',
        "set subject_nr 0", "set start lexsync_experiment",
        "set sound_sample_size -16", "set sound_freq 48000", "set sound_channels 2",
        "set sound_buf_size 1024", "set sampler_backend legacy", "set round_decimals 2",
        "set mouse_backend legacy", "set keyboard_backend legacy", "set height 768",
        "set fullscreen no", "set foreground white", "set font_size 32",
        "set font_family mono", 'set description "Generated by lexsync"',
        "set coordinates uniform", "set compensation 0", "set color_backend legacy",
        "set clock_backend legacy", "set canvas_backend xpyriment", "set background black", "",
        "define inline_script lexsync_trigger_setup",
        tb('set description "Open the trigger device with a test-mode fallback"'),
        tb('set _run ""'), tb("___prepare__"), *tb(setup), tb("__end__"), "",
        "define sketchpad lexsync_fixation",
        tb("set duration 500"), tb('set description "Fixation cross"'),
        tb('draw textline center=1 color=white font_family=mono font_size=40 html=yes show_if=always text="+" x=0 y=0 z_index=0'), "",
        "define sketchpad lexsync_word",
        tb("set duration 0"),
        tb('set description "Target word; onset trigger sent by the next item"'),
        tb('draw textline center=1 color=white font_family=mono font_size=40 html=yes show_if=always text="[word]" x=0 y=0 z_index=0'), "",
        "define inline_script lexsync_send_triggers",
        tb('set description "Send the onset trigger then the condition marker"'),
        tb('set _prepare ""'), tb("___run__"), *tb(send), tb("__end__"), "",
        "define keyboard_response lexsync_response",
        tb("set timeout 2000"), tb("set flush yes"), tb("set duration keypress"),
        tb('set description "Collect a response"'), tb('set allowed_responses "left;right"'), "",
        "define sequence lexsync_trial",
        tb("set flush_keyboard yes"),
        tb('set description "Fixation, word with onset trigger, response"'),
        tb("run lexsync_fixation always"), tb("run lexsync_word always"),
        tb("run lexsync_send_triggers always"), tb("run lexsync_response always"), "",
        "define loop lexsync_loop",
        tb(f'set source_file "{conditions_file}"'),
        tb("set source file"), tb("set repeat 1"), tb("set order random"),
        tb('set description "Present each stimulus once"'), tb("run lexsync_trial"), "",
        "define sequence lexsync_experiment",
        tb("set flush_keyboard yes"),
        tb('set description "Top-level experiment sequence"'),
        tb("run lexsync_trigger_setup always"), tb("run lexsync_loop always"), "",
    ]
    return "\n".join(lines)


def export_opensesame(stimuli, design, schema, outdir, base=None) -> str:
    base = base or slugify(design["name"], design["language"])
    csv_name = f"{base}_opensesame.csv"
    write_csv_utf8(loop_table(stimuli), os.path.join(outdir, csv_name))
    text = build_osexp(design["name"], design["language"], csv_name, schema)
    return _write_text(text, os.path.join(outdir, f"{base}.osexp"))


def export_experiments(stimuli, design, schema, outdir, base=None) -> dict:
    stimuli = assign_triggers(stimuli)
    return {
        "psychopy": export_psychopy(stimuli, design, schema, outdir, base),
        "opensesame": export_opensesame(stimuli, design, schema, outdir, base),
    }
