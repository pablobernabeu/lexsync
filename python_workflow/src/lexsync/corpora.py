"""Access to the many-language corpus registry.

Mirrors R_workflow/R/corpora.R, and adds the wordfreq connector (Connector B,
thirty registered languages; wordfreq covers 42). The demonstrations read the
bundled, pre-derived lexica; new languages are fetched on demand into a user
cache, and normalise_lexicon turns a corpus file in its publisher's layout into a
lexicon load_lexicon reads.
"""
from __future__ import annotations

import contextlib
import os
import re
import shutil
import time
import unicodedata

import numpy as np
import pandas as pd
import yaml

from .io_utils import _exact_sum, _fmt_g, _type_column, read_csv_utf8, sha256_file, write_csv_utf8
from .querying import _check_zipf_range, _fold_words, _nfc, _require_numbers, _zipf_from_permillion


def _registry_path(registry_path: str | None = None) -> str:
    # A path the caller names is read on its own, and one that does not exist is an
    # error, so a misspelt or stale path never falls through to the checkout's registry
    # or the bundled one. Mirrors .registry_path in R_workflow/R/corpora.R.
    if registry_path is not None:
        if not os.path.exists(registry_path):
            raise FileNotFoundError(f"lexsync: registry not found: '{registry_path}'.")
        return registry_path
    candidates = [
        os.environ.get("LEXSYNC_REGISTRY"),
        os.path.join("corpora", "registry.yaml"),
        os.path.join("..", "corpora", "registry.yaml"),
        os.path.join(os.path.dirname(__file__), "data", "registry.yaml"),
    ]
    for cand in candidates:
        if cand and os.path.exists(cand):
            return cand
    raise FileNotFoundError("lexsync: could not locate 'registry.yaml'; set LEXSYNC_REGISTRY.")


def list_corpora(registry_path: str | None = None) -> pd.DataFrame:
    """The corpus registry as a table.

    Reads the registry at ``registry_path``, which must exist when given. Left as None,
    the registry is the first found of the file the environment variable
    ``LEXSYNC_REGISTRY`` names, ``corpora/registry.yaml`` in the working directory,
    ``../corpora/registry.yaml`` and the copy bundled with the package.

    Returns a DataFrame with one row per entry under ``corpora`` in the registry and the
    columns ``name``, ``language``, ``iso``, ``status``, ``connector`` (``openlexicon``
    when the entry names none) and ``citation``. The language codes of the wordfreq
    connector are not listed, and ``fetch_corpus`` takes them by code.

    Raises FileNotFoundError when a named registry does not exist or none is found.
    Mirrors list_corpora in R_workflow/R/corpora.R, whose search reads the
    ``lexsync.registry`` option in place of the environment variable.
    """
    with open(_registry_path(registry_path), encoding="utf-8") as handle:
        reg = yaml.safe_load(handle)
    rows = []
    for name, entry in (reg.get("corpora") or {}).items():
        lang = entry.get("language") or {}
        rows.append(dict(
            name=name, language=lang.get("name"), iso=lang.get("iso"),
            status=entry.get("status"), connector=entry.get("connector", "openlexicon"),
            citation=entry.get("citation"),
        ))
    return pd.DataFrame(rows)


def _check_corpus_name(name) -> None:
    """Refuse a corpus name that could reach a file outside the cache.

    The name becomes a file name inside the cache, so a path separator, or the colon
    of a Windows drive such as 'D:', would let it reach a file other than the corpus's
    own: os.path.join() drops the cache directory before a drive. All three characters
    are refused on every platform, so the two engines refuse the same names. Both
    cache_clear and fetch_corpus apply the rule, fetch_corpus before it reads the
    registry, since an edited registry may name an entry '../../escaped'. Mirrors
    .check_corpus_name in R_workflow/R/corpora.R.
    """
    if not isinstance(name, str) or not name or re.search(r"[/\\:]", name):
        raise ValueError("lexsync: 'name' must be a single corpus name, not a path.")


def cache_dir() -> str:
    """Per-user cache directory for fetched corpora.

    Where ``fetch_corpus`` puts what it fetches, and the only place the
    package writes to without being handed a path. This function only reports
    the path. The directory is created by the first fetch into it, so until then
    it does not exist.

    The cache persists between sessions. A registered corpus is a delimited word
    list, and a download is refused above 200 MB, so a cache holding several
    large corpora can reach a few hundred megabytes. Each fetch into the cache
    first deletes any partial download that an interrupted transfer left there
    more than a day earlier, and fetching a corpus again replaces the earlier
    copy. Fetched corpora otherwise stay until ``cache_clear`` removes them,
    one corpus at a time or all together. Nothing kept there is irreplaceable, so
    the next call downloads afresh. The R twin documents the same contract in
    lexsync_cache_dir.Rd; only the location differs, since R uses
    tools::R_user_dir.
    """
    return os.path.join(os.path.expanduser("~"), ".lexsync", "cache")


def cache_clear(name: str | None = None) -> list[str]:
    """Remove fetched corpora from the cache.

    Deletes what ``fetch_corpus`` put in ``cache_dir``. Given a `name`,
    that is the corpus's ``<name>.csv``, any ``<name>.csv.part`` that an
    interrupted download left behind and the ``<name>_wordfreq.csv`` lexicon the
    wordfreq connector builds. With `name` left as None it is the whole cache
    directory, and the ``~/.lexsync`` directory above it once nothing else is left
    there. A corpus needed again is fetched afresh by the next
    ``fetch_corpus`` call. Mirrors lexsync_cache_clear() in
    R_workflow/R/corpora.R, whose engine has no wordfreq connector and so no
    ``_wordfreq.csv`` to remove.

    Returns the paths of the files removed, empty when there was nothing to
    remove. Raises OSError, naming them, when files survive the attempt (one held
    open on Windows, say).
    """
    cache = cache_dir()
    if name is None:
        if not os.path.isdir(cache):
            return []
        removed = sorted(os.path.join(root, fname)
                         for root, _dirs, files in os.walk(cache) for fname in files)
        targets = [cache]
        # Keep going past a file that cannot be deleted, as R's unlink() does, and
        # report what survives below.
        shutil.rmtree(cache, ignore_errors=True)
    else:
        _check_corpus_name(name)
        targets = [os.path.join(cache, f"{name}{suffix}")
                   for suffix in (".csv", ".csv.part", "_wordfreq.csv")]
        removed = [path for path in targets if os.path.isfile(path)]
        for path in removed:
            with contextlib.suppress(OSError):
                os.remove(path)
    left = [path for path in (targets if name is None else removed)
            if os.path.exists(path)]
    if left:
        raise OSError(f"lexsync: could not remove {', '.join(left)} from the cache; "
                      f"check that no other process is using it.")
    if name is None:
        # ~/.lexsync holds nothing but the cache, so an emptied one would be left
        # behind in the user's home. rmdir() removes it only when it is empty. R's
        # twin has no such step: the parent of its cache directory is shared by
        # every R package's cache.
        with contextlib.suppress(OSError):
            os.rmdir(os.path.dirname(cache))
    return removed


def _prepare_cache() -> str:
    """Ready the cache for a fetch into it, and return its path.

    Mirrors .prepare_cache() in R_workflow/R/corpora.R. A '.part' sidecar
    outlives its fetch only when the transfer was cut short in a way
    fetch_corpus()'s handlers never see: a KeyboardInterrupt derives from
    BaseException, which neither except clause catches, and a process that dies
    runs no handler at all. A sidecar can also belong to a download still running
    in another process, which writes to it as it goes and gives up on a stalled
    server after 60 s. A day without a write therefore marks a sidecar as
    abandoned, and only those are deleted. A younger one is left to its download,
    and a retry of the same corpus truncates its own.
    """
    cache = cache_dir()
    os.makedirs(cache, exist_ok=True)
    cutoff = time.time() - _STALE_PART_SECONDS
    for fname in os.listdir(cache):
        if fname.endswith(".part"):
            path = os.path.join(cache, fname)
            # Best effort, as R's unlink() is: a sidecar that cannot be deleted
            # (held open on Windows, say), or that its download renamed away
            # meanwhile, must not stop the fetch that follows.
            with contextlib.suppress(OSError):
                if os.path.getmtime(path) < cutoff:
                    os.remove(path)
    return cache


# How long a sidecar may go unwritten before the sweep treats it as abandoned.
# Mirrors .stale_part_seconds() in R_workflow/R/corpora.R.
_STALE_PART_SECONDS = 24 * 60 * 60


# The characters other than letters and marks that may join two letters inside a word,
# by language, with the letter they must join on both sides where only one will do.
# Ukrainian and Belarusian spell words such as п'ять and ім'я with an apostrophe, written
# U+0027 by wordfreq and U+2019 or U+02BC by other sources, and Catalan writes its
# geminate l as l·l (pel·lícula). Elsewhere, an apostrophe joins a contraction, an
# elision or a clitic (don't, aujourd'hui, se'n), two words in one token, and the
# middle dot spells no word, so neither is admitted. wordfreq 3 has no Belarusian list
# and answers 'be' with its Russian one, in which the entry finds nothing to admit.
_APOSTROPHES = frozenset("'\N{RIGHT SINGLE QUOTATION MARK}\N{MODIFIER LETTER APOSTROPHE}")
_WORD_JOINERS = {
    "uk": (_APOSTROPHES, None),
    "be": (_APOSTROPHES, None),
    "ca": (frozenset("\N{MIDDLE DOT}"), "l"),
}
# Persian spells many words with the zero-width non-joiner, and Indic scripts choose a
# half form with the zero-width joiner. Unicode classes both as format characters, so
# the test for combining marks does not cover them.
_ZERO_WIDTH = frozenset("\N{ZERO WIDTH NON-JOINER}\N{ZERO WIDTH JOINER}")


def _is_letter(ch: str) -> bool:
    # U+02BC is a modifier letter by category, but it is written as an apostrophe and
    # treated as one, a joiner where the language admits one and a letter nowhere.
    return unicodedata.category(ch).startswith("L") and ch not in _APOSTROPHES


def _spelt_with_letters(word: str, language: str) -> bool:
    """Does `word`, lower-cased and in NFC, pass the connector's letter filter?

    The word must open with a letter. Every later character must be a letter, a
    combining mark or a zero-width (non-)joiner, or one of the language's
    word-internal joiners with a letter on each side (an l, for the Catalan middle
    dot). Python's word class, which the filter used, excludes combining marks and
    the zero-width characters, so it dropped most Hindi and Bengali words and every
    Persian form spelt with a non-joiner.
    """
    joiners, between = _WORD_JOINERS.get(language, (frozenset(), None))
    if not word or not _is_letter(word[0]):
        return False
    for i, ch in enumerate(word):
        if (_is_letter(ch) or ch in _ZERO_WIDTH
                or unicodedata.category(ch).startswith("M")):
            continue
        if ch in joiners and 0 < i < len(word) - 1:
            before, after = word[i - 1], word[i + 1]
            if between is None:
                if _is_letter(before) and _is_letter(after):
                    continue
            elif before == after == between:
                continue
        return False
    return True


def _has_latin_letter(word: str) -> bool:
    # The standard library has no script property, and the regex module that has one is
    # a dependency of wordfreq, which the tests' stand-in does without. A Latin letter
    # is taken to be a letter whose Unicode name has the word LATIN. That covers the
    # plain, accented, extended, small-capital and fullwidth forms. It misses the
    # superscript modifier letters, the ordinal indicators and a few letterlike symbols,
    # none of which spells a word.
    return any(unicodedata.category(ch).startswith("L")
               and "LATIN" in unicodedata.name(ch, "").split() for ch in word)


def build_wordfreq_lexicon(language: str, n_words: int = 10000,
                           min_len: int = 2, max_len: int = 15, *,
                           strict: bool = False,
                           exclude_latin: bool = False) -> pd.DataFrame:
    """Build a (word, freq_zipf) lexicon for any wordfreq language.

    Takes wordfreq's most frequent forms for `language`, lower-cased and in Unicode
    NFC, until `n_words` of them pass the letter filter and are `min_len` to
    `max_len` characters long. It looks no further than the first 3 * `n_words`
    forms. A form passes when it opens with a letter and every other character is a
    letter, a combining mark or a zero-width non-joiner or joiner. Hindi है and
    Bengali না, spelt with combining vowel signs, therefore pass, as do the many
    Persian forms spelt with a non-joiner. A Ukrainian or Belarusian form may also
    hold an apostrophe between two letters (п'ять), and a Catalan one a middle dot
    between two l's (pel·lícula). Digits never pass, and nor do underscores or any
    punctuation mark besides those joiners, so English contractions and French
    elisions stay out. Length counts code points, as the lexicon readers count it,
    so vowel signs, viramas and zero-width characters count. A form that wordfreq
    gives no frequency is dropped.

    When the lexicon holds fewer than `n_words` forms, a line on standard output says
    so, and with `strict` the shortfall raises ValueError. `exclude_latin` drops every
    form holding a Latin letter, such as the English tokens in the Hindi list. It is
    not a one-script rule, so a Japanese lexicon keeps its kana and kanji together,
    and it leaves nothing of a language written in the Latin alphabet.

    Raises ModuleNotFoundError if the optional [corpora] extra is not installed.
    """
    # Deferred because wordfreq belongs to the [corpora] extra, so importing it at
    # module scope would break `import lexsync` on a default install. Guarded because
    # this is what `lexsync fetch fr` reaches, and the README advertises that command:
    # unguarded, a default install answers it with a bare ModuleNotFoundError nine
    # frames down, which names the missing module and no way to get it. Everything
    # else in this module answers a failure with the remedy, and so does this.
    # The R twin has no counterpart here: Connector B is Python-only, and R/corpora.R
    # reads its pre-derived output as an ordinary lexicon.
    try:
        import wordfreq
    except ImportError as exc:
        raise ModuleNotFoundError(
            f"lexsync: building a lexicon for '{language}' needs the wordfreq connector, "
            f"which ships in the optional [corpora] extra and is not installed. Install "
            'it with: pip install "wordfreq>=3.0,<4".'
        ) from exc

    words: list[str] = []
    seen: set[str] = set()
    for token in wordfreq.top_n_list(language, n_words * 3):
        # NFC after lower-casing, the order in which load_lexicon normalises a word. A
        # form that wordfreq gives decomposed, as it gives some Greek ones, then keeps
        # its marks, is stored as the readers will key it and is kept only once.
        w = unicodedata.normalize("NFC", token.lower())
        if (w in seen or not min_len <= len(w) <= max_len
                or not _spelt_with_letters(w, language)
                or (exclude_latin and _has_latin_letter(w))):
            continue
        seen.add(w)
        words.append(w)
        if len(words) >= n_words:
            break
    zipf = [wordfreq.zipf_frequency(w, language) for w in words]
    df = pd.DataFrame({"word": words, "freq_zipf": np.round(zipf, 3),
                       "language": language, "source": "wordfreq"})
    df = df[df.freq_zipf > 0].sort_values("word").reset_index(drop=True)
    if len(df) < n_words:
        # A short lexicon thins every frequency band a design draws on, so a shortfall is
        # reported.
        message = (f"lexsync: wordfreq supplied only {len(df)} forms for '{language}' "
                   f"that pass the letter filter (n_words was {n_words}).")
        if strict:
            raise ValueError(message)
        print(message)
    return df


_BOM = b"\xef\xbb\xbf"
_LEADING_WS = b" \t\n\r\v\f"


def _starts_with_markup(path: str) -> bool:
    """Does the file open with '<', i.e. an HTML or XML document?

    Mirrors .starts_with_markup() in R_workflow/R/corpora.R. A delimited file
    opens on data; a login wall, a redirect stub or a 404 page served with a 200
    status opens on a tag, and would otherwise be cached as <name>.csv and
    resurface much later as an unintelligible schema error.
    """
    with open(path, "rb") as handle:
        head = handle.read(512)
    if head.startswith(_BOM):
        head = head[len(_BOM):]
    return head.lstrip(_LEADING_WS).startswith(b"<")


def _max_download_bytes() -> int:
    """Hard cap on a corpus download, in bytes.

    Mirrors .max_download_bytes() in R_workflow/R/corpora.R. A function rather
    than a bare constant so the twin tests can lower it without writing 200 MB
    to disk; the message below names the real limit either way.
    """
    return 200 * 1024 * 1024


def _read_registry(registry_path: str | None) -> tuple:
    """The registry's path and its parsed contents."""
    path = _registry_path(registry_path)
    with open(path, encoding="utf-8") as handle:
        return path, (yaml.safe_load(handle) or {})


def _download_source(name: str, entry: dict, reg_path: str) -> tuple:
    """The URL a registry entry is fetched from, its sha256, and whether to normalise it.

    A ``derived`` file, ``{url, sha256}``, is a lexicon already normalised, so both
    engines can read the same bytes, and it is read first when an entry has one.
    Otherwise ``openlexicon`` names the corpus file in its publisher's layout, which
    normalise_lexicon turns into a lexicon. ``url`` alone is a landing page, and
    downloading that would cache an HTML document as <name>.csv. Mirrors
    .download_source in R_workflow/R/corpora.R.
    """
    derived = entry.get("derived")
    if derived is not None:
        if not isinstance(derived, dict) or not derived.get("url"):
            raise ValueError(f"lexsync: corpus '{name}' registers a 'derived' file without a "
                             f"url in '{reg_path}'.")
        return derived["url"], derived.get("sha256"), False
    if entry.get("openlexicon"):
        return entry["openlexicon"], entry.get("sha256"), True
    if entry.get("url"):
        raise ValueError(
            f"lexsync: corpus '{name}' registers only a landing page ({entry['url']}) in "
            f"'{reg_path}'; lexsync cannot download it automatically. Retrieve the "
            f"delimited file manually, convert it with normalise_lexicon() and pass the "
            f"result to load_lexicon().")
    raise ValueError(
        f"lexsync: corpus '{name}' registers no download URL in '{reg_path}'; retrieve "
        f"its file manually, convert it with normalise_lexicon() and pass the result to "
        f"load_lexicon().")


def fetch_corpus(name: str, registry_path: str | None = None, n_words: int = 10000, *,
                 strict: bool = False, exclude_latin: bool = False) -> str:
    """Fetch a registered corpus into the cache.

    `name` must be a single corpus name: one holding '/', '\\' or ':' is refused
    before the registry is read, since the name becomes the cached file's name.

    If `name` is a language code supported by the wordfreq connector, a lexicon
    is built with wordfreq from up to `n_words` of its most frequent forms that
    are spelt with letters. A form may hold combining marks, such as the vowel
    signs of Hindi and Bengali, and the zero-width non-joiner of Persian. It may
    also hold an apostrophe inside a Ukrainian word or a middle dot between two
    l's in a Catalan one, but no digit and no other punctuation mark. A lexicon
    left with fewer forms is reported on standard output, or refused with
    `strict`, and `exclude_latin` drops every form holding a Latin letter. These
    three arguments apply to the wordfreq connector only, and
    ``lexsync.corpora.build_wordfreq_lexicon`` gives the rule in full.

    For any other name the registry entry's file is downloaded, once its URL's scheme
    has been checked. An entry's ``derived`` file, a lexicon already normalised, is
    fetched when it has one and cached as it arrives. Otherwise its ``openlexicon``
    file is fetched and converted by ``normalise_lexicon`` with the entry's
    ``columns`` and ``duplicates``, so ``fetch_corpus("subtlex_us")`` caches a lexicon
    that ``lexsync.load_lexicon`` reads. The transfer lands in a sidecar file that
    is renamed into the cache only after the size cap, the markup sniff, any registered
    sha256 and the normalisation have all passed. A refusal of the registry entry, a
    failed transfer and a checksum mismatch name the registry file read. A
    `registry_path` that does not exist is refused.

    The file lands in ``cache_dir`` as ``<name>.csv``, or ``<name>_wordfreq.csv`` for
    a lexicon the wordfreq connector builds, and its path is returned. The cache
    directory is created only once the registry entry and its URL have been accepted,
    or the wordfreq lexicon built, so a refused call writes nothing. Each fetch into
    the cache begins by deleting any ``.part`` sidecar that an interrupted transfer
    left there more than a day earlier. The cache persists between sessions, and one
    corpus may reach the 200 MB download cap, so several of them add up.
    ``cache_clear`` removes one corpus or the whole cache, and the next call fetches
    the corpus again.
    """
    _check_corpus_name(name)
    reg_path, reg = _read_registry(registry_path)
    wf = reg.get("wordfreq_connector") or {}
    if name in (wf.get("languages") or []):
        df = build_wordfreq_lexicon(name, n_words, strict=strict, exclude_latin=exclude_latin)
        dest = os.path.join(_prepare_cache(), f"{name}_wordfreq.csv")
        # LF explicitly: pandas otherwise follows os.linesep, and the cached
        # lexicon's bytes (and any checksum of them) must not depend on the OS.
        df.to_csv(dest, index=False, encoding="utf-8", lineterminator="\n")
        print(f"lexsync: built '{name}' via wordfreq. Please cite: {wf.get('citation', '')}")
        return dest
    entry = (reg.get("corpora") or {}).get(name)
    if not entry:
        raise ValueError(f"lexsync: corpus '{name}' is not in the registry '{reg_path}'.")
    url, expected, normalise = _download_source(name, entry, reg_path)
    # A registry is editable, and fetch_corpus() writes wherever it points, so a
    # 'file://' or 'ftp://' entry would read a local path under the guise of a
    # download. Only the two schemes a corpus is published over are honoured.
    if not re.match(r"https?://", url, re.IGNORECASE):
        raise ValueError(
            f"lexsync: corpus '{name}' registers a non-http(s) URL ({url}) in "
            f"'{reg_path}'; refusing to download."
        )
    import urllib.error
    import urllib.request
    # Only now, with every refusal behind it, does the call touch the disk.
    dest = os.path.join(_prepare_cache(), f"{name}.csv")
    # The transfer lands in a sidecar and is renamed over `dest` only after every
    # check below has passed, so a truncated or unverified body can never sit at
    # the cache path, where a later run would trust it.
    part = dest + ".part"
    try:
        # 60 s guards against a stalled server, which urlretrieve() would wait on
        # forever; the R engine's download.file() honours options(timeout).
        with urllib.request.urlopen(url, timeout=60) as response, \
                open(part, "wb") as handle:
            received = 0
            for chunk in iter(lambda: response.read(65536), b""):
                received += len(chunk)
                if received > _max_download_bytes():
                    raise ValueError(
                        "lexsync: corpus download exceeded the 200 MB size limit. "
                        "Retrieve the delimited file manually and pass it to "
                        "load_lexicon()."
                    )
                handle.write(chunk)
    except (urllib.error.URLError, OSError) as exc:
        if os.path.exists(part):
            os.remove(part)
        raise RuntimeError(
            f"lexsync: could not download corpus '{name}' from {url} ({exc}). "
            f"Check the URL in '{reg_path}', or download the file manually, convert it "
            f"with normalise_lexicon() and pass the result to load_lexicon()."
        ) from exc
    except ValueError:
        if os.path.exists(part):
            os.remove(part)
        raise
    if _starts_with_markup(part):
        os.remove(part)
        raise ValueError(
            f"lexsync: corpus '{name}' returned an HTML page, not a delimited file "
            f"({url}); the registry URL may have rotted. Retrieve the delimited file "
            f"manually and pass it to load_lexicon()."
        )
    # 'sha256' is optional per registry entry; when present the download must
    # match it before it may enter the cache.
    if expected and sha256_file(part) != expected:
        os.remove(part)
        raise ValueError(
            f"lexsync: checksum mismatch for corpus '{name}'; the download does "
            f"not match the registry's sha256. Retry the download, or verify the "
            f"sha256 recorded in '{reg_path}'."
        )
    if normalise:
        # The corpus file is read into memory and its sidecar then holds the lexicon,
        # so a file that cannot be normalised leaves nothing behind either.
        try:
            # The file's name and extension, without any query or fragment.
            named = re.sub(r"[?#].*$", "", url)
            lexicon, message = _normalise(part, None, entry, _delimiter_for(named),
                                          os.path.basename(named))
        finally:
            os.remove(part)
        print(message)
        write_csv_utf8(lexicon, part)
    os.replace(part, dest)
    print(f"lexsync: downloaded '{name}'. Please cite: {entry.get('citation', '(see registry)')}")
    return dest


# ---- normalise_lexicon -------------------------------------------------------
# A corpus file in its publisher's layout, made into a lexicon load_lexicon reads. The
# registry's `columns` map names a source's columns, and its `duplicates` rule says
# what a repeated form means. Mirrors normalise_lexicon in R_workflow/R/corpora.R, and
# the twin tests hold both engines to the same output bytes.

# The lexsync columns a map may name, in the order they are written.
_NORMALISE_KEYS = ("word", "freq_zipf", "freq_permillion", "pos")
_DUPLICATE_RULES = ("first", "sum")


def _delimiter_for(name):
    """',' or a tab from a file name's extension, or None when it says neither."""
    ext = os.path.splitext(str(name).lower())[1]
    return {".tsv": "\t", ".tab": "\t", ".csv": ","}.get(ext)


def _sniff_delimiter(path: str) -> str:
    """A tab when the header line holds one, and a comma otherwise."""
    with open(path, "rb") as handle:
        head = handle.readline()
    return "\t" if b"\t" in head else ","


def _corpus_entry(entry) -> dict:
    """A registry entry given as itself, or by its name in the registry found by default."""
    if entry is None:
        return {}
    if isinstance(entry, str):
        reg_path, reg = _read_registry(None)
        found = (reg.get("corpora") or {}).get(entry)
        if not found:
            raise ValueError(f"lexsync: corpus '{entry}' is not in the registry '{reg_path}'.")
        return found
    if isinstance(entry, dict):
        return entry
    raise ValueError("lexsync: 'entry' must be a registry entry or the name of one.")


def _first_bad(values, bad):
    """The index of the first value `bad` flags, or None."""
    for i, v in enumerate(values):
        if bad(v):
            return i
    return None


def _normalise(path, columns, entry, delimiter, label) -> tuple:
    """normalise_lexicon's work: the lexicon and the line that reports on it."""
    entry = _corpus_entry(entry)
    cmap = dict(columns if columns is not None else (entry.get("columns") or {}))
    unknown = [k for k in cmap if k not in _NORMALISE_KEYS]
    if unknown:
        raise ValueError(f"lexsync: unknown key '{unknown[0]}' in the column map; known keys: "
                         f"word, freq_zipf, freq_permillion, pos.")
    if "freq_zipf" in cmap and "freq_permillion" in cmap:
        raise ValueError("lexsync: the column map names both frequency columns; name "
                         "freq_zipf or freq_permillion, not both.")
    rule = entry.get("duplicates") or "first"
    if rule not in _DUPLICATE_RULES:
        raise ValueError(f"lexsync: duplicates must be 'first' or 'sum', not '{rule}'.")
    if delimiter is None:
        delimiter = _delimiter_for(path) or _sniff_delimiter(path)
    if delimiter not in (",", "\t"):
        raise ValueError("lexsync: delimiter must be ',' or a tab.")
    df = read_csv_utf8(path, as_character=True, delim=delimiter)
    names = list(df.columns)
    if "freq_zipf" in cmap or "freq_permillion" in cmap:
        freq_key = "freq_zipf" if "freq_zipf" in cmap else "freq_permillion"
        freq_col = cmap[freq_key]
    elif "freq_zipf" in names or "freq_permillion" in names:
        freq_key = freq_col = "freq_zipf" if "freq_zipf" in names else "freq_permillion"
    else:
        raise ValueError(f"lexsync: '{label}' has no column named freq_zipf or "
                         f"freq_permillion, and the column map names neither; map one of "
                         f"them to the file's frequency column.")
    word_col = cmap.get("word", "word")
    pos_col = cmap.get("pos", "pos" if "pos" in names else None)
    wanted = [("word", word_col), (freq_key, freq_col)]
    if pos_col is not None:
        wanted.append(("pos", pos_col))
    for target, col in wanted:
        if col not in names:
            raise ValueError(f"lexsync: '{label}' has no column '{col}' (mapped to {target}); "
                             f"its columns are {', '.join(repr(n) for n in names)}.")
    if rule == "sum" and freq_key != "freq_permillion":
        raise ValueError("lexsync: duplicates: sum adds frequencies per million, so the "
                         "column map must name freq_permillion; Zipf values cannot be added.")
    n_read = len(df)
    freq = _type_column([None if v != v else v for v in df[freq_col]])
    _require_numbers(freq, freq_col)
    keep = (df[word_col].notna() & freq.notna()).to_numpy()
    words = _fold_words(df[word_col][keep])
    values = [float(v) for v in freq[keep]]
    pos = (list(df[pos_col][keep]) if pos_col is not None else None)
    nonempty = [i for i, w in enumerate(words) if w != ""]
    words = [_nfc(words[i]) for i in nonempty]
    values = [values[i] for i in nonempty]
    if pos is not None:
        pos = [pos[i] for i in nonempty]
    if not words:
        raise ValueError(f"lexsync: '{label}' has no usable rows: every row is missing its "
                         f"word or its frequency.")
    if freq_key == "freq_permillion":
        i = _first_bad(values, lambda v: v < 0)
        if i is not None:
            raise ValueError(f"lexsync: column '{freq_col}' holds {_fmt_g(values[i])} for "
                             f"'{words[i]}', and a frequency per million must be positive "
                             f"to have a Zipf value; remove such rows first.")
    # One row per form: the first in file order, or under `sum` the first row's other
    # cells with the frequencies of every row added in file order.
    first = {}
    for i, w in enumerate(words):
        first.setdefault(w, i)
    rows = sorted(first.values())
    if rule == "sum":
        groups = {}
        for w, v in zip(words, values, strict=True):
            groups.setdefault(w, []).append(v)
        resolved = [_exact_sum(groups[words[i]]) for i in rows]
    else:
        resolved = [values[i] for i in rows]
    forms = [words[i] for i in rows]
    if freq_key == "freq_permillion":
        i = _first_bad(resolved, lambda v: v <= 0)
        if i is not None:
            raise ValueError(f"lexsync: column '{freq_col}' holds {_fmt_g(resolved[i])} for "
                             f"'{forms[i]}', and a frequency per million must be positive "
                             f"to have a Zipf value; remove such rows first.")
        zipf, near = _zipf_from_permillion(resolved)
    else:
        _check_zipf_range(resolved)
        zipf, near = resolved, 0
    out = {"word": forms, "freq_zipf": zipf}
    if freq_key == "freq_permillion":
        out["freq_permillion"] = resolved
    if pos is not None:
        out["pos"] = [pos[i] for i in rows]
    frame = pd.DataFrame(out)
    frame["word"] = frame["word"].astype(object)
    # UTF-8 byte order, the order load_lexicon gives a lexicon in both engines.
    frame = (frame.assign(_k=frame["word"].map(lambda w: w.encode("utf-8")))
             .sort_values("_k", kind="stable").drop(columns="_k").reset_index(drop=True))
    derived = freq_key == "freq_permillion"
    frame.attrs["normalisation"] = {
        "n_read": int(n_read), "n_forms": len(frame), "n_merged": len(words) - len(frame),
        "duplicates": rule, "zipf_derived": derived, "near_boundary": int(near)}
    message = "lexsync: normalised %d form%s from '%s'" % (
        len(frame), "" if len(frame) == 1 else "s", label)
    if derived:
        message += (f"; {near} of the Zipf values derived from frequencies per million lay "
                    f"within 1e-9 of a rounding boundary.")
    else:
        message += "."
    return frame, message


def normalise_lexicon(path: str, columns=None, entry=None, delimiter=None,
                      out: str | None = None) -> pd.DataFrame:
    """Turn a corpus file in its publisher's layout into a lexicon load_lexicon reads.

    Reads a tab- or comma-separated file. ``delimiter`` names the separator, "," or
    "\\t". Left as None, it is taken from the extension (.tsv and .tab are tab, .csv is
    comma) and otherwise from the header line, which is tab-separated when it holds a
    tab. A tab-separated file is read with no quoting.

    ``columns`` maps lexsync's column names to the file's, as a registry entry's
    ``columns`` does: ``word``, one of ``freq_zipf`` and ``freq_permillion``, and
    optionally ``pos``. ``entry`` is a registry entry, or the name of one in the
    registry lexsync finds by default (see ``list_corpora``), and supplies the map
    when ``columns`` is None and the ``duplicates`` rule. Without a map the file's own
    ``word``, ``freq_zipf`` or ``freq_permillion``, and ``pos`` columns are read.

    Words are trimmed, lower-cased and put in Unicode NFC, as load_lexicon keys them,
    and rows missing a word or a frequency are dropped. A form that then appears more
    than once is resolved by ``duplicates``: ``first`` (the default) keeps the first
    row in file order, and ``sum`` adds its rows' frequencies per million, as Lexique
    needs, since it splits a homograph's frequency between its rows. Frequencies per
    million are converted with Zipf = log10(per million) + 3, rounded to three places
    by lexsync's shared rounder. A value of 0 or below has no Zipf value and is
    refused. Zipf values read as they are must lie between 0 and 9.

    The lexicon has the columns ``word``, ``freq_zipf``, then ``freq_permillion`` when
    Zipf was derived from it, and ``pos`` when the file has one, in the UTF-8 byte
    order of ``word``. With ``out`` it is also written there, comma-separated with LF
    line endings. A line on standard output gives the number of forms, and for derived
    Zipf values the number that lay within 1e-9 of a rounding boundary after scaling.
    That is the only step at which the two engines' log10 could round a value apart,
    and the count is expected to be 0. ``attrs["normalisation"]`` holds ``{"n_read",
    "n_forms", "n_merged", "duplicates", "zipf_derived", "near_boundary"}``, and a run
    over the lexicon records the boundary count in its run log and datasheet.

    Mirrors normalise_lexicon in R_workflow/R/corpora.R, which writes the same bytes.
    """
    frame, message = _normalise(path, columns, entry, delimiter, os.path.basename(str(path)))
    print(message)
    if out is not None:
        write_csv_utf8(frame, out)
    return frame
