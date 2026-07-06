# -*- coding: utf-8 -*-
"""Match-quality reporting: descriptives, standardised mean differences, TOST.

Mirrors R_workflow/R/validation.R.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats


def describe_stimuli(stimuli: pd.DataFrame, dims, by: str = "condition") -> pd.DataFrame:
    rows = []
    for g, d in stimuli.groupby(by, sort=False):
        for dim in dims:
            x = pd.to_numeric(d[dim], errors="coerce").dropna()
            rows.append(dict(
                group=g, dimension=dim, n=int(x.size),
                mean=round(float(x.mean()), 3), sd=round(float(x.std(ddof=1)), 3),
                min=round(float(x.min()), 3), median=round(float(x.median()), 3),
                max=round(float(x.max()), 3),
            ))
    return pd.DataFrame(rows)


def cohens_d(x, y) -> float:
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    x = x[~np.isnan(x)]; y = y[~np.isnan(y)]
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return 0.0
    sp = math.sqrt(((nx - 1) * x.var(ddof=1) + (ny - 1) * y.var(ddof=1)) / (nx + ny - 2))
    if sp == 0 or math.isnan(sp):
        return 0.0
    return float((x.mean() - y.mean()) / sp)


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
    sp = math.sqrt(((nx - 1) * x.var(ddof=1) + (ny - 1) * y.var(ddof=1)) / (nx + ny - 2))
    diff = float(x.mean() - y.mean())
    if sp == 0 or math.isnan(sp):
        # A constant dimension carries no sampling uncertainty: the interval is a
        # point at the (zero) standardised difference.
        return dict(d=0.0, ci_low=0.0, ci_high=0.0)
    d = diff / sp
    margin = float(stats.t.ppf(1 - alpha, nx + ny - 2) * math.sqrt(1 / nx + 1 / ny))
    return dict(d=float(d), ci_low=d - margin, ci_high=d + margin)


def tost_equiv(x, y, bound_d: float = 0.5, alpha: float = 0.05) -> dict:
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    x = x[~np.isnan(x)]; y = y[~np.isnan(y)]
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return dict(p=float("nan"), equivalent=None)
    sp = math.sqrt(((nx - 1) * x.var(ddof=1) + (ny - 1) * y.var(ddof=1)) / (nx + ny - 2))
    if sp == 0 or math.isnan(sp):
        # Both conditions are constants (e.g. a dimension fixed by the pool, such
        # as two-character Chinese words). They are equivalent iff they share that
        # constant; the standardised difference is then exactly zero.
        if float(x.mean() - y.mean()) == 0:
            return dict(p=0.0, equivalent=True)
        return dict(p=1.0, equivalent=False)
    se = sp * math.sqrt(1 / nx + 1 / ny)
    if se == 0 or math.isnan(se):
        return dict(p=float("nan"), equivalent=None)
    bound = bound_d * sp
    dfree = nx + ny - 2
    diff = x.mean() - y.mean()
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
    v_ref = ref.var(ddof=1)
    if v_ref == 0:
        return 1.0 if cond.var(ddof=1) == 0 else None
    return float(cond.var(ddof=1) / v_ref)


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


def match_report(stimuli: pd.DataFrame, dims, schema: dict) -> dict:
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
            rows.append(dict(
                condition=cc, reference=anchor, dimension=dim,
                cohens_d=round(cohens_d(x, y), 3),
                d_ci_low=round(ci["ci_low"], 3) if ci["ci_low"] == ci["ci_low"] else None,
                d_ci_high=round(ci["ci_high"], 3) if ci["ci_high"] == ci["ci_high"] else None,
                var_ratio=round(vr, 3) if vr is not None else None,
                tost_p=round(p, 4) if p == p else None,
                equivalent=tt["equivalent"],
            ))
    return dict(descriptives=desc, comparisons=pd.DataFrame(rows))


def _pearson(x, y):
    """Pearson correlation from raw sums, rounded to 9 dp so it is byte-comparable
    across the R and Python engines (not scipy/numpy's wrapper)."""
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    m = ~(np.isnan(x) | np.isnan(y))
    x = x[m]; y = y[m]
    if len(x) < 2:
        return None
    dx = x - x.mean(); dy = y - y.mean()
    denom = math.sqrt(float((dx * dx).sum()) * float((dy * dy).sum()))
    if denom == 0:
        return 0.0
    return round(float((dx * dy).sum() / denom), 9)


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
    span = round(float(valid.max() - valid.min()), 3) if len(valid) >= 2 else None
    rows = [dict(dimension=predictor, role="predictor", pearson_r=None, predictor_span=span)]
    for c in controls:
        cv = pd.to_numeric(stimuli[c], errors="coerce").to_numpy(dtype=float)
        r = _pearson(pv, cv)
        rows.append(dict(dimension=c, role="control",
                         pearson_r=round(r, 3) if r is not None else None,
                         predictor_span=span))
    return dict(descriptives=desc, comparisons=pd.DataFrame(rows))
