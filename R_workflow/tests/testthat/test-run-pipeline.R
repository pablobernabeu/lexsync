extdata <- function(f) system.file("extdata", f, package = "lexsync")

# Everything is written under tempdir(), so R CMD check leaves no artefacts and
# the committed output/ tree that the parity suite compares against is untouched.
tmp_out <- function() {
  d <- tempfile("lexsync-")
  dir.create(d, recursive = TRUE, showWarnings = FALSE)
  d
}

# run_pipeline() sets the verbosity option globally; restore it so the setting
# cannot leak into the tests that follow.
run_quiet <- function(...) {
  old <- options(lexsync.verbose = getOption("lexsync.verbose", TRUE))
  on.exit(options(old), add = TRUE)
  run_pipeline(..., verbose = FALSE)
}

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
