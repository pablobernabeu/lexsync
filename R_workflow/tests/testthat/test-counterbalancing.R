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

# The recipe used to fall back to factorial whenever a design declared its own
# events, before the paradigm was consulted. config/design_en_priming_jitter.yaml
# names priming and adjusts two durations, and every list held each target twice,
# once related and once unrelated, which is the repetition the Latin square exists
# to prevent. The same expectations are pinned in test_counterbalancing.py.
test_that("the paradigm decides the recipe even when the design declares events", {
  events <- list(list(type = "text", content = "{target}", duration_ms = 800L))
  expect_identical(lexsync:::.cb_recipe(list(paradigm = "priming", events = events)),
                   "latin_square_target")
  expect_identical(lexsync:::.cb_recipe(list(paradigm = "priming")), "latin_square_target")
  expect_identical(lexsync:::.cb_recipe(list(paradigm = "lexical_decision", events = events)),
                   "factorial")
  expect_identical(lexsync:::.cb_recipe(list(events = events)), "factorial")
  stim <- data.frame(prime = c("a", "b", "c", "d"), target = c("x", "x", "y", "y"),
                     condition = c("r", "u", "r", "u"), set = c(1, 1, 2, 2),
                     stringsAsFactors = FALSE)
  out <- counterbalance(stim, list(paradigm = "priming", events = events,
                                   counterbalance = list(lists = 2)), list(seed = 1))
  expect_false(any(duplicated(out[, c("list", "target")])))
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

test_that("the shuffle key hashes UTF-8 bytes whatever encoding the frame carries", {
  # digest(serialize = FALSE) hashes the stored bytes, so a latin1-marked
  # condition read from a user's CSV used to rank by different digests from the
  # same characters in UTF-8, and so from the Python engine. Wrapping the pasted
  # key in enc2utf8 did not close the gap: paste() had already translated a
  # latin1 component into the native encoding, which in a C locale is the escape
  # text "caf<e9>", and an unmarked string was escaped to "caf<c3><a9>" the same
  # way. Every character component is now normalised before it is pasted, so all
  # three markings rank by the digest Python computes, and the order is pinned to
  # the Python engine's rather than to another R run.
  python_order <- c("c", "e", "a", "f", "b", "h", "g", "d")
  stim <- data.frame(word = letters[1:8], list = 1L,
                     condition = rep(c("caf\u00e9", "na\u00efve"), 4),
                     set = rep(1:4, each = 2), stringsAsFactors = FALSE)
  stim$condition <- enc2utf8(stim$condition)
  lat <- stim
  lat$condition <- iconv(stim$condition, "UTF-8", "latin1")
  expect_identical(unique(Encoding(lat$condition)), "latin1")
  unk <- stim
  Encoding(unk$condition) <- "unknown"
  expect_identical(unique(Encoding(unk$condition)), "unknown")
  check <- function() {
    for (frame in list(stim, lat, unk)) {
      out <- lexsync:::.shuffle_deterministic(frame, 2026L)
      expect_identical(out$word, python_order)
      expect_identical(out$trial, 1:8)
    }
  }
  check()
  # The C locale is where the translations bit, so a UTF-8 runner switches to it too.
  old <- Sys.getlocale("LC_CTYPE")
  skip_if(!isTRUE(suppressWarnings(Sys.setlocale("LC_CTYPE", "C")) == "C"),
          "cannot switch to the C locale on this platform")
  on.exit(Sys.setlocale("LC_CTYPE", old), add = TRUE)
  check()
})

test_that("more lists than item sets is refused", {
  # Dealing sets round-robin used to leave the surplus lists empty and silent, while
  # the datasheet went on reporting the number of lists the design asked for. The
  # same refusal is pinned in test_counterbalancing.py.
  stim <- data.frame(word = letters[1:6], condition = rep(c("x", "y"), 3),
                     set = rep(1:3, each = 2), stringsAsFactors = FALSE)
  expect_error(counterbalance(stim, list(counterbalance = list(lists = 8)), list(seed = 1)),
               "only 3 item set")
  out <- counterbalance(stim, list(counterbalance = list(lists = 3L)), list(seed = 1))
  expect_identical(sort(unique(out$list)), 1:3)
})

test_that("more lists than conditions is refused by the Latin square", {
  # The rotation repeats after as many lists as there are conditions, so a fourth
  # list over two conditions would duplicate the first. Pinned in the Python suite too.
  stim <- data.frame(prime = letters[1:4], target = c("x", "x", "y", "y"),
                     condition = c("r", "u", "r", "u"), set = c(1, 1, 2, 2),
                     stringsAsFactors = FALSE)
  design <- list(paradigm = "priming", counterbalance = list(lists = 4))
  expect_error(counterbalance(stim, design, list(seed = 1)), "only 2 condition")
  design$counterbalance$lists <- 2L
  out <- counterbalance(stim, design, list(seed = 1))
  expect_identical(sort(unique(out$list)), 1:2)
})
