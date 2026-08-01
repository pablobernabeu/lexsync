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


def test_readme_use_example_reproduces_pipeline_selection(monkeypatch):
    snippet = _use_snippet()
    # Without this step the design's pool_filters are inert.
    assert "build_pool" in snippet
    monkeypatch.chdir(REPO)
    # The closing export_experiments call writes into the shipped output/ tree,
    # which tests must not regenerate; the selection contract is fully pinned
    # without it. It is the last statement in the example, so everything from it
    # onwards is dropped. Truncating rather than filtering one line keeps this
    # working when the call is wrapped over several lines, which dropping only
    # the opening line would leave as an orphaned, indented continuation.
    lines = snippet.splitlines()
    cut = next((i for i, line in enumerate(lines)
                if line.startswith("lexsync.export_experiments")), len(lines))
    body = "\n".join(lines[:cut])
    namespace = {}
    exec(body, namespace)
    committed = pd.read_csv(
        REPO / "output" / "stimuli" / "en_freqcontrast_english_stimuli_py.csv")
    assert sorted(namespace["stim"]["word"]) == sorted(committed["word"])
