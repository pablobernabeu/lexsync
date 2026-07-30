# -*- coding: utf-8 -*-
"""Export finalised, hardware-timed experiment scripts (PsychoPy + OpenSesame).

Mirrors R_workflow/R/scripting.R. Both backends render the same declarative trial
*event* sequence (see paradigms.py), so a new paradigm requires only a
configuration change rather than new backend code. The PsychoPy script reads
stimulus text as data from the
conditions file and interprets an embedded ``EVENTS`` list; the OpenSesame .osexp
is generated block by block. Generation imports neither psychopy nor pyserial: it
only writes text. The .osexp is built line for line identically to the R engine.
"""
from __future__ import annotations

import json
import os
import re

import pandas as pd

from .io_utils import _key_part, hash_int_range, slugify, write_csv_utf8
from .paradigms import content_field, referenced_fields, resolve_events

# Columns always carried in a loop table when present (besides the event fields).
# `block` travels with the trials because the runners need it: it is what an event's
# `blocks:` restriction is matched against, and what a runner watches to know a block
# boundary has been reached. Absent unless the design declares a practice or filler
# block, so no existing loop table gains a column.
_STD_COLS = ["trial", "list", "block", "set", "condition", "critical_region", "answer",
             "condition_trigger", "item_trigger"]


def _frames_to_ms(frames, hz) -> int:
    """Frames to milliseconds at a given refresh rate.

    Multiplication comes first so both engines evaluate the same two IEEE-754
    operations on the same doubles: ``frames * 1000 / hz``, never
    ``frames * (1000 / hz)``, which is a different computation and agrees with
    the first only by accident of the divisor. Must stay identical to
    frames_to_ms() in R_workflow/R/scripting.R.
    """
    return int(round(float(frames) * 1000 / float(hz)))


def _refresh_hz(schema: dict) -> float:
    """The refresh rate a design's frame counts were authored for.

    Only ever used to convert ``*_frames`` to milliseconds; it is not the rate
    the experiment runs at.
    """
    hz = float((schema or {}).get("presentation", {}).get("assumed_refresh_hz", 60))
    if not (hz > 0):
        raise ValueError("lexsync: presentation.assumed_refresh_hz must be a positive number.")
    return hz


def _trigger_hold_ms(schema: dict) -> float:
    """How long the onset code is held before it is reset to 0, in milliseconds.

    ``reset_after_frames: N`` is still accepted, but converting it needs care: the
    old implementation queued the reset on flip N and callOnFlip runs on the
    FOLLOWING flip, so the code was actually held for N + 1 flip intervals.
    Converting N directly would silently shorten every trigger by one frame, so the
    +1 is part of the compatibility contract, not an off-by-one. Must stay identical
    to .trigger_hold_ms in R_workflow/R/scripting.R.
    """
    triggers = (schema or {}).get("triggers") or {}
    if triggers.get("trigger_hold_ms") is not None:
        ms = float(triggers["trigger_hold_ms"])
    elif triggers.get("reset_after_frames") is not None:
        ms = float(_frames_to_ms(int(triggers["reset_after_frames"]) + 1, _refresh_hz(schema)))
    else:
        ms = 50.0
    if not (ms > 0):
        raise ValueError("lexsync: triggers.trigger_hold_ms must be a positive number.")
    return ms


def _event_ms(ev: dict, override_ms, override_frames, hz, default_frames: int = 1) -> int:
    """Resolve one event's duration to whole milliseconds.

    Milliseconds are canonical; a frame count is accepted for backward
    compatibility and converted at the design's assumed refresh rate. An explicit
    ``duration_ms`` wins over ``duration_frames`` if a design carries both.
    """
    if override_ms is not None:
        return int(override_ms)
    if override_frames is not None:
        return _frames_to_ms(override_frames, hz)
    if ev.get("duration_ms") is not None:
        return int(ev["duration_ms"])
    return _frames_to_ms(ev.get("duration_frames", default_frames), hz)


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
    """A per-condition marker and a per-item marker, both 0-255 EEG codes."""
    stimuli = stimuli.copy()
    conds = list(dict.fromkeys(stimuli["condition"]))
    stimuli["condition_trigger"] = stimuli["condition"].map(lambda c: 101 + conds.index(c))
    sets = sorted(stimuli["set"].unique(), key=lambda s: str(s))
    set_code = {s: 40 + (i % 200) for i, s in enumerate(sets)}
    stimuli["item_trigger"] = stimuli["set"].map(set_code)
    return stimuli


def _trigger_spec(value):
    """Translate a paradigm trigger token to a renderer spec (int or '@column')."""
    if value is None:
        return None
    if value == "condition":
        return "@condition_trigger"
    if value == "item":
        return "@item_trigger"
    return int(value)





def _duration_spec(ev: dict, index: int):
    """A design's per-event ``duration:`` block, if it declares one.

    ``duration: {from_column: soa_ms}``            read per trial from the items
    ``duration: {jitter: [400, 800], as: isi_ms}`` drawn per trial from the hash
    """
    d = ev.get("duration")
    if not isinstance(d, dict):
        return None
    if d.get("from_column") is not None:
        return {"column": str(d["from_column"]), "jitter": None}
    if d.get("jitter") is not None:
        rng = [int(v) for v in d["jitter"]]
        if len(rng) != 2:
            raise ValueError("lexsync: duration jitter must be a two-element range [lo, hi].")
        return {"column": str(d.get("as") or ("event%d_ms" % index)), "jitter": rng}
    raise ValueError("lexsync: a duration block needs either 'from_column' or 'jitter'.")


def resolve_trial_timing(stimuli: pd.DataFrame, design: dict, schema: dict) -> pd.DataFrame:
    """Realise per-trial event durations onto the stimuli table.

    An event may declare a duration that varies from trial to trial, either read
    from an item column or drawn from a range. A drawn value is a pure function of
    the keyed hash, so both engines realise the same milliseconds, and it is
    written into the stimuli table rather than only into the generated script:
    timing that varies is a variable the analysis needs, not presentation detail.
    """
    events = resolve_events(design)
    seed = (schema or {}).get("seed", 1)
    stimuli = stimuli.copy()
    for i, ev in enumerate(events, start=1):
        spec = _duration_spec(ev, i)
        if spec is None or spec["jitter"] is None:
            # from_column reads a column the items already carry; nothing to realise.
            if spec is not None and spec["column"] not in stimuli.columns:
                raise ValueError(
                    "lexsync: event %d reads its duration from column '%s', which the "
                    "items do not have." % (i, spec["column"]))
            continue
        lo, hi = spec["jitter"]
        # The key names the column as well as the trial, so two jittered events in
        # one design draw independently rather than sharing a value.
        lists = stimuli["list"] if "list" in stimuli.columns else [1] * len(stimuli)
        keys = ["|".join([_key_part(seed), "jitter", spec["column"],
                          _key_part(l), _key_part(s), _key_part(c)])
                for l, s, c in zip(lists, stimuli["set"], stimuli["condition"])]
        stimuli[spec["column"]] = [hash_int_range(k, lo, hi) for k in keys]
    return stimuli


def render_events(events: list, timing: dict, hz: float = 60) -> list:
    """Translate paradigm events into backend-neutral rendering dictionaries.

    Content becomes {field} or {text}; triggers become int / '@column'; the design
    ``timing`` overrides the fixation, critical-word and ISI durations.

    Durations are emitted as whole milliseconds (``ms``), the unit every backend
    consumes: OpenSesame and jsPsych schedule it directly, and the PsychoPy script
    converts it back into whole flips against the refresh rate it measures at
    start-up.
    """
    timing = timing or {}
    # A design's timing block was previously read key by key, so a typo such as
    # `fixation_frame` was silently ignored and the event kept a default duration.
    # Reject an unknown key instead: a mistimed experiment is not recoverable
    # after the data are collected. Must list the same names as scripting.R.
    known = ("fixation_ms", "word_ms", "isi_ms",
             "fixation_frames", "word_frames", "isi_frames")
    unknown = sorted(set(timing) - set(known))
    if unknown:
        raise ValueError(
            "lexsync: unknown timing key(s) %s. Known keys: %s."
            % (", ".join("'%s'" % k for k in unknown), ", ".join(known)))
    fix_ms, fix = timing.get("fixation_ms"), timing.get("fixation_frames")
    word_ms, word = timing.get("word_ms"), timing.get("word_frames")
    isi_ms, isi = timing.get("isi_ms"), timing.get("isi_frames")
    out = []
    for i, ev in enumerate(events, start=1):
        t = ev["type"]
        r = {"type": "region" if t == "region_by_region" else t}
        if t in ("fixation", "text", "mask"):
            f = content_field(ev.get("content"))
            if f:
                r["field"] = f
            else:
                r["text"] = str(ev.get("content", ""))
            # The overrides are type-keyed, as before: `fixation_*` reaches every
            # fixation and `word_*` only a text event whose trigger is "condition",
            # which is why a priming prime (trigger 20) keeps its own duration.
            is_word = t == "text" and ev.get("trigger") == "condition"
            spec = _duration_spec(ev, i)
            if spec is not None:
                r["ms_column"] = spec["column"]
            else:
                r["ms"] = _event_ms(
                    ev,
                    fix_ms if t == "fixation" else (word_ms if is_word else None),
                    fix if t == "fixation" else (word if is_word else None),
                    hz,
                )
            spec = _trigger_spec(ev.get("trigger"))
            if spec is not None:
                r["trigger"] = spec
        elif t == "blank":
            spec = _duration_spec(ev, i)
            if spec is not None:
                r["ms_column"] = spec["column"]
            else:
                r["ms"] = _event_ms(ev, isi_ms, isi, hz)
        elif t == "region_by_region":
            r["field"] = content_field(ev.get("content"))
            r["sep"] = ev.get("sep", "|")
            r["key"] = ev.get("advance", "space")
            spec = _trigger_spec(ev.get("critical_region_trigger"))
            if spec is not None:
                r["crit_trigger"] = spec
        elif t == "response":
            r["keys"] = list(ev.get("keys", ["left", "right"]))
            r["timeout"] = round(ev.get("timeout_ms", 2000) / 1000.0, 3)
        elif t == "question":
            r["field"] = content_field(ev.get("content"))
            r["keys"] = list(ev.get("keys", ["f", "j"]))
            r["timeout"] = round(ev.get("timeout_ms", 5000) / 1000.0, 3)
        elif t == "feedback":
            # Feedback compares the key the participant pressed against the key the item
            # says is correct, so `answer` names a loop-table column holding a KEY, not a
            # label: the runner then needs no mapping table and no notion of what the
            # keys mean.
            r["answer"] = str(ev.get("answer", "answer"))
            r["correct"] = str(ev.get("correct", "Correct"))
            r["incorrect"] = str(ev.get("incorrect", "Incorrect"))
            r["no_response"] = str(ev.get("no_response", "Too slow"))
            r["ms"] = _event_ms(ev, None, None, hz, default_frames=36)
        else:
            raise ValueError(f"lexsync: unknown event type '{t}'.")
        # An event may be restricted to named blocks. This is what lets feedback run
        # during practice and nowhere else: the event list is global to the design, so
        # the restriction has to travel with the event and be applied per trial at run
        # time, rather than by generating a second event list.
        if ev.get("blocks"):
            r["blocks"] = [str(b) for b in ev["blocks"]]
        out.append(r)
    return out


def loop_table(stimuli: pd.DataFrame, events: list | None = None) -> pd.DataFrame:
    """Per-trial table carrying exactly the fields the events reference."""
    fields = referenced_fields(events) if events else (["word"] if "word" in stimuli.columns else [])
    # A per-trial duration is read from the loop table at run time, so its column
    # has to travel with the trials rather than staying in the stimuli file.
    ms_cols = []
    for i, ev in enumerate(events or [], start=1):
        s = _duration_spec(ev, i)
        if s is not None and s["column"] not in ms_cols:
            ms_cols.append(s["column"])
    cols = []
    for c in _STD_COLS[:5] + fields + ms_cols + _STD_COLS[5:]:
        if c in stimuli.columns and c not in cols:
            cols.append(c)
    tab = stimuli[cols].copy()
    if "trial" in tab.columns:
        # Stable, as R's order() is: `trial` repeats across lists (and across a
        # resampled design's replicates), and on those ties the rows must keep
        # their incoming order or the two engines write different loop tables.
        tab = tab.sort_values("trial", kind="stable").reset_index(drop=True)
    return tab


def _write_text(text: str, path: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text + "\n")
    return path


def export_psychopy(stimuli, design, schema, outdir, base=None) -> str:
    base = base or slugify(design["name"], design["language"])
    events = resolve_events(design)
    rendered = render_events(events, design.get("timing") or {}, _refresh_hz(schema))
    csv_name = f"{base}_psychopy.csv"
    write_csv_utf8(loop_table(stimuli, events), os.path.join(outdir, csv_name))
    with open(find_template("psychopy/trial_runner_template.py"), encoding="utf-8") as handle:
        tmpl = handle.read()
    triggers = schema.get("triggers") or {}
    presentation = schema.get("presentation") or {}
    subs = {
        "DESIGN": design["name"], "LANGUAGE": design["language"], "CONDITIONS_FILE": csv_name,
        "TRIGGER_ADDRESS": triggers.get("parallel_address", "0x0378"),
        "TRIGGER_HOLD_MS": "%.17g" % _trigger_hold_ms(schema),
        "INTER_TRIGGER_S": triggers.get("inter_trigger_ms", 10) / 1000,
        "WORD_FONT": design.get("font") or presentation.get("font") or "Courier New",
        "FULLSCREEN": "False",
        # The fallback used only when the script cannot measure the display.
        "ASSUMED_REFRESH_HZ": "%.17g" % _refresh_hz(schema),
        "EVENTS_JSON": _json_r(rendered),
    }
    for key, value in subs.items():
        tmpl = tmpl.replace("{{" + key + "}}", str(value))
    return _write_text(tmpl.rstrip("\n"), os.path.join(outdir, f"{base}_psychopy.py"))


def _pyq(s: str) -> str:
    """A safe single-quoted Python u-string literal for embedding in generated code."""
    return "u'" + str(s).replace("\\", "\\\\").replace("'", "\\'") + "'"


def _content_expr(ev: dict) -> str:
    return f"var.{ev['field']}" if "field" in ev else _pyq(ev.get("text", ""))


def _trigger_expr(spec) -> str | None:
    if spec is None:
        return None
    if isinstance(spec, str) and spec.startswith("@"):
        return f"var.{spec[1:]}"
    return str(int(spec))


def _osexp_block_guard(body: list, blocks) -> list:
    """Restrict an inline script's body to the named blocks.

    The guard goes INSIDE the script rather than on the sequence's `run` line.
    OpenSesame does support a run condition, but its syntax and quoting could not be
    verified without the application, and an emitter that generates an experiment nobody
    can open is worse than one that generates a slightly longer script.
    """
    if not blocks:
        return body
    wanted = ", ".join(_pyq(str(b)) for b in blocks)
    return ["if unicode(var.get(u'block', u'main')) in [%s]:" % wanted] +            ["    " + line for line in body]


def _osexp_event_block(name: str, ev: dict) -> tuple:
    """Return (block_lines, run_names) for one rendered event."""
    t = ev["type"]
    blocks = ev.get("blocks")
    if blocks and t == "response":
        # A keyboard_response is not an inline script, so the guard cannot reach it.
        # Saying so beats emitting an experiment that ignores the restriction.
        raise ValueError(
            "lexsync: a `response` event cannot be restricted to blocks on the "
            "OpenSesame target. Restrict a feedback or stimulus event instead.")
    # A fixed duration is a literal; one that varies per trial reads the loop-table
    # column, which OpenSesame exposes on `var`. Must match .osexp_event_block in
    # scripting.R, since the two engines write the same .osexp.
    sleep_arg = ("int(var.%s)" % ev["ms_column"]) if ev.get("ms_column") else str(int(ev.get("ms", 0)))
    if t in ("fixation", "text", "mask", "blank"):
        body = ["c = Canvas()"]
        if t != "blank":
            body.append(f"c.text({_content_expr(ev)})")
        body.append("var.onset_time = c.show()")
        trig = _trigger_expr(ev.get("trigger"))
        if trig is not None:
            body.append(f"send_trigger({trig})")
        body.append(f"clock.sleep({sleep_arg})")
        return (_inline_block(name, "Show stimulus and send onset-aligned trigger",
                              _osexp_block_guard(body, blocks), run=True),
                [name])
    if t == "region":
        trig = _trigger_expr(ev.get("crit_trigger"))
        body = [
            f"_regions = [r for r in var.{ev['field']}.split({_pyq(ev.get('sep', '|'))}) if r != u'']",
            "_crit = int(var.critical_region) if var.get(u'critical_region') is not None else 0",
            f"_kb = Keyboard(keylist=[{_pyq(ev.get('key', 'space'))}], timeout=None)",
            "for _i, _region in enumerate(_regions, start=1):",
            "    c = Canvas(); c.text(_region); c.show()",
        ]
        if trig is not None:
            body.append(f"    if _i == _crit: send_trigger({trig})")
        body.append("    _kb.get_key()")
        return (_inline_block(name, "Self-paced reading region by region",
                              _osexp_block_guard(body, blocks), run=True), [name])
    if t == "question":
        body = [
            f"c = Canvas(); c.text(var.{ev['field']}); c.show()",
            f"_kb = Keyboard(keylist=[{', '.join(_pyq(k) for k in ev.get('keys', ['f', 'j']))}], "
            f"timeout={int(ev.get('timeout', 5) * 1000)})",
            "var.response, var.response_time = _kb.get_key()",
        ]
        return (_inline_block(name, "Comprehension question",
                              _osexp_block_guard(body, blocks), run=True), [name])
    if t == "feedback":
        # `var.response` is set by the keyboard_response above; `var.answer` (or whichever
        # column the event names) holds the KEY that is correct, so scoring is a string
        # comparison. A timeout leaves the response None, which is reported separately
        # because on a timed task it means something different from a wrong key.
        body = [
            "_want = unicode(var.get(u'%s', u'')).strip()" % ev.get("answer", "answer"),
            "_got = var.get(u'response', None)",
            "if _got is None: _msg = %s" % _pyq(ev.get("no_response", "Too slow")),
            "elif unicode(_got).strip() == _want: _msg = %s" % _pyq(ev.get("correct", "Correct")),
            "else: _msg = %s" % _pyq(ev.get("incorrect", "Incorrect")),
            "c = Canvas(); c.text(_msg); c.show()",
            "clock.sleep(%s)" % sleep_arg,
        ]
        return (_inline_block(name, "Practice feedback",
                              _osexp_block_guard(body, blocks), run=True), [name])
    if t == "response":
        keys = ";".join(ev.get("keys", ["left", "right"]))
        # A keyboard_response draws nothing, so the preceding canvas would stay up for
        # the whole response window. Blank it first, so the stimulus offsets at its own
        # duration as it does in the PsychoPy and jsPsych targets.
        block = _inline_block(f"{name}_blank", "Clear the screen for the response window",
                              ["c = Canvas()", "c.show()"], run=True)
        block += [
            f"define keyboard_response {name}",
            "\tset timeout " + str(int(ev.get("timeout", 2) * 1000)),
            "\tset flush yes", "\tset duration keypress",
            '\tset description "Collect a response"',
            f'\tset allowed_responses "{keys}"', "",
        ]
        return (block, [f"{name}_blank", name])
    raise ValueError(f"lexsync: unknown event type '{t}'.")


def _inline_block(name: str, desc: str, body: list, run: bool) -> list:
    tab = ["\t" + b for b in body]
    return [
        f"define inline_script {name}",
        f'\tset description "{desc}"',
        '\tset _prepare ""', "\t___run__", *tab, "\t__end__", "",
    ]


def build_osexp(design: dict, conditions_file: str, schema: dict, rendered: list,
                font: str = "mono") -> str:
    addr = (schema.get("triggers") or {}).get("parallel_address", "0x378")
    design_name, language = design["name"], design["language"]

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

    event_blocks, run_names = [], []
    for i, ev in enumerate(rendered):
        block, names = _osexp_event_block(f"lexsync_e{i}", ev)
        event_blocks.extend(block)
        run_names.extend(names)

    header = [
        "---", "API: 2.1", "OpenSesame: 3.3.14", "Platform: nt", "---",
        "set width 1024", "set uniform_coordinates yes",
        f'set title "lexsync: {design_name} ({language})"',
        "set subject_nr 0", "set start lexsync_experiment",
        "set sound_sample_size -16", "set sound_freq 48000", "set sound_channels 2",
        "set sound_buf_size 1024", "set sampler_backend legacy", "set round_decimals 2",
        "set mouse_backend legacy", "set keyboard_backend legacy", "set height 768",
        "set fullscreen no", "set foreground white", "set font_size 32",
        f"set font_family {font}", 'set description "Generated by lexsync"',
        "set coordinates uniform", "set compensation 0", "set color_backend legacy",
        "set clock_backend legacy", "set canvas_backend xpyriment", "set background black", "",
        "define inline_script lexsync_trigger_setup",
        '\tset description "Open the trigger device with a test-mode fallback"',
        '\tset _run ""', "\t___prepare__", *["\t" + s for s in setup], "\t__end__", "",
    ]
    trial = [
        "define sequence lexsync_trial",
        "\tset flush_keyboard yes",
        '\tset description "One trial: the paradigm event sequence"',
        *[f"\trun {n} always" for n in run_names], "",
        "define loop lexsync_loop",
        f'\tset source_file "{conditions_file}"',
        # Sequential, so the loop presents the seeded trial order the CSV is sorted
        # by; OpenSesame's default (random) would discard it and diverge from the
        # PsychoPy and jsPsych targets.
        "\tset source file", "\tset repeat 1", "\tset order sequential",
        '\tset description "Present each item once"', "\trun lexsync_trial", "",
        "define sequence lexsync_experiment",
        "\tset flush_keyboard yes",
        '\tset description "Top-level experiment sequence"',
        "\trun lexsync_trigger_setup always", "\trun lexsync_loop always", "",
    ]
    return "\n".join(header + event_blocks + trial)


def export_opensesame(stimuli, design, schema, outdir, base=None) -> str:
    base = base or slugify(design["name"], design["language"])
    events = resolve_events(design)
    rendered = render_events(events, design.get("timing") or {}, _refresh_hz(schema))
    csv_name = f"{base}_opensesame.csv"
    write_csv_utf8(loop_table(stimuli, events), os.path.join(outdir, csv_name))
    presentation = schema.get("presentation") or {}
    font = design.get("font") or presentation.get("opensesame_font") or "mono"
    text = build_osexp(design, csv_name, schema, rendered, font=font)
    return _write_text(text, os.path.join(outdir, f"{base}.osexp"))


# BCP 47 tags for the human-readable language labels the designs carry, covering the
# languages the corpus connectors derive lexica for (corpora/fetch_corpora.py).
_BCP47_TAGS = {"english": "en", "spanish": "es", "french": "fr", "german": "de",
               "dutch": "nl", "italian": "it", "portuguese": "pt",
               "chinese": "zh", "chinese (mandarin)": "zh"}
_BCP47_SHAPE = re.compile(r"^[A-Za-z]{2,3}(-[A-Za-z0-9]{1,8})*$")


def _language_tag(design: dict) -> str:
    """The design's BCP 47 tag for the generated HTML ``lang`` attribute.

    ``language`` is a free-text label ("english"), which is not a valid tag, so it is
    mapped. A design may state ``language_tag`` outright, and a label that is already
    tag-shaped ("en", "en-GB") is taken as given. Anything else becomes ``und``
    (BCP 47 "undetermined"): registered, and unlike ``lang="english"`` resolvable.

    Parameters
    ----------
    design : dict
        A parsed design configuration.

    Returns
    -------
    str
        A well-formed BCP 47 language tag.
    """
    tag = design.get("language_tag")
    if tag:
        return str(tag)
    label = str(design.get("language") or "").strip()
    if _BCP47_SHAPE.match(label):
        return label
    return _BCP47_TAGS.get(label.lower(), "und")


# Event-model key names (PsychoPy style) mapped to browser KeyboardEvent keys.
_JSPSYCH_KEYS = {"left": "arrowleft", "right": "arrowright", "up": "arrowup",
                 "down": "arrowdown", "space": " ", "return": "enter"}


def _map_keys_for_jspsych(rendered: list) -> list:
    out = []
    for ev in rendered:
        e = dict(ev)
        if "keys" in e:
            e["keys"] = [_JSPSYCH_KEYS.get(k, k) for k in e["keys"]]
        if "key" in e:
            e["key"] = _JSPSYCH_KEYS.get(e["key"], e["key"])
        out.append(e)
    return out


def _json_r(obj) -> str:
    """Serialise as R's jsonlite::toJSON(auto_unbox = TRUE) does.

    The generated experiment embeds this JSON, so the two engines emit byte-identical
    scripts only if they agree here. jsonlite writes no separator padding and cannot be
    made to, it drops a whole number's fractional part (a 2000 ms timeout becomes 2,
    not 2.0), and it writes non-ASCII text as raw UTF-8 where json.dumps defaults to
    \\uXXXX escapes, so Python is the side that conforms on all three counts.
    """
    def integral(o):
        if isinstance(o, float) and o.is_integer():
            return int(o)
        if isinstance(o, dict):
            # A missing value drops the KEY, as jsonlite does when it serialises a data
            # frame by rows. Without this the two engines' generated experiments differ --
            # and worse, this side emitted a bare NaN into the embedded JSON, which is not
            # valid JSON at all. A trial with no correct answer (a main-block trial in a
            # design whose practice items carry one) genuinely has none, so omitting the
            # field is also the honest rendering.
            return {k: integral(v) for k, v in o.items()
                    if v is not None and not (isinstance(v, float) and v != v)}
        if isinstance(o, list):
            return [integral(v) for v in o]
        return o
    return json.dumps(integral(obj), separators=(",", ":"), ensure_ascii=False)


def _json_html(obj) -> str:
    """JSON safe to embed inside an HTML <script> (escape <, >, & and JS line seps)."""
    return (_json_r(obj).replace("<", "\\u003c").replace(">", "\\u003e")
            .replace("&", "\\u0026").replace(" ", "\\u2028").replace(" ", "\\u2029"))


def export_jspsych(stimuli, design, schema, outdir, base=None) -> str:
    """A browser-runnable jsPsych experiment from the event list.

    The same rendered events and the trial data are embedded in one HTML file, so
    anyone can reproduce the exact procedure online from the same materials. The
    jsPsych library and stylesheet are loaded from a CDN, so the machine running the
    file needs an internet connection; the trial data are embedded and the responses
    are saved locally, so no server is required either to run it or to collect them.
    Onset triggers are recorded in each trial's data (a browser cannot drive a
    parallel port); online EEG synchronisation needs WebSerial/LSL or a photodiode.
    """
    base = base or slugify(design["name"], design["language"])
    events = resolve_events(design)
    rendered = _map_keys_for_jspsych(
        render_events(events, design.get("timing") or {}, _refresh_hz(schema)))
    trials = loop_table(stimuli, events).to_dict(orient="records")
    presentation = schema.get("presentation") or {}
    font = design.get("font") or presentation.get("font") or "Courier New"
    with open(find_template("jspsych/experiment_template.html"), encoding="utf-8") as handle:
        tmpl = handle.read()
    subs = {
        "DESIGN": design["name"], "LANGUAGE": design["language"],
        "LANGUAGE_TAG": _language_tag(design), "WORD_FONT": font,
        "EVENTS_JSON": _json_html(rendered), "TRIALS_JSON": _json_html(trials),
    }
    for k, v in subs.items():
        tmpl = tmpl.replace("{{" + k + "}}", str(v))
    return _write_text(tmpl.rstrip("\n"), os.path.join(outdir, f"{base}.html"))


def export_experiments(stimuli, design, schema, outdir, base=None) -> dict:
    stimuli = assign_triggers(stimuli)
    return {
        "psychopy": export_psychopy(stimuli, design, schema, outdir, base),
        "opensesame": export_opensesame(stimuli, design, schema, outdir, base),
        "jspsych": export_jspsych(stimuli, design, schema, outdir, base),
    }
