"""Access to the many-language corpus registry.

Mirrors R_workflow/R/corpora.R, and adds the wordfreq connector (Connector B,
thirty registered languages; wordfreq covers 42). The demonstrations read the
bundled, pre-derived lexica; new languages are fetched on demand into a user
cache.
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

from .io_utils import sha256_file


def _registry_path(registry_path: str | None = None) -> str:
    candidates = [
        registry_path,
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


def cache_dir() -> str:
    """Per-user cache directory for fetched corpora.

    Where :func:`fetch_corpus` puts what it fetches, and the only place the
    package writes to without being handed a path. This function only reports
    the path. The directory is created by the first fetch into it, so until then
    it does not exist.

    The cache persists between sessions. A registered corpus is a delimited word
    list, and a download is refused above 200 MB, so a cache holding several
    large corpora can reach a few hundred megabytes. Each fetch into the cache
    first deletes any partial download that an interrupted transfer left there
    more than a day earlier, and fetching a corpus again replaces the earlier
    copy. Fetched corpora otherwise stay until :func:`cache_clear` removes them,
    one corpus at a time or all together. Nothing kept there is irreplaceable, so
    the next call downloads afresh. The R twin documents the same contract in
    lexsync_cache_dir.Rd; only the location differs, since R uses
    tools::R_user_dir.
    """
    return os.path.join(os.path.expanduser("~"), ".lexsync", "cache")


def cache_clear(name: str | None = None) -> list[str]:
    """Remove fetched corpora from the cache.

    Deletes what :func:`fetch_corpus` put in :func:`cache_dir`. Given a `name`,
    that is the corpus's ``<name>.csv``, any ``<name>.csv.part`` that an
    interrupted download left behind and the ``<name>_wordfreq.csv`` lexicon the
    wordfreq connector builds. With `name` left as None it is the whole cache
    directory, and the ``~/.lexsync`` directory above it once nothing else is left
    there. A corpus needed again is fetched afresh by the next
    :func:`fetch_corpus` call. Mirrors lexsync_cache_clear() in
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
        # The name becomes a file name inside the cache, so a path separator, or
        # the colon of a Windows drive such as 'D:', would let it reach a file
        # other than the corpus's own: os.path.join() drops the cache directory
        # before a drive. All three characters are refused on every platform, so
        # the two engines refuse the same names.
        if not isinstance(name, str) or not name or re.search(r"[/\\:]", name):
            raise ValueError("lexsync: 'name' must be a single corpus name, not a path.")
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
    # else in this module answers a failure with the remedy, and so does this now.
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
        # A short lexicon thins every frequency band a design draws on, and a Hindi one
        # used to come back with 3,207 of the 10,000 forms asked for, and nothing said so.
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


def fetch_corpus(name: str, registry_path: str | None = None, n_words: int = 10000, *,
                 strict: bool = False, exclude_latin: bool = False) -> str:
    """Fetch a registered corpus into the cache.

    If `name` is a language code supported by the wordfreq connector, a lexicon
    is built with wordfreq from up to `n_words` of its most frequent forms that
    are spelt with letters. A form may hold combining marks, such as the vowel
    signs of Hindi and Bengali, and the zero-width non-joiner of Persian. It may
    also hold an apostrophe inside a Ukrainian word or a middle dot between two
    l's in a Catalan one, but no digit and no other punctuation mark. A lexicon
    left with fewer forms is reported on standard output, or refused with
    `strict`, and `exclude_latin` drops every form holding a Latin letter. These
    three arguments apply to the wordfreq connector only, and
    ``lexsync.corpora.build_wordfreq_lexicon`` gives the rule in full. Otherwise
    the corpus's registered URL is downloaded, once its scheme has been checked;
    the transfer lands in a sidecar file that is renamed into the cache only
    after the size cap, the markup sniff and any registered sha256 have all
    passed.

    The file lands in :func:`cache_dir`. The cache directory is created only once
    the registry entry and its URL have been accepted, or the wordfreq lexicon
    built, so a refused call writes nothing. Each fetch into the cache begins by
    deleting any ``.part`` sidecar that an interrupted transfer left there more
    than a day earlier. The cache persists between sessions, and one corpus may
    reach the 200 MB download cap, so several of them add up. :func:`cache_clear`
    removes one corpus or the whole cache, and the next call fetches the corpus
    again.
    """
    with open(_registry_path(registry_path), encoding="utf-8") as handle:
        reg = yaml.safe_load(handle)
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
        raise ValueError(f"lexsync: corpus '{name}' is not in the registry.")
    # Only 'openlexicon' names a delimited file; 'url' is the landing page, and
    # downloading that would silently cache an HTML document as <name>.csv.
    url = entry.get("openlexicon")
    if not url:
        raise ValueError(
            f"lexsync: corpus '{name}' registers only a landing page "
            f"({entry.get('url', 'see registry.yaml')}); lexsync cannot download it "
            f"automatically. Retrieve the delimited file manually and pass it to "
            f"load_lexicon()."
        )
    # A registry is editable, and fetch_corpus() writes wherever it points, so a
    # 'file://' or 'ftp://' entry would read a local path under the guise of a
    # download. Only the two schemes a corpus is published over are honoured.
    if not re.match(r"https?://", url, re.IGNORECASE):
        raise ValueError(
            f"lexsync: corpus '{name}' registers a non-http(s) URL ({url}); "
            f"refusing to download."
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
            f"Check the URL in registry.yaml, or download the file manually and "
            f"pass it to load_lexicon()."
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
    expected = entry.get("sha256")
    if expected and sha256_file(part) != expected:
        os.remove(part)
        raise ValueError(
            f"lexsync: checksum mismatch for corpus '{name}'; the download does "
            f"not match the registry's sha256. Retry the download, or verify the "
            f"sha256 recorded in registry.yaml."
        )
    os.replace(part, dest)
    print(f"lexsync: downloaded '{name}'. Please cite: {entry.get('citation', '(see registry)')}")
    return dest
