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
