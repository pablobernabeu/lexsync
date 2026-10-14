"""Lexical-decision generation with accented letters, and the refusal of logographic scripts.

The generators substituted only the letters a to z and left out every word holding any
other letter. A Spanish lexical decision lost 16.5% of a typical band (1,368 of 8,305
words, among them 261 preterites in -ó) and could never produce an accented pseudoword.
Their alphabet is now the set of letters the reference lexicon attests, in UTF-8 byte
order. Chinese is refused, since its characters are letters to Unicode but a form made by
swapping one character for another is of unknown validity as a pseudoword.
R_workflow/tests/testthat/test-generation-accents.R holds the R engine to the same tests,
by the same names.
"""
import json
import os

import pandas as pd
import pytest
import yaml
from helper_repo import REPO

import lexsync
from lexsync.generation import (
    _lexdec_eligible,
    _reference_alphabet,
    build_lexdec_stimuli,
    generate_pseudowords,
    generate_pseudowords_subsyllabic,
    segment_subsyllabic,
)
from lexsync.run_pipeline import run_pipeline

# Common Spanish words, nine of them accented.
ES = ["agua", "avión", "árbol", "café", "calle", "camión", "campo", "canción", "casa",
      "cielo", "ciudad", "fuego", "gato", "lápiz", "libro", "luna", "mañana", "mesa",
      "montaña", "mundo", "niño", "noche", "papel", "perro", "playa", "puerta", "silla",
      "tierra", "ventana"]
ES_POOL = pd.DataFrame({"word": ES, "length": [len(w) for w in ES]})


def _data(name):
    return os.path.join(os.path.dirname(lexsync.__file__), "data", name)


def test_the_alphabet_is_the_set_of_letters_the_reference_attests():
    # Letters only, so the hyphen of e-mail is left out, in UTF-8 byte order, so the
    # accented letters follow z.
    got = _reference_alphabet(["canción", "año", "e-mail", "pingüino"])
    assert got == ["a", "c", "e", "g", "i", "l", "m", "n", "o", "p", "ñ", "ó", "ü"]


def test_a_substitution_may_use_an_accented_letter_the_reference_attests():
    # The only legal substitution in 'tas' is an ó, which the a-z alphabet lacked, so
    # the generator found no candidate at all and refused the word.
    got = generate_pseudowords(["tas"], ["tó", "ós", "to"])
    assert got["pseudoword"].tolist() == ["tós"]


def test_build_lexdec_stimuli_keeps_accented_base_words():
    stim = build_lexdec_stimuli(ES_POOL, 8, reference_words=ES)
    words = stim.loc[stim["condition"] == "word", "target"].tolist()
    pseudo = stim.loc[stim["condition"] == "pseudoword", "target"].tolist()
    # The even spread over the byte-ordered pool reaches árbol, past z, and camión
    # keeps its accent in its pseudoword.
    assert words == ["agua", "camión", "cielo", "libro", "mesa", "noche", "puerta", "árbol"]
    assert pseudo == ["ague", "canión", "ciero", "liero", "iesa", "nocie", "fuerta", "erbol"]
    # The pool holds nothing but letters the reference attests, so every word is
    # eligible.
    assert len(_lexdec_eligible(ES_POOL, ES)) == len(ES)


def test_the_subsyllabic_segmenter_reads_accented_letters():
    assert segment_subsyllabic("canción") == [
        ("onset", "c"), ("nucleus", "a"), ("coda", "n"), ("onset", "c"),
        ("nucleus", "ió"), ("coda", "n")]
    assert segment_subsyllabic("pingüino") == [
        ("onset", "p"), ("nucleus", "i"), ("coda", "n"), ("onset", "g"),
        ("nucleus", "üi"), ("onset", "n"), ("nucleus", "o")]
    assert segment_subsyllabic("año") == [("nucleus", "a"), ("onset", "ñ"), ("nucleus", "o")]
    assert segment_subsyllabic("Canción") == segment_subsyllabic("canción")
    # A word with a character that is not a letter has no segments, nor has a word with
    # no Latin vowel, so both go to letter substitution.
    assert segment_subsyllabic("e-mail") == []
    assert segment_subsyllabic("молоко") == []


def test_the_subsyllabic_generator_keeps_accented_words():
    # Each word is segmented, so whole constituents are swapped and montaña's ñ stays
    # in its pseudoword. The a-z segmenter returned nothing for all three, which sent
    # them to letter substitution.
    got = generate_pseudowords_subsyllabic(["canción", "camión", "montaña"], ES)
    assert got["pseudoword"].tolist() == ["cancien", "namuan", "cantiño"]


def test_a_logographic_lexicon_is_refused():
    message = "pseudoword generation is defined for alphabetic scripts"
    zh = pd.read_csv(_data("zh_example.csv"), dtype={"word": str}, encoding="utf-8")
    zh["length"] = zh["word"].str.len()
    with pytest.raises(ValueError, match=message):
        build_lexdec_stimuli(zh, 4, reference_words=zh["word"].tolist())
    with pytest.raises(ValueError, match=message):
        generate_pseudowords(["中文"], ["中文", "汉字"])
    with pytest.raises(ValueError, match=message):
        generate_pseudowords_subsyllabic(["中文"], ["中文", "汉字"])


def test_a_generated_design_on_a_logographic_lexicon_is_refused(tmp_path):
    design = {"name": "zh_lexdec", "language": "chinese", "paradigm": "lexical_decision",
              "items": {"source": "generate",
                        "lexicon": _data("zh_example.csv").replace("\\", "/")},
              "n_per_condition": 4, "pool_filters": {"length": [2, 2]}}
    path = tmp_path / "design.yaml"
    path.write_text(yaml.safe_dump(design, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match="pseudoword generation is defined for alphabetic "
                                         "scripts, and '.+' is written in a logographic one"):
        run_pipeline(str(path), _data("schema.yaml"), str(tmp_path / "out"), verbose=False)


# The Spanish demonstration, read from the repository's committed outputs.
needs_repo = pytest.mark.skipif(REPO is None, reason="the demonstrations live in the repository")


@needs_repo
def test_the_spanish_demonstration_keeps_accented_words_and_avoids_known_forms():
    with open(REPO / "config" / "design_es_lexdec.yaml", encoding="utf-8") as handle:
        design = yaml.safe_load(handle)
    known_path = "corpora/derived/es_known_forms.txt"
    assert design["items"]["generation"]["exclude"] == [known_path]
    s = pd.read_csv(REPO / "output" / "stimuli" / "es_lexdec_spanish_stimuli_py.csv",
                    dtype=str, keep_default_na=False, encoding="utf-8")
    words = s.loc[s["condition"] == "word", "word"].tolist()
    pseudo = s.loc[s["condition"] == "pseudoword", "word"].tolist()
    assert len(words) == len(pseudo) == design["n_per_condition"]
    assert any(not w.isascii() for w in words)
    assert any(not p.isascii() for p in pseudo)
    with open(REPO / known_path, encoding="utf-8") as handle:
        known = set(handle.read().split("\n"))
    assert not set(pseudo) & known, sorted(set(pseudo) & known)
    with open(REPO / "output" / "reports" / "es_lexdec_spanish_datasheet_py.json",
              encoding="utf-8") as handle:
        ds = json.load(handle)
    # Every word in the band is written in letters es.csv attests, so the record counts
    # the whole band, accented words included.
    lex = pd.read_csv(REPO / "corpora" / "derived" / "es.csv", dtype={"word": str},
                      keep_default_na=False, encoding="utf-8")
    lo, hi = design["pool_filters"]["length"]
    flo, fhi = design["pool_filters"]["frequency"]
    band = lex[lex["word"].str.len().between(lo, hi) & lex["freq_zipf"].between(flo, fhi)]
    assert ds["selection"]["candidate_pool"] == [
        {"condition": "words in band", "n_candidates": len(band)}]
