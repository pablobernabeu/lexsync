import re
import unicodedata

import pandas as pd
import pytest
import yaml

from lexsync.querying import (
    add_neighbourhood,
    build_pool,
    load_items,
    load_lexicon,
    load_pool,
    merge_norms,
)

# Every code point Python's str.strip() removes, i.e. every one whose
# str.isspace() is true: the Unicode White_Space property plus the C0
# information separators U+001C-U+001F. Written as code points so the set is
# unambiguous and the source stays readable; test-querying.R pins this same
# list, holding R's stringi trim and Python's str.strip() to one definition.
STRIPPED = [
    0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x1C, 0x1D, 0x1E, 0x1F, 0x20, 0x85, 0xA0,
    0x1680, 0x2000, 0x2001, 0x2002, 0x2003, 0x2004, 0x2005, 0x2006, 0x2007,
    0x2008, 0x2009, 0x200A, 0x2028, 0x2029, 0x202F, 0x205F, 0x3000,
]
# Format characters, not whitespace: a zero-width space, a Mongolian vowel
# separator and a word joiner must survive in both engines.
KEPT = [0x200B, 0x180E, 0x2060]


# The R engine cannot ask Python what it strips: R_workflow/R/querying.R names
# the set instead, as ICU's White_Space plus the four separators. Both sides of
# that equation are asserted -- here against str.strip() itself, and in
# test-querying.R against stringi -- so neither can drift unnoticed.
def test_stripped_is_exactly_the_whitespace_python_strips():
    assert [cp for cp in range(0x110000) if chr(cp).isspace()] == STRIPPED
    assert [chr(cp).strip() for cp in STRIPPED] == [""] * len(STRIPPED)
    assert not any(chr(cp).isspace() for cp in KEPT)


def test_load_lexicon(schema, en_lexicon_path):
    lex = load_lexicon(en_lexicon_path, schema, "english")
    assert {"word", "freq_zipf", "length", "frequency", "id"} <= set(lex.columns)
    assert (lex["length"] == lex["word"].str.len()).all()
    assert lex["word"].is_unique


def test_add_neighbourhood():
    df = pd.DataFrame({"word": ["cat", "car", "cap", "dog"]})
    out = add_neighbourhood(df, reference=df["word"].tolist(), n_old=2)
    # 'cat' differs from 'car' and 'cap' by a single substitution -> N = 2
    assert int(out.loc[out.word == "cat", "n_density"].iloc[0]) == 2
    assert (out["old20"] > 0).all()


def test_build_pool():
    df = pd.DataFrame({"word": list("abcde"), "frequency": [1, 2, 3, 4, 5], "pos": "n"})
    assert len(build_pool(df, {"frequency": [2, 4]})) == 3
    assert len(build_pool(df, {"pos": "n"})) == 5


# Pins the same contract as "load_lexicon drops rows whose word is missing" in
# the R engine's test-querying.R: a missing word must be dropped, not coerced to
# a word-like string, or the two engines' ids diverge from this row on.
def test_load_lexicon_drops_missing_words(schema, tmp_path):
    path = tmp_path / "gappy.csv"
    path.write_text("word,freq_zipf\ncat,5.0\n,4.0\ndog,3.0\nNA,2.0\ncow,1.0\n", encoding="utf-8")
    lex = load_lexicon(str(path), schema)
    assert lex["word"].tolist() == ["cat", "cow", "dog"]
    assert lex["id"].tolist() == [1, 2, 3]


# Pins the same contract as "load_lexicon strips the whitespace Python strips"
# in the R engine's test-querying.R. The word is the canonical key behind every
# byte-order tie-break, so a word padded with a no-break space must reduce to
# the same key, length and id in both engines.
def test_load_lexicon_strips_unicode_whitespace(schema, tmp_path):
    pad = "".join(chr(cp) for cp in STRIPPED)
    path = tmp_path / "padded.csv"
    body = f'word,freq_zipf\n"{pad}dog{pad}",5.0\n" cat ",4.0\n'
    path.write_text(body, encoding="utf-8")
    lex = load_lexicon(str(path), schema)
    assert lex["word"].tolist() == ["cat", "dog"]
    assert lex["length"].tolist() == [3, 3]
    assert lex["id"].tolist() == [1, 2]


# The mirror of the above: these are format characters, not whitespace, so
# neither engine may strip them. Pinning the boundary stops a future Unicode
# trim from over-reaching and silently re-keying a lexicon.
def test_load_lexicon_keeps_zero_width_characters(schema, tmp_path):
    zw = chr(KEPT[0])
    path = tmp_path / "zw.csv"
    path.write_text(f'word,freq_zipf\n"{zw}dog{zw}",5.0\n', encoding="utf-8")
    lex = load_lexicon(str(path), schema)
    assert lex["word"].tolist() == [f"{zw}dog{zw}"]
    assert lex["length"].tolist() == [5]


# Pins the same contract as "load_lexicon and load_pool lower-case by the full Unicode
# mapping" in test-querying.R. A final capital sigma becomes U+03C2 and U+0130 becomes
# i + U+0307, as str.lower() and the R engine's .lower_invariant() give them. Under
# pandas 3 with pyarrow, the pandas .str.lower() this engine used gave U+03C3 and a
# bare i, so the two engines keyed, sorted and measured these words differently.
def test_load_lexicon_and_load_pool_lower_case_by_the_full_unicode_mapping(schema, tmp_path):
    def text(*cps):
        return "".join(map(chr, cps))
    upper = [text(0x39F, 0x394, 0x39F, 0x3A3), text(0x130) + "stanbul", text(0xC1) + "RBOL"]
    lower = [text(0x69, 0x307) + "stanbul", text(0xE1) + "rbol", text(0x3BF, 0x3B4, 0x3BF, 0x3C2)]
    path = tmp_path / "cased.csv"
    path.write_text("word,freq_zipf\n" + "".join(f"{w},4.0\n" for w in upper),
                    encoding="utf-8")
    lex = load_lexicon(str(path), schema)
    assert lex["word"].tolist() == lower
    assert lex["length"].tolist() == [9, 5, 4]
    assert load_pool(str(path), schema)["pool"]["word"].tolist() == lower


# Pins the same contract as "merge_norms preserves the lexicon's row order" in
# the R engine's test-dimensions.R.
def test_merge_norms_preserves_lexicon_order():
    lex = pd.DataFrame({"word": ["a", "b", "c", "d"], "freq": [1, 2, 3, 4]})
    norms = pd.DataFrame({"word": ["d", "b"], "conc": [1.0, 2.0]})
    out = merge_norms(lex, norms)
    assert out["word"].tolist() == ["a", "b", "c", "d"]
    assert out["freq"].tolist() == [1, 2, 3, 4]
    assert out["conc"].tolist()[1::2] == [2.0, 1.0]
    assert out["conc"].isna().tolist() == [True, False, True, False]
    assert list(out.columns) == ["word", "freq", "conc"]


def test_merge_norms_does_not_join_on_a_missing_key():
    lex = pd.DataFrame({"word": ["cat", None]})
    norms = pd.DataFrame({"word": ["cat", None], "conc": [1.0, 2.0]})
    out = merge_norms(lex, norms)
    assert out["conc"].tolist()[0] == 1.0
    assert out["conc"].isna().tolist() == [False, True]


# Pins the same contract as "merge_norms joins on the same cleaned key" in the R
# engine's test-querying.R: the join key gets the lexicon's own trim and
# case-fold, so a no-break-space-padded norm table still joins in both engines.
def test_merge_norms_trims_the_join_key():
    nbsp = chr(0xA0)
    lex = pd.DataFrame({"word": ["cat", "dog"]})
    norms = pd.DataFrame({"word": [nbsp + "CAT" + nbsp, " dog"], "conc": [1.0, 2.0]})
    out = merge_norms(lex, norms)
    assert out["conc"].tolist() == [1.0, 2.0]


# Pins the same contract as "load_lexicon reports a lexicon left with no rows"
# in the R engine's test-querying.R. R used to die here on base R's "replacement
# has 1 row, data has 0" while Python handed back an empty frame; both engines
# now raise the same message, naming the file.
@pytest.mark.parametrize(
    "body",
    ["word,freq_zipf\n", "word,freq_zipf\n,1.0\nNA,2.0\n", "word,freq_zipf\ncat,\n"],
    ids=["header-only", "no-words", "no-frequencies"],
)
def test_load_lexicon_reports_an_empty_lexicon(schema, tmp_path, body):
    path = tmp_path / "empty.csv"
    path.write_text(body, encoding="utf-8")
    with pytest.raises(ValueError, match="has no usable rows"):
        load_lexicon(str(path), schema, "english")


# Pins the same contract as "load_lexicon refuses a frequency column that is not
# numeric" in test-querying.R. A thousands separator makes the column text under the
# shared reading rule. This engine then failed inside pandas' float conversion, and the
# R engine had read "1,000" as 1000.
def test_load_lexicon_refuses_a_frequency_column_that_is_not_numeric(schema, tmp_path):
    path = tmp_path / "grouped.csv"
    path.write_text('word,freq_zipf\ncat,"1,000"\ndog,2\n', encoding="utf-8")
    msg = ("lexsync: lexicon column 'freq_zipf' must hold plain decimal numbers, "
           "but it holds '1,000'.")
    with pytest.raises(ValueError, match=re.escape(msg)):
        load_lexicon(str(path), schema, "english")


def test_missing_column_raises(schema, tmp_path):
    bad = tmp_path / "bad.csv"
    pd.DataFrame({"notword": ["x"]}).to_csv(bad, index=False)
    # pytest.raises, as everywhere else in this file. The try/assert False form
    # this replaces passes for the wrong reason under `python -O`, which strips
    # asserts: the call would raise nothing, the vanished assert would not
    # complain, and the test would report success having checked nothing.
    with pytest.raises(ValueError, match="required column"):
        load_lexicon(str(bad), schema)


# Pins the same contract as "load_items trims the ASCII whitespace readr trims"
# in the R engine's test-querying.R. Both engines' readers trim every field, so
# the same padded table gives the same stimulus text, set ids and condition
# labels in each.
def test_load_items_trims_ascii_whitespace(tmp_path):
    path = tmp_path / "items.csv"
    path.write_text(
        "item,condition,target\n"
        '"  i2  ","  related  ","  padded target  "\n'
        '"\ti1\t","\tunrelated\t","\ttab padded\t"\n',
        encoding="utf-8",
    )
    items = load_items(str(path), ["target"])
    assert items["target"].tolist() == ["padded target", "tab padded"]
    assert items["condition"].tolist() == ["related", "unrelated"]
    # The set id is byte order over the trimmed item, so the padding must not
    # decide it: trimmed, 'i1' sorts before 'i2'.
    assert items["set"].tolist() == [2, 1]


# A no-break space is not ASCII whitespace and readr does not touch it, so
# neither engine may: this pins the boundary that keeps the two readers agreed.
def test_load_items_keeps_non_ascii_whitespace(tmp_path):
    nbsp = chr(0xA0)
    path = tmp_path / "nbsp.csv"
    body = f'item,condition,target\ni1,related,"{nbsp}cat{nbsp}"\n'
    path.write_text(body, encoding="utf-8")
    items = load_items(str(path), ["target"])
    assert items["target"].tolist() == [f"{nbsp}cat{nbsp}"]


# Pins the same contract as "load_items refuses missing or blank cells" in the R
# engine's test-querying.R. A missing cell used to arrive as NaN, be stringified
# to the literal 'nan' and flow on; a blank condition then defeated the hash-key
# guard downstream. Both readers read a blank, 'NA' or all-whitespace cell as
# missing, and the message is the same.
@pytest.mark.parametrize(
    "body,col",
    [
        ("item,condition,target\n,related,cat\n", "item"),
        ("item,condition,target\ni1,,cat\n", "condition"),
        ("item,condition,target\ni1,related,\n", "target"),
        ('item,condition,target\ni1,"   ",cat\n', "condition"),
        ("item,condition,target\ni1,NA,cat\n", "condition"),
    ],
    ids=["blank-item", "blank-condition", "blank-target",
         "whitespace-condition", "literal-NA"],
)
def test_load_items_refuses_missing_cells(tmp_path, body, col):
    path = tmp_path / "items.csv"
    path.write_text(body, encoding="utf-8")
    msg = ("lexsync: the items table has missing value(s) in column '%s'; "
           "every item, condition and presented field must be filled." % col)
    with pytest.raises(ValueError, match=re.escape(msg)):
        load_items(str(path), ["target"])


# The boundary of the refusal above: both readers treat only '' and 'NA' as
# missing, so a literal 'nan' is a kept value and must stay one.
def test_load_items_keeps_a_literal_nan_label(tmp_path):
    path = tmp_path / "nan.csv"
    path.write_text("item,condition,target\ni1,nan,cat\n", encoding="utf-8")
    items = load_items(str(path), ["target"])
    assert items["condition"].tolist() == ["nan"]


# Pins the same contract as "load_items refuses a duplicate item and condition
# pair" in the R engine's test-querying.R: it is the pair that must be unique,
# so the same item under another condition passes.
def test_load_items_refuses_a_duplicate_item_condition_pair(tmp_path):
    path = tmp_path / "dup.csv"
    path.write_text(
        "item,condition,target\ni1,related,cat\ni1,unrelated,dog\ni1,related,cow\n",
        encoding="utf-8")
    msg = ("lexsync: the items table repeats item 'i1' for condition 'related'; "
           "each item and condition pair may appear once.")
    with pytest.raises(ValueError, match=re.escape(msg)):
        load_items(str(path), ["target"])


# Pins the same contract as "load_items keeps numeric ids as written" in the R
# engine's test-querying.R. `item` is now read as text: left to inference, both
# readers number-parsed '01' down to 1 (and pandas float-promoted the whole
# column to '1.0' ids whenever any cell was missing), so ids must survive
# exactly as written.
def test_load_items_keeps_numeric_ids_as_written(tmp_path):
    path = tmp_path / "ids.csv"
    path.write_text("item,condition,target\n01,related,cat\n2,related,dog\n",
                    encoding="utf-8")
    items = load_items(str(path), ["target"])
    assert items["item"].tolist() == ["01", "2"]
    assert items["set"].tolist() == [1, 2]


# Spanish words written once with a precomposed accent (NFC) and once with the base
# letter and a combining acute (NFD). The NFD forms are derived with unicodedata, since
# a literal one looks exactly like its NFC twin in the source. test-querying.R builds
# the same strings with intToUtf8().
NFC_WORDS = ["avión", "limón", "café", "árbol"]
NFD_WORDS = [unicodedata.normalize("NFD", w) for w in NFC_WORDS]


# Pins the same contract as "NFC and NFD spellings are one word" in the R engine's
# test-querying.R. The two spellings used to be two words of different lengths, so a
# matcher could put one in each condition of a single matched set. After trimming and
# case-folding, every word is normalised to NFC, and the first row in file order wins.
def test_nfc_and_nfd_spellings_are_one_word(schema, tmp_path):
    path = tmp_path / "mixed.csv"
    rows = ["word,grp,freq_zipf"]
    # Interleaved, so the row kept for a word is sometimes the NFD one.
    for i, (nfc, nfd) in enumerate(zip(NFC_WORDS, NFD_WORDS, strict=True)):
        first, second = (nfc, nfd) if i % 2 == 0 else (nfd, nfc)
        rows += [f"{first},a,{4 + i}", f"{second.upper()},b,{4 + i}"]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")

    for frame in (load_pool(str(path), schema)["pool"], load_lexicon(str(path), schema)):
        assert len(frame) == len(NFC_WORDS)
        assert all(unicodedata.is_normalized("NFC", w) for w in frame["word"])
        assert sorted(frame["word"]) == sorted(NFC_WORDS)
        assert frame["length"].tolist() == [len(w) for w in frame["word"]]
        # The first row in file order is kept, which is grp a for every word.
        assert set(frame["grp"]) == {"a"}
        # One of each word's two rows is NFD after case-folding, which keeps the
        # accent decomposed or composed as written. So four forms changed under NFC,
        # and eight distinct keys became four.
        assert frame.attrs["input_normalisation"] == {"changed": 4, "collapsed": 4}


# Clean input carries no normalisation record, so no shipped datasheet changes.
def test_nfc_input_carries_no_normalisation_record(schema, en_lexicon_path):
    assert "input_normalisation" not in load_lexicon(en_lexicon_path, schema).attrs


# Pins the same contract as "an NFD norm key joins an NFC lexicon" in the R engine's
# test-querying.R. The key used to miss, and the dimension was silently NaN.
def test_an_nfd_norm_key_joins_an_nfc_lexicon():
    lex = pd.DataFrame({"word": NFC_WORDS})
    norms = pd.DataFrame({"word": NFD_WORDS, "conc": [1.0, 2.0, 3.0, 4.0]})
    out = merge_norms(lex, norms)
    assert out["conc"].tolist() == [1.0, 2.0, 3.0, 4.0]


# Pins the same contract as "load_items stores its text in NFC" in the R engine's
# test-querying.R: the item id, the condition and every presented field.
def test_load_items_stores_its_text_in_nfc(tmp_path):
    path = tmp_path / "items.csv"
    path.write_text(
        "item,condition,target\n"
        f"{NFD_WORDS[0]},{NFD_WORDS[1]},{NFD_WORDS[2]}\n"
        f"{NFC_WORDS[0]},x,{NFC_WORDS[3]}\n",
        encoding="utf-8")
    items = load_items(str(path), ["target"])
    assert items["item"].tolist() == [NFC_WORDS[0], NFC_WORDS[0]]
    assert items["condition"].tolist() == [NFC_WORDS[1], "x"]
    assert items["target"].tolist() == [NFC_WORDS[2], NFC_WORDS[3]]
    # One item in NFC and NFD is one item, so both rows share a set.
    assert items["set"].tolist() == [1, 1]
    assert items.attrs["input_normalisation"] == {"changed": 3, "collapsed": 0}


# Pins the same contract as "build_pool refuses a reversed range" in the R
# engine's test-querying.R: [7, 3] used to empty the pool without a word.
def test_build_pool_refuses_a_reversed_range():
    df = pd.DataFrame({"word": list("abcde"), "frequency": [1, 2, 3, 4, 5]})
    msg = "lexsync: filter 'frequency' has a reversed range; give it as [low, high]."
    with pytest.raises(ValueError, match=re.escape(msg)):
        build_pool(df, {"frequency": [7, 3]})


# Pins the same contract as "build_pool refuses a non-finite bound" in the R
# engine's test-querying.R: YAML's .nan/.inf used to drop every row silently.
def test_build_pool_refuses_a_non_finite_bound():
    df = pd.DataFrame({"word": list("abcde"), "frequency": [1, 2, 3, 4, 5]})
    msg = "lexsync: filter 'frequency' has a non-finite bound; ranges need finite numbers."
    for bad in ([float("nan"), 4.0], [2.0, float("inf")]):
        with pytest.raises(ValueError, match=re.escape(msg)):
            build_pool(df, {"frequency": bad})


# Equal bounds are a point, not a reversal: the zh design filters with [2, 2].
def test_build_pool_keeps_a_degenerate_range():
    df = pd.DataFrame({"word": list("abcde"), "frequency": [1, 2, 3, 4, 5]})
    assert build_pool(df, {"frequency": [2, 2]})["word"].tolist() == ["b"]


# The lexicon of the four tests below, which test-querying.R writes row for row. Four
# words lack `animate` and one lacks `n_morph`, so this engine's reader holds both
# columns as floats. `is_noun` is logical, and `is_noun01` holds the same codes as 0
# and 1.
def _coded_lexicon(schema, tmp_path):
    rows = ["word,freq_zipf,animate,n_morph,is_noun,is_noun01"]
    for i in range(40):
        animate = "" if i % 10 == 9 else str(i % 2)
        n_morph = "" if i == 0 else str(1 + i % 3)
        noun = i % 3 != 0
        rows.append(f"w{i:02d},{3 + i % 4},{animate},{n_morph},"
                    f"{'TRUE' if noun else 'FALSE'},{int(noun)}")
    path = tmp_path / "coded.csv"
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return load_lexicon(str(path), schema)


def _n_selected(lex, text):
    """The rows build_pool keeps under a filter written as a design writes it."""
    return len(build_pool(lex, yaml.safe_load(text)))


# Pins the same contract as "a 0/1 norm with blanks filters categorically" in the R
# engine's test-querying.R. One missing value makes the column float, and the filter
# compared '1.0' with '1'. A condition on a norm that leaves some words uncovered thus
# selected nothing in this engine, where the R engine selected.
def test_a_zero_one_norm_with_blanks_filters_categorically(schema, tmp_path):
    lex = _coded_lexicon(schema, tmp_path)
    assert int(lex["animate"].isna().sum()) == 4
    assert lex["animate"].dtype == "float64"
    assert _n_selected(lex, "{animate: 1}") == 16
    assert _n_selected(lex, "{animate: 0}") == 20
    assert _n_selected(lex, "{animate: [1]}") == 16
    # A quoted code is text, compared with the cell as the R engine writes it: '1'.
    assert _n_selected(lex, "{animate: '1'}") == 16


# Pins the same contract as "a float column filters on whole values" in the R engine's
# test-querying.R.
def test_a_float_column_filters_on_whole_values(schema, tmp_path):
    lex = _coded_lexicon(schema, tmp_path)
    assert _n_selected(lex, "{n_morph: [1, 2, 3]}") == 39
    assert _n_selected(lex, "{n_morph: [1.0, 2.0, 3.0]}") == 39
    # Beside text, a number is text too, written as the R engine writes it.
    assert _n_selected(lex, "{n_morph: [1, a]}") == 13


# Pins the same contract as "a boolean filter on a logical column" in the R engine's
# test-querying.R. [true, false] was taken for a reversed numeric range and refused.
def test_a_boolean_filter_on_a_logical_column(schema, tmp_path):
    lex = _coded_lexicon(schema, tmp_path)
    assert _n_selected(lex, "{is_noun: [true, false]}") == 40
    assert _n_selected(lex, "{is_noun: [false, true]}") == 40
    assert _n_selected(lex, "{is_noun: [true]}") == 26
    assert _n_selected(lex, "{is_noun: ['TRUE']}") == 26


# Pins the same contract as "a boolean filter on a 0/1 column selects nothing" in the R
# engine's test-querying.R. A boolean is not a number in R, and as text it is TRUE or
# FALSE, which no 0/1 cell is.
def test_a_boolean_filter_on_a_zero_one_column_selects_nothing(schema, tmp_path):
    lex = _coded_lexicon(schema, tmp_path)
    assert _n_selected(lex, "{is_noun01: [true, false]}") == 0
    assert _n_selected(lex, "{is_noun01: true}") == 0
    assert _n_selected(lex, "{is_noun01: 1}") == 26


def _neighbourhood_by_loop(words, reference, n_old=20):
    """The word-by-word computation add_neighbourhood used before it was vectorised,
    kept here as the specification the matrix version must reproduce."""
    import numpy as np
    from rapidfuzz.distance import Hamming, Levenshtein
    ref = list(dict.fromkeys(reference))
    n_density, old = [], []
    for w in words:
        same_len = [r for r in ref if len(r) == len(w)]
        n_density.append(int(sum(Hamming.distance(w, s) == 1 for s in same_len)))
        ld = np.array([Levenshtein.distance(w, r) for r in ref], dtype=float)
        ld = ld[ld > 0]
        k = min(n_old, ld.size)
        old.append(float(np.mean(np.partition(ld, k - 1)[:k])) if k else float("nan"))
    return n_density, old


def test_vectorised_add_neighbourhood_equals_the_loop_on_500_words(schema, en_lexicon_path):
    lex = load_lexicon(en_lexicon_path, schema)
    reference = lex["word"].tolist()
    # 500 words spread over the byte order, so every length the lexicon holds is in.
    sample = lex.iloc[::6].head(500).reset_index(drop=True)
    out = add_neighbourhood(sample[["word"]], reference=reference)
    n_density, old = _neighbourhood_by_loop(sample["word"].tolist(), reference)
    assert out["n_density"].tolist() == n_density
    assert out["old20"].tolist() == old


def test_add_neighbourhood_handles_an_empty_frame_and_reference():
    empty = add_neighbourhood(pd.DataFrame({"word": pd.Series([], dtype=object)}),
                              reference=["cat"])
    assert empty["n_density"].tolist() == [] and empty["old20"].tolist() == []
    alone = add_neighbourhood(pd.DataFrame({"word": ["cat"]}), reference=["cat"])
    assert alone["n_density"].tolist() == [0]
    assert pd.isna(alone["old20"].iloc[0])


def test_load_pool_keeps_only_reference_members_in_the_reference(schema, tmp_path):
    from lexsync.querying import load_pool
    lexicon = tmp_path / "lexicon.csv"
    lexicon.write_text("word,freq_zipf,reference_member\ncat,5.0,1\ncap,4.0,0\n"
                       "cot,4.1,1\ndog,5.2,0\n", encoding="utf-8")
    pool = tmp_path / "pool.csv"
    pool.write_text("word\ncat\ndog\n", encoding="utf-8")
    res = load_pool(str(pool), schema, lexicon=str(lexicon))
    assert res["reference"] == ["cat", "cot"]


def test_a_reference_member_column_must_hold_zero_or_one(schema, tmp_path):
    from lexsync.querying import load_pool
    lexicon = tmp_path / "lexicon.csv"
    lexicon.write_text("word,freq_zipf,reference_member\ncat,5.0,1\ncap,4.0,2\n",
                       encoding="utf-8")
    pool = tmp_path / "pool.csv"
    pool.write_text("word\ncat\n", encoding="utf-8")
    with pytest.raises(ValueError, match="lexsync: lexicon column 'reference_member' must "
                                         "hold 0 or 1 for every word."):
        load_pool(str(pool), schema, lexicon=str(lexicon))
    lexicon.write_text("word,freq_zipf,reference_member\ncat,5.0,0\ncap,4.0,0\n",
                       encoding="utf-8")
    with pytest.raises(ValueError, match="lexsync: lexicon column 'reference_member' marks "
                                         "no word as a member of the neighbourhood "
                                         "reference."):
        load_pool(str(pool), schema, lexicon=str(lexicon))
