import re

import pandas as pd
import pytest

from lexsync import querying
from lexsync.querying import (
    add_neighbourhood,
    build_pool,
    load_items,
    load_lexicon,
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


# Both dimensions are read off one edit-distance matrix, so the case that tells
# them apart is worth pinning: 'cats' and 'at' are at distance 1 from 'cat' but
# are not the same length, so they count towards OLD20 and not towards N.
def test_add_neighbourhood_counts_only_same_length_neighbours():
    ref = ["cat", "car", "cap", "cats", "at", "dog"]
    out = add_neighbourhood(pd.DataFrame({"word": ["cat"]}), reference=ref)
    assert int(out["n_density"].iloc[0]) == 2
    assert out["old20"].iloc[0] == pytest.approx((1 + 1 + 1 + 1 + 3) / 5)


def test_add_neighbourhood_chunking_does_not_change_the_values(monkeypatch):
    words = [f"{a}{b}{c}" for a in "abcdef" for b in "abcdef" for c in "abcdefghijklmnopqrst"]
    assert len(words) > querying._NEIGHBOUR_CHUNK   # the fixture spans more than one chunk
    df = pd.DataFrame({"word": words})
    chunked = add_neighbourhood(df, reference=words)
    monkeypatch.setattr(querying, "_NEIGHBOUR_CHUNK", len(words) + 1)
    whole = add_neighbourhood(df, reference=words)
    assert chunked["n_density"].tolist() == whole["n_density"].tolist()
    assert [v.hex() for v in chunked["old20"]] == [v.hex() for v in whole["old20"]]


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
# in the R engine's test-querying.R. readr's trim_ws strips padding from every
# field before Python ever sees it, so without this the same table gives
# different stimulus text, set ids and condition labels per engine.
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
# guard downstream. The two readers reach the refusal at different stages (readr
# reads a blank or 'NA' or all-whitespace cell as NA; pandas keeps a quoted
# whitespace cell as text until the trim), but the message is the same.
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


def _banded():
    """One missing value promotes an integer-valued column to float, which is
    routine on a joined norm table."""
    return pd.DataFrame({"word": list("abcd"), "band": [1.0, 2.0, 3.0, float("nan")],
                         "flag": [True, False, True, True]})


# Pins the same contract as "build_pool matches a numeric filter numerically" in
# the R engine's test-querying.R: the values were compared as strings, and str()
# renders 2.0 as '2.0' where R's as.character() gives '2', so an integer literal
# matched nothing on a float column and emptied the pool without a word.
def test_build_pool_matches_a_numeric_value_filter_on_a_float_column():
    df = _banded()
    assert build_pool(df, {"band": [1, 2, 3]})["word"].tolist() == ["a", "b", "c"]
    assert build_pool(df, {"band": [2]})["word"].tolist() == ["b"]
    assert build_pool(df, {"band": 2})["word"].tolist() == ["b"]
    assert build_pool(df, {"band": [1.0, 2.0, 3.0]})["word"].tolist() == ["a", "b", "c"]


# Pins the same contract as "build_pool takes a boolean pair as permitted values"
# in the R engine's test-querying.R: bool is a subclass of int here, so the pair
# was read as a range and refused as reversed.
def test_build_pool_takes_a_boolean_filter_as_permitted_values():
    df = _banded()
    assert build_pool(df, {"flag": [True, False]})["word"].tolist() == list("abcd")
    assert build_pool(df, {"flag": [False]})["word"].tolist() == ["b"]
    # A boolean is spelt as R spells it, so a design quoting 'TRUE' selects the
    # same rows in both engines.
    assert build_pool(df, {"flag": ["TRUE"]})["word"].tolist() == ["a", "c", "d"]
