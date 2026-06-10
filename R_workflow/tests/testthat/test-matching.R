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

make_confounded_design <- function(method = NULL) {
  # Neighbourhood density is intrinsically confounded with length and
  # frequency, so the per-anchor matcher leaves a residual on the controls.
  d <- list(
    name = "tj", language = "english", n_per_condition = 20,
    pool_filters = list(length = c(3, 7), frequency = c(3.8, 7)),
    conditions = list(
      list(name = "dense",  define_by = list(n_density = c(4, 100))),
      list(name = "sparse", define_by = list(n_density = c(0, 1)))
    ),
    match_on = list("length", "frequency")
  )
  if (!is.null(method)) d$matching <- list(method = method)
  d
}

test_that("joint matching cancels the control-dimension confound", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"), schema, "english")
  s <- match_stimuli(lex, make_confounded_design(method = "joint"), schema)
  expect_equal(as.integer(table(s$condition)), c(20L, 20L))
  expect_gt(mean(s$n_density[s$condition == "dense"]),
            mean(s$n_density[s$condition == "sparse"]))      # density manipulated
  for (dim in c("length", "frequency")) {                    # controls equated tightly
    expect_lt(abs(cohens_d(s[[dim]][s$condition == "dense"],
                           s[[dim]][s$condition == "sparse"])), 0.1)
  }
  # Joint matching is at least as tight as the per-anchor matcher on the confound.
  s_std <- match_stimuli(lex, make_confounded_design(), schema)
  d_joint <- abs(cohens_d(s$length[s$condition == "dense"],
                          s$length[s$condition == "sparse"]))
  d_std <- abs(cohens_d(s_std$length[s_std$condition == "dense"],
                        s_std$length[s_std$condition == "sparse"]))
  expect_lte(d_joint, d_std + 1e-9)
})
