"""The known-form lists must stay what `fetch_corpora.py --known-forms` writes.

`corpora/derived/<lang>_known_forms.txt` holds every form in wordfreq's large list at
Zipf 1.0 or above, for a design's `items.generation.exclude`. A generated pseudoword
is refused for equalling any of them, so the files decide which pseudowords such a
design produces, and the datasheet records their checksums. These tests hold the
committed files to their format and to the counts and checksums ATTRIBUTION.md
gives, and rebuild the English list from wordfreq when it is installed. Data checks
on repository files, so the R suite has no twin of them.
"""
import hashlib
import importlib.util
import re
import sys
import unicodedata

import pytest
from helper_repo import REPO

DERIVED = REPO / "corpora" / "derived" if REPO else None
LANGS = ("en", "es")
# Forms the reference lexica lack, which reached shipped or trial pseudowords.
WITNESSES = {"en": ("crier", "pall", "titer"), "es": ("renos", "esteras")}

pytestmark = pytest.mark.skipif(REPO is None,
                                reason="repository-only data; absent from an installed copy")


def _list(lang):
    path = DERIVED / f"{lang}_known_forms.txt"
    if not path.exists():
        pytest.fail(f"{path.name} is missing; run python corpora/fetch_corpora.py "
                    f"--known-forms {lang}")
    return path


@pytest.mark.parametrize("lang", LANGS)
def test_a_known_form_list_is_sorted_unique_nfc_and_lf(lang):
    data = _list(lang).read_bytes()
    assert b"\r" not in data and data.endswith(b"\n")
    forms = data.decode("utf-8").split("\n")[:-1]
    assert all(forms)
    assert forms == sorted(set(forms), key=lambda w: w.encode("utf-8"))
    assert all(unicodedata.normalize("NFC", w) == w == w.lower() for w in forms)
    assert all(w in forms for w in WITNESSES[lang])


@pytest.mark.parametrize("lang", LANGS)
def test_attribution_records_each_known_form_list(lang):
    path = _list(lang)
    data = path.read_bytes()
    text = (REPO / "corpora" / "ATTRIBUTION.md").read_text(encoding="utf-8")
    entry = re.search(r"\('%s'\)\*\*, (\d+) forms in `%s`, sha256 `([0-9a-f]{64})`"
                      % (lang, re.escape(path.name)), text)
    assert entry, f"ATTRIBUTION.md has no entry for {path.name}"
    assert int(entry.group(1)) == data.count(b"\n")
    assert entry.group(2) == hashlib.sha256(data).hexdigest()


def test_the_english_known_form_list_rebuilds_byte_for_byte():
    pytest.importorskip("wordfreq")
    pytest.importorskip("rapidfuzz")
    spec = importlib.util.spec_from_file_location(
        "fetch_corpora", REPO / "corpora" / "fetch_corpora.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    built = ("\n".join(module.known_forms("en")) + "\n").encode("utf-8")
    assert built == _list("en").read_bytes(), (
        "rebuild with python corpora/fetch_corpora.py --known-forms en")
