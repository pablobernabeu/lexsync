test_that("count_syllables counts vowel runs", {
  expect_equal(count_syllables("cat"), 1L)
  expect_equal(count_syllables("table"), 2L)
  expect_equal(count_syllables("beautiful"), 3L)
  expect_equal(count_syllables("queue"), 1L)
  expect_equal(count_syllables("área"), 2L)   # accented vowels count (Spanish)
})

# The cross-check of the vowel class between the engines: SYLLABLE_CASES in
# test_dimensions.py holds the same words, in the same order, with the same counts.
# It covers ae, oe and every Latin Extended vowel the class was missing, which
# undercounted Polish, Czech, Hungarian, Romanian, Turkish, Danish and Norwegian
# words. The words are escaped to keep the R sources ASCII.
syllable_cases <- list(
  c("b\u0119d\u0119", 2),        # Polish, e with ogonek
  c("s\u0105", 1),               # Polish, a with ogonek
  c("\u0142\u0105ka", 2),        # Polish, l with stroke is a consonant
  c("k\u0131z", 1),              # Turkish, dotless i
  c("m\u0131", 1),
  c("d\u016fm", 1),              # Czech, u with ring
  c("m\u011bsto", 2),            # Czech, e with caron
  c("k\u0151", 1),               # Hungarian, o with double acute
  c("t\u0171z", 1),              # Hungarian, u with double acute
  c("m\u0103r", 1),              # Romanian, a with breve
  c("b\u00e6re", 2),             # Norwegian, ae
  c("s\u00f8ster", 2),           # Danish, o with stroke
  c("c\u0153ur", 1),             # French, oe
  c("m\u0101te", 2),             # Latvian, macrons
  c("m\u0113ness", 2),
  c("l\u012bdz", 1),
  c("\u016bdens", 2),
  c("g\u0117l\u0117", 2),        # Lithuanian, e with dot above
  c("\u012fvykis", 3),           # Lithuanian, i with ogonek
  c("rank\u0173", 2),            # Lithuanian, u with ogonek
  c("t\u014dky\u014d", 2),       # o with macron
  c("m\u01ce", 1),               # pinyin, vowels with caron
  c("n\u01d0", 1),
  c("w\u01d2", 1),
  c("b\u01d4", 1),
  c("m\u1ed9t", 1),              # Vietnamese, Latin Extended Additional
  c("ng\u01b0\u1eddi", 1),       # Vietnamese, u and o with horn
  c("\u0130stanbul", 3),         # lower-cases to i + U+0307, still Latin
  c("cafe\u0301", 2),            # decomposed input counts as composed
  c("don\u2019t", 1)             # a typographic apostrophe is punctuation
)

test_that("count_syllables counts the vowels of every Latin orthography", {
  words <- vapply(syllable_cases, `[`, character(1), 1L)
  expect_identical(count_syllables(words),
                   as.integer(vapply(syllable_cases, `[`, character(1), 2L)))
})

# Every value 0 let a design match on n_syllables in another script and report
# perfect balance; NA says the estimate does not apply.
test_that("count_syllables is missing for a word in another script", {
  words <- c("\u4e2d\u6587",                              # Chinese
             "\u043c\u043e\u043b\u043e\u043a\u043e",      # Russian
             "\u03bd\u03b5\u03c1\u03cc",                  # Greek
             "caf\u00e9\u4e2d")                           # one non-Latin letter
  expect_identical(count_syllables(words), rep(NA_integer_, 4L))
  expect_identical(count_syllables(NA), NA_integer_)
  expect_identical(count_syllables(""), 0L)
})

test_that("load_lexicon leaves n_syllables missing outside Latin script", {
  extdata <- function(f) system.file("extdata", f, package = "lexsync")
  schema <- yaml::read_yaml(extdata("schema.yaml"))
  zh <- load_lexicon(extdata("zh_example.csv"), schema)
  expect_true(all(is.na(zh$n_syllables)))
  expect_type(zh$n_syllables, "integer")
  en <- load_lexicon(extdata("en_example.csv"), schema)
  expect_false(anyNA(en$n_syllables))
  expect_type(en$n_syllables, "integer")
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

# The case-fold has to apply to the LEXICON's side of the key too. Only the norm
# table's side was normalised until now, and the test above passes either way
# because its lexicon is already lower-case -- so the suite asserted
# case-insensitivity in the one direction that happened to work. A lexicon holding
# `Dog` silently matched nothing and the design carried on with an all-NA
# dimension, in BOTH engines, which is why no parity test could have caught it.
# test_merge_norms_folds_the_lexicon_key_too in test_dimensions.py asserts the same.
test_that("merge_norms case-folds the lexicon's side of the key too", {
  lex <- data.frame(word = c("Dog", "cat", "BIRD"), stringsAsFactors = FALSE)
  norms <- data.frame(word = c("dog", "cat", "bird"), conc = c(4.9, 4.8, 4.7),
                      stringsAsFactors = FALSE)
  out <- merge_norms(lex, norms)
  expect_equal(out$conc, c(4.9, 4.8, 4.7))
  # The lexicon's own spelling survives: `word` is the byte-order tie-break behind
  # every selection, so the join must not rewrite it.
  expect_identical(out$word, c("Dog", "cat", "BIRD"))
})

# Pins the same contract as test_merge_norms_keeps_the_lexicon_column_order in
# test_dimensions.py. R's merge() hoists the by-column to position 1 while pandas
# keeps the left frame's order, so the two engines returned different column order
# whenever `on` was not already the first column -- measured, not supposed.
test_that("merge_norms keeps the lexicon's column order when the key is not first", {
  lex <- data.frame(id = 1:2, word = c("dog", "cat"), freq = c(5.0, 4.8),
                    stringsAsFactors = FALSE)
  norms <- data.frame(word = c("dog", "cat"), conc = c(1.0, 2.0), stringsAsFactors = FALSE)
  expect_identical(names(merge_norms(lex, norms)), c("id", "word", "freq", "conc"))

  # Also when the key is neither first nor named `word`.
  lex2 <- data.frame(word = c("dog", "cat"), lemma = c("DOG", " cat"),
                     stringsAsFactors = FALSE)
  norms2 <- data.frame(lemma = c("dog", "cat"), aoa = c(3.1, 3.4), stringsAsFactors = FALSE)
  out2 <- merge_norms(lex2, norms2, on = "lemma")
  expect_identical(names(out2), c("word", "lemma", "aoa"))
  expect_equal(out2$aoa, c(3.1, 3.4))
})

# A colliding name is the worst of the three divergences: R's merge() renames to
# `frequency.x`/`.y` and pandas to `frequency_x`/`_y`, so a design matching on
# `frequency` finds neither, in either engine. Refusing is the only safe answer.
test_that("merge_norms rejects a norm column that collides with the lexicon", {
  lex <- data.frame(word = "dog", frequency = 5.0, stringsAsFactors = FALSE)
  norms <- data.frame(word = "dog", frequency = 1.1, stringsAsFactors = FALSE)
  expect_error(merge_norms(lex, norms), "already exist on the lexicon")
  # Naming the columns to keep is the documented way out.
  norms2 <- data.frame(word = "dog", frequency = 1.1, conc = 2.0, stringsAsFactors = FALSE)
  expect_equal(merge_norms(lex, norms2, columns = "conc")$conc, 2.0)
})

test_that("merge_norms rejects an absent column or key", {
  lex <- data.frame(word = "cat", stringsAsFactors = FALSE)
  norms <- data.frame(word = "cat", conc = 1.0, stringsAsFactors = FALSE)
  expect_error(merge_norms(lex, norms, columns = c("conc", "nope")),
               "no column\\(s\\): 'nope'")
  expect_error(merge_norms(data.frame(w = "cat", stringsAsFactors = FALSE), norms),
               "'word' on the lexicon")
  expect_error(merge_norms(lex, data.frame(w = "cat", conc = 1.0, stringsAsFactors = FALSE)),
               "'word' on the norm table")
})

test_that("merge_norms keeps the first of a duplicated norm key", {
  out <- merge_norms(data.frame(word = "cat", stringsAsFactors = FALSE),
                     data.frame(word = c("cat", "CAT"), conc = c(1.0, 9.0),
                                stringsAsFactors = FALSE))
  expect_equal(out$conc, 1.0)
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
