test_that("cohens_d is zero for identical samples and large for separated ones", {
  expect_equal(cohens_d(c(1, 2, 3, 4), c(1, 2, 3, 4)), 0)
  expect_gt(abs(cohens_d(c(5, 6, 7, 8), c(1, 2, 3, 4))), 1)
})

test_that("tost_equiv flags closely matched samples as equivalent", {
  set.seed(1)
  x <- rep(c(4, 5, 6), 20)
  y <- rep(c(4, 5, 6), 20)
  tt <- tost_equiv(x, y, bound_d = 0.5)
  expect_true(isTRUE(tt$equivalent))
})

test_that("tost_equiv defaults to the schema's 0.5 bound", {
  # The bound is the schema's smallest effect size of interest (Lakens, 2017);
  # pinned here because every other test passes bound_d explicitly. The p-value is
  # the same literal asserted in test_validation.py, so the engines cannot drift apart.
  expect_identical(formals(tost_equiv)$bound_d, 0.5)
  expect_equal(round(tost_equiv(10:19, 11:20)$p, 9), 0.354383811)
})

test_that("cohens_d_ci brackets the point estimate and matches cohens_d", {
  x <- rep(c(5, 6, 7, 8), 10); y <- rep(c(1, 2, 3, 4), 10)
  ci <- cohens_d_ci(x, y)
  expect_lte(ci$ci_low, ci$d)
  expect_lte(ci$d, ci$ci_high)
  expect_equal(ci$d, cohens_d(x, y), tolerance = 1e-9)
})

test_that("cohens_d_ci uses the large-sample standard error of d", {
  # SE(d) = sqrt(1/nx + 1/ny + d^2 / (2 * (nx + ny))) (Hedges & Olkin, 1985;
  # Borenstein et al., 2009, eq. 4.20). The limits are the same literals asserted
  # in test_validation.py, so the engines cannot drift apart. The interval that
  # left out the d^2 term had a margin of 0.372 here, not 0.596.
  x <- rep(c(5, 6, 7, 8), 10); y <- rep(c(1, 2, 3, 4), 10)
  ci <- cohens_d_ci(x, y)
  expect_equal(round(c(ci$d, ci$ci_low, ci$ci_high), 9),
               c(3.532704347, 2.937150129, 4.128258564))
  se <- sqrt(1 / 40 + 1 / 40 + ci$d^2 / 160)
  expect_equal(ci$ci_high - ci$d, stats::qt(0.95, 78) * se, tolerance = 1e-12)
  # The d^2 term is what widens a large effect's interval: at the same n, a
  # difference near zero keeps close to the known-SD margin.
  null <- cohens_d_ci(rep(c(4, 5, 6), 20), rep(c(4, 5, 6), 20))
  expect_equal(null$ci_high, stats::qt(0.95, 118) * sqrt(2 / 60), tolerance = 1e-12)
  expect_gt(ci$ci_high - ci$ci_low, 1.5 * (2 * stats::qt(0.95, 78) * sqrt(1 / 20)))
})

test_that("cohens_d_ci width shrinks as the number of items grows", {
  small <- cohens_d_ci(rep(c(4, 5, 6), 2),  rep(c(4, 5, 7), 2))
  large <- cohens_d_ci(rep(c(4, 5, 6), 40), rep(c(4, 5, 7), 40))
  expect_gt(small$ci_high - small$ci_low, large$ci_high - large$ci_low)
})

test_that("cohens_d_ci within the bound coheres with the TOST verdict", {
  x <- rep(c(4, 5, 6), 20); y <- rep(c(4, 5, 6), 20)
  ci <- cohens_d_ci(x, y, alpha = 0.05)
  within <- ci$ci_low > -0.5 && ci$ci_high < 0.5
  expect_identical(within, isTRUE(tost_equiv(x, y, bound_d = 0.5, alpha = 0.05)$equivalent))
})

test_that("cohens_d_ci is a point for a constant dimension", {
  ci <- cohens_d_ci(c(2, 2, 2, 2), c(2, 2, 2, 2))
  expect_equal(c(ci$d, ci$ci_low, ci$ci_high), c(0, 0, 0))
})

test_that("a zero pooled SD with unequal means is undefined, not zero", {
  # Two conditions each constant at a different value differ by infinitely many
  # SDs: reporting d = 0 (perfect balance) inverted the truth. The equal-constant
  # case is pinned by the zh_freqcontrast golden and must stay exactly zero.
  x <- c(2, 2, 2, 2); y <- c(3, 3, 3, 3)
  expect_true(is.na(cohens_d(x, y)))
  ci <- cohens_d_ci(x, y)
  expect_true(all(is.na(c(ci$d, ci$ci_low, ci$ci_high))))
  expect_false(tost_equiv(x, y)$equivalent)  # already correct on this branch
  expect_equal(variance_ratio(y, x), 1)      # unchanged: both spreads are zero
  expect_equal(cohens_d(x, x), 0)            # equal constants stay exactly zero
})

test_that("match_report carries an undefined d as a missing cell", {
  # Serialised as an empty CSV cell and a null JSON value, exactly like the other
  # missing statistics, and identically in both engines.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- data.frame(word = c("aa", "bb", "cc", "dd"),
                     condition = c("a", "a", "b", "b"),
                     length = c(2, 2, 3, 3), stringsAsFactors = FALSE)
  cmp <- match_report(stim, "length", schema)$comparisons
  expect_true(is.na(cmp$cohens_d))
  expect_true(is.na(cmp$d_ci_low))
  expect_true(is.na(cmp$d_ci_high))
  expect_false(cmp$equivalent)
  expect_equal(cmp$var_ratio, 1)
})

# The columns of the comparisons frame, in order: the two CS-23 columns follow the ones
# a 0.1 reader already knows. Pinned identically in test_validation.py.
comparison_header <- c("condition", "reference", "dimension", "cohens_d", "d_ci_low",
                       "d_ci_high", "var_ratio", "tost_p", "equivalent", "mean_diff", "role")

test_that("match_report gives a single-condition design an empty comparisons frame", {
  # There is nothing to compare against the anchor, so the frame comes back with its
  # columns and no rows. rbind() over an empty list used to return NULL, which
  # run_pipeline's seq_len(nrow(...)) loop died on with "argument must be coercible
  # to non-negative integer", naming neither the design nor the cause, while the
  # Python engine carried on and wrote a comparisons CSV with no header at all.
  # Pinned identically in tests/test_validation.py.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- data.frame(word = c("aa", "bb"), condition = c("only", "only"),
                     length = c(2, 3), stringsAsFactors = FALSE)
  cmp <- match_report(stim, "length", schema)$comparisons
  expect_s3_class(cmp, "data.frame")
  expect_equal(nrow(cmp), 0L)
  expect_identical(names(cmp), comparison_header)
  # The loop that used to die on NULL now runs zero times.
  expect_length(seq_len(nrow(cmp)), 0L)
})

# describe_stimuli(), match_report() and match_report_continuous() are exported for use
# on a selection of one's own. A misspelt dimension gave a table of missing values here,
# with n of 0, which looked complete, and a bare KeyError in Python. Pinned identically
# in test_validation.py.
test_that("the reports refuse a column the stimuli do not carry", {
  stim <- data.frame(condition = c("hi", "hi", "lo", "lo"), frequency = c(6, 5, 3, 2),
                     stringsAsFactors = FALSE)
  expect_error(describe_stimuli(stim, "frequncy"),
               "dimension 'frequncy' is not a column of the stimuli", fixed = TRUE)
  expect_error(describe_stimuli(stim, "frequency", by = "group"),
               "grouping column 'group' is not a column of the stimuli", fixed = TRUE)
  expect_error(match_report_continuous(stim, "frequency", "old20", list()),
               "dimension 'old20' is not a column of the stimuli", fixed = TRUE)
  renamed <- stats::setNames(stim, c("cond", "frequency"))
  expect_error(match_report(renamed, "frequency", list()),
               "grouping column 'condition' is not a column of the stimuli", fixed = TRUE)
})

test_that("cohens_d is undefined with fewer than two items a side", {
  # One item has no spread, so the pooled SD and with it d are undefined. Both
  # functions returned 0, a perfect balance, for a frequency contrast of 6.5 against
  # 3.9. Pinned identically in test_validation.py.
  expect_true(is.na(cohens_d(6.5, 3.9)))
  expect_true(is.na(cohens_d(c(6.5, 6.0), 3.9)))
  expect_true(is.na(cohens_d(numeric(0), c(3.9, 4.1))))
  ci <- cohens_d_ci(6.5, 3.9)
  expect_true(all(is.na(c(ci$d, ci$ci_low, ci$ci_high))))
  ci <- cohens_d_ci(c(NA, 6.5), c(3.9, 4.1))
  expect_true(all(is.na(c(ci$d, ci$ci_low, ci$ci_high))))
})

cont_stim <- function() {
  data.frame(word = c("a", "b", "c", "d"), condition = "continuous",
             frequency = c(2, 3, 4, 5), length = c(3, 4, 3, 4),
             n_density = c(1, 2, 1, 2), old20 = c(1.5, 1.6, 1.5, 1.6),
             stringsAsFactors = FALSE)
}

# Two items per condition, so every d is defined. Condition `b` sits above `a` on length
# by half a letter, `c` and `d` a whole letter above it.
four_conditions <- function() {
  data.frame(word = c("a1", "a2", "b1", "b2", "c1", "c2", "d1", "d2"),
             condition = c("a", "a", "b", "b", "c", "c", "d", "d"),
             length = c(3, 4, 3, 5, 4, 6, 5, 5),
             frequency = c(6.0, 6.5, 6.1, 6.3, 3.0, 3.5, 3.2, 3.1),
             stringsAsFactors = FALSE)
}

test_that("match_report compares every pair after the anchor rows", {
  # The anchor rows come first and unchanged, then every further pair in condition
  # order, with the earlier condition as the reference. Only the anchor rows were
  # reported, so a 2 x 2 design never showed its within-factor contrasts. Pinned
  # identically in test_validation.py.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- four_conditions()
  cmp <- match_report(stim, c("length", "frequency"), schema)$comparisons
  expect_identical(names(cmp), comparison_header)
  pairs <- unique(paste(cmp$condition, cmp$reference))
  expect_identical(pairs, c("b a", "c a", "d a", "c b", "d b", "d c"))
  expect_identical(cmp$dimension, rep(c("length", "frequency"), 6))
  # A further pair carries the statistics of a two-condition report on its own
  # conditions, oriented from its reference.
  alone <- match_report(stim[stim$condition %in% c("b", "c"), ], c("length", "frequency"),
                        schema)$comparisons
  row <- cmp[cmp$condition == "c" & cmp$reference == "b", ]
  stats_cols <- c("cohens_d", "d_ci_low", "d_ci_high", "var_ratio", "tost_p",
                  "equivalent", "mean_diff")
  rownames(row) <- NULL
  expect_identical(row[, stats_cols], alone[, stats_cols])
})

test_that("match_report gives the raw mean difference", {
  # The reference mean minus the condition mean, in the dimension's own unit, to three
  # places by the shared rounder. Pinned identically in test_validation.py.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  cmp <- match_report(four_conditions(), "length", schema)$comparisons
  by_pair <- stats::setNames(cmp$mean_diff, paste(cmp$condition, cmp$reference))
  expect_identical(by_pair[["b a"]], -0.5)
  expect_identical(by_pair[["c b"]], -1)
  expect_identical(by_pair[["d c"]], 0)
  thirds <- data.frame(condition = rep(c("r", "s"), each = 3),
                       x = c(1, 1, 2, 1, 1, 1), stringsAsFactors = FALSE)
  expect_identical(match_report(thirds, "x", schema)$comparisons$mean_diff, 0.333)
})

test_that("match_report reports a mean difference where d is undefined", {
  # With one item a side d is undefined, but the raw difference is not: 6.5 against
  # 3.9 Zipf is 2.6. Pinned identically in test_validation.py.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- data.frame(condition = c("high", "low"), frequency = c(6.5, 3.9),
                     stringsAsFactors = FALSE)
  row <- match_report(stim, "frequency", schema)$comparisons
  expect_true(is.na(row$cohens_d) && is.na(row$d_ci_low) && is.na(row$tost_p))
  expect_identical(row$mean_diff, 2.6)
})

test_that("match_report skips a dimension with no numeric value", {
  # A dimension every item lacks, such as n_syllables for Chinese, or one that is not
  # numeric, such as a part-of-speech label named in define_by, has nothing to compare
  # and is left out of both frames. Pinned identically in test_validation.py.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- four_conditions()
  stim$n_syllables <- NA_real_
  stim$pos <- "noun"
  rep <- match_report(stim, c("length", "n_syllables", "pos"), schema)
  expect_identical(unique(rep$comparisons$dimension), "length")
  expect_identical(unique(rep$descriptives$dimension), "length")
  # With nothing left, both frames keep their columns and have no rows.
  none <- match_report(stim, "pos", schema)
  expect_identical(names(none$descriptives),
                   c("group", "dimension", "n", "mean", "sd", "min", "median", "max"))
  expect_identical(c(nrow(none$descriptives), nrow(none$comparisons)), c(0L, 0L))
})

test_that("match_report takes each row's role from roles", {
  # `roles` gives the role of each row from its condition, reference and dimension.
  # Without it the role is missing. Pinned identically in test_validation.py.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  seen <- character(0)
  roles <- function(condition, reference, dimension) {
    seen <<- c(seen, paste(condition, reference, dimension))
    if (identical(dimension, "length")) "controlled" else "manipulated"
  }
  cmp <- match_report(four_conditions(), c("length", "frequency"), schema,
                      roles = roles)$comparisons
  expect_identical(cmp$role, rep(c("controlled", "manipulated"), 6))
  expect_identical(seen[1:3], c("b a length", "b a frequency", "c a length"))
  plain <- match_report(four_conditions(), "length", schema)$comparisons
  expect_true(all(is.na(plain$role)))
})

test_that("match_report_continuous gives the spreads and the windows", {
  # The predictor's SD against that of as many values spaced evenly over its range,
  # each control's SD against the pool's and the control's window, both from the
  # selector's audit. Pinned identically in test_validation.py.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  audit <- list(control_windows = list(
    list(dimension = "length", low = 2.25, high = 4.75, pool_sd = 1),
    list(dimension = "n_density", low = 0.5, high = 2.5, pool_sd = 2),
    list(dimension = "old20", low = 1.4, high = 1.7, pool_sd = 0.1)))
  rep <- match_report_continuous(cont_stim(), "frequency",
                                 c("length", "n_density", "old20"), schema, audit = audit)
  c <- rep$comparisons
  expect_identical(names(c), c("dimension", "role", "pearson_r", "predictor_span", "sd",
                               "sd_ratio", "window_low", "window_high"))
  # frequency 2, 3, 4, 5 is itself an even spread, so its SD of 1.291 gives a ratio of
  # 1. Set against 3 / sqrt(12) = 0.866, the limit for many values, it read 1.491.
  expect_identical(c$sd[1], 1.291)
  expect_identical(c$sd_ratio[1], 1)
  expect_true(is.na(c$window_low[1]))
  # length 3, 4, 3, 4: SD 0.577 against the pool's 1.
  expect_identical(c$sd[2], 0.577)
  expect_identical(c$sd_ratio[2], 0.577)
  expect_identical(c(c$window_low[2], c$window_high[2]), c(2.25, 4.75))
  expect_identical(c$sd_ratio[3], 0.289)
  expect_identical(c$sd_ratio[4], 0.577)
})

test_that("match_report_continuous reads the windows off the selection", {
  # Without an explicit audit the report reads the one the selector attached, and
  # without either a control's ratio and window are missing. Pinned identically in
  # test_validation.py.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- cont_stim()
  attr(stim, "audit") <- list(control_windows = list(
    list(dimension = "length", low = 2, high = 5, pool_sd = 2)))
  c <- match_report_continuous(stim, "frequency", "length", schema)$comparisons
  expect_identical(c$sd_ratio[2], 0.289)
  expect_identical(c$window_high[2], 5)
  bare <- match_report_continuous(cont_stim(), "frequency", "length", schema)$comparisons
  expect_true(is.na(bare$sd_ratio[2]))
  expect_true(is.na(bare$window_low[2]))
  # The predictor's ratio needs only the selection itself.
  expect_identical(bare$sd_ratio[1], 1)
})

test_that("the predictor sd_ratio is 1 for an even spread of any size", {
  # The benchmark is the SD of as many values spaced evenly over the realised range,
  # (max - min) * sqrt(n (n + 1) / 12) / (n - 1), with the n - 1 that `sd` uses. Set
  # against (max - min) / sqrt(12), its limit for many values, an even spread of 8
  # items read 1.21 and one of 4 items 1.49, as if the items crowded the ends of the
  # range. Pinned identically in test_validation.py.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  ratio <- function(values) {
    stim <- data.frame(condition = "continuous", frequency = values,
                       length = rep(4, length(values)), stringsAsFactors = FALSE)
    match_report_continuous(stim, "frequency", "length", schema)$comparisons$sd_ratio[1]
  }
  for (n in c(2L, 3L, 8L, 80L)) {
    expect_identical(ratio(3 + 0.5 * (seq_len(n) - 1)), 1, info = n)
  }
  # Bunched in the middle of the range: SD 0.713 against 0.791.
  expect_identical(ratio(c(1, 2, 2.1, 2.2, 3)), 0.902)
  # Gathered at the two ends: SD 1.643 against 1.122.
  expect_identical(ratio(c(1, 1, 1, 4, 4, 4)), 1.464)
})

test_that("variance_ratio flags unequal spread", {
  expect_equal(variance_ratio(c(1, 2, 3, 4), c(1, 2, 3, 4)), 1)       # equal spread
  expect_gt(variance_ratio(c(0, 5, 10, 15), c(4, 5, 6, 7)), 1)        # condition wider
  expect_lt(variance_ratio(c(4, 5, 6, 7), c(0, 5, 10, 15)), 1)        # condition narrower
  expect_true(is.na(variance_ratio(c(1, 2, 3), c(5, 5, 5))))          # constant reference
  expect_equal(variance_ratio(c(5, 5, 5), c(2, 2, 2)), 1)             # both constant
})

test_that("match_report_continuous returns predictor and control rows", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  rep <- match_report_continuous(cont_stim(), "frequency", c("length", "n_density", "old20"),
                                 schema)
  expect_true(all(c("descriptives", "comparisons") %in% names(rep)))
  cmp <- rep$comparisons
  expect_identical(names(cmp), c("dimension", "role", "pearson_r", "predictor_span", "sd",
                                 "sd_ratio", "window_low", "window_high"))
  expect_identical(cmp$role, c("predictor", "control", "control", "control"))
  expect_equal(cmp$predictor_span[1], 3)
})

test_that("describe_stimuli summarises per group", {
  df <- data.frame(condition = c("a", "a", "b", "b"), x = c(1, 2, 3, 4), stringsAsFactors = FALSE)
  d <- describe_stimuli(df, "x")
  expect_true(all(c("group", "dimension", "n", "mean", "sd") %in% names(d)))
  expect_equal(nrow(d), 2)
})

test_that("describe_stimuli groups in order of first appearance", {
  # Not locale-collated order: this is the order validation.py's groupby(sort = FALSE)
  # yields, and the order in which match_report() takes its anchor from unique().
  df <- data.frame(condition = c("b", "b", "a", "a"), x = c(1, 2, 3, 4), stringsAsFactors = FALSE)
  expect_identical(describe_stimuli(df, "x")$group, c("b", "a"))
})

test_that("describe_stimuli reports an all-NA dimension as missing, not infinite", {
  df <- data.frame(condition = c("a", "a"), x = c(NA_real_, NA_real_))
  d <- describe_stimuli(df, "x")
  expect_identical(d$n, 0L)
  expect_true(is.na(d$min))
  expect_true(is.na(d$max))
  expect_false(is.infinite(d$min))
  expect_false(is.infinite(d$max))
})

test_that("balance_check detects imbalance", {
  balanced <- data.frame(condition = c("a", "a", "b", "b"))
  unbalanced <- data.frame(condition = c("a", "a", "a", "b"))
  expect_length(balance_check(balanced, "condition"), 0)
  expect_length(balance_check(unbalanced, "condition"), 1)
})
