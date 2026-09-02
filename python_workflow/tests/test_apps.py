"""Tests for the Streamlit front-end in apps/python_streamlit.

The app module is a Streamlit script, so importing it executes its UI. Streamlit
tolerates that outside a running server (widgets return their defaults), which is
enough to reach the plain helper functions the export path is built from.
"""
import importlib.util
import io
import os
import zipfile

import pytest

APP_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "apps", "python_streamlit", "lexsync_app.py",
)


@pytest.fixture(scope="module")
def app():
    pytest.importorskip("streamlit")
    spec = importlib.util.spec_from_file_location("lexsync_app_under_test", APP_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _names(payload):
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        return sorted(z.namelist())


def test_positive_tolerances_keeps_only_the_dimensions_given_a_positive_k(app):
    """A k of zero means "use the schema default", not "match to a zero-width
    window", so it must not reach the design. Pinned identically in test-apps.R."""
    assert app.positive_tolerances(
        {"length": 0, "frequency": 0.111, "n_density": 2}) == {"frequency": 0.111, "n_density": 2}
    assert app.positive_tolerances({"length": 0, "old20": 0}) == {}
    assert app.positive_tolerances({}) == {}
    assert app.positive_tolerances({"length": None, "frequency": 1}) == {"frequency": 1.0}


def test_positive_tolerances_preserves_the_order_the_dimensions_are_matched_on(app):
    assert list(app.positive_tolerances(
        {"old20": 2, "length": 1, "frequency": 0.5})) == ["old20", "length", "frequency"]


def test_make_zip_holds_the_design_and_every_artefact(app, tmp_path):
    out = tmp_path / "output"
    (out / "reports").mkdir(parents=True)
    (out / "stimuli.csv").write_text("word\ncat\n", encoding="utf-8")
    (out / "reports" / "datasheet.md").write_text("# datasheet\n", encoding="utf-8")

    payload = app.make_zip({"name": "my_design"}, "my_design.yaml", {"outdir": str(out)})

    # The artefact entries the Shiny app's write_bundle_zip also produces
    # (test-apps.R), plus the schema the run actually used: names are relative
    # to outdir and subdirectories survive.
    assert _names(payload) == ["config/schema.yaml", "my_design.yaml",
                               "reports/datasheet.md", "stimuli.csv"]


def test_make_zip_ships_an_uploaded_lexicon_at_the_path_the_design_names(app, tmp_path):
    """The design names corpora/mine.csv, a path the repository does not hold, so
    the bundle must carry the uploaded file there for the export to reproduce."""
    out = tmp_path / "output"
    out.mkdir()
    (out / "my_design_stimuli_py.csv").write_text("word\ncat\n", encoding="utf-8")
    upload = tmp_path / "upload" / "mine.csv"
    upload.parent.mkdir()
    upload.write_bytes(b"word,freq_zipf\ncat,5.0\n")

    design = {"name": "my_design", "lexicon": "corpora/mine.csv"}
    payload = app.make_zip(design, "my_design.yaml", {"outdir": str(out)},
                           {design["lexicon"]: str(upload)})

    assert "corpora/mine.csv" in _names(payload)
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        assert z.read("corpora/mine.csv") == b"word,freq_zipf\ncat,5.0\n"


def test_make_zip_ships_an_uploaded_item_table_under_its_own_root(app, tmp_path):
    """Item tables use items/, not corpora/, so the mapping must carry the design's
    own path string rather than assume a single root."""
    out = tmp_path / "output"
    out.mkdir()
    (out / "my_design_stimuli_py.csv").write_text("item\n1\n", encoding="utf-8")
    upload = tmp_path / "upload" / "pairs.csv"
    upload.parent.mkdir()
    upload.write_text("item,condition,prime,target\n1,rel,cat,dog\n", encoding="utf-8")

    design = {"name": "my_design", "items": {"source": "table", "path": "items/pairs.csv"}}
    payload = app.make_zip(design, "my_design.yaml", {"outdir": str(out)},
                           {design["items"]["path"]: str(upload)})

    assert "items/pairs.csv" in _names(payload)


def test_make_zip_without_uploads_is_unchanged(app, tmp_path):
    """A lexicon path the repository does not hold ships nothing beyond the schema."""
    out = tmp_path / "output"
    out.mkdir()
    (out / "my_design_stimuli_py.csv").write_text("word\ncat\n", encoding="utf-8")
    design = {"name": "my_design", "lexicon": "corpora/derived/en_example.csv"}

    assert (app.make_zip(design, "my_design.yaml", {"outdir": str(out)}, None)
            == app.make_zip(design, "my_design.yaml", {"outdir": str(out)}, {}))
    assert _names(app.make_zip(design, "my_design.yaml", {"outdir": str(out)})) == [
        "config/schema.yaml", "my_design.yaml", "my_design_stimuli_py.csv",
    ]


def test_make_zip_ships_a_repository_bundled_corpus(app, tmp_path):
    """A design built from a bundled corpus records corpora/derived/<x>.csv, a
    path that resolves to nothing outside the checkout, so the export must carry
    the file there for the reproduction code to run from the unzipped directory."""
    out = tmp_path / "output"
    out.mkdir()
    (out / "my_design_stimuli_py.csv").write_text("word\ncat\n", encoding="utf-8")
    design = {"name": "my_design", "lexicon": "corpora/derived/en.csv"}

    payload = app.make_zip(design, "my_design.yaml", {"outdir": str(out)})
    assert "corpora/derived/en.csv" in _names(payload)
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        with open(os.path.join(app.REPO_ROOT, "corpora", "derived", "en.csv"), "rb") as f:
            assert z.read("corpora/derived/en.csv") == f.read()


def test_the_datasheet_records_the_design_the_bundle_ships(app):
    """The run used to rewrite the design's lexicon to an absolute path, so the
    datasheet's design_sha256 identified a file that is in no bundle and the
    'Materials source' line named a directory on the machine that ran the app.
    Pinned identically in test-apps.R for the Shiny app."""
    import hashlib
    import json

    lexicon = os.path.join(app.REPO_ROOT, "corpora", "derived", "en.csv")
    if not os.path.exists(lexicon):
        pytest.skip("The bundled corpora are not in this tree.")
    design = {
        "name": "my_design", "language": "english",
        "lexicon": "corpora/derived/en.csv",
        "pool_filters": {"length": [3, 7], "frequency": [3.5, 7.0]},
        "paradigm": "factorial",
        "conditions": [
            {"name": "high_frequency", "define_by": {"frequency": [5.2, 7.0]}},
            {"name": "low_frequency", "define_by": {"frequency": [3.8, 4.4]}},
        ],
        "n_per_condition": 20, "match_on": ["length"],
        "matching": {"method": "standardised_euclidean"},
        "counterbalance": {"lists": 1},
    }
    bundle = app.run_design(design, lexicon, None)

    with zipfile.ZipFile(io.BytesIO(app.make_zip(design, "my_design.yaml", bundle))) as z:
        shipped = hashlib.sha256(z.read("my_design.yaml")).hexdigest()
    with open(os.path.join(bundle["outdir"], "reports",
                           bundle["base"] + "_datasheet_py.json"), encoding="utf-8") as handle:
        datasheet = json.load(handle)
    assert datasheet["reproducibility"]["design_sha256"] == shipped
    assert datasheet["materials_source"]["path"] == "corpora/derived/en.csv"


def test_staged_inputs_places_each_input_at_the_path_the_design_names(app):
    """The staging map is keyed by the design's own path string, so an uploaded
    lexicon under corpora/ and an item table under items/ each reach the run at
    the path the exported design records. Pinned identically in test-apps.R."""
    design = {"lexicon": "corpora/mine.csv",
              "items": {"source": "table", "path": "items/pairs.csv"}}
    assert app.staged_inputs(design, "/abs/mine.csv", "/abs/pairs.csv") == {
        "corpora/mine.csv": "/abs/mine.csv", "items/pairs.csv": "/abs/pairs.csv"}
    assert app.staged_inputs(design, None, None) == {}
    # Nothing to stage for a design that already names an absolute path.
    assert app.staged_inputs({"lexicon": "/elsewhere/mine.csv"}, "/abs/mine.csv", None) == {}


def test_a_condition_bound_that_is_not_a_number_drops_that_factor(app):
    """The conditions table is read while the page is drawn, above the handler that
    reports a pipeline error, so a bound the editor let through as text raised
    ValueError and took the whole page down, results already on screen included.
    Pinned identically in test-apps.R."""
    import pandas as pd

    nan = float("nan")
    frame = pd.DataFrame([
        {"name": "a", "dimension": "frequency", "lower": 5.0, "upper": 7.0,
         "categories": "", "dimension2": "n_density", "lower2": "9 or more", "upper2": 100.0},
        {"name": "b", "dimension": "frequency", "lower": "3.0", "upper": 4.0,
         "categories": "", "dimension2": "", "lower2": nan, "upper2": nan},
        {"name": "c", "dimension": "gender", "lower": nan, "upper": nan,
         "categories": "m, f", "dimension2": "", "lower2": nan, "upper2": nan},
        {"name": "", "dimension": "frequency", "lower": 1.0, "upper": 2.0,
         "categories": "", "dimension2": "", "lower2": nan, "upper2": nan},
    ])

    assert app.conditions_from_table(frame) == [
        {"name": "a", "define_by": {"frequency": [5.0, 7.0]}},
        {"name": "b", "define_by": {"frequency": [3.0, 4.0]}},
        {"name": "c", "define_by": {"gender": ["m", "f"]}},
    ]


def _comparisons():
    """Two comparisons against one anchor over two dimensions, as a 2x2 run gives."""
    import pandas as pd

    return pd.DataFrame({
        "condition": ["HF_smallN", "HF_smallN", "LF_largeN", "LF_largeN"],
        "reference": ["HF_largeN"] * 4,
        "dimension": ["length", "old20", "length", "old20"],
        "cohens_d": [-0.627, -4.824, 0.0, -0.094],
    })


def test_the_realised_control_chart_draws_one_bar_per_comparison(app):
    """comparisons holds one row per non-anchor condition per dimension, and the
    chart encoded dimension alone, so a 2x2 design's three comparisons landed at
    one x position where they differ by as much as five standard deviations.
    Pinned identically in test-apps.R."""
    comp = _comparisons()
    chart = app.control_chart(comp)
    assert len(chart) == len(comp)
    assert list(chart.columns) == ["dimension", "condition", "abs_d"]
    assert chart["abs_d"].tolist() == [0.627, 4.824, 0.0, 0.094]
    # The channel that keeps them apart: without it the bars share a position.
    spec = app.control_plot(chart).to_dict()
    bars, rule = spec["layer"]
    assert bars["encoding"]["xOffset"]["field"] == "condition"
    assert bars["encoding"]["color"]["field"] == "condition"
    # The 0.5-SD line both captions name: the Shiny chart drew it and this one
    # did not, so the same numbers reached the two readers marked differently.
    assert rule["mark"]["type"] == "rule"
    assert spec["datasets"][rule["data"]["name"]] == [{"abs_d": 0.5}]

    # An undefined d, which the engine reports when two conditions are each
    # constant on a matched dimension at different constants, stays undefined and
    # Vega-Lite draws no bar for it. The Shiny chart used to fill that cell with a
    # zero and so drew the bar of a perfectly matched dimension; pinned
    # identically in test-apps.R.
    comp.loc[1, "cohens_d"] = float("nan")
    undefined = app.control_chart(comp)
    assert undefined["abs_d"].isna().tolist() == [False, True, False, False]


def test_both_apps_word_the_realised_control_caption_alike(app):
    """The caption told the reader to read one bar per dimension. It now says how
    many bars there are and which condition each is measured against, and the two
    apps say it the same way, as they do the item-table notice above it."""
    import re

    caption = app.control_caption(_comparisons())
    assert caption.startswith("Absolute standardised mean difference by dimension, "
                              "one bar per condition against the anchor HF_largeN.")
    shiny_src = open(os.path.join(os.path.dirname(os.path.dirname(APP_PATH)),
                                  "r_shiny", "app.R"), encoding="utf-8").read()
    # Join string literals split across lines before searching, so the assertion
    # sees the sentence a reader of the app sees.
    joined = re.sub(r'"\s*,?\s*"', "", shiny_src)
    for fragment in ("Absolute standardised mean difference by dimension, one bar per "
                     "condition against the anchor",
                     "Manipulated dimensions stand high; matched dimensions sit near "
                     "zero (below the 0.5-SD line)"):
        assert fragment in joined
        assert fragment in re.sub(r'"\s*,?\s*"', "", open(APP_PATH, encoding="utf-8").read())


def test_dropdowns_offer_exactly_the_methods_the_engine_implements(app):
    """The app must not advertise a method run_pipeline would reject."""
    import inspect

    import lexsync

    source = inspect.getsource(app)
    assert 'methods = ["standardised_euclidean", "joint", "mahalanobis", "optimal"]' in source
    # Against the registry, not a written-out list: a paradigm added to the engine
    # must reach the chooser, and a hard-coded expectation would simply pin
    # whatever the app happened to offer. Pinned identically in test-apps.R.
    assert sorted(app.PARADIGMS.values()) == sorted(lexsync.PARADIGMS)
    # The engine default first: the design only names a method when the other is
    # chosen. Pinned identically in test-apps.R.
    assert app.GENERATION_METHODS == ["letter_substitution", "subsyllabic"]


def test_every_item_table_paradigm_has_a_bundled_example(app):
    """The app writes items/<example> into the design and runs the pipeline
    against it, so a named table that is not in the repository would fail at run
    time. Pinned identically in test-apps.R."""
    import lexsync

    assert app.ITEM_TABLE_PARADIGMS
    assert set(app.ITEM_TABLE_PARADIGMS) <= set(app.PARADIGMS.values())
    for paradigm, (example, _columns) in app.ITEM_TABLE_PARADIGMS.items():
        assert paradigm in lexsync.PARADIGMS
        assert os.path.exists(os.path.join(app.REPO_ROOT, "items", example))


def test_the_run_design_yaml_is_written_with_lf_endings(app, tmp_path):
    """The pipeline hashes the design file it ran into the datasheet's
    design_sha256, so the bytes must not record which operating system wrote
    them; without newline="\n" the text-mode default writes CRLF on Windows.
    test-apps.R pins the same property for the Shiny app's write_yaml_lf."""
    path = app._write_design_yaml({"name": "t", "n_per_condition": 10},
                                  str(tmp_path / "design.yaml"))
    raw = open(path, "rb").read()
    assert b"\r" not in raw
    assert raw.endswith(b"\n")


def test_both_apps_word_the_item_table_notice_alike():
    """The Realised control tab is empty for a paradigm that draws from an item
    table, and the two apps explained that differently: one said "no corpus-matching
    report", the other "no corpus-matching control report". Someone comparing the two
    front-ends should not have to work out whether they mean the same thing."""
    import re

    notice = ("This paradigm draws from an item table, so no corpus-matching "
              "control report is produced.")
    apps_dir = os.path.dirname(os.path.dirname(APP_PATH))
    for path in (APP_PATH, os.path.join(apps_dir, "r_shiny", "app.R")):
        with open(path, encoding="utf-8") as handle:
            src = handle.read()
        # Join string literals split across lines before searching, so the assertion
        # sees the sentence a reader of the app sees.
        assert notice in re.sub(r'"\s*,?\s*"', "", src), path


def test_both_apps_refuse_a_factorial_run_with_nothing_to_match_on():
    """'Match on' can be emptied in either app, and the pipeline accepts
    match_on: [] happily, so the run reported success over a set that was never
    matched on anything and a realised-control tab full of large effects, which
    reads as a matching failure rather than as a design with no matching asked
    for. The refusal must be word-identical across the two apps."""
    import re

    notice = "Choose at least one dimension to match on."
    apps_dir = os.path.dirname(os.path.dirname(APP_PATH))
    for path in (APP_PATH, os.path.join(apps_dir, "r_shiny", "app.R")):
        with open(path, encoding="utf-8") as handle:
            assert notice in re.sub(r'"\s*,?\s*"', "", handle.read()), path


def test_both_apps_state_the_same_parity_claim(app):
    """The caption used to say only the seeded trial order differs by ecosystem,
    contradicting the keyed-hash guarantee (counterbalancing.py's header: the
    two engines produce the same order byte for byte). It then claimed byte
    identity for every method, which the method chooser's own help text and the
    datasheet's 'Cross-engine determinism' line both deny for mahalanobis and
    optimal. Both wordings must stay word-identical across the two apps."""
    import re

    deterministic = ("The R and Python engines produce byte-identical stimuli and "
                     "trial order from this configuration.")
    approximate = ("This design's matching method uses a covariance inverse or an "
                   "assignment solver, so the R and Python engines select equivalent "
                   "but not byte-identical stimuli. The datasheet's 'Cross-engine "
                   "determinism' line records which case applies.")
    for method in ("standardised_euclidean", "joint"):
        assert app.parity_claim({"matching": {"method": method}}) == deterministic
    assert app.parity_claim({}) == deterministic
    for method in ("mahalanobis", "optimal"):
        assert app.parity_claim({"matching": {"method": method}}) == approximate

    apps_dir = os.path.dirname(os.path.dirname(APP_PATH))
    streamlit_src = open(APP_PATH, encoding="utf-8").read()
    shiny_src = open(os.path.join(apps_dir, "r_shiny", "app.R"),
                     encoding="utf-8").read()
    for src in (streamlit_src, shiny_src):
        # Join string literals split across lines before searching, so the
        # assertion sees the sentence a reader of the app sees.
        joined = re.sub(r'"\s*,?\s*"', "", src)
        assert deterministic in joined
        assert approximate in joined
        assert "only the seeded trial order differs" not in src


def _shiny_preset_matching(path):
    """The Shiny app's PRESET_MATCHING, read from its source."""
    import re

    block = re.search(r"PRESET_MATCHING <- list\((.*?)\n\)\n", open(path, encoding="utf-8").read(),
                      re.S).group(1)
    entries = re.findall(
        r'"([^"]+)" = list\(match_on = (c\([^)]*\)|"[^"]*"),\s*method = "([^"]+)"\)', block)
    return {name: (re.findall(r'"([^"]+)"', dims), method) for name, dims, method in entries}


def test_both_apps_start_a_preset_from_the_same_matched_dimensions(app):
    """A preset that manipulates a dimension must not also ask the engine to match
    on it. Only the Streamlit presets set the matched dimensions and the method;
    the Shiny ones filled the conditions table and left 'Match on' at its general
    default, so the neighbourhood preset matched on n_density and old20 and
    returned a much weaker manipulation with frequency and length uncontrolled."""
    shiny = _shiny_preset_matching(
        os.path.join(os.path.dirname(os.path.dirname(APP_PATH)), "r_shiny", "app.R"))
    assert list(shiny.items()) == list(app.PRESET_MATCHING.items())
    manipulated = {"High vs low frequency": {"frequency"},
                   "Dense vs sparse neighbourhood": {"n_density"},
                   "2x2 frequency x neighbourhood": {"frequency", "n_density"},
                   "Custom": {"frequency"}}
    for preset, (match_on, _method) in app.PRESET_MATCHING.items():
        assert not manipulated[preset] & set(match_on), preset


def test_the_app_passes_no_widget_argument_streamlit_has_removed():
    """use_container_width was deprecated with a removal date of 2025-12-31, and
    the dev extra names no upper bound, so once the argument goes every table, the
    conditions editor and the Run button raise TypeError on the first render and
    the app does not open at all. Nothing else would catch it: the suite reaches
    the module's helpers, not its widgets."""
    import inspect

    import streamlit as st

    with open(APP_PATH, encoding="utf-8") as handle:
        source = handle.read()
    assert "use_container_width" not in source
    assert 'width="stretch"' in source
    for widget in (st.dataframe, st.data_editor, st.button, st.altair_chart):
        assert "width" in inspect.signature(widget).parameters


def test_the_sidebar_fields_all_come_before_the_version_footer():
    """'Stimulus font' was created 200 lines below the sidebar block, and Streamlit
    places a widget where the call is made, so the field landed under the rule and
    the version line that close the sidebar. The Shiny sidebar has always ordered
    the four fields together, and both doc pages describe that order."""
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(APP_PATH, default_timeout=120)
    at.run()
    assert not at.exception
    kinds = [element.type for element in at.sidebar]
    labels = [getattr(element, "label", None) for element in at.sidebar]
    for field in ("Paradigm", "Design name", "Language label", "Stimulus font"):
        assert kinds.index("divider") > labels.index(field), field
    assert kinds.index("caption") > kinds.index("divider")


def test_every_preset_leaves_the_optional_second_factor_columns_numeric(app):
    """A preset that leaves the second factor empty still has to hand the editor a
    numeric column: None types it as object, and an edit to a cell of an object
    column then arrives as text that conditions_from_table cannot read as a bound.
    The Shiny twin is pinned by 'every preset leaves the optional second-factor
    columns numeric' in test-apps.R."""
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(APP_PATH, default_timeout=300)
    at.run()
    at.sidebar.selectbox[0].select("Factorial word contrast (corpus matching)").run()
    for preset in app.PRESET_MATCHING:
        chooser = [box for box in at.selectbox if box.label == "Start from a preset"]
        assert chooser, "the preset chooser is not on the page"
        at = chooser[0].select(preset).run()
        assert not at.exception, preset
        editors = [frame.value for frame in at.dataframe
                   if "lower2" in getattr(frame.value, "columns", [])]
        assert len(editors) == 1, preset
        assert editors[0]["lower2"].dtype.kind == "f", preset
        assert editors[0]["upper2"].dtype.kind == "f", preset


def test_an_upload_is_written_once_per_file_not_once_per_rerun(app, tmp_path):
    """The script re-executes top to bottom on every widget interaction and the
    uploader keeps handing back the file it holds, so writing it in the page body
    copied a lexicon of about a megabyte for every keystroke, tab and slider move,
    with nothing removing what it wrote."""
    import hashlib

    data = b"word,freq_zipf\ncat,5.0\n"
    digest = hashlib.sha256(data).hexdigest()
    first = app.staged_upload("mine.csv", digest, data)
    second = app.staged_upload("mine.csv", digest, data)
    assert first == second
    assert os.path.basename(first) == "mine.csv"
    with open(first, "rb") as handle:
        assert handle.read() == data

    other = b"word,freq_zipf\ndog,4.0\n"
    assert app.staged_upload("mine.csv", hashlib.sha256(other).hexdigest(), other) != first


def test_a_new_run_reclaims_the_previous_run_s_directory(app, tmp_path):
    """Every run writes its design, its staged inputs and a whole output tree under
    a fresh temporary directory, and nothing reclaimed them, so a long-lived
    process kept one complete set of artefacts per press of Run."""
    previous = tmp_path / "run"
    (previous / "output" / "reports").mkdir(parents=True)
    (previous / "output" / "reports" / "datasheet.md").write_text("# d\n", encoding="utf-8")

    app.discard_run_dir(str(previous))

    assert not previous.exists()
    # Nothing to reclaim before the first run, and a directory already gone is not
    # an error: both reach this from the run branch.
    app.discard_run_dir(None)
    app.discard_run_dir(str(previous))


def test_two_runs_at_once_each_read_their_own_staged_lexicon(app, tmp_path):
    """The run makes the staging directory the working directory, which is a
    property of the process, and Streamlit runs every browser session in a thread
    of one process. Two overlapping runs therefore resolved the design's relative
    lexicon path against whichever staging directory was entered last, and both
    reported success over one set of materials. One user with two tabs was enough."""
    import hashlib
    import json
    import threading

    lexicon = os.path.join(app.REPO_ROOT, "corpora", "derived", "en.csv")
    if not os.path.exists(lexicon):
        pytest.skip("The bundled corpora are not in this tree.")
    with open(lexicon, encoding="utf-8") as handle:
        rows = handle.readlines()
    # Two different lexicons that a design can be run over, both of which the app
    # stages at the one relative path the design names.
    lexicons = []
    for index, keep in enumerate((len(rows), len(rows) - 200)):
        path = tmp_path / f"lexicon_{index}.csv"
        path.write_text("".join(rows[:keep]), encoding="utf-8")
        lexicons.append(str(path))

    def design_for(name):
        return {
            "name": name, "language": "english",
            "lexicon": "corpora/derived/en.csv",
            "pool_filters": {"length": [3, 7], "frequency": [3.5, 7.0]},
            "paradigm": "factorial",
            "conditions": [
                {"name": "high_frequency", "define_by": {"frequency": [5.2, 7.0]}},
                {"name": "low_frequency", "define_by": {"frequency": [3.8, 4.4]}},
            ],
            "n_per_condition": 20, "match_on": ["length"],
            "matching": {"method": "standardised_euclidean"},
            "counterbalance": {"lists": 1},
        }

    start = threading.Barrier(len(lexicons))
    bundles, failures = {}, {}

    def run(index):
        try:
            start.wait(timeout=60)
            bundles[index] = app.run_design(design_for(f"run_{index}"), lexicons[index], None)
        except Exception as error:  # reported below, so the assertion names the run
            failures[index] = error

    threads = [threading.Thread(target=run, args=(i,)) for i in range(len(lexicons))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert not failures, failures

    for index, bundle in bundles.items():
        with open(os.path.join(bundle["outdir"], "reports",
                               bundle["base"] + "_datasheet_py.json"), encoding="utf-8") as handle:
            datasheet = json.load(handle)
        with open(lexicons[index], "rb") as handle:
            own = hashlib.sha256(handle.read()).hexdigest()
        assert datasheet["materials_source"]["sha256"] == own


def test_every_paradigm_the_app_offers_runs_to_a_result(app):
    """The suite reached the helpers the export path is built from and nothing
    else, so a name error in a paradigm branch, or a design a branch assembles
    that the engine refuses, would have shown up only when someone opened the
    page. Each paradigm is selected, run, and asked for its result. The Shiny
    twin is driven the same way in test-apps.R."""
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    for label in app.PARADIGMS:
        at = AppTest.from_file(APP_PATH, default_timeout=300)
        at.run()
        at.sidebar.selectbox[0].select(label).run()
        assert not at.exception, label
        # Enough rows to matter and few enough to keep the sweep quick; the
        # item-table paradigms take their trials from the table and offer no
        # such field.
        for number in at.number_input:
            if number.label.startswith("Items per condition"):
                number.set_value(8)
        at.run()

        at.button[0].click().run()
        assert not at.exception, label
        assert [e.value for e in at.error] == [], label
        assert at.success[0].value.startswith("Selected "), label
        # Stimuli, Realised control, Datasheet, Experiment scripts, Reproducible
        # code and Download: the results are on the page, not merely computed.
        assert len(at.tabs) == 6, label


def test_both_apps_take_the_lexsync_accent():
    """The Shiny app took Bootswatch's cosmo blue and the Streamlit app declared no
    theme at all, so two front-ends over one package looked unlike each other and
    unlike the documentation site. Cosmo's blue also reaches only 3.97:1 against the
    white label of the full-width Run button, below AA for that size, where the
    lexsync accent reaches 6.04:1. The two apps must name the same hex."""
    import re

    accent = "#7C4EA3"
    apps_dir = os.path.dirname(os.path.dirname(APP_PATH))
    repo = os.path.dirname(apps_dir)
    scss = os.path.join(repo, "R_workflow", "pkgdown", "extra.scss")
    with open(scss, encoding="utf-8") as handle:
        assert "--brand-primary:      %s;" % accent in handle.read()

    shiny = os.path.join(apps_dir, "r_shiny", "app.R")
    with open(shiny, encoding="utf-8") as handle:
        src = handle.read()
    assert 'BRAND_PRIMARY <- "%s"' % accent in src
    assert re.search(r"bs_theme\([^)]*primary = BRAND_PRIMARY", src, re.S)

    config = os.path.join(repo, ".streamlit", "config.toml")
    with open(config, encoding="utf-8") as handle:
        theme = handle.read()
    assert 'primaryColor = "%s"' % accent in theme
    # The accent and nothing else, as the Shiny theme does: pinning
    # backgroundColor and textColor held every viewer to a light page whatever
    # their system asked for.
    assert "backgroundColor" not in theme and "textColor" not in theme
