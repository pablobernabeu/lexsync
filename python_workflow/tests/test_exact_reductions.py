"""The reproducible reductions, and the cell formatter that matches readr.

Both exist because the package's byte-identity claim was failing in ways nothing
caught. The reductions replace numpy's pairwise summation, which differed from R's
mean() by enough to move a reported mean in the last decimal it publishes. The cell
formatter replaces pandas' float and bool rendering, which differed from readr's in
three ways across 653 cells of the shipped designs' artefacts.

test-exact-reductions.R asserts the same properties on the R side, and
test_byte_parity.py checks the end result on the real artefacts.
"""
import math

import pytest

from lexsync.io_utils import (_exact_mean, _exact_sd, _exact_sum, _exact_var,
                              _readr_cell, _readr_sci)


def test_the_sum_is_exact_where_a_naive_loop_is_not():
    # The classic compensated-summation case: a large value followed by many small ones
    # that a naive accumulator loses entirely.
    xs = [1e16] + [1.0] * 100
    naive = 0.0
    for v in xs:
        naive += v
    assert naive == 1e16                 # every 1.0 was swallowed
    assert _exact_sum(xs) == 1e16 + 100  # compensation recovers them
    # And it agrees with the exactly-rounded reference on the same data.
    assert _exact_sum(xs) == math.fsum(xs)


def test_the_sum_matches_the_exactly_rounded_reference():
    # math.fsum is exactly rounded, so agreeing with it over awkward data is the
    # strongest available check that the compensated sum is right. It is not what the
    # engines run -- both run the compensated loop -- but it is the right yardstick.
    cases = [
        [0.1] * 1000,
        [1e-20, 1e20, -1e20, 1e-20],
        [(-1) ** i * (i + 1) * 0.1 for i in range(500)],
        [1 / 7] * 999,
        [1e100, 1.0, -1e100],
    ]
    for xs in cases:
        assert _exact_sum(xs) == math.fsum(xs), xs[:3]


def test_order_does_not_change_the_sum_for_these_cases():
    # Not a general guarantee -- compensated summation is not order-independent in
    # principle -- but the engines iterate a column in the same order, and this pins
    # that the algorithm is stable for realistic data rather than luckily so.
    xs = [3.7, 1.2, 9.9, 0.001, 5.5, 2.25, 8.125]
    assert _exact_sum(xs) == _exact_sum(list(reversed(xs)))


def test_mean_and_variance_on_a_known_case():
    xs = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
    assert _exact_mean(xs) == 5.0
    assert _exact_var(xs) == pytest.approx(4.571428571428571, abs=0)
    assert _exact_sd(xs) == math.sqrt(_exact_var(xs))


def test_degenerate_inputs_are_not_silently_zero():
    assert _exact_mean([]) != _exact_mean([])       # NaN
    assert _exact_var([1.0]) != _exact_var([1.0])   # NaN: variance needs two values
    assert _exact_var([2.0, 2.0]) == 0.0
    assert _exact_sd([2.0, 2.0]) == 0.0


def test_variance_survives_data_far_from_zero():
    # The one-pass "sum of squares minus n times squared mean" form cancels
    # catastrophically here and can even return a negative variance; the two-pass form
    # gives the right answer.
    xs = [1e9 + 4.0, 1e9 + 7.0, 1e9 + 13.0, 1e9 + 16.0]
    assert _exact_var(xs) == pytest.approx(30.0, abs=1e-9)
    assert _exact_var(xs) >= 0


# --- The readr-matching cell formatter ---------------------------------------
# Every expected value here was measured from readr 2.2.0, not assumed.

@pytest.mark.parametrize("value,expected", [
    (0.0, "0"), (1.0, "1"), (-1.0, "-1"), (3.0, "3"), (1e5, "100000"),
    (1.5, "1.5"), (0.1, "0.1"), (0.001, "0.001"), (0.0012, "0.0012"),
    (0.0099, "0.0099"), (0.00999, "0.00999"), (0.15, "0.15"),
    (9e-4, "9e-4"), (0.00099, "9.9e-4"), (0.0009999, "9.999e-4"),
    (1e-4, "1e-4"), (0.00012, "1.2e-4"), (2.5e-5, "2.5e-5"), (1e-10, "1e-10"),
    (-9e-4, "-9e-4"), (0.000999999, "9.99999e-4"),
    (1 / 3, "0.3333333333333333"), (0.1 + 0.2, "0.30000000000000004"),
    (123456.789, "123456.789"),
])
def test_the_cell_formatter_reproduces_readr(value, expected):
    assert _readr_cell(value) == expected
    assert float(_readr_cell(value)) == value        # and it round-trips


def test_booleans_and_missing_values():
    assert _readr_cell(True) == "TRUE"
    assert _readr_cell(False) == "FALSE"
    assert _readr_cell(float("nan")) == ""
    assert _readr_cell(None) == ""


def test_the_large_magnitude_gap_is_now_an_error_rather_than_a_divergence():
    # This used to assert the divergence: readr wrote "1e15" and this writer wrote
    # "1000000000000000", and the gap was accepted because no shipped design reaches
    # that range. That protected the repository's own designs, which test_byte_parity.py
    # covers, and not a user's joined norm column, which nothing covers. The value is
    # refused by both engines now. The tests at the end of this file pin the boundary.
    with pytest.raises(ValueError):
        _readr_cell(1e15)


def test_the_scientific_helper_is_normalised_and_unpadded():
    # Python's own form pads the exponent ("1e-05"); readr does not.
    assert _readr_sci(1e-5) == "1e-5"
    assert _readr_sci(0.00025) == "2.5e-4"


@pytest.mark.parametrize("value,dp,expected", [
    (7.8125, 3, 7.813),     # half AWAY from zero
    (-7.8125, 3, -7.813),   # and away for negatives
    (2.5, 0, 3.0),
    (-2.5, 0, -3.0),
    (1.0005, 3, 1.001),
    (4.2505, 3, 4.251),
    (0.0, 3, 0.0),
])
def test_the_shared_decimal_rounder_is_pinned(value, dp, expected):
    """No pairing of built-ins agrees. Measured over 210,000 values including every 3-dp
    halfway case in range: Python's builtin round() disagrees with R's round(), numpy's
    disagrees with both, and even Python's "%.3f" disagrees with R's sprintf("%.3f") on
    274 of them. So the rounder is defined by its arithmetic instead, and both engines
    compute the same double by construction. test-exact-reductions.R asserts these same
    values."""
    from lexsync.io_utils import _round_dp
    assert _round_dp(value, dp) == expected


def test_the_shared_rounder_differs_from_the_builtins_where_expected():
    """The divergence this replaces, stated so it cannot quietly come back."""
    import numpy as np

    from lexsync.io_utils import _round_dp
    assert _round_dp(7.8125, 3) != round(7.8125, 3)          # builtin: half to even
    assert _round_dp(4.2505, 3) != float(np.round(4.2505, 3))
    # Non-finite values pass through rather than becoming nonsense.
    assert _round_dp(float("inf"), 3) == float("inf")
    assert _round_dp(float("nan"), 3) != _round_dp(float("nan"), 3)


# ---- The CSV writer's magnitude limits -------------------------------------------


@pytest.mark.parametrize("value,expected", [
    (5e14, "500000000000000"),          # readr keeps fixed notation up to 1e15
    (999999999999999.0, "999999999999999"),
    (100000000000000.5, "100000000000000.5"),
    (562949953421312.5, "562949953421312.5"),   # above 2**49, but unambiguous
    (0.0009, "9e-4"),
    (0.00012, "1.2e-4"),
    (1.0, "1"),
])
def test_the_writer_matches_readr_where_it_can(value, expected):
    """Each expected string was read off readr 2.2.0's own write_csv output, not
    assumed. test-exact-reductions.R writes the same values through readr and asserts
    the same strings, so a readr change breaks both suites rather than one."""
    from lexsync.io_utils import _readr_cell
    assert _readr_cell(value) == expected


@pytest.mark.parametrize("value", [1e15, 1.5e16, 5e22, 1.7976931348623157e308, -1e15])
def test_the_writer_refuses_magnitudes_it_cannot_reproduce(value):
    """readr's layout above 1e15 could not be reproduced: 1.5e16 comes out "15e15" with
    an integer mantissa, the largest double "17976931348623157e292", but the double
    nearest 5e22 "4.9999999999999996e+22" -- more digits than round-tripping needs. No
    rule fits all three, so the value is refused rather than written differently by the
    two engines. Nothing lexsync computes reaches this range; a joined norm table can."""
    from lexsync.io_utils import _readr_cell
    with pytest.raises(ValueError, match="too large to write identically"):
        _readr_cell(value)


def test_the_writer_refuses_an_ambiguous_shortest_decimal():
    """1000000000000000.25 has two shortest forms that both round-trip. readr prints
    ...0.3 and Python's repr gives ...0.2, and no reformatting reconciles them because
    the digits differ. Caught here rather than in a user's diff."""
    from lexsync.io_utils import _readr_cell, _shortest_digits_ambiguous
    assert _shortest_digits_ambiguous(1000000000000000.25)
    assert not _shortest_digits_ambiguous(562949953421312.5)
    with pytest.raises(ValueError):
        _readr_cell(1000000000000000.25)


def test_a_large_value_is_refused_on_the_way_into_a_csv(tmp_path):
    """The guard has to bite where user data actually arrives: a norm column joined onto
    the lexicon is written straight into the stimuli CSV."""
    import pandas as pd

    from lexsync.io_utils import write_csv_utf8
    df = pd.DataFrame({"word": ["a", "b"], "norm": [1.0, 2e15]})
    with pytest.raises(ValueError, match="too large to write identically"):
        write_csv_utf8(df, str(tmp_path / "x.csv"))
