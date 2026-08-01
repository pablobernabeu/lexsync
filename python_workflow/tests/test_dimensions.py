"""Richer lexical dimensions: syllables, bigram frequency, and the norm connector."""
import pandas as pd
import pytest

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


# The case-fold has to apply to the LEXICON's side of the key too. Only the norm
# table's side was normalised until now, and the test above passes either way
# because its lexicon is already lower-case -- so the suite asserted
# case-insensitivity in the one direction that happened to work. A lexicon holding
# `Dog` silently matched nothing and the design carried on with an all-NaN
# dimension, in BOTH engines, which is why no parity test could have caught it.
# "merge_norms case-folds the lexicon's side of the key too" in test-dimensions.R
# asserts the same.
def test_merge_norms_folds_the_lexicon_key_too():
    lex = pd.DataFrame({"word": ["Dog", "cat", "BIRD"]})
    norms = pd.DataFrame({"word": ["dog", "cat", "bird"], "conc": [4.9, 4.8, 4.7]})
    out = merge_norms(lex, norms)
    assert out["conc"].tolist() == [4.9, 4.8, 4.7]
    # The lexicon's own spelling survives: `word` is the byte-order tie-break behind
    # every selection, so the join must not rewrite it.
    assert out["word"].tolist() == ["Dog", "cat", "BIRD"]


# Pins the same contract as "merge_norms keeps the lexicon's column order when the
# key is not first" in test-dimensions.R. R's merge() hoists the by-column to
# position 1 while pandas keeps the left frame's order, so the two engines returned
# different column order whenever `on` was not already first -- measured, not supposed.
def test_merge_norms_keeps_the_lexicon_column_order():
    lex = pd.DataFrame({"id": [1, 2], "word": ["dog", "cat"], "freq": [5.0, 4.8]})
    norms = pd.DataFrame({"word": ["dog", "cat"], "conc": [1.0, 2.0]})
    assert list(merge_norms(lex, norms).columns) == ["id", "word", "freq", "conc"]

    # Also when the key is neither first nor named `word`.
    lex2 = pd.DataFrame({"word": ["dog", "cat"], "lemma": ["DOG", " cat"]})
    norms2 = pd.DataFrame({"lemma": ["dog", "cat"], "aoa": [3.1, 3.4]})
    out2 = merge_norms(lex2, norms2, on="lemma")
    assert list(out2.columns) == ["word", "lemma", "aoa"]
    assert out2["aoa"].tolist() == [3.1, 3.4]


# A colliding name is the worst of the three divergences: pandas renames to
# `frequency_x`/`_y` and R's merge() to `frequency.x`/`.y`, so a design matching on
# `frequency` finds neither, in either engine. Refusing is the only safe answer.
def test_merge_norms_rejects_a_colliding_norm_column():
    lex = pd.DataFrame({"word": ["dog"], "frequency": [5.0]})
    norms = pd.DataFrame({"word": ["dog"], "frequency": [1.1]})
    with pytest.raises(ValueError, match="already exist on the lexicon"):
        merge_norms(lex, norms)
    # Naming the columns to keep is the documented way out.
    norms2 = pd.DataFrame({"word": ["dog"], "frequency": [1.1], "conc": [2.0]})
    assert merge_norms(lex, norms2, columns=["conc"])["conc"].tolist() == [2.0]


def test_merge_norms_rejects_an_absent_column_or_key():
    lex = pd.DataFrame({"word": ["cat"]})
    norms = pd.DataFrame({"word": ["cat"], "conc": [1.0]})
    with pytest.raises(ValueError, match=r"no column\(s\): 'nope'"):
        merge_norms(lex, norms, columns=["conc", "nope"])
    with pytest.raises(ValueError, match="'word' on the lexicon"):
        merge_norms(pd.DataFrame({"w": ["cat"]}), norms)
    with pytest.raises(ValueError, match="'word' on the norm table"):
        merge_norms(lex, pd.DataFrame({"w": ["cat"], "conc": [1.0]}))


def test_merge_norms_keeps_the_first_of_a_duplicated_norm_key():
    out = merge_norms(pd.DataFrame({"word": ["cat"]}),
                      pd.DataFrame({"word": ["cat", "CAT"], "conc": [1.0, 9.0]}))
    assert out["conc"].tolist() == [1.0]
