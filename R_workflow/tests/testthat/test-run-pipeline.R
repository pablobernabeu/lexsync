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

test_that("pipeline functions require an explicit output directory", {
  expect_error(run_pipeline("not-used.yaml", verbose = FALSE),
               "outdir must be supplied")
  expect_error(run_all(config_dir = "not-used", verbose = FALSE),
               "outdir must be supplied")
})

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

# Ten nouns and ten verbs. Two nouns and one verb have no rating, as words a norm table
# does not cover would have none. The ratings are invented for this test.
rated_lexicon <- function(dir) {
  path <- file.path(dir, "lexicon.csv")
  writeLines(c("word,freq_zipf,pos,rating",
               "anchor,3.66,noun,2.1", "basket,3.88,noun,", "bottle,4.58,noun,3.0",
               "button,4.29,noun,2.6", "candle,3.79,noun,2.2", "carpet,3.92,noun,",
               "forest,4.62,noun,3.4", "garden,4.83,noun,2.8", "ladder,3.74,noun,2.4",
               "mirror,4.33,noun,3.1", "arrive,4.27,verb,2.0", "borrow,3.95,verb,2.7",
               "decide,4.88,verb,", "divide,3.98,verb,2.3", "escape,4.52,verb,3.3",
               "follow,5.08,verb,2.9", "gather,4.18,verb,2.5", "invite,4.03,verb,3.2",
               "listen,4.91,verb,2.2", "punish,3.77,verb,3.0"),
             path, useBytes = TRUE)
  path
}

test_that("an exclusion for a missing matched value reaches the record", {
  # Matching excludes a candidate missing a matched dimension, and the run log and the
  # datasheet say how many each condition lost. Twinned with test_run_pipeline.py.
  out <- tmp_out()
  design <- write_design(out, c(
    "name: guard_incomplete",
    "language: english",
    paste0("lexicon: ", as_yaml_path(rated_lexicon(out))),
    "n_per_condition: 4",
    "conditions:",
    "  - {name: noun, define_by: {pos: [noun]}}",
    "  - {name: verb, define_by: {pos: [verb]}}",
    "match_on: [length, rating]"
  ))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)
  ds <- jsonlite::fromJSON(file.path(out, "reports",
                                     "guard_incomplete_english_datasheet_R.json"),
                           simplifyVector = FALSE)
  expect_identical(ds$selection$incomplete_dropped,
                   list(list(condition = "noun", n = 2L), list(condition = "verb", n = 1L)))
  log <- paste(readLines(res$log, warn = FALSE), collapse = "\n")
  expect_true(grepl("dropped 2 candidate(s) of condition 'noun' missing a matched dimension",
                    log, fixed = TRUE))
  expect_true(grepl("dropped 1 candidate(s) of condition 'verb' missing a matched dimension",
                    log, fixed = TRUE))
})

test_that("a continuous design's exclusion reaches the record", {
  out <- tmp_out()
  design <- write_design(out, c(
    "name: guard_incomplete_cont",
    "language: english",
    paste0("lexicon: ", as_yaml_path(rated_lexicon(out))),
    "n_per_condition: 6",
    "continuous: {predictor: rating, controls: [length]}",
    "match_on: [length]"
  ))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)
  ds <- jsonlite::fromJSON(file.path(out, "reports",
                                     "guard_incomplete_cont_english_datasheet_R.json"),
                           simplifyVector = FALSE)
  expect_identical(ds$selection$incomplete_dropped,
                   list(list(condition = "continuous", n = 3L)))
  log <- paste(readLines(res$log, warn = FALSE), collapse = "\n")
  expect_true(grepl("dropped 3 candidate(s) missing the predictor or a control", log,
                    fixed = TRUE))
})

test_that("a pair design's exclusion reaches the record", {
  # The pair path selects over one row per set and copies the selector's audit onto
  # the re-expanded table. 'across' has no rating, so its set is excluded and the
  # count reaches the run log and the datasheet. Twinned with test_run_pipeline.py.
  out <- tmp_out()
  items <- file.path(out, "pairs.csv")
  writeLines(c("item,condition,prime,target",
               "1,related,aaa,flat", "1,unrelated,abba,flat",
               "2,related,acne,glass", "2,unrelated,aaron,glass",
               "3,related,alarm,across", "3,unrelated,abrams,across",
               "4,related,aha,house", "4,unrelated,abdel,house"),
             items, useBytes = TRUE)
  ratings <- file.path(out, "ratings.csv")
  writeLines(c("word,rating", "flat,2.5", "glass,3.1", "house,4.0"), ratings,
             useBytes = TRUE)
  design <- write_design(out, c(
    "name: guard_pair_incomplete",
    "language: english",
    "paradigm: priming",
    "norms:",
    paste0("  - {path: ", as_yaml_path(ratings), ", columns: [rating]}"),
    "items:",
    "  source: table",
    paste0("  path: ", as_yaml_path(items)),
    "  members: [prime, target]",
    paste0("  lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "  anchor_condition: related",
    "n_per_condition: 3",
    "continuous:",
    "  predictor: target.rating",
    "  controls: [target.length]",
    "match_on: [target.length]"
  ))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)
  ds <- jsonlite::fromJSON(file.path(out, "reports",
                                     "guard_pair_incomplete_english_datasheet_R.json"),
                           simplifyVector = FALSE)
  expect_identical(ds$selection$incomplete_dropped,
                   list(list(condition = "continuous", n = 1L)))
  log <- paste(readLines(res$log, warn = FALSE), collapse = "\n")
  expect_true(grepl("dropped 1 candidate(s) missing the predictor or a control", log,
                    fixed = TRUE))
  expect_false(any(grepl("across", readLines(res$stimuli, warn = FALSE), fixed = TRUE)))
})

test_that("a resampled design's exclusion reaches the record", {
  # resample_stimuli records the first replicate's exclusions, which are the whole
  # pool's, and the pipeline used to discard its audit. Twinned with
  # test_run_pipeline.py.
  out <- tmp_out()
  design <- write_design(out, c(
    "name: guard_incomplete_resample",
    "language: english",
    paste0("lexicon: ", as_yaml_path(rated_lexicon(out))),
    "n_per_condition: 3",
    "conditions:",
    "  - {name: noun, define_by: {pos: [noun]}}",
    "  - {name: verb, define_by: {pos: [verb]}}",
    "match_on: [length, rating]",
    "resample: {n_sets: 2}"
  ))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)
  ds <- jsonlite::fromJSON(file.path(out, "reports",
                                     "guard_incomplete_resample_english_datasheet_R.json"),
                           simplifyVector = FALSE)
  expect_identical(ds$selection$incomplete_dropped,
                   list(list(condition = "noun", n = 2L), list(condition = "verb", n = 1L)))
  log <- paste(readLines(res$log, warn = FALSE), collapse = "\n")
  expect_true(grepl("dropped 2 candidate(s) of condition 'noun' missing a matched dimension",
                    log, fixed = TRUE))
  expect_true(grepl("dropped 1 candidate(s) of condition 'verb' missing a matched dimension",
                    log, fixed = TRUE))
})

# Three conditions in two lists run under the default counterbalance.incomplete: allow,
# and the run log, the datasheet and the Methods text say what the rotation leaves out.
# Pinned identically in tests/test_run_pipeline.py.
test_that("an incomplete rotation reaches the run log and the datasheet", {
  out <- tmp_out()
  items <- file.path(out, "items.csv")
  grid <- expand.grid(c = c("identity", "related", "unrelated"), s = 1:6,
                      stringsAsFactors = FALSE)
  writeLines(c("item,condition,prime,target",
               sprintf("%d,%s,%s%d,t%d", grid$s, grid$c, substr(grid$c, 1L, 3L), grid$s,
                       grid$s)),
             items, useBytes = TRUE)
  design <- write_design(out, c(
    "name: guard_incomplete",
    "language: english",
    "paradigm: priming",
    "items:",
    "  source: table",
    paste0("  path: ", as_yaml_path(items)),
    "counterbalance:",
    "  lists: 2"
  ))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)
  issue <- "With 2 lists and 3 conditions, each item appears in only 2 of its 3 conditions."
  log <- paste(readLines(res$log, warn = FALSE), collapse = "\n")
  expect_true(grepl(paste0("counterbalancing: ", issue), log, fixed = TRUE))
  record <- jsonlite::fromJSON(file.path(out, "reports",
                                         "guard_incomplete_english_datasheet_R.json"),
                               simplifyVector = FALSE)$counterbalancing
  expect_false(record$complete)
  expect_identical(unlist(record$issues), issue)
  expect_identical(as.integer(record$lists), 2L)
  md <- paste(readLines(file.path(out, "reports", "guard_incomplete_english_datasheet_R.md"),
                        warn = FALSE), collapse = "\n")
  expect_true(grepl("(an incomplete Latin-square rotation)", md, fixed = TRUE))
})

# Two lists give two OpenSesame experiments, each with its own loop and text tables. The
# run log recorded the three experiment scripts only, and the datasheet listed no loop
# table, although the loop tables hold the trial order and the trigger codes. Pinned
# identically in tests/test_run_pipeline.py.
test_that("the run log and the datasheet name every experiment file", {
  out <- tmp_out()
  items <- file.path(out, "items.csv")
  grid <- expand.grid(c = c("related", "unrelated"), s = 1:4, stringsAsFactors = FALSE)
  writeLines(c("item,condition,prime,target",
               sprintf("%d,%s,%s%d,t%d", grid$s, grid$c, substr(grid$c, 1L, 3L), grid$s,
                       grid$s)),
             items, useBytes = TRUE)
  design <- write_design(out, c(
    "name: guard_versions",
    "language: english",
    "paradigm: priming",
    "items:",
    "  source: table",
    paste0("  path: ", as_yaml_path(items)),
    "counterbalance:",
    "  lists: 2"
  ))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)
  files <- res$experiments$files
  expect_identical(basename(files), c(
    "guard_versions_english_psychopy.py", "guard_versions_english_list1.osexp",
    "guard_versions_english_list2.osexp", "guard_versions_english.html",
    "guard_versions_english_psychopy.csv",
    "guard_versions_english_list1_opensesame.csv",
    "guard_versions_english_list1_opensesame_text.csv",
    "guard_versions_english_list2_opensesame.csv",
    "guard_versions_english_list2_opensesame_text.csv"))
  expect_identical(res$experiments$opensesame, files[2])
  log <- paste(readLines(res$log, warn = FALSE), collapse = "\n")
  for (p in files) {
    expect_true(grepl(sprintf("wrote '%s'", basename(p)), log, fixed = TRUE), info = p)
  }
  record <- jsonlite::fromJSON(file.path(out, "reports",
                                         "guard_versions_english_datasheet_R.json"),
                               simplifyVector = FALSE)
  recorded <- vapply(record$artifacts, function(a) basename(a$file), character(1))
  expect_identical(recorded[-1], basename(files))
  expect_identical(as.integer(record$counterbalancing$versions), 2L)
})

# One item set in three conditions, dealt to two lists, never shows its third
# condition. The check counts the conditions of the table the pipeline dealt, not those
# the lists hold, so it reports three conditions and gives the condition left out an
# empty cell in each list. Pinned identically in tests/test_run_pipeline.py.
test_that("a condition no list reaches is still counted", {
  out <- tmp_out()
  items <- file.path(out, "items.csv")
  writeLines(c("item,condition,prime,target", "1,identity,ide1,t1", "1,related,rel1,t1",
               "1,unrelated,unr1,t1"), items, useBytes = TRUE)
  design <- write_design(out, c(
    "name: guard_unreached",
    "language: english",
    "paradigm: priming",
    "items:",
    "  source: table",
    paste0("  path: ", as_yaml_path(items)),
    "counterbalance:",
    "  lists: 2"
  ))
  run_quiet(design, extdata("schema.yaml"), outdir = out)
  record <- jsonlite::fromJSON(file.path(out, "reports",
                                         "guard_unreached_english_datasheet_R.json"),
                               simplifyVector = FALSE)$counterbalancing
  expect_identical(unlist(record$issues), c(
    "With 2 lists and 3 conditions, each item appears in only 2 of its 3 conditions.",
    paste0("With 1 item set and 3 conditions, the item sets are not a multiple of the ",
           "conditions, so the conditions within each list differ by one trial.")))
  cells <- vapply(record$cells, function(x) sprintf("%s %s %s", x$list, x$condition,
                                                    x$n_trials), character(1))
  expect_identical(cells, c("1 identity 1", "1 related 0", "1 unrelated 0",
                            "2 identity 0", "2 related 1", "2 unrelated 0"))
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

# Pins the same contract as test_the_run_log_and_datasheet_record_nfc_normalisation in
# tests/test_run_pipeline.py. Each word appears in NFC and in NFD, the second spelling
# in the other condition. Before normalisation they were four words, and the matcher
# could put a word in both conditions of one set.
test_that("the run log and datasheet record NFC normalisation", {
  out <- tmp_out()
  avion <- intToUtf8(c(0x61, 0x76, 0x69, 0xF3, 0x6E))
  limon <- intToUtf8(c(0x6C, 0x69, 0x6D, 0xF3, 0x6E))
  cafe <- intToUtf8(c(0x63, 0x61, 0x66, 0xE9))
  papa <- intToUtf8(c(0x70, 0x61, 0x70, 0xE1))
  avion_d <- intToUtf8(c(0x61, 0x76, 0x69, 0x6F, 0x301, 0x6E))
  limon_d <- intToUtf8(c(0x6C, 0x69, 0x6D, 0x6F, 0x301, 0x6E))
  cafe_d <- intToUtf8(c(0x63, 0x61, 0x66, 0x65, 0x301))
  papa_d <- intToUtf8(c(0x70, 0x61, 0x70, 0x61, 0x301))
  pool_path <- file.path(out, "pool.csv")
  con <- file(pool_path, open = "wb")
  writeBin(charToRaw(enc2utf8(paste0(
    "word,grp\n", avion, ",a\n", avion_d, ",b\n", limon_d, ",b\n", limon, ",a\n",
    cafe, ",a\n", cafe_d, ",b\n", papa_d, ",b\n", papa, ",a\n"))), con)
  close(con)
  design <- write_design(out, c(
    "name: nfc_record",
    "language: spanish",
    "items:",
    "  source: pool",
    paste0("  path: ", as_yaml_path(pool_path)),
    "n_per_condition: 2",
    "conditions:",
    "  - {name: a, define_by: {grp: [a]}}",
    "  - {name: b, define_by: {grp: [b]}}",
    "match_on: [length]"
  ))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out,
                   reference_words = c(avion_d, limon_d))
  stim <- read_csv_utf8(res$stimuli)
  got <- paste(stim$condition, stim$word)
  expect_identical(sort(got, method = "radix"),
                   sort(paste(c("a", "a", "b", "b"), c(avion, cafe, limon, papa)),
                        method = "radix"))
  # Four pool rows and both reference words changed, and four pool rows were merged.
  log <- paste(readLines(res$log, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
  expect_true(grepl("normalised 6 word form(s) to NFC; 4 duplicate(s) removed", log,
                    fixed = TRUE))
  ds <- jsonlite::read_json(file.path(out, "reports", "nfc_record_spanish_datasheet_R.json"))
  expect_identical(ds$materials_source$input_normalisation,
                   list(changed = 6L, collapsed = 4L))

  # Input already in NFC leaves no trace, so no shipped datasheet changes.
  clean <- tmp_out()
  design <- write_design(clean, c(
    "name: clean_record",
    "language: english",
    paste0("lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "n_per_condition: 5",
    "pool_filters: {length: [3, 7], frequency: [3.8, 7]}",
    "conditions:",
    "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
    "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
    "match_on: [length]"
  ))
  run_quiet(design, extdata("schema.yaml"), outdir = clean)
  ds <- jsonlite::read_json(file.path(clean, "reports", "clean_record_english_datasheet_R.json"))
  expect_false("input_normalisation" %in% names(ds$materials_source))
})

# Pins the same contract as test_a_practice_tables_nfc_normalisation_is_recorded in
# tests/test_run_pipeline.py. A practice or filler table goes through load_items() like
# the main one, so its text is put in NFC too, and the record used to leave that out.
test_that("a practice table's NFC normalisation is recorded", {
  out <- tmp_out()
  practice <- file.path(out, "practice.csv")
  con <- file(practice, open = "wb")
  writeBin(charToRaw(enc2utf8(paste0(
    "item,condition,word\n1,high,", intToUtf8(c(0x63, 0x61, 0x66, 0x65, 0x301)),
    "\n2,low,dog\n"))), con)
  close(con)
  design <- write_design(out, c(
    "name: practice_record",
    "language: english",
    paste0("lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "n_per_condition: 5",
    "pool_filters: {length: [3, 7], frequency: [3.8, 7]}",
    "conditions:",
    "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
    "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
    "match_on: [length]",
    "practice:",
    paste0("  path: ", as_yaml_path(practice))
  ))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)
  log <- paste(readLines(res$log, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
  expect_true(grepl("normalised 1 word form(s) to NFC; 0 duplicate(s) removed", log,
                    fixed = TRUE))
  ds <- jsonlite::read_json(file.path(out, "reports", "practice_record_english_datasheet_R.json"))
  expect_identical(ds$materials_source$input_normalisation,
                   list(changed = 1L, collapsed = 0L))
})

# `$` on a list matches a name partially when no name matches exactly, so a design
# key that only began another key's name stood in for it. These two designs carry
# such keys, which the Python engine never read, and the pair is pinned identically
# in tests/test_run_pipeline.py.
test_that("a key that only begins a design key is not read", {
  out <- tmp_out()
  design <- write_design(out, c(
    "name: prefix_test",
    "language: english",
    paste0("lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "n_per_condition: 5",
    "pool_filters: {length: [3, 7], frequency: [3.8, 7]}",
    "conditions:",
    "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
    "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
    "match_on: [length]",
    "font_size: 40"
  ))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)
  # `font_size` is not `font`, so every target keeps the schema's fonts.
  psychopy <- readLines(res$experiments$psychopy, warn = FALSE)
  expect_true('WORD_FONT = "Courier New"' %in% psychopy)
  osexp <- readLines(res$experiments$opensesame, warn = FALSE)
  expect_true("set font_family mono" %in% osexp)
  html <- paste(readLines(res$experiments$jspsych, warn = FALSE), collapse = "\n")
  expect_true(grepl('font-family: "Courier New"', html, fixed = TRUE))
})

test_that("an annotation key does not make a design continuous", {
  out <- tmp_out()
  design <- write_design(out, c(
    "name: annotated_test",
    "language: english",
    paste0("lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "n_per_condition: 5",
    "pool_filters: {length: [3, 7], frequency: [3.8, 7]}",
    "conditions:",
    "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
    "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
    "match_on: [length]",
    "continuous_notes: frequency defines the two conditions"
  ))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)
  stim <- read_csv_utf8(res$stimuli)
  expect_setequal(unique(stim$condition), c("high", "low"))
  expect_equal(as.integer(table(stim$condition)), c(5L, 5L))
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

# Every file under `root`, relative to it, so a refusal can be shown to leave nothing
# behind.
files_under <- function(root) sort(list.files(root, recursive = TRUE, all.files = TRUE))

# Run a design that must be refused, and check that nothing reached outdir.
refused_before_writing <- function(lines, message, schema = extdata("schema.yaml")) {
  dir <- tmp_out()
  design <- write_design(dir, lines)
  outdir <- file.path(dir, "out")
  expect_error(run_quiet(design, schema, outdir = outdir), message, fixed = TRUE)
  expect_identical(files_under(outdir), character(0))
}

corpus_lines <- function(name = "check_test", extra = character(0), n = "5") {
  c(paste0("name: ", name),
    "language: english",
    paste0("lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    paste0("n_per_condition: ", n),
    "pool_filters: {length: [3, 7], frequency: [3.8, 7]}",
    "conditions:",
    "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
    "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
    "match_on: [length]",
    extra)
}

test_that("a_misspelt_design_key_is_refused_with_a_suggestion", {
  # `n_per_conditon: 8` was ignored, so the design silently got the default twenty
  # items per condition. Pinned identically in test_run_pipeline.py.
  lines <- corpus_lines()
  lines <- c(lines[!startsWith(lines, "n_per_condition")], "n_per_conditon: 8")
  refused_before_writing(
    lines, "lexsync: unknown design key 'n_per_conditon' (did you mean 'n_per_condition'?)")
  refused_before_writing(
    corpus_lines(extra = "matching: {methd: joint}"),
    "lexsync: unknown design key 'matching.methd' (did you mean 'matching.method'?)")
})

test_that("an_unknown_design_key_is_reported_in_the_run_log", {
  # A key far from every known one is not refused yet, but the run log says it was
  # ignored. `description` and a key beginning `x_` are annotations and pass quietly.
  # Pinned identically in test_run_pipeline.py.
  out <- tmp_out()
  design <- write_design(out, corpus_lines(extra = c(
    "notes: piloted in May",
    "description: two frequency bands",
    "x_reviewer: second author",
    "conditions_comment: high against low")))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)
  log <- paste(readLines(res$log, encoding = "UTF-8"), collapse = "\n")
  for (key in c("notes", "conditions_comment")) {
    expect_true(grepl(sprintf(paste(
      "lexsync: design key '%s' is not read by lexsync and is ignored; a later",
      "release will refuse it. Put annotations in `description` or a key",
      "beginning `x_`."), key), log, fixed = TRUE), info = key)
  }
  expect_false(grepl("'description'", log, fixed = TRUE))
  expect_false(grepl("x_reviewer", log, fixed = TRUE))
})

test_that("a_whole_float_n_per_condition_is_accepted", {
  # Pinned identically in test_run_pipeline.py, where 4.0 raised a TypeError.
  out <- tmp_out()
  res <- run_quiet(write_design(out, corpus_lines(n = "4.0")), extdata("schema.yaml"),
                   outdir = out)
  stim <- read_csv_utf8(res$stimuli)
  expect_equal(as.integer(table(stim$condition)), c(4L, 4L))
})

test_that("a_whole_float_n_reaches_the_generate_path", {
  out <- tmp_out()
  design <- write_design(out, c(
    "name: float_gen",
    "language: english",
    "paradigm: lexical_decision",
    "items:",
    "  source: generate",
    paste0("  lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "n_per_condition: 4.0",
    "pool_filters: {length: [4, 7], frequency: [3.5, 6.0]}"))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)
  expect_length(unique(read_csv_utf8(res$stimuli)$set), 4L)
})

test_that("a_schema_of_seed_and_lexicon_schema_runs", {
  # Every other schema block has a default, so a schema holding only these two runs.
  # The Python engine raised KeyError 'matching'. Pinned identically in
  # test_run_pipeline.py.
  out <- tmp_out()
  schema <- file.path(out, "schema.yaml")
  writeLines(c("seed: 7", "lexicon_schema:", "  required: [word, freq_zipf]"), schema)
  res <- run_quiet(write_design(out, corpus_lines()), schema, outdir = file.path(out, "out"))
  expect_true(file.exists(res$stimuli))
})

test_that("a_design_without_a_name_is_refused_before_anything_is_written", {
  # This engine wrote four files and then failed with 'argument is of length zero';
  # the Python engine raised a bare KeyError. Pinned identically in
  # test_run_pipeline.py.
  lines <- corpus_lines()
  refused_before_writing(lines[!startsWith(lines, "name:")],
                         "lexsync: the design has no `name`.")
})

test_that("language_tag_does_not_stand_in_for_language", {
  lines <- corpus_lines()
  lines[startsWith(lines, "language:")] <- "language_tag: en-GB"
  refused_before_writing(lines, "lexsync: the design has no `language`.")
})

test_that("a_language_that_yaml_reads_as_a_boolean_is_refused", {
  lines <- corpus_lines()
  lines[startsWith(lines, "language:")] <- "language: no"
  refused_before_writing(lines, paste(
    "lexsync: the design's `language` must be text; quote it if it is a code",
    "such as 'no'."))
})

test_that("an_unsafe_name_is_refused_before_any_file_exists", {
  # The name used to be checked only at export, after the stimuli, both reports and
  # the PsychoPy loop table were on disk.
  refused_before_writing(corpus_lines(name = "\"bad'name\""), "cannot be written safely")
})

test_that("an_unsafe_font_or_port_is_refused_before_any_file_exists", {
  refused_before_writing(corpus_lines(extra = "font: \"Arial'\""), "cannot be written safely")
  dir <- tmp_out()
  schema <- file.path(dir, "schema.yaml")
  text <- readLines(extdata("schema.yaml"), encoding = "UTF-8")
  writeLines(sub("parallel_address: '0x0378'", "parallel_address: 'LPT1'", text,
                 fixed = TRUE), schema, useBytes = TRUE)
  refused_before_writing(corpus_lines(), "must be a port address", schema = schema)
})

test_that("a_bad_response_key_is_refused_before_any_file_exists", {
  refused_before_writing(corpus_lines(extra = c(
    "events:",
    "  - {type: text, content: '{word}', duration_ms: 500, trigger: condition}",
    "  - {type: response, keys: ['a;b']}")), "must be a key name")
})

test_that("a_matched_design_without_match_on_is_refused", {
  # Without match_on this engine paired the byte-first words, and with an empty list
  # both engines did. Pinned identically in test_run_pipeline.py.
  message <- "lexsync: a matched design needs `match_on` naming at least one dimension."
  lines <- corpus_lines()
  lines <- lines[!startsWith(lines, "match_on")]
  refused_before_writing(lines, message)
  refused_before_writing(c(lines, "match_on: []"), message)
})

test_that("a_condition_name_that_is_not_text_is_refused", {
  refused_before_writing(sub("name: high", "name: 1", corpus_lines(), fixed = TRUE),
                         "lexsync: condition names must be text; quote '1'.")
})

test_that("a_non_ascii_name_writes_under_a_checksummed_stem", {
  # Two designs with Chinese names and the language 'chinese' both wrote chinese_*,
  # so the second overwrote the first. Pinned identically in test_run_pipeline.py.
  out <- tmp_out()
  lines <- corpus_lines(name = "\u8bcd\u9891")
  lines[startsWith(lines, "language:")] <- "language: chinese"
  res <- run_quiet(write_design(out, enc2utf8(lines)), extdata("schema.yaml"), outdir = out)
  expect_identical(basename(res$stimuli), "chinese_14aadfa7_stimuli_R.csv")
  expect_identical(basename(res$experiments$opensesame), "chinese_14aadfa7.osexp")
})

test_that("run_all_refuses_designs_that_would_write_the_same_files", {
  # `en-lexdec` and `en_lexdec` slugify alike, so the second design overwrote the
  # first's files. Pinned identically in test_run_pipeline.py.
  dir <- tmp_out()
  cfg <- file.path(dir, "config")
  dir.create(cfg)
  writeLines(corpus_lines(name = "en-lexdec"), file.path(cfg, "design_a.yaml"))
  writeLines(corpus_lines(name = "en_lexdec"), file.path(cfg, "design_b.yaml"))
  outdir <- file.path(dir, "out")
  expect_error(run_all(cfg, extdata("schema.yaml"), outdir, verbose = FALSE),
               paste("lexsync: 'design_a.yaml' and 'design_b.yaml' would write the same",
                     "files ('en_lexdec_english'); give the designs distinct names."),
               fixed = TRUE)
  expect_identical(files_under(outdir), character(0))
})

# ---- Derived dimensions (n_density, old20, bigram_freq) ---------------------------
# lexsync derived these only for dimensions named in match_on, and checked pool_filters
# against the lexicon before deriving anything, so a design that manipulated, filtered
# on or regressed on a derived dimension stopped with "absent from the pool". Each test
# below is pinned identically in test_run_pipeline.py.

read_datasheet <- function(out, stem) {
  jsonlite::fromJSON(file.path(out, "reports", paste0(stem, "_datasheet_R.json")),
                     simplifyVector = FALSE)
}

read_log <- function(res) paste(readLines(res$log, encoding = "UTF-8"), collapse = "\n")

# A copy of a bundled lexicon without the named columns, as `lexsync fetch` writes one
# (word, freq_zipf, language, source).
lexicon_without <- function(out, source, drop, name = "lexicon.csv") {
  lex <- read_csv_utf8(extdata(source))
  lex <- lex[, setdiff(names(lex), drop), drop = FALSE]
  path <- file.path(out, name)
  write_csv_utf8(lex, path)
  path
}

test_that("a_bigram_contrast_runs_on_a_lexicon_without_bigram_freq", {
  out <- tmp_out()
  design <- write_design(out, c(
    "name: bigram_contrast",
    "language: english",
    paste0("lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "n_per_condition: 5",
    "pool_filters: {length: [4, 7], frequency: [3.8, 7]}",
    "conditions:",
    "  - {name: high_bigram, define_by: {bigram_freq: [0.009, 1]}}",
    "  - {name: low_bigram, define_by: {bigram_freq: [0, 0.004]}}",
    "match_on: [length, frequency]"
  ))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)
  stim <- read_csv_utf8(res$stimuli)
  expect_equal(as.integer(table(stim$condition)), c(5L, 5L))
  expect_true(all(stim$bigram_freq[stim$condition == "high_bigram"] >= 0.009))
  expect_true(all(stim$bigram_freq[stim$condition == "low_bigram"] <= 0.004))
})

test_that("a_continuous_design_can_take_bigram_freq_as_its_predictor", {
  out <- tmp_out()
  design <- write_design(out, c(
    "name: bigram_continuous",
    "language: english",
    paste0("lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "n_per_condition: 10",
    "pool_filters: {length: [4, 7], frequency: [3.8, 7]}",
    "continuous:",
    "  predictor: bigram_freq",
    "  controls: [length]",
    "match_on: [length]"
  ))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)
  stim <- read_csv_utf8(res$stimuli)
  expect_identical(length(unique(stim$set)), 10L)
  expect_false(anyNA(stim$bigram_freq))
})

test_that("a_pool_filter_on_bigram_freq_runs", {
  out <- tmp_out()
  design <- write_design(out, c(
    "name: bigram_filter",
    "language: english",
    paste0("lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "n_per_condition: 5",
    "pool_filters: {length: [3, 7], frequency: [3.8, 7], bigram_freq: [0.005, 0.02]}",
    "conditions:",
    "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
    "  - {name: low, define_by: {frequency: [3.8, 4.4]}}",
    "match_on: [length]"
  ))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)
  stim <- read_csv_utf8(res$stimuli)
  expect_identical(nrow(stim), 10L)
  expect_true(all(stim$bigram_freq >= 0.005 & stim$bigram_freq <= 0.02))
})

test_that("an_ndensity_design_runs_on_a_lexicon_without_n_and_old20", {
  # design_es_ndensity on a lexicon such as `lexsync fetch es` writes. The measures
  # are computed against the whole lexicon, not against the filtered pool.
  out <- tmp_out()
  lexicon <- lexicon_without(out, "es_example.csv", c("n_density", "old20"))
  design <- write_design(out, c(
    "name: fetched_ndensity",
    "language: spanish",
    paste0("lexicon: ", as_yaml_path(lexicon)),
    "n_per_condition: 5",
    "pool_filters: {length: [3, 6], frequency: [3.8, 7.0]}",
    "conditions:",
    "  - {name: dense_neighbourhood, define_by: {n_density: [3, 100]}}",
    "  - {name: sparse_neighbourhood, define_by: {n_density: [0, 1]}}",
    "match_on: [length, frequency]",
    "matching: {method: joint}"
  ))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)
  stim <- read_csv_utf8(res$stimuli)
  expect_equal(as.integer(table(stim$condition)), c(5L, 5L))
  expect_true(all(stim$n_density[stim$condition == "dense_neighbourhood"] >= 3))
  want <- add_neighbourhood(stim[, "word", drop = FALSE],
                            reference = read_csv_utf8(lexicon)$word)
  expect_identical(as.integer(stim$n_density), as.integer(want$n_density))
  expect_identical(stim$old20, want$old20)
})

test_that("reference_words_recomputes_n_and_old20_and_is_recorded", {
  # Every bundled lexicon carries n_density and old20, so the override was ignored
  # while the datasheet recorded it as applied.
  out <- tmp_out()
  design <- write_design(out, corpus_lines(name = "guard_test"))
  res <- run_pipeline(design, extdata("schema.yaml"), outdir = out,
                      reference_words = c("zzzz", "qqqq"), verbose = FALSE)
  stim <- read_csv_utf8(res$stimuli)
  want <- add_neighbourhood(stim[, "word", drop = FALSE], reference = c("zzzz", "qqqq"))
  expect_true(all(stim$n_density == 0))
  expect_identical(stim$old20, want$old20)
  nref <- read_datasheet(out, "guard_test_english")$selection$neighbourhood_reference
  expect_identical(unlist(nref$applied_to), c("n_density", "old20"))
  expect_identical(as.integer(nref$n_words), 2L)
  expect_identical(nref$source, "user-supplied")
  expect_true(grepl("recomputed n_density, old20 against a supplied reference of 2 words",
                    read_log(res), fixed = TRUE))
})

test_that("reference_words_recomputes_bigram_freq_when_the_design_uses_it", {
  out <- tmp_out()
  lines <- corpus_lines(name = "guard_test")
  lines[startsWith(lines, "match_on")] <- "match_on: [length, bigram_freq]"
  res <- run_pipeline(write_design(out, lines), extdata("schema.yaml"), outdir = out,
                      reference_words = c("zzzz", "qqqq"), verbose = FALSE)
  nref <- read_datasheet(out, "guard_test_english")$selection$neighbourhood_reference
  expect_identical(unlist(nref$applied_to), c("n_density", "old20", "bigram_freq"))
  expect_true(grepl(paste("recomputed n_density, old20, bigram_freq against a supplied",
                          "reference of 2 words"), read_log(res), fixed = TRUE))
})

test_that("reference_words_on_a_generate_design_is_ignored_and_not_recorded", {
  out <- tmp_out()
  design <- write_design(out, c(
    "name: gen_ref",
    "language: english",
    "paradigm: lexical_decision",
    "items:",
    "  source: generate",
    paste0("  lexicon: ", as_yaml_path(extdata("en_example.csv"))),
    "n_per_condition: 5",
    "pool_filters: {length: [4, 7], frequency: [3.5, 6.0]}"
  ))
  res <- run_pipeline(design, extdata("schema.yaml"), outdir = out,
                      reference_words = c("zzzz", "qqqq"), verbose = FALSE)
  expect_false("neighbourhood_reference" %in%
                 names(read_datasheet(out, "gen_ref_english")$selection))
  expect_true(grepl("reference_words is not used by items.source 'generate' and was ignored",
                    read_log(res), fixed = TRUE))
})

test_that("reference_words_must_hold_a_word_and_no_missing_value", {
  # Once the override took effect, an empty list set every N to 0 and every OLD20 to
  # missing, and the selection went ahead on those values.
  for (words in list(character(0), c("zzzz", NA))) {
    out <- tmp_out()
    design <- write_design(out, corpus_lines(name = "guard_test"))
    expect_error(run_pipeline(design, extdata("schema.yaml"), outdir = out,
                              reference_words = words, verbose = FALSE),
                 "lexsync: reference_words must hold at least one word and no missing value.",
                 fixed = TRUE)
    expect_false(dir.exists(file.path(out, "reports")))
  }
})

test_that("a_lone_reference_word_is_one_word", {
  # A character scalar is one word here. The Python twin reads a string the same way
  # and does not split it into its letters.
  out <- tmp_out()
  design <- write_design(out, corpus_lines(name = "guard_test"))
  res <- run_pipeline(design, extdata("schema.yaml"), outdir = out,
                      reference_words = "zzzz", verbose = FALSE)
  nref <- read_datasheet(out, "guard_test_english")$selection$neighbourhood_reference
  expect_identical(as.integer(nref$n_words), 1L)
  stim <- read_csv_utf8(res$stimuli)
  want <- add_neighbourhood(stim[, "word", drop = FALSE], reference = "zzzz")
  expect_identical(stim$old20, want$old20)
})

test_that("a_reference_member_column_sets_the_neighbourhood_reference", {
  # A lexicon may mark the forms that make up the neighbourhood reference. The
  # measures it lacks are then computed against those rows alone.
  out <- tmp_out()
  lexicon <- file.path(out, "lexicon.csv")
  writeLines(c("word,freq_zipf,reference_member", "cat,5.0,1", "cot,4.0,1", "cut,4.1,1",
               "cap,4.2,0", "car,5.1,0", "dog,5.2,1", "dig,4.3,1", "dug,4.0,0"), lexicon)
  design <- write_design(out, c(
    "name: member_ref",
    "language: english",
    paste0("lexicon: ", as_yaml_path(lexicon)),
    "n_per_condition: 3",
    "conditions:",
    "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
    "  - {name: low, define_by: {frequency: [3.0, 4.5]}}",
    "match_on: [length, n_density]"
  ))
  res <- run_quiet(design, extdata("schema.yaml"), outdir = out)
  stim <- read_csv_utf8(res$stimuli)
  # Against the members cat, cot, cut, dog and dig: cat neighbours cot and cut but
  # not the non-members cap and car, and car and dog have one member neighbour each.
  expect_identical(as.integer(stim$n_density[match(c("cat", "car", "dog"), stim$word)]),
                   c(2L, 1L, 1L))
})

# ---- n_syllables outside Latin script (twinned with test_run_pipeline.py) -------
# count_syllables() returned 0 for every Chinese, Russian or Greek word, so a design
# could match on n_syllables and report perfect balance. It now gives NA there, and
# a design that refers to the dimension while the pool holds such words is refused
# before anything is written.

syllables_refused <- function(n) {
  sprintf(paste("lexsync: n_syllables is not available for %d word(s) in the pool: it",
                "counts Latin vowel letters, so it is undefined for other scripts. Remove",
                "it from the design or filter those words out."), n)
}

zh_lines <- function(extra) {
  c("name: zh_syllables",
    "language: chinese",
    paste0("lexicon: ", as_yaml_path(extdata("zh_example.csv"))),
    "n_per_condition: 5",
    "conditions:",
    "  - {name: high, define_by: {frequency: [5.0, 7.0]}}",
    "  - {name: low, define_by: {frequency: [3.5, 4.2]}}",
    extra)
}

test_that("a design matching on n_syllables over Chinese is refused", {
  refused_before_writing(zh_lines("match_on: [length, n_syllables]"), syllables_refused(3000))
})

test_that("a filter on n_syllables over Chinese is refused, not emptied", {
  # A filter drops the rows missing its column, so without the check this design
  # went on with an empty pool and failed far from the cause.
  refused_before_writing(zh_lines(c("pool_filters: {n_syllables: [1, 3]}",
                                    "match_on: [length]")),
                         syllables_refused(3000))
})

test_that("a Chinese design without n_syllables leaves the column empty", {
  out <- tmp_out()
  res <- run_quiet(write_design(out, zh_lines("match_on: [length]")),
                   extdata("schema.yaml"), outdir = out)
  stim <- read_csv_utf8(res$stimuli)
  expect_true(all(is.na(stim$n_syllables)))
})

test_that("n_syllables is checked on the filtered pool", {
  # A Cyrillic word that the design's other filters remove does not count against
  # it; one they keep does.
  for (freq in c("2.0", "5.0")) {
    dir <- tmp_out()
    lexicon <- file.path(dir, "lexicon.csv")
    text <- readLines(extdata("en_example.csv"), encoding = "UTF-8")
    row <- paste0("\u043c\u043e\u043b\u043e\u043a\u043e,", freq, ",en,test,0,1.0")
    writeLines(enc2utf8(c(text, row)), lexicon, useBytes = TRUE)
    lines <- sub(as_yaml_path(extdata("en_example.csv")), as_yaml_path(lexicon),
                 corpus_lines(name = "mixed_syllables"), fixed = TRUE)
    lines[startsWith(lines, "match_on")] <- "match_on: [length, n_syllables]"
    if (freq == "5.0") {
      refused_before_writing(lines, syllables_refused(1))
    } else {
      expect_no_error(run_quiet(write_design(dir, lines), extdata("schema.yaml"),
                                outdir = dir))
    }
  }
})
