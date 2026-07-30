ds_stim <- function() {
  data.frame(word = c("cat", "dog", "car", "cap"), condition = c("hi", "hi", "lo", "lo"),
             set = c(1, 2, 1, 2), length = 3L, frequency = c(6, 6, 3, 3),
             n_density = 2L, old20 = 1.5, stringsAsFactors = FALSE)
}
ds_design <- function() {
  list(name = "t", language = "english", match_on = list("length", "n_density", "old20"),
       n_per_condition = 2L, counterbalance = list(lists = 1))
}
ds_gen_stim <- function() {
  data.frame(word = c("cat", "dog", "cag", "dop"),
             condition = c("word", "word", "pseudoword", "pseudoword"),
             set = c(1, 2, 1, 2), length = 3L, stringsAsFactors = FALSE)
}
ds_gen_design <- function(method = NULL) {
  items <- list(source = "generate", lexicon = "corpora/derived/en.csv")
  if (!is.null(method)) items$generation <- list(method = method)
  list(name = "g", language = "english", paradigm = "lexical_decision",
       items = items, n_per_condition = 2L, counterbalance = list(lists = 1))
}
ds_schema <- function() {
  yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
}

test_that("datasheet captures structure and realised control", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- ds_stim()
  report <- match_report(stim, c("length", "frequency", "n_density", "old20"), schema)
  ds <- build_datasheet(ds_design(), schema, report, stim, "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_identical(ds$lexsync_datasheet_version, "1.1")
  expect_equal(ds$reproducibility$seed, 2026)
  roles <- stats::setNames(vapply(ds$realised_control, function(r) r$role, character(1)),
                           vapply(ds$realised_control, function(r) r$dimension, character(1)))
  expect_identical(unname(roles["length"]), "controlled")
  expect_identical(unname(roles["frequency"]), "manipulated/free")
})

test_that("methods paragraph reads naturally and prereg template is emitted", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- ds_stim()
  report <- match_report(stim, c("length", "frequency"), schema)
  ds <- build_datasheet(ds_design(), schema, report, stim, "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  m <- methods_paragraph(ds)
  expect_true(grepl("matched item by item", m, fixed = TRUE))
  expect_true(grepl("0.5-SD equivalence bound", m, fixed = TRUE))
  out <- tempfile("ds"); dir.create(out)
  paths <- write_datasheet(ds, file.path(out, "d.json"), file.path(out, "d.md"))
  loaded <- jsonlite::fromJSON(paths[1], simplifyVector = FALSE)
  expect_identical(loaded$lexsync_datasheet_version, "1.1")
  md <- paste(readLines(paths[2], warn = FALSE), collapse = "\n")
  expect_true(grepl("Pre-registration template", md, fixed = TRUE))
})

test_that("datasheet builds for a table source without a report", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- data.frame(prime = c("a", "b"), target = c("x", "y"),
                     condition = c("r", "u"), set = c(1, 1), stringsAsFactors = FALSE)
  design <- list(name = "p", language = "english", paradigm = "priming",
                 items = list(source = "table", path = "items/p.csv"),
                 counterbalance = list(lists = 2))
  ds <- build_datasheet(design, schema, NULL, stim, "items/p.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_length(ds$realised_control, 0)
  expect_identical(ds$counterbalancing$recipe, "latin_square_target")
  expect_true(grepl("item table", methods_paragraph(ds), fixed = TRUE))
  expect_length(ds$dimensions, 0L)
})

test_that("the datasheet records the tolerance windows the matcher applied", {
  # The design-level override is what match_stimuli applies, so it is what the
  # provenance record must state; the schema defaults survive for the rest.
  schema <- ds_schema()
  design <- ds_design()
  design$matching <- list(tolerance_k = list(frequency = 0.111))
  ds <- build_datasheet(design, schema, NULL, ds_stim(), "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_equal(ds$selection$tolerance_k$frequency, 0.111)
  expect_equal(ds$selection$tolerance_k$length, 2.0)
  plain <- build_datasheet(ds_design(), schema, NULL, ds_stim(), "x.csv",
                           list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_equal(plain$selection$tolerance_k$frequency, 1.0)
})

test_that("the datasheet names the generator that ran", {
  schema <- ds_schema()
  ds <- build_datasheet(ds_gen_design("subsyllabic"), schema, NULL, ds_gen_stim(), "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_identical(ds$selection$generation_method, "subsyllabic")
  expect_identical(ds$selection$method,
                   "subsyllabic constituent swap (Wuggy-style, deterministic pseudowords)")
  expect_true(grepl("subsyllabic constituent swap", methods_paragraph(ds), fixed = TRUE))
  default <- build_datasheet(ds_gen_design(), schema, NULL, ds_gen_stim(), "x.csv",
                             list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_identical(default$selection$generation_method, "letter_substitution")
  expect_identical(default$selection$method,
                   "constrained letter substitution (deterministic pseudowords)")
})

test_that("the datasheet dimensions are filtered to the controlled ones", {
  schema <- ds_schema()
  gen <- build_datasheet(ds_gen_design("subsyllabic"), schema, NULL, ds_gen_stim(), "x.csv",
                         list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_identical(names(gen$dimensions), "length")
  corpus <- build_datasheet(ds_design(), schema, NULL, ds_stim(), "x.csv",
                            list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_identical(names(corpus$dimensions), names(schema$dimensions))
  # An empty block must serialise as an object, matching the Python engine.
  tbl <- build_datasheet(list(name = "p", language = "english", paradigm = "priming",
                              items = list(source = "table", path = "items/p.csv"),
                              counterbalance = list(lists = 2)),
                         schema, NULL, ds_gen_stim(), "items/p.csv",
                         list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  json <- as.character(jsonlite::toJSON(tbl$dimensions, auto_unbox = TRUE))
  expect_identical(json, "{}")
})

test_that("the datasheet reports the installed lexsync version", {
  ds <- build_datasheet(ds_design(), ds_schema(), NULL, ds_stim(), "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_identical(ds$reproducibility$versions$lexsync,
                   as.character(utils::packageVersion("lexsync")))
})

test_that("datasheet emits a regression model for a continuous design", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- data.frame(word = c("a", "b", "c", "d"), condition = "continuous",
                     frequency = c(2, 3, 4, 5), length = c(3, 4, 3, 4),
                     n_density = c(1, 2, 1, 2), old20 = c(1.5, 1.6, 1.5, 1.6),
                     stringsAsFactors = FALSE)
  design <- list(name = "c", language = "english",
                 continuous = list(predictor = "frequency",
                                   controls = list("length", "n_density", "old20")),
                 match_on = list("length", "n_density", "old20"),
                 n_per_condition = 4, matching = list(tolerance_k = list(length = 1.5)),
                 counterbalance = list(lists = 1))
  rep <- match_report_continuous(stim, "frequency", c("length", "n_density", "old20"), schema)
  ds <- build_datasheet(design, schema, rep, stim, "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_identical(ds$analysis$suggested_model,
                   "response ~ frequency + length + n_density + old20 + (1 + frequency | subject) + (1 | item)")
  expect_identical(ds$realised_control[[1]]$role, "predictor")
  expect_true("predictor" %in% names(ds$selection))
  # The control bands the matcher applied are part of the record.
  expect_equal(ds$selection$tolerance_k$length, 1.5)
  expect_equal(ds$selection$tolerance_k$old20, 2.0)
  expect_true(grepl("span frequency", methods_paragraph(ds), fixed = TRUE))
})

# ---- Datasheet v1.1: joined norms, and honesty about the pair path ----------
# Both were required by the rule that anything affecting item selection is recorded
# in the datasheet. test_datasheet.py asserts the same properties.

ds_pair_stim <- function() {
  df <- data.frame(item = c(1L, 1L, 2L, 2L), set = c(1L, 1L, 2L, 2L),
                   condition = rep(c("related", "unrelated"), 2),
                   prime = c("nurse", "window", "dog", "table"),
                   target = c("doctor", "doctor", "cat", "cat"),
                   stringsAsFactors = FALSE)
  # .join_member_norms gives every member the same dimensions.
  df[["prime.frequency"]] <- c(4.4, 4.1, 5.1, 4.7)
  df[["prime.length"]] <- c(5L, 6L, 3L, 5L)
  df[["target.frequency"]] <- c(5.0, 5.0, 4.8, 4.8)
  df[["target.length"]] <- c(6L, 6L, 3L, 3L)
  df[["pair.lev"]] <- c(6L, 5L, 3L, 4L)
  df[["pair.overlap"]] <- c(0, 0.16, 0, 0.2)
  df
}

ds_pair_design <- function() {
  list(name = "pc", language = "english", paradigm = "priming",
       items = list(source = "table", path = "items/p.csv",
                    members = list("prime", "target"), lexicon = "corpora/derived/en.csv"),
       continuous = list(predictor = "target.frequency",
                         controls = list("target.length", "pair.overlap")),
       n_per_condition = 2L, counterbalance = list(lists = 2))
}

test_that("the datasheet records the joined norm tables", {
  schema <- ds_schema()
  norms <- list(list(path = "norms/en_conc.csv", sha256 = strrep("a", 64), on = "word",
                     columns = list(list(column = "concreteness", n_matched = 900L,
                                         n_total = 1000L))))
  ds <- build_datasheet(ds_design(), schema, NULL, ds_stim(), "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R",
                        norms = norms)
  expect_identical(ds$materials_source$norms, norms)
  # Coverage is rendered, because the rows a norm table does not cover carry a
  # missing value and are then dropped from the pool by the tolerance windows.
  md <- lexsync:::render_datasheet_md(ds)
  expect_true(grepl("## Joined norms", md, fixed = TRUE))
  expect_true(grepl("900 / 1000", md, fixed = TRUE))
  expect_true(grepl("en_conc.csv", methods_paragraph(ds), fixed = TRUE))
})

test_that("a design without norms has no norms key", {
  # Not `"norms": null`: every datasheet would then carry a key for a feature the
  # design does not use.
  ds <- build_datasheet(ds_design(), ds_schema(), NULL, ds_stim(), "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_false("norms" %in% names(ds$materials_source))
})

test_that("the datasheet is honest that the pair path selects", {
  # .cross_engine answered "n/a (user-supplied items)" for every table design. That is
  # true of a plain item table, but a pair-keyed continuous design performs a real
  # selection over it, and that selection is byte-identical across engines -- so the
  # record understated the guarantee on the one path that most needs it.
  schema <- ds_schema()
  stim <- ds_pair_stim()
  rep <- match_report_continuous(stim[c(1, 3), , drop = FALSE], "target.frequency",
                                 c("target.length", "pair.overlap"), schema)
  ds <- build_datasheet(ds_pair_design(), schema, rep, stim, "items/p.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_identical(ds$selection$cross_engine, "byte-identical")

  plain <- build_datasheet(list(name = "p", language = "english", paradigm = "priming",
                                items = list(source = "table", path = "items/p.csv"),
                                counterbalance = list(lists = 2)),
                           schema, NULL, stim, "items/p.csv",
                           list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_identical(plain$selection$cross_engine, "n/a (user-supplied items)")
  expect_null(plain$relational)
})

test_that("the datasheet separates member from relational dimensions", {
  schema <- ds_schema()
  stim <- ds_pair_stim()
  ds <- build_datasheet(ds_pair_design(), schema, NULL, stim, "items/p.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  rel <- ds$relational
  expect_identical(unlist(rel$members), c("prime", "target"))
  # n_pairs, because items$n_total counts ROWS -- one per pair per condition -- so a
  # reader comparing it against n_per_condition would find it doubled.
  expect_identical(rel$n_pairs, 2L)
  expect_identical(ds$items$n_total, 4L)
  # The member lexicon is where every member-level control came from, and nothing else
  # in the record names it: materials_source names the item table.
  expect_identical(rel$member_lexicon, "corpora/derived/en.csv")
  expect_identical(unlist(rel$member_dimensions), c("frequency", "length"))
  expect_identical(unlist(rel$relational_dimensions), c("pair.lev", "pair.overlap"))
  # A pair design joins every lexicon dimension onto each member, so the record lists
  # them all rather than the empty set a plain table design gets.
  expect_identical(names(ds$dimensions), names(schema$dimensions))
  md <- lexsync:::render_datasheet_md(ds)
  expect_true(grepl("## Pair-keyed items", md, fixed = TRUE))
  expect_true(grepl("re-expanded", md, fixed = TRUE))
})

test_that("the methods paragraph counts pairs, not items", {
  schema <- ds_schema()
  stim <- ds_pair_stim()
  rep <- match_report_continuous(stim[c(1, 3), , drop = FALSE], "target.frequency",
                                 c("target.length", "pair.overlap"), schema)
  ds <- build_datasheet(ds_pair_design(), schema, rep, stim, "items/p.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  m <- methods_paragraph(ds)
  expect_true(grepl("2 English prime-target pairs were selected", m, fixed = TRUE))
  expect_false(grepl("items were selected", m, fixed = TRUE))
})
