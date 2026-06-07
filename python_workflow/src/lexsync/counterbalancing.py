# -*- coding: utf-8 -*-
"""Assign matched stimuli to lists and trial order, and build participant tables.

Mirrors R_workflow/R/counterbalancing.R. Trial order is shuffled with a seeded
generator; the seed makes it reproducible within an engine (the R and Python
RNGs differ, so order, but not the matched selection, may differ between them).
"""
from __future__ import annotations

from itertools import product

import numpy as np
import pandas as pd


def counterbalance(stimuli: pd.DataFrame, design: dict, schema: dict) -> pd.DataFrame:
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


def participant_table(factors: dict, n_participants: int) -> pd.DataFrame:
    keys = list(factors.keys())
    grid = list(product(*[factors[k] for k in keys]))
    rows = [dict(zip(keys, grid[i % len(grid)])) for i in range(n_participants)]
    df = pd.DataFrame(rows)
    df["participant"] = np.arange(1, n_participants + 1)
    return df
