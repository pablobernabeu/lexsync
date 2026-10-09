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
    assert list(c.columns) == ["dimension", "role", "pearson_r", "predictor_span", "sd",
                               "sd_ratio", "window_low", "window_high"]
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


def test_cohens_d_ci_uses_the_large_sample_standard_error_of_d():
    # SE(d) = sqrt(1/nx + 1/ny + d**2 / (2 * (nx + ny))) (Hedges & Olkin, 1985;
    # Borenstein et al., 2009, eq. 4.20). The limits are the same literals asserted
    # in test-validation.R, so the engines cannot drift apart. The interval that
    # left out the d**2 term had a margin of 0.372 here, not 0.596.
    from scipy import stats

    x = [5, 6, 7, 8] * 10
    y = [1, 2, 3, 4] * 10
    ci = cohens_d_ci(x, y)
    assert [round(ci[k], 9) for k in ("d", "ci_low", "ci_high")] == [
        3.532704347, 2.937150129, 4.128258564]
    se = math.sqrt(1 / 40 + 1 / 40 + ci["d"] ** 2 / 160)
    assert math.isclose(ci["ci_high"] - ci["d"], stats.t.ppf(0.95, 78) * se, rel_tol=1e-12)
    # The d**2 term is what widens a large effect's interval: at the same n, a
    # difference near zero keeps close to the known-SD margin.
    null = cohens_d_ci([4, 5, 6] * 20, [4, 5, 6] * 20)
    assert math.isclose(null["ci_high"], stats.t.ppf(0.95, 118) * math.sqrt(2 / 60),
                        rel_tol=1e-12)
    assert ci["ci_high"] - ci["ci_low"] > 1.5 * (2 * stats.t.ppf(0.95, 78) * math.sqrt(1 / 20))


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


def test_match_report_gives_a_single_condition_design_an_empty_comparisons_frame(schema):
    """There is nothing to compare against the anchor, so the frame comes back with
    its columns and no rows. A DataFrame built from no rows carried no columns
    either, and wrote a comparisons CSV with no header at all, while the R engine's
    rbind() over an empty list returned NULL and killed run_pipeline's reporting
    loop. Pinned identically in test-validation.R."""
    stim = pd.DataFrame({"word": ["aa", "bb"], "condition": ["only", "only"],
                         "length": [2, 3]})
    cmp = match_report(stim, ["length"], schema)["comparisons"]
    assert len(cmp) == 0
    assert list(cmp.columns) == _COMPARISON_HEADER
    assert cmp.to_csv(index=False, lineterminator="\n").splitlines() == [
        ",".join(_COMPARISON_HEADER)]


# The columns of the comparisons frame, in order: the two CS-23 columns follow the
# ones a 0.1 reader already knows. Pinned identically in test-validation.R.
_COMPARISON_HEADER = ["condition", "reference", "dimension", "cohens_d", "d_ci_low",
                      "d_ci_high", "var_ratio", "tost_p", "equivalent", "mean_diff", "role"]


def test_cohens_d_is_undefined_with_fewer_than_two_items_a_side():
    """One item has no spread, so the pooled SD and with it d are undefined. Both
    functions returned 0, a perfect balance, for a frequency contrast of 6.5 against
    3.9. Pinned identically in test-validation.R."""
    assert cohens_d([6.5], [3.9]) is None
    assert cohens_d([6.5, 6.0], [3.9]) is None
    assert cohens_d([], [3.9, 4.1]) is None
    assert cohens_d_ci([6.5], [3.9]) == {"d": None, "ci_low": None, "ci_high": None}
    assert cohens_d_ci([np.nan, 6.5], [3.9, 4.1]) == {"d": None, "ci_low": None,
                                                      "ci_high": None}


def _four_conditions():
    # Two items per condition, so every d is defined. Condition `b` sits above `a` on
    # length by half a letter, `c` and `d` a whole letter above it.
    return pd.DataFrame({
        "word": ["a1", "a2", "b1", "b2", "c1", "c2", "d1", "d2"],
        "condition": ["a", "a", "b", "b", "c", "c", "d", "d"],
        "length": [3, 4, 3, 5, 4, 6, 5, 5],
        "frequency": [6.0, 6.5, 6.1, 6.3, 3.0, 3.5, 3.2, 3.1],
    })


def test_match_report_compares_every_pair_after_the_anchor_rows(schema):
    """The anchor rows come first and unchanged, then every further pair in condition
    order, with the earlier condition as the reference. Only the anchor rows were
    reported, so a 2 x 2 design never showed its within-factor contrasts. Pinned
    identically in test-validation.R."""
    stim = _four_conditions()
    cmp = match_report(stim, ["length", "frequency"], schema)["comparisons"]
    assert list(cmp.columns) == _COMPARISON_HEADER
    pairs = list(dict.fromkeys(zip(cmp["condition"], cmp["reference"], strict=True)))
    assert pairs == [("b", "a"), ("c", "a"), ("d", "a"),
                     ("c", "b"), ("d", "b"), ("d", "c")]
    assert list(cmp["dimension"]) == ["length", "frequency"] * 6
    # A further pair carries the statistics of a two-condition report on its own
    # conditions, oriented from its reference.
    alone = match_report(stim[stim["condition"].isin(["b", "c"])].reset_index(drop=True),
                         ["length", "frequency"], schema)["comparisons"]
    row = cmp[(cmp["condition"] == "c") & (cmp["reference"] == "b")].reset_index(drop=True)
    stats_cols = ["cohens_d", "d_ci_low", "d_ci_high", "var_ratio", "tost_p", "equivalent",
                  "mean_diff"]
    assert row[stats_cols].to_dict("records") == alone[stats_cols].to_dict("records")


def test_match_report_gives_the_raw_mean_difference(schema):
    """The reference mean minus the condition mean, in the dimension's own unit, to
    three places by the shared rounder. Pinned identically in test-validation.R."""
    cmp = match_report(_four_conditions(), ["length"], schema)["comparisons"]
    by_pair = {(c, r): v for c, r, v in zip(cmp["condition"], cmp["reference"],
                                            cmp["mean_diff"], strict=True)}
    assert by_pair[("b", "a")] == -0.5
    assert by_pair[("c", "b")] == -1.0
    assert by_pair[("d", "c")] == 0.0
    thirds = pd.DataFrame({"condition": ["r"] * 3 + ["s"] * 3,
                           "x": [1.0, 1.0, 2.0, 1.0, 1.0, 1.0]})
    assert match_report(thirds, ["x"], schema)["comparisons"]["mean_diff"].tolist() == [0.333]


def test_match_report_reports_a_mean_difference_where_d_is_undefined(schema):
    """With one item a side d is undefined, but the raw difference is not: 6.5 against
    3.9 Zipf is 2.6. Pinned identically in test-validation.R."""
    stim = pd.DataFrame({"condition": ["high", "low"], "frequency": [6.5, 3.9]})
    row = match_report(stim, ["frequency"], schema)["comparisons"].iloc[0]
    assert pd.isna(row["cohens_d"]) and pd.isna(row["d_ci_low"]) and pd.isna(row["tost_p"])
    assert row["mean_diff"] == 2.6


def test_match_report_skips_a_dimension_with_no_numeric_value(schema):
    """A dimension every item lacks, such as n_syllables for Chinese, or one that is
    not numeric, such as a part-of-speech label named in define_by, has nothing to
    compare and is left out of both frames. Pinned identically in test-validation.R."""
    stim = _four_conditions().assign(n_syllables=np.nan, pos="noun")
    rep = match_report(stim, ["length", "n_syllables", "pos"], schema)
    assert set(rep["comparisons"]["dimension"]) == {"length"}
    assert set(rep["descriptives"]["dimension"]) == {"length"}
    # With nothing left, both frames keep their columns and have no rows.
    none = match_report(stim, ["pos"], schema)
    assert list(none["descriptives"].columns) == ["group", "dimension", "n", "mean", "sd",
                                                  "min", "median", "max"]
    assert len(none["descriptives"]) == 0 and len(none["comparisons"]) == 0


def test_match_report_takes_each_rows_role_from_roles(schema):
    """`roles` gives the role of each row from its condition, reference and dimension.
    Without it the role is missing. Pinned identically in test-validation.R."""
    seen = []

    def roles(condition, reference, dimension):
        seen.append((condition, reference, dimension))
        return "controlled" if dimension == "length" else "manipulated"

    cmp = match_report(_four_conditions(), ["length", "frequency"], schema,
                       roles=roles)["comparisons"]
    assert list(cmp["role"]) == ["controlled", "manipulated"] * 6
    assert seen[:3] == [("b", "a", "length"), ("b", "a", "frequency"), ("c", "a", "length")]
    plain = match_report(_four_conditions(), ["length"], schema)["comparisons"]
    assert plain["role"].isna().all()


def test_match_report_continuous_gives_the_spreads_and_the_windows(schema):
    """The predictor's SD against that of as many values spaced evenly over its range,
    each control's SD against the pool's and the control's window, both from the
    selector's audit. Pinned identically in test-validation.R."""
    audit = {"control_windows": [
        {"dimension": "length", "low": 2.25, "high": 4.75, "pool_sd": 1.0},
        {"dimension": "n_density", "low": 0.5, "high": 2.5, "pool_sd": 2.0},
        {"dimension": "old20", "low": 1.4, "high": 1.7, "pool_sd": 0.1}]}
    rep = match_report_continuous(_cont_stim(), "frequency",
                                  ["length", "n_density", "old20"], schema, audit=audit)
    c = rep["comparisons"].set_index("dimension")
    assert list(rep["comparisons"].columns) == [
        "dimension", "role", "pearson_r", "predictor_span", "sd", "sd_ratio",
        "window_low", "window_high"]
    # frequency 2, 3, 4, 5 is itself an even spread, so its SD of 1.291 gives a ratio of
    # 1. Set against 3 / sqrt(12) = 0.866, the limit for many values, it read 1.491.
    assert c.loc["frequency", "sd"] == 1.291
    assert c.loc["frequency", "sd_ratio"] == 1.0
    assert pd.isna(c.loc["frequency", "window_low"])
    # length 3, 4, 3, 4: SD 0.577 against the pool's 1.
    assert c.loc["length", "sd"] == 0.577
    assert c.loc["length", "sd_ratio"] == 0.577
    assert (c.loc["length", "window_low"], c.loc["length", "window_high"]) == (2.25, 4.75)
    assert c.loc["n_density", "sd_ratio"] == 0.289
    assert c.loc["old20", "sd_ratio"] == 0.577


def test_match_report_continuous_reads_the_windows_off_the_selection(schema):
    """Without an explicit audit the report reads the one the selector attached, and
    without either a control's ratio and window are missing. Pinned identically in
    test-validation.R."""
    stim = _cont_stim()
    stim.attrs["audit"] = {"control_windows": [
        {"dimension": "length", "low": 2.0, "high": 5.0, "pool_sd": 2.0}]}
    c = match_report_continuous(stim, "frequency", ["length"], schema)["comparisons"]
    assert c.loc[1, "sd_ratio"] == 0.289 and c.loc[1, "window_high"] == 5.0
    bare = match_report_continuous(_cont_stim(), "frequency", ["length"], schema)
    assert pd.isna(bare["comparisons"].loc[1, "sd_ratio"])
    assert pd.isna(bare["comparisons"].loc[1, "window_low"])
    # The predictor's ratio needs only the selection itself.
    assert bare["comparisons"].loc[0, "sd_ratio"] == 1.0


def test_the_predictor_sd_ratio_is_1_for_an_even_spread_of_any_size(schema):
    """The benchmark is the SD of as many values spaced evenly over the realised range,
    (max - min) * sqrt(n (n + 1) / 12) / (n - 1), with the n - 1 that `sd` uses. Set
    against (max - min) / sqrt(12), its limit for many values, an even spread of 8
    items read 1.21 and one of 4 items 1.49, as if the items crowded the ends of the
    range. Pinned identically in test-validation.R."""
    def ratio(values):
        stim = pd.DataFrame({"condition": "continuous", "frequency": values,
                             "length": [4] * len(values)})
        cmp = match_report_continuous(stim, "frequency", ["length"], schema)["comparisons"]
        return cmp.loc[0, "sd_ratio"]

    for n in (2, 3, 8, 80):
        assert ratio([3.0 + 0.5 * i for i in range(n)]) == 1.0, n
    # Bunched in the middle of the range: SD 0.713 against 0.791.
    assert ratio([1.0, 2.0, 2.1, 2.2, 3.0]) == 0.902
    # Gathered at the two ends: SD 1.643 against 1.122.
    assert ratio([1.0, 1.0, 1.0, 4.0, 4.0, 4.0]) == 1.464


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
