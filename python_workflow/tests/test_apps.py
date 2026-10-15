"""Tests for the Streamlit front-end in apps/python_streamlit.

The app module is a Streamlit script, so importing it executes its UI. Streamlit
tolerates that outside a running server (widgets return their defaults), which is
enough to reach the plain helper functions the export path is built from.
"""
import importlib.util
import io
import json
import os
import re
import shutil
import tempfile
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


def test_make_zip_holds_the_run_directory_at_its_own_relative_paths(app, tmp_path):
    """The bundle is the directory the run ran in, archived whole, so the exported
    code finds the design, the schema and the outputs where it names them. The Shiny
    app's write_bundle_zip produces the same entries (test-apps.R)."""
    root = tmp_path / "run"
    (root / "config").mkdir(parents=True)
    (root / "output" / "reports").mkdir(parents=True)
    (root / "my_design.yaml").write_text("name: my_design\n", encoding="utf-8")
    (root / "config" / "schema.yaml").write_text("seed: 1\n", encoding="utf-8")
    (root / "output" / "stimuli.csv").write_bytes(b"word\ncat\n")
    (root / "output" / "reports" / "datasheet.md").write_text("# datasheet\n", encoding="utf-8")

    payload = app.make_zip({"root": str(root)})

    assert _names(payload) == ["config/schema.yaml", "my_design.yaml",
                               "output/reports/datasheet.md", "output/stimuli.csv"]
    assert _contents(payload)["output/stimuli.csv"] == b"word\ncat\n"


def test_the_run_directory_is_laid_out_like_the_bundle(app, tmp_path):
    """The design as displayed, the schema at config/schema.yaml and every input at
    the path the design records, uploads included, and nothing else. An uploaded
    lexicon lives only in a temporary directory, and a bundled one at a path that
    resolves to nothing outside the checkout. Pinned identically in test-apps.R."""
    lexicon = tmp_path / "upload" / "mine.csv"
    lexicon.parent.mkdir()
    lexicon.write_bytes(b"word,freq_zipf\ncat,5.0\n")
    table = tmp_path / "example" / "pairs.csv"
    table.parent.mkdir()
    table.write_bytes(b"item,condition,prime,target\n1,rel,cat,dog\n")
    design = {"name": "my design (v2)", "language": "english", "lexicon": "corpora/mine.csv",
              "items": {"source": "table", "path": "items/pairs.csv"}}

    inputs = app.staged_inputs(design, str(lexicon), str(table))
    assert inputs == {"corpora/mine.csv": str(lexicon), "items/pairs.csv": str(table)}
    assert app.staged_inputs({"name": "x"}, None, None) == {}

    root = app.stage_run(design, "my design (v2).yaml", inputs)
    try:
        found = sorted(os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/")
                       for d, _dirs, files in os.walk(root) for f in files)
        assert found == ["config/schema.yaml", "corpora/mine.csv", "items/pairs.csv",
                         "my design (v2).yaml"]

        def read(rel):
            with open(os.path.join(root, *rel.split("/")), "rb") as handle:
                return handle.read()

        # The file the pipeline hashes is the text the Reproducible code tab shows,
        # with LF endings on every platform.
        assert read("my design (v2).yaml") == app.yaml_block(design).encode("utf-8")
        with open(app.SCHEMA_PATH, "rb") as handle:
            assert read("config/schema.yaml") == handle.read()
        assert read("corpora/mine.csv") == lexicon.read_bytes()
        assert read("items/pairs.csv") == table.read_bytes()
    finally:
        shutil.rmtree(root, ignore_errors=True)


# Paths that would put a file outside the run directory: an uploaded file's name and
# the design's name both reach it. Pinned identically in test-apps.R.
ESCAPING = ["../x.csv", "corpora/../../x.csv", "/x.csv", "\\x.csv", "C:/x.csv", "c:x.csv",
            "~/x.csv", ""]


def _recording_mkdtemp(monkeypatch, app):
    """Record every directory the app's runs create, so a test can check each went."""
    made = []
    real = tempfile.mkdtemp

    def mkdtemp(*args, **kwargs):
        made.append(real(*args, **kwargs))
        return made[-1]

    monkeypatch.setattr(app.tempfile, "mkdtemp", mkdtemp)
    return made


def test_a_path_that_leaves_the_run_directory_is_refused(app, tmp_path, monkeypatch):
    root = str(tmp_path)
    assert app.bundle_path(root, "corpora/derived/en.csv") == os.path.join(
        root, "corpora", "derived", "en.csv")
    for rel in ESCAPING:
        with pytest.raises(ValueError, match="inside the bundle"):
            app.bundle_path(root, rel)
    source = tmp_path / "x.csv"
    source.write_bytes(b"word\n")
    made = _recording_mkdtemp(monkeypatch, app)
    with pytest.raises(ValueError, match="inside the bundle"):
        app.stage_run({"name": "x"}, "x.yaml", {"../x.csv": str(source)})
    with pytest.raises(ValueError, match="inside the bundle"):
        app.stage_run({"name": "x"}, "../x.yaml", {})
    # A refused staging leaves no directory behind.
    assert len(made) == 2
    assert [d for d in made if os.path.exists(d)] == []


# The downloads the Experiment scripts tab offers for a design with two lists, one per
# target, each with the files that target reads. Pinned identically in test-apps.R.
EXPERIMENT_FILES = ["out/a_psychopy.py", "out/a_list1.osexp", "out/a_list2.osexp", "out/a.html",
                    "out/a_psychopy.csv", "out/a_list1_opensesame.csv",
                    "out/a_list1_opensesame_text.csv", "out/a_list2_opensesame.csv",
                    "out/a_list2_opensesame_text.csv"]
EXPERIMENT_DOWNLOADS = [
    {"target": "PsychoPy", "file_name": "a_psychopy.zip",
     "files": ["out/a_psychopy.py", "out/a_psychopy.csv"]},
    {"target": "OpenSesame", "file_name": "a_opensesame.zip",
     "files": ["out/a_list1.osexp", "out/a_list2.osexp", "out/a_list1_opensesame.csv",
               "out/a_list1_opensesame_text.csv", "out/a_list2_opensesame.csv",
               "out/a_list2_opensesame_text.csv"]},
    {"target": "jsPsych", "file_name": "a.html", "files": ["out/a.html"]},
]


def test_each_experiment_download_carries_the_tables_it_loads(app):
    """The PsychoPy script loads its conditions file from its own folder and each
    OpenSesame experiment its loop and text tables, but the tab offered each file on
    its own, so a downloaded script could not run. The jsPsych page embeds its trials."""
    assert app.experiment_downloads(EXPERIMENT_FILES, "a") == EXPERIMENT_DOWNLOADS
    assert app.experiment_downloads([], "a") == []


def _sha256(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


# A small factorial design over the bundled en_v2, as the app would build it.
def _factorial_design(method="standardised_euclidean"):
    return {
        "name": "my_design", "language": "english",
        "lexicon": "corpora/derived/en_v2.csv",
        "pool_filters": {"length": [3, 7], "frequency": [3.5, 7.0], "nonstandard": [0, 0]},
        "paradigm": "factorial",
        "conditions": [
            {"name": "high_frequency", "define_by": {"frequency": [5.2, 7.0]}},
            {"name": "low_frequency", "define_by": {"frequency": [3.8, 4.4]}},
        ],
        "n_per_condition": 10, "match_on": ["length", "old20"],
        "matching": {"method": method},
        "counterbalance": {"lists": 1},
    }


@pytest.fixture(scope="module")
def bundled_run(app, tmp_path_factory):
    """One run through the app's own path, its download and the bundle unzipped."""
    lexicon = os.path.join(app.REPO_ROOT, "corpora", "derived", "en_v2.csv")
    if not os.path.exists(lexicon):
        pytest.skip("The bundled corpora are not in this tree.")
    design = _factorial_design()
    bundle = app.run_design(design, "my_design.yaml", app.staged_inputs(design, lexicon, None))
    try:
        payload = app.make_zip(bundle)
        unzipped = tmp_path_factory.mktemp("bundle")
        with zipfile.ZipFile(io.BytesIO(payload)) as z:
            z.extractall(unzipped)
        yield {"design": design, "bundle": bundle, "payload": payload, "dir": unzipped}
    finally:
        shutil.rmtree(bundle["root"], ignore_errors=True)


def _bundled(run, rel):
    return (run["dir"] / rel).read_bytes()


def test_the_bundled_datasheet_checksums_the_bundled_files(bundled_run):
    """The app ran a temporary copy of the design with absolute paths and then
    bundled the displayed design, so the datasheet's design checksum matched no file
    in the bundle. Pinned identically in test-apps.R."""
    base = bundled_run["bundle"]["base"]
    record = json.loads(_bundled(bundled_run, f"output/reports/{base}_datasheet_py.json"))
    repro = record["reproducibility"]
    assert repro["design_sha256"] == _sha256(_bundled(bundled_run, "my_design.yaml"))
    assert repro["schema_path"] == "config/schema.yaml"
    assert repro["schema_sha256"] == _sha256(_bundled(bundled_run, "config/schema.yaml"))
    source = record["materials_source"]
    assert source["path"] == "corpora/derived/en_v2.csv"
    assert source["sha256"] == _sha256(_bundled(bundled_run, source["path"]))
    assert record["items"]["stimuli_file"] == f"output/stimuli/{base}_stimuli_py.csv"
    files = [a["file"] for a in record["artifacts"]]
    assert files and all(f.startswith("output/") for f in files)
    for artefact in record["artifacts"]:
        assert artefact["sha256"] == _sha256(_bundled(bundled_run, artefact["file"]))


def _strings(value):
    if isinstance(value, dict):
        for v in value.values():
            yield from _strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from _strings(v)
    elif isinstance(value, str):
        yield value


ABSOLUTE = re.compile(r"^([A-Za-z]:[\\/]|[\\/]|~)")


def test_no_path_in_the_datasheet_or_run_logs_is_absolute(app, bundled_run):
    """The datasheet and run logs named the user's home and temporary directories."""
    base = bundled_run["bundle"]["base"]
    reports = bundled_run["dir"] / "output" / "reports"
    record = json.loads((reports / f"{base}_datasheet_py.json").read_text(encoding="utf-8"))
    assert [s for s in _strings(record) if ABSOLUTE.match(s)] == []
    for line in (reports / f"{base}_run_log_py.jsonl").read_text(encoding="utf-8").splitlines():
        assert [s for s in _strings(json.loads(line)) if ABSOLUTE.match(s)] == []
    places = {bundled_run["bundle"]["root"], tempfile.gettempdir(), os.path.expanduser("~"),
              app.REPO_ROOT}
    # A home directory of "/" would match every path, so a lone separator is dropped.
    needles = {n for n in {p.replace("\\", "/") for p in places} | places if len(n) > 1}
    for name in (f"{base}_datasheet_py.json", f"{base}_datasheet_py.md",
                 f"{base}_run_log_py.md", f"{base}_run_log_py.jsonl"):
        text = (reports / name).read_text(encoding="utf-8")
        assert [n for n in needles if n in text] == [], name


def test_the_exported_code_reproduces_the_bundle(app, bundled_run, monkeypatch):
    """Running the exported Python code from the unzipped bundle rewrites every output
    with the same bytes. The run logs record the time of the run, so they differ."""
    shipped = {name: data for name, data in _contents(bundled_run["payload"]).items()
               if name.startswith("output/") and "_run_log_" not in name}
    code = app.reproduction_code(bundled_run["design"], "my_design.yaml")["python"]
    monkeypatch.chdir(bundled_run["dir"])
    exec(compile(code, "<exported>", "exec"), {})
    rerun = {}
    for d, _dirs, files in os.walk(bundled_run["dir"] / "output"):
        for f in files:
            rel = os.path.relpath(os.path.join(d, f), bundled_run["dir"]).replace(os.sep, "/")
            if "_run_log_" not in rel:
                with open(os.path.join(d, f), "rb") as handle:
                    rerun[rel] = handle.read()
    assert sorted(rerun) == sorted(shipped)
    assert [name for name in shipped if rerun[name] != shipped[name]] == []


def test_the_experiment_downloads_hold_the_tables_the_experiments_load(app, bundled_run):
    bundle = bundled_run["bundle"]
    base = bundle["base"]
    groups = app.experiment_downloads(app.experiment_files(bundle["paths"]["experiments"]), base)
    assert [g["file_name"] for g in groups] == [f"{base}_psychopy.zip", f"{base}_opensesame.zip",
                                                f"{base}.html"]
    psychopy, opensesame, jspsych = (app.experiment_payload(g) for g in groups)
    assert _names(psychopy) == [f"{base}_psychopy.csv", f"{base}_psychopy.py"]
    assert _names(opensesame) == [f"{base}.osexp", f"{base}_opensesame.csv",
                                  f"{base}_opensesame_text.csv"]
    assert jspsych == _bundled(bundled_run, f"output/experiments/{base}.html")
    # The script loads the table it names, which now sits beside it.
    script = _contents(psychopy)[f"{base}_psychopy.py"].decode("utf-8")
    assert f"{base}_psychopy.csv" in script


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
    lexicon = os.path.join(app.REPO_ROOT, "corpora", "derived", "en_v2.csv")
    if not os.path.exists(lexicon):
        pytest.skip("The bundled corpora are not in this tree.")
    design = _factorial_design("mahalanobis")
    bundle = app.run_design(design, "my_design.yaml", app.staged_inputs(design, lexicon, None))
    try:
        record = bundle["record"]
        assert record["selection"]["cross_engine"].startswith("approximate")
        assert app.parity_claim(record) == APPROXIMATE
        assert app.interval_label(record) == "90% CI"
    finally:
        shutil.rmtree(bundle["root"], ignore_errors=True)


def test_a_refused_design_reports_the_pipeline_message(app, monkeypatch):
    """The run is a separate process now, so its refusal reaches the page as the
    pipeline's own message, and its directory goes with it."""
    lexicon = os.path.join(app.REPO_ROOT, "corpora", "derived", "en_v2.csv")
    if not os.path.exists(lexicon):
        pytest.skip("The bundled corpora are not in this tree.")
    design = dict(_factorial_design(), match_on=[])
    made = _recording_mkdtemp(monkeypatch, app)
    with pytest.raises(RuntimeError, match=r"^lexsync: "):
        app.run_design(design, "my_design.yaml", app.staged_inputs(design, lexicon, None))
    assert len(made) == 1
    assert not os.path.exists(made[0])


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


def test_a_new_run_discards_the_previous_run_directory():
    """Every run leaves a directory holding a copy of its inputs and every output, and
    a long-lived app kept one per press of Run. Only the run on screen is read from."""
    at = _app_test()
    if not os.path.isdir(os.path.join(REPO, "corpora", "derived")):
        pytest.skip("The bundled corpora are not in this tree.")
    roots = []
    for _ in range(2):
        [button for button in at.button if "Run design" in button.label][0].click().run()
        assert not at.exception
        assert [e.value for e in at.error] == []
        roots.append(at.session_state["bundle"]["root"])
    try:
        assert roots[0] != roots[1]
        assert not os.path.exists(roots[0])
        assert os.path.isdir(roots[1])
    finally:
        for root in roots:
            shutil.rmtree(root, ignore_errors=True)


# The notes on the Experiment scripts and Download tabs. Pinned identically in
# test-apps.R.
EXPERIMENT_NOTE = ("The same matched stimuli compile to three presentation targets. The PsychoPy "
                   "and OpenSesame downloads are archives that hold each experiment with the "
                   "tables it reads, so unzip one and run the experiment from that folder. The "
                   "jsPsych page holds its trials and runs on its own.")
DOWNLOAD_NOTE = ("The bundle is the folder the run ran in: the design, the schema at "
                 "config/schema.yaml, the lexicon or item table at the path the design names "
                 "and every output under output/. Running the exported code inside the unzipped "
                 "folder repeats the run.")


def test_both_apps_word_the_download_notes_alike(app):
    assert (app.EXPERIMENT_NOTE, app.DOWNLOAD_NOTE) == (EXPERIMENT_NOTE, DOWNLOAD_NOTE)
    for path, joined in _joined_sources().items():
        assert EXPERIMENT_NOTE in joined, path
        assert DOWNLOAD_NOTE in joined, path
        assert "so download them together" not in joined, path
