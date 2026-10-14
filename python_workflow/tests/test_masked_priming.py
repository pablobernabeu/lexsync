"""Masked priming, the letter case of a text event, and the reproductions that use them.

The `priming` paradigm shows the prime, a '#####' mask and the target, with no forward
mask and both strings in the item table's case, and it ends in a separate response
window. It is backward-masked priming, yet it drove the Rastle, Davis and New (2004)
reproduction, and without a forward mask a brief prime is usually visible (Forster &
Davis, 1984). The Andrews (1989) reproduction had no nonwords, so neither ran as the
lexical decision it reproduces.

`masked_priming` shows a forward mask of hash marks as long as the longest prime or
target, a lower-case prime for three frames and an upper-case target that stays until
the response. The mask is sized from the trials when the experiments are written, and
the case is applied by the runners as they show the text, because R's toupper() leaves
'ß' as it is where Python and JavaScript give 'SS'. Twinned with
R_workflow/tests/testthat/test-masked-priming.R, by the same names.
"""
import hashlib
import json
import os
import re

import pandas as pd
import pytest
from helper_repo import repo_path

from lexsync.counterbalancing import counterbalance
from lexsync.io_utils import read_config
from lexsync.paradigms import PARADIGMS, required_fields, resolve_events
from lexsync.scripting import _json_r, export_experiments, render_events

# The registry as both engines serialise it: each paradigm by name, in byte order, with
# its fields, its recipe and its events. test-masked-priming.R pins the same digest, so a
# paradigm changed in one engine only fails both suites.
PARADIGMS_SHA256 = "caa39a2fba929cb8279de523db3d023b4db1fb0b60c24c39cf7e48bd245b090c"


def _registry_json():
    return _json_r([{"name": name, "stimulus_fields": list(p["stimulus_fields"]),
                     "counterbalance": p["counterbalance"], "events": p["events"]}
                    for name, p in sorted(PARADIGMS.items())])


def test_the_paradigm_registry_is_the_same_in_both_engines():
    digest = hashlib.sha256(_registry_json().encode("utf-8")).hexdigest()
    assert digest == PARADIGMS_SHA256


def test_masked_priming_shows_a_forward_mask_a_prime_and_an_upper_case_target():
    p = PARADIGMS["masked_priming"]
    assert p["stimulus_fields"] == ["prime", "target"]
    assert p["counterbalance"] == "latin_square_target"
    assert required_fields({"paradigm": "masked_priming"}) == ["prime", "target"]
    rendered = render_events(resolve_events({"paradigm": "masked_priming"}), {}, 60)
    assert rendered == [
        # Hash marks for 500 ms, as many as the longest prime or target has characters.
        {"type": "mask", "text": "#", "length_of": ["prime", "target"], "ms": 500},
        # Three frames at 60 Hz, with the prime's own code.
        {"type": "text", "field": "prime", "ms": 50, "trigger": 20, "case": "lower"},
        # On until a key or 2,000 ms after its onset, whichever comes first.
        {"type": "text", "field": "target", "ms": 2000, "trigger": "@condition_trigger",
         "case": "upper", "respond": {"keys": ["left", "right"], "timeout": 0}},
        {"type": "blank", "ms": 250},
    ]
    # The backward-masked paradigm is as it was.
    assert [e["type"] for e in PARADIGMS["priming"]["events"]] == [
        "fixation", "text", "mask", "text", "response", "blank"]
    assert "case" not in str(PARADIGMS["priming"]["events"])


def test_a_text_event_carries_its_case_to_the_runners():
    events = [{"type": "text", "content": "{prime}", "duration_ms": 50, "case": "lower"},
              {"type": "text", "content": "{target}", "duration_ms": 500, "case": "upper"},
              {"type": "text", "content": "{target}", "duration_ms": 500}]
    assert [e.get("case") for e in render_events(events, {}, 60)] == ["lower", "upper", None]
    for bad in ("Upper", "title"):
        with pytest.raises(ValueError, match=re.escape(
                "lexsync: event 1 has case '%s'; a text event takes case: upper or "
                "case: lower." % bad)):
            render_events([{"type": "text", "content": "{target}", "case": bad}], {}, 60)
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: event 1 is a mask event, and only a text event takes `case`.")):
        render_events([{"type": "mask", "content": "#####", "case": "upper"}], {}, 60)


def test_a_mask_sized_from_the_trials_needs_one_character_and_named_fields():
    # A scalar names one field, as a YAML scalar `length_of: target` would.
    assert render_events([{"type": "mask", "content": "#", "length_of": "target"}],
                         {}, 60)[0]["length_of"] == ["target"]
    for content in ("##", "{prime}", ""):
        with pytest.raises(ValueError, match=re.escape(
                "lexsync: event 1 repeats its content to the length of the longest text "
                "of the trials, so its content must be one character, such as '#'.")):
            render_events([{"type": "mask", "content": content, "length_of": ["prime"]}],
                          {}, 60)
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: event 1 has length_of 'two words'; name the fields whose longest "
            "text sets the mask's length, as in [prime, target].")):
        render_events([{"type": "mask", "content": "#", "length_of": "two words"}], {}, 60)
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: event 1 is a text event, and only a mask event takes `length_of`.")):
        render_events([{"type": "text", "content": "x", "length_of": ["prime"]}], {}, 60)


def _primed(schema):
    """Two targets over two lists. 'Naïveté' has seven characters and nine UTF-8 bytes,
    so a mask counted in bytes would be two marks too long, and the 'ß' of 'straße'
    upper-cases differently in R."""
    items = pd.DataFrame({"prime": ["Naïveté", "cat", "dog", "sun"],
                          "target": ["straße", "straße", "moon", "moon"],
                          "condition": ["related", "unrelated"] * 2, "set": [1, 1, 2, 2]})
    design = {"name": "mp", "language": "english", "paradigm": "masked_priming",
              "counterbalance": {"lists": 2}}
    return counterbalance(items, design, schema), design


def _embedded(path, pattern):
    with open(path, encoding="utf-8") as handle:
        return json.loads(re.search(pattern, handle.read(), re.S).group(1))


def test_the_experiments_carry_the_forward_mask_and_the_case(schema, tmp_path):
    stim, design = _primed(schema)
    out = export_experiments(stim, design, schema, str(tmp_path))
    for events in (_embedded(out["psychopy"], r'EVENTS = json\.loads\(r"""(.*?)"""\)'),
                   _embedded(out["jspsych"], r"const EVENTS = (.*?);\n")):
        assert events[0] == {"type": "mask", "text": "#######", "ms": 500}
        assert [e.get("case") for e in events] == [None, "lower", "upper", None]
        # The item text travels unchanged: the runner applies the case as it shows it.
        assert events[2]["field"] == "target"
    experiments = [p for p in out["files"] if p.endswith(".osexp")]
    assert len(experiments) == 2
    for path in experiments:
        with open(path, encoding="utf-8") as handle:
            osexp = handle.read()
        # One mask for every version, sized from all the trials.
        assert "\t_lexsync_c_e0.text(u'#######')" in osexp
        assert "\t_lexsync_c_e1.text(_lexsync_row()[u'prime'].lower())" in osexp
        assert "\t_lexsync_c_e2.text(_lexsync_row()[u'target'].upper())" in osexp
    # The loop table keeps each item as it was written.
    table = pd.read_csv(os.path.join(str(tmp_path), "mp_english_psychopy.csv"))
    assert sorted(set(table["target"])) == ["moon", "straße"]
    assert "Naïveté" in set(table["prime"])


def test_a_mask_needs_the_fields_it_is_sized_from(schema, tmp_path):
    stim, _ = _primed(schema)
    design = {"name": "mp", "language": "english", "counterbalance": {"lists": 2},
              "events": [{"type": "mask", "content": "#", "length_of": ["cue"],
                          "duration_ms": 500},
                         {"type": "text", "content": "{target}", "duration_ms": 500,
                          "trigger": "condition"}]}
    with pytest.raises(ValueError, match=re.escape(
            "lexsync: a mask takes its length from field 'cue', which the trials do not "
            "have.")):
        export_experiments(stim, design, schema, str(tmp_path))


# ---- The reproductions ---------------------------------------------------------------


def _read(*parts):
    return pd.read_csv(repo_path(*parts), dtype=str, keep_default_na=False,
                       encoding="utf-8")


def test_the_reproductions_run_as_lexical_decisions():
    rastle = read_config(str(repo_path("config", "design_en_rastle_repro.yaml")))
    assert rastle["paradigm"] == "masked_priming"
    assert rastle["fillers"] == {"path": "items/rastle_nonword_fillers_en.csv"}
    assert rastle["response_mapping"] == {"related": "left", "unrelated": "left"}
    andrews = read_config(str(repo_path("config", "design_en_andrews_repro.yaml")))
    assert andrews["fillers"] == {"path": "items/andrews_pseudoword_fillers_en.csv"}
    assert set(andrews["response_mapping"].values()) == {"left"}
    for stem, n_main, filler in (("en_rastle_repro", 12, "nonword"),
                                 ("en_andrews_repro", 72, "pseudoword")):
        table = _read("output", "experiments", f"{stem}_english_psychopy.csv")
        for _, rows in table.groupby("list"):
            main = rows[rows["block"] == "main"]
            fillers = rows[rows["block"] == "filler"]
            assert len(main) == len(fillers) == n_main, stem
            # Every trial is scored: a word takes the left arrow, a nonword the right.
            assert set(main["answer"]) == {"left"}, stem
            assert set(fillers["answer"]) == {"right"}, stem
            assert set(fillers["condition"]) == {filler}, stem
            # The fillers are interleaved with the words, not appended to them.
            assert rows["block"].iloc[:n_main].nunique() == 2, stem
    script = repo_path("output", "experiments", "en_rastle_repro_english_psychopy.py")
    events = _embedded(script, r'EVENTS = json\.loads\(r"""(.*?)"""\)')
    table = _read("output", "experiments", "en_rastle_repro_english_psychopy.csv")
    longest = max(len(s) for s in list(table["prime"]) + list(table["target"]))
    assert events[0] == {"type": "mask", "text": "#" * longest, "ms": 500}
    assert [e.get("case") for e in events] == [None, "lower", "upper", None]


def test_the_reproductions_nonwords_are_new_forms_of_their_words_lengths():
    with open(repo_path("corpora", "derived", "en_known_forms.txt"),
              encoding="utf-8") as handle:
        known = set(handle.read().split("\n"))
    v2 = _read("corpora", "derived", "en_v2.csv").set_index("word")
    items = _read("items", "rastle_priming_en.csv")
    fillers = _read("items", "rastle_nonword_fillers_en.csv")
    assert list(fillers.columns) == ["item", "condition", "prime", "target", "answer"]
    words = sorted(set(items["target"]))
    assert len(fillers) == len(words) == 12
    assert sorted(map(len, fillers["target"])) == sorted(map(len, words))
    assert not set(fillers["target"]) & known
    # Each nonword target has a real, screened word as its prime, used nowhere else.
    primes = list(fillers["prime"])
    assert len(set(primes)) == len(primes)
    assert not set(primes) & set(items["prime"]) and not set(primes) & set(items["target"])
    assert (v2.loc[primes, "nonstandard"] == "0").all()
    andrews = _read("items", "andrews_pseudoword_fillers_en.csv")
    assert list(andrews.columns) == ["item", "condition", "word", "answer"]
    selected = _read("output", "stimuli", "en_andrews_repro_english_stimuli_py.csv")["word"]
    assert len(andrews) == len(selected) == 72
    assert sorted(map(len, andrews["word"])) == sorted(map(len, selected))
    assert len(set(andrews["word"])) == 72 and not set(andrews["word"]) & known
