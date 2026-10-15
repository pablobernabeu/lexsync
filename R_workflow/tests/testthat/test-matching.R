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

maha_pool <- function() {
  # Six rows complete on all three dimensions, then one row missing each of the first
  # two. The complete rows correlate, so a metric that dropped them would differ from
  # the pinned one in every off-diagonal cell.
  rbind(c(1, 2, 0.5), c(2, 2.5, 1.5), c(3, 2, 1), c(4, 3.5, 2.5), c(5, 4, 2),
        c(6, 5.5, 3.5), c(NA, 3, 2), c(3.5, NA, 1))
}

test_that("mahalanobis correlations come from complete rows", {
  # cor() under its default use = "everything" returns NA for every pair involving a
  # column with a missing value, and .maha_metric read NA as no correlation, so such a
  # dimension lost all its correlations and entered the distance as an independent
  # term. The correlations now come from the rows complete on every matched
  # dimension. The expected matrix is the inverse of the six complete rows'
  # correlation matrix plus the 1e-6 ridge, pinned identically in test_matching.py, so
  # the two engines' metrics agree to 1e-9.
  expected <- rbind(c(6.508789703372, -4.641761938509, -1.404061170998),
                    c(-4.641761938509, 12.925495086475, -8.100175947949),
                    c(-1.404061170998, -8.100175947949, 9.918090174968))
  metric <- .maha_metric(maha_pool())
  expect_lt(max(abs(metric - expected)), 1e-9)
})

test_that("mahalanobis refuses a pool with too few complete rows", {
  # k dimensions need k + 2 complete rows here. Twinned with test_matching.py.
  z <- maha_pool()[c(1, 2, 3, 4, 7, 8), ]       # four complete rows of three dimensions
  expect_error(.maha_metric(z),
               paste0("needs at least 5 items complete on the matched dimensions to ",
                      "estimate their correlations, but the pool has 4."),
               fixed = TRUE)
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

test_that("select_continuous_stimuli requires match_on to equal the controls", {
  # Twin of test_select_continuous_requires_match_on_equals_controls, which this suite
  # was missing. The two keys state one contract twice, so a design where they disagree
  # is ambiguous about which dimensions are actually held constant, and the datasheet
  # would record whichever list it happened to read.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"), schema, "english")
  pool <- build_pool(lex, make_continuous_design()$pool_filters)
  d <- make_continuous_design()
  d$match_on <- list("length", "n_density")   # short of continuous.controls
  expect_error(select_continuous_stimuli(pool, d, schema), "match_on must equal")
})

test_that("select_continuous_stimuli requires at least one control", {
  # With no control there is nothing held constant, and an even spread over the
  # predictor alone would still be recorded as a controlled selection.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"), schema, "english")
  pool <- build_pool(lex, make_continuous_design()$pool_filters)
  d <- make_continuous_design()
  d$continuous$controls <- list()
  d$match_on <- list()
  expect_error(select_continuous_stimuli(pool, d, schema), "at least one control")
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

test_that("an NA-depleted condition raises rather than duplicating words", {
  # The raw row count clears n_per_condition, but only two rows carry the matched
  # dimension. The other three are excluded before matching, so two candidates face
  # four anchors and the matcher raises rather than re-picking them. Pinned
  # identically in test_matching.py.
  pool <- data.frame(
    id = 1:9,
    word = c("laa", "lab", "lac", "lad", "lae", "hab", "hac", "had", "hae"),
    frequency = c(1.0, 1.5, 2.0, 2.5, 3.0, 5.0, 5.5, 6.0, 6.5),
    concreteness = c(3.0, 3.1, NA, NA, NA, 3.0, 3.1, 2.9, 3.2),
    stringsAsFactors = FALSE
  )
  expect_error(match_stimuli(pool, na_design(4L), tiny_schema()),
               "condition 'low' has only 2 candidate")
})

test_that("a single-item anchor relaxes the window rather than selecting NA", {
  # An anchor of one item gives sd = NA, so every tolerance bound is NA. Without
  # keep[is.na(keep)] <- FALSE the whole vector goes NA and cand[keep, ] indexes
  # all-NA filler rows, which clear both count guards and are then selected. Python
  # compares False against NaN and relaxes; test_matching.py pins the same word.
  pool <- data.frame(
    id = 1:5,
    word = c("aaa", "bbb", "ccc", "ddd", "eee"),
    frequency = c(1.0, 2.0, 3.0, 4.0, 5.0),
    concreteness = c(3.0, 3.1, 3.2, 3.3, 3.4),
    stringsAsFactors = FALSE
  )
  design <- list(name = "one", language = "english", n_per_condition = 1L,
                 conditions = list(
                   list(name = "high", define_by = list(frequency = c(1.0, 1.0))),
                   list(name = "low",  define_by = list(frequency = c(2.0, 5.0)))
                 ),
                 match_on = list("concreteness"))
  s <- match_stimuli(pool, design, tiny_schema())
  expect_identical(s$word[s$condition == "low"], "bbb")
  expect_false(any(is.na(s$word)))
})

# ---- candidates missing a matched dimension ----------------------------------
# Twinned with test_matching.py, which pins the same words, counts and messages.

x_pool <- function(a_words, a_x) {
  # Condition A spans frequency 5 to 7 and B 1 to 3. B's six candidates are complete.
  data.frame(
    id = seq_len(length(a_words) + 6L),
    word = c(a_words, "eagle", "fig", "grape", "hat", "igloo", "jam"),
    frequency = c(c(6.0, 6.1, 6.2, 6.3, 6.4)[seq_along(a_words)],
                  2.0, 2.1, 2.2, 2.3, 2.4, 2.5),
    x = c(a_x, 1.1, 2.1, 3.1, 0.5, 2.6, 1.6),
    stringsAsFactors = FALSE
  )
}

x_design <- function(n, matching = NULL) {
  d <- list(name = "x", language = "english", n_per_condition = n,
            conditions = list(
              list(name = "A", define_by = list(frequency = c(5.0, 7.0))),
              list(name = "B", define_by = list(frequency = c(1.0, 3.0)))
            ),
            match_on = list("x"))
  if (!is.null(matching)) d$matching <- matching
  d
}

x_schema <- function() {
  list(matching = list(method = "standardised_euclidean", tolerance_k = list(x = 2.0)))
}

test_that("an incomplete anchor never reuses a candidate", {
  # cloud lacks x. Used candidates were set to Inf and a missing distance ranked after
  # Inf, so cloud re-picked eagle and the run stopped with a false 'overlapping
  # conditions' error. cloud is now excluded before the anchor spread.
  pool <- x_pool(c("apple", "brick", "cloud", "drum"), c(1.0, 2.0, NA, 3.0))
  expect_error(match_stimuli(pool, x_design(4L), x_schema()),
               "4 sets per condition were requested but only 3", fixed = TRUE)
  s <- match_stimuli(pool, x_design(4L, list(shortfall = "allow")), x_schema())
  expect_identical(s$word[s$condition == "A"], c("apple", "brick", "drum"))
  expect_identical(s$word[s$condition == "B"], c("eagle", "fig", "grape"))
  expect_identical(attr(s, "audit")$incomplete_dropped, list(list(condition = "A", n = 1L)))
})

test_that("an incomplete first anchor is excluded", {
  # apple lacks x and comes first in the anchor spread. Its distance to every
  # candidate was missing, so the byte-first word in the window, fig, became its
  # counterpart.
  pool <- x_pool(c("apple", "brick", "cloud", "drum"), c(NA, 2.0, 2.5, 3.0))
  s <- match_stimuli(pool, x_design(3L), x_schema())
  expect_identical(s$word[s$condition == "A"], c("brick", "cloud", "drum"))
  expect_identical(s$word[s$condition == "B"], c("fig", "igloo", "grape"))
  expect_false(anyNA(s$x))
  expect_identical(attr(s, "audit")$incomplete_dropped, list(list(condition = "A", n = 1L)))
})

joint_x_pool <- function() {
  # Condition A has three complete rows and two that lack x. All six rows of B are
  # complete.
  x_pool(c("aa", "ab", "ac", "ad", "ae"), c(1.0, 2.0, 3.0, NA, NA))
}

x_pairs <- function(s) {
  sort(vapply(split(s$word, s$set), paste, character(1), collapse = "+"),
       method = "radix")
}

test_that("joint reports a shortfall instead of pairing incomplete rows", {
  # A missing cost sorted after every real one, so once the complete pairs ran out
  # joint paired ad, which lacks x, to reach n.
  expect_error(match_stimuli(joint_x_pool(), x_design(4L, list(method = "joint")), x_schema()),
               "4 sets per condition were requested but only 3", fixed = TRUE)
  s <- match_stimuli(joint_x_pool(), x_design(4L, list(method = "joint", shortfall = "allow")),
                     x_schema())
  expect_identical(unname(x_pairs(s)), c("aa+eagle", "ab+fig", "ac+grape"))
  expect_identical(attr(s, "audit")$incomplete_dropped, list(list(condition = "A", n = 2L)))
})

test_that("optimal selects cleanly with an incomplete row", {
  # A missing cost reached the assignment solver, which refused it with an error that
  # differed between the engines.
  skip_if_not_installed("clue")
  s <- match_stimuli(joint_x_pool(), x_design(3L, list(method = "optimal")), x_schema())
  expect_identical(unname(x_pairs(s)), c("aa+eagle", "ab+fig", "ac+grape"))
  expect_identical(attr(s, "audit")$incomplete_dropped, list(list(condition = "A", n = 2L)))
})

test_that("a condition left without complete candidates is refused by name", {
  # Every low candidate lacks the matched dimension. Without the check the condition
  # would be reported as having no candidates, although its window holds two words.
  pool <- data.frame(
    id = 1:5,
    word = c("hab", "hac", "had", "laa", "lab"),
    frequency = c(5.0, 6.0, 7.0, 1.0, 2.0),
    concreteness = c(3.0, 3.1, 2.9, NA, NA),
    stringsAsFactors = FALSE
  )
  expect_error(match_stimuli(pool, na_design(2L), tiny_schema()),
               paste0("condition 'low' has no candidates complete on the matched ",
                      "dimensions (2 lacked a value)"),
               fixed = TRUE)
})

test_that("verbose matching reports the excluded candidates", {
  # The console reports the exclusion as it happens, as it reports a relaxed window.
  pool <- x_pool(c("apple", "brick", "cloud", "drum"), c(NA, 2.0, 2.5, 3.0))
  expect_message(match_stimuli(pool, x_design(3L), x_schema(), verbose = TRUE),
                 "lexsync: dropped 1 candidate(s) of condition 'A' missing a matched dimension.",
                 fixed = TRUE)
})

test_that("a within-condition repeat is reported as an internal error", {
  # A repeat inside one condition is a defect of the matcher, which used to be
  # reported as overlapping conditions.
  out <- data.frame(word = c("apple", "apple", "eagle", "fig"),
                    condition = c("A", "A", "B", "B"), stringsAsFactors = FALSE)
  expect_error(.assert_distinct_words(out),
               paste0("lexsync: internal error: condition 'A' selected the word 'apple' ",
                      "more than once; please report this."),
               fixed = TRUE)
})

continuous_x_pool <- function() {
  # 50 words of one length, 20 of them (40%) without x. The other 30 values of x are
  # distinct, so the spread has no ties to break.
  i <- 0:49
  x <- ((37 * i) %% 50) / 10
  x[(i %% 5) < 2] <- NA_real_
  data.frame(id = i + 1L, word = sprintf("w%03d", i), frequency = 4.0, length = 4L,
             x = x, stringsAsFactors = FALSE)
}

continuous_x_design <- function() {
  list(name = "cx", language = "english", n_per_condition = 10L,
       continuous = list(predictor = "x", controls = list("length")),
       match_on = list("length"))
}

test_that("the continuous selector excludes rows missing the predictor", {
  # A missing predictor sorted last and the even spread always takes the last row, so
  # 4 of the 10 items selected here lacked it.
  s <- select_continuous_stimuli(continuous_x_pool(), continuous_x_design(), tiny_schema())
  expect_identical(s$word, c("w023", "w038", "w003", "w014", "w029",
                             "w044", "w009", "w047", "w012", "w027"))
  expect_false(anyNA(s$x))
  expect_identical(attr(s, "audit")$incomplete_dropped,
                   list(list(condition = "continuous", n = 20L)))
})

test_that("a continuous pool without a complete row is refused", {
  pool <- continuous_x_pool()
  pool$x <- NA_real_
  expect_error(select_continuous_stimuli(pool, continuous_x_design(), tiny_schema()),
               paste0("no item in the pool is complete on the predictor and the controls ",
                      "(50 lacked a value)"),
               fixed = TRUE)
})

test_that("a selection does not inherit an audit from its pool", {
  # R keeps attributes through a row subset, so an audit already on the pool reached
  # the continuous selector's result as if the selection had made it. The matcher
  # subsets columns before it binds, which drops them, but pandas carried the audit
  # through every method. Twinned with test_matching.py.
  stale <- list(incomplete_dropped = list(list(condition = "A", n = 99L)))
  pool <- x_pool(c("apple", "brick", "drum"), c(1.0, 2.0, 3.0))
  attr(pool, "audit") <- stale
  expect_null(attr(match_stimuli(pool, x_design(3L), x_schema()), "audit"))
  cpool <- continuous_x_pool()
  cpool <- cpool[!is.na(cpool$x), , drop = FALSE]
  attr(cpool, "audit") <- stale
  sel <- select_continuous_stimuli(cpool, continuous_x_design(), tiny_schema())
  # A continuous selection always records its control windows, and nothing else here.
  expect_identical(names(attr(sel, "audit")), "control_windows")
})

test_that("the continuous selector records its windows and the pool's spread", {
  # The windows are mean +/- k SD of the first pass, and the pool's SD is that of the
  # complete candidates, so the report can set each control's realised SD against it.
  # Pinned identically in test_matching.py.
  pool <- data.frame(word = sprintf("w%02d", 0:11), x = as.numeric(0:11),
                     length = rep(c(3, 4, 5, 6), 3), stringsAsFactors = FALSE)
  design <- list(name = "cw", language = "english", n_per_condition = 4L,
                 continuous = list(predictor = "x", controls = list("length")),
                 match_on = list("length"))
  sel <- select_continuous_stimuli(pool, design, tiny_schema())
  # The first pass takes x = 0, 4, 7 and 11, whose lengths 3, 3, 6 and 6 have mean 4.5
  # and SD sqrt(3); k defaults to 2.
  w <- attr(sel, "audit")$control_windows
  expect_length(w, 1L)
  expect_identical(w[[1]]$dimension, "length")
  expect_equal(w[[1]]$low, 4.5 - 2 * sqrt(3), tolerance = 1e-12)
  expect_equal(w[[1]]$high, 4.5 + 2 * sqrt(3), tolerance = 1e-12)
  expect_equal(w[[1]]$pool_sd, sqrt(15 / 11), tolerance = 1e-12)
})

test_that("a resampled selection records the first replicate's exclusions", {
  # The first replicate draws on the whole pool, so its exclusions are recorded, and
  # only it relaxes a window here, which is not. pd.concat dropped an audit that
  # differed between replicates while rbind kept the first replicate's, window
  # relaxation included, so the two engines returned different records. Twinned with
  # test_matching.py.
  pool <- data.frame(
    id = 1:11,
    word = c("ace", "bay", "cod", "dew", "elk", "fir", "gem", "hop", "ink", "jot", "kin"),
    frequency = c(6.0, 6.1, 6.2, 6.3, 6.4, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5),
    x = c(1.0, 0.0, 5.0, 1.0, NA, 0.2, 0.4, 4.8, 4.6, 2.0, NA),
    stringsAsFactors = FALSE
  )
  s <- resample_stimuli(pool, x_design(2L), x_schema(), 2L)
  expect_identical(s$word, c("ace", "dew", "gem", "fir", "bay", "cod", "jot", "hop"))
  expect_identical(attr(s, "audit"),
                   list(incomplete_dropped = list(list(condition = "A", n = 1L),
                                                  list(condition = "B", n = 1L))))
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

# A fractional count was truncated in silence, a logical or a quoted number was taken
# as a count, and zero gave an empty selection here and pandas' 'No objects to
# concatenate' in Python. validate_design() refuses the design key by the same rule.
# Pinned identically in test_matching.py.
test_that("resample_stimuli refuses a count that is not a positive whole number", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"), schema, "english")
  design <- list(name = "r", language = "english", n_per_condition = 5,
    pool_filters = list(length = c(3, 7), frequency = c(3.8, 7)),
    conditions = list(list(name = "high", define_by = list(frequency = c(5.0, 7.0))),
                      list(name = "low", define_by = list(frequency = c(3.8, 4.4)))),
    match_on = list("length"))
  pool <- build_pool(lex, design$pool_filters)
  message <- "resample.n_sets must be a positive whole number"
  for (bad in list(0, -1, 2.5, TRUE, "3", Inf)) {
    expect_error(resample_stimuli(pool, design, schema, bad), message, fixed = TRUE)
    resampled <- utils::modifyList(design, list(resample = list(n_sets = bad)))
    expect_error(validate_design(resampled, schema), message, fixed = TRUE)
  }
  expect_length(validate_design(utils::modifyList(design, list(resample = list(n_sets = 2))),
                                schema), 0L)
})

# ---- shortfall and tolerance policies, guards -------------------------------
# Twinned with test_matching.py: every fixture, expectation and message below
# must stay in step with the Python suite.

small_pool <- function() {
  data.frame(
    id = 1:8,
    word = c("haa", "hab", "hac", "laa", "lab", "lac", "lad", "lae"),
    frequency = c(5.0, 5.5, 6.0, 1.0, 1.5, 2.0, 2.5, 3.0),
    concreteness = c(3.0, 3.1, 2.9, 3.0, 3.1, 3.2, 2.8, 3.3),
    stringsAsFactors = FALSE
  )
}

small_design <- function(n, matching = NULL) {
  d <- list(
    name = "sf", language = "english", n_per_condition = n,
    conditions = list(
      list(name = "high", define_by = list(frequency = c(5.0, 7.0))),
      list(name = "low",  define_by = list(frequency = c(1.0, 3.0)))
    ),
    match_on = list("concreteness")
  )
  if (!is.null(matching)) d$matching <- matching
  d
}

test_that("a shortfall is an error by default", {
  # Three anchor candidates cannot honour n = 5; a silent shrink would change the
  # design that was planned without the design's consent.
  expect_error(match_stimuli(small_pool(), small_design(5L), tiny_schema()),
               "5 sets per condition were requested but only 3")
})

test_that("shortfall: allow accepts the shrink", {
  s <- match_stimuli(small_pool(), small_design(5L, matching = list(shortfall = "allow")),
                     tiny_schema())
  expect_equal(sort(as.integer(table(s$condition))), c(3L, 3L))
})

test_that("an unknown shortfall policy is an error", {
  expect_error(match_stimuli(small_pool(), small_design(3L, matching = list(shortfall = "maybe")),
                             tiny_schema()),
               "unknown shortfall policy 'maybe'")
})

test_that("joint matching errors on a shortfall by default", {
  # At most three disjoint pairs exist, so n = 5 cannot be met.
  pool <- small_pool()[1:6, , drop = FALSE]
  expect_error(match_stimuli(pool, small_design(5L, matching = list(method = "joint")),
                             tiny_schema()),
               "5 sets per condition were requested but only 3")
})

test_that("on_insufficient_tolerance: error refuses to relax", {
  # In the na_pool scenario the low condition has too few candidates inside
  # the anchor window, which the default policy silently relaxes.
  d <- na_design()
  d$matching <- list(on_insufficient_tolerance = "error")
  expect_error(match_stimuli(na_pool(), d, tiny_schema()),
               "within tolerance but 3 are needed")
})

test_that("a window relaxation is recorded in the audit attribute", {
  s <- match_stimuli(na_pool(), na_design(), tiny_schema())
  audit <- attr(s, "audit")
  expect_false(is.null(audit))
  rx <- audit$window_relaxations
  expect_length(rx, 1)
  expect_identical(rx[[1]]$condition, "low")
  expect_identical(rx[[1]]$n_needed, 3L)
})

test_that("a complete pool records no exclusion", {
  # Every shipped design has complete matched dimensions, so neither its audit nor the
  # datasheet built from it may gain an entry.
  s <- match_stimuli(small_pool(), small_design(3L), tiny_schema())
  expect_null(attr(s, "audit")[["incomplete_dropped"]])
})

overlapping_design <- function(n, method) {
  # Both conditions admit the whole pool, so every word sits in both subpools
  # and its self-pair costs exactly zero.
  list(
    name = "ov", language = "english", n_per_condition = n,
    conditions = list(
      list(name = "a", define_by = list(frequency = c(1.0, 7.0))),
      list(name = "b", define_by = list(frequency = c(1.0, 7.0)))
    ),
    match_on = list("concreteness"),
    matching = list(method = method, shortfall = "allow")
  )
}

test_that("joint matching never pairs a word with itself", {
  s <- match_stimuli(small_pool(), overlapping_design(3L, "joint"), tiny_schema())
  expect_false(any(duplicated(s$word)))
  for (st in split(s$word, s$set)) expect_length(unique(st), 2)
})

test_that("optimal matching never pairs a word with itself", {
  skip_if_not_installed("clue")
  s <- match_stimuli(small_pool(), overlapping_design(3L, "optimal"), tiny_schema())
  expect_false(any(duplicated(s$word)))
  for (st in split(s$word, s$set)) expect_length(unique(st), 2)
})

test_that("a misspelt define_by dimension is an error, not a widened condition", {
  d <- small_design(3L)
  d$conditions[[2]]$define_by <- list(frequnecy = c(1.0, 3.0))
  expect_error(match_stimuli(small_pool(), d, tiny_schema()),
               "dimension 'frequnecy' in condition 'low'")
})

test_that("a condition without define_by draws on the whole pool", {
  # NULL define_by falls back to the whole pool (and, for the anchor, to
  # ordering by 'frequency'); the Python engine used to crash with a bare
  # KeyError on a design this engine accepted. The words are pinned identically
  # in test_matching.py, so the two engines select the same stimuli.
  d <- small_design(3L)
  d$conditions[[2]] <- list(name = "rest")
  s <- match_stimuli(small_pool(), d, tiny_schema())
  expect_identical(s$word[s$condition == "high"], c("haa", "hab", "hac"))
  expect_identical(s$word[s$condition == "rest"], c("laa", "lab", "lad"))
  # An anchor without define_by orders by the fallback dimension.
  d <- small_design(3L)
  d$conditions[[1]] <- list(name = "any")
  d$conditions[[2]] <- list(name = "low", define_by = list(frequency = c(1.0, 3.0)))
  s <- match_stimuli(small_pool(), d, tiny_schema())
  expect_identical(s$word[s$condition == "any"], c("laa", "lad", "hac"))
  expect_identical(s$word[s$condition == "low"], c("lab", "lac", "lae"))
})

test_that("duplicate condition names are an error", {
  d <- small_design(3L)
  d$conditions[[2]]$name <- "high"
  expect_error(match_stimuli(small_pool(), d, tiny_schema()),
               "condition name 'high' appears more than once")
})

test_that("a negative tolerance is an error", {
  expect_error(match_stimuli(small_pool(),
                             small_design(3L, matching = list(tolerance_k = list(concreteness = -1))),
                             tiny_schema()),
               "tolerance_k for dimension 'concreteness' is negative")
})

test_that("a design without conditions is an error", {
  d <- small_design(3L)
  d$conditions <- NULL
  expect_error(match_stimuli(small_pool(), d, tiny_schema()),
               "the design has no conditions")
})

test_that("a_missing_or_empty_match_on_is_refused", {
  # Without match_on this engine scored every candidate at distance zero and returned
  # the byte-first words; with an empty list both engines did, under every anchored
  # method. Pinned identically in test_matching.py.
  msg <- "a matched design needs `match_on` naming at least one dimension"
  for (method in c("standardised_euclidean", "joint", "mahalanobis")) {
    d <- small_design(3L, matching = list(method = method))
    d$match_on <- NULL
    expect_error(match_stimuli(small_pool(), d, tiny_schema()), msg, fixed = TRUE)
    d$match_on <- list()
    expect_error(match_stimuli(small_pool(), d, tiny_schema()), msg, fixed = TRUE)
  }
})

test_that("a_whole_float_n_is_accepted_by_both_selectors", {
  # The Python engine raised a TypeError on 4.0. Pinned identically in
  # test_matching.py.
  s <- match_stimuli(small_pool(), small_design(3.0), tiny_schema())
  expect_identical(s$set, c(1L, 2L, 3L, 1L, 2L, 3L))
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"), schema, "english")
  pool <- build_pool(lex, make_continuous_design()$pool_filters)
  d <- make_continuous_design()
  d$n_per_condition <- 10.0
  expect_equal(nrow(select_continuous_stimuli(pool, d, schema)), 10L)
})

test_that("n_per_condition_zero_is_refused_by_both_selectors", {
  # The Python engine read a configured 0 as absent and returned its default sizes;
  # this one failed inside the selection with 'replacement has 1 row'. Pinned
  # identically in test_matching.py.
  msg <- "n_per_condition must be a positive whole number"
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"), schema, "english")
  pool <- build_pool(lex, make_continuous_design()$pool_filters)
  for (n_per_cell in list(NULL, 3L)) {
    d <- small_design(0L)
    d$n_per_cell <- n_per_cell
    expect_error(match_stimuli(small_pool(), d, tiny_schema()), msg, fixed = TRUE)
    d <- make_continuous_design()
    d$n_per_condition <- 0L
    d$n_per_cell <- n_per_cell
    expect_error(select_continuous_stimuli(pool, d, schema), msg, fixed = TRUE)
  }
})

null_tolerance_pool <- function() {
  # The anchors' concreteness has mean 3 and SD 1, so k = 0.01 admits one low
  # candidate and relaxes the window, while k = 2 admits three and does not.
  data.frame(
    id = 1:7,
    word = c("haa", "hab", "hac", "laa", "lab", "lac", "lad"),
    frequency = c(5.0, 5.5, 6.0, 1.0, 1.5, 2.0, 2.5),
    concreteness = c(2.0, 3.0, 4.0, 2.5, 3.0, 3.5, 9.0),
    stringsAsFactors = FALSE
  )
}

test_that("a_null_tolerance_is_read_as_modifylist_reads_it", {
  # A null in the schema's tolerance_k is dropped and k falls back to 2; a null in
  # the design's deletes the schema's value. The Python engine raised a TypeError on
  # either. Pinned identically in test_matching.py.
  tight <- list(matching = list(tolerance_k = list(concreteness = 0.01)))
  relaxed <- match_stimuli(null_tolerance_pool(), small_design(3L), tight)
  expect_false(is.null(attr(relaxed, "audit")))
  deleted <- match_stimuli(null_tolerance_pool(),
                           small_design(3L, matching = list(
                             tolerance_k = list(concreteness = NULL))), tight)
  expect_null(attr(deleted, "audit"))
  dropped <- match_stimuli(null_tolerance_pool(), small_design(3L),
                           list(matching = list(tolerance_k = list(concreteness = NULL))))
  expect_null(attr(dropped, "audit"))
  expect_identical(dropped$word, deleted$word)
  expect_identical(dropped$word, c("haa", "hab", "hac", "laa", "lab", "lac"))
})

test_that("a_schema_without_a_matching_block_is_accepted", {
  # Pinned identically in test_matching.py, where both selectors raised KeyError.
  expect_equal(nrow(match_stimuli(small_pool(), small_design(3L), list())), 6L)
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"), schema, "english")
  pool <- build_pool(lex, make_continuous_design()$pool_filters)
  expect_equal(nrow(select_continuous_stimuli(pool, make_continuous_design(), list())), 40L)
})

test_that("selection ignores unused columns and the seed", {
  # Metamorphic invariants: an inert extra column must not steer selection, and
  # the schema seed only ever reaches the shuffle keys, never the matcher.
  base <- match_stimuli(small_pool(), small_design(3L), tiny_schema())
  with_extra <- small_pool()
  with_extra$unused_norm <- c(9.9, 1.2, 5.5, 0.1, 7.7, 3.3, 2.2, 8.8)
  seeded <- tiny_schema()
  seeded$seed <- 99L
  expect_identical(match_stimuli(with_extra, small_design(3L), tiny_schema())$word, base$word)
  expect_identical(match_stimuli(small_pool(), small_design(3L), seeded)$word, base$word)
})

test_that("the matching module uses the shared rounder on distance paths", {
  # The 9-dp distance and cost roundings must go through .round_dp: native
  # round() pairs with numpy's different scale-rint-unscale algorithm. The two
  # remaining native calls are the 0-dp even-spread index sites, which are
  # half-even on exactly representable halves in both engines and pinned by the
  # committed goldens -- converting them would change selections.
  # Reads the package source, which only a source checkout has: R CMD check runs
  # the tests from lexsync.Rcheck/tests/testthat, where the installed copy holds a
  # lazy-load database and no R/ directory. Skip there rather than fail, the same
  # way test-config.R skips its repository-level checks.
  path <- testthat::test_path("..", "..", "R", "matching.R")
  skip_if_not(file.exists(path), "package sources not available")
  src <- readLines(path)
  src <- sub("#.*$", "", src)   # comments legitimately mention round()
  hits <- sum(lengths(regmatches(src, gregexpr("(?<![._[:alnum:]])round\\(", src, perl = TRUE))))
  expect_identical(hits, 2L)
})

# ---- the tie-break rule ------------------------------------------------------
# Lengths and neighbourhood counts are whole numbers and frequencies carry two
# decimals, so exact ties decide most picks. matching.tie_break chooses how: `hash`, the
# default, gives a tie to the smaller keyed SHA-256 of the word, and `bytes`, the rule of
# lexsync 0.1, to the spelling that sorts first. Twinned with test_matching.py, which
# pins the same keys, words and pairs.

# Computed here and not through the package, so the expectations below do not rest on
# the function under test.
tie_digest <- function(words) {
  vapply(words, function(w) digest::digest(enc2utf8(paste0("lexsync-tie-v1|", w)),
                                           algo = "sha256", serialize = FALSE),
         character(1), USE.NAMES = FALSE)
}
by_digest <- function(words) words[order(tie_digest(words), method = "radix")]

test_that("the_tie_key_is_identical_across_engines", {
  # An English, a Spanish and a Chinese word, the last two written as escapes so that
  # the source stays ASCII.
  expect_identical(.tie_keys(c("cat", "año", "中文")),
                   c("b9d1fe3608e2667c6c6782afccc91b43caeb9aede31bfb89e61407bb1def5df0",
                     "a3eb8cd8d71694705bf6dee05bac085f3df1e93f9771978f55389420979d5f3c",
                     "be465219474dd1ca446c19e4185cdc870f4e605cfd25e1f462c50aae7997bada"))
  expect_identical(.tie_keys("cat"), tie_digest("cat"))
})

tie_pool <- function() {
  # Four B candidates lie at x = 1 and two at x = 3, as do the anchors, so every pick is
  # an exact tie at distance 0. The keyed hash reverses the spelling order of bat, cat,
  # dog and eel.
  data.frame(id = 1:9,
             word = c("kiwi", "lime", "plum", "bat", "cat", "dog", "eel", "axe", "dot"),
             frequency = c(6.0, 6.1, 6.2, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5),
             x = c(1, 1, 3, 1, 1, 1, 1, 3, 3), stringsAsFactors = FALSE)
}

test_that("hash_tie_break_orders_exact_ties_by_the_keyed_digest", {
  pool <- tie_pool()
  by_bytes <- match_stimuli(pool, x_design(3L, list(tie_break = "bytes")), x_schema())
  expect_identical(by_bytes$word[by_bytes$condition == "B"], c("bat", "cat", "axe"))
  by_hash <- match_stimuli(pool, x_design(3L, list(tie_break = "hash")), x_schema())
  expect_identical(by_hash$word[by_hash$condition == "A"], c("kiwi", "lime", "plum"))
  expected <- c(by_digest(c("bat", "cat", "dog", "eel"))[1:2], by_digest(c("axe", "dot"))[1])
  expect_identical(expected, c("eel", "dog", "dot"))
  expect_identical(by_hash$word[by_hash$condition == "B"], expected)
  # The schema may set the rule, and a design's own setting overrides it.
  as_0_1 <- x_schema()
  as_0_1$matching$tie_break <- "bytes"
  expect_identical(match_stimuli(pool, x_design(3L), as_0_1)$word, by_bytes$word)
  expect_identical(match_stimuli(pool, x_design(3L, list(tie_break = "hash")), as_0_1)$word,
                   by_hash$word)
})

test_that("the_tie_break_defaults_to_hash", {
  # With no rule in the design or the schema, the keyed hash breaks exact ties. The
  # default was `bytes` until the demonstrations moved to the hash.
  expect_identical(.resolve_tie_break(list(), list()), "hash")
  pool <- tie_pool()
  by_default <- match_stimuli(pool, x_design(3L), x_schema())
  expect_identical(by_default$word,
                   match_stimuli(pool, x_design(3L, list(tie_break = "hash")), x_schema())$word)
  expect_identical(by_default$word[by_default$condition == "B"], c("eel", "dog", "dot"))
})

test_that("an_unknown_tie_break_rule_is_refused", {
  expect_error(match_stimuli(tie_pool(), x_design(3L, list(tie_break = "alphabetical")),
                             x_schema()),
               "lexsync: unknown tie_break policy 'alphabetical'. Known policies: hash, bytes.",
               fixed = TRUE)
})

tie_pairs_pool <- function(a_x, b_x) {
  # In spelling order A holds ash, beech, cedar and elm, which the keyed hash orders
  # beech, cedar, ash, elm, and B holds bat, cat, dog and eel, which it reverses.
  data.frame(id = 1:8,
             word = c("ash", "beech", "cedar", "elm", "bat", "cat", "dog", "eel"),
             frequency = c(6.0, 6.1, 6.2, 6.3, 2.0, 2.1, 2.2, 2.3),
             x = c(a_x, b_x), stringsAsFactors = FALSE)
}

test_that("hash_tie_break_orders_joint_pairs_by_hash_rank", {
  # Every pair costs 0, so the pair order alone decides which items are kept.
  pool <- tie_pairs_pool(rep(1, 4), rep(1, 4))
  by_bytes <- match_stimuli(pool, x_design(2L, list(method = "joint", tie_break = "bytes")),
                            x_schema())
  expect_identical(unname(x_pairs(by_bytes)), c("ash+bat", "beech+cat"))
  expect_identical(by_digest(c("ash", "beech", "cedar", "elm"))[1:2], c("beech", "cedar"))
  expect_identical(by_digest(c("bat", "cat", "dog", "eel"))[1:2], c("eel", "dog"))
  by_hash <- match_stimuli(pool, x_design(2L, list(method = "joint", tie_break = "hash")),
                           x_schema())
  expect_identical(unname(x_pairs(by_hash)), c("beech+eel", "cedar+dog"))
  expect_identical(by_hash$word[by_hash$set == 1L], c("beech", "eel"))
})

test_that("hash_tie_break_decides_the_overlap_cap", {
  # Every row lies at the same distance from the other condition's centroid, so the
  # tie-break alone decides which two rows of each condition survive the cap. A cap that
  # kept the first two rows by position would keep ash, beech, bat and cat, and the hash
  # order would then pair beech with cat.
  pool <- tie_pairs_pool(rep(1, 4), rep(1, 4))
  a <- pool[pool$frequency > 5, , drop = FALSE]
  b <- pool[pool$frequency < 5, , drop = FALSE]
  by_bytes <- match_joint(list(a, b), c("A", "B"), "x", c(x = 0), c(x = 1), 2L, cap = 2L)
  expect_identical(unname(x_pairs(by_bytes)), c("ash+bat", "beech+cat"))
  by_hash <- match_joint(list(a, b), c("A", "B"), "x", c(x = 0), c(x = 1), 2L, cap = 2L,
                         tie_break = "hash")
  expect_identical(unname(x_pairs(by_hash)), c("beech+eel", "cedar+dog"))
})

test_that("hash_tie_break_numbers_the_optimal_pairs_by_hash_rank", {
  # Two pairs cost 0 and every other pair costs more, so the optimum is unique and the
  # two engines' solvers cannot differ on it. Both pairs cost the same, and the
  # tie-break alone decides which of them is set 1. Among several equally cheap sets of
  # pairs, which set is kept is the solver's choice, which is why this test no longer
  # asks the tie-break to decide that.
  skip_if_not_installed("clue")
  pool <- tie_pairs_pool(c(1, 2, 10, 20), c(1, 2, 30, 40))
  by_bytes <- match_stimuli(pool, x_design(2L, list(method = "optimal", tie_break = "bytes")),
                            x_schema())
  expect_identical(unname(x_pairs(by_bytes)), c("ash+bat", "beech+cat"))
  expect_identical(by_bytes$word[by_bytes$set == 1L], c("ash", "bat"))
  by_hash <- match_stimuli(pool, x_design(2L, list(method = "optimal", tie_break = "hash")),
                           x_schema())
  expect_identical(unname(x_pairs(by_hash)), c("ash+bat", "beech+cat"))
  expect_identical(by_hash$word[by_hash$set == 1L], c("beech", "cat"))
})

# ---- exact optimal matching ---------------------------------------------------
# `optimal` selects the n pairs of least summed distance, the k-cardinality assignment
# problem, solved through a padded square assignment (Volgenant, 2004). Twinned with
# test_matching.py, which builds the same fixtures from the same formula and pins the
# same summed distance.

# Three continuous dimensions from fixed quadratic residues, so both engines build the
# same pool without a random number generator. Every intermediate is a whole number
# below 2^53, so the arithmetic is exact in both. A linear formula would repeat the same
# distance along every diagonal of the cost matrix.
formula_pool <- function(prefix, ks, shift = 0) {
  k <- as.numeric(ks)
  data.frame(word = sprintf("%s%04d", prefix, as.integer(k)),
             d1 = ((k * k * 7919 + k * 13 + 1) %% 10007) / 10007 + shift,
             d2 = ((k * k * 104729 + k * 7 + 3) %% 10009) / 10009,
             d3 = ((k * k * 3571 + k * 3 + 5) %% 10037) / 10037,
             stringsAsFactors = FALSE)
}

formula_dims <- c("d1", "d2", "d3")

solve_pairs <- function(method, a, b, n, ...) {
  fn <- if (identical(method, "optimal")) match_optimal else match_joint
  k <- length(formula_dims)
  fn(list(a, b), c("A", "B"), formula_dims, rep(0, k), rep(1, k), n, ...)
}

summed_distance <- function(out) {
  a <- out[out$condition == "A", , drop = FALSE]
  b <- out[out$condition == "B", , drop = FALSE]
  a <- as.matrix(a[order(a$set), formula_dims]); b <- as.matrix(b[order(b$set), formula_dims])
  sum(sqrt(rowSums((a - b)^2)))
}

# Every ordered choice of n distinct items out of m, one per row.
injections <- function(m, n) {
  if (n == 0L) return(matrix(integer(0), 1L, 0L))
  do.call(rbind, lapply(seq_len(m), function(first) {
    rest <- injections(m - 1L, n - 1L)
    others <- setdiff(seq_len(m), first)
    cbind(first, matrix(others[rest], nrow(rest)))
  }))
}

brute_force <- function(a, b, n) {
  za <- as.matrix(a[, formula_dims]); zb <- as.matrix(b[, formula_dims])
  cost <- sqrt(Reduce(`+`, lapply(seq_len(ncol(za)), function(d)
    outer(za[, d], zb[, d], "-")^2)))
  cols <- injections(nrow(zb), n)
  best <- Inf
  for (rows in asplit(utils::combn(nrow(za), n), 2L)) {
    for (r in seq_len(nrow(cols))) {
      best <- min(best, sum(cost[cbind(rows, cols[r, ])]))
    }
  }
  best
}

test_that("optimal equals brute-force enumeration on small problems", {
  # The complete assignment kept its n cheapest pairs, which is not the cheapest set of
  # n pairs whenever the full assignment had to spend a good counterpart elsewhere.
  skip_if_not_installed("clue")
  for (p in list(c(6L, 6L, 3L), c(5L, 7L, 4L))) {
    m0 <- p[1]; m1 <- p[2]; n <- p[3]
    a <- formula_pool("a", seq_len(m0))
    b <- formula_pool("b", m0 + seq_len(m1))
    out <- solve_pairs("optimal", a, b, n)
    expect_identical(length(unique(out$set)), n)
    expect_lte(abs(summed_distance(out) - brute_force(a, b, n)), 1e-9)
  }
})

# The summed distance of the optimal selection on the 300 + 300 fixture with n = 30,
# pinned identically in test_matching.py so the two engines agree to 1e-9. An
# independent padded solve over the unrounded costs gave the same value.
optimal_sum_300_n30 <- 1.272647404213

test_that("optimal is never worse than joint", {
  # Greedy joint matching came within a few per cent of the optimum, and the old
  # optimal was 1.15 to 2.5 times it.
  skip_if_not_installed("clue")
  a <- formula_pool("a", 1:300, shift = 0.05)
  b <- formula_pool("b", 301:600)
  for (n in c(30L, 150L)) {
    opt <- summed_distance(solve_pairs("optimal", a, b, n))
    joint <- summed_distance(solve_pairs("joint", a, b, n))
    expect_lte(opt, joint + 1e-9)
    if (n == 30L) expect_lte(abs(opt - optimal_sum_300_n30), 1e-9)
  }
})

test_that("optimal solves a problem at the candidate cap within seconds", {
  # The complete assignment over two 1,200-row subpools took about 71 s.
  skip_on_cran()
  skip_if_not_installed("clue")
  a <- formula_pool("a", 1:1200, shift = 0.05)
  b <- formula_pool("b", 1201:2400)
  elapsed <- system.time(out <- solve_pairs("optimal", a, b, 80L))[["elapsed"]]
  expect_identical(length(unique(out$set)), 80L)
  expect_lt(elapsed, 10)
})

test_that("optimal does not depend on the pool order", {
  # Every pair costs 0, so the solver's preference among equal costs decides which
  # pairs are kept. Under bytes the subpools are put in spelling order first, so that
  # preference follows the spelling and not the order the rows arrived in.
  skip_if_not_installed("clue")
  pool <- tie_pairs_pool(rep(1, 4), rep(1, 4))
  for (rule in c("bytes", "hash")) {
    design <- x_design(2L, list(method = "optimal", tie_break = rule))
    forward <- match_stimuli(pool, design, x_schema())
    backward <- match_stimuli(pool[rev(seq_len(nrow(pool))), , drop = FALSE], design,
                              x_schema())
    expect_identical(forward$word, backward$word, label = rule)
  }
})

test_that("optimal fills overlapping conditions with distinct words", {
  # Every word sits in both conditions. Three zero-cost pairs exist only by using a pair
  # in both directions (haa with laa, laa with haa), which reuses both words. The
  # duplicate is dropped and a second solve over the unused words fills its place, so
  # the design gets its three sets under the default shortfall policy, as it does under
  # the other methods.
  skip_if_not_installed("clue")
  design <- overlapping_design(3L, "optimal")
  design$matching$shortfall <- "error"
  s <- match_stimuli(small_pool(), design, tiny_schema())
  expect_identical(length(unique(s$set)), 3L)
  expect_false(anyDuplicated(s$word) > 0L)
  pairs <- vapply(split(s$word, s$set), function(w) paste(sort(w), collapse = "+"),
                  character(1))
  # Which direction of a zero-cost pair the solver uses is a tie, so the two zero-cost
  # pairs are sets 1 and 2 in either order.
  expect_identical(sort(unname(pairs[1:2]), method = "radix"), c("haa+laa", "hab+lab"))
})

test_that("optimal fills n when the conditions share every word", {
  # With the same 300 words in both conditions, every pair costs the same in both
  # directions, and a single solve used about half of its pairs twice.
  skip_if_not_installed("clue")
  pool <- formula_pool("w", 1:300)
  for (n in c(30L, 80L)) {
    out <- solve_pairs("optimal", pool, pool, n)
    expect_identical(length(unique(out$set)), n)
    expect_false(anyDuplicated(out$word) > 0L)
  }
})

# The shipped English designs as lexsync 0.1 ran them, on en.csv. Repository-coupled: the
# full lexicon lives in corpora/, not in the package, so these skip on CRAN and outside
# the repository. The lexicon is read once for the three tests.
en_corpus <- local({
  cache <- NULL
  function() {
    if (is.null(cache)) {
      schema <- read_config(repo_path("config", "schema.yaml"))
      cache <<- list(schema = schema,
                     lexicon = load_lexicon(repo_path("corpora", "derived", "en.csv"),
                                            schema, "english"))
    }
    cache
  }
})

# A shipped design as lexsync 0.1 ran it. The demonstrations now read en_v2.csv, filter
# on its `nonstandard` column and leave out the words of an exclusion list. en.csv has no
# such column, and match_stimuli() does not read exclude_words, so both are dropped here
# and the design runs on en_corpus()'s en.csv.
as_in_0_1 <- function(name, tie_break = NULL) {
  design <- read_config(repo_path("config", paste0("design_", name, ".yaml")))
  filters <- design[["pool_filters"]]
  design[["pool_filters"]] <- filters[names(filters) != "nonstandard"]
  design[["exclude_words"]] <- NULL
  if (!is.null(tie_break)) {
    design[["matching"]] <- c(design[["matching"]], list(tie_break = tie_break))
  }
  design
}

initial_share <- function(words) mean(substr(words, 1L, 1L) %in% c("a", "b"))

test_that("hash_tie_break_returns_freqcontrast_initials_to_the_pool_rate", {
  # Under bytes, 61% of the low-frequency words begin with a or b, against 13% of the
  # condition's candidates. Under hash the share lies within 0.1 of the candidates',
  # and Cohen's d on each matched dimension moves by at most 0.01.
  en <- en_corpus()
  design <- as_in_0_1("en_freqcontrast", "bytes")
  pool <- build_pool(en$lexicon, design[["pool_filters"]])
  low <- Filter(function(cd) identical(cd[["name"]], "low_frequency"),
                design[["conditions"]])[[1]]
  candidates <- build_pool(pool, low[["define_by"]])
  by_bytes <- match_stimuli(pool, design, en$schema)
  by_hash <- match_stimuli(pool, as_in_0_1("en_freqcontrast", "hash"), en$schema)
  share <- initial_share(by_hash$word[by_hash$condition == "low_frequency"])
  expect_lte(abs(share - initial_share(candidates$word)), 0.1)
  for (dim in unlist(design[["match_on"]])) {
    d <- vapply(list(by_bytes, by_hash), function(s)
      cohens_d(s[[dim]][s$condition == "high_frequency"],
               s[[dim]][s$condition == "low_frequency"]), numeric(1))
    expect_lte(abs(d[1] - d[2]), 0.01, label = dim)
  }
})

test_that("hash_tie_break_spreads_the_ndensity_dense_initials", {
  # Under bytes every dense word of the joint design began with a or b (73 b, 7 a).
  en <- en_corpus()
  design <- as_in_0_1("en_ndensity", "hash")
  s <- match_stimuli(build_pool(en$lexicon, design[["pool_filters"]]), design, en$schema)
  expect_lte(initial_share(s$word[s$condition == "dense_neighbourhood"]), 0.25)
})

# The selections lexsync 0.1.1 committed for the two designs, both engines alike, as the
# SHA-256 of their word|condition|set lines in byte order. The committed stimuli now come
# from the screened lexicon, so the old ones are pinned here. Pinned identically in
# test_matching.py.
selections_0_1_1 <- c(
  en_freqcontrast = "f5a58e0486182d23309c921106c41fde9dd9533b1c990ef4c77b2a971b588595",
  en_ndensity = "f266d1b7611890cfba586b61efa04066616acbb89a3134a42dba09a9e4490a8b"
)

selection_digest <- function(s) {
  lines <- sort(paste(s$word, s$condition, as.integer(s$set), sep = "|"), method = "radix")
  digest::digest(enc2utf8(paste(lines, collapse = "\n")), algo = "sha256", serialize = FALSE)
}

test_that("bytes_tie_break_reproduces_the_0_1_selections", {
  # `bytes` must select again what lexsync 0.1.1 selected from en.csv, and the default,
  # now the keyed hash, must not.
  en <- en_corpus()
  for (name in names(selections_0_1_1)) {
    for (rule in list("bytes", NULL)) {
      design <- as_in_0_1(name, rule)
      s <- match_stimuli(build_pool(en$lexicon, design[["pool_filters"]]), design, en$schema)
      expect_identical(selection_digest(s) == selections_0_1_1[[name]], !is.null(rule),
                       info = paste(name, if (is.null(rule)) "default" else rule))
    }
  }
})
