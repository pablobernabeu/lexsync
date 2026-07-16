import pandas as pd
import pytest

from lexsync.querying import add_neighbourhood, build_pool, load_items, load_lexicon, merge_norms

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
    body = 'word,freq_zipf\n"{p}dog{p}",5.0\n" cat ",4.0\n'.format(p=pad)
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
    path.write_text('word,freq_zipf\n"{z}dog{z}",5.0\n'.format(z=zw), encoding="utf-8")
    lex = load_lexicon(str(path), schema)
    assert lex["word"].tolist() == ["{z}dog{z}".format(z=zw)]
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
    try:
        load_lexicon(str(bad), schema)
        assert False, "expected a ValueError"
    except ValueError as exc:
        assert "required column" in str(exc)


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
    body = 'item,condition,target\ni1,related,"{s}cat{s}"\n'.format(s=nbsp)
    path.write_text(body, encoding="utf-8")
    items = load_items(str(path), ["target"])
    assert items["target"].tolist() == ["{s}cat{s}".format(s=nbsp)]
