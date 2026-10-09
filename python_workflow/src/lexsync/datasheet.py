"""Materials datasheet and pre-registration template.

A *materials datasheet* is a machine- and human-readable provenance record for a
design. It records where the items came from, how they were selected, matched and
counterbalanced, the realised control, and the seeds, versions and checksums needed
to reproduce them exactly. It is the shareable materials record whose scarcity
motivates lexsync (Bochynska et al., 2023; Roettger, 2019). The
module also emits an auto-filled Methods paragraph and a pre-registration
skeleton. Mirrors R_workflow/R/datasheet.R.
"""
from __future__ import annotations

import json
import platform

# The recipe and the rotation check come from the module that counterbalances, so
# the record describes the counterbalancing that ran.
from .counterbalancing import _recipe
from .counterbalancing import counterbalance_check as _counterbalance_check

# The tolerance windows as match_stimuli resolves them: one resolver, so the record
# cannot drift from the selection.
from .design import _resolve_tolerance_k
from .io_utils import _fmt_dp, _is_continuous, _round_dp, sha256_file

# The cap the pairwise (joint, optimal) matchers apply before pairing, and the
# tie-break rule and its salt. Imported from matching so the datasheet can only ever
# record the values the selection used.
from .matching import PAIRWISE_CAP, TIE_SALT, _resolve_tie_break
from .paradigms import resolve_events

# The versions and the response windows come from the module that writes the
# experiments, so the record counts the versions the participants are given and states
# the windows they respond in.
from .scripting import _refresh_hz, _response_windows, presentation_versions

# 1.1 added `materials_source["norms"]` (the design's joined norm tables, with their
# checksums and per-column coverage) and, for a pair-keyed design, a `relational`
# block plus an honest `selection["cross_engine"]`. Both were required by the rule
# that anything affecting item selection is recorded here: a norm table can carry the
# manipulated variable itself, and the pair path performs a real selection that the
# record used to describe as "n/a (user-supplied items)".
#
# 1.2 records the counterbalancing that ran. Each later field of 1.2 adds a line here.
#   counterbalancing.recipe     the recipe counterbalance() applied (1.1 inferred it
#                               from the item source)
#   counterbalancing.lists      the lists the stimuli table holds (1.1 copied
#                               counterbalance.lists, with a default of 1)
#   counterbalancing.complete   whether a Latin-square rotation is complete
#   counterbalancing.issues     what leaves it incomplete
#   counterbalancing.cells      the trials per list and condition
#   materials_source["input_normalisation"]   what NFC normalisation did to the inputs
#                                             ({changed, collapsed}), present only when
#                                             it changed something
#   selection.incomplete_dropped  the candidates each condition lost for missing a
#                               matched dimension, present only when it lost any
#   counterbalancing.versions   the presentation versions, one per (replicate, list)
#   counterbalancing.assignment the rule that gives each participant one version
#   selection.neighbourhood_reference.applied_to
#                               the derived columns a supplied reference_words list
#                               recomputed. The record is now written only when one
#                               ran.
#   selection["generation_exclude"]   the known-form lists a generated pseudoword was
#                                     checked against ({source, sha256, n_forms} each),
#                                     present only when the design names any
#   selection.tie_break         the rule that broke exact ties between equally close
#                               candidates ({rule, salt}, the salt only for hash),
#                               present for a matched corpus or pool design
#   presentation.response_windows  each response event's window, {event, from,
#                               window_ms}; window_ms is null, with duration_column and
#                               timeout_ms, when the stimulus's duration varies by trial
#                               (analysis.response now says where a reaction time starts)
DATASHEET_VERSION = "1.2"

# Datasheet labels for the pseudoword generators in generation.py, keyed by the
# items.generation.method token. Kept character-for-character identical to
# .GENERATION_LABELS in datasheet.R so the two engines' records stay comparable.
_GENERATION_LABELS = {
    "letter_substitution": "constrained letter substitution (deterministic pseudowords)",
    "subsyllabic": "subsyllabic constituent swap (Wuggy-style, deterministic pseudowords)",
}


def _lexsync_version() -> str:
    """The installed lexsync version, mirroring datasheet.R's packageVersion lookup."""
    try:
        from importlib.metadata import version
        return version("lexsync")
    except Exception:
        # Deferred: __init__ imports this module before it binds __version__.
        from . import __version__
        return __version__


def _versions(engine: str) -> dict:
    out = {"engine": engine, "lexsync": _lexsync_version()}
    if engine == "python":
        import numpy as np
        import pandas as pd
        out["python"] = platform.python_version()
        out["pandas"] = pd.__version__
        out["numpy"] = np.__version__
        try:
            import scipy
            out["scipy"] = scipy.__version__
        except Exception:
            pass
        # Distribution metadata, because neither package exports __version__.
        from importlib.metadata import version
        for pkg in ("rapidfuzz", "pyyaml"):
            try:
                out[pkg] = version(pkg)
            except Exception:
                pass
    # The OS completes the environment record; per-engine, like the rest of the block.
    out["os"] = platform.system() + " " + platform.machine()
    return out


def _cross_engine(method, source: str, selected: bool = False) -> str:
    """Whether the R and Python engines select byte-identical materials.

    The deterministic methods are byte-identical; ``mahalanobis`` and ``optimal``
    are the exception, because they use a covariance-matrix inverse and an
    assignment solver whose last bits differ between the two linear-algebra
    backends (see matching.py).

    ``selected`` distinguishes the two things an item table can now mean. A plain
    table design does no selection, so there is nothing for the engines to agree on
    and "n/a" is the whole story. A pair-keyed continuous design selects over that
    table, and that selection was measured to be byte-identical, so answering "n/a"
    there understated the guarantee on the one path where a reader most needs it.
    """
    if source == "table" and not selected:
        return "n/a (user-supplied items)"
    if method in ("mahalanobis", "optimal"):
        return "approximate (platform linear algebra)"
    return "byte-identical"


def _relational_record(design: dict, stimuli) -> dict | None:
    """The pair-keyed part of the record, or None for a design that is not pair-keyed.

    Derived from the design and the realised stimuli rather than passed in, so both
    engines compute it from the same two objects and cannot disagree about it.

    Three of these fields answer questions the rest of the datasheet gets wrong for a
    pair design. ``n_pairs`` is stated because ``items["n_total"]`` counts ROWS, which
    is one per pair per condition, so a reader comparing it against the design's
    ``n_per_condition`` would find it doubled. The member lexicon is named and
    checksummed because it is where every member-level control came from, and nothing
    else in the record mentions it. ``materials_source`` names the item table. And
    the member dimensions are separated from the relational ones because they are
    different kinds of variable: ``target.frequency`` is a property of one word,
    ``pair.overlap`` is a property of the pair, and only the second is unavailable
    from any word-level norm database. Mirrors datasheet.R.
    """
    items_cfg = design.get("items") or {}
    members = list(items_cfg.get("members") or [])
    if not members:
        return None
    cols = list(stimuli.columns)
    # The union over members, not the first member's alone. join_member_norms gives
    # every member the same dimensions, so the sets coincide in anything the pipeline
    # produced; taking the union means a hand-built frame cannot report an empty list
    # merely because the first member happens to carry no prefixed column.
    # startswith, not a regex: a member name is user-supplied and may contain a
    # character a regex would read as syntax.
    member_dims = set()
    for m in members:
        prefix = m + "."
        member_dims.update(c[len(prefix):] for c in cols if c.startswith(prefix))
    lexicon = items_cfg.get("lexicon") or design.get("lexicon")
    return {
        "members": members,
        "n_pairs": int(stimuli["set"].nunique()),
        "member_lexicon": lexicon,
        "member_lexicon_sha256": sha256_file(lexicon),
        "member_dimensions": sorted(member_dims, key=lambda s: s.encode("utf-8")),
        "relational_dimensions": sorted((c for c in cols if c.startswith("pair.")),
                                        key=lambda s: s.encode("utf-8")),
    }


def _controlled(design: dict, source: str) -> list:
    # A supplied pool goes through the same matcher as a corpus, so it controls the same
    # dimensions; only the origin of the candidate words differs.
    if source in ("corpus", "pool"):
        return list(design.get("match_on") or [])
    if source == "generate":
        return ["length"]
    return []


def _response_text(windows: list, events: list) -> str:
    """The response the analysis models, with where its reaction time starts.

    From the first response window: a reaction time from the onset of the stimulus
    the response answers, or from the opening of a window after it. A design without a
    response event keeps the generic outcome. Mirrors .response_text in datasheet.R.
    """
    if not windows:
        return "the trial outcome (e.g. reaction time or accuracy)"
    w = windows[0]
    if w["from"] == "offset":
        return ("reaction time from the opening of a response window after the stimulus; "
                "responses collected for %d ms; a response ends the trial" % w["window_ms"])
    target = str(events[w["event"] - 2].get("content", ""))
    span = ("for %d ms" % w["window_ms"] if w["window_ms"] is not None
            else "until %d ms after its offset" % w["timeout_ms"])
    return ("reaction time from the onset of `%s`; responses collected %s; a response "
            "ends the trial" % (target, span))


def _response_note(ds: dict) -> str:
    """The response window, for the Methods text.

    From the first response window the record holds. Empty without one, and for a
    record written before the field existed. Mirrors .response_note in datasheet.R.
    """
    windows = (ds.get("presentation") or {}).get("response_windows") or []
    if not windows:
        return ""
    w = windows[0]
    if w["from"] == "offset":
        return (" Responses were collected in a %d ms window that opened after the "
                "stimulus, and a response ended the trial." % int(w["window_ms"]))
    if w.get("window_ms") is None:
        return (" Responses were collected from target onset until %d ms after its "
                "offset, and a response ended the trial." % int(w["timeout_ms"]))
    return (" Responses were collected from target onset until %d ms after it, and a "
            "response ended the trial." % int(w["window_ms"]))


def _analysis(design: dict, source: str,
              response: str = "the trial outcome (e.g. reaction time or accuracy)") -> dict:
    """A suggested crossed mixed-model formula for the design.

    Handing the user an items-crossed model guards against the
    language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008): items are
    a random sample of the language, so an analysis that treats them as fixed
    over-generalises. The manipulated factor is within subjects (each participant
    sees every condition) and, for corpus/lexical-decision designs, between items
    (each item belongs to one condition), so items take a random intercept; in the
    counterbalanced table paradigms the factor is within items too, so items also
    take a random slope.
    """
    cont = design.get("continuous")
    if cont:
        predictor = cont["predictor"]
        controls = list(cont.get("controls") or [])
        fixed = " + ".join([predictor] + controls)
        note = ("The predictor is kept continuous and analysed by regression or a "
                "mixed model rather than dichotomised (Kuperman, 2015; Liben-Nowell "
                "et al., 2019); the controls enter as covariates. Crossed random "
                "effects for subjects and items guard the language-as-fixed-effect "
                "fallacy (Clark, 1973; Baayen et al., 2008); reduce the structure if "
                "it does not converge (Matuschek et al., 2017).")
        # A pair design's member-prefixed terms carry a dot, which R formulas accept
        # but Patsy reads as syntax, so the Python analyst needs the quoting stated.
        if any("." in t for t in [predictor] + controls):
            note += (" Dotted dimension names are valid in R formulas but must be "
                     "quoted as Q(\"...\") in Patsy-style Python interfaces.")
        return {
            "response": response,
            "suggested_model": f"response ~ {fixed} + (1 + {predictor} | subject) + (1 | item)",
            "note": note,
        }
    paradigm = design.get("paradigm", "factorial")
    if source == "generate" or paradigm == "lexical_decision":
        factor, item_re = "lexicality", "(1 | item)"
    elif paradigm in ("priming", "self_paced_reading"):
        factor, item_re = "condition", "(1 + condition | item)"
    else:
        factor, item_re = "condition", "(1 | item)"
    return {
        "response": response,
        "suggested_model": f"response ~ {factor} + (1 + {factor} | subject) + {item_re}",
        "note": ("Crossed random effects for subjects and items guard against the "
                 "language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). "
                 "Begin with this maximal structure (Barr et al., 2013) and reduce it "
                 "if the model does not converge (Matuschek et al., 2017). The formula "
                 "is lme4 syntax, for lme4 in R or pymer4 in Python; statsmodels "
                 "MixedLM cannot take it directly and needs the random effects "
                 "restated in its own arguments. The equivalence tests in the realised "
                 "control are post-selection diagnostics on deterministically selected "
                 "items, not inferential tests over a sample."),
    }


def build_datasheet(design, schema, report, stimuli, source_path, artifacts,
                    seed, engine="python", candidate_pool=None, norms=None,
                    balance=None, blocks=None, design_path=None, schema_path=None,
                    selection_audit=None, neighbourhood_reference=None,
                    counterbalance_check=None, input_normalisation=None,
                    generation_exclude=None) -> dict:
    """Assemble the datasheet dictionary from the pipeline's objects.

    ``candidate_pool`` (optional) is a list of ``{"condition", "n_candidates"}``
    recording how many items satisfied each condition's window before matching,
    the size of the discretionary pool the selection drew from, reported so that
    item-selection bias is auditable (Forster, 2000; Simmons et al., 2011).

    ``norms`` (optional) is a list of norm-table provenance records from the design's
    ``norms:`` block. Each names a file, its sha256, the join key and the per-column
    coverage. Recorded because a norm table can supply the very variable a design
    manipulates, so a record that omitted it would describe a selection over columns
    of unstated origin.

    ``balance`` (optional) is the balance-optimiser report from ``balance_lists``.
    Recorded because it decides which items each participant sees.

    ``design_path`` / ``schema_path`` (optional) are the design and schema files the
    run read; when given, their sha256 checksums complete the reproducibility
    record, because those two files decide everything the seed does not.

    ``selection_audit`` (optional) is the matcher's audit record; its
    ``window_relaxations`` entries are recorded because a relaxed window changes
    what "matched" means for that condition. Its ``incomplete_dropped`` entries
    (``{"condition", "n"}``) count the candidates excluded for missing a matched
    dimension, which ``candidate_pool`` still includes. They are recorded because
    the selection drew on a smaller pool than the window holds.

    ``neighbourhood_reference`` (optional) records a supplied reference the derived
    dimensions were recomputed against (``{"source", "n_words", "sha256",
    "applied_to"}``, where ``applied_to`` lists the recomputed columns), verbatim.

    ``counterbalance_check`` (optional) is the pipeline's ``counterbalance_check``
    report on the counterbalanced table. Without it, the check is run here on
    ``stimuli``. The record gives the recipe that ran and the lists the table holds,
    or for a table without a ``list`` column the lists counterbalance() would deal. It
    says whether a Latin-square rotation is complete and counts the trials per list
    and condition. It also gives the presentation versions, one per (replicate, list)
    pair, and the rule that assigns each participant one of them.

    ``input_normalisation`` (optional) is ``{"changed", "collapsed"}``: how many text
    keys the run's inputs held that Unicode NFC normalisation rewrote, and how many
    duplicates the rewriting created and removed. Recorded only when given, which the
    pipeline does only when either count is above zero, because a merged spelling
    changes the candidate pool.

    ``artifacts`` names the files written for the design: ``stimuli``,
    ``descriptives``, ``comparisons`` and ``experiments``, the result of
    ``export_experiments``. Each file is recorded with its sha256: the three tables,
    then every file in ``experiments["files"]``, the loop and text tables included,
    or the three experiment paths of a result that has no ``files``.

    ``generation_exclude`` (optional, generated designs) lists the known-form lists
    of ``items.generation.exclude`` as ``{"source", "sha256", "n_forms"}`` records.
    A pseudoword was refused for equalling any form in them, so they decide which
    pseudowords a run produces, as the lexicon does.
    """
    source = (design.get("items") or {}).get("source", "corpus")
    is_continuous = _is_continuous(design)
    controlled = _controlled(design, source)
    relational = _relational_record(design, stimuli)
    conditions = list(dict.fromkeys(stimuli["condition"]))
    # The response windows the generated experiments open, and with them where a
    # reaction time starts, which the analysis has to know.
    events = resolve_events(design)
    windows = _response_windows(events, design.get("timing") or {}, _refresh_hz(schema))
    incomplete = (selection_audit or {}).get("incomplete_dropped") or []
    dropped = {d["condition"]: int(d["n"]) for d in incomplete}

    realised = []
    if report is not None:
        for _, r in report["comparisons"].iterrows():
            if is_continuous:
                realised.append({
                    "dimension": r["dimension"], "role": r["role"],
                    "pearson_r": _num(r.get("pearson_r")),
                    "predictor_span": _num(r.get("predictor_span")),
                })
            else:
                realised.append({
                    "dimension": r["dimension"],
                    "role": "controlled" if r["dimension"] in controlled else "manipulated/free",
                    "cohens_d": _num(r["cohens_d"]),
                    "ci_low": _num(r.get("d_ci_low")), "ci_high": _num(r.get("d_ci_high")),
                    "var_ratio": _num(r.get("var_ratio")),
                    "tost_p": _num(r.get("tost_p")), "equivalent": _bool(r.get("equivalent")),
                })

    if is_continuous:
        # The controls are banded by the same tolerance windows the matcher uses, so
        # the record states them here too; without them the banding is unreproducible.
        selection = {"method": "continuous even-spread (predictor spanned, controls banded)",
                     "predictor": design["continuous"]["predictor"],
                     "controls": list(design["continuous"].get("controls") or []),
                     "tolerance_k": _resolve_tolerance_k(design, schema)}
    elif source in ("corpus", "pool"):
        method = ((design.get("matching") or {}).get("method")
                  or (schema.get("matching") or {}).get("method")
                  or "standardised_euclidean")
        selection = {"method": method, "match_on": controlled}
        if method in ("joint", "optimal"):
            # The pairwise methods rank whole pairs and never consult the tolerance
            # windows; recording tolerance_k here would claim a filter that was not
            # applied. They get the cap they do apply instead, with a per-condition
            # verdict on whether it fired. The candidates excluded for a missing
            # matched value never reach the cap, so the verdict counts the rest.
            selection["candidate_cap"] = {
                "cap": int(PAIRWISE_CAP),
                "applied": {c["condition"]: bool(c["n_candidates"]
                                                 - dropped.get(c["condition"], 0)
                                                 > PAIRWISE_CAP)
                            for c in (candidate_pool or [])
                            if c.get("condition") is not None
                            and c.get("n_candidates") is not None},
            }
        else:
            selection["tolerance_k"] = _resolve_tolerance_k(design, schema)
        # Exact ties decide most picks when the matched dimensions are whole numbers, so
        # the rule that broke them is part of the selection. The salt goes with the
        # hash, which makes every tie key recomputable from the record.
        rule = _resolve_tie_break(design, schema)
        selection["tie_break"] = ({"rule": rule, "salt": TIE_SALT} if rule == "hash"
                                  else {"rule": rule})
    elif source == "generate":
        gen_method = ((design.get("items") or {}).get("generation") or {}).get(
            "method", "letter_substitution")
        selection = {"method": _GENERATION_LABELS.get(
            gen_method, f"{gen_method} (deterministic pseudowords)"),
            "generation_method": gen_method,
            "matched_on": ["length"]}
    else:
        selection = {"method": "item table (user-supplied)"}
    if candidate_pool is not None and source in ("corpus", "pool", "generate"):
        selection["candidate_pool"] = candidate_pool
    # A pair-keyed continuous design does select, over the item table.
    selection["cross_engine"] = _cross_engine(
        selection.get("method"), source, selected=is_continuous and relational is not None)
    # A relaxed window changes what "matched" means for that condition, so the
    # matcher's audit trail belongs in the record, not only in the run narration.
    # Integers only, so both engines serialise the counts identically.
    relaxations = (selection_audit or {}).get("window_relaxations") or []
    if relaxations:
        selection["window_relaxations"] = [
            {"condition": r["condition"],
             "n_within_tolerance": int(r["n_within_tolerance"]),
             "n_needed": int(r["n_needed"])} for r in relaxations]
    # The candidates excluded for missing a matched dimension, which candidate_pool
    # still counts: the selection drew on a smaller pool than the windows hold.
    if incomplete:
        selection["incomplete_dropped"] = [
            {"condition": d["condition"], "n": int(d["n"])} for d in incomplete]
    if neighbourhood_reference is not None:
        selection["neighbourhood_reference"] = neighbourhood_reference
    if generation_exclude and source == "generate":
        selection["generation_exclude"] = [
            {"source": r["source"], "sha256": r["sha256"], "n_forms": int(r["n_forms"])}
            for r in generation_exclude]

    if source in ("corpus", "generate"):
        provenance = ("wordfreq (Speer, 2022), data CC BY-SA 4.0; full corpus licence "
                      "and citation at https://github.com/pablobernabeu/lexsync/blob/"
                      "main/corpora/ATTRIBUTION.md")
    elif source == "pool":
        provenance = "user-supplied word pool, matched by lexsync"
    else:
        provenance = "user-supplied item table"
    materials_source = {
        "type": source, "path": _posix(source_path), "sha256": sha256_file(source_path),
        "provenance": provenance,
    }
    # A supplied pool usually draws its dimensions from a corpus lexicon, and that
    # lexicon is where every matched value came from, so it is named and checksummed
    # here: `path` above records only the word list itself.
    if source == "pool":
        dim_lex = (design.get("items") or {}).get("lexicon") or design.get("lexicon")
        materials_source["dimensions_from"] = (
            dim_lex if dim_lex else "the supplied pool's own columns (no lexicon given)")
        if dim_lex:
            materials_source["dimensions_sha256"] = sha256_file(dim_lex)
    # Added only when present, so a design with no `norms:` block gets no key at all
    # rather than a "norms": null that every datasheet would then carry. Matches the R
    # engine, where assigning NULL to a list element removes it.
    if norms:
        materials_source["norms"] = norms
    if input_normalisation is not None:
        materials_source["input_normalisation"] = {
            "changed": int(input_normalisation["changed"]),
            "collapsed": int(input_normalisation["collapsed"])}

    # A corpus design draws on every schema dimension, and so does a pair-keyed
    # design: every lexicon dimension is joined onto each member. A generate or plain
    # table design reports only the ones it controlled, so the record does not claim
    # dimensions that played no part in the selection.
    all_dims = source in ("corpus", "pool") or relational is not None
    # `or {}`, not a default argument, for the reason load_lexicon carries the same
    # guard: an empty `dimensions:` key parses to None here, which is not iterable,
    # while the R twin's schema$dimensions[keep] returns NULL and the record simply
    # carries no dimensions.
    schema_dims = schema.get("dimensions") or {}
    dims = {d: schema_dims[d] for d in schema_dims if all_dims or d in controlled}

    # The recipe comes from the resolver counterbalance() dispatches on, and the lists
    # from the table. The record used to infer the recipe from the item source and to
    # copy counterbalance.lists with a default of 1, though a Latin square without
    # that key deals one list per condition.
    recipe = _recipe(design)
    check = (counterbalance_check if counterbalance_check is not None
             else _counterbalance_check(stimuli, design, recipe))
    versions = _version_count(stimuli, int(check["lists"]))
    counterbalancing = {
        "recipe": recipe,
        "lists": int(check["lists"]),
        "complete": bool(check["complete"]),
        "issues": list(check["issues"]),
        "cells": list(check["cells"]),
        "versions": versions,
        "assignment": (f"version = ((participant - 1) mod {versions}) + 1 unless a version "
                       "is given at launch"),
    }
    # The balance report is added only when the optimiser ran, for the same reason the
    # norms record is: a key that is null on every design that does not use the feature
    # is noise in a research artefact.
    if balance:
        counterbalancing["optimise"] = balance
    # Practice and filler trials change what a participant sees but not what is
    # analysed, so the record has to state both counts: a reader comparing the stimuli
    # file against the experiment would otherwise find them a different length with no
    # explanation.
    if blocks:
        counterbalancing["blocks"] = blocks

    # The equivalence settings the report's TOST verdicts were computed against,
    # recorded so the Methods prose can state the bound it actually ran with.
    equivalence = {"bound_d": (schema.get("equivalence") or {}).get("bound_d", 0.5),
                   "alpha": (schema.get("equivalence") or {}).get("alpha", 0.05)}

    reproducibility = {"seed": seed, "versions": _versions(engine)}
    # The design and schema decide everything the seed does not, so their checksums
    # complete the reproducibility record when the pipeline names them.
    if design_path is not None:
        reproducibility["design_sha256"] = sha256_file(design_path)
    if schema_path is not None:
        reproducibility["schema_sha256"] = sha256_file(schema_path)

    return {
        "lexsync_datasheet_version": DATASHEET_VERSION,
        "design": {
            "name": design["name"], "language": design["language"],
            "paradigm": design.get("paradigm", "factorial"), "source": source,
            "description": design.get("description"),
            "n_per_condition": design.get("n_per_condition") or design.get("n_per_cell"),
        },
        "materials_source": materials_source,
        "dimensions": dims,
        "selection": selection,
        "relational": relational,
        "analysis": _analysis(design, source, _response_text(windows, events)),
        "equivalence": equivalence,
        "realised_control": realised,
        "counterbalancing": counterbalancing,
        "presentation": {"response_windows": windows},
        "resampling": ({"n_sets": (design.get("resample") or {}).get("n_sets"),
                        "disjoint": True} if design.get("resample") else None),
        "items": {
            "n_total": int(len(stimuli)), "n_conditions": len(conditions),
            "conditions": conditions,
            "stimuli_file": _posix(artifacts.get("stimuli")),
            "stimuli_sha256": sha256_file(artifacts.get("stimuli")),
        },
        "reproducibility": reproducibility,
        "artifacts": [{"file": _posix(p), "sha256": sha256_file(p)}
                      for p in _artifact_paths(artifacts) if p],
    }


def _posix(path):
    """Record a path in POSIX form, as R's file.path() already produces.

    os.path.join gives backslashes on Windows, which would make the datasheet, a
    record meant to travel with the materials and be read anywhere, describe the
    machine that happened to build it, and disagree with the R engine's record of the
    same file.
    """
    return path.replace("\\", "/") if isinstance(path, str) else path


def _artifact_paths(artifacts: dict) -> list:
    """The files the record checksums: the three tables, then every experiment file.

    ``export_experiments`` lists every file it wrote under ``files``, the loop and text
    tables that hold the trial order and the trigger codes among them. A result without
    ``files`` contributes its three experiment paths. Mirrors .artifact_paths in
    datasheet.R.
    """
    paths = [artifacts.get(k) for k in ("stimuli", "descriptives", "comparisons")]
    exps = artifacts.get("experiments") or {}
    files = exps.get("files")
    paths += list(files) if files is not None else list(exps.values())
    return paths


def _version_count(stimuli, lists: int) -> int:
    """The presentation versions the trials give, one per (replicate, list) pair.

    A table without a ``list`` column has the lists counterbalance() would deal in
    each replicate, ``lists`` of them, as the record's ``lists`` does. Mirrors
    .version_count in datasheet.R.
    """
    if "list" in stimuli.columns:
        return len(presentation_versions(stimuli))
    replicates = int(stimuli["replicate"].nunique()) if "replicate" in stimuli.columns else 1
    return max(replicates, 1) * int(lists)


def _versions_note(ds: dict) -> str:
    """How participants met the presentation versions, for the Methods text.

    Empty for a single version, and for a record written before the field existed.
    Mirrors .versions_note in datasheet.R.
    """
    n = (ds.get("counterbalancing") or {}).get("versions")
    if not n or n < 2:
        return ""
    unit = ("presentation versions (one list of one item set)" if ds.get("resampling")
            else "lists")
    return (f" Each participant was presented one of the {n} {unit}, assigned in rotation "
            "by participant number.")


def _num(v):
    try:
        return None if v is None or v != v else _round_dp(float(v), 4)
    except (TypeError, ValueError):
        return None


def _fmt_tost_p(p) -> str:
    """The TOST p as the Markdown shows it.

    Four places, the precision the comparisons report stores, through _fmt_dp like
    every other number. It was printed raw, so this engine wrote 0.0009 and 1.0 where
    R wrote 9e-04 and 1. A p that rounds to zero at four places is shown as the bound
    it is below. Mirrors .fmt_tost_p in datasheet.R.
    """
    s = _fmt_dp(p, 4)
    return "< 0.0001" if s == "0.0000" else s


def _bool(v):
    return None if v is None or (isinstance(v, float) and v != v) else bool(v)


def _norms_note(ds: dict) -> str:
    """The norm tables named in the Methods prose.

    Basenames only: the full paths and checksums are in the datasheet, and a paper's
    Methods section wants the source, not the directory it happened to sit in on one
    machine. Mirrors .norms_note in datasheet.R.
    """
    norms = (ds.get("materials_source") or {}).get("norms")
    if not norms:
        return ""
    files = ", ".join(str(t["path"]).replace("\\", "/").rsplit("/", 1)[-1] for t in norms)
    return (" Norm dimensions were joined from %s, whose checksums and per-column "
            "coverage are recorded in the datasheet." % files)


def _known_forms_note(ds: dict) -> str:
    """The known-form lists a generated design checked its pseudowords against, for the
    Methods prose, by basename like the norm tables. Empty when it named none. Mirrors
    .known_forms_note in datasheet.R.
    """
    recs = (ds.get("selection") or {}).get("generation_exclude") or []
    if not recs:
        return ""
    parts = ["%d known word form%s (%s)"
             % (r["n_forms"], "" if r["n_forms"] == 1 else "s",
                str(r["source"]).replace("\\", "/").rsplit("/", 1)[-1]) for r in recs]
    listed = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]
    return ". Besides the lexicon, pseudowords were checked against " + listed


def _recipe_label(cb: dict) -> str:
    """The counterbalancing recipe as the Methods text names it.

    A Latin square the check found incomplete is called incomplete, since the bare
    label would claim a rotation the lists or the item sets did not complete. A
    record without the check, written before datasheet 1.2, keeps the bare label.
    Mirrors .recipe_label in datasheet.R.
    """
    if cb["recipe"] == "latin_square_target":
        return ("an incomplete Latin-square rotation" if cb.get("complete") is False
                else "a Latin-square rotation")
    return {"factorial": "a factorial split"}.get(cb["recipe"], cb["recipe"])


def methods_paragraph(ds: dict) -> str:
    """A ready-to-adapt Methods paragraph rendered from a datasheet.

    Every number in the paragraph is printed by lexsync's own formatter, rounded
    half away from zero from the value the datasheet stores, so the R and Python
    engines write the same text from the same record, a record read back from its
    JSON included. Mirrors methods_paragraph in datasheet.R.
    """
    d = ds["design"]
    src = ds["materials_source"]["type"]
    n = d["n_per_condition"]
    lang = d["language"].capitalize()
    sel = ds.get("selection") or {}
    # What was selected. A pair design's unit is the pair, and its `n_per_condition`
    # counts pairs, so calling them "items" would misreport the size of the materials
    # by a factor of the number of conditions.
    rel = ds.get("relational")
    unit = "items" if not rel else "-".join(rel["members"]) + " pairs"
    if "predictor" in sel:
        predictor = sel["predictor"]
        controls = ", ".join(sel.get("controls") or []) or "the control dimensions"
        rc = ds.get("realised_control") or []
        span = next((r.get("predictor_span") for r in rc if r.get("predictor_span") is not None), None)
        rs = [abs(r["pearson_r"]) for r in rc
              if r.get("pearson_r") is not None and r["pearson_r"] == r["pearson_r"]]
        span_str = f" (a span of {_fmt_dp(span, 2)})" if span is not None else ""
        # |r| is printed at three places, the precision of the comparisons report it
        # comes from (the record keeps up to four, see _num), so the record holds the
        # digit shown. _fmt_dp prints it, as every number here, because R's sprintf()
        # rounds a tie such as 0.0825 to 0.082 on Windows where this engine gives 0.083.
        corr_str = (", and the largest predictor-control correlation was |r| = "
                    + _fmt_dp(max(rs), 3) if rs else "")
        cb = ds["counterbalancing"]
        recipe_label = _recipe_label(cb)
        return (f"{n} {lang} {unit} were selected to span {predictor}{span_str} continuously "
                f"while holding {controls} near-constant{corr_str}, for analysis by regression "
                f"or a mixed model rather than a between-condition contrast (Kuperman, 2015; "
                f"Liben-Nowell et al., 2019).{_norms_note(ds)} Materials were counterbalanced "
                f"into {cb['lists']} list(s) ({recipe_label}) and generated for PsychoPy, "
                f"OpenSesame and jsPsych.{_versions_note(ds)}{_response_note(ds)} The "
                f"selection is deterministic and reproducible (lexsync "
                f"{ds['reproducibility']['versions']['lexsync']}), and the seed "
                f"({ds['reproducibility']['seed']}) fixes the trial order.")
    if src == "corpus":
        ctrl = ", ".join(ds["selection"]["match_on"]) or "the control dimensions"
        lead = (f"{n} items per condition were selected from the {lang} lexicon "
                f"({ds['materials_source']['provenance']}) and matched item by item on "
                f"{ctrl} using lexsync's {ds['selection']['method']} matcher")
    elif src == "pool":
        # A supplied pool is matched exactly as a corpus is; what differs, and what the
        # Methods section has to say, is that the candidate words were chosen by the
        # researcher rather than drawn from the whole lexicon.
        ctrl = ", ".join(ds["selection"]["match_on"]) or "the control dimensions"
        lead = (f"{n} {lang} items per condition were selected from a supplied candidate "
                f"pool and matched item by item on {ctrl} using lexsync's "
                f"{ds['selection']['method']} matcher, with the matched dimensions taken "
                f"from {ds['materials_source']['dimensions_from']}")
    elif src == "generate":
        lead = (f"{n} real {lang} words and {n} length-matched pseudowords "
                f"(generated by {ds['selection']['method']}) were assembled for a "
                f"lexical-decision contrast{_known_forms_note(ds)}")
    else:
        lead = (f"{ds['items']['n_total'] // max(1, ds['items']['n_conditions'])} items "
                f"were drawn from an item table for a {d['paradigm']} design ({lang})")
    ctrl_rows = [r for r in ds["realised_control"] if r["role"] == "controlled"]
    defined = [r for r in ctrl_rows if r["cohens_d"] is not None]
    control = ""
    if ctrl_rows:
        # Affirmative only when the stored verdicts support it: every controlled row
        # has a defined d and every one of them passed the TOST. An undefined d
        # (constant dimensions at different constants) is the worst possible failure
        # of the matching, not an excludable row.
        all_equivalent = (len(defined) == len(ctrl_rows)
                          and all(r.get("equivalent") is True for r in defined))
        if all_equivalent and defined:
            worst = max(defined, key=lambda r: abs(r["cohens_d"]))
            control = (f". The realised control was close. The largest standardised difference on "
                       f"any matched dimension was {_fmt_dp(worst['cohens_d'], 2)} "
                       f"(90% CI [{_fmt_dp(worst['ci_low'], 2)}, "
                       f"{_fmt_dp(worst['ci_high'], 2)}]), within the "
                       f"{ds['equivalence']['bound_d']}-SD equivalence bound")
        else:
            control = (". Equivalence was not confirmed on every matched dimension; "
                       "the per-dimension differences are reported in the "
                       "realised-control table")
    rs = ds.get("resampling")
    resamp = (f". {rs['n_sets']} disjoint matched item sets were drawn, so items can be "
              f"treated as a random factor" if rs else "")
    cb = ds["counterbalancing"]
    recipe_label = _recipe_label(cb)
    tail = (resamp + f". Materials were counterbalanced into {cb['lists']} list(s) "
            f"({recipe_label}) and generated for PsychoPy, OpenSesame and "
            f"jsPsych.{_versions_note(ds)}{_response_note(ds)} The selection is "
            f"deterministic and reproducible (lexsync "
            f"{ds['reproducibility']['versions']['lexsync']}), and the seed "
            f"({ds['reproducibility']['seed']}) fixes the trial order.")
    cp = (ds.get("selection") or {}).get("candidate_pool")
    # The candidate pool counts the candidates excluded for a missing matched value,
    # which were never eligible, so they come off the count of the condition that
    # lost them. Mirrors methods_paragraph in datasheet.R.
    lost = {}
    for d in (ds.get("selection") or {}).get("incomplete_dropped") or []:
        lost[d["condition"]] = lost.get(d["condition"], 0) + int(d["n"])
    pool_note = ""
    if cp:
        sizes = [c["n_candidates"] - lost.get(c.get("condition"), 0) for c in cp
                 if c.get("n_candidates") is not None]
        if sizes:
            pool_note = (f". The smallest condition was selected from {min(sizes)} "
                         "eligible candidates, and the selection was deterministic and "
                         "blind to any outcome measure")
    cap_rec = (ds.get("selection") or {}).get("candidate_cap")
    cap_note = ""
    if cap_rec and any(cap_rec.get("applied", {}).values()):
        cap_note = (f". Each candidate pool exceeding the pairwise cap was reduced to "
                    f"the {int(cap_rec['cap'])} candidates nearest the other "
                    f"condition's centroid before pairing")
    ce_note = ""
    if str((ds.get("selection") or {}).get("cross_engine", "")).startswith("approximate"):
        ce_note = (". This design's matching method uses a covariance inverse or an "
                   "assignment solver, so the R and Python engines select equivalent "
                   "but not byte-identical materials")
    bal = (ds.get("counterbalancing") or {}).get("optimise")
    bal_note = "" if not bal else (
        ". Item sets were assigned to lists so as to equate the lists on %s rather than "
        "by an arbitrary deal, by a deterministic integer search (%d swap(s); imbalance "
        "reduced from %d to %d)"
        % (", ".join(bal["dimensions"]), bal["n_swaps"],
           bal["cost_before"], bal["cost_after"]))
    return lead + control + pool_note + cap_note + ce_note + bal_note + tail + _norms_note(ds)


def prereg_template(ds: dict) -> str:
    return (
        "## Pre-registration template\n\n"
        "*Auto-generated by lexsync. The Materials section is filled from the datasheet; "
        "complete the remaining sections before data collection.*\n\n"
        "### Study information\n- Title:\n- Authors:\n- Research questions:\n\n"
        "### Hypotheses\n- H1:\n\n"
        "### Design\n- Manipulated variable(s):\n- Measured variable(s):\n"
        f"- Paradigm: {ds['design']['paradigm']}\n\n"
        "### Materials (from the lexsync datasheet)\n" + methods_paragraph(ds) + "\n\n"
        "### Sampling plan\n- Sample size and justification:\n- Stopping rule:\n\n"
        "### Analysis plan\n- Statistical model: "
        + ds["analysis"]["suggested_model"] + "\n  (" + ds["analysis"]["note"] + ")\n"
        "- Inference criteria:\n"
        "- Treatment of items (e.g. items as a random factor):\n"
    )


def _transparency_note(ds: dict) -> str:
    """How the selection was made, as the Markdown's transparency section states it.

    Selection reads no seed, so the note names what it does depend on, and how exact
    ties were broken when the record gives the rule. It used to call the selection
    deterministic given the seed and free of item-selection bias, though the
    spelling tie-break skewed tied conditions towards early-alphabet words. Mirrors
    .transparency_note in datasheet.R.
    """
    rule = ((ds.get("selection") or {}).get("tie_break") or {}).get("rule")
    if rule == "hash":
        ties = (" Exact ties between equally close candidates are broken by a keyed hash "
                "of each word (salt %s), so no part of the alphabet is favoured."
                % ds["selection"]["tie_break"]["salt"])
    elif rule == "bytes":
        ties = (" Exact ties between equally close candidates are broken by spelling, in "
                "byte order, as lexsync 0.1 did, so every tie goes to the spelling that "
                "sorts first.")
    else:
        ties = ""
    return ("Selection is a deterministic function of the materials source, the design "
            "and the schema, blind to any outcome measure, and does not depend on the "
            "seed, which fixes the trial order." + ties + " Automating the choice "
            "removes the experimenter's discretion that Forster (2000) showed can bias "
            "item selection.")


def render_datasheet_md(ds: dict) -> str:
    d = ds["design"]
    lines = [f"# Materials datasheet — {d['name']} ({d['language']})", "",
             f"*lexsync datasheet v{ds['lexsync_datasheet_version']}; "
             f"{ds['reproducibility']['versions']['engine']} engine.*", "",
             "## Provenance", "",
             f"- **Paradigm:** {d['paradigm']}  |  **Item source:** {d['source']}",
             f"- **Description:** {d.get('description') or '--'}",
             f"- **Materials source:** `{ds['materials_source']['path']}` "
             f"(sha256 `{(ds['materials_source']['sha256'] or '')[:16]}…`)"]
    # Where a supplied pool's matched values came from. Without this the record names
    # only the word list, and the numbers every control rests on have no stated origin.
    # Appended here rather than inserted at an index, so the position stays right if a
    # line above it is ever added or removed.
    dim_from = (ds.get("materials_source") or {}).get("dimensions_from")
    if dim_from:
        dim_sha = (ds.get("materials_source") or {}).get("dimensions_sha256")
        lines.append("- **Dimensions from:** `%s`%s"
                     % (dim_from, "" if not dim_sha else " (sha256 `%s…`)" % dim_sha[:16]))
    nfc = (ds.get("materials_source") or {}).get("input_normalisation")
    if nfc:
        lines.append("- **Input normalisation:** %d text form(s) rewritten to Unicode NFC, "
                     "%d duplicate(s) removed" % (nfc["changed"], nfc["collapsed"]))
    # The known-form lists a generated design's pseudowords were checked against: they
    # decide which pseudowords the run produced, as the lexicon does.
    for r in (ds.get("selection") or {}).get("generation_exclude") or []:
        lines.append("- **Known word forms:** `%s` (%d forms, sha256 `%s…`)"
                     % (r["source"], r["n_forms"], (r.get("sha256") or "")[:16]))
    lines += [
        f"- **Selection:** {ds['selection']['method']}",
        f"- **Cross-engine determinism:** {ds['selection'].get('cross_engine', 'byte-identical')}",
        f"- **Counterbalancing:** {ds['counterbalancing']['recipe']}, "
        f"{ds['counterbalancing']['lists']} list(s)"]
    # Said only where there is a choice to make, so a single-version record reads as
    # it always has.
    if (ds["counterbalancing"].get("versions") or 1) > 1:
        lines.append(f"- **Presentation versions:** {ds['counterbalancing']['versions']}, "
                     f"assigned as {ds['counterbalancing']['assignment']}")
    lines += [
        f"- **Items:** {ds['items']['n_total']} rows across "
        f"{ds['items']['n_conditions']} conditions "
        f"({', '.join(ds['items']['conditions'])})",
        f"- **Seed:** {ds['reproducibility']['seed']}  |  **Versions:** "
        + ", ".join(f"{k} {v}" for k, v in ds["reproducibility"]["versions"].items()), ""]
    # Norm tables, with their checksums and coverage. A dimension covering only part of
    # the lexicon matters to a reader: the uncovered rows carry NaN and are dropped by
    # the tolerance windows, so coverage is part of how the pool was defined.
    nrm = (ds.get("materials_source") or {}).get("norms")
    if nrm:
        lines += ["## Joined norms", "",
                  "| File | Key | Column | Coverage | sha256 |", "|---|---|---|---|---|"]
        for t in nrm:
            for cl in t["columns"]:
                lines.append(f"| `{t['path']}` | {t['on']} | {cl['column']} | "
                             f"{cl['n_matched']} / {cl['n_total']} | "
                             f"`{(t.get('sha256') or '')[:16]}…` |")
        lines.append("")
    # Balance-aware list assignment. Reported because it decides which items each
    # participant sees, and the before/after costs are what make the claim checkable
    # rather than a bare assertion that the lists are balanced.
    bal = (ds.get("counterbalancing") or {}).get("optimise")
    if bal:
        lines += ["## Balanced list assignment", "",
                  "- **Balanced on:** " + ", ".join(bal["dimensions"]),
                  "- **Imbalance:** %d before, %d after, in %d swap(s)"
                  % (bal["cost_before"], bal["cost_after"], bal["n_swaps"]),
                  "- **Cost unit:** " + bal["cost_unit"],
                  ("- The search stopped at its pass bound rather than at a local "
                   "optimum, so a higher `counterbalance.max_passes` may balance the "
                   "lists further.") if bal.get("max_passes_reached") else
                  ("- The search ran to a local optimum: no single exchange of two item "
                   "sets between lists would reduce the imbalance further."),
                  ("- The search is a deterministic integer descent with a keyed-hash "
                   "tie-break, so it uses no random number generator and the R and "
                   "Python engines produce the same assignment."), ""]
    # The trials each list gives each condition, and whatever leaves a Latin-square
    # rotation incomplete, so a reader can check the rotation against the counts.
    # Mirrors render_datasheet_md in datasheet.R.
    cbk = ds.get("counterbalancing") or {}
    issues = cbk.get("issues") or []
    cells = cbk.get("cells") or []
    if issues or cells:
        lines += ["## Counterbalanced lists", ""]
        if issues:
            lines += ["- **Incomplete rotation:** " + issue for issue in issues] + [""]
        if cells:
            with_rep = any("replicate" in c for c in cells)
            lines += (["| Replicate | List | Condition | Trials |", "|---|---|---|---|"]
                      if with_rep else ["| List | Condition | Trials |", "|---|---|---|"])
            lines += [("| %s | " % c["replicate"] if with_rep else "| ")
                      + "%s | %s | %s |" % (c["list"], c["condition"], c["n_trials"])
                      for c in cells] + [""]
    rel = ds.get("relational")
    if rel:
        lines += ["## Pair-keyed items", "",
                  f"- **Members:** {', '.join(rel['members'])}  |  "
                  f"**Pairs:** {rel['n_pairs']}",
                  f"- **Member lexicon:** `{rel['member_lexicon']}` "
                  f"(sha256 `{(rel.get('member_lexicon_sha256') or '')[:16]}…`)",
                  "- **Member-level dimensions** (one word): "
                  + ", ".join(rel["member_dimensions"]),
                  "- **Relational dimensions** (the pair): "
                  + ", ".join(rel["relational_dimensions"]),
                  "- Selection ran on one row per pair and the result was re-expanded, so "
                  "every condition row of every chosen pair is present.", ""]
    cp = (ds.get("selection") or {}).get("candidate_pool")
    if cp:
        parts = ", ".join(f"{c['condition']}: {c['n_candidates']}" for c in cp
                          if "condition" in c and "n_candidates" in c)
        lines += ["## Selection transparency", "",
                  "- **Candidate pool** (items satisfying each condition's window before "
                  f"matching): {parts}.",
                  "- " + _transparency_note(ds), ""]
    if ds["realised_control"] and "predictor" in (ds.get("selection") or {}):
        lines += ["## Realised control (continuous predictor)", "",
                  "| Dimension | Role | r with predictor | Predictor span |",
                  "|---|---|---|---|"]
        for r in ds["realised_control"]:
            # A missing value prints "--", not an em dash: the R renderer's
            # placeholder, kept identical.
            lines.append(f"| {r['dimension']} | {r['role']} | "
                         f"{_fmt_dp(r.get('pearson_r'), 3)} | "
                         f"{_fmt_dp(r.get('predictor_span'), 3)} |")
        lines.append("")
    elif ds["realised_control"]:
        lines += ["## Realised control", "",
                  "| Dimension | Role | Cohen's d | 90% CI | Var ratio | TOST p | Equivalent |",
                  "|---|---|---|---|---|---|---|"]
        for r in ds["realised_control"]:
            # "--", not an em dash: the R renderer's placeholder, kept identical.
            # An undefined d (unequal constants) reaches every one of these cells.
            ci = (f"[{_fmt_dp(r['ci_low'], 2)}, {_fmt_dp(r['ci_high'], 2)}]"
                  if r["ci_low"] is not None else "--")
            lines.append(f"| {r['dimension']} | {r['role']} | {_fmt_dp(r['cohens_d'], 2)} | "
                         f"{ci} | {_fmt_dp(r.get('var_ratio'), 2)} | "
                         f"{_fmt_tost_p(r['tost_p'])} | {r['equivalent']} |")
        lines.append("")
    a = ds.get("analysis")
    if a:
        lines += ["## Suggested analysis", "",
                  f"- **Model:** `{a['suggested_model']}` — where the response is "
                  f"{a['response']}.",
                  f"- {a['note']}", ""]
    lines += ["## Methods paragraph", "", methods_paragraph(ds), "", prereg_template(ds)]
    return "\n".join(lines)


def _at_15_significant_digits(o):
    """Round every float in the record to 15 significant digits.

    The R engine writes this JSON with jsonlite, whose numeric precision is a single
    setting for the whole document; 15 significant digits (``digits = NA``) is R's full
    display precision and the closest common ground. Without this the two engines'
    records disagreed on any value that had not already been rounded on the way in.
    A `tolerance_k` of 1/9 was written to 16 digits here and 15 there, so a reader
    diffing the two records saw a difference that meant nothing.

    Fifteen digits is ample for a provenance record: every value in it either came from
    a human-written design file or was deliberately rounded to four places. The design
    file remains the authoritative source for an exact re-run.
    """
    if isinstance(o, float):
        return float("%.15g" % o)
    if isinstance(o, dict):
        return {k: _at_15_significant_digits(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_at_15_significant_digits(v) for v in o]
    return o


def write_datasheet(ds: dict, json_path: str, md_path: str) -> tuple:
    import os
    os.makedirs(os.path.dirname(json_path) or ".", exist_ok=True)
    with open(json_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(_at_15_significant_digits(ds), handle, indent=2, ensure_ascii=False,
                  sort_keys=True)
        handle.write("\n")
    with open(md_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(render_datasheet_md(ds) + "\n")
    return json_path, md_path
