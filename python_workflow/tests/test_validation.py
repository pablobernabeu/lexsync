import pandas as pd

from lexsync.validation import (
    balance_check, cohens_d, cohens_d_ci, describe_stimuli, tost_equiv,
)


def test_cohens_d():
    assert cohens_d([1, 2, 3, 4], [1, 2, 3, 4]) == 0
    assert abs(cohens_d([5, 6, 7, 8], [1, 2, 3, 4])) > 1


def test_tost_equivalent_for_matched_samples():
    x = [4, 5, 6] * 20
    y = [4, 5, 6] * 20
    assert tost_equiv(x, y, bound_d=0.5)["equivalent"] is True


def test_cohens_d_ci_brackets_point_estimate():
    x = [5, 6, 7, 8] * 10
    y = [1, 2, 3, 4] * 10
    ci = cohens_d_ci(x, y)
    assert ci["ci_low"] <= ci["d"] <= ci["ci_high"]
    # The point estimate matches the standalone Cohen's d.
    assert abs(ci["d"] - cohens_d(x, y)) < 1e-9


def test_cohens_d_ci_width_shrinks_with_more_items():
    # The interval's dependence on the number of items is the property that makes
    # it a robust complement to the binary TOST verdict: few items -> wide CI.
    small = cohens_d_ci([4, 5, 6] * 2, [4, 5, 7] * 2)
    large = cohens_d_ci([4, 5, 6] * 40, [4, 5, 7] * 40)
    assert (small["ci_high"] - small["ci_low"]) > (large["ci_high"] - large["ci_low"])


def test_cohens_d_ci_coheres_with_tost():
    # The 90% CI lying inside +/- bound is equivalent to a TOST pass at .05.
    x = [4, 5, 6] * 20
    y = [4, 5, 6] * 20
    ci = cohens_d_ci(x, y, alpha=0.05)
    within = (ci["ci_low"] > -0.5) and (ci["ci_high"] < 0.5)
    assert within == bool(tost_equiv(x, y, bound_d=0.5, alpha=0.05)["equivalent"])


def test_cohens_d_ci_constant_dimension_is_a_point():
    # A dimension fixed by the pool (e.g. two-character words) has no uncertainty.
    ci = cohens_d_ci([2, 2, 2, 2], [2, 2, 2, 2])
    assert ci == {"d": 0.0, "ci_low": 0.0, "ci_high": 0.0}


def test_describe_and_balance():
    df = pd.DataFrame({"condition": ["a", "a", "b", "b"], "x": [1, 2, 3, 4]})
    d = describe_stimuli(df, ["x"])
    assert {"group", "dimension", "n", "mean", "sd"} <= set(d.columns)
    assert len(d) == 2
    assert len(balance_check(pd.DataFrame({"condition": ["a", "a", "a", "b"]}), "condition")) == 1
    assert len(balance_check(pd.DataFrame({"condition": ["a", "a", "b", "b"]}), "condition")) == 0
