import os

import pandas as pd
import pytest
from conftest import _pkg_data

from lexsync import counterbalancing as cb
from lexsync.counterbalancing import counterbalance, participant_table
from lexsync.run_pipeline import run_pipeline

# The design block of config/design_en_priming_jitter.yaml: the priming paradigm with
# its own events, which read the prime's duration from the items and jitter the
# blank, dealt to two lists. Pinned identically in test-counterbalancing.R.
JITTER_EVENTS = [
    {"type": "fixation", "content": "+", "duration_ms": 500},
    {"type": "text", "content": "{prime}", "duration": {"from_column": "prime_ms"},
     "trigger": 20, "onset_locked": True},
    {"type": "mask", "content": "#####", "duration_ms": 33},
    {"type": "text", "content": "{target}", "duration_ms": 800, "trigger": "condition",
     "onset_locked": True},
    {"type": "response", "keys": ["left", "right"], "timeout_ms": 2000},
    {"type": "blank", "duration": {"jitter": [400, 800], "as": "iti_ms"}},
]

# items/priming_pairs_en_soa.csv: each target with its related and unrelated prime and
# the prime's duration in milliseconds.
SOA_PAIRS = [
    ("doctor", "nurse", "window", 60), ("cat", "dog", "table", 250),
    ("king", "queen", "pencil", 1200), ("bread", "butter", "planet", 60),
    ("hot", "cold", "paper", 250), ("black", "white", "river", 1200),
    ("moon", "star", "chair", 60), ("salt", "pepper", "engine", 250),
    ("day", "night", "carpet", 1200), ("hand", "foot", "cloud", 60),
    ("north", "south", "lemon", 250), ("cup", "saucer", "tractor", 1200),
]


def _soa_items():
    rows = []
    for i, (target, related, unrelated, ms) in enumerate(SOA_PAIRS, start=1):
        rows.append({"item": i, "set": i, "condition": "related", "prime": related,
                     "target": target, "prime_ms": ms})
        rows.append({"item": i, "set": i, "condition": "unrelated", "prime": unrelated,
                     "target": target, "prime_ms": ms})
    return pd.DataFrame(rows)


def _three_condition_items(n_sets=6):
    """A priming table with three conditions per target, sorted by byte order as the
    Latin square sorts them: identity, related, unrelated."""
    rows = []
    for s in range(1, n_sets + 1):
        for cond in ("identity", "related", "unrelated"):
            rows.append({"item": s, "set": s, "condition": cond,
                         "prime": "%s%d" % (cond[:3], s), "target": "t%d" % s})
    return pd.DataFrame(rows)


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


# ---- The recipe that runs, and incomplete rotations --------------------------
# Every test in this block is pinned identically in test-counterbalancing.R.

def test_explicit_events_keep_the_paradigms_latin_square():
    # Any `events:` list used to make counterbalance() deal the items factorially, so
    # en_priming_jitter showed six targets per list, each in both conditions, while
    # the datasheet and the Methods text described a Latin square. Per-trial timing
    # can be declared only inside events, so every priming, categorisation or
    # self-paced reading design with such timing was dealt this way.
    design = {"paradigm": "priming", "events": JITTER_EVENTS, "counterbalance": {"lists": 2}}
    assert cb._recipe(design) == "latin_square_target"
    out = counterbalance(_soa_items(), design, {"seed": 2026})
    assert out.groupby(["list", "set"]).size().max() == 1
    assert out.groupby("list")["set"].nunique().tolist() == [12, 12]
    # The other Latin-square paradigms keep theirs too, whatever their events hold.
    for paradigm in ("categorisation", "self_paced_reading"):
        own = {"paradigm": paradigm, "events": [{"type": "blank", "duration_ms": 250}]}
        assert cb._recipe(own) == "latin_square_target"
    # A design that names no paradigm still counterbalances factorially.
    assert cb._recipe({"events": JITTER_EVENTS}) == "factorial"
    # The optimiser is refused for these designs, as for every Latin square.
    optimised = dict(design, counterbalance={"lists": 2, "optimise": True},
                     match_on=["prime_ms"])
    with pytest.raises(ValueError, match="does not apply to a Latin-square design"):
        cb.balance_lists(_soa_items(), optimised, {"seed": 2026})


def test_counterbalance_recipe_override_is_validated():
    # counterbalance.recipe wins over the paradigm's recipe, in either direction.
    assert cb._recipe({"paradigm": "priming",
                       "counterbalance": {"recipe": "factorial"}}) == "factorial"
    assert cb._recipe({"counterbalance": {"recipe": "latin_square_target"}}) == (
        "latin_square_target")
    out = counterbalance(_soa_items(), {"paradigm": "priming",
                                        "counterbalance": {"recipe": "factorial", "lists": 2}},
                         {"seed": 2026})
    assert out.groupby(["list", "set"]).size().max() == 2
    with pytest.raises(ValueError) as err:
        counterbalance(_soa_items(), {"paradigm": "priming",
                                      "counterbalance": {"recipe": "latin_square"}},
                       {"seed": 2026})
    assert str(err.value) == ("lexsync: unknown counterbalance.recipe 'latin_square'. "
                              "Known recipes: factorial, latin_square_target.")


def test_an_incomplete_latin_square_is_reported(tmp_path):
    # Three conditions in two lists: each item is shown in only two of its three
    # conditions, and nothing used to say so.
    design = {"paradigm": "priming", "counterbalance": {"lists": 2}}
    out = counterbalance(_three_condition_items(), design, {"seed": 2026})
    check = cb.counterbalance_check(out, design)
    assert check["complete"] is False
    assert check["lists"] == 2
    assert check["issues"] == [
        "With 2 lists and 3 conditions, each item appears in only 2 of its 3 conditions."]
    assert check["cells"] == [
        {"list": lst, "condition": cond, "n_trials": 2}
        for lst in (1, 2) for cond in ("identity", "related", "unrelated")]
    # Item sets that are not a multiple of the conditions leave the cells unequal.
    seven = counterbalance(_three_condition_items(7), design, {"seed": 2026})
    assert cb.counterbalance_check(seven, design)["issues"] == [
        "With 2 lists and 3 conditions, each item appears in only 2 of its 3 conditions.",
        "With 7 item sets and 3 conditions, the item sets are not a multiple of the "
        "conditions, so the conditions within each list differ by one trial."]
    # One list confounds item and condition completely, and lists that are not a
    # multiple of the conditions rotate some conditions more often than others.
    one = counterbalance(_soa_items(), {"paradigm": "priming", "counterbalance": {"lists": 1}},
                         {"seed": 2026})
    assert cb.counterbalance_check(one, {"paradigm": "priming"})["issues"] == [
        "With one list, every participant sees each item in the same condition, so item "
        "and condition are fully confounded."]
    three = counterbalance(_soa_items(), {"paradigm": "priming", "counterbalance": {"lists": 3}},
                           {"seed": 2026})
    assert cb.counterbalance_check(three, {"paradigm": "priming"})["issues"] == [
        "With 3 lists and 2 conditions, the lists are not a multiple of the conditions, "
        "so each item appears in some conditions in more lists than in others."]
    full = counterbalance(_soa_items(), {"paradigm": "priming"}, {"seed": 2026})
    assert cb.counterbalance_check(full, {"paradigm": "priming"})["complete"] is True

    # counterbalance.incomplete: error refuses the run with the issue text.
    items = os.path.join(str(tmp_path), "items.csv")
    _three_condition_items().drop(columns="set").to_csv(items, index=False)
    design_path = os.path.join(str(tmp_path), "design.yaml")
    with open(design_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join([
            "name: incomplete_test", "language: english", "paradigm: priming",
            "items:", "  source: table", "  path: " + items.replace("\\", "/"),
            "counterbalance:", "  lists: 2", "  incomplete: error"]) + "\n")
    with pytest.raises(ValueError) as err:
        run_pipeline(design_path, _pkg_data("schema.yaml"), outdir=str(tmp_path / "out"),
                     verbose=False)
    assert str(err.value) == (
        "lexsync: the Latin-square rotation is incomplete and counterbalance.incomplete "
        "is 'error'. With 2 lists and 3 conditions, each item appears in only 2 of its 3 "
        "conditions. Make the lists and the item sets multiples of the number of "
        "conditions, or set counterbalance.incomplete: allow.")


def test_counterbalance_incomplete_resolves_design_over_schema_over_default():
    strict = {"counterbalance": {"incomplete": "error"}}
    assert cb._incomplete_policy({}, {}) == "allow"
    assert cb._incomplete_policy({}, strict) == "error"
    assert cb._incomplete_policy({"counterbalance": {"incomplete": "allow"}}, strict) == "allow"
    with pytest.raises(ValueError) as err:
        cb._incomplete_policy({"counterbalance": {"incomplete": "warn"}}, {})
    assert str(err.value) == ("lexsync: unknown counterbalance.incomplete policy 'warn'. "
                              "Known policies: allow, error.")


def test_a_factorial_design_with_more_lists_than_sets_is_refused():
    # The surplus lists used to come out empty, and the datasheet still recorded them.
    stim = pd.DataFrame({"word": list("abcdef"), "condition": ["x", "y"] * 3,
                         "set": [1, 1, 2, 2, 3, 3]})
    with pytest.raises(ValueError) as err:
        counterbalance(stim, {"counterbalance": {"lists": 4}}, {"seed": 1})
    assert str(err.value) == ("lexsync: counterbalance.lists is 4 but there are only 3 item "
                              "sets, so list 4 would be empty; lower lists or add items.")
    with pytest.raises(ValueError) as err:
        counterbalance(stim, {"counterbalance": {"lists": 5}}, {"seed": 1})
    assert str(err.value) == ("lexsync: counterbalance.lists is 5 but there are only 3 item "
                              "sets, so lists 4 to 5 would be empty; lower lists or add items.")
    # As many lists as sets is allowed, one set to each.
    out = counterbalance(stim, {"counterbalance": {"lists": 3}}, {"seed": 1})
    assert sorted(out["list"].unique()) == [1, 2, 3]


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
