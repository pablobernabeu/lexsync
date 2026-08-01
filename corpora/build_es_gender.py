#!/usr/bin/env python3
"""Rebuild the gender-tagged Spanish lexicon from the derived Spanish corpus.

Usage:
    python corpora/build_es_gender.py            # rebuild and write
    python corpora/build_es_gender.py --check    # verify without writing

This writes ``corpora/derived/es_gender.csv``, the lexicon behind the
demonstration that reproduces the gender-assignment design of González Alonso et
al. (2025), configured in ``config/design_es_gender_repro.yaml``.

The file was previously produced ad hoc and committed with no script to
regenerate it, which left the only worked design in the repository whose input
could not be rebuilt from its source. This reconstructs it from
``corpora/derived/es.csv`` and reproduces the committed file exactly.

What it does
------------
Grammatical gender is approximated from the orthographic ending, not looked up
in a lexical database. Spanish nouns and adjectives ending in -a are tagged
feminine and those ending in -o masculine, which is the canonical pattern and
the one the reproduced design relies on. The original study used EsPal (Duchon
et al., 2013) for real lexical gender, so this is an approximation and words
whose ending misrepresents their gender are mislabelled: ``problema`` and
``mapa`` are masculine, ``mano`` and ``foto`` feminine, and all four are tagged
the wrong way here.

Frequencies and the neighbourhood measures are carried over from ``es.csv``
unchanged rather than recomputed. That is deliberate: Coltheart's N and OLD20 are
properties of a word within a reference lexicon, and the reference is the whole
Spanish lexicon, not the gender-bearing subset of it. Recomputing over the subset
would silently redefine both measures.

A KNOWN LIMITATION, preserved rather than fixed
-----------------------------------------------
Gerunds end in -o and are excluded, since a gerund carries no grammatical gender.
The exclusion tests the endings -ando, -endo and -yendo, and -endo is broader than
the gerund ending -iendo: it also removes thirteen ordinary words that are not
gerunds, among them the adjectives ``estupendo``, ``tremendo`` and ``horrendo``,
the nouns ``atuendo``, ``referendo`` and ``reverendo``, and the first-person
present verb forms ``aprendo``, ``comprendo``, ``pretendo``, ``prendo`` and
``vendo``.

Narrowing the test to -iendo would be the linguistically correct rule, but it
would add those thirteen words to the lexicon and so change the stimuli the
demonstration selects, the committed artefacts under output/, and the golden
files the cross-engine parity tests compare. This script therefore reproduces the
committed behaviour. Changing the rule is a deliberate decision that belongs with
regenerating the demonstration, not with restoring reproducibility.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "corpora" / "derived" / "es.csv"
TARGET = ROOT / "corpora" / "derived" / "es_gender.csv"

# Word-length bounds in characters, matching the bundled example slices.
MIN_LEN, MAX_LEN = 3, 12

# See the module docstring: -endo is deliberately broader than the gerund ending.
GERUND_ENDINGS = ("ando", "endo", "yendo")

GENDER_BY_ENDING = {"a": "feminine", "o": "masculine"}

SOURCE_NOTE = (
    "wordfreq (Speer 2022); gender by canonical -o/-a ending, gerunds excluded"
)


def read_lexicon(path: Path) -> pd.DataFrame:
    """Read a derived lexicon without letting pandas invent missing values.

    ``keep_default_na=False`` matters here: Spanish has the word 'nan', which the
    default NA handling turns into a null and then drops or breaks on. It is not
    in the gender subset, so this has never changed the output, but any script
    reading these files needs the same guard.
    """
    return pd.read_csv(path, encoding="utf-8", keep_default_na=False)


def build(lexicon: pd.DataFrame) -> pd.DataFrame:
    length = lexicon.word.str.len()
    selected = lexicon[
        lexicon.word.str.endswith(tuple(GENDER_BY_ENDING))
        & length.between(MIN_LEN, MAX_LEN)
        & ~lexicon.word.str.endswith(GERUND_ENDINGS)
    ].copy()
    selected["source"] = SOURCE_NOTE
    selected["gender"] = [GENDER_BY_ENDING[w[-1]] for w in selected.word]
    return selected.reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="compare against the committed file and exit non-zero on any difference")
    args = ap.parse_args()

    built = build(read_lexicon(SOURCE))

    if args.check:
        if not TARGET.exists():
            sys.exit(f"{TARGET} does not exist")
        committed = read_lexicon(TARGET)
        if built.equals(committed):
            print(f"[build_es_gender] OK: {len(built)} rows, identical to the committed file")
            return
        sys.exit(
            f"[build_es_gender] MISMATCH: built {len(built)} rows against "
            f"{len(committed)} committed. Columns equal: "
            f"{list(built.columns) == list(committed.columns)}."
        )

    # to_csv writes the file itself rather than going through write_text, which on
    # Windows opens in text mode and would translate every \n into \r\n. The
    # committed corpora are LF throughout, and so is the sibling fetch_corpora.py.
    built.to_csv(TARGET, index=False, encoding="utf-8", lineterminator="\n")
    counts = built.gender.value_counts().to_dict()
    print(f"[build_es_gender] wrote {TARGET.relative_to(ROOT)}: {len(built)} words "
          f"({counts.get('feminine', 0)} feminine, {counts.get('masculine', 0)} masculine)")


if __name__ == "__main__":
    main()
