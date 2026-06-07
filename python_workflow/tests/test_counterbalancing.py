import pandas as pd

from lexsync.counterbalancing import counterbalance, participant_table


def test_participant_table():
    pt = participant_table({"order": ["A", "B"], "lang": ["en", "es"]}, 8)
    assert len(pt) == 8
    assert {"order", "lang", "participant"} <= set(pt.columns)
    assert list(pt["participant"]) == list(range(1, 9))


def test_counterbalance_adds_list_and_trial():
    stim = pd.DataFrame({"word": list("abcd"), "condition": ["x", "x", "y", "y"], "set": [1, 2, 1, 2]})
    out = counterbalance(stim, {"counterbalance": {"lists": 1}}, {"seed": 1})
    assert {"list", "trial"} <= set(out.columns)
    assert sorted(out["trial"]) == [1, 2, 3, 4]
