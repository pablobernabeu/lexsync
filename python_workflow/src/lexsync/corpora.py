# -*- coding: utf-8 -*-
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


def fetch_corpus(name: str, registry_path: str | None = None, n_words: int = 10000) -> str:
    """Fetch a registered corpus into the cache.

    If `name` is a language code supported by the wordfreq connector, a lexicon
    is built with wordfreq. Otherwise the corpus's registered URL is downloaded.
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
    import urllib.request
    dest = os.path.join(cache_dir(), f"{name}.csv")
    urllib.request.urlretrieve(url, dest)
    print(f"lexsync: downloaded '{name}'. Please cite: {entry.get('citation', '(see registry)')}")
    return dest
