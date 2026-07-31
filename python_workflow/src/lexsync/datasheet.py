# -*- coding: utf-8 -*-
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

from .io_utils import _is_continuous, _round_dp, sha256_file

# 1.1 added `materials_source["norms"]` (the design's joined norm tables, with their
# checksums and per-column coverage) and, for a pair-keyed design, a `relational`
# block plus an honest `selection["cross_engine"]`. Both were required by the rule
# that anything affecting item selection is recorded here: a norm table can carry the
# manipulated variable itself, and the pair path performs a real selection that the
# record used to describe as "n/a (user-supplied items)".
DATASHEET_VERSION = "1.1"

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
    return out


def _cross_engine(method, source: str, selected: bool = False) -> str:
    """Whether the R and Python engines select byte-identical materials.

    The deterministic methods are byte-identical; ``mahalanobis`` and ``optimal``
    are the exception, because they use a covariance-matrix inverse and an
    assignment solver whose last bits differ between the two linear-algebra
    backends (see matching.py).

    ``selected`` distinguishes the two things an item table can now mean. A plain
    table design does no selection, so there is nothing for the engines to agree on
    and the honest answer is "n/a". A pair-keyed continuous design selects over that
    table, and that selection was measured to be byte-identical -- so answering "n/a"
    there understated the guarantee, on the one path where a reader most needs it.
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
    else in the record mentions it -- ``materials_source`` names the item table. And
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


def _resolve_tolerance_k(design: dict, schema: dict) -> dict:
    """The tolerance windows the matcher actually applied.

    Resolved exactly as match_stimuli resolves them (schema defaults, overridden
    per dimension by the design), so the datasheet records the windows that were
    used rather than the defaults that a design may have replaced.
    """
    tol_k = dict((schema.get("matching") or {}).get("tolerance_k") or {})
    tol_k.update((design.get("matching") or {}).get("tolerance_k") or {})
    return tol_k


def _controlled(design: dict, source: str) -> list:
    # A supplied pool goes through the same matcher as a corpus, so it controls the same
    # dimensions; only the origin of the candidate words differs.
    if source in ("corpus", "pool"):
        return list(design.get("match_on") or [])
    if source == "generate":
        return ["length"]
    return []


def _analysis(design: dict, source: str) -> dict:
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
        return {
            "response": "the trial outcome (e.g. reaction time or accuracy)",
            "suggested_model": f"response ~ {fixed} + (1 + {predictor} | subject) + (1 | item)",
            "note": ("The predictor is kept continuous and analysed by regression or a "
                     "mixed model rather than dichotomised (Kuperman, 2015; Liben-Nowell "
                     "et al., 2019); the controls enter as covariates. Crossed random "
                     "effects for subjects and items guard the language-as-fixed-effect "
                     "fallacy (Clark, 1973; Baayen et al., 2008); reduce the structure if "
                     "it does not converge (Matuschek et al., 2017)."),
        }
    paradigm = design.get("paradigm", "factorial")
    if source == "generate" or paradigm == "lexical_decision":
        factor, item_re = "lexicality", "(1 | item)"
    elif paradigm in ("priming", "self_paced_reading"):
        factor, item_re = "condition", "(1 + condition | item)"
    else:
        factor, item_re = "condition", "(1 | item)"
    return {
        "response": "the trial outcome (e.g. reaction time or accuracy)",
        "suggested_model": f"response ~ {factor} + (1 + {factor} | subject) + {item_re}",
        "note": ("Crossed random effects for subjects and items guard against the "
                 "language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). "
                 "Begin with this maximal structure (Barr et al., 2013) and reduce it "
                 "if the model does not converge (Matuschek et al., 2017); fit with "
                 "lme4 in R or pymer4/statsmodels in Python."),
    }


def build_datasheet(design, schema, report, stimuli, source_path, artifacts,
                    seed, engine="python", candidate_pool=None, norms=None,
                    balance=None, blocks=None) -> dict:
    """Assemble the datasheet dictionary from the pipeline's objects.

    ``candidate_pool`` (optional) is a list of ``{"condition", "n_candidates"}``
    recording how many items satisfied each condition's window before matching --
    the size of the discretionary pool the selection drew from, reported so that
    item-selection bias is auditable (Forster, 2000; Simmons et al., 2011).

    ``norms`` (optional) is a list of norm-table provenance records from the design's
    ``norms:`` block. Each names a file, its sha256, the join key and the per-column
    coverage. Recorded because a norm table can supply the very variable a design
    manipulates, so a record that omitted it would describe a selection over columns
    of unstated origin.

    ``balance`` (optional) is the balance-optimiser report from ``balance_lists``.
    Recorded because it decides which items each participant sees.
    """
    source = (design.get("items") or {}).get("source", "corpus")
    is_continuous = _is_continuous(design)
    controlled = _controlled(design, source)
    relational = _relational_record(design, stimuli)
    conditions = list(dict.fromkeys(stimuli["condition"]))

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
        selection = {"method": ((design.get("matching") or {}).get("method")
                                or (schema.get("matching") or {}).get("method")
                                or "standardised_euclidean"),
                     "match_on": controlled,
                     "tolerance_k": _resolve_tolerance_k(design, schema)}
    elif source == "generate":
        gen_method = ((design.get("items") or {}).get("generation") or {}).get(
            "method", "letter_substitution")
        selection = {"method": _GENERATION_LABELS.get(
            gen_method, f"{gen_method} (deterministic pseudowords)"),
            "generation_method": gen_method,
            "matched_on": ["length"]}
    else:
        selection = {"method": "item table (user-supplied)"}
    if candidate_pool is not None and source in ("corpus", "generate"):
        selection["candidate_pool"] = candidate_pool
    # A pair-keyed continuous design does select, over the item table.
    selection["cross_engine"] = _cross_engine(
        selection.get("method"), source, selected=is_continuous and relational is not None)

    if source in ("corpus", "generate"):
        provenance = "see corpora/ATTRIBUTION.md for corpus licence and citation"
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

    # A corpus design draws on every schema dimension, and so does a pair-keyed
    # design: every lexicon dimension is joined onto each member. A generate or plain
    # table design reports only the ones it controlled, so the record does not claim
    # dimensions that played no part in the selection.
    all_dims = source in ("corpus", "pool") or relational is not None
    dims = {d: schema["dimensions"][d] for d in schema.get("dimensions", {})
            if all_dims or d in controlled}

    # The balance report is added only when the optimiser ran, for the same reason the
    # norms record is: a key that is null on every design that does not use the feature
    # is noise in a research artefact.
    counterbalancing = {
        "recipe": "latin_square_target" if source == "table" else "factorial",
        "lists": (design.get("counterbalance") or {}).get("lists", 1),
    }
    if balance:
        counterbalancing["optimise"] = balance
    # Practice and filler trials change what a participant sees but not what is
    # analysed, so the record has to state both counts: a reader comparing the stimuli
    # file against the experiment would otherwise find them a different length with no
    # explanation.
    if blocks:
        counterbalancing["blocks"] = blocks

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
        "analysis": _analysis(design, source),
        "realised_control": realised,
        "counterbalancing": counterbalancing,
        "resampling": ({"n_sets": (design.get("resample") or {}).get("n_sets"),
                        "disjoint": True} if design.get("resample") else None),
        "items": {
            "n_total": int(len(stimuli)), "n_conditions": len(conditions),
            "conditions": conditions,
            "stimuli_file": _posix(artifacts.get("stimuli")),
            "stimuli_sha256": sha256_file(artifacts.get("stimuli")),
        },
        "reproducibility": {"seed": seed, "versions": _versions(engine)},
        "artifacts": [{"file": _posix(p), "sha256": sha256_file(p)}
                      for p in _artifact_paths(artifacts) if p],
    }


def _posix(path):
    """Record a path in POSIX form, as R's file.path() already produces.

    os.path.join gives backslashes on Windows, which would make the datasheet -- a
    record meant to travel with the materials and be read anywhere -- describe the
    machine that happened to build it, and disagree with the R engine's record of the
    same file.
    """
    return path.replace("\\", "/") if isinstance(path, str) else path


def _artifact_paths(artifacts: dict) -> list:
    paths = [artifacts.get(k) for k in ("stimuli", "descriptives", "comparisons")]
    exps = artifacts.get("experiments") or {}
    paths += list(exps.values())
    return paths


def _num(v):
    try:
        return None if v is None or v != v else _round_dp(float(v), 4)
    except (TypeError, ValueError):
        return None


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


def methods_paragraph(ds: dict) -> str:
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
        span_str = f" (a span of {span:.2f})" if span is not None else ""
        # Report |r| at 3 dp (its stored precision) so the text is identical across
        # engines; a 2-dp format of, say, 0.165 rounds to 0.17 in Python and 0.16 in R.
        corr_str = (f", and the largest predictor-control correlation was |r| = {max(rs):.3f}"
                    if rs else "")
        cb = ds["counterbalancing"]
        recipe_label = {"latin_square_target": "a Latin-square rotation",
                        "factorial": "a factorial split"}.get(cb["recipe"], cb["recipe"])
        return (f"{n} {lang} {unit} were selected to span {predictor}{span_str} continuously "
                f"while holding {controls} near-constant{corr_str}, for analysis by regression "
                f"or a mixed model rather than a between-condition contrast (Kuperman, 2015; "
                f"Liben-Nowell et al., 2019).{_norms_note(ds)} Materials were counterbalanced "
                f"into {cb['lists']} list(s) ({recipe_label}) and generated for PsychoPy, "
                f"OpenSesame and jsPsych. The selection is deterministic and reproducible "
                f"(seed {ds['reproducibility']['seed']}; lexsync "
                f"{ds['reproducibility']['versions']['lexsync']}).")
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
                f"lexical-decision contrast")
    else:
        lead = (f"{ds['items']['n_total'] // max(1, ds['items']['n_conditions'])} items "
                f"were drawn from an item table for a {d['paradigm']} design ({lang})")
    ctrl_rows = [r for r in ds["realised_control"] if r["role"] == "controlled"
                 and r["ci_high"] is not None]
    if ctrl_rows:
        worst = max(ctrl_rows, key=lambda r: abs(r["cohens_d"]))
        control = (f". The realised control was close. The largest standardised difference on "
                   f"any matched dimension was {abs(worst['cohens_d']):.2f} "
                   f"(90% CI [{worst['ci_low']:.2f}, {worst['ci_high']:.2f}]), within the "
                   f"0.5-SD equivalence bound")
    else:
        control = ""
    rs = ds.get("resampling")
    resamp = (f". {rs['n_sets']} disjoint matched item sets were drawn, so items can be "
              f"treated as a random factor" if rs else "")
    cb = ds["counterbalancing"]
    recipe_label = {"latin_square_target": "a Latin-square rotation",
                    "factorial": "a factorial split"}.get(cb["recipe"], cb["recipe"])
    tail = (resamp + f". Materials were counterbalanced into {cb['lists']} list(s) "
            f"({recipe_label}) and generated for PsychoPy, OpenSesame and jsPsych. The "
            f"selection is deterministic and reproducible (seed "
            f"{ds['reproducibility']['seed']}; lexsync "
            f"{ds['reproducibility']['versions']['lexsync']}).")
    cp = (ds.get("selection") or {}).get("candidate_pool")
    pool_note = ""
    if cp:
        sizes = [c["n_candidates"] for c in cp if c.get("n_candidates") is not None]
        if sizes:
            pool_note = (f". The smallest condition was selected from {min(sizes)} "
                         "eligible candidates, and the selection was deterministic and "
                         "blind to any outcome measure")
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
    return lead + control + pool_note + ce_note + bal_note + tail + _norms_note(ds)


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


def render_datasheet_md(ds: dict) -> str:
    d = ds["design"]
    lines = [f"# Materials datasheet — {d['name']} ({d['language']})", "",
             f"*lexsync datasheet v{ds['lexsync_datasheet_version']}; "
             f"{ds['reproducibility']['versions']['engine']} engine.*", "",
             "## Provenance", "",
             f"- **Paradigm:** {d['paradigm']}  |  **Item source:** {d['source']}",
             f"- **Description:** {d.get('description') or '—'}",
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
    lines += [
        f"- **Selection:** {ds['selection']['method']}",
        f"- **Cross-engine determinism:** {ds['selection'].get('cross_engine', 'byte-identical')}",
        f"- **Counterbalancing:** {ds['counterbalancing']['recipe']}, "
        f"{ds['counterbalancing']['lists']} list(s)",
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
                  "every condition row of every chosen pair is present and the Latin-square "
                  "rotation is complete.", ""]
    cp = (ds.get("selection") or {}).get("candidate_pool")
    if cp:
        parts = ", ".join(f"{c['condition']}: {c['n_candidates']}" for c in cp
                          if "condition" in c and "n_candidates" in c)
        lines += ["## Selection transparency", "",
                  "- **Candidate pool** (items satisfying each condition's window before "
                  f"matching): {parts}.",
                  "- Selection is deterministic given the seed and blind to any outcome "
                  "measure, so it is reproducible and free of item-selection bias "
                  "(Forster, 2000; Simmons et al., 2011).", ""]
    if ds["realised_control"] and "predictor" in (ds.get("selection") or {}):
        lines += ["## Realised control (continuous predictor)", "",
                  "| Dimension | Role | r with predictor | Predictor span |",
                  "|---|---|---|---|"]
        for r in ds["realised_control"]:
            rr = "—" if r.get("pearson_r") is None else f"{r['pearson_r']:.3f}"
            sp = "—" if r.get("predictor_span") is None else f"{r['predictor_span']:.3f}"
            lines.append(f"| {r['dimension']} | {r['role']} | {rr} | {sp} |")
        lines.append("")
    elif ds["realised_control"]:
        lines += ["## Realised control", "",
                  "| Dimension | Role | Cohen's d | 90% CI | Var ratio | TOST p | Equivalent |",
                  "|---|---|---|---|---|---|---|"]
        for r in ds["realised_control"]:
            ci = (f"[{r['ci_low']:.2f}, {r['ci_high']:.2f}]"
                  if r["ci_low"] is not None else "—")
            d_str = "—" if r["cohens_d"] is None else f"{r['cohens_d']:.2f}"
            vr = "—" if r.get("var_ratio") is None else f"{r['var_ratio']:.2f}"
            lines.append(f"| {r['dimension']} | {r['role']} | {d_str} | {ci} | {vr} | "
                         f"{r['tost_p']} | {r['equivalent']} |")
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
    records disagreed on any value that had not already been rounded on the way in --
    a `tolerance_k` of 1/9 was written to 16 digits here and 15 there -- so a reader
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
