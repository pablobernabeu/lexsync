import pandas as pd
import pytest

from lexsync.io_utils import clean_field, read_csv_utf8, sha256_file, slugify, write_csv_utf8

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
    path = write_csv_utf8(_frame(), str(tmp_path / "nested" / "s.csv"))
    assert read_csv_utf8(path).equals(_frame())


def test_read_csv_utf8_keeps_words_that_look_like_missing_values(tmp_path):
    path = tmp_path / "s.csv"
    path.write_bytes(b"word,gloss\nnull,x\nnan,y\n,z\nNA,w\n")
    out = read_csv_utf8(str(path))
    assert list(out["word"][:2]) == ["null", "nan"]
    assert out["word"][2:].isna().all()


def test_clean_field_rejects_control_characters():
    with pytest.raises(ValueError, match="control characters"):
        clean_field("cat\ndog", "word")


def test_clean_field_allows_commas_and_quotes():
    assert clean_field('the "big" cat, asleep', "word") == 'the "big" cat, asleep'


def test_slugify_is_lowercase_and_path_safe():
    assert slugify("En Lexdec", "English!") == "en_lexdec_english"
