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


def tost_equiv(x, y, bound_d: float = 0.5, alpha: float = 0.05) -> dict:
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    x = x[~np.isnan(x)]; y = y[~np.isnan(y)]
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return dict(p=float("nan"), equivalent=None)
    sp = math.sqrt(((nx - 1) * x.var(ddof=1) + (ny - 1) * y.var(ddof=1)) / (nx + ny - 2))
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
            p = tt["p"]
            rows.append(dict(
                condition=cc, reference=anchor, dimension=dim,
                cohens_d=round(cohens_d(x, y), 3),
                tost_p=round(p, 4) if p == p else None,
                equivalent=tt["equivalent"],
            ))
    return dict(descriptives=desc, comparisons=pd.DataFrame(rows))
