make_design <- function() {
  list(
    name = "t", language = "english", n_per_condition = 10,
    pool_filters = list(length = c(3, 7), frequency = c(3.8, 7)),
    conditions = list(
      list(name = "high", define_by = list(frequency = c(5.2, 7.0))),
      list(name = "low",  define_by = list(frequency = c(3.8, 4.4)))
    ),
    match_on = list("length", "n_density", "old20")
  )
}

test_that("match_stimuli is deterministic", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"), schema, "english")
  s1 <- match_stimuli(lex, make_design(), schema)
  s2 <- match_stimuli(lex, make_design(), schema)
  expect_identical(s1$word, s2$word)
})

test_that("match_stimuli balances conditions and isolates the manipulated dimension", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"), schema, "english")
  s <- match_stimuli(lex, make_design(), schema)
  expect_equal(as.integer(table(s$condition)), c(10L, 10L))
  hi <- s$frequency[s$condition == "high"]
  lo <- s$frequency[s$condition == "low"]
  expect_gt(mean(hi), mean(lo))                              # frequency manipulated
  expect_lt(abs(cohens_d(s$length[s$condition == "high"],
                         s$length[s$condition == "low"])), 0.3)  # length controlled
})
