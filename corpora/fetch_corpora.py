#!/usr/bin/env python3
"""Build lexsync derived lexica from wordfreq, with N and OLD20 precomputed.

Usage:
    python corpora/fetch_corpora.py --languages en es --n-words 10000

This ingestion step writes:
  corpora/derived/<lang>.csv                          full derived lexicon
  R_workflow/inst/extdata/<lang>_example.csv          bundled slice (length 3-9)
  python_workflow/src/lexsync/data/<lang>_example.csv bundled slice (length 3-9)
and (re)writes corpora/ATTRIBUTION.md.

The orthographic-neighbourhood variables (Coltheart's N and OLD20) are computed
openly here with rapidfuzz and stored in the derived files, so both the R and
Python pipelines read identical, inspectable values. The standalone
add_neighbourhood()/compute_dimensions() functions remain available for users
who supply their own raw lexica.

wordfreq (Speer, 2022; MIT) aggregates several subtitle and web corpora,
including the SUBTLEX family. corpora/registry.yaml lists the curated,
individually citable SUBTLEX/openlexicon corpora that lexsync also supports.
"""
from __future__ import annotations

import argparse
import datetime
import re
from pathlib import Path

import numpy as np
import pandas as pd
import wordfreq
from rapidfuzz import process
from rapidfuzz.distance import Levenshtein

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "corpora" / "derived"
PACKAGE_DATA_DIRS = (
    ROOT / "R_workflow" / "inst" / "extdata",
    ROOT / "python_workflow" / "src" / "lexsync" / "data",
)

LANG_NAMES = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German",
    "nl": "Dutch", "it": "Italian", "pt": "Portuguese", "zh": "Chinese (Mandarin)",
}
# Letters admitted per language (lower case, accents where relevant). For Chinese
# (a logographic script) the admitted forms are runs of CJK unified ideographs,
# and 'length' is therefore measured in characters rather than letters.
WORD_RE = {
    "default": re.compile(r"^[a-z]+$"),
    "es": re.compile(r"^[a-záéíóúüñ]+$"),
    "fr": re.compile(r"^[a-zàâäçéèêëîïôöùûüÿœæ]+$"),
    "de": re.compile(r"^[a-zäöüß]+$"),
    "pt": re.compile(r"^[a-záàâãçéêíóôõú]+$"),
    "it": re.compile(r"^[a-zàèéìíîòóùú]+$"),
    "nl": re.compile(r"^[a-zàäéëïóöü]+$"),
    "zh": re.compile(r"^[一-鿿]+$"),
}
# Word-length bounds (in characters) for the full lexicon and for the bundled
# example slice. Chinese words are short: two-character words dominate the
# language, so the demonstration draws on two- and three-character words.
LEN_BOUNDS = {"default": (2, 15), "zh": (2, 3)}
SLICE_LEN = {"default": (3, 9), "zh": (2, 3)}


def clean_words(lang: str, n_words: int, min_len: int = 2, max_len: int = 15) -> list[str]:
    """Return up to `n_words` cleaned forms by frequency, admitted by the script."""
    rx = WORD_RE.get(lang, WORD_RE["default"])
    out: list[str] = []
    for w in wordfreq.top_n_list(lang, n_words * 3):
        w = w.lower()
        if rx.match(w) and min_len <= len(w) <= max_len:
            out.append(w)
        if len(out) >= n_words:
            break
    return out


def neighbourhood(words: list[str], n_old: int = 20, chunk: int = 1000):
    """Coltheart's N (same-length, single substitution) and OLD20 for `words`."""
    lengths = np.array([len(w) for w in words])
    m = len(words)
    n_density = np.zeros(m, dtype=int)
    old = np.full(m, np.nan)
    for start in range(0, m, chunk):
        stop = min(start + chunk, m)
        block = process.cdist(
            words[start:stop], words,
            scorer=Levenshtein.distance, dtype=np.uint16, workers=-1,
        )
        for r in range(stop - start):
            i = start + r
            row = block[r]
            # Same length + Levenshtein 1 implies a single substitution (Hamming 1).
            n_density[i] = int(np.sum((row == 1) & (lengths == lengths[i])))
            nz = row[row > 0]
            if nz.size:
                k = min(n_old, nz.size)
                old[i] = float(np.mean(np.partition(nz, k - 1)[:k]))
    return n_density, old


def build(lang: str, n_words: int) -> pd.DataFrame:
    lo, hi = LEN_BOUNDS.get(lang, LEN_BOUNDS["default"])
    words = clean_words(lang, n_words, min_len=lo, max_len=hi)
    zipf = [wordfreq.zipf_frequency(w, lang) for w in words]
    df = pd.DataFrame({
        "word": words,
        "freq_zipf": np.round(zipf, 3),
        "language": lang,
        "source": "wordfreq",
    })
    df = df[df.freq_zipf > 0].reset_index(drop=True)
    n_density, old = neighbourhood(df.word.tolist())
    df["n_density"] = n_density
    df["old20"] = np.round(old, 3)
    return df.sort_values("word").reset_index(drop=True)


def write_slice(df: pd.DataFrame, lang: str, target: int = 3000) -> int:
    """Write a small, frequency-stratified example slice for the packages.

    The full derived lexicon (corpora/derived/) is the realistic neighbourhood
    reference; the installed packages bundle only this compact slice for tests
    and examples, so they stay within distribution size limits.
    """
    lo, hi = SLICE_LEN.get(lang, SLICE_LEN["default"])
    sl = df[(df.word.str.len() >= lo) & (df.word.str.len() <= hi)].copy()
    if len(sl) > target:
        sl = sl.assign(_bin=pd.qcut(sl.freq_zipf, 10, labels=False, duplicates="drop"))
        per = max(1, target // max(1, sl["_bin"].nunique()))
        parts = []
        for _, g in sl.groupby("_bin"):
            g = g.sort_values("word")
            if len(g) > per:
                idx = np.unique(np.round(np.linspace(0, len(g) - 1, per)).astype(int))
                g = g.iloc[idx]
            parts.append(g)
        sl = pd.concat(parts).drop(columns="_bin")
    sl = sl.sort_values("word").reset_index(drop=True)
    for d in PACKAGE_DATA_DIRS:
        d.mkdir(parents=True, exist_ok=True)
        sl.to_csv(d / f"{lang}_example.csv", index=False, encoding="utf-8")
    return len(sl)


# Languages whose 'length' and neighbourhood measures are character-based rather
# than letter-based (logographic scripts).
CHAR_BASED = {"zh"}


def attribution_entry(lang: str, df: pd.DataFrame, date: str) -> str:
    zmin, zmax = df.freq_zipf.min(), df.freq_zipf.max()
    unit = "over characters " if lang in CHAR_BASED else ""
    return (
        f"- **{LANG_NAMES.get(lang, lang)} ('{lang}')** — {len(df)} words, "
        f"Zipf {zmin:.2f}-{zmax:.2f}. Source: wordfreq (Speer, 2022; MIT), "
        f"retrieved {date}. N and OLD20 computed {unit}by lexsync."
    )


def write_attribution(fresh_dates: dict[str, str]) -> None:
    """Regenerate ATTRIBUTION.md from *every* derived lexicon present.

    Scanning the derived directory (rather than only the languages built in the
    current run) keeps the attribution complete when languages are added one at a
    time. Languages built this run carry today's date; others carry the
    modification date of their derived file.
    """
    path = ROOT / "corpora" / "ATTRIBUTION.md"
    entries = []
    for csv in sorted(DERIVED.glob("*.csv")):
        lang = csv.stem
        df = pd.read_csv(csv, encoding="utf-8")
        date = fresh_dates.get(lang) or datetime.date.fromtimestamp(csv.stat().st_mtime).isoformat()
        entries.append(attribution_entry(lang, df, date))
    text = (
        "# Corpus attribution\n\n"
        "Lexical corpora used by lexsync, with their sources, licences and retrieval\n"
        "dates. Bundled derivatives are distributed under CC BY-SA 4.0 (see LICENSE-DATA).\n\n"
        "## Demonstration corpora (bundled)\n\n"
        + "\n".join(entries)
        + "\n\n## Citations\n\n"
        "- Speer, R. (2022). rspeer/wordfreq: v3.0. Zenodo. https://doi.org/10.5281/zenodo.7199437\n"
        "- van Heuven, W. J. B., Mandera, P., Keuleers, E., & Brysbaert, M. (2014). "
        "SUBTLEX-UK. Quarterly Journal of Experimental Psychology, 67(6), 1176-1190. "
        "https://doi.org/10.1080/17470218.2013.850521\n"
        "- Cuetos, F., González-Nosti, M., Barbón, A., & Brysbaert, M. (2011). "
        "SUBTLEX-ESP. Psicológica, 32(2), 133-143.\n"
        "- See corpora/registry.yaml for the full list of curated, individually "
        "citable SUBTLEX/openlexicon corpora that lexsync supports.\n"
    )
    path.write_text(text, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Build lexsync derived lexica.")
    ap.add_argument("--languages", nargs="+", default=["en", "es"])
    ap.add_argument("--n-words", type=int, default=10000)
    args = ap.parse_args()

    DERIVED.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    fresh_dates: dict[str, str] = {}
    for lang in args.languages:
        print(f"[fetch_corpora] building '{lang}' (target {args.n_words} words) ...", flush=True)
        df = build(lang, args.n_words)
        out = DERIVED / f"{lang}.csv"
        df.to_csv(out, index=False, encoding="utf-8")
        n_slice = write_slice(df, lang)
        zmin, zmax = df.freq_zipf.min(), df.freq_zipf.max()
        print(f"  -> {out.name}: {len(df)} words (Zipf {zmin:.2f}-{zmax:.2f}); slice {n_slice}", flush=True)
        fresh_dates[lang] = today
    # Regenerate the attribution from all derived lexica, so adding one language
    # never drops the others.
    write_attribution(fresh_dates)
    print("[fetch_corpora] done.", flush=True)


if __name__ == "__main__":
    main()
