import pandas as pd

from lexsync.querying import add_neighbourhood, build_pool, load_lexicon, merge_norms


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


def test_missing_column_raises(schema, tmp_path):
    bad = tmp_path / "bad.csv"
    pd.DataFrame({"notword": ["x"]}).to_csv(bad, index=False)
    try:
        load_lexicon(str(bad), schema)
        assert False, "expected a ValueError"
    except ValueError as exc:
        assert "required column" in str(exc)
