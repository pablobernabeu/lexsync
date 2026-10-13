"""Structural validation of the generated jsPsych experiment (no browser needed)."""
import importlib.util
import json
import re
import shutil
import subprocess

import pandas as pd
import pytest
from helper_repo import repo_path

from lexsync.counterbalancing import counterbalance
from lexsync.paradigms import referenced_fields, resolve_events
from lexsync.scripting import assign_triggers, export_jspsych


def validate_jspsych(text):
    assert text.lstrip().startswith("<!DOCTYPE html>")
    assert "</html>" in text
    assert "jspsych@" in text                      # the library is loaded
    assert "initJsPsych()" in text and "jsPsych.run(timeline)" in text
    # The embedded data parse as JSON (the HTML-safe < etc. are valid escapes).
    events = json.loads(re.search(r"const EVENTS = (.*?);\n", text, re.S).group(1))
    trials = json.loads(re.search(r"const TRIALS = (.*?);\n", text, re.S).group(1))
    assert events and trials
    return events, trials


def _stim():
    s = pd.DataFrame({
        "word": ["cat", "dog", "car", "cap"], "condition": ["a", "a", "b", "b"],
        "set": [1, 2, 1, 2], "trial": [1, 2, 3, 4], "length": 3, "frequency": 5,
        "n_density": 2, "old20": 1.5,
    })
    return assign_triggers(s)


def test_jspsych_is_structurally_valid(schema, tmp_path):
    design = {"name": "t", "language": "english", "timing": {}}
    path = export_jspsych(_stim(), design, schema, str(tmp_path))
    events, trials = validate_jspsych(open(path, encoding="utf-8").read())
    # every trial carries the fields the events reference and the trigger columns
    fields = referenced_fields(resolve_events(design))
    for trial in trials:
        for f in fields:
            assert f in trial
        assert "condition_trigger" in trial and 0 <= int(trial["condition_trigger"]) <= 255


def test_jspsych_maps_keys_to_browser_names(schema, tmp_path):
    design = {"name": "t", "language": "english", "timing": {}}
    events, _ = validate_jspsych(
        open(export_jspsych(_stim(), design, schema, str(tmp_path)), encoding="utf-8").read())
    respond = [e["respond"] for e in events if "respond" in e][0]
    assert respond["keys"] == ["arrowleft", "arrowright"]  # 'left'/'right' -> browser keys
    # A delayed response event is mapped too.
    delayed = dict(design, events=[
        {"type": "text", "content": "{word}", "duration_ms": 800},
        {"type": "response", "keys": ["left", "space"], "from": "offset"}])
    events, _ = validate_jspsych(
        open(export_jspsych(_stim(), delayed, schema, str(tmp_path)), encoding="utf-8").read())
    assert events[1]["keys"] == ["arrowleft", " "]


def test_jspsych_escapes_html_in_data(schema, tmp_path):
    # A crafted stimulus cannot break out of the <script> block.
    stim = assign_triggers(pd.DataFrame({
        "word": ["</script><b>x"], "condition": ["a"], "set": [1], "trial": [1],
        "length": 3, "frequency": 5, "n_density": 2, "old20": 1.5,
    }))
    text = open(export_jspsych(stim, {"name": "t", "language": "english", "timing": {}},
                               schema, str(tmp_path)), encoding="utf-8").read()
    assert "</script><b>x" not in text          # the literal closing tag is escaped
    _, trials = validate_jspsych(text)
    assert trials[0]["word"] == "</script><b>x"  # but the value round-trips via JSON


# ---- One counterbalancing version per participant ------------------------------------
#
# The page embeds every version's trials, because one page serves every participant, and
# its timeline used to run them all. test-jspsych.R holds the R engine to the same page.

def _two_list_stimuli(schema):
    """Two targets, each related in one list and unrelated in the other."""
    stim = pd.DataFrame({"prime": ["hot", "sky", "sun", "big"],
                         "target": ["cold", "cold", "moon", "moon"],
                         "condition": ["related", "unrelated"] * 2, "set": [1, 1, 2, 2]})
    design = {"name": "t", "language": "english", "paradigm": "priming",
              "counterbalance": {"lists": 2}}
    return assign_triggers(counterbalance(stim, design, schema)), design


def _versions(text):
    return json.loads(re.search(r"const VERSIONS = (.*?);\n", text, re.S).group(1))


def test_the_page_carries_the_versions_and_selects_one(schema, tmp_path):
    stim, design = _two_list_stimuli(schema)
    text = open(export_jspsych(stim, design, schema, str(tmp_path)), encoding="utf-8").read()
    _, trials = validate_jspsych(text)
    versions = _versions(text)
    assert versions == [{"version": 1, "replicate": 1, "list": 1, "n_trials": 2},
                        {"version": 2, "replicate": 1, "list": 2, "n_trials": 2}]
    assert "const RUN_TRIALS = TRIALS.filter(" in text
    # The embedded trials hold both versions. The page's filter keeps a trial whose
    # replicate and list are the version's, a trial without either column counting as
    # replicate 1 or list 1. Each version then shows each target once.
    for v in versions:
        rows = [t for t in trials
                if (t.get("replicate", 1), t.get("list", 1)) == (v["replicate"], v["list"])]
        assert len(rows) == v["n_trials"]
        assert sorted(t["target"] for t in rows) == ["cold", "moon"]


NODE = shutil.which("node")

# Runs the page's own script in a JavaScript runtime, with stand-ins for the browser
# and for jsPsych, and prints the timeline it built and the properties it set. Given a
# third argument, the data store's scored row holds that key as its response, and a
# stimulus built when its screen is shown, as a feedback screen's is, is built then.
_HARNESS = r"""
const fs = require("fs");
const vm = require("vm");
const [page, search, pressed] = process.argv.slice(2);
const html = fs.readFileSync(page, "utf8");
const inline = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
const out = { properties: null, timeline: [] };
const sandbox = {
  window: { location: { search } },
  document: { title: "lexsync: t" },
  URLSearchParams,
  jsPsychHtmlKeyboardResponse: "html-keyboard-response",
  initJsPsych: () => ({
    data: {
      addProperties: (p) => { out.properties = p; },
      get: () => ({ filter: () => ({ last: () => ({
                      values: () => (pressed === undefined ? [] : [{ response: pressed }]) }) }),
                    localSave: () => {} }),
    },
    run: (timeline) => { out.timeline = timeline; },
  }),
};
vm.createContext(sandbox);
vm.runInContext(inline[inline.length - 1][1], sandbox);
process.stdout.write(JSON.stringify({
  properties: out.properties,
  data: out.timeline.map((t) => t.data || {}),
  stimuli: out.timeline.map((t) => (typeof t.stimulus === "string" ? t.stimulus
    : (typeof t.stimulus === "function" && pressed !== undefined ? t.stimulus() : ""))),
  trials: out.timeline.map((t) => ({
    choices: t.choices === undefined ? null : t.choices,
    stimulus_duration: t.stimulus_duration === undefined ? null : t.stimulus_duration,
    trial_duration: t.trial_duration === undefined ? null : t.trial_duration,
    response_ends_trial: t.response_ends_trial === undefined ? null : t.response_ends_trial,
  })),
}));
"""


def _run_page(path, query, tmp_path, pressed=None):
    harness = tmp_path / "harness.js"
    harness.write_text(_HARNESS, encoding="utf-8")
    proc = subprocess.run([NODE, str(harness), str(path), query]
                          + ([] if pressed is None else [pressed]), capture_output=True,
                          text=True, encoding="utf-8", timeout=120)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_the_page_runs_only_the_version_its_address_names(schema, tmp_path):
    stim, design = _two_list_stimuli(schema)
    path = export_jspsych(stim, design, schema, str(tmp_path))
    for query, version in (("?version=2", 2), ("?participant=3", 1), ("?participant=4", 2),
                           ("?list=2", 2), ("?participant=2&version=1", 1)):
        run = _run_page(path, query, tmp_path)
        shown = [d for d in run["data"] if d.get("lexsync_event") == "fixation"]
        assert {d["list"] for d in shown} == {version}, query
        assert sorted(d["target"] for d in shown) == ["cold", "moon"], query
        assert run["properties"]["version"] == version, query
        assert run["properties"]["list"] == version, query
        # The welcome screen counts the trials this participant will see.
        assert "There are 2 items in total." in run["stimuli"][0], query
    assert _run_page(path, "?participant=3", tmp_path)["properties"]["participant"] == 3
    # With two versions and neither parameter, or one the page does not have, the page
    # names the parameters instead of running anything.
    for query in ("", "?version=3", "?version=x", "?participant=0", "?list=1.5"):
        run = _run_page(path, query, tmp_path)
        assert [d.get("lexsync_event") for d in run["data"]] == ["version_error"], query
        assert "?participant=" in run["stimuli"][0] and "?version=" in run["stimuli"][0]


def test_every_published_link_to_a_demo_names_a_version_it_runs(monkeypatch):
    """A page with several versions runs none without one in its address, so the site's
    landing page and its demos index link each such page with a version. The landing
    page linked the two-list self-paced reading demonstration bare."""
    folder = repo_path("output", "experiments")
    landing = repo_path(".github", "landing.html").read_text(encoding="utf-8")
    links = re.findall(r'href="demos/([^"?]+\.html)(\?[^"]*)?"', landing)
    assert links
    for page, query in links:
        if len(_versions((folder / page).read_text(encoding="utf-8"))) > 1:
            assert re.fullmatch(r"\?(version|participant|list)=[1-9][0-9]*", query), page
    # The index builder reads the staged pages, which are copies of these.
    spec = importlib.util.spec_from_file_location(
        "build_demo_index", repo_path(".github", "build_demo_index.py"))
    index = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(index)
    monkeypatch.setattr(index, "DEMO_DIR", folder)
    cards = {}
    for card in index.collect():
        page, _, query = card["file"].partition("?")
        cards.setdefault(page, []).append(query)
    assert cards
    for page, queries in cards.items():
        n = len(_versions((folder / page).read_text(encoding="utf-8")))
        assert queries == ([f"version={k}" for k in range(1, n + 1)] if n > 1 else [""]), page


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_a_single_version_page_runs_without_parameters(schema, tmp_path):
    path = export_jspsych(_stim(), {"name": "t", "language": "english", "timing": {}},
                          schema, str(tmp_path))
    run = _run_page(path, "", tmp_path)
    assert len([d for d in run["data"] if d.get("lexsync_event") == "fixation"]) == 4
    assert run["properties"] == {"version": 1, "replicate": 1, "list": 1}


def test_the_target_carries_its_response_window(schema, tmp_path):
    # The rendered target names its response keys and timeout, mapped to browser key
    # names; there is no separate response event. test-jspsych.R pins the same EVENTS.
    events, _ = validate_jspsych(open(export_jspsych(
        _stim(), {"name": "t", "language": "english", "timing": {}}, schema, str(tmp_path)),
        encoding="utf-8").read())
    assert [e["type"] for e in events] == ["fixation", "text", "blank"]
    assert events[1]["ms"] == 800
    assert events[1]["respond"] == {"keys": ["arrowleft", "arrowright"], "timeout": 2}


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_the_target_trial_collects_the_response_from_its_onset(schema, tmp_path):
    # The target was shown with no keys allowed, and a separate blank trial timed the
    # response from the target's offset, so a press while the target was up was lost.
    # The target is now one trial that accepts the keys from its onset, shows the word
    # for its 800 ms and runs for the whole 2,800 ms window unless a key ends it.
    path = export_jspsych(_stim(), {"name": "t", "language": "english", "timing": {}},
                          schema, str(tmp_path))
    run = _run_page(path, "", tmp_path)
    events = [d.get("lexsync_event") for d in run["data"]]
    assert "response" not in events
    targets = [i for i, e in enumerate(events) if e == "target"]
    assert len(targets) == 4
    for uid, i in enumerate(targets, start=1):
        assert run["trials"][i] == {"choices": ["arrowleft", "arrowright"],
                                    "stimulus_duration": 800, "trial_duration": 2800,
                                    "response_ends_trial": True}
        data = run["data"][i]
        assert data["marker"] == int(data["condition_trigger"])
        # The row feedback scores, as the response row was.
        assert data["lexsync_scored"] == uid
    # The welcome screen still names the response keys, now in lexsync's instructions
    # for a design that gives none of its own.
    assert "press the left arrow key or the right arrow key" in run["stimuli"][0]


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_the_welcome_screen_shows_the_instructions(schema, tmp_path):
    # The welcome named the keys and said nothing of what they meant. It now shows the
    # design's instructions, escaped, with each line break kept, and waits for the space
    # bar before the first trial.
    design = {"name": "t", "language": "english", "timing": {},
              "instructions": "Read each word.\nPress <f> & go."}
    run = _run_page(export_jspsych(_stim(), design, schema, str(tmp_path)), "", tmp_path)
    assert run["data"][0] == {"lexsync_event": "instructions"}
    assert run["trials"][0]["choices"] == [" "]
    welcome = run["stimuli"][0]
    assert "<p>Read each word.<br>Press &lt;f&gt; &amp; go.</p>" in welcome
    assert "Press the space bar to begin." in welcome
    # A mapping rotated across lists gives each version its own keys.
    stim = assign_triggers(pd.DataFrame({
        "target": ["cat", "cag", "dog", "dop"], "condition": ["word", "pseudoword"] * 2,
        "set": [1, 1, 2, 2], "trial": [1, 2, 1, 2], "list": [1, 1, 2, 2]}))
    rotated = {"name": "t", "language": "english", "paradigm": "lexical_decision",
               "rotate_mapping_by_list": True}
    path = export_jspsych(stim, rotated, schema, str(tmp_path))
    for query, first, second in (("?version=1", "left", "right"), ("?version=2", "right", "left")):
        welcome = _run_page(path, query, tmp_path)["stimuli"][0]
        assert (f"Press the {first} arrow key if it is a real English word and the {second} "
                "arrow key if it is not.") in welcome, query


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_fillers_run_with_the_main_trials_and_only_the_practice_ends_in_a_pause(
        schema, tmp_path):
    # The page paused wherever the block changed, and fillers are interleaved with the
    # main trials, so a pause came before and after every filler, set it apart and, after
    # each one, said that the practice was over. Fillers now run with the main trials,
    # and the one pause comes where the practice trials end.
    stim = assign_triggers(pd.DataFrame({
        "target": ["tree", "trel", "cat", "sun", "cag", "map", "dop"],
        "condition": ["word", "pseudoword", "word", "word", "pseudoword", "word",
                      "pseudoword"],
        "block": ["practice", "practice", "main", "filler", "main", "filler", "main"],
        "set": [10, 11, 1, 20, 1, 21, 2], "trial": list(range(1, 8)), "list": 1}))
    design = {"name": "t", "language": "english", "paradigm": "lexical_decision"}
    run = _run_page(export_jspsych(stim, design, schema, str(tmp_path)), "", tmp_path)
    shown = [(d.get("lexsync_event"), d.get("target")) for d in run["data"]
             if d.get("lexsync_event") in ("target", "block_break")]
    assert shown == [("target", "tree"), ("target", "trel"), ("block_break", None),
                     ("target", "cat"), ("target", "sun"), ("target", "cag"),
                     ("target", "map"), ("target", "dop")]
    pause = [s for s, d in zip(run["stimuli"], run["data"], strict=True)
             if d.get("lexsync_event") == "block_break"]
    assert len(pause) == 1 and "<h1>End of practice</h1>" in pause[0]


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_feedback_scores_an_arrow_key_against_its_answer(schema, tmp_path):
    # jsPsych records a press of the left arrow as arrowleft, and the page named the
    # answer left, as the loop table does, so the feedback screen called a correct
    # press incorrect. The page now names the answer as the browser names the key.
    design = {"name": "t", "language": "english", "paradigm": "lexical_decision",
              "events": [
                  {"type": "text", "content": "{target}", "duration_ms": 800,
                   "trigger": "condition"},
                  {"type": "response", "keys": ["left", "right"], "timeout_ms": 2000},
                  {"type": "feedback", "answer": "answer", "duration_ms": 600}]}
    stim = assign_triggers(pd.DataFrame({"target": ["cat"], "condition": ["word"], "set": [1],
                                         "trial": [1], "answer": ["left"]}))
    path = export_jspsych(stim, design, schema, str(tmp_path))
    for pressed, verdict in (("arrowleft", "Correct"), ("arrowright", "Incorrect")):
        run = _run_page(path, "", tmp_path, pressed)
        shown = [s for s, d in zip(run["stimuli"], run["data"], strict=True)
                 if d.get("lexsync_event") == "feedback"]
        assert shown == ['<span class="lexsync-stim">%s</span>' % verdict], pressed
