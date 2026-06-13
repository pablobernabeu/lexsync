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


def _cap_to_overlap(df, z, other_centroid, cap):
    """Keep the `cap` rows nearest the other condition's centroid (byte-rank ties)."""
    if len(df) <= cap:
        return df.reset_index(drop=True), z
    d = np.round(np.sqrt(((z - other_centroid) ** 2).sum(axis=1)), 9)
    order = sorted(range(len(df)), key=lambda i: (d[i], i))[:cap]
    keep = sorted(order)
    return df.iloc[keep].reset_index(drop=True), z[keep]


def _match_joint(subpools, cond_names, match_on, center, scale, n, cap=1200):
    """Select the `n` best-matched pairs jointly across two conditions.

    Rather than fixing one condition and matching the other to it, this scores
    every cross-condition pair on the control dimensions and greedily takes the
    cheapest disjoint pairs. Only items with a good counterpart are kept, so the
    control dimensions are equated even when the manipulation is confounded with
    them (e.g. neighbourhood density with word length). Deterministic and
    identical to the R engine (rounded costs; byte-rank tie-breaks).
    """
    s0 = subpools[0].reset_index(drop=True)
    s1 = subpools[1].reset_index(drop=True)
    if len(s0) == 0 or len(s1) == 0:
        raise ValueError("lexsync: a condition has no candidates for joint matching.")
    z0 = _zmat(s0, match_on, center, scale)
    z1 = _zmat(s1, match_on, center, scale)
    s0, z0 = _cap_to_overlap(s0, z0, z1.mean(axis=0), cap)
    s1, z1 = _cap_to_overlap(s1, z1, z0.mean(axis=0), cap)
    cost = np.round(np.sqrt(((z0[:, None, :] - z1[None, :, :]) ** 2).sum(axis=2)), 9)
    m0, m1 = cost.shape
    rows = np.repeat(np.arange(m0), m1)
    cols = np.tile(np.arange(m1), m0)
    order = np.lexsort((cols, rows, cost.ravel()))   # by cost, then row, then col
    used0 = np.zeros(m0, dtype=bool)
    used1 = np.zeros(m1, dtype=bool)
    pi, pj = [], []
    for idx in order:
        i = int(rows[idx]); j = int(cols[idx])
        if used0[i] or used1[j]:
            continue
        used0[i] = True
        used1[j] = True
        pi.append(i)
        pj.append(j)
        if len(pi) >= n:
            break
    a = s0.iloc[pi].copy(); a["condition"] = cond_names[0]
    b = s1.iloc[pj].copy(); b["condition"] = cond_names[1]
    common = [c for c in a.columns if c in b.columns]
    out = pd.concat([a[common], b[common]], ignore_index=True)
    out["set"] = list(range(1, len(pi) + 1)) * 2
    return out


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

    method = ((design.get("matching") or {}).get("method")
              or (schema.get("matching") or {}).get("method") or "standardised_euclidean")
    if method == "joint" and len(conditions) == 2:
        return _match_joint(subpools, cond_names, match_on, center, scale, n)

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


def resample_stimuli(pool: pd.DataFrame, design: dict, schema: dict,
                     n_sets: int, verbose: bool = False) -> pd.DataFrame:
    """Produce ``n_sets`` disjoint matched item sets (a ``replicate`` column).

    Each replicate is an independent, fully matched set drawn from the pool with
    the items of earlier replicates removed, so no item is reused. This lets a
    study treat its items as a random factor — running different item samples
    across participant groups, or showing an effect holds across samples — rather
    than as a fixed set (Clark, 1973; Yarkoni, 2020). Deterministic: the matcher is
    deterministic and the used-item set evolves identically across engines.
    """
    used: set = set()
    parts = []
    for k in range(1, int(n_sets) + 1):
        pk = pool[~pool["word"].isin(used)].reset_index(drop=True)
        sk = match_stimuli(pk, design, schema, verbose=verbose).copy()
        sk["replicate"] = k
        used |= set(sk["word"])
        parts.append(sk)
    return pd.concat(parts, ignore_index=True)
