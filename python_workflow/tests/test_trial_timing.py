"""Per-trial event durations: jittered, or read from an item column.

A fixed duration is a property of the design; one that varies from trial to trial
is a property of the trial, and therefore a variable the analysis needs. Both
forms are resolved here into the stimuli table before anything is generated, so
the realised milliseconds travel with the stimuli rather than living only inside
the presentation script.

The jitter draws no random number. It is a uniform integer keyed on the seed, the
column name, the list, the set and the condition, so the two engines realise the
same milliseconds and a rerun reproduces them. Naming the column in the key is
what makes two jittered events in one design draw independently instead of
sharing a value.

R_workflow/tests/testthat/test-trial-timing.R asserts the same values.
"""
import re

import pandas as pd
import pytest

from lexsync.scripting import _duration_spec, _key_part, loop_table, render_events, resolve_trial_timing

SCHEMA = {"seed": 42}

EVENTS = [
    {"type": "fixation", "content": "+", "duration_ms": 500},
    {"type": "text", "content": "{prime}", "duration": {"from_column": "soa_ms"}, "trigger": 20},
    {"type": "text", "content": "{target}", "duration_ms": 800, "trigger": "condition"},
    {"type": "blank", "duration": {"jitter": [400, 800], "as": "isi_ms"}},
]

STIM = pd.DataFrame({
    "set": [1, 2, 3, 4],
    "condition": ["related", "unrelated", "related", "unrelated"],
    "list": [1, 1, 2, 2],
    "prime": ["cat", "sun", "dog", "car"],
    "target": ["pet", "sky", "pet", "van"],
    "soa_ms": [60, 250, 1200, 60],
    "trial": [1, 2, 3, 4],
})


def test_a_jittered_duration_lands_in_the_stimuli_table_within_its_range():
    out = resolve_trial_timing(STIM, {"events": EVENTS}, SCHEMA)
    assert "isi_ms" in out.columns
    assert out["isi_ms"].between(400, 800).all()
    # Deterministic: the same inputs give the same milliseconds every time.
    assert list(out["isi_ms"]) == list(resolve_trial_timing(STIM, {"events": EVENTS}, SCHEMA)["isi_ms"])


def test_the_realised_values_match_the_r_engine():
    out = resolve_trial_timing(STIM, {"events": EVENTS}, SCHEMA)
    assert list(out["isi_ms"]) == [537, 583, 764, 594]


def test_the_seed_changes_the_draw_and_nothing_else_does():
    a = resolve_trial_timing(STIM, {"events": EVENTS}, {"seed": 42})["isi_ms"]
    b = resolve_trial_timing(STIM, {"events": EVENTS}, {"seed": 43})["isi_ms"]
    assert list(a) != list(b)


def test_two_jittered_events_draw_independently():
    events = [
        {"type": "blank", "duration": {"jitter": [0, 1000], "as": "gap_a_ms"}},
        {"type": "blank", "duration": {"jitter": [0, 1000], "as": "gap_b_ms"}},
    ]
    out = resolve_trial_timing(STIM, {"events": events}, SCHEMA)
    # Sharing a key would make these identical; the column name is in the key.
    assert list(out["gap_a_ms"]) != list(out["gap_b_ms"])


def test_a_column_duration_is_referenced_rather_than_baked_in():
    rendered = render_events(EVENTS, {}, 60)
    assert rendered[0]["ms"] == 500                 # fixed, resolved at build time
    assert rendered[1]["ms_column"] == "soa_ms"     # per trial, resolved at run time
    assert "ms" not in rendered[1]
    assert rendered[3]["ms_column"] == "isi_ms"


def test_the_loop_table_carries_every_per_trial_duration_column():
    out = resolve_trial_timing(STIM, {"events": EVENTS}, SCHEMA)
    tab = loop_table(out, EVENTS)
    assert "soa_ms" in tab.columns and "isi_ms" in tab.columns


def test_a_missing_source_column_is_an_error_not_a_silent_default():
    events = [{"type": "blank", "duration": {"from_column": "not_there"}}]
    with pytest.raises(ValueError, match="which the items do not have"):
        resolve_trial_timing(STIM, {"events": events}, SCHEMA)


def test_a_malformed_duration_block_is_rejected():
    with pytest.raises(ValueError, match="two-element range"):
        render_events([{"type": "blank", "duration": {"jitter": [400]}}], {}, 60)
    with pytest.raises(ValueError, match="from_column' or 'jitter'"):
        render_events([{"type": "blank", "duration": {"nonsense": 1}}], {}, 60)


def test_an_unnamed_jitter_column_falls_back_to_the_event_index():
    events = [{"type": "fixation", "content": "+"}, {"type": "blank",
              "duration": {"jitter": [10, 20]}}]
    assert _duration_spec(events[1], 2)["column"] == "event2_ms"


def test_key_parts_render_integral_floats_like_r_does():
    # The hazard this guards: a pandas column promoted to float64 by one missing
    # value would otherwise key on "3.0" in Python and "3" in R.
    assert _key_part(3) == "3"
    assert _key_part(3.0) == "3"
    assert _key_part(-7.0) == "-7"
    assert _key_part("related") == "related"
    assert _key_part(2.5) == "2.5"


def test_a_hash_key_component_that_cannot_be_rendered_identically_is_refused():
    """Measured divergence before this: a missing value rendered "nan" here and "NA" in
    R, True/False against TRUE/FALSE, inf against Inf. A blank `condition` cell is a
    routine data error that neither reader rejects, and it produced a DIFFERENT trial
    order in each engine -- reproducibly, with nothing to signal it."""
    import pytest

    from lexsync.io_utils import _key_part
    for bad in (None, float("nan")):
        with pytest.raises(ValueError, match="missing"):
            _key_part(bad)
    with pytest.raises(ValueError, match="not finite"):
        _key_part(float("inf"))
    # Booleans are legitimate, so they get a pinned spelling rather than a refusal.
    # test-trial-timing.R asserts the same two strings.
    assert _key_part(True) == "TRUE"
    assert _key_part(False) == "FALSE"
    # A value past the integer range would make R's as.integer() return NA, which would
    # put an empty component into the key.
    assert _key_part(3e9) == "3000000000"


# ---- A duration read from the items is checked, and a fractional one rounded --------
#
# A blank or negative value used to reach the experiments, where OpenSesame's int('')
# and PsychoPy's float('') raised during the session and jsPsych ended the trial at
# once. A fractional value kept all its digits, which R's jsonlite cut to four decimal
# places, so the two engines' jsPsych pages differed. test-trial-timing.R pins the same
# values and messages.

def _with_soa(values):
    return STIM.assign(soa_ms=values)


def test_a_fractional_column_duration_is_rounded_once_and_recorded():
    # A frame at 60 Hz lasts 1000/60 ms, which an item table carries to six places.
    out = resolve_trial_timing(_with_soa([33.333333, 250, 82.5, 66.666667]),
                               {"events": EVENTS}, SCHEMA)
    # The shared rounder takes 82.5 away from zero, where Python's round() gives 82.
    assert list(out["soa_ms"]) == [33, 250, 83, 67]
    assert out.attrs["duration_rounding"] == [{"event": 2, "column": "soa_ms", "n_rounded": 3}]
    assert list(loop_table(out, EVENTS)["soa_ms"]) == [33, 250, 83, 67]
    # Rounded once: the realised table has nothing left to round, and the record of the
    # first call does not carry over to the second.
    again = resolve_trial_timing(out, {"events": EVENTS}, SCHEMA)
    assert list(again["soa_ms"]) == [33, 250, 83, 67]
    assert "duration_rounding" not in again.attrs


def test_whole_column_durations_are_left_as_they_are():
    out = resolve_trial_timing(STIM, {"events": EVENTS}, SCHEMA)
    assert list(out["soa_ms"]) == [60, 250, 1200, 60]
    assert out["soa_ms"].dtype == STIM["soa_ms"].dtype
    assert "duration_rounding" not in out.attrs


@pytest.mark.parametrize("value,what", [
    (float("nan"), "is blank"),
    (None, "is blank"),
    (-50, "holds '-50'"),
    (float("inf"), "holds 'Inf'"),
    ("fast", "holds 'fast'"),
])
def test_a_column_duration_that_is_blank_negative_or_not_a_number_is_refused(value, what):
    stim = _with_soa([60, value, 1200, 60])
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: event 2 reads its duration from column 'soa_ms', which %s for set 2 in "
            "condition 'unrelated'; a duration must be a finite number of milliseconds, not "
            "negative." % what)):
        resolve_trial_timing(stim, {"events": EVENTS}, SCHEMA)
    # A column of booleans is not a duration either, although Python counts True as 1.
    with pytest.raises(ValueError, match=re.escape(
            "which holds 'true' for set 1 in condition 'related'")):
        resolve_trial_timing(_with_soa([True, False, True, False]), {"events": EVENTS}, SCHEMA)


def test_a_refused_column_duration_names_the_block_of_its_trial():
    stim = _with_soa([60, 250, -1, 60]).assign(block=["practice", "main", "main", "main"])
    with pytest.raises(ValueError, match=re.escape(
            "which holds '-1' for set 3 in condition 'related' of block 'main'")):
        resolve_trial_timing(stim, {"events": EVENTS}, SCHEMA)


def test_a_jitter_range_must_start_at_zero_or_more():
    for bad, shown in (([-100, 200], "[-100, 200]"), ([0, float("nan")], "[0, NaN]")):
        with pytest.raises(ValueError, match=re.escape(
                "lexsync: event 1 has jitter %s; a jittered duration needs finite bounds, "
                "the lower one not negative." % shown)):
            render_events([{"type": "blank", "duration": {"jitter": bad}}], {}, 60)
    # Zero is a duration like any other.
    ok = render_events([{"type": "blank", "duration": {"jitter": [0, 200]}}], {}, 60)
    assert ok[0]["ms_column"] == "event1_ms"
