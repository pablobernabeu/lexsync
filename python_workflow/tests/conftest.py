import os
import sys

import pytest
import yaml

# Make the package importable without installation, mirroring the repo layout.
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

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
