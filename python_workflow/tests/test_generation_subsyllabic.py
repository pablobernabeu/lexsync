"""The subsyllabic (Wuggy-style) pseudoword generator."""
import pytest

from lexsync.generation import (_legal, bigram_counts, build_constituent_inventory,
                                build_lexdec_stimuli, generate_pseudowords_subsyllabic,
                                segment_subsyllabic)
from lexsync.querying import build_pool, load_lexicon


def test_segmentation_worked_examples():
    assert segment_subsyllabic("bridge") == [
        ("onset", "br"), ("nucleus", "i"), ("coda", "d"), ("onset", "g"), ("nucleus", "e")]
    assert segment_subsyllabic("planet") == [
        ("onset", "pl"), ("nucleus", "a"), ("onset", "n"), ("nucleus", "e"), ("coda", "t")]
    assert segment_subsyllabic("strength") == [
        ("onset", "str"), ("nucleus", "e"), ("coda", "ngth")]
    assert segment_subsyllabic("a") == [("nucleus", "a")]
    assert segment_subsyllabic("crwth") == []          # no vowel run -> empty (caller falls back)


def test_inventory_is_order_independent():
    ref = ["bridge", "planet", "strength", "brake", "grape", "plane", "clip", "drum"]
    assert build_constituent_inventory(ref) == build_constituent_inventory(list(reversed(ref)))


def test_generate_subsyllabic_legal_nonword_length_preserved(schema, en_lexicon_path):
    lex = load_lexicon(en_lexicon_path, schema, "english")
    ref = lex["word"].tolist()
    base = build_pool(lex, {"length": [4, 7]})["word"].tolist()[:30]
    gen = generate_pseudowords_subsyllabic(base, ref)
    lexset = set(ref)
    bg = bigram_counts(ref)
    for w, pw in zip(gen["base_word"], gen["pseudoword"]):
        assert len(pw) == len(w)             # length preserved exactly
        assert pw not in lexset              # a novel non-word
        assert _legal(pw, bg)                # every bigram attested
    assert gen["pseudoword"].nunique() == len(gen)     # all distinct


def test_build_lexdec_unknown_method_raises(schema, en_lexicon_path):
    lex = load_lexicon(en_lexicon_path, schema, "english")
    pool = build_pool(lex, {"length": [4, 6]})
    with pytest.raises(ValueError, match="unknown pseudoword generation method"):
        build_lexdec_stimuli(pool, 10, reference_words=lex["word"].tolist(), method="invalid")
