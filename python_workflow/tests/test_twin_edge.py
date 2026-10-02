"""Twin-edge parity: small edge-case designs held to a pinned outcome.

test_parity.py and test_byte_parity.py compare the engines on the shipped designs,
whose inputs are clean: every cell NFC, unpadded and covered by its norms. Inputs
that are not (padded fields, missing values, unusual YAML) take code paths the
shipped designs never reach, and two engines that agree can still both be wrong.
Each case under parity/twin_edge/ at the repository root therefore pins what the
engine must do: write these artefacts byte for byte, or raise this refusal.
R_workflow/tests/testthat/test-twin-edge.R holds the R engine to the same
expectations, and tools/compare_engines.py runs the two engines against each other.

A case is a folder holding design.yaml, its inputs (paths relative to the folder),
an optional schema.yaml (config/schema.yaml otherwise) and expect.yaml:

    outcome: artefacts      # or: refusal
    refusal: "lexsync: ..." # outcome refusal: a substring the error must contain
    compare: [stimuli, descriptives, comparisons, experiments]
    datasheet:              # optional, outcome artefacts only
      counterbalancing.lists: 2

With outcome artefacts, expected/ mirrors the output tree (stimuli/, reports/,
experiments/) for the kinds named in `compare`, with the engine tag stripped from
the file names. `python tools/twin_edge.py --update <case>` writes it from this
engine. A datasheet key is a dotted path into the datasheet JSON, in which a list
element is addressed by its position, counted from 0.
"""
import json
import os
import re

import pytest
import yaml
from helper_repo import REPO, repo_path

from lexsync.run_pipeline import run_pipeline

REQUIRE_PARITY = os.environ.get("LEXSYNC_REQUIRE_PARITY") == "1"

KINDS = ("stimuli", "descriptives", "comparisons", "experiments")
OUTCOMES = ("artefacts", "refusal")
EXPECT_KEYS = {"outcome", "refusal", "compare", "datasheet"}
# The engine tag on value artefacts (en_x_stimuli_py.csv). The experiments carry none.
ENGINE_TAG = re.compile(r"_(?:R|py)(\.[^.]+)$")
REPORT_KIND = re.compile(r"_(descriptives|comparisons)(?:_(?:R|py))?\.[^.]+$")


def _case_names():
    root = None if REPO is None else REPO / "parity" / "twin_edge"
    if root is None or not root.is_dir():
        return []
    return sorted(p.name for p in root.iterdir() if p.is_dir())


CASES = _case_names()


def _kind(rel):
    """The artefact kind of a path relative to an output directory or to expected/,
    with or without the engine tag, or None for provenance (datasheets and run logs),
    which no case pins."""
    folder, _, name = rel.partition("/")
    if folder in ("stimuli", "experiments"):
        return folder
    match = REPORT_KIND.search(name)
    return match.group(1) if match else None


def _tree(root):
    """Every file under `root`, as {path relative to root with '/' separators: bytes}."""
    out = {}
    for d, _, files in os.walk(root):
        for f in files:
            full = os.path.join(d, f)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            with open(full, "rb") as handle:
                out[rel] = handle.read()
    return out


def _pinned(outdir, compare):
    """The run's artefacts of the compared kinds, keyed as expected/ names them."""
    return {ENGINE_TAG.sub(r"\1", rel): data for rel, data in _tree(outdir).items()
            if _kind(rel) in compare}


def _read_expect(case_dir):
    with open(os.path.join(case_dir, "expect.yaml"), encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _problems(case_dir):
    """Everything wrong with a case folder's layout and expect.yaml, as messages."""
    if not os.path.isfile(os.path.join(case_dir, "design.yaml")):
        return ["design.yaml is missing"]
    if not os.path.isfile(os.path.join(case_dir, "expect.yaml")):
        return ["expect.yaml is missing"]
    try:
        expect = _read_expect(case_dir)
    except yaml.YAMLError as err:
        return [f"expect.yaml does not parse: {err}"]
    if not isinstance(expect, dict):
        return ["expect.yaml must be a mapping"]
    out = []
    unknown = sorted(set(expect) - EXPECT_KEYS)
    if unknown:
        out.append(f"unknown keys {unknown}")
    outcome = expect.get("outcome")
    expected = os.path.join(case_dir, "expected")
    if outcome not in OUTCOMES:
        out.append(f"outcome must be one of {list(OUTCOMES)}, not {outcome!r}")
    elif outcome == "refusal":
        refusal = expect.get("refusal")
        if not isinstance(refusal, str) or not refusal.strip():
            out.append("outcome refusal needs a non-empty refusal string")
        for key in ("compare", "datasheet"):
            if key in expect:
                out.append(f"{key} applies only to outcome artefacts")
        if os.path.exists(expected):
            out.append("a refusal case has no expected/ folder")
    else:
        if "refusal" in expect:
            out.append("refusal applies only to outcome refusal")
        compare = expect.get("compare")
        if (not isinstance(compare, list) or not compare
                or any(k not in KINDS for k in compare) or len(set(compare)) != len(compare)):
            out.append(f"compare must list distinct kinds from {list(KINDS)}")
            compare = []
        datasheet = expect.get("datasheet", {})
        if not isinstance(datasheet, dict) or not all(isinstance(k, str) for k in datasheet):
            out.append("datasheet must map dotted paths to values")
        pinned = _tree(expected) if os.path.isdir(expected) else {}
        kinds = {_kind(rel) for rel in pinned if "/" in rel}
        for kind in compare:
            if kind not in kinds:
                out.append(f"expected/ holds no {kind} file (run tools/twin_edge.py --update)")
        stray = sorted(rel for rel in pinned if "/" not in rel or _kind(rel) not in compare)
        if stray:
            out.append(f"expected/ holds files no compared kind covers: {stray}")
    return out


def _lookup(record, dotted):
    node = record
    for part in dotted.split("."):
        if isinstance(node, list):
            node = node[int(part)]
        else:
            node = node[part]
    return node


def _run(case_dir, outdir):
    schema = os.path.join(case_dir, "schema.yaml")
    if not os.path.isfile(schema):
        schema = str(REPO / "config" / "schema.yaml")
    return run_pipeline("design.yaml", schema, str(outdir), verbose=False)


def test_twin_edge_cases_have_valid_expectations():
    """A malformed expect.yaml would make its case pin nothing, so every case folder
    is checked before any is run."""
    root = repo_path("parity", "twin_edge", required=REQUIRE_PARITY)
    assert CASES, f"no twin-edge cases under {root}"
    problems = {case: _problems(os.path.join(root, case)) for case in CASES}
    problems = {case: p for case, p in problems.items() if p}
    assert not problems, problems


# One placeholder keeps the test visible when there are no cases, so a checkout that
# lost them fails here instead of collecting nothing.
@pytest.mark.parametrize("case", CASES or [None])
def test_twin_edge_case_matches_its_pinned_outcome(case, tmp_path, monkeypatch):
    root = repo_path("parity", "twin_edge", required=REQUIRE_PARITY)
    if case is None:
        pytest.fail(f"no twin-edge cases under {root}")
    case_dir = os.path.join(root, case)
    problems = _problems(case_dir)
    assert not problems, f"{case}: {problems}"
    expect = _read_expect(case_dir)
    before = _tree(case_dir)
    outdir = tmp_path / "out"
    monkeypatch.chdir(case_dir)

    if expect["outcome"] == "refusal":
        with pytest.raises(Exception, match=re.escape(expect["refusal"])):
            _run(case_dir, outdir)
    else:
        _run(case_dir, outdir)
        got = _pinned(outdir, expect["compare"])
        want = _tree(os.path.join(case_dir, "expected"))
        assert sorted(got) == sorted(want), f"{case}: the run wrote a different set of files"
        differing = sorted(rel for rel in want if got[rel] != want[rel])
        assert not differing, f"{case}: these artefacts differ from the pinned ones: {differing}"
        datasheets = [rel for rel in _tree(outdir)
                      if rel.startswith("reports/") and rel.endswith("_datasheet_py.json")]
        assert len(datasheets) == 1, datasheets
        with open(outdir / datasheets[0], encoding="utf-8") as handle:
            record = json.load(handle)
        for dotted, value in (expect.get("datasheet") or {}).items():
            assert _lookup(record, dotted) == value, f"{case}: datasheet {dotted}"

    # The inputs are fixtures: a run that wrote beside them would change the next run.
    assert _tree(case_dir) == before, f"{case}: the run wrote into the case folder"
