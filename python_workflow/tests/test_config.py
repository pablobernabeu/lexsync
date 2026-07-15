"""Contracts for the shipped configuration files.

The bundled schema copy must stay byte-identical to config/schema.yaml, and the
schema must not advertise keys that no code reads: a key that parses but is
never consulted invites users to edit the one setting (the tie-break) that
underpins the byte-identical R<->Python parity guarantee. Repository-level
checks skip gracefully when the package is tested in isolation.
"""
import os

import pytest
import yaml

import lexsync

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUNDLED_SCHEMA = os.path.join(os.path.dirname(lexsync.__file__), "data", "schema.yaml")


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
