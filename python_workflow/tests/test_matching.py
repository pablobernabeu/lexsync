from lexsync.matching import match_stimuli
from lexsync.querying import load_lexicon
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
