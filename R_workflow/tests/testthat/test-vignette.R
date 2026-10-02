# The vignette's design chunk declares pool_filters, which match_stimuli never
# reads: the filter takes effect only through the explicit build_pool step the
# vignette demonstrates, mirroring run_pipeline. This pins that the demonstrated
# code applies the filter and that skipping the step would change the selection.
# The design is the Python README's quick start, so the twins demonstrate the same
# outcome: with 60 items per condition every control passes the equivalence test,
# which no dimension that varies can do with fewer than 23.
test_that("vignette design chunk applies pool_filters through build_pool", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"),
                      schema, language = "english")
  design <- list(
    name = "quick_start", language = "english", n_per_condition = 60,
    pool_filters = list(length = c(3, 8), frequency = c(3.8, 7.0)),
    conditions = list(
      list(name = "high_frequency", define_by = list(frequency = c(5.2, 7.0))),
      list(name = "low_frequency",  define_by = list(frequency = c(3.8, 4.4)))
    ),
    match_on = list("length", "n_density", "old20"),
    counterbalance = list(lists = 1)
  )
  pool <- build_pool(lex, design$pool_filters)
  expect_true(all(pool$length >= 3 & pool$length <= 8))
  expect_true(all(pool$frequency >= 3.8 & pool$frequency <= 7))
  stim <- match_stimuli(pool, design, schema)
  expect_equal(nrow(stim), 120L)
  expect_true(all(stim$length <= 8))
  report <- match_report(stim, c("length", "frequency", "n_density", "old20"), schema)
  controls <- report$comparisons[report$comparisons$dimension != "frequency", ]
  expect_true(all(controls$equivalent))
  # Passing the raw lexicon silently drops the filter: longer words become
  # eligible and the selection changes.
  unfiltered <- match_stimuli(lex, design, schema)
  expect_false(identical(sort(unfiltered$word), sort(stim$word)))
})
