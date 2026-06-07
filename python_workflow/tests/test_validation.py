import pandas as pd

from lexsync.validation import balance_check, cohens_d, describe_stimuli, tost_equiv


def test_cohens_d():
    assert cohens_d([1, 2, 3, 4], [1, 2, 3, 4]) == 0
    assert abs(cohens_d([5, 6, 7, 8], [1, 2, 3, 4])) > 1


def test_tost_equivalent_for_matched_samples():
    x = [4, 5, 6] * 20
    y = [4, 5, 6] * 20
    assert tost_equiv(x, y, bound_d=0.5)["equivalent"] is True


def test_describe_and_balance():
    df = pd.DataFrame({"condition": ["a", "a", "b", "b"], "x": [1, 2, 3, 4]})
    d = describe_stimuli(df, ["x"])
    assert {"group", "dimension", "n", "mean", "sd"} <= set(d.columns)
    assert len(d) == 2
    assert len(balance_check(pd.DataFrame({"condition": ["a", "a", "a", "b"]}), "condition")) == 1
    assert len(balance_check(pd.DataFrame({"condition": ["a", "a", "b", "b"]}), "condition")) == 0
