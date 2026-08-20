"""The experiment templates are mirrored into both packages; the mirrors must match.

templates/ at the repository root is the canonical copy. Both packages carry their
own so an installed copy can reach one without the repository: the Python package
under src/lexsync/templates/, the R package under inst/templates/, and each
resolves its own through find_template() / .lexsync_template().

Nothing enforced that the three agree, and no functional test can. A stale mirror
is still a perfectly valid template: it renders, it runs, and the experiment it
produces is simply not the one the repository documents. For the trigger
templates that is worse than an ordinary staleness bug, because what drifts is
the code that time-locks EEG markers to stimulus onset, and an experiment that
records the wrong onset does not fail, it quietly collects unusable data.

Comparing the bytes is the check that catches it. Twinned with
R_workflow/tests/testthat/test-templates.R,
which holds the R mirror to the same canonical copy. Both skip rather than fail
when the repository is not present, since an installed package checked in
isolation has no root templates/ to compare against.
"""

import os

import pytest

import lexsync

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CANONICAL = os.path.join(REPO, "templates")
PACKAGED = os.path.join(os.path.dirname(lexsync.__file__), "templates")

pytestmark = pytest.mark.skipif(
    not os.path.isdir(CANONICAL), reason="repository templates not available"
)


def _tree(root):
    """Every file below ``root``, as paths relative to it, in a stable order."""
    out = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            full = os.path.join(dirpath, name)
            out.append(os.path.relpath(full, root).replace(os.sep, "/"))
    return sorted(out)


def _read(path):
    with open(path, "rb") as handle:
        return handle.read()


def test_the_packaged_mirror_holds_the_same_files_as_the_repository():
    canonical = _tree(CANONICAL)
    assert canonical, "no templates found in the repository copy"
    assert _tree(PACKAGED) == canonical


@pytest.mark.parametrize("relpath", _tree(CANONICAL) if os.path.isdir(CANONICAL) else [])
def test_each_packaged_template_is_byte_identical_to_the_repository_copy(relpath):
    assert _read(os.path.join(PACKAGED, relpath)) == _read(os.path.join(CANONICAL, relpath))


def test_find_template_resolves_to_the_packaged_copy():
    """The mirror is what an installed package actually serves, so it is the copy
    worth pinning: find_template() prefers it over the working directory."""
    from lexsync.scripting import find_template

    for relpath in _tree(CANONICAL):
        resolved = find_template(relpath)
        assert os.path.exists(resolved)
        assert _read(resolved) == _read(os.path.join(CANONICAL, relpath))
