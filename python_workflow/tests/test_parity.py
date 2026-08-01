"""Cross-engine parity: the Python engine reproduces the R engine's selection.

Regenerates the Python stimuli for a design and compares them to the committed R
reference under output/stimuli/. Skips gracefully if the R reference is absent
(e.g. when the package is tested in isolation from the repository); CI sets
LEXSYNC_REQUIRE_PARITY=1 to turn those skips into failures, so a job that was
meant to run both engines cannot pass by quietly skipping.
"""
import os

import pandas as pd
import pytest

from lexsync.run_pipeline import run_pipeline

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# When the repository is present both engines must be compared; only a standalone
# install of the package may skip.
REQUIRE_PARITY = os.environ.get("LEXSYNC_REQUIRE_PARITY") == "1"

# base -> (design config, identity columns that must match across engines).
# `set` is the matcher's pairing -- it records which item was matched to which --
# so it is an identity column throughout: every word appears once per design, and
# without `set` the comparison would place no constraint at all on the pairing.
CASES = [
    ("en_freqcontrast_english", "config/design_en_freqcontrast.yaml", ["word", "condition", "set"]),
    ("en_ndensity_english", "config/design_en_ndensity.yaml", ["word", "condition", "set"]),
    ("es_freqcontrast_spanish", "config/design_es_freqcontrast.yaml", ["word", "condition", "set"]),
    ("es_ndensity_spanish", "config/design_es_ndensity.yaml", ["word", "condition", "set"]),
    ("zh_freqcontrast_chinese", "config/design_zh_freqcontrast.yaml", ["word", "condition", "set"]),
    ("en_lexdec_english", "config/design_en_lexdec.yaml", ["target", "condition", "set"]),
    ("en_lexdec_wuggy_english", "config/design_en_lexdec_wuggy.yaml", ["target", "condition", "set"]),
    # Practice and filler blocks. The stimuli file holds only the analysed rows, so this
    # case checks that the split lands the same way in both engines; the presented set,
    # which is larger, reaches the shared loop table that both engines write.
    ("en_lexdec_blocks_english", "config/design_en_lexdec_blocks.yaml",
     ["target", "condition", "set", "trial"]),
    ("en_richdim_english", "config/design_en_richdim.yaml", ["word", "condition", "set"]),
    ("en_freqcontinuous_english", "config/design_en_freqcontinuous.yaml",
     ["word", "condition", "set"]),
    # Balanced list assignment. `list` is an identity column here, so the engines must
    # agree on the deterministic integer search's output and not merely on which words
    # were selected: a one-ulp split in the objective would show up as a different
    # list for some item, which is exactly the failure the integer objective prevents.
    ("en_balanced_lists_english", "config/design_en_balanced_lists.yaml",
     ["word", "condition", "set", "list"]),
    ("en_resample_english", "config/design_en_resample.yaml",
     ["replicate", "word", "condition", "set"]),
    ("en_priming_english", "config/design_en_priming.yaml", ["list", "set", "condition", "prime", "target"]),
    # Variable timing: soa_ms is read from the items, iti_ms is drawn from the
    # keyed hash. Both are identity columns, so the engines must agree on the
    # realised milliseconds and not merely on which stimuli were chosen.
    ("en_priming_jitter_english", "config/design_en_priming_jitter.yaml",
     ["list", "set", "condition", "prime", "target", "soa_ms", "iti_ms"]),
    # The pair-keyed model: member norms joined onto both words, a relational
    # dimension computed in-engine, and continuous selection over pairs. The
    # member and pair columns are identity columns, so the engines must agree on
    # the joined values and the computed overlap, not only on which pairs won.
    ("en_priming_continuous_english", "config/design_en_priming_continuous.yaml",
     ["list", "set", "condition", "prime", "target",
      "target.frequency", "target.length", "pair.lev", "pair.overlap"]),
    ("en_spr_english", "config/design_en_spr.yaml", ["list", "set", "condition", "sentence"]),
    # A supplied candidate pool: the words are the researcher's, the matching is
    # lexsync's. The dimensions are identity columns because they arrive by lookup from
    # the lexicon rather than being computed on the pool, and a wrong reference set would
    # show up here as different neighbourhood values.
    ("en_supplied_pool_english", "config/design_en_supplied_pool.yaml",
     ["word", "condition", "set", "n_density", "old20"]),
    # Cued categorisation. `answer` is an identity column on purpose: it holds the
    # response key `f`, which readr reads as the logical FALSE unless the reader is told
    # otherwise, so this column is the regression guard for that type trap.
    ("en_categorisation_english", "config/design_en_categorisation.yaml",
     ["list", "set", "condition", "target", "category", "answer"]),
    # Reproductions of published designs.
    ("es_gender_repro_spanish", "config/design_es_gender_repro.yaml", ["word", "condition", "set"]),
    ("en_andrews_repro_english", "config/design_en_andrews_repro.yaml", ["word", "condition", "set"]),
    ("en_rastle_repro_english", "config/design_en_rastle_repro.yaml",
     ["list", "set", "condition", "prime", "target", "prime_type"]),
]

# Trial order is part of the parity contract: the keyed-hash shuffle (see the
# counterbalancing module docstring) makes it a pure function of the design, so
# the two engines must agree on every row's `trial` exactly as they must on every
# other value. Rows are still sorted on the identity columns before comparison,
# because the engines may legitimately differ in how they ORDER the rows of the
# stimuli CSV itself; the `trial` value each row carries is what is pinned.
ORDER_COLS: set = set()


@pytest.mark.parametrize("base,design,cols", CASES)
def test_r_python_parity(base, design, cols):
    r_ref = os.path.join(REPO, "output", "stimuli", f"{base}_stimuli_R.csv")
    if not os.path.exists(r_ref):
        if REQUIRE_PARITY:
            pytest.fail(f"R reference missing for {base}; the R pipeline did not run")
        pytest.skip("R reference output not present; run the R pipeline first")
    if not os.path.exists(os.path.join(REPO, design)):
        if REQUIRE_PARITY:
            pytest.fail(f"design config missing: {design}")
        pytest.skip("repository design configs not present")

    cwd = os.getcwd()
    os.chdir(REPO)
    try:
        run_pipeline(design, "config/schema.yaml", "output", verbose=False)
    finally:
        os.chdir(cwd)

    r = pd.read_csv(r_ref)
    p = pd.read_csv(os.path.join(REPO, "output", "stimuli", f"{base}_stimuli_py.csv"))

    # A column vanishing from one engine's output must fail, not quietly narrow
    # the comparison.
    missing = [c for c in cols if c not in r.columns or c not in p.columns]
    assert not missing, f"{base}: identity columns absent from an engine's output: {missing}"

    r_rows = r[cols].astype(str).sort_values(cols).reset_index(drop=True)
    p_rows = p[cols].astype(str).sort_values(cols).reset_index(drop=True)
    assert r_rows.equals(p_rows), (
        f"parity mismatch for {base}: {len(r_rows)} R rows vs {len(p_rows)} Python rows; "
        f"identity columns {cols} differ"
    )

    # Matching the selection and the pairing is necessary but not sufficient: the
    # dimensions each engine computes at run time (n_syllables, bigram_freq,
    # n_density, old20) are exported to the stimuli CSV and must agree too. Every
    # shipped design matches with `standardised_euclidean` or `joint`, both of
    # which are byte-identical across the engines; were a design here to use
    # `mahalanobis` or `optimal`, whose cross-engine identity is not guaranteed,
    # it would need an explicit numeric tolerance instead of this exact test.
    m = r.merge(p, on=cols, suffixes=("_r", "_p"))
    assert len(m) == len(r), f"{base}: identity key {cols} is not unique across engines"
    shared = [c for c in r.columns
              if c in p.columns and c not in cols and c not in ORDER_COLS]
    for c in shared:
        a, b = m[f"{c}_r"], m[f"{c}_p"]
        # Missing on both sides is agreement, and that has to be stated rather than
        # relied on. Until pandas 3, `astype(str)` rendered a missing value as the
        # literal "nan", so two of them compared equal by accident; pandas 3 keeps it
        # missing, NaN != NaN, and a column legitimately empty in both engines --
        # `item`, on a design whose main block generates its own items -- reported
        # every row as differing while the two files were byte-identical.
        both_missing = a.isna().to_numpy() & b.isna().to_numpy()
        differs = (a.astype(str) != b.astype(str)).fillna(True).to_numpy()
        n_bad = int((differs & ~both_missing).sum())
        assert n_bad == 0, f"{base}: column '{c}' differs across engines in {n_bad}/{len(m)} rows"


def test_events_json_is_serialised_as_jsonlite_would():
    """The generated PsychoPy script and OpenSesame experiment must match the R
    engine's byte for byte, and the embedded event JSON is where they most easily
    drift: jsonlite pads no separators and drops a whole number's fractional part, so a
    2000 ms timeout must serialise as 2, not 2.0. A CI step runs both engines into
    separate directories and compares those two files; this pins the rule it relies on.
    """
    from lexsync.scripting import _json_r
    assert _json_r([{"type": "response", "keys": ["left", "right"], "timeout": 2.0}]) == (
        '[{"type":"response","keys":["left","right"],"timeout":2}]')
    # A genuinely fractional timeout keeps its decimal part in both engines.
    assert _json_r({"timeout": 2.5}) == '{"timeout":2.5}'
