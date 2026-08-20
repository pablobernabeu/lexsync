"""Balance-aware list assignment (`counterbalance.optimise`).

The factorial recipe deals item sets to lists by rank, which balances nothing: any
dimension that varies smoothly across set ids is dealt out unevenly, and where each
list goes to a different group of participants that unevenness is confounded with the
group. `balance_lists` searches for an assignment whose lists are equated instead.

Two properties have to hold, and each is pinned here.

The search must be identical in the two engines, so the objective is all-integer.
Cohen's d was measured to differ between R and Python by around 3e-16, which at nine
decimal places leaves roughly a one-in-three chance over a full run of a candidate
comparison resolving differently -- and the failure would be silent and total,
different words rather than different last bits. The assignment asserted below is
pinned character for character against test-balance.R.

It must be off by default. Switching it on changes which items a participant sees, so
a design that does not ask for it has to be unaffected.

test-balance.R asserts the same properties.
"""
import pandas as pd
import pytest

from lexsync.counterbalancing import balance_lists, counterbalance, counterbalance_factorial

SCHEMA = {"seed": 2026}


def mk(n_sets=16):
    """Sets whose properties vary smoothly with set id, which is the case the rank
    deal handles worst: it hands every Nth set to the same list."""
    s = [i for i in range(1, n_sets + 1) for _ in range(2)]
    return pd.DataFrame({
        "word": ["w%03d%s" % (si, c) for si, c in zip(s, ["a", "b"] * n_sets, strict=True)],
        "set": s,
        "condition": ["hi", "lo"] * n_sets,
        "frequency": [2.0 + 0.31 * si for si in s],
        "length": [12 - (si % 7) for si in s],
        "old20": [1.0 + 0.07 * ((si * 5) % 11) for si in s],
    })


DESIGN = {"name": "b", "language": "english",
          "match_on": ["frequency", "length", "old20"],
          "counterbalance": {"lists": 4, "optimise": True}}


def _spread(stim, assign, dim):
    tot = {}
    for a, v in zip(assign, stim[dim], strict=True):
        tot[a] = tot.get(a, 0) + v
    return max(tot.values()) - min(tot.values())


def test_the_assignment_is_pinned_across_engines():
    res = balance_lists(mk(), DESIGN, SCHEMA)
    assert list(res["list_of_set"].values()) == [1, 2, 3, 4, 3, 2, 1, 4,
                                                 4, 3, 2, 4, 1, 2, 3, 1]
    assert res["report"]["cost_before"] == 88128
    assert res["report"]["cost_after"] == 33440
    assert res["report"]["n_swaps"] == 3
    assert res["report"]["max_passes_reached"] is False
    # Integers, not floats: a float cost is what would let the engines diverge.
    assert isinstance(res["report"]["cost_before"], int)
    assert isinstance(res["report"]["cost_after"], int)


def test_every_balanced_dimension_improves_on_the_rank_deal():
    stim = mk()
    res = balance_lists(stim, DESIGN, SCHEMA)
    sets = sorted(stim["set"].unique())
    deal = {s: (i % 4) + 1 for i, s in enumerate(sets)}
    before = [deal[s] for s in stim["set"]]
    after = [res["list_of_set"][s] for s in stim["set"]]
    for dim in ("frequency", "length", "old20"):
        assert _spread(stim, after, dim) < _spread(stim, before, dim), dim


def test_the_search_is_repeatable_and_preserves_list_sizes():
    a = balance_lists(mk(), DESIGN, SCHEMA)["list_of_set"]
    b = balance_lists(mk(), DESIGN, SCHEMA)["list_of_set"]
    assert a == b
    sizes = {}
    for v in a.values():
        sizes[v] = sizes.get(v, 0) + 1
    # A swap exchanges one set for another, so the rank deal's sizes are invariant.
    assert sorted(sizes.values()) == [4, 4, 4, 4]


def test_the_cost_never_increases():
    res = balance_lists(mk(), DESIGN, SCHEMA)
    assert res["report"]["cost_after"] <= res["report"]["cost_before"]


def test_optimise_is_refused_where_it_does_not_apply():
    # A Latin square already puts every item in every list, so there is nothing to
    # balance; saying so beats silently doing nothing.
    with pytest.raises(ValueError, match="Latin-square"):
        balance_lists(mk(), {"paradigm": "priming", "match_on": ["frequency"],
                             "counterbalance": {"lists": 2}}, SCHEMA)
    with pytest.raises(ValueError, match="2 or more"):
        balance_lists(mk(), {"match_on": ["frequency"],
                             "counterbalance": {"lists": 1}}, SCHEMA)
    with pytest.raises(ValueError, match="no dimensions to balance"):
        balance_lists(mk(), {"counterbalance": {"lists": 2}}, SCHEMA)
    with pytest.raises(ValueError, match="do not have: 'nope'"):
        balance_lists(mk(), {"match_on": ["nope"],
                             "counterbalance": {"lists": 2}}, SCHEMA)


def test_a_missing_dimension_value_is_refused():
    # Treating a missing value as zero would bias the objective silently.
    bad = mk()
    bad.loc[2, "frequency"] = float("nan")
    with pytest.raises(ValueError, match="missing values"):
        balance_lists(bad, DESIGN, SCHEMA)


def test_balance_on_defaults_to_match_on():
    explicit = dict(DESIGN)
    explicit["counterbalance"] = {"lists": 4, "optimise": True,
                                  "balance_on": ["frequency", "length", "old20"]}
    assert (balance_lists(mk(), explicit, SCHEMA)["list_of_set"]
            == balance_lists(mk(), DESIGN, SCHEMA)["list_of_set"])


def test_counterbalance_uses_the_supplied_assignment():
    stim = mk()
    res = balance_lists(stim, DESIGN, SCHEMA)
    out = counterbalance(stim, DESIGN, SCHEMA, res["list_of_set"])
    for s, l in zip(out["set"], out["list"], strict=True):
        assert l == res["list_of_set"][s]


def test_an_assignment_that_misses_a_set_is_an_error():
    # Silently defaulting the uncovered sets to list 1 would unbalance the very thing
    # the caller asked to balance.
    stim = mk()
    partial = {s: 1 for s in sorted(stim["set"].unique())[:-1]}
    with pytest.raises(ValueError, match="does not cover set"):
        counterbalance_factorial(stim, DESIGN, SCHEMA, partial)


def test_a_design_without_optimise_is_dealt_by_rank():
    # The default must be untouched: enabling the optimiser changes which items a
    # participant sees, so it cannot happen to a design on upgrade.
    stim = mk()
    plain = {"name": "b", "language": "english", "match_on": ["frequency"],
             "counterbalance": {"lists": 4}}
    out = counterbalance(stim, plain, SCHEMA)
    sets = sorted(stim["set"].unique())
    deal = {s: (i % 4) + 1 for i, s in enumerate(sets)}
    for s, l in zip(out["set"], out["list"], strict=True):
        assert l == deal[s]
