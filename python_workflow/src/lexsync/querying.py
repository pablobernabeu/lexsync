# -*- coding: utf-8 -*-
"""Load lexica, validate the column contract and compute lexical dimensions.

Mirrors R_workflow/R/querying.R.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd
from rapidfuzz.distance import Hamming, Levenshtein

from .io_utils import clean_field, read_csv_utf8

# Maximal runs of (possibly accented) Latin vowels approximate syllable nuclei.
_VOWELS = re.compile(r"[aeiouyàáâãäåèéêëìíîïòóôõöøùúûüýÿ]+")


def count_syllables(word) -> int:
    """An orthographic syllable estimate: the number of maximal vowel runs."""
    return len(_VOWELS.findall(str(word).lower()))


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
    # Filter before coercing: astype(str) renders a missing word as the literal
    # string "nan", which survives both guards below, whereas the R engine (where
    # as.character(NA) stays NA) drops the row. Coercing first would therefore
    # desynchronise the two engines' row counts and shift every subsequent id.
    df = df[df["word"].notna() & df[freq_col].notna()].copy()
    df["word"] = df["word"].astype(str).str.strip().str.lower()
    df = df[df["word"] != ""]
    df = df.drop_duplicates(subset="word")
    # Sort by UTF-8 byte order so the lexicon order is locale-independent and
    # identical to the R engine (which uses a 'radix' byte-order sort).
    df = (df.assign(_k=df["word"].map(lambda w: w.encode("utf-8")))
            .sort_values("_k").drop(columns="_k").reset_index(drop=True))
    df["id"] = np.arange(1, len(df) + 1)
    df["length"] = df["word"].str.len()
    df["n_syllables"] = df["word"].map(count_syllables)
    df["frequency"] = df[freq_col].astype(float)
    if language is not None:
        df["language"] = language
    return df.reset_index(drop=True)


def add_bigram_frequency(df: pd.DataFrame, reference=None) -> pd.DataFrame:
    """Mean positional bigram probability, a phonotactic-probability proxy.

    For each word, the mean over its adjacent letter bigrams of the corpus bigram
    probability (count divided by the total bigram count). Computed from integer
    counts and rounded, so it is identical in the R and Python engines.
    """
    ref = [str(w) for w in (reference if reference is not None else df["word"].tolist())]
    counts: dict[str, int] = {}
    total = 0
    for w in ref:
        for i in range(len(w) - 1):
            counts[w[i:i + 2]] = counts.get(w[i:i + 2], 0) + 1
            total += 1
    total = total or 1

    def bf(w):
        w = str(w)
        bgs = [w[i:i + 2] for i in range(len(w) - 1)]
        if not bgs:
            return 0.0
        return round(sum(counts.get(b, 0) for b in bgs) / len(bgs) / total, 9)

    out = df.copy()
    out["bigram_freq"] = out["word"].map(bf)
    return out


def merge_norms(lexicon: pd.DataFrame, norms, on: str = "word", columns=None) -> pd.DataFrame:
    """Left-join a norm table (e.g. concreteness, age of acquisition, valence).

    ``norms`` is a data frame or the path to a CSV with a word column and one or
    more norm columns. This is the connector for semantic dimensions: the norm data
    themselves are fetched separately (licensing varies), then merged here so the
    matcher can equate on them. The join is deterministic and identical across
    engines, and preserves the lexicon's row order.
    """
    n = norms if isinstance(norms, pd.DataFrame) else read_csv_utf8(norms)
    cols = list(columns) if columns else [c for c in n.columns if c != on]
    # Drop missing keys before coercing, for the reason given in load_lexicon: a
    # NaN key would otherwise join on the literal string "nan".
    n = n[[on] + cols]
    n = n[n[on].notna()].copy()
    n[on] = n[on].astype(str).str.strip().str.lower()
    return lexicon.merge(n.drop_duplicates(subset=on), on=on, how="left")


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


def load_items(path: str, required_fields) -> pd.DataFrame:
    """Load a paradigm item table (prime-target pairs, sentences, …).

    The table must carry an ``item`` identifier, a ``condition`` label and the
    paradigm's presented fields. Field values are validated (no control
    characters; bounded length) so a crafted item cannot corrupt the generated
    loop table or scripts. Items are mapped to a deterministic integer ``set`` id
    (byte order) so counterbalancing matches the corpus path and the two engines.
    """
    parts = str(path).replace("\\", "/").split("/")
    if ".." in parts:
        raise ValueError("lexsync: items path must not contain '..'.")
    df = read_csv_utf8(path)
    needed = ["item", "condition"] + list(required_fields)
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"lexsync: items table '{path}' is missing column(s): {', '.join(missing)}.")
    df = df.copy()
    for f in [c for c in required_fields if c in df.columns]:
        df[f] = [clean_field(v, f) for v in df[f]]
    items = sorted(df["item"].astype(str).unique(), key=lambda s: s.encode("utf-8"))
    set_map = {it: i + 1 for i, it in enumerate(items)}
    df["set"] = df["item"].astype(str).map(set_map)
    df["condition"] = df["condition"].astype(str)
    return df.reset_index(drop=True)


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
