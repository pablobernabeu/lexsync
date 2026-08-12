"""Access to the many-language corpus registry.

Mirrors R_workflow/R/corpora.R, and adds the wordfreq connector (Connector B,
~40 languages). The demonstrations read the bundled, pre-derived lexica; new
languages are fetched on demand into a user cache.
"""
from __future__ import annotations

import os
import re

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
    path = os.path.join(os.path.expanduser("~"), ".lexsync", "cache")
    os.makedirs(path, exist_ok=True)
    return path


def build_wordfreq_lexicon(language: str, n_words: int = 10000,
                           min_len: int = 2, max_len: int = 15) -> pd.DataFrame:
    """Build a (word, freq_zipf) lexicon for any wordfreq language."""
    import wordfreq  # optional dependency (the [corpora] extra)

    rx = re.compile(r"^[^\W\d_]+$", re.UNICODE)
    words = []
    for w in wordfreq.top_n_list(language, n_words * 3):
        w = w.lower()
        if rx.match(w) and min_len <= len(w) <= max_len:
            words.append(w)
        if len(words) >= n_words:
            break
    zipf = [wordfreq.zipf_frequency(w, language) for w in words]
    df = pd.DataFrame({"word": words, "freq_zipf": np.round(zipf, 3),
                       "language": language, "source": "wordfreq"})
    return df[df.freq_zipf > 0].sort_values("word").reset_index(drop=True)


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


def fetch_corpus(name: str, registry_path: str | None = None, n_words: int = 10000) -> str:
    """Fetch a registered corpus into the cache.

    If `name` is a language code supported by the wordfreq connector, a lexicon
    is built with wordfreq. Otherwise the corpus's registered URL is downloaded,
    once its scheme has been checked; the transfer lands in a sidecar file that
    is renamed into the cache only after the size cap, the markup sniff and any
    registered sha256 have all passed.
    """
    with open(_registry_path(registry_path), encoding="utf-8") as handle:
        reg = yaml.safe_load(handle)
    wf = reg.get("wordfreq_connector") or {}
    if name in (wf.get("languages") or []):
        df = build_wordfreq_lexicon(name, n_words)
        dest = os.path.join(cache_dir(), f"{name}_wordfreq.csv")
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
    dest = os.path.join(cache_dir(), f"{name}.csv")
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
