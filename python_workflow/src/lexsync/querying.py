# -*- coding: utf-8 -*-
"""Load lexica, validate the column contract and compute lexical dimensions.

Mirrors R_workflow/R/querying.R.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from rapidfuzz.distance import Hamming, Levenshtein

from .io_utils import read_csv_utf8


def validate_lexicon(df: pd.DataFrame, schema: dict) -> None:
    required = schema["lexicon_schema"]["required"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        cols = ", ".join(f"'{m}'" for m in missing)
        raise ValueError(f"lexsync: lexicon is missing required column(s): {cols}")


def load_lexicon(path: str, schema: dict, language: str | None = None) -> pd.DataFrame:
    df = read_csv_utf8(path)
    validate_lexicon(df, schema)
    freq_col = (schema.get("dimensions", {}).get("frequency", {}) or {}).get("column") or "freq_zipf"
    df = df.copy()
    df["word"] = df["word"].astype(str).str.strip().str.lower()
    df = df[df["word"].notna() & (df["word"] != "") & df[freq_col].notna()]
    df = df.drop_duplicates(subset="word")
    # Sort by UTF-8 byte order so the lexicon order is locale-independent and
    # identical to the R engine (which uses a 'radix' byte-order sort).
    df = (df.assign(_k=df["word"].map(lambda w: w.encode("utf-8")))
            .sort_values("_k").drop(columns="_k").reset_index(drop=True))
    df["id"] = np.arange(1, len(df) + 1)
    df["length"] = df["word"].str.len()
    df["frequency"] = df[freq_col].astype(float)
    if language is not None:
        df["language"] = language
    return df.reset_index(drop=True)


def add_neighbourhood(df: pd.DataFrame, reference=None, n_old: int = 20) -> pd.DataFrame:
    """Coltheart's N (same-length, single substitution) and OLD20 for each word."""
    words = df["word"].astype(str).tolist()
    ref = list(dict.fromkeys(str(w) for w in (reference if reference is not None else words)))
    ref_len = np.array([len(w) for w in ref])
    n_density = np.zeros(len(words), dtype=int)
    old = np.full(len(words), np.nan)
    for i, w in enumerate(words):
        same_len = [r for r, L in zip(ref, ref_len) if L == len(w)]
        if same_len:
            hd = np.array([Hamming.distance(w, s) for s in same_len])
            n_density[i] = int(np.sum(hd == 1))
        ld = np.array([Levenshtein.distance(w, r) for r in ref], dtype=float)
        ld = ld[ld > 0]
        if ld.size:
            k = min(n_old, ld.size)
            old[i] = float(np.mean(np.partition(ld, k - 1)[:k]))
    out = df.copy()
    out["n_density"] = n_density
    out["old20"] = old
    return out


def build_pool(lexicon: pd.DataFrame, filters: dict | None = None) -> pd.DataFrame:
    df = lexicon
    if filters:
        for col, rng in filters.items():
            if col not in df.columns:
                continue
            vals = list(rng) if isinstance(rng, (list, tuple)) else [rng]
            if len(vals) == 2 and all(isinstance(v, (int, float)) for v in vals):
                df = df[df[col].notna() & (df[col] >= vals[0]) & (df[col] <= vals[1])]
            else:
                df = df[df[col].notna() & df[col].astype(str).isin([str(v) for v in vals])]
    return df.reset_index(drop=True)
