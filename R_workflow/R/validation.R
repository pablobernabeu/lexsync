# validation.R -- match-quality reporting: per-condition descriptive statistics,
# standardised mean differences and equivalence tests. This elevates the
# original workflow's equal-frequency warning loop into an inspectable report.
#
# The one place a non-elementary function reaches a compared artefact. Everything
# else on the path to a stimuli, descriptives or comparisons file is built from
# operations IEEE-754 either mandates correctly rounded or makes exact, so the two
# engines agree by construction. The Student t quantile and distribution behind
# the confidence interval and the TOST p-value are not among those: stats::qt and
# stats::pt here, scipy.stats.t there, two independent implementations. Measured
# on R 4.6.1 against SciPy 1.17.1, they disagree by at most about 1e-12 over the
# range these reports use, while the published values are rounded to three and
# four decimal places, which leaves 5e-4 and 5e-5 of headroom before a byte could
# move. The comparisons artefacts are therefore byte-identical on the evidence of
# a margin of some seven orders of magnitude, not on the by-construction argument
# that carries the rest. Mirrors the note in validation.py.

# Refuse a grouping column or a dimension the stimuli do not carry. The reports are
# exported for use on a selection of one's own, where a misspelt dimension gave a table
# of missing values with n of 0, which looked complete, and the Python twin a bare
# KeyError. Mirrors _require_columns in validation.py.
.require_columns <- function(stimuli, dims, by = NULL) {
  if (!is.null(by) && !by %in% names(stimuli)) {
    stop(sprintf("lexsync: grouping column '%s' is not a column of the stimuli.", by),
         call. = FALSE)
  }
  for (d in dims) {
    if (!d %in% names(stimuli)) {
      stop(sprintf("lexsync: dimension '%s' is not a column of the stimuli.", d),
           call. = FALSE)
    }
  }
  invisible(NULL)
}

#' Per-group descriptive statistics for several dimensions
#'
#' A grouping column or a dimension the stimuli do not carry is refused.
#'
#' @param stimuli A stimuli data frame.
#' @param dims Character vector of dimension columns.
#' @param by Grouping column (default `"condition"`).
#' @return A long data frame with n, mean, sd, min, median and max per group.
#' @export
describe_stimuli <- function(stimuli, dims, by = "condition") {
  .require_columns(stimuli, dims, by)
  # Group in order of first appearance: split() alone coerces to a factor whose
  # levels are locale-collated sort(unique(x)), which diverges from validation.py's
  # groupby(sort = FALSE) and from the anchor match_report() takes from unique().
  by_vals <- as.character(stimuli[[by]])
  groups <- split(stimuli, factor(by_vals, levels = unique(by_vals)))
  rows <- list()
  for (g in names(groups)) {
    d <- groups[[g]]
    for (dim in dims) {
      x <- .numeric_values(d[[dim]])
      xv <- x[!is.na(x)]
      rows[[length(rows) + 1]] <- data.frame(
        group = g, dimension = dim, n = length(xv),
        mean = .exact_mean(xv), sd = .exact_sd(xv),
        # NA (not Inf/-Inf, which is what min/max of an empty vector give) when a
        # dimension is entirely missing, so both engines agree.
        min = if (length(xv)) min(xv) else NA_real_,
        # .exact_median, not stats::median: the latter averages the two middle
        # values through mean()'s long-double accumulator, the one reduction
        # here that would bypass the shared exact primitives.
        median = .exact_median(xv),
        max = if (length(xv)) max(xv) else NA_real_,
        stringsAsFactors = FALSE
      )
    }
  }
  # No dimension to describe, as when match_report() leaves out every one it was given:
  # the columns with no rows, as the Python twin returns, in place of NULL.
  if (!length(rows)) {
    return(data.frame(group = character(0), dimension = character(0), n = integer(0),
                      mean = numeric(0), sd = numeric(0), min = numeric(0),
                      median = numeric(0), max = numeric(0), stringsAsFactors = FALSE))
  }
  out <- do.call(rbind, rows)
  numcols <- c("mean", "sd", "min", "median", "max")
  out[numcols] <- lapply(out[numcols], function(v) .round_dp(v, 3))
  out
}

#' Cohen's d (pooled-SD standardised mean difference)
#'
#' @param x,y Numeric vectors.
#' @return The standardised mean difference. It is 0 when both samples share one
#'   constant, and `NA` when either sample has fewer than two values (one value has
#'   no spread, so the pooled SD is undefined) or when the pooled SD is zero but the
#'   means differ (the standardised difference is then unbounded, not zero).
#' @examples
#' cohens_d(c(5, 6, 7, 8), c(5, 6, 7, 9))
#' @export
cohens_d <- function(x, y) {
  x <- x[!is.na(x)]; y <- y[!is.na(y)]
  nx <- length(x); ny <- length(y)
  # Undefined, not 0: a frequency contrast of 6.5 against 3.9 Zipf with one item a
  # side was reported as a perfect balance.
  if (nx < 2 || ny < 2) return(NA_real_)
  sp <- sqrt(((nx - 1) * .exact_var(x) + (ny - 1) * .exact_var(y)) / (nx + ny - 2))
  if (is.na(sp) || sp == 0) {
    # Two constants: an exactly-zero difference is exactly zero SDs apart, but
    # unequal constants are infinitely many. That is undefined, not perfect balance.
    if (.exact_mean(x) - .exact_mean(y) == 0) return(0)
    return(NA_real_)
  }
  (.exact_mean(x) - .exact_mean(y)) / sp
}

#' Cohen's d with a confidence interval, complementing the TOST verdict
#'
#' The interval is the `(1 - 2 * alpha)` confidence interval for the standardised
#' mean difference, so `alpha = 0.05` gives the 90% interval that goes with a
#' TOST decision at the .05 level (Lakens, 2017). Reporting the interval, rather
#' than only a binary verdict, makes the realised imbalance and its sampling
#' uncertainty explicit, and keeps the dependence on the number of items visible.
#' With few items the interval is wide, whatever the point estimate. Both the
#' interval and the TOST treat the selected items as a sample, although a test on
#' stimuli concerns a closed population. Sassenhagen and Alday (2016) recommend
#' describing the stimuli and entering potential confounds in the analysis as
#' covariates.
#'
#' The limits are `d +/- t * SE(d)`, where `t` is the Student t quantile on
#' `nx + ny - 2` degrees of freedom and `SE(d)` is the large-sample standard
#' error of d, `sqrt(1/nx + 1/ny + d^2 / (2 * (nx + ny)))` (Hedges & Olkin, 1985;
#' Borenstein et al., 2009, eq. 4.20). The `d^2` term carries the sampling error
#' of the pooled standard deviation. It is negligible for a well-matched control,
#' where d is near zero, but it dominates for a manipulated dimension and can
#' more than double the width of that interval. TOST tests the raw mean
#' difference, so the interval is slightly wider than the one its decision
#' implies, and when a control's limit lies close to the bound, `tost_p` gives the
#' verdict.
#'
#' @param x,y Numeric vectors.
#' @param alpha Significance level matching the TOST (default 0.05).
#' @return A list with `d`, `ci_low` and `ci_high`, all three `NA` when either
#'   sample has fewer than two values, as for [cohens_d()].
#' @importFrom stats qt
#' @export
cohens_d_ci <- function(x, y, alpha = 0.05) {
  x <- x[!is.na(x)]; y <- y[!is.na(y)]
  nx <- length(x); ny <- length(y)
  if (nx < 2 || ny < 2) return(list(d = NA_real_, ci_low = NA_real_, ci_high = NA_real_))
  sp <- sqrt(((nx - 1) * .exact_var(x) + (ny - 1) * .exact_var(y)) / (nx + ny - 2))
  diff <- .exact_mean(x) - .exact_mean(y)
  if (is.na(sp) || sp == 0) {
    # Equal constants carry no sampling uncertainty: a point at zero. Unequal
    # constants are infinitely many SDs apart, so the estimate and its interval
    # are undefined, not a perfect [0, 0].
    if (diff == 0) return(list(d = 0, ci_low = 0, ci_high = 0))
    return(list(d = NA_real_, ci_low = NA_real_, ci_high = NA_real_))
  }
  d <- diff / sp
  # Large-sample variance of d: 1/nx + 1/ny + d^2 / (2 * (nx + ny)) (Hedges &
  # Olkin, 1985; Borenstein et al., 2009, eq. 4.20). Without the d^2 term the
  # interval treated the pooled SD as known, which gave a manipulated dimension
  # with d = 5.6 and 40 items a side a margin of 0.37 in place of 0.83. Written
  # with d * d, not d^2, and summed in the same order as validation.py, so both
  # engines round every step identically.
  se <- sqrt(1 / nx + 1 / ny + d * d / (2 * (nx + ny)))
  margin <- stats::qt(1 - alpha, nx + ny - 2) * se
  list(d = d, ci_low = d - margin, ci_high = d + margin)
}

#' Two one-sided tests (TOST) of equivalence on a Cohen's d bound
#'
#' Reports the larger of the two one-sided p-values; a value below `alpha`
#' supports equivalence within +/- `bound_d` standard deviations. A
#' non-significant difference test is not itself evidence of equivalence, hence
#' TOST is reported alongside the standardised mean difference (Lakens, 2017).
#'
#' @param x,y Numeric vectors.
#' @param bound_d Smallest effect size of interest (Cohen's d); defaults to the
#'   schema value of 0.5. That value is a convention and not a default of Lakens
#'   (2017), who asks for the bound to be justified for the study. At 0.5 and
#'   alpha .05, no dimension that varies can pass with fewer than 23 items per
#'   condition, even when the conditions are identical.
#' @param alpha Significance level.
#' @return A list with `p` and logical `equivalent`.
#' @importFrom stats pt
#' @export
tost_equiv <- function(x, y, bound_d = 0.5, alpha = 0.05) {
  x <- x[!is.na(x)]; y <- y[!is.na(y)]
  nx <- length(x); ny <- length(y)
  if (nx < 2 || ny < 2) return(list(p = NA_real_, equivalent = NA))
  sp <- sqrt(((nx - 1) * .exact_var(x) + (ny - 1) * .exact_var(y)) / (nx + ny - 2))
  if (is.na(sp) || sp == 0) {
    # Both conditions are constants (e.g. a dimension fixed by the pool, such as
    # two-character Chinese words). They are equivalent iff they share that
    # constant; the standardised difference is then exactly zero.
    if (.exact_mean(x) - .exact_mean(y) == 0) return(list(p = 0, equivalent = TRUE))
    return(list(p = 1, equivalent = FALSE))
  }
  se <- sp * sqrt(1 / nx + 1 / ny)
  if (is.na(se) || se == 0) return(list(p = NA_real_, equivalent = NA))
  bound <- bound_d * sp
  dfree <- nx + ny - 2
  diff <- .exact_mean(x) - .exact_mean(y)
  t_low <- (diff + bound) / se
  t_high <- (diff - bound) / se
  p <- max(stats::pt(t_low, dfree, lower.tail = FALSE),
           stats::pt(t_high, dfree, lower.tail = TRUE))
  list(p = p, equivalent = isTRUE(p < alpha))
}

#' Variance ratio: a distributional balance check
#'
#' The ratio of a condition's variance to the reference's, complementing the
#' mean-based Cohen's d and TOST. Two conditions can share a mean yet differ in
#' spread and still confound, which a mean-based statistic misses
#' (Armstrong et al., 2012; Austin, 2009). A ratio near 1 is balanced; a common
#' heuristic flags ratios outside roughly 0.5 to 2.
#'
#' @param cond,ref Numeric vectors (condition and reference).
#' @return The variance ratio, or `NA` when a variance is undefined.
#' @examples
#' variance_ratio(c(1, 2, 3, 4), c(1, 2, 3, 8))
#' @export
variance_ratio <- function(cond, ref) {
  cond <- cond[!is.na(cond)]; ref <- ref[!is.na(ref)]
  if (length(cond) < 2 || length(ref) < 2) return(NA_real_)
  v_ref <- .exact_var(ref)
  if (v_ref == 0) return(if (.exact_var(cond) == 0) 1 else NA_real_)
  as.numeric(.exact_var(cond) / v_ref)
}

#' Check that the levels of given columns occur equally often
#'
#' @param stimuli A stimuli data frame.
#' @param columns Columns whose level counts should be equal.
#' @return A character vector of human-readable balance warnings (empty if none).
#' @export
balance_check <- function(stimuli, columns) {
  issues <- character(0)
  for (col in columns) {
    if (!col %in% names(stimuli)) next
    tab <- table(stimuli[[col]])
    if (length(unique(as.integer(tab))) > 1) {
      issues <- c(issues, sprintf(
        "Column '%s' is unbalanced: %s", col,
        paste(sprintf("%s=%d", names(tab), as.integer(tab)), collapse = ", ")
      ))
    }
  }
  issues
}

# A dimension's values as numbers, with a missing value or a non-number as NA. A factor
# is read by its labels, not its codes, as pandas reads a category. Mirrors _numeric in
# validation.py.
.numeric_values <- function(v) {
  if (is.factor(v)) v <- as.character(v)
  suppressWarnings(as.numeric(v))
}

# The dimensions a report can compare, in the order given. A dimension with no numeric
# value among the stimuli is left out: one every item lacks, as n_syllables is for a
# Chinese word, or one that is not numeric, as a part-of-speech label named in a
# condition's define_by is. A name that is not a column of the stimuli is refused.
# Mirrors _reportable in validation.py.
.reportable <- function(stimuli, dims) {
  .require_columns(stimuli, dims)
  keep <- vapply(dims, function(d) any(!is.na(.numeric_values(stimuli[[d]]))), logical(1))
  dims[keep]
}

# The (reference, condition) pairs a report compares, in order. The anchor rows come
# first, every other condition against the first, as a 0.1 report gave them. Every
# further pair (i, j) with 2 <= i < j follows in condition order, with condition i as
# the reference. Mirrors _condition_pairs in validation.py.
.condition_pairs <- function(conds) {
  k <- length(conds)
  pairs <- lapply(conds[-1], function(cc) c(conds[1], cc))
  if (k > 2L) {
    for (i in 2:(k - 1L)) {
      for (j in (i + 1L):k) pairs[[length(pairs) + 1L]] <- c(conds[i], conds[j])
    }
  }
  pairs
}

#' Build the full match-quality report
#'
#' @param stimuli A matched-stimuli data frame (must contain `condition`).
#' @param dims Dimensions to summarise and compare.
#' @param schema The parsed global schema (equivalence settings).
#' @param roles Optional function of `condition`, `reference` and `dimension` that
#'   returns the row's `role`: `"manipulated"` when the design sets the two
#'   conditions apart on the dimension, `"controlled"` when it matches them on it
#'   and `"uncontrolled"` otherwise. [run_pipeline()] derives it from the design.
#'   Without it, `role` is `NA`.
#' @return A list with `descriptives` and `comparisons` data frames. Every pair of
#'   conditions is compared on every dimension. The rows against the first condition
#'   in order of appearance, the anchor, come first, then every further pair in
#'   condition order, so a design with a single condition has nothing to compare and
#'   `comparisons` comes back with its columns and no rows. A dimension with no
#'   numeric value among the stimuli, such as `n_syllables` for Chinese or a text
#'   label, is left out of both frames.
#'
#'   Each row of `comparisons` names the earlier condition of its pair in `reference`
#'   and the later one in `condition`. The signed statistics run from the reference
#'   to the other condition: `cohens_d`, `d_ci_low` and `d_ci_high` are the
#'   reference mean minus the `condition` mean, in pooled standard deviations, so a
#'   positive d means the reference scores higher. `mean_diff` is the same
#'   difference in the dimension's own unit, to three places. `var_ratio` is the
#'   other way up, the `condition` variance over the reference variance.
#' @export
match_report <- function(stimuli, dims, schema, roles = NULL) {
  .require_columns(stimuli, character(0), "condition")
  conds <- unique(as.character(stimuli$condition))
  dims <- .reportable(stimuli, dims)
  desc <- describe_stimuli(stimuli, dims, by = "condition")
  bound <- schema[["equivalence"]][["bound_d"]] %||% 0.5
  alpha <- schema[["equivalence"]][["alpha"]] %||% 0.05
  comp <- list()
  for (pr in .condition_pairs(conds)) {
    ref <- pr[[1]]; cc <- pr[[2]]
    for (dim in dims) {
      x <- .numeric_values(stimuli[stimuli$condition == ref, dim, drop = TRUE])
      y <- .numeric_values(stimuli[stimuli$condition == cc, dim, drop = TRUE])
      tt <- tost_equiv(x, y, bound_d = bound, alpha = alpha)
      ci <- cohens_d_ci(x, y, alpha = alpha)
      vr <- variance_ratio(y, x)
      # The raw difference needs one value a side, where d needs two.
      xv <- x[!is.na(x)]; yv <- y[!is.na(y)]
      diff <- if (length(xv) && length(yv)) .exact_mean(xv) - .exact_mean(yv) else NA_real_
      role <- if (is.null(roles)) NULL else roles(cc, ref, dim)
      comp[[length(comp) + 1]] <- data.frame(
        condition = cc, reference = ref, dimension = dim,
        cohens_d = .round_dp(cohens_d(x, y), 3),
        d_ci_low = .round_dp(ci$ci_low, 3), d_ci_high = .round_dp(ci$ci_high, 3),
        var_ratio = if (is.na(vr)) NA_real_ else .round_dp(vr, 3),
        tost_p = .round_dp(tt$p, 4), equivalent = tt$equivalent,
        mean_diff = .round_dp(diff, 3),
        role = if (length(role) == 1L) as.character(role) else NA_character_,
        stringsAsFactors = FALSE
      )
    }
  }
  list(descriptives = desc,
       comparisons = if (length(comp)) do.call(rbind, comp) else .empty_comparisons())
}

# The comparisons frame a single-condition design produces: the columns, no rows.
# rbind() of an empty list returns NULL, which run_pipeline's seq_len(nrow(...)) loop
# then died on with "argument must be coercible to non-negative integer", naming
# neither the design nor the cause, while the Python engine went on and wrote a
# comparisons CSV with no header at all. Naming the columns here gives both engines
# the same header-only file and the same empty loop. `mean_diff` and `role` follow the
# columns a 0.1 reader already knows.
# Must list the same columns, in the same order, as _COMPARISON_COLUMNS in
# python_workflow/src/lexsync/validation.py.
#' @keywords internal
.empty_comparisons <- function() {
  data.frame(condition = character(0), reference = character(0),
             dimension = character(0), cohens_d = numeric(0),
             d_ci_low = numeric(0), d_ci_high = numeric(0),
             var_ratio = numeric(0), tost_p = numeric(0),
             equivalent = logical(0), mean_diff = numeric(0),
             role = character(0), stringsAsFactors = FALSE)
}

# Pearson correlation from raw sums, rounded to 9 dp so it is byte-comparable across
# the R and Python engines (not stats::cor). Mirrors validation.py _pearson.
.pearson <- function(x, y) {
  ok <- !(is.na(x) | is.na(y)); x <- x[ok]; y <- y[ok]
  if (length(x) < 2) return(NA_real_)
  dx <- x - .exact_mean(x); dy <- y - .exact_mean(y)
  denom <- sqrt(.exact_sum(dx * dx) * .exact_sum(dy * dy))
  if (denom == 0) return(0)
  .round_dp(.exact_sum(dx * dy) / denom, 9)
}

# a / b, or NA when either is missing or b is zero. Mirrors _ratio in validation.py.
.ratio <- function(a, b) {
  if (is.null(a) || is.null(b) || is.na(a) || is.na(b) || b == 0) NA_real_ else a / b
}

#' Realised-control report for a continuous design
#'
#' Returns the same list shape as [match_report()] (`descriptives` + `comparisons`),
#' but the comparisons describe a continuous predictor: its realised span and, for
#' each control, the Pearson correlation with the predictor (near zero when the
#' control is held constant). Mirrors match_report_continuous in validation.py.
#'
#' `sd` is each dimension's realised SD. For the predictor, `sd_ratio` sets it
#' against the SD of as many values spaced evenly over the same range,
#' `(max - min) * sqrt(n * (n + 1) / 12) / (n - 1)` with the n - 1 that `sd` uses, so
#' an even spread has a ratio of 1 whatever its size and a selection that follows a
#' skewed pool a ratio below 1. That benchmark tends to `(max - min) / sqrt(12)`, the
#' SD of a uniform distribution over the range, as n grows. For a control, `sd_ratio`
#' sets the realised SD against the SD of the pool the selector drew from, and
#' `window_low` and `window_high` give the window the selector banded it to, before
#' any relaxation. Both come from `audit`, the selector's record.
#'
#' @param stimuli A stimuli data frame (a single "continuous" group).
#' @param predictor The spanned predictor dimension.
#' @param controls Character vector of control dimensions.
#' @param schema The parsed global schema.
#' @param audit The selector's audit record, by default the `"audit"` attribute
#'   [select_continuous_stimuli()] attaches to its result. Its `control_windows`
#'   give each control's window and pool SD. Without them, a control's `sd_ratio`
#'   and window are `NA`.
#' @return A list with `descriptives` and `comparisons` data frames.
#' @export
match_report_continuous <- function(stimuli, predictor, controls, schema,
                                    audit = attr(stimuli, "audit")) {
  windows <- list()
  for (w in audit[["control_windows"]] %||% list()) windows[[w[["dimension"]]]] <- w
  desc <- describe_stimuli(stimuli, c(predictor, controls), by = "condition")
  pv <- suppressWarnings(as.numeric(stimuli[[predictor]]))
  valid <- pv[!is.na(pv)]
  # NA (not -Inf) when the predictor has no span, so both engines agree.
  span <- if (length(valid) >= 2) .round_dp(max(valid) - min(valid), 3) else NA_real_
  # The SD of n values spaced evenly over the realised range. (max - min) / sqrt(12)
  # alone is its limit for large n, and against it an even spread of 4 values read
  # 1.49, as if the items crowded the ends of the range. The operations run in the
  # order of the Python twin, so both engines get the same double.
  nv <- as.numeric(length(valid))
  even <- if (nv >= 2) (max(valid) - min(valid)) * sqrt(nv * (nv + 1) / 12) / (nv - 1)
          else NA_real_
  sd <- .exact_sd(valid)
  rows <- list(data.frame(dimension = predictor, role = "predictor",
                          pearson_r = NA_real_, predictor_span = span,
                          sd = .round_dp(sd, 3), sd_ratio = .round_dp(.ratio(sd, even), 3),
                          window_low = NA_real_, window_high = NA_real_,
                          stringsAsFactors = FALSE))
  for (cc in controls) {
    cv <- suppressWarnings(as.numeric(stimuli[[cc]]))
    r <- .pearson(pv, cv)
    csd <- .exact_sd(cv[!is.na(cv)])
    w <- windows[[cc]]
    rows[[length(rows) + 1L]] <- data.frame(
      dimension = cc, role = "control",
      pearson_r = if (is.na(r)) NA_real_ else .round_dp(r, 3),
      predictor_span = span, sd = .round_dp(csd, 3),
      sd_ratio = .round_dp(.ratio(csd, w[["pool_sd"]]), 3),
      window_low = .round_dp(w[["low"]] %||% NA_real_, 3),
      window_high = .round_dp(w[["high"]] %||% NA_real_, 3),
      stringsAsFactors = FALSE)
  }
  list(descriptives = desc, comparisons = do.call(rbind, rows))
}
