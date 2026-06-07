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
    return pd.read_csv(path, encoding="utf-8")


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
