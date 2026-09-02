extdata <- function(f) system.file("extdata", f, package = "lexsync")

# Everything is written under tempdir(), so R CMD check leaves no artefacts and
# the committed output/ tree that the parity suite compares against is untouched.
tmp_out <- function() {
  d <- tempfile("lexsync-")
  dir.create(d, recursive = TRUE, showWarnings = FALSE)
  d
}

# One quiet call, so the suite is not narrated. run_pipeline() restores the
# verbosity option itself, so nothing has to be put back here.
run_quiet <- function(...) run_pipeline(..., verbose = FALSE)

write_design <- function(dir, text) {
  p <- file.path(dir, "design.yaml")
  writeLines(text, p, useBytes = TRUE)
  p
}

as_yaml_path <- function(p) gsub("\\\\", "/", p)

test_that("run_pipeline exports every artefact for a corpus design", {
  # Mirrors test_cli.py::test_run_one_design, but asserts on the whole artefact
  # set: nothing else in R CMD check executes the orchestrator.
  out <- tmp_out()
  design <- write_design(out, c(
    "name: cli_test",
    "language: english",
    paste0("lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "n_per_condition: 5",
    "pool_filters: {length: [3, 7], frequency: [3.8, 7]}",
    "conditions:",
    "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
    "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
    "match_on: [length]"
  ))

  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)

  for (f in c(file.path("stimuli", "cli_test_english_stimuli_R.csv"),
              file.path("reports", "cli_test_english_descriptives_R.csv"),
              file.path("reports", "cli_test_english_comparisons_R.csv"),
              file.path("reports", "cli_test_english_datasheet_R.json"),
              file.path("reports", "cli_test_english_datasheet_R.md"),
              file.path("reports", "cli_test_english_run_log_R.md"))) {
    expect_true(file.exists(file.path(out, f)), info = f)
  }
  expect_named(res, c("stimuli", "descriptives", "comparisons", "experiments", "log"))

  stim <- read_csv_utf8(res$stimuli)
  expect_equal(as.integer(table(stim$condition)), c(5L, 5L))
  expect_equal(sort(unique(stim$set)), 1:5)
  expect_true(all(c("word", "condition", "set", "trial") %in% names(stim)))
})

test_that("run_pipeline generates pseudowords for a generate design", {
  out <- tmp_out()
  design <- write_design(out, c(
    "name: gen_test",
    "language: english",
    "paradigm: lexical_decision",
    "items:",
    "  source: generate",
    paste0("  lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "n_per_condition: 5",
    "pool_filters: {length: [4, 7], frequency: [3.5, 6.0]}"
  ))

  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)

  stim <- read_csv_utf8(res$stimuli)
  expect_setequal(unique(stim$condition), c("word", "pseudoword"))
  expect_equal(as.integer(table(stim$condition)), c(5L, 5L))
})

test_that("run_pipeline reads a table design from its items file", {
  out <- tmp_out()
  items <- file.path(out, "pairs.csv")
  writeLines(c("item,condition,prime,target",
               "1,related,nurse,doctor",
               "1,unrelated,window,doctor",
               "2,related,dog,cat",
               "2,unrelated,table,cat"), items, useBytes = TRUE)
  design <- write_design(out, c(
    "name: tab_test",
    "language: english",
    "paradigm: priming",
    "items:",
    "  source: table",
    paste0("  path: ", as_yaml_path(items)),
    "counterbalance:",
    "  lists: 2"
  ))

  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)

  stim <- read_csv_utf8(res$stimuli)
  expect_setequal(unique(stim$target), c("doctor", "cat"))
  # A table design matches nothing, so no descriptives report is produced.
  expect_null(res$descriptives)
  expect_null(res$comparisons)
})

test_that("an unknown item source is an error, not a silent fallback", {
  out <- tmp_out()
  design <- write_design(out, c(
    "name: bad_test",
    "language: english",
    "items:",
    "  source: telepathy"
  ))
  expect_error(run_quiet(design, extdata("schema.yaml"), outdir = out),
               "unknown item source 'telepathy'")
})

test_that("run_all errors when the configuration directory holds no designs", {
  out <- tmp_out()
  expect_error(run_all(config_dir = out, schema_path = extdata("schema.yaml"),
                       outdir = out, verbose = FALSE),
               "no design_.*yaml files")
})

# ---- pipeline-level guards --------------------------------------------------
# Twinned with test_run_pipeline.py: every fixture, expectation and message
# below must stay in step with the Python suite.

test_that("a misspelt pool filter is an error, not an unfiltered pool", {
  out <- tmp_out()
  design <- write_design(out, c(
    "name: guard_test",
    "language: english",
    paste0("lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "n_per_condition: 5",
    "pool_filters: {frequncy: [3.8, 7]}",
    "conditions:",
    "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
    "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
    "match_on: [length]"
  ))
  expect_error(run_quiet(design, extdata("schema.yaml"), outdir = out),
               "pool_filters name column")
})

test_that("a non-integer n_per_condition is an error", {
  out <- tmp_out()
  design <- write_design(out, c(
    "name: guard_test",
    "language: english",
    paste0("lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "n_per_condition: 2.5",
    "conditions:",
    "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
    "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
    "match_on: [length]"
  ))
  expect_error(run_quiet(design, extdata("schema.yaml"), outdir = out),
               "positive whole number")
})

# Both values used to slip past this guard in one engine only. A configured 0 is
# falsy in Python, so `or` read it as absent, fell through to the matcher's default
# of twenty and ran; `%||%` here falls back on NULL alone and refused. An infinite
# request went the other way: trunc(Inf) is Inf, so this engine took it as a whole
# number and selected the whole pool, while Python's int() raised OverflowError.
# Pinned identically in tests/test_run_pipeline.py.
test_that("a zero or infinite n_per_condition is an error", {
  for (n in c("0", ".inf")) {
    out <- tmp_out()
    design <- write_design(out, c(
      "name: guard_test",
      "language: english",
      paste0("lexicon: ", as_yaml_path(extdata("en_example.csv"))),
      paste0("n_per_condition: ", n),
      "conditions:",
      "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
      "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
      "match_on: [length]"
    ))
    expect_error(run_quiet(design, extdata("schema.yaml"), outdir = out),
                 "positive whole number", info = n)
  }
})

# A design with one condition has nothing to compare against the anchor, and the
# engines used to part company there: this one died inside the reporting loop on
# seq_len(nrow(NULL)), while the Python engine finished and wrote a comparisons CSV
# with no header. Both now write this header and no rows. Pinned identically in
# tests/test_run_pipeline.py.
test_that("a single-condition design completes and writes a header-only comparisons file", {
  out <- tmp_out()
  design <- write_design(out, c(
    "name: onecond",
    "language: english",
    paste0("lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "n_per_condition: 5",
    "pool_filters: {length: [3, 7], frequency: [3.8, 7]}",
    "conditions:",
    "  - {name: only, define_by: {frequency: [4.0, 7.0]}}",
    "match_on: [length]"
  ))

  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)

  expect_true(file.exists(res$comparisons))
  expect_identical(
    readLines(res$comparisons, warn = FALSE),
    paste0("condition,reference,dimension,cohens_d,d_ci_low,d_ci_high,",
           "var_ratio,tost_p,equivalent"))
})

test_that("a continuous table without members is an error", {
  out <- tmp_out()
  items <- file.path(out, "pairs.csv")
  writeLines(c("item,condition,prime,target", "1,related,nurse,doctor"),
             items, useBytes = TRUE)
  design <- write_design(out, c(
    "name: guard_test",
    "language: english",
    "paradigm: priming",
    "items:",
    "  source: table",
    paste0("  path: ", as_yaml_path(items)),
    "continuous:",
    "  predictor: target.frequency",
    "  controls: [target.length]",
    "match_on: [target.length]"
  ))
  expect_error(run_quiet(design, extdata("schema.yaml"), outdir = out),
               "requires items.members")
})

test_that("pool_filters on a plain table are an error", {
  out <- tmp_out()
  items <- file.path(out, "pairs.csv")
  writeLines(c("item,condition,prime,target",
               "1,related,nurse,doctor",
               "1,unrelated,window,doctor"), items, useBytes = TRUE)
  design <- write_design(out, c(
    "name: guard_test",
    "language: english",
    "paradigm: priming",
    "items:",
    "  source: table",
    paste0("  path: ", as_yaml_path(items)),
    "pool_filters: {length: [3, 7]}"
  ))
  expect_error(run_quiet(design, extdata("schema.yaml"), outdir = out),
               "pool_filters have no effect")
})

test_that("a generate shortfall errors by default and allow accepts it", {
  out <- tmp_out()
  base <- c(
    "name: guard_gen",
    "language: english",
    "paradigm: lexical_decision",
    "items:",
    "  source: generate",
    paste0("  lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "n_per_condition: 2000",
    "pool_filters: {length: [4, 7], frequency: [3.5, 6.0]}"
  )
  expect_error(run_quiet(write_design(out, base), extdata("schema.yaml"), outdir = out),
               "could be generated")
  out2 <- tmp_out()
  design <- write_design(out2, c(base, "matching: {shortfall: allow}"))
  res <- suppressMessages(run_quiet(design, extdata("schema.yaml"), outdir = out2))
  expect_true(file.exists(res$stimuli))
})

test_that("a condition without define_by reaches the datasheet", {
  # This engine's NULL define_by always fell back to the whole pool; the Python
  # engine used to crash with a bare KeyError on the same design, so this run is
  # pinned in both suites.
  out <- tmp_out()
  design <- write_design(out, c(
    "name: guard_bare",
    "language: english",
    paste0("lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "n_per_condition: 3",
    "pool_filters: {length: [3, 7], frequency: [3.8, 7]}",
    "conditions:",
    "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
    "  - {name: rest}",
    "match_on: [length]"
  ))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)
  stim <- read_csv_utf8(res$stimuli)
  expect_setequal(unique(stim$condition), c("high", "rest"))
  ds <- jsonlite::fromJSON(file.path(out, "reports", "guard_bare_english_datasheet_R.json"),
                           simplifyVector = FALSE)
  entries <- ds$selection$candidate_pool
  conds <- vapply(entries, function(e) e$condition, character(1))
  counts <- vapply(entries, function(e) as.numeric(e$n_candidates), numeric(1))
  expect_setequal(conds, c("high", "rest"))
  # The bare condition's candidates are the whole filtered pool.
  expect_gte(counts[conds == "rest"], counts[conds == "high"])
  expect_gt(counts[conds == "high"], 0)
})

test_that("a pair design's window relaxation reaches the datasheet", {
  # The pair path dropped the selector's audit on re-expansion, so a tolerance
  # relaxation never reached the run log or the datasheet. tolerance_k 0 pins a
  # zero-width window that no pair satisfies, forcing the relaxation.
  out <- tmp_out()
  items <- file.path(out, "pairs.csv")
  writeLines(c("item,condition,prime,target",
               "1,related,aaa,flat", "1,unrelated,abba,flat",
               "2,related,acne,glass", "2,unrelated,aaron,glass",
               "3,related,alarm,across", "3,unrelated,abrams,across",
               "4,related,aha,house", "4,unrelated,abdel,house"),
             items, useBytes = TRUE)
  design <- write_design(out, c(
    "name: guard_pair_relax",
    "language: english",
    "paradigm: priming",
    "items:",
    "  source: table",
    paste0("  path: ", as_yaml_path(items)),
    "  members: [prime, target]",
    paste0("  lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "  anchor_condition: related",
    "n_per_condition: 3",
    "continuous:",
    "  predictor: target.frequency",
    "  controls: [target.length]",
    "match_on: [target.length]",
    "matching: {tolerance_k: {target.length: 0}}"
  ))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)
  ds <- jsonlite::fromJSON(file.path(out, "reports",
                                     "guard_pair_relax_english_datasheet_R.json"),
                           simplifyVector = FALSE)
  rx <- ds$selection$window_relaxations
  expect_length(rx, 1)
  expect_identical(rx[[1]]$condition, "continuous")
  expect_identical(as.integer(rx[[1]]$n_needed), 3L)
  log <- paste(readLines(res$log, warn = FALSE), collapse = "\n")
  expect_true(grepl("tolerance window relaxed", log, fixed = TRUE))
})

test_that("a continuous design over a supplied pool selects continuously", {
  # The predicate that gates the continuous selector must treat a supplied
  # pool like a corpus; before the fix this design fell through to the
  # conditions matcher and crashed differently in each engine.
  out <- tmp_out()
  lex <- read_csv_utf8(extdata("en_example.csv"))
  pool_path <- file.path(out, "pool.csv")
  write_csv_utf8(data.frame(word = head(lex$word, 60)), pool_path)
  design <- write_design(out, c(
    "name: guard_pool",
    "language: english",
    "items:",
    "  source: pool",
    paste0("  path: ", as_yaml_path(pool_path)),
    paste0("  lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "n_per_condition: 10",
    "continuous:",
    "  predictor: frequency",
    "  controls: [length]",
    "match_on: [length]"
  ))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)
  stim <- read_csv_utf8(res$stimuli)
  expect_true(all(stim$condition == "continuous"))
  expect_equal(sort(unique(stim$set)), 1:10)
})

test_that("run_pipeline leaves the verbosity option as it found it", {
  # An exported function that set an option and walked away would silence, or
  # unsilence, the rest of the caller's session. Both exit paths are covered,
  # since a design that fails validation must restore it too.
  # test_run_pipeline.py::test_verbose_false_keeps_the_console_silent asserts the
  # same property on the Python engine's module-level gate.
  out <- tmp_out()
  design <- write_design(out, c(
    "name: opt_test",
    "language: english",
    paste0("lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "n_per_condition: 5",
    "pool_filters: {length: [3, 7], frequency: [3.8, 7]}",
    "conditions:",
    "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
    "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
    "match_on: [length]"
  ))

  before <- getOption("lexsync.verbose")
  invisible(run_quiet(design, extdata("schema.yaml"), outdir = out))
  expect_identical(getOption("lexsync.verbose"), before)

  bad <- write_design(out, c(
    "name: opt_test_bad",
    "language: english",
    paste0("lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "n_per_condition: 0",
    "conditions:",
    "  - {name: high, define_by: {frequency: [5.0, 7.0]}}"
  ))
  expect_error(run_quiet(bad, extdata("schema.yaml"), outdir = out),
               "positive whole number")
  expect_identical(getOption("lexsync.verbose"), before)
})

# The example lexicon, shortened, without the columns lexsync derives itself.
# load_lexicon() requires `word` and `freq_zipf` alone, so this is a lexicon a user
# may legitimately point lexsync at. Twinned with _bare_lexicon in
# test_run_pipeline.py.
bare_lexicon <- function(dir, n = 600L) {
  lex <- read_csv_utf8(extdata("en_example.csv"))[seq_len(n), , drop = FALSE]
  path <- file.path(dir, "bare.csv")
  write_csv_utf8(lex[setdiff(names(lex), c("n_density", "old20"))], path)
  path
}

# The dimension as add_neighbourhood() computes it, over the same reference list.
derived_here <- function(path, words, dim) {
  ref <- as.character(read_csv_utf8(path)$word)
  add_neighbourhood(data.frame(word = words, stringsAsFactors = FALSE),
                    reference = ref)[[dim]]
}

test_that("a condition defined by a derived dimension computes it", {
  # The derivation used to be triggered by `match_on` alone, so a design that defined
  # its conditions by n_density -- the shape of the shipped design_en_ndensity.yaml --
  # stopped on any lexicon that did not ship the column.
  out <- tmp_out()
  lexicon <- bare_lexicon(out)
  design <- write_design(out, c(
    "name: derived_define", "language: english",
    paste0("lexicon: ", as_yaml_path(lexicon)), "n_per_condition: 3",
    "pool_filters: {length: [3, 7]}",
    "conditions:",
    "  - {name: dense, define_by: {n_density: [5, 100]}}",
    "  - {name: sparse, define_by: {n_density: [0, 1]}}",
    "match_on: [length, frequency]"))
  stim <- read_csv_utf8(run_quiet(design, extdata("schema.yaml"), outdir = out)$stimuli)
  expect_equal(nrow(stim), 6)
  expect_equal(stim$n_density, derived_here(lexicon, stim$word, "n_density"))
  expect_true(all(stim$n_density[stim$condition == "dense"] >= 5))
})

test_that("a pool filter on a derived dimension computes it", {
  # The filter names a column the lexicon does not have, and the guard on unknown
  # filter names used to reject the design before anything could derive it.
  out <- tmp_out()
  lexicon <- bare_lexicon(out)
  design <- write_design(out, c(
    "name: derived_filter", "language: english",
    paste0("lexicon: ", as_yaml_path(lexicon)), "n_per_condition: 3",
    "pool_filters: {length: [3, 7], old20: [1.0, 2.0]}",
    "conditions:",
    "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
    "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
    "match_on: [length]"))
  stim <- read_csv_utf8(run_quiet(design, extdata("schema.yaml"), outdir = out)$stimuli)
  expect_equal(nrow(stim), 6)
  expect_true(all(stim$old20 >= 1.0 & stim$old20 <= 2.0))
  expect_equal(stim$old20, derived_here(lexicon, stim$word, "old20"))
})

test_that("a continuous predictor on a derived dimension computes it", {
  out <- tmp_out()
  lexicon <- bare_lexicon(out)
  design <- write_design(out, c(
    "name: derived_continuous", "language: english",
    paste0("lexicon: ", as_yaml_path(lexicon)), "n_per_condition: 6",
    "pool_filters: {length: [3, 7]}",
    "continuous: {predictor: old20, controls: [length, frequency]}",
    "match_on: [length, frequency]"))
  stim <- read_csv_utf8(run_quiet(design, extdata("schema.yaml"), outdir = out)$stimuli)
  expect_equal(nrow(stim), 6)
  expect_equal(stim$old20, derived_here(lexicon, stim$word, "old20"))
})

test_that("a misspelt filter is still refused beside a derived one", {
  out <- tmp_out()
  lexicon <- bare_lexicon(out)
  design <- write_design(out, c(
    "name: derived_typo", "language: english",
    paste0("lexicon: ", as_yaml_path(lexicon)), "n_per_condition: 3",
    "pool_filters: {old20: [1.0, 2.0], frequncy: [3.8, 7]}",
    "conditions:",
    "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
    "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
    "match_on: [length]"))
  expect_error(run_quiet(design, extdata("schema.yaml"), outdir = out),
               "pool_filters name column")
})

constant_pool_design <- function(dir) {
  # Two conditions each constant on the one matched dimension, at different
  # constants, so Cohen's d and its interval are undefined for every comparison.
  pool <- file.path(dir, "pool.csv")
  words <- c("abcd", "efgh", "ijkl", "mnop", "qrst", "uvwx",
             "abcdef", "ghijkl", "mnopqr", "stuvwx", "yzabcd", "efghij")
  write_csv_utf8(data.frame(word = words, stringsAsFactors = FALSE), pool)
  write_design(dir, c(
    "name: undefined_d", "language: english",
    "items:", "  source: pool", paste0("  path: ", as_yaml_path(pool)),
    "n_per_condition: 3",
    "conditions:",
    "  - {name: four, define_by: {length: [4, 4]}}",
    "  - {name: six, define_by: {length: [6, 6]}}",
    "match_on: [length]"))
}

test_that("an undefined Cohen's d on every comparison still runs", {
  # Twin of test_run_pipeline.py::test_an_undefined_cohens_d_on_every_comparison_
  # still_runs, which pins the same run log line: the Python engine used to stop
  # here rather than report the statistic as missing.
  out <- tmp_out()
  res <- run_quiet(constant_pool_design(out), extdata("schema.yaml"), outdir = out)
  comparisons <- read_csv_utf8(res$comparisons)
  expect_true(all(is.na(comparisons$cohens_d)))
  expect_true(any(grepl("equivalence six vs four on 'length': d = NA,",
                        readLines(res$log, encoding = "UTF-8"), fixed = TRUE)))
})

# The two engines' run logs quoted different numbers for the same statistic: the
# stored value is at four places and R rounded to three while Python printed all of
# them, so 0.0016 was also written 0.002 and 1.0 was also written 1.000. The Python
# suite pins the same two lines, fixture for fixture.
fractional_tost_design <- function(dir) {
  pool <- file.path(dir, "pool.csv")
  rows <- list()
  i <- 0L
  for (a in letters[1:10]) for (b in c("a", "e", "i", "o", "u")) for (cc in letters[1:6]) {
    word <- if (i %% 3L) paste0(a, b, cc) else paste0(a, b, cc, "z")
    rows[[length(rows) + 1L]] <- data.frame(word = word,
                                            frequency = 1 + (i %% 19L) / 4.5,
                                            stringsAsFactors = FALSE)
    i <- i + 1L
  }
  df <- do.call(rbind, rows)
  write_csv_utf8(df[!duplicated(df$word), , drop = FALSE], pool)
  write_design(dir, c(
    "name: tost_format", "language: english",
    "items:", "  source: pool", paste0("  path: ", as_yaml_path(pool)),
    "n_per_condition: 25",
    "conditions:",
    "  - {name: low, define_by: {frequency: [1.0, 2.0]}}",
    "  - {name: high, define_by: {frequency: [3.5, 5.5]}}",
    "match_on: [length]"))
}

test_that("the run log writes the TOST p at four places", {
  out <- tmp_out()
  res <- run_quiet(fractional_tost_design(out), extdata("schema.yaml"), outdir = out)
  log <- readLines(res$log, encoding = "UTF-8")
  expect_true(any(grepl("on 'length': d = 0.00 [-0.47, 0.47], TOST p = 0.0417 (equivalent)",
                        log, fixed = TRUE)))
  expect_true(any(grepl("TOST p = 1.0000 (not shown equivalent)", log, fixed = TRUE)))
})

malformed <- function(dir, name, text) {
  p <- file.path(dir, name)
  writeLines(text, p, useBytes = TRUE)
  p
}

test_that("a design that is not a mapping names the file", {
  # An empty or list-shaped design used to report an R type and not the file.
  # Mirrored in test_run_pipeline.py.
  out <- tmp_out()
  for (text in list(character(0), c("- a", "- b"))) {
    design <- malformed(out, "design_bad.yaml", text)
    expect_error(run_quiet(design, extdata("schema.yaml"), outdir = out),
                 sprintf("lexsync: design '%s' did not parse to a mapping of keys", design),
                 fixed = TRUE)
  }
})

test_that("a design without a name or a language is refused", {
  # The base name for every artefact is built from both, so a nameless design used
  # to write its files under the language alone.
  out <- tmp_out()
  cases <- list(list(c("language: english"), "name"),
                list(c("name: nameless"), "language"),
                list(c("name: ' '", "language: english"), "name"))
  for (case in cases) {
    design <- write_design(out, case[[1]])
    expect_error(run_quiet(design, extdata("schema.yaml"), outdir = out),
                 sprintf("is missing the required key(s) '%s'.", case[[2]]), fixed = TRUE)
  }
  expect_length(list.files(out, pattern = "_stimuli_R[.]csv$", recursive = TRUE), 0L)
})

test_that("a schema without its structural blocks is refused", {
  out <- tmp_out()
  schema <- malformed(out, "schema.yaml", "seed: 2026")
  design <- write_design(out, c(
    "name: guard_test", "language: english",
    paste0("lexicon: ", as_yaml_path(extdata("en_example.csv"))), "n_per_condition: 5",
    "conditions:",
    "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
    "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
    "match_on: [length]"))
  expect_error(run_quiet(design, schema, outdir = out),
               sprintf(paste("lexsync: schema '%s' is missing the required key(s)",
                             "'lexicon_schema', 'matching'."), schema), fixed = TRUE)
})

test_that("run_all names the design that failed", {
  # A quiet sweep reported the bare failure of an unnamed one of twenty designs.
  out <- tmp_out()
  malformed(out, "design_b_bad.yaml", character(0))
  expect_error(run_all(config_dir = out, schema_path = extdata("schema.yaml"),
                       outdir = out, verbose = FALSE),
               "lexsync: design 'design_b_bad.yaml' failed: ", fixed = TRUE)
})
