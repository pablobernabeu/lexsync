"""The gates in the workflows that nothing else can fail, read from the
workflow files themselves.

Each is a line of YAML that no test suite can fail, so a narrowing goes
unnoticed. The regeneration diff once covered `output/stimuli/` alone: the same
run rewrites the descriptives, the comparisons and the five generated experiment
files per design, and docs.yml publishes the committed experiments verbatim, so a
stale copy there is what a reader is handed while every job stays green.
LEXSYNC_REQUIRE_PARITY is another. It turns the parity suites' 'nothing to
compare' skips into failures, and it reached test_parity.py alone, so the suite
that makes the byte-identical claim checkable could have skipped everywhere and
said nothing. The lint job is the third: it runs from python_workflow, so the
Streamlit app, the repository's only other Python source, was seen by no linter.
The fourth is in docs.yml, where the two documentation builds are the only check
the documentation has and ran after merge alone.
"""
import os

import pytest
import yaml

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORKFLOW = os.path.join(REPO, ".github", "workflows", "python-tests.yaml")
DOCS_WORKFLOW = os.path.join(REPO, ".github", "workflows", "docs.yml")


def _parity_steps():
    if not os.path.exists(WORKFLOW):
        pytest.skip("repository workflows not available")
    with open(WORKFLOW, encoding="utf-8") as handle:
        flow = yaml.safe_load(handle)
    return flow["jobs"]["parity"]["steps"]


def _run(step):
    return step.get("run") or ""


def test_the_regeneration_gate_covers_every_committed_artefact():
    gates = [_run(s) for s in _parity_steps()
             if "git diff" in _run(s) and "output/" in _run(s)]
    assert len(gates) == 1, "the regeneration gate is not where this test looks"
    gate = gates[0]
    assert "-- output/ " in gate or "-- output/\n" in gate, (
        "the gate diffs a subtree of output/, so the artefacts outside it can go "
        "stale without failing CI: %s" % gate)
    # The two exclusions are the per-engine provenance records, which cannot match
    # across machines. Everything else must be inside the gate.
    for excluded in ("':!output/reports/*_run_log_*'", "':!output/reports/*_datasheet_*'"):
        assert excluded in gate, gate


def test_require_parity_reaches_both_parity_suites():
    steps = [s for s in _parity_steps()
             if (s.get("env") or {}).get("LEXSYNC_REQUIRE_PARITY") == "1"]
    assert steps, "nothing in the parity job turns a skipped comparison into a failure"
    unfiltered = [_run(s) for s in steps if " -k " not in _run(s)]
    for suite in ("tests/test_parity.py", "tests/test_byte_parity.py"):
        assert any(suite in run for run in unfiltered), (
            "%s never runs with LEXSYNC_REQUIRE_PARITY set, so it may skip every "
            "comparison and leave the job green" % suite)


def test_the_lint_job_covers_the_apps_tree():
    if not os.path.exists(WORKFLOW):
        pytest.skip("repository workflows not available")
    with open(WORKFLOW, encoding="utf-8") as handle:
        flow = yaml.safe_load(handle)
    job = flow["jobs"]["lint"]
    assert job["defaults"]["run"]["working-directory"] == "python_workflow"
    runs = [_run(s) for s in job["steps"]]
    assert any(r.strip() == "ruff check ." for r in runs)
    assert any("ruff check ../apps" in r for r in runs), (
        "apps/ sits outside the lint job's working directory, so nothing lints "
        "the Streamlit app: %s" % runs)


def test_the_documentation_is_built_on_pull_requests_and_deployed_only_after():
    if not os.path.exists(DOCS_WORKFLOW):
        pytest.skip("repository workflows not available")
    with open(DOCS_WORKFLOW, encoding="utf-8") as handle:
        flow = yaml.safe_load(handle)
    # YAML reads a bare `on` as the boolean, so the triggers arrive under True.
    triggers = flow.get("on", flow.get(True))
    assert "pull_request" in triggers, (
        "mkdocs --strict and pkgdown are the documentation's only checks, and a "
        "workflow that runs after merge alone turns main red rather than the "
        "change that broke it")
    deploy = flow["jobs"]["deploy"]
    # The whole gate, not the substring: `github.event_name == 'pull_request'`
    # holds it too and is the one thing this test exists to catch.
    assert deploy["if"].replace('"', "'") == "github.event_name != 'pull_request'", (
        "a pull request would publish the site")
    assert deploy["permissions"] == {"contents": "write"}
    assert flow["permissions"] == {"contents": "read"}
