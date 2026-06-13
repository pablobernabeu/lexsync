# -*- coding: utf-8 -*-
"""The orchestrator. Mirrors R_workflow/R/run_pipeline.R.

For each design it obtains stimuli from the configured item source -- a corpus
(matched on lexical dimensions), generated pseudowords (lexical decision), or an
item table (priming, self-paced reading) -- then counterbalances, writes any
match-quality report and the run log, and exports the PsychoPy and OpenSesame
scripts from the design's trial-event sequence. run_all loops over every design.
"""
from __future__ import annotations

import glob
import os

from . import logging as runlog
from .counterbalancing import counterbalance
from .generation import build_lexdec_stimuli
from .io_utils import read_config, slugify, write_csv_utf8
from .matching import match_stimuli
from .paradigms import required_fields
from .querying import add_neighbourhood, build_pool, load_items, load_lexicon
from .scripting import export_experiments
from .validation import balance_check, match_report


def run_pipeline(design_path, schema_path="config/schema.yaml", outdir="output",
                 reference_words=None, verbose=True) -> dict:
    schema = read_config(schema_path)
    design = read_config(design_path)
    items_cfg = design.get("items") or {}
    source = items_cfg.get("source", "corpus")
    paradigm = design.get("paradigm", "factorial")

    log = runlog.new_run_log(design["name"], meta={
        "design": design["name"], "language": design["language"],
        "paradigm": paradigm, "source": source, "seed": schema.get("seed"),
    })

    report = None
    if source in ("corpus", "generate"):
        lexicon = items_cfg.get("lexicon") or design.get("lexicon")
        runlog.log_step(log, f"loading lexicon '{lexicon}'")
        lex = load_lexicon(lexicon, schema, language=design["language"])
        runlog.log_step(log, f"lexicon loaded: {len(lex)} words", {"words": len(lex)})
        pool = build_pool(lex, design.get("pool_filters"))
        runlog.log_step(log, f"pool after filters: {len(pool)} words", {"pool": len(pool)})

    if source == "corpus":
        match_on = list(design.get("match_on") or [])
        needed = [d for d in ("n_density", "old20") if d in match_on]
        if needed and any(d not in pool.columns for d in needed):
            runlog.log_step(log, "computing orthographic neighbourhood (N, OLD20)")
            ref = reference_words if reference_words is not None else lex["word"].tolist()
            pool = add_neighbourhood(pool, reference=ref)
        stim = match_stimuli(pool, design, schema, verbose=verbose)
        runlog.log_step(log, f"matched {len(stim)} items across {stim['condition'].nunique()} conditions",
                        {"conditions": ", ".join(dict.fromkeys(stim["condition"]))})
        dims = [d for d in ("length", "frequency", "n_density", "old20") if d in stim.columns]
        report = match_report(stim, dims, schema)
    elif source == "generate":
        n = design.get("n_per_condition") or design.get("n_per_cell") or 40
        stim = build_lexdec_stimuli(pool, n, reference_words=lex["word"].tolist())
        runlog.log_step(log, f"generated {len(stim)} items (words + pseudowords)",
                        {"conditions": ", ".join(dict.fromkeys(stim["condition"]))})
        report = match_report(stim, ["length"], schema)
    elif source == "table":
        path = items_cfg["path"]
        runlog.log_step(log, f"loading items '{path}'")
        stim = load_items(path, required_fields(design))
        runlog.log_step(log, f"loaded {stim['set'].nunique()} items across "
                             f"{stim['condition'].nunique()} conditions",
                        {"conditions": ", ".join(dict.fromkeys(stim["condition"]))})
    else:
        raise ValueError(f"lexsync: unknown item source '{source}'.")

    if report is not None:
        for msg in balance_check(stim, "condition"):
            runlog.log_step(log, "balance: " + msg)
        for _, cr in report["comparisons"].iterrows():
            verdict = "equivalent" if cr["equivalent"] else "not shown equivalent"
            lo, hi = cr["d_ci_low"], cr["d_ci_high"]
            ci = f" [{lo:.2f}, {hi:.2f}]" if (lo == lo and hi == hi) else ""  # NaN-safe
            runlog.log_step(log, f"equivalence {cr['condition']} vs {cr['reference']} on "
                                 f"'{cr['dimension']}': d = {cr['cohens_d']:.2f}{ci}, "
                                 f"TOST p = {cr['tost_p']} ({verdict})")

    stim = counterbalance(stim, design, schema)

    base = slugify(design["name"], design["language"])
    for sub in ("stimuli", "reports", "experiments"):
        os.makedirs(os.path.join(outdir, sub), exist_ok=True)

    stim_path = os.path.join(outdir, "stimuli", f"{base}_stimuli_py.csv")
    write_csv_utf8(stim, stim_path)
    runlog.log_artefact(log, stim_path, len(stim))
    desc_path = comp_path = None
    if report is not None:
        desc_path = os.path.join(outdir, "reports", f"{base}_descriptives_py.csv")
        write_csv_utf8(report["descriptives"], desc_path)
        runlog.log_artefact(log, desc_path, len(report["descriptives"]))
        comp_path = os.path.join(outdir, "reports", f"{base}_comparisons_py.csv")
        write_csv_utf8(report["comparisons"], comp_path)
        runlog.log_artefact(log, comp_path, len(report["comparisons"]))

    exps = export_experiments(stim, design, schema, os.path.join(outdir, "experiments"), base)
    for path in exps.values():
        runlog.log_artefact(log, path)

    log_md = os.path.join(outdir, "reports", f"{base}_run_log_py.md")
    runlog.write_run_log(log, log_md, os.path.join(outdir, "reports", f"{base}_run_log_py.jsonl"))

    if verbose:
        print(f"[lexsync] design '{base}' complete.")
    return {"stimuli": stim_path, "descriptives": desc_path, "comparisons": comp_path,
            "experiments": exps, "log": log_md}


def run_all(config_dir="config", schema_path=None, outdir="output", verbose=True) -> dict:
    schema_path = schema_path or os.path.join(config_dir, "schema.yaml")
    designs = sorted(glob.glob(os.path.join(config_dir, "design_*.yaml")) +
                     glob.glob(os.path.join(config_dir, "design_*.yml")))
    if not designs:
        raise FileNotFoundError(f"lexsync: no design_*.yaml files in '{config_dir}'.")
    results = {}
    for design in designs:
        if verbose:
            print(f"\n=== lexsync: design '{os.path.basename(design)}' ===")
        results[os.path.basename(design)] = run_pipeline(design, schema_path, outdir, verbose=verbose)
    if verbose:
        print(f"\n[lexsync] all {len(designs)} designs complete.")
    return results
