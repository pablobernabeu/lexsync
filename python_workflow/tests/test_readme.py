"""The README's "Use" example is executable documentation of the library API.

It is presented as the equivalent of `lexsync run config/design_en_freqcontrast.yaml`,
so it must reproduce that pipeline's committed selection. The step that makes it
do so is build_pool: match_stimuli never reads the design's pool_filters, so an
example that omits the pool step silently matches over the whole lexicon.
"""
import re
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]


def _use_snippet():
    text = (REPO / "python_workflow" / "README.md").read_text(encoding="utf-8")
    # The first python fence under "## Use", not necessarily the line after the
    # heading: the section opens with a sentence saying what the example does and
    # that it must be run from a checkout, and it closes with a bash fence for the
    # command-line equivalent.
    match = re.search(r"## Use\b.*?```python\n(.*?)```", text, re.DOTALL)
    assert match, "README 'Use' python fence not found"
    return match.group(1)


def test_readme_use_example_reproduces_pipeline_selection(monkeypatch, tmp_path):
    snippet = _use_snippet()
    # Without this step the design's pool_filters are inert.
    assert "build_pool" in snippet
    monkeypatch.chdir(REPO)
    # The closing export_experiments call is run too, so no statement of the
    # example goes unexercised, but into a temporary directory: the shipped
    # output/ tree is a committed artefact that tests must not regenerate.
    body = snippet.replace('"output/experiments"', repr(str(tmp_path)))
    assert repr(str(tmp_path)) in body, "the export's output directory moved"
    namespace = {}
    exec(body, namespace)
    committed = pd.read_csv(
        REPO / "output" / "stimuli" / "en_freqcontrast_english_stimuli_py.csv")
    assert sorted(namespace["stim"]["word"]) == sorted(committed["word"])
    assert sorted(p.suffix for p in tmp_path.iterdir()) == [
        ".csv", ".csv", ".html", ".osexp", ".py"]


def test_readme_use_example_does_not_assign_triggers_itself():
    """export_experiments assigns them, as api.md and the guide both say and as
    the R vignette's equivalent example relies on, so calling assign_triggers
    first teaches a step the package's own reference tells the reader to skip."""
    assert "assign_triggers(" not in _use_snippet()
