"""Locating the lexsync repository around the package, for the tests that hold the
package to files kept only in the repository: templates/, config/, items/, corpora/,
output/, apps/, the R package and the citation metadata at the root.

From a checkout the tests run in python_workflow/tests, two levels below the root.
The sdist ships tests/ as well, for conda-forge, Debian and Nix to build from (see
pyproject.toml), and there the same walk ends in whatever directory the sdist was
unpacked into, which can hold anything. A bare name can therefore be somebody
else's file: the R twin's test for templates/ failed CRAN's Linux checks on
finding the unrelated CRAN package of that name. A candidate root counts only if
it carries the R package's own DESCRIPTION under R_workflow/ and python_workflow/
beside it, which is the check R_workflow/tests/testthat/helper-repo.R makes.
Anywhere else REPO is None, and every test that needs it skips.
"""
import re
from pathlib import Path

import pytest


def repo_root():
    """The repository root, or None when the package is not inside its repository."""
    # In the repository this file sits at python_workflow/tests/, so it always has
    # three parents. A shallower path, such as tests/ unpacked straight into / or
    # C:\, cannot be the repository, and indexing past the root there would raise
    # at import and halt collection of the whole suite.
    parents = Path(__file__).resolve().parents
    if len(parents) < 3:
        return None
    root = parents[2]
    desc = root / "R_workflow" / "DESCRIPTION"
    if not desc.is_file() or not (root / "python_workflow").is_dir():
        return None
    try:
        text = desc.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    package = re.search(r"^Package:[ \t]*(\S+)", text, re.MULTILINE)
    return root if package and package.group(1) == "lexsync" else None


# Resolved once, at import, because some modules build their paths and parameters
# from it at collection time.
REPO = repo_root()


def repo_path(*parts, reason="the lexsync repository is not around this package",
              required=False):
    """A path under the repository root, skipping the calling test with `reason`
    when the package is not inside its repository. With `required` the test fails
    instead, for a job that set out to run against the repository."""
    # Report the skip or failure at the caller, which names the test, not here.
    __tracebackhide__ = True
    if REPO is None:
        if required:
            pytest.fail(reason)
        pytest.skip(reason)
    return REPO.joinpath(*parts)
