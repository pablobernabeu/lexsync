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
