# -*- coding: utf-8 -*-
"""Paradigm registry and the trial-event model.

A *paradigm* is a named default sequence of trial *events* plus the trial fields
it requires and a counterbalancing recipe. A design either names a ``paradigm``
(and inherits its event sequence) or supplies an explicit ``events`` list. Every
presentation backend renders the same event list, so adding a paradigm is purely a
matter of configuration.

An *event* is a small dictionary::

    {type, content, duration_frames|duration_ms, trigger, onset_locked, keys, timeout_ms}

``type``     one of fixation | text | mask | blank | region_by_region | response | question
``content``  a literal ("+", "#####") or a field reference ("{target}", "{sentence}")
``trigger``  an integer EEG code, or the token "condition" / "item"
``onset_locked``  write the trigger on the event's verified onset flip

This module is pure data and small helpers, identical in the R and Python
engines (see R_workflow/R/paradigms.R), so the two produce the same trial
structure from the same design.
"""
from __future__ import annotations

import re

# Default frame durations (at 60 Hz) and response timeout, overridable per design.
_FIX = 30
_WORD = 48
_ISI = 15

PARADIGMS = {
    # The original word-list factorial design: fixation, critical word (onset-
    # locked condition marker), response, blank.
    "factorial": {
        "stimulus_fields": ["word"],
        "counterbalance": "factorial",
        "events": [
            {"type": "fixation", "content": "+", "duration_frames": _FIX},
            {"type": "text", "content": "{word}", "duration_frames": _WORD,
             "trigger": "condition", "onset_locked": True},
            {"type": "response", "keys": ["left", "right"], "timeout_ms": 2000},
            {"type": "blank", "duration_frames": _ISI},
        ],
    },
    # Lexical decision: a single target (real word or pseudoword); word/nonword
    # response. Same trial shape as factorial but the target field is generic.
    "lexical_decision": {
        "stimulus_fields": ["target"],
        "counterbalance": "factorial",
        "events": [
            {"type": "fixation", "content": "+", "duration_frames": _FIX},
            {"type": "text", "content": "{target}", "duration_frames": _WORD,
             "trigger": "condition", "onset_locked": True},
            {"type": "response", "keys": ["left", "right"], "timeout_ms": 2000},
            {"type": "blank", "duration_frames": _ISI},
        ],
    },
    # Priming: a briefly-presented prime, a mask, then the target. The prime
    # onset carries a fixed marker; the target onset carries the condition marker.
    "priming": {
        "stimulus_fields": ["prime", "target"],
        "counterbalance": "latin_square_target",
        "events": [
            {"type": "fixation", "content": "+", "duration_frames": _FIX},
            {"type": "text", "content": "{prime}", "duration_frames": 3,
             "trigger": 20, "onset_locked": True},
            {"type": "mask", "content": "#####", "duration_frames": 2},
            {"type": "text", "content": "{target}", "duration_frames": _WORD,
             "trigger": "condition", "onset_locked": True},
            {"type": "response", "keys": ["left", "right"], "timeout_ms": 2000},
            {"type": "blank", "duration_frames": _ISI},
        ],
    },
    # Self-paced reading: a sentence presented region by region (space-advanced),
    # with the critical region carrying the condition marker, then a yes/no
    # comprehension question.
    "self_paced_reading": {
        "stimulus_fields": ["sentence", "question"],
        "counterbalance": "latin_square_target",
        "events": [
            {"type": "fixation", "content": "+", "duration_frames": _FIX},
            {"type": "region_by_region", "content": "{sentence}", "advance": "space",
             "critical_region_trigger": "condition"},
            {"type": "question", "content": "{question}", "keys": ["f", "j"],
             "timeout_ms": 5000},
            {"type": "blank", "duration_frames": _ISI},
        ],
    },
}

_FIELD_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


def get_paradigm(name: str) -> dict:
    if name not in PARADIGMS:
        known = ", ".join(sorted(PARADIGMS))
        raise ValueError(f"lexsync: unknown paradigm '{name}'. Known paradigms: {known}.")
    return PARADIGMS[name]


def resolve_events(design: dict) -> list:
    """Return the event list for a design: explicit ``events`` or paradigm default."""
    if design.get("events"):
        return [dict(e) for e in design["events"]]
    name = design.get("paradigm", "factorial")
    return [dict(e) for e in get_paradigm(name)["events"]]


def content_field(content) -> str | None:
    """If ``content`` is a single field reference like "{target}", return the field."""
    if not isinstance(content, str):
        return None
    m = _FIELD_RE.fullmatch(content.strip())
    return m.group(1) if m else None


def referenced_fields(events: list) -> list:
    """The ordered, unique trial fields referenced by an event list's content."""
    fields = []
    for ev in events:
        f = content_field(ev.get("content"))
        if f and f not in fields:
            fields.append(f)
    return fields


def required_fields(design: dict) -> list:
    """Trial fields a design needs present in its items (paradigm + events)."""
    name = design.get("paradigm", "factorial")
    base = list(get_paradigm(name)["stimulus_fields"]) if name in PARADIGMS else []
    for f in referenced_fields(resolve_events(design)):
        if f not in base:
            base.append(f)
    return base
