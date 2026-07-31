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
import pandas as pd
import pytest

from lexsync.scripting import (_duration_spec, _key_part, loop_table, render_events,
                               resolve_trial_timing)

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
