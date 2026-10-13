"""The orchestrator. Mirrors R_workflow/R/run_pipeline.R.

For each design it obtains stimuli from the configured item source (a corpus
matched on lexical dimensions, generated pseudowords for lexical decision, or an
item table for priming and self-paced reading), then counterbalances, writes any
match-quality report and the run log, and exports the PsychoPy and OpenSesame
scripts from the design's trial-event sequence. run_all loops over every design.
"""
from __future__ import annotations

import functools
import glob
import hashlib
import os

import pandas as pd

from . import logging as runlog
from .blocks import BLOCK_MAIN, add_blocks
from .counterbalancing import (
    _check_incomplete,
    _incomplete_policy,
    _recipe,
    balance_lists,
    counterbalance,
    counterbalance_check,
)
from .datasheet import (
    _comparison_roles,
    _controlled,
    _posix,
    build_datasheet,
    write_datasheet,
)
from .design import (
    N_DEFAULT_GENERATED,
    _exclude_words,
    _referenced_dimensions,
    _resolve_n,
    design_stem,
    validate_design,
)
from .generation import _lexdec_eligible, _read_known_forms, build_lexdec_stimuli
from .io_utils import _is_continuous, read_config, write_csv_utf8
from .matching import _resolve_policy, match_stimuli, resample_stimuli, select_continuous_stimuli
from .pairs import join_member_norms, member_lexicon_path, select_continuous_pairs
from .paradigms import required_fields, resolve_events
from .paths import resolve_schema
from .querying import (
    _apply_exclude_words,
    _neighbourhood_reference,
    _nfc_count,
    _nfc_record,
    _read_exclude_words,
    add_bigram_frequency,
    add_neighbourhood,
    add_pair_overlap,
    apply_norms,
    build_pool,
    load_items,
    load_lexicon,
    load_pool,
)
from .scripting import (
    _allocate_codes,
    _design_condition_names,
    export_experiments,
    resolve_trial_timing,
)
from .validation import balance_check, match_report, match_report_continuous

# The dimensions lexsync derives from the forms when a lexicon lacks them, in the
# order add_neighbourhood and add_bigram_frequency add them.
DERIVED_DIMS = ("n_density", "old20", "bigram_freq")

# The dimensions a corpus or pool design's realised-control report covers whenever the
# stimuli carry them, ahead of the ones the design names. A report of match_on alone
# left uncontrolled confounds unreported: en_ndensity's dense words had fewer estimated
# syllables than its sparse ones (d = -0.83).
REPORT_DIMS = ("length", "frequency", "n_density", "old20", "n_syllables", "bigram_freq")

# A generated lexical decision's report: length, which every pseudoword shares with its
# base word, and three dimensions the generator does not hold. Its pseudowords are more
# bigram-typical than their words (d about -1.0 in en_lexdec).
LEXDEC_REPORT_DIMS = ("length", "bigram_freq", "n_density", "old20")


def _report_dims(design: dict, norms) -> list:
    """The dimensions a corpus or pool design's report covers, in first-mention order.

    REPORT_DIMS, then ``match_on``, every condition's ``define_by`` keys and every
    joined norm column. The report leaves out those the stimuli lack and those with no
    numeric value (see ``match_report``). Mirrors .report_dims in
    R_workflow/R/run_pipeline.R.
    """
    names = list(REPORT_DIMS) + [str(d) for d in (design.get("match_on") or [])]
    for cond in design.get("conditions") or []:
        if isinstance(cond, dict) and isinstance(cond.get("define_by"), dict):
            names += [str(k) for k in cond["define_by"]]
    for rec in norms or []:
        names += [str(c["column"]) for c in rec["columns"]]
    return list(dict.fromkeys(names))


def _present(v) -> bool:
    """Whether a report cell holds a value: neither None nor NaN."""
    return v is not None and v == v


def _dims_to_derive(design: dict, columns, override: bool) -> list:
    """The derived dimensions the run must compute, in DERIVED_DIMS order.

    Those the design refers to and the lexicon lacks. With a supplied reference
    (``override``) also n_density and old20, which every report shows, and bigram_freq
    when the lexicon carries it, since the lexicon's columns were computed against a
    different reference. Mirrors .dims_to_derive in R_workflow/R/run_pipeline.R.
    """
    referenced = _referenced_dimensions(design)
    out = []
    for d in DERIVED_DIMS:
        if d in referenced and d not in columns:
            out.append(d)
        elif override and (d != "bigram_freq" or d in columns or d in referenced):
            out.append(d)
    return out


def _derive_dims(frame, dims, reference, log, n_supplied=None):
    """Compute the named derived dimensions on `frame` against `reference`.

    N and OLD20 come from one pass and are computed together. A recomputation against
    a supplied reference overwrites the lexicon's columns in place and is logged as
    one step naming them.
    """
    if not dims:
        return frame
    if n_supplied is not None:
        runlog.log_step(log, "recomputed %s against a supplied reference of %d words"
                             % (", ".join(dims), n_supplied))
    if "n_density" in dims or "old20" in dims:
        if n_supplied is None:
            runlog.log_step(log, "computing orthographic neighbourhood (N, OLD20)")
        frame = add_neighbourhood(frame, reference=reference)
    if "bigram_freq" in dims:
        if n_supplied is None:
            runlog.log_step(log, "computing bigram frequency (phonotactic-probability proxy)")
        frame = add_bigram_frequency(frame, reference=reference)
    return frame


def _require_syllables(pool, design: dict) -> None:
    """Refuse a design that refers to n_syllables while a pool word lacks it.

    count_syllables gives a missing value for a word outside Latin script. The
    selectors would drop such words as incomplete candidates and a filter would drop
    them without a word, neither saying that the dimension does not apply to the
    script, so the run stops here and says so.
    Mirrors .require_syllables in R_workflow/R/run_pipeline.R.
    """
    if "n_syllables" not in _referenced_dimensions(design) or "n_syllables" not in pool:
        return
    n = int(pool["n_syllables"].isna().sum())
    if n:
        raise ValueError(
            "lexsync: n_syllables is not available for %d word(s) in the pool: it counts "
            "Latin vowel letters, so it is undefined for other scripts. Remove it from the "
            "design or filter those words out." % n)


def _restores_verbosity(fn):
    """Keep ``verbose`` from outliving the call.

    The narration gate is module state, so a public entry point that set it and
    walked away would silence, or unsilence, the rest of the session. Restoring it
    on every exit path, error included, mirrors the R twin's
    on.exit(options(old_opts)).
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        previous = runlog.get_verbose()
        try:
            return fn(*args, **kwargs)
        finally:
            runlog.set_verbose(previous)
    return wrapper


@_restores_verbosity
def run_pipeline(design_path: str, schema_path: str | None = None, outdir: str = "output",
                 reference_words: list | str | None = None, verbose: bool = True) -> dict:
    """Run the lexsync pipeline for one design.

    A design may refer to a derived dimension (``n_density``, ``old20``,
    ``bigram_freq``) in ``match_on``, a condition's ``define_by``, ``pool_filters``,
    a continuous predictor or control, or ``counterbalance.balance_on``. When the
    lexicon lacks it, the pipeline computes it on the pool against the neighbourhood
    reference, after the filters the lexicon can answer and before those on the
    derived dimension.

    A design that refers to ``n_syllables`` in any of those places is refused when a
    word that passes the other filters the lexicon can answer has no syllable
    estimate, which is the case for every word outside the Latin script (see
    ``count_syllables``).

    A corpus, pool or generate design may list words to leave out under
    ``exclude_words``, or name a file of them with ``exclude_words: {path: ...}``.
    They are removed from the candidates after any ``norms:`` join and before the pool
    filters, and the datasheet records the list with its checksum. The neighbourhood
    reference, and the words a generated pseudoword must not equal, keep them.

    Args:
        design_path: Path to a design configuration (YAML).
        schema_path: The schema to read. Left as None, it is resolved by
            :func:`lexsync.paths.resolve_schema`: ``config/schema.yaml`` in the
            working directory, then ``schema.yaml`` beside the design, then the copy
            bundled with the package, with a line on stderr naming the file chosen.
            A named schema that does not exist is an error. The path used is recorded
            in the run log and in the datasheet's ``reproducibility.schema_path``.
        outdir: Output directory, in which the subdirectories ``stimuli``,
            ``reports`` and ``experiments`` are created.
        reference_words: Optional list of words to compute the derived dimensions
            against. By default they are computed against the lexicon, or against
            its rows marked 1 in a ``reference_member`` column. For a corpus or pool
            design, a supplied list recomputes ``n_density`` and ``old20``, and
            ``bigram_freq`` when the lexicon carries it or the design refers to it,
            overriding the lexicon's columns. The datasheet then records the list's
            size and checksum and the columns it was applied to. A generate or table
            design does not use it, and the run log says so. A lone string is one
            word. A list that is empty or holds a missing value is refused. Its words
            are normalised to Unicode NFC before use, like every other text key the
            pipeline reads.
        verbose: Whether to print progress.

    Returns:
        A mapping of the output paths written.
    """
    runlog.set_verbose(verbose)
    # The design first, so a mistyped design path is reported on its own and not
    # after a line announcing which schema the run would have used.
    design = read_config(design_path)
    schema_path, _ = resolve_schema(schema_path, design_path=design_path)
    schema = read_config(schema_path)
    # Everything a design can be refused for without reading its lexicon is checked
    # here, before the output directory is touched: the keys, the name and language,
    # n_per_condition, the metadata written into the experiments, the events, the
    # condition names and match_on. Unknown keys come back as notes for the run log.
    key_notes = validate_design(design, schema)
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
    # counterbalance.recipe and counterbalance.incomplete take closed sets of values,
    # so a misspelt one is refused here, before any lexicon is read or file written.
    recipe = _recipe(design)
    incomplete_policy = _incomplete_policy(design, schema)
    # A lone string is one word, as R reads a character scalar, not a list of letters.
    # An empty list would set every word's N to 0 and its OLD20 to NaN, and the
    # selection would go ahead on those values. Mirrors the R twin.
    if isinstance(reference_words, str):
        reference_words = [reference_words]
    if reference_words is not None:
        reference_words = list(reference_words)
        if not reference_words or any(pd.isna(w) for w in reference_words):
            raise ValueError("lexsync: reference_words must hold at least one word and no "
                             "missing value.")
    # The words the design takes out of its candidates, read now, so that a list that
    # cannot be read is refused before any lexicon is loaded or file written.
    exclude = _exclude_words(design)
    excluded = None if exclude is None else _read_exclude_words(exclude)

    log = runlog.new_run_log(design["name"], meta={
        "design": design["name"], "language": design["language"],
        "paradigm": paradigm, "source": source, "seed": schema.get("seed"),
        "mode": "continuous" if is_continuous else "conditions",
        "schema_path": _posix(schema_path),
    })
    for note in key_notes:
        runlog.log_step(log, note)
    # Only a corpus or a supplied pool has derived dimensions to compute. Elsewhere the
    # argument changes nothing, so it is said here and kept out of the datasheet.
    override = reference_words is not None and source in ("corpus", "pool")
    if reference_words is not None and not override:
        runlog.log_step(log, "reference_words is not used by items.source '%s' and was "
                             "ignored" % source)

    report = None
    pair_eligible = None
    generation_exclude = None
    exclusions = None
    norms: list = []
    selection_audit = None
    # What NFC normalisation did to the inputs this run read (see querying._nfc_count),
    # summed for the run log and the datasheet.
    nfc_total = {"changed": 0, "collapsed": 0}

    def tally(record):
        for k in nfc_total:
            nfc_total[k] += int((record or {}).get(k, 0))

    # Read the matcher's audit attribute straight off the returned frame (pd.concat
    # and rbind drop attrs) and put any excluded candidates and window relaxations on
    # the run log, in the order the matcher met them. The datasheet records both too.
    # Returns the frame unchanged.
    def take_audit(stim):
        nonlocal selection_audit
        selection_audit = stim.attrs.get("audit")
        for dx in (selection_audit or {}).get("incomplete_dropped", []):
            if is_continuous:
                msg = "dropped %d candidate(s) missing the predictor or a control" % dx["n"]
            else:
                msg = ("dropped %d candidate(s) of condition '%s' missing a matched "
                       "dimension" % (dx["n"], dx["condition"]))
            runlog.log_step(log, msg, {"condition": dx["condition"], "n": dx["n"]})
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
        tally(joined["normalisation"])
        norms.extend(joined["provenance"])
        # A bare `on:` that was read as the join key, which the design should spell
        # `join_on:`.
        for note in joined["notes"]:
            runlog.log_step(log, note)
        for rec in joined["provenance"]:
            runlog.log_step(log, "joined %d norm column(s) from '%s'"
                                 % (len(rec["columns"]), rec["path"]),
                            {"norms": rec["path"], "sha256": rec["sha256"]})
        return joined["lexicon"]

    # A supplied reference list is a set of word keys like any other, so it is put in
    # NFC too, before any derived dimension is computed against it. The datasheet's
    # checksum below stays that of the list as supplied.
    ref_supplied = None
    if reference_words is not None:
        ref_supplied, n_changed, n_collapsed = _nfc_count(list(reference_words))
        tally({"changed": n_changed, "collapsed": n_collapsed})

    ref_words = None
    derived = []
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
            tally(lex.attrs.get("input_normalisation"))
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
            tally(lex.attrs.get("input_normalisation"))
            runlog.log_step(log, f"lexicon loaded: {len(lex)} words", {"words": len(lex)})
            ref_words = _neighbourhood_reference(lex)
        lex = join_norms(lex)
        # The design's exclude_words leave the candidates here, after the norms join and
        # before the pool filters. `lex` keeps them, because an excluded word is still a
        # word of the language: the neighbourhood reference came from it above, and a
        # generated design's pseudowords are checked against it below.
        candidates = lex
        if excluded is not None:
            candidates = _apply_exclude_words(lex, excluded["words"])
            exclusions = dict(excluded["record"], n_removed=len(lex) - len(candidates))
            runlog.log_step(
                log, "exclude_words: removed %d of the %d listed word(s) from the "
                     "candidates (%s)" % (exclusions["n_removed"], exclusions["n_listed"],
                                          exclusions["path"]),
                {"exclude_words": exclusions["path"], "sha256": exclusions["sha256"],
                 "n_removed": exclusions["n_removed"]})
        filters = dict(design.get("pool_filters") or {})
        derived = _dims_to_derive(design, lex.columns, override)
        reference = ref_supplied if override else ref_words
        n_supplied = len(reference_words) if override else None
        # A filter on a dimension still to be derived waits until it is: the other
        # filters run first and the derivation, quadratic in the reference, then runs
        # on the smaller frame. The values do not depend on which rows carry them,
        # because every word is measured against the whole reference.
        deferred = {k: v for k, v in filters.items() if k in derived}
        # build_pool skips a filter column it does not recognise, so a misspelt key
        # would silently leave the pool unfiltered; the pair path carries the same
        # guard. Checked after the norms join, which legitimately adds filterable
        # columns.
        unknown = [c for c in filters if c not in lex.columns and c not in deferred]
        if unknown:
            raise ValueError("lexsync: pool_filters name column(s) the lexicon does not "
                             "have: %s." % ", ".join(unknown))
        early = {k: v for k, v in filters.items() if k not in deferred}
        # The syllable check sees the words that the other filters on lexicon columns
        # keep (a filter on a dimension still to be derived runs later), and its own
        # filter runs after it: a filter drops the rows missing its column, so a
        # filter on n_syllables over Chinese would otherwise leave an empty pool and
        # an error far from the cause. Filters commute, so the rows are those of one
        # pass.
        pool = build_pool(candidates, {k: v for k, v in early.items() if k != "n_syllables"})
        _require_syllables(pool, design)
        pool = build_pool(pool, {k: v for k, v in early.items() if k == "n_syllables"})
        pending = derived
        if deferred:
            pool = build_pool(_derive_dims(pool, derived, reference, log, n_supplied),
                              deferred)
            pending = []
        runlog.log_step(log, f"pool after filters: {len(pool)} words", {"pool": len(pool)})

    if source in ("corpus", "pool"):
        pool = _derive_dims(pool, pending, reference, log, n_supplied)
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
                # resample_stimuli records the first replicate's exclusions, which
                # are the whole pool's. A window relaxation inside a replicate
                # reaches only the console, via verbose.
                n_sets = resample.get("n_sets", 2)
                stim = take_audit(resample_stimuli(pool, design, schema, n_sets,
                                                   verbose=verbose))
                runlog.log_step(log, f"resampled {stim['replicate'].nunique()} disjoint matched "
                                     f"sets ({len(stim)} items total)",
                                {"conditions": ", ".join(dict.fromkeys(stim["condition"]))})
            else:
                stim = take_audit(match_stimuli(pool, design, schema, verbose=verbose))
                runlog.log_step(log,
                                f"matched {len(stim)} items across "
                                f"{stim['condition'].nunique()} conditions",
                                {"conditions": ", ".join(dict.fromkeys(stim["condition"]))})
            # Bigram frequency is reported for every design, computed against the
            # run's reference on a copy when the stimuli lack it, so the stimuli file
            # and the selection stay as they were.
            report_stim = (stim if "bigram_freq" in stim.columns
                           else add_bigram_frequency(stim, reference=reference))
            # First-occurrence order, through dict.fromkeys in _report_dims: sorted()
            # would give a collated order that drifts from the R engine. A joined norm
            # the design matches on or defines its conditions by then reaches the
            # descriptives, comparisons and realised-control record, and not only the
            # stimuli file.
            dims = [d for d in _report_dims(design, norms) if d in report_stim.columns]
            report = match_report(report_stim, dims, schema,
                                  roles=_comparison_roles(design, _controlled(design, source)))
    elif source == "generate":
        n = _resolve_n(design, N_DEFAULT_GENERATED)
        gen_cfg = items_cfg.get("generation") or {}
        gen_method = gen_cfg.get("method", "letter_substitution")
        # Further known word forms a pseudoword must not equal. The lexicon stops at
        # its frequency floor, so on its own it lets real low-frequency words through.
        exclude = None
        if gen_cfg.get("exclude") is not None:
            known = _read_known_forms(gen_cfg.get("exclude"))
            exclude = known["forms"]
            generation_exclude = known["records"]
            for rec in generation_exclude:
                runlog.log_step(log, "pseudowords checked against %d known word form(s) "
                                     "from '%s'" % (rec["n_forms"], rec["source"]),
                                {"exclude": rec["source"], "sha256": rec["sha256"]})
        stim = build_lexdec_stimuli(pool, n, reference_words=lex["word"].tolist(),
                                    method=gen_method, exclude=exclude)
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
        # Words and pseudowords share their length by construction, so the report also
        # sets them against each other on the dimensions the generator does not hold,
        # computed against the lexicon's reference on a copy of the stimuli.
        report_stim = add_bigram_frequency(add_neighbourhood(stim, reference=ref_words),
                                           reference=ref_words)
        report = match_report(report_stim, list(LEXDEC_REPORT_DIMS), schema,
                              roles=_comparison_roles(design, _controlled(design, source)))
    elif source == "table":
        path = items_cfg["path"]
        runlog.log_step(log, f"loading items '{path}'")
        stim = load_items(path, required_fields(design))
        tally(stim.attrs.get("input_normalisation"))
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
            tally(mem_lex.attrs.get("input_normalisation"))
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
                # A missing d or p is None or NaN and prints "NA", as R's sprintf()
                # prints it, and a missing interval is left out, as in R. Formatting
                # None raised a TypeError when a condition had a single item.
                ci = f" [{lo:.2f}, {hi:.2f}]" if (_present(lo) and _present(hi)) else ""
                d = f"{cr['cohens_d']:.2f}" if _present(cr["cohens_d"]) else "NA"
                p = cr["tost_p"] if _present(cr["tost_p"]) else "NA"
                runlog.log_step(log, f"equivalence {cr['condition']} vs {cr['reference']} on "
                                     f"'{cr['dimension']}': d = {d}{ci}, "
                                     f"TOST p = {p} ({verdict})")

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
    # The trigger codes follow the design's conditions, then any other condition in
    # the order the item source lists it (a generated lexical decision's words
    # before its pseudowords, an item table's own order). Taken here, before the
    # shuffle, because the order of first appearance after it depends on the seed.
    condition_order = list(dict.fromkeys(
        (_design_condition_names(design) or []) + [str(c) for c in stim["condition"]]))
    # The conditions the table holds before it is dealt, which a Latin square with
    # fewer item sets than conditions can leave out of every list.
    cb_conditions = list(dict.fromkeys(str(c) for c in stim["condition"]))
    stim = counterbalance(stim, design, schema, list_of_set)
    # An incomplete rotation is a design decision the researcher may accept, so under
    # the default policy it is reported, in the run log here and in the datasheet,
    # and only counterbalance.incomplete: error refuses it.
    cb_check = counterbalance_check(stim, design, recipe, conditions=cb_conditions)
    for issue in cb_check["issues"]:
        runlog.log_step(log, "counterbalancing: " + issue)
    _check_incomplete(cb_check, incomplete_policy)
    # Practice and filler trials are presented but not analysed, so the frame splits
    # here: the experiment is generated from every presented trial, the stimuli file and
    # the reports from the main ones. A design declaring neither block is unaffected,
    # down to not gaining a `block` column.
    blk = add_blocks(stim, design, schema)
    blocks = blk["report"]
    tally(blk["normalisation"])
    # Logged here, once the practice and filler tables have been read too, and only when
    # normalising changed something, so a run over NFC input, every shipped design
    # included, writes the same log and datasheet as before.
    input_normalisation = _nfc_record(nfc_total["changed"], nfc_total["collapsed"])
    if input_normalisation:
        runlog.log_step(log, "normalised %d word form(s) to NFC; %d duplicate(s) removed"
                             % (input_normalisation["changed"],
                                input_normalisation["collapsed"]),
                        dict(input_normalisation))
    # Realise any per-trial duration before the stimuli are written, so a jittered
    # or item-driven interval is recorded as a variable rather than living only
    # inside the generated script.
    # Run on the presented set, so practice and filler trials get their own realised
    # durations too.
    presented = resolve_trial_timing(blk["presented"], design, schema)
    # Fractional milliseconds read from the items are rounded once, and the run log says
    # how many. The record is read straight off the frame and dropped, so no table
    # written later carries it.
    for note in presented.attrs.pop("duration_rounding", []):
        runlog.log_step(log, "rounded %d fractional duration(s) in column '%s' to whole "
                             "milliseconds" % (note["n_rounded"], note["column"]), dict(note))
    # A design whose item codes cannot be kept apart from its other trigger codes is
    # refused here, before any file is written. export_experiments allocates the same
    # codes again and reports on them.
    _allocate_codes(presented, condition_order, resolve_events(design), schema)
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

    base = design_stem(design)
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
                              os.path.join(outdir, "experiments"), base,
                              conditions=condition_order)
    # Every file, the loop and text tables included: they hold the trial order and the
    # trigger codes the experiments present, and the scripts alone did not record them.
    for path in exps["files"]:
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
        # The words the generator can use, which build_lexdec_stimuli draws from: the
        # band after the a-z filter, not before it.
        candidate_pool = [{"condition": "words in band",
                           "n_candidates": int(len(_lexdec_eligible(pool)))}]
    # The neighbourhood reference is provenance: overriding it changes n_density,
    # old20 and bigram_freq without touching any input file the datasheet hashes. It
    # is recorded only when a recomputation ran, with the columns it was applied to.
    nref = None
    if override and derived:
        nref = {"source": "user-supplied", "n_words": len(reference_words),
                "sha256": hashlib.sha256("\n".join(reference_words).encode("utf-8")).hexdigest(),
                "applied_to": list(derived)}
    ds = build_datasheet(design, schema, report, stim, source_path, artifacts,
                         schema.get("seed"), engine="python", candidate_pool=candidate_pool,
                         norms=norms, balance=balance, blocks=blocks,
                         design_path=design_path, schema_path=schema_path,
                         selection_audit=selection_audit,
                         neighbourhood_reference=nref, counterbalance_check=cb_check,
                         input_normalisation=input_normalisation,
                         generation_exclude=generation_exclude, exclusions=exclusions)
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
    """Run every ``design_*.yaml`` in ``config_dir`` and return each design's paths.

    ``schema_path`` left as None is resolved by :func:`lexsync.paths.resolve_schema`:
    ``<config_dir>/schema.yaml``, then ``config/schema.yaml`` in the working
    directory, then the copy bundled with the package, with a line on stderr naming
    the file chosen. A named schema that does not exist is an error, raised before
    any design runs.
    """
    if schema_path is not None:
        schema_path, _ = resolve_schema(schema_path)
    designs = sorted(glob.glob(os.path.join(config_dir, "design_*.yaml")) +
                     glob.glob(os.path.join(config_dir, "design_*.yml")))
    if not designs:
        raise FileNotFoundError(f"lexsync: no design_*.yaml files in '{config_dir}'.")
    # Two designs with one stem write the same files, and the second would overwrite
    # the first's without a word, so every stem is checked before any design runs.
    # `en-lexdec` and `en_lexdec` collide this way, as names differing only outside
    # ASCII did before design_stem gave them a checksum.
    stems: dict = {}
    for design in designs:
        stem = design_stem(read_config(design))
        if stem in stems:
            raise ValueError(f"lexsync: '{os.path.basename(stems[stem])}' and "
                             f"'{os.path.basename(design)}' would write the same files "
                             f"('{stem}'); give the designs distinct names.")
        stems[stem] = design
    if schema_path is None:
        # Resolved once, after the designs are found, so a folder without designs is
        # reported on its own and every design reads the same file.
        schema_path, _ = resolve_schema(config_dir=config_dir)
    results = {}
    for design in designs:
        if verbose:
            print(f"\n=== lexsync: design '{os.path.basename(design)}' ===")
        results[os.path.basename(design)] = run_pipeline(design, schema_path, outdir, verbose=verbose)
    if verbose:
        print(f"\n[lexsync] all {len(designs)} designs complete.")
    return results
