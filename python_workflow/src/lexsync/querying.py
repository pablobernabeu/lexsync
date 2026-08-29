"""Load lexica, validate the column contract and compute lexical dimensions.

Mirrors R_workflow/R/querying.R.
"""
from __future__ import annotations

import math
import re

import numpy as np
import pandas as pd
from rapidfuzz.distance import Hamming, Levenshtein

from .io_utils import _round_dp, clean_field, read_csv_utf8, sha256_file

# Maximal runs of (possibly accented) Latin vowels approximate syllable nuclei. The
# R mirror builds the same 26 accented code points with intToUtf8, to keep its source
# ASCII for CRAN, so the two lists look nothing alike and must be checked against each
# other by hand: a character in one and not the other changes n_syllables, which a
# design may match on. Must cover the same code points as .VOWELS in
# R_workflow/R/querying.R.
_VOWELS = re.compile(r"[aeiouyàáâãäåèéêëìíîïòóôõöøùúûüýÿ]+")

# readr trims ASCII whitespace from every field (trim_ws defaults to TRUE) and
# pandas trims nothing, so the same padded item table would otherwise yield
# different stimulus text, set ids and condition labels per engine. This pins the
# set readr removes; R_workflow/R/querying.R states the same trim, and explains
# why the reader's own trim_ws is left alone.
_ASCII_WS = " \t\r\n"


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
    # `or {}` at every level: an empty `dimensions:` or `frequency:` key parses to
    # None here and to NULL in R, where `$` chains through it to the default. A
    # default argument only covers an ABSENT key, so the two engines answered the
    # same schema with a column name and an AttributeError.
    freq_col = ((schema.get("dimensions") or {}).get("frequency") or {}).get("column") or "freq_zipf"
    # Filter before coercing: astype(str) renders a missing word as the literal
    # string "nan", which survives both guards below, whereas the R engine (where
    # as.character(NA) stays NA) drops the row. Coercing first would therefore
    # desynchronise the two engines' row counts and shift every subsequent id.
    df = df[df["word"].notna() & df[freq_col].notna()].copy()
    df["word"] = df["word"].astype(str).str.strip().str.lower()
    df = df[df["word"] != ""]
    df = df.drop_duplicates(subset="word")
    # An empty selection is never what the caller meant, and it fails far from
    # here: pandas would hand back a well-formed frame of nothing, while the R
    # engine dies on base R's "replacement has 1 row, data has 0". Both engines
    # raise this message instead, while the path is still in scope.
    if df.empty:
        raise ValueError(
            f"lexsync: lexicon '{path}' has no usable rows: it is empty, "
            f"or every row is missing 'word' or '{freq_col}'."
        )
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


def load_pool(path: str, schema: dict, lexicon=None, language=None) -> dict:
    """Load a supplied candidate pool of words and give it the matcher's dimensions.

    A researcher who already has a curated word list (from a previous study, a norming
    session, a colleague) should not have to dress it up as a corpus lexicon
    to get lexsync's matching, validation and datasheet. This reads such a list and
    returns something the matcher accepts.

    The list needs only a ``word`` column. Length and the syllable estimate are derived
    from the form. Everything else is either supplied on the list itself or looked up:
    with ``lexicon`` given, the corpus dimensions (frequency above all) are joined for
    those words, and a word the lexicon does not have is a hard error rather than a
    NaN, because the tolerance windows drop missing rows silently and the pool would
    then be smaller than the user believes it is.

    The returned ``reference`` matters as much as the pool. ``n_density`` and ``old20``
    are properties of a word in its *language*, not among the handful of words a study
    happens to use, so computing them against a 200-word supplied list would give
    numbers that mean nothing. When a lexicon is given, the reference is the lexicon's
    words; only without one does it fall back to the pool itself.

    Returns ``{"pool": DataFrame, "reference": list}``. Mirrors load_pool in
    R_workflow/R/querying.R.
    """
    if ".." in str(path).replace("\\", "/").split("/"):
        raise ValueError("lexsync: pool path must not contain '..'.")
    df = read_csv_utf8(path)
    if "word" not in df.columns:
        raise ValueError(
            "lexsync: supplied pool '%s' is missing the required 'word' column." % path)
    # The same normalisation load_lexicon applies, for the same reason: `word` is the
    # canonical key behind every byte-order tie-break, so the two engines must fold and
    # trim it identically before anything is sorted or numbered by it.
    df = df[df["word"].notna()].copy()
    df["word"] = df["word"].astype(str).str.strip().str.lower()
    df = df[df["word"] != ""].drop_duplicates(subset="word")
    if df.empty:
        raise ValueError(
            "lexsync: supplied pool '%s' has no usable rows: it is empty, or every row "
            "is missing 'word'." % path)
    df = (df.assign(_k=df["word"].map(lambda w: w.encode("utf-8")))
            .sort_values("_k").drop(columns="_k").reset_index(drop=True))

    reference = df["word"].tolist()
    if lexicon:
        lex = load_lexicon(lexicon, schema, language=language)
        reference = lex["word"].tolist()
        # `id` is the lexicon's own row number, meaningless once the pool is a subset.
        dims = [c for c in lex.columns if c not in ("word", "language", "source", "id")]
        clash = sorted((c for c in dims if c in df.columns),
                       key=lambda s: s.encode("utf-8"))
        if clash:
            raise ValueError(
                "lexsync: supplied pool '%s' already has column(s) %s, which the lexicon "
                "would also supply. Rename or drop them, so it is unambiguous which "
                "values the matcher used."
                % (path, ", ".join("'%s'" % c for c in clash)))
        known = set(lex["word"])
        absent = sorted((w for w in df["word"] if w not in known),
                        key=lambda s: s.encode("utf-8"))
        if absent:
            shown = absent[:5]
            raise ValueError(
                "lexsync: %d word(s) of supplied pool '%s' are absent from lexicon "
                "'%s': %s%s." % (len(absent), path, lexicon,
                                 ", ".join("'%s'" % w for w in shown),
                                 ", ..." if len(absent) > len(shown) else ""))
        by_word = lex.set_index("word")
        rows = by_word.loc[df["word"].tolist()]
        for d in dims:
            df[d] = rows[d].to_numpy()
    # Derived after any join, so a lexicon cannot overwrite them with its own copies.
    df["length"] = df["word"].str.len()
    df["n_syllables"] = df["word"].map(count_syllables)
    if language is not None:
        df["language"] = language
    df["id"] = np.arange(1, len(df) + 1)
    return {"pool": df.reset_index(drop=True), "reference": reference}


def add_bigram_frequency(df: pd.DataFrame, reference=None) -> pd.DataFrame:
    """Mean bigram probability (type-based, non-positional), a phonotactic-probability proxy.

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
        return _round_dp(sum(counts.get(b, 0) for b in bgs) / len(bgs) / total, 9)

    out = df.copy()
    out["bigram_freq"] = out["word"].map(bf)
    return out


def _norm_key(x) -> pd.Series:
    """The join key, normalised identically on both sides and in both engines.

    Trimmed and case-folded, which is what ``load_lexicon`` does to ``word``. A
    missing value stays missing rather than becoming the literal string ``"nan"``
    that ``astype(str)`` would produce and then happily join on.
    """
    values = [None if v is None or v != v else str(v).strip().lower() for v in x]
    return pd.Series(values, index=getattr(x, "index", None), dtype="object")


def merge_norms(lexicon: pd.DataFrame, norms, on: str = "word", columns=None) -> pd.DataFrame:
    """Left-join a norm table (e.g. concreteness, age of acquisition, valence).

    ``norms`` is a data frame or the path to a CSV with a word column and one or
    more norm columns. This is the connector for semantic dimensions: the norm data
    themselves are fetched separately (licensing varies), then merged here so the
    matcher can equate on them.

    The result is the lexicon itself with the norm columns appended, and the key is
    looked up positionally rather than through ``merge``. That is what makes the two
    engines agree by construction, with nothing to repair afterwards, because ``merge``
    and R's ``merge()`` were measured to diverge in three ways, each of them silent:
    R hoists the ``by`` column to position 1 while pandas keeps the left frame's
    order, so the column order differed whenever ``on`` was not already first; R
    disambiguates a colliding column name with ``.x``/``.y`` and pandas with
    ``_x``/``_y``, and either way a dimension the design matches on disappears under
    a name nothing looks for; and R's ``merge(sort = FALSE)`` leaves the row order
    unspecified. A positional lookup has none of those degrees of freedom. A
    colliding name is now an error instead.

    The key is trimmed and case-folded on *both* sides. Only the norm table's side
    was normalised before, so a lexicon holding ``Dog`` matched nothing and the
    design carried on with an all-``NaN`` dimension. Because both engines agreed on
    that wrong answer, no parity test could have caught it. The lexicon's
    own spelling is preserved rather than folded in place: ``word`` is the
    byte-order tie-break behind every selection, so the join must not rewrite it.

    Mirrors merge_norms in R_workflow/R/querying.R.
    """
    n = norms if isinstance(norms, pd.DataFrame) else read_csv_utf8(norms)
    if on not in lexicon.columns:
        raise ValueError(
            "lexsync: merge_norms needs join column '%s' on the lexicon." % on)
    if on not in n.columns:
        raise ValueError(
            "lexsync: merge_norms needs join column '%s' on the norm table." % on)
    cols = list(columns) if columns else [c for c in n.columns if c != on]
    absent = [c for c in cols if c not in n.columns]
    if absent:
        raise ValueError("lexsync: the norm table has no column(s): %s."
                         % ", ".join("'%s'" % c for c in absent))
    # Silently renaming the clash, as both merges do, is the worst outcome
    # available: a design matching on `frequency` would find neither `frequency.x`
    # nor `frequency_x` and would fail far from the cause, or match on the norm
    # table's column believing it was the lexicon's.
    clash = [c for c in cols if c in lexicon.columns]
    if clash:
        raise ValueError(
            "lexsync: norm column(s) %s already exist on the lexicon. Rename them "
            "in the norm table, or name the ones you want in `columns`."
            % ", ".join("'%s'" % c for c in clash))
    key = _norm_key(n[on])
    keep = (key.notna() & ~key.duplicated()).to_numpy()
    add = n.loc[keep, cols].copy()
    add.index = pd.Index(key.to_numpy()[keep], dtype="object")
    # reindex on a de-duplicated index is a left join: a label that is absent
    # (including a missing lexicon key) yields NaN, exactly as R's match() gives NA.
    joined = add.reindex(_norm_key(lexicon[on]).to_numpy())
    out = lexicon.copy()
    for c in cols:
        out[c] = joined[c].to_numpy()
    return out


# ---- The design's `norms:` block --------------------------------------------
# A design may name norm tables to be joined onto the lexicon before the pool is
# built, so `pool_filters`, `match_on` and a continuous `predictor` can all refer to
# a semantic dimension lexsync does not compute:
#
#   norms:
#     - path: norms/en_concreteness.csv
#       on: word                  # optional join key, default 'word'
#       columns: [concreteness]   # optional; default every column but the key
#
# The join itself is merge_norms(). What this adds is provenance, and that is not a
# nicety: a norm table can carry the very variable a design manipulates, so a
# datasheet that did not name the file and its checksum would describe a selection
# over columns whose origin is recorded nowhere. The loader hands the records back
# for build_datasheet() to write down.
#
# Coverage is recorded per column rather than per file, because one table can cover a
# dimension well and another badly, and an unmatched row becomes a NaN that the
# tolerance windows then drop from the pool without saying so.
#
# Mirrors .norm_specs / .apply_norms in R_workflow/R/querying.R.


def _norm_specs(design: dict):
    """The `norms:` entries, accepting a single bare mapping as well as a sequence."""
    specs = design.get("norms") or []
    return [specs] if isinstance(specs, dict) else list(specs)


def apply_norms(lex: pd.DataFrame, design: dict) -> dict:
    """Join the design's norm tables onto the lexicon, returning it and its record."""
    records = []
    for spec in _norm_specs(design):
        path = spec.get("path")
        if not path:
            raise ValueError("lexsync: every entry under `norms:` needs a `path`.")
        if ".." in str(path).replace("\\", "/").split("/"):
            raise ValueError("lexsync: norms path must not contain '..'.")
        on = spec.get("on") or "word"
        cols = list(spec["columns"]) if spec.get("columns") else None
        before = list(lex.columns)
        lex = merge_norms(lex, path, on=on, columns=cols)
        added = [c for c in lex.columns if c not in before]
        records.append({
            "path": path,
            "sha256": sha256_file(path),
            "on": on,
            "columns": [{"column": c, "n_matched": int(lex[c].notna().sum()),
                         "n_total": int(len(lex))} for c in added],
        })
    return {"lexicon": lex, "provenance": records}


def add_neighbourhood(df: pd.DataFrame, reference=None, n_old: int = 20) -> pd.DataFrame:
    """Coltheart's N (same-length, single substitution) and OLD20 for each word."""
    words = df["word"].astype(str).tolist()
    ref = list(dict.fromkeys(str(w) for w in (reference if reference is not None else words)))
    ref_len = np.array([len(w) for w in ref])
    n_density = np.zeros(len(words), dtype=int)
    old = np.full(len(words), np.nan)
    for i, w in enumerate(words):
        same_len = [r for r, L in zip(ref, ref_len, strict=True) if L == len(w)]
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



def add_pair_overlap(df: pd.DataFrame, prime: str = "prime",
                     target: str = "target") -> pd.DataFrame:
    """Orthographic overlap between the two members of each pair.

    Adds two columns. ``pair.lev`` is the Levenshtein distance between the pair's
    two orthographic forms, and ``pair.overlap`` is ``1 - lev / max(len)``, the
    proportion of the longer form the two share. Overlap is the standard confound
    control in a priming design: a related pair that also shares letters confounds
    semantic relatedness with orthographic similarity.

    Both engines return identical values, and the reasons are worth stating because
    they are the constraints on any future relational dimension. The core is an
    integer edit distance, and rapidfuzz's ``Levenshtein.distance`` and
    ``stringdist(method = "lv")`` agree exactly, including on decomposed Unicode and
    CJK, which is the same cross-library agreement ``add_neighbourhood`` already
    stakes ``old20`` on. Length is counted in code points, ``len()`` and R's
    ``nchar()`` default, never in bytes. The arithmetic uses only ``-`` and ``/``,
    which IEEE-754 mandates be correctly rounded, and the result is rounded to nine
    decimal places, the constant used everywhere else in the package. A degenerate
    pair of two empty forms returns 0 rather than ``0/0``, because a NaN would be
    sorted and compared and would then drop the row from one engine's control window
    but not the other's.
    """
    for col in (prime, target):
        if col not in df.columns:
            raise ValueError("lexsync: add_pair_overlap needs column '%s'." % col)
    a = [str(w).strip().lower() for w in df[prime]]
    b = [str(w).strip().lower() for w in df[target]]
    lev = [Levenshtein.distance(x, y) for x, y in zip(a, b, strict=True)]
    den = [max(len(x), len(y)) for x, y in zip(a, b, strict=True)]
    out = df.copy()
    out["pair.lev"] = np.array(lev, dtype=int)
    out["pair.overlap"] = [0.0 if d == 0 else _round_dp(1 - l / d, 9)
                           for l, d in zip(lev, den, strict=True)]
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
    # The item id, the condition label and the paradigm's presented fields are read as
    # text, never type-guessed. This engine happens to keep "f" a string anyway, but the
    # R engine's reader turns a column of `f` or `t` into a LOGICAL, so a design coding
    # its two response keys as f and j had `answer` become FALSE there and "f" here; and
    # `item` left to inference float-promoted a numeric id column, so '01' became '1'
    # (or, with a missing cell, '1.0'). Forcing the type on both sides makes the
    # agreement structural, where it would otherwise be coincidental.
    df = read_csv_utf8(path, as_character=["item", "condition"] + list(required_fields))
    needed = ["item", "condition"] + list(required_fields)
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"lexsync: items table '{path}' is missing column(s): {', '.join(missing)}.")
    # Missingness is tested before any string coercion: a missing cell in a dtype=str
    # column still arrives as NaN, and str() would render it as the literal 'nan',
    # which a blank condition then carries past the hash-key guard downstream.
    for col in needed:
        if df[col].isna().any():
            raise ValueError(
                f"lexsync: the items table has missing value(s) in column '{col}'; "
                "every item, condition and presented field must be filled.")
    df = df.copy()
    for f in [c for c in required_fields if c in df.columns]:
        df[f] = [str(v).strip(_ASCII_WS) for v in df[f]]
    item_key = df["item"].astype(str).str.strip(_ASCII_WS)
    df["condition"] = df["condition"].astype(str).str.strip(_ASCII_WS)
    # An all-whitespace cell is already missing in the R engine's reader (readr trims
    # before matching its na strings), so refusing the trimmed-empty value here keeps
    # the two engines refusing the same tables, with the same message.
    for col in needed:
        vals = item_key if col == "item" else df[col]
        if (vals == "").any():
            raise ValueError(
                f"lexsync: the items table has missing value(s) in column '{col}'; "
                "every item, condition and presented field must be filled.")
    # A repeated item-condition pair is a slip that would silently duplicate a trial
    # in every generated list; the first repeat in file order is reported.
    seen = set()
    for it, cond in zip(item_key, df["condition"], strict=True):
        if (it, cond) in seen:
            raise ValueError(
                f"lexsync: the items table repeats item '{it}' for condition '{cond}'; "
                "each item and condition pair may appear once.")
        seen.add((it, cond))
    for f in [c for c in required_fields if c in df.columns]:
        df[f] = [clean_field(v, f) for v in df[f]]
    items = sorted(item_key.unique(), key=lambda s: s.encode("utf-8"))
    set_map = {it: i + 1 for i, it in enumerate(items)}
    df["set"] = item_key.map(set_map)
    return df.reset_index(drop=True)


def build_pool(lexicon: pd.DataFrame, filters: dict | None = None) -> pd.DataFrame:
    """Build an experimental candidate pool by filtering a lexicon.

    ``filters`` maps a column to either a two-element numeric range or a list of
    permitted values. A row missing the filtered column is dropped under either
    kind, and a range with a reversed or non-finite bound is an error rather than an
    empty pool.

    A filter naming a column the frame does not have is silently skipped, because the
    same function filters lexica, supplied pools and pair tables, and those carry
    different columns. The cost is that a misspelt key silently widens a
    selection, so every caller that takes its filters from a design checks the names
    against the frame first: ``run_pipeline`` for ``pool_filters``,
    ``match_stimuli`` for a condition's ``define_by``, and
    ``select_continuous_pairs`` for both. Mirrors build_pool in
    R_workflow/R/querying.R.
    """
    df = lexicon
    if filters:
        for col, rng in filters.items():
            if col not in df.columns:
                continue
            vals = list(rng) if isinstance(rng, (list, tuple)) else [rng]
            if len(vals) == 2 and all(isinstance(v, (int, float)) for v in vals):
                # YAML's .inf and .nan arrive as ordinary floats, and either one,
                # like a reversed range, silently empties the pool row by row.
                # Non-finite first: a NaN bound would make the reversal test
                # meaningless. Equal bounds stay legal (the zh design uses [2, 2]).
                if not all(math.isfinite(float(v)) for v in vals):
                    raise ValueError(
                        f"lexsync: filter '{col}' has a non-finite bound; "
                        "ranges need finite numbers.")
                if vals[0] > vals[1]:
                    raise ValueError(
                        f"lexsync: filter '{col}' has a reversed range; "
                        "give it as [low, high].")
                df = df[df[col].notna() & (df[col] >= vals[0]) & (df[col] <= vals[1])]
            else:
                df = df[df[col].notna() & df[col].astype(str).isin([str(v) for v in vals])]
    return df.reset_index(drop=True)
