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

    # The same three entries the Shiny app's write_bundle_zip produces (test-apps.R):
    # names are relative to outdir and subdirectories survive.
    assert _names(payload) == ["my_design.yaml", "reports/datasheet.md", "stimuli.csv"]


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
    """A bundled corpus resolves in the repository, so nothing extra is shipped."""
    out = tmp_path / "output"
    out.mkdir()
    (out / "my_design_stimuli_py.csv").write_text("word\ncat\n", encoding="utf-8")
    design = {"name": "my_design", "lexicon": "corpora/derived/en_example.csv"}

    assert (app.make_zip(design, "my_design.yaml", {"outdir": str(out)}, None)
            == app.make_zip(design, "my_design.yaml", {"outdir": str(out)}, {}))
    assert _names(app.make_zip(design, "my_design.yaml", {"outdir": str(out)})) == [
        "my_design.yaml", "my_design_stimuli_py.csv",
    ]


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
