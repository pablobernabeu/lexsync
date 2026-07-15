import os

import pytest
import yaml

import lexsync
from lexsync.corpora import fetch_corpus, list_corpora


def _registry_path():
    return os.path.join(os.path.dirname(lexsync.__file__), "data", "registry.yaml")


@pytest.fixture
def registry():
    with open(_registry_path(), encoding="utf-8") as handle:
        return yaml.safe_load(handle)


# Pins the same contract as "fetch_corpus refuses an entry that registers only a
# landing page" in the R engine's test-corpora.R: 'url' is the human-facing page
# and 'openlexicon' the delimited file, so falling back to 'url' would cache an
# HTML document as <name>.csv and fail later as a confusing schema error.
def test_fetch_corpus_refuses_landing_page_only_entry(tmp_path):
    with pytest.raises(ValueError, match="landing page"):
        fetch_corpus("subtlex_esp", registry_path=_registry_path())


def test_fetch_corpus_rejects_unregistered_corpus():
    with pytest.raises(ValueError, match="not in the registry"):
        fetch_corpus("subtlex_klingon", registry_path=_registry_path())


# The registry's own header defines 'validated' as a bundled example slice
# demonstrated end to end. Every bundled lexicon is wordfreq-derived, so no
# SUBTLEX entry may claim it; list_corpora() shows 'status' to users.
def test_registry_status_reflects_what_is_actually_shipped(registry):
    corpora = registry["corpora"]
    assert corpora["subtlex_uk"]["status"] == "supported"
    assert corpora["subtlex_esp"]["status"] == "listed"
    assert not any(entry.get("status") == "validated" for entry in corpora.values())
    assert not any("bundled" in entry for entry in corpora.values())


# 'supported' means fetchable into the user cache, which fetch_corpus() can only
# honour through an 'openlexicon' key.
def test_supported_corpora_are_fetchable(registry):
    for name, entry in registry["corpora"].items():
        if entry.get("status") == "supported":
            assert entry.get("openlexicon"), f"{name} is 'supported' but has no openlexicon file"


def test_list_corpora_surfaces_registry_status():
    frame = list_corpora(_registry_path())
    status = dict(zip(frame["name"], frame["status"]))
    assert status["subtlex_uk"] == "supported"
    assert status["subtlex_esp"] == "listed"
    assert "validated" not in set(status.values())
