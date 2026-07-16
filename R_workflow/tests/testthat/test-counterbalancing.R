test_that("participant_table crosses factors and covers all participants", {
  pt <- participant_table(list(order = c("A", "B"), lang = c("en", "es")), 8)
  expect_equal(nrow(pt), 8)
  expect_true(all(c("order", "lang", "participant") %in% names(pt)))
  expect_equal(pt$participant, 1:8)
})

test_that("participant_table varies the first factor fastest", {
  # Same expected cells are pinned in test_counterbalancing.py: the engines must
  # allocate a participant number to the same cell.
  pt <- participant_table(list(order = c("A", "B"), lang = c("en", "es")), 8)
  expect_equal(pt$order, c("A", "B", "A", "B", "A", "B", "A", "B"))
  expect_equal(pt$lang, c("en", "en", "es", "es", "en", "en", "es", "es"))
})

test_that("participant_table varies the first factor fastest with three factors", {
  pt <- participant_table(list(a = c(1, 2), b = c("x", "y"), c = c("p", "q")), 8)
  expect_equal(pt$a, c(1, 2, 1, 2, 1, 2, 1, 2))
  expect_equal(pt$b, c("x", "x", "y", "y", "x", "x", "y", "y"))
  expect_equal(pt$c, c("p", "p", "p", "p", "q", "q", "q", "q"))
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

test_that("counterbalance_factorial deals lists by set rank", {
  # Non-contiguous set numbers: the deal follows the rank of the set, not its
  # value. Same expected mapping is pinned in test_counterbalancing.py.
  stim <- data.frame(
    word = letters[1:8], condition = rep(c("x", "y"), 4),
    set = c(2, 2, 4, 4, 6, 6, 8, 8), stringsAsFactors = FALSE
  )
  out <- counterbalance(stim, list(counterbalance = list(lists = 2)), list(seed = 1))
  deal <- out$list[match(c(2, 4, 6, 8), out$set)]
  expect_equal(deal, c(1L, 2L, 1L, 2L))
})

test_that("counterbalance leaves the caller's RNG stream untouched", {
  # The keyed-hash shuffle draws no random numbers, so the caller's stream must
  # be exactly where they left it: a stronger guarantee than the save-and-restore
  # this once tested, and the reason no RNG may reappear in this path.
  stim <- data.frame(
    word = c("a", "b", "c", "d"), condition = c("x", "x", "y", "y"),
    set = c(1, 2, 1, 2), stringsAsFactors = FALSE
  )
  set.seed(99)
  before <- .Random.seed
  counterbalance(stim, list(counterbalance = list(lists = 1)), list(seed = 1))
  expect_identical(.Random.seed, before)
})

test_that("counterbalance creates no .Random.seed when the caller had none", {
  # A session that has never drawn a random number must still have none after a
  # full counterbalance: proof that the shuffle touches no random state at all.
  stim <- data.frame(
    word = c("a", "b", "c", "d"), condition = c("x", "x", "y", "y"),
    set = c(1, 2, 1, 2), stringsAsFactors = FALSE
  )
  if (exists(".Random.seed", envir = globalenv(), inherits = FALSE)) {
    rm(".Random.seed", envir = globalenv())
  }
  counterbalance(stim, list(counterbalance = list(lists = 1)), list(seed = 1))
  expect_false(exists(".Random.seed", envir = globalenv(), inherits = FALSE))
})

test_that("the keyed-hash shuffle gives both engines the same trial order", {
  # The hash of "seed|replicate|list|set|condition" decides each trial's position,
  # so the order is a pure function of the design and the two engines must produce
  # it byte for byte. test_counterbalancing.py pins these same words against these
  # same trials; a change to the key format or the digest breaks both suites.
  stim <- data.frame(word = letters[1:8], condition = rep(c("x", "y"), 4),
                     set = rep(1:4, each = 2), stringsAsFactors = FALSE)
  out <- counterbalance(stim, list(counterbalance = list(lists = 2)), list(seed = 2026))
  out <- out[order(out$list, out$trial), , drop = FALSE]
  expect_identical(out$word, c("b", "f", "e", "a", "c", "g", "h", "d"))
  # A different seed is a different permutation.
  out2 <- counterbalance(stim, list(counterbalance = list(lists = 2)), list(seed = 1))
  out2 <- out2[order(out2$list, out2$trial), , drop = FALSE]
  expect_false(identical(out$word, out2$word))
})
