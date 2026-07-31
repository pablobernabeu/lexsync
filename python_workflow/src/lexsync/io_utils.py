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
from decimal import Decimal

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


# Where readr leaves fixed notation for large magnitudes, measured the same way the 1e-3
# threshold at the other end was: readr 2.2.0 writes 5e14, 9.99e14 and 999999999999999
# fixed, and 1e15, 1.5e15 and 1.25e15 in scientific.
_READR_BIG = 1e15
# Above 2**49 consecutive doubles are more than 0.1 apart, so a single decimal digit can
# round-trip -- and two different ones can round-trip to the SAME double. Below that they
# cannot, so the shortest form is unique and both engines must print it.
_READR_TIE = float(2 ** 49)


def _shortest_digits_ambiguous(v: float) -> bool:
    """Whether more than one decimal string of the shortest length round-trips to ``v``.

    ``repr`` gives *a* shortest round-tripping decimal, not *the* one: where the gap
    between neighbouring doubles exceeds the last digit's place value, the string one
    step up or down parses back to the same double, and R and Python then disagree about
    which to print. readr writes 1000000000000000.25 as "1000000000000000.3" and Python
    gives "1000000000000000.2"; both are correct and neither can be reformatted into the
    other, because the digits themselves differ. Detecting the tie exactly beats refusing
    a magnitude wholesale, since 562949953421312.5 is above the threshold and has only
    one shortest form.
    """
    s = repr(abs(v))
    if "e" in s or "." not in s:
        return False
    step = Decimal(1).scaleb(-len(s.partition(".")[2]))
    d = Decimal(s)
    return float(d + step) == abs(v) or float(d - step) == abs(v)


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

    A value at or above 1e15 is refused rather than written. readr leaves fixed notation
    there, and its layout beyond it could not be reproduced: it writes 1.5e16 as "15e15"
    with an integer mantissa, the largest double as "17976931348623157e292", but the
    double nearest 5e22 as "4.9999999999999996e+22", a padded form with more digits than
    round-tripping needs. No rule fitted all three. Nothing lexsync computes goes near
    that range -- frequencies are Zipf values under 8, counts and durations under 1e6 --
    but a joined norm table, a supplied pool or an item table may carry any column the
    user likes, and those columns are written straight into the stimuli CSV. Leaving the
    range unhandled meant the guarantee held for the shipped designs, which the
    byte-parity test covers, and failed silently for the user's own data, which nothing
    covers. An error naming the value is the honest outcome.

    Missing values become the empty string, matching ``readr::write_csv(na = "")``.
    """
    if v is None:
        return ""
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, float):
        if v != v:                      # NaN
            return ""
        if abs(v) >= _READR_BIG:
            raise ValueError(
                "lexsync: %r is too large to write identically from both engines. Above "
                "1e15 readr's number format could not be reproduced exactly, so the R "
                "and Python CSVs would differ with nothing to signal it. Scale the "
                "column, or carry it as text." % v)
        if abs(v) >= _READR_TIE and not v.is_integer() and _shortest_digits_ambiguous(v):
            raise ValueError(
                "lexsync: %r has more than one shortest decimal form, and the R and "
                "Python engines print different ones, so the two CSVs would differ with "
                "nothing to signal it. Round the column, or carry it as text." % v)
        # A float that is exactly a whole number: drop the trailing ".0". Below 1e15
        # every such double is well under 2**53, so int() is exact.
        if v.is_integer():
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


# ---- One decimal rounder, shared by both engines ---------------------------
#
# No pairing of built-ins works. Measured over 210,000 values including every 3-dp
# halfway case in range: Python's builtin round() disagrees with R's round(), numpy's
# round() disagrees with both, and even Python's "%.3f" disagrees with R's
# sprintf("%.3f") on 274 of them, because R's delegates to the platform C library while
# this one is correctly rounded. So a value rounded for an artefact cannot be handed to
# any language's own rounder.
#
# This one is defined by its arithmetic instead: scale, truncate toward zero, then step
# away from zero when the remainder reaches a half. Every operation is *, -, /, trunc,
# abs or a comparison, all of which IEEE-754 either mandates correctly rounded or makes
# exact, so both engines compute the same double from the same input by construction.
#
# It rounds the SCALED double rather than the true decimal value, which for a tie that
# is not exactly representable is a choice rather than a theorem. That is the same
# trade-off the balance optimiser's quantisation already makes, and it is the right way
# round: reproducible across engines matters more here than agreeing with what a
# calculator would say about a value that was never exactly a half.
# Must stay identical to .round_dp in R_workflow/R/io_utils.R.


def _round_dp(x, dp: int) -> float:
    v = float(x)
    if v != v or v in (float("inf"), float("-inf")):
        return v
    p = 10.0 ** dp
    y = v * p
    t = math.trunc(y)
    r = y - t
    # The step is away from zero, so a negative value moves down, not up.
    adj = (1 if y > 0 else -1) if abs(r) >= 0.5 else 0
    return (t + adj) / p


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

    Never interpolate a number directly: R prints 42.0 as "42" and Python as "42.0",
    and a pandas column silently promoted to float64 by a single missing value would
    otherwise change every digest and so every realised duration.

    A component that cannot be rendered identically in both engines must never be
    silently hashed. Measured: a missing value rendered "nan" here and "NA" in R,
    True/False against TRUE/FALSE, inf against Inf. A blank ``condition`` cell is a
    routine data error that neither reader rejects, and it produced a DIFFERENT trial
    order in each engine -- reproducibly, and with nothing to signal it.

    Raising beats picking a spelling. A missing condition, set or list is always a data
    error, and a reproducible order computed over a meaningless key is worse than a
    stop. Booleans do get a pinned spelling, because they are legitimate: the spelling
    is fixed to R's here rather than left to each language.

    Must stay identical to .key_part in R_workflow/R/io_utils.R.
    """
    if x is None:
        raise ValueError(
            "lexsync: a hash-key component is missing, so the trial order cannot be "
            "made identical across engines. Check the items table for a blank "
            "condition, set or list cell.")
    if isinstance(x, bool):
        return "TRUE" if x else "FALSE"
    if isinstance(x, (int, float)):
        f = float(x)
        if f != f:
            raise ValueError(
                "lexsync: a hash-key component is missing, so the trial order cannot be "
                "made identical across engines. Check the items table for a blank "
                "condition, set or list cell.")
        if f in (float("inf"), float("-inf")):
            raise ValueError(
                "lexsync: a hash-key component is not finite, so it cannot be keyed.")
        # The integer bound matters: R's as.integer() beyond it yields NA, which would
        # put an empty component into the key.
        if f.is_integer() and abs(f) <= 2147483647:
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
