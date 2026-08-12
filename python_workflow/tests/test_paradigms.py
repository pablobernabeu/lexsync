"""Trial-event model, pseudoword generation, item tables and counterbalancing."""
import pandas as pd
import pytest

from lexsync.counterbalancing import counterbalance
from lexsync.generation import (bigram_counts, build_lexdec_stimuli,
                                generate_pseudowords)
from lexsync.io_utils import clean_field
from lexsync.paradigms import (PARADIGMS, content_field, referenced_fields,
                               required_fields, resolve_events)
from lexsync.querying import build_pool, load_items, load_lexicon


# ---- the trial-event model ------------------------------------------------

def test_every_paradigm_resolves_to_typed_events():
    for name in PARADIGMS:
        events = resolve_events({"paradigm": name})
        assert events and all("type" in e for e in events)
        # required fields are exactly the paradigm fields plus any referenced ones
        assert set(PARADIGMS[name]["stimulus_fields"]) <= set(required_fields({"paradigm": name}))


def test_content_field_and_referenced_fields():
    assert content_field("{target}") == "target"
    assert content_field("+") is None
    events = resolve_events({"paradigm": "priming"})
    assert referenced_fields(events) == ["prime", "target"]


def test_explicit_events_override_paradigm():
    design = {"events": [{"type": "text", "content": "{w}", "duration_frames": 10}]}
    assert [e["type"] for e in resolve_events(design)] == ["text"]


# ---- pseudoword generation ------------------------------------------------

LEX = ["cat", "cap", "car", "can", "cab", "bat", "bad", "bag", "ban",
       "rat", "ran", "ram", "rag", "tan", "tap", "tar", "mat", "map", "man"]


def test_pseudowords_are_deterministic():
    a = generate_pseudowords(["cat", "bat", "rat"], LEX)
    b = generate_pseudowords(["cat", "bat", "rat"], LEX)
    assert list(a["pseudoword"]) == list(b["pseudoword"])


def test_pseudowords_are_legal_nonwords_of_matched_length():
    gen = generate_pseudowords(["cat", "bat", "rat", "man"], LEX)
    lex = set(LEX)
    for base, pw in zip(gen["base_word"], gen["pseudoword"], strict=True):
        assert pw not in lex                    # not a real word
        assert len(pw) == len(base)             # length preserved
        bg = bigram_counts(LEX)
        assert all(pw[i:i + 2] in bg for i in range(len(pw) - 1))  # orthographically legal
    assert len(set(gen["pseudoword"])) == len(gen)  # unique


def test_build_lexdec_stimuli_pairs_words_and_pseudowords(schema, en_lexicon_path):
    lex = load_lexicon(en_lexicon_path, schema, "english")
    pool = build_pool(lex, {"length": [4, 6], "frequency": [3.0, 6.5]})
    stim = build_lexdec_stimuli(pool, 15, reference_words=lex["word"].tolist())
    assert set(stim["condition"]) == {"word", "pseudoword"}
    assert (stim["condition"] == "word").sum() == (stim["condition"] == "pseudoword").sum()
    # paired by set, length matched within each set
    for _, g in stim.groupby("set"):
        assert g["length"].nunique() == 1


# ---- item tables and counterbalancing -------------------------------------

def test_load_items_validates_columns(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("item,prime\n1,nurse\n", encoding="utf-8")  # missing 'condition'
    with pytest.raises(ValueError):
        load_items(str(p), ["prime", "target"])


def test_clean_field_rejects_control_characters():
    with pytest.raises(ValueError):
        clean_field("ab\ncd", "target")          # newline
    with pytest.raises(ValueError):
        clean_field("ab\tcd", "target")          # tab
    assert clean_field("a clean, quoted 'item'", "x") == "a clean, quoted 'item'"


def test_load_items_rejects_crafted_item(tmp_path):
    p = tmp_path / "items.csv"
    p.write_text('item,condition,target\n1,a,"bad\ttab"\n', encoding="utf-8")
    with pytest.raises(ValueError):
        load_items(str(p), ["target"])


def test_latin_square_shows_each_item_once_per_list_balanced():
    items = pd.DataFrame({
        "item": [1, 1, 2, 2, 3, 3, 4, 4],
        "condition": ["related", "unrelated"] * 4,
        "prime": list("abcdefgh"), "target": ["x", "x", "y", "y", "z", "z", "w", "w"],
    })
    items["set"] = items["item"]
    design = {"paradigm": "priming", "counterbalance": {"lists": 2}}
    out = counterbalance(items, design, {"seed": 1})
    for _, lst in out.groupby("list"):
        assert lst["set"].nunique() == len(lst)              # each item once
        assert lst["target"].nunique() == len(lst)           # no target repeated
        assert set(lst["condition"]) == {"related", "unrelated"}  # both conditions present
        assert (lst["condition"] == "related").sum() == (lst["condition"] == "unrelated").sum()
