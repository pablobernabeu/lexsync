import pandas as pd

from lexsync.querying import add_neighbourhood, build_pool, load_lexicon


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


def test_missing_column_raises(schema, tmp_path):
    bad = tmp_path / "bad.csv"
    pd.DataFrame({"notword": ["x"]}).to_csv(bad, index=False)
    try:
        load_lexicon(str(bad), schema)
        assert False, "expected a ValueError"
    except ValueError as exc:
        assert "required column" in str(exc)
