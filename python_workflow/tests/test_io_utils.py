import re
import struct

import pandas as pd
import pytest

from lexsync.io_utils import (
    _is_continuous,
    clean_field,
    read_config,
    read_csv_utf8,
    sha256_file,
    slugify,
    write_csv_utf8,
)

# The R engine (readr) writes LF on every platform, so LF is the cross-engine
# contract. test-io_utils.R pins these same bytes and this same digest.
EXPECTED_BYTES = b"word,condition\ncat,high\ndog,low\n"
EXPECTED_SHA256 = "8084f4888fa65455ee56e7eca2954b07b114f5b962bb78c6e8c73c9928e66ad5"


def _frame():
    return pd.DataFrame({"word": ["cat", "dog"], "condition": ["high", "low"]})


def test_write_csv_utf8_pins_lf_on_every_platform(tmp_path):
    path = write_csv_utf8(_frame(), str(tmp_path / "s.csv"))
    assert open(path, "rb").read() == EXPECTED_BYTES


def test_write_csv_utf8_digest_is_platform_independent(tmp_path):
    # The datasheet advertises this digest as provenance, so it must be fixed by
    # the content alone -- not by the os.linesep of the machine that ran it.
    path = write_csv_utf8(_frame(), str(tmp_path / "s.csv"))
    assert sha256_file(path) == EXPECTED_SHA256


def test_write_csv_utf8_round_trips(tmp_path):
    # read_csv_utf8 gives text columns the object dtype under every pandas, so the
    # frame read back is compared with object columns. pandas 3 builds _frame() with
    # its own "str" dtype, and DataFrame.equals compares dtypes as well as values.
    path = write_csv_utf8(_frame(), str(tmp_path / "nested" / "s.csv"))
    assert read_csv_utf8(path).equals(_frame().astype(object))


def test_read_csv_utf8_keeps_words_that_look_like_missing_values(tmp_path):
    path = tmp_path / "s.csv"
    path.write_bytes(b"word,gloss\nnull,x\nnan,y\n,z\nNA,w\n")
    out = read_csv_utf8(str(path))
    assert list(out["word"][:2]) == ["null", "nan"]
    assert out["word"][2:].isna().all()


# The datasheet's numbers used to go through format specifications such as :.3f,
# which round correctly here but differently from R's sprintf(), which hands the
# rounding to the platform's C library: R 4.6.1 on Windows printed 0.0825 at three
# places as "0.082" and 0.165 at two as "0.16". _fmt_dp prints the integer that
# _round_dp's own arithmetic gives, so no printf rounds anything. test-io_utils.R
# pins the same strings for .fmt_dp.
def test_fmt_dp_rounds_half_away_from_zero_without_a_printf():
    from lexsync.io_utils import _fmt_dp, _round_dp
    assert _fmt_dp(0.0825, 3) == "0.083"
    assert _fmt_dp(0.1125, 3) == "0.113"
    assert _fmt_dp(0.165, 2) == "0.17"
    assert _fmt_dp(0.0005, 4) == "0.0005"
    assert _fmt_dp(-0.0825, 3) == "-0.083"
    assert _fmt_dp(-0.465, 2) == "-0.47"
    assert _fmt_dp(1, 4) == "1.0000"
    assert _fmt_dp(3.05, 3) == "3.050"
    assert _fmt_dp(12.5, 0) == "13"
    # A value that rounds to zero never prints as "-0".
    assert _fmt_dp(-0.0004, 3) == "0.000"
    # The stored record keeps four places, so a display at three rounds twice:
    # 0.08249 is stored as 0.0825 and shown as 0.083. This is the documented residual.
    assert _fmt_dp(_round_dp(0.08249, 4), 3) == "0.083"
    # Missing values print the placeholder.
    assert _fmt_dp(None, 2) == "--"
    assert _fmt_dp(float("nan"), 2) == "--"
    assert _fmt_dp(None, 2, na="n/a") == "n/a"
    assert [_fmt_dp(v, 2) for v in (float("inf"), float("-inf"))] == ["Inf", "-Inf"]


# A setting such as an alpha, a bound or a tolerance k, and the confidence level an
# alpha gives, are printed with %g once the shared rounder has taken them to six
# places, so 1 - 2 * 0.05 prints as 90 and a bound read as 1.0 or 1 prints as 1 in
# both engines. test-io_utils.R pins the same strings for .fmt_g.
def test_fmt_g_prints_a_setting_without_trailing_digits():
    from lexsync.io_utils import _fmt_g
    assert _fmt_g((1 - 2 * 0.05) * 100) == "90"
    assert _fmt_g((1 - 2 * 0.005) * 100) == "99"
    assert _fmt_g((1 - 2 * 0.001) * 100) == "99.8"
    assert [_fmt_g(v) for v in (0.05, 0.5, 1.0, 1, 1.5, 2.0)] == [
        "0.05", "0.5", "1", "1", "1.5", "2"]



def _csv_fixture():
    """The CSV-reading fixture, built row by row exactly as test-io_utils.R builds it.

    1,200 rows, so that a reader guessing types from the first 1,000 sees only numbers
    in `late` and misses the 'n/a' at row 1,101.
    """
    lines = ["word , freq_zipf,pos,tf,flag,grouped,late,date,miss,n,num,inf"]
    for i in range(1, 1201):
        lines.append(",".join([
            "w%04d" % i,
            " 3.25 " if i == 1 else "4.5",
            {1: '" NOUN "', 2: "\tverb\t", 3: ""}.get(i, "noun"),
            "T" if i % 2 else "F",
            "" if i == 4 else ("TRUE" if i % 2 else "False"),
            '"1,000"' if i == 1 else "2",
            "n/a" if i == 1101 else str(i),
            "2026-10-02",
            {1: " NA ", 2: '"NA"'}.get(i, "1.5"),
            str(i),
            {1: "+1.5", 2: ".5", 3: "5.", 4: "-2E-2", 5: "1e3"}.get(i, "0"),
            "Inf" if i == 1 else "1",
        ]))
    return ("\n".join(lines) + "\n").encode("ascii")


def _kind(col):
    """A column's type as the cross-engine contract names it."""
    if col.dtype == "int64":
        return "integer"
    if col.dtype == "float64":
        return "number"
    if col.dtype == bool or all(isinstance(v, bool) for v in col.dropna()):
        return "logical"
    return "text"


def _cells(col, n):
    return [None if pd.isna(v) else v for v in col[:n]]


# The same fixture, types and values are pinned by "one CSV fixture reads the same in
# both engines" in test-io_utils.R.
def test_one_csv_fixture_reads_the_same_in_both_engines(tmp_path):
    path = tmp_path / "f.csv"
    path.write_bytes(_csv_fixture())
    out = read_csv_utf8(str(path))
    assert list(out.columns) == ["word", "freq_zipf", "pos", "tf", "flag", "grouped",
                                 "late", "date", "miss", "n", "num", "inf"]
    assert {c: _kind(out[c]) for c in out.columns} == {
        "word": "text", "freq_zipf": "number", "pos": "text", "tf": "text",
        "flag": "logical", "grouped": "text", "late": "text", "date": "text",
        "miss": "number", "n": "integer", "num": "number", "inf": "text"}
    assert len(out) == 1200
    assert _cells(out["freq_zipf"], 2) == [3.25, 4.5]
    assert _cells(out["pos"], 4) == ["NOUN", "verb", None, "noun"]
    assert _cells(out["tf"], 2) == ["T", "F"]
    assert _cells(out["flag"], 5) == [True, False, True, None, True]
    assert _cells(out["grouped"], 2) == ["1,000", "2"]
    assert out["late"][1100] == "n/a" and out["late"][0] == "1"
    assert out["date"][0] == "2026-10-02"
    assert _cells(out["miss"], 3) == [None, None, 1.5]
    assert list(out["n"]) == list(range(1, 1201))
    assert _cells(out["num"], 6) == [1.5, 0.5, 5.0, -0.02, 1000.0, 0.0]
    assert _cells(out["inf"], 2) == ["Inf", "1"]


def test_read_csv_utf8_keeps_as_character_columns_as_trimmed_text(tmp_path):
    path = tmp_path / "f.csv"
    path.write_bytes(_csv_fixture())
    out = read_csv_utf8(str(path), as_character=["n", "flag", "freq_zipf", "absent"])
    assert _cells(out["n"], 2) == ["1", "2"]
    assert _cells(out["flag"], 4) == ["TRUE", "False", "TRUE", None]
    assert _cells(out["freq_zipf"], 2) == ["3.25", "4.5"]
    assert "absent" not in out.columns


def test_read_csv_utf8_refuses_a_column_name_given_twice(tmp_path):
    # Trimming the header can make two names one, and either engine's reader would
    # then rename one of them by its own rule, so neither would know which is `word`.
    path = tmp_path / "f.csv"
    path.write_bytes(b"word,freq_zipf,word \ncat,4,dog\n")
    with pytest.raises(ValueError, match="names column 'word' more than once"):
        read_csv_utf8(str(path))


def test_read_csv_utf8_names_an_empty_header_cell_by_its_position(tmp_path):
    path = tmp_path / "f.csv"
    path.write_bytes(b"word,,freq_zipf,\ncat,x,4,\n")
    out = read_csv_utf8(str(path))
    assert list(out.columns) == ["word", "...2", "freq_zipf", "...4"]


def test_read_csv_utf8_reads_an_empty_file_as_no_columns(tmp_path):
    path = tmp_path / "f.csv"
    path.write_bytes(b"")
    out = read_csv_utf8(str(path))
    assert list(out.columns) == [] and len(out) == 0


# Pins the same bits as "read_csv_utf8 parses a number to the double both engines
# reach" in test-io_utils.R. R's own parsers miss the nearest double on the first five:
# as.numeric() on the first and third, readr on the second, fourth and fifth. The
# eighth to twelfth defeated the as.numeric() fallback the R engine once used beyond 15
# significant digits, on x86-64, and the fourth defeated it on Apple Silicon, where
# long double is no wider than double. The last three are a decimal just above the
# largest double, which rounds down to it, the next 17-digit decimal, which rounds to
# inf, and a decimal just above half the smallest subnormal, which rounds up to that
# subnormal. A negative zero is read as zero, which both writers print as "0".
NUMBER_BITS = [
    ("0.586135918132", "3fe2c1a01cec6975"),
    ("50.768212762897100", "40496254cbba81a5"),
    ("2.91e-11", "3dbffeebfc8b81b5"),
    ("0.12345678901234567", "3fbf9add3746f65e"),
    ("1e-400", "0000000000000000"),
    ("-0", "0000000000000000"),
    ("-0.00", "0000000000000000"),
    ("4720.053418320736", "40b2700dacd2b491"),
    ("10e125", "5a17a2ecc414a03f"),
    ("5332246559989354200684", "447210fc94adb741"),
    ("7.3230939350514581251e+14", "4304d0408a1fdbcf"),
    ("1.7976931348623158e308", "7fefffffffffffff"),
    ("1.7976931348623159e308", "7ff0000000000000"),
    ("2.4703282292062328e-324", "0000000000000001"),
]


def test_read_csv_utf8_parses_a_number_to_the_double_both_engines_reach(tmp_path):
    path = tmp_path / "f.csv"
    path.write_bytes(("x\n" + "\n".join(s for s, _ in NUMBER_BITS) + "\n").encode("ascii"))
    out = read_csv_utf8(str(path))
    assert out["x"].dtype == "float64"
    assert [struct.pack(">d", v).hex() for v in out["x"]] == [b for _, b in NUMBER_BITS]
    path.write_bytes(b"z\n-0.00\n1.5\n")
    written = tmp_path / "w.csv"
    write_csv_utf8(read_csv_utf8(str(path)), str(written))
    assert written.read_bytes() == b"z\n0\n1.5\n"


def test_clean_field_rejects_control_characters():
    with pytest.raises(ValueError, match="control characters"):
        clean_field("cat\ndog", "word")


def test_clean_field_allows_commas_and_quotes():
    assert clean_field('the "big" cat, asleep', "word") == 'the "big" cat, asleep'


def test_slugify_is_lowercase_and_path_safe():
    assert slugify("En Lexdec", "English!") == "en_lexdec_english"


# Pins the same contract as "slugify folds case whatever the locale" in the R
# engine's test-io_utils.R, where base tolower() folded "I" to the dotless "i"
# under a Turkish locale and wrote the design's artefacts under a name this
# engine never produces. str.lower() is already locale-invariant; the assertion
# is what the R engine is now held to.
def test_slugify_is_locale_invariant():
    assert slugify("STUDY_I") == "study_i"
    assert slugify("En Lexdec", "English!").isascii()


def test_read_config_refuses_a_duplicated_mapping_key(tmp_path):
    # yaml.safe_load keeps the last value for a repeated key, silently; the R
    # engine's yaml::read_yaml() rejects the key by its libyaml parser default,
    # so this engine accepted a config the R engine refused. The messages differ
    # because R's comes from the C parser; behavioural parity -- both engines
    # refuse -- is the contract, and test-io_utils.R pins the R side of it.
    path = tmp_path / "dup.yaml"
    path.write_text("name: a\nname: b\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate mapping key 'name'"):
        read_config(str(path))
    # A key repeated in a NESTED mapping must be caught too, not just at the top.
    path.write_text("items:\n  source: table\n  source: pool\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate mapping key 'source'"):
        read_config(str(path))
    # And an ordinary config still loads, so the strict loader costs nothing.
    path.write_text("name: a\nitems:\n  source: pool\n", encoding="utf-8")
    assert read_config(str(path)) == {"name": "a", "items": {"source": "pool"}}


# The two key vocabularies, joined by newlines and hashed. test-io_utils.R pins the
# same digests for .DESIGN_KEYS and .SCHEMA_KEYS, so a key added to one engine only
# fails both suites.
DESIGN_KEYS_SHA256 = "85bb0bc2e376483bf5c818469cbc9e9446f952d5095d64c69e9e19086c5ee357"
SCHEMA_KEYS_SHA256 = "a62e1a4f7cc410ef37d511e9758107b414bedec2c7ab008704c57171fc7f0e5c"


def test_the_key_vocabularies_agree_across_engines():
    import hashlib

    from lexsync.design import DESIGN_KEYS, SCHEMA_KEYS
    for keys, digest in ((DESIGN_KEYS, DESIGN_KEYS_SHA256), (SCHEMA_KEYS, SCHEMA_KEYS_SHA256)):
        assert hashlib.sha256("\n".join(keys).encode("utf-8")).hexdigest() == digest


def _valid_design(**extra):
    return {"name": "kt", "language": "english", "conditions": [
        {"name": "high", "define_by": {"frequency": [5, 7]}},
        {"name": "low", "define_by": {"frequency": [1, 3]}}],
        "match_on": ["length"], **extra}


def test_a_key_near_a_known_one_is_refused_and_any_other_is_noted():
    """One edit is a typo for a key of up to five characters and two for a longer
    one; a transposition counts as one edit. `notes` is two edits from `norms` and so
    is only noted. Pinned identically in test-io_utils.R."""
    from lexsync.design import validate_design
    refusals = {
        "nmae": "'nmae' (did you mean 'name'?)",
        "langauge": "'langauge' (did you mean 'language'?)",
        "fonts": "'fonts' (did you mean 'font'?)",
    }
    for key, tail in refusals.items():
        with pytest.raises(ValueError, match=re.escape("lexsync: unknown design key " + tail)):
            validate_design(_valid_design(**{key: "x"}), {})
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: unknown design key 'counterbalance.list' "
            "(did you mean 'counterbalance.lists'?)")):
        validate_design(_valid_design(counterbalance={"list": 2}), {})
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: unknown design key 'conditions[2].nmae' "
            "(did you mean 'conditions[2].name'?)")):
        validate_design({"name": "kt", "language": "english", "match_on": ["length"],
                         "conditions": [{"name": "a"}, {"nmae": "b"}]}, {})
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: unknown schema key 'matchin' (did you mean 'matching'?)")):
        validate_design(_valid_design(), {"matchin": {}})
    # The schema may set counterbalance.incomplete, which the counterbalancing reads,
    # so it is neither refused nor noted as ignored.
    assert validate_design(_valid_design(), {"counterbalance": {"incomplete": "error"}}) == []
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: unknown schema key 'counterbalance.incomplet' "
            "(did you mean 'counterbalance.incomplete'?)")):
        validate_design(_valid_design(), {"counterbalance": {"incomplet": "error"}})
    notes = validate_design(_valid_design(notes="x", date="May", x_owner="pb",
                                          events=[{"type": "blank", "duration_ms": 100,
                                                   "colour": "red"}]),
                            {"x_site": "Oxford", "comment": "y"})
    assert notes == [
        "lexsync: design key '%s' is not read by lexsync and is ignored; a later release "
        "will refuse it. Put annotations in `description` or a key beginning `x_`." % k
        for k in ("notes", "date", "events[1].colour")] + [
        "lexsync: schema key 'comment' is not read by lexsync and is ignored; a later "
        "release will refuse it. Put annotations in `description` or a key beginning `x_`."]


def test_the_tie_break_key_is_read_in_a_design_and_a_schema():
    """matching.tie_break is a setting in both files, so neither run notes it as
    ignored. Pinned identically in test-io_utils.R."""
    from lexsync.design import validate_design
    assert validate_design(_valid_design(matching={"tie_break": "hash"}),
                           {"matching": {"tie_break": "bytes"}}) == []


def test_a_response_events_from_is_a_key_lexsync_reads():
    """`from` on a response event says where its window opens, so it is neither refused
    nor noted, and a value other than onset or offset is refused before anything is
    written. Pinned identically in test-io_utils.R."""
    from lexsync.design import validate_design
    events = [{"type": "text", "content": "{word}", "duration_ms": 800},
              {"type": "response", "keys": ["f", "j"], "from": "offset"}]
    assert validate_design(_valid_design(events=events), {}) == []
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: event 2 gives `from: later`, but a response event takes from: onset "
            "or from: offset.")):
        validate_design(_valid_design(events=[events[0], dict(events[1], **{"from": "later"})]),
                        {})


def test_repeated_and_blank_names_are_judged_alike_in_both_engines():
    """The first entry that repeats an earlier name is the one reported, as R's
    duplicated() reports it. Only spaces, tabs and line breaks make a name blank, as
    for R's trimws(): a no-break space is a name, and a vertical tab is a control
    character. str.strip() called both blank. Pinned identically in test-io_utils.R."""
    from lexsync.design import design_stem, validate_design
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: condition name 'b' appears more than once")):
        validate_design({"name": "kt", "language": "english", "match_on": ["length"],
                         "conditions": [{"name": n} for n in ("a", "b", "b", "a")]}, {})
    assert validate_design({"name": " ", "language": "english"}, {}) == []
    assert design_stem({"name": " ", "language": "english"}) == "english_fc0557ea"
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: the design's `name` contains control characters")):
        validate_design({"name": "\x0b", "language": "english"}, {})
    with pytest.raises(ValueError, match=re.escape("lexsync: the design has no `name`.")):
        validate_design({"name": " \t\r\n", "language": "english"}, {})


def test_design_stem_keeps_ascii_names_and_checksums_others():
    """Designs named 词频 and 笔画 in Chinese both wrote chinese_*, and an all-Chinese
    name and language wrote files beginning with an underscore or a dot. The suffix is
    over the NFC form, so canonically equivalent spellings share a stem. Pinned
    identically in test-io_utils.R."""
    from lexsync.design import design_stem
    assert design_stem({"name": "En Lexdec", "language": "english"}) == "en_lexdec_english"
    assert design_stem({"name": "词频", "language": "chinese"}) == "chinese_14aadfa7"
    assert design_stem({"name": "笔画", "language": "chinese"}) == "chinese_444a1c5f"
    assert design_stem({"name": "频率", "language": "中文"}) == "e525cb84"
    assert design_stem({"name": "café", "language": "french"}) == "caf_french_b679d075"
    assert design_stem({"name": "café", "language": "french"}) == "caf_french_b679d075"
    with pytest.raises(ValueError, match="hold no letter or digit"):
        design_stem({"name": "!!", "language": "--"})
    with pytest.raises(ValueError, match="the design has no `name`"):
        design_stem({"language": "english"})


def test_a_continuous_design_over_a_supplied_pool_takes_the_continuous_path():
    # The predicate allowed corpus and table only, so a 'continuous' block over
    # items.source 'pool' fell through to the conditions matcher and failed with
    # a different obscure error in each engine, even though run_pipeline's
    # corpus/pool branch handles continuous selection generically. The R twin
    # "a continuous design over a supplied pool takes the continuous path" in
    # test-io_utils.R pins the same outcomes.
    cont = {"predictor": "frequency", "controls": ["length"]}
    assert _is_continuous({"continuous": cont, "items": {"source": "pool"}})
    assert _is_continuous({"continuous": cont})            # default source: corpus
    assert not _is_continuous({"items": {"source": "pool"}})
    with pytest.raises(ValueError,
                       match="cannot be combined with items.source 'generate'"):
        _is_continuous({"continuous": cont, "items": {"source": "generate"}})
