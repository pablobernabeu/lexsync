import numpy as np
import pandas as pd
import pytest

from lexsync.matching import (match_stimuli, resample_stimuli,
                              select_continuous_stimuli)
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
    pool = _continuous_pool(schema, en_lexicon_path)
    d = _continuous_design()
    d["match_on"] = ["length", "n_density"]     # != continuous.controls
    with pytest.raises(ValueError):
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
    # dimension. The rest rank last on a NaN distance and are never assigned, so the
    # greedy pass would exhaust the usable rows and re-pick them. Pinned identically
    # in test-matching.R.
    pool = pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "word": ["laa", "lab", "lac", "lad", "lae", "hab", "hac", "had", "hae"],
        "frequency": [1.0, 1.5, 2.0, 2.5, 3.0, 5.0, 5.5, 6.0, 6.5],
        "concreteness": [3.0, 3.1, np.nan, np.nan, np.nan, 3.0, 3.1, 2.9, 3.2],
    })
    with pytest.raises(ValueError, match="condition 'low' has only 2 usable candidate"):
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
