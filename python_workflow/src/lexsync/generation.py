"""Deterministic, orthographically-controlled pseudoword generation.

For each real base word a pseudoword is produced by *constrained letter
substitution*: change the fewest letters so that (i) every resulting letter
bigram is attested in the corpus (orthographic legality), (ii) the form is not in
the reference word list, and (iii) the length is preserved exactly. Among the
legal candidates the most bigram-typical is chosen, with byte-order tie-breaks,
so the R and Python engines generate the identical pseudoword from the identical
corpus (see R_workflow/R/generation.R).

A real word is anything in the reference list, so a low-frequency word below the
lexicon's floor (Zipf 2.95 in the bundled English lexicon) is not one. The
generators therefore take an ``exclude`` list of further known word forms, which a
pseudoword must not equal either, and ``_read_known_forms`` reads such lists for a
design's ``items.generation.exclude``. Lexicality is checked against those forms
only, so a form missing from all of them may still be a word: crier, pall and
titer have come through with the English lexicon and no exclusion list. Because
the scoring picks the most typical candidate and does not match the base word,
pseudowords are more bigram-typical than their base words (d about -1.5, words
minus pseudowords, in en_lexdec).

The subsyllabic method is an orthographic approximation of Wuggy (Keuleers &
Brysbaert, 2010), and it differs from Wuggy in several ways. Wuggy matches the
template's transition frequencies, matches letter length by default and has
orthographic language plugins. By default it keeps two thirds of the segments,
whereas lexsync's subsyllabic method replaces up to ceil(2k/3) of a word's k
constituents.
"""
from __future__ import annotations

import os
import re

import numpy as np
import pandas as pd
import yaml

from . import corpora as _corpora
from .io_utils import read_csv_utf8, sha256_file
from .querying import _SYLLABLE_VOWELS, _norm_key

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


def _norm_forms(values) -> list:
    """Word forms keyed as a lexicon's words are: trimmed, lower-cased, NFC."""
    return _norm_key(pd.Series(list(values), dtype=object)).tolist()


def _known_set(reference_words, exclude) -> set:
    """The forms a pseudoword must not equal: the reference words and ``exclude``.

    The excluded forms are trimmed, lower-cased and put in NFC, as a lexicon's words
    are, so a list written in another case or spelling still matches. They only
    widen this set. The bigram statistics and the constituent inventory still come
    from the reference words alone, so an exclusion list removes candidates without
    changing how the others are scored. Mirrors .known_set in generation.R.
    """
    known = set(str(w) for w in reference_words)
    if exclude is not None:
        # A bare string is one form, as the R twin's length-one vector is.
        forms = [exclude] if isinstance(exclude, str) else exclude
        known.update(v for v in _norm_forms(forms) if v)
    return known


def generate_pseudowords(base_words, reference_words, exclude=None) -> pd.DataFrame:
    """A length-matched pseudoword for each base word.

    Base words are processed in byte order so the ``used`` set evolves identically
    across engines. ``exclude`` (optional) lists further word forms no pseudoword
    may equal, such as a list of low-frequency words the reference lacks. Returns a
    frame with ``base_word`` and ``pseudoword``.
    """
    base = [str(w) for w in base_words]
    lexicon = _known_set(reference_words, exclude)
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
    spans = [(m.start(), m.end()) for m in _SYLLABLE_VOWELS.finditer(w)]
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


def generate_pseudowords_subsyllabic(base_words, reference_words,
                                     exclude=None) -> pd.DataFrame:
    """A subsyllabic pseudoword for each base word (with letter-substitution fallback).

    Base words are processed in byte order so the ``used`` set evolves identically
    across engines; a base word with no legal subsyllabic swap falls back to the
    letter-substitution generator, so every word yields a pseudoword. ``exclude``
    is as for :func:`generate_pseudowords`.
    """
    base = [str(w) for w in base_words]
    lexicon = _known_set(reference_words, exclude)
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


def _lexdec_eligible(pool: pd.DataFrame) -> pd.DataFrame:
    """The rows of a pool the pseudoword generators can use, in the pool's order.

    The generators are orthographic and defined for Latin a-z words, so a word with
    any other character (an accent, a hyphen, a digit) is left out. The pipeline
    counts these rows as a generated design's candidates: counting the whole band
    reported, for a Spanish band, accented words the generator never sees. Mirrors
    .lexdec_eligible in generation.R.
    """
    keep = pool["word"].astype(str).str.fullmatch(r"[a-z]+").fillna(False).astype(bool)
    return pool[keep.to_numpy()].reset_index(drop=True)


def build_lexdec_stimuli(pool: pd.DataFrame, n: int, reference_words=None,
                         method: str = "letter_substitution", exclude=None) -> pd.DataFrame:
    """Assemble a word-vs-pseudoword lexical-decision set from a candidate pool.

    Real words are drawn by an even spread across the byte-ordered pool (the same
    deterministic device as the matcher's anchor), then a length-matched
    pseudoword is generated for each. The pool is first filtered to lower-case
    a-z forms, the only ones the pseudoword generators are defined for, so the
    eligible pool can be smaller than the request; the pipeline's shortfall
    policy then decides whether that errors. ``reference_words`` (the full lexicon)
    supplies the bigram statistics and the real-word list a pseudoword must avoid;
    it falls back to the pool when not given. ``exclude`` (optional) lists further
    known word forms a pseudoword must not equal, which the reference may lack. The
    presented string is the ``target`` column; conditions are ``word`` and
    ``pseudoword`` and ``set`` pairs them.
    """
    pool = (pool.assign(_k=pool["word"].map(lambda w: w.encode("utf-8")))
            .sort_values("_k").drop(columns="_k").reset_index(drop=True))
    # The pseudoword generators are orthographic and defined for Latin a-z words;
    # any word with another character is skipped, keeping the two engines in step.
    pool = _lexdec_eligible(pool)
    if len(pool) == 0:
        raise ValueError("lexsync: lexical-decision pool has no a-z words.")
    n_take = min(n, len(pool))
    idx = np.unique(np.round(np.linspace(1, len(pool), n_take)).astype(int)) - 1
    words = pool.iloc[idx].reset_index(drop=True)
    ref = list(reference_words) if reference_words is not None else pool["word"].tolist()
    if method == "subsyllabic":
        gen = generate_pseudowords_subsyllabic(words["word"].tolist(), ref, exclude=exclude)
    elif method == "letter_substitution":
        gen = generate_pseudowords(words["word"].tolist(), ref, exclude=exclude)
    else:
        raise ValueError(f"lexsync: unknown pseudoword generation method '{method}'.")
    pw_map = dict(zip(gen["base_word"], gen["pseudoword"], strict=True))

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


# A registry corpus is named by a bare token; anything else in an exclusion list is a
# path. Mirrors .REGISTRY_NAME in generation.R.
_REGISTRY_NAME = re.compile(r"[A-Za-z0-9_-]+")
_EXCLUDE_MESSAGE = ("lexsync: items.generation.exclude must list file paths or registry "
                    "corpus names.")


def _registry_entry(name: str):
    """The registry's `corpora` entry for a bare name, or None.

    A registry that cannot be found or read leaves the name to be read as a path.
    """
    if not _REGISTRY_NAME.fullmatch(name):
        return None
    try:
        with open(_corpora._registry_path(None), encoding="utf-8") as handle:
            reg = yaml.safe_load(handle) or {}
    except (OSError, ValueError, yaml.YAMLError):
        return None
    entry = (reg.get("corpora") or {}).get(name)
    return entry if isinstance(entry, dict) else None


def _read_text_bytes(path: str) -> list:
    """The lines of a UTF-8 file, without a byte-order mark or line feeds.

    A file in another encoding is refused, because its accented forms would be
    misread, and the R twin's reader would find no forms in it at all.
    """
    with open(path, "rb") as handle:
        data = handle.read()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError(f"lexsync: known-form list '{path}' is not UTF-8 text.") from None
    if text.startswith("\ufeff"):
        text = text[1:]
    return text.split("\n")


# A line of a one-form-per-line list that holds one of these is a table row, which
# would be kept whole as one form and match no pseudoword, so the list would exclude
# nothing while the datasheet counted its rows. SUBTLEX-US, for one, is distributed as
# a tab-separated .txt file. Mirrors .TABLE_SEPARATORS in generation.R.
_TABLE_SEPARATORS = ("\t", ",", ";")


def _forms_from_lines(lines, path: str) -> list:
    """Word forms from a one-form-per-line list. Blank lines and lines beginning '#'
    are skipped, and every form is trimmed, lower-cased and put in NFC. A line that
    holds a tab, a comma or a semicolon is refused, since the file is then a table."""
    out = []
    for i, v in enumerate(_norm_forms(lines), start=1):
        if not v or v.startswith("#"):
            continue
        if any(sep in v for sep in _TABLE_SEPARATORS):
            raise ValueError(
                f"lexsync: line {i} of the known-form list '{path}' holds a tab, comma or "
                f"semicolon, so the file is a table. List one form per line, or give a "
                f"CSV file with a 'word' column.")
        out.append(v)
    return out


def _forms_from_tab_table(path: str, column: str) -> list:
    """One column of a tab-separated table, the layout openlexicon serves. Read by
    splitting each line, with no quoting rule, so both engines read the same cells."""
    lines = [ln for ln in _read_text_bytes(path) if ln.strip(" \t\r\n")]
    if not lines:
        return []
    header = [h.strip(" \t\r\n") for h in lines[0].split("\t")]
    if column not in header:
        raise ValueError(f"lexsync: known-form table '{path}' has no '{column}' column.")
    j = header.index(column)
    cells = [row.split("\t")[j] if len(row.split("\t")) > j else "" for row in lines[1:]]
    return [v for v in _norm_forms(cells) if v]


def _forms_from_csv(path: str, column: str) -> list:
    table = read_csv_utf8(path, as_character=[column])
    if column not in table.columns:
        raise ValueError(f"lexsync: known-form table '{path}' has no '{column}' column.")
    return [v for v in _norm_forms(table[column]) if v]


def _read_known_forms(entries) -> dict:
    """Read the word-form lists of a design's ``items.generation.exclude``.

    Each entry is a path or the name of a corpus in the registry. A path ending in
    ``.csv`` is a table whose ``word`` column holds the forms; any other path is a
    UTF-8 text file with one form per line, in which blank lines and lines beginning
    ``#`` are skipped and a line holding a tab, comma or semicolon is refused as a
    table row. A registry name is read from the copy ``fetch_corpus`` put in
    the cache, by the column the registry maps to ``word``, and is refused with the
    fetch command when no copy is there. Every form is trimmed, lower-cased and put
    in NFC, as a lexicon's words are.

    Returns ``{"forms": [...], "records": [...]}``: the distinct forms of all the
    lists in UTF-8 byte order, and for each list its ``source`` (the path with '/'
    separators, or the registry name), the ``sha256`` of the file read and
    ``n_forms``, the number of distinct forms it holds. Mirrors .read_known_forms in
    generation.R.
    """
    if entries is None:
        entries = []
    elif isinstance(entries, str):
        entries = [entries]
    elif not isinstance(entries, (list, tuple)):
        raise ValueError(_EXCLUDE_MESSAGE)
    forms: set = set()
    records = []
    for entry in entries:
        if not isinstance(entry, str) or not entry.strip(" \t\r\n"):
            raise ValueError(_EXCLUDE_MESSAGE)
        reg = _registry_entry(entry)
        if reg is not None:
            path = os.path.join(_corpora.cache_dir(), f"{entry}.csv")
            if not os.path.isfile(path):
                raise ValueError(
                    f"lexsync: items.generation.exclude names the registry corpus "
                    f"'{entry}', which is not in the cache ({path}). Fetch it first with "
                    f"fetch_corpus('{entry}'), or list a word-form file instead.")
            column = str((reg.get("columns") or {}).get("word") or "word")
            first = _read_text_bytes(path)[0]
            got = (_forms_from_tab_table(path, column) if "\t" in first
                   else _forms_from_csv(path, column))
            source = entry
        else:
            if not os.path.isfile(entry):
                raise ValueError(
                    f"lexsync: items.generation.exclude names '{entry}', which is neither "
                    f"a readable file nor a corpus in the registry.")
            path = entry
            got = (_forms_from_csv(path, "word") if entry.lower().endswith(".csv")
                   else _forms_from_lines(_read_text_bytes(path), entry))
            source = entry.replace("\\", "/")
        distinct = set(got)
        forms.update(distinct)
        records.append({"source": source, "sha256": sha256_file(path),
                        "n_forms": len(distinct)})
    return {"forms": sorted(forms, key=lambda w: w.encode("utf-8")), "records": records}
