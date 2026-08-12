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


# Pins the same contract as "slugify folds case whatever the locale" in the R
# engine's test-io_utils.R, where base tolower() folded "I" to the dotless "i"
# under a Turkish locale and wrote the design's artifacts under a name this
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
