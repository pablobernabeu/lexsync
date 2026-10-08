"""Load lexica, validate the column contract and compute lexical dimensions.

Mirrors R_workflow/R/querying.R.
"""
from __future__ import annotations

import math
import re
import unicodedata

import numpy as np
import pandas as pd
from rapidfuzz import process
from rapidfuzz.distance import Levenshtein

from .io_utils import _NUMERIC_CELL, _round_dp, clean_field, read_csv_utf8, sha256_file

# The syllable estimate counts maximal runs of Latin vowel letters. A word is first
# decomposed (NFD) and stripped of its combining marks, so every accented vowel counts
# as its base letter. That covers the Latin-1 vowels, those of Latin Extended-A and -B
# (ą ę ě ő ű ă ǎ and the rest) and the Vietnamese vowels of Latin Extended Additional.
# Four vowel letters do not decompose and are named: æ, ø, dotless ı and œ. The class
# used to list 26 precomposed Latin-1 vowels without æ, so Polish, Czech, Hungarian,
# Romanian, Turkish, Danish and Norwegian words were undercounted.
#
# The estimate is defined only for words written wholly in Latin script. That is
# taken as four ranges of code points: U+0001-U+024F (ASCII to Latin Extended-B),
# U+02B0-U+036F (spacing modifier letters and combining marks), U+1E00-U+1EFF (Latin
# Extended Additional) and U+2000-U+206F (general punctuation, such as a typographic
# apostrophe). Any other code point makes it missing. A Chinese, Russian or Greek
# word used to count 0 syllables, and a design matching on n_syllables then reported
# perfect balance. Testing code-point ranges keeps the result independent of the
# engines' Unicode tables, and Unicode's stability policy fixes a character's
# canonical decomposition once it is encoded.
#
# The three patterns name the same code points as .SYLLABLE_SCRIPT, .SYLLABLE_MARKS
# and .SYLLABLE_VOWELS in R_workflow/R/querying.R, escape for escape (\uXXXX here,
# \x{XXXX} there, which ICU reads through stringi), and SYLLABLE_CASES in
# tests/test_dimensions.py and its R twin pin the counts. They also serve the
# subsyllabic segmentation in generation.py.
_SYLLABLE_SCRIPT = re.compile(r"[\u0001-\u024f\u02b0-\u036f\u1e00-\u1eff\u2000-\u206f]*")
_SYLLABLE_MARKS = re.compile(r"[\u0300-\u036f]")
_SYLLABLE_VOWELS = re.compile(r"[aeiouy\u00e6\u00f8\u0131\u0153]+")


def count_syllables(word):
    """An orthographic syllable estimate: the number of maximal vowel runs.

    Counts the maximal runs of Latin vowel letters after decomposing the word and
    setting its diacritics aside, so a vowel counts whatever its accent. The vowels
    of Polish, Czech, Hungarian, Romanian, Turkish, Danish, Norwegian and Vietnamese
    count as those of English, Spanish, French and German do. Hiatus (``idea``
    counts 2) and syllabic consonants such as the Czech l in ``vlk`` and r in ``krk``
    stay undercounted.

    Returns ``None`` for a missing value and for a word holding a character outside
    the Latin script (Chinese, Cyrillic or Greek, for example), where the estimate is
    undefined. ``load_lexicon`` and ``load_pool`` then leave ``n_syllables`` NaN.
    Mirrors count_syllables in R_workflow/R/querying.R.
    """
    # pd.isna covers None, NaN of any float width, pd.NA and NaT, which str() would
    # otherwise turn into a word ("<NA>" counts one syllable).
    if not isinstance(word, str) and pd.api.types.is_scalar(word) and pd.isna(word):
        return None
    w = unicodedata.normalize("NFD", str(word).lower())
    if not _SYLLABLE_SCRIPT.fullmatch(w):
        return None
    return len(_SYLLABLE_VOWELS.findall(_SYLLABLE_MARKS.sub("", w)))


def _syllable_column(words) -> np.ndarray:
    """``count_syllables`` over a column: integers, or floats with NaN where missing.

    A column without a missing count keeps its integer type, so the lexica and
    selections of Latin-script languages are unchanged. The CSV writer renders whole
    floats as integers and NaN as an empty cell, as readr writes R's integer NA.
    """
    counts = [count_syllables(w) for w in words]
    if any(c is None for c in counts):
        return np.array([np.nan if c is None else c for c in counts], dtype=float)
    return np.array(counts, dtype=np.int64)


def _nfc(s):
    """A text key in Unicode Normalization Form C, with None passing through.

    A precomposed letter such as U+00F3 and the base letter followed by a combining
    accent are canonically equivalent, but they compare unequal and differ in length.
    Unnormalised, the two spellings of one word were two candidates, which the matcher
    could place in opposite conditions of one matched set, and a norm or member join
    missed whichever spelling the lexicon did not use. Applied after trimming and
    case-folding, because case mapping does not guarantee normalised output. Mirrors
    .nfc in R_workflow/R/querying.R, which calls ICU through stringi; the two agree on
    every character assigned in both engines' Unicode versions.
    """
    return None if s is None else unicodedata.normalize("NFC", s)


def _nfc_count(values) -> tuple:
    """Normalise a sequence of text keys and say what normalising did.

    Returns the normalised list, the number of values it changed and the number of
    distinct values it merged into another, missing values counting for neither.
    Mirrors .nfc_count in R_workflow/R/querying.R.
    """
    before = [None if v is None or v != v else str(v) for v in values]
    after = [_nfc(v) for v in before]
    present = [i for i, v in enumerate(before) if v is not None]
    changed = sum(before[i] != after[i] for i in present)
    collapsed = len({before[i] for i in present}) - len({after[i] for i in present})
    return after, changed, collapsed


def _nfc_record(changed: int, collapsed: int):
    """The `input_normalisation` record, or None when normalising changed nothing.

    None keeps the record off every frame and datasheet whose input was already NFC,
    which is every shipped one. Mirrors .nfc_record in R_workflow/R/querying.R.
    """
    if not changed and not collapsed:
        return None
    return {"changed": int(changed), "collapsed": int(collapsed)}


def validate_lexicon(df: pd.DataFrame, schema: dict) -> None:
    required = schema["lexicon_schema"]["required"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        cols = ", ".join(f"'{m}'" for m in missing)
        raise ValueError(f"lexsync: lexicon is missing required column(s): {cols}")


def _require_numbers(col: pd.Series, name: str) -> None:
    """Refuse a lexicon column that the shared CSV rule did not read as numbers.

    A value such as "1,000" leaves the whole column text under that rule. pandas' float
    conversion then failed with its own message here, while the R engine took
    as.numeric()'s NA with a warning, so the refusal is spelled out, naming the first
    value that is not a plain decimal number. Mirrors .require_numbers in
    R_workflow/R/querying.R.
    """
    if pd.api.types.is_numeric_dtype(col) and not pd.api.types.is_bool_dtype(col):
        return
    for v in col:
        if isinstance(v, bool):
            bad = "TRUE" if v else "FALSE"
        elif pd.isna(v) or _NUMERIC_CELL.fullmatch(str(v)):
            continue
        else:
            bad = str(v)
        raise ValueError(
            "lexsync: lexicon column '%s' must hold plain decimal numbers, but it holds "
            "'%s'." % (name, bad))


def load_lexicon(path: str, schema: dict, language: str | None = None) -> pd.DataFrame:
    """Load a derived lexicon and give it the inexpensive dimensions.

    ``word`` is trimmed, lower-cased and normalised to Unicode NFC, and duplicates are
    then removed, keeping the first row in file order. When normalisation changed or
    merged any word, ``attrs["input_normalisation"]`` holds ``{"changed",
    "collapsed"}``: the words it rewrote and the duplicate rows it removed. Mirrors
    load_lexicon in R_workflow/R/querying.R.
    """
    df = read_csv_utf8(path)
    validate_lexicon(df, schema)
    # `or {}` at every level: an empty `dimensions:` or `frequency:` key parses to
    # None here and to NULL in R, where `$` chains through it to the default. A
    # default argument only covers an ABSENT key, so the two engines answered the
    # same schema with a column name and an AttributeError.
    freq_col = ((schema.get("dimensions") or {}).get("frequency") or {}).get("column") or "freq_zipf"
    _require_numbers(df[freq_col], freq_col)
    # Filter before coercing: astype(str) renders a missing word as the literal
    # string "nan", which survives both guards below, whereas the R engine (where
    # as.character(NA) stays NA) drops the row. Coercing first would therefore
    # desynchronise the two engines' row counts and shift every subsequent id.
    df = df[df["word"].notna() & df[freq_col].notna()].copy()
    df["word"] = df["word"].astype(str).str.strip().str.lower()
    df = df[df["word"] != ""].copy()
    # NFC before de-duplication, so the two spellings of a word are one word and the
    # first row in file order is the one kept.
    df["word"], changed, collapsed = _nfc_count(df["word"])
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
    df["n_syllables"] = _syllable_column(df["word"])
    df["frequency"] = df[freq_col].astype(float)
    if language is not None:
        df["language"] = language
    df = df.reset_index(drop=True)
    # Read by run_pipeline for the run log and the datasheet.
    record = _nfc_record(changed, collapsed)
    if record:
        df.attrs["input_normalisation"] = record
    return df


def _neighbourhood_reference(lex: pd.DataFrame) -> list:
    """The words a lexicon offers as the reference for the derived dimensions.

    Every word, unless the lexicon carries a ``reference_member`` column, in which case
    the rows marked 1. A lexicon that keeps proper names or acronyms for selection can
    so leave them out of the neighbourhoods. The column must hold 0 or 1 in every row
    and mark at least one word. Mirrors .neighbourhood_reference in
    R_workflow/R/querying.R.
    """
    if "reference_member" not in lex.columns:
        return lex["word"].tolist()
    flags = lex["reference_member"]
    valid = flags.map(lambda v: not isinstance(v, str) and v is not None and v == v
                      and v in (0, 1))
    if not valid.all():
        raise ValueError("lexsync: lexicon column 'reference_member' must hold 0 or 1 for "
                         "every word.")
    members = lex.loc[flags == 1, "word"].tolist()
    if not members:
        raise ValueError("lexsync: lexicon column 'reference_member' marks no word as a "
                         "member of the neighbourhood reference.")
    return members


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
    words; only without one does it fall back to the pool itself. A
    ``reference_member`` column on whichever of the two supplies the reference keeps
    only the rows it marks 1.

    Returns ``{"pool": DataFrame, "reference": list}``. Words are trimmed, lower-cased
    and normalised to Unicode NFC as in ``load_lexicon``, and the pool carries the same
    ``attrs["input_normalisation"]`` record when that changed or merged any word of
    the pool or the lexicon. Mirrors load_pool in R_workflow/R/querying.R.
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
    df = df[df["word"] != ""].copy()
    df["word"], changed, collapsed = _nfc_count(df["word"])
    df = df.drop_duplicates(subset="word")
    if df.empty:
        raise ValueError(
            "lexsync: supplied pool '%s' has no usable rows: it is empty, or every row "
            "is missing 'word'." % path)
    df = (df.assign(_k=df["word"].map(lambda w: w.encode("utf-8")))
            .sort_values("_k").drop(columns="_k").reset_index(drop=True))

    reference = None if lexicon else _neighbourhood_reference(df)
    if lexicon:
        lex = load_lexicon(lexicon, schema, language=language)
        # The lexicon's own normalisation is reported with the pool's, since the run
        # read both.
        lex_record = lex.attrs.get("input_normalisation") or {}
        changed += lex_record.get("changed", 0)
        collapsed += lex_record.get("collapsed", 0)
        reference = _neighbourhood_reference(lex)
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
    df["n_syllables"] = _syllable_column(df["word"])
    if language is not None:
        df["language"] = language
    df["id"] = np.arange(1, len(df) + 1)
    df = df.reset_index(drop=True)
    record = _nfc_record(changed, collapsed)
    if record:
        df.attrs["input_normalisation"] = record
    return {"pool": df, "reference": reference}


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

    Trimmed, case-folded and normalised to NFC, which is what ``load_lexicon`` does
    to ``word``. A missing value stays missing rather than becoming the literal
    string ``"nan"`` that ``astype(str)`` would produce and then happily join on.
    """
    values = [None if v is None or v != v else _nfc(str(v).strip().lower()) for v in x]
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

    The key is trimmed, case-folded and normalised to NFC on *both* sides. Only the
    norm table's side was trimmed and case-folded before, so a lexicon holding
    ``Dog`` matched nothing and the design carried on with an all-``NaN`` dimension.
    Because both engines agreed on that wrong answer, no parity test could have
    caught it. The lexicon's
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
# dimension well and another badly, and an unmatched row becomes a NaN that takes the
# word out of any selection that filters, matches or spans on the column.
#
# Mirrors .norm_specs / .apply_norms in R_workflow/R/querying.R.


def _norm_specs(design: dict):
    """The `norms:` entries, accepting a single bare mapping as well as a sequence."""
    specs = design.get("norms") or []
    return [specs] if isinstance(specs, dict) else list(specs)


def apply_norms(lex: pd.DataFrame, design: dict) -> dict:
    """Join the design's norm tables onto the lexicon, returning it and its record.

    ``normalisation`` in the result counts the norm-table keys that NFC changed and
    the duplicate keys it created, which the join then dropped, summed over the
    tables (see ``_nfc_count``).
    """
    records = []
    changed = collapsed = 0
    for spec in _norm_specs(design):
        path = spec.get("path")
        if not path:
            raise ValueError("lexsync: every entry under `norms:` needs a `path`.")
        if ".." in str(path).replace("\\", "/").split("/"):
            raise ValueError("lexsync: norms path must not contain '..'.")
        on = spec.get("on") or "word"
        cols = list(spec["columns"]) if spec.get("columns") else None
        before = list(lex.columns)
        table = read_csv_utf8(path)
        lex = merge_norms(lex, table, on=on, columns=cols)
        # merge_norms has checked that the key column exists.
        _, n_changed, n_collapsed = _nfc_count(
            [None if v is None or v != v else str(v).strip().lower() for v in table[on]])
        changed += n_changed
        collapsed += n_collapsed
        added = [c for c in lex.columns if c not in before]
        records.append({
            "path": path,
            "sha256": sha256_file(path),
            "on": on,
            "columns": [{"column": c, "n_matched": int(lex[c].notna().sum()),
                         "n_total": int(len(lex))} for c in added],
        })
    return {"lexicon": lex, "provenance": records,
            "normalisation": {"changed": changed, "collapsed": collapsed}}


# Rows of the distance matrix computed at a time: 1,000 rows against a 30,000-word
# reference is a 120 MB block of 32-bit integers.
_NEIGHBOURHOOD_CHUNK = 1000


def add_neighbourhood(df: pd.DataFrame, reference=None, n_old: int = 20) -> pd.DataFrame:
    """Coltheart's N (same-length, single substitution) and OLD20 for each word.

    The Levenshtein distances to the reference come from one rapidfuzz distance matrix
    per block of rows, which took 0.9 s for 500 words against the 30,000-word English
    lexicon where the word-by-word loop it replaces took 19 s. Between two forms of the same
    length a distance of 1 is a single substitution, so N counts the same-length
    reference words at distance 1, as the Hamming distance did. The distances are
    integers, so N and OLD20 are the values the loop gave and the R engine gives.
    """
    words = df["word"].astype(str).tolist()
    ref = list(dict.fromkeys(str(w) for w in (reference if reference is not None else words)))
    ref_len = np.array([len(w) for w in ref])
    n_density = np.zeros(len(words), dtype=int)
    old = np.full(len(words), np.nan)
    for start in range(0, len(words) if ref else 0, _NEIGHBOURHOOD_CHUNK):
        chunk = words[start:start + _NEIGHBOURHOOD_CHUNK]
        dist = process.cdist(chunk, ref, scorer=Levenshtein.distance, dtype=np.int32,
                             workers=-1)
        for j, w in enumerate(chunk):
            row = dist[j]
            n_density[start + j] = int(np.sum((row == 1) & (ref_len == len(w))))
            ld = row[row > 0].astype(float)
            if ld.size:
                k = min(n_old, ld.size)
                old[start + j] = float(np.mean(np.partition(ld, k - 1)[:k]))
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
    a = [_nfc(str(w).strip().lower()) for w in df[prime]]
    b = [_nfc(str(w).strip().lower()) for w in df[target]]
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
    The item id, the condition and the presented fields are normalised to Unicode
    NFC. When that changed any cell, ``attrs["input_normalisation"]`` holds
    ``{"changed", "collapsed"}``, with ``collapsed`` always 0 since no row is removed.
    """
    parts = str(path).replace("\\", "/").split("/")
    if ".." in parts:
        raise ValueError("lexsync: items path must not contain '..'.")
    # The item id, the condition label and the paradigm's presented fields stay text.
    # Typed by their values, a column of response keys such as TRUE and FALSE would
    # become logical, and an `item` column of numbers would lose the zero of '01'. The
    # reader trims every cell and reads a blank, all-whitespace or 'NA' cell as
    # missing, in both engines (see read_csv_utf8).
    df = read_csv_utf8(path, as_character=["item", "condition"] + list(required_fields))
    needed = ["item", "condition"] + list(required_fields)
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"lexsync: items table '{path}' is missing column(s): {', '.join(missing)}.")
    # Missingness is tested before any string coercion: str() would render a missing
    # cell as the literal 'nan', which a blank condition then carries past the
    # hash-key guard downstream.
    for col in needed:
        if df[col].isna().any():
            raise ValueError(
                f"lexsync: the items table has missing value(s) in column '{col}'; "
                "every item, condition and presented field must be filled.")
    df = df.copy()
    # The item id, the condition and the presented text in NFC, as every other text
    # key is, so one item spelt two ways is one set and its text one string. A merged
    # spelling removes no row here, so only the changed cells are counted.
    changed = 0
    for col in dict.fromkeys(needed):
        df[col], n_changed, _ = _nfc_count(df[col].astype(str))
        changed += n_changed
    item_key = df["item"].astype(str)
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
    df = df.reset_index(drop=True)
    record = _nfc_record(changed, 0)
    if record:
        df.attrs["input_normalisation"] = record
    return df


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
