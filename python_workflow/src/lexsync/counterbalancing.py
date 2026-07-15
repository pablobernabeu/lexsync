# -*- coding: utf-8 -*-
"""Assign matched stimuli to lists and trial order, and build participant tables.

Mirrors R_workflow/R/counterbalancing.R. Two recipes are provided: the original
``factorial`` one (every matched item is shown, lists split the matched sets) and
``latin_square_target`` for paired/sentence paradigms (each item appears once per
list in one rotated condition, so a target is never repeated within a list). Trial
order within a list is shuffled with a seeded generator; the seed makes it
reproducible within an engine (the R and Python RNGs differ, so order — but not
the matched selection or the condition assignment — may differ between them).
"""
from __future__ import annotations

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
    rng = np.random.default_rng(seed)
    parts = []
    for _, df in stimuli.groupby("list", sort=True):
        df = df.iloc[rng.permutation(len(df))].copy()
        df["trial"] = np.arange(1, len(df) + 1)
        parts.append(df)
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
    rng = np.random.default_rng(seed)
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
        df = df.iloc[rng.permutation(len(df))].reset_index(drop=True)
        df["trial"] = np.arange(1, len(df) + 1)
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
