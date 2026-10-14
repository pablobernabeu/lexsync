# Lexical-decision generation with accented letters, and the refusal of logographic
# scripts.
#
# The generators substituted only the letters a to z and left out every word holding any
# other letter. A Spanish lexical decision lost 16.5% of a typical band (1,368 of 8,305
# words, among them 261 preterites in -o with an acute accent) and could never produce an
# accented pseudoword. Their alphabet is now the set of letters the reference lexicon
# attests, in UTF-8 byte order. Chinese is refused, since its characters are letters to
# Unicode but a form made by swapping one character for another is of unknown validity
# as a pseudoword. test_generation_accents.py holds the Python engine to the same tests,
# by the same names. The accented letters are written as escapes, so the file stays
# ASCII.

ga_es <- c("agua", "avi\u00f3n", "\u00e1rbol", "caf\u00e9", "calle", "cami\u00f3n", "campo",
           "canci\u00f3n", "casa", "cielo", "ciudad", "fuego", "gato", "l\u00e1piz", "libro",
           "luna", "ma\u00f1ana", "mesa", "monta\u00f1a", "mundo", "ni\u00f1o", "noche",
           "papel", "perro", "playa", "puerta", "silla", "tierra", "ventana")
ga_pool <- function() {
  data.frame(word = ga_es, length = nchar(ga_es), stringsAsFactors = FALSE)
}
ga_seg <- function(...) {
  pairs <- list(...)
  lapply(seq(1L, length(pairs), by = 2L),
         function(i) list(role = pairs[[i]], text = pairs[[i + 1L]]))
}
ga_data <- function(name) system.file("extdata", name, package = "lexsync")
ga_ascii <- function(x) !grepl("[^\\x01-\\x7f]", x, perl = TRUE)

test_that("the_alphabet_is_the_set_of_letters_the_reference_attests", {
  # Letters only, so the hyphen of e-mail is left out, in UTF-8 byte order, so the
  # accented letters follow z.
  got <- .reference_alphabet(c("canci\u00f3n", "a\u00f1o", "e-mail", "ping\u00fcino"))
  expect_identical(got, c("a", "c", "e", "g", "i", "l", "m", "n", "o", "p",
                          "\u00f1", "\u00f3", "\u00fc"))
})

test_that("a_substitution_may_use_an_accented_letter_the_reference_attests", {
  # The only legal substitution in 'tas' is an o with an acute accent, which the a-z
  # alphabet lacked, so the generator found no candidate at all and refused the word.
  got <- generate_pseudowords("tas", c("t\u00f3", "\u00f3s", "to"))
  expect_identical(got$pseudoword, "t\u00f3s")
})

test_that("build_lexdec_stimuli_keeps_accented_base_words", {
  stim <- build_lexdec_stimuli(ga_pool(), 8L, reference_words = ga_es)
  words <- stim$target[stim$condition == "word"]
  pseudo <- stim$target[stim$condition == "pseudoword"]
  # The even spread over the byte-ordered pool reaches the a with an acute accent of
  # arbol, past z, and camion keeps its accent in its pseudoword.
  expect_identical(words, c("agua", "cami\u00f3n", "cielo", "libro", "mesa", "noche",
                            "puerta", "\u00e1rbol"))
  expect_identical(pseudo, c("ague", "cani\u00f3n", "ciero", "liero", "iesa", "nocie",
                             "fuerta", "erbol"))
  # The pool holds nothing but letters the reference attests, so every word is eligible.
  expect_identical(nrow(.lexdec_eligible(ga_pool(), ga_es)), length(ga_es))
})

test_that("the_subsyllabic_segmenter_reads_accented_letters", {
  expect_identical(segment_subsyllabic("canci\u00f3n"),
                   ga_seg("onset", "c", "nucleus", "a", "coda", "n", "onset", "c",
                          "nucleus", "i\u00f3", "coda", "n"))
  expect_identical(segment_subsyllabic("ping\u00fcino"),
                   ga_seg("onset", "p", "nucleus", "i", "coda", "n", "onset", "g",
                          "nucleus", "\u00fci", "onset", "n", "nucleus", "o"))
  expect_identical(segment_subsyllabic("a\u00f1o"),
                   ga_seg("nucleus", "a", "onset", "\u00f1", "nucleus", "o"))
  expect_identical(segment_subsyllabic("Canci\u00f3n"), segment_subsyllabic("canci\u00f3n"))
  # A word with a character that is not a letter has no segments, nor has a word with no
  # Latin vowel, so both go to letter substitution.
  expect_length(segment_subsyllabic("e-mail"), 0)
  expect_length(segment_subsyllabic("\u043c\u043e\u043b\u043e\u043a\u043e"), 0)
})

test_that("the_subsyllabic_generator_keeps_accented_words", {
  # Each word is segmented, so whole constituents are swapped and the n with a tilde of
  # montana stays in its pseudoword. The a-z segmenter returned nothing for all three,
  # which sent them to letter substitution.
  got <- generate_pseudowords_subsyllabic(c("canci\u00f3n", "cami\u00f3n", "monta\u00f1a"),
                                          ga_es)
  expect_identical(got$pseudoword, c("cancien", "namuan", "canti\u00f1o"))
})

test_that("a_logographic_lexicon_is_refused", {
  message <- "pseudoword generation is defined for alphabetic scripts"
  zh <- read_csv_utf8(ga_data("zh_example.csv"), as_character = "word")
  zh$length <- nchar(zh$word)
  expect_error(build_lexdec_stimuli(zh, 4L, reference_words = zh$word), message,
               fixed = TRUE)
  expect_error(generate_pseudowords("\u4e2d\u6587", c("\u4e2d\u6587", "\u6c49\u5b57")),
               message, fixed = TRUE)
  expect_error(generate_pseudowords_subsyllabic("\u4e2d\u6587",
                                                c("\u4e2d\u6587", "\u6c49\u5b57")),
               message, fixed = TRUE)
})

test_that("a_generated_design_on_a_logographic_lexicon_is_refused", {
  dir <- tempfile("zh_lexdec_"); dir.create(dir); on.exit(unlink(dir, recursive = TRUE))
  design <- list(name = "zh_lexdec", language = "chinese", paradigm = "lexical_decision",
                 items = list(source = "generate", lexicon = ga_data("zh_example.csv")),
                 n_per_condition = 4L, pool_filters = list(length = c(2L, 2L)))
  path <- file.path(dir, "design.yaml")
  yaml::write_yaml(design, path)
  expect_error(run_pipeline(path, ga_data("schema.yaml"), file.path(dir, "out"),
                            verbose = FALSE),
               paste0("pseudoword generation is defined for alphabetic scripts, and '.+' ",
                      "is written in a logographic one"))
})

# The Spanish demonstration, read from the repository's committed outputs.
test_that("the_spanish_demonstration_keeps_accented_words_and_avoids_known_forms", {
  design <- yaml::read_yaml(repo_path("config", "design_es_lexdec.yaml"))
  known_path <- "corpora/derived/es_known_forms.txt"
  expect_identical(design$items$generation$exclude, known_path)
  s <- read_csv_utf8(repo_path("output", "stimuli", "es_lexdec_spanish_stimuli_R.csv"),
                     as_character = c("word", "target"))
  words <- s$word[s$condition == "word"]
  pseudo <- s$word[s$condition == "pseudoword"]
  expect_identical(length(words), as.integer(design$n_per_condition))
  expect_identical(length(pseudo), length(words))
  expect_true(any(!ga_ascii(words)))
  expect_true(any(!ga_ascii(pseudo)))
  known <- .read_utf8_lines(repo_path(known_path))
  expect_identical(intersect(pseudo, known), character(0))
  ds <- jsonlite::read_json(repo_path("output", "reports", "es_lexdec_spanish_datasheet_R.json"))
  # Every word in the band is written in letters es.csv attests, so the record counts
  # the whole band, accented words included.
  lex <- read_csv_utf8(repo_path("corpora", "derived", "es.csv"), as_character = "word")
  len <- design$pool_filters$length
  frq <- design$pool_filters$frequency
  n_band <- sum(nchar(lex$word) >= len[1] & nchar(lex$word) <= len[2] &
                lex$freq_zipf >= frq[1] & lex$freq_zipf <= frq[2])
  expect_identical(ds$selection$candidate_pool,
                   list(list(condition = "words in band", n_candidates = n_band)))
})
