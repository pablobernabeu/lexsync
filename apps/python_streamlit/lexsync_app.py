# -*- coding: utf-8 -*-
"""lexsync web application (Python / Streamlit).

A browser front-end for the lexsync package. The user assembles a design through
the interface; the app writes the corresponding design configuration, runs the
same verified pipeline that the package and command line use, displays the matched
stimuli, the realised-control report and the materials datasheet, and exports the
reproducible R, Python and command-line code that performs the identical
operation. The application is a front-end only: every result it shows is produced
by the installed lexsync package, and the design it builds is an ordinary YAML
configuration file.

Run from the repository root:
    streamlit run apps/python_streamlit/lexsync_app.py
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

import pandas as pd
import streamlit as st
import yaml

import lexsync

PKG_DIR = os.path.dirname(lexsync.__file__)
SCHEMA_PATH = os.path.join(PKG_DIR, "data", "schema.yaml")
# Where a run directory, and so the download bundle, keeps the schema and the outputs:
# the paths the exported code names. The Shiny app uses the same two.
BUNDLE_SCHEMA = "config/schema.yaml"
BUNDLE_OUTDIR = "output"

DIMENSIONS = ["length", "frequency", "n_density", "old20", "n_syllables", "bigram_freq"]
# The engine's pseudoword generators (items.generation.method). The first is the
# engine default, so the design only names a method when the other is chosen.
GENERATION_METHODS = ["letter_substitution", "subsyllabic"]
DIM_LABEL = {
    "length": "Length", "frequency": "Frequency (Zipf)", "n_density": "Neighbourhood N",
    "old20": "OLD20", "n_syllables": "Syllables", "bigram_freq": "Bigram frequency",
}
PARADIGMS = {
    "Factorial word contrast (corpus matching)": "factorial",
    "Lexical decision (generated pseudowords)": "lexical_decision",
    "Priming (item table)": "priming",
    "Self-paced reading (item table)": "self_paced_reading",
}
# The lexicon the app opens on: English screened against SUBTLEX-US, the lexicon the
# shipped English designs use. The Shiny app opens on the same one.
DEFAULT_LEXICON = "en_v2"
SCREEN_HELP = ("Adds nonstandard: [0, 0] to the pool filters, which keeps only the forms "
               "the lexicon leaves unmarked. In en_v2, a form is marked when SUBTLEX-US "
               "lacks it or when under a tenth of its uses begin with a lower-case letter.")
# Each preset's matched dimensions and matching method, as the repository's design
# files match such contrasts (design_en_freqcontrast.yaml, design_en_ndensity.yaml,
# design_en_andrews_repro.yaml). A preset never matches on a dimension it
# manipulates. The Shiny app's PRESET_MATCHING holds the same table, and
# tests/test_apps.py and test-apps.R pin both.
PRESET_MATCHING = {
    "High vs low frequency": (["length", "n_density", "old20"], "standardised_euclidean"),
    "Dense vs sparse neighbourhood": (["length", "frequency"], "joint"),
    "2x2 frequency x neighbourhood": (["length"], "standardised_euclidean"),
    "Custom": (["length"], "standardised_euclidean"),
}
METHOD_HELP = ("joint/optimal pair two conditions (optimal selects the n pairs of "
               "least summed distance, joint takes the closest pair at each step); "
               "mahalanobis down-weights correlated dimensions. mahalanobis and "
               "optimal use a covariance inverse / assignment solver, so the R and "
               "Python engines agree closely but not byte-for-byte on them.")
EMPTY_MATCH_ON = "Choose at least one dimension to match on."
# The caption under the exported code, chosen by the run's datasheet. Word-identical
# to the Shiny app's.
BYTE_IDENTICAL = ("The R and Python engines select byte-identical stimuli and trial order "
                  "from this configuration.")
APPROXIMATE = ("The R and Python engines select equivalent but not byte-identical stimuli "
               "for this matching method.")
# The notes on the Experiment scripts and Download tabs. Word-identical to the Shiny
# app's.
EXPERIMENT_NOTE = ("The same matched stimuli compile to three presentation targets. The PsychoPy "
                   "and OpenSesame downloads are archives that hold each experiment with the "
                   "tables it reads, so unzip one and run the experiment from that folder. The "
                   "jsPsych page holds its trials and runs on its own.")
DOWNLOAD_NOTE = ("The bundle is the folder the run ran in: the design, the schema at "
                 "config/schema.yaml, the lexicon or item table at the path the design names "
                 "and every output under output/. Running the exported code inside the unzipped "
                 "folder repeats the run.")
# The files each presentation target reads, by the end of their names, and the name its
# download takes after the design's stem. A PsychoPy script loads its conditions file
# from its own folder and an OpenSesame experiment its loop and text tables, so those
# two downloads are archives. The jsPsych page embeds its trials. The Shiny app's
# EXPERIMENT_TARGETS holds the same table.
EXPERIMENT_TARGETS = [
    ("PsychoPy", "_psychopy.zip", ("_psychopy.py", "_psychopy.csv")),
    ("OpenSesame", "_opensesame.zip", (".osexp", "_opensesame.csv", "_opensesame_text.csv")),
    ("jsPsych", ".html", (".html",)),
]


def find_repo_root() -> str:
    """Locate a directory that holds corpora/derived, walking up from the cwd."""
    here = os.path.abspath(os.getcwd())
    for cand in (here, os.path.dirname(here), os.path.dirname(os.path.dirname(here))):
        if os.path.isdir(os.path.join(cand, "corpora", "derived")):
            return cand
    return here


REPO_ROOT = find_repo_root()
CORPORA_DIR = os.path.join(REPO_ROOT, "corpora", "derived")
ITEMS_DIR = os.path.join(REPO_ROOT, "items")


@st.cache_data(show_spinner=False)
def list_corpora() -> dict:
    """Map a human label to each bundled corpus CSV (word + freq_zipf columns)."""
    out = {}
    if os.path.isdir(CORPORA_DIR):
        for f in sorted(os.listdir(CORPORA_DIR)):
            if f.endswith(".csv"):
                out[f[:-4]] = os.path.join(CORPORA_DIR, f)
    return out


@st.cache_data(show_spinner=False)
def corpus_preview(path: str) -> pd.DataFrame:
    return pd.read_csv(path, nrows=5, keep_default_na=False, na_values=["", "NA"])


@st.cache_data(show_spinner=False)
def staged_upload(name: str, digest: str, _data: bytes) -> str:
    """Write an uploaded file to a temporary folder, once for its content.

    Streamlit runs the script again on every widget interaction, and the uploader
    hands back the file it holds each time, so writing the upload where it is
    received made a new folder and a new copy of the file on every rerun. The cache
    is keyed on the name and the content's digest; ``_data``, whose leading
    underscore keeps it out of the key, is written only on the first call.

    Parameters
    ----------
    name : str
        The uploaded file's name, which the written file keeps.
    digest : str
        The SHA-256 of ``_data``.
    _data : bytes
        The uploaded bytes.

    Returns
    -------
    str
        The path of the written file.
    """
    path = os.path.join(tempfile.mkdtemp(prefix="lexsync_upload_"), name)
    with open(path, "wb") as fh:
        fh.write(_data)
    return path


def received_upload(up) -> str:
    """The path of an uploaded file's copy on disk (see :func:`staged_upload`).

    A copy that has gone since it was cached, as a sweep of the temporary folder may
    remove it, is written again.
    """
    data = up.getvalue()
    digest = hashlib.sha256(data).hexdigest()
    path = staged_upload(up.name, digest, data)
    if not os.path.exists(path):
        staged_upload.clear()
        path = staged_upload(up.name, digest, data)
    return path


@st.cache_data(show_spinner=False)
def lexicon_columns(path: str) -> list:
    """The column names of a lexicon CSV, or an empty list when it cannot be read."""
    try:
        return list(pd.read_csv(path, nrows=0).columns)
    except (OSError, ValueError):
        return []


def pool_filters(length_range, frequency_range, columns, screened: bool) -> dict:
    """The design's pool filters from the two sliders and the screen checkbox.

    A lexicon with a ``nonstandard`` column marks the forms its screen flags, and
    ``nonstandard: [0, 0]`` keeps only the unmarked ones, as the shipped English
    designs do. Mirrors pool_filters() in the Shiny app.

    Parameters
    ----------
    length_range, frequency_range : sequence
        The two ends of each slider.
    columns : list
        The chosen lexicon's column names.
    screened : bool
        Whether 'Screened forms only' is ticked.

    Returns
    -------
    dict
        The ``pool_filters`` mapping.
    """
    filters = {"length": list(length_range), "frequency": list(frequency_range)}
    if screened and "nonstandard" in columns:
        filters["nonstandard"] = [0, 0]
    return filters


# An empty bound is NaN, as the Shiny presets' is NA_real_. A column of None alone is
# one Streamlit's editor offers as free text and passes back unconverted, so the
# presets with one factor took text in lower2 and upper2. A NaN keeps the column
# numeric, and the editor then takes only numbers in it.
def _preset_row(name, dim, lo, hi, cats="", dim2="", lo2=float("nan"), hi2=float("nan")):
    return {"name": name, "dimension": dim, "lower": lo, "upper": hi, "categories": cats,
            "dimension2": dim2, "lower2": lo2, "upper2": hi2}


def preset_rows(preset: str) -> list:
    """The conditions table a preset fills, one mapping per row.

    The same rows as preset_df() in the Shiny app. Any name that is not a preset
    gives the Custom rows.
    """
    if preset == "High vs low frequency":
        return [_preset_row("high_frequency", "frequency", 5.2, 7.0),
                _preset_row("low_frequency", "frequency", 3.8, 4.4)]
    if preset == "Dense vs sparse neighbourhood":
        return [_preset_row("dense_neighbourhood", "n_density", 5.0, 100.0),
                _preset_row("sparse_neighbourhood", "n_density", 0.0, 1.0)]
    if preset == "2x2 frequency x neighbourhood":
        return [_preset_row("HF_largeN", "frequency", 5.0, 7.0, "", "n_density", 9.0, 100.0),
                _preset_row("HF_smallN", "frequency", 5.0, 7.0, "", "n_density", 0.0, 5.0),
                _preset_row("LF_largeN", "frequency", 2.5, 4.2, "", "n_density", 9.0, 100.0),
                _preset_row("LF_smallN", "frequency", 2.5, 4.2, "", "n_density", 0.0, 5.0)]
    return [_preset_row("condition_a", "frequency", 5.0, 7.0),
            _preset_row("condition_b", "frequency", 3.5, 4.5)]


def _bound(x):
    """One end of a condition's window as a number, or None when the cell holds none.

    A cell that holds text which is not a number, such as '4,5', counts as empty, so
    the factor it belongs to is left out. The table is read while the page is drawn,
    above the handler that reports a pipeline error, and a bare float() on such a cell
    stopped the whole page. Mirrors bound() in the Shiny app.
    """
    try:
        value = float(x)
    except (TypeError, ValueError):
        return None
    return None if value != value else value


def conditions_from_table(cond_df: pd.DataFrame) -> list:
    """Read the conditions editor's rows into the design's ``conditions`` list.

    A row contributes a condition when it names one and defines at least one window,
    a category list or a pair of numeric bounds. The optional second factor is added
    only when both of its bounds are numbers. Mirrors conditions_from_table() in the
    Shiny app.
    """
    conditions = []
    for _, row in cond_df.iterrows():
        nm = str(row.get("name") or "").strip()
        dim = str(row.get("dimension") or "").strip()
        if not nm or not dim:
            continue
        cats = str(row.get("categories") or "").strip()
        define_by = {}
        lower, upper = _bound(row.get("lower")), _bound(row.get("upper"))
        if cats:
            define_by[dim] = [c.strip() for c in cats.split(",") if c.strip()]
        elif lower is not None and upper is not None:
            define_by[dim] = [lower, upper]
        dim2 = str(row.get("dimension2") or "").strip()
        lower2, upper2 = _bound(row.get("lower2")), _bound(row.get("upper2"))
        if dim2 and lower2 is not None and upper2 is not None:
            define_by[dim2] = [lower2, upper2]
        if define_by:
            conditions.append({"name": nm, "define_by": define_by})
    return conditions


def manipulated_matches(conditions: list, match_on: list) -> list:
    """The matched dimensions on which the conditions take different windows.

    Matching on such a dimension works against the contrast the windows define. A
    band that every condition shares only restricts the pool, so it is not listed.
    A dimension that one condition restricts and another leaves open is listed.
    Mirrors manipulated_matches() in the Shiny app.

    Parameters
    ----------
    conditions : list
        The design's ``conditions``.
    match_on : list
        The dimensions chosen under 'Match on'.

    Returns
    -------
    list
        The listed dimensions, in ``match_on`` order.
    """
    out = []
    for dim in match_on:
        windows = [(c.get("define_by") or {}).get(dim) for c in conditions]
        if any(w is not None for w in windows) and any(w != windows[0] for w in windows):
            out.append(dim)
    return out


def manipulation_warning(dims: list) -> str | None:
    """The warning shown under 'Match on' for :func:`manipulated_matches`, or None."""
    if not dims:
        return None
    named = dims[0] if len(dims) == 1 else ", ".join(dims[:-1]) + " and " + dims[-1]
    return (f"'Match on' includes {named}, on which the conditions take different "
            "windows. Matching on a dimension the conditions manipulate works against "
            "the contrast they define.")


def parity_claim(record: dict | None) -> str:
    """The caption under the exported code, from the run's datasheet record.

    ``selection.cross_engine`` says whether the two engines select byte-identical
    materials for the run: ``mahalanobis`` and ``optimal`` agree only approximately,
    because their linear algebra differs in the last bits between the engines. A
    record without the field is read as the datasheet's own renderer reads it.
    Mirrors parity_claim() in the Shiny app.
    """
    cross = str(((record or {}).get("selection") or {}).get("cross_engine", "byte-identical"))
    return APPROXIMATE if cross.startswith("approximate") else BYTE_IDENTICAL


def interval_label(record: dict | None) -> str:
    """The heading of the d interval column, from the run's datasheet record.

    The interval beside a TOST at alpha is the 1 - 2 alpha interval, so 90% at the
    default alpha of .05. Mirrors interval_label() in the Shiny app.
    """
    alpha = ((record or {}).get("equivalence") or {}).get("alpha", 0.05)
    return f"{(1 - 2 * float(alpha)) * 100:g}% CI"


def yaml_block(d: dict) -> str:
    return yaml.safe_dump(d, sort_keys=False, allow_unicode=True, default_flow_style=False)


def reproduction_code(design: dict, design_filename: str) -> dict:
    """The R, Python and command-line code that reproduces this design exactly."""
    cfg = design_filename
    py = (
        "# Python\n"
        "from lexsync import run_pipeline\n\n"
        f'run_pipeline("{cfg}", schema_path="config/schema.yaml", outdir="output")'
    )
    r = (
        "# R\n"
        "library(lexsync)\n\n"
        f'run_pipeline("{cfg}", schema_path = "config/schema.yaml", outdir = "output")'
    )
    # Double quotes outside and single quotes inside, which bash, cmd.exe and both
    # PowerShells pass on unchanged: clean_meta() refuses every character in a
    # design's name that would end either string. Each comment has a line of its
    # own, because cmd.exe passes a trailing # on as one more argument. Word-identical
    # to the Shiny app's block.
    cli = (
        "# R\n"
        f"Rscript -e \"lexsync::run_pipeline('{cfg}', schema_path = 'config/schema.yaml', "
        "outdir = 'output')\"\n"
        "# Python console script\n"
        f'lexsync run "{cfg}"\n'
        "# Python (module form)\n"
        f'python -m lexsync run "{cfg}"'
    )
    return {"yaml": yaml_block(design), "python": py, "r": r, "cli": cli}


def _write_design_yaml(design: dict, path: str) -> str:
    """Write the design YAML with LF line endings on every platform.

    Without newline="\\n" the text-mode default writes CRLF on Windows, and the
    pipeline hashes this file into the datasheet's design_sha256, so its bytes
    must depend on the content alone, never on the operating system. The text is
    the one the Reproducible code tab shows. The Shiny app's write_yaml_lf pins the
    same convention.
    """
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(yaml_block(design))
    return path


def staged_inputs(design: dict, lexicon_abs: str | None, items_abs: str | None) -> dict:
    """Map each input file the design names to the file chosen for it.

    Mirrors staged_inputs() in the Shiny app.

    Parameters
    ----------
    design : dict
        The design as shown to the user, carrying design-relative paths.
    lexicon_abs, items_abs : str, optional
        The chosen or uploaded lexicon and item table.

    Returns
    -------
    dict
        Design-relative path -> the file to place there.
    """
    out = {}
    if lexicon_abs and isinstance(design.get("lexicon"), str):
        out[design["lexicon"]] = lexicon_abs
    items = design.get("items")
    if items_abs and isinstance(items, dict) and isinstance(items.get("path"), str):
        out[items["path"]] = items_abs
    return out


# A path that would leave the run directory: absolute, under a drive or a home
# directory, or climbing out through "..".
_OUTSIDE = re.compile(r"^([/\\~]|[A-Za-z]:)")


def bundle_path(root: str, rel: str) -> str:
    """The place of a design-relative path inside a run directory.

    An uploaded file's name and the design's name both reach this, so a path that
    would put a file outside the directory is refused. Mirrors bundle_path() in the
    Shiny app.
    """
    parts = re.split(r"[/\\]", rel) if isinstance(rel, str) else []
    if not rel or not isinstance(rel, str) or _OUTSIDE.match(rel) or ".." in parts:
        raise ValueError(f"The path '{rel}' does not lie inside the bundle.")
    return os.path.join(root, *parts)


def stage_run(design: dict, design_filename: str, inputs: dict) -> str:
    """Lay out a temporary directory as the download bundle, ready to run.

    It holds the design as displayed, under ``design_filename``, the schema at
    config/schema.yaml and every input at the path the design records. The run
    happens in it and the download archives it, so the datasheet checksums the
    files the bundle holds and records the paths the exported code uses. Mirrors
    stage_run() in the Shiny app.

    Parameters
    ----------
    design : dict
        The design as shown to the user.
    design_filename : str
        The name the design takes, which the exported code names.
    inputs : dict
        A :func:`staged_inputs` mapping.

    Returns
    -------
    str
        The directory.
    """
    root = tempfile.mkdtemp(prefix="lexsync_app_")
    try:
        def place(rel, source=None):
            dest = bundle_path(root, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            if source is not None:
                shutil.copyfile(source, dest)
            return dest

        _write_design_yaml(design, place(design_filename))
        place(BUNDLE_SCHEMA, SCHEMA_PATH)
        for rel, source in inputs.items():
            place(rel, source)
    except Exception:
        shutil.rmtree(root, ignore_errors=True)
        raise
    return root


def run_command(design_filename: str) -> list:
    """The command a run executes in its directory.

    The exported command line, ``python -m lexsync run "<design>"``, with the schema
    and the output directory it resolves to in that directory written out.
    """
    return [sys.executable, "-m", "lexsync", "run", design_filename,
            "--schema", BUNDLE_SCHEMA, "--outdir", BUNDLE_OUTDIR]


def _run_environment() -> dict:
    """The environment of the run, which imports the lexsync this app imported.

    A copy installed into site-packages is found there anyway. A source checkout
    (PYTHONPATH or the test suite's path) is put first on PYTHONPATH, so the run
    cannot pick up another install. UTF-8 output keeps a word outside the console's
    code page from stopping the run while it narrates.
    """
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    parent = os.path.dirname(PKG_DIR)
    if os.path.basename(parent) not in ("site-packages", "dist-packages"):
        env["PYTHONPATH"] = os.pathsep.join(p for p in (parent, env.get("PYTHONPATH")) if p)
    return env


def discard_run_dir(path: str | None) -> None:
    """Remove a run directory whose results have left the screen.

    Each holds a copy of the run's inputs and every output, and a long-lived app
    otherwise kept one per press of Run.
    """
    if path and os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)


def run_design(design: dict, design_filename: str, inputs: dict) -> dict:
    """Run the design in a directory laid out like the bundle, and collect the outputs.

    The run is a separate process started in that directory. ``os.chdir`` would move
    every session at once, because Streamlit runs each session's script on a thread
    of one process. A refused design raises RuntimeError with the pipeline's message,
    and its directory is removed.
    """
    root = stage_run(design, design_filename, inputs)
    proc = subprocess.run(run_command(design_filename), cwd=root, env=_run_environment(),
                          capture_output=True, encoding="utf-8", errors="replace", check=False)
    if proc.returncode != 0:
        discard_run_dir(root)
        lines = [line for line in proc.stderr.splitlines() if line.strip()]
        raise RuntimeError(lines[-1] if lines else
                           f"the pipeline stopped with exit status {proc.returncode}")
    return collect_run(root, design)


def collect_run(root: str, design: dict) -> dict:
    """Read a finished run's outputs for the result tabs.

    Parameters
    ----------
    root : str
        The run directory.
    design : dict
        The design that ran, whose stem names its files.

    Returns
    -------
    dict
        The directory (``root``), the output paths (``paths``) and the tables, the
        datasheet and its record the tabs show.
    """
    base = lexsync.design_stem(design)
    out = os.path.join(root, BUNDLE_OUTDIR)

    def output(sub, name):
        path = os.path.join(out, sub, name)
        return path if os.path.exists(path) else None

    exp_dir = os.path.join(out, "experiments")
    files = (sorted(os.path.join(exp_dir, f) for f in os.listdir(exp_dir))
             if os.path.isdir(exp_dir) else [])
    result = {"stimuli": output("stimuli", f"{base}_stimuli_py.csv"),
              "descriptives": output("reports", f"{base}_descriptives_py.csv"),
              "comparisons": output("reports", f"{base}_comparisons_py.csv"),
              "experiments": {"files": files}}
    bundle = {"root": root, "paths": result, "outdir": out}
    bundle["stimuli"] = pd.read_csv(result["stimuli"])
    bundle["descriptives"] = (pd.read_csv(result["descriptives"])
                              if result["descriptives"] else None)
    bundle["comparisons"] = (pd.read_csv(result["comparisons"])
                             if result["comparisons"] else None)
    ds_md = os.path.join(out, "reports", f"{base}_datasheet_py.md")
    bundle["datasheet_md"] = None
    if os.path.exists(ds_md):
        # A `with` block, not open(...).read(): the app is long-lived and reruns this
        # on every widget interaction, so a handle left to the garbage collector is a
        # descriptor leak rather than a style point.
        with open(ds_md, encoding="utf-8") as handle:
            bundle["datasheet_md"] = handle.read()
    # The machine-readable datasheet, which the caption under the exported code and
    # the interval heading are read from.
    ds_json = os.path.join(out, "reports", f"{base}_datasheet_py.json")
    bundle["record"] = None
    if os.path.exists(ds_json):
        with open(ds_json, encoding="utf-8") as handle:
            bundle["record"] = json.load(handle)
    bundle["base"] = base
    return bundle


def positive_tolerances(values: dict) -> dict:
    """Keep the dimensions the user gave a positive tolerance k.

    A k of zero means "leave the schema default for this dimension alone". Carried
    into the design it would instead pin the pre-filter window to zero width and
    admit no candidate at all, so it is dropped here rather than written out.

    Parameters
    ----------
    values : dict
        Dimension name -> k, in the order the dimensions are matched on.

    Returns
    -------
    dict
        The subset with k > 0, order preserved.
    """
    return {d: float(k) for d, k in values.items() if k is not None and k > 0}


def experiment_files(experiments: dict) -> list:
    """Every experiment file a run wrote, for the Experiment tab.

    A design with several counterbalancing versions writes one OpenSesame experiment
    per version, each with its own tables, and ``export_experiments`` lists them all
    under ``files``. A result without ``files``, from an older lexsync, offers its
    three scripts. Mirrors experiment_files() in the Shiny app.

    Parameters
    ----------
    experiments : dict
        The ``experiments`` entry of a run's output paths (:func:`collect_run`).

    Returns
    -------
    list
        The paths, in the order the export wrote them.
    """
    if "files" in experiments:
        return list(experiments["files"])
    return [experiments[k] for k in ("psychopy", "opensesame", "jspsych") if experiments.get(k)]


def experiment_downloads(files: list, base: str) -> list:
    """The Experiment scripts tab's downloads, one per presentation target.

    Each takes the files of its target from ``files``, in the order given, and its
    name from the design's stem (see ``EXPERIMENT_TARGETS``). A target that wrote
    nothing is left out. Mirrors experiment_downloads() in the Shiny app.

    Parameters
    ----------
    files : list
        The paths :func:`experiment_files` gives.
    base : str
        The stem every file of the design is named after.

    Returns
    -------
    list
        One mapping per download, with ``target``, ``file_name`` and ``files``.
    """
    out = []
    for target, suffix, endings in EXPERIMENT_TARGETS:
        chosen = [f for f in files if os.path.basename(f).endswith(endings)]
        if chosen:
            out.append({"target": target, "file_name": base + suffix, "files": chosen})
    return out


def experiment_payload(group: dict) -> bytes:
    """The bytes of one :func:`experiment_downloads` entry.

    The jsPsych page as it stands, and any other target as a zip archive holding
    its files side by side, which is where each experiment looks for its tables.
    """
    if len(group["files"]) == 1 and group["file_name"].endswith(".html"):
        with open(group["files"][0], "rb") as handle:
            return handle.read()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(group["files"], key=os.path.basename):
            z.write(path, os.path.basename(path))
    return buf.getvalue()


def make_zip(bundle: dict) -> bytes:
    """Archive a run directory whole, at paths relative to it.

    The directory holds the design, the schema, the inputs at the paths the design
    records and every output (see :func:`stage_run`), so the exported code runs from
    the unzipped archive and rewrites its outputs.

    Parameters
    ----------
    bundle : dict
        A :func:`run_design` result, whose ``root`` is archived.

    Returns
    -------
    bytes
        The zip archive.
    """
    root = bundle["root"]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for folder, dirs, files in os.walk(root):
            dirs.sort()
            for f in sorted(files):
                full = os.path.join(folder, f)
                z.write(full, os.path.relpath(full, root).replace(os.sep, "/"))
    return buf.getvalue()


# --------------------------------------------------------------------------- UI

st.set_page_config(page_title="lexsync", layout="wide", page_icon="🔤")
st.title("lexsync")
st.markdown(
    "Reproducible psycholinguistic stimulus design, running on the Python engine. "
    "Assemble a design below, run the verified lexsync pipeline, and export the "
    "design file together with the R, Python and command-line code that reproduces "
    "it. Under the deterministic matching methods, which include the default, the two "
    "engines select byte-identical stimuli, so the exported code runs the same "
    "operation in either ecosystem."
)

corpora = list_corpora()
if not corpora:
    st.warning(
        "No bundled corpora were found under `corpora/derived/`. Launch the app from "
        "the lexsync repository root, or upload a lexicon CSV below."
    )

with st.sidebar:
    st.header("Design")
    paradigm_label = st.selectbox("Paradigm", list(PARADIGMS), index=0)
    paradigm = PARADIGMS[paradigm_label]
    name = st.text_input("Design name", value="my_design")
    language = st.text_input("Language label", value="english")
    # Here with the other design fields: Streamlit draws a widget where its call is
    # made, and a call further down put this one under the rule and the version line.
    font = st.text_input("Stimulus font", value="Courier New")
    st.divider()
    st.caption(
        "lexsync " + getattr(lexsync, "__version__", "") +
        " · the app runs the installed package, not a re-implementation."
    )

design: dict = {"name": name, "language": language}
lexicon_abs = None
items_abs = None
# Design-relative path -> absolute temp path, for inputs the user uploaded and the
# repository therefore does not hold. Recorded where the upload is written, so the
# key is by construction the same string the design names.
uploaded_inputs: dict = {}

# --------------------------------------------------------- corpus / generate UI
if paradigm in ("factorial", "lexical_decision"):
    st.subheader("Corpus")
    col1, col2 = st.columns([2, 3])
    with col1:
        corpus_choice = st.selectbox(
            "Lexicon", list(corpora) + ["Upload a CSV…"],
            index=list(corpora).index(DEFAULT_LEXICON) if DEFAULT_LEXICON in corpora else 0,
            help="A word-frequency lexicon with at least `word` and `freq_zipf` columns.",
        )
    if corpus_choice == "Upload a CSV…":
        up = st.file_uploader("Lexicon CSV (word, freq_zipf, …)", type=["csv"])
        if up is not None:
            lexicon_abs = received_upload(up)
            design["lexicon"] = f"corpora/{up.name}"
            uploaded_inputs[design["lexicon"]] = lexicon_abs
    else:
        lexicon_abs = corpora[corpus_choice]
        design["lexicon"] = f"corpora/derived/{corpus_choice}.csv"
        with col2:
            st.dataframe(corpus_preview(lexicon_abs), width="stretch", height=150)

    st.subheader("Pool filters")
    c1, c2 = st.columns(2)
    with c1:
        length = st.slider("Length (letters/characters)", 1, 20, (3, 7))
    with c2:
        frequency = st.slider("Frequency (Zipf)", 1.0, 8.0, (3.5, 7.0), step=0.1)
    columns = lexicon_columns(lexicon_abs) if lexicon_abs else []
    screened = ("nonstandard" in columns
                and st.checkbox("Screened forms only", value=True, help=SCREEN_HELP))
    design["pool_filters"] = pool_filters(length, frequency, columns, screened)

if paradigm == "factorial":
    design["paradigm"] = "factorial"
    st.subheader("Conditions")
    st.caption(
        "Each condition is defined by a window on one dimension (numeric range) or "
        "by a category (comma-separated values, e.g. a `gender` column). Leave the "
        "categorical column blank to use the numeric range."
    )
    st.caption(
        "Columns *dimension/lower/upper* set the first factor (or *categories* for a "
        "categorical column such as `gender`). The optional *dimension2/lower2/upper2* "
        "add a second factor, so a row can define a full 2x2 cell."
    )
    preset = st.selectbox("Start from a preset", list(PRESET_MATCHING))
    cond_default = pd.DataFrame(preset_rows(preset))
    match_default, method_default = PRESET_MATCHING.get(preset, PRESET_MATCHING["Custom"])

    cond_df = st.data_editor(
        cond_default, num_rows="dynamic", width="stretch", key=f"cond_editor_{preset}",
        column_config={
            "dimension": st.column_config.SelectboxColumn("dimension", options=DIMENSIONS),
            "dimension2": st.column_config.SelectboxColumn("dimension2", options=[""] + DIMENSIONS),
        },
    )
    design["conditions"] = conditions_from_table(cond_df)

    design["n_per_condition"] = st.number_input("Items per condition", 4, 400, 80, step=2)
    design["match_on"] = st.multiselect(
        "Match on (controlled dimensions)", DIMENSIONS, default=match_default,
        format_func=lambda d: DIM_LABEL[d],
    )
    if not design["match_on"]:
        st.warning(EMPTY_MATCH_ON)
    else:
        note = manipulation_warning(manipulated_matches(design["conditions"], design["match_on"]))
        if note:
            st.warning(note)
    c1, c2 = st.columns(2)
    with c1:
        methods = ["standardised_euclidean", "joint", "mahalanobis", "optimal"]
        method = st.radio(
            "Matching method", methods,
            index=methods.index(method_default) if method_default in methods else 0,
            help=METHOD_HELP,
        )
    with c2:
        n_sets = st.number_input("Resampled disjoint sets (0 = off)", 0, 20, 0,
                                 help="Draw several disjoint matched sets, no item reused, "
                                      "so items can be treated as a random factor.")
    matching = {"method": method}
    with st.expander("Advanced: per-dimension tolerance windows (mean ± k·SD)"):
        st.caption("Override the schema defaults; e.g. frequency 0.111 reproduces the "
                   "mean ± SD/9 window of González Alonso et al. (2025).")
        tol = positive_tolerances({
            d: st.number_input(f"k for {DIM_LABEL[d]}", 0.0, 10.0, 0.0, step=0.05, key=f"tol_{d}")
            for d in design["match_on"]
        })
        if tol:
            matching["tolerance_k"] = tol
    design["matching"] = matching
    if n_sets and n_sets >= 2:
        design["resample"] = {"n_sets": int(n_sets)}
    design["counterbalance"] = {"lists": st.number_input("Counterbalancing lists", 1, 16, 1)}

elif paradigm == "lexical_decision":
    design["paradigm"] = "lexical_decision"
    design["items"] = {"source": "generate"}  # lexicon comes from the top-level field
    design["n_per_condition"] = st.number_input("Items per condition (words = pseudowords)", 4, 200, 60, step=2)
    gen_method = st.selectbox(
        "Pseudoword generation method", GENERATION_METHODS,
        help="letter_substitution changes the fewest single letters, keeping every "
             "bigram attested; subsyllabic swaps whole onset/nucleus/coda constituents "
             "(Wuggy-style; Keuleers & Brysbaert, 2010). Both are deterministic, so "
             "the two engines generate identical pseudowords.",
    )
    if gen_method != GENERATION_METHODS[0]:
        design["items"]["generation"] = {"method": gen_method}
    design["counterbalance"] = {"lists": 1}
    st.caption("Real words in the frequency/length band are paired with deterministically "
               "generated, orthographically legal pseudowords matched on length.")

elif paradigm in ("priming", "self_paced_reading"):
    design["paradigm"] = paradigm
    st.subheader("Item table")
    default_item = ("priming_pairs_en.csv" if paradigm == "priming" else "spr_sentences_en.csv")
    example = os.path.join(ITEMS_DIR, default_item)
    use_example = False
    if os.path.exists(example):
        use_example = st.checkbox(f"Use the bundled example ({default_item})", value=True)
    if use_example and os.path.exists(example):
        items_abs = example
        design["items"] = {"source": "table", "path": f"items/{default_item}"}
        st.dataframe(pd.read_csv(example).head(8), width="stretch")
    else:
        req = "item, condition, prime, target" if paradigm == "priming" else "item, condition, sentence (regions split by |), critical_region"
        up = st.file_uploader(f"Item table CSV ({req})", type=["csv"])
        if up is not None:
            items_abs = received_upload(up)
            design["items"] = {"source": "table", "path": f"items/{up.name}"}
            uploaded_inputs[design["items"]["path"]] = items_abs
            st.dataframe(pd.read_csv(items_abs).head(8), width="stretch")
    design["counterbalance"] = {"lists": st.number_input("Counterbalancing lists", 1, 16, 2)}

if font and font != "Courier New":
    design["font"] = font

design_filename = f"{name}.yaml"

# A factorial design with nothing under 'Match on' cannot run: every distance would be
# zero and the tie-break alone would choose the words, so the engines refuse it.
# The message sits under 'Match on'.
run_blocked = paradigm == "factorial" and not design.get("match_on")
run = st.button("▶  Run design", type="primary", width="stretch", disabled=run_blocked)

if run:
    ready = True
    if paradigm in ("factorial", "lexical_decision") and not lexicon_abs:
        st.error("Choose a lexicon (or upload one) first.")
        ready = False
    if paradigm == "factorial" and len(design.get("conditions", [])) < 2:
        st.error("Define at least two conditions.")
        ready = False
    if paradigm in ("priming", "self_paced_reading") and not items_abs:
        st.error("Choose or upload an item table first.")
        ready = False
    if ready:
        try:
            with st.spinner("Running the lexsync pipeline…"):
                bundle = run_design(design, design_filename,
                                    staged_inputs(design, lexicon_abs, items_abs))
            # The tabs now show this run, so the previous run's directory can go.
            discard_run_dir((st.session_state.get("bundle") or {}).get("root"))
            st.session_state["bundle"] = bundle
            st.session_state["design"] = design
            st.session_state["design_filename"] = design_filename
            st.session_state["uploaded_inputs"] = uploaded_inputs
            st.success(f"Selected {len(bundle['stimuli'])} rows.")
        except Exception as exc:  # surface pipeline errors to the user
            discard_run_dir((st.session_state.pop("bundle", None) or {}).get("root"))
            st.error(f"The pipeline raised an error: {exc}")

if "bundle" in st.session_state:
    bundle = st.session_state["bundle"]
    design = st.session_state["design"]
    design_filename = st.session_state["design_filename"]
    extra_files = {rel: full for rel, full in st.session_state.get("uploaded_inputs", {}).items()
                   if os.path.exists(full)}
    tabs = st.tabs(["Stimuli", "Realised control", "Datasheet", "Experiment scripts",
                    "Reproducible code", "Download"])

    with tabs[0]:
        st.dataframe(bundle["stimuli"], width="stretch", height=460)

    with tabs[1]:
        comp = bundle["comparisons"]
        if comp is None:
            st.info("This paradigm draws from an item table, so no corpus-matching "
                    "control report is produced.")
        else:
            show = comp.copy()
            # The interval goes with the TOST at the schema's alpha, so its heading
            # comes from the run's datasheet.
            ci = interval_label(bundle.get("record"))
            if {"d_ci_low", "d_ci_high"}.issubset(show.columns):
                show[ci] = show.apply(lambda r: f"[{r['d_ci_low']:.2f}, {r['d_ci_high']:.2f}]", axis=1)
            cols = [c for c in ["condition", "reference", "dimension", "role", "mean_diff",
                                "cohens_d", ci, "var_ratio", "tost_p", "equivalent"]
                    if c in show.columns]
            st.markdown("**Realised control for every pair of conditions and every dimension** "
                        f"(its role, the raw difference, Cohen's *d* with its {ci}, and the "
                        "TOST verdict).")
            st.dataframe(show[cols], width="stretch")
            try:
                # One bar per dimension and pair: a design with more than two conditions
                # compares every pair, and bars sharing a dimension's label would merge.
                chart = pd.DataFrame({
                    "comparison": [f"{d} ({c} vs {r})" for d, c, r in
                                   zip(comp["dimension"], comp["condition"], comp["reference"],
                                       strict=True)],
                    "abs_d": comp["cohens_d"].abs()})
                st.bar_chart(chart, x="comparison", y="abs_d", height=240)
                st.caption("Absolute standardised mean difference by dimension and pair. "
                           "Manipulated dimensions stand high; matched dimensions sit near "
                           "zero, and uncontrolled ones may sit anywhere.")
            except Exception:
                pass
        if bundle["descriptives"] is not None:
            st.markdown("**Per-condition descriptive statistics**")
            st.dataframe(bundle["descriptives"], width="stretch")

    with tabs[2]:
        if bundle["datasheet_md"]:
            st.markdown(bundle["datasheet_md"])
        else:
            st.info("No datasheet was produced for this design.")

    with tabs[3]:
        st.caption(EXPERIMENT_NOTE)
        files = [p for p in experiment_files(bundle["paths"].get("experiments", {}))
                 if p and os.path.exists(p)]
        for group in experiment_downloads(files, bundle["base"]):
            zipped = group["file_name"].endswith(".zip")
            st.download_button(f"Download {group['file_name']}", experiment_payload(group),
                               file_name=group["file_name"],
                               mime="application/zip" if zipped else "text/html",
                               key=f"dl_exp_{group['target']}")

    with tabs[4]:
        code = reproduction_code(design, design_filename)
        st.markdown(f"**Design configuration** — save as `{design_filename}`")
        st.code(code["yaml"], language="yaml")
        st.markdown("**Reproduce in Python**")
        st.code(code["python"], language="python")
        st.markdown("**Reproduce in R**")
        st.code(code["r"], language="r")
        st.markdown("**Reproduce from the command line**")
        st.code(code["cli"], language="bash")
        st.caption(parity_claim(bundle.get("record")))
        if extra_files:
            st.warning(
                "This design names " + ", ".join(f"`{p}`" for p in extra_files) +
                ", which you uploaded and the repository does not hold. The Download "
                "tab's bundle carries the file at that path, so run the code above from "
                "the unzipped bundle."
            )

    with tabs[5]:
        st.download_button(
            "Download everything (design + stimuli + report + datasheet + scripts)",
            make_zip(bundle), file_name=f"{design['name']}_lexsync.zip",
            mime="application/zip", type="primary",
        )
        st.caption(DOWNLOAD_NOTE)
else:
    st.info("Configure a design in the sidebar and panels above, then press **Run design**.")
