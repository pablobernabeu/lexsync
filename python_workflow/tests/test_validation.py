import inspect
import math

import numpy as np
import pandas as pd

from lexsync.validation import (
    balance_check,
    cohens_d,
    cohens_d_ci,
    describe_stimuli,
    match_report,
    match_report_continuous,
    tost_equiv,
    variance_ratio,
)


def _cont_stim():
    return pd.DataFrame({
        "word": ["a", "b", "c", "d"], "condition": "continuous",
        "frequency": [2.0, 3.0, 4.0, 5.0], "length": [3, 4, 3, 4],
        "n_density": [1, 2, 1, 2], "old20": [1.5, 1.6, 1.5, 1.6],
    })


def test_match_report_continuous_shape(schema):
    rep = match_report_continuous(_cont_stim(), "frequency",
                                  ["length", "n_density", "old20"], schema)
    assert set(rep) == {"descriptives", "comparisons"}
    c = rep["comparisons"]
    assert list(c.columns) == ["dimension", "role", "pearson_r", "predictor_span"]
    assert list(c["role"]) == ["predictor", "control", "control", "control"]
    assert c.loc[c.dimension == "frequency", "predictor_span"].iloc[0] == 3.0


def test_cohens_d():
    assert cohens_d([1, 2, 3, 4], [1, 2, 3, 4]) == 0
    assert abs(cohens_d([5, 6, 7, 8], [1, 2, 3, 4])) > 1


def test_tost_equivalent_for_matched_samples():
    x = [4, 5, 6] * 20
    y = [4, 5, 6] * 20
    assert tost_equiv(x, y, bound_d=0.5)["equivalent"] is True


def test_tost_default_bound_is_the_schema_bound():
    # The bound is the schema's smallest effect size of interest (Lakens, 2017);
    # pinned here because every other test passes bound_d explicitly. The p-value is
    # the same literal asserted in test-validation.R, so the engines cannot drift apart.
    assert inspect.signature(tost_equiv).parameters["bound_d"].default == 0.5
    assert round(tost_equiv(range(10, 20), range(11, 21))["p"], 9) == 0.354383811


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


def test_zero_pooled_sd_with_unequal_means_is_undefined_not_zero():
    # Two conditions each constant at a different value differ by infinitely many
    # SDs: reporting d = 0 (perfect balance) inverted the truth. The equal-constant
    # case is pinned by the zh_freqcontrast golden and must stay exactly zero.
    x = [2, 2, 2, 2]
    y = [3, 3, 3, 3]
    assert cohens_d(x, y) is None
    assert cohens_d_ci(x, y) == {"d": None, "ci_low": None, "ci_high": None}
    assert tost_equiv(x, y)["equivalent"] is False  # already correct on this branch
    assert variance_ratio(y, x) == 1.0              # unchanged: both spreads are zero
    assert cohens_d(x, x) == 0                      # equal constants stay exactly zero


def test_match_report_carries_an_undefined_d_as_a_missing_cell(schema):
    # Serialised as an empty CSV cell and a null JSON value, exactly like the other
    # missing statistics, and identically in both engines.
    stim = pd.DataFrame({"word": ["aa", "bb", "cc", "dd"],
                         "condition": ["a", "a", "b", "b"],
                         "length": [2, 2, 3, 3]})
    cmp = match_report(stim, ["length"], schema)["comparisons"]
    assert cmp["cohens_d"].isna().iloc[0]
    assert cmp["d_ci_low"].isna().iloc[0]
    assert cmp["d_ci_high"].isna().iloc[0]
    assert cmp["equivalent"].iloc[0] == False  # noqa: E712 -- numpy bool, not None
    assert cmp["var_ratio"].iloc[0] == 1.0


def test_variance_ratio():
    assert abs(variance_ratio([1, 2, 3, 4], [1, 2, 3, 4]) - 1.0) < 1e-9  # equal spread
    assert variance_ratio([0, 5, 10, 15], [4, 5, 6, 7]) > 1              # condition wider
    assert variance_ratio([4, 5, 6, 7], [0, 5, 10, 15]) < 1             # condition narrower
    assert variance_ratio([1, 2, 3], [5, 5, 5]) is None                  # constant reference
    assert variance_ratio([5, 5, 5], [2, 2, 2]) == 1.0                   # both constant


def test_describe_and_balance():
    df = pd.DataFrame({"condition": ["a", "a", "b", "b"], "x": [1, 2, 3, 4]})
    d = describe_stimuli(df, ["x"])
    assert {"group", "dimension", "n", "mean", "sd"} <= set(d.columns)
    assert len(d) == 2
    assert len(balance_check(pd.DataFrame({"condition": ["a", "a", "a", "b"]}), "condition")) == 1
    assert len(balance_check(pd.DataFrame({"condition": ["a", "a", "b", "b"]}), "condition")) == 0


def test_describe_stimuli_groups_in_first_appearance_order():
    # Not sorted order: this is the order validation.R's appearance-ordered factor
    # yields, and the order in which match_report() takes its anchor.
    df = pd.DataFrame({"condition": ["b", "b", "a", "a"], "x": [1, 2, 3, 4]})
    assert list(describe_stimuli(df, ["x"])["group"]) == ["b", "a"]


def test_describe_stimuli_all_na_dimension_is_missing_not_infinite():
    df = pd.DataFrame({"condition": ["a", "a"], "x": [np.nan, np.nan]})
    d = describe_stimuli(df, ["x"])
    assert d["n"].iloc[0] == 0
    assert math.isnan(d["min"].iloc[0])
    assert math.isnan(d["max"].iloc[0])
    assert not math.isinf(d["min"].iloc[0])
    assert not math.isinf(d["max"].iloc[0])
