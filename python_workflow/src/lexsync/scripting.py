"""Export finalised experiments: hardware-timed PsychoPy and OpenSesame scripts and a jsPsych page.

Mirrors R_workflow/R/scripting.R. All three targets render the same declarative trial
*event* sequence (see paradigms.py), so a new paradigm requires only a
configuration change rather than new backend code. The PsychoPy script reads
stimulus text as data from the
conditions file and interprets an embedded ``EVENTS`` list; the OpenSesame .osexp
is generated block by block. The jsPsych page embeds the events and the trials as
JSON. Generation imports neither psychopy nor pyserial: it only writes text. The
.osexp is built line for line identically to the R engine.
"""
from __future__ import annotations

import json
import math
import numbers
import os
import re

import pandas as pd

from .design import _INT_MAX, _key_name, _require_bool, _shown, design_stem
from .io_utils import (
    _key_part,
    _readr_cell,
    _round_dp,
    clean_column,
    clean_key,
    clean_meta,
    clean_port,
    clean_serial_port,
    hash_int_range,
    write_csv_utf8,
)
from .paradigms import content_field, referenced_fields, resolve_events

# Columns always carried in a loop table when present (besides the event fields).
# `block` travels with the trials because the runners need it: it is what an event's
# `blocks:` restriction is matched against, and what a runner watches to know a block
# boundary has been reached. Absent unless the design declares a practice or filler
# block. `replicate`, present only in a resampled design, is what tells its item
# samples apart, since each is numbered from trial 1 and set 1. The first six are
# written before the event fields.
_STD_COLS = ["trial", "list", "replicate", "block", "set", "condition", "critical_region",
             "answer", "condition_trigger", "item_trigger"]
_LEADING_COLS = 6

# The loop-table columns the OpenSesame target carries as numbers, under the names its
# loop table gives them. OpenSesame evaluates every cell of a loop table. In 4.x, a cell
# holding a single `{` runs as a Python f-string, and in 3.3 a cell starting with `=` or
# holding `[=...]` runs as Python. Both versions retype a cell such as 'nan' or '007'.
# That loop table therefore holds numbers only, and the presented text travels in a
# companion table that the inline scripts read with the csv module. OpenSesame 4 also
# makes every loop column a global of the inline scripts, where `list` and `set` would
# shadow Python's builtins, so those two are renamed and `trial` with them. Must match
# .OS_NUMERIC in scripting.R.
_OS_NUMERIC = {"trial": "lexsync_trial", "list": "lexsync_list", "replicate": "replicate",
               "set": "lexsync_set", "critical_region": "critical_region",
               "condition_trigger": "condition_trigger", "item_trigger": "item_trigger"}
# A plain decimal number, which both OpenSesame versions store and read back as written.
# [0-9], not \d, which in Python also matches the digits of other scripts.
_PLAIN_NUMBER = re.compile(r"\A-?[0-9]+(\.[0-9]+)?\Z")
# A trigger code written as text: digits only, so no sign, space or decimal point.
_DIGITS = re.compile(r"\A[0-9]+\Z")
# The codes item markers are drawn from, 40 to 239. That leaves 1 to 39 for a design's
# own codes, such as the priming paradigm's 20, and keeps clear of the session markers
# 254 and 255.
_ITEM_CODES = range(40, 240)


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

    It converts ``*_frames`` to milliseconds, and the PsychoPy script and the
    OpenSesame setup fall back on it when they cannot measure the display. Otherwise
    it is not the rate the experiment runs at.
    """
    # `or {}`, not a default argument: a schema whose `presentation:` key is present
    # but empty parses to None here and to NULL in R, where `%||% list()` falls back
    # to the default, so both engines answer such a schema with the default rate.
    # isfinite for the reason run_pipeline tests
    # n_per_condition that way: `hz > 0` admits Inf, which R's is.finite() refuses,
    # and _frames_to_ms would then turn every frame count into 0 ms.
    hz = float(((schema or {}).get("presentation") or {}).get("assumed_refresh_hz", 60))
    if not math.isfinite(hz) or hz <= 0:
        raise ValueError("lexsync: presentation.assumed_refresh_hz must be a positive number.")
    return hz


# The shortest hold either laboratory target gives a code, in milliseconds: a pulse
# shorter than this may not register on a recorder at all. The PsychoPy template applies
# the same floor as MIN_TRIGGER_HOLD_MS. Must match .MIN_HOLD_MS in scripting.R.
_MIN_HOLD_MS = 10.0


def _trigger_hold_ms(schema: dict) -> float:
    """How long the onset code is held before it is reset to 0, in milliseconds.

    ``reset_after_frames: N`` is read as a hold of N + 1 flip intervals: the key names
    the flip on which a callOnFlip reset is queued, and callOnFlip runs on the
    FOLLOWING flip. It is converted as N + 1 frames at
    ``presentation.assumed_refresh_hz``, and the +1 is not an off-by-one: converting N
    would shorten every trigger by one frame. Must stay identical to .trigger_hold_ms
    in R_workflow/R/scripting.R.
    """
    triggers = (schema or {}).get("triggers") or {}
    if triggers.get("trigger_hold_ms") is not None:
        ms = float(triggers["trigger_hold_ms"])
    elif triggers.get("reset_after_frames") is not None:
        ms = float(_frames_to_ms(int(triggers["reset_after_frames"]) + 1, _refresh_hz(schema)))
    else:
        ms = 50.0
    # isfinite as well as the sign, mirroring the R twin's is.finite(): `ms > 0`
    # alone admits Inf, which R refuses with this same message.
    if not math.isfinite(ms) or ms <= 0:
        raise ValueError("lexsync: triggers.trigger_hold_ms must be a positive number.")
    return ms


def _whole_number(value, low: int, high: int) -> bool:
    """Whether a setting is a whole number from `low` to `high`, written as 48 or 48.0.

    A boolean is not one, although Python counts True as 1, and neither is text. Must
    match .whole_number in scripting.R."""
    return (not isinstance(value, bool) and isinstance(value, numbers.Real)
            and math.isfinite(value) and value == int(value) and low <= value <= high)


def _fullscreen(schema: dict) -> bool:
    """Whether the PsychoPy script runs full screen, presentation.fullscreen.

    True by default, as PsychoPy advises for frame timing. OpenSesame takes full screen
    from the mode it is launched in. Must match .fullscreen in scripting.R.
    """
    value = ((schema or {}).get("presentation") or {}).get("fullscreen")
    if value is None:
        return True
    return _require_bool(value, "presentation.fullscreen")


def _text_height_px(schema: dict) -> int:
    """The height of the stimulus text in pixels, presentation.text_height_px.

    48 by default, the PsychoPy and jsPsych size, and the size of every text the
    OpenSesame experiment shows, since it sets OpenSesame's font_size. Must match
    .text_height_px in scripting.R.
    """
    value = ((schema or {}).get("presentation") or {}).get("text_height_px")
    if value is None:
        return 48
    if not _whole_number(value, 8, 400):
        raise ValueError("lexsync: presentation.text_height_px must be a whole number of "
                         "pixels from 8 to 400.")
    return int(value)


# The values triggers.mode and triggers.backend take, the default first. Must match
# .TRIGGER_MODES and .TRIGGER_BACKENDS in scripting.R.
_TRIGGER_MODES = ("auto", "hardware", "mock")
_TRIGGER_BACKENDS = ("parallel", "serial")


def _one_of(value, key: str, choices: tuple) -> str:
    """A setting that names one of `choices`, the first when it is absent."""
    if value is None:
        return choices[0]
    if not isinstance(value, str) or value not in choices:
        allowed = ", ".join(choices[:-1]) + " or " + choices[-1]
        raise ValueError(f"lexsync: {key} must be {allowed}, not '{_shown(value)}'.")
    return value


def _trigger_settings(schema: dict) -> dict:
    """The trigger device the laboratory targets write to, and what they do without it.

    ``mode`` is triggers.mode: ``auto`` prints the codes when the device cannot be
    opened and says so before the first trial, ``hardware`` stops instead, and ``mock``
    prints them without trying the device, after the same notice. ``backend`` is
    triggers.backend: the parallel port at triggers.parallel_address, or ``serial``,
    which writes each code as one byte to triggers.serial_port at triggers.baudrate
    (115200 by default). A serial backend must name its port. Taking the first port
    found could send the codes to another device. The port is checked whatever the
    backend, since the PsychoPy script carries it either way. Must match
    .trigger_settings in scripting.R.
    """
    triggers = (schema or {}).get("triggers") or {}
    mode = _one_of(triggers.get("mode"), "triggers.mode", _TRIGGER_MODES)
    backend = _one_of(triggers.get("backend"), "triggers.backend", _TRIGGER_BACKENDS)
    port = triggers.get("serial_port")
    if port is not None:
        port = clean_serial_port(port)
    elif backend == "serial":
        raise ValueError("lexsync: triggers.backend is serial, so triggers.serial_port must "
                         "name the serial device, such as COM3 or /dev/ttyUSB0.")
    baudrate = triggers.get("baudrate")
    if baudrate is None:
        baudrate = 115200
    elif not _whole_number(baudrate, 1, _INT_MAX):
        raise ValueError("lexsync: triggers.baudrate must be a whole number of bits per "
                         "second, such as 115200.")
    return {"mode": mode, "backend": backend, "serial_port": port or "",
            "baudrate": int(baudrate)}


def _trigger_device(settings: dict, address: str) -> str:
    """The trigger device as the experiments' messages name it. Must match
    .trigger_device in scripting.R."""
    if settings["backend"] == "serial":
        return "the serial port " + settings["serial_port"]
    return "the parallel port at " + address


def _as_duration(value):
    """A duration as a float, or None when the value is not a number.

    A number is taken as it is, and so is text that is a plain decimal number, as a
    design that quotes a duration carries it and as a column holding some text is read.
    A boolean is not a duration, although Python counts True as 1. Must match
    .as_duration in scripting.R.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, numbers.Real):
        return float(value)
    if isinstance(value, str) and _PLAIN_NUMBER.match(value):
        return float(value)
    return None


def _fixed_duration(value, what: str) -> float:
    """A duration the design fixes, checked: a finite number, not negative.

    ``what`` names the value in the refusal, as in ``event 2 has duration_ms`` or
    ``timing.word_ms is``. Must match .fixed_duration in scripting.R.
    """
    number = _as_duration(value)
    if number is None or not math.isfinite(number) or number < 0:
        raise ValueError("lexsync: %s '%s'; a duration must be a finite number, not negative."
                         % (what, _shown(value)))
    return number


def _event_ms(ev: dict, override_ms, override_frames, hz, default_frames: int = 1,
              index: int | None = None) -> int:
    """Resolve one event's duration to whole milliseconds.

    Milliseconds are canonical; a frame count is accepted for backward
    compatibility and converted at the design's assumed refresh rate. An explicit
    ``duration_ms`` wins over ``duration_frames`` if a design carries both.

    Either must be a finite number, not negative, or the event is refused, named by
    ``index``, its place in the design counted from 1. A fractional ``duration_ms`` is
    rounded with _round_dp, as a duration read from the items is. int() would truncate
    it, so 33.7 ms would be presented as 33. A null ``duration_frames`` counts as
    absent, as it does in the R engine. The overrides come from the design's ``timing``
    block, which _render_each has already checked. Must match .event_ms in scripting.R.
    """
    where = "an event" if index is None else "event %d" % index
    if override_ms is not None:
        return int(_round_dp(float(override_ms), 0))
    if override_frames is not None:
        return _frames_to_ms(override_frames, hz)
    if ev.get("duration_ms") is not None:
        ms = _fixed_duration(ev["duration_ms"], where + " has duration_ms")
        return int(_round_dp(ms, 0))
    frames = ev.get("duration_frames")
    if frames is None:
        return _frames_to_ms(default_frames, hz)
    return _frames_to_ms(_fixed_duration(frames, where + " has duration_frames"), hz)


def find_template(relpath: str) -> str:
    """The path of the template ``relpath``, from the first location that holds it.

    The locations are, in order, the directory that the environment variable
    ``LEXSYNC_TEMPLATES`` names, the copy inside the package, then ``templates/`` and
    ``../templates/`` relative to the working directory. A template found through the
    variable replaces the bundled one in every PsychoPy and jsPsych export, so it
    changes the generated experiments and the checksums their datasheets record.
    Mirrors find_template in scripting.R.
    """
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


def assign_triggers(stimuli: pd.DataFrame, conditions=None, events=None,
                    schema=None) -> pd.DataFrame:
    """A per-condition marker and a per-item marker, both 0-255 EEG codes.

    ``condition_trigger`` numbers the conditions from 101 upwards and
    ``item_trigger`` numbers the item sets from 40, in code-point order of their
    labels, so with sets 1 to 20, set 10 is 41 and set 2 is 51. Decode an item code
    through the loop table, not from the set's label. The item range holds 200 codes
    (an 8-bit-port constraint), so past 200 sets the codes wrap and repeat, and a
    printed notice says so.

    ``events``, the design's event list, says which codes the experiment sends. When
    it sends item codes together with condition codes, or with a code of its own from
    40 to 239, the item codes skip 101 to 100 + k, the codes of the k conditions, and
    the design's own codes, so that no item takes a code that marks something else.
    Without the skip, sets 65 and 66 of a 70-set design would take 101 and 102, the
    condition codes. With it, a design with more item sets than free codes is refused, unless
    ``schema`` sets ``triggers.allow_code_overlap: true``, which lets the item codes
    wrap and repeat within the free codes. Every other design, and a call without
    ``events``, takes the item codes described above, from 40 upwards in code-point
    order of the set labels, wrapping and repeating past 200 sets. Each trigger in
    ``events`` is checked as ``render_events`` checks it.

    A notice is printed for a code of the design's own that the stream already uses
    for something else: 254 or 255, which the PsychoPy and OpenSesame experiments send
    when the session starts and ends, a condition code the design sends, or a code
    within the range of the item codes it sends.

    The condition codes follow ``conditions`` when it is given: its first entry is
    101, its second 102, and so on, whether or not every entry occurs in
    ``stimuli``, so the same condition keeps the same code in a subset such as a
    practice block. A condition present in ``stimuli`` but missing from
    ``conditions`` takes the next free codes, in code-point order of its label.
    Either way the mapping depends only on the labels, never on the row order.
    Without ``conditions``, the codes follow the order in which the conditions
    first appear in ``stimuli``, as in lexsync 0.1.0. On a shuffled trial list that
    order comes from the shuffle, so a different seed can swap two conditions'
    codes. ``export_experiments`` passes the design's order, and the pipeline
    passes the order of the design's ``conditions``, followed by any other
    condition in the order the item source lists it.

    Examples:
        >>> stim = pd.DataFrame({"condition": ["low", "high", "low", "high"],
        ...                      "set": [1, 1, 2, 2]})
        >>> assign_triggers(stim)["condition_trigger"].tolist()
        [101, 102, 101, 102]
        >>> assign_triggers(stim, conditions=["high", "low"])["condition_trigger"].tolist()
        [102, 101, 102, 101]
    """
    stimuli, notes = _allocate_codes(stimuli, conditions, events, schema)
    for note in notes:
        print(note)
    return stimuli


def _allocate_codes(stimuli: pd.DataFrame, conditions=None, events=None,
                    schema=None) -> tuple:
    """assign_triggers without its notices: ``(stimuli with the codes, notices)``.

    run_pipeline calls it before any file is written, so that a design whose item
    codes cannot be kept apart is refused there, and assign_triggers prints the
    notices once, when the experiments are written. Must match .allocate_codes in
    scripting.R.
    """
    allow_overlap = _allow_code_overlap(schema)
    stimuli = stimuli.copy()
    if conditions is None:
        conds = list(dict.fromkeys(stimuli["condition"]))
        stimuli["condition_trigger"] = stimuli["condition"].map(lambda c: 101 + conds.index(c))
    else:
        if isinstance(conditions, str):
            conditions = [conditions]
        conds = list(dict.fromkeys(str(c) for c in conditions))
        present = dict.fromkeys(str(c) for c in stimuli["condition"])
        # sorted() on str is code-point order, the same order R's radix sort gives.
        conds += sorted(c for c in present if c not in conds)
        stimuli["condition_trigger"] = stimuli["condition"].map(
            lambda c: 101 + conds.index(str(c)))
    sets = sorted(stimuli["set"].unique(), key=lambda s: str(s))
    sent = _codes_sent(events)
    own = sorted({code for _, code in sent["literals"]})
    notes = []
    if sent["item"] and (sent["condition"] or any(c in _ITEM_CODES for c in own)):
        # The item codes share the stream with codes that mean something else, so they
        # are drawn only from the codes nothing else takes.
        condition_codes = range(101, 101 + len(conds))
        free = [c for c in _ITEM_CODES if c not in condition_codes and c not in own]
        if len(sets) > len(free):
            if not (allow_overlap and free):
                raise ValueError(
                    "lexsync: %d item sets need %d item codes, but only %d of the codes from "
                    "40 to 239 are free of the condition codes and the design's own codes; "
                    "send fewer kinds of code, or set triggers.allow_code_overlap: true to "
                    "let item codes repeat." % (len(sets), len(sets), len(free)))
            notes.append("lexsync: %d item sets exceed the %d free item codes; item codes "
                         "wrap and repeat." % (len(sets), len(free)))
        set_code = {s: free[i % len(free)] for i, s in enumerate(sets)}
    else:
        # A wrapped code no longer identifies its item one to one, which the analyst
        # must hear about at generation time, not at decode time.
        if len(sets) > 200:
            notes.append(f"lexsync: {len(sets)} item sets exceed the 200-code trigger range; "
                         "item codes wrap and repeat.")
        set_code = {s: 40 + (i % 200) for i, s in enumerate(sets)}
    stimuli["item_trigger"] = stimuli["set"].map(set_code)
    notes += _code_notes(sent, conds, list(set_code.values()))
    return stimuli, notes


def _allow_code_overlap(schema) -> bool:
    """The schema's ``triggers.allow_code_overlap``, false when absent.

    Read strictly: a value that is not a boolean is refused, as R's isTRUE() would
    quietly read 'yes' as false where Python's truth test reads it as true. Must match
    .allow_code_overlap in scripting.R.
    """
    value = ((schema or {}).get("triggers") or {}).get("allow_code_overlap")
    if value is None:
        return False
    if not isinstance(value, bool):
        raise ValueError("lexsync: triggers.allow_code_overlap must be true or false.")
    return value


def _codes_sent(events) -> dict:
    """The codes a design's events send.

    ``item`` and ``condition`` say whether any event sends the item code or the
    condition code, and ``literals`` lists the design's own codes as ``(event, code)``
    pairs, the event counted from 1, in event order. A fixation, text or mask event
    sends its ``trigger`` and a region-by-region event its ``critical_region_trigger``,
    the keys render_events reads, and each is checked as it is there. Must match
    .codes_sent in scripting.R.
    """
    sent = {"item": False, "condition": False, "literals": []}
    for i, ev in enumerate(events or [], start=1):
        kind = ev.get("type")
        key = ("trigger" if kind in ("fixation", "text", "mask")
               else "critical_region_trigger" if kind == "region_by_region" else None)
        spec = None if key is None else _trigger_spec(ev.get(key), i, key)
        if spec == "@item_trigger":
            sent["item"] = True
        elif spec == "@condition_trigger":
            sent["condition"] = True
        elif spec is not None:
            sent["literals"].append((i, spec))
    return sent


def _code_notes(sent: dict, conds: list, item_codes: list) -> list:
    """The notices for the design's own codes that the stream already uses.

    A code of 254 or 255, which the PsychoPy and OpenSesame experiments send when the
    session starts and ends, a code equal to a condition code the design sends, and a
    code within the range of the item codes it sends. The allocation keeps every item
    code off the design's own codes, so the last is a warning for anyone who decodes
    item codes by their range. Must match .code_notes in scripting.R.
    """
    notes = []
    for i, code in sent["literals"]:
        if code in (254, 255):
            notes.append("lexsync: event %d sends code %d, which the PsychoPy and OpenSesame "
                         "experiments also send when the session %s."
                         % (i, code, "starts" if code == 254 else "ends"))
        if sent["condition"] and 101 <= code <= 100 + len(conds):
            notes.append("lexsync: event %d sends code %d, which is also the condition code "
                         "of '%s'." % (i, code, _shown(conds[code - 101])))
        if sent["item"] and item_codes and min(item_codes) <= code <= max(item_codes):
            notes.append("lexsync: event %d sends code %d, which lies inside the range of the "
                         "item codes (%d to %d); decode item codes through the loop table."
                         % (i, code, min(item_codes), max(item_codes)))
    return notes


def _keys_of(ev: dict, default: list) -> list:
    """An event's response keys, normalised and validated.

    A YAML scalar (`keys: space`) arrives as a str and is taken as one key, as R keeps
    the scalar whole, since `list("space")` would be five one-character keys. A YAML
    boolean is refused. Both engines read an unquoted yes, no, true, false, on or off
    as a boolean. str() would then make the key True here, and R would write TRUE, so
    neither experiment could register a response. The message names the boolean as R
    does. Each key is then validated because OpenSesame writes them into
    `set allowed_responses "a;b"`, one line of a line-oriented format. Must match
    .keys_of in R_workflow/R/scripting.R.
    """
    keys = ev.get("keys", default)
    if isinstance(keys, (str, bool)):
        keys = [keys]
    for key in keys:
        if isinstance(key, bool):
            raise ValueError("lexsync: response key %s is a YAML boolean; quote it ('%s') or "
                             "choose another key." % (("TRUE", "yes") if key else ("FALSE", "no")))
    return [clean_key(k) for k in keys]


def _trigger_spec(value, index: int | None = None, key: str = "trigger"):
    """Translate a paradigm trigger token to a renderer spec (int or '@column').

    A trigger is the token "condition" or "item", or a whole number from 1 to 255,
    written as a number or as a string of digits. Anything else is refused, naming the
    event by ``index``, its place in the design counted from 1, and the ``key`` the
    value came from. A code outside 1 to 255 is refused because the port keeps only
    its low byte, a fractional code such as 20.5 because it is not a code, and a
    misspelt token such as "conditon" because it is neither token. Must match
    trigger_spec in scripting.R.
    """
    if value is None:
        return None
    code = None
    if isinstance(value, str):
        if value == "condition":
            return "@condition_trigger"
        if value == "item":
            return "@item_trigger"
        if _DIGITS.match(value):
            code = int(value)
    elif (isinstance(value, numbers.Real) and not isinstance(value, bool)
          and math.isfinite(value) and value == int(value)):
        code = int(value)
    if code is None or not 1 <= code <= 255:
        where = "an event" if index is None else "event %d" % index
        raise ValueError("lexsync: %s has %s '%s'; use 'condition', 'item' or a code from 1 "
                         "to 255." % (where, key, _shown(value)))
    return code


def _case_of(ev: dict, index: int) -> str:
    """A text event's ``case``, "upper" or "lower", checked.

    The case travels with the rendered event and the runners apply it as they show the
    text: str.upper() and str.lower() in PsychoPy and OpenSesame, toUpperCase() and
    toLowerCase() in jsPsych. The generators never change the text, because R's
    toupper() leaves 'ß' as it is where Python gives 'SS', and the two engines must
    write the same files. Must match .case_of in scripting.R.
    """
    value = ev.get("case")
    if not isinstance(value, str) or value not in ("upper", "lower"):
        raise ValueError("lexsync: event %d has case '%s'; a text event takes case: upper or "
                         "case: lower." % (index, _shown(value)))
    return value


# A field a mask's length_of may name, as a {field} reference names one.
_FIELD_NAME = re.compile(r"\A[A-Za-z_][A-Za-z0-9_]*\Z")


def _length_of(ev: dict, index: int) -> list:
    """A mask's ``length_of``, the fields whose longest text sets its length, checked.

    A scalar names one field. The mask's content must be one character, which
    _sized_masks repeats once the trials are known. Must match .length_of in
    scripting.R.
    """
    value = ev["length_of"]
    fields = [value] if isinstance(value, str) else value
    if (not isinstance(fields, list) or not fields
            or not all(isinstance(f, str) and _FIELD_NAME.match(f) for f in fields)):
        raise ValueError("lexsync: event %d has length_of '%s'; name the fields whose longest "
                         "text sets the mask's length, as in [prime, target]."
                         % (index, _shown(value)))
    content = ev.get("content")
    if not isinstance(content, str) or len(content) != 1:
        raise ValueError("lexsync: event %d repeats its content to the length of the longest "
                         "text of the trials, so its content must be one character, such as "
                         "'#'." % index)
    return list(fields)


def _sized_masks(rendered: list, stimuli: pd.DataFrame) -> list:
    """The rendered events with each ``length_of`` mask written out for these trials.

    Such a mask's character is repeated as many times as the longest text of its fields
    has characters (code points, so 'naïveté' counts 7 where UTF-8 gives 9 bytes),
    among all the trials of every version, so each target and each version shows the
    same mask. A missing cell is passed over. The mask then travels as literal text, as
    any other mask does. Must match .sized_masks in scripting.R.
    """
    out = []
    for ev in rendered:
        if "length_of" not in ev:
            out.append(ev)
            continue
        longest = 1
        for field in ev["length_of"]:
            if field not in stimuli.columns:
                raise ValueError("lexsync: a mask takes its length from field '%s', which the "
                                 "trials do not have." % field)
            for value in stimuli[field]:
                if value is None or value is pd.NA or (isinstance(value, float)
                                                       and value != value):
                    continue
                text = value if isinstance(value, str) else _readr_cell(value)
                longest = max(longest, len(text))
        sized = {k: v for k, v in ev.items() if k != "length_of"}
        sized["text"] = ev["text"] * longest
        out.append(sized)
    return out


def _duration_spec(ev: dict, index: int):
    """A design's per-event ``duration:`` block, if it declares one.

    ``duration: {from_column: soa_ms}``            read per trial from the items
    ``duration: {jitter: [400, 800], as: isi_ms}`` drawn per trial from the hash

    A jitter's bounds must be finite numbers and the lower one not negative, since
    every value drawn between them is a duration. A lone bound is a range of one and
    is refused, as the R engine refuses it.
    Must match .duration_spec in scripting.R.
    """
    d = ev.get("duration")
    if not isinstance(d, dict):
        return None
    if d.get("from_column") is not None:
        return {"column": str(d["from_column"]), "jitter": None}
    if d.get("jitter") is not None:
        bounds = d["jitter"]
        if isinstance(bounds, dict):
            bounds = list(bounds.values())
        bounds = list(bounds) if isinstance(bounds, (list, tuple)) else [bounds]
        if len(bounds) != 2:
            raise ValueError("lexsync: duration jitter must be a two-element range [lo, hi].")
        lo, hi = (_as_duration(v) for v in bounds)
        if lo is None or hi is None or not (math.isfinite(lo) and math.isfinite(hi)) or lo < 0:
            raise ValueError("lexsync: event %d has jitter %s; a jittered duration needs finite "
                             "bounds, the lower one not negative." % (index, _shown(bounds)))
        return {"column": str(d.get("as") or ("event%d_ms" % index)),
                "jitter": [int(lo), int(hi)]}
    raise ValueError("lexsync: a duration block needs either 'from_column' or 'jitter'.")


def resolve_trial_timing(stimuli: pd.DataFrame, design: dict, schema: dict) -> pd.DataFrame:
    """Realise per-trial event durations onto the stimuli table.

    An event may declare a duration that varies from trial to trial, either read
    from an item column or drawn from a range. A drawn value is a pure function of
    the keyed hash, so both engines realise the same milliseconds, and it is
    written into the stimuli table as well as the generated script, because timing
    that varies is a variable the analysis needs, not presentation detail.

    An event declares it as ``duration: {from_column: <column>}``, to read each
    trial's milliseconds from an item column, or as
    ``duration: {jitter: [lo, hi], as: <column>}``, to draw a whole number of
    milliseconds from ``lo`` to ``hi``, both included, into the column ``as`` names
    (``event<i>_ms`` by default, ``i`` counting the design's events from 1). The draw
    is keyed on the seed, the column, the list, the set and the condition.

    Every value read from a column must be a finite number of milliseconds, not
    negative. The first that is not, a blank cell included, is refused, naming the
    column and the trial's set and condition. When a column holds fractional
    milliseconds, each of its values is rounded once with the rounder both engines
    share and written back, so the stimuli, the loop tables and every target carry the
    same whole milliseconds. A column of whole numbers is left as it is. Each column
    rounded is recorded in the returned frame's ``attrs["duration_rounding"]``, as one
    ``{"event", "column", "n_rounded"}`` entry, which run_pipeline writes into the run
    log.
    """
    events = resolve_events(design)
    seed = (schema or {}).get("seed", 1)
    stimuli = stimuli.copy()
    # A record carried in from an earlier call describes that call, not this one.
    stimuli.attrs.pop("duration_rounding", None)
    rounding = []
    for i, ev in enumerate(events, start=1):
        spec = _duration_spec(ev, i)
        if spec is None:
            continue
        if spec["jitter"] is None:
            # from_column reads a column the items already carry, so it is checked here.
            if spec["column"] not in stimuli.columns:
                raise ValueError(
                    "lexsync: event %d reads its duration from column '%s', which the "
                    "items do not have." % (i, spec["column"]))
            n_rounded = _column_durations(stimuli, i, spec["column"])
            if n_rounded:
                rounding.append({"event": i, "column": spec["column"], "n_rounded": n_rounded})
            continue
        lo, hi = spec["jitter"]
        # The key names the column as well as the trial, so two jittered events in
        # one design draw independently, where a key naming only the trial would
        # give them one shared value.
        lists = stimuli["list"] if "list" in stimuli.columns else [1] * len(stimuli)
        keys = ["|".join([_key_part(seed), "jitter", spec["column"],
                          _key_part(l), _key_part(s), _key_part(c)])
                for l, s, c in zip(lists, stimuli["set"], stimuli["condition"], strict=True)]
        stimuli[spec["column"]] = [hash_int_range(k, lo, hi) for k in keys]
    if rounding:
        stimuli.attrs["duration_rounding"] = rounding
    return stimuli


def _column_durations(stimuli: pd.DataFrame, index: int, column: str) -> int:
    """Check the durations event ``index`` reads from ``column``, and round fractions.

    A column holding fractional milliseconds is written back rounded, in ``stimuli``
    itself, and the number of values that changed is returned. A value given as text
    is read as a number when it is a plain decimal one, so the refusal names the cell
    that is not. Must match .column_durations in scripting.R.
    """
    values = []
    for row, value in enumerate(stimuli[column].tolist()):
        blank = value is None or value is pd.NA or (isinstance(value, float) and value != value)
        number = None if blank else _as_duration(value)
        if number is None or not math.isfinite(number) or number < 0:
            what = "is blank" if blank else "holds '%s'" % _shown(value)
            raise ValueError(
                "lexsync: event %d reads its duration from column '%s', which %s for %s; a "
                "duration must be a finite number of milliseconds, not negative."
                % (index, column, what, _trial_named(stimuli, row)))
        values.append(number)
    n_rounded = sum(1 for v in values if v != math.trunc(v))
    if n_rounded:
        stimuli[column] = [_round_dp(v, 0) for v in values]
    return n_rounded


def _trial_named(stimuli: pd.DataFrame, row: int) -> str:
    """A trial as a refusal names it: its set and condition, and its block when the
    trials carry one, or else its row, counted from 1. Must match .trial_named in
    scripting.R."""
    if "set" not in stimuli.columns or "condition" not in stimuli.columns:
        return "row %d" % (row + 1)
    named = "set %s in condition '%s'" % (_shown(stimuli["set"].iloc[row]),
                                          _shown(stimuli["condition"].iloc[row]))
    if "block" in stimuli.columns:
        named += " of block '%s'" % _shown(stimuli["block"].iloc[row])
    return named


def render_events(events: list, timing: dict, hz: float = 60) -> list:
    """Translate paradigm events into backend-neutral rendering dictionaries.

    Content becomes {field} or {text}; triggers become int / '@column'; the design
    ``timing`` overrides the fixation, critical-word and ISI durations.

    A fixed duration is emitted as whole milliseconds (``ms``), the unit every backend
    consumes: OpenSesame and jsPsych schedule it directly, and the PsychoPy script
    converts it back into whole flips against the refresh rate it measures at
    start-up. A duration read from the items or jittered (a ``duration:`` block) is
    emitted as ``ms_column``, the loop-table column holding each trial's milliseconds.
    A response or question event's ``timeout`` is in seconds, rounded to three places.

    A response collected from the onset of the text event before it (see
    ``_response_from``) is rendered with that event, as its ``respond`` entry
    (``{"keys", "timeout"}``). The text keeps its ``ms`` (or ``ms_column``) as its
    longest display time, and the window runs from its onset for ``ms`` plus the
    timeout, so the total window is the one the two events had. A response collected
    from the offset stays an event of its own.

    A text event's ``case`` is carried as it is, for the runners to apply. A mask's
    ``length_of`` is carried too, with the one character to repeat as its ``text``, and
    the exporters write the mask out for their trials (see ``_sized_masks``).
    """
    rendered = _render_each(events, timing, hz)
    out = []
    for i, r in enumerate(rendered, start=1):
        if r["type"] == "response" and _response_from(events, i) == "onset":
            text = out[-1]
            # The merged event runs where the text runs, so a response restricted to
            # other blocks than its stimulus has no window to open.
            if r.get("blocks") != text.get("blocks"):
                raise ValueError(
                    "lexsync: event %d collects its response from the onset of event %d, "
                    "so the two must run in the same blocks; give them the same `blocks`, "
                    "or use from: offset." % (i, i - 1))
            text["respond"] = {"keys": r["keys"], "timeout": r["timeout"]}
            continue
        out.append(r)
    return out


def _response_from(events: list, i: int) -> str:
    """Where response event ``i``, counted from 1, opens its window: "onset" or "offset".

    From "onset", the window opens with the text event just before the response, so a
    key pressed while that stimulus is on screen counts and the reaction time runs from
    its onset. From "offset", it opens when the stimulus has gone, for a design that
    asks the participant to wait. A design says which with ``from:``, and without it a
    response after a text event is collected from the onset and any other from the
    offset. Must match .response_from in scripting.R.
    """
    ev = events[i - 1]
    prev = events[i - 2] if i > 1 else None
    after_text = prev is not None and prev.get("type") == "text"
    given = ev.get("from")
    if given is None:
        return "onset" if after_text else "offset"
    if not isinstance(given, str) or given not in ("onset", "offset"):
        raise ValueError("lexsync: event %d gives `from: %s`, but a response event takes "
                         "from: onset or from: offset." % (i, _shown(given)))
    if given == "onset" and not after_text:
        what = ("no event precedes it" if prev is None
                else "event %d is a %s" % (i - 1, _shown(prev.get("type"))))
        raise ValueError("lexsync: event %d collects its response from the onset of the "
                         "preceding stimulus, but %s; use from: offset." % (i, what))
    return given


def _whole_ms(seconds) -> int:
    """A rendered timeout, in seconds, as the whole milliseconds the design declared.

    Rounded through _round_dp. int() would truncate 1.001 * 1000, which is
    1000.9999999999999 in binary floating point, writing a declared 1,001 ms as 1,000,
    and 95 of the whole-millisecond values from 1 to 10,000 would come out one short.
    Must match .whole_ms in scripting.R.
    """
    return int(_round_dp(float(seconds) * 1000, 0))


def _response_windows(events: list, timing: dict, hz: float) -> list:
    """Each response event's window, as the datasheet records it.

    One ``{"event", "from", "window_ms"}`` per response event, where ``event`` counts
    the design's events from 1. A window from the onset runs for the stimulus's
    duration and the timeout, and one from the offset for the timeout. When the
    stimulus's duration varies by trial, ``window_ms`` is None and the entry adds the
    ``duration_column`` and the ``timeout_ms`` that make it up. Whole milliseconds, as
    every target writes them. Mirrors .response_windows in scripting.R.
    """
    rendered = _render_each(events, timing, hz)
    out = []
    for i, r in enumerate(rendered, start=1):
        if r["type"] != "response":
            continue
        start = _response_from(events, i)
        timeout_ms = _whole_ms(r["timeout"])
        entry = {"event": i, "from": start}
        stimulus = rendered[i - 2] if start == "onset" else None
        if stimulus is None:
            entry["window_ms"] = timeout_ms
        elif "ms_column" in stimulus:
            entry.update(window_ms=None, duration_column=stimulus["ms_column"],
                         timeout_ms=timeout_ms)
        else:
            entry["window_ms"] = int(stimulus["ms"]) + timeout_ms
        out.append(entry)
    return out


def _render_each(events: list, timing: dict, hz: float) -> list:
    """Each event rendered on its own, before a response joins its stimulus."""
    timing = timing or {}
    # An unknown timing key, such as the typo `fixation_frame`, is refused rather than
    # ignored, which would leave the event at its default duration: a mistimed
    # experiment is not recoverable after the data are collected. Must list the same
    # names as scripting.R.
    known = ("fixation_ms", "word_ms", "isi_ms",
             "fixation_frames", "word_frames", "isi_frames")
    unknown = sorted(set(timing) - set(known))
    if unknown:
        raise ValueError(
            "lexsync: unknown timing key(s) %s. Known keys: %s."
            % (", ".join("'%s'" % k for k in unknown), ", ".join(known)))
    # Each value of the block is a fixed duration, checked as an event's own is, in the
    # order of `known` so that both engines name the same key first.
    checked = {key: _fixed_duration(timing[key], "timing.%s is" % key)
               for key in known if timing.get(key) is not None}
    fix_ms, fix = checked.get("fixation_ms"), checked.get("fixation_frames")
    word_ms, word = checked.get("word_ms"), checked.get("word_frames")
    isi_ms, isi = checked.get("isi_ms"), checked.get("isi_frames")
    # A feedback event scores the key the participant pressed, so something must have
    # collected one first. With no preceding response or question, every target would
    # show the no-response message on every trial, which surfaces only at run time,
    # for one design error that is obvious here.
    seen_response = False
    for i, ev in enumerate(events, start=1):
        ty = ev.get("type")
        if ty in ("response", "question"):
            seen_response = True
        if ty == "feedback" and not seen_response:
            raise ValueError(
                "lexsync: event %d is a feedback event, but no response or question "
                "event precedes it, so there is no response to score." % i)
    out = []
    for i, ev in enumerate(events, start=1):
        t = ev["type"]
        r = {"type": "region" if t == "region_by_region" else t}
        if ev.get("case") is not None and t != "text":
            raise ValueError("lexsync: event %d is a %s event, and only a text event takes "
                             "`case`." % (i, _shown(t)))
        if ev.get("length_of") is not None and t != "mask":
            raise ValueError("lexsync: event %d is a %s event, and only a mask event takes "
                             "`length_of`." % (i, _shown(t)))
        if t in ("fixation", "text", "mask"):
            f = content_field(ev.get("content"))
            if f:
                r["field"] = f
            else:
                r["text"] = str(ev.get("content", ""))
            if ev.get("length_of") is not None:
                r["length_of"] = _length_of(ev, i)
            # The overrides are type-keyed: `fixation_*` reaches every
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
                    hz, index=i,
                )
            spec = _trigger_spec(ev.get("trigger"), i)
            if spec is not None:
                r["trigger"] = spec
            if ev.get("case") is not None:
                r["case"] = _case_of(ev, i)
        elif t == "blank":
            spec = _duration_spec(ev, i)
            if spec is not None:
                r["ms_column"] = spec["column"]
            else:
                r["ms"] = _event_ms(ev, isi_ms, isi, hz, index=i)
        elif t == "region_by_region":
            r["field"] = content_field(ev.get("content"))
            r["sep"] = ev.get("sep", "|")
            r["key"] = ev.get("advance", "space")
            spec = _trigger_spec(ev.get("critical_region_trigger"), i, "critical_region_trigger")
            if spec is not None:
                r["crit_trigger"] = spec
        elif t == "response":
            r["keys"] = _keys_of(ev, ["left", "right"])
            # _round_dp, not round(): the timeout is written into experiment files
            # both engines emit as the same bytes, and the two languages' own
            # rounders disagree on 3-dp halfway cases (see _round_dp in io_utils.py).
            r["timeout"] = _round_dp(ev.get("timeout_ms", 2000) / 1000.0, 3)
        elif t == "question":
            r["field"] = content_field(ev.get("content"))
            r["keys"] = _keys_of(ev, ["f", "j"])
            r["timeout"] = _round_dp(ev.get("timeout_ms", 5000) / 1000.0, 3)
        elif t == "feedback":
            # Feedback compares the key the participant pressed against the key the item
            # says is correct, so `answer` names a loop-table column holding a KEY, not a
            # label: the runner then needs no mapping table and no notion of what the
            # keys mean.
            r["answer"] = str(ev.get("answer", "answer"))
            r["correct"] = str(ev.get("correct", "Correct"))
            r["incorrect"] = str(ev.get("incorrect", "Incorrect"))
            r["no_response"] = str(ev.get("no_response", "Too slow"))
            r["ms"] = _event_ms(ev, None, None, hz, default_frames=36, index=i)
        else:
            raise ValueError(f"lexsync: unknown event type '{t}'.")
        # An event may be restricted to named blocks. This is what lets feedback run
        # during practice and nowhere else: the event list is global to the design, so
        # the restriction has to travel with the event and be applied per trial at run
        # time. Generating a second event list would be the alternative, and a worse one.
        if ev.get("blocks"):
            # A scalar `blocks: practice` is a str, and iterating it would yield
            # characters, which the OpenSesame guard would compare against "p", "r",
            # ... and never match.
            blks = ev["blocks"]
            blks = [blks] if isinstance(blks, str) else list(blks)
            r["blocks"] = [str(b) for b in blks]
        out.append(r)
    return out


def _order_columns(stimuli: pd.DataFrame) -> list:
    """The trial-order columns ``order_1`` to ``order_m`` the trials carry, in order.

    ``counterbalance`` writes them when a design asks for more than one order. The
    numbering runs from ``order_1`` without a gap, so a column of another name, such as
    an item table's own ``order_9``, is not taken for one. Mirrors .order_columns in
    scripting.R.
    """
    out = []
    while "order_%d" % (len(out) + 1) in stimuli.columns:
        out.append("order_%d" % (len(out) + 1))
    return out if len(out) > 1 else []


def _n_orders(stimuli: pd.DataFrame) -> int:
    """The number of trial orders the trials carry, 1 when they carry none."""
    return max(1, len(_order_columns(stimuli)))


def _ms_columns(events: list | None) -> list:
    """The per-trial duration columns an event list reads, in event order."""
    cols = []
    for i, ev in enumerate(events or [], start=1):
        s = _duration_spec(ev, i)
        if s is not None and s["column"] not in cols:
            cols.append(s["column"])
    return cols


def loop_table(stimuli: pd.DataFrame, events: list | None = None) -> pd.DataFrame:
    """Per-trial table of the columns the experiments read.

    The columns are those of ``stimuli``, where present, in this order: ``trial``,
    ``list``, ``replicate``, ``block``, ``set``, ``condition``, ``order_1`` to
    ``order_m`` (with two or more orders), the fields the events' content references
    (``referenced_fields``), or ``word`` when ``events`` is ``None`` or empty, the
    per-trial duration columns the events read, ``critical_region``, ``answer``,
    ``condition_trigger`` and ``item_trigger``. Every other column of ``stimuli`` is
    left out.

    The rows are in presentation order within each version: by replicate when the
    table has one, then by list, then by trial. `trial` restarts at 1 in every list
    and in every replicate, so ordering on it alone would interleave the versions. The
    sort is stable, as R's order() is, so rows that tie keep their incoming order and
    the two engines write the same table. A design with ``counterbalance.orders``
    carries ``order_1`` to ``order_m`` after the columns that place a trial, each
    trial's position in each order, which the experiments sort a version by.
    """
    fields = referenced_fields(events) if events else (["word"] if "word" in stimuli.columns else [])
    # A per-trial duration is read from the loop table at run time, so its column
    # has to travel with the trials, and cannot stay behind in the stimuli file.
    ms_cols = _ms_columns(events)
    order_cols = _order_columns(stimuli)
    cols = []
    for c in (_STD_COLS[:_LEADING_COLS] + order_cols + fields + ms_cols
              + _STD_COLS[_LEADING_COLS:]):
        if c in stimuli.columns and c not in cols:
            cols.append(c)
    tab = stimuli[cols].copy()
    keys = [c for c in ("replicate", "list", "trial") if c in tab.columns]
    if keys:
        tab = tab.sort_values(keys, kind="stable").reset_index(drop=True)
    return tab


def _version_key(stimuli: pd.DataFrame, column: str) -> list:
    """Each row's replicate or list, as a whole number.

    A table without the column is one replicate, or one list, numbered 1, and so is a
    row that leaves it empty. Any other value that is not a whole number is refused,
    because a version is numbered by those whole numbers in order. A number is judged
    by its value, and text only when it is a plain decimal number (``_PLAIN_NUMBER``),
    as .version_key in scripting.R judges them: float() alone also takes "1_0" and the
    digits of other scripts, and R's as.numeric() takes "0x10". A refused number is
    shown to 17 significant digits in both engines.
    """
    if column not in stimuli.columns:
        return [1] * len(stimuli)
    out = []
    for value in stimuli[column]:
        if pd.isna(value):
            out.append(1)
            continue
        if isinstance(value, numbers.Real) and not isinstance(value, bool):
            number = float(value)
            shown = "%.17g" % number
        else:
            # The characters R's trimws() removes, and no other space.
            shown = str(value).strip(" \t\r\n")
            if not shown:
                out.append(1)
                continue
            number = float(shown) if _PLAIN_NUMBER.fullmatch(shown) else math.nan
        if not (math.isfinite(number) and number == math.trunc(number)):
            raise ValueError(f"lexsync: the trials' `{column}` column holds '{shown}', but a "
                             "presentation version is numbered by whole-number lists and "
                             "replicates.")
        out.append(int(number))
    return out


def _version_keys(stimuli: pd.DataFrame) -> list:
    """Each row's (replicate, list) pair."""
    return list(zip(_version_key(stimuli, "replicate"), _version_key(stimuli, "list"),
                    strict=True))


def presentation_versions(stimuli: pd.DataFrame) -> list:
    """The presentation versions a set of trials holds, in the order they are numbered.

    A version is one (replicate, list) pair of the trials, and each participant is
    presented one version. Version 1 is the first pair in (replicate, list) order,
    version 2 the next, and so on. A table without a ``replicate`` column is one
    replicate, numbered 1, and one without ``list`` is one list. Participant ``p`` runs
    version ``((p - 1) mod V) + 1`` of ``V`` unless another is chosen at launch, the
    rule ``participant_table`` allocates by. The PsychoPy script and the jsPsych page
    carry this list. An OpenSesame experiment holds one version, and
    ``export_opensesame`` writes one experiment per version and trial order when a design
    has more than one of either. Mirrors .presentation_versions in scripting.R.

    Args:
        stimuli: The presented trials, with the ``list`` (and any ``replicate``)
            column that ``counterbalance`` adds.

    Returns:
        A list of ``{"version", "replicate", "list", "n_trials"}`` dictionaries, one per
            version, numbered from 1.

    Raises:
        ValueError: If a ``list`` or ``replicate`` value is not a whole number.

    Examples:
        >>> stim = pd.DataFrame({"list": [2, 1, 2], "set": [1, 1, 2]})
        >>> [(v["version"], v["list"], v["n_trials"]) for v in presentation_versions(stim)]
        [(1, 1, 1), (2, 2, 2)]
    """
    keys = _version_keys(stimuli)
    return [{"version": k, "replicate": rep, "list": lst,
             "n_trials": sum(1 for key in keys if key == (rep, lst))}
            for k, (rep, lst) in enumerate(sorted(set(keys)), start=1)]


def _version_rows(stimuli: pd.DataFrame, version: dict) -> pd.DataFrame:
    """The rows of one presentation version, in their incoming order."""
    wanted = (version["replicate"], version["list"])
    mask = pd.Series([key == wanted for key in _version_keys(stimuli)], index=stimuli.index,
                     dtype=bool)
    return stimuli.loc[mask].reset_index(drop=True)


def _rows_in_order(rows: pd.DataFrame, order: int) -> pd.DataFrame:
    """One version's rows in trial order ``order``, with ``trial`` set to each trial's
    position in it, so a table written from them numbers the trials as presented."""
    key = "order_%d" % order
    out = rows.sort_values(key, kind="stable").reset_index(drop=True)
    out["trial"] = out[key].to_numpy()
    return out


def _spans_replicates(versions: list) -> bool:
    """Whether the versions come from more than one replicate. A list then names no
    single version, so file names and launch options name the replicate as well."""
    return len({v["replicate"] for v in versions}) > 1


def _opensesame_tables(stimuli: pd.DataFrame, events: list) -> tuple:
    """The OpenSesame target's loop table and its companion text table.

    Both are the loop table, split by column and joined by ``lexsync_row``, the trial's
    position in loop order (1..N). The loop table holds ``lexsync_row`` and the numeric
    columns of ``_OS_NUMERIC`` plus any per-trial duration. The text table holds
    ``lexsync_row``, every presented field and every other column (``condition``,
    ``block``, ``answer``). A presented field that is also numeric goes to both.

    A numeric column's cells are checked as ``write_csv_utf8`` renders them, so the
    check sees the bytes OpenSesame will read. A cell that is not a plain decimal
    number is refused, naming the column. An empty cell passes, since OpenSesame leaves
    it alone and a filler sentence may have no critical region. Must match
    .opensesame_tables in scripting.R.
    """
    tab = loop_table(stimuli, events)
    presented = referenced_fields(events)
    numeric = list(_OS_NUMERIC) + _ms_columns(events)
    rows = list(range(1, len(tab) + 1))
    numbers = pd.DataFrame({"lexsync_row": rows})
    text = pd.DataFrame({"lexsync_row": rows})
    for col in tab.columns:
        if col in numeric:
            for value in tab[col]:
                cell = _readr_cell(value)
                if cell and not _PLAIN_NUMBER.match(cell):
                    raise ValueError(
                        "lexsync: column '%s' holds '%s', and the OpenSesame loop table "
                        "holds numbers only, because OpenSesame evaluates the cells of a "
                        "loop table." % (col, cell))
            numbers[_OS_NUMERIC.get(col, col)] = tab[col].to_numpy()
        if col in presented or col not in numeric:
            text[col] = tab[col].to_numpy()
    return numbers, text


def _write_text(text: str, path: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text + "\n")
    return path


def export_psychopy(stimuli: pd.DataFrame, design: dict, schema: dict, outdir: str,
                    base: str | None = None) -> str:
    """Write a runnable PsychoPy script and the conditions file it reads.

    The conditions file, ``<base>_psychopy.csv``, holds every presentation version
    (see ``presentation_versions``), and the script presents one per run: the
    version given by ``--version`` (or ``--list`` when there are no replicates), else
    the participant's by the rule ``((participant - 1) mod V) + 1`` from
    ``--participant``, else what a start-up dialogue asks for. A version the script does
    not have stops the run with a message. With ``counterbalance.orders: m`` the
    conditions file holds each trial's position in each of m orders, and the script
    presents the version in order ``(((participant - 1) div V) mod m) + 1``, or in order 1
    without a participant number. The data file then records the order.

    Before the first trial, the script shows the version's instructions, the design's
    ``instructions`` or lexsync's for its task, and waits for the space bar, which also
    lets the experimenter start the run. Escape there stops the run before anything is
    recorded. The text is embedded as JSON data, one text per version.

    Each run writes ``data/<base>_p<participant>_v<version>_<date>-<time>.csv`` beside
    the script, without the ``_p`` part when no participant number is given, one row
    per trial, each written as its trial ends. A row holds the run, the trial's fields
    and trigger codes, the response and its reaction time from the onset of the
    stimulus it answers, whether the window closed without one, whether the key was
    the trial's ``answer``, the self-paced reading times, the question's response and
    reaction time, the measured refresh rate, the trigger mode the run used, and each
    event's realised flips and onset.

    Each trigger code goes out on its stimulus's first flip and is held for
    ``triggers.trigger_hold_ms``, in whole flips at the measured refresh and never under
    10 ms, through the events after it when its own is shorter, unless the next onset's
    code replaces it first. The session markers, 254 before the first trial and 255
    after the last, are held the same way.

    The script runs full screen unless ``presentation.fullscreen`` is false, when it
    opens a 1280 x 1024 window, and draws its stimuli ``presentation.text_height_px``
    pixels high, 48 by default. It writes the codes to the parallel port at
    ``triggers.parallel_address`` or, with ``triggers.backend: serial``, as single bytes
    to ``triggers.serial_port`` at ``triggers.baudrate``. ``triggers.mode`` decides what
    happens when that device cannot be opened. Under ``auto``, the script prints the
    codes instead and, before the instructions, shows a notice that the experimenter
    dismisses with the C key. Under ``hardware``, it stops before its window opens, and
    under ``mock`` it prints the codes without trying the device, after the same
    notice. The data file's ``trigger_mode`` column records ``hardware`` or ``mock``.

    Args:
        stimuli: Stimuli with trigger columns (see ``assign_triggers``).
        design: A parsed design configuration.
        schema: The parsed global schema (trigger and presentation settings).
        outdir: Output directory.
        base: Optional file-name stem, by default the design's ``design_stem``.

    Returns:
        The path to the generated ``.py``.
    """
    return _psychopy_files(stimuli, design, schema, outdir, base)[0]


def _psychopy_files(stimuli, design, schema, outdir, base=None) -> list:
    """Write the PsychoPy script and its conditions file, and return both paths."""
    base = base or design_stem(design)
    events = resolve_events(design)
    rendered = _sized_masks(
        render_events(events, design.get("timing") or {}, _refresh_hz(schema)), stimuli)
    versions = presentation_versions(stimuli)
    csv_name = f"{base}_psychopy.csv"
    write_csv_utf8(loop_table(stimuli, events), os.path.join(outdir, csv_name))
    with open(find_template("psychopy/trial_runner_template.py"), encoding="utf-8") as handle:
        tmpl = handle.read()
    triggers = schema.get("triggers") or {}
    presentation = schema.get("presentation") or {}
    address = clean_port(triggers.get("parallel_address", "0x0378"))
    device = _trigger_settings(schema)
    # These land in CODE positions -- a module docstring, a bare assignment, a string
    # literal, so they are validated on the way in. Escaping would need three
    # different rules for three targets in two engines. See clean_meta in io_utils.
    subs = {
        "DESIGN": clean_meta(design["name"], "the design's `name`"),
        "LANGUAGE": clean_meta(design["language"], "the design's `language`"),
        "CONDITIONS_FILE": csv_name,
        # The data files are named after the experiment, as data/<base>_p<n>_v<k>_...
        "BASE": base,
        "TRIGGER_ADDRESS": address,
        "TRIGGER_BACKEND": device["backend"],
        "SERIAL_PORT": device["serial_port"],
        "SERIAL_BAUDRATE": str(device["baudrate"]),
        "TRIGGER_DEVICE": _trigger_device(device, address),
        "TRIGGER_MODE": device["mode"],
        "TRIGGER_HOLD_MS": "%.17g" % _trigger_hold_ms(schema),
        "WORD_FONT": clean_meta(
            design.get("font") or presentation.get("font") or "Courier New", "the font"),
        "FULLSCREEN": "True" if _fullscreen(schema) else "False",
        "TEXT_HEIGHT_PX": str(_text_height_px(schema)),
        # The fallback used only when the script cannot measure the display.
        "ASSUMED_REFRESH_HZ": "%.17g" % _refresh_hz(schema),
        "EVENTS_JSON": _json_r(rendered),
        "VERSIONS_JSON": _json_r(versions),
        "ORDERS": str(_n_orders(stimuli)),
        "INSTRUCTIONS_JSON": _json_r(_instruction_texts(design, versions)),
    }
    for key, value in subs.items():
        tmpl = tmpl.replace("{{" + key + "}}", str(value))
    script = _write_text(tmpl.rstrip("\n"), os.path.join(outdir, f"{base}_psychopy.py"))
    return [script, os.path.join(outdir, csv_name)]


def _pyq(s: str) -> str:
    """A safe single-quoted Python u-string literal for embedding in generated code.

    A newline is escaped as well as the backslash and the quote. An .osexp is a
    line-oriented format whose inline scripts are delimited by their own lines, so a raw
    newline in a value would not merely break the literal: it would close the script
    block and let the rest of the value start a new top-level item in the emitted
    experiment.
    """
    return ("u'" + str(s).replace("\\", "\\\\").replace("'", "\\'")
            .replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t") + "'")


def _text_expr(field: str) -> str:
    """A trial's text for `field`, from its row of the companion table."""
    return "_lexsync_row()[%s]" % _pyq(field)


def _number_expr(column: str) -> str:
    """A trial's value of a numeric loop column, read without evaluation."""
    return "int(var.get(%s, _eval=False))" % _pyq(column)


def _content_expr(ev: dict) -> str:
    """The text an event shows, as the inline script computes it. A text event's `case`
    is applied there, with Python's str.upper() or str.lower(), as the text is shown."""
    expr = _text_expr(ev["field"]) if "field" in ev else _pyq(ev.get("text", ""))
    return expr + {"upper": ".upper()", "lower": ".lower()"}.get(ev.get("case"), "")


def _trigger_expr(spec) -> str | None:
    if spec is None:
        return None
    if isinstance(spec, str) and spec.startswith("@"):
        return _number_expr(spec[1:])
    return str(int(spec))


# The Python that OpenSesame's inline_script actually runs.
#
# Two spellings below are forced by OpenSesame's runtime:
#
# `str`, never `unicode`. OpenSesame 3.3 and later run inline scripts in a Python 3
# workspace and inject only a fixed set of globals (exp, var, pool, items, clock, log and
# a small API); `unicode` is a Python 2 builtin and is not among them, so a guard or
# feedback script using it would die with NameError on the first trial.
#
# `var.get(name, u'')`, never `var.get(name, None)`. OpenSesame's var_store.get ends
# `elif default is not None: val = default / else: raise VariableDoesNotExist(var)`, so
# passing None explicitly is indistinguishable from passing no default and RAISES rather
# than yielding None. A non-None sentinel is the only default that works.
#
# And no text from `var` at all. OpenSesame evaluates a loop cell when the loop sets it
# and again when a script reads it. The presented text, the block and the answer
# therefore come from the trial's row of the companion table (`_lexsync_row()`, defined
# by the setup script). What is still read from `var`, the numeric loop columns and the
# response, is read with `_eval=False`: an evaluated read in 4.x turns a timed-out
# response, stored as None, into the string 'None'.


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
    return (["if _lexsync_row().get(u'block', u'main') in [%s]:" % wanted]
            + ["    " + line for line in body])


def _osexp_correct(key: str) -> list:
    """Lines that score the key held in `key` against the trial's `answer`.

    ``var.correct`` becomes 1 or 0, or stays empty when the trial names no answer. It is
    computed here, not by OpenSesame's ``correct_response``, whose variable syntax
    differs between 3.3 ([answer]) and 4.x ({answer}), and whose answer would have to
    come from the variable store, which evaluates text.
    """
    return ["_want = str(_lexsync_row().get(u'answer', u'')).strip()",
            "_got = u'' if %s is None else str(%s).strip()" % (key, key),
            "var.correct = (1 if _got == _want else 0) if _want else u''"]


def _osexp_event_block(name: str, ev: dict, scores: bool = True,
                       feedback_scores: str = "response") -> tuple:
    """Return (block_lines, run_names) for one rendered event.

    ``scores`` says whether a response or question this event collects is the one
    ``var.correct`` scores: the design's response events, or its questions when it has
    no response event. ``feedback_scores`` names the variable a feedback event reads,
    ``response`` or ``question_response``, after whichever collected a key last.

    Every canvas an event shows is built in its script's prepare phase, which OpenSesame
    runs for every item of the trial sequence before it runs any, so building and drawing
    take no time between one display and the next. The canvas is named after its script,
    ``_lexsync_c_e<i>``, because all inline scripts share one workspace and a shared name
    would show, in every script, the canvas prepared last. The run phase shows it and
    times everything from the onset that show() returns, through the helpers the setup
    script defines (see _osexp_timing): ``_lexsync_onset`` sends the event's code,
    ``_lexsync_wait`` sleeps and ``_lexsync_key`` polls the keyboard until a time
    measured from the onset, each resetting a code whose hold has run out.
    """
    t = ev["type"]
    blocks = ev.get("blocks")
    if blocks and t == "response":
        # A keyboard_response is not an inline script, so the guard cannot reach it.
        # Saying so beats emitting an experiment that ignores the restriction.
        raise ValueError(
            "lexsync: a `response` event cannot be restricted to blocks on the "
            "OpenSesame target. Restrict a feedback or stimulus event instead.")
    canvas = "_lexsync_c_" + name[len("lexsync_"):]
    # A fixed duration is a literal; one that varies per trial reads the loop-table
    # column, which OpenSesame exposes on `var`. Must match .osexp_event_block in
    # scripting.R, since the two engines write the same .osexp.
    ms = ("int(float(var.get(%s, _eval=False)))"
          % _pyq(clean_column(ev["ms_column"], "a jittered duration's `as`"))
          if ev.get("ms_column") else str(int(ev.get("ms", 0))))
    # The event ends half a frame before its duration is up. The next show() then waits
    # for the refresh that ends the duration, and lands on it, where sleeping the whole
    # duration would make it miss that refresh and wait for the next (OpenSesame's Timing
    # manual advises asking for slightly less than the interval wanted).
    end = f"_t0 + {ms} - _LEXSYNC_HALF_FRAME"
    trig = _trigger_expr(ev.get("trigger"))
    onset = [] if trig is None else [f"_lexsync_onset({trig}, _t0)"]
    if t == "text" and ev.get("respond"):
        # The stimulus collects its own response, from its onset. The keyboard is
        # flushed once the trigger is out, so nothing pressed before the stimulus counts,
        # and polled while the stimulus is shown. Without a key by its end, the screen
        # blanks and the keyboard is polled until the timeout has passed after it, so the
        # window is the one the stimulus and a separate response event had, timed from
        # the onset. A key ends the event either way, and does not cut its code short.
        respond = ev["respond"]
        keylist = ", ".join(_pyq(k) for k in respond["keys"])
        prepare = [f"{canvas} = Canvas()", f"{canvas}.text({_content_expr(ev)})",
                   f"{canvas}_blank = Canvas()"]
        body = [f"_t0 = {canvas}.show()", "var.onset_time = _t0", *onset,
                f"_kb = Keyboard(keylist=[{keylist}])",
                "_kb.flush()",
                f"_key, _t = _lexsync_key(_kb, {end})",
                "if _key is None:",
                f"    {canvas}_blank.show()",
                f"    _key, _t = _lexsync_key(_kb, _t0 + {ms} + "
                f"{_whole_ms(respond['timeout'])})",
                "var.response = _key",
                "var.response_time = u'' if _key is None else _t - _t0",
                "var.timed_out = 1 if _key is None else 0"]
        if scores:
            body += _osexp_correct("_key")
        return (_inline_block(name, "Show the stimulus and collect the response from its "
                              "onset", _osexp_block_guard(body, blocks), run=True,
                              prepare=_osexp_block_guard(prepare, blocks)), [name])
    if t in ("fixation", "text", "mask", "blank"):
        prepare = [f"{canvas} = Canvas()"]
        if t != "blank":
            prepare.append(f"{canvas}.text({_content_expr(ev)})")
        body = [f"_t0 = {canvas}.show()", "var.onset_time = _t0", *onset,
                f"_lexsync_wait({end})"]
        return (_inline_block(name, "Show stimulus and send onset-aligned trigger",
                              _osexp_block_guard(body, blocks), run=True,
                              prepare=_osexp_block_guard(prepare, blocks)),
                [name])
    if t == "region":
        trig = _trigger_expr(ev.get("crit_trigger"))
        # One canvas per region, in a list. Each region is timed from its own onset,
        # and the keyboard is flushed as it appears, so a key pressed before it cannot
        # advance it.
        prepare = [
            f"{canvas} = []",
            f"for _r in [r for r in {_text_expr(ev['field'])}"
            f".split({_pyq(ev.get('sep', '|'))}) if r != u'']:",
            "    _c = Canvas()",
            "    _c.text(_r)",
            f"    {canvas}.append(_c)",
        ]
        body = [
            # An empty cell, a sentence with no critical region, reads as 0: no trigger.
            "_crit = int(var.get(u'critical_region', 0, _eval=False) or 0)",
            f"_kb = Keyboard(keylist=[{_pyq(ev.get('key', 'space'))}], timeout=None)",
            "_rts = []",
            f"for _i, _c in enumerate({canvas}, start=1):",
            "    _t0 = _c.show()",
        ]
        if trig is not None:
            body.append(f"    if _i == _crit: _lexsync_onset({trig}, _t0)")
        body += ["    _kb.flush()",
                 "    _key, _t = _lexsync_key(_kb, None)",
                 "    _rts.append(u'%.1f' % (_t - _t0))",
                 "var.lexsync_region_rts = u'|'.join(_rts)"]
        return (_inline_block(name, "Self-paced reading region by region",
                              _osexp_block_guard(body, blocks), run=True,
                              prepare=_osexp_block_guard(prepare, blocks)), [name])
    if t == "question":
        prepare = [f"{canvas} = Canvas()", f"{canvas}.text({_text_expr(ev['field'])})"]
        body = [
            f"_t0 = {canvas}.show()",
            f"_kb = Keyboard(keylist=[{', '.join(_pyq(k) for k in ev.get('keys', ['f', 'j']))}])",
            "_kb.flush()",
            f"_key, _t = _lexsync_key(_kb, _t0 + {_whole_ms(ev.get('timeout', 5))})",
            "var.question_response = _key",
            "var.question_rt = u'' if _key is None else _t - _t0",
        ]
        if scores:
            body += _osexp_correct("_key")
        return (_inline_block(name, "Comprehension question",
                              _osexp_block_guard(body, blocks), run=True,
                              prepare=_osexp_block_guard(prepare, blocks)), [name])
    if t == "feedback":
        # The key comes from whichever response or question collected one last. The
        # answer column (or whichever column the event names) holds the KEY that is
        # correct, so scoring is a string comparison. A timeout is reported separately,
        # because on a timed task it means something different from a wrong key.
        # OpenSesame 4.x stores it as None and 3.3 as the string 'None', so both count
        # as no response. The response is not known until the trial runs, so all three
        # messages are prepared and the run phase shows one.
        prepare = [f"{canvas} = {{u'correct': Canvas(), u'incorrect': Canvas(), "
                   "u'no_response': Canvas()}"]
        prepare += [f"{canvas}[u'{key}'].text({_pyq(ev.get(key, default))})"
                    for key, default in (("correct", "Correct"), ("incorrect", "Incorrect"),
                                         ("no_response", "Too slow"))]
        body = [
            "_want = str(_lexsync_row().get(u'%s', u'')).strip()"
            % clean_column(ev.get("answer", "answer"), "a feedback event's `answer`"),
            "_got = var.get(u'%s', u'', _eval=False)" % feedback_scores,
            "_got = u'' if _got is None else str(_got).strip()",
            "if _got in (u'', u'None'): _msg = u'no_response'",
            "elif _got == _want: _msg = u'correct'",
            "else: _msg = u'incorrect'",
            f"_t0 = {canvas}[_msg].show()",
            f"_lexsync_wait({end})",
        ]
        return (_inline_block(name, "Practice feedback",
                              _osexp_block_guard(body, blocks), run=True,
                              prepare=_osexp_block_guard(prepare, blocks)), [name])
    if t == "response":
        keys = ";".join(ev.get("keys", ["left", "right"]))
        # A keyboard_response draws nothing, so the preceding canvas would stay up for
        # the whole response window. Blank it first, so the stimulus offsets at its own
        # duration as it does in the PsychoPy and jsPsych targets. The keyboard_response
        # runs no code of lexsync's, so a code still held is held out first.
        block = _inline_block(f"{name}_blank", "Clear the screen for the response window",
                              [f"{canvas}_blank.show()", "_lexsync_end_hold()"], run=True,
                              prepare=[f"{canvas}_blank = Canvas()"])
        block += [
            f"define keyboard_response {name}",
            "\tset timeout " + str(_whole_ms(ev.get("timeout", 2))),
            "\tset flush yes", "\tset duration keypress",
            '\tset description "Collect a response"',
            f'\tset allowed_responses "{keys}"', "",
        ]
        # The keyboard_response records the key and its time from the window's onset.
        # Whether it timed out, and whether the key was the trial's answer, are
        # recorded here, as the onset-locked script records them.
        score = ["_key = var.get(u'response', u'', _eval=False)",
                 "_timed_out = _key is None or str(_key).strip() in (u'', u'None')",
                 "var.timed_out = 1 if _timed_out else 0",
                 "if _timed_out:",
                 "    _key = None",
                 "    var.response_time = u''"]
        if scores:
            score += _osexp_correct("_key")
        block += _inline_block(f"{name}_score", "Record the timeout and the accuracy",
                               score, run=True)
        return (block, [f"{name}_blank", name, f"{name}_score"])
    raise ValueError(f"lexsync: unknown event type '{t}'.")


def _osexp_trial_start() -> list:
    """The inline script that opens every trial by clearing what the last one recorded.

    OpenSesame keeps a variable from one trial to the next, so a response event that
    does not run in a block would otherwise leave the previous trial's key in the log
    and for the feedback. Must match .osexp_trial_start in scripting.R.
    """
    body = ["var.%s = u''" % v for v in ("response", "response_time", "timed_out",
                                          "correct", "question_response", "question_rt",
                                          "lexsync_region_rts")]
    return _inline_block("lexsync_trial_start", "Clear the previous trial's responses",
                         body, run=True)


def _osexp_record() -> list:
    """The inline script that copies the trial's labels into the variables the logger
    writes.

    The labels stay out of the loop table, which OpenSesame evaluates, so the logger
    would not see them. Nothing reads these variables back, and both versions' loggers
    read without evaluation. Must match .osexp_record in scripting.R.
    """
    body = ["_row = _lexsync_row()",
            "var.lexsync_condition = _row.get(u'condition', u'')",
            "var.lexsync_block = _row.get(u'block', u'')",
            "var.lexsync_answer = _row.get(u'answer', u'')"]
    return _inline_block("lexsync_record", "Copy the trial's labels for the logger", body,
                         run=True)


def _inline_block(name: str, desc: str, body: list, run: bool,
                  prepare: list | None = None) -> list:
    """An inline_script item whose run phase is ``body`` and whose prepare phase is
    ``prepare``. A sequence runs the prepare phase of every item it holds before it runs
    any, so ``prepare`` is where a script builds what it shows. Must match
    .inline_block in scripting.R."""
    head = [f"define inline_script {name}", f'\tset description "{desc}"']
    if prepare:
        head += ["\t___prepare__", *["\t" + p for p in prepare], "\t__end__"]
    else:
        head.append('\tset _prepare ""')
    return [*head, "\t___run__", *["\t" + b for b in body], "\t__end__", ""]


def _osexp_timing(schema: dict) -> list:
    """The setup's lines that measure the display and time the events and their codes.

    The frame period is measured once, as the median of the 20 intervals between 21
    flips of a blank canvas. A median outside 1 to 50 ms, a refresh rate outside 20 to
    1000 Hz, is a failed measurement, such as a backend without a blocking flip gives,
    and ``presentation.assumed_refresh_hz`` stands in for it. The period is logged as
    ``lexsync_frame_ms``. An event ends half a period before its duration is up (see
    _osexp_event_block).

    The trigger device writes a code and returns. A code is held for
    ``triggers.trigger_hold_ms``, never less than _MIN_HOLD_MS, from the onset it marks:
    ``_lexsync_onset`` writes it and notes when it is due to be reset, and
    ``_lexsync_wait`` and ``_lexsync_key`` reset it on the way when that time comes no
    later than the time they wait for. A code that outlasts its event is therefore
    reset in a later event, without delaying any display, unless the next onset's code
    replaces it first, with a 0 written just before. Before a wait that runs no code of
    lexsync's, a keyboard_response, ``_lexsync_end_hold`` waits out the rest of the
    hold. ``_lexsync_marker`` sends a session marker and holds it. The legacy clock the
    experiment selects counts and sleeps whole milliseconds, so a hold that ends during
    a wait lasts within a millisecond of what is asked. One that ends while show()
    waits for the next refresh lasts until that display, up to a frame longer. One that
    ends after the last wait of a trial lasts until the next trial's first display.
    Must match .osexp_timing in scripting.R.
    """
    return [
        "_c = Canvas()",
        "_d = [_c.show() for _i in range(21)]",
        "_d = sorted(_b - _a for _a, _b in zip(_d, _d[1:]))",
        "_LEXSYNC_FRAME = (_d[9] + _d[10]) / 2.0",
        "if not 1.0 < _LEXSYNC_FRAME < 50.0:",
        "    _LEXSYNC_FRAME = 1000.0 / %.17g" % _refresh_hz(schema),
        "var.lexsync_frame_ms = _LEXSYNC_FRAME",
        "_LEXSYNC_HALF_FRAME = _LEXSYNC_FRAME / 2.0",
        "_LEXSYNC_HOLD = %.17g" % max(_trigger_hold_ms(schema), _MIN_HOLD_MS),
        "_lexsync_due = [None]",
        "def _lexsync_until(t):",
        "    _left = t - clock.time()",
        "    if _left > 0:",
        "        clock.sleep(_left)",
        "def _lexsync_onset(code, t0):",
        "    if _lexsync_due[0] is not None:",
        "        send_trigger(0)",
        "    send_trigger(code)",
        "    _lexsync_due[0] = t0 + _LEXSYNC_HOLD",
        "def _lexsync_reset():",
        "    send_trigger(0)",
        "    _lexsync_due[0] = None",
        "def _lexsync_wait(t):",
        "    if _lexsync_due[0] is not None and _lexsync_due[0] <= t:",
        "        _lexsync_until(_lexsync_due[0])",
        "        _lexsync_reset()",
        "    _lexsync_until(t)",
        "def _lexsync_key(kb, t):",
        "    if _lexsync_due[0] is not None and (t is None or _lexsync_due[0] <= t):",
        "        _left = _lexsync_due[0] - clock.time()",
        "        if _left > 0:",
        "            _key, _t = kb.get_key(timeout=_left)",
        "            if _key is not None:",
        "                return _key, _t",
        "        _lexsync_reset()",
        "    return kb.get_key(timeout=None if t is None else max(0, t - clock.time()))",
        "def _lexsync_end_hold():",
        "    if _lexsync_due[0] is not None:",
        "        _lexsync_until(_lexsync_due[0])",
        "        _lexsync_reset()",
        "def _lexsync_marker(code):",
        "    _lexsync_onset(code, clock.time())",
        "    _lexsync_end_hold()",
    ]


def _osexp_trigger_device(settings: dict, address: str) -> list:
    """The setup's lines that open the trigger device, as triggers.mode and
    triggers.backend ask (see _trigger_settings).

    Only the configured backend's branch is written, and a serial device is opened by
    the name the schema gives, never as the first serial port found. When the device
    cannot be opened, ``hardware`` stops the experiment before anything is shown, and
    ``auto`` falls back to printing the codes. ``_lexsync_no_codes`` is left holding the
    reason no codes will be sent, or None when they go to the device, for the notice
    (_osexp_trigger_notice). ``lexsync_trigger_mode``, which the logger writes with
    every trial, says ``hardware`` or ``mock``, and ``test_mode`` says ``yes`` when the
    codes are printed instead. Must match .osexp_trigger_device in scripting.R.
    """
    if settings["backend"] == "serial":
        record = ["var.trigger_backend = u'serial'"]
        opening = ["        import serial",
                   "        _sp = serial.Serial(%s, %d)" % (_pyq(settings["serial_port"]),
                                                          settings["baudrate"]),
                   "        def send_trigger(code):",
                   "            _sp.write(int(code).to_bytes(1, 'big'))"]
    else:
        record = ["var.trigger_backend = u'parallel'",
                  f"var.parallel_port_address = {address}"]
        opening = ["        from ctypes import windll",
                   "        _io = windll.dlportio",
                   "        _addr = int(var.parallel_port_address)",
                   "        def send_trigger(code):",
                   "            _io.DlPortWritePortUchar(_addr, int(code))"]
    return [
        *record,
        "var.test_mode = u'no'",
        "def _printer(code):",
        "    print(u'[lexsync test trigger] %d' % int(code))",
        "send_trigger = _printer",
        "_lexsync_mode = %s" % _pyq(settings["mode"]),
        "_lexsync_device = %s" % _pyq(_trigger_device(settings, address)),
        "_lexsync_no_codes = None",
        "if _lexsync_mode == u'mock':",
        "    _lexsync_no_codes = u'triggers.mode is mock'",
        "else:",
        "    try:",
        *opening,
        "        send_trigger(0)",
        "    except Exception as _exc:",
        "        if _lexsync_mode == u'hardware':",
        "            raise RuntimeError(u'lexsync: %s could not be opened (%s: %s). "
        "triggers.mode is hardware, so the experiment does not run without it.' % "
        "(_lexsync_device, type(_exc).__name__, _exc))",
        "        print(u'lexsync: %s could not be opened (%s: %s).' % "
        "(_lexsync_device, type(_exc).__name__, _exc))",
        "        send_trigger = _printer",
        "        _lexsync_no_codes = u'%s could not be opened' % _lexsync_device",
        "var.lexsync_trigger_mode = u'hardware' if _lexsync_no_codes is None else u'mock'",
        "if _lexsync_no_codes is not None:",
        "    var.test_mode = u'yes'",
        "    print(u'lexsync: no trigger codes will be sent, because %s. Each code is "
        "printed here instead.' % _lexsync_no_codes)",
    ]


def _osexp_trigger_notice() -> list:
    """The inline script that tells the experimenter that no trigger codes will be sent.

    It runs just after the setup, before any screen the participant sees, shows the
    reason the setup found and waits for C. Escape stops the session. When the codes go
    to the device, it shows nothing. The reason is a device name the schema's check
    allows or the mode, so it holds nothing OpenSesame's canvas would read as markup.
    Must match .osexp_trigger_notice in scripting.R.
    """
    body = [
        "if _lexsync_no_codes is not None:",
        "    c = Canvas()",
        "    c.text(u'No trigger codes will be sent, because %s. Each code is printed in "
        "the console instead.<br /><br />Press C to continue without triggers, or escape "
        "to stop.' % _lexsync_no_codes)",
        "    c.show()",
        "    _key, _t = Keyboard(keylist=[u'c', u'escape'], timeout=None).get_key()",
        "    if _key == u'escape':",
        "        raise RuntimeError(u'lexsync: stopped at the trigger notice, because no "
        "trigger codes would be sent.')",
    ]
    return _inline_block("lexsync_trigger_notice", "Say when no trigger codes will be sent",
                         body, run=True)


def _osexp_markers() -> list:
    """The two inline scripts that send the session markers, 254 just before the loop
    and 255 just after it, each held for the hold, as the PsychoPy script sends them.
    Must match .osexp_markers in scripting.R."""
    return (_inline_block("lexsync_session_start", "Mark the start of the trials with 254",
                          ["_lexsync_marker(254)"], run=True)
            + _inline_block("lexsync_session_end", "Mark the end of the trials with 255",
                            ["_lexsync_marker(255)"], run=True))


def _osexp_version_check(version: int, n_versions: int, order: int = 1,
                         n_orders: int = 1) -> list:
    """The inline script that checks the subject number against this file's version.

    A design with several presentation versions gets one experiment per version, and
    the experimenter opens the participant's. OpenSesame asks for a subject number at
    start-up, and participant p normally runs version ((p - 1) mod V) + 1. When the
    number belongs to another version, this shows a screen saying so and waits for a
    key. Space goes on with this file, and escape stops the session. It runs before the
    loop, so the experiment needs no run-if condition, a syntax that differs between
    OpenSesame 3.3 and 4.x. With ``n_orders`` above 1, each experiment is one order of
    one version, and participant p normally runs order (((p - 1) div V) mod m) + 1, which
    the check compares too. Must match .osexp_version_check in scripting.R.
    """
    if n_orders > 1:
        return _inline_block(
            "lexsync_version_check",
            "Warn when the subject number belongs to another version or order", [
                f"_version = {int(version)}",
                f"_versions = {int(n_versions)}",
                f"_order = {int(order)}",
                f"_orders = {int(n_orders)}",
                "try:",
                "    _p = int(var.get(u'subject_nr', 0, _eval=False))",
                "except (TypeError, ValueError):",
                "    _p = 0",
                "_expected = (_p - 1) % _versions + 1",
                "_expected_order = (_p - 1) // _versions % _orders + 1",
                "if (_expected, _expected_order) != (_version, _order):",
                "    c = Canvas()",
                "    c.text(u'Participant %d would normally run version %d in order %d, and "
                "this file runs version %d in order %d. Press space to continue with this "
                "one or escape to stop.' % (_p, _expected, _expected_order, _version, "
                "_order))",
                "    c.show()",
                "    _key, _t = Keyboard(keylist=[u'space', u'escape'], timeout=None).get_key()",
                "    if _key == u'escape':",
                "        raise RuntimeError(u'lexsync: stopped at the version check, because "
                "participant %d would normally run version %d in order %d.' % (_p, "
                "_expected, _expected_order))",
            ], run=True)
    body = [
        f"_version = {int(version)}",
        f"_versions = {int(n_versions)}",
        "try:",
        "    _p = int(var.get(u'subject_nr', 0, _eval=False))",
        "except (TypeError, ValueError):",
        "    _p = 0",
        "_expected = (_p - 1) % _versions + 1",
        "if _expected != _version:",
        "    c = Canvas()",
        "    c.text(u'Participant %d would normally run version %d, and this file runs "
        "version %d. Press space to continue with this one or escape to stop.' "
        "% (_p, _expected, _version))",
        "    c.show()",
        "    _key, _t = Keyboard(keylist=[u'space', u'escape'], timeout=None).get_key()",
        "    if _key == u'escape':",
        "        raise RuntimeError(u'lexsync: stopped at the version check, because "
        "participant %d would normally run version %d.' % (_p, _expected))",
    ]
    return _inline_block("lexsync_version_check",
                         "Warn when the subject number belongs to another version", body,
                         run=True)


def _osexp_html(text: str) -> str:
    """Text for OpenSesame's canvas, which reads a subset of HTML: &, < and > escaped, and
    each line break written as <br />. Mirrors .osexp_html in scripting.R."""
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace("\n", "<br />"))


def _osexp_instructions(text: str) -> list:
    """The inline script that shows the instructions and waits for the space bar.

    It runs once, before the loop, so the participant reads at their own pace and the
    first trial starts on the space bar, which also lets the experimenter start the run.
    Escape stops the session, as it does at the version check. The text is written into
    the script as a _pyq literal, which escapes its line breaks, so it cannot add a line
    to the experiment. Must match .osexp_instructions in scripting.R.
    """
    body = ["c = Canvas()",
            "c.text(%s)" % _pyq(_osexp_html(text) + "<br /><br />" + _START_PROMPT),
            "c.show()",
            "_key, _t = Keyboard(keylist=[u'space', u'escape'], timeout=None).get_key()",
            "if _key == u'escape':",
            "    raise RuntimeError(u'lexsync: stopped at the instructions.')"]
    return _inline_block("lexsync_instructions",
                         "Show the instructions and wait for the space bar", body, run=True)


def build_osexp(design: dict, conditions_file: str, schema: dict, rendered: list,
                font: str = "mono", text_file: str | None = None,
                version: int | None = None, n_versions: int | None = None,
                instructions: str | None = None, order: int = 1,
                n_orders: int = 1) -> str:
    """The plain text of an OpenSesame experiment for a rendered event list.

    ``conditions_file`` names the loop table and ``text_file`` its companion text
    table, which defaults to the loop table's name with ``_text`` before ``.csv``.
    Both are looked up through OpenSesame's file pool, which also searches the
    experiment's own folder. ``version`` and ``n_versions`` mark the experiment as
    version ``version`` of ``n_versions``, and ``order`` and ``n_orders`` as trial order
    ``order`` of ``n_orders``. With more than one version or order, the experiment
    checks OpenSesame's subject number against its own before the loop and warns when
    the participant would normally run another. With more than one order, it also sets
    ``lexsync_order``, which every trial logs. It then shows ``instructions`` and
    waits for the space bar. By default they are list 1's instructions, the design's own
    text or lexsync's for its task. Each trial starts by clearing the last trial's
    responses and ends with a logger item. The setup script opens the trigger device
    the schema names (see _osexp_trigger_device), measures the frame period and defines
    the helpers that time the events and hold their codes (see _osexp_timing). A notice
    follows it when no codes will be sent, and the session markers 254 and 255 are sent
    just before and after the loop. Every text is drawn at
    ``presentation.text_height_px``. A ``response`` event collected from the offset,
    which becomes a keyboard_response, is refused when it carries ``blocks``, since the
    block restriction is applied only within lexsync's inline scripts. Restrict a
    feedback or stimulus event instead. Must match build_osexp in scripting.R.
    """
    if instructions is None:
        instructions = _instructions(design, _response_mapping(design))
    addr = clean_port((schema.get("triggers") or {}).get("parallel_address", "0x378"))
    design_name = clean_meta(design["name"], "the design's `name`")
    language = clean_meta(design["language"], "the design's `language`")
    # `set font_family <font>` takes the value unquoted on its own line, so it is
    # guarded here rather than at the caller: an .osexp is line-oriented and a newline
    # would add items to the experiment.
    font = clean_meta(font, "the font")
    if text_file is None:
        text_file = re.sub(r"\.csv$", "", conditions_file) + "_text.csv"

    setup = [
        # The trial texts, read as data with the csv module and keyed by the loop's
        # `lexsync_row` (not by the loop's position, which a user who switches the loop
        # to random order would change). utf-8-sig also reads a copy that a spreadsheet
        # saved with a byte-order mark.
        "import csv as _csv",
        "with open(pool[%s], encoding=u'utf-8-sig', newline=u'') as _f:" % _pyq(text_file),
        "    _LEXSYNC_ROWS = {int(_r[u'lexsync_row']): _r for _r in _csv.DictReader(_f)}",
        "def _lexsync_row():",
        "    return _LEXSYNC_ROWS[int(var.get(u'lexsync_row', _eval=False))]",
        # The device writes a code and returns, and the scripts reset it when its hold is
        # up (see _osexp_timing). Sleeping 10 ms and resetting the code itself would make
        # every triggered event overrun by those 10 ms and ignore the schema's hold.
        *_osexp_trigger_device(_trigger_settings(schema), addr),
        *_osexp_timing(schema),
    ]

    # var.correct scores the response, or the question in a design with no response
    # event, as the PsychoPy data file does.
    has_response = any(ev["type"] == "response" or ev.get("respond") for ev in rendered)
    event_blocks, run_names = _osexp_trial_start(), ["lexsync_trial_start"]
    last = "response"
    for i, ev in enumerate(rendered):
        collects = "response" if (ev["type"] == "response" or ev.get("respond")) else (
            "question" if ev["type"] == "question" else None)
        block, names = _osexp_event_block(
            f"lexsync_e{i}", ev,
            scores=collects == ("response" if has_response else "question"),
            feedback_scores="question_response" if last == "question" else "response")
        event_blocks.extend(block)
        run_names.extend(names)
        last = collects or last
    # OpenSesame logs nothing without a logger item. This one runs last in every trial
    # and writes every variable, the labels copied in just before it included.
    event_blocks += _osexp_record() + [
        "define logger lexsync_logger", '\tset description "Log the trial"',
        "\tset auto_log yes", ""]
    run_names += ["lexsync_record", "lexsync_logger"]

    header = [
        "---", "API: 2.1", "OpenSesame: 3.3.14", "Platform: nt", "---",
        "set width 1024", "set uniform_coordinates yes",
        f'set title "lexsync: {design_name} ({language})"',
        "set subject_nr 0", "set start lexsync_experiment",
        "set sound_sample_size -16", "set sound_freq 48000", "set sound_channels 2",
        "set sound_buf_size 1024", "set sampler_backend legacy", "set round_decimals 2",
        "set mouse_backend legacy", "set keyboard_backend legacy", "set height 768",
        # OpenSesame takes full screen from the mode it is launched in, whatever this
        # line says. font_size is the size of every text the experiment shows.
        "set fullscreen no", "set foreground white",
        f"set font_size {_text_height_px(schema)}",
        f"set font_family {font}", 'set description "Generated by lexsync"',
        "set coordinates uniform", "set compensation 0", "set color_backend legacy",
        "set clock_backend legacy", "set canvas_backend xpyriment", "set background black",
        # The trial order this experiment presents, logged with every trial.
        *([f"set lexsync_order {int(order)}"] if n_orders > 1 else []), "",
        "define inline_script lexsync_trigger_setup",
        '\tset description "Load the trial texts and open the trigger device"',
        '\tset _run ""', "\t___prepare__", *["\t" + s for s in setup], "\t__end__", "",
    ]
    checked = version is not None and n_versions is not None and (
        int(n_versions) > 1 or n_orders > 1)
    check = _osexp_version_check(version, n_versions, order, n_orders) if checked else []
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
        "\trun lexsync_trigger_setup always",
        "\trun lexsync_trigger_notice always",
        *(["\trun lexsync_version_check always"] if checked else []),
        "\trun lexsync_instructions always",
        "\trun lexsync_session_start always",
        "\trun lexsync_loop always",
        "\trun lexsync_session_end always", "",
    ]
    return "\n".join(header + _osexp_trigger_notice() + check
                     + _osexp_instructions(instructions) + _osexp_markers() + event_blocks
                     + trial)


def export_opensesame(stimuli, design, schema, outdir, base=None) -> str:
    """Write complete plain-text OpenSesame experiments and the two tables each reads.

    ``<base>.osexp`` loops over ``<base>_opensesame.csv``, which holds numbers only:
    ``lexsync_row`` (the trial's position in loop order, from 1), ``lexsync_trial``,
    ``lexsync_list``, ``replicate`` in a resampled design, ``lexsync_set``, the trigger
    codes, ``critical_region`` and any per-trial duration. The presented text,
    ``condition``, ``block``, ``answer`` and, with ``counterbalance.orders``,
    ``order_1`` to ``order_m`` are in ``<base>_opensesame_text.csv``, which the inline
    scripts read with Python's ``csv`` module, so OpenSesame never evaluates them. Copy
    both tables with the experiment.

    Before the loop, an inline script, ``lexsync_instructions``, shows the design's
    ``instructions``, or lexsync's for its task, and waits for the space bar. Every
    trial is logged. A response after a text event is collected by that event's
    script from the stimulus's onset, which sets ``response``, ``response_time``,
    ``timed_out`` and ``correct``. A response kept after the stimulus with
    ``from: offset`` is a keyboard_response, and a script after it sets ``timed_out``
    and ``correct``. Such a response cannot be restricted to ``blocks``: a design that
    restricts one is refused here, although the PsychoPy and jsPsych targets accept
    it. Self-paced reading sets ``lexsync_region_rts`` and a question
    ``question_response`` and ``question_rt``. A script clears these as each trial
    starts, another copies the trial's labels into ``lexsync_condition``,
    ``lexsync_block`` and ``lexsync_answer``, and a logger item ends the trial.

    Every canvas a trial shows is built before the trial runs, in the prepare phase of
    its script, and each event is timed from the onset its display returns. An event
    ends half a frame before its duration is up, so that the next display lands on
    the refresh that ends it. The frame period is measured at start-up and logged as
    ``lexsync_frame_ms``, with ``presentation.assumed_refresh_hz`` as the fallback when
    the measurement fails. Each trigger code is held for ``triggers.trigger_hold_ms``,
    at least 10 ms, through the events after it when its own is shorter, unless the
    next onset's code replaces it first. The session markers, 254 and 255, are sent
    just before the first trial and just after the last, held the same way.

    The setup writes the codes to the parallel port at ``triggers.parallel_address`` or,
    with ``triggers.backend: serial``, as single bytes to ``triggers.serial_port`` at
    ``triggers.baudrate``. When that device cannot be opened, ``triggers.mode: auto``
    prints the codes instead. An inline script, ``lexsync_trigger_notice``, then says
    so before any other screen and waits for the C key. ``hardware`` stops the
    experiment there, and ``mock`` prints the codes without trying the device, after the
    same notice. Every trial logs ``lexsync_trigger_mode``, ``hardware`` or ``mock``.
    Text is drawn ``presentation.text_height_px`` pixels high, OpenSesame's
    ``font_size``, and OpenSesame takes full screen from the mode it is launched in.

    A design with more than one presentation version (see
    ``presentation_versions``) gets one experiment per version instead, each with
    its own two tables holding only that version's trials: ``<base>_list<k>.osexp``, or
    ``<base>_rep<r>_list<k>.osexp`` when the versions span several replicates. Each one
    checks OpenSesame's subject number at start-up and shows a warning when that
    participant would normally run another version. A design with
    ``counterbalance.orders: m`` gets one experiment per version and order,
    ``<base>_list<k>_order<j>.osexp`` (``<base>_order<j>.osexp`` for a single version),
    each with tables sorted by its order, a ``lexsync_order`` variable that every trial
    logs, and a check that compares the participant's order too, order
    ``(((p - 1) div V) mod m) + 1``. ``export_experiments`` lists every file written.

    OpenSesame evaluates the cells of a loop table: in 4.x a cell holding ``{`` runs as
    a Python f-string, and in 3.3 a cell starting with ``=`` or holding ``[=...]`` runs
    as Python. A value in a numeric column that is not a plain number is therefore
    refused, naming the column. An empty cell passes. These rules were checked against
    the sources of OpenSesame 3.3.14 and 4.1.20.

    Args:
        stimuli (pandas.DataFrame): Stimuli with trigger columns (see
            ``lexsync.scripting.assign_triggers``).
        design (dict): A parsed design configuration.
        schema (dict): The parsed global schema (trigger and presentation settings).
        outdir (str): Output directory.
        base (str, optional): File-name stem, by default
            ``lexsync.design.design_stem(design)``, built from the design's name and
            language.

    Returns:
        The path to the generated ``.osexp``, version 1's when there are several.
    """
    return _opensesame_files(stimuli, design, schema, outdir, base)[0][0]


def _opensesame_files(stimuli, design, schema, outdir, base=None) -> tuple:
    """Write the OpenSesame experiments and their tables, one experiment per version.

    Returns ``(experiments, tables)``: the ``.osexp`` paths in version order, and each
    version's loop table and text table in the same order. Every table is checked
    before anything is written, so a refused value leaves no partial set behind.
    """
    base = base or design_stem(design)
    events = resolve_events(design)
    # Sized from every version's trials, so each version's experiment shows one mask.
    rendered = _sized_masks(
        render_events(events, design.get("timing") or {}, _refresh_hz(schema)), stimuli)
    presentation = schema.get("presentation") or {}
    font = design.get("font") or presentation.get("opensesame_font") or "mono"
    versions = presentation_versions(stimuli)
    texts = _instruction_texts(design, versions)
    n_orders = _n_orders(stimuli)
    if len(versions) <= 1 and n_orders == 1:
        # One version, in one order, is written under the bare stem.
        parts = [(base, stimuli, None, texts[0] if texts else None, 1)]
    else:
        by_replicate = _spans_replicates(versions)
        parts = []
        for k, v in enumerate(versions):
            stem = (base if len(versions) == 1
                    else f"{base}_rep{v['replicate']}_list{v['list']}" if by_replicate
                    else f"{base}_list{v['list']}")
            rows = _version_rows(stimuli, v)
            if n_orders == 1:
                parts.append((stem, rows, v, texts[k], 1))
                continue
            # OpenSesame's loop presents its table in file order, so each order of a
            # version is an experiment of its own, its tables sorted by that order.
            for j in range(1, n_orders + 1):
                parts.append((f"{stem}_order{j}", _rows_in_order(rows, j), v, texts[k], j))
    written = []
    for stem, rows, v, instructions, order in parts:
        numbers, text = _opensesame_tables(rows, events)
        csv_name, text_name = f"{stem}_opensesame.csv", f"{stem}_opensesame_text.csv"
        osexp = build_osexp(design, csv_name, schema, rendered, font=font, text_file=text_name,
                            version=None if v is None else v["version"],
                            n_versions=len(versions), instructions=instructions,
                            order=order, n_orders=n_orders)
        written.append((stem, csv_name, text_name, numbers, text, osexp))
    experiments, tables = [], []
    for stem, csv_name, text_name, numbers, text, osexp in written:
        write_csv_utf8(numbers, os.path.join(outdir, csv_name))
        write_csv_utf8(text, os.path.join(outdir, text_name))
        experiments.append(_write_text(osexp, os.path.join(outdir, f"{stem}.osexp")))
        tables += [os.path.join(outdir, csv_name), os.path.join(outdir, text_name)]
    return experiments, tables


# BCP 47 tags for some human-readable language labels the designs carry: those of the
# lexica lexsync ships and a few other European languages. Any other label that is not
# itself tag-shaped becomes "und" (see _language_tag), so a design in another language
# states `language_tag`.
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
    # The shape check applies to a STATED tag too: returned verbatim,
    # `language_tag: 'en"><script>...'` would reach the lang attribute of the generated
    # HTML intact, and it is the one input to this function that an attacker would
    # actually choose.
    tag = str(design.get("language_tag") or "").strip()
    if tag:
        return tag if _BCP47_SHAPE.match(tag) else "und"
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
        if "respond" in e:
            e["respond"] = dict(e["respond"],
                                keys=[_JSPSYCH_KEYS.get(k, k) for k in e["respond"]["keys"]])
        out.append(e)
    return out


def _map_answers_for_jspsych(trials: pd.DataFrame) -> pd.DataFrame:
    """The loop table with each trial's ``answer`` named as the browser names the key.

    jsPsych records the key pressed by the browser's name for it, so a press of the left
    arrow is recorded as ``arrowleft``, the name the page's events give the key (see
    _map_keys_for_jspsych). The loop tables name it ``left``, as PsychoPy and OpenSesame
    record it. The page's answers are named as its keys are, so a correct response equals
    its trial's answer, in the data rows and on the feedback screen. The spaces the
    runners ignore around an answer are ignored here too. Mirrors .map_answers_jspsych in
    scripting.R.
    """
    if "answer" not in trials.columns:
        return trials
    out = trials.copy()
    out["answer"] = [_JSPSYCH_KEYS.get(v.strip(" \t\r\n"), v) if isinstance(v, str) else v
                     for v in out["answer"]]
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
            # frame by rows, so the two engines embed the same JSON and no bare NaN,
            # which is not valid JSON, reaches it. A trial with no correct answer (a
            # main-block trial in a design whose practice items carry one) has none, so
            # omitting the field is also the honest rendering.
            return {k: integral(v) for k, v in o.items()
                    if v is not None and not (isinstance(v, float) and v != v)}
        if isinstance(o, list):
            return [integral(v) for v in o]
        return o
    return json.dumps(integral(obj), separators=(",", ":"), ensure_ascii=False)


def _fifteen_digits(value):
    """A trial's number as the R engine's jsonlite::toJSON(digits = I(15)) writes it.

    jsonlite writes a double to 15 significant digits, dropping the last digits of a
    value such as 1000 / 30, so the double nearest that 15-digit decimal is embedded
    here, and json.dumps then writes the same digits. jsonlite's default of four
    decimal places would write 33.3333 for an item table's 33.333333, so the R engine
    asks for 15 digits. Must match the TRIALS_JSON line of export_jspsych in
    scripting.R.
    """
    if isinstance(value, float) and math.isfinite(value):
        return float("%.15g" % value)
    return value


def _json_html(obj) -> str:
    """JSON safe to embed inside an HTML <script> (escape <, >, & and JS line seps)."""
    return (_json_r(obj).replace("<", "\\u003c").replace(">", "\\u003e")
            .replace("&", "\\u0026").replace(" ", "\\u2028").replace(" ", "\\u2029"))


def export_jspsych(stimuli, design, schema, outdir, base=None) -> str:
    """Write ``<base>.html``, a browser-runnable jsPsych experiment from the event list, and return its path.

    The same rendered events and the trial data are embedded in one HTML file, so
    anyone can reproduce the exact procedure online from the same materials. The
    jsPsych library, its keyboard-response plugin and its stylesheet are loaded from a
    CDN, so the machine running the file needs an internet connection; the trial data
    are embedded and the responses are saved locally, so no server is required either
    to run it or to collect them.
    Each of the three files carries its SHA-384 as Subresource Integrity, so a browser
    refuses a copy that differs from the published release. Stimuli are drawn
    ``presentation.text_height_px`` pixels high, 48 by default.
    Onset triggers are recorded in each trial's data (a browser cannot drive a
    parallel port); online EEG synchronisation needs WebSerial/LSL or a photodiode.
    A stimulus that collects its response is one trial, recorded as ``target``: it
    accepts the keys from its onset, shows the stimulus for its duration and stays
    open for the timeout after it, a key ends it, and ``rt`` runs from the onset.

    The page embeds every presentation version (see ``presentation_versions``) and
    runs one, named in its address: ``?version=K``, ``?list=K`` when there are no
    replicates, or ``?participant=N``, whose version is ``((N - 1) mod V) + 1``. A page
    with more than one version, opened with none of these, shows a screen naming them
    and runs nothing. With ``counterbalance.orders: m`` the page presents the version in
    order ``(((N - 1) div V) mod m) + 1``, or in order 1 without a participant number,
    and every data row carries the order. Its welcome screen shows the version's instructions, the design's
    ``instructions`` or lexsync's for its task, and waits for the space bar. The data
    rows carry the participant, the version, the list and the replicate, and the data
    file is named after the participant and the version. The page names the keys as the
    browser does, ``arrowleft`` for ``left``, in its events and in each trial's
    ``answer``, so a recorded response can be compared with the answer as it stands.
    """
    base = base or design_stem(design)
    events = resolve_events(design)
    rendered = _map_keys_for_jspsych(_sized_masks(
        render_events(events, design.get("timing") or {}, _refresh_hz(schema)), stimuli))
    versions = presentation_versions(stimuli)
    trials = [{key: _fifteen_digits(value) for key, value in row.items()}
              for row in _map_answers_for_jspsych(
                  loop_table(stimuli, events)).to_dict(orient="records")]
    presentation = schema.get("presentation") or {}
    font = design.get("font") or presentation.get("font") or "Courier New"
    with open(find_template("jspsych/experiment_template.html"), encoding="utf-8") as handle:
        tmpl = handle.read()
    # DESIGN lands in <title> and a comment, LANGUAGE_TAG in a lang attribute, WORD_FONT
    # inside a CSS font-family declaration. Only the JSON blobs, the instructions among
    # them, are escaped by _json_html; the rest are validated, since a quote or an angle
    # bracket in any of them would leave its attribute or rule and start markup in a page
    # that collects participant responses.
    subs = {
        "DESIGN": clean_meta(design["name"], "the design's `name`"),
        "LANGUAGE": clean_meta(design["language"], "the design's `language`"),
        "LANGUAGE_TAG": _language_tag(design), "WORD_FONT": clean_meta(font, "the font"),
        "TEXT_HEIGHT_PX": str(_text_height_px(schema)),
        "EVENTS_JSON": _json_html(rendered), "TRIALS_JSON": _json_html(trials),
        "VERSIONS_JSON": _json_html(versions),
        "ORDERS": str(_n_orders(stimuli)),
        "INSTRUCTIONS_JSON": _json_html(_instruction_texts(design, versions)),
    }
    for k, v in subs.items():
        tmpl = tmpl.replace("{{" + k + "}}", str(v))
    return _write_text(tmpl.rstrip("\n"), os.path.join(outdir, f"{base}.html"))


# ---- Instructions and the response mapping --------------------------------------------
#
# Every experiment shows instructions and waits for the space bar before its first trial.
# A design may give its own text, which travels as data: JSON in the PsychoPy script and
# the jsPsych page, and a _pyq literal in the OpenSesame script. Without one, lexsync
# writes English instructions for the tasks it knows. The loop tables carry each trial's
# correct key in `answer`, taken from the response mapping where the trial names none.

# The prompt every target shows below the instructions. It and the runners' other
# messages are in English. Must match both templates and .START_PROMPT in scripting.R.
_START_PROMPT = "Press the space bar to begin."

# What instructions may not hold: every control character but the line feed, and the two
# Unicode separators, which end a line in JavaScript before ES2019 and in Python's
# str.splitlines(), so they could split the OpenSesame script the text is written into.
# Must match the code-point test in .design_instructions in scripting.R.
_INSTRUCTION_CONTROL = re.compile("[\x00-\x09\x0b-\x1f\x7f-\x9f  ]")

# The names the instructions give the keys that are more than one character.
_KEY_LABELS = {"space": "the space bar", "left": "the left arrow key",
               "right": "the right arrow key", "up": "the up arrow key",
               "down": "the down arrow key", "return": "the Enter key"}

_MAPPING_SHAPE = ("lexsync: response_mapping must map each condition to one response key, "
                  "as in {word: f, pseudoword: j}.")


def _key_label(key) -> str:
    """A response key as the instructions and the Methods text name it.

    A single character is upper-cased, as a keyboard prints it (F, J, 1), and the arrow
    keys, the space bar and Enter are named. Any other key is "the <name> key". Key names
    are ASCII (see clean_key), so the two engines upper-case them alike. Mirrors
    .key_label in scripting.R.
    """
    key = str(key)
    if key in _KEY_LABELS:
        return _KEY_LABELS[key]
    return key.upper() if len(key) == 1 else "the %s key" % key


def _join_words(parts, conjunction: str) -> str:
    """Words joined as a list in prose: "a", "a or b", "a, b or c". Mirrors .join_words
    in scripting.R."""
    parts = [str(p) for p in parts]
    if len(parts) < 2:
        return "".join(parts)
    return "%s %s %s" % (", ".join(parts[:-1]), conjunction, parts[-1])


def _first_event(events: list, kind: str):
    """The first event of a type, or None."""
    return next((ev for ev in events if ev.get("type") == kind), None)


def _response_keys(design: dict):
    """The keys the design's first response event allows, or None without one."""
    ev = _first_event(resolve_events(design), "response")
    return None if ev is None else _keys_of(ev, ["left", "right"])


def _design_instructions(design: dict):
    """The design's own `instructions`, checked, or None when it gives none.

    Free text, which may hold line breaks and no other control character. Spaces and line
    breaks at either end are trimmed, so the closing line break of a YAML block scalar adds
    no empty line. Must stay identical to .design_instructions in scripting.R.
    """
    value = design.get("instructions")
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("lexsync: the design's `instructions` must be text.")
    bad = _INSTRUCTION_CONTROL.search(value)
    if bad:
        raise ValueError("lexsync: the design's `instructions` contain the control character "
                         "U+%04X; only line breaks are allowed." % ord(bad.group(0)))
    text = value.strip(" \n")
    if not text:
        raise ValueError("lexsync: the design's `instructions` are empty; write the text or "
                         "leave the key out.")
    return text


def _response_mapping(design: dict):
    """The design's response mapping, ``{condition: key}``, or None when it has none.

    A design's own `response_mapping` maps each condition to a key that its first response
    event allows. Without one, a lexical decision maps word to that event's first key and
    pseudoword to its second, the order in which its practice table codes them, so its
    main trials can be scored. No other paradigm has a default. Must stay identical to
    .response_mapping in scripting.R.
    """
    keys = _response_keys(design)
    given = design.get("response_mapping")
    if given is None:
        if (design.get("paradigm") == "lexical_decision" and keys is not None
                and len(keys) >= 2):
            return {"word": keys[0], "pseudoword": keys[1]}
        return None
    if not isinstance(given, dict) or not given:
        raise ValueError(_MAPPING_SHAPE)
    if keys is None:
        raise ValueError("lexsync: the design gives `response_mapping`, but none of its events "
                         "is a response whose keys it could name.")
    out = {}
    for cond, key in given.items():
        if isinstance(key, bool) or not isinstance(key, (str, numbers.Real)):
            raise ValueError(_MAPPING_SHAPE)
        key = clean_key(key, "a key in response_mapping")
        if key not in keys:
            raise ValueError("lexsync: response_mapping maps '%s' to '%s', but the response "
                             "event allows only %s."
                             % (_key_name(cond), key, _join_words(keys, "and")))
        out[_key_name(cond)] = key
    return out


def _rotates(design: dict) -> bool:
    """Whether the design rotates its response mapping across lists, checked."""
    value = design.get("rotate_mapping_by_list")
    if value is None:
        return False
    if not isinstance(value, bool):
        raise ValueError("lexsync: rotate_mapping_by_list must be true or false.")
    return value


def _list_mapping(design: dict, mapping, lst):
    """The response mapping in list ``lst``.

    Rotated, list k moves each key k - 1 places along the response event's keys, so with
    two keys every even-numbered list swaps them. Mirrors .list_mapping in scripting.R.
    """
    if mapping is None or not _rotates(design):
        return mapping
    keys = _response_keys(design)
    return {c: keys[(keys.index(k) + int(lst) - 1) % len(keys)] for c, k in mapping.items()}


def _check_instructions_and_mapping(design: dict) -> None:
    """Refuse instructions, a response mapping or a rotation the experiments cannot carry.

    validate_design calls this. Mirrors .check_instructions_and_mapping in scripting.R.
    """
    _design_instructions(design)
    mapping = _response_mapping(design)
    if _rotates(design) and mapping is None:
        raise ValueError("lexsync: rotate_mapping_by_list rotates a response mapping, and the "
                         "design has none; give `response_mapping`.")


def _default_instructions(design: dict, mapping) -> tuple:
    """lexsync's English instructions for a design that gives none, and whether they say
    what every key the participant presses means.

    A lexical decision names the keys its mapping gives word and pseudoword. A
    categorisation says that the first key of its response means yes and the second no,
    and a comprehension question says the same of its keys. Self-paced reading names the
    key that shows the next part. Any other response is only named, so the text cannot
    say what its keys mean, which is all a factorial or priming design gets. A design with
    neither a response nor a question is told what it will see. Must stay identical to
    .default_instructions in scripting.R.
    """
    events = resolve_events(design)
    paradigm = design.get("paradigm", "factorial")
    keys = _response_keys(design)
    region = _first_event(events, "region_by_region")
    question = _first_event(events, "question")
    parts, explained = [], True
    if (paradigm == "lexical_decision" and mapping is not None
            and "word" in mapping and "pseudoword" in mapping):
        parts.append("You will see a string of letters. Press %s if it is a real English word "
                     "and %s if it is not." % (_key_label(mapping["word"]),
                                               _key_label(mapping["pseudoword"])))
    elif paradigm == "categorisation" and keys is not None and len(keys) == 2:
        parts.append("You will see a category and then a word. Press %s for yes if the word "
                     "belongs to the category and %s for no if it does not."
                     % (_key_label(keys[0]), _key_label(keys[1])))
    elif keys is not None:
        parts.append("When a response is needed, press %s."
                     % _join_words([_key_label(k) for k in keys], "or"))
        explained = False
    if region is not None:
        parts.append("You will read each sentence one part at a time. Press %s to see the "
                     "next part." % _key_label(region.get("advance", "space")))
    if question is not None:
        qkeys = _keys_of(question, ["f", "j"])
        if len(qkeys) == 2:
            parts.append("Answer each question by pressing %s for yes and %s for no."
                         % (_key_label(qkeys[0]), _key_label(qkeys[1])))
        else:
            parts.append("Answer each question by pressing %s."
                         % _join_words([_key_label(k) for k in qkeys], "or"))
            explained = False
    if keys is not None:
        parts.append("Respond as quickly and accurately as you can.")
    if not parts:
        parts.append("You will see items presented one at a time on the screen.")
    return " ".join(parts), explained


def _instructions(design: dict, mapping) -> str:
    """The instructions shown with ``mapping``, one list's response mapping: the
    design's own text, or lexsync's."""
    own = _design_instructions(design)
    return own if own is not None else _default_instructions(design, mapping)[0]


def _instruction_texts(design: dict, versions: list) -> list:
    """The instructions each presentation version shows, in version order.

    A mapping rotated across lists names each list's keys, so the texts can differ from
    one version to the next. Mirrors .instruction_texts in scripting.R.
    """
    mapping = _response_mapping(design)
    return [_instructions(design, _list_mapping(design, mapping, v["list"])) for v in versions]


def _instruction_notes(design: dict) -> list:
    """The run-log notes on a design's instructions, in the order the run log gives them.

    A design that gives none shows lexsync's, which are in English, so a design in another
    language is told so. One whose response keys lexsync cannot explain is told that its
    experiments only name them, as a factorial or priming design's do. A design that
    rotates its mapping across lists and gives its own text is reminded that the text is
    the same in every list. Mirrors .instruction_notes in scripting.R.
    """
    notes = []
    if _design_instructions(design) is None:
        if _language_tag(design).split("-")[0].lower() != "en":
            notes.append("lexsync: the design gives no `instructions` and its language is "
                         "'%s', so the experiments show lexsync's instructions in English; "
                         "give `instructions` in the participants' language."
                         % design.get("language"))
        if not _default_instructions(design, _response_mapping(design))[1]:
            notes.append("lexsync: the design gives no `instructions`, and lexsync cannot tell "
                         "what the response keys of a %s design mean, so the experiments only "
                         "name the keys; give `instructions` that say what each key means."
                         % design.get("paradigm", "factorial"))
    elif _rotates(design) and _response_mapping(design) is not None:
        notes.append("lexsync: the response keys rotate across lists, but the design's "
                     "`instructions` are the same in every list, so they should not name the "
                     "keys.")
    return notes


def _answer_text(value):
    """A trial's own answer as the text its loop-table cell holds, or None when it names
    none.

    A table's answer column is typed by its values, so a practice table that codes its
    answers as number keys is read as numbers. This engine holds them as floats once the
    main trials' missing answers join them. Such an answer is the text the CSV writer
    gives it, 1 and not 1.0, and so the text the R engine gives it. Text is kept as it
    is. Mirrors .answer_text in scripting.R.
    """
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if pd.isna(value):
        return None
    return _readr_cell(value)


def _answer_given(value):
    """A trial's own answer, trimmed, or None when it names none."""
    text = _answer_text(value)
    if text is None:
        return None
    # The characters R's trimws() removes, and no other space.
    text = text.strip(" \t\r\n")
    return text or None


def _assign_answers(stimuli: pd.DataFrame, design: dict) -> tuple:
    """Fill each trial's `answer` from the response mapping, where the trial names none.

    Returns ``(stimuli, notes)``, the trials with their answers and the run-log notes. A
    trial that names its own answer, such as a practice or filler trial, keeps it as text
    (see _answer_text), and a note counts the trials whose answer contradicts the mapping
    for their condition and list. With rotation, each trial takes its list's mapping. A
    design's own mapping is refused when it gives no key for a condition whose trials
    name no answer, or names a condition no trial has, since both are typing errors that
    would leave trials unscored. The lexical-decision default maps word and pseudoword
    only, and a note counts the trials of any other condition it leaves without an
    answer. Without a mapping, the trials come back as they came. export_experiments
    applies this as it assigns the trigger codes, so the stimuli file does not change.
    Must stay identical to .assign_answers in scripting.R.
    """
    mapping = _response_mapping(design)
    if mapping is None:
        return stimuli, []
    n = len(stimuli)
    lists = _version_key(stimuli, "list")
    conditions = [str(c) for c in stimuli["condition"]]
    own = list(stimuli["answer"]) if "answer" in stimuli.columns else [None] * n
    blocks = ([None if pd.isna(b) else str(b) for b in stimuli["block"]]
              if "block" in stimuli.columns else [None] * n)
    by_list = {lst: _list_mapping(design, mapping, lst) for lst in dict.fromkeys(lists)}
    answers, missing, conflicts = [], {}, {}
    for lst, cond, mine, blk in zip(lists, conditions, own, blocks, strict=True):
        want = by_list[lst].get(cond)
        have = _answer_given(mine)
        if have is not None:
            answers.append(_answer_text(mine))
            if want is not None and have != want:
                key = (blk, lst, cond, have, want)
                conflicts[key] = conflicts.get(key, 0) + 1
        else:
            answers.append(want)
            if want is None:
                missing[cond] = missing.get(cond, 0) + 1
    if design.get("response_mapping") is not None:
        for cond, count in missing.items():
            raise ValueError("lexsync: response_mapping gives no key for condition '%s', and "
                             "%d trial(s) of it have no answer of their own." % (cond, count))
        present = list(dict.fromkeys(conditions))
        for cond in mapping:
            if cond not in present:
                raise ValueError("lexsync: response_mapping names condition '%s', which no "
                                 "trial has; the trials' conditions are %s."
                                 % (cond, _join_words(present, "and")))
    several = len(set(lists)) > 1
    notes = ["lexsync: %d %strial(s) of condition '%s'%s keep their answer '%s', where the "
             "response mapping gives '%s'."
             % (count, "" if blk is None else blk + " ", cond,
                " in list %d" % lst if several else "", have, want)
             for (blk, lst, cond, have, want), count in conflicts.items()]
    notes += ["lexsync: %d trial(s) of condition '%s' have no answer, since the "
              "lexical-decision default maps only word and pseudoword; give "
              "`response_mapping`." % (count, cond) for cond, count in missing.items()]
    out = stimuli.copy()
    out["answer"] = answers
    return out, notes


def _design_condition_names(design) -> list | None:
    """The names of a design's declared conditions, in the order the design lists
    them, or None when it declares none (a generated lexical decision, an item
    table, a continuous design). Mirrors .design_condition_names in scripting.R."""
    conds = design.get("conditions")
    if not isinstance(conds, list) or not conds:
        return None
    names = [str(c["name"]) for c in conds if isinstance(c, dict) and c.get("name") is not None]
    return names or None


def export_experiments(stimuli, design, schema, outdir, base=None, conditions=None) -> dict:
    """Write every presentation target (PsychoPy, OpenSesame, jsPsych).

    Assigns the EEG trigger codes with ``assign_triggers`` and then writes each
    target. The condition codes follow ``conditions``, which defaults to the order
    of the design's ``conditions`` entries, so in a design that declares its
    conditions the first is 101, the second 102, and so on, whatever order the
    counterbalanced trials put them in. A design with no ``conditions`` block (a
    generated lexical decision, an item table) falls back to the order of first
    appearance, unless ``conditions`` is given. ``assign_triggers`` is given the
    design's events and the schema, so the item codes of a design that sends them
    alongside other codes are kept apart from those codes, and a code of the design's
    own that the stream already uses is reported.

    Each trial that names no ``answer`` of its own takes the key the design's response
    mapping gives its condition in its list, so the loop tables can score every trial.
    A lexical decision maps word to its response event's first key and pseudoword to
    its second unless the design gives ``response_mapping``, and
    ``rotate_mapping_by_list: true`` rotates the keys across lists. A practice or filler
    trial keeps the answer its table gives. The stimuli passed in are not changed. Every
    target shows the design's ``instructions``, or lexsync's English instructions for its
    task, and waits for the space bar before the first trial.

    Returns the generated paths by target: ``psychopy``, ``opensesame`` (version 1's
    experiment when a design has several, see ``export_opensesame``) and
    ``jspsych``. ``files`` lists every file written, in a fixed order: the PsychoPy
    script, each OpenSesame experiment in version order, the jsPsych page, the PsychoPy
    conditions file, and then each OpenSesame experiment's loop table and text table.
    """
    if conditions is None:
        conditions = _design_condition_names(design)
    stimuli = assign_triggers(stimuli, conditions, events=resolve_events(design), schema=schema)
    stimuli = _assign_answers(stimuli, design)[0]
    script, conditions_file = _psychopy_files(stimuli, design, schema, outdir, base)
    experiments, tables = _opensesame_files(stimuli, design, schema, outdir, base)
    page = export_jspsych(stimuli, design, schema, outdir, base)
    return {
        "psychopy": script,
        "opensesame": experiments[0],
        "jspsych": page,
        "files": [script, *experiments, page, conditions_file, *tables],
    }
