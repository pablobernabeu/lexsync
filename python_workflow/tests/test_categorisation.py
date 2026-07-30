"""The cued-categorisation paradigm, and the type trap it exposed.

Two things are pinned here.

The paradigm rotates rather than crossing. Each item carries a narrow cue and a broad
one, so the factorial recipe would hand a participant the same target twice and the
second presentation would be a repetition-priming trial rather than a categorisation
trial. That was the first version's actual behaviour, caught by counting targets per
list, so it is asserted rather than assumed.

`answer` survives as text. It holds the response KEY, and the natural coding for a
two-choice task is `f` and `j` -- which R's readr reads as the LOGICAL value FALSE while
pandas keeps the string. A design's correct answer was therefore silently turned into
FALSE in one engine. Measured on readr 2.2.0: f, t, T and F infer as logical; j, y and n
do not, which is the worst possible split because f/j and t/f are the two commonest key
pairs in the field.

test-categorisation.R asserts the same properties.
"""
import os

import pytest
import yaml

from lexsync.counterbalancing import counterbalance
from lexsync.paradigms import PARADIGMS, get_paradigm, required_fields, resolve_events
from lexsync.querying import load_items
from lexsync.scripting import export_jspsych, render_events

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ITEMS = os.path.join(REPO, "items", "categorisation_en.csv")
DESIGN_PATH = os.path.join(REPO, "config", "design_en_categorisation.yaml")


@pytest.fixture()
def schema():
    with open(os.path.join(REPO, "config", "schema.yaml"), encoding="utf-8") as h:
        return yaml.safe_load(h)


@pytest.fixture()
def design():
    with open(DESIGN_PATH, encoding="utf-8") as h:
        return yaml.safe_load(h)


def test_the_paradigm_is_registered_with_the_fields_it_needs():
    p = get_paradigm("categorisation")
    # `answer` is required, so a categorisation experiment cannot be generated without a
    # way to score it.
    assert p["stimulus_fields"] == ["target", "category", "answer"]
    assert "categorisation" in PARADIGMS
    types = [e["type"] for e in p["events"]]
    # The cue is a trial event, not one-off instructions: the category varies by trial.
    assert types == ["fixation", "text", "text", "response", "blank"]
    assert p["events"][1]["content"] == "{category}"
    assert p["events"][2]["content"] == "{target}"
    # Only the target onset carries the condition marker; the cue is not the stimulus.
    assert p["events"][2]["trigger"] == "condition"
    assert "trigger" not in p["events"][1]


def test_the_paradigm_rotates_rather_than_crossing():
    # The reason this matters: with the factorial recipe a participant sees each target
    # under both cues, and the second is a repetition trial. Asserted because the first
    # version of this paradigm got it wrong.
    assert get_paradigm("categorisation")["counterbalance"] == "latin_square_target"


def test_required_fields_include_the_cue_and_the_answer(design):
    assert set(required_fields(design)) >= {"target", "category", "answer"}


@pytest.mark.skipif(not os.path.exists(ITEMS), reason="repository item table absent")
def test_the_answer_key_is_read_as_text_not_a_boolean(design):
    items = load_items(ITEMS, required_fields(design))
    assert set(items["answer"]) == {"f"}
    assert items["answer"].dtype == object
    # The whole point: not the string "FALSE" and not the boolean False.
    assert "FALSE" not in set(items["answer"])
    assert False not in set(items["answer"])


@pytest.mark.skipif(not os.path.exists(ITEMS), reason="repository item table absent")
def test_each_target_appears_once_per_list(design, schema):
    items = load_items(ITEMS, required_fields(design))
    out = counterbalance(items, design, schema)
    for (lst, target), n in out.groupby(["list", "target"]).size().items():
        assert n == 1, "target %r appears %d times in list %s" % (target, n, lst)
    # And the two cues stay balanced within each list.
    counts = out.groupby(["list", "condition"]).size()
    assert counts.nunique() == 1


@pytest.mark.skipif(not os.path.exists(ITEMS), reason="repository item table absent")
def test_the_jspsych_export_carries_the_cue_and_the_answer(design, schema, tmp_path):
    """jsPsych is generated from the same event list as the other two targets, so the
    new paradigm needs no browser-specific code -- but "needs none" is a claim, and this
    is what checks it."""
    items = load_items(ITEMS, required_fields(design))
    stim = counterbalance(items, design, schema)
    out = export_jspsych(stim, design, schema, str(tmp_path), "cat")
    html = open(out, encoding="utf-8").read()
    # The cue and the answer reach the embedded trial data.
    assert '"category"' in html and '"answer"' in html
    assert "A BIRD?" in html
    assert '"answer":"f"' in html or '"answer": "f"' in html
    # Two text events, so the cue is presented as well as the target.
    assert html.count('"type":"text"') == 2 or html.count('"type": "text"') == 2
    # The response keys the paradigm declares reach the browser.
    assert '"f"' in html and '"j"' in html
    # And nothing was left unsubstituted.
    assert "{{" not in html


def test_the_rendered_events_use_milliseconds(schema):
    d = {"paradigm": "categorisation", "name": "c", "language": "english"}
    rendered = render_events(resolve_events(d), {}, 60)
    assert [r["type"] for r in rendered] == ["fixation", "text", "text", "response", "blank"]
    assert rendered[0]["ms"] == 500
    assert rendered[1]["ms"] == 750 and rendered[1]["field"] == "category"
    assert rendered[2]["ms"] == 800 and rendered[2]["field"] == "target"
    assert rendered[3]["timeout"] == 2.5
    assert rendered[4]["ms"] == 250


def test_readr_style_logical_inference_is_neutralised(tmp_path):
    """The general form of the bug, on the tokens that trigger it."""
    p = tmp_path / "items.csv"
    p.write_text("item,condition,target,category,answer\n"
                 "1,a,dog,AN ANIMAL?,f\n2,b,cat,AN ANIMAL?,t\n",
                 encoding="utf-8", newline="\n")
    items = load_items(str(p), ["target", "category", "answer"])
    assert list(items["answer"]) == ["f", "t"]
    assert list(items["condition"]) == ["a", "b"]
