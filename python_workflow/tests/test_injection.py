"""A design file must not be able to execute code on the machine that runs it.

A design is meant to be shared: posted with a pre-registration, attached to a paper,
handed to a collaborator running the other engine. The recipient runs it and opens the
generated PsychoPy script, OpenSesame experiment or jsPsych page -- which is the only
thing those files are for. Every value the design controls therefore has to stay data.

Stimulus text always did: it travels in the loop-table CSV the experiment reads at run
time. Design METADATA did not. The name, language label, font, parallel-port address
and the column names on jitter and feedback events were substituted straight into code
and markup positions, so a quote or an angle bracket there stopped being text.

Mirrors test-injection.R. Both suites assert refusal rather than escaping: see
clean_meta in io_utils for why one rule beats three escapes across two engines.
"""
from importlib.resources import files

import pandas as pd
import pytest
import yaml

from lexsync.scripting import _language_tag, _pyq, export_jspsych, export_opensesame, export_psychopy


@pytest.fixture
def schema():
    return yaml.safe_load(
        (files("lexsync") / "data" / "schema.yaml").read_text(encoding="utf-8"))


def _design(**over):
    d = {"name": "inj", "language": "english", "timing": {}}
    d.update(over)
    return d


def _stim():
    return pd.DataFrame({
        "word": ["alpha", "beta"], "condition": ["a", "b"], "item": [1, 2],
        "set": [1, 2], "list": [1, 1], "trial": [1, 2],
    })


# Payloads that ended a string literal, a tag or a CSS rule in the generated file.
PAYLOADS = [
    'x"""; __import__("os").system("calc"); """',   # PsychoPy docstring
    "x'; __import__('os').system('calc'); #",       # single-quoted literal
    '</title><script>alert(1)</script>',            # jsPsych title
    'Courier New"; } body { background: url(//e.invalid) } .z {',  # CSS rule
    'x`+fetch("//e.invalid")+`',                    # JS template literal
    "x<img src=x onerror=alert(1)>",                # HTML attribute
    "x&amp;y",                                      # entity
]


@pytest.mark.parametrize("payload", PAYLOADS)
@pytest.mark.parametrize("field", ["name", "language", "font"])
def test_a_design_cannot_inject_through_its_metadata(payload, field, schema, tmp_path):
    design = _design(**{field: payload})
    for export in (export_psychopy, export_jspsych, export_opensesame):
        with pytest.raises(ValueError, match="cannot be written safely"):
            export(_stim(), design, schema, str(tmp_path))


def test_the_parallel_port_address_must_be_an_address(schema, tmp_path):
    # It is written into `TRIGGER_ADDRESS = {{...}}` and `var.parallel_port_address = ...`
    # with no quotes at all, so anything that is not a number is a statement.
    bad = dict(schema)
    bad["triggers"] = dict(schema.get("triggers") or {},
                           parallel_address='0x378; __import__("os").system("calc")')
    with pytest.raises(ValueError, match="must be a port address"):
        export_psychopy(_stim(), _design(), bad, str(tmp_path))
    for good in ("0x0378", "0x378", "888"):
        ok = dict(schema)
        ok["triggers"] = dict(schema.get("triggers") or {}, parallel_address=good)
        export_psychopy(_stim(), _design(), ok, str(tmp_path))


def test_event_column_names_must_be_identifiers(schema, tmp_path):
    # `as:` on a jittered duration and `answer:` on a feedback event both become a
    # variable reference in the emitted OpenSesame Python.
    payload = "ans'); __import__('os').system('calc'); ('"
    design = _design(events=[
        {"type": "text", "content": "{word}", "duration_ms": 100},
        {"type": "response", "keys": ["f", "j"], "timeout_ms": 500},
        {"type": "feedback", "answer": payload, "duration_ms": 100},
    ])
    with pytest.raises(ValueError, match="must be a plain column name"):
        export_opensesame(_stim(), design, schema, str(tmp_path))


def test_a_stated_language_tag_is_shape_checked():
    # It used to be returned verbatim into the generated page's lang attribute.
    assert _language_tag({"language_tag": 'en"><script>alert(1)</script>'}) == "und"
    assert _language_tag({"language_tag": "en-GB"}) == "en-GB"
    assert _language_tag({"language": "english"}) == "en"


def test_pyq_escapes_a_newline():
    # An .osexp is line-oriented: a raw newline closed the inline-script block and let
    # the rest of the value start a new top-level item in the emitted experiment.
    assert "\n" not in _pyq("a\nb")
    assert _pyq("a\nb") == r"u'a\nb'"
    assert _pyq("a\r\tb") == r"u'a\r\tb'"


def test_legitimate_metadata_still_passes(schema, tmp_path):
    # The guard must not cost a real design anything: these are the values the shipped
    # designs actually use, including the Chinese font and an accented label.
    for name, language, font in [
        ("en_lexdec", "english", "Courier New"),
        ("zh_freqcontrast", "chinese", "SimHei"),
        ("es_gender_repro", "español", "Courier New"),
        ("a-design_1.0 (v2)", "British English", "DejaVu Sans Mono"),
    ]:
        design = _design(name=name, language=language, font=font)
        export_psychopy(_stim(), design, schema, str(tmp_path))
        export_jspsych(_stim(), design, schema, str(tmp_path))


# ---- Bypasses found by adversarially attacking the first version of the guards ----


def test_a_response_key_cannot_inject_osexp_items(schema, tmp_path):
    """The guards' biggest miss, found independently by three reviewers.

    OpenSesame takes the keys as `set allowed_responses "a;b"` on ONE line of a
    line-oriented format. A key holding a double quote closed that string and a newline
    ended the line, so the rest of the value became new top-level items -- including an
    `inline_script` whose ___run__ body OpenSesame executes.
    """
    payload = ('j"\n\ndefine inline_script lexsync_pwned\n\tset _prepare ""\n'
               "\t___run__\n\t__import__('os').system('calc')\n\t__end__\n"
               'define sequence dummy\n\tset x "')
    design = _design(events=[
        {"type": "text", "content": "{word}", "duration_ms": 100},
        {"type": "response", "keys": ["f", payload], "timeout_ms": 500},
    ])
    for export in (export_psychopy, export_jspsych, export_opensesame):
        with pytest.raises(ValueError, match="must be a key name"):
            export(_stim(), design, schema, str(tmp_path))


@pytest.mark.parametrize("bad", ['f"', "f\n", "f;j", "f'", "f<", "", "x" * 21])
def test_key_shapes_that_must_be_refused(bad):
    from lexsync.io_utils import clean_key
    with pytest.raises(ValueError):
        clean_key(bad)


@pytest.mark.parametrize("good", ["f", "j", "space", "left", "arrowleft", "num_1", "a b"])
def test_key_shapes_that_must_pass(good):
    from lexsync.io_utils import clean_key
    assert clean_key(good) == good


def test_a_trailing_newline_does_not_slip_past_the_shape_guards():
    r"""`$` also matches just BEFORE a final newline, in Python's re and in R's PCRE
    alike, so "888\n" and "iti_ms\n" satisfied a `$`-anchored check and carried a
    newline into a line-oriented .osexp. The anchors are \Z / \z now."""
    from lexsync.io_utils import clean_column, clean_port
    for bad in ("888\n", "0x378\n"):
        with pytest.raises(ValueError):
            clean_port(bad)
    for bad in ("iti_ms\n", "answer\n"):
        with pytest.raises(ValueError):
            clean_column(bad)
    assert clean_port("888") == "888"
    assert clean_column("iti_ms") == "iti_ms"


def test_a_scalar_keys_or_blocks_is_not_exploded_into_characters(schema):
    """YAML allows `keys: space` and `blocks: practice` as scalars. Python's list() then
    made five one-character keys where R kept the string whole, so one design produced
    two different allowed-response lists -- and a scalar `blocks:` made the OpenSesame
    guard compare against "p", "r", ... so the event ran in every block in Python and
    only the named one in R."""
    from lexsync.paradigms import resolve_events
    from lexsync.scripting import render_events
    design = _design(events=[
        {"type": "text", "content": "{word}", "duration_ms": 100},
        {"type": "response", "keys": "space", "timeout_ms": 500},
        {"type": "feedback", "answer": "answer", "blocks": "practice",
         "duration_ms": 100},
    ])
    rendered = render_events(resolve_events(design), {}, 60.0)
    assert rendered[1]["keys"] == ["space"]
    assert rendered[2]["blocks"] == ["practice"]


def test_the_html_escape_covers_the_javascript_line_separators():
    """U+2028 and U+2029 end a line in JavaScript but are not ASCII controls, so
    clean_field passes them. Python escaped them and R did not, so the same design
    produced different bytes and R's <script> was a SyntaxError before ES2019."""
    from lexsync.scripting import _json_html
    out = _json_html({"w": "a\u2028b\u2029c"})
    assert "\u2028" not in out and "\u2029" not in out   # no raw separator survives
    assert r"\u2028" in out and r"\u2029" in out          # both arrive escaped
