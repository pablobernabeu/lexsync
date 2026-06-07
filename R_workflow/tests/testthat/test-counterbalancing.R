test_that("participant_table crosses factors and covers all participants", {
  pt <- participant_table(list(order = c("A", "B"), lang = c("en", "es")), 8)
  expect_equal(nrow(pt), 8)
  expect_true(all(c("order", "lang", "participant") %in% names(pt)))
  expect_equal(pt$participant, 1:8)
})

test_that("counterbalance adds list and trial columns", {
  stim <- data.frame(
    word = c("a", "b", "c", "d"), condition = c("x", "x", "y", "y"),
    set = c(1, 2, 1, 2), stringsAsFactors = FALSE
  )
  schema <- list(seed = 1)
  out <- counterbalance(stim, list(counterbalance = list(lists = 1)), schema)
  expect_true(all(c("list", "trial") %in% names(out)))
  expect_setequal(out$trial, 1:4)
})
