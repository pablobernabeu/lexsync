"""The pair-keyed item model.

Word-level norms joined onto each member of a prime-target pair, and continuous
selection over pairs rather than words.

Before this, a design could have matching or its own item table but never both: the
continuous selector consumed a word pool while ``items.source: table`` bypassed
selection entirely. A relational design needs both at once, because its predictor
(distributional similarity, associative strength) is a property of the pair while its
controls (frequency, length) are properties of each member.

Mirrors R_workflow/R/pairs.R.
"""
from __future__ import annotations

import pandas as pd

from .matching import select_continuous_stimuli
from .querying import build_pool, load_lexicon
from .validation import match_report_continuous

# Column names a member may not take. The engines read all of these directly, and
# R's `$` partial-matches on a data frame, so a joined `word.frequency` with no bare
# `word` present would make the selector's tie-break silently sort by it in R while
# this engine raised KeyError. Rejecting the name is cheaper than defending every
# read site. Must list the same names as pairs.R.
RESERVED_MEMBER_NAMES = ("word", "id", "set", "list", "trial", "condition",
                         "replicate", "item")


def _check_members(members, stim: pd.DataFrame) -> None:
    bad = sorted(set(members) & set(RESERVED_MEMBER_NAMES))
    if bad:
        raise ValueError(
            "lexsync: items.members may not use the reserved name(s) %s; the engines "
            "read those columns directly." % ", ".join("'%s'" % b for b in bad))
    missing = sorted(set(members) - set(stim.columns))
    if missing:
        raise ValueError(
            "lexsync: items.members name column(s) the item table does not have: %s."
            % ", ".join("'%s'" % m for m in missing))


def member_lexicon_path(items_cfg: dict, design: dict) -> str:
    """Where a pair design's member norms come from.

    Resolved here rather than inline so that run_pipeline, which loads the lexicon
    itself in order to apply the design's ``norms:`` block to it, asks the same
    question and reports the same error.
    """
    path = items_cfg.get("lexicon") or design.get("lexicon")
    if not path:
        raise ValueError(
            "lexsync: items.members needs a lexicon (items.lexicon or the design's "
            "lexicon) to draw norms from.")
    return path


def join_member_norms(stim: pd.DataFrame, members, items_cfg: dict, design: dict,
                      schema: dict, lex: pd.DataFrame | None = None) -> pd.DataFrame:
    """Join the lexicon's dimensions onto each member, as ``<member>.<dimension>``.

    The prefix leads deliberately. ``prime.frequency`` is safe because R's
    ``df$prime`` still exact-matches the bare ``prime`` column, whereas
    ``frequency.prime`` would be a partial-match hazard for any code reading
    ``df$frequency``.

    A member form absent from the lexicon is a hard error rather than an NA. An NA
    norm would be dropped by the control-window filter, which removes ROWS from a
    set, and a set missing one of its condition rows detonates the Latin square's
    completeness guard. Naming the first few offenders in byte order keeps the
    message deterministic across engines.

    ``lex`` is the already-loaded lexicon when the caller has one. run_pipeline
    passes it because it must apply the design's ``norms:`` block to that lexicon
    first and record where the norms came from; loading it here as well would read
    the file twice and, worse, would join the un-normed copy, so a semantic predictor
    named in ``norms:`` would silently be missing from the members.
    """
    _check_members(members, stim)
    lexicon = member_lexicon_path(items_cfg, design)
    if lex is None:
        lex = load_lexicon(lexicon, schema, language=design.get("language"))
    # `id` is a row identifier rather than a dimension; joining it would put a
    # meaningless `prime.id` in the stimuli file and in the datasheet.
    dims = [c for c in lex.columns if c not in ("word", "language", "source", "id")]

    keys = {m: [str(w).strip().lower() for w in stim[m]] for m in members}
    known = set(lex["word"])
    missing = sorted({w for m in members for w in keys[m]} - known)
    if missing:
        shown = missing[:5]
        raise ValueError(
            "lexsync: %d member form(s) are absent from lexicon '%s': %s%s."
            % (len(missing), lexicon, ", ".join("'%s'" % w for w in shown),
               ", ..." if len(missing) > len(shown) else ""))

    out = stim.copy()
    by_word = lex.set_index("word")
    for m in members:
        rows = by_word.loc[keys[m]]
        for d in dims:
            out["%s.%s" % (m, d)] = rows[d].to_numpy()
    return out


def select_continuous_pairs(stim: pd.DataFrame, items_cfg: dict, design: dict,
                            schema: dict, verbose: bool = False) -> dict:
    """Collapse a pair table to one row per set, select over it, then re-expand.

    The re-expansion is what keeps the Latin square valid. ``build_pool`` and the
    control windows filter ROWS, and a filter on ``prime.frequency`` would keep a
    pair's related row while dropping its unrelated one, leaving a set that has no
    row for one condition. So eligibility is decided at set granularity, selection
    runs on one row per set, and the result is re-expanded as a pure row subset of
    the original frame: every condition row of every surviving set is present, and no
    norm or relational value is recomputed and so none can drift.
    """
    cfg = design["continuous"]
    predictor = cfg["predictor"]
    controls = list(cfg.get("controls") or [])

    # build_pool silently skips a column it does not recognise, which on this path
    # would mean a mistyped filter quietly widening the selection.
    unknown = sorted(set((design.get("pool_filters") or {})) - set(stim.columns))
    if unknown:
        raise ValueError(
            "lexsync: pool_filters name column(s) the item table does not have: %s."
            % ", ".join("'%s'" % u for u in unknown))

    # Step A: a set is eligible only if EVERY one of its rows passes the filters.
    tagged = stim.copy()
    tagged["..lexsync_pair_row"] = range(len(tagged))
    passed = build_pool(tagged, design.get("pool_filters"))
    kept = set(passed["..lexsync_pair_row"])
    failed = {s for s, r in zip(tagged["set"], tagged["..lexsync_pair_row"], strict=True) if r not in kept}
    eligible = [s for s in dict.fromkeys(stim["set"]) if s not in failed]
    if not eligible:
        raise ValueError(
            "lexsync: no item set passes the pool filters on every one of its rows.")

    # Step B: collapse to the anchor condition. The default is the byte-first
    # condition, using the same sort the Latin square uses, so the two engines agree
    # without inventing a new convention.
    anchor_cond = items_cfg.get("anchor_condition") or sorted(
        {str(c) for c in stim["condition"]}, key=lambda s: s.encode("utf-8"))[0]
    elig = set(eligible)
    anchor = stim[[s in elig and str(c) == anchor_cond
                   for s, c in zip(stim["set"], stim["condition"], strict=True)]].reset_index(drop=True)
    dup = sorted({s for s in anchor["set"] if list(anchor["set"]).count(s) > 1})
    if dup:
        raise ValueError("lexsync: item set(s) %s have more than one '%s' row."
                         % (", ".join(str(s) for s in dup), anchor_cond))
    if len(anchor) != len(eligible):
        raise ValueError("lexsync: %d eligible item set(s) have no '%s' row."
                         % (len(eligible) - len(anchor), anchor_cond))

    # Step C: select over the collapsed frame. `set` is the tie-break: after the
    # collapse it is unique per row, it is an integer, and load_items already derived
    # it deterministically. No `word` column is needed anywhere on this path.
    sel = select_continuous_stimuli(anchor, design, schema, verbose=verbose,
                                    key="set", label=None, renumber_sets=False)

    # Step D: re-expand as a pure row subset, preserving the item table's own order.
    chosen = set(sel["set"])
    out = stim[[s in chosen for s in stim["set"]]].reset_index(drop=True)

    # Step E: report on the COLLAPSED frame. On the expanded one every target would
    # be counted once per condition, and the predictor-control correlations would be
    # computed over duplicated rows.
    report = match_report_continuous(sel, predictor, controls, schema)
    return {"stim": out, "report": report, "n_eligible": len(eligible)}
