"""Byte-level cross-engine parity of the generated value artefacts.

This exists because test_parity.py could not catch a whole class of failure. It reads
both engines' CSVs back with pandas and compares columns, so "1" and "1.0" both become
the float 1.0 and compare equal. Under that test, 13 of the 18 shipped designs differed
byte for byte between the engines and the gate stayed green: 589 whole-number doubles
written "1" by readr and "1.0" by pandas, 56 booleans written "FALSE" and "False", 8
small values written "9e-4" and "0.0009", and -- the one that was not merely cosmetic --
2 reported means that differed in the last decimal the descriptives publish, because
numpy sums pairwise and R's mean() does not.

The package's headline claim is that the two engines produce identical artefacts, and
the README and the reproducibility vignette both say "byte-identical". This test is what
makes that claim checkable. Comparing parsed values is necessary but not sufficient;
comparing bytes is the claim as stated.

The datasheet and run-log files are deliberately excluded and the exclusion is
justified below: they record which engine wrote them, so they cannot be byte-identical
and were never meant to be.
"""
import os

import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REQUIRE_PARITY = os.environ.get("LEXSYNC_REQUIRE_PARITY") == "1"

# Artefacts whose bytes must match exactly. These carry values, not provenance.
VALUE_ARTEFACTS = ("_stimuli_", "_descriptives_", "_comparisons_")

# A datasheet records its own engine, that engine's package versions, and the sha256 of
# its own stimuli file -- which is a different file from the other engine's. A run log
# additionally records wall-clock timestamps. Neither can be byte-identical, and
# test_parity.py's field-level comparison plus test_datasheet.py cover their content.
PROVENANCE_ARTEFACTS = ("_datasheet_", "_run_log_")


def _pairs():
    out = []
    for sub in ("stimuli", "reports"):
        d = os.path.join(REPO, "output", sub)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if "_R." not in name:
                continue
            if not any(tag in name for tag in VALUE_ARTEFACTS):
                continue
            twin = name.replace("_R.", "_py.")
            if os.path.exists(os.path.join(d, twin)):
                out.append((os.path.join(d, name), os.path.join(d, twin)))
    return out


def test_there_are_artefacts_to_compare():
    """A silently empty sweep would make every assertion below vacuous."""
    pairs = _pairs()
    if not pairs:
        if REQUIRE_PARITY:
            pytest.fail("no _R/_py artefact pairs found; neither pipeline ran")
        pytest.skip("no generated artefacts present; run both pipelines first")
    # 19 designs: stimuli always, descriptives and comparisons where a report exists.
    assert len(pairs) >= 40


@pytest.mark.parametrize("which", VALUE_ARTEFACTS)
def test_each_artefact_kind_is_covered(which):
    """Guards the sweep itself: if a naming change made one kind invisible, the byte
    comparison would quietly stop testing it."""
    pairs = _pairs()
    if not pairs:
        pytest.skip("no generated artefacts present")
    assert any(which in os.path.basename(r) for r, _ in pairs), which


def test_value_artefacts_are_byte_identical_across_engines():
    pairs = _pairs()
    if not pairs:
        if REQUIRE_PARITY:
            pytest.fail("no _R/_py artefact pairs found; neither pipeline ran")
        pytest.skip("no generated artefacts present; run both pipelines first")
    differing = []
    for r, p in pairs:
        with open(r, "rb") as a, open(p, "rb") as b:
            if a.read() != b.read():
                differing.append(os.path.basename(r))
    assert differing == [], (
        "these artefacts differ between the engines byte for byte, so the "
        "byte-identical claim does not hold for them: %s" % ", ".join(differing))


def test_provenance_artefacts_are_excluded_deliberately():
    """The exclusion is asserted, not assumed: if a datasheet ever became
    byte-identical, the reason for excluding it would have gone away and this test
    should be revisited rather than silently over-excluding."""
    d = os.path.join(REPO, "output", "reports")
    if not os.path.isdir(d):
        pytest.skip("no generated reports present")
    names = [n for n in os.listdir(d)
             if "_R." in n and any(t in n for t in PROVENANCE_ARTEFACTS)]
    if not names:
        pytest.skip("no provenance artefacts present")
    # Each one names its own engine, which is exactly why it cannot match.
    sample = os.path.join(d, sorted(names)[0])
    text = open(sample, encoding="utf-8").read()
    assert '"R"' in text or "R engine" in text or "engine: R" in text
