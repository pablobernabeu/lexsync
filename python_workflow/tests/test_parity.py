"""Cross-engine parity: the Python engine reproduces the R engine's selection.

Regenerates the Python stimuli for a design and compares them to the committed R
reference under output/stimuli/. Skips gracefully if the R reference is absent
(e.g. when the package is tested in isolation from the repository).
"""
import os

import pandas as pd
import pytest

from lexsync.run_pipeline import run_pipeline

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

CASES = [
    ("en_freqcontrast_english", "config/design_en_freqcontrast.yaml"),
    ("en_ndensity_english", "config/design_en_ndensity.yaml"),
    ("es_freqcontrast_spanish", "config/design_es_freqcontrast.yaml"),
    ("es_ndensity_spanish", "config/design_es_ndensity.yaml"),
    ("zh_freqcontrast_chinese", "config/design_zh_freqcontrast.yaml"),
]


@pytest.mark.parametrize("base,design", CASES)
def test_r_python_parity(base, design):
    r_ref = os.path.join(REPO, "output", "stimuli", f"{base}_stimuli_R.csv")
    if not os.path.exists(r_ref):
        pytest.skip("R reference output not present; run the R pipeline first")
    if not os.path.exists(os.path.join(REPO, design)):
        pytest.skip("repository design configs not present")

    cwd = os.getcwd()
    os.chdir(REPO)
    try:
        run_pipeline(design, "config/schema.yaml", "output", verbose=False)
    finally:
        os.chdir(cwd)

    r = pd.read_csv(r_ref)
    p = pd.read_csv(os.path.join(REPO, "output", "stimuli", f"{base}_stimuli_py.csv"))
    r_set = set(map(tuple, r[["word", "condition"]].values))
    p_set = set(map(tuple, p[["word", "condition"]].values))
    assert r_set == p_set, (
        f"parity mismatch for {base}: {len(r_set & p_set)}/{len(r_set)} identical"
    )
