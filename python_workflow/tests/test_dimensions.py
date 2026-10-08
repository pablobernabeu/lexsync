"""Richer lexical dimensions: syllables, bigram frequency, and the norm connector."""
import pandas as pd
import pytest
from conftest import _pkg_data

from lexsync.querying import add_bigram_frequency, count_syllables, load_lexicon, merge_norms


def test_count_syllables_counts_vowel_runs():
    assert count_syllables("cat") == 1
    assert count_syllables("table") == 2
    assert count_syllables("beautiful") == 3      # b-eau-t-i-f-u-l
    assert count_syllables("queue") == 1          # one vowel run
    assert count_syllables("área") == 2           # accented vowels count (Spanish)


# The cross-check of the vowel class between the engines: "count_syllables counts
# the vowels of every Latin orthography" in test-dimensions.R holds the same words, in
# the same order, with the same counts. It covers æ, œ and every Latin Extended vowel
# the class was missing, which undercounted Polish, Czech, Hungarian, Romanian,
# Turkish, Danish and Norwegian words.
SYLLABLE_CASES = [
    ("b\u0119d\u0119", 2),        # Polish, e with ogonek
    ("s\u0105", 1),               # Polish, a with ogonek
    ("\u0142\u0105ka", 2),        # Polish, l with stroke is a consonant
    ("k\u0131z", 1),              # Turkish, dotless i
    ("m\u0131", 1),
    ("d\u016fm", 1),              # Czech, u with ring
    ("m\u011bsto", 2),            # Czech, e with caron
    ("k\u0151", 1),               # Hungarian, o with double acute
    ("t\u0171z", 1),              # Hungarian, u with double acute
    ("m\u0103r", 1),              # Romanian, a with breve
    ("b\u00e6re", 2),             # Norwegian, ae
    ("s\u00f8ster", 2),           # Danish, o with stroke
    ("c\u0153ur", 1),             # French, oe
    ("m\u0101te", 2),             # Latvian, macrons
    ("m\u0113ness", 2),
    ("l\u012bdz", 1),
    ("\u016bdens", 2),
    ("g\u0117l\u0117", 2),        # Lithuanian, e with dot above
    ("\u012fvykis", 3),           # Lithuanian, i with ogonek
    ("rank\u0173", 2),            # Lithuanian, u with ogonek
    ("t\u014dky\u014d", 2),       # o with macron
    ("m\u01ce", 1),               # pinyin, vowels with caron
    ("n\u01d0", 1),
    ("w\u01d2", 1),
    ("b\u01d4", 1),
    ("m\u1ed9t", 1),              # Vietnamese, Latin Extended Additional
    ("ng\u01b0\u1eddi", 1),       # Vietnamese, u and o with horn
    ("\u0130stanbul", 3),         # lower-cases to i + U+0307, still Latin
    ("cafe\u0301", 2),            # decomposed input counts as composed
    ("don\u2019t", 1),            # a typographic apostrophe is punctuation
]


def test_count_syllables_counts_the_vowels_of_every_latin_orthography():
    assert [count_syllables(w) for w, _ in SYLLABLE_CASES] == [n for _, n in SYLLABLE_CASES]


# Every value 0 let a design match on n_syllables in another script and report
# perfect balance; NA says the estimate does not apply.
def test_count_syllables_is_missing_for_a_word_in_another_script():
    for word in ["\u4e2d\u6587",                              # Chinese
                 "\u043c\u043e\u043b\u043e\u043a\u043e",      # Russian
                 "\u03bd\u03b5\u03c1\u03cc",                  # Greek
                 "caf\u00e9\u4e2d"]:                          # one non-Latin letter
        assert count_syllables(word) is None, word
    assert count_syllables(None) is None
    assert count_syllables(float("nan")) is None
    assert count_syllables(pd.NA) is None             # as R's NA, not the word "<NA>"
    assert count_syllables("") == 0


def test_load_lexicon_leaves_n_syllables_missing_outside_latin_script(schema):
    zh = load_lexicon(_pkg_data("zh_example.csv"), schema)
    assert zh["n_syllables"].isna().all()
    en = load_lexicon(_pkg_data("en_example.csv"), schema)
    assert en["n_syllables"].notna().all()
    assert en["n_syllables"].dtype.kind == "i"


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
