import pandas as pd

from lexsync.counterbalancing import counterbalance, participant_table


def test_participant_table():
    pt = participant_table({"order": ["A", "B"], "lang": ["en", "es"]}, 8)
    assert len(pt) == 8
    assert {"order", "lang", "participant"} <= set(pt.columns)
    assert list(pt["participant"]) == list(range(1, 9))


def test_participant_table_varies_the_first_factor_fastest():
    # Same expected cells are pinned in test-counterbalancing.R: the engines must
    # allocate a participant number to the same cell.
    pt = participant_table({"order": ["A", "B"], "lang": ["en", "es"]}, 8)
    assert list(pt["order"]) == ["A", "B", "A", "B", "A", "B", "A", "B"]
    assert list(pt["lang"]) == ["en", "en", "es", "es", "en", "en", "es", "es"]


def test_participant_table_first_factor_fastest_with_three_factors():
    pt = participant_table({"a": [1, 2], "b": ["x", "y"], "c": ["p", "q"]}, 8)
    assert list(pt["a"]) == [1, 2, 1, 2, 1, 2, 1, 2]
    assert list(pt["b"]) == ["x", "x", "y", "y", "x", "x", "y", "y"]
    assert list(pt["c"]) == ["p", "p", "p", "p", "q", "q", "q", "q"]


def test_counterbalance_adds_list_and_trial():
    stim = pd.DataFrame({"word": list("abcd"), "condition": ["x", "x", "y", "y"], "set": [1, 2, 1, 2]})
    out = counterbalance(stim, {"counterbalance": {"lists": 1}}, {"seed": 1})
    assert {"list", "trial"} <= set(out.columns)
    assert sorted(out["trial"]) == [1, 2, 3, 4]


def test_counterbalance_factorial_deals_lists_by_set_rank():
    # Non-contiguous set numbers: the deal follows the rank of the set, not its
    # value. Same expected mapping is pinned in test-counterbalancing.R.
    stim = pd.DataFrame({"word": list("abcdefgh"), "condition": ["x", "y"] * 4,
                         "set": [2, 2, 4, 4, 6, 6, 8, 8]})
    out = counterbalance(stim, {"counterbalance": {"lists": 2}}, {"seed": 1})
    assert dict(zip(out["set"], out["list"])) == {2: 1, 4: 2, 6: 1, 8: 2}
