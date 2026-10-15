#!/usr/bin/env python3
"""Build lexsync derived lexica from wordfreq, with N and OLD20 precomputed.

Usage:
    python corpora/fetch_corpora.py --languages en es --n-words 30000
    python corpora/fetch_corpora.py --languages zh --n-words 20000
    python corpora/fetch_corpora.py --known-forms en es
    python corpora/fetch_corpora.py --screen-en [--subtlex-us PATH]
    python corpora/fetch_corpora.py --slice-en

This ingestion step writes:
  corpora/derived/<lang>.csv                          full derived lexicon
  R_workflow/inst/extdata/<lang>_example.csv          bundled slice (length 3-9)
  python_workflow/src/lexsync/data/<lang>_example.csv bundled slice (length 3-9)
and (re)writes corpora/ATTRIBUTION.md. With --known-forms it writes
  corpora/derived/<lang>_known_forms.txt              every known form, one per line
instead, for a design's items.generation.exclude, and with --screen-en
  corpora/derived/en_v2.csv                           en.csv screened against SUBTLEX-US
Either builds no lexicon unless --languages is given too. These files stay in the
repository: neither package ships them. The English slices are the exception to the
first list: they are drawn from the forms en_v2.csv keeps, by --screen-en or by
--slice-en, which reads the committed en_v2.csv and needs no SUBTLEX-US.

The orthographic-neighbourhood variables (Coltheart's N and OLD20) are computed
openly here with rapidfuzz and stored in the derived files, so both the R and
Python pipelines read identical, inspectable values. The standalone
add_neighbourhood()/compute_dimensions() functions remain available for users
who supply their own raw lexica.

wordfreq blends up to eight domains of text per language, among them subtitle
corpora that draw in part on the SUBTLEX family. Its code is Apache-2.0 and its
data files are redistributable under CC BY-SA 4.0, which is therefore the
licence on everything this script writes; see LICENSE-DATA for the reasoning and
for the SUBTLEX credit that wordfreq's terms require. corpora/registry.yaml
lists the curated, individually citable SUBTLEX/openlexicon corpora that lexsync
also supports, which are separate resources a user loads directly rather than
the source of anything bundled here, apart from the screening columns that
--screen-en takes from SUBTLEX-US.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import re
import textwrap
import unicodedata
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import wordfreq
from rapidfuzz import process
from rapidfuzz.distance import Levenshtein

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "corpora" / "derived"
PACKAGE_DATA_DIRS = (
    ROOT / "R_workflow" / "inst" / "extdata",
    ROOT / "python_workflow" / "src" / "lexsync" / "data",
)

LANG_NAMES = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German",
    "nl": "Dutch", "it": "Italian", "pt": "Portuguese", "zh": "Chinese (Mandarin)",
    # Not a language but a derivative of 'es', built outside this script and
    # committed. It is named here so the generated attribution reads sensibly;
    # the hand-written region explains how it was derived.
    "es_gender": "Spanish, gender-tagged subset",
    # A derivative of 'en' that --screen-en builds (see screen_en below).
    "en_v2": "English, screened against SUBTLEX-US",
}
# Letters admitted per language (lower case, accents where relevant). For Chinese
# (a logographic script) the admitted forms are runs of CJK unified ideographs,
# and 'length' is therefore measured in characters rather than letters.
WORD_RE = {
    "default": re.compile(r"^[a-z]+$"),
    "es": re.compile(r"^[a-záéíóúüñ]+$"),
    "fr": re.compile(r"^[a-zàâäçéèêëîïôöùûüÿœæ]+$"),
    "de": re.compile(r"^[a-zäöüß]+$"),
    "pt": re.compile(r"^[a-záàâãçéêíóôõú]+$"),
    "it": re.compile(r"^[a-zàèéìíîòóùú]+$"),
    "nl": re.compile(r"^[a-zàäéëïóöü]+$"),
    "zh": re.compile(r"^[一-鿿]+$"),
}
# Word-length bounds (in characters) for the full lexicon and for the bundled
# example slice. Chinese words are short: two-character words dominate the
# language, so the demonstration draws on two- and three-character words.
LEN_BOUNDS = {"default": (2, 15), "zh": (2, 3)}
SLICE_LEN = {"default": (3, 9), "zh": (2, 3)}


def clean_words(lang: str, n_words: int, min_len: int = 2, max_len: int = 15) -> list[str]:
    """Return up to `n_words` cleaned forms by frequency, admitted by the script."""
    rx = WORD_RE.get(lang, WORD_RE["default"])
    out: list[str] = []
    for w in wordfreq.top_n_list(lang, n_words * 3):
        w = w.lower()
        if rx.match(w) and min_len <= len(w) <= max_len:
            out.append(w)
        if len(out) >= n_words:
            break
    return out


def neighbourhood(words: list[str], n_old: int = 20, chunk: int = 1000,
                  reference: list[str] | None = None):
    """Coltheart's N (same-length, single substitution) and OLD20 for `words`, measured
    against `reference`, by default the words themselves. Distances of 0 are skipped,
    so a word is never its own neighbour, whether or not the reference holds it."""
    ref = words if reference is None else reference
    ref_lengths = np.array([len(w) for w in ref])
    m = len(words)
    n_density = np.zeros(m, dtype=int)
    old = np.full(m, np.nan)
    for start in range(0, m, chunk):
        stop = min(start + chunk, m)
        block = process.cdist(
            words[start:stop], ref,
            scorer=Levenshtein.distance, dtype=np.uint16, workers=-1,
        )
        for r in range(stop - start):
            i = start + r
            row = block[r]
            # Same length + Levenshtein 1 implies a single substitution (Hamming 1).
            n_density[i] = int(np.sum((row == 1) & (ref_lengths == len(words[i]))))
            nz = row[row > 0]
            if nz.size:
                k = min(n_old, nz.size)
                old[i] = float(np.mean(np.partition(nz, k - 1)[:k]))
    return n_density, old


def build(lang: str, n_words: int) -> pd.DataFrame:
    lo, hi = LEN_BOUNDS.get(lang, LEN_BOUNDS["default"])
    words = clean_words(lang, n_words, min_len=lo, max_len=hi)
    zipf = [wordfreq.zipf_frequency(w, lang) for w in words]
    df = pd.DataFrame({
        "word": words,
        "freq_zipf": np.round(zipf, 3),
        "language": lang,
        "source": "wordfreq",
    })
    df = df[df.freq_zipf > 0].reset_index(drop=True)
    n_density, old = neighbourhood(df.word.tolist())
    df["n_density"] = n_density
    df["old20"] = np.round(old, 3)
    return df.sort_values("word").reset_index(drop=True)


def write_slice(df: pd.DataFrame, lang: str, target: int = 3000) -> int:
    """Write a small, frequency-stratified example slice for the packages.

    The full derived lexicon (corpora/derived/) is the realistic neighbourhood
    reference; the installed packages bundle only this compact slice for tests
    and examples, so they stay within distribution size limits.
    """
    lo, hi = SLICE_LEN.get(lang, SLICE_LEN["default"])
    sl = df[(df.word.str.len() >= lo) & (df.word.str.len() <= hi)].copy()
    if len(sl) > target:
        sl = sl.assign(_bin=pd.qcut(sl.freq_zipf, 10, labels=False, duplicates="drop"))
        per = max(1, target // max(1, sl["_bin"].nunique()))
        parts = []
        for _, g in sl.groupby("_bin"):
            g = g.sort_values("word")
            if len(g) > per:
                idx = np.unique(np.round(np.linspace(0, len(g) - 1, per)).astype(int))
                g = g.iloc[idx]
            parts.append(g)
        sl = pd.concat(parts).drop(columns="_bin")
    sl = sl.sort_values("word").reset_index(drop=True)
    for d in PACKAGE_DATA_DIRS:
        d.mkdir(parents=True, exist_ok=True)
        # LF on every platform, as git stores the slices: pandas otherwise ends lines
        # with os.linesep, and a rebuild on Windows would differ from the committed bytes.
        sl.to_csv(d / f"{lang}_example.csv", index=False, encoding="utf-8",
                  lineterminator="\n")
    return len(sl)


# Languages whose 'length' and neighbourhood measures are character-based rather
# than letter-based (logographic scripts).
CHAR_BASED = {"zh"}


# The known-form lists. The derived lexica stop at the 30,000th form, Zipf 2.95 in
# English and 3.11 in Spanish, so a generator that checks its pseudowords against the
# lexicon alone lets real low-frequency words through (crier, pall; renos, esteras).
# wordfreq's 'large' list goes much lower. Zipf 1.0 is one occurrence per hundred
# million words, near the floor of what its sources attest.
KNOWN_WORDLIST = "large"
KNOWN_MIN_ZIPF = 1.0
KNOWN_SUFFIX = "_known_forms.txt"


def known_forms(lang: str) -> list[str]:
    """Every form in wordfreq's 'large' list for `lang` at Zipf 1.0 or above that the
    language's WORD_RE admits, lower-cased and in Unicode NFC, without duplicates and
    in UTF-8 byte order (289,023 forms for English with wordfreq 3.1)."""
    if lang not in wordfreq.available_languages(KNOWN_WORDLIST):
        raise SystemExit(f"[fetch_corpora] wordfreq has no '{KNOWN_WORDLIST}' list for '{lang}'.")
    rx = WORD_RE.get(lang, WORD_RE["default"])
    out: set[str] = set()
    for w in wordfreq.iter_wordlist(lang, KNOWN_WORDLIST):
        if wordfreq.zipf_frequency(w, lang, wordlist=KNOWN_WORDLIST) < KNOWN_MIN_ZIPF:
            continue
        v = unicodedata.normalize("NFC", w.lower())
        if rx.match(v):
            out.add(v)
    return sorted(out, key=lambda s: s.encode("utf-8"))


def write_known_forms(lang: str) -> Path:
    """Write corpora/derived/<lang>_known_forms.txt: UTF-8, one form per line, LF."""
    path = DERIVED / f"{lang}{KNOWN_SUFFIX}"
    path.write_bytes(("\n".join(known_forms(lang)) + "\n").encode("utf-8"))
    return path


def known_forms_entry(lang: str, path: Path, date: str) -> str:
    data = path.read_bytes()
    n = data.decode("utf-8").count("\n")
    return (
        f"- **{LANG_NAMES.get(lang, lang)} ('{lang}')**, {n} forms in "
        f"`{path.name}`, sha256 `{hashlib.sha256(data).hexdigest()}`. Source: "
        f"wordfreq's '{KNOWN_WORDLIST}' list at Zipf {KNOWN_MIN_ZIPF:.1f} or above "
        f"(Speer, 2022; data CC BY-SA 4.0), retrieved {date}."
    )


# ---- The screened English lexicon (en_v2) ---------------------------------------
# en.csv keeps every wordfreq form that matches ^[a-z]+$ after lower-casing, so names,
# acronyms and internet forms are among its words and among each other's neighbours.
# cat has N = 32, counting caa, cbt, cdt and crt. Rebuilding en.csv would move every
# selection made from it, so the screen is a second file. en_v2.csv keeps en.csv's
# rows and adds columns from SUBTLEX-US (Brysbaert & New, 2009), which counts the uses
# of each word (FREQcount) and those that begin with a lower-case letter (FREQlow).
# openlexicon serves it under CC BY-SA 4.0. https://www.lexique.org fails the TLS
# hostname check, and the bare domain serves the same bytes.
SUBTLEX_US_URL = "https://lexique.org/databases/SUBTLEX-US/SUBTLEXus74286wordstextversion.tsv"
SUBTLEX_US_FILE = "SUBTLEXus74286wordstextversion.tsv"
SUBTLEX_US_SHA256 = "c5f86f065fc5d057fbf366433b8c5ca550aa7c24e128362dea4394f2b29c86e4"
RAW = ROOT / "corpora" / "raw"
# A form is marked nonstandard when SUBTLEX-US lacks it or when under a tenth of its
# uses begin with a lower-case letter, as with names and acronyms. A threshold of 0.5
# would mark words that often open a sentence: what, how, why, maybe, okay and yes
# all fall below it. This one marks the days, the months other than march and may,
# most nationality words, god, ok and tv too, and every form the 2009 corpus lacks,
# such as selfie, emoji and covid.
SCREEN_MAX_SHARE = 0.10
# Forms kept in the reference whatever the rule says. Each would be justified in the
# hand-written region of ATTRIBUTION.md, and there are none.
SCREEN_ALLOW: frozenset[str] = frozenset()


def subtlex_us(path: Path | None = None) -> Path:
    """The SUBTLEX-US word list, checked against its SHA-256.

    `path` names a copy already saved. Without it the copy in corpora/raw/ is used, and
    is downloaded there first when absent. corpora/raw/ is not committed. A file with
    other bytes is refused, because en_v2.csv could not then be reproduced from it.
    """
    target = RAW / SUBTLEX_US_FILE if path is None else Path(path)
    if path is None and not target.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        part = target.with_name(target.name + ".part")
        print(f"[fetch_corpora] downloading {SUBTLEX_US_URL} ...", flush=True)
        with urllib.request.urlopen(SUBTLEX_US_URL, timeout=120) as response:
            part.write_bytes(response.read())
        if hashlib.sha256(part.read_bytes()).hexdigest() != SUBTLEX_US_SHA256:
            part.unlink()
            raise SystemExit("[fetch_corpora] the SUBTLEX-US download does not have the "
                             f"SHA-256 {SUBTLEX_US_SHA256}; it was not kept.")
        part.replace(target)
    if not target.is_file():
        raise SystemExit(f"[fetch_corpora] no SUBTLEX-US file at {target}.")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    if digest != SUBTLEX_US_SHA256:
        raise SystemExit(f"[fetch_corpora] {target} has the SHA-256 {digest}, where "
                         f"SUBTLEX-US has {SUBTLEX_US_SHA256}.")
    return target


def read_subtlex_us(path: Path) -> dict[str, tuple[int, int]]:
    """FREQcount and FREQlow of every SUBTLEX-US entry, keyed by its lower-cased Word.

    The Word column spells an entry as it is mostly written ('What', 'I'), and its
    counts cover every spelling, so lower-casing gives each word one key.
    """
    lines = path.read_bytes().decode("utf-8").splitlines()
    header = lines[0].split("\t")
    word, count, low = (header.index(name) for name in ("Word", "FREQcount", "FREQlow"))
    out: dict[str, tuple[int, int]] = {}
    for line in lines[1:]:
        if not line:
            continue
        cells = line.split("\t")
        key = cells[word].lower()
        if key in out:
            raise SystemExit(f"[fetch_corpora] SUBTLEX-US lists '{key}' twice.")
        out[key] = (int(cells[count]), int(cells[low]))
    return out


def screen_en(tsv: Path, en: Path = DERIVED / "en.csv") -> bytes:
    """The bytes of en_v2.csv: the rows of en.csv screened against SUBTLEX-US.

    en.csv is read as text and its cells are copied unchanged, so the forms, the
    frequencies and the earlier N and OLD20 (as n_density_raw and old20_raw) are
    en.csv's to the byte. in_subtlex_us is 1 when SUBTLEX-US lists the form.
    lowercase_share is FREQlow / FREQcount to three places, and is empty for a form
    SUBTLEX-US lacks. nonstandard is 1 for a form SUBTLEX-US lacks or whose share is
    below SCREEN_MAX_SHARE, unless SCREEN_ALLOW lists it, and reference_member is
    1 - nonstandard. n_density and old20 are measured against the reference members
    only. The rule reads the share as written, so the flag and the column agree.
    """
    df = pd.read_csv(en, dtype=str, keep_default_na=False, encoding="utf-8")
    counts = read_subtlex_us(tsv)
    words = df["word"].tolist()
    share = np.round([counts[w][1] / counts[w][0] if w in counts else np.nan
                      for w in words], 3)
    marked = [int(w not in SCREEN_ALLOW and (w not in counts or s < SCREEN_MAX_SHARE))
              for w, s in zip(words, share, strict=True)]
    members = [w for w, m in zip(words, marked, strict=True) if not m]
    n_density, old = neighbourhood(words, reference=members)
    out = pd.DataFrame({
        "word": df["word"], "freq_zipf": df["freq_zipf"],
        "language": df["language"], "source": df["source"],
        "n_density": n_density, "old20": np.round(old, 3),
        "in_subtlex_us": [int(w in counts) for w in words],
        "lowercase_share": share,
        "nonstandard": marked,
        "reference_member": [1 - m for m in marked],
        "n_density_raw": df["n_density"], "old20_raw": df["old20"],
    })
    # LF on every platform: pandas otherwise ends lines with os.linesep.
    return out.to_csv(index=False, lineterminator="\n").encode("utf-8")


def write_screened_en(tsv: Path) -> Path:
    """Write corpora/derived/en_v2.csv, and print every marked form of up to three
    letters for review, since short forms are where names and acronyms crowd."""
    path = DERIVED / "en_v2.csv"
    path.write_bytes(screen_en(tsv))
    v2 = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")
    marked = v2["nonstandard"] == "1"
    absent = int((marked & (v2["in_subtlex_us"] == "0")).sum())
    print(f"  -> {path.name}: {len(v2)} forms, {int(marked.sum())} marked nonstandard "
          f"({absent} absent from SUBTLEX-US, {int(marked.sum()) - absent} rarely lower-case); "
          f"{int((~marked).sum())} in the neighbourhood reference", flush=True)
    short = sorted((w for w in v2.loc[marked, "word"] if len(w) <= 3),
                   key=lambda s: s.encode("utf-8"))
    print(f"  marked forms of three letters or fewer ({len(short)}):", flush=True)
    for line in textwrap.wrap(" ".join(short), 88):
        print("    " + line, flush=True)
    return path


# The English example slices both packages bundle. A slice of en.csv was a quarter names,
# acronyms and other forms the screen marks, and the examples and tests that read it
# selected them. The slices are now drawn from the forms en_v2.csv keeps, whose N and
# OLD20 count neighbours among those forms only.
SLICE_COLUMNS = ["word", "freq_zipf", "language", "source", "n_density", "old20"]


def screened_slice_rows(path: Path = DERIVED / "en_v2.csv") -> pd.DataFrame:
    """The rows of en_v2.csv that the screen keeps (nonstandard 0), in a slice's columns.

    The cells are read as text, so they are written back as en_v2.csv holds them. The
    frequency is the exception, since write_slice bins on it, and a Zipf value of three
    decimals reads back to the text it was read from.
    """
    v2 = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")
    kept = v2.loc[v2["nonstandard"] == "0", SLICE_COLUMNS].copy()
    kept["freq_zipf"] = kept["freq_zipf"].astype(float)
    return kept.reset_index(drop=True)


def write_screened_slice() -> int:
    """Write both packages' en_example.csv from the forms en_v2.csv keeps."""
    return write_slice(screened_slice_rows(), "en")


def recorded_dates(path: Path) -> dict[str, str]:
    """The retrieval date ATTRIBUTION.md records for each entry, keyed by its code
    ('en') or by its known-form file name ('en_known_forms.txt')."""
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"- \*\*.*\('([^']+)'\)\*\*, .*retrieved (\d{4}-\d{2}-\d{2})\.", line)
        if not m:
            continue
        known = re.search(r"`([^`]+" + re.escape(KNOWN_SUFFIX) + ")`", line)
        out[known.group(1) if known else m.group(1)] = m.group(2)
    return out


# A lexicon that a newer file replaces for new designs. It keeps its bytes, so designs
# written for it still select what they did.
SUPERSEDED = {"en": "en_v2"}


def attribution_entry(lang: str, df: pd.DataFrame, date: str) -> str:
    zmin, zmax = df.freq_zipf.min(), df.freq_zipf.max()
    unit = "over characters " if lang in CHAR_BASED else ""
    head = (f"- **{LANG_NAMES.get(lang, lang)} ('{lang}')**, {len(df)} words, "
            f"Zipf {zmin:.2f}-{zmax:.2f}. ")
    if "nonstandard" in df.columns:
        n_marked = int((df.nonstandard == 1).sum())
        return head + (
            f"Source: wordfreq (Speer, 2022; data CC BY-SA 4.0) screened against "
            f"SUBTLEX-US (Brysbaert & New, 2009; data CC BY-SA 4.0), retrieved {date}. "
            f"{n_marked} forms marked `nonstandard`, and N and OLD20 computed by lexsync "
            f"against the other {len(df) - n_marked}.")
    entry = head + (f"Source: wordfreq (Speer, 2022; data CC BY-SA 4.0), retrieved {date}. "
                    f"N and OLD20 computed {unit}by lexsync.")
    if lang in SUPERSEDED:
        entry += (f" Superseded by `{SUPERSEDED[lang]}.csv` for new designs, and kept "
                  f"unchanged so that earlier designs select what they selected.")
    return entry


HAND_START = "<!-- hand-written: start -->"
HAND_END = "<!-- hand-written: end -->"


def read_hand_written(path: Path) -> str:
    """Return the hand-maintained region of an existing ATTRIBUTION.md.

    Everything this script can derive from the data is regenerated, but the file
    also carries prose no script can reconstruct: the note on data currency, and
    the description of how es_gender was derived. Earlier versions rewrote the
    whole file, so any such prose was silently destroyed on the next run. The
    markers below fence the part that survives.
    """
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    start, end = text.find(HAND_START), text.find(HAND_END)
    if start == -1 or end == -1 or end < start:
        return ""
    return text[start + len(HAND_START):end].strip("\n")


def write_attribution(fresh_dates: dict[str, str]) -> None:
    """Regenerate ATTRIBUTION.md from *every* derived lexicon present.

    Scanning the derived directory (rather than only the languages built in the
    current run) keeps the attribution complete when languages are added one at a
    time. Languages built this run carry today's date, and the others keep the date
    this file already records for them. Only an entry it does not record yet falls
    back to the modification date of its derived file, which is a lower bound rather
    than the true retrieval date: a fresh checkout dates every file to the checkout,
    and anything that rewrites the file, such as adding a column, moves it forward.
    The known-form lists are dated the same way, by file name.

    The citations below are not decoration. wordfreq carries the SUBTLEX lists by
    permission on the condition that work derived from it credits their authors
    and keeps it clear that SUBTLEX is freely available, so these entries are a
    licence obligation inherited from the data. See LICENSE-DATA.
    """
    path = ROOT / "corpora" / "ATTRIBUTION.md"
    hand = read_hand_written(path)
    recorded = recorded_dates(path)

    def date_of(key: str, file: Path) -> str:
        return (fresh_dates.get(key) or recorded.get(key)
                or datetime.date.fromtimestamp(file.stat().st_mtime).isoformat())

    entries = []
    # The lexica screened against SUBTLEX-US, which is then a direct source too.
    screened = []
    for csv in sorted(DERIVED.glob("*.csv")):
        lang = csv.stem
        df = pd.read_csv(csv, encoding="utf-8")
        if "nonstandard" in df.columns:
            screened.append(f"`{csv.name}`")
        entries.append(attribution_entry(lang, df, date_of(lang, csv)))
    screened_files = " and ".join(screened)
    if screened:
        # The English slices are drawn from en_v2.csv (see write_screened_slice), so
        # SUBTLEX-US chose their rows as well.
        licence = textwrap.fill(
            "Lexical corpora used by lexsync, with their sources, licences and retrieval "
            "dates. The bundled derivatives come from wordfreq, whose data files are "
            "redistributable under CC BY-SA 4.0, and the screening columns of "
            f"{screened_files} from SUBTLEX-US, which openlexicon distributes under the "
            "same licence and which also chose the rows of the packages' English example "
            "slices, so the derivatives carry that licence too. See LICENSE-DATA for the "
            "full reasoning.", width=80) + "\n\n"
        registry_note = (
            "Those are loaded directly by a user, and none of them is the source of "
            "anything bundled here except SUBTLEX-US, which supplies the screening "
            f"columns of {screened_files} and chose the rows of the packages' English "
            "example slices.\n")
    else:
        licence = (
            "Lexical corpora used by lexsync, with their sources, licences and retrieval\n"
            "dates. The bundled derivatives come from wordfreq, whose data files are\n"
            "redistributable under CC BY-SA 4.0, so they carry that licence too. See\n"
            "LICENSE-DATA for the full reasoning.\n\n")
        registry_note = ("Those are loaded directly by a user and are not the source of "
                         "anything bundled here.\n")
    known = [known_forms_entry(txt.name[:-len(KNOWN_SUFFIX)], txt, date_of(txt.name, txt))
             for txt in sorted(DERIVED.glob(f"*{KNOWN_SUFFIX}"))]
    known_section = "" if not known else (
        "\n\n## Known-form lists (repository only)\n\n"
        "Each list holds every form in wordfreq's large list for a language at Zipf 1.0\n"
        "or above that the language's letters admit. `fetch_corpora.py --known-forms`\n"
        "writes them for a design's `items.generation.exclude`, so that a generated\n"
        "pseudoword cannot be a real word too rare for the lexicon. Neither package\n"
        "ships them.\n\n"
        + "\n".join(known))
    text = (
        "# Corpus attribution\n\n"
        + licence +
        "This file is regenerated by corpora/fetch_corpora.py. Edits outside the\n"
        "hand-written region below will not survive the next run.\n\n"
        "## Demonstration corpora (bundled)\n\n"
        + "\n".join(entries)
        + known_section
        + f"\n\n{HAND_START}\n{hand}\n{HAND_END}\n"
        + "\n## Citations\n\n"
        "- Speer, R. (2022). rspeer/wordfreq: v3.0. Zenodo. https://doi.org/10.5281/zenodo.7199437\n"
        "\nwordfreq's terms require that work derived from it credit the SUBTLEX authors\n"
        "and keep it clear that SUBTLEX is freely available data. The lists it carries\n"
        "are:\n\n"
        "- Brysbaert, M., & New, B. (2009). SUBTLEX-US. Behavior Research Methods, "
        "41(4), 977-990. https://doi.org/10.3758/BRM.41.4.977\n"
        "- van Heuven, W. J. B., Mandera, P., Keuleers, E., & Brysbaert, M. (2014). "
        "SUBTLEX-UK. Quarterly Journal of Experimental Psychology, 67(6), 1176-1190. "
        "https://doi.org/10.1080/17470218.2013.850521\n"
        "- Cai, Q., & Brysbaert, M. (2010). SUBTLEX-CH. PLoS ONE, 5(6), e10729. "
        "https://doi.org/10.1371/journal.pone.0010729\n"
        "- Brysbaert, M., Buchmeier, M., Conrad, M., Jacobs, A. M., Bölte, J., & "
        "Böhl, A. (2011). SUBTLEX-DE. Experimental Psychology, 58(5), 412-424. "
        "https://doi.org/10.1027/1618-3169/a000123\n"
        "- Keuleers, E., Brysbaert, M., & New, B. (2010). SUBTLEX-NL. Behavior "
        "Research Methods, 42(3), 643-650. https://doi.org/10.3758/BRM.42.3.643\n"
        "\n- See corpora/registry.yaml for the curated, individually citable "
        "SUBTLEX/openlexicon corpora that lexsync supports as separate resources. "
        + registry_note
    )
    # LF on every platform, as .gitattributes stores it.
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    ap = argparse.ArgumentParser(description="Build lexsync derived lexica.")
    ap.add_argument("--languages", nargs="+", default=None,
                    help="lexica to build (default: en es, unless --known-forms is given)")
    ap.add_argument("--n-words", type=int, default=10000)
    ap.add_argument("--known-forms", nargs="+", default=[], metavar="LANG",
                    help="write corpora/derived/<lang>_known_forms.txt for these languages")
    ap.add_argument("--screen-en", action="store_true",
                    help="write corpora/derived/en_v2.csv, en.csv screened against SUBTLEX-US")
    ap.add_argument("--subtlex-us", type=Path, default=None, metavar="PATH",
                    help="a copy of SUBTLEX-US's TSV for --screen-en (default: corpora/raw/, "
                         "downloaded when absent)")
    ap.add_argument("--slice-en", action="store_true",
                    help="write the packages' en_example.csv from the forms en_v2.csv keeps "
                         "(--screen-en does so too)")
    args = ap.parse_args()
    if args.subtlex_us is not None and not args.screen_en:
        ap.error("--subtlex-us is read only with --screen-en")
    languages = args.languages
    if languages is None:
        languages = ([] if (args.known_forms or args.screen_en or args.slice_en)
                     else ["en", "es"])

    DERIVED.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    fresh_dates: dict[str, str] = {}
    for lang in args.known_forms:
        print(f"[fetch_corpora] listing the known forms of '{lang}' ...", flush=True)
        out = write_known_forms(lang)
        n_forms = out.read_bytes().count(b"\n")
        print(f"  -> {out.name}: {n_forms} forms", flush=True)
        fresh_dates[out.name] = today
    for lang in languages:
        print(f"[fetch_corpora] building '{lang}' (target {args.n_words} words) ...", flush=True)
        df = build(lang, args.n_words)
        out = DERIVED / f"{lang}.csv"
        # LF on every platform: pandas would end each row with os.linesep, and the
        # datasheet of every run that reads this lexicon records the SHA-256 of its bytes.
        df.to_csv(out, index=False, encoding="utf-8", lineterminator="\n")
        zmin, zmax = df.freq_zipf.min(), df.freq_zipf.max()
        # A superseded lexicon no longer supplies the slices: the English ones come from
        # en_v2.csv, which --screen-en rebuilds from this file.
        if lang in SUPERSEDED:
            slice_note = f"slice drawn from {SUPERSEDED[lang]}.csv by --screen-en or --slice-en"
        else:
            slice_note = f"slice {write_slice(df, lang)}"
        print(f"  -> {out.name}: {len(df)} words (Zipf {zmin:.2f}-{zmax:.2f}); {slice_note}",
              flush=True)
        fresh_dates[lang] = today
    # After any rebuild of en.csv, which the screen reads.
    if args.screen_en:
        print("[fetch_corpora] screening 'en' against SUBTLEX-US ...", flush=True)
        write_screened_en(subtlex_us(args.subtlex_us))
        fresh_dates["en_v2"] = today
    if args.screen_en or args.slice_en:
        n_slice = write_screened_slice()
        print(f"  -> en_example.csv: {n_slice} of the forms en_v2.csv keeps", flush=True)
    # Regenerate the attribution from all derived lexica, so adding one language
    # never drops the others.
    write_attribution(fresh_dates)
    print("[fetch_corpora] done.", flush=True)


if __name__ == "__main__":
    main()
