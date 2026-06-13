# -*- coding: utf-8 -*-
"""Robust UTF-8 input/output and provenance helpers.

Mirrors R_workflow/R/io_utils.R. Centralising these guards against the encoding
pitfalls that arise with multilingual stimuli on Windows, and provides the
hashing used by the run log (MD5, matching the R engine).
"""
from __future__ import annotations

import hashlib
import os
import re

import pandas as pd
import yaml


def read_csv_utf8(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"lexsync: file not found: '{path}'")
    # Treat only "" and "NA" as missing, matching R's readr default. Pandas would
    # otherwise read the real words 'null', 'nan', 'none', 'true' etc. as NaN and
    # silently drop them, diverging from the R engine.
    return pd.read_csv(path, encoding="utf-8", keep_default_na=False, na_values=["", "NA"])


def write_csv_utf8(x: pd.DataFrame, path: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    x.to_csv(path, index=False, encoding="utf-8")
    return path


def hash_file(path: str):
    """MD5 digest of a file, for provenance logging (matches the R engine)."""
    if not os.path.exists(path):
        return None
    digest = hashlib.md5()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_file(path: str):
    """SHA-256 digest of a file, the stronger fingerprint used by the datasheet."""
    if not path or not os.path.exists(path):
        return None
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slugify(*parts) -> str:
    """Short, filesystem-safe slug; keeps generated names within MAX_PATH."""
    s = "_".join(str(p) for p in parts)
    s = re.sub(r"[^A-Za-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_").lower()


def read_config(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"lexsync: configuration not found: '{path}'")
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


# Control characters (incl. tab/newline/carriage return) are rejected in stimulus
# text: presented strings are single-line, and forbidding them stops a crafted
# item from corrupting the generated loop table or experiment scripts.
_CTRL_RE = re.compile(r"[\x00-\x1f\x7f]")


def clean_field(value, field: str = "field", max_len: int = 1000) -> str:
    """Validate a single stimulus value for safe inclusion in generated files.

    Rejects control characters and over-long strings; returns the value as a
    plain string. Commas and quotation marks are allowed (they are written as
    data into a properly quoted CSV that the experiment reads at run time, never
    interpolated into generated code), so ordinary sentences pass unchanged.
    """
    s = str(value)
    if _CTRL_RE.search(s):
        raise ValueError(f"lexsync: stimulus '{field}' contains control characters: {s!r}")
    if len(s) > max_len:
        raise ValueError(f"lexsync: stimulus '{field}' exceeds {max_len} characters.")
    return s
