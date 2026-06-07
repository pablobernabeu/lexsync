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
