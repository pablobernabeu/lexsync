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
from helper_repo import REPO

# The app is not part of the package, and it is executed, so it is taken only from the
# lexsync repository itself (see helper_repo.py), as test-apps.R takes the Shiny app.
APP_PATH = os.path.join(REPO, "apps", "python_streamlit", "lexsync_app.py") if REPO else None

pytestmark = pytest.mark.skipif(REPO is None, reason="the Streamlit app source is not in this tree")


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


def _contents(payload):
    """Each entry's bytes, by name. Two archives of the same files are not equal as
    bytes: make_zip() stamps the design it writes from memory with the current time,
    and a zip counts time in two-second steps, so archives made either side of a step
    differ in their headers."""
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        return {name: z.read(name) for name in z.namelist()}


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

    assert (_contents(app.make_zip(design, "my_design.yaml", {"outdir": str(out)}, None))
            == _contents(app.make_zip(design, "my_design.yaml", {"outdir": str(out)}, {})))
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


def test_dropdowns_offer_exactly_the_methods_the_engine_implements(app):
    """The app must not advertise a method run_pipeline would reject."""
    import inspect

    source = inspect.getsource(app)
    assert 'methods = ["standardised_euclidean", "joint", "mahalanobis", "optimal"]' in source
    assert sorted(app.PARADIGMS.values()) == [
        "factorial", "lexical_decision", "priming", "self_paced_reading",
    ]
    # The engine default first: the design only names a method when the other is
    # chosen. Pinned identically in test-apps.R.
    assert app.GENERATION_METHODS == ["letter_substitution", "subsyllabic"]


def test_the_experiment_tab_offers_every_file_the_export_wrote(app):
    """A design with several counterbalancing versions writes one OpenSesame
    experiment per version, and each runs from its own tables, so the tab offers every
    file export_experiments lists, not only the three scripts. Pinned identically in
    test-apps.R."""
    files = ["a_psychopy.py", "a_list1.osexp", "a_list2.osexp", "a.html", "a_psychopy.csv"]
    assert app.experiment_files({"psychopy": files[0], "opensesame": files[1],
                                 "jspsych": files[3], "files": files}) == files
    # A result without `files`, from an older lexsync, still offers its three scripts.
    assert app.experiment_files({"psychopy": "a.py", "opensesame": "a.osexp",
                                 "jspsych": "a.html"}) == ["a.py", "a.osexp", "a.html"]
    assert app.experiment_files({}) == []


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


def _joined_sources():
    """Both apps' sources with string literals split across lines joined, so an
    assertion sees the sentence a reader of the app sees."""
    import re

    apps_dir = os.path.dirname(os.path.dirname(APP_PATH))
    out = {}
    for path in (APP_PATH, os.path.join(apps_dir, "r_shiny", "app.R")):
        with open(path, encoding="utf-8") as handle:
            out[path] = re.sub(r'"\s*,?\s*"', "", handle.read())
    return out


# The two captions under the exported code. Which one a run shows is read from its
# datasheet's selection.cross_engine. Pinned identically in test-apps.R.
BYTE_IDENTICAL = ("The R and Python engines select byte-identical stimuli and trial order "
                  "from this configuration.")
APPROXIMATE = ("The R and Python engines select equivalent but not byte-identical stimuli "
               "for this matching method.")


def test_both_apps_state_the_same_parity_claim():
    """The caption used to say only the seeded trial order differs by ecosystem,
    contradicting the keyed-hash guarantee (counterbalancing.py's header: the
    two engines produce the same order byte for byte). It then claimed byte
    identity whatever the method, although mahalanobis and optimal agree only
    approximately and the run's own datasheet says so. Both sentences must stay
    word-identical across the two apps."""
    for path, joined in _joined_sources().items():
        assert BYTE_IDENTICAL in joined, path
        assert APPROXIMATE in joined, path
        assert "only the seeded trial order differs" not in joined, path
        assert "produce byte-identical stimuli and trial order" not in joined, path


def test_the_parity_claim_follows_the_run_datasheet(app):
    """The caption is taken from the datasheet's selection.cross_engine, so it says
    what the run's own record says. Pinned identically in test-apps.R."""
    def record(cross):
        return {"selection": {"cross_engine": cross}}

    assert app.parity_claim(record("byte-identical")) == BYTE_IDENTICAL
    assert app.parity_claim(record("approximate (platform linear algebra)")) == APPROXIMATE
    # An item-table design selects nothing, and both engines write the same files.
    assert app.parity_claim(record("n/a (user-supplied items)")) == BYTE_IDENTICAL
    # The datasheet's own renderer reads a missing field as byte-identical.
    assert app.parity_claim({}) == BYTE_IDENTICAL
    assert app.parity_claim(None) == BYTE_IDENTICAL


def test_the_interval_label_follows_the_datasheet_alpha(app):
    """Cohen's d carries the 1 - 2 alpha interval that goes with the TOST, and the
    column was headed 90% whatever the schema's alpha. Pinned identically in
    test-apps.R."""
    def record(alpha):
        return {"equivalence": {"bound_d": 0.5, "alpha": alpha}}

    assert app.interval_label(record(0.05)) == "90% CI"
    assert app.interval_label(record(0.025)) == "95% CI"
    assert app.interval_label(record(0.005)) == "99% CI"
    assert app.interval_label(record(0.1)) == "80% CI"
    # A record without the field was written at the default alpha.
    assert app.interval_label({}) == "90% CI"
    assert app.interval_label(None) == "90% CI"


def test_the_caption_and_the_interval_label_come_from_the_run_datasheet(app):
    """End to end: a Mahalanobis run records an approximate cross-engine agreement,
    and the caption under its exported code says so. Pinned identically in
    test-apps.R for the Shiny app."""
    import shutil

    lexicon = os.path.join(app.REPO_ROOT, "corpora", "derived", "en_v2.csv")
    if not os.path.exists(lexicon):
        pytest.skip("The bundled corpora are not in this tree.")
    design = {
        "name": "my_design", "language": "english",
        "lexicon": "corpora/derived/en_v2.csv",
        "pool_filters": {"length": [3, 7], "frequency": [3.5, 7.0], "nonstandard": [0, 0]},
        "paradigm": "factorial",
        "conditions": [
            {"name": "high_frequency", "define_by": {"frequency": [5.2, 7.0]}},
            {"name": "low_frequency", "define_by": {"frequency": [3.8, 4.4]}},
        ],
        "n_per_condition": 10, "match_on": ["length", "old20"],
        "matching": {"method": "mahalanobis"},
        "counterbalance": {"lists": 1},
    }
    bundle = app.run_design(design, lexicon, None)
    try:
        record = bundle["record"]
        assert record["selection"]["cross_engine"].startswith("approximate")
        assert app.parity_claim(record) == APPROXIMATE
        assert app.interval_label(record) == "90% CI"
    finally:
        shutil.rmtree(os.path.dirname(bundle["outdir"]), ignore_errors=True)


# Each preset's rows (name, dimension, lower, upper, categories, dimension2, lower2,
# upper2; None is an empty bound), its matched dimensions and its method, as the
# repository's design files match such contrasts. Pinned identically in test-apps.R.
PRESETS = {
    "High vs low frequency": (
        [("high_frequency", "frequency", 5.2, 7.0, "", "", None, None),
         ("low_frequency", "frequency", 3.8, 4.4, "", "", None, None)],
        ["length", "n_density", "old20"], "standardised_euclidean"),
    "Dense vs sparse neighbourhood": (
        [("dense_neighbourhood", "n_density", 5.0, 100.0, "", "", None, None),
         ("sparse_neighbourhood", "n_density", 0.0, 1.0, "", "", None, None)],
        ["length", "frequency"], "joint"),
    "2x2 frequency x neighbourhood": (
        [("HF_largeN", "frequency", 5.0, 7.0, "", "n_density", 9.0, 100.0),
         ("HF_smallN", "frequency", 5.0, 7.0, "", "n_density", 0.0, 5.0),
         ("LF_largeN", "frequency", 2.5, 4.2, "", "n_density", 9.0, 100.0),
         ("LF_smallN", "frequency", 2.5, 4.2, "", "n_density", 0.0, 5.0)],
        ["length"], "standardised_euclidean"),
    "Custom": (
        [("condition_a", "frequency", 5.0, 7.0, "", "", None, None),
         ("condition_b", "frequency", 3.5, 4.5, "", "", None, None)],
        ["length"], "standardised_euclidean"),
}
PRESET_COLUMNS = ("name", "dimension", "lower", "upper", "categories", "dimension2",
                  "lower2", "upper2")


def test_both_apps_pin_the_same_presets(app):
    """The Shiny presets filled the conditions table and left 'Match on' and the
    method at their general defaults, so its neighbourhood preset matched on N and
    OLD20 and left length unequated, while the Streamlit preset of the same name
    matched on length and frequency."""
    assert list(app.PRESET_MATCHING) == list(PRESETS)
    for preset, (rows, match_on, method) in PRESETS.items():
        got = [tuple(row[c] for c in PRESET_COLUMNS) for row in app.preset_rows(preset)]
        assert got == rows, preset
        assert app.PRESET_MATCHING[preset] == (match_on, method), preset


def test_no_preset_matches_on_a_dimension_it_manipulates(app):
    import pandas as pd

    for preset, (_rows, match_on, _method) in PRESETS.items():
        conditions = app.conditions_from_table(pd.DataFrame(app.preset_rows(preset)))
        assert len(conditions) == len(app.preset_rows(preset)), preset
        assert app.manipulated_matches(conditions, match_on) == [], preset


def test_manipulated_matches_names_the_dimensions_whose_windows_differ(app):
    """A matched dimension that defines the conditions with different windows works
    against the contrast. A band every condition shares restricts the pool and is
    legitimate. Pinned identically in test-apps.R."""
    freq = [{"name": "high", "define_by": {"frequency": [5.2, 7.0]}},
            {"name": "low", "define_by": {"frequency": [3.8, 4.4]}}]
    assert app.manipulated_matches(freq, ["length", "frequency"]) == ["frequency"]
    assert app.manipulated_matches(freq, ["length", "old20"]) == []
    assert app.manipulated_matches(freq, []) == []
    shared = [{"name": "dense", "define_by": {"frequency": [4.0, 6.0], "n_density": [5.0, 100.0]}},
              {"name": "sparse", "define_by": {"frequency": [4.0, 6.0], "n_density": [0.0, 1.0]}}]
    assert app.manipulated_matches(shared, ["frequency", "n_density", "length"]) == ["n_density"]
    # A window on one condition alone leaves the others unrestricted on it.
    one_sided = [{"name": "a", "define_by": {"frequency": [5.0, 7.0], "length": [3.0, 5.0]}},
                 {"name": "b", "define_by": {"frequency": [3.0, 4.0]}}]
    assert app.manipulated_matches(one_sided, ["old20", "length"]) == ["length"]
    assert app.manipulated_matches([], ["length"]) == []

    assert app.manipulation_warning([]) is None
    assert app.manipulation_warning(["frequency"]) == (
        "'Match on' includes frequency, on which the conditions take different windows. "
        "Matching on a dimension the conditions manipulate works against the contrast "
        "they define.")
    assert app.manipulation_warning(["frequency", "n_density", "old20"]).startswith(
        "'Match on' includes frequency, n_density and old20, on which")


# The sentence that keeps Run disabled while 'Match on' is empty. Pinned identically
# in test-apps.R.
EMPTY_MATCH_ON = "Choose at least one dimension to match on."
# The Streamlit method help, which the Shiny selector now shows too.
METHOD_HELP = ("joint/optimal pair two conditions (optimal selects the n pairs of "
               "least summed distance, joint takes the closest pair at each step); "
               "mahalanobis down-weights correlated dimensions. mahalanobis and "
               "optimal use a covariance inverse / assignment solver, so the R and "
               "Python engines agree closely but not byte-for-byte on them.")


def test_both_apps_word_the_guards_and_the_method_help_alike(app):
    assert app.EMPTY_MATCH_ON == EMPTY_MATCH_ON
    assert app.METHOD_HELP == METHOD_HELP
    for path, joined in _joined_sources().items():
        for sentence in (EMPTY_MATCH_ON, METHOD_HELP, app.SCREEN_HELP):
            assert sentence in joined, (path, sentence)


def test_both_app_headers_qualify_byte_identity():
    """Both headers claimed byte-identical stimuli outright, while each app offers
    the two methods that agree only approximately."""
    for path, joined in _joined_sources().items():
        assert ("Under the deterministic matching methods, which include the default, "
                "the two") in joined, path
        assert "The two engines select byte-identical stimuli" not in joined, path


# The command lines under 'Reproducible code' for a design named "my design (v2)".
# Double quotes outside and single quotes inside run in bash, cmd.exe, Windows
# PowerShell and PowerShell 7, and clean_meta() refuses every character that would
# end such a string. Each comment has a line of its own, because cmd.exe reads a
# trailing # as one more argument. Pinned identically in test-apps.R.
CLI = (
    "# R\n"
    "Rscript -e \"lexsync::run_pipeline('my design (v2).yaml', "
    "schema_path = 'config/schema.yaml', outdir = 'output')\"\n"
    "# Python console script\n"
    "lexsync run \"my design (v2).yaml\"\n"
    "# Python (module form)\n"
    "python -m lexsync run \"my design (v2).yaml\""
)


def test_the_command_lines_quote_the_design_file_and_name_the_output(app):
    """Streamlit's R line omitted outdir, which run_pipeline requires, and both apps
    quoted the R expression with single quotes outside, which cmd.exe and Windows
    PowerShell break. The Python lines left the file name unquoted."""
    import shlex

    cli = app.reproduction_code({"name": "my design (v2)"}, "my design (v2).yaml")["cli"]
    assert cli == CLI
    commands = [line for line in cli.split("\n") if not line.startswith("#")]
    assert [shlex.split(line) for line in commands] == [
        ["Rscript", "-e", "lexsync::run_pipeline('my design (v2).yaml', "
                          "schema_path = 'config/schema.yaml', outdir = 'output')"],
        ["lexsync", "run", "my design (v2).yaml"],
        ["python", "-m", "lexsync", "run", "my design (v2).yaml"],
    ]


# The lexicon both apps open on. Pinned identically in test-apps.R.
DEFAULT_LEXICON = "en_v2"


def test_the_pool_filters_screen_marked_forms_when_the_lexicon_marks_them(app):
    """en_v2 marks the forms its SUBTLEX-US screen flags, and the shipped English
    designs keep only the unmarked ones with nonstandard: [0, 0]. The apps offered
    the unscreened en.csv first and no way to apply the screen. Pinned identically
    in test-apps.R."""
    assert app.DEFAULT_LEXICON == DEFAULT_LEXICON
    marked = ["word", "freq_zipf", "nonstandard"]
    assert app.pool_filters((3, 7), (3.5, 7.0), marked, True) == {
        "length": [3, 7], "frequency": [3.5, 7.0], "nonstandard": [0, 0]}
    assert app.pool_filters((3, 7), (3.5, 7.0), marked, False) == {
        "length": [3, 7], "frequency": [3.5, 7.0]}
    assert app.pool_filters((3, 7), (3.5, 7.0), ["word", "freq_zipf"], True) == {
        "length": [3, 7], "frequency": [3.5, 7.0]}
    lexicon = os.path.join(app.REPO_ROOT, "corpora", "derived", "en_v2.csv")
    if os.path.exists(lexicon):
        assert "nonstandard" in app.lexicon_columns(lexicon)


def test_the_app_passes_no_widget_argument_streamlit_is_removing():
    """use_container_width is deprecated, with a removal date of 2025-12-31, and the
    dev extra named no upper bound. Once it goes, the Run button, created at the top
    level of the script, raises TypeError and the app does not open. width="stretch"
    replaces it, and st.dataframe and st.data_editor accept it from Streamlit 1.49,
    so the floor and the documented install lines move there."""
    with open(APP_PATH, encoding="utf-8") as handle:
        source = handle.read()
    assert "use_container_width" not in source
    assert source.count('width="stretch"') == 8
    root = os.path.dirname(os.path.dirname(os.path.dirname(APP_PATH)))
    with open(os.path.join(root, "python_workflow", "pyproject.toml"), encoding="utf-8") as handle:
        assert '"streamlit>=1.49"' in handle.read()
    for doc in (os.path.join(root, "apps", "README.md"),
                os.path.join(root, "python_workflow", "docs", "the-app.md")):
        with open(doc, encoding="utf-8") as handle:
            text = handle.read()
        assert 'pip install "streamlit>=1.49"' in text, doc
        assert "pip install streamlit\n" not in text, doc


def _app_test():
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(APP_PATH, default_timeout=120)
    at.run()
    assert not at.exception
    return at


def _labelled(elements, label):
    found = [element for element in elements if element.label == label]
    assert len(found) == 1, label
    return found[0]


def test_a_preset_sets_the_matched_dimensions_and_the_method():
    at = _app_test()
    for preset, (_rows, match_on, method) in PRESETS.items():
        _labelled(at.selectbox, "Start from a preset").select(preset).run()
        assert not at.exception, preset
        assert _labelled(at.multiselect, "Match on (controlled dimensions)").value == match_on
        assert _labelled(at.radio, "Matching method").value == method


def test_the_app_opens_on_the_screened_lexicon_and_guards_match_on():
    """The app opens on en_v2 with the screen applied. A matched dimension that
    the conditions manipulate draws a warning, and an empty 'Match on' disables
    Run, which used to report success over a set matched on nothing."""
    at = _app_test()
    assert _labelled(at.selectbox, "Lexicon").value == DEFAULT_LEXICON
    assert _labelled(at.checkbox, "Screened forms only").value is True
    run = [button for button in at.button if "Run design" in button.label]
    assert len(run) == 1 and not run[0].disabled
    assert [w.value for w in at.warning] == []

    match_on = _labelled(at.multiselect, "Match on (controlled dimensions)")
    match_on.set_value(["length", "frequency"]).run()
    assert not at.exception
    assert [w.value for w in at.warning] == [
        "'Match on' includes frequency, on which the conditions take different windows. "
        "Matching on a dimension the conditions manipulate works against the contrast "
        "they define."]

    _labelled(at.multiselect, "Match on (controlled dimensions)").set_value([]).run()
    assert not at.exception
    assert [w.value for w in at.warning] == [EMPTY_MATCH_ON]
    run = [button for button in at.button if "Run design" in button.label]
    assert run[0].disabled
