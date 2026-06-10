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

test_that("cohens_d_ci brackets the point estimate and matches cohens_d", {
  x <- rep(c(5, 6, 7, 8), 10); y <- rep(c(1, 2, 3, 4), 10)
  ci <- cohens_d_ci(x, y)
  expect_lte(ci$ci_low, ci$d)
  expect_lte(ci$d, ci$ci_high)
  expect_equal(ci$d, cohens_d(x, y), tolerance = 1e-9)
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

test_that("describe_stimuli summarises per group", {
  df <- data.frame(condition = c("a", "a", "b", "b"), x = c(1, 2, 3, 4), stringsAsFactors = FALSE)
  d <- describe_stimuli(df, "x")
  expect_true(all(c("group", "dimension", "n", "mean", "sd") %in% names(d)))
  expect_equal(nrow(d), 2)
})

test_that("balance_check detects imbalance", {
  balanced <- data.frame(condition = c("a", "a", "b", "b"))
  unbalanced <- data.frame(condition = c("a", "a", "a", "b"))
  expect_length(balance_check(balanced, "condition"), 0)
  expect_length(balance_check(unbalanced, "condition"), 1)
})
