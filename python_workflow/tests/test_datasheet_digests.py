"""The committed datasheets publish digests that a fresh checkout reproduces.

A datasheet records the SHA-256 of every file a run read and wrote, so that a
reader can confirm the materials are the ones described. That is worth something
only if a fresh checkout reproduces each digest. 28 of the 42 committed datasheets
once recorded the digest of corpora/derived/en.csv or es.csv as one machine had
converted them to CRLF, and two recorded a CRLF copy of
config/design_en_priming_continuous.yaml. Git stores and .gitattributes checks out
all three with LF, so recomputing the digest told the reader the lexicon had been
altered. The tests recompute every digest from the bytes in this checkout, hashed
here with hashlib so that a fault in the package's own sha256_file() cannot hide
one. Twinned in test-datasheet-digests.R.
"""
import hashlib
import json

import pytest
from helper_repo import repo_path


def _reports():
    reports = repo_path("output", "reports", reason="committed reports not available")
    sheets = sorted(reports.glob("*_datasheet_*.json")) if reports.is_dir() else []
    if not sheets:
        pytest.skip("committed reports not available")
    # 21 shipped designs, one datasheet per engine. A sweep that finds far fewer
    # has lost its inputs, and passing it would prove nothing.
    assert len(sheets) >= 40
    return sheets


def _read(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _checkout_sha256(*parts):
    return hashlib.sha256(repo_path(*parts).read_bytes()).hexdigest()


def _recorded_digests(ds):
    """Every (path, sha256) pair a datasheet records, the path relative to the root."""
    ms = ds.get("materials_source") or {}
    rel = ds.get("relational") or {}
    items = ds.get("items") or {}
    pairs = [(ms.get("path"), ms.get("sha256")),
             (ms.get("dimensions_from"), ms.get("dimensions_sha256")),
             (rel.get("member_lexicon"), rel.get("member_lexicon_sha256")),
             (items.get("stimuli_file"), items.get("stimuli_sha256"))]
    pairs += [(t.get("path"), t.get("sha256")) for t in ms.get("norms") or []]
    # An exclusion list written in the design has no file, and its digest is the list's.
    excluded = ms.get("exclusions") or {}
    if excluded.get("path") != "inline":
        pairs.append((excluded.get("path"), excluded.get("sha256")))
    pairs += [(a.get("file"), a.get("sha256")) for a in ds.get("artifacts") or []]
    return [(p, s) for p, s in pairs if p is not None and s is not None]


def test_committed_datasheets_record_digests_this_checkout_reproduces():
    sheets = _reports()
    wrong = []
    checked = 0
    for sheet in sheets:
        for path, recorded in _recorded_digests(_read(sheet)):
            path = path.replace("\\", "/")
            checked += 1
            if not repo_path(path).is_file():
                wrong.append("%s: %s (no such file in the checkout)" % (sheet.name, path))
            elif _checkout_sha256(path) != recorded:
                wrong.append("%s: %s" % (sheet.name, path))
    # Each datasheet names at least its lexicon and its stimuli file.
    assert checked >= 2 * len(sheets)
    assert wrong == [], "digests this checkout does not reproduce:\n" + "\n".join(wrong)


# The design and schema digests carry no path. The pipeline reads the design from
# config/design_<name>.yaml and the schema from config/schema.yaml.
def test_committed_datasheets_record_the_digests_of_the_shipped_design_and_schema():
    sheets = _reports()
    schema = _checkout_sha256("config", "schema.yaml")
    wrong = []
    for sheet in sheets:
        ds = _read(sheet)
        reproducibility = ds.get("reproducibility") or {}
        design = "config/design_%s.yaml" % ds["design"]["name"]
        if not repo_path(design).is_file():
            wrong.append("%s: %s (no such file in the checkout)" % (sheet.name, design))
        elif reproducibility.get("design_sha256") != _checkout_sha256(design):
            wrong.append("%s: %s" % (sheet.name, design))
        if reproducibility.get("schema_sha256") != schema:
            wrong.append("%s: config/schema.yaml" % sheet.name)
    assert wrong == [], "digests this checkout does not reproduce:\n" + "\n".join(wrong)
