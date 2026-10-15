# Balance-aware list assignment (`counterbalance.optimise`).
#
# The factorial recipe deals item sets to lists by rank, which balances nothing: any
# dimension that varies smoothly across set ids is dealt out unevenly, and where each
# list goes to a different group of participants that unevenness is confounded with the
# group. balance_lists() searches for an assignment whose lists are equated instead.
#
# Two properties have to hold, and each is pinned here.
#
# The search must be identical in the two engines, so the objective is all-integer.
# Cohen's d was measured to differ between R and Python by around 3e-16, which at nine
# decimal places leaves roughly a one-in-three chance over a full run of a candidate
# comparison resolving differently -- and the failure would be silent and total,
# different words rather than different last bits. The assignment asserted below is
# pinned character for character against test_balance.py.
#
# It must be off by default. Switching it on changes which items a participant sees, so
# a design that does not ask for it has to be unaffected.
#
# python_workflow/tests/test_balance.py asserts the same properties.

bal_schema <- list(seed = 2026)

# Sets whose properties vary smoothly with set id, which is the case the rank deal
# handles worst: it hands every Nth set to the same list.
bal_mk <- function(n_sets = 16L) {
  s <- rep(seq_len(n_sets), each = 2L)
  data.frame(
    word = sprintf("w%03d%s", s, rep(c("a", "b"), n_sets)),
    set = s,
    condition = rep(c("hi", "lo"), n_sets),
    frequency = 2.0 + 0.31 * s,
    length = 12L - (s %% 7L),
    old20 = 1.0 + 0.07 * ((s * 5L) %% 11L),
    stringsAsFactors = FALSE
  )
}

bal_design <- function() {
  list(name = "b", language = "english",
       match_on = list("frequency", "length", "old20"),
       counterbalance = list(lists = 4L, optimise = TRUE))
}

bal_spread <- function(stim, assign, dim) {
  t <- tapply(stim[[dim]], assign, sum)
  max(t) - min(t)
}

test_that("the assignment is pinned across engines", {
  res <- balance_lists(bal_mk(), bal_design(), bal_schema)
  expect_identical(unname(res$list_of_set),
                   c(1L, 2L, 3L, 4L, 3L, 2L, 1L, 4L, 4L, 3L, 2L, 4L, 1L, 2L, 3L, 1L))
  expect_equal(res$report$cost_before, 88128)
  expect_equal(res$report$cost_after, 33440)
  expect_identical(res$report$n_swaps, 3L)
  expect_false(res$report$max_passes_reached)
  # Whole numbers, not fractions: a float cost is what would let the engines diverge.
  expect_identical(res$report$cost_before, trunc(res$report$cost_before))
  expect_identical(res$report$cost_after, trunc(res$report$cost_after))
})

test_that("every balanced dimension improves on the rank deal", {
  stim <- bal_mk()
  res <- balance_lists(stim, bal_design(), bal_schema)
  sets <- sort(unique(stim$set))
  before <- ((match(stim$set, sets) - 1L) %% 4L) + 1L
  after <- as.integer(res$list_of_set[as.character(stim$set)])
  for (dim in c("frequency", "length", "old20")) {
    expect_lt(bal_spread(stim, after, dim), bal_spread(stim, before, dim))
  }
})

test_that("the search is repeatable and preserves list sizes", {
  a <- balance_lists(bal_mk(), bal_design(), bal_schema)$list_of_set
  b <- balance_lists(bal_mk(), bal_design(), bal_schema)$list_of_set
  expect_identical(a, b)
  # A swap exchanges one set for another, so the rank deal's sizes are invariant.
  expect_identical(sort(as.integer(table(a))), c(4L, 4L, 4L, 4L))
})

test_that("the cost never increases", {
  res <- balance_lists(bal_mk(), bal_design(), bal_schema)
  expect_lte(res$report$cost_after, res$report$cost_before)
})

test_that("optimise is refused where it does not apply", {
  # A Latin square already puts every item in every list, so there is nothing to
  # balance; saying so beats silently doing nothing.
  expect_error(balance_lists(bal_mk(), list(paradigm = "priming",
                                            match_on = list("frequency"),
                                            counterbalance = list(lists = 2L)),
                             bal_schema), "Latin-square")
  expect_error(balance_lists(bal_mk(), list(match_on = list("frequency"),
                                            counterbalance = list(lists = 1L)),
                             bal_schema), "2 or more")
  expect_error(balance_lists(bal_mk(), list(counterbalance = list(lists = 2L)),
                             bal_schema), "no dimensions to balance")
  expect_error(balance_lists(bal_mk(), list(match_on = list("nope"),
                                            counterbalance = list(lists = 2L)),
                             bal_schema), "do not have: 'nope'")
})

test_that("a missing dimension value is refused", {
  # Treating a missing value as zero would bias the objective silently.
  bad <- bal_mk(); bad$frequency[3] <- NA
  expect_error(balance_lists(bad, bal_design(), bal_schema), "missing values")
})

test_that("balance_on defaults to match_on", {
  explicit <- bal_design()
  explicit$counterbalance$balance_on <- list("frequency", "length", "old20")
  expect_identical(balance_lists(bal_mk(), explicit, bal_schema)$list_of_set,
                   balance_lists(bal_mk(), bal_design(), bal_schema)$list_of_set)
})

test_that("counterbalance uses the supplied assignment", {
  stim <- bal_mk()
  res <- balance_lists(stim, bal_design(), bal_schema)
  out <- counterbalance(stim, bal_design(), bal_schema, res$list_of_set)
  expect_identical(out$list, as.integer(res$list_of_set[as.character(out$set)]))
})

test_that("an assignment that misses a set is an error", {
  # Silently defaulting the uncovered sets to list 1 would unbalance the very thing
  # the caller asked to balance.
  stim <- bal_mk()
  sets <- sort(unique(stim$set))
  partial <- stats::setNames(rep(1L, length(sets) - 1L),
                             as.character(sets[-length(sets)]))
  expect_error(lexsync:::counterbalance_factorial(stim, bal_design(), bal_schema, partial),
               "does not cover set")
})

test_that("a design without optimise is dealt by rank", {
  # The default must be untouched: enabling the optimiser changes which items a
  # participant sees, so it cannot happen to a design on upgrade.
  stim <- bal_mk()
  plain <- list(name = "b", language = "english", match_on = list("frequency"),
                counterbalance = list(lists = 4L))
  out <- counterbalance(stim, plain, bal_schema)
  sets <- sort(unique(stim$set))
  deal <- ((match(out$set, sets) - 1L) %% 4L) + 1L
  expect_identical(out$list, deal)
})

# ---- counterbalance.scale ----------------------------------------------------
#
# The mean scale divides each dimension by its mean, so a dimension's weight in the
# objective is proportional to SD / mean and depends on where its scale starts. On
# en_balanced_lists, Zipf frequency (SD / mean 0.17) counts for least, and writing it
# as Zipf - 3 moves 22 of the 40 sets to another list. The mad scale quantises each
# dimension's deviations from its mean in units of its mean absolute deviation, which
# a constant shift on the hundredths grid leaves exactly as they were.

bal_en_balanced <- function(scale = NULL) {
  d <- list(name = "en_balanced_lists", language = "english",
            match_on = list("length", "n_density", "old20"),
            counterbalance = list(lists = 4L, optimise = TRUE,
                                  balance_on = list("length", "n_density", "old20",
                                                    "frequency")))
  d$counterbalance$scale <- scale
  d
}

bal_mean_cost_unit <- paste("summed absolute deviation of each list's dimension total",
                            "from its fair share, in milli-units of the dimension's",
                            "mean, scaled by the number of item sets")

# The committed en_balanced_lists stimuli, whose `list` column the default scale dealt.
bal_en_stimuli <- function() {
  as.data.frame(read_csv_utf8(repo_path("output", "stimuli",
                                        "en_balanced_lists_english_stimuli_R.csv"),
                              as_character = "word"))
}

# Zipf - 3, a quarter added to OLD20 and two letters off every length: shifts that are
# exact on the hundredths grid.
bal_shifted <- function(stim) {
  stim$frequency <- stim$frequency - 3
  stim$old20 <- stim$old20 + 0.25
  stim$length <- stim$length - 2L
  stim
}

test_that("under mad, shifting a scale moves no set", {
  stim <- bal_en_stimuli()
  mad <- bal_en_balanced("mad")
  expect_identical(balance_lists(bal_shifted(stim), mad, bal_schema)$list_of_set,
                   balance_lists(stim, mad, bal_schema)$list_of_set)
  # The same shifts move sets under the mean scale, which is what mad is for.
  expect_false(identical(
    balance_lists(bal_shifted(stim), bal_en_balanced(), bal_schema)$list_of_set,
    balance_lists(stim, bal_en_balanced(), bal_schema)$list_of_set))
})

test_that("the engines agree on en_balanced_lists under mad", {
  # Pinned character for character in test_balance.py.
  res <- balance_lists(bal_en_stimuli(), bal_en_balanced("mad"), bal_schema)
  expect_identical(paste(res$list_of_set, collapse = ""),
                   "4434123412113234223122143432123411341324")
  expect_equal(res$report$cost_before, 435405140)
  expect_equal(res$report$cost_after, 22133820)
  expect_identical(res$report$n_swaps, 8L)
  expect_identical(res$report$scale, "mad")
  expect_identical(res$report$cost_unit,
                   paste("summed absolute deviation of each list's dimension total from",
                         "its fair share, in hundred-thousandths of the dimension's mean",
                         "absolute deviation about its mean, scaled by the number of",
                         "item sets"))
})

test_that("the default scale reproduces the shipped lists", {
  # Running studies keep their lists: the default, and `mean` named explicitly, deal
  # the committed stimuli exactly as they were dealt, and the report reads as it did.
  stim <- bal_en_stimuli()
  shipped <- tapply(stim$list, stim$set, unique)
  for (scale in list(NULL, "mean")) {
    res <- balance_lists(stim, bal_en_balanced(scale), bal_schema)
    expect_identical(unname(res$list_of_set), as.integer(unname(shipped)))
    expect_identical(names(res$list_of_set), names(shipped))
    expect_null(res$report$scale)
    expect_identical(res$report$cost_unit, bal_mean_cost_unit)
  }
})

test_that("the mad quantiser arithmetic is pinned across engines", {
  # 0.125 is a tie on the hundredths grid and rounds away from zero. The shared rounder
  # rounds the scaled double: 2.675 is stored a hair below 2.675 but scales to exactly
  # 267.5 and rounds up, and 1.005 scales to 100.49999999999999 and rounds down. The
  # hundredths sum to -59, so the integer mean is the floor, -8, where truncation would
  # give -7. Pinned identically in test_balance.py.
  vals <- c(-1.5, 0.25, -0.02, 0.125, -0.125, 2.675, 1.005, -3.0)
  expect_identical(lexsync:::.quantise_dim(vals, "x", "mad"),
                   c(-129090, 30000, 5454, 19090, -4545, 250909, 98181, -265454))
  # A dimension that does not vary contributes nothing, and its unit floors at 1.
  expect_identical(lexsync:::.quantise_dim(c(4L, 4L, 4L), "x", "mad"), c(0, 0, 0))
  expect_error(lexsync:::.quantise_dim(c(1, NA), "x", "mad"), "missing values")
  for (big in c(1e10, Inf)) {
    expect_error(lexsync:::.quantise_dim(c(1, big), "x", "mad"), "too large to balance on")
  }
})

test_that("an unknown scale is refused", {
  d <- bal_design()
  d$counterbalance$scale <- "range"
  expect_error(balance_lists(bal_mk(), d, bal_schema),
               "lexsync: unknown counterbalance.scale 'range'. Known scales: mean, mad.",
               fixed = TRUE)
})

test_that("the datasheet names the scale", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- bal_mk()
  texts <- list()
  for (scale in c("mean", "mad")) {
    design <- bal_design()
    design$counterbalance$scale <- scale
    res <- balance_lists(stim, design, bal_schema)
    ds <- build_datasheet(design, schema, NULL,
                          counterbalance(stim, design, bal_schema, res$list_of_set),
                          "x.csv", list(stimuli = NULL, experiments = list()), 2026,
                          engine = "R", balance = res$report)
    texts[[scale]] <- list(record = ds$counterbalancing$optimise,
                           methods = methods_paragraph(ds),
                           md = render_datasheet_md(ds))
  }
  mad <- texts$mad
  expect_identical(mad$record$scale, "mad")
  expect_true(grepl(paste0("by a deterministic integer search on each dimension's ",
                           "deviations from its mean, in units of its mean absolute ",
                           "deviation ("), mad$methods, fixed = TRUE))
  expect_true(grepl(paste0("- **Cost unit:** ", mad$record$cost_unit), mad$md,
                    fixed = TRUE))
  # The default's sentence and record read as they did before the option existed.
  mean <- texts$mean
  expect_null(mean$record$scale)
  expect_true(grepl("by a deterministic integer search (", mean$methods, fixed = TRUE))
  expect_true(grepl(paste0("- **Cost unit:** ", bal_mean_cost_unit), mean$md,
                    fixed = TRUE))
})
