"""The gender-tagged Spanish lexicon must stay derivable from its source.

`corpora/derived/es_gender.csv` is an input to a worked design
(`config/design_es_gender_repro.yaml`), and it is a derivative of
`corpora/derived/es.csv` rather than an independently retrieved corpus. It was
committed for a while with no script behind it, so nothing caught a drift
between the two. `corpora/build_es_gender.py` now rebuilds it, and this test
asserts the committed file is exactly what that script produces.

The failure this guards against is regenerating the Spanish corpus without
rebuilding the subset, which would leave the demonstration running on a lexicon
that no longer matches the one its parent file describes.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / "corpora" / "build_es_gender.py"


def _load_builder():
    spec = importlib.util.spec_from_file_location("build_es_gender", BUILDER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.skipif(not BUILDER.exists(), reason="repository-only script; absent from an installed copy")
def test_committed_es_gender_matches_the_builder():
    build_es_gender = _load_builder()
    if not build_es_gender.SOURCE.exists() or not build_es_gender.TARGET.exists():
        pytest.skip("derived corpora absent from this checkout")

    built = build_es_gender.build(build_es_gender.read_lexicon(build_es_gender.SOURCE))
    committed = build_es_gender.read_lexicon(build_es_gender.TARGET)

    assert list(built.columns) == list(committed.columns)
    assert len(built) == len(committed), (
        f"builder produced {len(built)} rows, committed file has {len(committed)}; "
        "rebuild with `python corpora/build_es_gender.py`"
    )
    assert list(built.word) == list(committed.word)
    assert built.equals(committed)


@pytest.mark.skipif(not BUILDER.exists(), reason="repository-only script; absent from an installed copy")
def test_gender_follows_the_final_letter():
    build_es_gender = _load_builder()
    if not build_es_gender.TARGET.exists():
        pytest.skip("derived corpora absent from this checkout")
    committed = build_es_gender.read_lexicon(build_es_gender.TARGET)
    endings = {w[-1] for w in committed.word}
    assert endings == {"a", "o"}
    mismatched = [
        w for w, g in zip(committed.word, committed.gender, strict=True)
        if build_es_gender.GENDER_BY_ENDING[w[-1]] != g
    ]
    assert not mismatched, f"gender does not follow the ending for: {mismatched[:5]}"
