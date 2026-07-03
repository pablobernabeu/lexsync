from lexsync.matching import match_stimuli, resample_stimuli
from lexsync.querying import build_pool, load_lexicon
from lexsync.validation import cohens_d


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
