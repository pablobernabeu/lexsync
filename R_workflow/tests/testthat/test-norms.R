# The design's `norms:` block: a semantic dimension joined before the pool is built.
#
# The join itself is merge_norms, tested in test-dimensions.R. What is tested here is
# the part that makes it usable and honest: the orchestrator applies the block before
# build_pool, so a norm column can be filtered on, matched on and spanned; and every
# table it joined is recorded in the materials datasheet with its checksum and its
# per-column coverage.
#
# That record is not decoration. A norm table can supply the very variable a design
# manipulates, so a run whose datasheet did not name the file would describe a
# selection over columns of unstated origin -- unreproducible from the record that
# exists to make it reproducible. Coverage is recorded for the same reason: a word the
# table does not cover gets an NA, which takes it out of any selection that filters,
# matches or spans on the column.
#
# No norm data is bundled. These tests write their own tiny lexicon and norm table, so
# the feature is covered end to end without shipping a norm dataset.
#
# python_workflow/tests/test_norms.py asserts the same properties.

NORM_WORDS <- c("cat", "dog", "car", "cap", "bat", "bag", "cot", "cog", "rat", "rag",
                "hat", "hag", "pot", "peg", "man", "map")

norm_schema <- function() {
  yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
}

# A tiny lexicon. `upper` writes the forms in capitals, which load_lexicon folds.
norm_lexicon <- function(dir, upper = FALSE) {
  path <- file.path(dir, "lex.csv")
  lexsync:::write_csv_utf8(
    data.frame(word = if (upper) toupper(NORM_WORDS) else NORM_WORDS,
               freq_zipf = 3.0 + 0.2 * seq_along(NORM_WORDS) - 0.2,
               stringsAsFactors = FALSE), path)
  path
}

# A norm table covering `covered` of the lexicon (all of it by default).
norm_table <- function(dir, covered = NULL, name = "conc.csv") {
  words <- if (is.null(covered)) NORM_WORDS else NORM_WORDS[seq_len(covered)]
  path <- file.path(dir, name)
  lexsync:::write_csv_utf8(
    # Deliberately not monotonic in frequency, so a filter on concreteness selects a
    # set that a filter on frequency could not have produced by accident.
    data.frame(word = words,
               concreteness = 2.0 + ((seq_along(words) - 1L) %% 4L),
               stringsAsFactors = FALSE), path)
  path
}

test_that(".apply_norms joins and records provenance", {
  dir <- tempfile("norms"); dir.create(dir)
  schema <- norm_schema()
  lex <- load_lexicon(norm_lexicon(dir), schema)
  path <- norm_table(dir)
  out <- lexsync:::.apply_norms(lex, list(norms = list(list(path = path))))
  expect_true("concreteness" %in% names(out$lexicon))
  rec <- out$provenance[[1]]
  expect_identical(rec$path, path)
  expect_identical(nchar(rec$sha256), 64L)
  expect_identical(rec$on, "word")
  expect_identical(rec$columns,
                   list(list(column = "concreteness", n_matched = length(NORM_WORDS),
                             n_total = length(NORM_WORDS))))
})

test_that(".apply_norms records partial coverage", {
  # The uncovered rows carry NA, which the tolerance windows drop from the pool, so
  # coverage is part of how the pool was defined and belongs in the record.
  dir <- tempfile("norms"); dir.create(dir)
  schema <- norm_schema()
  lex <- load_lexicon(norm_lexicon(dir), schema)
  out <- lexsync:::.apply_norms(
    lex, list(norms = list(list(path = norm_table(dir, covered = 10)))))
  expect_identical(out$provenance[[1]]$columns[[1]],
                   list(column = "concreteness", n_matched = 10L,
                        n_total = length(NORM_WORDS)))
})

test_that(".apply_norms accepts a single bare mapping", {
  # Writing one table as a bare mapping rather than a one-element list is the obvious
  # thing to do in YAML, so it must not be silently ignored.
  dir <- tempfile("norms"); dir.create(dir)
  lex <- load_lexicon(norm_lexicon(dir), norm_schema())
  out <- lexsync:::.apply_norms(lex, list(norms = list(path = norm_table(dir))))
  expect_true("concreteness" %in% names(out$lexicon))
  expect_length(out$provenance, 1L)
})

test_that(".apply_norms is a no-op without the block", {
  # Every shipped design lacks a `norms:` block, so this path must not touch the
  # lexicon at all -- otherwise adding the feature would move existing artefacts.
  dir <- tempfile("norms"); dir.create(dir)
  lex <- load_lexicon(norm_lexicon(dir), norm_schema())
  out <- lexsync:::.apply_norms(lex, list(name = "x"))
  expect_length(out$provenance, 0L)
  expect_identical(out$lexicon, lex)
})

test_that(".apply_norms rejects a traversing path or a missing one", {
  dir <- tempfile("norms"); dir.create(dir)
  lex <- load_lexicon(norm_lexicon(dir), norm_schema())
  expect_error(lexsync:::.apply_norms(lex, list(norms = list(list(path = "../secrets/x.csv")))),
               "must not contain '..'", fixed = TRUE)
  expect_error(lexsync:::.apply_norms(lex, list(norms = list(list(columns = list("concreteness"))))),
               "needs a `path`", fixed = TRUE)
})

test_that(".apply_norms folds the lexicon key", {
  # load_lexicon case-folds `word`, so an upper-case source still joins. This is the
  # regression guard for the half-folded key: only the norm table's side used to be
  # normalised, and both engines then agreed on an all-NA dimension.
  dir <- tempfile("norms"); dir.create(dir)
  lex <- load_lexicon(norm_lexicon(dir, upper = TRUE), norm_schema())
  out <- lexsync:::.apply_norms(lex, list(norms = list(list(path = norm_table(dir)))))
  expect_false(any(is.na(out$lexicon$concreteness)))
})

# ---- The join key of a norms entry --------------------------------------------
# YAML 1.1 reads a bare `on` as the boolean true in both engines, so the documented
# `on: lemma` reached the join as a key named TRUE (True in Python) and every join
# silently used `word`. The key is now written `join_on`. These tests write their
# entries as YAML and read them with read_config(), as run_pipeline() does, because the
# defect lived in the reading.

ON_NOTE <- paste("lexsync: read `on:` in a norms entry as the join key; YAML reads a bare",
                 "`on` as true, so write `join_on:`.")
FORMS <- c("cat", "cats", "dog", "dogs", "mice", "mouse")
LEMMAS <- c("cat", "cat", "dog", "dog", "mouse", "mouse")
BY_LEMMA <- c(4.9, 4.9, 4.8, 4.8, 4.7, 4.7)

# Word forms with their lemmas, in byte order, so the lexicon keeps this order.
lemma_lexicon <- function(dir) {
  path <- file.path(dir, "lemma_lex.csv")
  lexsync:::write_csv_utf8(
    data.frame(word = FORMS, freq_zipf = 4.0 + 0.1 * (seq_along(FORMS) - 1L), lemma = LEMMAS,
               stringsAsFactors = FALSE), path)
  path
}

# A lemma-level norm table. With `with_word`, it also lists each lemma's citation form
# under `word`. A join on `word` then matches only the forms that are their own lemma,
# so the key a join used can be read off its coverage.
lemma_norms <- function(dir, with_word = TRUE) {
  path <- file.path(dir, "lemma_norms.csv")
  table <- data.frame(lemma = c("cat", "dog", "mouse"), concreteness = c(4.9, 4.8, 4.7),
                      stringsAsFactors = FALSE)
  if (with_word) table <- cbind(data.frame(word = table$lemma, stringsAsFactors = FALSE), table)
  lexsync:::write_csv_utf8(table, path)
  path
}

# A design whose single norms entry is the YAML mapping `{path: ..., <entry>}`.
norms_entry <- function(dir, entry, norms_path) {
  path <- file.path(dir, "norms_entry.yaml")
  writeLines(c("norms:", sprintf("  - {path: %s, %s}", gsub("\\\\", "/", norms_path), entry)),
             path)
  read_config(path)
}

test_that("a_bare_on_key_is_read_as_the_join_key", {
  # Pinned identically in test_norms.py.
  dir <- tempfile("norms"); dir.create(dir)
  lex <- load_lexicon(lemma_lexicon(dir), norm_schema())
  design <- norms_entry(dir, "on: lemma, columns: [concreteness]", lemma_norms(dir))
  out <- lexsync:::.apply_norms(lex, design)
  expect_equal(out$lexicon$concreteness, BY_LEMMA)
  expect_identical(out$provenance[[1]]$on, "lemma")
  expect_identical(out$notes, ON_NOTE)
})

test_that("join_on_names_the_join_key_and_wins_over_on", {
  # `join_on` joins with no note, and so does a quoted 'on'. Given both, `join_on` wins.
  # Without either, the join uses `word`, which covers only the forms that are their
  # own lemma. Pinned identically in test_norms.py.
  dir <- tempfile("norms"); dir.create(dir)
  lex <- load_lexicon(lemma_lexicon(dir), norm_schema())
  norms_path <- lemma_norms(dir)
  for (entry in c("join_on: lemma", "'on': lemma", "join_on: lemma, on: word",
                  "join_on: lemma, 'on': word")) {
    out <- lexsync:::.apply_norms(
      lex, norms_entry(dir, paste0(entry, ", columns: [concreteness]"), norms_path))
    expect_equal(out$lexicon$concreteness, BY_LEMMA, info = entry)
    expect_identical(out$provenance[[1]]$on, "lemma", info = entry)
    expect_identical(out$notes, character(0), info = entry)
  }
  out <- lexsync:::.apply_norms(lex, norms_entry(dir, "columns: [concreteness]", norms_path))
  expect_equal(out$lexicon$concreteness, c(4.9, NA, 4.8, NA, NA, 4.7))
  expect_identical(out$provenance[[1]]$on, "word")
})

test_that("an_unknown_key_in_a_norms_entry_is_refused", {
  # A misspelt `join_on` fell back to `word` as silently as the bare `on` did. A key
  # YAML reads as false is named as this engine names it. Pinned identically in
  # test_norms.py.
  dir <- tempfile("norms"); dir.create(dir)
  lex <- load_lexicon(lemma_lexicon(dir), norm_schema())
  norms_path <- lemma_norms(dir)
  for (case in list(c("joinon: lemma", "joinon"), c("off: lemma", "FALSE"))) {
    expect_error(lexsync:::.apply_norms(lex, norms_entry(dir, case[1], norms_path)),
                 sprintf(paste("lexsync: unknown key '%s' in a norms entry; known keys:",
                               "path, join_on, columns."), case[2]), fixed = TRUE)
  }
  # A single entry written as a bare mapping is checked in the same way. This engine
  # took a bare mapping without `path` for a list of entries, so it reported the
  # missing path where the Python engine named the misspelt key.
  bare <- file.path(dir, "bare_entry.yaml")
  writeLines("norms: {joinon: lemma, columns: [concreteness]}", bare)
  expect_error(lexsync:::.apply_norms(lex, read_config(bare)),
               paste("lexsync: unknown key 'joinon' in a norms entry; known keys: path,",
                     "join_on, columns."), fixed = TRUE)
  # A mapping of named entries is checked as one entry whose keys are the names. This
  # engine joined each entry, and the Python engine refused the block.
  writeLines(c("norms:", sprintf("  conc: {path: %s}", gsub("\\\\", "/", norms_path))), bare)
  expect_error(lexsync:::.apply_norms(lex, read_config(bare)),
               paste("lexsync: unknown key 'conc' in a norms entry; known keys: path,",
                     "join_on, columns."), fixed = TRUE)
  # An empty mapping holds no entry at all, in both engines.
  writeLines("norms: {}", bare)
  expect_identical(lexsync:::.apply_norms(lex, read_config(bare))$provenance, list())
  # An entry that is not a mapping has no path to read.
  expect_error(lexsync:::.apply_norms(lex, list(norms = list(norms_path))),
               "lexsync: every entry under `norms:` needs a `path`.", fixed = TRUE)
})

test_that("the_pipeline_joins_on_a_bare_on_and_notes_it", {
  # End to end, from a hand-written design: the table has no `word` column, so the join
  # on `word` that the bare `on` used to give stopped the run. Pinned identically in
  # test_norms.py.
  dir <- tempfile("norms"); dir.create(dir)
  lexicon <- file.path(dir, "lex_lemma.csv")
  lexsync:::write_csv_utf8(
    data.frame(word = NORM_WORDS, freq_zipf = 3.0 + 0.2 * (seq_along(NORM_WORDS) - 1L),
               lemma = NORM_WORDS, stringsAsFactors = FALSE), lexicon)
  norms_path <- file.path(dir, "conc_lemma.csv")
  lexsync:::write_csv_utf8(
    data.frame(lemma = NORM_WORDS, concreteness = 2.0 + ((seq_along(NORM_WORDS) - 1L) %% 4L),
               stringsAsFactors = FALSE), norms_path)
  design_path <- file.path(dir, "design_lemmatest.yaml")
  writeLines(c(
    "name: lemmatest",
    "language: english",
    paste0("lexicon: ", gsub("\\\\", "/", lexicon)),
    "n_per_condition: 3",
    "norms:",
    paste0("  - path: ", gsub("\\\\", "/", norms_path)),
    "    on: lemma",
    "    columns: [concreteness]",
    "conditions:",
    "  - {name: high, define_by: {frequency: [4.2, 7.0]}}",
    "  - {name: low, define_by: {frequency: [3.0, 3.8]}}",
    "match_on: [length, concreteness]"), design_path)
  outdir <- file.path(dir, "out")
  run_pipeline(design_path, system.file("extdata", "schema.yaml", package = "lexsync"),
               outdir, verbose = FALSE)
  stim <- as.data.frame(lexsync:::read_csv_utf8(
    file.path(outdir, "stimuli", "lemmatest_english_stimuli_R.csv")))
  expect_false(any(is.na(stim$concreteness)))
  ds <- jsonlite::fromJSON(file.path(outdir, "reports", "lemmatest_english_datasheet_R.json"),
                           simplifyVector = FALSE)
  expect_identical(ds$materials_source$norms[[1]]$on, "lemma")
  log <- readLines(file.path(outdir, "reports", "lemmatest_english_run_log_R.jsonl"),
                   encoding = "UTF-8", warn = FALSE)
  messages <- vapply(log, function(line) jsonlite::fromJSON(line)$message, character(1),
                     USE.NAMES = FALSE)
  expect_true(ON_NOTE %in% messages)
})

# End to end: the block is applied before the pool, so a norm column is matchable.
# This is what the wiring buys. Before it, merge_norms existed but nothing called it,
# so a semantic dimension could not reach `match_on` at all.
test_that("the pipeline matches on a norm column and records it", {
  dir <- tempfile("norms"); dir.create(dir)
  lexicon <- norm_lexicon(dir)
  norms_path <- norm_table(dir)
  design <- list(
    name = "normtest", language = "english", lexicon = lexicon,
    description = "A design whose control dimension comes from a norm table.",
    n_per_condition = 3L,
    norms = list(list(path = norms_path, columns = list("concreteness"))),
    pool_filters = list(concreteness = c(2.0, 5.0)),
    conditions = list(list(name = "high", define_by = list(frequency = c(4.2, 7.0))),
                      list(name = "low", define_by = list(frequency = c(3.0, 3.8)))),
    match_on = list("length", "concreteness"),
    counterbalance = list(lists = 1L),
    timing = list(fixation_ms = 500L, word_ms = 500L, isi_ms = 250L))
  design_path <- file.path(dir, "design_normtest.yaml")
  yaml::write_yaml(design, design_path)

  outdir <- file.path(dir, "out")
  run_pipeline(design_path, system.file("extdata", "schema.yaml", package = "lexsync"),
               outdir, verbose = FALSE)

  stim <- as.data.frame(lexsync:::read_csv_utf8(
    file.path(outdir, "stimuli", "normtest_english_stimuli_R.csv")))
  # The norm column reached the stimuli table, and the pool filter held.
  expect_true("concreteness" %in% names(stim))
  expect_false(any(is.na(stim$concreteness)))
  expect_true(all(stim$concreteness >= 2.0 & stim$concreteness <= 5.0))

  ds <- jsonlite::fromJSON(file.path(outdir, "reports", "normtest_english_datasheet_R.json"),
                           simplifyVector = FALSE)
  recorded <- ds$materials_source$norms
  expect_length(recorded, 1L)
  expect_identical(recorded[[1]]$path, norms_path)
  expect_identical(recorded[[1]]$columns[[1]]$column, "concreteness")
  # The matched dimension is named as controlled, and the norm file is named in the
  # Methods prose a user pastes into a paper.
  expect_true("concreteness" %in% unlist(ds$selection$match_on))
  md <- paste(readLines(file.path(outdir, "reports", "normtest_english_datasheet_R.md"),
                        warn = FALSE), collapse = "\n")
  expect_true(grepl("## Joined norms", md, fixed = TRUE))
  expect_true(grepl("Norm dimensions were joined from conc.csv", md, fixed = TRUE))
})
