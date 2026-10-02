"""Run the R and Python engines over the same designs and compare what they write.

    python tools/compare_engines.py [--config DIR ...] [--keep DIR]

This is the CI parity job's whole-tree comparison, runnable on any platform. Each
engine writes into its own temporary directory, the engine tag is stripped from the
file names (en_x_stimuli_R.csv and en_x_stimuli_py.csv both become en_x_stimuli.csv),
and every file except the datasheets and run logs must match byte for byte. Those two
are per-engine provenance records: each names the engine that wrote it.

Without --config the tool compares config/ and every twin-edge case under
parity/twin_edge/ whose outcome is artefacts. A DIR may be a folder of design_*.yaml
files (run with run_all() from the repository root, as CI does, against DIR's own
schema.yaml), a twin-edge case folder, or a folder of cases. Refusal cases are left to
the two test suites, which check the refusal text.

Both engines come from this checkout: R through pkgload::load_all("R_workflow") and
Python from python_workflow/src. The Rscript executable is taken from the
LEXSYNC_RSCRIPT environment variable, or from PATH. The tool lists every differing
file and exits 1 on any difference or error, 0 when the engines agree.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import twin_edge  # noqa: E402

REPO = twin_edge.REPO


def rscript() -> str:
    exe = os.environ.get("LEXSYNC_RSCRIPT") or shutil.which("Rscript")
    if not exe:
        raise SystemExit("compare_engines: Rscript not found; put it on PATH or set "
                         "LEXSYNC_RSCRIPT to its full path.")
    return exe


def jobs_for(path: Path) -> list:
    """(label, kind, source) for every comparison a --config DIR asks for."""
    path = path.resolve()
    if (path / "expect.yaml").is_file() or any(path.glob("*/expect.yaml")):
        out = []
        for case in twin_edge.find_cases(path):
            if twin_edge.read_expect(case).get("outcome") == "artefacts":
                out.append((f"twin_edge/{case.name}", "case", case))
        return out
    if any(path.glob("design_*.yaml")) or any(path.glob("design_*.yml")):
        return [(path.name, "config", path)]
    raise SystemExit(f"compare_engines: {path} holds neither design_*.yaml files nor "
                     "twin-edge cases")


# One R session runs every job, so the package is loaded once. Each job's error is
# written beside its output directory and the session moves on, as the Python side does.
R_TEMPLATE = r"""
suppressMessages(pkgload::load_all(%(pkg)s, quiet = TRUE))
jobs <- jsonlite::fromJSON(%(jobs)s, simplifyDataFrame = FALSE)
for (job in jobs) {
  old <- setwd(job$wd)
  res <- tryCatch({
    if (identical(job$kind, "config")) {
      run_all(job$source, job$schema, job$out, verbose = FALSE)
    } else {
      run_pipeline("design.yaml", job$schema, job$out, verbose = FALSE)
    }
    NULL
  }, error = function(e) conditionMessage(e))
  setwd(old)
  if (!is.null(res)) writeLines(enc2utf8(res), paste0(job$out, ".error"), useBytes = TRUE)
}
"""


def run_r(specs: list, work: Path) -> None:
    payload = [{"kind": s["kind"], "source": s["source"], "schema": s["schema"],
                "wd": s["wd"], "out": s["out_r"]} for s in specs]
    code = R_TEMPLATE % {"pkg": json.dumps(str(REPO / "R_workflow").replace("\\", "/")),
                         "jobs": json.dumps(json.dumps(payload))}
    # A script file, not -e: given a multi-line -e argument, Rscript on Windows runs
    # its first line and silently drops the rest.
    script = work / "run_engines.R"
    script.write_text(code, encoding="utf-8")
    proc = subprocess.run([rscript(), str(script)], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout + proc.stderr)
        raise SystemExit("compare_engines: the R session failed before it could run the "
                         "designs")


def run_py(spec: dict) -> None:
    twin_edge.use_checkout_engine()
    from lexsync.run_pipeline import run_all, run_pipeline
    cwd = os.getcwd()
    os.chdir(spec["wd"])
    try:
        if spec["kind"] == "config":
            run_all(spec["source"], spec["schema"], spec["out_py"], verbose=False)
        else:
            run_pipeline("design.yaml", spec["schema"], spec["out_py"], verbose=False)
    except Exception as err:  # reported with the comparison, as for R
        Path(spec["out_py"] + ".error").write_text(
            f"{type(err).__name__}: {err}\n{traceback.format_exc()}", encoding="utf-8")
    finally:
        os.chdir(cwd)


def compare(spec: dict) -> list:
    """Messages describing every way the two engines' outputs for a job differ."""
    out = []
    for engine, key in (("R", "out_r"), ("Python", "out_py")):
        err = Path(spec[key] + ".error")
        if err.is_file():
            first = err.read_text(encoding="utf-8").strip().splitlines()[0]
            out.append(f"{engine} engine failed: {first}")
    if out:
        return out
    r = twin_edge.comparable(spec["out_r"])
    p = twin_edge.comparable(spec["out_py"])
    if not r:
        out.append("the engines wrote no artefacts to compare")
    out += [f"only from R: {rel}" for rel in sorted(set(r) - set(p))]
    out += [f"only from Python: {rel}" for rel in sorted(set(p) - set(r))]
    out += [f"differs: {rel}" for rel in sorted(set(r) & set(p)) if r[rel] != p[rel]]
    spec["n_files"] = len(set(r) & set(p))
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Run both lexsync engines and compare their artefacts byte for byte.")
    parser.add_argument("--config", nargs="+", action="extend", metavar="DIR",
                        help="design folders or twin-edge case folders to compare "
                             "(default: config and parity/twin_edge)")
    parser.add_argument("--keep", metavar="DIR",
                        help="write the two engines' outputs here and keep them")
    args = parser.parse_args(argv)
    dirs = [Path(d) for d in (args.config or [REPO / "config", twin_edge.CASES_DIR])]
    jobs = [job for d in dirs for job in jobs_for(d)]
    if not jobs:
        print("compare_engines: nothing to compare")
        return 1

    work = Path(args.keep).resolve() if args.keep else Path(tempfile.mkdtemp(prefix="engines_"))
    try:
        specs = []
        for label, kind, source in jobs:
            base = work / label.replace("/", "__")
            if base.exists():
                shutil.rmtree(base)
            base.mkdir(parents=True)
            schema = (source / "schema.yaml" if kind == "config"
                      else Path(twin_edge.case_schema(source)))
            specs.append({"label": label, "kind": kind, "source": str(source).replace("\\", "/"),
                          "schema": str(schema).replace("\\", "/"),
                          "wd": str(REPO if kind == "config" else source).replace("\\", "/"),
                          "out_r": str(base / "R").replace("\\", "/"),
                          "out_py": str(base / "py").replace("\\", "/")})
        print(f"compare_engines: running R on {len(specs)} job(s)", flush=True)
        run_r(specs, work)
        print(f"compare_engines: running Python on {len(specs)} job(s)", flush=True)
        for spec in specs:
            run_py(spec)
        failed = 0
        for spec in specs:
            problems = compare(spec)
            if problems:
                failed += 1
                print(f"DIFFER {spec['label']}")
                for msg in problems:
                    print(f"  {msg}")
            else:
                print(f"same   {spec['label']} ({spec['n_files']} files)")
        if failed:
            print(f"compare_engines: the engines differ on {failed} of {len(specs)} job(s)")
            return 1
        print(f"compare_engines: the engines agree on all {len(specs)} job(s)")
        return 0
    finally:
        if not args.keep:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
