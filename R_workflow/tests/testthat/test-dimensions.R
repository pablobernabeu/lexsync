test_that("count_syllables counts vowel runs", {
  expect_equal(count_syllables("cat"), 1L)
  expect_equal(count_syllables("table"), 2L)
  expect_equal(count_syllables("beautiful"), 3L)
  expect_equal(count_syllables("queue"), 1L)
  expect_equal(count_syllables("área"), 2L)   # accented vowels count (Spanish)
  expect_equal(count_syllables("中文"), 0L) # no Latin vowels (Chinese)
})

test_that("add_bigram_frequency is deterministic and a probability", {
  ref <- c("the", "then", "they", "there", "their", "them", "than", "that")
  a <- add_bigram_frequency(data.frame(word = c("the", "tha"), stringsAsFactors = FALSE), reference = ref)
  b <- add_bigram_frequency(data.frame(word = c("the", "tha"), stringsAsFactors = FALSE), reference = ref)
  expect_identical(a$bigram_freq, b$bigram_freq)
  expect_true(all(a$bigram_freq >= 0 & a$bigram_freq <= 1))
  expect_gt(a$bigram_freq[a$word == "the"], 0)
})

test_that("merge_norms joins case-insensitively and marks missing", {
  lex <- data.frame(word = c("cat", "dog", "xyz"), stringsAsFactors = FALSE)
  norms <- data.frame(word = c("Cat", "dog"), concreteness = c(4.9, 4.8), stringsAsFactors = FALSE)
  out <- merge_norms(lex, norms)
  expect_true("concreteness" %in% names(out))
  expect_equal(out$concreteness[out$word == "cat"], 4.9)
  expect_true(is.na(out$concreteness[out$word == "xyz"]))
})

# Pins the same contract as test_merge_norms_preserves_lexicon_order in the
# Python engine's test_querying.py. Norms covering only a later subset of the
# lexicon is the arrangement that makes merge(sort = FALSE) reorder the result.
test_that("merge_norms preserves the lexicon's row order", {
  lex <- data.frame(word = c("a", "b", "c", "d"), freq = 1:4, stringsAsFactors = FALSE)
  norms <- data.frame(word = c("d", "b"), conc = c(1, 2), stringsAsFactors = FALSE)
  out <- merge_norms(lex, norms)
  expect_identical(out$word, c("a", "b", "c", "d"))
  expect_identical(out$freq, 1:4)
  expect_equal(out$conc, c(NA, 2, NA, 1))
  expect_identical(names(out), c("word", "freq", "conc"))
  expect_identical(rownames(out), as.character(1:4))
})

test_that("merge_norms does not join on a missing key", {
  lex <- data.frame(word = c("cat", NA), stringsAsFactors = FALSE)
  norms <- data.frame(word = c("cat", NA), conc = c(1, 2), stringsAsFactors = FALSE)
  out <- merge_norms(lex, norms)
  expect_identical(out$word, c("cat", NA))
  expect_equal(out$conc, c(1, NA))
})
