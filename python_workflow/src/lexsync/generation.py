# -*- coding: utf-8 -*-
"""Deterministic, orthographically-controlled pseudoword generation.

For each real base word a pseudoword is produced by *constrained letter
substitution*: change the fewest letters so that (i) every resulting letter
bigram is attested in the corpus (orthographic legality), (ii) the form is not a
real word, and (iii) the length is preserved exactly. Among the legal non-word
neighbours the most bigram-plausible is chosen, with byte-order tie-breaks, so
the R and Python engines generate the identical pseudoword from the identical
corpus (see R_workflow/R/generation.R). This is a deterministic orthographic
cousin of Wuggy (Keuleers & Brysbaert, 2010); it trades Wuggy's subsyllabic model
for exact length matching and cross-engine reproducibility.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

_LETTERS = "abcdefghijklmnopqrstuvwxyz"


def bigram_counts(words) -> dict:
    """Integer counts of adjacent letter bigrams across a word list."""
    counts: dict[str, int] = {}
    for w in words:
        w = str(w)
        for i in range(len(w) - 1):
            bg = w[i:i + 2]
            counts[bg] = counts.get(bg, 0) + 1
    return counts


def _legal(cand: str, bigrams: dict) -> bool:
    return all(cand[i:i + 2] in bigrams for i in range(len(cand) - 1))


def _score(cand: str, bigrams: dict) -> int:
    return sum(bigrams.get(cand[i:i + 2], 0) for i in range(len(cand) - 1))


def make_pseudoword(word: str, bigrams: dict, lexicon: set, used: set) -> str | None:
    """The most bigram-plausible legal non-word at the smallest edit distance.

    Searches single-letter substitutions first, then two-letter substitutions;
    candidates are ranked by summed bigram frequency with a byte-order tie-break,
    so the choice is deterministic and identical across engines.
    """
    word = str(word)
    L = len(word)
    # Distance 1: one substituted position.
    cands = []
    for pos in range(L):
        for c in _LETTERS:
            if c == word[pos]:
                continue
            cand = word[:pos] + c + word[pos + 1:]
            if cand in lexicon or cand in used:
                continue
            if _legal(cand, bigrams):
                cands.append(cand)
    if not cands:
        # Distance 2: two substituted positions (rare fallback).
        for i in range(L):
            for j in range(i + 1, L):
                for ci in _LETTERS:
                    if ci == word[i]:
                        continue
                    for cj in _LETTERS:
                        if cj == word[j]:
                            continue
                        cand = word[:i] + ci + word[i + 1:j] + cj + word[j + 1:]
                        if cand in lexicon or cand in used:
                            continue
                        if _legal(cand, bigrams):
                            cands.append(cand)
    if not cands:
        return None
    return min(cands, key=lambda c: (-_score(c, bigrams), c.encode("utf-8")))


def generate_pseudowords(base_words, reference_words) -> pd.DataFrame:
    """A length-matched pseudoword for each base word.

    Base words are processed in byte order so the ``used`` set evolves identically
    across engines. Returns a frame with ``base_word`` and ``pseudoword``.
    """
    base = [str(w) for w in base_words]
    lexicon = set(str(w) for w in reference_words)
    bigrams = bigram_counts(reference_words)
    order = sorted(range(len(base)), key=lambda i: base[i].encode("utf-8"))
    used: set = set()
    pseudo = [None] * len(base)
    for i in order:
        pw = make_pseudoword(base[i], bigrams, lexicon, used)
        if pw is None:
            raise ValueError(f"lexsync: could not generate a pseudoword for '{base[i]}'.")
        used.add(pw)
        pseudo[i] = pw
    return pd.DataFrame({"base_word": base, "pseudoword": pseudo})


def build_lexdec_stimuli(pool: pd.DataFrame, n: int, reference_words=None) -> pd.DataFrame:
    """Assemble a word-vs-pseudoword lexical-decision set from a candidate pool.

    Real words are drawn by an even spread across the byte-ordered pool (the same
    deterministic device as the matcher's anchor), then a length-matched
    pseudoword is generated for each. ``reference_words`` (the full lexicon)
    supplies the bigram statistics and the real-word list a pseudoword must avoid;
    it falls back to the pool when not given. The presented string is the
    ``target`` column; conditions are ``word`` and ``pseudoword`` and ``set``
    pairs them.
    """
    pool = (pool.assign(_k=pool["word"].map(lambda w: w.encode("utf-8")))
            .sort_values("_k").drop(columns="_k").reset_index(drop=True))
    if len(pool) == 0:
        raise ValueError("lexsync: lexical-decision pool is empty.")
    n_take = min(n, len(pool))
    idx = np.unique(np.round(np.linspace(1, len(pool), n_take)).astype(int)) - 1
    words = pool.iloc[idx].reset_index(drop=True)
    ref = list(reference_words) if reference_words is not None else pool["word"].tolist()
    gen = generate_pseudowords(words["word"].tolist(), ref)
    pw_map = dict(zip(gen["base_word"], gen["pseudoword"]))

    real = pd.DataFrame({
        "target": words["word"].tolist(), "word": words["word"].tolist(),
        "condition": "word", "length": words["length"].tolist(),
        "set": list(range(1, len(words) + 1)),
    })
    pseudo = pd.DataFrame({
        "target": [pw_map[w] for w in words["word"]], "word": [pw_map[w] for w in words["word"]],
        "condition": "pseudoword", "length": words["length"].tolist(),
        "set": list(range(1, len(words) + 1)),
    })
    out = pd.concat([real, pseudo], ignore_index=True)
    return out
