"""Contracts for the shipped configuration files.

The bundled copies of config/schema.yaml and corpora/registry.yaml must stay
byte-identical to the repository's own, and the schema must not advertise keys
that no code reads: a key that parses but is
never consulted invites users to edit the one setting (the tie-break) that
underpins the byte-identical R<->Python parity guarantee. Repository-level
checks skip gracefully when the package is tested in isolation.

The committed datasheets are checked here too: every sha256 one of them publishes
has to be reproducible from the checkout it ships in.
"""
import json
import os
import re

import pytest
import yaml

import lexsync

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUNDLED_DATA = os.path.join(os.path.dirname(lexsync.__file__), "data")
BUNDLED_SCHEMA = os.path.join(BUNDLED_DATA, "schema.yaml")
BUNDLED_REGISTRY = os.path.join(BUNDLED_DATA, "registry.yaml")
EXAMPLE_LEXICA = ("en_example.csv", "es_example.csv", "zh_example.csv")


def _load(path):
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _repo_file(*parts):
    path = os.path.join(REPO, *parts)
    if not os.path.exists(path):
        pytest.skip("repository configuration not available")
    return path


def test_bundled_schema_matches_repo_schema():
    repo_schema = _repo_file("config", "schema.yaml")
    with open(repo_schema, "rb") as a, open(BUNDLED_SCHEMA, "rb") as b:
        assert a.read() == b.read()


# The registry is mirrored into both packages by hand, and README.md tells the
# reader that adding a corpus takes an entry in corpora/registry.yaml and no code
# change. Both mirrors had already fallen a line behind that file, so an
# installed copy of either package documented the registry format less fully
# than a checkout did.
def test_bundled_registry_matches_repo_registry():
    repo_registry = _repo_file("corpora", "registry.yaml")
    with open(repo_registry, "rb") as a, open(BUNDLED_REGISTRY, "rb") as b:
        assert a.read() == b.read()


# corpora/fetch_corpora.py writes the example slices into both packages at once,
# so a hand-edit or a partial rebuild reaching only one of them would leave the
# two engines demonstrating on different lexica.
def test_bundled_example_lexica_match_across_the_engines():
    for name in EXAMPLE_LEXICA:
        r_copy = _repo_file("R_workflow", "inst", "extdata", name)
        with open(r_copy, "rb") as a, open(os.path.join(BUNDLED_DATA, name), "rb") as b:
            assert a.read() == b.read(), name


# pandas follows os.linesep unless told otherwise, so the builders behind these
# files must pin LF: the datasheet publishes the sha256 of the lexicon a run
# read, and a digest that depends on the machine that built the file tells a
# recipient the materials were altered when they were not.
def test_committed_lexica_carry_no_carriage_return():
    paths = [_repo_file("corpora", "derived", f"{lang}.csv")
             for lang in ("en", "es", "es_gender", "zh")]
    paths += [os.path.join(BUNDLED_DATA, name) for name in EXAMPLE_LEXICA]
    paths += [_repo_file("R_workflow", "inst", "extdata", name) for name in EXAMPLE_LEXICA]
    for path in paths:
        with open(path, "rb") as handle:
            assert b"\r" not in handle.read(), path


# A checkout normalises line endings, so the committed files cannot show which
# platform wrote them. The guard that can is the writer: both repository
# builders pin LF at every to_csv, since pandas otherwise follows os.linesep.
def test_the_corpus_builders_pin_lf():
    for name in ("fetch_corpora.py", "build_es_gender.py"):
        with open(_repo_file("corpora", name), encoding="utf-8") as handle:
            source = handle.read()
        calls = re.findall(r"\.to_csv\([^()]*\)", source, re.S)
        assert calls, name
        for call in calls:
            assert 'lineterminator="\\n"' in call, (name, call)


# Every key in the schema must be read by the code; the tie-break order, the
# TOST choice and the trigger reset value are fixed in matching/validation/
# scripting, so they live in comments, not as (inert) configurable keys.
def test_schema_carries_no_inert_keys():
    schema = _load(BUNDLED_SCHEMA)
    assert "tie_break" not in (schema.get("matching") or {})
    assert "test" not in (schema.get("equivalence") or {})
    assert "reset_value" not in (schema.get("triggers") or {})


# Pins the same contract as "the reproduction design encodes the origin study's
# SD/9 window exactly" in the R engine's test-config.R. The truncated 0.111 gave
# a window 0.1% narrower than the criterion the design claims to reproduce.
def test_es_gender_repro_frequency_tolerance_is_exactly_one_ninth():
    design = _load(_repo_file("config", "design_es_gender_repro.yaml"))
    assert design["matching"]["tolerance_k"]["frequency"] == 1 / 9


# A datasheet publishes the sha256 of everything the run consumed and produced so a
# recipient can verify the materials, which is worth nothing if the digests do not
# match the files the repository ships. 28 committed datasheets recorded digests of
# CRLF copies of inputs that .gitattributes checks out as LF, so anyone who followed
# the instructions and recomputed one concluded the materials had been altered.
# Twinned in the R engine's test-config.R.
def _recorded_digests(ds):
    """Every (path, sha256) pair a datasheet publishes."""
    pairs = []
    ms = ds.get("materials_source") or {}
    pairs.append((ms.get("path"), ms.get("sha256")))
    pairs.append((ms.get("dimensions_from"), ms.get("dimensions_sha256")))
    for table in ms.get("norms") or []:
        pairs.append((table.get("path"), table.get("sha256")))
    rel = ds.get("relational") or {}
    pairs.append((rel.get("member_lexicon"), rel.get("member_lexicon_sha256")))
    items = ds.get("items") or {}
    pairs.append((items.get("stimuli_file"), items.get("stimuli_sha256")))
    for art in ds.get("artifacts") or []:
        pairs.append((art.get("file"), art.get("sha256")))
    return [(p, s) for p, s in pairs if p and s]


def test_committed_datasheets_record_digests_this_checkout_reproduces():
    from lexsync.io_utils import sha256_file
    reports = os.path.join(REPO, "output", "reports")
    if not os.path.isdir(reports):
        pytest.skip("generated reports not available")
    names = sorted(n for n in os.listdir(reports)
                   if "_datasheet_" in n and n.endswith(".json"))
    if not names:
        pytest.skip("generated reports not available")
    assert len(names) >= 40, "the sweep is too small for this test to mean anything"
    wrong = []
    checked = 0
    for name in names:
        with open(os.path.join(reports, name), encoding="utf-8") as handle:
            ds = json.load(handle)
        for path, recorded in _recorded_digests(ds):
            full = os.path.join(REPO, path.replace("\\", "/"))
            if not os.path.exists(full):
                continue
            checked += 1
            if sha256_file(full) != recorded:
                wrong.append("%s: %s" % (name, path))
    assert checked > len(names), "no digest was actually checked"
    assert wrong == [], (
        "these datasheets publish a sha256 no checkout can reproduce, so a reader "
        "verifying the materials is told they have been altered: %s"
        % ", ".join(sorted(set(wrong))))
