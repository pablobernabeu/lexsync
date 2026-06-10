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
            p = tt["p"]
            rows.append(dict(
                condition=cc, reference=anchor, dimension=dim,
                cohens_d=round(cohens_d(x, y), 3),
                d_ci_low=round(ci["ci_low"], 3) if ci["ci_low"] == ci["ci_low"] else None,
                d_ci_high=round(ci["ci_high"], 3) if ci["ci_high"] == ci["ci_high"] else None,
                tost_p=round(p, 4) if p == p else None,
                equivalent=tt["equivalent"],
            ))
    return dict(descriptives=desc, comparisons=pd.DataFrame(rows))
