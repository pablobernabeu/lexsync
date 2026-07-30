# -*- coding: utf-8 -*-
"""Robust UTF-8 input/output and provenance helpers.

Mirrors R_workflow/R/io_utils.R. Centralising these guards against the encoding
pitfalls that arise with multilingual stimuli on Windows, and provides the
hashing used by the run log (MD5, matching the R engine).
"""
from __future__ import annotations

import hashlib
import math
import os
import re

import pandas as pd
import yaml


def read_csv_utf8(path: str, as_character=None) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"lexsync: file not found: '{path}'")
    # `as_character` names columns whose type must NOT be inferred. This engine already
    # keeps a single "f" a string, but the R engine's readr reads a column of `f`, `t`,
    # `T` or `F` as LOGICAL, so a design coding its two response keys as f and j had
    # `answer` turned into FALSE there. Forcing the type on both sides makes the
    # agreement structural rather than a coincidence of two readers' heuristics.
    #
    # Treat only "" and "NA" as missing, matching R's readr default. Pandas would
    # otherwise read the real words 'null', 'nan', 'none', 'true' etc. as NaN and
    # silently drop them, diverging from the R engine.
    dtype = {c: str for c in (as_character or [])} or None
    return pd.read_csv(path, encoding="utf-8", keep_default_na=False,
                       na_values=["", "NA"], dtype=dtype)


def _readr_sci(v: float) -> str:
    """A small double in readr's scientific form: a normalised mantissa and an
    unpadded exponent, so 0.0009 becomes "9e-4" and 0.00012 becomes "1.2e-4".

    Built from ``repr``, which is the shortest decimal that round-trips -- the same
    digits readr's own shortest-representation formatter produces -- and then
    re-presented in readr's layout. Python's own scientific form pads the exponent
    ("1e-05"), which is the third way the two engines' CSVs came apart.
    """
    s = repr(float(v))
    neg = s.startswith("-")
    if neg:
        s = s[1:]
    mant, _, exp = s.partition("e")
    e = int(exp) if exp else 0
    ip, _, fp = mant.partition(".")
    all_digits = ip + fp
    significant = all_digits.lstrip("0")
    leading_zeros = len(all_digits) - len(significant)
    # Exponent of the first significant digit, then trailing zeros dropped so the
    # mantissa is as short as the digits allow.
    exp10 = e + len(ip) - 1 - leading_zeros
    digits = significant.rstrip("0") or "0"
    head = digits[0] + ("." + digits[1:] if len(digits) > 1 else "")
    return ("-" if neg else "") + head + "e" + str(exp10)


def _readr_cell(v):
    """One cell rendered as readr renders it.

    pandas and readr agree on almost every value, and the three places they do not
    agree were all silently breaking the package's central claim that the two engines
    write identical artefacts. A byte comparison of all 18 shipped designs found 589
    cells of the first kind, 56 of the second and 8 of the third.

    A whole-number double. readr writes the shortest representation that round-trips,
    so 1.0 becomes "1"; pandas writes repr(), which keeps the ".0".

    A boolean. readr writes TRUE and FALSE; Python writes True and False. R's spelling
    wins because readr offers no way to change it, whereas this writer does, and
    pandas reads either form back correctly.

    A value below 1e-3. readr switches to scientific notation there and pandas does
    not, so a p-value of 0.0009 was written "9e-4" by one engine and "0.0009" by the
    other. The 1e-3 threshold is measured, not assumed: readr 2.2.0 writes 0.001,
    0.0011, 0.0012, 0.0099 and 0.00999 in fixed notation and 0.00099, 0.0009999,
    1e-4, 1.2e-4, 2.5e-5 and 9.99999e-4 in scientific.

    readr's rule at the OTHER end -- where it starts preferring scientific for large
    magnitudes -- resisted a clean characterisation (it writes 1e14 fixed but 1.5e15
    as "15e14"), so it is deliberately not reproduced. No lexsync artefact goes near
    that range: frequencies are Zipf values under 8, counts and durations under 1e6.
    If one ever did, the byte-parity test would fail rather than the difference
    passing unnoticed, which is the outcome that matters.

    Missing values become the empty string, matching ``readr::write_csv(na = "")``.
    """
    if v is None:
        return ""
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, float):
        if v != v:                      # NaN
            return ""
        # A float that is exactly a whole number and small enough to be one: drop the
        # trailing ".0". `is_integer` is exact, and 2**53 is where consecutive integers
        # stop being representable, beyond which repr is the honest rendering anyway.
        if v.is_integer() and abs(v) < 2 ** 53:
            return str(int(v))
        if v != 0 and abs(v) < 1e-3:
            return _readr_sci(v)
        return repr(v)
    return str(v)


def write_csv_utf8(x: pd.DataFrame, path: str) -> str:
    # Pin LF: pandas defaults `lineterminator` to os.linesep, so the same selection
    # would be stamped with a different SHA-256 on Windows than on Linux. The
    # datasheet advertises those digests as provenance, so they must depend on the
    # content alone. LF is also readr's terminator on every platform, keeping the
    # two engines to one convention.
    #
    # Cells are rendered through _readr_cell first, then written as text, because
    # pandas' own float and bool formatting differs from readr's in two ways that made
    # the two engines' CSVs differ byte for byte (see _readr_cell). Converting to
    # strings here and letting the csv writer quote them keeps pandas' quoting and
    # escaping, which already match readr's.
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    rendered = pd.DataFrame({c: [_readr_cell(v) for v in x[c]] for c in x.columns},
                            columns=x.columns)
    rendered.to_csv(path, index=False, encoding="utf-8", lineterminator="\n")
    return path


# ---- Reproducible reductions -----------------------------------------------
# A sum, mean and variance that give the same bits in the R and Python engines.
#
# This is not pedantry; it was a live bug. Two designs' reported means differed between
# the engines in the last decimal place the descriptives publish -- 1.447 against 1.448
# -- because numpy sums pairwise while R's mean() uses a two-pass long-double
# algorithm, and the true value happened to sit on a rounding boundary. Summing 20000
# identical doubles was measured to give three different answers across R's sum(),
# math.fsum, numpy's pairwise sum and a naive loop, so no language's built-in reduction
# can be relied on for a cross-engine artefact.
#
# Neumaier compensated summation is used instead, written out in plain double
# arithmetic in both engines. Every operation is +, -, abs or a comparison, and
# IEEE-754 requires + and - to be correctly rounded, so the two engines execute the
# same sequence of exactly-specified operations and cannot disagree. That is an
# argument rather than a measurement, which is what relying on numpy's pairwise
# ordering amounted to.
#
# math.fsum would also be exactly rounded, but it is not what the R engine can run:
# the point is that BOTH engines execute this same algorithm. Mirrors io_utils.R.


def _exact_sum(x) -> float:
    s = 0.0
    comp = 0.0
    for v in x:
        v = float(v)
        t = s + v
        # The larger magnitude keeps its low bits; the smaller one's are what get lost,
        # so the correction is computed from whichever term is smaller.
        comp += ((s - t) + v) if abs(s) >= abs(v) else ((v - t) + s)
        s = t
    return s + comp


def _exact_mean(x):
    vals = [float(v) for v in x]
    if not vals:
        return float("nan")
    return _exact_sum(vals) / len(vals)


def _exact_var(x):
    """Two-pass variance: the mean first, then the compensated sum of squared
    deviations. The textbook one-pass form (sum of squares minus n times the squared
    mean) is catastrophically cancelling for data far from zero and would differ
    between engines by far more than a last bit."""
    vals = [float(v) for v in x]
    n = len(vals)
    if n < 2:
        return float("nan")
    m = _exact_mean(vals)
    return _exact_sum([(v - m) * (v - m) for v in vals]) / (n - 1)


def _exact_sd(x):
    v = _exact_var(x)
    # sqrt is correctly rounded under IEEE-754, so it adds no divergence.
    return v if v != v else math.sqrt(v)


def hash_file(path: str):
    """MD5 digest of a file, for provenance logging (matches the R engine)."""
    if not os.path.exists(path):
        return None
    digest = hashlib.md5()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_file(path: str):
    """SHA-256 digest of a file, the stronger fingerprint used by the datasheet."""
    if not path or not os.path.exists(path):
        return None
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()




def _is_continuous(design: dict) -> bool:
    """Is this design a continuous (non-dichotomised) selection?

    One predicate rather than four copies of the same expression. It was repeated
    verbatim in run_pipeline.py, datasheet.py and both R twins, which is how a
    ``continuous:`` block under ``items.source: table`` came to be silently inert in
    all four places at once. ``generate`` stays excluded deliberately: a continuous
    block there would push a word/pseudoword frame into the selector. Must stay
    identical to .is_continuous in R_workflow/R/io_utils.R.
    """
    src = ((design or {}).get("items") or {}).get("source", "corpus")
    if design.get("continuous") and src == "generate":
        raise ValueError(
            "lexsync: a 'continuous' block cannot be combined with items.source 'generate'.")
    return bool(design.get("continuous")) and src in ("corpus", "table")

def _key_part(x) -> str:
    """Render one component of a hash key.

    Never interpolate a number directly: R prints 42.0 as "42" and Python as
    "42.0", and a pandas column silently promoted to float64 by a single missing
    value would otherwise change every digest and so every realised duration.
    Integral values go through %d in both engines. Must stay identical to
    .key_part in R_workflow/R/io_utils.R.
    """
    if isinstance(x, bool):
        return str(x)
    if isinstance(x, (int, float)):
        f = float(x)
        if f == f and f not in (float("inf"), float("-inf")) and f.is_integer():
            return "%d" % int(f)
        return "%.17g" % f
    return str(x)


def hash_unit(key: str) -> float:
    """A uniform variate in [0, 1) derived from a keyed SHA-256 digest.

    This is how lexsync gets anything that looks stochastic without a generator:
    jittered durations, and any future search that needs a candidate order. The
    scheme is chosen for exact reproducibility across the two engines rather than
    for elegance, and every part of it is load-bearing.

    Thirteen hex digits give a 52-bit integer, which a double represents exactly;
    dividing by 2**52 is exact because the divisor is a power of two. The result
    is therefore the same bits in R and Python rather than merely close. Fourteen
    digits or more would round up to exactly 1.0, and ``lo + floor(u * n)`` would
    then silently return ``hi + 1``.

    Only +, -, * and / are used downstream. IEEE-754 mandates those to be
    correctly rounded, so they agree on any conforming platform; ``exp``, ``log``
    and ``**`` do not, and were measured to differ between R and Python by one
    unit in the last place. Must stay identical to hash_unit() in
    R_workflow/R/io_utils.R.
    """
    h = hashlib.sha256(str(key).encode("utf-8")).hexdigest()
    return int(h[:13], 16) / 4503599627370496


def hash_int_range(key: str, lo: int, hi: int) -> int:
    """A uniform integer in [lo, hi], both ends included, from a keyed digest."""
    lo, hi = int(lo), int(hi)
    if hi < lo:
        raise ValueError("lexsync: jitter range must have hi >= lo.")
    return lo + int(math.floor(hash_unit(key) * (hi - lo + 1)))

def slugify(*parts) -> str:
    """Short, filesystem-safe slug; keeps generated names within MAX_PATH."""
    s = "_".join(str(p) for p in parts)
    s = re.sub(r"[^A-Za-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_").lower()


def read_config(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"lexsync: configuration not found: '{path}'")
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


# Control characters (incl. tab/newline/carriage return) are rejected in stimulus
# text: presented strings are single-line, and forbidding them stops a crafted
# item from corrupting the generated loop table or experiment scripts.
_CTRL_RE = re.compile(r"[\x00-\x1f\x7f]")


def clean_field(value, field: str = "field", max_len: int = 1000) -> str:
    """Validate a single stimulus value for safe inclusion in generated files.

    Rejects control characters and over-long strings; returns the value as a
    plain string. Commas and quotation marks are allowed (they are written as
    data into a properly quoted CSV that the experiment reads at run time, never
    interpolated into generated code), so ordinary sentences pass unchanged.
    """
    s = str(value)
    if _CTRL_RE.search(s):
        raise ValueError(f"lexsync: stimulus '{field}' contains control characters: {s!r}")
    if len(s) > max_len:
        raise ValueError(f"lexsync: stimulus '{field}' exceeds {max_len} characters.")
    return s
