import pandas as pd

from lexsync.counterbalancing import _recipe, counterbalance, participant_table


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


def test_the_paradigm_decides_the_recipe_even_when_the_design_declares_events():
    # The recipe used to fall back to factorial whenever a design declared its own
    # events, before the paradigm was consulted. config/design_en_priming_jitter.yaml
    # names priming and adjusts two durations, and every list held each target twice,
    # once related and once unrelated, which is the repetition the Latin square exists
    # to prevent. The same expectations are pinned in test-counterbalancing.R.
    events = [{"type": "text", "content": "{target}", "duration_ms": 800}]
    assert _recipe({"paradigm": "priming", "events": events}) == "latin_square_target"
    assert _recipe({"paradigm": "priming"}) == "latin_square_target"
    assert _recipe({"paradigm": "lexical_decision", "events": events}) == "factorial"
    assert _recipe({"events": events}) == "factorial"
    stim = pd.DataFrame({"prime": list("abcd"), "target": ["x", "x", "y", "y"],
                         "condition": ["r", "u", "r", "u"], "set": [1, 1, 2, 2]})
    out = counterbalance(stim, {"paradigm": "priming", "events": events,
                                "counterbalance": {"lists": 2}}, {"seed": 1})
    assert not out.duplicated(["list", "target"]).any()


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
    assert dict(zip(out["set"], out["list"], strict=True)) == {2: 1, 4: 2, 6: 1, 8: 2}


def test_keyed_hash_shuffle_matches_the_r_engine():
    # The hash of "seed|replicate|list|set|condition" decides each trial's position,
    # so the order is a pure function of the design and the two engines must produce
    # it byte for byte. test-counterbalancing.R pins these same words against these
    # same trials; a change to the key format or the digest breaks both suites.
    stim = pd.DataFrame({"word": list("abcdefgh"), "condition": ["x", "y"] * 4,
                         "set": [1, 1, 2, 2, 3, 3, 4, 4]})
    out = counterbalance(stim, {"counterbalance": {"lists": 2}}, {"seed": 2026})
    out = out.sort_values(["list", "trial"], kind="stable")
    assert list(out["word"]) == ["b", "f", "e", "a", "c", "g", "h", "d"]
    out2 = counterbalance(stim, {"counterbalance": {"lists": 2}}, {"seed": 1})
    out2 = out2.sort_values(["list", "trial"], kind="stable")
    assert list(out2["word"]) != list(out["word"])


def test_keyed_hash_shuffle_is_a_uniform_permutation():
    # Ranking by a hash is only a legitimate randomisation if the resulting
    # permutation is uniform: an item must be as likely to appear first as last,
    # or the design would carry systematic position effects. Over a fixed range of
    # seeds every item's mean position must sit at the centre of the list, and
    # every item must reach first place at least once. The shuffle is deterministic,
    # so these bounds are fixed facts about it rather than a sampling test that
    # could flake.
    n = 12
    stim = pd.DataFrame({"word": [f"w{i:02d}" for i in range(n)],
                         "condition": ["x"] * n, "set": list(range(n))})
    positions = {w: [] for w in stim["word"]}
    firsts = set()
    for seed in range(400):
        out = counterbalance(stim, {"counterbalance": {"lists": 1}}, {"seed": seed})
        out = out.sort_values("trial", kind="stable")
        firsts.add(out.iloc[0]["word"])
        for w, t in zip(out["word"], out["trial"], strict=True):
            positions[w].append(t)
    centre = (n + 1) / 2
    means = {w: sum(p) / len(p) for w, p in positions.items()}
    assert all(abs(m - centre) < 0.6 for m in means.values()), means
    assert firsts == set(stim["word"])
