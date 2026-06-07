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

test_that("missing required columns raise an informative error", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  bad <- tempfile(fileext = ".csv")
  utils::write.csv(data.frame(notword = "x"), bad, row.names = FALSE)
  expect_error(load_lexicon(bad, schema), "required column")
})
