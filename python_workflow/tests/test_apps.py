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


def test_both_apps_state_the_same_parity_claim():
    """The caption used to say only the seeded trial order differs by ecosystem,
    contradicting the keyed-hash guarantee (counterbalancing.py's header: the
    two engines produce the same order byte for byte). The corrected sentence
    must stay word-identical across the two apps."""
    import re

    claim = ("The R and Python engines produce byte-identical stimuli and "
             "trial order from this configuration.")
    apps_dir = os.path.dirname(os.path.dirname(APP_PATH))
    streamlit_src = open(APP_PATH, encoding="utf-8").read()
    shiny_src = open(os.path.join(apps_dir, "r_shiny", "app.R"),
                     encoding="utf-8").read()
    for src in (streamlit_src, shiny_src):
        # Join string literals split across lines before searching, so the
        # assertion sees the sentence a reader of the app sees.
        joined = re.sub(r'"\s*,?\s*"', "", src)
        assert claim in joined
        assert "only the seeded trial order differs" not in src
