#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Thin wrapper that runs every lexsync demonstration design.

Usage (from the repository root):  python python_workflow/run_pipeline.py
Adds the package source to sys.path so it works before installation too.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "src"))
os.chdir(REPO)

from lexsync.run_pipeline import run_all  # noqa: E402

if __name__ == "__main__":
    run_all(config_dir="config", schema_path="config/schema.yaml", outdir="output")
