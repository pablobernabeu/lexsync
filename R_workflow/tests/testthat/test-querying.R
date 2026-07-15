test_that("load_lexicon validates and computes basic dimensions", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  path <- system.file("extdata", "en_example.csv", package = "lexsync")
  lex <- load_lexicon(path, schema, language = "english")
  expect_true(all(c("word", "freq_zipf", "length", "frequency", "id") %in% names(lex)))
  expect_equal(lex$length, nchar(lex$word))
  expect_false(any(duplicated(lex$word)))
})

test_that("add_neighbourhood computes Coltheart's N and OLD20", {
  df <- data.frame(word = c("cat", "car", "cap", "dog"), stringsAsFactors = FALSE)
  out <- add_neighbourhood(df, reference = df$word, n_old = 2)
  # 'cat' differs from 'car' and 'cap' by a single substitution -> N = 2
  expect_equal(out$n_density[out$word == "cat"], 2L)
  expect_true(all(out$old20 > 0))
})

test_that("build_pool filters by numeric range and membership", {
  df <- data.frame(word = letters[1:5], frequency = 1:5, pos = "n", stringsAsFactors = FALSE)
  expect_equal(nrow(build_pool(df, list(frequency = c(2, 4)))), 3)
  expect_equal(nrow(build_pool(df, list(pos = "n"))), 5)
})

# Pins the same contract as test_load_lexicon_drops_missing_words in the Python
# engine's test_querying.py: a missing word must be dropped, not coerced to a
# word-like string, or the two engines' ids diverge from this row on.
test_that("load_lexicon drops rows whose word is missing", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  path <- tempfile(fileext = ".csv")
  on.exit(unlink(path), add = TRUE)
  writeLines(c("word,freq_zipf", "cat,5.0", ",4.0", "dog,3.0", "NA,2.0", "cow,1.0"), path)
  lex <- load_lexicon(path, schema)
  expect_identical(lex$word, c("cat", "cow", "dog"))
  expect_identical(lex$id, 1:3)
})

test_that(".lower_invariant reproduces Unicode default casing whatever the locale", {
  # Written as code points so the source stays ASCII (CRAN), and so the expected
  # Greek final sigma (U+03C2) and dotted-I expansion are unambiguous.
  upper <- c(intToUtf8(c(0xC1, 0x52, 0x42, 0x4F, 0x4C)),   # ARBOL, A acute
             intToUtf8(c(0x39F, 0x394, 0x39F, 0x3A3)),     # ODOS, Greek
             intToUtf8(0x130))                             # I with dot above
  lower <- c(intToUtf8(c(0xE1, 0x72, 0x62, 0x6F, 0x6C)),
             intToUtf8(c(0x3BF, 0x3B4, 0x3BF, 0x3C2)),
             intToUtf8(c(0x69, 0x307)))
  expect_identical(.lower_invariant(upper), lower)
  expect_identical(.lower_invariant(NA_character_), NA_character_)

  old <- Sys.getlocale("LC_CTYPE")
  skip_if(!isTRUE(suppressWarnings(Sys.setlocale("LC_CTYPE", "C")) == "C"),
          "cannot switch to the C locale on this platform")
  on.exit(Sys.setlocale("LC_CTYPE", old), add = TRUE)
  expect_identical(.lower_invariant(upper), lower)
})

test_that("missing required columns raise an informative error", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  bad <- tempfile(fileext = ".csv")
  utils::write.csv(data.frame(notword = "x"), bad, row.names = FALSE)
  expect_error(load_lexicon(bad, schema), "required column")
})
