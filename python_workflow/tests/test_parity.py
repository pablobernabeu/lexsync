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

# base -> (design config, identity columns that must match across engines)
CASES = [
    ("en_freqcontrast_english", "config/design_en_freqcontrast.yaml", ["word", "condition"]),
    ("en_ndensity_english", "config/design_en_ndensity.yaml", ["word", "condition"]),
    ("es_freqcontrast_spanish", "config/design_es_freqcontrast.yaml", ["word", "condition"]),
    ("es_ndensity_spanish", "config/design_es_ndensity.yaml", ["word", "condition"]),
    ("zh_freqcontrast_chinese", "config/design_zh_freqcontrast.yaml", ["word", "condition"]),
    ("en_lexdec_english", "config/design_en_lexdec.yaml", ["target", "condition"]),
    ("en_richdim_english", "config/design_en_richdim.yaml", ["word", "condition"]),
    ("en_priming_english", "config/design_en_priming.yaml", ["list", "set", "condition", "prime", "target"]),
    ("en_spr_english", "config/design_en_spr.yaml", ["list", "set", "condition", "sentence"]),
]


@pytest.mark.parametrize("base,design,cols", CASES)
def test_r_python_parity(base, design, cols):
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
    cols = [c for c in cols if c in r.columns and c in p.columns]
    r_set = set(map(tuple, r[cols].astype(str).values))
    p_set = set(map(tuple, p[cols].astype(str).values))
    assert r_set == p_set, (
        f"parity mismatch for {base}: {len(r_set & p_set)}/{len(r_set)} identical"
    )
