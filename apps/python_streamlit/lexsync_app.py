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

import io
import os
import tempfile
import zipfile

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
    "Self-paced reading (item table)": "self_paced_reading",
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


def run_design(design: dict, lexicon_abs: str | None, items_abs: str | None) -> dict:
    """Write the design to a temp file, run the pipeline, and collect the outputs.

    The design shown to the user keeps clean relative paths; the copy that is
    actually executed is resolved to absolute paths so it runs from any directory.
    """
    run_design_dict = {k: v for k, v in design.items()}
    if lexicon_abs:
        run_design_dict["lexicon"] = lexicon_abs
    if items_abs:
        items = dict(run_design_dict.get("items") or {})
        items["path"] = items_abs
        run_design_dict["items"] = items

    tmp = tempfile.mkdtemp(prefix="lexsync_app_")
    design_path = _write_design_yaml(run_design_dict, os.path.join(tmp, "design.yaml"))
    out = os.path.join(tmp, "output")
    result = run_pipeline(design_path, schema_path=SCHEMA_PATH, outdir=out, verbose=False)

    bundle = {"paths": result, "outdir": out}
    bundle["stimuli"] = pd.read_csv(result["stimuli"])
    bundle["descriptives"] = (pd.read_csv(result["descriptives"])
                              if result.get("descriptives") and os.path.exists(result["descriptives"]) else None)
    bundle["comparisons"] = (pd.read_csv(result["comparisons"])
                             if result.get("comparisons") and os.path.exists(result["comparisons"]) else None)
    base = os.path.splitext(os.path.basename(result["stimuli"]))[0].replace("_stimuli_py", "")
    ds_md = os.path.join(out, "reports", f"{base}_datasheet_py.md")
    bundle["datasheet_md"] = open(ds_md, encoding="utf-8").read() if os.path.exists(ds_md) else None
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
    "**Reproducible psycholinguistic stimulus design — Python engine.** "
    "Assemble a design below, run the verified lexsync pipeline, and export the "
    "design file together with the R, Python and command-line code that reproduces "
    "it. The two engines select byte-identical stimuli, so the exported code runs "
    "the same operation in either ecosystem."
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
    seed_note = st.empty()
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
            tmpdir = tempfile.mkdtemp(prefix="lexsync_lex_")
            lexicon_abs = os.path.join(tmpdir, up.name)
            with open(lexicon_abs, "wb") as fh:
                fh.write(up.getbuffer())
            design["lexicon"] = f"corpora/{up.name}"
            uploaded_inputs[design["lexicon"]] = lexicon_abs
    else:
        lexicon_abs = corpora[corpus_choice]
        design["lexicon"] = f"corpora/derived/{corpus_choice}.csv"
        with col2:
            st.dataframe(corpus_preview(lexicon_abs), use_container_width=True, height=150)

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
    preset = st.selectbox(
        "Start from a preset",
        ["High vs low frequency", "Dense vs sparse neighbourhood",
         "2x2 frequency x neighbourhood", "Custom"],
    )

    def _row(name, dim, lo, hi, cats="", dim2="", lo2=None, hi2=None):
        return {"name": name, "dimension": dim, "lower": lo, "upper": hi, "categories": cats,
                "dimension2": dim2, "lower2": lo2, "upper2": hi2}

    if preset == "High vs low frequency":
        cond_default = pd.DataFrame([
            _row("high_frequency", "frequency", 5.2, 7.0),
            _row("low_frequency", "frequency", 3.8, 4.4),
        ])
        match_default, method_default = ["length", "n_density", "old20"], "standardised_euclidean"
    elif preset == "Dense vs sparse neighbourhood":
        cond_default = pd.DataFrame([
            _row("dense_neighbourhood", "n_density", 5.0, 100.0),
            _row("sparse_neighbourhood", "n_density", 0.0, 1.0),
        ])
        match_default, method_default = ["length", "frequency"], "joint"
    elif preset == "2x2 frequency x neighbourhood":
        cond_default = pd.DataFrame([
            _row("HF_largeN", "frequency", 5.0, 7.0, "", "n_density", 9.0, 100.0),
            _row("HF_smallN", "frequency", 5.0, 7.0, "", "n_density", 0.0, 5.0),
            _row("LF_largeN", "frequency", 2.5, 4.2, "", "n_density", 9.0, 100.0),
            _row("LF_smallN", "frequency", 2.5, 4.2, "", "n_density", 0.0, 5.0),
        ])
        match_default, method_default = ["length"], "standardised_euclidean"
    else:
        cond_default = pd.DataFrame([
            _row("condition_a", "frequency", 5.0, 7.0),
            _row("condition_b", "frequency", 3.5, 4.5),
        ])
        match_default, method_default = ["length"], "standardised_euclidean"

    cond_df = st.data_editor(
        cond_default, num_rows="dynamic", use_container_width=True, key=f"cond_editor_{preset}",
        column_config={
            "dimension": st.column_config.SelectboxColumn("dimension", options=DIMENSIONS),
            "dimension2": st.column_config.SelectboxColumn("dimension2", options=[""] + DIMENSIONS),
        },
    )

    def _isnum(x):
        try:
            return x is not None and x == x and str(x) != ""  # not None, not NaN, not ""
        except Exception:
            return False

    conditions = []
    for _, row in cond_df.iterrows():
        nm = str(row.get("name") or "").strip()
        dim = str(row.get("dimension") or "").strip()
        if not nm or not dim:
            continue
        cats = str(row.get("categories") or "").strip()
        define_by = {}
        if cats:
            define_by[dim] = [c.strip() for c in cats.split(",") if c.strip()]
        elif _isnum(row.get("lower")) and _isnum(row.get("upper")):
            define_by[dim] = [float(row["lower"]), float(row["upper"])]
        dim2 = str(row.get("dimension2") or "").strip()
        if dim2 and _isnum(row.get("lower2")) and _isnum(row.get("upper2")):
            define_by[dim2] = [float(row["lower2"]), float(row["upper2"])]
        if define_by:
            conditions.append({"name": nm, "define_by": define_by})
    design["conditions"] = conditions

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
        st.dataframe(pd.read_csv(example).head(8), use_container_width=True)
    else:
        req = "item, condition, prime, target" if paradigm == "priming" else "item, condition, sentence (regions split by |), critical_region"
        up = st.file_uploader(f"Item table CSV ({req})", type=["csv"])
        if up is not None:
            tmpdir = tempfile.mkdtemp(prefix="lexsync_items_")
            items_abs = os.path.join(tmpdir, up.name)
            with open(items_abs, "wb") as fh:
                fh.write(up.getbuffer())
            design["items"] = {"source": "table", "path": f"items/{up.name}"}
            uploaded_inputs[design["items"]["path"]] = items_abs
            st.dataframe(pd.read_csv(items_abs).head(8), use_container_width=True)
    design["counterbalance"] = {"lists": st.number_input("Counterbalancing lists", 1, 16, 2)}

font = st.sidebar.text_input("Stimulus font", value="Courier New")
if font and font != "Courier New":
    design["font"] = font

design_filename = f"{name}.yaml"

run = st.button("▶  Run design", type="primary", use_container_width=True)

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
                bundle = run_design(design, lexicon_abs, items_abs)
            st.session_state["bundle"] = bundle
            st.session_state["design"] = design
            st.session_state["design_filename"] = design_filename
            st.session_state["uploaded_inputs"] = uploaded_inputs
            st.success(f"Done — {len(bundle['stimuli'])} rows selected.")
        except Exception as exc:  # surface pipeline errors to the user
            st.session_state.pop("bundle", None)
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
        st.dataframe(bundle["stimuli"], use_container_width=True, height=460)

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
            st.dataframe(show[cols], use_container_width=True)
            try:
                chart = comp.assign(abs_d=comp["cohens_d"].abs())[["dimension", "abs_d"]]
                st.bar_chart(chart, x="dimension", y="abs_d", height=240)
                st.caption("Absolute standardised mean difference by dimension. Manipulated "
                           "dimensions stand high; matched dimensions sit near zero.")
            except Exception:
                pass
        if bundle["descriptives"] is not None:
            st.markdown("**Per-condition descriptive statistics**")
            st.dataframe(bundle["descriptives"], use_container_width=True)

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
        st.caption("The R and Python engines produce byte-identical stimuli and "
                   "trial order from this configuration.")
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
