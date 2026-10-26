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
import numbers
from itertools import product

import numpy as np
import pandas as pd

from .design import _shown
from .io_utils import _key_part, _round_dp_scaled
from .paradigms import get_paradigm

# The recipes counterbalance() knows, which counterbalance.recipe may name, and the
# policies counterbalance.incomplete accepts. Both are closed sets, so a misspelt
# value is refused, and the error names it.
RECIPES = ("factorial", "latin_square_target")
INCOMPLETE_POLICIES = ("allow", "error")


def _recipe(design: dict) -> str:
    """The recipe counterbalance() applies to a design.

    ``counterbalance.recipe`` when the design names one, else the recipe of the
    paradigm it names, else ``factorial``. An ``events`` list has no say in it, so a
    priming design that reads its prime's duration from the items keeps the paradigm's
    Latin square, which shows no target in both conditions of a list. The datasheet
    takes its recipe from here too, so the record names the recipe that ran. Mirrors
    .cb_recipe in R_workflow/R/counterbalancing.R.
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


def _order_ranks(df: pd.DataFrame, seed, order: int = 1) -> list:
    """Each row's SHA-256 rank in trial order ``order`` of its list.

    Order 1 hashes "seed|replicate|list|set|condition", the key _shuffle_deterministic
    ranks by, so a design's first order is the order it has without
    counterbalance.orders. Order j from 2 hashes
    "seed|order<j>|replicate|list|set|condition". Mirrors .order_ranks in
    R_workflow/R/counterbalancing.R.
    """
    rep = df["replicate"] if "replicate" in df.columns else [0] * len(df)
    head = [_key_part(seed)] + ([] if order == 1 else ["order%d" % order])
    # Every component is formatted explicitly rather than interpolated. Default
    # stringification is where the two engines silently part company: R renders
    # the double 42 as "42" and Python as "42.0", and a pandas column is promoted
    # to float64 by a single missing value, which would change every digest, every
    # trial order and every generated artefact with nothing to signal it.
    return [hashlib.sha256("|".join(
                head + [_key_part(r), _key_part(l), _key_part(s), _key_part(c)]
            ).encode("utf-8")).hexdigest()
            for r, l, s, c in zip(rep, df["list"], df["set"], df["condition"], strict=True)]


def _shuffle_deterministic(df: pd.DataFrame, seed) -> pd.DataFrame:
    """Order the trials of one list by a keyed hash, not a random number generator.

    Each row is ranked by the SHA-256 digest of "seed|replicate|list|set|condition",
    a tuple that identifies the trial uniquely under either recipe. Distinct inputs
    to SHA-256 behave as independent uniform draws, so ordering by the digest
    realises a seeded random permutation, but as a pure function of the design: the
    same bytes from the R and Python engines on any platform, and a different order
    for every seed. R's sample() and numpy's PCG64 could never agree on a
    permutation, so a generator-based shuffle would be engine-specific in an otherwise
    byte-identical pipeline. The replicate term keeps independently counterbalanced
    item sets from sharing one permutation pattern.
    """
    df = df.iloc[np.argsort(_order_ranks(df, seed), kind="stable")].copy()
    df["trial"] = np.arange(1, len(df) + 1)
    return df


# ---- Trial-order constraints (counterbalance.max_run, run_on, orders) --------
#
# The keyed-hash order is a uniform shuffle, and a uniform shuffle gives long runs of
# one condition: over seeds 1 to 1000 of a 60 + 60 lexical decision the longest run
# had a median of 7 and a maximum of 21. `max_run: k` repairs the seeded order so that
# no run of one `run_on` value is longer than k, the kind of sequence constraint that
# pseudorandomisation programs such as Mix impose (van Casteren & Davis, 2006). The
# repair is deterministic and identical in both engines, and it refuses only a
# constraint that no order can meet. `orders: m` gives each list m orders, the first
# being the order the list has without the key, so that participants on one list need
# not all meet one order. Mirrors R_workflow/R/counterbalancing.R.

_ORDER_KEY_MESSAGE = "lexsync: counterbalance.%s must be a whole number of at least 1."


def _whole_at_least_one(value) -> bool:
    """Whether a design value is a whole number from 1, written as 2 or 2.0, within the
    range R's as.integer() holds. Must match .whole_at_least_one in
    R_workflow/R/counterbalancing.R."""
    return (not isinstance(value, bool) and isinstance(value, numbers.Real)
            and math.isfinite(value) and value == int(value) and 1 <= value <= 2147483647)


def _trial_order_settings(design: dict) -> dict:
    """``counterbalance.max_run``, ``run_on`` and ``orders``, checked.

    Returns ``{"max_run", "run_on", "orders"}``: ``max_run`` is None when the design sets
    no limit, ``run_on`` defaults to ``condition`` and ``orders`` to 1. A limit or a
    number of orders that is not a whole number from 1 is refused, and so is a
    ``run_on`` that is not the name of a column. Mirrors .trial_order_settings in
    R_workflow/R/counterbalancing.R.
    """
    cb = design.get("counterbalance") if isinstance(design, dict) else None
    cb = cb if isinstance(cb, dict) else {}
    k = cb.get("max_run")
    if k is not None and not _whole_at_least_one(k):
        raise ValueError(_ORDER_KEY_MESSAGE % "max_run")
    run_on = cb.get("run_on")
    if run_on is None:
        run_on = "condition"
    elif not isinstance(run_on, str) or not run_on.strip(" \t\r\n"):
        raise ValueError("lexsync: counterbalance.run_on must name a column of the trials.")
    m = cb.get("orders")
    if m is None:
        m = 1
    elif not _whole_at_least_one(m):
        raise ValueError(_ORDER_KEY_MESSAGE % "orders")
    return {"max_run": None if k is None else int(k), "run_on": run_on, "orders": int(m)}


def _unit_label(df: pd.DataFrame) -> str:
    """The list a frame of trials belongs to, as the refusals name it: "list 2", or
    "list 2 of replicate 3" when the frame carries a replicate."""
    label = "list " + _key_part(df["list"].iloc[0])
    if "replicate" in df.columns:
        label += " of replicate " + _key_part(df["replicate"].iloc[0])
    return label


def _missing_category(value) -> bool:
    """A missing run_on value: NA, or text that is empty once R's trimws() set of
    spaces is stripped. Every missing value forms one category."""
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip(" \t\r\n")
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _run_categories(df: pd.DataFrame, run_on: str, unit: str) -> list:
    """Each row's run_on value as a category: None for a missing value, else the value
    as the hash key renders it, so 1 and 1.0 are one category in both engines."""
    if run_on not in df.columns:
        raise ValueError(f"lexsync: counterbalance.run_on names '{run_on}', a column that "
                         f"{unit} does not have.")
    return [None if _missing_category(v) else _key_part(v) for v in df[run_on]]


def _run_feasible(remaining: dict, current, run: int, k: int) -> bool:
    """Whether the trials still to place can follow the current run with no run longer
    than k. Category c can be split by the others into at most (others + 1) runs of k,
    and its first run continues the current run when c is the current run's category:
    remaining(c) <= k * (others + 1), less the current run's length for that category.
    The test is exact: on 2,417 small multisets it agreed with exhaustive search."""
    total = sum(remaining.values())
    for c, r in remaining.items():
        if r and r > k * (total - r + 1) - (run if c == current else 0):
            return False
    return True


def _check_run_limit(categories: list, k: int, run_on: str, unit: str) -> None:
    """Refuse a limit no order of these trials can meet. At most one category can
    break it, the one holding more than half the trials, so the message names it."""
    counts: dict = {}
    for c in categories:
        counts[c] = counts.get(c, 0) + 1
    if _run_feasible(counts, object(), 0, k):
        return
    total = len(categories)
    worst = next(c for c, r in counts.items() if r > k * (total - r + 1))
    n = counts[worst]
    label = (f"trials with no '{run_on}'" if worst is None else f"'{worst}' trials")
    raise ValueError(f"lexsync: no order of {unit} keeps runs of '{run_on}' to {k} or "
                     f"fewer: {n} {label} against {total - n} others.")


def _repair_runs(perm: list, categories: list, k: int) -> list:
    """The seeded order ``perm`` (row indices in rank order), repaired so that no run
    of one category is longer than k.

    Each step takes the earliest trial still unplaced in the seeded order that neither
    extends the current run beyond k nor leaves the rest infeasible (see
    _run_feasible). A trial that keeps both is always there once the start is
    feasible, which _check_run_limit has established. Taking the earliest trial that
    does not extend the run, without the look-ahead, refused 931 of 1,000 seeds of a
    feasible 40 + 80 design at k = 2 near the end of the list. Mirrors .repair_runs in
    R_workflow/R/counterbalancing.R.
    """
    remaining: dict = {}
    for c in categories:
        remaining[c] = remaining.get(c, 0) + 1
    left = list(perm)
    out = []
    current, run = object(), 0
    while left:
        verdict: dict = {}
        for pos in range(len(left)):
            c = categories[left[pos]]
            if c == current and run >= k:
                continue
            if c not in verdict:
                remaining[c] -= 1
                verdict[c] = _run_feasible(remaining, c, run + 1 if c == current else 1, k)
                remaining[c] += 1
            if verdict[c]:
                break
        else:
            raise ValueError("lexsync: the trial-order repair found no trial to place.")
        out.append(left.pop(pos))
        remaining[c] -= 1
        run = run + 1 if c == current else 1
        current = c
    return out


def _order_trials(df: pd.DataFrame, seed, settings: dict, unit: str,
                  max_run: bool = True) -> pd.DataFrame:
    """Order one list's trials, and add each trial's position in every order.

    The rows come back in order 1 with ``trial`` numbered from 1. With
    ``settings["orders"]`` above 1, ``order_1`` to ``order_m`` give each trial's position
    in each order, ``order_1`` equal to ``trial``. With ``settings["max_run"]`` set and
    ``max_run`` true, every order is repaired so that no run of one ``run_on`` value is
    longer than the limit. Without either setting this is _shuffle_deterministic.
    """
    k = settings.get("max_run") if max_run else None
    m = settings.get("orders", 1)
    categories = None
    if k is not None:
        categories = _run_categories(df, settings["run_on"], unit)
        _check_run_limit(categories, k, settings["run_on"], unit)
    perms = []
    for j in range(1, m + 1):
        perm = [int(i) for i in np.argsort(_order_ranks(df, seed, j), kind="stable")]
        if k is not None:
            perm = _repair_runs(perm, categories, k)
        perms.append(perm)
    out = df.iloc[perms[0]].copy()
    n = len(df)
    out["trial"] = np.arange(1, n + 1)
    if m > 1:
        for j, perm in enumerate(perms, start=1):
            position = np.empty(n, dtype=np.int64)
            position[perm] = np.arange(1, n + 1)
            out["order_%d" % j] = position[perms[0]]
    return out


def _longest_runs(trials: pd.DataFrame, run_on: str, orders: int) -> int:
    """The longest run of one ``run_on`` value in a version's presented trials, over
    every order. The PsychoPy and jsPsych experiments pause after the practice trials,
    so a run is counted as ending there. The OpenSesame experiment runs every trial in
    one loop without a pause, so there a run can continue from the practice trials into
    the main ones."""
    if run_on not in trials.columns or not len(trials):
        return 0
    best = 0
    for j in range(1, orders + 1):
        column = "order_%d" % j if orders > 1 else "trial"
        ordered = trials.sort_values(column, kind="stable")
        practice = (list(ordered["block"] == "practice") if "block" in ordered.columns
                    else [False] * len(ordered))
        previous, run = object(), 0
        for value, part in zip(ordered[run_on], practice, strict=True):
            c = (part, None if _missing_category(value) else _key_part(value))
            run = run + 1 if c == previous else 1
            previous = c
            best = max(best, run)
    return best


def _trial_order_record(presented: pd.DataFrame, design: dict) -> dict:
    """What the datasheet records of the trial-order settings, from the presented
    trials: ``{"max_run": {"k", "run_on", "longest"}}`` when the design sets a limit,
    ``longest`` giving the longest run realised in each presentation version, and
    ``{"orders": m}`` when it asks for more than one order. Empty for a design with
    neither. Mirrors .trial_order_record in R_workflow/R/counterbalancing.R."""
    settings = _trial_order_settings(design)
    record: dict = {}
    if settings["max_run"] is not None:
        # Imported here: scripting imports this module.
        from .scripting import _version_rows, presentation_versions
        longest = []
        for v in presentation_versions(presented):
            row = {"list": int(v["list"])}
            if "replicate" in presented.columns:
                row = {"replicate": int(v["replicate"]), **row}
            row["longest_run"] = _longest_runs(_version_rows(presented, v),
                                               settings["run_on"], settings["orders"])
            longest.append(row)
        record["max_run"] = {"k": settings["max_run"], "run_on": settings["run_on"],
                             "longest": longest}
    if settings["orders"] > 1:
        record["orders"] = settings["orders"]
    return record


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

# Each dimension is quantised to its own unit, the mean's or the mean absolute
# deviation's as counterbalance.scale says (see _quantise_dim). Expressing all
# dimensions in such a unit is what lets their imbalances be added without a
# per-dimension float weight: a word's length and its Zipf frequency differ by orders
# of magnitude in raw units, and summing raw deviations would silently optimise almost
# entirely for whichever dimension has the larger numbers.
#
# Under the mean scale the constant is 1000 times the 100 that `unit` already carries,
# so a value at the dimension's mean quantises to 1000, a milli-unit of the mean. That
# factor is not cosmetic: with 1000 here, a value at the mean would quantise to 10,
# leaving about ten distinguishable levels across a dimension's whole range, so
# imbalances smaller than a tenth of the mean would be invisible to the objective and
# the search would trade away a dimension it could not see in order to improve one it
# could. Under the mad scale the deviation and the unit are both in hundredths, so a
# deviation of one mean absolute deviation quantises to 100000.
BALANCE_UNIT_SCALE = 100000

# Guard on the objective's magnitude. Python ints are arbitrary precision, but the R
# engine holds these as doubles and is exact only below 2^53; the bound is shared so
# both engines refuse the same designs rather than one of them silently rounding.
# Nothing near this is reachable with realistic designs.
BALANCE_MAX_MAGNITUDE = 2 ** 50

# The scales counterbalance.scale may name. A closed set, so a misspelt value is
# refused, and the error names it.
BALANCE_SCALES = ("mean", "mad")

# What the report's cost is counted in, under each scale. Must stay identical to
# .BALANCE_COST_UNITS in R_workflow/R/counterbalancing.R.
_BALANCE_COST_UNITS = {
    "mean": ("summed absolute deviation of each list's dimension total from its fair "
             "share, in milli-units of the dimension's mean, scaled by the number of "
             "item sets"),
    "mad": ("summed absolute deviation of each list's dimension total from its fair "
            "share, in hundred-thousandths of the dimension's mean absolute deviation "
            "about its mean, scaled by the number of item sets"),
}


def _balance_scale(design: dict) -> str:
    """The scale balance_lists() quantises each dimension on.

    ``counterbalance.scale`` when the design names one, else ``mean``.
    Read on presence, as R's %||% reads it, so the two engines refuse the same values.
    validate_design() calls this too, so an unknown scale is refused before anything
    is selected. Mirrors .balance_scale in R_workflow/R/counterbalancing.R.
    """
    val = (design.get("counterbalance") or {}).get("scale")
    if val is None:
        return "mean"
    if not isinstance(val, str) or val not in BALANCE_SCALES:
        raise ValueError(f"lexsync: unknown counterbalance.scale '{_shown(val)}'. "
                         f"Known scales: {', '.join(BALANCE_SCALES)}.")
    return val


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


def _quantise_dim(values, name: str, scale: str = "mean") -> list:
    """Quantise one dimension to integers, on the scale counterbalance.scale names.

    Under ``mean``, each value in milli-units of the dimension's own mean. The only
    floating-point steps in the whole optimiser are here, and each is a single IEEE
    operation that the standard requires to be correctly rounded, so both engines hold
    the same double before it is truncated. Truncation of a double is exact, so no
    rounding mode is involved. ``round`` would have agreed on every case measured, but
    truncation removes the question rather than answering it.

    The mean is computed from INTEGER counts, never as a float sum: summing 20000
    doubles was measured to give three different answers across R's sum(),
    math.fsum, numpy's pairwise sum and a naive loop, so a float mean here could put
    the two engines on different search paths from the first step.

    Dividing by the mean weights a dimension by its SD / mean, which depends on where
    its scale starts: Zipf frequency, which starts near 3, counted for least of the
    four dimensions in en_balanced_lists. That suits ratio scales only. ``mad``
    quantises deviations from the mean instead (see _quantise_mad).
    """
    vals = [float(v) for v in values]
    if any(v != v for v in vals):
        raise ValueError(
            "lexsync: dimension '%s' has missing values, so it cannot be balanced "
            "across lists. Fill or drop those items." % name)
    if scale == "mad":
        return _quantise_mad(vals, name)
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


def _quantise_mad(vals: list, name: str) -> list:
    """Quantise one dimension's deviations from its mean, in hundred-thousandths of
    its mean absolute deviation.

    Each value becomes a whole number of hundredths by the shared rounder, the
    integer mean is the floor of their sum over their count, and the unit is the
    integer mean of the absolute deviations from it, at least 1. The values are
    rounded, not truncated, because a shifted value can scale to a hair below a whole
    hundredth ((5.26 - 3) * 100 is 225.99999999999997), and truncation would move it
    by one. Adding a constant that is a whole number of hundredths then moves every
    value, and the mean with them, by the same whole number, and leaves the
    deviations and the unit as they were. The division by the unit is a single IEEE
    operation and the truncation is exact, so both engines hold the same integers.
    Mirrors .quantise_mad in R_workflow/R/counterbalancing.R.
    """
    hundredths = []
    for v in vals:
        y = v * 100
        # An infinite value has no hundredths. The R twin's rounder passes it through
        # to the size refusal, so it is refused here by the same message.
        h = _round_dp_scaled(y) if math.isfinite(y) else None
        if h is None or abs(h) > 2 ** 31 - 1:
            raise ValueError(
                "lexsync: dimension '%s' has values too large to balance on." % name)
        hundredths.append(h)
    n = len(hundredths)
    # Floor division, as R's %/% gives, so a negative sum rounds down in both engines.
    centre = sum(hundredths) // n
    deviations = [h - centre for h in hundredths]
    unit = max(1, sum(abs(d) for d in deviations) // n)
    return [math.trunc(float(d * BALANCE_UNIT_SCALE) / unit) for d in deviations]


def _balance_values(stimuli: pd.DataFrame, dims: list, scale: str = "mean") -> dict:
    """One integer per set per dimension: the set's total, because a list receives
    whole sets. Rows are grouped by set in sorted order so both engines build the
    same matrix from the same frame."""
    sets = sorted(stimuli["set"].unique())
    V = {}
    for d in dims:
        q = _quantise_dim(stimuli[d], d, scale)
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

    ``counterbalance.scale`` sets each dimension's unit. ``mean``, the default,
    divides by the dimension's mean, which suits ratio scales only. ``mad`` balances
    deviations from the mean in units of the mean absolute deviation, so adding a
    constant to a dimension, such as writing Zipf frequency as Zipf - 3, leaves the
    lists unchanged. The report then gives ``scale`` too, and ``cost_unit`` names the
    unit under either scale.

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

    scale = _balance_scale(design)
    sets = sorted(stimuli["set"].unique())
    n_sets = len(sets)
    V = _balance_values(stimuli, dims, scale)
    totals = {d: sum(v) for d, v in V.items()}
    # Bounded on the sum of the absolute set totals, which bounds every list's total.
    # Under mad the values are deviations whose total is near zero, so a bound on the
    # total would bound nothing. For values of one sign the two bounds are the same.
    if (max((sum(abs(v) for v in vals) for vals in V.values()), default=0) * n_sets
            > BALANCE_MAX_MAGNITUDE):
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

    report = {
        "dimensions": list(dims), "cost_before": int(cost0),
        "cost_after": int(cost), "n_swaps": int(n_swaps),
        "max_passes_reached": hit_bound,
        "cost_unit": _BALANCE_COST_UNITS[scale],
    }
    # Recorded only off the default: under the default, cost_unit names the mean.
    if scale != "mean":
        report["scale"] = scale
    return {"list_of_set": {s: int(a) for s, a in zip(sets, assign, strict=True)},
            "report": report}


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
    factorial recipe deals sets to lists by rank: the first set to list 1, the second
    to list 2 and so on, cycling.

    Each list's trials are ordered by the seeded keyed hash. ``counterbalance.max_run``
    repairs that order so that no run of one ``counterbalance.run_on`` value (by default
    the condition) is longer than the limit, and refuses a limit no order can meet. A
    design with fillers has the limit applied by ``add_blocks``, to the order the fillers
    are interleaved in. ``counterbalance.orders: m`` adds ``order_1`` to ``order_m``,
    each trial's position in each of m orders of its list, ``order_1`` being the order
    ``trial`` gives.

    Returns the trials, sorted by replicate, list and trial, with ``list`` and
    ``trial`` columns added, and ``order_1`` to ``order_m`` when there is more than one
    order. Under the factorial recipe, every row of ``stimuli`` appears once, in the list
    its set is dealt to. Under the Latin square, each list holds one row per item set,
    in the condition the rotation gives that set in that list, so the result has one
    row per set per list and not every row of ``stimuli``. Mirrors counterbalance() in
    R_workflow/R/counterbalancing.R.
    """
    _trial_order_settings(design)
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
    settings = _trial_order_settings(design)
    # With fillers, add_blocks draws the order again over the main trials and the
    # fillers together, and the limit belongs to that order: the main trials alone may
    # be all one condition, as a lexical decision's words are when its pseudowords are
    # fillers.
    limit = not design.get("fillers")
    parts = [_order_trials(df, seed, settings, _unit_label(df), max_run=limit)
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
    settings = _trial_order_settings(design)
    limit = not design.get("fillers")
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
        df = _order_trials(df, seed, settings, _unit_label(df),
                           max_run=limit).reset_index(drop=True)
        parts.append(df)
    return pd.concat(parts, ignore_index=True)


def participant_table(factors: dict, n_participants: int) -> pd.DataFrame:
    """Allocate participants to the cells of fully crossed factors.

    ``factors`` maps each factor's name to its levels. The cells are every
    combination of the levels, ordered with the first factor varying fastest, as R's
    ``expand.grid()`` orders them, and participant ``p`` takes cell
    ``((p - 1) mod C) + 1`` of the ``C`` cells. The allocation therefore cycles through
    the grid, and the cells' counts are equal when ``n_participants`` is a multiple of
    ``C`` and otherwise differ by one.

    Returns a DataFrame with one row per participant: a column per factor and a
    ``participant`` column numbered from 1. Mirrors participant_table in
    R_workflow/R/counterbalancing.R.
    """
    keys = list(factors.keys())
    # R's expand.grid() varies the first factor fastest, itertools.product the
    # last; cross the reversed keys and unreverse each cell so a participant
    # number is allocated the same cell by either engine.
    grid = [cell[::-1] for cell in product(*[factors[k] for k in reversed(keys)])]
    rows = [dict(zip(keys, grid[i % len(grid)], strict=True)) for i in range(n_participants)]
    df = pd.DataFrame(rows)
    df["participant"] = np.arange(1, n_participants + 1)
    return df
