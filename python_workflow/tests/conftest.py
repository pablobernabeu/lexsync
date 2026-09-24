import os
import sys

import pytest
import yaml

# Make the package importable without installation, mirroring the repo layout.
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
# And helper_repo.py beside this file. pytest's default import mode puts this
# directory on the path anyway, but --import-mode=importlib does not, and a
# packager who runs the suite that way would otherwise lose every repo-coupled
# module to an ImportError at collection, not a skip.
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import lexsync  # noqa: E402


def _pkg_data(name):
    return os.path.join(os.path.dirname(lexsync.__file__), "data", name)


@pytest.fixture
def schema():
    with open(_pkg_data("schema.yaml"), encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@pytest.fixture
def en_lexicon_path():
    return _pkg_data("en_example.csv")
