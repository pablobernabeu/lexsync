import hashlib
import math
import re

import numpy as np
import pandas as pd
import pytest
from helper_repo import repo_path

from lexsync.io_utils import read_config
from lexsync.matching import (
    _maha_metric,
    match_stimuli,
    resample_stimuli,
    select_continuous_stimuli,
)
from lexsync.querying import build_pool, load_lexicon
from lexsync.validation import _pearson, cohens_d


def _design():
    return {
        "name": "t", "language": "english", "n_per_condition": 10,
        "pool_filters": {"length": [3, 7], "frequency": [3.8, 7]},
        "conditions": [
            {"name": "high", "define_by": {"frequency": [5.2, 7.0]}},
            {"name": "low", "define_by": {"frequency": [3.8, 4.4]}},
        ],
        "match_on": ["length", "n_density", "old20"],
    }


def test_deterministic(schema, en_lexicon_path):
    lex = load_lexicon(en_lexicon_path, schema, "english")
    s1 = match_stimuli(lex, _design(), schema)
    s2 = match_stimuli(lex, _design(), schema)
    assert list(s1["word"]) == list(s2["word"])


def test_balanced_and_isolated(schema, en_lexicon_path):
    lex = load_lexicon(en_lexicon_path, schema, "english")
    s = match_stimuli(lex, _design(), schema)
    assert sorted(s["condition"].value_counts().tolist()) == [10, 10]
    hi = s.loc[s.condition == "high", "frequency"]
    lo = s.loc[s.condition == "low", "frequency"]
    assert hi.mean() > lo.mean()
    assert abs(cohens_d(s.loc[s.condition == "high", "length"],
                        s.loc[s.condition == "low", "length"])) < 0.3


def _confounded_design(method=None):
    # Neighbourhood density is intrinsically confounded with length and
    # frequency, so the per-anchor matcher leaves a residual on the controls.
    design = {
        "name": "tj", "language": "english", "n_per_condition": 20,
        "pool_filters": {"length": [3, 7], "frequency": [3.8, 7]},
        "conditions": [
            {"name": "dense", "define_by": {"n_density": [4, 100]}},
            {"name": "sparse", "define_by": {"n_density": [0, 1]}},
        ],
        "match_on": ["length", "frequency"],
    }
    if method is not None:
        design["matching"] = {"method": method}
    return design


def test_joint_cancels_control_confound(schema, en_lexicon_path):
    lex = load_lexicon(en_lexicon_path, schema, "english")
    s = match_stimuli(lex, _confounded_design(method="joint"), schema)
    # Conditions stay balanced and the manipulated dimension is separated.
    assert sorted(s["condition"].value_counts().tolist()) == [20, 20]
    dense_n = s.loc[s.condition == "dense", "n_density"]
    sparse_n = s.loc[s.condition == "sparse", "n_density"]
    assert dense_n.mean() > sparse_n.mean()
    # Joint matching equates the controls almost exactly...
    for dim in ("length", "frequency"):
        d_joint = abs(cohens_d(s.loc[s.condition == "dense", dim],
                               s.loc[s.condition == "sparse", dim]))
        assert d_joint < 0.1, (dim, d_joint)
    # ...and does so at least as tightly as the per-anchor matcher.
    s_std = match_stimuli(lex, _confounded_design(), schema)
    d_joint = abs(cohens_d(s.loc[s.condition == "dense", "length"],
                           s.loc[s.condition == "sparse", "length"]))
    d_std = abs(cohens_d(s_std.loc[s_std.condition == "dense", "length"],
                         s_std.loc[s_std.condition == "sparse", "length"]))
    assert d_joint <= d_std + 1e-9


def test_mahalanobis_matches_and_is_deterministic(schema, en_lexicon_path):
    lex = load_lexicon(en_lexicon_path, schema, "english")
    d = _design()
    d["matching"] = {"method": "mahalanobis"}
    s = match_stimuli(lex, d, schema)
    assert sorted(s["condition"].value_counts().tolist()) == [10, 10]
    assert s.loc[s.condition == "high", "frequency"].mean() > \
           s.loc[s.condition == "low", "frequency"].mean()
    # the covariance-aware metric keeps the correlated controls balanced
    for dim in ("length", "n_density", "old20"):
        assert abs(cohens_d(s.loc[s.condition == "high", dim],
                            s.loc[s.condition == "low", dim])) < 0.5, dim
    # deterministic within an engine (cross-engine identity is not guaranteed here)
    assert list(s["word"]) == list(match_stimuli(lex, d, schema)["word"])


def _maha_pool():
    # Six rows complete on all three dimensions, then one row missing each of the
    # first two. The complete rows correlate, so a metric that dropped them would
    # differ from the pinned one in every off-diagonal cell.
    nan = np.nan
    return np.array([[1.0, 2.0, 0.5], [2.0, 2.5, 1.5], [3.0, 2.0, 1.0],
                     [4.0, 3.5, 2.5], [5.0, 4.0, 2.0], [6.0, 5.5, 3.5],
                     [nan, 3.0, 2.0], [3.5, nan, 1.0]])


# The inverse of the six complete rows' correlation matrix plus the 1e-6 ridge. The
# same values are pinned in test-matching.R, so the two engines' metrics agree to 1e-9.
_MAHA_COMPLETE_CASE = np.array([
    [6.508789703372, -4.641761938509, -1.404061170998],
    [-4.641761938509, 12.925495086475, -8.100175947949],
    [-1.404061170998, -8.100175947949, 9.918090174968],
])


def test_mahalanobis_correlations_come_from_complete_rows():
    """np.corrcoef returns NaN for every pair involving a column with a missing value,
    and _maha_metric read NaN as no correlation, so such a dimension lost all its
    correlations and entered the distance as an independent term. The correlations
    now come from the rows complete on every matched dimension. Pinned identically in
    test-matching.R."""
    metric = _maha_metric(_maha_pool())
    assert np.allclose(metric, _MAHA_COMPLETE_CASE, rtol=0, atol=1e-9)


def test_mahalanobis_refuses_a_pool_with_too_few_complete_rows():
    """k dimensions need k + 2 complete rows here. Twinned with test-matching.R."""
    z = _maha_pool()[[0, 1, 2, 3, 6, 7]]          # four complete rows of three dimensions
    with pytest.raises(ValueError, match=r"needs at least 5 items complete on the matched "
                                         r"dimensions to estimate their correlations, but "
                                         r"the pool has 4\."):
        _maha_metric(z)


def test_optimal_matches_confound_and_is_deterministic(schema, en_lexicon_path):
    lex = load_lexicon(en_lexicon_path, schema, "english")
    s = match_stimuli(lex, _confounded_design(method="optimal"), schema)
    assert sorted(s["condition"].value_counts().tolist()) == [20, 20]
    assert s.loc[s.condition == "dense", "n_density"].mean() > \
           s.loc[s.condition == "sparse", "n_density"].mean()
    # optimal assignment equates the controls tightly, like joint
    for dim in ("length", "frequency"):
        assert abs(cohens_d(s.loc[s.condition == "dense", dim],
                            s.loc[s.condition == "sparse", dim])) < 0.15, dim
    assert list(s["word"]) == list(
        match_stimuli(lex, _confounded_design(method="optimal"), schema)["word"])


def _continuous_design():
    return {
        "name": "cont", "language": "english", "n_per_condition": 40,
        "pool_filters": {"length": [3, 8], "frequency": [3.8, 7.0]},
        "continuous": {"predictor": "frequency",
                       "controls": ["length", "n_density", "old20"]},
        "match_on": ["length", "n_density", "old20"],
        "matching": {"tolerance_k": {"length": 1.5, "n_density": 1.5, "old20": 1.5}},
    }


def _continuous_pool(schema, en_lexicon_path):
    # The bundled example lexicon already carries n_density and old20.
    lex = load_lexicon(en_lexicon_path, schema, "english")
    return build_pool(lex, _continuous_design()["pool_filters"])


def test_select_continuous_spans_and_decorrelates(schema, en_lexicon_path):
    pool = _continuous_pool(schema, en_lexicon_path)
    s = select_continuous_stimuli(pool, _continuous_design(), schema)
    assert (s["condition"] == "continuous").all()
    assert list(s["set"]) == list(range(1, len(s) + 1))
    # banding holds the controls low-correlated with the predictor (a loose
    # sanity bound on the small example lexicon; the full corpus reaches ~0.17)
    for c in ("length", "n_density", "old20"):
        assert abs(_pearson(s["frequency"].to_numpy(), s[c].to_numpy())) < 0.6, c
    # deterministic within an engine
    assert list(s["word"]) == list(
        select_continuous_stimuli(pool, _continuous_design(), schema)["word"])


def test_select_continuous_driven_by_byte_order_not_row_order(schema, en_lexicon_path):
    pool = _continuous_pool(schema, en_lexicon_path)
    a = select_continuous_stimuli(pool, _continuous_design(), schema)
    b = select_continuous_stimuli(pool.iloc[::-1].reset_index(drop=True),
                                  _continuous_design(), schema)
    assert set(a["word"]) == set(b["word"])


def test_select_continuous_requires_match_on_equals_controls(schema, en_lexicon_path):
    """The two keys state one contract twice, so a design where they disagree is
    ambiguous about which dimensions are actually held constant. The message is matched
    as well as the type: any other ValueError would otherwise pass this test."""
    pool = _continuous_pool(schema, en_lexicon_path)
    d = _continuous_design()
    d["match_on"] = ["length", "n_density"]     # short of continuous.controls
    with pytest.raises(ValueError, match="match_on must equal"):
        select_continuous_stimuli(pool, d, schema)


def test_select_continuous_requires_at_least_one_control(schema, en_lexicon_path):
    """With no control there is nothing held constant, and an even spread over the
    predictor alone would still be recorded as a controlled selection. Twinned with
    test-matching.R."""
    pool = _continuous_pool(schema, en_lexicon_path)
    d = _continuous_design()
    d["continuous"]["controls"] = []
    d["match_on"] = []
    with pytest.raises(ValueError, match="at least one control"):
        select_continuous_stimuli(pool, d, schema)


def test_select_continuous_rejects_predictor_in_controls(schema, en_lexicon_path):
    pool = _continuous_pool(schema, en_lexicon_path)
    d = _continuous_design()
    d["continuous"]["controls"] = ["frequency", "length"]   # predictor is a control
    d["match_on"] = ["frequency", "length"]
    with pytest.raises(ValueError, match="must not also appear"):
        select_continuous_stimuli(pool, d, schema)


def _tiny_schema():
    return {"matching": {"method": "standardised_euclidean", "tolerance_k": {}}}


def _na_pool():
    # The two missing-concreteness rows lead the low subpool deliberately: a matcher
    # that ranks a NaN distance by row order rather than last would pick them first.
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6, 7, 8],
        "word": ["lac", "lad", "laa", "lab", "laz", "hab", "hac", "had"],
        "frequency": [2.0, 2.5, 1.0, 1.5, 3.0, 5.0, 6.0, 7.0],
        "concreteness": [np.nan, np.nan, 3.0, 2.95, 9.0, 3.0, 3.1, 2.9],
    })


def _na_design(n=3):
    return {
        "name": "na", "language": "english", "n_per_condition": n,
        "conditions": [
            {"name": "high", "define_by": {"frequency": [5.0, 7.0]}},
            {"name": "low", "define_by": {"frequency": [1.0, 3.0]}},
        ],
        "match_on": ["concreteness"],
    }


def test_missing_dimension_rows_are_dropped_and_ranked_last():
    # Pins the same contract as test-matching.R: only two low candidates fall inside
    # the anchor window, so the window relaxes, and the NaN rows must never be chosen
    # ahead of a real one. The R and Python engines must agree word for word.
    s = match_stimuli(_na_pool(), _na_design(), _tiny_schema())
    assert list(s.loc[s.condition == "high", "word"]) == ["hab", "hac", "had"]
    assert list(s.loc[s.condition == "low", "word"]) == ["laa", "lab", "laz"]
    assert not s["concreteness"].isna().any()


def test_undersized_condition_raises_instead_of_duplicating():
    # Five anchors but only two low candidates: the greedy assignment would exhaust
    # the low pool and re-pick its first word for sets 3 to 5.
    pool = pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6, 7],
        "word": ["laa", "lab", "hab", "hac", "had", "hae", "haf"],
        "frequency": [1.0, 1.5, 5.0, 5.5, 6.0, 6.5, 7.0],
        "concreteness": [3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0],
    })
    with pytest.raises(ValueError, match="condition 'low' has only 2 candidate"):
        match_stimuli(pool, _na_design(n=5), _tiny_schema())


def test_na_depleted_condition_raises_instead_of_duplicating():
    # The raw row count clears n_per_condition, but only two rows carry the matched
    # dimension. The other three are excluded before matching, so two candidates
    # face four anchors and the matcher raises rather than re-picking them. Pinned
    # identically in test-matching.R.
    pool = pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "word": ["laa", "lab", "lac", "lad", "lae", "hab", "hac", "had", "hae"],
        "frequency": [1.0, 1.5, 2.0, 2.5, 3.0, 5.0, 5.5, 6.0, 6.5],
        "concreteness": [3.0, 3.1, np.nan, np.nan, np.nan, 3.0, 3.1, 2.9, 3.2],
    })
    with pytest.raises(ValueError, match="condition 'low' has only 2 candidate"):
        match_stimuli(pool, _na_design(n=4), _tiny_schema())


def test_single_item_anchor_relaxes_rather_than_selecting_na():
    # An anchor of one item gives sd = NA, so every tolerance bound is NaN and each
    # comparison is False: the window relaxes and a real word is selected. The R engine
    # reaches the same row only because keep[is.na(keep)] <- FALSE resolves the NA the
    # bounds introduce; test-matching.R pins this same expectation.
    pool = pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "word": ["aaa", "bbb", "ccc", "ddd", "eee"],
        "frequency": [1.0, 2.0, 3.0, 4.0, 5.0],
        "concreteness": [3.0, 3.1, 3.2, 3.3, 3.4],
    })
    design = {
        "name": "one", "language": "english", "n_per_condition": 1,
        "conditions": [
            {"name": "high", "define_by": {"frequency": [1.0, 1.0]}},
            {"name": "low", "define_by": {"frequency": [2.0, 5.0]}},
        ],
        "match_on": ["concreteness"],
    }
    s = match_stimuli(pool, design, _tiny_schema())
    assert list(s.loc[s.condition == "low", "word"]) == ["bbb"]
    assert not s["word"].isna().any()


# ---- candidates missing a matched dimension ----------------------------------
# Twinned with test-matching.R, which pins the same words, counts and messages.

def _x_pool(rows):
    # rows: (word, frequency, x). Condition A spans frequency 5 to 7 and B 1 to 3.
    df = pd.DataFrame(rows, columns=["word", "frequency", "x"])
    df.insert(0, "id", range(1, len(df) + 1))
    return df


_B_ROWS = [("eagle", 2.0, 1.1), ("fig", 2.1, 2.1), ("grape", 2.2, 3.1),
           ("hat", 2.3, 0.5), ("igloo", 2.4, 2.6), ("jam", 2.5, 1.6)]


def _x_design(n, **matching):
    return {
        "name": "x", "language": "english", "n_per_condition": n,
        "conditions": [
            {"name": "A", "define_by": {"frequency": [5.0, 7.0]}},
            {"name": "B", "define_by": {"frequency": [1.0, 3.0]}},
        ],
        "match_on": ["x"],
        **({"matching": matching} if matching else {}),
    }


def _x_schema():
    return {"matching": {"method": "standardised_euclidean", "tolerance_k": {"x": 2.0}}}


def test_an_incomplete_anchor_never_reuses_a_candidate():
    # cloud lacks x. Used candidates were set to Inf and a missing distance ranked
    # after Inf, so cloud re-picked eagle and the run stopped with a false
    # 'overlapping conditions' error. cloud is now excluded before the anchor spread.
    pool = _x_pool([("apple", 6.0, 1.0), ("brick", 6.1, 2.0), ("cloud", 6.2, np.nan),
                    ("drum", 6.3, 3.0)] + _B_ROWS)
    with pytest.raises(ValueError, match="4 sets per condition were requested but only 3"):
        match_stimuli(pool, _x_design(4), _x_schema())
    s = match_stimuli(pool, _x_design(4, shortfall="allow"), _x_schema())
    assert list(s.loc[s.condition == "A", "word"]) == ["apple", "brick", "drum"]
    assert list(s.loc[s.condition == "B", "word"]) == ["eagle", "fig", "grape"]
    assert s.attrs["audit"]["incomplete_dropped"] == [{"condition": "A", "n": 1}]


def test_an_incomplete_first_anchor_is_excluded():
    # apple lacks x and comes first in the anchor spread. Its distance to every
    # candidate was missing, so the byte-first word in the window, fig, became its
    # counterpart.
    pool = _x_pool([("apple", 6.0, np.nan), ("brick", 6.1, 2.0), ("cloud", 6.2, 2.5),
                    ("drum", 6.3, 3.0)] + _B_ROWS)
    s = match_stimuli(pool, _x_design(3), _x_schema())
    assert list(s.loc[s.condition == "A", "word"]) == ["brick", "cloud", "drum"]
    assert list(s.loc[s.condition == "B", "word"]) == ["fig", "igloo", "grape"]
    assert not s["x"].isna().any()
    assert s.attrs["audit"]["incomplete_dropped"] == [{"condition": "A", "n": 1}]


def _joint_x_pool():
    # Condition A has three complete rows and two that lack x. All six rows of B are
    # complete.
    return _x_pool([("aa", 6.0, 1.0), ("ab", 6.1, 2.0), ("ac", 6.2, 3.0),
                    ("ad", 6.3, np.nan), ("ae", 6.4, np.nan)] + _B_ROWS)


def _pairs(s):
    by_set = s.groupby("set")["word"].apply(list)
    return sorted(tuple(w) for w in by_set)


def test_joint_reports_a_shortfall_instead_of_pairing_incomplete_rows():
    # A missing cost sorted after every real one, so once the complete pairs ran out
    # joint paired ad, which lacks x, to reach n.
    with pytest.raises(ValueError, match="4 sets per condition were requested but only 3"):
        match_stimuli(_joint_x_pool(), _x_design(4, method="joint"), _x_schema())
    s = match_stimuli(_joint_x_pool(), _x_design(4, method="joint", shortfall="allow"),
                      _x_schema())
    assert _pairs(s) == [("aa", "eagle"), ("ab", "fig"), ("ac", "grape")]
    assert s.attrs["audit"]["incomplete_dropped"] == [{"condition": "A", "n": 2}]


def test_optimal_selects_cleanly_with_an_incomplete_row():
    # A missing cost reached the assignment solver, which refused it with an error
    # that differed between the engines.
    pytest.importorskip("scipy")
    s = match_stimuli(_joint_x_pool(), _x_design(3, method="optimal"), _x_schema())
    assert _pairs(s) == [("aa", "eagle"), ("ab", "fig"), ("ac", "grape")]
    assert s.attrs["audit"]["incomplete_dropped"] == [{"condition": "A", "n": 2}]


def test_a_condition_left_without_complete_candidates_is_refused_by_name():
    # Every low candidate lacks the matched dimension. Without the check the
    # condition would be reported as having no candidates, although its window
    # holds two words.
    pool = pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "word": ["hab", "hac", "had", "laa", "lab"],
        "frequency": [5.0, 6.0, 7.0, 1.0, 2.0],
        "concreteness": [3.0, 3.1, 2.9, np.nan, np.nan],
    })
    with pytest.raises(ValueError, match=r"condition 'low' has no candidates complete on "
                                         r"the matched dimensions \(2 lacked a value\)"):
        match_stimuli(pool, _na_design(n=2), _tiny_schema())


def test_verbose_matching_reports_the_excluded_candidates(capsys):
    # The console reports the exclusion as it happens, as it reports a relaxed window.
    pool = _x_pool([("apple", 6.0, np.nan), ("brick", 6.1, 2.0), ("cloud", 6.2, 2.5),
                    ("drum", 6.3, 3.0)] + _B_ROWS)
    match_stimuli(pool, _x_design(3), _x_schema(), verbose=True)
    assert ("lexsync: dropped 1 candidate(s) of condition 'A' missing a matched "
            "dimension.") in capsys.readouterr().out


def test_a_within_condition_repeat_is_reported_as_an_internal_error():
    # A repeat inside one condition is a defect of the matcher, which used to be
    # reported as overlapping conditions.
    from lexsync.matching import _assert_distinct_words
    out = pd.DataFrame({"word": ["apple", "apple", "eagle", "fig"],
                        "condition": ["A", "A", "B", "B"]})
    with pytest.raises(ValueError, match=r"lexsync: internal error: condition 'A' "
                                         r"selected the word 'apple' more than once; "
                                         r"please report this\."):
        _assert_distinct_words(out)


def _continuous_x_pool():
    # 50 words of one length, 20 of them (40%) without x. The other 30 values of x
    # are distinct, so the spread has no ties to break.
    i = np.arange(50)
    x = ((37 * i) % 50) / 10
    x[(i % 5) < 2] = np.nan
    return pd.DataFrame({"id": i + 1, "word": ["w%03d" % k for k in i],
                         "frequency": 4.0, "length": 4, "x": x})


def _continuous_x_design():
    return {"name": "cx", "language": "english", "n_per_condition": 10,
            "continuous": {"predictor": "x", "controls": ["length"]},
            "match_on": ["length"]}


def test_the_continuous_selector_excludes_rows_missing_the_predictor():
    # A missing predictor sorted last and the even spread always takes the last
    # row, so 4 of the 10 items selected here lacked it.
    s = select_continuous_stimuli(_continuous_x_pool(), _continuous_x_design(),
                                  _tiny_schema())
    assert list(s["word"]) == ["w023", "w038", "w003", "w014", "w029",
                               "w044", "w009", "w047", "w012", "w027"]
    assert not s["x"].isna().any()
    assert s.attrs["audit"]["incomplete_dropped"] == [{"condition": "continuous", "n": 20}]


def test_a_continuous_pool_without_a_complete_row_is_refused():
    pool = _continuous_x_pool().assign(x=np.nan)
    with pytest.raises(ValueError, match=r"no item in the pool is complete on the "
                                         r"predictor and the controls \(50 lacked a "
                                         r"value\)"):
        select_continuous_stimuli(pool, _continuous_x_design(), _tiny_schema())


def test_a_selection_does_not_inherit_an_audit_from_its_pool():
    # pandas carries attrs through a row subset, and through pd.concat when every part
    # holds the same. An audit already on the pool therefore reached the result as if
    # this selection had made it, whatever the method. R carried it through the
    # continuous selector. Twinned with test-matching.R.
    stale = {"incomplete_dropped": [{"condition": "A", "n": 99}]}
    pool = _x_pool([("apple", 6.0, 1.0), ("brick", 6.1, 2.0), ("drum", 6.2, 3.0)]
                   + _B_ROWS)
    pool.attrs["audit"] = stale
    assert "audit" not in match_stimuli(pool, _x_design(3), _x_schema()).attrs
    cpool = _continuous_x_pool().dropna(subset=["x"])
    cpool.attrs["audit"] = stale
    sel = select_continuous_stimuli(cpool, _continuous_x_design(), _tiny_schema())
    # A continuous selection always records its control windows, and nothing else here.
    assert list(sel.attrs["audit"]) == ["control_windows"]


def test_the_continuous_selector_records_its_windows_and_the_pools_spread():
    """The windows are mean +/- k SD of the first pass, and the pool's SD is that of the
    complete candidates, so the report can set each control's realised SD against it.
    Pinned identically in test-matching.R."""
    pool = pd.DataFrame({"word": ["w%02d" % i for i in range(12)],
                         "x": [float(i) for i in range(12)],
                         "length": [3, 4, 5, 6] * 3})
    design = {"name": "cw", "language": "english", "n_per_condition": 4,
              "continuous": {"predictor": "x", "controls": ["length"]},
              "match_on": ["length"]}
    sel = select_continuous_stimuli(pool, design, _tiny_schema())
    # The first pass takes x = 0, 4, 7 and 11, whose lengths 3, 3, 6 and 6 have mean
    # 4.5 and SD sqrt(3); k defaults to 2.
    [w] = sel.attrs["audit"]["control_windows"]
    assert w["dimension"] == "length"
    assert math.isclose(w["low"], 4.5 - 2 * math.sqrt(3), rel_tol=1e-12)
    assert math.isclose(w["high"], 4.5 + 2 * math.sqrt(3), rel_tol=1e-12)
    assert math.isclose(w["pool_sd"], math.sqrt(15 / 11), rel_tol=1e-12)


def test_a_resampled_selection_records_the_first_replicates_exclusions():
    # The first replicate draws on the whole pool, so its exclusions are recorded, and
    # only it relaxes a window here, which is not. pd.concat dropped an audit that
    # differed between replicates while R's rbind kept the first replicate's, window
    # relaxation included, so the two engines returned different records. Twinned with
    # test-matching.R.
    pool = _x_pool([("ace", 6.0, 1.0), ("bay", 6.1, 0.0), ("cod", 6.2, 5.0),
                    ("dew", 6.3, 1.0), ("elk", 6.4, np.nan), ("fir", 2.0, 0.2),
                    ("gem", 2.1, 0.4), ("hop", 2.2, 4.8), ("ink", 2.3, 4.6),
                    ("jot", 2.4, 2.0), ("kin", 2.5, np.nan)])
    s = resample_stimuli(pool, _x_design(2), _x_schema(), 2)
    assert list(s["word"]) == ["ace", "dew", "gem", "fir", "bay", "cod", "jot", "hop"]
    assert s.attrs["audit"] == {"incomplete_dropped": [{"condition": "A", "n": 1},
                                                      {"condition": "B", "n": 1}]}


def test_unknown_method_raises(schema, en_lexicon_path):
    lex = load_lexicon(en_lexicon_path, schema, "english")
    d = _design()
    d["matching"] = {"method": "jiont"}
    with pytest.raises(ValueError, match="unknown matching method 'jiont'"):
        match_stimuli(lex, d, schema)


def test_joint_rejects_designs_without_exactly_two_conditions(schema, en_lexicon_path):
    lex = load_lexicon(en_lexicon_path, schema, "english")
    d = _design()
    d["matching"] = {"method": "joint"}
    d["conditions"].append({"name": "mid", "define_by": {"frequency": [4.4, 5.2]}})
    with pytest.raises(ValueError, match="requires exactly two conditions"):
        match_stimuli(lex, d, schema)


def _resample_design():
    return {
        "name": "r", "language": "english", "n_per_condition": 5,
        "pool_filters": {"length": [3, 7], "frequency": [3.8, 7]},
        "conditions": [
            {"name": "high", "define_by": {"frequency": [5.0, 7.0]}},
            {"name": "low", "define_by": {"frequency": [3.8, 4.4]}},
        ],
        "match_on": ["length"],
    }


def test_resample_produces_disjoint_matched_sets(schema, en_lexicon_path):
    lex = load_lexicon(en_lexicon_path, schema, "english")
    pool = build_pool(lex, _resample_design()["pool_filters"])
    s = resample_stimuli(pool, _resample_design(), schema, 3)
    assert sorted(s["replicate"].unique()) == [1, 2, 3]
    # each replicate is balanced and the manipulation is separated
    for _, g in s.groupby("replicate"):
        assert sorted(g["condition"].value_counts().tolist()) == [5, 5]
        assert g.loc[g.condition == "high", "frequency"].mean() > \
               g.loc[g.condition == "low", "frequency"].mean()
    # no item is reused across the disjoint sets
    words = {r: set(g["word"]) for r, g in s.groupby("replicate")}
    assert len(words[1] & words[2]) == 0
    assert len(words[1] & words[3]) == 0
    assert len(words[2] & words[3]) == 0


# ---- shortfall and tolerance policies, guards -------------------------------
# Twinned with test-matching.R: every fixture, expectation and message below
# must stay in step with the R suite.

def _small_pool():
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6, 7, 8],
        "word": ["haa", "hab", "hac", "laa", "lab", "lac", "lad", "lae"],
        "frequency": [5.0, 5.5, 6.0, 1.0, 1.5, 2.0, 2.5, 3.0],
        "concreteness": [3.0, 3.1, 2.9, 3.0, 3.1, 3.2, 2.8, 3.3],
    })


def _small_design(n, **matching):
    return {
        "name": "sf", "language": "english", "n_per_condition": n,
        "conditions": [
            {"name": "high", "define_by": {"frequency": [5.0, 7.0]}},
            {"name": "low", "define_by": {"frequency": [1.0, 3.0]}},
        ],
        "match_on": ["concreteness"],
        **({"matching": matching} if matching else {}),
    }


def test_shortfall_errors_by_default():
    # Three anchor candidates cannot honour n = 5; a silent shrink would change the
    # design that was planned without the design's consent.
    with pytest.raises(ValueError, match="5 sets per condition were requested but only 3"):
        match_stimuli(_small_pool(), _small_design(5), _tiny_schema())


def test_shortfall_allow_accepts_the_shrink():
    s = match_stimuli(_small_pool(), _small_design(5, shortfall="allow"), _tiny_schema())
    assert sorted(s["condition"].value_counts().tolist()) == [3, 3]


def test_unknown_shortfall_policy_raises():
    with pytest.raises(ValueError, match="unknown shortfall policy 'maybe'"):
        match_stimuli(_small_pool(), _small_design(3, shortfall="maybe"), _tiny_schema())


def test_joint_shortfall_errors_by_default():
    # At most three disjoint pairs exist, so n = 5 cannot be met.
    pool = _small_pool().iloc[[0, 1, 2, 3, 4, 5]].reset_index(drop=True)
    with pytest.raises(ValueError, match="5 sets per condition were requested but only 3"):
        match_stimuli(pool, _small_design(5, method="joint"), _tiny_schema())


def test_on_insufficient_tolerance_error_refuses_to_relax():
    # In the _na_pool scenario the low condition has too few candidates inside
    # the anchor window, which the default policy silently relaxes.
    d = _na_design()
    d["matching"] = {"on_insufficient_tolerance": "error"}
    with pytest.raises(ValueError, match="within tolerance but 3 are needed"):
        match_stimuli(_na_pool(), d, _tiny_schema())


def test_relaxation_is_recorded_in_the_audit():
    s = match_stimuli(_na_pool(), _na_design(), _tiny_schema())
    audit = s.attrs.get("audit")
    assert audit is not None
    rx = audit["window_relaxations"]
    assert len(rx) == 1
    assert rx[0]["condition"] == "low"
    assert isinstance(rx[0]["n_within_tolerance"], int)
    assert rx[0]["n_needed"] == 3


def test_a_complete_pool_records_no_exclusion():
    # Every shipped design has complete matched dimensions, so neither its audit nor
    # the datasheet built from it may gain an entry.
    s = match_stimuli(_small_pool(), _small_design(3), _tiny_schema())
    assert "incomplete_dropped" not in s.attrs.get("audit", {})


def _overlapping_design(n, method):
    # Both conditions admit the whole pool, so every word sits in both subpools
    # and its self-pair costs exactly zero.
    return {
        "name": "ov", "language": "english", "n_per_condition": n,
        "conditions": [
            {"name": "a", "define_by": {"frequency": [1.0, 7.0]}},
            {"name": "b", "define_by": {"frequency": [1.0, 7.0]}},
        ],
        "match_on": ["concreteness"],
        "matching": {"method": method, "shortfall": "allow"},
    }


def test_joint_never_pairs_a_word_with_itself():
    s = match_stimuli(_small_pool(), _overlapping_design(3, "joint"), _tiny_schema())
    assert not s["word"].duplicated().any()
    for _, g in s.groupby("set"):
        assert g["word"].nunique() == 2


def test_optimal_never_pairs_a_word_with_itself():
    pytest.importorskip("scipy")
    s = match_stimuli(_small_pool(), _overlapping_design(3, "optimal"), _tiny_schema())
    assert not s["word"].duplicated().any()
    for _, g in s.groupby("set"):
        assert g["word"].nunique() == 2


def test_misspelt_define_by_raises_instead_of_widening():
    d = _small_design(3)
    d["conditions"][1]["define_by"] = {"frequnecy": [1.0, 3.0]}
    with pytest.raises(ValueError, match="dimension 'frequnecy' in condition 'low'"):
        match_stimuli(_small_pool(), d, _tiny_schema())


def test_a_condition_without_define_by_draws_on_the_whole_pool():
    # The R engine's NULL define_by falls back to the whole pool (and, for the
    # anchor, to ordering by 'frequency'); a bare KeyError here meant Python
    # crashed on a design R accepted. The words are pinned identically in
    # test-matching.R, so the two engines select the same stimuli.
    d = _small_design(3)
    d["conditions"][1] = {"name": "rest"}
    s = match_stimuli(_small_pool(), d, _tiny_schema())
    assert list(s.loc[s.condition == "high", "word"]) == ["haa", "hab", "hac"]
    assert list(s.loc[s.condition == "rest", "word"]) == ["laa", "lab", "lad"]
    # An anchor without define_by orders by the fallback dimension.
    d = _small_design(3)
    d["conditions"][0] = {"name": "any"}
    d["conditions"][1] = {"name": "low", "define_by": {"frequency": [1.0, 3.0]}}
    s = match_stimuli(_small_pool(), d, _tiny_schema())
    assert list(s.loc[s.condition == "any", "word"]) == ["laa", "lad", "hac"]
    assert list(s.loc[s.condition == "low", "word"]) == ["lab", "lac", "lae"]


def test_duplicate_condition_names_raise():
    d = _small_design(3)
    d["conditions"][1]["name"] = "high"
    with pytest.raises(ValueError, match="condition name 'high' appears more than once"):
        match_stimuli(_small_pool(), d, _tiny_schema())


def test_negative_tolerance_raises():
    with pytest.raises(ValueError, match="tolerance_k for dimension 'concreteness' is negative"):
        match_stimuli(_small_pool(),
                      _small_design(3, tolerance_k={"concreteness": -1}),
                      _tiny_schema())


def test_missing_conditions_raise():
    d = _small_design(3)
    del d["conditions"]
    with pytest.raises(ValueError, match="the design has no conditions"):
        match_stimuli(_small_pool(), d, _tiny_schema())


def test_a_missing_or_empty_match_on_is_refused():
    """Without match_on the R engine scored every candidate at distance zero and
    returned the byte-first words; with an empty list both engines did, under every
    anchored method. Pinned identically in test-matching.R."""
    msg = "a matched design needs `match_on` naming at least one dimension"
    for method in ("standardised_euclidean", "joint", "mahalanobis"):
        d = _small_design(3, method=method)
        del d["match_on"]
        with pytest.raises(ValueError, match=msg):
            match_stimuli(_small_pool(), d, _tiny_schema())
        d["match_on"] = []
        with pytest.raises(ValueError, match=msg):
            match_stimuli(_small_pool(), d, _tiny_schema())


def test_a_whole_float_n_is_accepted_by_both_selectors(schema, en_lexicon_path):
    """`4.0` raised a TypeError here and ran in R. Pinned identically in
    test-matching.R."""
    s = match_stimuli(_small_pool(), _small_design(3.0), _tiny_schema())
    assert s["set"].tolist() == [1, 2, 3, 1, 2, 3]
    d = dict(_continuous_design(), n_per_condition=10.0)
    c = select_continuous_stimuli(_continuous_pool(schema, en_lexicon_path), d, schema)
    assert len(c) == 10


def test_n_per_condition_zero_is_refused_by_both_selectors(schema, en_lexicon_path):
    """`or` read a configured 0 as absent, so the selectors returned their default
    sizes (40 and 60 rows), or n_per_cell when it was set. Pinned identically in
    test-matching.R."""
    msg = "n_per_condition must be a positive whole number"
    pool = _continuous_pool(schema, en_lexicon_path)
    for extra in ({}, {"n_per_cell": 3}):
        with pytest.raises(ValueError, match=msg):
            match_stimuli(_small_pool(), dict(_small_design(0), **extra), _tiny_schema())
        with pytest.raises(ValueError, match=msg):
            select_continuous_stimuli(pool, dict(_continuous_design(), n_per_condition=0,
                                                 **extra), schema)


def _null_tolerance_pool():
    # The anchors' concreteness has mean 3 and SD 1, so k = 0.01 admits one low
    # candidate and relaxes the window, while k = 2 admits three and does not.
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6, 7],
        "word": ["haa", "hab", "hac", "laa", "lab", "lac", "lad"],
        "frequency": [5.0, 5.5, 6.0, 1.0, 1.5, 2.0, 2.5],
        "concreteness": [2.0, 3.0, 4.0, 2.5, 3.0, 3.5, 9.0],
    })


def test_a_null_tolerance_is_read_as_modifylist_reads_it():
    """A null in the schema's tolerance_k is dropped and k falls back to 2; a null in
    the design's deletes the schema's value. This engine raised a TypeError on
    either. Pinned identically in test-matching.R."""
    tight = {"matching": {"tolerance_k": {"concreteness": 0.01}}}
    relaxed = match_stimuli(_null_tolerance_pool(), _small_design(3), tight)
    assert relaxed.attrs.get("audit") is not None
    deleted = match_stimuli(_null_tolerance_pool(),
                            _small_design(3, tolerance_k={"concreteness": None}), tight)
    assert deleted.attrs.get("audit") is None
    dropped = match_stimuli(_null_tolerance_pool(), _small_design(3),
                            {"matching": {"tolerance_k": {"concreteness": None}}})
    assert dropped.attrs.get("audit") is None
    assert list(dropped["word"]) == list(deleted["word"]) == [
        "haa", "hab", "hac", "laa", "lab", "lac"]


def test_a_schema_without_a_matching_block_is_accepted(schema, en_lexicon_path):
    """Both selectors subscripted schema['matching'] and raised KeyError on a schema
    that R reads without complaint. Pinned identically in test-matching.R."""
    s = match_stimuli(_small_pool(), _small_design(3), {})
    assert len(s) == 6
    c = select_continuous_stimuli(_continuous_pool(schema, en_lexicon_path),
                                  _continuous_design(), {})
    assert len(c) == 40


def test_selection_ignores_unused_columns_and_the_seed():
    # Metamorphic invariants: an inert extra column must not steer selection, and
    # the schema seed only ever reaches the shuffle keys, never the matcher.
    base = match_stimuli(_small_pool(), _small_design(3), _tiny_schema())
    with_extra = _small_pool().assign(unused_norm=[9.9, 1.2, 5.5, 0.1, 7.7, 3.3, 2.2, 8.8])
    seeded = dict(_tiny_schema(), seed=99)
    assert list(match_stimuli(with_extra, _small_design(3), _tiny_schema())["word"]) == \
           list(base["word"])
    assert list(match_stimuli(_small_pool(), _small_design(3), seeded)["word"]) == \
           list(base["word"])


def test_matching_module_uses_the_shared_rounder():
    # The 9-dp distance and cost roundings must go through _round_dp_vec: native
    # np.round pairs with R's different decimal algorithm. The two remaining
    # native calls are the 0-dp even-spread index sites, which are half-even on
    # exactly representable halves in both engines and pinned by the committed
    # goldens -- converting them would change selections.
    import lexsync.matching as m
    src = open(m.__file__, encoding="utf-8").read()
    assert src.count("np.round(") == 2


# ---- the tie-break rule -------------------------------------------------------
# Lengths and neighbourhood counts are whole numbers and frequencies carry two
# decimals, so exact ties decide most picks. matching.tie_break chooses how: `hash`, the
# default, gives a tie to the smaller keyed SHA-256 of the word, and `bytes`, the rule of
# lexsync 0.1, to the spelling that sorts first. Twinned with test-matching.R, which
# pins the same keys, words and pairs.

def _digest(word):
    # Computed here and not through the package, so the expectations below do not
    # rest on the function under test.
    return hashlib.sha256(("lexsync-tie-v1|" + word).encode("utf-8")).hexdigest()


def test_the_tie_key_is_identical_across_engines():
    from lexsync.matching import _tie_keys
    assert _tie_keys(["cat", "año", "中文"]) == [
        "b9d1fe3608e2667c6c6782afccc91b43caeb9aede31bfb89e61407bb1def5df0",
        "a3eb8cd8d71694705bf6dee05bac085f3df1e93f9771978f55389420979d5f3c",
        "be465219474dd1ca446c19e4185cdc870f4e605cfd25e1f462c50aae7997bada",
    ]
    assert _tie_keys(["cat"]) == [_digest("cat")]


def _tie_pool():
    # Four B candidates lie at x = 1 and two at x = 3, as do the anchors, so every pick
    # is an exact tie at distance 0. The keyed hash reverses the spelling order of
    # bat, cat, dog and eel.
    return _x_pool([("kiwi", 6.0, 1.0), ("lime", 6.1, 1.0), ("plum", 6.2, 3.0),
                    ("bat", 2.0, 1.0), ("cat", 2.1, 1.0), ("dog", 2.2, 1.0),
                    ("eel", 2.3, 1.0), ("axe", 2.4, 3.0), ("dot", 2.5, 3.0)])


def test_hash_tie_break_orders_exact_ties_by_the_keyed_digest():
    pool = _tie_pool()
    by_bytes = match_stimuli(pool, _x_design(3, tie_break="bytes"), _x_schema())
    assert list(by_bytes.loc[by_bytes.condition == "B", "word"]) == ["bat", "cat", "axe"]
    by_hash = match_stimuli(pool, _x_design(3, tie_break="hash"), _x_schema())
    assert list(by_hash.loc[by_hash.condition == "A", "word"]) == ["kiwi", "lime", "plum"]
    expected = (sorted(["bat", "cat", "dog", "eel"], key=_digest)[:2]
                + sorted(["axe", "dot"], key=_digest)[:1])
    assert expected == ["eel", "dog", "dot"]
    assert list(by_hash.loc[by_hash.condition == "B", "word"]) == expected
    # The schema may set the rule, and a design's own setting overrides it.
    as_0_1 = {"matching": dict(_x_schema()["matching"], tie_break="bytes")}
    assert list(match_stimuli(pool, _x_design(3), as_0_1)["word"]) == list(by_bytes["word"])
    assert list(match_stimuli(pool, _x_design(3, tie_break="hash"), as_0_1)["word"]) == \
        list(by_hash["word"])


def test_the_tie_break_defaults_to_hash():
    # With no rule in the design or the schema, the keyed hash breaks exact ties. The
    # default was `bytes` until the demonstrations moved to the hash.
    from lexsync.matching import _resolve_tie_break
    assert _resolve_tie_break({}, {}) == "hash"
    pool = _tie_pool()
    by_default = match_stimuli(pool, _x_design(3), _x_schema())
    assert list(by_default["word"]) == list(
        match_stimuli(pool, _x_design(3, tie_break="hash"), _x_schema())["word"])
    assert list(by_default.loc[by_default.condition == "B", "word"]) == ["eel", "dog", "dot"]


def test_an_unknown_tie_break_rule_is_refused():
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: unknown tie_break policy 'alphabetical'. "
            "Known policies: hash, bytes.")):
        match_stimuli(_tie_pool(), _x_design(3, tie_break="alphabetical"), _x_schema())


def _tie_pairs_pool(a_x, b_x):
    # In spelling order A holds ash, beech, cedar and elm, which the keyed hash orders
    # beech, cedar, ash, elm, and B holds bat, cat, dog and eel, which it reverses.
    a_words = ["ash", "beech", "cedar", "elm"]
    b_words = ["bat", "cat", "dog", "eel"]
    rows = [(w, 6.0 + i / 10, x) for i, (w, x) in enumerate(zip(a_words, a_x, strict=True))]
    rows += [(w, 2.0 + i / 10, x) for i, (w, x) in enumerate(zip(b_words, b_x, strict=True))]
    return _x_pool(rows)


def test_hash_tie_break_orders_joint_pairs_by_hash_rank():
    # Every pair costs 0, so the pair order alone decides which items are kept.
    pool = _tie_pairs_pool([1.0] * 4, [1.0] * 4)
    by_bytes = match_stimuli(pool, _x_design(2, method="joint", tie_break="bytes"), _x_schema())
    assert _pairs(by_bytes) == [("ash", "bat"), ("beech", "cat")]
    assert sorted(["ash", "beech", "cedar", "elm"], key=_digest)[:2] == ["beech", "cedar"]
    assert sorted(["bat", "cat", "dog", "eel"], key=_digest)[:2] == ["eel", "dog"]
    by_hash = match_stimuli(pool, _x_design(2, method="joint", tie_break="hash"), _x_schema())
    assert _pairs(by_hash) == [("beech", "eel"), ("cedar", "dog")]
    assert list(by_hash.loc[by_hash.set == 1, "word"]) == ["beech", "eel"]


def test_hash_tie_break_decides_the_overlap_cap():
    # Every row lies at the same distance from the other condition's centroid, so the
    # tie-break alone decides which two rows of each condition survive the cap. A cap
    # that kept the first two rows by position would keep ash, beech, bat and cat, and
    # the hash order would then pair beech with cat.
    from lexsync.matching import _match_joint
    pool = _tie_pairs_pool([1.0] * 4, [1.0] * 4)
    a = pool[pool.frequency > 5].reset_index(drop=True)
    b = pool[pool.frequency < 5].reset_index(drop=True)
    centre, scale = np.array([0.0]), np.array([1.0])
    by_bytes = _match_joint([a, b], ["A", "B"], ["x"], centre, scale, 2, cap=2)
    assert _pairs(by_bytes) == [("ash", "bat"), ("beech", "cat")]
    by_hash = _match_joint([a, b], ["A", "B"], ["x"], centre, scale, 2, cap=2,
                           tie_break="hash")
    assert _pairs(by_hash) == [("beech", "eel"), ("cedar", "dog")]


def test_hash_tie_break_numbers_the_optimal_pairs_by_hash_rank():
    # Two pairs cost 0 and every other pair costs more, so the optimum is unique and
    # the two engines' solvers cannot differ on it. Both pairs cost the same, and the
    # tie-break alone decides which of them is set 1. Among several equally cheap sets
    # of pairs, which set is kept is the solver's choice, which is why this test no
    # longer asks the tie-break to decide that.
    pytest.importorskip("scipy")
    pool = _tie_pairs_pool([1.0, 2.0, 10.0, 20.0], [1.0, 2.0, 30.0, 40.0])
    by_bytes = match_stimuli(pool, _x_design(2, method="optimal", tie_break="bytes"),
                             _x_schema())
    assert _pairs(by_bytes) == [("ash", "bat"), ("beech", "cat")]
    assert list(by_bytes.loc[by_bytes.set == 1, "word"]) == ["ash", "bat"]
    by_hash = match_stimuli(pool, _x_design(2, method="optimal", tie_break="hash"),
                            _x_schema())
    assert _pairs(by_hash) == [("ash", "bat"), ("beech", "cat")]
    assert list(by_hash.loc[by_hash.set == 1, "word"]) == ["beech", "cat"]


# ---- exact optimal matching ---------------------------------------------------
# `optimal` selects the n pairs of least summed distance, the k-cardinality assignment
# problem, solved through a padded square assignment (Volgenant, 2004). Twinned with
# test-matching.R, which builds the same fixtures from the same formula and pins the
# same summed distance.

def _formula_pool(prefix, ks, shift=0.0):
    """Three continuous dimensions from fixed quadratic residues, so both engines build
    the same pool without a random number generator. Every intermediate is a whole
    number below 2^53, so the arithmetic is exact in both. A linear formula would repeat
    the same distance along every diagonal of the cost matrix."""
    k = np.asarray(ks, dtype=float)
    return pd.DataFrame({
        "word": [f"{prefix}{int(i):04d}" for i in k],
        "d1": ((k * k * 7919 + k * 13 + 1) % 10007) / 10007 + shift,
        "d2": ((k * k * 104729 + k * 7 + 3) % 10009) / 10009,
        "d3": ((k * k * 3571 + k * 3 + 5) % 10037) / 10037,
    })


_DIMS = ["d1", "d2", "d3"]


def _solve(method, a, b, n, dims=_DIMS, **kw):
    from lexsync.matching import _match_joint, _match_optimal
    fn = _match_optimal if method == "optimal" else _match_joint
    z = np.zeros(len(dims)), np.ones(len(dims))
    return fn([a, b], ["A", "B"], dims, z[0], z[1], n, **kw)


def _summed_distance(out, dims=_DIMS):
    a = out[out.condition == "A"].sort_values("set")[dims].to_numpy()
    b = out[out.condition == "B"].sort_values("set")[dims].to_numpy()
    return float(np.sqrt(((a - b) ** 2).sum(axis=1)).sum())


def _brute_force(a, b, n, dims=_DIMS):
    from itertools import combinations, permutations
    za, zb = a[dims].to_numpy(), b[dims].to_numpy()
    cost = np.sqrt(((za[:, None, :] - zb[None, :, :]) ** 2).sum(axis=2))
    return min(sum(cost[i, j] for i, j in zip(rows, cols, strict=True))
               for rows in combinations(range(len(a)), n)
               for cols in permutations(range(len(b)), n))


@pytest.mark.parametrize(("m0", "m1", "n"), [(6, 6, 3), (5, 7, 4)])
def test_optimal_equals_brute_force_on_small_problems(m0, m1, n):
    # The complete assignment kept its n cheapest pairs, which is not the cheapest set
    # of n pairs whenever the full assignment had to spend a good counterpart elsewhere.
    pytest.importorskip("scipy")
    a = _formula_pool("a", range(1, m0 + 1))
    b = _formula_pool("b", range(m0 + 1, m0 + m1 + 1))
    out = _solve("optimal", a, b, n)
    assert out["set"].nunique() == n
    assert abs(_summed_distance(out) - _brute_force(a, b, n)) <= 1e-9


# The summed distance of the optimal selection on the 300 + 300 fixture with n = 30,
# pinned identically in test-matching.R so the two engines agree to 1e-9. An
# independent padded solve over the unrounded costs gave the same value.
_OPTIMAL_SUM_300_N30 = 1.272647404213


@pytest.mark.parametrize("n", [30, 150])
def test_optimal_is_never_worse_than_joint(n):
    # Greedy joint matching came within a few per cent of the optimum, and the old
    # optimal was 1.15 to 2.5 times it.
    pytest.importorskip("scipy")
    a = _formula_pool("a", range(1, 301), shift=0.05)
    b = _formula_pool("b", range(301, 601))
    opt = _summed_distance(_solve("optimal", a, b, n))
    joint = _summed_distance(_solve("joint", a, b, n))
    assert opt <= joint + 1e-9
    if n == 30:
        assert abs(opt - _OPTIMAL_SUM_300_N30) <= 1e-9


def test_optimal_does_not_depend_on_the_pool_order():
    # Every pair costs 0, so the solver's preference among equal costs decides which
    # pairs are kept. Under bytes the subpools are put in spelling order first, so that
    # preference follows the spelling and not the order the rows arrived in.
    pytest.importorskip("scipy")
    pool = _tie_pairs_pool([1.0] * 4, [1.0] * 4)
    for rule in ("bytes", "hash"):
        design = _x_design(2, method="optimal", tie_break=rule)
        forward = match_stimuli(pool, design, _x_schema())
        backward = match_stimuli(pool.iloc[::-1].reset_index(drop=True), design, _x_schema())
        assert list(forward["word"]) == list(backward["word"]), rule


def test_optimal_fills_overlapping_conditions_with_distinct_words():
    # Every word sits in both conditions. Three zero-cost pairs exist only by using a
    # pair in both directions (haa with laa, laa with haa), which reuses both words. The
    # duplicate is dropped and a second solve over the unused words fills its place, so
    # the design gets its three sets under the default shortfall policy, as it does
    # under the other methods.
    pytest.importorskip("scipy")
    design = _overlapping_design(3, "optimal")
    design["matching"]["shortfall"] = "error"
    s = match_stimuli(_small_pool(), design, _tiny_schema())
    assert s["set"].nunique() == 3
    assert not s["word"].duplicated().any()
    # Which direction of a zero-cost pair the solver uses is a tie, so the two zero-cost
    # pairs are sets 1 and 2 in either order.
    pairs = [tuple(sorted(p)) for p in _pairs(s)]
    assert sorted(pairs[:2]) == [("haa", "laa"), ("hab", "lab")]


def test_optimal_fills_n_when_the_conditions_share_every_word():
    # With the same 300 words in both conditions, every pair costs the same in both
    # directions, and a single solve used about half of its pairs twice.
    pytest.importorskip("scipy")
    pool = _formula_pool("w", range(1, 301))
    for n in (30, 80):
        out = _solve("optimal", pool, pool, n)
        assert out["set"].nunique() == n
        assert not out["word"].duplicated().any()


# The shipped English designs as lexsync 0.1 ran them, on en.csv. Repository-coupled:
# the full lexicon lives in corpora/, not in the package, so these skip when the package
# is tested on its own.

@pytest.fixture(scope="module")
def en_corpus():
    schema = read_config(str(repo_path("config", "schema.yaml")))
    lexicon = load_lexicon(str(repo_path("corpora", "derived", "en.csv")), schema, "english")
    return schema, lexicon


def _as_in_0_1(name, tie_break=None):
    """A shipped design as lexsync 0.1 ran it. The demonstrations now read en_v2.csv,
    filter on its `nonstandard` column and leave out the words of an exclusion list.
    en.csv has no such column, and match_stimuli does not read exclude_words, so both
    are dropped here and the design runs on the en_corpus fixture's en.csv."""
    design = read_config(str(repo_path("config", f"design_{name}.yaml")))
    design["pool_filters"] = {k: v for k, v in design["pool_filters"].items()
                              if k != "nonstandard"}
    design.pop("exclude_words", None)
    if tie_break is not None:
        design["matching"] = dict(design.get("matching") or {}, tie_break=tie_break)
    return design


def _initial_share(words):
    words = list(words)
    return sum(w[:1] in ("a", "b") for w in words) / len(words)


def test_hash_tie_break_returns_freqcontrast_initials_to_the_pool_rate(en_corpus):
    # Under bytes, 61% of the low-frequency words begin with a or b, against 13% of the
    # condition's candidates. Under hash the share lies within 0.1 of the candidates',
    # and Cohen's d on each matched dimension moves by at most 0.01.
    schema, lexicon = en_corpus
    design = _as_in_0_1("en_freqcontrast", "bytes")
    pool = build_pool(lexicon, design["pool_filters"])
    low = next(c for c in design["conditions"] if c["name"] == "low_frequency")
    candidates = build_pool(pool, low["define_by"])
    by_bytes = match_stimuli(pool, design, schema)
    by_hash = match_stimuli(pool, _as_in_0_1("en_freqcontrast", "hash"), schema)
    share = _initial_share(by_hash.loc[by_hash.condition == "low_frequency", "word"])
    assert abs(share - _initial_share(candidates["word"])) <= 0.1
    for dim in design["match_on"]:
        d = [cohens_d(s.loc[s.condition == "high_frequency", dim],
                      s.loc[s.condition == "low_frequency", dim]) for s in (by_bytes, by_hash)]
        assert abs(d[0] - d[1]) <= 0.01, dim


def test_hash_tie_break_spreads_the_ndensity_dense_initials(en_corpus):
    # Under bytes every dense word of the joint design began with a or b (73 b, 7 a).
    schema, lexicon = en_corpus
    design = _as_in_0_1("en_ndensity", "hash")
    s = match_stimuli(build_pool(lexicon, design["pool_filters"]), design, schema)
    assert _initial_share(s.loc[s.condition == "dense_neighbourhood", "word"]) <= 0.25


# The selections lexsync 0.1.1 committed for the two designs, both engines alike, as the
# SHA-256 of their word|condition|set lines in byte order. The committed stimuli now come
# from the screened lexicon, so the old ones are pinned here. Pinned identically in
# test-matching.R.
_SELECTIONS_0_1_1 = {
    "en_freqcontrast": "f5a58e0486182d23309c921106c41fde9dd9533b1c990ef4c77b2a971b588595",
    "en_ndensity": "f266d1b7611890cfba586b61efa04066616acbb89a3134a42dba09a9e4490a8b",
}


def _selection_digest(s):
    lines = sorted(f"{w}|{c}|{int(k)}"
                   for w, c, k in zip(s["word"], s["condition"], s["set"], strict=True))
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def test_bytes_tie_break_reproduces_the_0_1_selections(en_corpus):
    # `bytes` must select again what lexsync 0.1.1 selected from en.csv, and the
    # default, now the keyed hash, must not.
    schema, lexicon = en_corpus
    for name, want in _SELECTIONS_0_1_1.items():
        for rule, reproduces in (("bytes", True), (None, False)):
            design = _as_in_0_1(name, rule)
            s = match_stimuli(build_pool(lexicon, design["pool_filters"]), design, schema)
            assert (_selection_digest(s) == want) is reproduces, (name, rule)
