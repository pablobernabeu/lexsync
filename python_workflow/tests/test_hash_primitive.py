"""The keyed-hash primitive, which every deterministic-but-varying value rests on.

lexsync draws no random numbers. Anything that looks stochastic — a jittered
duration, and any future search needing a candidate order — is a pure function of
a SHA-256 digest of a key string. `hash_unit` turns that digest into a uniform
variate in [0, 1), and it has to give the *same bits* in R and Python or the two
engines will select different stimuli.

The golden digests below were frozen only after both engines were compared
bit-for-bit over 20,005 keys, including accented Spanish and CJK strings and the
empty key. R_workflow/tests/testthat/test-hash-primitive.R computes the same
digests independently, so the two suites fail together if either engine drifts.

The scheme's fragile parts, each of which this file pins:
  * 13 hex digits, not 14. Fourteen rounds up to exactly 1.0, and the integer
    mapping would then return hi + 1 with no test noticing.
  * Division by 2**52, a power of two, so the result is exact rather than close.
  * Only +, -, * and / downstream. IEEE-754 mandates those correctly rounded;
    exp, log and ** differ between R and Python by one unit in the last place.
"""
import hashlib
import struct

import pytest

from lexsync.io_utils import hash_int_range, hash_unit

TWO52 = 4503599627370496


def _bits(x: float) -> str:
    """The IEEE-754 bit pattern, so a one-bit difference cannot hide in rounding."""
    return struct.pack("<d", x)[::-1].hex()


def test_the_variate_lies_strictly_inside_the_unit_interval():
    values = [hash_unit(f"sweep|{i}") for i in range(5000)]
    assert all(0.0 <= u < 1.0 for u in values)
    # 13 hex digits cap the variate one ulp below 1, which is what stops
    # lo + floor(u * n) from ever returning hi + 1.
    assert max(values) <= 1.0 - 1.0 / TWO52


def test_known_keys_including_non_ascii():
    # These exact values are reproduced by the R suite from R's own digest call.
    assert _bits(hash_unit("sweep|0")) == "3fcd8a2fd4c97bd0"
    assert hash_int_range("42|0|A|1|niño_corazón", 200, 800) == 302
    assert hash_int_range("42|0|A|1|北京大学汉字", 200, 800) == 209


def test_the_integer_mapping_respects_both_bounds():
    for lo, hi in [(0, 1), (1, 3), (200, 800), (0, 0), (-5, 5)]:
        seen = {hash_int_range(f"k|{i}", lo, hi) for i in range(3000)}
        assert min(seen) >= lo and max(seen) <= hi
    # A degenerate range is not an error; it is a constant.
    assert hash_int_range("anything", 7, 7) == 7
    with pytest.raises(ValueError, match="hi >= lo"):
        hash_int_range("k", 10, 2)


def test_the_variate_stream_matches_the_r_engine():
    stream = "|".join(_bits(hash_unit(f"sweep|{i}")) for i in range(20000))
    assert (hashlib.sha256(stream.encode("utf-8")).hexdigest()
            == "8c1dabf515645b54c85e10529275bf0920ba965708f0d115a9c5a3b810d800f3")


def test_the_integer_stream_matches_the_r_engine():
    stream = "|".join(str(hash_int_range(f"sweep|{i}", 200, 800)) for i in range(20000))
    assert (hashlib.sha256(stream.encode("utf-8")).hexdigest()
            == "170c356c58314548ca0d2bffc31ac4da56f960d5037dc05ca78234dcb045ad97")


def test_distinct_keys_do_not_collide_in_practice():
    """Not a uniformity proof, only a guard against a broken derivation.

    A truncated or constant digest would show up immediately as a collapsed
    range, which is the failure worth catching cheaply.
    """
    values = {hash_unit(f"sweep|{i}") for i in range(20000)}
    assert len(values) == 20000
