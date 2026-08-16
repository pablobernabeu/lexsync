"""The multidimensional constraint-matching engine.

Mirrors R_workflow/R/matching.R exactly: a per-dimension tolerance pre-filter
followed by standardised nearest-neighbour assignment with a stable tie-break.
The same standardisation (sample SD), the same even-spread anchor selection and
the same tie-break order are used as in R, so the two engines return matching
selections from identical input.

Cross-engine determinism. The default methods (``standardised_euclidean`` and
``joint``) use no floating-point operation whose last bit differs across
platforms, so the R and Python engines select byte-identical stimuli. The
optional ``mahalanobis`` and ``optimal`` methods are the exception: they rely on
a covariance-matrix inverse and a linear-assignment solver respectively, whose
last-bit results differ between the R and Python linear-algebra backends (the
LAPACK build behind the matrix inverse, and the assignment algorithm itself). The
two engines therefore agree closely but are not guaranteed byte-for-byte on those
two methods.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# The z-scoring centre and scale go through the reproducible reductions, not numpy's.
# Selection was robust to the difference for a structural reason worth stating: a
# distance is computed between z-VECTORS, so a shift in the centre cancels in the
# difference, a change of scale is a monotone rescaling that cannot reorder candidates,
# and the distances are rounded to nine places on top of that. Even so, "robust for a
# reason" is not the same as "identical by construction", and the latter is what the
# package claims. Switching these was verified to change no design's selection.
from .io_utils import _exact_mean, _exact_sd, _round_dp_vec
from .querying import build_pool

# Fixed order, as documented in schema.yaml; not sorted(), because the R mirror's
# sort() on character vectors is locale-collated and the two error messages must agree.
_KNOWN_METHODS = ("standardised_euclidean", "joint", "mahalanobis", "optimal")

# Candidate cap for the pairwise (joint, optimal) matchers. The datasheet reports
# whether the cap fired, so the literal lives in one place per engine.
# Must stay identical to .PAIRWISE_CAP in R_workflow/R/matching.R.
PAIRWISE_CAP = 1200


def _resolve_policy(design, schema, key, default, known):
    """Resolve a matching policy with a design-over-schema-over-default cascade.

    Mirrors how tolerance_k is resolved. Must stay identical to .resolve_policy
    in R_workflow/R/matching.R.
    """
    val = ((design.get("matching") or {}).get(key)
           or (schema.get("matching") or {}).get(key) or default)
    if val not in known:
        raise ValueError(f"lexsync: unknown {key} policy '{val}'. "
                         f"Known policies: {', '.join(known)}.")
    return val


def _check_shortfall(realised, n, policy, continuous=False):
    """Refuse a selection smaller than the design requested, unless allowed.

    A shortfall silently invalidates the datasheet and the generated Methods
    text, which state the requested n. Must stay identical to .check_shortfall
    in R_workflow/R/matching.R.
    """
    if realised >= n or policy == "allow":
        return
    if continuous:
        raise ValueError(f"lexsync: {n} items were requested but only {realised} could be "
                         f"selected; widen the pool or lower n_per_condition, or set "
                         f"matching: shortfall: allow to accept a smaller set.")
    raise ValueError(f"lexsync: {n} sets per condition were requested but only {realised} "
                     f"could be selected; widen pool_filters/define_by or lower "
                     f"n_per_condition, or set matching: shortfall: allow to accept a "
                     f"smaller set.")


def _assert_distinct_words(out):
    """A word selected for two conditions is a confound, not a match.

    The anchored and joint paths prevent it structurally; the optimal path can
    only be steered away by a finite penalty, so the invariant is asserted on
    every path's output. Must stay identical to .assert_distinct_words in
    R_workflow/R/matching.R.
    """
    dup = out["word"][out["word"].duplicated()]
    if len(dup):
        raise ValueError(f"lexsync: overlapping conditions selected the word "
                         f"'{dup.iloc[0]}' in more than one condition; make the "
                         f"conditions disjoint or lower n_per_condition.")


def _zmat(df: pd.DataFrame, match_on, center, scale) -> np.ndarray:
    m = df[match_on].to_numpy(dtype=float)
    return (m - center) / scale


def _exact_colmeans(z):
    """Column means for the overlap-cap centroid, through the compensated reduction
    rather than numpy's. The cap decides which candidates survive into matching -- it
    fires for the shipped en_ndensity and es_ndensity designs -- so a centroid that
    differs in the last bits between engines is a selection difference waiting to
    happen, not a rounding curiosity. Mirrors .exact_colmeans in matching.R."""
    return np.array([_exact_mean(z[:, j]) for j in range(z.shape[1])], dtype=float)


def _cap_to_overlap(df, z, other_centroid, cap):
    """Keep the `cap` rows nearest the other condition's centroid (byte-rank ties)."""
    if len(df) <= cap:
        return df.reset_index(drop=True), z
    d = _round_dp_vec(np.sqrt(((z - other_centroid) ** 2).sum(axis=1)), 9)
    order = sorted(range(len(df)), key=lambda i: (d[i], i))[:cap]
    keep = sorted(order)
    return df.iloc[keep].reset_index(drop=True), z[keep]


def _match_joint(subpools, cond_names, match_on, center, scale, n, cap=PAIRWISE_CAP):
    """Select the `n` best-matched pairs jointly across two conditions.

    Rather than fixing one condition and matching the other to it, this scores
    every cross-condition pair on the control dimensions and greedily takes the
    cheapest disjoint pairs. Only items with a good counterpart are kept, so the
    control dimensions are equated even when the manipulation is confounded with
    them (e.g. neighbourhood density with word length). Deterministic and
    identical to the R engine (rounded costs; byte-rank tie-breaks).
    """
    s0 = subpools[0].reset_index(drop=True)
    s1 = subpools[1].reset_index(drop=True)
    if len(s0) == 0 or len(s1) == 0:
        raise ValueError("lexsync: a condition has no candidates for joint matching.")
    z0 = _zmat(s0, match_on, center, scale)
    z1 = _zmat(s1, match_on, center, scale)
    s0, z0 = _cap_to_overlap(s0, z0, _exact_colmeans(z1), cap)
    s1, z1 = _cap_to_overlap(s1, z1, _exact_colmeans(z0), cap)
    cost = _round_dp_vec(np.sqrt(((z0[:, None, :] - z1[None, :, :]) ** 2).sum(axis=2)), 9)
    m0, m1 = cost.shape
    rows = np.repeat(np.arange(m0), m1)
    cols = np.tile(np.arange(m1), m0)
    order = np.lexsort((cols, rows, cost.ravel()))   # by cost, then row, then col
    w0 = s0["word"].to_numpy()
    w1 = s1["word"].to_numpy()
    used0 = np.zeros(m0, dtype=bool)
    used1 = np.zeros(m1, dtype=bool)
    # Word-level tracking, as in the anchored matcher: overlapping condition
    # windows can put one word in both subpools, where its self-pair costs
    # exactly 0 and a mirrored re-pick (x with y, then y with x) would reuse
    # both words. For disjoint conditions no word appears twice, so these skips
    # never fire and the selection is unchanged.
    used_words: set = set()
    pi, pj = [], []
    for idx in order:
        i = int(rows[idx]); j = int(cols[idx])
        if used0[i] or used1[j]:
            continue
        if w0[i] == w1[j]:
            continue
        if w0[i] in used_words or w1[j] in used_words:
            continue
        used0[i] = True
        used1[j] = True
        used_words.add(w0[i])
        used_words.add(w1[j])
        pi.append(i)
        pj.append(j)
        if len(pi) >= n:
            break
    a = s0.iloc[pi].copy(); a["condition"] = cond_names[0]
    b = s1.iloc[pj].copy(); b["condition"] = cond_names[1]
    common = [c for c in a.columns if c in b.columns]
    out = pd.concat([a[common], b[common]], ignore_index=True)
    out["set"] = list(range(1, len(pi) + 1)) * 2
    return out


def _maha_metric(z_pool: np.ndarray, ridge: float = 1e-6) -> np.ndarray:
    """The metric matrix for Mahalanobis distance in standardised space.

    Returns the inverse of the pool's correlation matrix (the covariance of the
    z-scored dimensions), so the distance down-weights correlated dimensions
    instead of double-counting the variance they share (Rubin, 1980; Stuart,
    2010). A small ridge keeps the matrix invertible when dimensions are nearly
    collinear. This inverse is a linear-algebra operation, so its last bits, and
    hence occasionally a matched item under a near-tie, may differ from the R
    engine (see the module note).
    """
    if z_pool.shape[1] == 1:
        return np.array([[1.0]])
    c = np.atleast_2d(np.corrcoef(z_pool, rowvar=False))
    c = np.nan_to_num(c, nan=0.0)          # a constant dimension -> treat as uncorrelated
    np.fill_diagonal(c, 1.0)
    c = c + ridge * np.eye(c.shape[0])
    return np.linalg.inv(c)


def _match_optimal(subpools, cond_names, match_on, center, scale, n, cap=PAIRWISE_CAP):
    """Optimal (minimum-total-distance) pairing for a two-condition design.

    Unlike the greedy ``joint`` matcher, this solves the linear-assignment problem
    globally, so it minimises the summed pair distance rather than taking the
    cheapest disjoint pair at each step; it produces fewer poorly matched pairs
    (Gu & Rosenbaum, 1993; Hansen & Klopfer, 2006). The assignment solver's tie
    handling differs between engines, so the two agree closely but not byte-for-byte.
    """
    from scipy.optimize import linear_sum_assignment
    s0 = subpools[0].reset_index(drop=True)
    s1 = subpools[1].reset_index(drop=True)
    if len(s0) == 0 or len(s1) == 0:
        raise ValueError("lexsync: a condition has no candidates for optimal matching.")
    z0 = _zmat(s0, match_on, center, scale)
    z1 = _zmat(s1, match_on, center, scale)
    s0, z0 = _cap_to_overlap(s0, z0, _exact_colmeans(z1), cap)
    s1, z1 = _cap_to_overlap(s1, z1, _exact_colmeans(z0), cap)
    cost = _round_dp_vec(np.sqrt(((z0[:, None, :] - z1[None, :, :]) ** 2).sum(axis=2)), 9)
    # A word present in both subpools (overlapping condition windows) must not be
    # paired with itself. The penalty is a large FINITE constant because both
    # scipy's linear_sum_assignment and clue::solve_LSAP reject Inf, and their
    # failure modes differ across engines; 1e9 dominates any real distance, and
    # the selection is asserted same-word-free afterwards in match_stimuli.
    # Must stay identical to the constant in match_optimal (matching.R).
    same = s0["word"].to_numpy()[:, None] == s1["word"].to_numpy()[None, :]
    cost[same] = 1e9
    row_ind, col_ind = linear_sum_assignment(cost)      # complete min-cost matching
    pair_cost = cost[row_ind, col_ind]
    order = sorted(range(len(row_ind)),
                   key=lambda t: (pair_cost[t], int(row_ind[t]), int(col_ind[t])))
    # The penalty steers the assignment away from self-pairs, but an overlapping
    # design can still mirror a pair (x with y, then y with x), reusing both
    # words. Greedy word-level dedup over the cost-ordered assignment keeps the
    # selection identical for disjoint designs, where every assigned word is
    # distinct.
    w0 = s0["word"].to_numpy()
    w1 = s1["word"].to_numpy()
    used_words: set = set()
    pi, pj = [], []
    for t in order:
        wi = w0[int(row_ind[t])]; wj = w1[int(col_ind[t])]
        if wi == wj or wi in used_words or wj in used_words:
            continue
        used_words.add(wi)
        used_words.add(wj)
        pi.append(int(row_ind[t]))
        pj.append(int(col_ind[t]))
        if len(pi) >= n:
            break
    a = s0.iloc[pi].copy(); a["condition"] = cond_names[0]
    b = s1.iloc[pj].copy(); b["condition"] = cond_names[1]
    common = [c for c in a.columns if c in b.columns]
    out = pd.concat([a[common], b[common]], ignore_index=True)
    out["set"] = list(range(1, len(pi) + 1)) * 2
    return out


def match_stimuli(pool: pd.DataFrame, design: dict, schema: dict, verbose: bool = False) -> pd.DataFrame:
    """Match stimuli across conditions on the ``match_on`` dimensions.

    Two policies govern degraded selections, each read from the design's
    ``matching`` block with the schema as fallback: ``shortfall`` ("error", the
    default, refuses to return fewer sets than requested; "allow" accepts the
    shrink) and ``on_insufficient_tolerance`` ("relax", the default, widens an
    undersupplied tolerance window to the full condition subpool and records the
    relaxation in ``out.attrs["audit"]``; "error" refuses instead).
    """
    conditions = design.get("conditions")
    if not conditions:
        # Without this, the anchor lookup below dies with a KeyError here and a
        # bare subscript error in R -- two different messages for the same mistake.
        raise ValueError("lexsync: the design has no conditions; a matched design "
                         "needs a conditions list.")
    match_on = list(design["match_on"])
    n = design.get("n_per_condition") or design.get("n_per_cell") or 20
    # Tolerance window k per dimension (window = anchor mean +/- k * SD). A design
    # may override the schema defaults per dimension, e.g. to reproduce a published
    # study's exact windows (Gonzalez Alonso et al. used SD/9 for frequency).
    tol_k = dict(schema["matching"].get("tolerance_k") or {})
    tol_k.update((design.get("matching") or {}).get("tolerance_k") or {})
    shortfall = _resolve_policy(design, schema, "shortfall", "error", ("error", "allow"))
    on_tol = _resolve_policy(design, schema, "on_insufficient_tolerance", "relax",
                             ("relax", "error"))

    for d in match_on:
        if d not in pool.columns:
            raise ValueError(f"lexsync: dimension '{d}' is absent from the pool.")
        k = tol_k.get(d, 2)
        if isinstance(k, (int, float)) and k < 0:
            # A negative k inverts the window (upper bound below the lower), which
            # empties the candidate set and silently relaxes to the full pool --
            # never intended.
            raise ValueError(f"lexsync: tolerance_k for dimension '{d}' is negative; "
                             f"tolerances must be zero or positive.")
    cnames = [c["name"] for c in conditions]
    dup_name = [x for x in cnames if cnames.count(x) > 1]
    if dup_name:
        raise ValueError(f"lexsync: condition name '{dup_name[0]}' appears more than "
                         f"once; condition names must be unique.")
    for c in conditions:
        for d in (c.get("define_by") or {}):
            # build_pool skips a column it does not recognise, so a misspelt
            # define_by key would silently hand the condition the whole pool as
            # its subpool and the manipulated contrast would vanish while
            # matching proceeds.
            if d not in pool.columns:
                raise ValueError(f"lexsync: dimension '{d}' in condition '{c['name']}' "
                                 f"is absent from the pool.")

    center = np.array([_exact_mean(pool[d].dropna()) for d in match_on], dtype=float)
    scale = np.array([_exact_sd(pool[d].dropna()) for d in match_on], dtype=float)
    scale[np.isnan(scale) | (scale == 0)] = 1.0

    # .get, not ["define_by"]: a condition without define_by draws on the whole
    # pool, as the R engine's NULL does through build_pool.
    subpools = [build_pool(pool, c.get("define_by")) for c in conditions]
    cond_names = [c["name"] for c in conditions]

    method = ((design.get("matching") or {}).get("method")
              or (schema.get("matching") or {}).get("method") or "standardised_euclidean")
    if method not in _KNOWN_METHODS:
        raise ValueError(f"lexsync: unknown matching method '{method}'. "
                         f"Known methods: {', '.join(_KNOWN_METHODS)}.")
    if method in ("joint", "optimal") and len(conditions) != 2:
        # Both are pairwise matchers; falling back to the anchor matcher here would
        # make the datasheet's recorded method differ from the one actually used.
        raise ValueError(f"lexsync: matching method '{method}' requires exactly two "
                         f"conditions, got {len(conditions)}.")
    if method == "joint" and len(conditions) == 2:
        out = _match_joint(subpools, cond_names, match_on, center, scale, n)
        _check_shortfall(out["set"].nunique(), n, shortfall)
        _assert_distinct_words(out)
        return out
    if method == "optimal" and len(conditions) == 2:
        out = _match_optimal(subpools, cond_names, match_on, center, scale, n)
        _check_shortfall(out["set"].nunique(), n, shortfall)
        _assert_distinct_words(out)
        return out
    # A covariance-aware metric for Mahalanobis matching (None -> plain Euclidean).
    metric = _maha_metric(_zmat(pool, match_on, center, scale)) if method == "mahalanobis" else None

    anchor_pool = subpools[0]
    if len(anchor_pool) == 0:
        raise ValueError(f"lexsync: anchor condition '{cond_names[0]}' has no candidates.")
    # An anchor without define_by orders by the default dimension, as the R
    # engine's names(NULL)[1] falls back to "frequency".
    ord_keys = list((conditions[0].get("define_by") or {}).keys())
    ord_dim = ord_keys[0] if ord_keys else "frequency"
    if ord_dim not in anchor_pool.columns:
        ord_dim = "frequency"
    anchor_pool = (anchor_pool.assign(_k=anchor_pool["word"].map(lambda w: w.encode("utf-8")))
                   .sort_values([ord_dim, "_k"], kind="mergesort").drop(columns="_k").reset_index(drop=True))
    n_take = min(n, len(anchor_pool))
    idx1 = np.unique(np.round(np.linspace(1, len(anchor_pool), n_take)).astype(int))
    anchor = anchor_pool.iloc[idx1 - 1].copy()
    anchor["condition"] = cond_names[0]
    n_take = len(anchor)
    _check_shortfall(n_take, n, shortfall)
    if verbose and n_take < n:
        print(f"lexsync: anchor condition '{cond_names[0]}' yields only {n_take} items; "
              f"n_per_condition is {n}.")
    z_anchor = _zmat(anchor, match_on, center, scale)

    win = {}
    for d in match_on:
        m = _exact_mean(anchor[d].dropna())
        s = _exact_sd(anchor[d].dropna())
        k = tol_k.get(d, 2)
        win[d] = (m - k * s, m + k * s)

    selected = [anchor]
    used_words = set(anchor["word"])
    relaxations = []

    for ci in range(1, len(conditions)):
        cname = cond_names[ci]
        cand = subpools[ci]
        cand = cand[~cand["word"].isin(used_words)]
        if len(cand) == 0:
            raise ValueError(f"lexsync: condition '{cname}' has no candidates left to match.")
        keep = np.ones(len(cand), dtype=bool)
        for d in match_on:
            col = cand[d].to_numpy()
            keep &= (col >= win[d][0]) & (col <= win[d][1])
        cand_f = cand[keep]
        if len(cand_f) < n_take:
            if on_tol == "error":
                raise ValueError(f"lexsync: condition '{cname}' has {len(cand_f)} candidates "
                                 f"within tolerance but {n_take} are needed; raise tolerance_k "
                                 f"or set matching: on_insufficient_tolerance: relax to widen "
                                 f"the window.")
            if verbose:
                print(f"lexsync: condition '{cname}' has {len(cand_f)} candidates within tolerance "
                      f"(< {n_take} needed); relaxing the window.")
            # The relaxation changes what "matched" means for this condition, so it
            # is recorded on the result for the run log and datasheet, not only
            # narrated.
            relaxations.append({"condition": cname,
                                "n_within_tolerance": int(len(cand_f)),
                                "n_needed": int(n_take)})
            cand_f = cand
        if len(cand_f) < n_take:
            # The assignment below would otherwise re-pick an exhausted pool's first
            # item (every remaining distance is Inf, so the tie-break decides), and
            # emit the same word in several sets.
            raise ValueError(f"lexsync: condition '{cname}' has only {len(cand_f)} candidate(s) "
                             f"but {n_take} are needed; widen pool_filters/define_by or lower "
                             f"n_per_condition.")
        # Relaxing the window re-admits rows missing a matched dimension. Their distance
        # is NaN and they rank last, so they are never assigned; counting them would let an
        # NA-depleted pool past the guard above and back into re-picking used rows.
        usable = int(cand_f[match_on].notna().all(axis=1).sum())
        if usable < n_take:
            raise ValueError(f"lexsync: condition '{cname}' has only {usable} usable candidate(s) "
                             f"complete on the matched dimensions but {n_take} are needed; widen "
                             f"pool_filters/define_by or lower n_per_condition.")
        cand_f = cand_f.reset_index(drop=True)
        z_cand = _zmat(cand_f, match_on, center, scale)
        words = cand_f["word"].to_numpy()
        ids = cand_f["id"].to_numpy()
        used = np.zeros(len(cand_f), dtype=bool)
        pick = np.empty(n_take, dtype=int)
        for a in range(n_take):
            # Rounded to 9 dp through the shared rule so the stable tie-break below
            # is itself reproducible across R and Python. np.round would pair
            # numpy's scale-rint-unscale with R's decimal algorithm, a pairing
            # io_utils documents as disagreeing at boundaries -- and on the
            # mahalanobis path the inputs already differ in their last bits, so
            # the absorber must be the same function in both engines.
            delta = z_cand - z_anchor[a]
            if metric is None:
                dvec = _round_dp_vec(np.sqrt((delta ** 2).sum(axis=1)), 9)
            else:
                dvec = _round_dp_vec(np.sqrt(np.maximum((delta @ metric * delta).sum(axis=1), 0.0)), 9)
            dvec = np.where(used, np.inf, dvec)
            # A relaxed window can admit a row whose matched dimension is missing, and
            # its distance is NaN. Rank those last, as R's order(na.last = TRUE) does:
            # a bare min() over NaN keeps whichever row it saw first, so the selection
            # would otherwise depend on pool row order and diverge from the R engine.
            nan_last = np.isnan(dvec)
            best = min(range(len(cand_f)),
                       key=lambda j: (bool(nan_last[j]), 0.0 if nan_last[j] else dvec[j],
                                      words[j].encode("utf-8"), int(ids[j])))
            pick[a] = best
            used[best] = True
        sel = cand_f.iloc[pick].copy()
        sel["condition"] = cname
        used_words |= set(sel["word"])
        selected.append(sel)

    common = [c for c in selected[0].columns if all(c in s.columns for s in selected)]
    out = pd.concat([s[common] for s in selected], ignore_index=True)
    out["set"] = list(range(1, n_take + 1)) * len(conditions)
    _assert_distinct_words(out)
    if relaxations:
        # pd.concat and rbind both drop attrs, so the pipeline reads this
        # immediately after the call, before any reshaping.
        out.attrs["audit"] = {"window_relaxations": relaxations}
    return out


def select_continuous_stimuli(pool: pd.DataFrame, design: dict, schema: dict,
                              verbose: bool = False, key: str = "word",
                              label: str | None = "continuous",
                              renumber_sets: bool = True) -> pd.DataFrame:
    """Select a set that spans a continuous predictor, holding controls constant.

    Instead of dichotomising the predictor into conditions and matching, items are
    chosen to cover the predictor's range evenly while the control dimensions are
    held within a tolerance band, so they stay near-constant and near-uncorrelated
    with the predictor. The set is analysed by regression / mixed models rather
    than by between-condition contrasts, which avoids the loss of power and the
    selection artefacts of matched dichotomies (Kuperman, 2015; Liben-Nowell et
    al., 2019).

    Two deterministic passes reuse the matcher's even-spread primitive, so the R
    and Python engines select byte-identical stimuli: an even spread over the
    predictor defines a tolerance window on each control; the pool is filtered to
    that window; a second even spread over the filtered pool is the selection.
    There is no per-item matching and no random number generator.
    """
    cfg = design["continuous"]
    predictor = cfg["predictor"]
    controls = list(cfg.get("controls") or [])
    match_on = list(design.get("match_on") or [])
    if not controls:
        raise ValueError("lexsync: a continuous design needs at least one control "
                         "dimension (continuous.controls must be non-empty).")
    if predictor in controls:
        raise ValueError(f"lexsync: the continuous predictor '{predictor}' must not "
                         "also appear in continuous.controls.")
    if sorted(match_on) != sorted(controls):
        raise ValueError("lexsync: for a continuous design, match_on must equal "
                         "continuous.controls.")
    for d in [predictor] + controls:
        if d not in pool.columns:
            raise ValueError(f"lexsync: dimension '{d}' is absent from the pool.")
    if key not in pool.columns:
        raise ValueError(
            "lexsync: the continuous tie-break column '%s' is absent from the pool." % key)
    n = design.get("n_per_condition") or design.get("n_per_cell") or 60
    tol_k = dict(schema["matching"].get("tolerance_k") or {})
    tol_k.update((design.get("matching") or {}).get("tolerance_k") or {})
    shortfall = _resolve_policy(design, schema, "shortfall", "error", ("error", "allow"))
    on_tol = _resolve_policy(design, schema, "on_insufficient_tolerance", "relax",
                             ("relax", "error"))
    for d in controls:
        k = tol_k.get(d, 2)
        if isinstance(k, (int, float)) and k < 0:
            raise ValueError(f"lexsync: tolerance_k for dimension '{d}' is negative; "
                             f"tolerances must be zero or positive.")

    def even_spread(df):
        # `key` is the deterministic tie-break when two rows share a predictor
        # value: `word` for a corpus pool, `set` for a collapsed pair table where
        # no `word` column exists. A text key is compared as UTF-8 BYTES, which is
        # what R's radix sort does; a numeric key is compared numerically in both.
        k = df[key]
        if pd.api.types.is_object_dtype(k) or pd.api.types.is_string_dtype(k):
            k = k.map(lambda w: str(w).encode("utf-8"))
        df = (df.assign(_k=k)
              .sort_values([predictor, "_k"], kind="mergesort")
              .drop(columns="_k").reset_index(drop=True))
        if len(df) == 0:
            return df
        n_take = min(n, len(df))
        idx = np.unique(np.round(np.linspace(1, len(df), n_take)).astype(int))
        return df.iloc[idx - 1].reset_index(drop=True)

    # Pass 1: an even spread over the whole pool defines the control windows.
    spread = even_spread(pool)
    if len(spread) == 0:
        raise ValueError("lexsync: the pool is empty for the continuous design.")
    win = {}
    for d in controls:
        m = _exact_mean(spread[d].dropna())
        s = _exact_sd(spread[d].dropna())
        k = tol_k.get(d, 2)
        win[d] = (m - k * s, m + k * s)
    keep = np.ones(len(pool), dtype=bool)
    for d in controls:
        col = pool[d].to_numpy()
        keep &= (col >= win[d][0]) & (col <= win[d][1])
    filtered = pool[keep]
    relaxations = []
    if len(filtered) < n:
        if on_tol == "error":
            raise ValueError(f"lexsync: {len(filtered)} items lie within the control windows "
                             f"but {n} are needed; raise tolerance_k or set matching: "
                             f"on_insufficient_tolerance: relax to widen the window.")
        if verbose:
            print(f"lexsync: {len(filtered)} items within the control windows "
                  f"(< {n} needed); relaxing to the full pool.")
        relaxations.append({"condition": "continuous",
                            "n_within_tolerance": int(len(filtered)),
                            "n_needed": int(n)})
        filtered = pool
    # Pass 2: an even spread over the filtered pool is the selection.
    sel = even_spread(filtered).copy()
    _check_shortfall(len(sel), n, shortfall, continuous=True)
    # A pair table already carries its own `condition` and `set`, which the Latin
    # square and the trial-order digest depend on, so the pair path passes
    # label=None and renumber_sets=False to leave both alone.
    if label is not None:
        sel["condition"] = label
    if renumber_sets:
        sel["set"] = list(range(1, len(sel) + 1))
    if relaxations:
        sel.attrs["audit"] = {"window_relaxations": relaxations}
    return sel


def resample_stimuli(pool: pd.DataFrame, design: dict, schema: dict,
                     n_sets: int, verbose: bool = False) -> pd.DataFrame:
    """Produce ``n_sets`` disjoint matched item sets (a ``replicate`` column).

    Each replicate is an independent, fully matched set drawn from the pool with
    the items of earlier replicates removed, so no item is reused. This lets a
    study treat its items as a random factor (running different item samples
    across participant groups, or showing an effect holds across samples) instead
    of treating them as a fixed set (Clark, 1973; Yarkoni, 2022). Deterministic: the matcher is
    deterministic and the used-item set evolves identically across engines.
    """
    used: set = set()
    parts = []
    for k in range(1, int(n_sets) + 1):
        pk = pool[~pool["word"].isin(used)].reset_index(drop=True)
        sk = match_stimuli(pk, design, schema, verbose=verbose).copy()
        sk["replicate"] = k
        used |= set(sk["word"])
        parts.append(sk)
    return pd.concat(parts, ignore_index=True)
