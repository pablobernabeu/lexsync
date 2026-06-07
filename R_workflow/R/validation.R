# validation.R -- match-quality reporting: per-condition descriptive statistics,
# standardised mean differences and equivalence tests. This elevates the
# original workflow's equal-frequency warning loop into an inspectable report.

#' Per-group descriptive statistics for several dimensions
#'
#' @param stimuli A stimuli data frame.
#' @param dims Character vector of dimension columns.
#' @param by Grouping column (default `"condition"`).
#' @return A long data frame with n, mean, sd, min, median and max per group.
#' @importFrom stats sd median
#' @export
describe_stimuli <- function(stimuli, dims, by = "condition") {
  groups <- split(stimuli, stimuli[[by]])
  rows <- list()
  for (g in names(groups)) {
    d <- groups[[g]]
    for (dim in dims) {
      x <- suppressWarnings(as.numeric(d[[dim]]))
      rows[[length(rows) + 1]] <- data.frame(
        group = g, dimension = dim, n = sum(!is.na(x)),
        mean = mean(x, na.rm = TRUE), sd = stats::sd(x, na.rm = TRUE),
        min = suppressWarnings(min(x, na.rm = TRUE)),
        median = stats::median(x, na.rm = TRUE),
        max = suppressWarnings(max(x, na.rm = TRUE)),
        stringsAsFactors = FALSE
      )
    }
  }
  out <- do.call(rbind, rows)
  numcols <- c("mean", "sd", "min", "median", "max")
  out[numcols] <- lapply(out[numcols], function(v) round(v, 3))
  out
}

#' Cohen's d (pooled-SD standardised mean difference)
#'
#' @param x,y Numeric vectors.
#' @return The standardised mean difference, or 0 when undefined.
#' @importFrom stats var
#' @export
cohens_d <- function(x, y) {
  x <- x[!is.na(x)]; y <- y[!is.na(y)]
  nx <- length(x); ny <- length(y)
  if (nx < 2 || ny < 2) return(0)
  sp <- sqrt(((nx - 1) * stats::var(x) + (ny - 1) * stats::var(y)) / (nx + ny - 2))
  if (is.na(sp) || sp == 0) return(0)
  (mean(x) - mean(y)) / sp
}

#' Two one-sided tests (TOST) of equivalence on a Cohen's d bound
#'
#' Reports the larger of the two one-sided p-values; a value below `alpha`
#' supports equivalence within +/- `bound_d` standard deviations. A
#' non-significant difference test is not itself evidence of equivalence, hence
#' TOST is reported alongside the standardised mean difference (Lakens, 2017).
#'
#' @param x,y Numeric vectors.
#' @param bound_d Smallest effect size of interest (Cohen's d).
#' @param alpha Significance level.
#' @return A list with `p` and logical `equivalent`.
#' @importFrom stats var pt
#' @export
tost_equiv <- function(x, y, bound_d = 0.4, alpha = 0.05) {
  x <- x[!is.na(x)]; y <- y[!is.na(y)]
  nx <- length(x); ny <- length(y)
  if (nx < 2 || ny < 2) return(list(p = NA_real_, equivalent = NA))
  sp <- sqrt(((nx - 1) * stats::var(x) + (ny - 1) * stats::var(y)) / (nx + ny - 2))
  se <- sp * sqrt(1 / nx + 1 / ny)
  if (is.na(se) || se == 0) return(list(p = NA_real_, equivalent = NA))
  bound <- bound_d * sp
  dfree <- nx + ny - 2
  diff <- mean(x) - mean(y)
  t_low <- (diff + bound) / se
  t_high <- (diff - bound) / se
  p <- max(stats::pt(t_low, dfree, lower.tail = FALSE),
           stats::pt(t_high, dfree, lower.tail = TRUE))
  list(p = p, equivalent = isTRUE(p < alpha))
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

#' Build the full match-quality report
#'
#' @param stimuli A matched-stimuli data frame (must contain `condition`).
#' @param dims Dimensions to summarise and compare.
#' @param schema The parsed global schema (equivalence settings).
#' @return A list with `descriptives` and `comparisons` data frames.
#' @export
match_report <- function(stimuli, dims, schema) {
  conds <- unique(stimuli$condition)
  anchor <- conds[1]
  desc <- describe_stimuli(stimuli, dims, by = "condition")
  bound <- schema$equivalence$bound_d %||% 0.4
  alpha <- schema$equivalence$alpha %||% 0.05
  comp <- list()
  for (cc in conds[-1]) {
    for (dim in dims) {
      x <- suppressWarnings(as.numeric(stimuli[stimuli$condition == anchor, dim, drop = TRUE]))
      y <- suppressWarnings(as.numeric(stimuli[stimuli$condition == cc, dim, drop = TRUE]))
      tt <- tost_equiv(x, y, bound_d = bound, alpha = alpha)
      comp[[length(comp) + 1]] <- data.frame(
        condition = cc, reference = anchor, dimension = dim,
        cohens_d = round(cohens_d(x, y), 3),
        tost_p = round(tt$p, 4), equivalent = tt$equivalent,
        stringsAsFactors = FALSE
      )
    }
  }
  list(descriptives = desc, comparisons = do.call(rbind, comp))
}
