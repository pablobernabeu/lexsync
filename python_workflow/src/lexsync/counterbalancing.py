# -*- coding: utf-8 -*-
"""Assign matched stimuli to lists and trial order, and build participant tables.

Mirrors R_workflow/R/counterbalancing.R. Two recipes are provided: the original
``factorial`` one (every matched item is shown, lists split the matched sets) and
``latin_square_target`` for paired/sentence paradigms (each item appears once per
list in one rotated condition, so a target is never repeated within a list). Trial
order within a list comes from a seeded, keyed-hash shuffle, so the R and Python
engines produce the same order byte for byte.
"""
from __future__ import annotations

import hashlib
from itertools import product

import numpy as np
import pandas as pd

from .paradigms import get_paradigm


def _recipe(design: dict) -> str:
    if design.get("events"):
        return "factorial"
    name = design.get("paradigm", "factorial")
    try:
        return get_paradigm(name).get("counterbalance", "factorial")
    except ValueError:
        return "factorial"


def _shuffle_deterministic(df: pd.DataFrame, seed) -> pd.DataFrame:
    """Order the trials of one list by a keyed hash, not a random number generator.

    Each row is ranked by the SHA-256 digest of "seed|replicate|list|set|condition",
    a tuple that identifies the trial uniquely under either recipe. Distinct inputs
    to SHA-256 behave as independent uniform draws, so ordering by the digest
    realises a seeded random permutation, but as a pure function of the design: the
    same bytes from the R and Python engines on any platform, and a different order
    for every seed. R's sample() and numpy's PCG64 could never agree on a
    permutation, which used to be the one engine-specific artefact in an otherwise
    byte-identical pipeline. The replicate term keeps independently counterbalanced
    item sets from sharing one permutation pattern.
    """
    rep = df["replicate"] if "replicate" in df.columns else [0] * len(df)
    ranks = [hashlib.sha256(f"{seed}|{r}|{l}|{s}|{c}".encode("utf-8")).hexdigest()
             for r, l, s, c in zip(rep, df["list"], df["set"], df["condition"])]
    df = df.iloc[np.argsort(ranks, kind="stable")].copy()
    df["trial"] = np.arange(1, len(df) + 1)
    return df


def counterbalance(stimuli: pd.DataFrame, design: dict, schema: dict) -> pd.DataFrame:
    # Resampled designs counterbalance each replicate (an independent item set)
    # on its own, so trial order is numbered within each replicate.
    if "replicate" in stimuli.columns and stimuli["replicate"].nunique() > 1:
        parts = [_counterbalance_one(g.reset_index(drop=True), design, schema)
                 for _, g in stimuli.groupby("replicate", sort=True)]
        return pd.concat(parts, ignore_index=True)
    return _counterbalance_one(stimuli, design, schema)


def _counterbalance_one(stimuli: pd.DataFrame, design: dict, schema: dict) -> pd.DataFrame:
    if _recipe(design) == "latin_square_target":
        return counterbalance_latin_square(stimuli, design, schema)
    return counterbalance_factorial(stimuli, design, schema)


def counterbalance_factorial(stimuli: pd.DataFrame, design: dict, schema: dict) -> pd.DataFrame:
    n_lists = (design.get("counterbalance") or {}).get("lists", 1)
    seed = schema.get("seed", 1)
    stimuli = stimuli.copy()
    stimuli["list"] = 1
    if n_lists > 1:
        sets = sorted(stimuli["set"].unique())
        mapping = {s: (i % n_lists) + 1 for i, s in enumerate(sets)}
        stimuli["list"] = stimuli["set"].map(mapping)
    parts = [_shuffle_deterministic(df, seed)
             for _, df in stimuli.groupby("list", sort=True)]
    return pd.concat(parts, ignore_index=True)


def counterbalance_latin_square(stimuli: pd.DataFrame, design: dict, schema: dict) -> pd.DataFrame:
    """One row per item per list, condition rotated across lists (Latin square).

    Each item (``set``) contributes exactly one trial to a list, so its target is
    never repeated within a list; conditions are balanced because items rotate
    through them. With ``lists`` unset the number of lists equals the number of
    conditions, the canonical fully-counterbalanced design.
    """
    seed = schema.get("seed", 1)
    conds = sorted(stimuli["condition"].unique(), key=lambda s: str(s).encode("utf-8"))
    n_cond = len(conds)
    n_lists = (design.get("counterbalance") or {}).get("lists", n_cond)
    sets = sorted(stimuli["set"].unique())
    parts = []
    for li in range(n_lists):
        rows = []
        for si, s in enumerate(sets):
            cond = conds[(si + li) % n_cond]
            row = stimuli[(stimuli["set"] == s) & (stimuli["condition"] == cond)]
            if len(row) == 0:
                raise ValueError(f"lexsync: item set {s} has no row for condition '{cond}'.")
            rows.append(row.iloc[0])
        df = pd.DataFrame(rows).reset_index(drop=True)
        df["list"] = li + 1
        df = _shuffle_deterministic(df, seed).reset_index(drop=True)
        parts.append(df)
    return pd.concat(parts, ignore_index=True)


def participant_table(factors: dict, n_participants: int) -> pd.DataFrame:
    keys = list(factors.keys())
    # R's expand.grid() varies the first factor fastest, itertools.product the
    # last; cross the reversed keys and unreverse each cell so a participant
    # number is allocated the same cell by either engine.
    grid = [cell[::-1] for cell in product(*[factors[k] for k in reversed(keys)])]
    rows = [dict(zip(keys, grid[i % len(grid)])) for i in range(n_participants)]
    df = pd.DataFrame(rows)
    df["participant"] = np.arange(1, n_participants + 1)
    return df
