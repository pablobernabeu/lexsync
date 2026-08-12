import os
import re

import lexsync

HERE = os.path.dirname(os.path.abspath(__file__))
NAMESPACE = os.path.join(os.path.dirname(os.path.dirname(HERE)), "R_workflow", "NAMESPACE")

# R exports a run-logging and trigger-assignment tier that Python keeps at submodule
# level (lexsync.logging, lexsync.scripting, lexsync.corpora). That split predates the
# two packages' analysis API and is not part of the mirrored surface, so the parity
# check below excludes it rather than forcing names into the Python top level.
R_ONLY_INFRASTRUCTURE = {
    "assign_triggers",
    "lexsync_cache_dir",
    "log_artefact",
    "log_step",
    "new_run_log",
    "write_run_log",
}


def _r_exports():
    with open(NAMESPACE, encoding="utf-8") as handle:
        return set(re.findall(r"^export\((.+)\)$", handle.read(), flags=re.MULTILINE))


def test_r_analysis_exports_are_all_on_the_python_top_level():
    missing = sorted(_r_exports() - R_ONLY_INFRASTRUCTURE - set(lexsync.__all__))
    assert missing == []


def test_all_names_are_importable_from_the_top_level():
    for name in lexsync.__all__:
        assert hasattr(lexsync, name), name


def test_continuous_and_variance_helpers_are_public():
    # Regression guard: these three were exported by R while __init__.py still omitted
    # them, so `from lexsync import ...` failed for the continuous-design API alone.
    from lexsync import match_report_continuous, select_continuous_stimuli, variance_ratio

    assert select_continuous_stimuli is lexsync.matching.select_continuous_stimuli
    assert match_report_continuous is lexsync.validation.match_report_continuous
    assert variance_ratio is lexsync.validation.variance_ratio
