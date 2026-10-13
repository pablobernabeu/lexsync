"""Durations are canonically milliseconds, and both engines must convert alike.

Event durations used to be frame counts that the OpenSesame and jsPsych paths
converted at a hard-coded 60 Hz, so a design presented different real durations
on a 120 or 144 Hz monitor depending on which target ran it. Milliseconds are now
canonical and the PsychoPy script derives flips from the refresh it measures.

The conversion is pinned here rather than left implicit because it is arithmetic
that has to agree bit for bit with R_workflow/R/scripting.R: the multiplication
comes first (``frames * 1000 / hz``), which is a different floating-point
computation from ``frames * (1000 / hz)`` and agrees with it only by accident of
the divisor being 60.
"""
import re

import pytest

from lexsync.scripting import _event_ms, _frames_to_ms, _refresh_hz, render_events

PRIMING_EVENTS = [
    {"type": "fixation", "content": "+", "duration_frames": 30},
    {"type": "text", "content": "{prime}", "duration_frames": 3, "trigger": 20},
    {"type": "mask", "content": "#####", "duration_frames": 2},
    {"type": "text", "content": "{target}", "duration_frames": 48, "trigger": "condition"},
    {"type": "blank", "duration_frames": 15},
]


def test_frames_convert_at_sixty_hz_to_the_documented_milliseconds():
    # The durations the committed OpenSesame goldens time their events by.
    assert [e["ms"] for e in render_events(PRIMING_EVENTS, {}, 60)] == [500, 50, 33, 800, 250]


@pytest.mark.parametrize("frames,ms", [(30, 500), (48, 800), (15, 250), (3, 50), (2, 33), (1, 17)])
def test_individual_frame_counts_at_sixty_hz(frames, ms):
    assert _frames_to_ms(frames, 60) == ms


def test_a_declared_duration_in_milliseconds_is_independent_of_the_refresh_rate():
    ev = [{"type": "fixation", "content": "+", "duration_ms": 500}]
    for hz in (60, 75, 100, 120, 144, 165, 240):
        assert render_events(ev, {}, hz)[0]["ms"] == 500


def test_milliseconds_win_over_frames_when_a_design_declares_both():
    ev = [{"type": "fixation", "content": "+", "duration_frames": 30, "duration_ms": 123}]
    assert render_events(ev, {}, 60)[0]["ms"] == 123


def test_the_timing_block_overrides_by_event_type_in_either_unit():
    # word_* reaches only a text event whose trigger is "condition", so the
    # priming prime (trigger 20) keeps its own duration.
    out = render_events(PRIMING_EVENTS, {"fixation_ms": 250, "word_ms": 400, "isi_ms": 900}, 60)
    assert [e["ms"] for e in out] == [250, 50, 33, 400, 900]
    out = render_events(PRIMING_EVENTS, {"fixation_frames": 15, "word_frames": 24}, 60)
    assert [e["ms"] for e in out] == [250, 50, 33, 400, 250]


def test_an_unknown_timing_key_is_rejected_rather_than_ignored():
    with pytest.raises(ValueError, match="unknown timing key"):
        render_events(PRIMING_EVENTS, {"fixation_frame": 30}, 60)


def test_the_assumed_refresh_rate_is_read_from_the_schema_and_must_be_positive():
    assert _refresh_hz({}) == 60.0
    assert _refresh_hz({"presentation": {"assumed_refresh_hz": 144}}) == 144.0
    with pytest.raises(ValueError, match="positive"):
        _refresh_hz({"presentation": {"assumed_refresh_hz": 0}})


def test_conversion_matches_the_r_engine_over_the_whole_reachable_surface():
    """A golden digest over frames 1..600 at every plausible refresh rate.

    R_workflow/tests/testthat/test-timing.R computes the same digest, so the two
    suites fail together if either engine's arithmetic drifts. Regenerate both
    together, never one.
    """
    import hashlib

    parts = []
    for hz in (60, 75, 100, 120, 144, 165, 240):
        for frames in range(1, 601):
            parts.append("%d:%d:%d" % (hz, frames, _frames_to_ms(frames, hz)))
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
    assert digest == "b57787d6860cff4956e5aaa3e5951584c5e55d8064f6cabb2eb9feb66f7a2c13"


def test_event_ms_prefers_an_override_over_the_events_own_duration():
    ev = {"type": "fixation", "duration_frames": 30}
    assert _event_ms(ev, 111, None, 60) == 111          # ms override wins
    assert _event_ms(ev, None, 6, 60) == 100            # frame override converts
    assert _event_ms(ev, None, None, 60) == 500         # falls back to the event


def test_the_trigger_hold_is_declared_in_milliseconds():
    from lexsync.scripting import _trigger_hold_ms
    assert _trigger_hold_ms({"triggers": {"trigger_hold_ms": 50}}) == 50.0
    assert _trigger_hold_ms({}) == 50.0
    with pytest.raises(ValueError, match="positive"):
        _trigger_hold_ms({"triggers": {"trigger_hold_ms": 0}})


def test_reset_after_frames_converts_with_the_off_by_one_it_actually_had():
    """`reset_after_frames: N` held the code for N + 1 flip intervals, not N.

    The reset was queued on flip N and callOnFlip fires on the FOLLOWING flip, so
    converting N directly would silently shorten every trigger by one frame. The
    default of 2 must therefore land on 50 ms at 60 Hz, not 33 ms.
    """
    from lexsync.scripting import _trigger_hold_ms
    assert _trigger_hold_ms({"triggers": {"reset_after_frames": 2}}) == 50.0
    assert (_trigger_hold_ms({"triggers": {"reset_after_frames": 2}})
            == _trigger_hold_ms({"triggers": {"trigger_hold_ms": 50}}))
    # An explicit hold wins over the legacy key.
    assert _trigger_hold_ms(
        {"triggers": {"trigger_hold_ms": 20, "reset_after_frames": 2}}) == 20.0


# ---- A fixed duration is a finite number that is not negative --------------------
#
# duration_ms: -50 was written into the OpenSesame experiment as clock.sleep(-50), the R
# engine wrote clock.sleep(NA) for a NaN, and both truncated 33.7 ms to 33.
# test-timing.R pins the same rules and messages.

_DURATION_RULE = "; a duration must be a finite number, not negative."


@pytest.mark.parametrize("event,message", [
    ({"type": "fixation", "content": "+", "duration_ms": -50},
     "lexsync: event 1 has duration_ms '-50'"),
    ({"type": "fixation", "content": "+", "duration_ms": float("nan")},
     "lexsync: event 1 has duration_ms 'NaN'"),
    ({"type": "blank", "duration_frames": -2}, "lexsync: event 1 has duration_frames '-2'"),
    ({"type": "blank", "duration_frames": float("inf")},
     "lexsync: event 1 has duration_frames 'Inf'"),
    ({"type": "fixation", "content": "+", "duration_ms": "500ms"},
     "lexsync: event 1 has duration_ms '500ms'"),
    ({"type": "fixation", "content": "+", "duration_ms": True},
     "lexsync: event 1 has duration_ms 'true'"),
])
def test_a_negative_or_non_finite_fixed_duration_is_refused(event, message):
    with pytest.raises(ValueError, match=re.escape(message + _DURATION_RULE)):
        render_events([event], {}, 60)


def test_a_timing_block_duration_is_checked_like_an_events_own():
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: timing.word_ms is '-50'" + _DURATION_RULE)):
        render_events(PRIMING_EVENTS, {"word_ms": -50}, 60)
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: timing.isi_frames is 'NaN'" + _DURATION_RULE)):
        render_events(PRIMING_EVENTS, {"isi_frames": float("nan")}, 60)
    # A feedback event is numbered where it stands in the design.
    feedback = [{"type": "response"}, {"type": "feedback", "duration_ms": -1}]
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: event 2 has duration_ms '-1'" + _DURATION_RULE)):
        render_events(feedback, {}, 60)


def test_a_fractional_fixed_duration_is_rounded_not_truncated():
    events = [{"type": "fixation", "content": "+", "duration_ms": 33.7},
              {"type": "text", "content": "{w}", "duration_ms": 82.5, "trigger": "condition"},
              {"type": "blank", "duration_ms": "250"}]
    # The shared rounder takes 82.5 away from zero. A duration written as a plain
    # number in quotes is read as that number, as before.
    assert [e["ms"] for e in render_events(events, {}, 60)] == [34, 83, 250]
    assert render_events(events, {"word_ms": 400.5}, 60)[1]["ms"] == 401
    # A null duration_frames is absent, as it is in the R engine, so the default of one
    # frame applies.
    assert render_events([{"type": "blank", "duration_frames": None}], {}, 60)[0]["ms"] == 17
