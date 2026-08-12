"""The pair-keyed item model: member norms, relational dimensions, pair selection.

A relational design's predictor is a property of the PAIR while its controls are
properties of each MEMBER, so it needs an item table and selection at the same time.
Until this existed a design could have one or the other.

Three properties are load-bearing and each has a test here.

The member prefix leads (`prime.frequency`, never `frequency.prime`). R's `$`
partial-matches on a data frame, so a joined `word.frequency` with no bare `word`
would make the selector's tie-break silently sort by it in R while this engine raised
KeyError. The reserved-name check is what prevents that class of divergence.

Selection runs on one row per pair and re-expands. A filter on `target.frequency`
applied row-wise would keep a pair's related row and drop its unrelated one, leaving
a set the Latin-square counterbalancer cannot complete.

`pair.overlap` is computed in-engine, which is only safe because the core is an
integer edit distance and the arithmetic uses no transcendental. Its bit patterns are
pinned in R_workflow/tests/testthat/test-pairs.R against the same values.
"""
import pandas as pd
import pytest

from lexsync.pairs import RESERVED_MEMBER_NAMES, _check_members, select_continuous_pairs
from lexsync.querying import add_pair_overlap

PAIRS = pd.DataFrame({
    "item": [1, 1, 2, 2, 3, 3],
    "set": [1, 1, 2, 2, 3, 3],
    "condition": ["related", "unrelated"] * 3,
    "prime": ["nurse", "window", "dog", "table", "queen", "pencil"],
    "target": ["doctor", "doctor", "cat", "cat", "king", "king"],
    "target.frequency": [5.0, 5.0, 4.8, 4.8, 5.2, 5.2],
    "target.length": [6, 6, 3, 3, 4, 4],
})


def test_relational_overlap_matches_the_r_engine():
    out = add_pair_overlap(PAIRS)
    assert list(out["pair.lev"]) == [6, 5, 3, 4, 5, 5]
    assert list(out["pair.overlap"]) == [0.0, 0.166666667, 0.0, 0.2, 0.0, 0.166666667]


def test_overlap_handles_non_ascii_and_the_degenerate_pair():
    df = pd.DataFrame({"prime": ["café", "", "北京"], "target": ["cafe", "", "北方"]})
    out = add_pair_overlap(df)
    assert list(out["pair.lev"]) == [1, 0, 1]
    # Two empty forms give 0, never 0/0: a NaN would be sorted and compared, and
    # would drop the row from one engine's control window but not the other's.
    assert list(out["pair.overlap"]) == [0.75, 0.0, 0.5]


def test_a_reserved_member_name_is_rejected():
    for name in ("word", "set", "condition", "item"):
        assert name in RESERVED_MEMBER_NAMES
        with pytest.raises(ValueError, match="reserved name"):
            _check_members([name], PAIRS)


def test_a_member_column_that_is_absent_is_rejected():
    with pytest.raises(ValueError, match="does not have"):
        _check_members(["prime", "nope"], PAIRS)


def test_selection_keeps_every_condition_row_of_every_chosen_pair():
    design = {
        "n_per_condition": 2,
        "continuous": {"predictor": "target.frequency", "controls": ["target.length"]},
        "match_on": ["target.length"],
    }
    res = select_continuous_pairs(PAIRS, {"anchor_condition": "related"}, design,
                                  {"matching": {"tolerance_k": {"target.length": 2}}})
    out = res["stim"]
    # Two pairs chosen, each contributing both of its condition rows.
    assert out["set"].nunique() == 2
    assert len(out) == 4
    assert all(n == 2 for n in out.groupby("set")["condition"].nunique())


def test_a_pair_failing_a_filter_on_any_row_is_excluded_whole():
    design = {
        "n_per_condition": 3,
        "pool_filters": {"target.length": [4, 6]},   # excludes set 2 (length 3)
        "continuous": {"predictor": "target.frequency", "controls": ["target.length"]},
        "match_on": ["target.length"],
        # The exclusion leaves 2 of the 3 requested pairs; accepting that shrink
        # is the point of the test, so the shortfall policy is opted out of here.
        "matching": {"shortfall": "allow"},
    }
    res = select_continuous_pairs(PAIRS, {"anchor_condition": "related"}, design,
                                  {"matching": {"tolerance_k": {"target.length": 2}}})
    assert res["n_eligible"] == 2
    assert 2 not in set(res["stim"]["set"])


def test_a_mistyped_pool_filter_is_rejected_rather_than_skipped():
    design = {
        "n_per_condition": 2,
        "pool_filters": {"target.lenght": [3, 6]},
        "continuous": {"predictor": "target.frequency", "controls": ["target.length"]},
        "match_on": ["target.length"],
    }
    # build_pool silently skips an unknown column, which would quietly widen the
    # selection rather than failing.
    with pytest.raises(ValueError, match="does not have"):
        select_continuous_pairs(PAIRS, {}, design, {"matching": {"tolerance_k": {}}})


def test_the_anchor_condition_defaults_to_the_byte_first_one():
    design = {
        "n_per_condition": 3,
        "continuous": {"predictor": "target.frequency", "controls": ["target.length"]},
        "match_on": ["target.length"],
    }
    # 'related' sorts before 'unrelated' in byte order, which is the same sort the
    # Latin square uses, so no new convention enters the engine.
    explicit = select_continuous_pairs(PAIRS, {"anchor_condition": "related"}, design,
                                       {"matching": {"tolerance_k": {}}})
    default = select_continuous_pairs(PAIRS, {}, design, {"matching": {"tolerance_k": {}}})
    assert list(default["stim"]["set"]) == list(explicit["stim"]["set"])


def test_a_pair_missing_its_anchor_row_is_an_error():
    partial = PAIRS[PAIRS["condition"] == "unrelated"].reset_index(drop=True)
    design = {
        "n_per_condition": 2,
        "continuous": {"predictor": "target.frequency", "controls": ["target.length"]},
        "match_on": ["target.length"],
    }
    with pytest.raises(ValueError, match="no 'related' row"):
        select_continuous_pairs(partial, {"anchor_condition": "related"}, design,
                                {"matching": {"tolerance_k": {}}})
