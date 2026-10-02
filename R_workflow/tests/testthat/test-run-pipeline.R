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
