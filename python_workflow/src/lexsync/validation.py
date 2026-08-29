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
    return pd.DataFrame(rows)


def cohens_d(x, y):
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    x = x[~np.isnan(x)]; y = y[~np.isnan(y)]
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return 0.0
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
    standardised mean difference; for ``alpha = 0.05`` this is the 90% interval
    that corresponds exactly to a two one-sided tests (TOST) decision at the .05
    level (Lakens, 2017). Reporting the interval, rather than only a binary
    "equivalent / not" verdict, makes the realised imbalance and its sampling
    uncertainty explicit and keeps the dependence on the number of items visible
    rather than hidden: with few items the interval is wide, so a small point
    estimate cannot be over-read as evidence of a small true difference
    (Sassenhagen & Alday, 2016). The upper limit of the interval on ``|d|`` is the
    largest imbalance still consistent with the stimuli.
    """
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    x = x[~np.isnan(x)]; y = y[~np.isnan(y)]
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return dict(d=0.0, ci_low=float("nan"), ci_high=float("nan"))
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
    margin = float(stats.t.ppf(1 - alpha, nx + ny - 2) * math.sqrt(1 / nx + 1 / ny))
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
# cause. Must list the same columns, in the same order, as .empty_comparisons in
# R_workflow/R/validation.R.
_COMPARISON_COLUMNS = ("condition", "reference", "dimension", "cohens_d", "d_ci_low",
                       "d_ci_high", "var_ratio", "tost_p", "equivalent")


def match_report(stimuli: pd.DataFrame, dims, schema: dict) -> dict:
    """Build the full match-quality report: descriptives and comparisons.

    Every comparison is against the first condition in order of appearance, so a
    design with a single condition has nothing to compare and ``comparisons`` comes
    back with its columns and no rows.
    """
    conds = list(dict.fromkeys(stimuli["condition"]))
    anchor = conds[0]
    desc = describe_stimuli(stimuli, dims)
    bound = (schema.get("equivalence") or {}).get("bound_d", 0.5)
    alpha = (schema.get("equivalence") or {}).get("alpha", 0.05)
    rows = []
    for cc in conds[1:]:
        for dim in dims:
            x = pd.to_numeric(stimuli.loc[stimuli["condition"] == anchor, dim], errors="coerce")
            y = pd.to_numeric(stimuli.loc[stimuli["condition"] == cc, dim], errors="coerce")
            tt = tost_equiv(x, y, bound, alpha)
            ci = cohens_d_ci(x, y, alpha)
            vr = variance_ratio(y, x)
            p = tt["p"]
            # An undefined d and its interval serialise as missing cells (empty in
            # the CSV, null in the datasheet), exactly like the other missing stats.
            d = cohens_d(x, y)
            lo, hi = ci["ci_low"], ci["ci_high"]
            rows.append(dict(
                condition=cc, reference=anchor, dimension=dim,
                cohens_d=_round_dp(d, 3) if d is not None else None,
                d_ci_low=_round_dp(lo, 3) if lo is not None and lo == lo else None,
                d_ci_high=_round_dp(hi, 3) if hi is not None and hi == hi else None,
                var_ratio=_round_dp(vr, 3) if vr is not None else None,
                tost_p=_round_dp(p, 4) if p == p else None,
                equivalent=tt["equivalent"],
            ))
    return dict(descriptives=desc,
                comparisons=pd.DataFrame(rows) if rows
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


def match_report_continuous(stimuli, predictor, controls, schema) -> dict:
    """Realised-control report for a continuous design.

    Returns the same ``{descriptives, comparisons}`` shape as :func:`match_report`,
    so the pipeline and datasheet stay uniform, but the comparisons describe a
    continuous predictor instead of a between-condition contrast: the predictor's
    realised span and, for each control, its Pearson correlation with the predictor
    (near zero when the control is held constant). The set is meant for regression /
    mixed-model analysis, not equivalence tests.
    """
    desc = describe_stimuli(stimuli, [predictor] + controls)
    pv = pd.to_numeric(stimuli[predictor], errors="coerce").to_numpy(dtype=float)
    valid = pv[~np.isnan(pv)]
    # None (not NaN) when the predictor has no span, so both engines agree.
    span = _round_dp(float(valid.max() - valid.min()), 3) if len(valid) >= 2 else None
    rows = [dict(dimension=predictor, role="predictor", pearson_r=None, predictor_span=span)]
    for c in controls:
        cv = pd.to_numeric(stimuli[c], errors="coerce").to_numpy(dtype=float)
        r = _pearson(pv, cv)
        rows.append(dict(dimension=c, role="control",
                         pearson_r=_round_dp(r, 3) if r is not None else None,
                         predictor_span=span))
    return dict(descriptives=desc, comparisons=pd.DataFrame(rows))
