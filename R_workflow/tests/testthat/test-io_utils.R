# The Python engine pins LF to match readr's always-LF output; test_io_utils.py
# pins these same bytes and this same digest.
expected_bytes <- charToRaw("word,condition\ncat,high\ndog,low\n")
expected_sha256 <- "8084f4888fa65455ee56e7eca2954b07b114f5b962bb78c6e8c73c9928e66ad5"

make_frame <- function() {
  data.frame(
    word = c("cat", "dog"), condition = c("high", "low"),
    stringsAsFactors = FALSE
  )
}

test_that("write_csv_utf8 pins LF on every platform", {
  path <- file.path(tempfile("lexsync"), "s.csv")
  write_csv_utf8(make_frame(), path)
  expect_identical(readBin(path, "raw", file.size(path)), expected_bytes)
})

test_that("write_csv_utf8 digest is platform-independent", {
  # The datasheet advertises this digest as provenance, so it must be fixed by
  # the content alone -- not by the line terminator of the host platform.
  path <- file.path(tempfile("lexsync"), "s.csv")
  write_csv_utf8(make_frame(), path)
  expect_identical(sha256_file(path), expected_sha256)
})

test_that("write_csv_utf8 round-trips through read_csv_utf8", {
  path <- file.path(tempfile("lexsync"), "nested", "s.csv")
  write_csv_utf8(make_frame(), path)
  expect_equal(as.data.frame(read_csv_utf8(path)), make_frame())
})

# Every artefact-writing path must pin LF, not just the CSV one. write_datasheet and
# write_run_log used bare writeLines(), whose connection is opened in TEXT mode, so on
# Windows all three of their outputs came out CRLF while the Python engine's twins were
# LF: measured 109 CRLF against 0 in one datasheet. The datasheet is the provenance
# artefact of the whole package, so its bytes are the last that should depend on which
# machine happened to build it. The .jsonl run log was already binary and is included
# here so the whole set is covered by one assertion.
test_that("the datasheet and run log pin LF like every other artefact", {
  dir <- tempfile("lf"); dir.create(dir)
  # Fixtures are local: testthat runs each file in its own environment, so the ones in
  # test-datasheet.R are not in scope here.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- data.frame(word = c("cat", "dog"), condition = c("hi", "lo"), set = c(1, 1),
                     length = 3L, frequency = c(6, 3), stringsAsFactors = FALSE)
  design <- list(name = "lf", language = "english", match_on = list("length"),
                 n_per_condition = 1L, counterbalance = list(lists = 1))
  ds <- build_datasheet(design, schema, NULL, stim, "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  paths <- write_datasheet(ds, file.path(dir, "d.json"), file.path(dir, "d.md"))

  log <- new_run_log("lf", meta = list(design = "lf"))
  log <- log_step(log, "a step", list(n = 1L))
  write_run_log(log, file.path(dir, "log.md"), file.path(dir, "log.jsonl"))

  for (p in c(paths, file.path(dir, c("log.md", "log.jsonl")))) {
    raw <- readBin(p, "raw", file.size(p))
    expect_false(as.raw(13) %in% raw, info = basename(p))
    expect_true(as.raw(10) %in% raw, info = basename(p))
  }
})

test_that("clean_field rejects control characters but allows commas and quotes", {
  expect_error(clean_field("cat\ndog", "word"), "control characters")
  expect_identical(clean_field('the "big" cat, asleep', "word"), 'the "big" cat, asleep')
})

test_that("slugify is lower-case and path-safe", {
  expect_identical(slugify("En Lexdec", "English!"), "en_lexdec_english")
})

# Pins the same contract as test_slugify_is_locale_invariant in the Python
# engine's test_io_utils.py. Every artifact path in both engines is built from
# slugify(), so a locale-sensitive fold would write this design's files under a
# name the Python engine never produces. Base `tolower()` maps "I" to the
# dotless "i" under a Turkish or Azeri locale, taking the slug out of ASCII --
# and it does so after the reduction to [A-Za-z0-9_], which is why that
# reduction does not make the fold safe by itself.
test_that("slugify folds case whatever the locale", {
  expect_identical(slugify("STUDY_I"), "study_i")

  old <- Sys.getlocale("LC_CTYPE")
  turkish <- suppressWarnings(Sys.setlocale("LC_CTYPE", "Turkish"))
  skip_if(!nzchar(turkish), "cannot switch to a Turkish locale on this platform")
  on.exit(Sys.setlocale("LC_CTYPE", old), add = TRUE)
  expect_identical(slugify("STUDY_I"), "study_i")
  expect_identical(slugify("En Lexdec", "English!"), "en_lexdec_english")
})
