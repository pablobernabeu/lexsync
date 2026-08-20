"""The orchestrator. Mirrors R_workflow/R/run_pipeline.R.

For each design it obtains stimuli from the configured item source (a corpus
matched on lexical dimensions, generated pseudowords for lexical decision, or an
item table for priming and self-paced reading), then counterbalances, writes any
match-quality report and the run log, and exports the PsychoPy and OpenSesame
scripts from the design's trial-event sequence. run_all loops over every design.
"""
from __future__ import annotations

import glob
import hashlib
import math
import os

from . import logging as runlog
from .blocks import BLOCK_MAIN, add_blocks
from .counterbalancing import balance_lists, counterbalance
from .datasheet import build_datasheet, write_datasheet
from .generation import build_lexdec_stimuli
from .io_utils import _is_continuous, read_config, slugify, write_csv_utf8
from .matching import _resolve_policy, match_stimuli, resample_stimuli, select_continuous_stimuli
from .pairs import join_member_norms, member_lexicon_path, select_continuous_pairs
from .paradigms import required_fields
from .querying import (
    add_bigram_frequency,
    add_neighbourhood,
    add_pair_overlap,
    apply_norms,
    build_pool,
    load_items,
    load_lexicon,
    load_pool,
)
from .scripting import export_experiments, resolve_trial_timing
from .validation import balance_check, match_report, match_report_continuous


def run_pipeline(design_path, schema_path="config/schema.yaml", outdir="output",
                 reference_words=None, verbose=True) -> dict:
    runlog.set_verbose(verbose)
    schema = read_config(schema_path)
    design = read_config(design_path)
    # Resolved on presence, not truth: `or` treats a configured 0 as absent and would
    # fall through to n_per_cell and then to the matcher's default n, where the R
    # engine's %||% falls back on NULL alone and so reaches the refusal below. A
    # design asking for zero items must be refused by both engines, not silently
    # given twenty by one of them.
    n_req = design.get("n_per_condition")
    if n_req is None:
        n_req = design.get("n_per_cell")
    # isfinite, not a bare NaN test: int(inf) raises OverflowError here, while R's
    # trunc(Inf) equals Inf and let an infinite request through to select the whole
    # pool. Both engines refuse it now, with this message.
    if n_req is not None and (not isinstance(n_req, (int, float)) or isinstance(n_req, bool)
                              or not math.isfinite(n_req) or n_req < 1
                              or n_req != int(n_req)):
        raise ValueError("lexsync: n_per_condition must be a positive whole number.")
    items_cfg = design.get("items") or {}
    source = items_cfg.get("source", "corpus")
    paradigm = design.get("paradigm", "factorial")
    is_continuous = _is_continuous(design)
    if is_continuous and source == "table" and not list(items_cfg.get("members") or []):
        # Without members the table branch loads the rows and never selects, while
        # the log and datasheet would still record continuous mode, which is a
        # provenance lie.
        raise ValueError("lexsync: a 'continuous' block with items.source 'table' "
                         "requires items.members.")
    if source == "table" and not is_continuous and design.get("pool_filters") is not None:
        # Only the continuous pairs selector consumes pool_filters on the table
        # path; a curated item table is the researcher's selection, so a stray
        # filter here is always a mistake rather than a request to drop rows.
        raise ValueError("lexsync: pool_filters have no effect for items.source 'table' "
                         "without a 'continuous' block; remove them or use a continuous "
                         "design.")

    log = runlog.new_run_log(design["name"], meta={
        "design": design["name"], "language": design["language"],
        "paradigm": paradigm, "source": source, "seed": schema.get("seed"),
        "mode": "continuous" if is_continuous else "conditions",
    })

    report = None
    pair_eligible = None
    norms: list = []
    selection_audit = None

    # Read the matcher's audit attribute straight off the returned frame (pd.concat
    # and rbind drop attrs) and put any window relaxation on the run log; the
    # datasheet records it too. Returns the frame unchanged.
    def take_audit(stim):
        nonlocal selection_audit
        selection_audit = stim.attrs.get("audit")
        for rx in (selection_audit or {}).get("window_relaxations", []):
            runlog.log_step(log,
                            "tolerance window relaxed for condition '%s'"
                            " (%d within tolerance, %d needed)"
                            % (rx["condition"], rx["n_within_tolerance"], rx["n_needed"]),
                            {"condition": rx["condition"],
                             "n_within_tolerance": rx["n_within_tolerance"],
                             "n_needed": rx["n_needed"]})
        return stim

    # The design's `norms:` tables are joined onto the lexicon before the pool is
    # built, so a filter, a matched dimension or a continuous predictor may name a
    # semantic dimension lexsync does not compute. The records come back with the
    # lexicon and go into the datasheet: a norm table can carry the manipulated
    # variable itself, so the run is not reproducible from a record that does not name
    # the file and its checksum.
    def join_norms(lex):
        joined = apply_norms(lex, design)
        norms.extend(joined["provenance"])
        for rec in joined["provenance"]:
            runlog.log_step(log, "joined %d norm column(s) from '%s'"
                                 % (len(rec["columns"]), rec["path"]),
                            {"norms": rec["path"], "sha256": rec["sha256"]})
        return joined["lexicon"]

    ref_words = None
    if source in ("corpus", "generate", "pool"):
        if source == "pool":
            # A supplied word list, given the matcher's dimensions rather than dressed
            # up as a corpus lexicon. `reference` comes back separately because the
            # neighbourhood dimensions are properties of the language, not of the list.
            pool_path = items_cfg["path"]
            lexicon = items_cfg.get("lexicon") or design.get("lexicon")
            runlog.log_step(log, f"loading supplied pool '{pool_path}'")
            lp = load_pool(pool_path, schema, lexicon=lexicon, language=design["language"])
            lex = lp["pool"]
            ref_words = lp["reference"]
            runlog.log_step(
                log, "supplied pool: %d words%s"
                     % (len(lex), "" if not lexicon
                        else " (dimensions from '%s')" % lexicon),
                {"words": len(lex), "lexicon": lexicon})
        else:
            lexicon = items_cfg.get("lexicon") or design.get("lexicon")
            runlog.log_step(log, f"loading lexicon '{lexicon}'")
            lex = load_lexicon(lexicon, schema, language=design["language"])
            runlog.log_step(log, f"lexicon loaded: {len(lex)} words", {"words": len(lex)})
            ref_words = lex["word"].tolist()
        lex = join_norms(lex)
        # build_pool skips a filter column it does not recognise, so a misspelt key
        # would silently leave the pool unfiltered; the pair path carries the same
        # guard. Checked after the norms join, which legitimately adds filterable
        # columns.
        unknown = [c for c in (design.get("pool_filters") or {}) if c not in lex.columns]
        if unknown:
            raise ValueError("lexsync: pool_filters name column(s) the lexicon does not "
                             "have: %s." % ", ".join(unknown))
        pool = build_pool(lex, design.get("pool_filters"))
        runlog.log_step(log, f"pool after filters: {len(pool)} words", {"pool": len(pool)})

    if source in ("corpus", "pool"):
        match_on = list(design.get("match_on") or [])
        ref = reference_words if reference_words is not None else ref_words
        needed = [d for d in ("n_density", "old20") if d in match_on]
        if needed and any(d not in pool.columns for d in needed):
            runlog.log_step(log, "computing orthographic neighbourhood (N, OLD20)")
            pool = add_neighbourhood(pool, reference=ref)
        if "bigram_freq" in match_on and "bigram_freq" not in pool.columns:
            runlog.log_step(log, "computing bigram frequency (phonotactic-probability proxy)")
            pool = add_bigram_frequency(pool, reference=ref)
        if is_continuous:
            predictor = design["continuous"]["predictor"]
            controls = list(design["continuous"].get("controls") or [])
            stim = take_audit(select_continuous_stimuli(pool, design, schema, verbose=verbose))
            runlog.log_step(log, f"selected {len(stim)} items spanning '{predictor}' "
                                 f"(continuous design)", {"predictor": predictor})
            report = match_report_continuous(stim, predictor, controls, schema)
        else:
            resample = design.get("resample")
            if resample:
                # Per-replicate audits are dropped with the concat inside
                # resample_stimuli; a relaxation there still reaches the console
                # via verbose.
                n_sets = resample.get("n_sets", 2)
                stim = resample_stimuli(pool, design, schema, n_sets, verbose=verbose)
                runlog.log_step(log, f"resampled {stim['replicate'].nunique()} disjoint matched "
                                     f"sets ({len(stim)} items total)",
                                {"conditions": ", ".join(dict.fromkeys(stim["condition"]))})
            else:
                stim = take_audit(match_stimuli(pool, design, schema, verbose=verbose))
                runlog.log_step(log,
                                f"matched {len(stim)} items across "
                                f"{stim['condition'].nunique()} conditions",
                                {"conditions": ", ".join(dict.fromkeys(stim["condition"]))})
            std = ["length", "frequency", "n_density", "old20"]
            # First-occurrence-order union with match_on, through dict.fromkeys:
            # sorted() would give a collated order that drifts from the R engine.
            # A custom joined norm the design matches on then reaches the
            # descriptives, comparisons and realised-control record, and not only
            # the stimuli file.
            dims = [d for d in dict.fromkeys(std + match_on) if d in stim.columns]
            report = match_report(stim, dims, schema)
    elif source == "generate":
        n = design.get("n_per_condition") or design.get("n_per_cell") or 40
        gen_method = (items_cfg.get("generation") or {}).get("method", "letter_substitution")
        stim = build_lexdec_stimuli(pool, n, reference_words=lex["word"].tolist(),
                                    method=gen_method)
        sf = _resolve_policy(design, schema, "shortfall", "error", ("error", "allow"))
        realised = int(stim["set"].nunique())
        if realised < n and sf != "allow":
            # build_lexdec_stimuli filters the pool to a-z forms before selecting,
            # so the eligible pool can be smaller than the request without any
            # pool_filters.
            raise ValueError(f"lexsync: {n} sets per condition were requested but only "
                             f"{realised} could be generated; the eligible a-z pool is "
                             f"smaller than the request, so lower n_per_condition or supply "
                             f"more words, or set matching: shortfall: allow to accept a "
                             f"smaller set.")
        runlog.log_step(log, f"generated {len(stim)} items (words + pseudowords, {gen_method})",
                        {"conditions": ", ".join(dict.fromkeys(stim["condition"]))})
        report = match_report(stim, ["length"], schema)
    elif source == "table":
        path = items_cfg["path"]
        runlog.log_step(log, f"loading items '{path}'")
        stim = load_items(path, required_fields(design))
        runlog.log_step(log, f"loaded {stim['set'].nunique()} items across "
                             f"{stim['condition'].nunique()} conditions",
                        {"conditions": ", ".join(dict.fromkeys(stim["condition"]))})
        members = list(items_cfg.get("members") or [])
        if members:
            # Load the member lexicon here rather than inside join_member_norms, so the
            # design's `norms:` block reaches the members too: a semantic predictor such
            # as `target.concreteness` needs the norm columns present before they are
            # prefixed.
            mem_lexicon = member_lexicon_path(items_cfg, design)
            runlog.log_step(log, f"loading member lexicon '{mem_lexicon}'")
            mem_lex = load_lexicon(mem_lexicon, schema, language=design["language"])
            mem_lex = join_norms(mem_lex)
            stim = join_member_norms(stim, members, items_cfg, design, schema, lex=mem_lex)
            runlog.log_step(log, "joined word-level norms onto %s" % " and ".join(members))
            if "prime" in members and "target" in members:
                # The columns by name, not members[0]/members[1]: a member listed
                # before prime/target would silently redirect the overlap to the
                # wrong pair.
                stim = add_pair_overlap(stim, "prime", "target")
                runlog.log_step(log, "computed relational dimensions (pair.lev, pair.overlap)")
            if is_continuous:
                res = select_continuous_pairs(stim, items_cfg, design, schema, verbose)
                stim, report = take_audit(res["stim"]), res["report"]
                pair_eligible = res["n_eligible"]
                runlog.log_step(
                    log, "selected %d pairs spanning '%s' (%d eligible)"
                         % (stim["set"].nunique(), design["continuous"]["predictor"],
                            res["n_eligible"]),
                    {"sets": int(stim["set"].nunique()), "eligible": res["n_eligible"]})
    else:
        raise ValueError(f"lexsync: unknown item source '{source}'. "
                         "Known sources: corpus, pool, generate, table.")

    if report is not None:
        for msg in balance_check(stim, "condition"):
            runlog.log_step(log, "balance: " + msg)
        if is_continuous:
            for _, cr in report["comparisons"].iterrows():
                if cr["role"] == "control":
                    runlog.log_step(log, f"continuous: '{cr['dimension']}' correlation with "
                                         f"the predictor r = {cr['pearson_r']}")
        else:
            for _, cr in report["comparisons"].iterrows():
                verdict = "equivalent" if cr["equivalent"] else "not shown equivalent"
                lo, hi = cr["d_ci_low"], cr["d_ci_high"]
                ci = f" [{lo:.2f}, {hi:.2f}]" if (lo == lo and hi == hi) else ""  # NaN-safe
                runlog.log_step(log, f"equivalence {cr['condition']} vs {cr['reference']} on "
                                     f"'{cr['dimension']}': d = {cr['cohens_d']:.2f}{ci}, "
                                     f"TOST p = {cr['tost_p']} ({verdict})")

    # Balance-aware list assignment, when the design asks for it. Off by default,
    # because it changes which items a participant sees. The Latin-square recipe
    # rejects it: there every item is in every list already.
    list_of_set = None
    balance = None
    if (design.get("counterbalance") or {}).get("optimise"):
        bl = balance_lists(stim, design, schema)
        list_of_set = bl["list_of_set"]
        balance = bl["report"]
        runlog.log_step(
            log, "balanced %d item sets across %d lists on %s: cost %d -> %d in %d swap(s)"
                 % (len(list_of_set), (design.get("counterbalance") or {}).get("lists", 1),
                    ", ".join(balance["dimensions"]), balance["cost_before"],
                    balance["cost_after"], balance["n_swaps"]),
            {"cost_before": balance["cost_before"], "cost_after": balance["cost_after"],
             "swaps": balance["n_swaps"]})
        if balance["max_passes_reached"]:
            runlog.log_step(log, "balance: the pass bound was reached, so the search "
                                 "stopped before it ran out of improving swaps")
    stim = counterbalance(stim, design, schema, list_of_set)
    # Practice and filler trials are presented but not analysed, so the frame splits
    # here: the experiment is generated from every presented trial, the stimuli file and
    # the reports from the main ones. A design declaring neither block is unaffected,
    # down to not gaining a `block` column.
    blk = add_blocks(stim, design, schema)
    blocks = blk["report"]
    # Realise any per-trial duration before the stimuli are written, so a jittered
    # or item-driven interval is recorded as a variable rather than living only
    # inside the generated script.
    # Run on the presented set, so practice and filler trials get their own realised
    # durations too.
    presented = resolve_trial_timing(blk["presented"], design, schema)
    stim = (presented if blocks is None
            else presented[presented["block"] == BLOCK_MAIN].reset_index(drop=True))
    if blocks is not None:
        for b in blocks["blocks"]:
            runlog.log_step(
                log, "block '%s': %d trial(s) per list%s"
                     % (b["block"], b["n_per_list"],
                        "" if not b.get("placement") else ", " + b["placement"]),
                {"block": b["block"], "n_per_list": b["n_per_list"]})
        runlog.log_step(log, "presented %d trial(s); %d analysed"
                             % (len(presented), len(stim)))

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

    # Generated from the PRESENTED set: the experiment runs the practice and filler
    # trials too, even though they are absent from the stimuli file above.
    exps = export_experiments(presented, design, schema,
                              os.path.join(outdir, "experiments"), base)
    for path in exps.values():
        runlog.log_artefact(log, path)

    # A materials datasheet (machine + human readable) and a pre-registration
    # template: the shareable provenance record the reproducibility literature asks
    # for (Bochynska et al., 2023; Roettger, 2019).
    source_path = items_cfg.get("path") or items_cfg.get("lexicon") or design.get("lexicon")
    artifacts = {"stimuli": stim_path, "descriptives": desc_path,
                 "comparisons": comp_path, "experiments": exps}
    candidate_pool = None
    if is_continuous and source == "table":
        # A pair design has no word pool. Its candidates are the item sets that
        # passed the filters on every one of their rows, counted at set granularity.
        candidate_pool = [{"condition": "eligible pairs", "n_candidates": pair_eligible}]
    elif is_continuous:
        candidate_pool = [{"condition": "continuous", "n_candidates": int(len(pool))}]
    elif source in ("corpus", "pool"):
        # .get, not ["define_by"]: a condition without define_by counts the whole
        # pool, as the R engine's NULL does through build_pool.
        candidate_pool = [{"condition": c["name"],
                           "n_candidates": int(len(build_pool(pool, c.get("define_by"))))}
                          for c in (design.get("conditions") or [])]
    elif source == "generate":
        candidate_pool = [{"condition": "words in band", "n_candidates": int(len(pool))}]
    # The neighbourhood reference is provenance: overriding it changes n_density,
    # old20 and bigram_freq without touching any input file the datasheet hashes.
    nref = None
    if reference_words is not None:
        nref = {"source": "user-supplied", "n_words": len(reference_words),
                "sha256": hashlib.sha256("\n".join(reference_words).encode("utf-8")).hexdigest()}
    ds = build_datasheet(design, schema, report, stim, source_path, artifacts,
                         schema.get("seed"), engine="python", candidate_pool=candidate_pool,
                         norms=norms, balance=balance, blocks=blocks,
                         design_path=design_path, schema_path=schema_path,
                         selection_audit=selection_audit,
                         neighbourhood_reference=nref)
    ds_json = os.path.join(outdir, "reports", f"{base}_datasheet_py.json")
    ds_md = os.path.join(outdir, "reports", f"{base}_datasheet_py.md")
    write_datasheet(ds, ds_json, ds_md)
    runlog.log_artefact(log, ds_json)
    runlog.log_artefact(log, ds_md)

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
