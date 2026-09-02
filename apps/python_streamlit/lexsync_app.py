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
import os
import shutil
import tempfile
import threading
import zipfile

import altair as alt
import pandas as pd
import streamlit as st
import yaml

import lexsync
from lexsync import run_pipeline

PKG_DIR = os.path.dirname(lexsync.__file__)
SCHEMA_PATH = os.path.join(PKG_DIR, "data", "schema.yaml")

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
    "Categorisation (item table)": "categorisation",
    "Self-paced reading (item table)": "self_paced_reading",
}
# Each preset's matched dimensions and matching method. A preset that manipulates
# a dimension must not also ask the engine to match on it, so the neighbourhood
# contrast is matched on length and frequency rather than on the general default.
# The Shiny app's PRESET_MATCHING holds the same table (tests/test_apps.py).
PRESET_MATCHING = {
    "High vs low frequency": (["length", "n_density", "old20"], "standardised_euclidean"),
    "Dense vs sparse neighbourhood": (["length", "frequency"], "joint"),
    "2x2 frequency x neighbourhood": (["length"], "standardised_euclidean"),
    "Custom": (["length"], "standardised_euclidean"),
}
# The paradigms that take their trials from an item table rather than from the
# corpus, each with the bundled example table and the columns such a table must
# carry. Keeping the set in one place is what stops the chooser and the design
# builder from disagreeing about which paradigms need a table.
ITEM_TABLE_PARADIGMS = {
    "priming": ("priming_pairs_en.csv", "item, condition, prime, target"),
    "categorisation": ("categorisation_en.csv",
                       "item, condition, target, category, answer (the correct key)"),
    "self_paced_reading": ("spr_sentences_en.csv",
                           "item, condition, sentence (regions split by |), critical_region"),
}


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
    """Write an uploaded file once per upload rather than once per rerun.

    The script re-executes top to bottom on every widget interaction and the
    uploader keeps handing back the file it holds, so writing it here directly
    copied a lexicon of about a megabyte for every keystroke, tab and slider move.
    The cache is keyed on the content digest, and ``_data`` is left out of the key
    by its leading underscore, so the same upload resolves to the same path.

    Parameters
    ----------
    name : str
        The uploaded file's own name, which the written file keeps.
    digest : str
        Hex digest of ``_data``; the cache key.
    _data : bytes
        The uploaded bytes.

    Returns
    -------
    str
        Absolute path of the written file.
    """
    path = os.path.join(tempfile.mkdtemp(prefix="lexsync_upload_"), name)
    with open(path, "wb") as fh:
        fh.write(_data)
    return path


def discard_run_dir(path: str | None) -> None:
    """Remove a previous run's temporary tree.

    Every run writes its design, its staged inputs and a whole output tree under a
    fresh temporary directory, and nothing reclaimed them, so a long-lived process
    kept one complete set of artefacts per press of Run. Only the run whose results
    are on screen is still read from.
    """
    if path and os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)


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
    cli = (
        "# Command line\n"
        f"lexsync run {cfg}                              # Python console script\n"
        f"python -m lexsync run {cfg}                    # Python (module form)\n"
        f"Rscript -e 'lexsync::run_pipeline(\"{cfg}\")'    # R"
    )
    return {"yaml": yaml_block(design), "python": py, "r": r, "cli": cli}


def parity_claim(design: dict) -> str:
    """The sentence under the exported code, conditioned on the matching method.

    ``mahalanobis`` and ``optimal`` use a covariance inverse and an assignment
    solver, whose last bits differ between the two linear-algebra backends, so the
    unqualified claim contradicted the method chooser's own help text and the
    'Cross-engine determinism' line of the datasheet one tab away. The Shiny app
    words both cases the same way.
    """
    if ((design.get("matching") or {}).get("method")) in ("mahalanobis", "optimal"):
        return ("This design's matching method uses a covariance inverse or an "
                "assignment solver, so the R and Python engines select equivalent "
                "but not byte-identical stimuli. The datasheet's 'Cross-engine "
                "determinism' line records which case applies.")
    return ("The R and Python engines produce byte-identical stimuli and "
            "trial order from this configuration.")


def _write_design_yaml(design: dict, path: str) -> str:
    """Write the design YAML with LF line endings on every platform.

    Without newline="\\n" the text-mode default writes CRLF on Windows, and the
    pipeline hashes this file into the datasheet's design_sha256, so its bytes
    must depend on the content alone, never on the operating system. The Shiny
    app's write_yaml_lf pins the same convention.
    """
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        yaml.safe_dump(design, fh, sort_keys=False, allow_unicode=True)
    return path


def staged_inputs(design: dict, lexicon_abs: str | None, items_abs: str | None) -> dict:
    """Map each input the design names to the file the run should read it from.

    Parameters
    ----------
    design : dict
        The design as shown to the user, carrying repository-relative paths.
    lexicon_abs : str, optional
        Absolute path of the chosen or uploaded lexicon.
    items_abs : str, optional
        Absolute path of the chosen or uploaded item table.

    Returns
    -------
    dict
        Design-relative path -> absolute path of the file to place there. A design
        that already names an absolute path needs no staging and is omitted.
    """
    out = {}
    lexicon = design.get("lexicon")
    if lexicon_abs and isinstance(lexicon, str) and not os.path.isabs(lexicon):
        out[lexicon] = lexicon_abs
    items = design.get("items")
    items_path = items.get("path") if isinstance(items, dict) else None
    if items_abs and isinstance(items_path, str) and not os.path.isabs(items_path):
        out[items_path] = items_abs
    return out


# The working directory is process-global, and Streamlit runs each browser
# session's script in a thread of one process, so two runs that overlap would
# resolve each other's relative design and lexicon paths. Only one run holds the
# directory at a time.
_RUN_LOCK = threading.Lock()


def run_design(design: dict, lexicon_abs: str | None, items_abs: str | None) -> dict:
    """Stage the design's inputs, run the pipeline over them, and collect the outputs.

    The run uses the design exactly as it is shown, exported and archived, because
    the pipeline hashes the design file it ran into the datasheet's design_sha256
    and records the lexicon path it was given as the materials source. Rewriting
    those paths to absolute ones would give the recipient of a bundle a datasheet
    whose checksum names no file in it and a materials line naming a directory on
    the machine that ran the app. So each input is placed at the path the design
    records, inside a temporary directory the pipeline runs from.
    """
    tmp = tempfile.mkdtemp(prefix="lexsync_app_")
    design_path = _write_design_yaml(design, os.path.join(tmp, "design.yaml"))
    for rel, full in staged_inputs(design, lexicon_abs, items_abs).items():
        dest = os.path.join(tmp, *rel.split("/"))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(full, dest)
    out = os.path.join(tmp, "output")
    # The design's paths are relative, so the pipeline has to read them from the
    # staging directory. outdir and the schema are absolute, so nothing else in the
    # call depends on where the process happens to stand.
    with _RUN_LOCK:
        cwd = os.getcwd()
        try:
            os.chdir(tmp)
            result = run_pipeline(os.path.basename(design_path), schema_path=SCHEMA_PATH,
                                  outdir=out, verbose=False)
        finally:
            os.chdir(cwd)

    bundle = {"paths": result, "outdir": out, "rundir": tmp}
    bundle["stimuli"] = pd.read_csv(result["stimuli"])
    bundle["descriptives"] = (
        pd.read_csv(result["descriptives"])
        if result.get("descriptives") and os.path.exists(result["descriptives"]) else None)
    bundle["comparisons"] = (pd.read_csv(result["comparisons"])
                             if result.get("comparisons") and os.path.exists(result["comparisons"]) else None)
    base = os.path.splitext(os.path.basename(result["stimuli"]))[0].replace("_stimuli_py", "")
    ds_md = os.path.join(out, "reports", f"{base}_datasheet_py.md")
    bundle["datasheet_md"] = None
    if os.path.exists(ds_md):
        # A `with` block, not open(...).read(): the app is long-lived and reruns this
        # on every widget interaction, so a handle left to the garbage collector is a
        # descriptor leak rather than a style point.
        with open(ds_md, encoding="utf-8") as handle:
            bundle["datasheet_md"] = handle.read()
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


def _bound(x):
    """One end of a condition's window as a number, or None when the cell holds none.

    The editor's columns are typed, but a cell it classifies as empty passes the
    client's value through unconverted, so a bound can reach here as text. This
    runs while the page is being drawn, above the handler that reports a pipeline
    error, so a bare float() would take the whole page down, results already on
    screen included, rather than drop the factor the cell belongs to.
    """
    try:
        if x is None or x != x or str(x).strip() == "":  # None, NaN or blank
            return None
        return float(x)
    except (TypeError, ValueError):
        return None


def conditions_from_table(cond_df: pd.DataFrame) -> list:
    """Read the conditions editor's rows into the design's ``conditions`` list.

    A row contributes a condition when it names one and defines at least one
    window, either a category list or a pair of numeric bounds. The optional
    second factor is added only when both of its bounds are numbers.

    Parameters
    ----------
    cond_df : pandas.DataFrame
        The edited conditions table.

    Returns
    -------
    list
        One ``{"name": ..., "define_by": {...}}`` mapping per usable row.
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


def control_chart(comp: pd.DataFrame) -> pd.DataFrame:
    """The realised-control bar chart's data, one row per comparison.

    ``comparisons`` carries one row per non-anchor condition per dimension, so a
    2x2 design contributes three comparisons to every dimension. The chart used
    dimension alone as its x channel and drew those three at one position, where
    they differ by as much as five standard deviations, so the condition travels
    with each value here and separates the bars. The Shiny app groups the same rows.

    Parameters
    ----------
    comp : pandas.DataFrame
        The comparisons table from the run.

    Returns
    -------
    pandas.DataFrame
        Columns dimension, condition and abs_d, one row per input row.
    """
    return pd.DataFrame({"dimension": comp["dimension"], "condition": comp["condition"],
                         "abs_d": comp["cohens_d"].abs()})


def control_plot(chart: pd.DataFrame) -> alt.LayerChart:
    """The realised-control chart: one bar per comparison, with the 0.5-SD line.

    The bars are offset by condition, which is what keeps a 2x2 design's three
    comparisons on a dimension apart. ``st.bar_chart`` draws no reference line, so
    this chart left unmarked the half a standard deviation that the Shiny chart
    marks and that the caption of both apps names. Altair ships with Streamlit.

    Parameters
    ----------
    chart : pandas.DataFrame
        A :func:`control_chart` frame.

    Returns
    -------
    altair.LayerChart
        The bars and the reference line.
    """
    bars = alt.Chart(chart).mark_bar().encode(
        x=alt.X("dimension:N", title=None),
        xOffset=alt.XOffset("condition:N"),
        y=alt.Y("abs_d:Q", title="|Cohen's d|"),
        color=alt.Color("condition:N", title="condition"),
    )
    rule = alt.Chart(pd.DataFrame({"abs_d": [0.5]})).mark_rule(
        strokeDash=[4, 4], color="grey").encode(y=alt.Y("abs_d:Q"))
    return (bars + rule).properties(height=240)


def control_caption(comp: pd.DataFrame) -> str:
    """The sentence under that chart, naming the anchor the bars are measured against.

    Every comparison is against one anchor condition, which the chart itself does
    not show. The Shiny app words this the same way.
    """
    ref = comp["reference"].iloc[0] if "reference" in comp.columns and len(comp) else None
    anchor = f" {ref}" if ref else ""
    return ("Absolute standardised mean difference by dimension, one bar per "
            "condition against the anchor" + anchor + ". Manipulated dimensions "
            "stand high; matched dimensions sit near zero (below the 0.5-SD line).")


def bundled_inputs(design: dict) -> dict:
    """Map each repository-bundled input the design names to its source file.

    A design built from a bundled corpus or example item table records the
    repository-relative path (``corpora/derived/<x>.csv``, ``items/<x>.csv``).
    Outside the repository that path resolves to nothing, so the export carries
    the file at exactly the path the design records. Uploaded inputs are handled
    separately, through ``extra_files``.

    Parameters
    ----------
    design : dict
        The design as shown to the user, carrying repository-relative paths.

    Returns
    -------
    dict
        Design-relative path -> absolute path under the repository root.
    """
    out = {}
    lexicon = design.get("lexicon")
    if isinstance(lexicon, str) and lexicon.startswith("corpora/derived/"):
        full = os.path.join(REPO_ROOT, *lexicon.split("/"))
        if os.path.exists(full):
            out[lexicon] = full
    items = design.get("items")
    items_path = items.get("path") if isinstance(items, dict) else None
    if isinstance(items_path, str) and items_path.startswith("items/"):
        full = os.path.join(REPO_ROOT, *items_path.split("/"))
        if os.path.exists(full):
            out[items_path] = full
    return out


def make_zip(design: dict, design_filename: str, bundle: dict,
             extra_files: dict | None = None) -> bytes:
    """Archive the design, the schema, every generated artefact, and the inputs.

    Parameters
    ----------
    design : dict
        The design as shown to the user, carrying repository-relative paths.
        Any repository-bundled input it names (a corpora/derived lexicon, an
        items/ example table) is stored at that relative path, so the exported
        reproduction code runs from the unzipped directory alone.
    design_filename : str
        Name the design YAML takes inside the archive.
    bundle : dict
        A :func:`run_design` result; its ``outdir`` is walked for artefacts.
    extra_files : dict, optional
        Maps a design-relative path (``corpora/mine.csv``) to the absolute path of
        the file to store there. An uploaded lexicon or item table lives only in a
        temporary directory, so without this the design would name a path that the
        bundle does not supply and the export would not reproduce the run.

    Returns
    -------
    bytes
        The zip archive.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(design_filename, yaml_block(design))
        # The exported reproduction code passes schema_path="config/schema.yaml",
        # so the archive carries the schema the run actually used (the installed
        # package copy) at that path.
        z.write(SCHEMA_PATH, "config/schema.yaml")
        inputs = dict(extra_files or {})
        # An upload wins over a same-named repository file: it is the copy the run used.
        for rel, full in bundled_inputs(design).items():
            inputs.setdefault(rel, full)
        for rel, full in inputs.items():
            z.write(full, rel)
        out = bundle["outdir"]
        for root, _dirs, files in os.walk(out):
            for f in files:
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, out))
    return buf.getvalue()


# --------------------------------------------------------------------------- UI

st.set_page_config(page_title="lexsync", layout="wide", page_icon="🔤")
st.title("lexsync")
st.markdown(
    "Reproducible psycholinguistic stimulus design, running on the Python engine. "
    "Assemble a design below, run the verified lexsync pipeline, and export the "
    "design file together with the R, Python and command-line code that reproduces "
    "it. The two engines select byte-identical stimuli under the deterministic "
    "matching methods, so the exported code runs the same operation in either "
    "ecosystem."
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
    # Created here, with the other three sidebar fields: Streamlit places a widget
    # where the call is made, so a st.sidebar call further down the script would
    # put this field below the rule and the version line that close the sidebar.
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
            help="A word-frequency lexicon with at least `word` and `freq_zipf` columns.",
        )
    if corpus_choice == "Upload a CSV…":
        up = st.file_uploader("Lexicon CSV (word, freq_zipf, …)", type=["csv"])
        if up is not None:
            data = up.getvalue()
            lexicon_abs = staged_upload(up.name, hashlib.sha256(data).hexdigest(), data)
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
    design["pool_filters"] = {"length": list(length), "frequency": list(frequency)}

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

    # lo2/hi2 default to NaN, not None, so a preset that leaves the second factor
    # empty still hands the editor a numeric column, as the Shiny table does.
    def _row(name, dim, lo, hi, cats="", dim2="", lo2=float("nan"), hi2=float("nan")):
        return {"name": name, "dimension": dim, "lower": lo, "upper": hi, "categories": cats,
                "dimension2": dim2, "lower2": lo2, "upper2": hi2}

    if preset == "High vs low frequency":
        cond_default = pd.DataFrame([
            _row("high_frequency", "frequency", 5.2, 7.0),
            _row("low_frequency", "frequency", 3.8, 4.4),
        ])
    elif preset == "Dense vs sparse neighbourhood":
        cond_default = pd.DataFrame([
            _row("dense_neighbourhood", "n_density", 5.0, 100.0),
            _row("sparse_neighbourhood", "n_density", 0.0, 1.0),
        ])
    elif preset == "2x2 frequency x neighbourhood":
        cond_default = pd.DataFrame([
            _row("HF_largeN", "frequency", 5.0, 7.0, "", "n_density", 9.0, 100.0),
            _row("HF_smallN", "frequency", 5.0, 7.0, "", "n_density", 0.0, 5.0),
            _row("LF_largeN", "frequency", 2.5, 4.2, "", "n_density", 9.0, 100.0),
            _row("LF_smallN", "frequency", 2.5, 4.2, "", "n_density", 0.0, 5.0),
        ])
    else:
        cond_default = pd.DataFrame([
            _row("condition_a", "frequency", 5.0, 7.0),
            _row("condition_b", "frequency", 3.5, 4.5),
        ])
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
    c1, c2 = st.columns(2)
    with c1:
        methods = ["standardised_euclidean", "joint", "mahalanobis", "optimal"]
        method = st.radio(
            "Matching method", methods,
            index=methods.index(method_default) if method_default in methods else 0,
            help="joint/optimal pair two conditions (optimal is globally best); "
                 "mahalanobis down-weights correlated dimensions. mahalanobis and "
                 "optimal use a covariance inverse / assignment solver, so the R and "
                 "Python engines agree closely but not byte-for-byte on them.",
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
    design["n_per_condition"] = st.number_input(
        "Items per condition (words = pseudowords)", 4, 200, 60, step=2)
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

elif paradigm in ITEM_TABLE_PARADIGMS:
    design["paradigm"] = paradigm
    st.subheader("Item table")
    default_item, req = ITEM_TABLE_PARADIGMS[paradigm]
    example = os.path.join(ITEMS_DIR, default_item)
    use_example = False
    if os.path.exists(example):
        use_example = st.checkbox(f"Use the bundled example ({default_item})", value=True)
    if use_example and os.path.exists(example):
        items_abs = example
        design["items"] = {"source": "table", "path": f"items/{default_item}"}
        st.dataframe(pd.read_csv(example).head(8), width="stretch")
    else:
        up = st.file_uploader(f"Item table CSV ({req})", type=["csv"])
        if up is not None:
            data = up.getvalue()
            items_abs = staged_upload(up.name, hashlib.sha256(data).hexdigest(), data)
            design["items"] = {"source": "table", "path": f"items/{up.name}"}
            uploaded_inputs[design["items"]["path"]] = items_abs
            st.dataframe(pd.read_csv(items_abs).head(8), width="stretch")
    design["counterbalance"] = {"lists": st.number_input("Counterbalancing lists", 1, 16, 2)}

if font and font != "Courier New":
    design["font"] = font

design_filename = f"{name}.yaml"

run = st.button("▶  Run design", type="primary", width="stretch")

if run:
    ready = True
    if paradigm in ("factorial", "lexical_decision") and not lexicon_abs:
        st.error("Choose a lexicon (or upload one) first.")
        ready = False
    if paradigm == "factorial" and len(design.get("conditions", [])) < 2:
        st.error("Define at least two conditions.")
        ready = False
    if paradigm == "factorial" and not design.get("match_on"):
        st.error("Choose at least one dimension to match on.")
        ready = False
    if paradigm in ITEM_TABLE_PARADIGMS and not items_abs:
        st.error("Choose or upload an item table first.")
        ready = False
    if ready:
        try:
            with st.spinner("Running the lexsync pipeline…"):
                bundle = run_design(design, lexicon_abs, items_abs)
            # One run's tree at a time: the results on screen are read from the
            # newest, and the process may serve many runs before it ends.
            discard_run_dir(st.session_state.get("run_dir"))
            st.session_state["run_dir"] = bundle["rundir"]
            st.session_state["bundle"] = bundle
            st.session_state["design"] = design
            st.session_state["design_filename"] = design_filename
            st.session_state["uploaded_inputs"] = uploaded_inputs
            st.success(f"Selected {len(bundle['stimuli'])} rows.")
        except Exception as exc:  # surface pipeline errors to the user
            st.session_state.pop("bundle", None)
            discard_run_dir(st.session_state.pop("run_dir", None))
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
            if {"d_ci_low", "d_ci_high"}.issubset(show.columns):
                show["90% CI"] = show.apply(lambda r: f"[{r['d_ci_low']:.2f}, {r['d_ci_high']:.2f}]", axis=1)
            cols = [c for c in ["condition", "reference", "dimension", "cohens_d", "90% CI",
                                "var_ratio", "tost_p", "equivalent"] if c in show.columns]
            st.markdown("**Effect size and equivalence per controlled dimension** "
                        "(Cohen's *d* against the anchor, 90% CI, and the TOST verdict).")
            st.dataframe(show[cols], width="stretch")
            try:
                st.altair_chart(control_plot(control_chart(comp)), width="stretch")
                st.caption(control_caption(comp))
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
        st.caption("The same matched stimuli compile to three presentation targets.")
        exps = bundle["paths"].get("experiments", {})
        for label, path in exps.items():
            if path and os.path.exists(path):
                with open(path, "rb") as fh:
                    st.download_button(f"Download {os.path.basename(path)}", fh.read(),
                                       file_name=os.path.basename(path), key=f"dl_{label}_{path}")

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
        st.caption(parity_claim(design))
        if extra_files:
            st.warning(
                "This design names " + ", ".join(f"`{p}`" for p in extra_files) +
                ", which you uploaded and the repository does not hold. The Download "
                "tab's bundle carries the file at that path: extract the bundle at the "
                "repository root before running the code above."
            )

    with tabs[5]:
        zip_bytes = make_zip(design, design_filename, bundle, extra_files)
        st.download_button(
            "Download everything (design + stimuli + report + datasheet + scripts)",
            zip_bytes, file_name=f"{design['name']}_lexsync.zip", mime="application/zip",
            type="primary",
        )
        st.caption("A self-contained bundle: the design YAML, the schema, every generated "
                   "artefact, and the lexicon or item table the design names, at the path "
                   "the design records.")
else:
    st.info("Configure a design in the sidebar and panels above, then press **Run design**.")
