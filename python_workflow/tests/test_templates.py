"""The experiment templates are mirrored into both packages; the mirrors must match.

templates/ at the repository root is the canonical copy. Both packages carry their
own so an installed copy can reach one without the repository: the Python package
under src/lexsync/templates/, the R package under inst/templates/, and each
resolves its own through find_template() / .lexsync_template().

Nothing enforced that the three agree, and no functional test can. A stale mirror
is still a perfectly valid template: it renders, it runs, and the experiment it
produces is simply not the one the repository documents. For the trigger
templates that is worse than an ordinary staleness bug, because what drifts is
the code that time-locks EEG markers to stimulus onset, and an experiment that
records the wrong onset does not fail, it quietly collects unusable data.

Comparing the bytes is the check that catches it. Twinned with
R_workflow/tests/testthat/test-templates.R,
which holds the R mirror to the same canonical copy. Both skip rather than fail
away from the repository, since an installed package checked in isolation has no
root templates/ to compare against. helper_repo.py, like helper-repo.R on the R
side, says why a directory named templates/ is not enough to go on.
"""

import os
import re
import sys
import types
from html.parser import HTMLParser

import pytest
from helper_repo import REPO

import lexsync

# None away from the repository, where every test below skips.
CANONICAL = os.path.join(REPO, "templates") if REPO else None
PACKAGED = os.path.join(os.path.dirname(lexsync.__file__), "templates")

pytestmark = pytest.mark.skipif(REPO is None, reason="repository templates not available")


def _tree(root):
    """Every file below ``root``, as paths relative to it, in a stable order."""
    out = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            full = os.path.join(dirpath, name)
            out.append(os.path.relpath(full, root).replace(os.sep, "/"))
    return sorted(out)


def _read(path):
    with open(path, "rb") as handle:
        return handle.read()


def test_the_packaged_mirror_holds_the_same_files_as_the_repository():
    canonical = _tree(CANONICAL)
    assert canonical, "no templates found in the repository copy"
    assert _tree(PACKAGED) == canonical


@pytest.mark.parametrize("relpath", _tree(CANONICAL) if CANONICAL else [])
def test_each_packaged_template_is_byte_identical_to_the_repository_copy(relpath):
    assert _read(os.path.join(PACKAGED, relpath)) == _read(os.path.join(CANONICAL, relpath))


def test_find_template_resolves_to_the_packaged_copy():
    """The mirror is what an installed package actually serves, so it is the copy
    worth pinning: find_template() prefers it over the working directory."""
    from lexsync.scripting import find_template

    for relpath in _tree(CANONICAL):
        resolved = find_template(relpath)
        assert os.path.exists(resolved)
        assert _read(resolved) == _read(os.path.join(CANONICAL, relpath))


class _Fetched(HTMLParser):
    """Every script and stylesheet a page loads over http or https, as (tag, address,
    attributes)."""

    def __init__(self):
        super().__init__()
        self.found = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        address = attrs.get("src") if tag == "script" else (
            attrs.get("href") if tag == "link" and attrs.get("rel") == "stylesheet" else None)
        if address and address.startswith(("http://", "https://")):
            self.found.append((tag, address, attrs))


def test_every_script_and_stylesheet_from_a_cdn_carries_its_integrity():
    """The jsPsych page loaded jsPsych, its keyboard plugin and its stylesheet from unpkg
    with no integrity attribute, so a copy altered on the CDN would run in the page that
    collects the participants' responses. Each tag now names its file in full and
    carries the file's SHA-384 and crossorigin="anonymous", without which a browser
    cannot check the hash of a file from another origin. Twinned with
    test-templates.R."""
    path = os.path.join(CANONICAL, "jspsych", "experiment_template.html")
    page = _Fetched()
    with open(path, encoding="utf-8") as handle:
        page.feed(handle.read())
    assert [(tag, address.rsplit(".", 1)[1]) for tag, address, _ in page.found] == [
        ("script", "js"), ("script", "js"), ("link", "css")]
    for _tag, address, attrs in page.found:
        assert re.fullmatch(r"sha384-[A-Za-z0-9+/]{64}", attrs.get("integrity") or ""), address
        assert attrs.get("crossorigin") == "anonymous", address
        # The file itself: a bare package address is answered with a redirect.
        assert re.search(r"@[0-9.]+/(dist|css)/[a-z.]+\.(js|css)\Z", address), address
    # The SHA-384 of each published file, which the files unpkg serves and the npm
    # registry's tarballs of these releases both give. A wrong hash would stop the page
    # from loading jsPsych at all.
    assert {address: attrs["integrity"] for _tag, address, attrs in page.found} == {
        "https://unpkg.com/jspsych@7.3.4/dist/index.browser.min.js":
            "sha384-XAUySaEe2MZZhTzbstOfwmVuzWlsblgOwTje2VO+r73k+MzUbgzn/AwQlxq7OdCi",
        "https://unpkg.com/@jspsych/plugin-html-keyboard-response@1.1.3/dist/"
        "index.browser.min.js":
            "sha384-dY7LWgOfoIq6dkJslZMW+KMzvwcrQwzIbqPqWm/vQdrc+2o69tyPWHsIZQUQ1NYi",
        "https://unpkg.com/jspsych@7.3.4/css/jspsych.css":
            "sha384-F1pvd1ZCaxuJalclhLrJj8A5LWkFVuFinaHeIgOZXnnCGt7HAbSPzTw7fO3qeJ8F",
    }


def test_the_opensesame_snippet_opens_the_serial_port_it_names(monkeypatch):
    """The snippet's serial branch opened the first port pyserial listed, at pyserial's
    default rate, and that port could be another device. It now opens the port named at
    its top, at the rate named there, as the generated setup opens the one the schema
    names. It is run here with its backend set to serial, in a stand-in for the inline
    script's namespace, with a fake pyserial that lists another port first. Twinned
    with test-templates.R."""
    opened = []

    class Serial:
        def __init__(self, port=None, baudrate=9600, **kwargs):
            opened.append((port, baudrate))

        def write(self, data):
            return len(data)

    serial = types.ModuleType("serial")
    tools = types.ModuleType("serial.tools")
    list_ports = types.ModuleType("serial.tools.list_ports")
    list_ports.comports = lambda: [types.SimpleNamespace(device="COM1"),
                                   types.SimpleNamespace(device="COM3")]
    serial.Serial, serial.tools, tools.list_ports = Serial, tools, list_ports
    for name, module in (("serial", serial), ("serial.tools", tools),
                         ("serial.tools.list_ports", list_ports)):
        monkeypatch.setitem(sys.modules, name, module)
    path = os.path.join(CANONICAL, "opensesame", "inline_trigger_setup.py")
    with open(path, encoding="utf-8") as handle:
        code = handle.read()
    serial_code = code.replace("var.trigger_backend = u'parallel'",
                               "var.trigger_backend = u'serial'")
    assert serial_code != code
    var = types.SimpleNamespace()
    exec(serial_code, {"var": var})
    assert opened == [("COM3", 115200)]
    assert (var.serial_port, var.serial_baudrate, var.test_mode) == ("COM3", 115200, "no")


def test_the_opensesame_snippet_sends_only_the_condition_code_at_onset():
    """The snippet for pasting into an existing experiment sent the item code and then,
    once that 10 ms pulse had ended, the condition code. The marker an ERP analysis
    epochs on therefore came at least 10 ms after the onset, and the stream held item
    codes that could equal a condition code. It is run here in a stand-in for the inline
    script's namespace, as OpenSesame would run it."""
    sent, slept = [], []

    class Var:
        word, item_trigger, condition_trigger, word_duration_ms = "cat", 45, 101, 500

    class Canvas:
        def text(self, text):
            pass

        def show(self):
            return 0.0

    class Clock:
        def sleep(self, ms):
            slept.append(ms)

    path = os.path.join(CANONICAL, "opensesame", "inline_send_triggers.py")
    with open(path, encoding="utf-8") as handle:
        exec(handle.read(), {"var": Var(), "Canvas": Canvas, "clock": Clock(),
                             "send_trigger": sent.append})
    assert sent == [101]
    assert slept == [500]
