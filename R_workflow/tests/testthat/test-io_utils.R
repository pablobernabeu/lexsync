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
