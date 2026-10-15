# Trial-order constraints and per-participant orders (counterbalance.max_run, orders).
#
# The keyed-hash order behaves as a uniform shuffle, so it gives runs of one condition
# as long as a uniform shuffle does: over seeds 1 to 1000 of a 60 + 60 lexical decision
# the longest run had a median of 7 and a maximum of 21. counterbalance.max_run repairs
# the seeded order so that no run is longer than k, and refuses only a constraint that
# no order can meet. counterbalance.orders: m writes m orders per list into the loop
# tables, and the experiments choose one by participant number. Every test here is
# pinned identically in test_trial_order.py.

to_lexdec <- function(n_words, n_pseudo) {
  data.frame(word = c(sprintf("w%03d", seq_len(n_words)), sprintf("p%03d", seq_len(n_pseudo))),
             set = c(seq_len(n_words), seq_len(n_pseudo)),
             condition = c(rep("word", n_words), rep("pseudoword", n_pseudo)),
             stringsAsFactors = FALSE)
}

to_longest_run <- function(labels) {
  if (!length(labels)) return(0L)
  max(rle(as.character(labels))$lengths)
}

to_in_order <- function(out, column = "trial") {
  out[order(out$list, out[[column]], method = "radix"), , drop = FALSE]
}

test_that("max_run holds for every seed on balanced and unbalanced lists", {
  design <- list(counterbalance = list(lists = 1L, max_run = 2L))
  for (sizes in list(c(60L, 60L), c(40L, 80L))) {
    stim <- to_lexdec(sizes[1], sizes[2])
    for (seed in 1:50) {
      out <- to_in_order(counterbalance(stim, design, list(seed = seed)))
      expect_lte(to_longest_run(out$condition), 2L)
      expect_identical(sort(out$word), sort(stim$word))
      expect_identical(out$trial, seq_len(nrow(stim)))
    }
  }
})

test_that("the unconstrained order has long runs and the repair changes only what it must", {
  stim <- to_lexdec(60L, 60L)
  plain <- to_in_order(counterbalance(stim, list(counterbalance = list(lists = 1L)),
                                      list(seed = 7L)))
  expect_gt(to_longest_run(plain$condition), 2L)
  loose <- to_in_order(counterbalance(
    stim, list(counterbalance = list(lists = 1L, max_run = 120L)), list(seed = 7L)))
  expect_identical(loose$word, plain$word)
  tight <- to_in_order(counterbalance(
    stim, list(counterbalance = list(lists = 1L, max_run = 2L)), list(seed = 7L)))
  labels <- plain$condition
  first_break <- which(vapply(3:length(labels), function(i)
    labels[i] == labels[i - 1L] && labels[i] == labels[i - 2L], logical(1)))[1] + 2L
  keep <- seq_len(first_break - 1L)
  expect_identical(tight$word[keep], plain$word[keep])
})

test_that("an impossible run limit is refused with one message", {
  expect_error(
    counterbalance(to_lexdec(40L, 80L), list(counterbalance = list(lists = 1L, max_run = 1L)),
                   list(seed = 1L)),
    paste0("lexsync: no order of list 1 keeps runs of 'condition' to 1 or fewer: 80 ",
           "'pseudoword' trials against 40 others."), fixed = TRUE)
  expect_error(
    counterbalance(to_lexdec(40L, 90L), list(counterbalance = list(lists = 1L, max_run = 2L)),
                   list(seed = 1L)),
    paste0("lexsync: no order of list 1 keeps runs of 'condition' to 2 or fewer: 90 ",
           "'pseudoword' trials against 40 others."), fixed = TRUE)
})

test_that("run_on names a column and a missing value is a category of its own", {
  stim <- to_lexdec(6L, 6L)
  stim$answer <- c(rep("f", 6), rep(NA, 6))
  out <- to_in_order(counterbalance(
    stim, list(counterbalance = list(lists = 1L, max_run = 1L, run_on = "answer")),
    list(seed = 3L)))
  shown <- ifelse(is.na(out$answer), "", out$answer)
  expect_identical(to_longest_run(shown), 1L)
  expect_error(
    counterbalance(stim, list(counterbalance = list(lists = 1L, max_run = 1L,
                                                    run_on = "animacy")), list(seed = 3L)),
    "lexsync: counterbalance.run_on names 'animacy', a column that list 1 does not have.",
    fixed = TRUE)
  stim$answer <- c(rep(NA, 9), rep("f", 3))
  expect_error(
    counterbalance(stim, list(counterbalance = list(lists = 1L, max_run = 2L,
                                                    run_on = "answer")), list(seed = 3L)),
    paste0("lexsync: no order of list 1 keeps runs of 'answer' to 2 or fewer: 9 trials ",
           "with no 'answer' against 3 others."), fixed = TRUE)
})

test_that("the run limit applies within each list of a Latin square", {
  rows <- expand.grid(condition = c("related", "unrelated"), set = 1:12,
                      stringsAsFactors = FALSE)
  rows$target <- paste0("t", rows$set)
  design <- list(paradigm = "priming", counterbalance = list(lists = 2L, max_run = 1L))
  for (seed in 1:10) {
    out <- to_in_order(counterbalance(rows, design, list(seed = seed)))
    for (l in 1:2) expect_identical(to_longest_run(out$condition[out$list == l]), 1L)
  }
})

test_that("the trial order keys are validated", {
  base <- list(name = "t", language = "english")
  cases <- list(
    list(list(max_run = 0L), "lexsync: counterbalance.max_run must be a whole number of at least 1."),
    list(list(max_run = 1.5), "lexsync: counterbalance.max_run must be a whole number of at least 1."),
    list(list(max_run = "2"), "lexsync: counterbalance.max_run must be a whole number of at least 1."),
    list(list(max_run = TRUE), "lexsync: counterbalance.max_run must be a whole number of at least 1."),
    list(list(orders = 0L), "lexsync: counterbalance.orders must be a whole number of at least 1."),
    list(list(run_on = 3L), "lexsync: counterbalance.run_on must name a column of the trials."),
    list(list(run_on = " "), "lexsync: counterbalance.run_on must name a column of the trials."))
  for (case in cases) {
    expect_error(validate_design(c(base, list(counterbalance = case[[1]])), list()),
                 case[[2]], fixed = TRUE)
  }
  expect_identical(validate_design(c(base, list(counterbalance = list(
    max_run = 2.0, orders = 3L, run_on = "answer"))), list()), character(0))
})

test_that("orders give distinct orders that each keep the run limit", {
  stim <- to_lexdec(30L, 30L)
  design <- list(counterbalance = list(lists = 1L, orders = 3L, max_run = 2L))
  out <- counterbalance(stim, design, list(seed = 11L))
  expect_identical(grep("^order_", names(out), value = TRUE),
                   c("order_1", "order_2", "order_3"))
  expect_identical(out$order_1, out$trial)
  sequences <- character(0)
  for (j in 1:3) {
    ordered <- out[order(out[[paste0("order_", j)]]), , drop = FALSE]
    expect_identical(sort(ordered[[paste0("order_", j)]]), 1:60)
    expect_lte(to_longest_run(ordered$condition), 2L)
    sequences <- c(sequences, paste(ordered$word, collapse = " "))
  }
  expect_length(unique(sequences), 3L)
  plain <- counterbalance(stim, list(counterbalance = list(lists = 1L, max_run = 2L)),
                          list(seed = 11L))
  expect_identical(plain$word, out$word)
  expect_false("order_1" %in% names(plain))
})

test_that("the order keys give both engines the same orders", {
  # Order j > 1 ranks each trial by the SHA-256 of "seed|order<j>|replicate|list|set|
  # condition". test_trial_order.py pins these same words.
  stim <- data.frame(word = letters[1:8], condition = rep(c("x", "y"), 4),
                     set = c(1, 1, 2, 2, 3, 3, 4, 4), stringsAsFactors = FALSE)
  out <- counterbalance(stim, list(counterbalance = list(lists = 2L, orders = 3L)),
                        list(seed = 2026L))
  expect_identical(to_in_order(out, "order_1")$word, c("b", "f", "e", "a", "c", "g", "h", "d"))
  expect_identical(to_in_order(out, "order_2")$word, c("f", "a", "e", "b", "c", "h", "d", "g"))
  expect_identical(to_in_order(out, "order_3")$word, c("f", "b", "e", "a", "d", "c", "h", "g"))
})

test_that("practice and fillers follow every order", {
  dir <- tempfile("lexsync_order_"); dir.create(dir)
  practice <- file.path(dir, "practice.csv")
  utils::write.csv(data.frame(item = 1:6, condition = rep(c("word", "pseudoword"), 3),
                              target = c("pa", "pb", "pc", "pd", "pe", "pf")),
                   practice, row.names = FALSE)
  fillers <- file.path(dir, "fillers.csv")
  utils::write.csv(data.frame(item = 1:20, condition = rep("pseudoword", 20),
                              target = sprintf("f%02d", 1:20)), fillers, row.names = FALSE)
  design <- list(name = "t", language = "english", paradigm = "lexical_decision",
                 practice = list(path = practice), fillers = list(path = fillers),
                 counterbalance = list(lists = 1L, orders = 2L, max_run = 2L))
  stim <- to_lexdec(20L, 0L)
  names(stim)[names(stim) == "word"] <- "target"
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  out <- .add_blocks(counterbalance(stim, design, schema), design, schema)$presented
  for (j in 1:2) {
    ordered <- out[order(out[[paste0("order_", j)]]), , drop = FALSE]
    expect_identical(ordered$block[1:6], rep("practice", 6))
    body <- ordered[ordered$block != "practice", , drop = FALSE]
    expect_lte(to_longest_run(body$condition), 2L)
    expect_lte(to_longest_run(ordered$condition[1:6]), 2L)
  }
  expect_identical(out$order_1, out$trial)
  tab <- loop_table(out, list(list(type = "text", content = "{target}", duration_ms = 500L)))
  expect_identical(names(tab)[1:8], c("trial", "list", "block", "set", "condition",
                                      "order_1", "order_2", "target"))
})

test_that("the counterbalancing record states the limit and the orders", {
  dir <- tempfile("lexsync_order_"); dir.create(dir)
  rows <- expand.grid(condition = c("related", "unrelated"), item = 1:12,
                      stringsAsFactors = FALSE)[, c("item", "condition")]
  rows$prime <- paste0(substr(rows$condition, 1, 3), rows$item)
  rows$target <- paste0("t", rows$item)
  items <- file.path(dir, "items.csv")
  utils::write.csv(rows, items, row.names = FALSE)
  design_path <- file.path(dir, "design.yaml")
  yaml::write_yaml(list(name = "order_record", language = "english", paradigm = "priming",
                        items = list(source = "table", path = items),
                        counterbalance = list(lists = 2L, max_run = 2L, orders = 3L)),
                   design_path)
  out <- file.path(dir, "out")
  run_pipeline(design_path, system.file("extdata", "schema.yaml", package = "lexsync"),
               outdir = out, verbose = FALSE)
  ds <- jsonlite::read_json(file.path(out, "reports", "order_record_english_datasheet_R.json"))
  rec <- ds$counterbalancing
  expect_identical(rec$max_run$k, 2L)
  expect_identical(rec$max_run$run_on, "condition")
  expect_identical(vapply(rec$max_run$longest, function(r) r$list, integer(1)), 1:2)
  expect_true(all(vapply(rec$max_run$longest, function(r) r$longest_run, integer(1)) %in% 1:2))
  expect_identical(rec$orders, list(
    m = 3L, rule = paste("order = (((participant - 1) div 2) mod 3) + 1; a run without a",
                         "participant number presents order 1")))
  md <- paste(readLines(file.path(out, "reports", "order_record_english_datasheet_R.md"),
                        encoding = "UTF-8"), collapse = "\n")
  expect_true(grepl(paste("Each list was presented in 3 trial orders, assigned in rotation by",
                          "participant number. Runs of consecutive trials with the same",
                          "condition were limited to 2 (van Casteren & Davis, 2006)."),
                    md, fixed = TRUE))
  expect_true(grepl("- **Trial orders:** 3 per list", md, fixed = TRUE))
})

test_that("the settings resolve to the defaults when the design gives none", {
  expect_identical(.trial_order_settings(list()),
                   list(max_run = NULL, run_on = "condition", orders = 1L))
  expect_identical(.trial_order_settings(list(counterbalance = list(max_run = 3L, orders = 2.0))),
                   list(max_run = 3L, run_on = "condition", orders = 2L))
})
