# -*- coding: utf-8 -*-
"""The orchestrator. Mirrors R_workflow/R/run_pipeline.R.

For each design it loads a lexicon, builds the pool, computes any missing
dimensions, matches stimuli, counterbalances, writes the descriptives report and
run log, and exports the PsychoPy and OpenSesame scripts. run_all loops over
every design configuration.
"""
from __future__ import annotations

import glob
import os

from . import logging as runlog
from .counterbalancing import counterbalance
from .io_utils import read_config, slugify, write_csv_utf8
from .matching import match_stimuli
from .querying import add_neighbourhood, build_pool, load_lexicon
from .scripting import export_experiments
from .validation import balance_check, match_report


def run_pipeline(design_path, schema_path="config/schema.yaml", outdir="output",
                 reference_words=None, verbose=True) -> dict:
    schema = read_config(schema_path)
    design = read_config(design_path)

    log = runlog.new_run_log(design["name"], meta={
        "design": design["name"], "language": design["language"], "lexicon": design["lexicon"],
        "seed": schema.get("seed"), "match_on": ", ".join(design["match_on"]),
    })
    runlog.log_step(log, f"loading lexicon '{design['lexicon']}'")
    lex = load_lexicon(design["lexicon"], schema, language=design["language"])
    runlog.log_step(log, f"lexicon loaded: {len(lex)} words", {"words": len(lex)})

    pool = build_pool(lex, design.get("pool_filters"))
    runlog.log_step(log, f"pool after filters: {len(pool)} words", {"pool": len(pool)})

    match_on = list(design["match_on"])
    needed = [d for d in ("n_density", "old20") if d in match_on]
    if needed and any(d not in pool.columns for d in needed):
        runlog.log_step(log, "computing orthographic neighbourhood (N, OLD20)")
        ref = reference_words if reference_words is not None else lex["word"].tolist()
        pool = add_neighbourhood(pool, reference=ref)

    stim = match_stimuli(pool, design, schema, verbose=verbose)
    runlog.log_step(log, f"matched {len(stim)} items across {stim['condition'].nunique()} conditions",
                    {"conditions": ", ".join(dict.fromkeys(stim["condition"]))})

    # The match report is computed on the matched set before counterbalancing,
    # so the reference condition is always the matching anchor. Report on every
    # standard dimension present, so the manipulated dimension is always shown.
    dims = [d for d in ("length", "frequency", "n_density", "old20") if d in stim.columns]
    report = match_report(stim, dims, schema)
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
    write_csv_utf8(stim, stim_path); runlog.log_artefact(log, stim_path, len(stim))
    desc_path = os.path.join(outdir, "reports", f"{base}_descriptives_py.csv")
    write_csv_utf8(report["descriptives"], desc_path); runlog.log_artefact(log, desc_path, len(report["descriptives"]))
    comp_path = os.path.join(outdir, "reports", f"{base}_comparisons_py.csv")
    write_csv_utf8(report["comparisons"], comp_path); runlog.log_artefact(log, comp_path, len(report["comparisons"]))

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
