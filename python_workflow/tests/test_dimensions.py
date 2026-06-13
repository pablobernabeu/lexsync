"""Richer lexical dimensions: syllables, bigram frequency, and the norm connector."""
import pandas as pd

from lexsync.querying import add_bigram_frequency, count_syllables, merge_norms


def test_count_syllables_counts_vowel_runs():
    assert count_syllables("cat") == 1
    assert count_syllables("table") == 2
    assert count_syllables("beautiful") == 3      # b-eau-t-i-f-u-l
    assert count_syllables("queue") == 1          # one vowel run
    assert count_syllables("área") == 2           # accented vowels count (Spanish)
    assert count_syllables("中文") == 0           # no Latin vowels (Chinese)


def test_bigram_frequency_is_deterministic_and_a_probability():
    ref = ["the", "then", "they", "there", "their", "them", "than", "that"]
    a = add_bigram_frequency(pd.DataFrame({"word": ["the", "tha"]}), reference=ref)
    b = add_bigram_frequency(pd.DataFrame({"word": ["the", "tha"]}), reference=ref)
    assert list(a["bigram_freq"]) == list(b["bigram_freq"])      # deterministic
    assert (a["bigram_freq"] >= 0).all() and (a["bigram_freq"] <= 1).all()
    # "th" is the most frequent bigram in the reference, so 'the' scores highly
    assert a.loc[a["word"] == "the", "bigram_freq"].iloc[0] > 0


def test_merge_norms_joins_and_marks_missing():
    lex = pd.DataFrame({"word": ["cat", "dog", "xyz"]})
    norms = pd.DataFrame({"word": ["Cat", "dog"], "concreteness": [4.9, 4.8]})
    out = merge_norms(lex, norms)
    assert "concreteness" in out.columns
    assert out.loc[out["word"] == "cat", "concreteness"].iloc[0] == 4.9   # case-insensitive
    assert pd.isna(out.loc[out["word"] == "xyz", "concreteness"].iloc[0])  # missing -> NaN
