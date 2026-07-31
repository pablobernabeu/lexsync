"""Practice and filler blocks, the feedback event, and the per-block event filter.

The property that matters is the split: the experiment runs more trials than the study
analyses. The stimuli file and the reports are written from the main rows; the generated
experiments are written from every presented trial. Getting that backwards would either
put practice items into the realised-control statistics or leave them out of the
experiment entirely.

Three placements are asserted rather than assumed, because each is a methodological
choice and not a convenience:

Practice comes strictly first.

Fillers are INTERLEAVED, not appended. A block of fillers at the end is not a filler --
it is a second block the participant can tell apart. That is why they are merged in
before the order is drawn.

Feedback is restricted to practice, via `blocks:` on the event, because feedback in the
task itself would contaminate the reaction times it is measuring.

A design that declares neither block must be untouched, down to not gaining a `block`
column, so adding this feature moved no existing artefact.

test-blocks.R asserts the same properties.
"""
import os

import pandas as pd
import pytest
import yaml

from lexsync.blocks import BLOCK_MAIN, add_blocks
from lexsync.scripting import export_jspsych, loop_table, render_events

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DESIGN_PATH = os.path.join(REPO, "config", "design_en_lexdec_blocks.yaml")


@pytest.fixture()
def schema():
    with open(os.path.join(REPO, "config", "schema.yaml"), encoding="utf-8") as h:
        return yaml.safe_load(h)


@pytest.fixture()
def design(monkeypatch):
    # The design names its item tables relative to the repository root, which is where
    # the pipeline runs; pytest runs from python_workflow, so the tests that load those
    # tables need the same working directory.
    monkeypatch.chdir(REPO)
    with open(DESIGN_PATH, encoding="utf-8") as h:
        return yaml.safe_load(h)


def _main(n=8):
    return pd.DataFrame({
        "item": list(range(1, n + 1)), "set": list(range(1, n + 1)),
        "condition": ["word", "pseudoword"] * (n // 2),
        "target": ["w%02d" % i for i in range(1, n + 1)],
        "answer": ["f", "j"] * (n // 2),
        "list": 1, "trial": list(range(1, n + 1)),
    })


def test_a_design_without_blocks_is_untouched(schema):
    stim = _main()
    out = add_blocks(stim, {"name": "x"}, schema)
    assert out["report"] is None
    # Not even a block column: adding this feature must move no existing artefact.
    assert "block" not in out["presented"].columns
    assert out["presented"].equals(stim)


@pytest.mark.skipif(not os.path.exists(DESIGN_PATH), reason="repository design absent")
def test_practice_comes_first_and_fillers_interleave(design, schema):
    out = add_blocks(_main(), design, schema)
    order = list(out["presented"].sort_values("trial")["block"])
    first_main = order.index(BLOCK_MAIN)
    assert set(order[:first_main]) == {"practice"}, "practice must be strictly first"
    filler = [i for i, b in enumerate(order) if b == "filler"]
    main = [i for i, b in enumerate(order) if b == BLOCK_MAIN]
    # Genuinely mixed through, not a trailing run.
    assert min(filler) < max(main) and max(filler) > min(main)


@pytest.mark.skipif(not os.path.exists(DESIGN_PATH), reason="repository design absent")
def test_block_sets_do_not_collide_with_the_main_ones(design, schema):
    """`set` is part of the key the trial-order shuffle hashes, so two rows sharing one
    would be ordered by a coin the package does not own."""
    out = add_blocks(_main(), design, schema)
    per_block = out["presented"].groupby("block")["set"].apply(set)
    assert not (per_block["practice"] & per_block[BLOCK_MAIN])
    assert not (per_block["filler"] & per_block[BLOCK_MAIN])
    assert not (per_block["practice"] & per_block["filler"])


@pytest.mark.skipif(not os.path.exists(DESIGN_PATH), reason="repository design absent")
def test_the_shuffle_key_columns_keep_their_integer_type(design, schema):
    """pandas promotes an integer column to float the moment a missing value enters it,
    and the shuffle formats an integer set as "3" but a float one as "3.0" -- which would
    change every digest and every trial order with nothing to signal it."""
    out = add_blocks(_main(), design, schema)["presented"]
    for col in ("set", "list", "trial"):
        assert str(out[col].dtype).startswith("int"), (col, out[col].dtype)


@pytest.mark.skipif(not os.path.exists(DESIGN_PATH), reason="repository design absent")
def test_every_block_appears_in_every_list(design, schema):
    stim = _main()
    stim["list"] = [1, 1, 1, 1, 2, 2, 2, 2]
    out = add_blocks(stim, design, schema)["presented"]
    for li, g in out.groupby("list"):
        assert set(g["block"]) == {"practice", "filler", BLOCK_MAIN}, li


@pytest.mark.skipif(not os.path.exists(DESIGN_PATH), reason="repository design absent")
def test_the_report_names_the_tables_and_their_checksums(design, schema):
    report = add_blocks(_main(), design, schema)["report"]
    assert report["analysed"] == BLOCK_MAIN
    by = {b["block"]: b for b in report["blocks"]}
    assert set(by) == {"main", "practice", "filler"}
    for name in ("practice", "filler"):
        assert len(by[name]["sha256"]) == 64
        assert by[name]["n_per_list"] == 8
    assert "interleaved" in by["filler"]["placement"]
    assert "before" in by["practice"]["placement"]


def test_a_block_without_a_path_is_refused(schema):
    with pytest.raises(ValueError, match="needs a `path`"):
        add_blocks(_main(), {"practice": {"n": 4}}, schema)


# --- The feedback event and the per-block filter ------------------------------

def _feedback_design():
    return {"name": "f", "language": "english", "events": [
        {"type": "text", "content": "{target}", "duration_ms": 800},
        {"type": "response", "keys": ["f", "j"], "timeout_ms": 2000},
        {"type": "feedback", "answer": "answer", "duration_ms": 600,
         "blocks": ["practice"]},
    ]}


def test_the_feedback_event_renders_with_its_texts_and_restriction():
    rendered = render_events(_feedback_design()["events"], {}, 60)
    fb = rendered[-1]
    assert fb["type"] == "feedback"
    # `answer` names a loop-table column holding a KEY, so scoring needs no mapping.
    assert fb["answer"] == "answer"
    assert fb["ms"] == 600
    # A timeout is reported separately from a wrong key: on a timed task they mean
    # different things to a participant.
    assert fb["correct"] and fb["incorrect"] and fb["no_response"]
    assert fb["blocks"] == ["practice"]
    # An unrestricted event carries no filter at all, so nothing changes for designs
    # that do not use blocks.
    assert "blocks" not in rendered[0]


def test_block_reaches_the_loop_table():
    """The runners match an event's restriction against it and watch it for a block
    boundary, so it has to travel with the trials rather than stay in the stimuli file."""
    stim = _main()
    stim["block"] = "main"
    tab = loop_table(stim, _feedback_design()["events"])
    assert "block" in tab.columns
    # And it is absent when the design has no blocks, so no existing loop table changes.
    assert "block" not in loop_table(_main(), _feedback_design()["events"]).columns


def test_the_jspsych_export_carries_the_filter_and_the_break(schema, tmp_path):
    stim = _main()
    stim["block"] = ["practice"] * 4 + ["main"] * 4
    d = _feedback_design()
    out = export_jspsych(stim, d, schema, str(tmp_path), "fb")
    html = open(out, encoding="utf-8").read()
    assert '"blocks":["practice"]' in html
    assert "eventApplies" in html            # the per-trial filter
    assert "block_break" in html             # the boundary screen
    assert "lexsync_scored" in html          # feedback finds ITS trial's response
    assert "{{" not in html


def test_a_missing_value_drops_the_key_rather_than_emitting_nan():
    """The regression that made the two engines' generated experiments differ.

    A design whose practice items carry an `answer` but whose main items do not leaves
    the main rows missing that value. This engine embedded a bare `NaN` into the JSON --
    which is not valid JSON at all -- while jsonlite dropped the key. Both now drop it,
    which is also the honest rendering: a trial with no correct answer has none.

    test-blocks.R pins the same behaviour on the R side.
    """
    from lexsync.scripting import _json_r
    assert _json_r({"a": 1, "b": float("nan")}) == '{"a":1}'
    assert _json_r({"a": 1, "b": None}) == '{"a":1}'
    assert _json_r([{"a": float("nan")}, {"a": 2}]) == '[{},{"a":2}]'
    # A present value is untouched, including a whole-number float (jsonlite drops the
    # fractional part, so 2.0 must serialise as 2).
    assert _json_r({"a": 2.0, "b": 2.5}) == '{"a":2,"b":2.5}'


def test_the_opensesame_emitter_writes_python_3():
    """str, not unicode: OpenSesame 3.3+ runs inline scripts in a Python 3 workspace and
    does not inject the Python 2 builtin, so the earlier spelling died with NameError on
    the first trial of any design using a feedback event or a blocks restriction. And
    var.get(name, None) is indistinguishable from no default in OpenSesame's var_store,
    which RAISES rather than yielding None."""
    from lexsync.scripting import _osexp_event_block
    ev = render_events(_feedback_design()["events"], {}, 60)
    lines, _ = _osexp_event_block("ev_fb", ev[-1])
    txt = "\n".join(lines)
    assert "if str(var.get(u'block', u'main')) in [u'practice']:" in txt
    assert "unicode(" not in txt
    assert "var.get(u'response', None)" not in txt


def test_a_feedback_event_with_nothing_to_score_is_refused():
    ev = [{"type": "text", "content": "{target}", "duration_ms": 800},
          {"type": "feedback", "answer": "answer", "duration_ms": 600}]
    with pytest.raises(ValueError, match="no response or question event"):
        render_events(ev, {}, 60)
    ok = [ev[0], {"type": "response", "keys": ["f", "j"], "timeout_ms": 2000}, ev[1]]
    assert len(render_events(ok, {}, 60)) == 3
