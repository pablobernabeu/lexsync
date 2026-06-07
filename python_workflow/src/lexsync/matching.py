# -*- coding: utf-8 -*-
"""The multidimensional constraint-matching engine.

Mirrors R_workflow/R/matching.R exactly: a per-dimension tolerance pre-filter
followed by standardised nearest-neighbour assignment with a stable tie-break.
The same standardisation (sample SD), the same even-spread anchor selection and
the same tie-break order are used as in R, so the two engines return matching
selections from identical input.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .querying import build_pool


def _zmat(df: pd.DataFrame, match_on, center, scale) -> np.ndarray:
    m = df[match_on].to_numpy(dtype=float)
    return (m - center) / scale


def match_stimuli(pool: pd.DataFrame, design: dict, schema: dict, verbose: bool = False) -> pd.DataFrame:
    conditions = design["conditions"]
    match_on = list(design["match_on"])
    n = design.get("n_per_condition") or design.get("n_per_cell") or 20
    tol_k = schema["matching"]["tolerance_k"]

    for d in match_on:
        if d not in pool.columns:
            raise ValueError(f"lexsync: dimension '{d}' is absent from the pool.")

    center = np.array([pool[d].mean() for d in match_on], dtype=float)
    scale = np.array([pool[d].std(ddof=1) for d in match_on], dtype=float)
    scale[np.isnan(scale) | (scale == 0)] = 1.0

    subpools = [build_pool(pool, c["define_by"]) for c in conditions]
    cond_names = [c["name"] for c in conditions]

    anchor_pool = subpools[0]
    if len(anchor_pool) == 0:
        raise ValueError(f"lexsync: anchor condition '{cond_names[0]}' has no candidates.")
    ord_dim = list(conditions[0]["define_by"].keys())[0]
    if ord_dim not in anchor_pool.columns:
        ord_dim = "frequency"
    anchor_pool = (anchor_pool.assign(_k=anchor_pool["word"].map(lambda w: w.encode("utf-8")))
                   .sort_values([ord_dim, "_k"], kind="mergesort").drop(columns="_k").reset_index(drop=True))
    n_take = min(n, len(anchor_pool))
    idx1 = np.unique(np.round(np.linspace(1, len(anchor_pool), n_take)).astype(int))
    anchor = anchor_pool.iloc[idx1 - 1].copy()
    anchor["condition"] = cond_names[0]
    n_take = len(anchor)
    z_anchor = _zmat(anchor, match_on, center, scale)

    win = {}
    for d in match_on:
        m = anchor[d].mean()
        s = anchor[d].std(ddof=1)
        k = tol_k.get(d, 2)
        win[d] = (m - k * s, m + k * s)

    selected = [anchor]
    used_words = set(anchor["word"])

    for ci in range(1, len(conditions)):
        cname = cond_names[ci]
        cand = subpools[ci]
        cand = cand[~cand["word"].isin(used_words)]
        if len(cand) == 0:
            raise ValueError(f"lexsync: condition '{cname}' has no candidates left to match.")
        keep = np.ones(len(cand), dtype=bool)
        for d in match_on:
            col = cand[d].to_numpy()
            keep &= (col >= win[d][0]) & (col <= win[d][1])
        cand_f = cand[keep]
        if len(cand_f) < n_take:
            if verbose:
                print(f"lexsync: condition '{cname}' has {len(cand_f)} candidates within tolerance "
                      f"(< {n_take} needed); relaxing the window.")
            cand_f = cand
        cand_f = cand_f.reset_index(drop=True)
        z_cand = _zmat(cand_f, match_on, center, scale)
        words = cand_f["word"].to_numpy()
        ids = cand_f["id"].to_numpy()
        used = np.zeros(len(cand_f), dtype=bool)
        pick = np.empty(n_take, dtype=int)
        for a in range(n_take):
            # Round to absorb last-ULP floating-point differences between engines,
            # so the stable tie-break below is itself reproducible across R and Python.
            dvec = np.round(np.sqrt(((z_cand - z_anchor[a]) ** 2).sum(axis=1)), 9)
            dvec = np.where(used, np.inf, dvec)
            best = min(range(len(cand_f)), key=lambda j: (dvec[j], words[j].encode("utf-8"), int(ids[j])))
            pick[a] = best
            used[best] = True
        sel = cand_f.iloc[pick].copy()
        sel["condition"] = cname
        used_words |= set(sel["word"])
        selected.append(sel)

    common = [c for c in selected[0].columns if all(c in s.columns for s in selected)]
    out = pd.concat([s[common] for s in selected], ignore_index=True)
    out["set"] = list(range(1, n_take + 1)) * len(conditions)
    return out
