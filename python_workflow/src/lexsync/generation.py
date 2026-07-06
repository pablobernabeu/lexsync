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

from .querying import _VOWELS

_LETTERS = "abcdefghijklmnopqrstuvwxyz"
# Order in which subsyllabic constituents are considered for substitution: codas
# and nuclei vary more freely than onsets, which carry the most identifying
# orthography, so they are changed first.
_ROLE_ORDER = {"coda": 0, "nucleus": 1, "onset": 2}


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


def segment_subsyllabic(word) -> list:
    """Split a word into ordered ``(role, text)`` subsyllabic constituents.

    Nuclei are the maximal vowel runs (the same regex used for syllable counting);
    the consonants before the first nucleus form the first onset, those after the
    last nucleus the final coda, and a consonant run *between* two nuclei is split
    at its midpoint (``floor(m/2)`` to the left coda, the rest to the right onset).
    Segmentation is on character indices, so accented multi-byte vowels are handled
    identically in R and Python. A word with no vowel run returns ``[]`` (its caller
    falls back to letter substitution). This is a deterministic orthographic
    approximation of Wuggy's subsyllabic model (Keuleers & Brysbaert, 2010), not
    phonological syllabification.
    """
    w = str(word).lower()
    # Subsyllabic segmentation is an orthographic model for Latin a-z words; any
    # word with a character outside a-z (accented, hyphenated, digit) returns [] so
    # the caller falls back to letter substitution, which keeps the two engines in
    # step and avoids multi-byte-string edge cases.
    if not (w.isascii() and w.isalpha()):
        return []
    spans = [(m.start(), m.end()) for m in _VOWELS.finditer(w)]
    if not spans:
        return []
    out = []
    if spans[0][0] > 0:
        out.append(("onset", w[:spans[0][0]]))
    for si, (s, e) in enumerate(spans):
        out.append(("nucleus", w[s:e]))
        run = w[e:(spans[si + 1][0] if si + 1 < len(spans) else len(w))]
        m = len(run)
        if si + 1 < len(spans):
            cut = m // 2
            if cut:
                out.append(("coda", run[:cut]))
            if m - cut:
                out.append(("onset", run[cut:]))
        elif m:
            out.append(("coda", run))
    return out


def build_constituent_inventory(reference_words) -> dict:
    """Attested subsyllabic constituents keyed by ``(role, length)`` with counts.

    Integer counts, order-independent, so the inventory is identical however the
    reference lexicon is ordered.
    """
    inv: dict = {}
    for w in reference_words:
        for role, text in segment_subsyllabic(w):
            key = (role, len(text))
            bucket = inv.setdefault(key, {})
            bucket[text] = bucket.get(text, 0) + 1
    return inv


def make_subsyllabic_pseudoword(word, inv, bigrams, lexicon, used):
    """A pseudoword built by swapping whole subsyllabic constituents.

    Up to ``ceil(2k/3)`` of the word's ``k`` constituents (codas and nuclei before
    onsets) are each replaced, one at a time, by an attested constituent of the
    same role and length, keeping every letter bigram legal and the form a novel
    non-word. Each swap preserves length, so the whole form does. Returns ``None``
    if no legal swap is possible (the caller then falls back to letter
    substitution), so structure is respected without ever failing to produce a
    pseudoword. The winning replacement is the most bigram-plausible with a
    byte-order tie-break, so the two engines agree.
    """
    segs = segment_subsyllabic(word)
    if not any(role == "nucleus" for role, _ in segs):
        return None
    k = len(segs)
    target = -(-2 * k // 3)                      # ceil(2k/3)
    texts = [t for _, t in segs]
    eligible = [i for i, (role, t) in enumerate(segs)
                if len(inv.get((role, len(t)), {})) >= 2]
    eligible.sort(key=lambda i: (_ROLE_ORDER[segs[i][0]], i))
    changed = 0
    for i in eligible[:target]:
        role, orig = segs[i][0], texts[i]
        best = None
        for alt in inv[(role, len(orig))]:
            if alt == orig:
                continue
            trial = texts[:]
            trial[i] = alt
            cand = "".join(trial)
            if cand in lexicon or cand in used or not _legal(cand, bigrams):
                continue
            key = (-_score(cand, bigrams), cand.encode("utf-8"))
            if best is None or key < best[0]:
                best = (key, trial)
        if best is not None:
            texts = best[1]
            changed += 1
    if changed == 0:
        return None
    final = "".join(texts)
    if final in lexicon or final in used or not _legal(final, bigrams):
        return None
    return final


def generate_pseudowords_subsyllabic(base_words, reference_words) -> pd.DataFrame:
    """A subsyllabic pseudoword for each base word (with letter-substitution fallback).

    Base words are processed in byte order so the ``used`` set evolves identically
    across engines; a base word with no legal subsyllabic swap falls back to the
    letter-substitution generator, so every word yields a pseudoword.
    """
    base = [str(w) for w in base_words]
    lexicon = set(str(w) for w in reference_words)
    bigrams = bigram_counts(reference_words)
    inv = build_constituent_inventory(reference_words)
    order = sorted(range(len(base)), key=lambda i: base[i].encode("utf-8"))
    used: set = set()
    pseudo = [None] * len(base)
    for i in order:
        pw = make_subsyllabic_pseudoword(base[i], inv, bigrams, lexicon, used)
        if pw is None:
            pw = make_pseudoword(base[i], bigrams, lexicon, used)
        if pw is None:
            raise ValueError(f"lexsync: could not generate a pseudoword for '{base[i]}'.")
        used.add(pw)
        pseudo[i] = pw
    return pd.DataFrame({"base_word": base, "pseudoword": pseudo})


def build_lexdec_stimuli(pool: pd.DataFrame, n: int, reference_words=None,
                         method: str = "letter_substitution") -> pd.DataFrame:
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
    # The pseudoword generators are orthographic and defined for Latin a-z words;
    # any word with another character is skipped, keeping the two engines in step.
    pool = pool[pool["word"].astype(str).str.fullmatch(r"[a-z]+")].reset_index(drop=True)
    if len(pool) == 0:
        raise ValueError("lexsync: lexical-decision pool has no a-z words.")
    n_take = min(n, len(pool))
    idx = np.unique(np.round(np.linspace(1, len(pool), n_take)).astype(int)) - 1
    words = pool.iloc[idx].reset_index(drop=True)
    ref = list(reference_words) if reference_words is not None else pool["word"].tolist()
    if method == "subsyllabic":
        gen = generate_pseudowords_subsyllabic(words["word"].tolist(), ref)
    elif method == "letter_substitution":
        gen = generate_pseudowords(words["word"].tolist(), ref)
    else:
        raise ValueError(f"lexsync: unknown pseudoword generation method '{method}'.")
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
