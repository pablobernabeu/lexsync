"""Assign matched stimuli to lists and trial order, and build participant tables.

Mirrors R_workflow/R/counterbalancing.R. Two recipes are provided: the original
``factorial`` one (every matched item is shown, lists split the matched sets) and
``latin_square_target`` for paired/sentence paradigms (each item appears once per
list in one rotated condition, so a target is never repeated within a list). The
design's paradigm chooses between them, and ``counterbalance.recipe`` overrides it.
Trial order within a list comes from a seeded, keyed-hash shuffle, so the R and
Python engines produce the same order byte for byte. ``counterbalance_check``
reports a rotation that the lists or the item sets leave incomplete.
"""
from __future__ import annotations

import hashlib
import math
from itertools import product

import numpy as np
import pandas as pd

from .io_utils import _key_part
from .paradigms import get_paradigm

# The recipes counterbalance() knows, which counterbalance.recipe may name, and the
# policies counterbalance.incomplete accepts. Both are closed sets, so a misspelt
# value is refused, and the error names it.
RECIPES = ("factorial", "latin_square_target")
INCOMPLETE_POLICIES = ("allow", "error")


def _recipe(design: dict) -> str:
    """The recipe counterbalance() applies to a design.

    ``counterbalance.recipe`` when the design names one, else the recipe of the
    paradigm it names, else ``factorial``. An ``events`` list has no say in it. It
    used to switch the recipe to ``factorial``. A priming design that read its
    prime's duration from the items then showed every target in both conditions of
    each list, the repetition the paradigm's Latin square exists to prevent. The
    datasheet takes its recipe from here too, so the record names the recipe that
    ran. Mirrors .cb_recipe in R_workflow/R/counterbalancing.R.
    """
    # Read on presence, as R's %||% reads it, so an empty string is refused like any
    # other unknown name and never falls through to the paradigm.
    named = (design.get("counterbalance") or {}).get("recipe")
    if named is not None:
        if not isinstance(named, str) or named not in RECIPES:
            raise ValueError(f"lexsync: unknown counterbalance.recipe '{named}'. "
                             f"Known recipes: {', '.join(RECIPES)}.")
        return named
    name = design.get("paradigm", "factorial")
    try:
        return get_paradigm(name).get("counterbalance", "factorial")
    except ValueError:
        return "factorial"


def _incomplete_policy(design: dict, schema: dict) -> str:
    """Resolve ``counterbalance.incomplete``: the design's, else the schema's, else ``allow``.

    This is the cascade of matching.shortfall. Like R's %||%, it takes any value that
    is present, so the two engines resolve the same one. Mirrors
    .cb_incomplete_policy in R_workflow/R/counterbalancing.R.
    """
    val = (design.get("counterbalance") or {}).get("incomplete")
    if val is None:
        val = (schema.get("counterbalance") or {}).get("incomplete")
    if val is None:
        val = "allow"
    if not isinstance(val, str) or val not in INCOMPLETE_POLICIES:
        raise ValueError(f"lexsync: unknown counterbalance.incomplete policy '{val}'. "
                         f"Known policies: {', '.join(INCOMPLETE_POLICIES)}.")
    return val


def _default_lists(design: dict, recipe: str, n_cond: int) -> int:
    """The lists counterbalance() deals when the frame does not say: the declared
    ``counterbalance.lists``, else one per condition for a Latin square and one list
    for the factorial recipe."""
    lists = (design.get("counterbalance") or {}).get("lists")
    if lists is None:
        return n_cond if recipe == "latin_square_target" else 1
    return int(lists)


def counterbalance_check(stimuli: pd.DataFrame, design: dict, recipe: str | None = None,
                         conditions=None) -> dict:
    """Whether a counterbalanced table rotates its conditions completely.

    A Latin square is complete when every item takes each of its conditions in the
    same number of lists and every list holds each condition equally often. Four
    things break that, and each one is reported in a sentence that both engines word
    identically. One list shows every participant an item in the same condition,
    which confounds item and condition fully. Fewer lists than conditions leave each
    item out of some of its conditions. More lists than conditions, but not a
    multiple of them, give an item some conditions in more lists than others. And
    item sets that are not a multiple of the conditions leave the conditions within a
    list one trial apart. The factorial recipe raises none of these: it shows every
    item in every condition, and counterbalance() refuses lists it would leave empty.

    ``stimuli`` is the table counterbalance() returned. Without a ``list`` column, the
    lists are the ones counterbalance() would deal. ``conditions`` names the conditions
    the design rotates through, by default those the table holds. The pipeline passes
    them from the table it counterbalanced, since a Latin square with fewer item sets
    than conditions can leave a condition out of every list.

    Returns ``{"complete", "issues", "lists", "cells"}``. ``complete`` says whether no
    issue was found and ``issues`` gives the sentences. ``lists`` is the number of
    lists, and ``cells`` counts the trials in each cell of (replicate, when the table
    has one) by list by condition, empty cells included. Mirrors
    .counterbalance_check in R_workflow/R/counterbalancing.R.
    """
    recipe = recipe if recipe is not None else _recipe(design)
    source = stimuli["condition"] if conditions is None else conditions
    conds = sorted({str(c) for c in source}, key=lambda s: s.encode("utf-8"))
    n_cond = len(conds)
    has_list = "list" in stimuli.columns
    n_lists = (int(stimuli["list"].nunique()) if has_list
               else _default_lists(design, recipe, n_cond))
    has_rep = "replicate" in stimuli.columns
    parts = ([(int(r), g) for r, g in stimuli.groupby("replicate", sort=True)]
             if has_rep else [(None, stimuli)])

    issues = []
    if recipe == "latin_square_target" and n_cond > 1:
        if n_lists == 1:
            issues.append("With one list, every participant sees each item in the same "
                          "condition, so item and condition are fully confounded.")
        elif n_lists < n_cond:
            issues.append(f"With {n_lists} lists and {n_cond} conditions, each item "
                          f"appears in only {n_lists} of its {n_cond} conditions.")
        elif n_lists % n_cond:
            issues.append(f"With {n_lists} lists and {n_cond} conditions, the lists are "
                          "not a multiple of the conditions, so each item appears in some "
                          "conditions in more lists than in others.")
        # Each replicate is rotated on its own, so each is checked on its own.
        # Replicates of one size give one sentence between them.
        for _, part in parts:
            n_sets = int(part["set"].nunique())
            if n_sets % n_cond:
                issue = (f"With {n_sets} item {'set' if n_sets == 1 else 'sets'} and "
                         f"{n_cond} conditions, the item sets are not a multiple of the "
                         "conditions, so the conditions within each list differ by one "
                         "trial.")
                if issue not in issues:
                    issues.append(issue)

    cells = []
    if has_list:
        lists = sorted(int(v) for v in stimuli["list"].unique())
        for rep, part in parts:
            labels = part["condition"].astype(str)
            for lst in lists:
                in_list = part["list"] == lst
                for cond in conds:
                    cell = {"list": lst, "condition": cond,
                            "n_trials": int((in_list & (labels == cond)).sum())}
                    cells.append(cell if rep is None else {"replicate": rep, **cell})
    return {"complete": not issues, "issues": issues, "lists": n_lists, "cells": cells}


def _check_incomplete(check: dict, policy: str) -> None:
    """Refuse an incomplete rotation when counterbalance.incomplete is ``error``.

    Must stay identical to .check_incomplete in R_workflow/R/counterbalancing.R.
    """
    if check["complete"] or policy != "error":
        return
    raise ValueError("lexsync: the Latin-square rotation is incomplete and "
                     "counterbalance.incomplete is 'error'. " + " ".join(check["issues"])
                     + " Make the lists and the item sets multiples of the number of "
                     "conditions, or set counterbalance.incomplete: allow.")


def _shuffle_deterministic(df: pd.DataFrame, seed) -> pd.DataFrame:
    """Order the trials of one list by a keyed hash, not a random number generator.

    Each row is ranked by the SHA-256 digest of "seed|replicate|list|set|condition",
    a tuple that identifies the trial uniquely under either recipe. Distinct inputs
    to SHA-256 behave as independent uniform draws, so ordering by the digest
    realises a seeded random permutation, but as a pure function of the design: the
    same bytes from the R and Python engines on any platform, and a different order
    for every seed. R's sample() and numpy's PCG64 could never agree on a
    permutation, which used to be the one engine-specific artefact in an otherwise
    byte-identical pipeline. The replicate term keeps independently counterbalanced
    item sets from sharing one permutation pattern.
    """
    rep = df["replicate"] if "replicate" in df.columns else [0] * len(df)
    # Every component is formatted explicitly rather than interpolated. Default
    # stringification is where the two engines silently part company: R renders
    # the double 42 as "42" and Python as "42.0", and a pandas column is promoted
    # to float64 by a single missing value, which would change every digest, every
    # trial order and every generated artefact with nothing to signal it. The
    # values are integers today, so this changes no output; it removes a trap.
    ranks = [hashlib.sha256("|".join(
                 [_key_part(seed), _key_part(r), _key_part(l), _key_part(s), _key_part(c)]
             ).encode("utf-8")).hexdigest()
             for r, l, s, c in zip(rep, df["list"], df["set"], df["condition"], strict=True)]
    df = df.iloc[np.argsort(ranks, kind="stable")].copy()
    df["trial"] = np.arange(1, len(df) + 1)
    return df


# ---- Balance-aware list assignment (counterbalance.optimise) ----------------
#
# The factorial recipe deals item sets to lists by rank: set 1 to list 1, set 2 to
# list 2, and so on. That is reproducible but arbitrary with respect to the items
# themselves, so one list can end up holding systematically shorter or more frequent
# words than another. Where lists are given to different participants, that difference
# is confounded with the between-subjects factor.
#
# ``counterbalance.optimise: true`` searches for an assignment whose lists match on
# the declared dimensions instead. It is off by default: switching it on changes which
# items a participant sees, so it must be an explicit choice rather than something
# that happens to a design on upgrade.
#
# The search obeys the package's two hard rules, and both shape the code below more
# than is obvious.
#
# No RNG. The order of the search and every tie in it is decided by the seeded keyed
# hash already used for trial order, so the result is a pure function of the design.
#
# An ALL-INTEGER objective. This is not fastidiousness. Cohen's d computed in the two
# engines was measured to differ by about 3e-16 on average, which at nine decimal
# places leaves roughly a one-in-three chance over a full run that a comparison of two
# candidate swaps resolves differently in Python than in R -- and the failure is
# silent and total, different words rather than different last bits. The values are
# quantised to integers ONCE, and the search then uses only +, -, * and comparison.
# There is no division anywhere in the objective.
#
# Mirrors R_workflow/R/counterbalancing.R.

# Milli-units of a dimension's own mean, the scale every dimension is quantised to.
# Expressing all dimensions in one unit is what lets their imbalances be added without
# a per-dimension float weight: a word's length and its Zipf frequency differ by
# orders of magnitude in raw units, and summing raw deviations would silently optimise
# almost entirely for whichever dimension has the larger numbers.
#
# The constant is 1000 times the 100 that `unit` already carries (see _quantise_dim),
# so a value at the dimension's mean quantises to 1000. That factor is not cosmetic: at
# 1000 here, a value at the mean quantised to 10, which left only about ten
# distinguishable levels across a dimension's whole range, and imbalances smaller than
# a tenth of the mean were invisible to the objective. The search then traded away a
# dimension it could not see in order to improve one it could.
BALANCE_UNIT_SCALE = 100000

# Guard on the objective's magnitude. Python ints are arbitrary precision, but the R
# engine holds these as doubles and is exact only below 2^53; the bound is shared so
# both engines refuse the same designs rather than one of them silently rounding.
# Nothing near this is reachable with realistic designs.
BALANCE_MAX_MAGNITUDE = 2 ** 50


def _balance_dims(design: dict) -> list:
    cb = design.get("counterbalance") or {}
    dims = list(cb.get("balance_on") or [])
    if not dims:
        dims = list(design.get("match_on") or [])
    if not dims and design.get("continuous"):
        dims = [design["continuous"]["predictor"]] + list(
            design["continuous"].get("controls") or [])
    seen, out = set(), []
    for d in dims:
        if str(d) not in seen:
            seen.add(str(d))
            out.append(str(d))
    return out


def _quantise_dim(values, name: str) -> list:
    """Quantise one dimension to integers in milli-units of its own mean.

    The only floating-point steps in the whole optimiser are here, and each is a
    single IEEE operation that the standard requires to be correctly rounded, so both
    engines hold the same double before it is truncated. Truncation of a double is
    exact, so no rounding mode is involved. ``round`` would have agreed on every case
    measured, but truncation removes the question rather than answering it.

    The mean is computed from INTEGER counts, never as a float sum: summing 20000
    doubles was measured to give three different answers across R's sum(),
    math.fsum, numpy's pairwise sum and a naive loop, so a float mean here could put
    the two engines on different search paths from the first step.
    """
    vals = [float(v) for v in values]
    if any(v != v for v in vals):
        raise ValueError(
            "lexsync: dimension '%s' has missing values, so it cannot be balanced "
            "across lists. Fill or drop those items." % name)
    # math.trunc, guarded on finiteness, rather than a bare int(): int(inf) raises
    # OverflowError with a message of Python's own, where R's trunc(Inf) is Inf and
    # reaches the size refusal below. Truncating BEFORE the comparison, as the R twin
    # does, so the two engines refuse exactly the same values.
    scaled = [math.trunc(s) if math.isfinite(s) else s
              for s in (abs(v) * 100 for v in vals)]
    if max(scaled, default=0) > 2 ** 31 - 1:
        raise ValueError(
            "lexsync: dimension '%s' has values too large to balance on." % name)
    unit = max(1, sum(scaled) // len(scaled))
    return [int(v * BALANCE_UNIT_SCALE / unit) for v in vals]


def _balance_values(stimuli: pd.DataFrame, dims: list) -> dict:
    """One integer per set per dimension: the set's total, because a list receives
    whole sets. Rows are grouped by set in sorted order so both engines build the
    same matrix from the same frame."""
    sets = sorted(stimuli["set"].unique())
    V = {}
    for d in dims:
        q = _quantise_dim(stimuli[d], d)
        by_set = {s: 0 for s in sets}
        for s, qv in zip(stimuli["set"], q, strict=True):
            by_set[s] += qv                          # exact integer sum
        V[d] = [by_set[s] for s in sets]
    return V


def _balance_cost(V: dict, assign: list, n_lists: int, n_sets: int) -> int:
    """Total absolute deviation of each list's dimension total from its fair share,
    scaled by the number of sets so the fair share stays an integer. Every term is an
    exact integer; there is no division."""
    cost = 0
    for vals in V.values():
        total = sum(vals)
        for l in range(1, n_lists + 1):
            s = sum(v for v, a in zip(vals, assign, strict=True) if a == l)
            n_in = sum(1 for a in assign if a == l)
            cost += abs(s * n_sets - total * n_in)
    return cost


def balance_lists(stimuli: pd.DataFrame, design: dict, schema: dict) -> dict:
    """Assign item sets to lists so the lists match on the item dimensions.

    The factorial recipe's default deal is by set rank, which balances nothing. This
    searches instead for an assignment whose lists have near-equal totals on each
    declared dimension, by steepest-descent pairwise swaps between lists. List sizes
    are preserved, because a swap exchanges one set for another.

    The search is deterministic and identical in the R and Python engines: the
    objective is all-integer (see the notes in this module), the descent takes the
    single best swap each pass, and ties are broken by the seeded keyed hash rather
    than by position, so no list is favoured by being numbered first. Because the cost
    is a non-negative integer that strictly decreases, the search terminates;
    ``max_passes`` bounds it anyway and the report says whether the bound was reached.

    Five situations raise ``ValueError`` rather than being answered with an assignment
    that would mislead. A Latin-square design is refused because every item already
    appears in every list there, so there is nothing left to equate, and fewer than two
    lists leaves no pair of lists to exchange sets between. A design with no resolvable
    balance dimension is refused, as is one naming a dimension the stimuli do not carry,
    and the message names the columns. The last refusal is arithmetic: the search stops
    if the integer objective would leave the range a double represents exactly, since
    past that point the two engines could disagree.

    Returns ``{"list_of_set": {set: list}, "report": {...}}``.
    """
    cb = design.get("counterbalance") or {}
    n_lists = int(cb.get("lists", 1))
    seed = schema.get("seed", 1)
    if _recipe(design) == "latin_square_target":
        raise ValueError(
            "lexsync: counterbalance.optimise does not apply to a Latin-square "
            "design. Every item already appears in every list there, so the lists are "
            "balanced on the items by construction; the rotation decides only which "
            "condition each item takes.")
    if n_lists < 2:
        raise ValueError("lexsync: counterbalance.optimise needs "
                         "counterbalance.lists to be 2 or more.")
    dims = _balance_dims(design)
    if not dims:
        raise ValueError(
            "lexsync: counterbalance.optimise has no dimensions to balance. Name them "
            "in counterbalance.balance_on, or give the design a match_on.")
    absent = sorted((d for d in dims if d not in stimuli.columns),
                    key=lambda s: s.encode("utf-8"))
    if absent:
        raise ValueError("lexsync: cannot balance on column(s) the stimuli do not "
                         "have: %s." % ", ".join("'%s'" % a for a in absent))

    sets = sorted(stimuli["set"].unique())
    n_sets = len(sets)
    V = _balance_values(stimuli, dims)
    totals = {d: sum(v) for d, v in V.items()}
    if max((abs(t) for t in totals.values()), default=0) * n_sets > BALANCE_MAX_MAGNITUDE:
        raise ValueError(
            "lexsync: the balance objective would exceed the exact-integer range.")

    # Start from the default deal, so the search improves on the shipped behaviour
    # rather than starting somewhere unrelated to it.
    assign = [(i % n_lists) + 1 for i in range(n_sets)]
    cost0 = _balance_cost(V, assign, n_lists, n_sets)

    pairs = [(i, j) for i in range(n_sets - 1) for j in range(i + 1, n_sets)]
    max_passes = int(cb.get("max_passes", 500))
    n_swaps = 0
    cost = cost0
    hit_bound = False
    for pass_i in range(1, max(0, max_passes) + 1):
        cand = [(i, j) for i, j in pairs if assign[i] != assign[j]]
        if not cand:
            break
        n_in = [sum(1 for a in assign if a == l) for l in range(1, n_lists + 1)]
        S = {d: [sum(v for v, a in zip(V[d], assign, strict=True) if a == l)
                 for l in range(1, n_lists + 1)] for d in dims}
        best = 0
        tied = []
        for i, j in cand:
            la, lb = assign[i], assign[j]
            delta = 0
            for d in dims:
                va, vb = V[d][i], V[d][j]
                Sa, Sb = S[d][la - 1], S[d][lb - 1]
                sha = totals[d] * n_in[la - 1]
                shb = totals[d] * n_in[lb - 1]
                delta += (abs((Sa - va + vb) * n_sets - sha)
                          + abs((Sb - vb + va) * n_sets - shb)
                          - abs(Sa * n_sets - sha)
                          - abs(Sb * n_sets - shb))
            if delta < best:
                best, tied = delta, [(i, j)]
            elif delta == best and tied:
                tied.append((i, j))
        if best >= 0 or not tied:
            break
        if len(tied) > 1:
            # Hash tie-break, not position: taking the first tied pair would
            # systematically prefer low-numbered sets, and the digest is the package's
            # established way of choosing without a generator.
            def _h(pair):
                key = "|".join([_key_part(seed), "balance",
                                _key_part(sets[pair[0]]), _key_part(sets[pair[1]])])
                return hashlib.sha256(key.encode("utf-8")).hexdigest()
            pick = sorted(tied, key=_h)[0]
        else:
            pick = tied[0]
        i, j = pick
        assign[i], assign[j] = assign[j], assign[i]
        cost += best
        n_swaps += 1
        if pass_i == max_passes:
            hit_bound = True

    return {
        "list_of_set": {s: int(a) for s, a in zip(sets, assign, strict=True)},
        "report": {
            "dimensions": list(dims), "cost_before": int(cost0),
            "cost_after": int(cost), "n_swaps": int(n_swaps),
            "max_passes_reached": hit_bound,
            "cost_unit": ("summed absolute deviation of each list's dimension total "
                          "from its fair share, in milli-units of the dimension's "
                          "mean, scaled by the number of item sets"),
        },
    }


def counterbalance(stimuli: pd.DataFrame, design: dict, schema: dict,
                   list_of_set=None) -> pd.DataFrame:
    """Assign stimuli to lists and a randomised, reproducible trial order.

    The recipe is ``counterbalance.recipe`` when the design names one, and otherwise
    the recipe of the paradigm it names. That is the factorial recipe for matched word
    lists, or a Latin square over conditions for the paired and sentence paradigms. A
    design's own ``events`` list has no say in the recipe. The factorial recipe
    refuses more lists than item sets, since the surplus lists would be empty.

    ``list_of_set`` optionally maps each ``set`` to a list, from ``balance_lists``.
    The pipeline supplies it when ``counterbalance.optimise`` is on. Without it, the
    factorial recipe deals sets to lists by rank.

    Returns ``stimuli`` with added ``list`` and ``trial`` columns. Mirrors
    counterbalance() in R_workflow/R/counterbalancing.R.
    """
    # Resampled designs counterbalance each replicate (an independent item set)
    # on its own, so trial order is numbered within each replicate.
    if "replicate" in stimuli.columns and stimuli["replicate"].nunique() > 1:
        parts = [_counterbalance_one(g.reset_index(drop=True), design, schema, list_of_set)
                 for _, g in stimuli.groupby("replicate", sort=True)]
        return pd.concat(parts, ignore_index=True)
    return _counterbalance_one(stimuli, design, schema, list_of_set)


def _counterbalance_one(stimuli: pd.DataFrame, design: dict, schema: dict,
                        list_of_set=None) -> pd.DataFrame:
    if _recipe(design) == "latin_square_target":
        return counterbalance_latin_square(stimuli, design, schema)
    return counterbalance_factorial(stimuli, design, schema, list_of_set)


def counterbalance_factorial(stimuli: pd.DataFrame, design: dict, schema: dict,
                             list_of_set=None) -> pd.DataFrame:
    n_lists = (design.get("counterbalance") or {}).get("lists", 1)
    seed = schema.get("seed", 1)
    stimuli = stimuli.copy()
    stimuli["list"] = 1
    sets = sorted(stimuli["set"].unique())
    if n_lists > len(sets):
        # Each list receives whole item sets, so lists beyond the number of sets would
        # be empty, and the datasheet would describe lists that do not exist. Must
        # stay identical to the refusal in counterbalance_factorial in
        # R_workflow/R/counterbalancing.R.
        n_sets = len(sets)
        have = ("there is only 1 item set" if n_sets == 1
                else f"there are only {n_sets} item sets")
        empty = (f"list {n_sets + 1}" if n_lists == n_sets + 1
                 else f"lists {n_sets + 1} to {n_lists}")
        raise ValueError(f"lexsync: counterbalance.lists is {n_lists} but {have}, so "
                         f"{empty} would be empty; lower lists or add items.")
    if n_lists > 1:
        if list_of_set is not None:
            # A balanced assignment from balance_lists(). Looked up by set VALUE, since
            # the map is keyed by it; a set the map does not name is a caller error
            # rather than a silent fall-back to list 1.
            missing = sorted(set(stimuli["set"]) - set(list_of_set),
                             key=lambda s: str(s))
            if missing:
                raise ValueError(
                    "lexsync: the balanced list assignment does not cover set(s) %s."
                    % ", ".join(str(m) for m in missing))
            mapping = dict(list_of_set)
        else:
            # Deal by set RANK, not by set value, so the deal does not depend on `set`
            # being contiguous and starting at 1 (R's seq_along does the same).
            mapping = {s: (i % n_lists) + 1 for i, s in enumerate(sets)}
        stimuli["list"] = stimuli["set"].map(mapping)
    parts = [_shuffle_deterministic(df, seed)
             for _, df in stimuli.groupby("list", sort=True)]
    return pd.concat(parts, ignore_index=True)


def counterbalance_latin_square(stimuli: pd.DataFrame, design: dict, schema: dict) -> pd.DataFrame:
    """One row per item per list, condition rotated across lists (Latin square).

    Each item (``set``) contributes exactly one trial to a list, so its target is
    never repeated within a list. The conditions are balanced when the lists and the
    item sets are both multiples of the number of conditions, and
    ``counterbalance_check`` reports a rotation that is not. With ``lists`` unset the
    number of lists equals the number of conditions, the canonical
    fully-counterbalanced design.
    """
    seed = schema.get("seed", 1)
    conds = sorted(stimuli["condition"].unique(), key=lambda s: str(s).encode("utf-8"))
    n_cond = len(conds)
    n_lists = (design.get("counterbalance") or {}).get("lists", n_cond)
    sets = sorted(stimuli["set"].unique())
    parts = []
    for li in range(n_lists):
        rows = []
        for si, s in enumerate(sets):
            cond = conds[(si + li) % n_cond]
            row = stimuli[(stimuli["set"] == s) & (stimuli["condition"] == cond)]
            if len(row) == 0:
                raise ValueError(f"lexsync: item set {s} has no row for condition '{cond}'.")
            rows.append(row.iloc[0])
        df = pd.DataFrame(rows).reset_index(drop=True)
        df["list"] = li + 1
        df = _shuffle_deterministic(df, seed).reset_index(drop=True)
        parts.append(df)
    return pd.concat(parts, ignore_index=True)


def participant_table(factors: dict, n_participants: int) -> pd.DataFrame:
    keys = list(factors.keys())
    # R's expand.grid() varies the first factor fastest, itertools.product the
    # last; cross the reversed keys and unreverse each cell so a participant
    # number is allocated the same cell by either engine.
    grid = [cell[::-1] for cell in product(*[factors[k] for k in reversed(keys)])]
    rows = [dict(zip(keys, grid[i % len(grid)], strict=True)) for i in range(n_participants)]
    df = pd.DataFrame(rows)
    df["participant"] = np.arange(1, n_participants + 1)
    return df
