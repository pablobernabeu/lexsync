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
import math
import numbers
import os
import re

import pandas as pd

from .design import _shown, design_stem
from .io_utils import (
    _key_part,
    _readr_cell,
    _round_dp,
    clean_column,
    clean_key,
    clean_meta,
    clean_port,
    hash_int_range,
    write_csv_utf8,
)
from .paradigms import content_field, referenced_fields, resolve_events

# Columns always carried in a loop table when present (besides the event fields).
# `block` travels with the trials because the runners need it: it is what an event's
# `blocks:` restriction is matched against, and what a runner watches to know a block
# boundary has been reached. Absent unless the design declares a practice or filler
# block, so no existing loop table gains a column. `replicate`, present only in a
# resampled design, is what tells its item samples apart, since each is numbered from
# trial 1 and set 1. The first six are written before the event fields.
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
    # `or {}`, not a default argument: a schema whose `presentation:` key is present
    # but empty parses to None here and to NULL in R, where `%||% list()` falls back
    # to the default, so the two engines answered the same schema with a refresh rate
    # and an AttributeError. isfinite for the reason run_pipeline tests
    # n_per_condition that way: `hz > 0` admits Inf, which R's is.finite() refuses,
    # and _frames_to_ms would then turn every frame count into 0 ms.
    hz = float(((schema or {}).get("presentation") or {}).get("assumed_refresh_hz", 60))
    if not math.isfinite(hz) or hz <= 0:
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
    # isfinite as well as the sign, mirroring the R twin's is.finite(): `ms > 0`
    # alone admits Inf, which R refuses with this same message.
    if not math.isfinite(ms) or ms <= 0:
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


def assign_triggers(stimuli: pd.DataFrame, conditions=None) -> pd.DataFrame:
    """A per-condition marker and a per-item marker, both 0-255 EEG codes.

    ``condition_trigger`` numbers the conditions from 101 upwards and
    ``item_trigger`` numbers the item sets from 40. The item range holds 200 codes
    (an 8-bit-port constraint), so past 200 sets the codes wrap and repeat, and a
    runtime notice says so.

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

    >>> stim = pd.DataFrame({"condition": ["low", "high", "low", "high"],
    ...                      "set": [1, 1, 2, 2]})
    >>> assign_triggers(stim)["condition_trigger"].tolist()
    [101, 102, 101, 102]
    >>> assign_triggers(stim, conditions=["high", "low"])["condition_trigger"].tolist()
    [102, 101, 102, 101]
    """
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
    # A wrapped code no longer identifies its item one to one, which the analyst
    # must hear about at generation time, not at decode time.
    if len(sets) > 200:
        print(f"lexsync: {len(sets)} item sets exceed the 200-code trigger range; "
              "item codes wrap and repeat.")
    set_code = {s: 40 + (i % 200) for i, s in enumerate(sets)}
    stimuli["item_trigger"] = stimuli["set"].map(set_code)
    return stimuli


def _keys_of(ev: dict, default: list) -> list:
    """An event's response keys, normalised and validated.

    A YAML scalar (`keys: space`) arrives as a str, and `list("space")` is five
    one-character keys, while R keeps the scalar whole -- so one design produced two
    different allowed-response lists. Each key is then validated because OpenSesame
    writes them into `set allowed_responses "a;b"`, one line of a line-oriented format.
    """
    keys = ev.get("keys", default)
    if isinstance(keys, str):
        keys = [keys]
    return [clean_key(k) for k in keys]


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
    written into the stimuli table as well as the generated script, because timing
    that varies is a variable the analysis needs, not presentation detail.
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
        # one design draw independently, where a key naming only the trial would
        # give them one shared value.
        lists = stimuli["list"] if "list" in stimuli.columns else [1] * len(stimuli)
        keys = ["|".join([_key_part(seed), "jitter", spec["column"],
                          _key_part(l), _key_part(s), _key_part(c)])
                for l, s, c in zip(lists, stimuli["set"], stimuli["condition"], strict=True)]
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

    A response collected from the onset of the text event before it (see
    ``_response_from``) is rendered with that event, as its ``respond`` entry
    (``{"keys", "timeout"}``). The text keeps ``ms`` as its longest display time, and
    the window runs from its onset for ``ms`` plus the timeout, so the total window is
    the one the two events had. A response collected from the offset stays an event of
    its own.
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
    offset, so a response after a blank keeps the window it had. Must match
    .response_from in scripting.R.
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

    Rounded through _round_dp. int() truncated 1.001 * 1000, which is
    1000.9999999999999 in binary floating point, so a declared 1,001 ms was written as
    1,000, and 95 of the whole-millisecond values from 1 to 10,000 came out one short.
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
    # A feedback event scores the key the participant pressed, so something must have
    # collected one first. With no preceding response or question the OpenSesame runner
    # raises on the unset variable, PsychoPy compares against None and jsPsych finds no
    # scored row -- three different confusing failures at run time, for one design error
    # that is obvious here.
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
            r["ms"] = _event_ms(ev, None, None, hz, default_frames=36)
        else:
            raise ValueError(f"lexsync: unknown event type '{t}'.")
        # An event may be restricted to named blocks. This is what lets feedback run
        # during practice and nowhere else: the event list is global to the design, so
        # the restriction has to travel with the event and be applied per trial at run
        # time. Generating a second event list would be the alternative, and a worse one.
        if ev.get("blocks"):
            # A scalar `blocks: practice` is a str, and iterating it yields
            # characters, so the OpenSesame guard compared against "p", "r", ... and
            # never matched -- the event silently ran in every block in Python and
            # only in the named one in R.
            blks = ev["blocks"]
            blks = [blks] if isinstance(blks, str) else list(blks)
            r["blocks"] = [str(b) for b in blks]
        out.append(r)
    return out


def _ms_columns(events: list | None) -> list:
    """The per-trial duration columns an event list reads, in event order."""
    cols = []
    for i, ev in enumerate(events or [], start=1):
        s = _duration_spec(ev, i)
        if s is not None and s["column"] not in cols:
            cols.append(s["column"])
    return cols


def loop_table(stimuli: pd.DataFrame, events: list | None = None) -> pd.DataFrame:
    """Per-trial table carrying exactly the fields the events reference.

    The rows are in presentation order within each version: by replicate when the
    table has one, then by list, then by trial. `trial` restarts at 1 in every list
    and in every replicate, so ordering on it alone interleaved the versions. The
    sort is stable, as R's order() is, so rows that tie keep their incoming order and
    the two engines write the same table.
    """
    fields = referenced_fields(events) if events else (["word"] if "word" in stimuli.columns else [])
    # A per-trial duration is read from the loop table at run time, so its column
    # has to travel with the trials, and cannot stay behind in the stimuli file.
    ms_cols = _ms_columns(events)
    cols = []
    for c in _STD_COLS[:_LEADING_COLS] + fields + ms_cols + _STD_COLS[_LEADING_COLS:]:
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
    rule ``participant_table`` allocates by. Every generated experiment carries this
    list, and ``export_opensesame`` writes one experiment per version when there is
    more than one. Mirrors .presentation_versions in scripting.R.

    Args:
        stimuli: The presented trials, with the ``list`` (and any ``replicate``)
            column that ``counterbalance`` adds.

    Returns:
        A list of ``{"version", "replicate", "list", "n_trials"}`` dictionaries, one per
        version, numbered from 1.

    Raises:
        ValueError: If a ``list`` or ``replicate`` value is not a whole number.

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


def export_psychopy(stimuli, design, schema, outdir, base=None) -> str:
    """Write a runnable PsychoPy script and the conditions file it reads.

    The conditions file, ``<base>_psychopy.csv``, holds every presentation version
    (see :func:`presentation_versions`), and the script presents one per run: the
    version given by ``--version`` (or ``--list`` when there are no replicates), else
    the participant's by the rule ``((participant - 1) mod V) + 1`` from
    ``--participant``, else what a start-up dialogue asks for. A version the script does
    not have stops the run with a message.

    Each run writes ``data/<base>_p<participant>_v<version>_<date>-<time>.csv`` beside
    the script, without the ``_p`` part when no participant number is given, one row
    per trial, each written as its trial ends. A row holds the run, the trial's fields
    and trigger codes, the response and its reaction time from the onset of the
    stimulus it answers, whether the window closed without one, whether the key was
    the trial's ``answer``, the self-paced reading times, the question's response and
    reaction time, the measured refresh rate, and each event's realised flips and
    onset.

    Args:
        stimuli: Stimuli with trigger columns (see :func:`assign_triggers`).
        design: A parsed design configuration.
        schema: The parsed global schema (trigger and presentation settings).
        outdir: Output directory.
        base: Optional file-name stem, by default the design's :func:`design_stem`.

    Returns:
        The path to the generated ``.py``.
    """
    return _psychopy_files(stimuli, design, schema, outdir, base)[0]


def _psychopy_files(stimuli, design, schema, outdir, base=None) -> list:
    """Write the PsychoPy script and its conditions file, and return both paths."""
    base = base or design_stem(design)
    events = resolve_events(design)
    rendered = render_events(events, design.get("timing") or {}, _refresh_hz(schema))
    versions = presentation_versions(stimuli)
    csv_name = f"{base}_psychopy.csv"
    write_csv_utf8(loop_table(stimuli, events), os.path.join(outdir, csv_name))
    with open(find_template("psychopy/trial_runner_template.py"), encoding="utf-8") as handle:
        tmpl = handle.read()
    triggers = schema.get("triggers") or {}
    presentation = schema.get("presentation") or {}
    # These land in CODE positions -- a module docstring, a bare assignment, a string
    # literal, so they are validated on the way in. Escaping would need three
    # different rules for three targets in two engines. See clean_meta in io_utils.
    subs = {
        "DESIGN": clean_meta(design["name"], "the design's `name`"),
        "LANGUAGE": clean_meta(design["language"], "the design's `language`"),
        "CONDITIONS_FILE": csv_name,
        # The data files are named after the experiment, as data/<base>_p<n>_v<k>_...
        "BASE": base,
        "TRIGGER_ADDRESS": clean_port(triggers.get("parallel_address", "0x0378")),
        "TRIGGER_HOLD_MS": "%.17g" % _trigger_hold_ms(schema),
        # Through %.17g like its neighbours, never default stringification: str()
        # and R's as.character() part company on a non-integer quotient
        # (str(16.65 / 1000) gives "0.016649999999999998", as.character gives
        # "0.01665"), and this value lands in the generated script.
        "INTER_TRIGGER_S": "%.17g" % (triggers.get("inter_trigger_ms", 10) / 1000),
        "WORD_FONT": clean_meta(
            design.get("font") or presentation.get("font") or "Courier New", "the font"),
        "FULLSCREEN": "False",
        # The fallback used only when the script cannot measure the display.
        "ASSUMED_REFRESH_HZ": "%.17g" % _refresh_hz(schema),
        "EVENTS_JSON": _json_r(rendered),
        "VERSIONS_JSON": _json_r(versions),
    }
    for key, value in subs.items():
        tmpl = tmpl.replace("{{" + key + "}}", str(value))
    script = _write_text(tmpl.rstrip("\n"), os.path.join(outdir, f"{base}_psychopy.py"))
    return [script, os.path.join(outdir, csv_name)]


def _pyq(s: str) -> str:
    """A safe single-quoted Python u-string literal for embedding in generated code.

    A newline had to be escaped as well as the backslash and the quote. An .osexp is a
    line-oriented format whose inline scripts are delimited by their own lines, so a raw
    newline in a value did not merely break the literal: it closed the script block and
    let the rest of the value start a new top-level item in the emitted experiment.
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
    return _text_expr(ev["field"]) if "field" in ev else _pyq(ev.get("text", ""))


def _trigger_expr(spec) -> str | None:
    if spec is None:
        return None
    if isinstance(spec, str) and spec.startswith("@"):
        return _number_expr(spec[1:])
    return str(int(spec))


# The Python that OpenSesame's inline_script actually runs.
#
# Two spellings below are forced by OpenSesame's runtime and were both wrong at first:
#
# `str`, never `unicode`. OpenSesame 3.3 and later run inline scripts in a Python 3
# workspace and inject only a fixed set of globals (exp, var, pool, items, clock, log and
# a small API); `unicode` is a Python 2 builtin and is not among them, so every emitted
# guard and feedback script died with NameError on the first trial.
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
    """
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
    sleep_arg = ("int(float(var.get(%s, _eval=False)))"
                 % _pyq(clean_column(ev["ms_column"], "a jittered duration's `as`"))
                 if ev.get("ms_column") else str(int(ev.get("ms", 0))))
    if t == "text" and ev.get("respond"):
        # The stimulus collects its own response, from its onset. The keyboard is
        # flushed once the trigger is out, so nothing pressed before the stimulus counts,
        # and polled while the stimulus is shown. Without a key by its end, the screen
        # blanks and the keyboard is polled for the timeout, so the window is the one the
        # stimulus and a separate response event had. A key ends the event either way.
        respond = ev["respond"]
        keylist = ", ".join(_pyq(k) for k in respond["keys"])
        body = ["c = Canvas()", f"c.text({_content_expr(ev)})", "_t0 = c.show()",
                "var.onset_time = _t0"]
        trig = _trigger_expr(ev.get("trigger"))
        if trig is not None:
            body.append(f"send_trigger({trig})")
        body += [f"_kb = Keyboard(keylist=[{keylist}])",
                 "_kb.flush()",
                 f"_key, _t = _kb.get_key(timeout={sleep_arg})",
                 "if _key is None:",
                 "    c = Canvas()",
                 "    c.show()",
                 f"    _key, _t = _kb.get_key(timeout={_whole_ms(respond['timeout'])})",
                 "var.response = _key",
                 "var.response_time = u'' if _key is None else _t - _t0",
                 "var.timed_out = 1 if _key is None else 0"]
        if scores:
            body += _osexp_correct("_key")
        return (_inline_block(name, "Show the stimulus and collect the response from its "
                              "onset", _osexp_block_guard(body, blocks), run=True), [name])
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
        # Each region is timed from its own onset, and the keyboard is flushed as it
        # appears, so a key pressed before it cannot advance it.
        body = [
            f"_regions = [r for r in {_text_expr(ev['field'])}.split({_pyq(ev.get('sep', '|'))})"
            " if r != u'']",
            # An empty cell, a sentence with no critical region, reads as 0: no trigger.
            "_crit = int(var.get(u'critical_region', 0, _eval=False) or 0)",
            f"_kb = Keyboard(keylist=[{_pyq(ev.get('key', 'space'))}], timeout=None)",
            "_rts = []",
            "for _i, _region in enumerate(_regions, start=1):",
            "    c = Canvas(); c.text(_region); _t0 = c.show()",
        ]
        if trig is not None:
            body.append(f"    if _i == _crit: send_trigger({trig})")
        body += ["    _kb.flush()",
                 "    _key, _t = _kb.get_key()",
                 "    _rts.append(u'%.1f' % (_t - _t0))",
                 "var.lexsync_region_rts = u'|'.join(_rts)"]
        return (_inline_block(name, "Self-paced reading region by region",
                              _osexp_block_guard(body, blocks), run=True), [name])
    if t == "question":
        body = [
            f"c = Canvas(); c.text({_text_expr(ev['field'])}); _t0 = c.show()",
            f"_kb = Keyboard(keylist=[{', '.join(_pyq(k) for k in ev.get('keys', ['f', 'j']))}], "
            f"timeout={_whole_ms(ev.get('timeout', 5))})",
            "_kb.flush()",
            "_key, _t = _kb.get_key()",
            "var.question_response = _key",
            "var.question_rt = u'' if _key is None else _t - _t0",
        ]
        if scores:
            body += _osexp_correct("_key")
        return (_inline_block(name, "Comprehension question",
                              _osexp_block_guard(body, blocks), run=True), [name])
    if t == "feedback":
        # The key comes from whichever response or question collected one last. The
        # answer column (or whichever column the event names) holds the KEY that is
        # correct, so scoring is a string comparison. A timeout is reported separately,
        # because on a timed task it means something different from a wrong key.
        # OpenSesame 4.x stores it as None and 3.3 as the string 'None', so both count
        # as no response.
        body = [
            "_want = str(_lexsync_row().get(u'%s', u'')).strip()"
            % clean_column(ev.get("answer", "answer"), "a feedback event's `answer`"),
            "_got = var.get(u'%s', u'', _eval=False)" % feedback_scores,
            "_got = u'' if _got is None else str(_got).strip()",
            "if _got in (u'', u'None'): _msg = %s" % _pyq(ev.get("no_response", "Too slow")),
            "elif _got == _want: _msg = %s" % _pyq(ev.get("correct", "Correct")),
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


def _inline_block(name: str, desc: str, body: list, run: bool) -> list:
    tab = ["\t" + b for b in body]
    return [
        f"define inline_script {name}",
        f'\tset description "{desc}"',
        '\tset _prepare ""', "\t___run__", *tab, "\t__end__", "",
    ]


def _osexp_version_check(version: int, n_versions: int) -> list:
    """The inline script that checks the subject number against this file's version.

    A design with several presentation versions gets one experiment per version, and
    the experimenter opens the participant's. OpenSesame asks for a subject number at
    start-up, and participant p normally runs version ((p - 1) mod V) + 1. When the
    number belongs to another version, this shows a screen saying so and waits for a
    key. Space goes on with this file, and escape stops the session. It runs before the
    loop, so the experiment needs no run-if condition, a syntax that differs between
    OpenSesame 3.3 and 4.x. Must match .osexp_version_check in scripting.R.
    """
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


def build_osexp(design: dict, conditions_file: str, schema: dict, rendered: list,
                font: str = "mono", text_file: str | None = None,
                version: int | None = None, n_versions: int | None = None) -> str:
    """The plain text of an OpenSesame experiment for a rendered event list.

    ``conditions_file`` names the loop table and ``text_file`` its companion text
    table, which defaults to the loop table's name with ``_text`` before ``.csv``.
    Both are looked up through OpenSesame's file pool, which also searches the
    experiment's own folder. ``version`` and ``n_versions`` mark the experiment as
    version ``version`` of ``n_versions``. With more than one version, the experiment
    checks OpenSesame's subject number against its own before the loop and warns when
    the participant would normally run another. Each trial starts by clearing the last
    trial's responses and ends with a logger item. Must match build_osexp in
    scripting.R.
    """
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
        "set fullscreen no", "set foreground white", "set font_size 32",
        f"set font_family {font}", 'set description "Generated by lexsync"',
        "set coordinates uniform", "set compensation 0", "set color_backend legacy",
        "set clock_backend legacy", "set canvas_backend xpyriment", "set background black", "",
        "define inline_script lexsync_trigger_setup",
        '\tset description "Load the trial texts and open the trigger device with a '
        'test-mode fallback"',
        '\tset _run ""', "\t___prepare__", *["\t" + s for s in setup], "\t__end__", "",
    ]
    checked = version is not None and n_versions is not None and int(n_versions) > 1
    check = _osexp_version_check(version, n_versions) if checked else []
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
        *(["\trun lexsync_version_check always"] if checked else []),
        "\trun lexsync_loop always", "",
    ]
    return "\n".join(header + check + event_blocks + trial)


def export_opensesame(stimuli, design, schema, outdir, base=None) -> str:
    """Write complete plain-text OpenSesame experiments and the two tables each reads.

    ``<base>.osexp`` loops over ``<base>_opensesame.csv``, which holds numbers only:
    ``lexsync_row`` (the trial's position in loop order, from 1), ``lexsync_trial``,
    ``lexsync_list``, ``lexsync_set``, the trigger codes, ``critical_region`` and any
    per-trial duration. The presented text, ``condition``, ``block`` and ``answer`` are
    in ``<base>_opensesame_text.csv``, which the inline scripts read with Python's
    ``csv`` module, so OpenSesame never evaluates them. Copy both tables with the
    experiment.

    Every trial is logged. A response after a text event is collected by that event's
    script from the stimulus's onset, which sets ``response``, ``response_time``,
    ``timed_out`` and ``correct``. A response kept after the stimulus with
    ``from: offset`` is a keyboard_response, and a script after it sets ``timed_out``
    and ``correct``. Self-paced reading sets ``lexsync_region_rts`` and a question
    ``question_response`` and ``question_rt``. A script clears these as each trial
    starts, another copies the trial's labels into ``lexsync_condition``,
    ``lexsync_block`` and ``lexsync_answer``, and a logger item ends the trial.

    A design with more than one presentation version (see
    :func:`presentation_versions`) gets one experiment per version instead, each with
    its own two tables holding only that version's trials: ``<base>_list<k>.osexp``, or
    ``<base>_rep<r>_list<k>.osexp`` when the versions span several replicates. Each one
    checks OpenSesame's subject number at start-up and shows a warning when that
    participant would normally run another version. ``export_experiments`` lists every
    file written.

    OpenSesame evaluates the cells of a loop table: in 4.x a cell holding ``{`` runs as
    a Python f-string, and in 3.3 a cell starting with ``=`` or holding ``[=...]`` runs
    as Python. A value in a numeric column that is not a plain number is therefore
    refused, naming the column. An empty cell passes. These rules were checked against
    the sources of OpenSesame 3.3.14 and 4.1.20.

    Parameters
    ----------
    stimuli : pandas.DataFrame
        Stimuli with trigger columns (see ``lexsync.scripting.assign_triggers``).
    design : dict
        A parsed design configuration.
    schema : dict
        The parsed global schema (trigger and presentation settings).
    outdir : str
        Output directory.
    base : str, optional
        File-name stem, by default ``lexsync.design.design_stem(design)``, built
        from the design's name and language.

    Returns
    -------
    str
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
    rendered = render_events(events, design.get("timing") or {}, _refresh_hz(schema))
    presentation = schema.get("presentation") or {}
    font = design.get("font") or presentation.get("opensesame_font") or "mono"
    versions = presentation_versions(stimuli)
    if len(versions) <= 1:
        # One version keeps the file names an experiment has always had.
        parts = [(base, stimuli, None)]
    else:
        by_replicate = _spans_replicates(versions)
        parts = [((f"{base}_rep{v['replicate']}_list{v['list']}" if by_replicate
                   else f"{base}_list{v['list']}"), _version_rows(stimuli, v), v)
                 for v in versions]
    written = []
    for stem, rows, v in parts:
        numbers, text = _opensesame_tables(rows, events)
        csv_name, text_name = f"{stem}_opensesame.csv", f"{stem}_opensesame_text.csv"
        osexp = build_osexp(design, csv_name, schema, rendered, font=font, text_file=text_name,
                            version=None if v is None else v["version"],
                            n_versions=len(versions))
        written.append((stem, csv_name, text_name, numbers, text, osexp))
    experiments, tables = [], []
    for stem, csv_name, text_name, numbers, text, osexp in written:
        write_csv_utf8(numbers, os.path.join(outdir, csv_name))
        write_csv_utf8(text, os.path.join(outdir, text_name))
        experiments.append(_write_text(osexp, os.path.join(outdir, f"{stem}.osexp")))
        tables += [os.path.join(outdir, csv_name), os.path.join(outdir, text_name)]
    return experiments, tables


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
    # The shape check applies to a STATED tag too. It used to be returned verbatim, so
    # `language_tag: 'en"><script>...'` reached the lang attribute of the generated HTML
    # intact -- the one input to this function that an attacker would actually choose.
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
            # design whose practice items carry one) has none, so omitting the field is
            # also the honest rendering.
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
    A stimulus that collects its response is one trial, recorded as ``target``: it
    accepts the keys from its onset, shows the stimulus for its duration and stays
    open for the timeout after it, a key ends it, and ``rt`` runs from the onset.

    The page embeds every presentation version (see :func:`presentation_versions`) and
    runs one, named in its address: ``?version=K``, ``?list=K`` when there are no
    replicates, or ``?participant=N``, whose version is ``((N - 1) mod V) + 1``. A page
    with more than one version, opened with none of these, shows a screen naming them
    and runs nothing. The data rows carry the participant, the version, the list and
    the replicate, and the data file is named after the participant and the version.
    """
    base = base or design_stem(design)
    events = resolve_events(design)
    rendered = _map_keys_for_jspsych(
        render_events(events, design.get("timing") or {}, _refresh_hz(schema)))
    versions = presentation_versions(stimuli)
    trials = loop_table(stimuli, events).to_dict(orient="records")
    presentation = schema.get("presentation") or {}
    font = design.get("font") or presentation.get("font") or "Courier New"
    with open(find_template("jspsych/experiment_template.html"), encoding="utf-8") as handle:
        tmpl = handle.read()
    # DESIGN lands in <title> and a comment, LANGUAGE_TAG in a lang attribute, WORD_FONT
    # inside a CSS font-family declaration. Only the two JSON blobs are escaped by
    # _json_html; the rest are validated, since a quote or an angle bracket in any of
    # them would leave its attribute or rule and start markup in a page that collects
    # participant responses.
    subs = {
        "DESIGN": clean_meta(design["name"], "the design's `name`"),
        "LANGUAGE": clean_meta(design["language"], "the design's `language`"),
        "LANGUAGE_TAG": _language_tag(design), "WORD_FONT": clean_meta(font, "the font"),
        "EVENTS_JSON": _json_html(rendered), "TRIALS_JSON": _json_html(trials),
        "VERSIONS_JSON": _json_html(versions),
    }
    for k, v in subs.items():
        tmpl = tmpl.replace("{{" + k + "}}", str(v))
    return _write_text(tmpl.rstrip("\n"), os.path.join(outdir, f"{base}.html"))


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
    appearance, unless ``conditions`` is given.

    Returns the generated paths by target: ``psychopy``, ``opensesame`` (version 1's
    experiment when a design has several, see :func:`export_opensesame`) and
    ``jspsych``. ``files`` lists every file written, in a fixed order: the PsychoPy
    script, each OpenSesame experiment in version order, the jsPsych page, the PsychoPy
    conditions file, and then each OpenSesame experiment's loop table and text table.
    """
    if conditions is None:
        conditions = _design_condition_names(design)
    stimuli = assign_triggers(stimuli, conditions)
    script, conditions_file = _psychopy_files(stimuli, design, schema, outdir, base)
    experiments, tables = _opensesame_files(stimuli, design, schema, outdir, base)
    page = export_jspsych(stimuli, design, schema, outdir, base)
    return {
        "psychopy": script,
        "opensesame": experiments[0],
        "jspsych": page,
        "files": [script, *experiments, page, conditions_file, *tables],
    }
