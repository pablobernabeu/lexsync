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
  expect_identical(ds$lexsync_datasheet_version, "1.2")
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
  expect_identical(loaded$lexsync_datasheet_version, "1.2")
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

# ---- Datasheet v1.2: the counterbalancing that ran --------------------------
# test_datasheet.py asserts the same properties.

ds_priming_table <- function(conditions = c("related", "unrelated"), n_sets = 4L) {
  s <- rep(seq_len(n_sets), each = length(conditions))
  data.frame(item = s, set = s, condition = rep(conditions, n_sets),
             prime = paste0(rep(substr(conditions, 1L, 3L), n_sets), s),
             target = paste0("t", s), stringsAsFactors = FALSE)
}

ds_table_design <- function(...) {
  utils::modifyList(list(name = "p", language = "english", paradigm = "priming",
                         items = list(source = "table", path = "items/p.csv")),
                    list(...))
}

test_that("the datasheet records the realised lists", {
  # A Latin square without counterbalance.lists realises one list per condition, but
  # the record read counterbalance.lists with a default of 1, and the Methods text
  # said "1 list(s)". The latin_no_lists twin-edge case pins the same run.
  schema <- ds_schema()
  design <- ds_table_design()
  out <- counterbalance(ds_priming_table(), design, schema)
  ds <- build_datasheet(design, schema, NULL, out, "items/p.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  record <- ds$counterbalancing
  expect_identical(record$recipe, "latin_square_target")
  expect_identical(record$lists, 2L)
  expect_true(record$complete)
  expect_length(record$issues, 0L)
  cells <- list()
  for (l in 1:2) for (cnd in c("related", "unrelated")) {
    cells[[length(cells) + 1L]] <- list(list = l, condition = cnd, n_trials = 2L)
  }
  expect_identical(record$cells, cells)
  expect_true(grepl("counterbalanced into 2 list(s) (a Latin-square rotation)",
                    methods_paragraph(ds), fixed = TRUE))
  md <- lexsync:::render_datasheet_md(ds)
  expect_true(grepl("## Counterbalanced lists", md, fixed = TRUE))
  expect_true(grepl("| 2 | unrelated | 2 |", md, fixed = TRUE))
})

test_that("build_datasheet accepts a frame without list", {
  # build_datasheet is exported, so it may be given a frame that was never
  # counterbalanced. The record then gives the lists counterbalance() would deal: one
  # per condition for a Latin square, else counterbalance.lists or 1.
  schema <- ds_schema()
  stim <- ds_priming_table()
  files <- list(stimuli = NULL, experiments = list())
  ds <- build_datasheet(ds_table_design(), schema, NULL, stim, "items/p.csv", files, 2026,
                        engine = "R")
  expect_identical(ds$counterbalancing$lists, 2L)
  expect_length(ds$counterbalancing$cells, 0L)
  four <- build_datasheet(ds_table_design(counterbalance = list(lists = 4L)), schema, NULL,
                          stim, "items/p.csv", files, 2026, engine = "R")
  expect_identical(four$counterbalancing$lists, 4L)
  corpus <- build_datasheet(ds_design(), schema, NULL, ds_stim(), "x.csv", files, 2026,
                            engine = "R")
  expect_identical(corpus$counterbalancing$lists, 1L)
  unset <- ds_design()
  unset$counterbalance <- NULL
  expect_identical(build_datasheet(unset, schema, NULL, ds_stim(), "x.csv", files, 2026,
                                   engine = "R")$counterbalancing$lists, 1L)
})

test_that("the datasheet records the recipe counterbalance applied", {
  # The record inferred the recipe from items.source while counterbalance() dispatched
  # on the paradigm, so a table-sourced lexical-decision design was recorded as a
  # Latin-square rotation it never had.
  schema <- ds_schema()
  stim <- data.frame(target = c("a", "b"), condition = c("word", "pseudoword"),
                     set = c(1, 1), stringsAsFactors = FALSE)
  files <- list(stimuli = NULL, experiments = list())
  design <- list(name = "t", language = "english", paradigm = "lexical_decision",
                 items = list(source = "table", path = "items/t.csv"),
                 counterbalance = list(lists = 1L))
  ds <- build_datasheet(design, schema, NULL, stim, "items/t.csv", files, 2026, engine = "R")
  expect_identical(ds$counterbalancing$recipe, "factorial")
  expect_false(grepl("Latin-square", methods_paragraph(ds), fixed = TRUE))
  design$paradigm <- "priming"
  design$events <- list(list(type = "text", content = "{target}", duration_ms = 800L))
  ds <- build_datasheet(design, schema, NULL, stim, "items/t.csv", files, 2026, engine = "R")
  expect_identical(ds$counterbalancing$recipe, "latin_square_target")
  design$counterbalance <- list(lists = 1L, recipe = "factorial")
  ds <- build_datasheet(design, schema, NULL, stim, "items/t.csv", files, 2026, engine = "R")
  expect_identical(ds$counterbalancing$recipe, "factorial")
})

test_that("the datasheet lists every experiment file", {
  # The record listed the three experiment scripts only, so it could not verify the
  # loop tables, which hold the trial order and the trigger codes those experiments
  # present. It now lists every file export_experiments() wrote.
  schema <- ds_schema()
  design <- ds_table_design(counterbalance = list(lists = 2L))
  stim <- counterbalance(ds_priming_table(), design, schema)
  out <- tempfile("ds"); dir.create(out)
  res <- export_experiments(stim, design, schema, out)
  ds <- build_datasheet(design, schema, NULL, stim, "items/p.csv",
                        list(stimuli = NULL, experiments = res), 2026, engine = "R")
  files <- vapply(ds$artifacts, function(a) a$file, character(1))
  expect_identical(files, res$files)
  expect_identical(basename(files)[-(1:4)], c(
    "p_english_psychopy.csv", "p_english_list1_opensesame.csv",
    "p_english_list1_opensesame_text.csv", "p_english_list2_opensesame.csv",
    "p_english_list2_opensesame_text.csv"))
  expect_true(all(nchar(vapply(ds$artifacts, function(a) a$sha256, character(1))) == 64L))
})

test_that("the datasheet records the presentation versions", {
  schema <- ds_schema()
  design <- ds_table_design(counterbalance = list(lists = 2L))
  ds <- build_datasheet(design, schema, NULL, counterbalance(ds_priming_table(), design, schema),
                        "items/p.csv", list(stimuli = NULL, experiments = list()), 2026,
                        engine = "R")
  expect_identical(ds$counterbalancing$versions, 2L)
  expect_identical(ds$counterbalancing$assignment,
                   "version = ((participant - 1) mod 2) + 1 unless a version is given at launch")
  expect_true(grepl(paste("generated for PsychoPy, OpenSesame and jsPsych. Each participant",
                          "was presented one of the 2 lists, assigned in rotation by",
                          "participant number. The selection"),
                    methods_paragraph(ds), fixed = TRUE))
  expect_true(grepl(paste("- **Presentation versions:** 2, assigned as version =",
                          "((participant - 1) mod 2) + 1 unless a version is given at launch"),
                    lexsync:::render_datasheet_md(ds), fixed = TRUE))
  # One version: nothing to assign, and nothing said about it.
  single <- build_datasheet(ds_design(), schema, NULL, ds_stim(), "x.csv",
                            list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_identical(single$counterbalancing$versions, 1L)
  expect_false(grepl("Each participant was presented", methods_paragraph(single), fixed = TRUE))
  expect_false(grepl("Presentation versions", lexsync:::render_datasheet_md(single),
                     fixed = TRUE))
  # Replicates multiply the versions, and a frame without `list` counts the lists
  # counterbalance() would deal.
  reps <- do.call(rbind, lapply(1:3, function(r) cbind(ds_priming_table(), replicate = r)))
  resampled <- utils::modifyList(design, list(resample = list(n_sets = 3L)))
  ds <- build_datasheet(resampled, schema, NULL, counterbalance(reps, resampled, schema),
                        "items/p.csv", list(stimuli = NULL, experiments = list()), 2026,
                        engine = "R")
  expect_identical(ds$counterbalancing$versions, 6L)
  expect_true(grepl(paste("Each participant was presented one of the 6 presentation",
                          "versions (one list of one item set), assigned in rotation by",
                          "participant number."), methods_paragraph(ds), fixed = TRUE))
  unlisted <- build_datasheet(resampled, schema, NULL, reps, "items/p.csv",
                              list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_identical(unlisted$counterbalancing$versions, 6L)
})

test_that("an incomplete rotation is described as incomplete", {
  schema <- ds_schema()
  design <- ds_table_design(counterbalance = list(lists = 2L))
  out <- counterbalance(ds_priming_table(c("identity", "related", "unrelated"), 6L),
                        design, schema)
  ds <- build_datasheet(design, schema, NULL, out, "items/p.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  issue <- "With 2 lists and 3 conditions, each item appears in only 2 of its 3 conditions."
  expect_false(ds$counterbalancing$complete)
  expect_identical(unlist(ds$counterbalancing$issues), issue)
  expect_true(grepl("counterbalanced into 2 list(s) (an incomplete Latin-square rotation)",
                    methods_paragraph(ds), fixed = TRUE))
  expect_true(grepl(paste0("- **Incomplete rotation:** ", issue),
                    lexsync:::render_datasheet_md(ds), fixed = TRUE))
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
  # missing value and drop out of any selection that uses the column.
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

# ---- Truthful prose, audit honesty and provenance completeness --------------
# test_datasheet.py asserts the same properties.

test_that("the datasheet records the equivalence settings the report used", {
  ds <- build_datasheet(ds_design(), ds_schema(), NULL, ds_stim(), "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_equal(ds$equivalence$bound_d, 0.5)
  expect_equal(ds$equivalence$alpha, 0.05)
})

test_that("the methods prose states the schema's bound, not a literal 0.5", {
  schema <- ds_schema()
  schema$equivalence$bound_d <- 0.4
  stim <- ds_stim()
  report <- match_report(stim, c("length", "frequency"), schema)
  ds <- build_datasheet(ds_design(), schema, report, stim, "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_equal(ds$equivalence$bound_d, 0.4)
  expect_true(grepl("within the 0.4-SD equivalence bound", methods_paragraph(ds), fixed = TRUE))
})

test_that("an undefined d forces the non-affirmative methods sentence", {
  # A controlled dimension constant at a different value in each condition has an
  # undefined d: the worst possible failure of the matching, not an excludable row.
  schema <- ds_schema()
  stim <- ds_stim()
  stim$length <- ifelse(stim$condition == "hi", 3, 4)
  report <- match_report(stim, c("length", "frequency"), schema)
  ds <- build_datasheet(ds_design(), schema, report, stim, "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  m <- methods_paragraph(ds)
  expect_true(grepl("Equivalence was not confirmed on every matched dimension", m, fixed = TRUE))
  expect_true(grepl("realised-control table", m, fixed = TRUE))
  expect_false(grepl("equivalence bound", m, fixed = TRUE))
  # The undefined cells render as the ASCII placeholder, matching the Python engine.
  md <- lexsync:::render_datasheet_md(ds)
  expect_true(grepl("| length | controlled | -- | -- |", md, fixed = TRUE))
})

test_that("a failed TOST on a controlled dimension blocks the affirmative sentence", {
  schema <- ds_schema()
  stim <- ds_stim()
  stim$length <- c(3, 9, 3, 4)  # defined d, but far too few items to pass a TOST
  report <- match_report(stim, c("length", "frequency"), schema)
  ds <- build_datasheet(ds_design(), schema, report, stim, "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  m <- methods_paragraph(ds)
  expect_true(grepl("Equivalence was not confirmed on every matched dimension", m, fixed = TRUE))
  expect_false(grepl("The realised control was close", m, fixed = TRUE))
})

test_that("the affirmative sentence prints the signed d beside its signed CI", {
  schema <- ds_schema()
  stim <- data.frame(word = paste0("w", 1:120),
                     condition = rep(c("hi", "lo"), each = 60),
                     length = c(rep(c(4, 5, 6), 20), rep(c(4.1, 5.1, 6.1), 20)),
                     frequency = rep(c(6, 3), each = 60),
                     set = rep(1:60, 2), stringsAsFactors = FALSE)
  report <- match_report(stim, c("length", "frequency"), schema)
  ds <- build_datasheet(ds_design(), schema, report, stim, "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  m <- methods_paragraph(ds)
  # The anchor's mean is below the comparison's, so the worst d is negative and
  # must be printed with its sign: |d| beside a signed CI misstated the direction.
  expect_true(grepl("was -0.12 (90% CI [", m, fixed = TRUE))
  expect_true(grepl("within the 0.5-SD equivalence bound", m, fixed = TRUE))
})

test_that("a pairwise method records the candidate cap instead of tolerance windows", {
  schema <- ds_schema()
  design <- ds_design()
  design$matching <- list(method = "joint")
  cp <- list(list(condition = "hi", n_candidates = 5000L),
             list(condition = "lo", n_candidates = 40L))
  ds <- build_datasheet(design, schema, NULL, ds_stim(), "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R",
                        candidate_pool = cp)
  expect_false("tolerance_k" %in% names(ds$selection))
  expect_identical(ds$selection$candidate_cap$cap, 1200L)
  expect_true(ds$selection$candidate_cap$applied$hi)
  expect_false(ds$selection$candidate_cap$applied$lo)
  expect_true(grepl(paste0("reduced to the 1200 candidates nearest the other ",
                           "condition's centroid before pairing"),
                    methods_paragraph(ds), fixed = TRUE))
  # The nearest-neighbour default keeps the windows it applies and takes no cap.
  plain <- build_datasheet(ds_design(), schema, NULL, ds_stim(), "x.csv",
                           list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_true("tolerance_k" %in% names(plain$selection))
  expect_false("candidate_cap" %in% names(plain$selection))
})

test_that("an uncapped pairwise run says nothing about the cap in the prose", {
  schema <- ds_schema()
  design <- ds_design()
  design$matching <- list(method = "optimal")
  ds <- build_datasheet(design, schema, NULL, ds_stim(), "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R",
                        candidate_pool = list(list(condition = "hi", n_candidates = 40L),
                                              list(condition = "lo", n_candidates = 40L)))
  expect_false(any(vapply(ds$selection$candidate_cap$applied, isTRUE, logical(1))))
  expect_false(grepl("nearest the other condition's centroid",
                     methods_paragraph(ds), fixed = TRUE))
})

test_that("a pool design's candidate pool is recorded like a corpus design's", {
  design <- ds_design()
  design$items <- list(source = "pool", path = "items/pool.csv")
  cp <- list(list(condition = "hi", n_candidates = 12L))
  ds <- build_datasheet(design, ds_schema(), NULL, ds_stim(), "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R",
                        candidate_pool = cp)
  expect_identical(ds$selection$candidate_pool, cp)
})

test_that("the datasheet records design and schema checksums and the matcher audit", {
  schema <- ds_schema()
  dpath <- tempfile("design", fileext = ".yaml"); writeLines("name: t", dpath)
  spath <- tempfile("schema", fileext = ".yaml"); writeLines("seed: 2026", spath)
  audit <- list(window_relaxations = list(list(condition = "lo",
                                               n_within_tolerance = 1L, n_needed = 2L)))
  nref <- list(source = "corpora/derived/en.csv", n_words = 25000L,
               sha256 = strrep("b", 64))
  ds <- build_datasheet(ds_design(), schema, NULL, ds_stim(), "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R",
                        design_path = dpath, schema_path = spath,
                        selection_audit = audit, neighbourhood_reference = nref)
  expect_identical(ds$reproducibility$design_sha256, sha256_file(dpath))
  expect_identical(ds$reproducibility$schema_sha256, sha256_file(spath))
  expect_identical(ds$selection$window_relaxations,
                   list(list(condition = "lo", n_within_tolerance = 1L, n_needed = 2L)))
  expect_identical(ds$selection$neighbourhood_reference, nref)
  # Existing call sites pass none of these, so nothing appears without them, and an
  # audit that recorded no relaxation leaves no key either.
  plain <- build_datasheet(ds_design(), schema, NULL, ds_stim(), "x.csv",
                           list(stimuli = NULL, experiments = list()), 2026, engine = "R",
                           selection_audit = list(window_relaxations = list()))
  expect_false("design_sha256" %in% names(plain$reproducibility))
  expect_false("schema_sha256" %in% names(plain$reproducibility))
  expect_false("window_relaxations" %in% names(plain$selection))
  expect_false("neighbourhood_reference" %in% names(plain$selection))
})

test_that("the datasheet records the candidates excluded for a missing value", {
  # A candidate missing a matched dimension is excluded before anything is selected,
  # and the record says how many each condition lost. The field is absent when nothing
  # was excluded, so the datasheets of complete pools do not change. Twinned with
  # test_datasheet.py.
  audit <- list(incomplete_dropped = list(list(condition = "hi", n = 3L),
                                          list(condition = "lo", n = 1L)))
  ds <- build_datasheet(ds_design(), ds_schema(), NULL, ds_stim(), "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R",
                        selection_audit = audit)
  expect_identical(ds$selection$incomplete_dropped,
                   list(list(condition = "hi", n = 3L), list(condition = "lo", n = 1L)))
  plain <- build_datasheet(ds_design(), ds_schema(), NULL, ds_stim(), "x.csv",
                           list(stimuli = NULL, experiments = list()), 2026, engine = "R",
                           selection_audit = list(window_relaxations = list()))
  expect_false("incomplete_dropped" %in% names(plain$selection))
  # The excluded candidates never reach the pairwise cap, so a condition the exclusion
  # brings under it is recorded as uncapped.
  design <- ds_design()
  design$matching <- list(method = "joint")
  capped <- build_datasheet(design, ds_schema(), NULL, ds_stim(), "x.csv",
                            list(stimuli = NULL, experiments = list()), 2026, engine = "R",
                            candidate_pool = list(list(condition = "hi", n_candidates = 1250L),
                                                  list(condition = "lo", n_candidates = 1300L)),
                            selection_audit = list(incomplete_dropped = list(
                              list(condition = "hi", n = 100L))))
  expect_identical(capped$selection$candidate_cap$applied, list(hi = FALSE, lo = TRUE))
})

test_that("the Methods text counts only the candidates that could be matched", {
  # The candidate pool counts every word in a condition's window, the ones excluded for
  # a missing matched value among them. Those were never eligible, so the Methods text
  # takes them off, and here the exclusion makes 'hi' the smaller condition. Twinned
  # with test_datasheet.py.
  ds <- build_datasheet(ds_design(), ds_schema(), NULL, ds_stim(), "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R",
                        candidate_pool = list(list(condition = "hi", n_candidates = 30L),
                                              list(condition = "lo", n_candidates = 25L)),
                        selection_audit = list(incomplete_dropped = list(
                          list(condition = "hi", n = 14L))))
  m <- methods_paragraph(ds)
  expect_true(grepl("The smallest condition was selected from 16 eligible candidates", m,
                    fixed = TRUE))
  # A record read back from its JSON renders the same text.
  out <- tempfile("ds"); dir.create(out)
  paths <- write_datasheet(ds, file.path(out, "d.json"), file.path(out, "d.md"))
  loaded <- jsonlite::fromJSON(paths[1], simplifyVector = FALSE)
  expect_identical(methods_paragraph(loaded), m)
})

test_that("the versions block records the OS and the parsing packages", {
  v <- lexsync:::.versions_R("R")
  expect_true(all(c("yaml", "stringi", "os") %in% names(v)))
  expect_identical(v$os, paste(Sys.info()[["sysname"]], Sys.info()[["machine"]]))
})

test_that("the analysis note is truthful about Python mixed-model tooling", {
  ds <- build_datasheet(ds_design(), ds_schema(), NULL, ds_stim(), "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_true(grepl("lme4 syntax", ds$analysis$note, fixed = TRUE))
  expect_true(grepl("statsmodels MixedLM", ds$analysis$note, fixed = TRUE))
  expect_false(grepl("pymer4/statsmodels", ds$analysis$note, fixed = TRUE))
  expect_true(grepl("post-selection diagnostics", ds$analysis$note, fixed = TRUE))
})

test_that("a dotted model term earns the Patsy quoting note", {
  ds <- build_datasheet(ds_pair_design(), ds_schema(), NULL, ds_pair_stim(), "items/p.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_true(grepl('Q("...")', ds$analysis$note, fixed = TRUE))
  plain <- build_datasheet(list(name = "c", language = "english",
                                continuous = list(predictor = "frequency",
                                                  controls = list("length")),
                                n_per_condition = 4, counterbalance = list(lists = 1)),
                           ds_schema(), NULL, ds_stim(), "x.csv",
                           list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_false(grepl("Patsy", plain$analysis$note, fixed = TRUE))
})

# ---- Numbers are printed by lexsync, not by each language's printf ----------
# sprintf() hands decimal ties to the platform's C library: R 4.6.1 on Windows
# printed 0.165 at two places as "0.16" where Python printed "0.17", and an exact
# tie such as -0.125 goes to the even digit in Python. Every number in the
# Markdown and the Methods paragraph now goes through .fmt_dp, which rounds half
# away from zero by the package's own arithmetic. test_datasheet.py pins the same
# strings.

tie_rows <- function() {
  list(
    list(dimension = "length", role = "controlled", cohens_d = 0.165,
         ci_low = -0.125, ci_high = 0.455, var_ratio = 0.0825, tost_p = 9e-04,
         equivalent = TRUE),
    list(dimension = "old20", role = "controlled", cohens_d = 0.1, ci_low = -0.2,
         ci_high = 0.3, var_ratio = 1, tost_p = 0, equivalent = TRUE),
    list(dimension = "frequency", role = "manipulated/free", cohens_d = 5.27,
         ci_low = 4.72, ci_high = 5.83, var_ratio = 0.21, tost_p = 1,
         equivalent = FALSE))
}

test_that("decimal ties print the same in the Methods paragraph and the table", {
  ds <- build_datasheet(ds_design(), ds_schema(), NULL, ds_stim(), "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  ds$realised_control <- tie_rows()
  expect_true(grepl("was 0.17 (90% CI [-0.13, 0.46]), within", methods_paragraph(ds),
                    fixed = TRUE))
  md <- lexsync:::render_datasheet_md(ds)
  # The TOST p is printed to four places, and a stored 0 as a bound.
  expect_true(grepl("| length | controlled | 0.17 | [-0.13, 0.46] | 0.08 | 0.0009 |",
                    md, fixed = TRUE))
  expect_true(grepl("| old20 | controlled | 0.10 | [-0.20, 0.30] | 1.00 | < 0.0001 |",
                    md, fixed = TRUE))
  expect_true(grepl("| frequency | manipulated/free | 5.27 | [4.72, 5.83] | 0.21 | 1.0000 |",
                    md, fixed = TRUE))
})

test_that("a continuous design prints its span and correlations through the formatter", {
  ds <- build_datasheet(list(name = "c", language = "english",
                             continuous = list(predictor = "frequency",
                                               controls = list("length")),
                             n_per_condition = 4, counterbalance = list(lists = 1)),
                        ds_schema(), NULL, ds_stim(), "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  ds$realised_control <- list(
    list(dimension = "frequency", role = "predictor", pearson_r = NULL,
         predictor_span = 0.165),
    list(dimension = "length", role = "control", pearson_r = -0.0825,
         predictor_span = 0.165))
  m <- methods_paragraph(ds)
  expect_true(grepl("span frequency (a span of 0.17) continuously", m, fixed = TRUE))
  expect_true(grepl("correlation was |r| = 0.083,", m, fixed = TRUE))
  md <- lexsync:::render_datasheet_md(ds)
  expect_true(grepl("| frequency | predictor | -- | 0.165 |", md, fixed = TRUE))
  expect_true(grepl("| length | control | -0.083 | 0.165 |", md, fixed = TRUE))
})

ds_files <- function() list(stimuli = NULL, experiments = list())

test_that("the_datasheet_records_the_tie_break_rule", {
  # A matched design records the rule that broke exact ties, with its salt under hash. A
  # design that runs no matcher records none. Twinned with test_datasheet.py.
  schema <- ds_schema()
  ds <- build_datasheet(ds_design(), schema, NULL, ds_stim(), "x.csv", ds_files(), 2026)
  expect_identical(ds$selection[["tie_break"]], list(rule = "bytes"))
  hashed <- ds_design()
  hashed$matching <- list(tie_break = "hash")
  ds <- build_datasheet(hashed, schema, NULL, ds_stim(), "x.csv", ds_files(), 2026)
  expect_identical(ds$selection[["tie_break"]], list(rule = "hash", salt = "lexsync-tie-v1"))
  schema_hash <- schema
  schema_hash$matching$tie_break <- "hash"
  joint <- ds_design()
  joint$matching <- list(method = "joint")
  ds <- build_datasheet(joint, schema_hash, NULL, ds_stim(), "x.csv", ds_files(), 2026)
  expect_identical(ds$selection[["tie_break"]], list(rule = "hash", salt = "lexsync-tie-v1"))
  gen <- build_datasheet(ds_gen_design(), schema, NULL, ds_gen_stim(), "x.csv", ds_files(),
                         2026)
  expect_null(gen$selection[["tie_break"]])
  cont <- build_datasheet(list(name = "c", language = "english",
                               continuous = list(predictor = "frequency",
                                                 controls = list("length")),
                               n_per_condition = 4L, counterbalance = list(lists = 1)),
                          schema, NULL, ds_stim(), "x.csv", ds_files(), 2026)
  expect_null(cont$selection[["tie_break"]])
})

test_that("selection_transparency_says_the_seed_does_not_select", {
  # The section said selection was deterministic given the seed, which plays no part in
  # it, and that it was free of item-selection bias. Twinned with test_datasheet.py.
  schema <- ds_schema()
  cp <- list(list(condition = "hi", n_candidates = 40L),
             list(condition = "lo", n_candidates = 30L))
  lead <- paste("- Selection is a deterministic function of the materials source, the",
                "design and the schema, blind to any outcome measure, and does not depend",
                "on the seed, which fixes the trial order.")
  tail <- paste("Automating the choice removes the experimenter's discretion that Forster",
                "(2000) showed can bias item selection.")
  md <- lexsync:::render_datasheet_md(build_datasheet(ds_design(), schema, NULL, ds_stim(),
                                                      "x.csv", ds_files(), 2026,
                                                      candidate_pool = cp))
  expect_false(grepl("given the seed", md, fixed = TRUE))
  expect_false(grepl("free of item-selection bias", md, fixed = TRUE))
  expect_true(grepl(paste(lead, "Exact ties between equally close candidates are broken by",
                          "spelling, in byte order, as lexsync 0.1 did, so every tie goes",
                          "to the spelling that sorts first.", tail), md, fixed = TRUE))
  hashed <- ds_design()
  hashed$matching <- list(tie_break = "hash")
  md <- lexsync:::render_datasheet_md(build_datasheet(hashed, schema, NULL, ds_stim(),
                                                      "x.csv", ds_files(), 2026,
                                                      candidate_pool = cp))
  expect_true(grepl(paste(lead, "Exact ties between equally close candidates are broken by a",
                          "keyed hash of each word (salt lexsync-tie-v1), so no part of the",
                          "alphabet is favoured.", tail), md, fixed = TRUE))
  gen <- lexsync:::render_datasheet_md(build_datasheet(
    ds_gen_design(), schema, NULL, ds_gen_stim(), "x.csv", ds_files(), 2026,
    candidate_pool = list(list(condition = "words in band", n_candidates = 100L))))
  expect_true(grepl(paste(lead, tail), gen, fixed = TRUE))
})

test_that("the_methods_paragraph_says_the_seed_fixes_the_trial_order", {
  # The seed plays no part in selection, so the Methods text no longer presents it as
  # what makes the selection reproducible. Twinned with test_datasheet.py.
  schema <- ds_schema()
  ds <- build_datasheet(ds_design(), schema, NULL, ds_stim(), "x.csv", ds_files(), 2026)
  sentence <- sprintf(paste("The selection is deterministic and reproducible (lexsync %s),",
                            "and the seed (2026) fixes the trial order."),
                      ds$reproducibility$versions$lexsync)
  expect_true(grepl(sentence, methods_paragraph(ds), fixed = TRUE))
  cont <- build_datasheet(list(name = "c", language = "english",
                               continuous = list(predictor = "frequency",
                                                 controls = list("length")),
                               n_per_condition = 4L, counterbalance = list(lists = 1)),
                          schema, NULL, ds_stim(), "x.csv", ds_files(), 2026)
  expect_true(grepl(sentence, methods_paragraph(cont), fixed = TRUE))
  expect_false(grepl("(seed 2026;", paste(methods_paragraph(ds), methods_paragraph(cont)),
                     fixed = TRUE))
})

# The Methods paragraph is the part of the datasheet meant to be identical across
# engines; the rest of the Markdown names its engine and is excluded from the
# cross-engine diff. This engine renders the paragraph from the Python engine's
# committed record of en_freqcontrast, read back from JSON as a reader would, and it
# must match the paragraph the Python engine wrote. test_datasheet.py does the same
# from the R record.
test_that("the Methods paragraph from the Python record matches the Python rendering", {
  reports <- repo_path("output", "reports", message = "committed reports not available")
  base <- file.path(reports, "en_freqcontrast_english_datasheet_py")
  ds <- jsonlite::fromJSON(paste0(base, ".json"), simplifyVector = FALSE)
  md <- readLines(paste0(base, ".md"), encoding = "UTF-8", warn = FALSE)
  at <- match("## Methods paragraph", md)
  expect_false(is.na(at))
  expect_identical(methods_paragraph(ds), md[[at + 2L]])
})
