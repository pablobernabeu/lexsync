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
    response = [e for e in events if e["type"] == "response"][0]
    assert response["keys"] == ["arrowleft", "arrowright"]  # 'left'/'right' -> browser keys


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
# and for jsPsych, and prints the timeline it built and the properties it set.
_HARNESS = r"""
const fs = require("fs");
const vm = require("vm");
const [page, search] = process.argv.slice(2);
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
      get: () => ({ filter: () => ({ last: () => ({ values: () => [] }) }),
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
  stimuli: out.timeline.map((t) => (typeof t.stimulus === "string" ? t.stimulus : "")),
}));
"""


def _run_page(path, query, tmp_path):
    harness = tmp_path / "harness.js"
    harness.write_text(_HARNESS, encoding="utf-8")
    proc = subprocess.run([NODE, str(harness), str(path), query], capture_output=True,
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
