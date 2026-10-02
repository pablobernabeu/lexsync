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

# ---- The recipe that runs, and incomplete rotations --------------------------
# Every test in this block is pinned identically in test_counterbalancing.py.

# The design block of config/design_en_priming_jitter.yaml: the priming paradigm with
# its own events, which read the prime's duration from the items and jitter the blank.
cb_jitter_events <- function() {
  list(
    list(type = "fixation", content = "+", duration_ms = 500L),
    list(type = "text", content = "{prime}", duration = list(from_column = "prime_ms"),
         trigger = 20L, onset_locked = TRUE),
    list(type = "mask", content = "#####", duration_ms = 33L),
    list(type = "text", content = "{target}", duration_ms = 800L, trigger = "condition",
         onset_locked = TRUE),
    list(type = "response", keys = c("left", "right"), timeout_ms = 2000L),
    list(type = "blank", duration = list(jitter = c(400L, 800L), as = "iti_ms"))
  )
}

# items/priming_pairs_en_soa.csv: each target with its related and unrelated prime and
# the prime's duration in milliseconds.
cb_soa_items <- function() {
  target <- c("doctor", "cat", "king", "bread", "hot", "black", "moon", "salt", "day",
              "hand", "north", "cup")
  related <- c("nurse", "dog", "queen", "butter", "cold", "white", "star", "pepper",
               "night", "foot", "south", "saucer")
  unrelated <- c("window", "table", "pencil", "planet", "paper", "river", "chair",
                 "engine", "carpet", "cloud", "lemon", "tractor")
  n <- length(target)
  data.frame(item = rep(seq_len(n), each = 2L), set = rep(seq_len(n), each = 2L),
             condition = rep(c("related", "unrelated"), n),
             prime = as.vector(rbind(related, unrelated)),
             target = rep(target, each = 2L),
             prime_ms = rep(rep(c(60L, 250L, 1200L), 4L), each = 2L),
             stringsAsFactors = FALSE)
}

# A priming table with three conditions per target, which the Latin square sorts by
# byte order: identity, related, unrelated.
cb_three_condition_items <- function(n_sets = 6L) {
  conds <- c("identity", "related", "unrelated")
  s <- rep(seq_len(n_sets), each = 3L)
  data.frame(item = s, set = s, condition = rep(conds, n_sets),
             prime = paste0(rep(substr(conds, 1L, 3L), n_sets), s),
             target = paste0("t", s), stringsAsFactors = FALSE)
}

# The message of the error an expression raises, or NA when it raises none, so a
# refusal can be compared with its full text as the Python suite compares it.
cb_error <- function(expr) {
  tryCatch({ force(expr); NA_character_ }, error = function(e) conditionMessage(e))
}

# Any `events:` list used to make counterbalance() deal the items factorially, so
# en_priming_jitter showed six targets per list, each in both conditions, while the
# datasheet and the Methods text described a Latin square. Per-trial timing can be
# declared only inside events, so every priming, categorisation or self-paced reading
# design with such timing was dealt this way.
test_that("explicit events keep the paradigm's Latin square", {
  design <- list(paradigm = "priming", events = cb_jitter_events(),
                 counterbalance = list(lists = 2L))
  expect_identical(lexsync:::.cb_recipe(design), "latin_square_target")
  out <- counterbalance(cb_soa_items(), design, list(seed = 2026L))
  expect_identical(max(table(paste(out$list, out$set))), 1L)
  expect_identical(as.vector(tapply(out$set, out$list, function(s) length(unique(s)))),
                   c(12L, 12L))
  # The other Latin-square paradigms keep theirs too, whatever their events hold.
  for (paradigm in c("categorisation", "self_paced_reading")) {
    own <- list(paradigm = paradigm, events = list(list(type = "blank", duration_ms = 250L)))
    expect_identical(lexsync:::.cb_recipe(own), "latin_square_target")
  }
  # A design that names no paradigm still counterbalances factorially.
  expect_identical(lexsync:::.cb_recipe(list(events = cb_jitter_events())), "factorial")
  # The optimiser is refused for these designs, as for every Latin square.
  optimised <- design
  optimised$counterbalance <- list(lists = 2L, optimise = TRUE)
  optimised$match_on <- list("prime_ms")
  expect_error(balance_lists(cb_soa_items(), optimised, list(seed = 2026L)),
               "does not apply to a Latin-square design", fixed = TRUE)
})

test_that("counterbalance.recipe override is validated", {
  # counterbalance.recipe wins over the paradigm's recipe, in either direction.
  expect_identical(lexsync:::.cb_recipe(list(paradigm = "priming",
                                             counterbalance = list(recipe = "factorial"))),
                   "factorial")
  expect_identical(lexsync:::.cb_recipe(list(counterbalance =
                                               list(recipe = "latin_square_target"))),
                   "latin_square_target")
  out <- counterbalance(cb_soa_items(),
                        list(paradigm = "priming",
                             counterbalance = list(recipe = "factorial", lists = 2L)),
                        list(seed = 2026L))
  expect_identical(max(table(paste(out$list, out$set))), 2L)
  expect_identical(
    cb_error(counterbalance(cb_soa_items(),
                            list(paradigm = "priming",
                                 counterbalance = list(recipe = "latin_square")),
                            list(seed = 2026L))),
    paste0("lexsync: unknown counterbalance.recipe 'latin_square'. ",
           "Known recipes: factorial, latin_square_target."))
})

test_that("an incomplete Latin square is reported", {
  # Three conditions in two lists: each item is shown in only two of its three
  # conditions, and nothing used to say so.
  design <- list(paradigm = "priming", counterbalance = list(lists = 2L))
  out <- counterbalance(cb_three_condition_items(), design, list(seed = 2026L))
  check <- lexsync:::.counterbalance_check(out, design)
  expect_false(check$complete)
  expect_identical(check$lists, 2L)
  expect_identical(check$issues,
                   "With 2 lists and 3 conditions, each item appears in only 2 of its 3 conditions.")
  cells <- list()
  for (l in 1:2) for (cnd in c("identity", "related", "unrelated")) {
    cells[[length(cells) + 1L]] <- list(list = l, condition = cnd, n_trials = 2L)
  }
  expect_identical(check$cells, cells)
  # Item sets that are not a multiple of the conditions leave the cells unequal.
  seven <- counterbalance(cb_three_condition_items(7L), design, list(seed = 2026L))
  expect_identical(
    lexsync:::.counterbalance_check(seven, design)$issues,
    c("With 2 lists and 3 conditions, each item appears in only 2 of its 3 conditions.",
      paste0("With 7 item sets and 3 conditions, the item sets are not a multiple of the ",
             "conditions, so the conditions within each list differ by one trial.")))
  # One list confounds item and condition completely, and lists that are not a
  # multiple of the conditions rotate some conditions more often than others.
  one <- counterbalance(cb_soa_items(), list(paradigm = "priming",
                                             counterbalance = list(lists = 1L)),
                        list(seed = 2026L))
  expect_identical(lexsync:::.counterbalance_check(one, list(paradigm = "priming"))$issues,
                   paste0("With one list, every participant sees each item in the same ",
                          "condition, so item and condition are fully confounded."))
  three <- counterbalance(cb_soa_items(), list(paradigm = "priming",
                                               counterbalance = list(lists = 3L)),
                          list(seed = 2026L))
  expect_identical(lexsync:::.counterbalance_check(three, list(paradigm = "priming"))$issues,
                   paste0("With 3 lists and 2 conditions, the lists are not a multiple of ",
                          "the conditions, so each item appears in some conditions in more ",
                          "lists than in others."))
  full <- counterbalance(cb_soa_items(), list(paradigm = "priming"), list(seed = 2026L))
  expect_true(lexsync:::.counterbalance_check(full, list(paradigm = "priming"))$complete)

  # counterbalance.incomplete: error refuses the run with the issue text.
  dir <- tempfile("cb-incomplete-")
  dir.create(dir)
  items <- file.path(dir, "items.csv")
  write_csv_utf8(cb_three_condition_items()[, c("item", "condition", "prime", "target")],
                 items)
  design_path <- file.path(dir, "design.yaml")
  writeLines(c("name: incomplete_test", "language: english", "paradigm: priming",
               "items:", "  source: table", paste0("  path: ", gsub("\\\\", "/", items)),
               "counterbalance:", "  lists: 2", "  incomplete: error"),
             design_path, useBytes = TRUE)
  msg <- cb_error(run_pipeline(design_path,
                               system.file("extdata", "schema.yaml", package = "lexsync"),
                               outdir = file.path(dir, "out"), verbose = FALSE))
  expect_identical(msg, paste0(
    "lexsync: the Latin-square rotation is incomplete and counterbalance.incomplete ",
    "is 'error'. With 2 lists and 3 conditions, each item appears in only 2 of its 3 ",
    "conditions. Make the lists and the item sets multiples of the number of ",
    "conditions, or set counterbalance.incomplete: allow."))
  unlink(dir, recursive = TRUE)
})

test_that("counterbalance.incomplete resolves design over schema over default", {
  strict <- list(counterbalance = list(incomplete = "error"))
  expect_identical(lexsync:::.cb_incomplete_policy(list(), list()), "allow")
  expect_identical(lexsync:::.cb_incomplete_policy(list(), strict), "error")
  expect_identical(lexsync:::.cb_incomplete_policy(
    list(counterbalance = list(incomplete = "allow")), strict), "allow")
  expect_identical(
    cb_error(lexsync:::.cb_incomplete_policy(list(counterbalance = list(incomplete = "warn")),
                                             list())),
    "lexsync: unknown counterbalance.incomplete policy 'warn'. Known policies: allow, error.")
})

test_that("a factorial design with more lists than sets is refused", {
  # The surplus lists used to come out empty, and the datasheet still recorded them.
  stim <- data.frame(word = letters[1:6], condition = rep(c("x", "y"), 3),
                     set = rep(1:3, each = 2), stringsAsFactors = FALSE)
  expect_identical(
    cb_error(counterbalance(stim, list(counterbalance = list(lists = 4L)), list(seed = 1L))),
    paste0("lexsync: counterbalance.lists is 4 but there are only 3 item sets, so list 4 ",
           "would be empty; lower lists or add items."))
  expect_identical(
    cb_error(counterbalance(stim, list(counterbalance = list(lists = 5L)), list(seed = 1L))),
    paste0("lexsync: counterbalance.lists is 5 but there are only 3 item sets, so lists 4 ",
           "to 5 would be empty; lower lists or add items."))
  # As many lists as sets is allowed, one set to each.
  out <- counterbalance(stim, list(counterbalance = list(lists = 3L)), list(seed = 1L))
  expect_identical(sort(unique(out$list)), 1:3)
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
  # same characters in UTF-8, and so from the Python engine. The key now goes
  # through enc2utf8, as hash_unit always has.
  stim <- data.frame(word = letters[1:8], list = 1L,
                     condition = rep(c("café", "naïve"), 4),
                     set = rep(1:4, each = 2), stringsAsFactors = FALSE)
  stim$condition <- enc2utf8(stim$condition)
  lat <- stim
  lat$condition <- iconv(stim$condition, "UTF-8", "latin1")
  expect_identical(unique(Encoding(lat$condition)), "latin1")
  out_utf <- lexsync:::.shuffle_deterministic(stim, 2026L)
  out_lat <- lexsync:::.shuffle_deterministic(lat, 2026L)
  expect_identical(out_lat$word, out_utf$word)
  expect_identical(out_lat$trial, out_utf$trial)
})
