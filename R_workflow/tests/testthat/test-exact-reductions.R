# The reproducible reductions.
#
# These exist because the package's byte-identity claim was failing in a way nothing
# caught. Two designs' reported means differed between the engines in the last decimal
# the descriptives publish -- 1.448 against 1.447 -- because R's mean() uses a two-pass
# long-double algorithm while numpy sums pairwise, and the true value sat on a rounding
# boundary. Every reduction in validation.R now goes through these instead.
#
# The algorithm is Neumaier compensated summation, written out in plain double
# arithmetic in both engines: every operation is +, -, abs or a comparison, and IEEE-754
# requires + and - to be correctly rounded, so the two engines cannot disagree. That is
# an argument rather than a measurement, which is what relying on R's long-double
# accumulator amounted to.
#
# python_workflow/tests/test_exact_reductions.py asserts the same properties, and
# test_byte_parity.py checks the end result on the real artefacts.

test_that("the sum is exact where a naive loop is not", {
  # The classic compensated-summation case: a large value followed by many small ones
  # that a naive accumulator loses entirely.
  xs <- c(1e16, rep(1, 100))
  naive <- 0
  for (v in xs) naive <- naive + v
  expect_identical(naive, 1e16)                          # every 1 was swallowed
  expect_identical(lexsync:::.exact_sum(xs), 1e16 + 100) # compensation recovers them
})

test_that("the sum handles catastrophic cancellation", {
  expect_identical(lexsync:::.exact_sum(c(1e-20, 1e20, -1e20, 1e-20)), 2e-20)
  expect_identical(lexsync:::.exact_sum(c(1e100, 1, -1e100)), 1)
})

test_that("order does not change the sum for these cases", {
  # Not a general guarantee -- compensated summation is not order-independent in
  # principle -- but the engines iterate a column in the same order, and this pins that
  # the algorithm is stable for realistic data rather than luckily so.
  xs <- c(3.7, 1.2, 9.9, 0.001, 5.5, 2.25, 8.125)
  expect_identical(lexsync:::.exact_sum(xs), lexsync:::.exact_sum(rev(xs)))
})

test_that("mean and variance on a known case", {
  xs <- c(2, 4, 4, 4, 5, 5, 7, 9)
  expect_identical(lexsync:::.exact_mean(xs), 5)
  expect_equal(lexsync:::.exact_var(xs), 4.571428571428571, tolerance = 0)
  expect_identical(lexsync:::.exact_sd(xs), sqrt(lexsync:::.exact_var(xs)))
})

test_that("degenerate inputs are not silently zero", {
  expect_true(is.na(lexsync:::.exact_mean(numeric(0))))
  # A variance needs two values; returning 0 would claim a spread of nothing.
  expect_true(is.na(lexsync:::.exact_var(1)))
  expect_identical(lexsync:::.exact_var(c(2, 2)), 0)
  expect_identical(lexsync:::.exact_sd(c(2, 2)), 0)
})

test_that("variance survives data far from zero", {
  # The one-pass "sum of squares minus n times squared mean" form cancels
  # catastrophically here and can even return a negative variance; the two-pass form
  # gives the right answer.
  xs <- 1e9 + c(4, 7, 13, 16)
  expect_equal(lexsync:::.exact_var(xs), 30, tolerance = 1e-9)
  expect_gte(lexsync:::.exact_var(xs), 0)
})

test_that("the reductions agree with R's own on well-conditioned data", {
  # Where the built-ins are reliable the replacements must not have changed the answer;
  # the point of the change is the boundary cases, not a different definition.
  set_free <- c(3.65, 5.4, 4.2, 5.3, 2.96, 4.07, 3.715, 6.1)
  expect_equal(lexsync:::.exact_mean(set_free), mean(set_free), tolerance = 1e-15)
  expect_equal(lexsync:::.exact_var(set_free), stats::var(set_free), tolerance = 1e-15)
  expect_equal(lexsync:::.exact_sd(set_free), stats::sd(set_free), tolerance = 1e-15)
})


test_that("the shared decimal rounder is pinned", {
  # No pairing of built-ins agrees. Measured over 210,000 values including every 3-dp
  # halfway case in range: R's round() disagrees with Python's builtin round(), Python's
  # builtin disagrees with numpy's, and even R's sprintf("%.3f") disagrees with Python's
  # "%.3f" on 274 of them. So the rounder is defined by its arithmetic instead, and both
  # engines compute the same double by construction. test_exact_reductions.py asserts
  # these same values.
  expect_identical(lexsync:::.round_dp(7.8125, 3), 7.813)   # half AWAY from zero
  expect_identical(lexsync:::.round_dp(-7.8125, 3), -7.813) # and away for negatives
  expect_identical(lexsync:::.round_dp(2.5, 0), 3)
  expect_identical(lexsync:::.round_dp(-2.5, 0), -3)
  expect_identical(lexsync:::.round_dp(1.0005, 3), 1.001)
  expect_identical(lexsync:::.round_dp(4.2505, 3), 4.251)
  expect_identical(lexsync:::.round_dp(0, 3), 0)
  # R's own round() would give the half-to-even answer on the first of these, which is
  # exactly the divergence this replaces.
  expect_false(identical(round(7.8125, 3), lexsync:::.round_dp(7.8125, 3)))
  # Vectorised, and non-finite values pass through rather than becoming nonsense.
  expect_identical(lexsync:::.round_dp(c(1.0005, 2.0005), 3), c(1.001, 2.001))
  expect_true(is.na(lexsync:::.round_dp(NA_real_, 3)))
  expect_identical(lexsync:::.round_dp(Inf, 3), Inf)
})
