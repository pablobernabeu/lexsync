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

test_that("mahalanobis matching balances and is deterministic within an engine", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"), schema, "english")
  d <- make_design(); d$matching <- list(method = "mahalanobis")
  s <- match_stimuli(lex, d, schema)
  expect_equal(as.integer(table(s$condition)), c(10L, 10L))
  expect_gt(mean(s$frequency[s$condition == "high"]), mean(s$frequency[s$condition == "low"]))
  for (dim in c("length", "n_density", "old20")) {           # correlated controls balanced
    expect_lt(abs(cohens_d(s[[dim]][s$condition == "high"],
                           s[[dim]][s$condition == "low"])), 0.5)
  }
  # deterministic within an engine (cross-engine identity is not guaranteed here)
  expect_identical(s$word, match_stimuli(lex, d, schema)$word)
})

test_that("optimal matching equates the confound and is deterministic within an engine", {
  skip_if_not_installed("clue")
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"), schema, "english")
  s <- match_stimuli(lex, make_confounded_design(method = "optimal"), schema)
  expect_equal(as.integer(table(s$condition)), c(20L, 20L))
  expect_gt(mean(s$n_density[s$condition == "dense"]),
            mean(s$n_density[s$condition == "sparse"]))
  for (dim in c("length", "frequency")) {
    expect_lt(abs(cohens_d(s[[dim]][s$condition == "dense"],
                           s[[dim]][s$condition == "sparse"])), 0.15)
  }
  expect_identical(s$word,
                   match_stimuli(lex, make_confounded_design(method = "optimal"), schema)$word)
})

make_continuous_design <- function() {
  list(name = "cont", language = "english", n_per_condition = 40,
    pool_filters = list(length = c(3, 8), frequency = c(3.8, 7.0)),
    continuous = list(predictor = "frequency",
                      controls = list("length", "n_density", "old20")),
    match_on = list("length", "n_density", "old20"),
    matching = list(tolerance_k = list(length = 1.5, n_density = 1.5, old20 = 1.5)))
}

test_that("select_continuous_stimuli spans the predictor and decorrelates controls", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"), schema, "english")
  pool <- build_pool(lex, make_continuous_design()$pool_filters)
  s <- select_continuous_stimuli(pool, make_continuous_design(), schema)
  expect_true(all(s$condition == "continuous"))
  expect_equal(s$set, seq_len(nrow(s)))
  for (cc in c("length", "n_density", "old20")) {
    expect_lt(abs(suppressWarnings(stats::cor(s$frequency, s[[cc]]))), 0.6)
  }
  # deterministic within an engine
  expect_identical(s$word, select_continuous_stimuli(pool, make_continuous_design(), schema)$word)
})

test_that("select_continuous_stimuli is driven by byte order, not row order", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"), schema, "english")
  pool <- build_pool(lex, make_continuous_design()$pool_filters)
  a <- select_continuous_stimuli(pool, make_continuous_design(), schema)
  b <- select_continuous_stimuli(pool[rev(seq_len(nrow(pool))), , drop = FALSE],
                                 make_continuous_design(), schema)
  expect_setequal(a$word, b$word)
})

test_that("select_continuous_stimuli rejects the predictor appearing in controls", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"), schema, "english")
  pool <- build_pool(lex, make_continuous_design()$pool_filters)
  d <- make_continuous_design()
  d$continuous$controls <- list("frequency", "length")
  d$match_on <- list("frequency", "length")
  expect_error(select_continuous_stimuli(pool, d, schema), "must not also appear")
})

tiny_schema <- function() {
  list(matching = list(method = "standardised_euclidean", tolerance_k = list()))
}

na_pool <- function() {
  # The two missing-concreteness rows lead the low subpool deliberately: a matcher
  # that ranks an NA distance by row order rather than last would pick them first.
  data.frame(
    id = 1:8,
    word = c("lac", "lad", "laa", "lab", "laz", "hab", "hac", "had"),
    frequency = c(2.0, 2.5, 1.0, 1.5, 3.0, 5.0, 6.0, 7.0),
    concreteness = c(NA, NA, 3.0, 2.95, 9.0, 3.0, 3.1, 2.9),
    stringsAsFactors = FALSE
  )
}

na_design <- function(n = 3L) {
  list(name = "na", language = "english", n_per_condition = n,
       conditions = list(
         list(name = "high", define_by = list(frequency = c(5.0, 7.0))),
         list(name = "low",  define_by = list(frequency = c(1.0, 3.0)))
       ),
       match_on = list("concreteness"))
}

test_that("rows missing a matched dimension are dropped and ranked last", {
  # Pins the same contract as test_matching.py: only two low candidates fall inside
  # the anchor window, so the window relaxes, and the NA rows must never be chosen
  # ahead of a real one. The R and Python engines must agree word for word.
  s <- match_stimuli(na_pool(), na_design(), tiny_schema())
  expect_identical(s$word[s$condition == "high"], c("hab", "hac", "had"))
  expect_identical(s$word[s$condition == "low"], c("laa", "lab", "laz"))
  expect_false(any(is.na(s$concreteness)))
})

test_that("an undersized condition raises rather than duplicating words", {
  # Five anchors but only two low candidates: the greedy assignment would exhaust
  # the low pool and re-pick its first word for sets 3 to 5.
  pool <- data.frame(
    id = 1:7,
    word = c("laa", "lab", "hab", "hac", "had", "hae", "haf"),
    frequency = c(1.0, 1.5, 5.0, 5.5, 6.0, 6.5, 7.0),
    concreteness = rep(3.0, 7),
    stringsAsFactors = FALSE
  )
  expect_error(match_stimuli(pool, na_design(5L), tiny_schema()),
               "condition 'low' has only 2 candidate")
})

test_that("an unknown matching method is an error, not a silent fallback", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"), schema, "english")
  d <- make_design(); d$matching <- list(method = "jiont")
  expect_error(match_stimuli(lex, d, schema), "unknown matching method 'jiont'")
})

test_that("joint matching rejects a design without exactly two conditions", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"), schema, "english")
  d <- make_design()
  d$matching <- list(method = "joint")
  d$conditions[[3]] <- list(name = "mid", define_by = list(frequency = c(4.4, 5.2)))
  expect_error(match_stimuli(lex, d, schema), "requires exactly two conditions")
})

test_that("resample_stimuli produces disjoint matched sets", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"), schema, "english")
  design <- list(name = "r", language = "english", n_per_condition = 5,
    pool_filters = list(length = c(3, 7), frequency = c(3.8, 7)),
    conditions = list(list(name = "high", define_by = list(frequency = c(5.0, 7.0))),
                      list(name = "low", define_by = list(frequency = c(3.8, 4.4)))),
    match_on = list("length"))
  pool <- build_pool(lex, design$pool_filters)
  s <- resample_stimuli(pool, design, schema, 3L)
  expect_setequal(unique(s$replicate), c(1L, 2L, 3L))
  for (r in unique(s$replicate)) {
    expect_equal(sort(as.integer(table(s$condition[s$replicate == r]))), c(5L, 5L))
  }
  w <- split(s$word, s$replicate)
  expect_length(intersect(w[[1]], w[[2]]), 0)
  expect_length(intersect(w[[1]], w[[3]]), 0)
  expect_length(intersect(w[[2]], w[[3]]), 0)
})
