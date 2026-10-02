"""Write a twin-edge case's pinned artefacts from the Python engine.

    python tools/twin_edge.py --update CASE [CASE ...]
    python tools/twin_edge.py --list

A twin-edge case is a folder under parity/twin_edge/ that pins what both engines must
do with one small edge-case design: write these artefacts byte for byte, or raise this
refusal. python_workflow/tests/test_twin_edge.py describes the layout of a case and of
its expect.yaml. CASE is a folder name under parity/twin_edge/ or a path to one.

--update runs the case's design.yaml through the Python engine of this checkout
(python_workflow/src, never an installed copy) and replaces expected/ with the run's
artefacts of the kinds expect.yaml compares, the engine tag stripped from their names.
The R suite's test-twin-edge.R then confirms that the R engine writes the same bytes;
run it before committing, since a case the R engine does not reproduce fails there.
tools/compare_engines.py imports the helpers below.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
CASES_DIR = REPO / "parity" / "twin_edge"

KINDS = ("stimuli", "descriptives", "comparisons", "experiments")
# The engine tag on value artefacts (en_x_stimuli_py.csv). The experiments carry none.
ENGINE_TAG = re.compile(r"_(?:R|py)(\.[^.]+)$")
REPORT_KIND = re.compile(r"_(descriptives|comparisons)(?:_(?:R|py))?\.[^.]+$")
# The per-engine provenance records, which name the engine that wrote them. The CI
# tree diff leaves them out with -x '*_datasheet_*' -x '*_run_log_*'.
PROVENANCE = re.compile(r"_(?:datasheet|run_log)_")


def use_checkout_engine():
    """Put this checkout's Python package first on the path, so the engine compared or
    pinned is the one beside the R sources, not whatever lexsync is installed."""
    src = str(REPO / "python_workflow" / "src")
    if src not in sys.path:
        sys.path.insert(0, src)


def kind_of(rel: str) -> str | None:
    """The artefact kind of a path relative to an output directory ('stimuli/x.csv')
    or to expected/, with or without the engine tag, or None for provenance
    (datasheets and run logs), which differs by engine."""
    folder, _, name = rel.partition("/")
    if folder in ("stimuli", "experiments"):
        return folder
    match = REPORT_KIND.search(name)
    return match.group(1) if match else None


def strip_tag(rel: str) -> str:
    return ENGINE_TAG.sub(r"\1", rel)


def tree(root) -> dict:
    """Every file under `root`, as {relative path with '/' separators: bytes}."""
    out = {}
    for d, _, files in os.walk(root):
        for f in files:
            full = os.path.join(d, f)
            with open(full, "rb") as handle:
                out[os.path.relpath(full, root).replace(os.sep, "/")] = handle.read()
    return out


def artefacts(outdir, kinds=KINDS) -> dict:
    """A run's artefacts of the given kinds, keyed by tag-stripped relative path."""
    return {strip_tag(rel): data for rel, data in tree(outdir).items()
            if kind_of(rel) in kinds}


def comparable(outdir) -> dict:
    """Every file a run wrote except the datasheets and run logs, keyed by tag-stripped
    relative path. A file of a kind no case pins yet is still compared across engines."""
    return {strip_tag(rel): data for rel, data in tree(outdir).items()
            if not PROVENANCE.search(rel.rpartition("/")[2])}


def read_expect(case_dir) -> dict:
    with open(os.path.join(case_dir, "expect.yaml"), encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def case_schema(case_dir) -> str:
    """The case's own schema.yaml, or the repository's config/schema.yaml."""
    own = os.path.join(case_dir, "schema.yaml")
    return own if os.path.isfile(own) else str(REPO / "config" / "schema.yaml")


def find_cases(root=CASES_DIR) -> list:
    root = Path(root)
    if (root / "expect.yaml").is_file():
        return [root]
    if not root.is_dir():
        return []
    return sorted(p for p in root.iterdir() if (p / "expect.yaml").is_file())


def resolve_case(name: str) -> Path:
    path = Path(name)
    if not (path / "expect.yaml").is_file():
        path = CASES_DIR / name
    if not (path / "expect.yaml").is_file():
        raise SystemExit(f"twin_edge: no case '{name}' (looked for {path / 'expect.yaml'})")
    return path.resolve()


def run_python(case_dir, outdir):
    """Run a case's design through this checkout's Python engine, from the case folder
    so that its input paths resolve."""
    use_checkout_engine()
    from lexsync.run_pipeline import run_pipeline
    cwd = os.getcwd()
    os.chdir(case_dir)
    try:
        return run_pipeline("design.yaml", case_schema(case_dir), str(outdir), verbose=False)
    finally:
        os.chdir(cwd)


def update(case_dir: Path) -> int:
    expect = read_expect(case_dir)
    if expect.get("outcome") != "artefacts":
        print(f"{case_dir.name}: outcome is {expect.get('outcome')!r}; "
              "only an artefacts case has an expected/ folder")
        return 1
    compare = list(expect.get("compare") or [])
    unknown = [k for k in compare if k not in KINDS]
    if not compare or unknown:
        print(f"{case_dir.name}: compare must list kinds from {list(KINDS)}")
        return 1
    with tempfile.TemporaryDirectory(prefix="twin_edge_") as tmp:
        run_python(case_dir, Path(tmp) / "out")
        pinned = artefacts(Path(tmp) / "out", compare)
    expected = case_dir / "expected"
    if expected.exists():
        shutil.rmtree(expected)
    for rel, data in sorted(pinned.items()):
        target = expected / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(f"{case_dir.name}: wrote {len(pinned)} file(s) to {expected}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--update", nargs="+", metavar="CASE",
                       help="write expected/ for these cases from the Python engine")
    group.add_argument("--list", action="store_true", help="list the cases and outcomes")
    args = parser.parse_args(argv)
    if args.list:
        for case in find_cases():
            print(f"{case.name}: {read_expect(case).get('outcome')}")
        return 0
    status = 0
    for name in args.update:
        status |= update(resolve_case(name))
    return status


if __name__ == "__main__":
    sys.exit(main())
