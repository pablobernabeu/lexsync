"""Match-quality reporting: descriptives, standardised mean differences, TOST.

The one place a non-elementary function reaches a compared artefact. Everything
else on the path to a stimuli, descriptives or comparisons file is built from
operations IEEE-754 either mandates correctly rounded or makes exact, so the two
engines agree by construction. The Student t quantile and distribution behind the
confidence interval and the TOST p-value are not among those: scipy.stats.t here,
stats::qt and stats::pt in R, two independent implementations. Measured on SciPy
1.17.1 against R 4.6.1, they disagree by at most about 1e-12 over the range these
reports use, while the published values are rounded to three and four decimal
places, which leaves 5e-4 and 5e-5 of headroom before a byte could move. The
comparisons artefacts are therefore byte-identical on the evidence of a margin of
some seven orders of magnitude, not on the by-construction argument that carries
the rest.

Mirrors R_workflow/R/validation.R.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats

# Every reduction in this module goes through these rather than through numpy or
# pandas. Two designs' reported means used to differ between the engines in the last
# published decimal because numpy sums pairwise and R's mean() does not; see io_utils.
from .io_utils import _exact_mean, _exact_median, _exact_sd, _exact_sum, _exact_var, _round_dp


def describe_stimuli(stimuli: pd.DataFrame, dims, by: str = "condition") -> pd.DataFrame:
    rows = []
    for g, d in stimuli.groupby(by, sort=False):
        for dim in dims:
            x = pd.to_numeric(d[dim], errors="coerce").dropna()
            rows.append(dict(
                group=g, dimension=dim, n=int(x.size),
                mean=_round_dp(_exact_mean(x), 3), sd=_round_dp(_exact_sd(x), 3),
                min=_round_dp(float(x.min()), 3),
                # _exact_median, not pandas' .median(): the latter reduces through
                # numpy, the one reduction here that would bypass the shared exact
                # primitives.
                median=_round_dp(_exact_median(x), 3),
                max=_round_dp(float(x.max()), 3),
            ))
    # The columns even without rows, as when match_report leaves out every dimension
    # it was given, so the frame has the header the R twin's has.
    return pd.DataFrame(rows, columns=["group", "dimension", "n", "mean", "sd", "min",
                                       "median", "max"])


def cohens_d(x, y):
    """Cohen's *d*, the pooled-SD standardised mean difference of ``x`` and ``y``.

    ``None`` when either sample has fewer than two values, since one value has no
    spread and the pooled SD is then undefined, and when the pooled SD is zero but
    the means differ. Two samples of one shared constant give 0. Mirrors cohens_d in
    R_workflow/R/validation.R.
    """
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    x = x[~np.isnan(x)]; y = y[~np.isnan(y)]
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        # Undefined, not 0: a frequency contrast of 6.5 against 3.9 Zipf with one item
        # a side was reported as a perfect balance.
        return None
    sp = math.sqrt(((nx - 1) * _exact_var(x) + (ny - 1) * _exact_var(y)) / (nx + ny - 2))
    if sp == 0 or math.isnan(sp):
        # Two constants: an exactly-zero difference is exactly zero SDs apart, but
        # unequal constants are infinitely many. That is undefined, not perfect balance.
        if float(_exact_mean(x) - _exact_mean(y)) == 0:
            return 0.0
        return None
    return float((_exact_mean(x) - _exact_mean(y)) / sp)


def cohens_d_ci(x, y, alpha: float = 0.05) -> dict:
    """Cohen's *d* with a confidence interval, complementing the TOST verdict.

    The interval is the ``(1 - 2 * alpha)`` confidence interval for the
    standardised mean difference, so ``alpha = 0.05`` gives the 90% interval that
    goes with a two one-sided tests (TOST) decision at the .05 level (Lakens,
    2017). Reporting the interval, rather than only a binary "equivalent / not"
    verdict, makes the realised imbalance and its sampling uncertainty explicit and
    keeps the dependence on the number of items visible: with few items the
    interval is wide, whatever the point estimate. The upper limit of the interval
    on ``|d|`` is the largest imbalance still consistent with the stimuli. Both the
    interval and the TOST treat the selected items as a sample, although a test on
    stimuli concerns a closed population. Sassenhagen and Alday (2016) recommend
    describing the stimuli and entering potential confounds in the analysis as
    covariates.

    The limits are ``d +/- t * SE(d)``, where ``t`` is the Student *t* quantile on
    ``nx + ny - 2`` degrees of freedom and ``SE(d)`` is the large-sample standard
    error of *d*, ``sqrt(1/nx + 1/ny + d**2 / (2 * (nx + ny)))`` (Hedges & Olkin,
    1985; Borenstein et al., 2009, eq. 4.20). The ``d**2`` term carries the
    sampling error of the pooled standard deviation. It is negligible for a
    well-matched control, where *d* is near zero, but it dominates for a
    manipulated dimension and can more than double the width of that
    interval. TOST tests the raw mean difference, so the interval is slightly
    wider than the one its decision implies, and when a control's limit lies
    close to the bound, ``tost_p`` gives the verdict.

    The estimate and both limits are ``None`` when either sample has fewer than two
    values, as :func:`cohens_d` is.
    """
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    x = x[~np.isnan(x)]; y = y[~np.isnan(y)]
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return dict(d=None, ci_low=None, ci_high=None)
    sp = math.sqrt(((nx - 1) * _exact_var(x) + (ny - 1) * _exact_var(y)) / (nx + ny - 2))
    diff = float(_exact_mean(x) - _exact_mean(y))
    if sp == 0 or math.isnan(sp):
        # Equal constants carry no sampling uncertainty: a point at zero. Unequal
        # constants are infinitely many SDs apart, so the estimate and its interval
        # are undefined, not a perfect [0, 0].
        if diff == 0:
            return dict(d=0.0, ci_low=0.0, ci_high=0.0)
        return dict(d=None, ci_low=None, ci_high=None)
    d = diff / sp
    # Large-sample variance of d: 1/nx + 1/ny + d**2 / (2 * (nx + ny)) (Hedges &
    # Olkin, 1985; Borenstein et al., 2009, eq. 4.20). Without the d**2 term the
    # interval treated the pooled SD as known, which gave a manipulated dimension
    # with d = 5.6 and 40 items a side a margin of 0.37 in place of 0.83. Written
    # with d * d, not d ** 2, and summed in the same order as validation.R, so both
    # engines round every step identically.
    se = math.sqrt(1 / nx + 1 / ny + d * d / (2 * (nx + ny)))
    margin = float(stats.t.ppf(1 - alpha, nx + ny - 2) * se)
    return dict(d=float(d), ci_low=d - margin, ci_high=d + margin)


def tost_equiv(x, y, bound_d: float = 0.5, alpha: float = 0.05) -> dict:
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    x = x[~np.isnan(x)]; y = y[~np.isnan(y)]
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return dict(p=float("nan"), equivalent=None)
    sp = math.sqrt(((nx - 1) * _exact_var(x) + (ny - 1) * _exact_var(y)) / (nx + ny - 2))
    if sp == 0 or math.isnan(sp):
        # Both conditions are constants (e.g. a dimension fixed by the pool, such
        # as two-character Chinese words). They are equivalent iff they share that
        # constant; the standardised difference is then exactly zero.
        if float(_exact_mean(x) - _exact_mean(y)) == 0:
            return dict(p=0.0, equivalent=True)
        return dict(p=1.0, equivalent=False)
    se = sp * math.sqrt(1 / nx + 1 / ny)
    if se == 0 or math.isnan(se):
        return dict(p=float("nan"), equivalent=None)
    bound = bound_d * sp
    dfree = nx + ny - 2
    diff = _exact_mean(x) - _exact_mean(y)
    p = max(stats.t.sf((diff + bound) / se, dfree), stats.t.cdf((diff - bound) / se, dfree))
    return dict(p=float(p), equivalent=bool(p < alpha))


def variance_ratio(cond, ref):
    """Ratio of a condition's variance to the reference's: a distributional
    balance check that complements the mean-based Cohen's d and TOST.

    Two conditions can share a mean yet differ in spread and still confound, which
    a mean-based statistic misses (Armstrong, Watson & Plaut, 2012; Austin, 2009).
    A ratio near 1 is balanced; a common heuristic flags ratios outside about
    [0.5, 2] as unequal spread. Returns ``None`` when a variance is undefined.
    """
    cond = np.asarray(cond, dtype=float); ref = np.asarray(ref, dtype=float)
    cond = cond[~np.isnan(cond)]; ref = ref[~np.isnan(ref)]
    if len(cond) < 2 or len(ref) < 2:
        return None
    v_ref = _exact_var(ref)
    if v_ref == 0:
        return 1.0 if _exact_var(cond) == 0 else None
    return float(_exact_var(cond) / v_ref)


def balance_check(stimuli: pd.DataFrame, columns) -> list:
    if isinstance(columns, str):
        columns = [columns]
    issues = []
    for col in columns:
        if col not in stimuli.columns:
            continue
        tab = stimuli[col].value_counts()
        if tab.nunique() > 1:
            detail = ", ".join(f"{k}={v}" for k, v in tab.items())
            issues.append(f"Column '{col}' is unbalanced: {detail}")
    return issues


# The columns of the comparisons frame, needed explicitly for the single-condition
# case where there is nothing to compare against the anchor. A DataFrame built from
# no rows carries no columns either, and wrote a comparisons CSV with no header at
# all, while the R engine's rbind() over an empty list returned NULL and killed the
# pipeline's reporting loop with a message that named neither the design nor the
# cause. `mean_diff` and `role` follow the columns a 0.1 reader already knows. Must
# list the same columns, in the same order, as .empty_comparisons in
# R_workflow/R/validation.R.
_COMPARISON_COLUMNS = ("condition", "reference", "dimension", "cohens_d", "d_ci_low",
                       "d_ci_high", "var_ratio", "tost_p", "equivalent", "mean_diff",
                       "role")


def _numeric(values) -> pd.Series:
    """A dimension's values as numbers, with a missing value or a non-number as NaN."""
    return pd.to_numeric(values, errors="coerce")


def _reportable(stimuli: pd.DataFrame, dims) -> list:
    """The dimensions a report can compare, in the order given.

    A dimension with no numeric value among the stimuli is left out: one every item
    lacks, as ``n_syllables`` is for a Chinese word, or one that is not numeric, as a
    part-of-speech label named in a condition's ``define_by`` is. A name that is not a
    column of the stimuli is refused. Mirrors .reportable in R_workflow/R/validation.R.
    """
    for d in dims:
        if d not in stimuli.columns:
            raise ValueError(f"lexsync: dimension '{d}' is not a column of the stimuli.")
    return [d for d in dims if _numeric(stimuli[d]).notna().any()]


def _condition_pairs(conds) -> list:
    """The (reference, condition) pairs a report compares, in order.

    The anchor rows come first, every other condition against the first, as a 0.1
    report gave them. Every further pair (i, j) with 1 <= i < j follows in condition
    order, with condition i as the reference. Mirrors .condition_pairs in
    R_workflow/R/validation.R.
    """
    pairs = [(conds[0], c) for c in conds[1:]]
    pairs += [(conds[i], conds[j]) for i in range(1, len(conds))
              for j in range(i + 1, len(conds))]
    return pairs


def match_report(stimuli: pd.DataFrame, dims, schema: dict, roles=None) -> dict:
    """Build the full match-quality report: descriptives and comparisons.

    Every pair of conditions is compared on every dimension. The rows against the
    first condition in order of appearance, the anchor, come first, then every further
    pair in condition order, so a design with a single condition has nothing to
    compare and ``comparisons`` comes back with its columns and no rows. A dimension
    with no numeric value among the stimuli, such as ``n_syllables`` for Chinese or a
    text label, is left out of both frames.

    Each row of ``comparisons`` names the earlier condition of its pair in
    ``reference`` and the later one in ``condition``. The signed statistics run from
    the reference to the other condition: ``cohens_d``, ``d_ci_low`` and ``d_ci_high``
    are the reference mean minus the ``condition`` mean, in pooled standard
    deviations, so a positive *d* means the reference scores higher. ``mean_diff`` is
    the same difference in the dimension's own unit, to three places. ``var_ratio``
    is the other way up, the ``condition`` variance over the reference variance.

    ``roles`` (optional) is a function of ``(condition, reference, dimension)`` that
    returns the row's ``role``: ``manipulated`` when the design sets the two
    conditions apart on the dimension, ``controlled`` when it matches them on it and
    ``uncontrolled`` otherwise. ``run_pipeline`` derives it from the design. Without
    it, ``role`` is missing.
    """
    conds = list(dict.fromkeys(stimuli["condition"]))
    dims = _reportable(stimuli, dims)
    desc = describe_stimuli(stimuli, dims)
    bound = (schema.get("equivalence") or {}).get("bound_d", 0.5)
    alpha = (schema.get("equivalence") or {}).get("alpha", 0.05)
    rows = []
    for ref, cc in _condition_pairs(conds):
        for dim in dims:
            x = _numeric(stimuli.loc[stimuli["condition"] == ref, dim])
            y = _numeric(stimuli.loc[stimuli["condition"] == cc, dim])
            tt = tost_equiv(x, y, bound, alpha)
            ci = cohens_d_ci(x, y, alpha)
            vr = variance_ratio(y, x)
            p = tt["p"]
            # An undefined d and its interval serialise as missing cells (empty in
            # the CSV, null in the datasheet), exactly like the other missing stats.
            d = cohens_d(x, y)
            lo, hi = ci["ci_low"], ci["ci_high"]
            # The raw difference needs one value a side, where d needs two.
            xv, yv = x.dropna(), y.dropna()
            diff = _exact_mean(xv) - _exact_mean(yv) if len(xv) and len(yv) else None
            rows.append(dict(
                condition=cc, reference=ref, dimension=dim,
                cohens_d=_round_dp(d, 3) if d is not None else None,
                d_ci_low=_round_dp(lo, 3) if lo is not None and lo == lo else None,
                d_ci_high=_round_dp(hi, 3) if hi is not None and hi == hi else None,
                var_ratio=_round_dp(vr, 3) if vr is not None else None,
                tost_p=_round_dp(p, 4) if p == p else None,
                equivalent=tt["equivalent"],
                mean_diff=_round_dp(diff, 3) if diff is not None else None,
                role=roles(cc, ref, dim) if roles is not None else None,
            ))
    return dict(descriptives=desc,
                comparisons=pd.DataFrame(rows, columns=list(_COMPARISON_COLUMNS)) if rows
                else pd.DataFrame(columns=list(_COMPARISON_COLUMNS)))


def _pearson(x, y):
    """Pearson correlation from raw sums, rounded to 9 dp so it is byte-comparable
    across the R and Python engines (not scipy/numpy's wrapper)."""
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    m = ~(np.isnan(x) | np.isnan(y))
    x = x[m]; y = y[m]
    if len(x) < 2:
        return None
    dx = x - _exact_mean(x); dy = y - _exact_mean(y)
    denom = math.sqrt(_exact_sum(dx * dx) * _exact_sum(dy * dy))
    if denom == 0:
        return 0.0
    return _round_dp(_exact_sum(dx * dy) / denom, 9)


def _round3(v):
    """A value rounded to three places by the shared rounder, or None when missing."""
    return None if v is None or v != v else _round_dp(float(v), 3)


def _ratio(a, b):
    """``a / b``, or None when either is missing or ``b`` is zero."""
    if a is None or b is None or a != a or b != b or b == 0:
        return None
    return a / b


def match_report_continuous(stimuli, predictor, controls, schema, audit=None) -> dict:
    """Realised-control report for a continuous design.

    Returns the same ``{descriptives, comparisons}`` shape as :func:`match_report`,
    so the pipeline and datasheet stay uniform, but the comparisons describe a
    continuous predictor instead of a between-condition contrast: the predictor's
    realised span and, for each control, its Pearson correlation with the predictor
    (near zero when the control is held constant). The set is meant for regression /
    mixed-model analysis, not equivalence tests.

    ``sd`` is each dimension's realised SD. For the predictor, ``sd_ratio`` sets it
    against the SD of as many values spaced evenly over the same range,
    ``(max - min) * sqrt(n * (n + 1) / 12) / (n - 1)`` with the n - 1 that ``sd``
    uses, so an even spread has a ratio of 1 whatever its size and a selection that
    follows a skewed pool a ratio below 1. That benchmark tends to
    ``(max - min) / sqrt(12)``, the SD of a uniform distribution over the range, as n
    grows. For a control, ``sd_ratio`` sets the realised SD against the SD of the pool
    the selector drew from, and ``window_low`` and ``window_high`` give the window the
    selector banded it to, before any relaxation. Both come from ``audit``, the
    selector's record, which is read from ``stimuli.attrs["audit"]`` when not given.
    Without one, a control's ratio and window are missing.
    """
    if audit is None:
        audit = stimuli.attrs.get("audit")
    windows = {w["dimension"]: w for w in ((audit or {}).get("control_windows") or [])}
    desc = describe_stimuli(stimuli, [predictor] + controls)
    pv = pd.to_numeric(stimuli[predictor], errors="coerce").to_numpy(dtype=float)
    valid = pv[~np.isnan(pv)]
    # None (not NaN) when the predictor has no span, so both engines agree.
    span = _round_dp(float(valid.max() - valid.min()), 3) if len(valid) >= 2 else None
    # The SD of n values spaced evenly over the realised range. (max - min) / sqrt(12)
    # alone is its limit for large n, and against it an even spread of 4 values read
    # 1.49, as if the items crowded the ends of the range. The operations run in the
    # order of the R twin, so both engines get the same double.
    nv = len(valid)
    even = (float(valid.max() - valid.min()) * math.sqrt(nv * (nv + 1) / 12) / (nv - 1)
            if nv >= 2 else None)
    sd = _exact_sd(valid)
    rows = [dict(dimension=predictor, role="predictor", pearson_r=None, predictor_span=span,
                 sd=_round3(sd), sd_ratio=_round3(_ratio(sd, even)), window_low=None,
                 window_high=None)]
    for c in controls:
        cv = pd.to_numeric(stimuli[c], errors="coerce").to_numpy(dtype=float)
        r = _pearson(pv, cv)
        csd = _exact_sd(cv[~np.isnan(cv)])
        w = windows.get(c) or {}
        rows.append(dict(dimension=c, role="control",
                         pearson_r=_round_dp(r, 3) if r is not None else None,
                         predictor_span=span, sd=_round3(csd),
                         sd_ratio=_round3(_ratio(csd, w.get("pool_sd"))),
                         window_low=_round3(w.get("low")), window_high=_round3(w.get("high"))))
    return dict(descriptives=desc, comparisons=pd.DataFrame(rows))
