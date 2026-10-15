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
  # The design declares no conditions, so no window sets frequency apart.
  expect_identical(unname(roles["frequency"]), "uncontrolled")
})

test_that("every recorded path takes forward slashes", {
  # The materials source, the stimuli file and every artefact were recorded as given,
  # so a run handed Windows paths wrote backslashes where the Python engine writes
  # forward slashes. Pinned identically in test_datasheet.py.
  schema <- ds_schema()
  exps <- list(psychopy = "output\\experiments\\t.py",
               opensesame = "output\\experiments\\t.osexp",
               jspsych = "output\\experiments\\t.html",
               files = c("output\\experiments\\t.py", "output\\experiments\\t.osexp",
                         "output\\experiments\\t.html"))
  ds <- build_datasheet(ds_design(), schema, NULL, ds_stim(), "corpora\\derived\\x.csv",
                        list(stimuli = "output\\stimuli\\t_stimuli.csv",
                             descriptives = "output\\reports\\t_descriptives.csv",
                             experiments = exps),
                        2026, engine = "R", schema_path = "config\\schema.yaml")
  expect_identical(ds$materials_source$path, "corpora/derived/x.csv")
  expect_identical(ds$items$stimuli_file, "output/stimuli/t_stimuli.csv")
  expect_identical(vapply(ds$artifacts, function(a) a$file, character(1)),
                   c("output/stimuli/t_stimuli.csv", "output/reports/t_descriptives.csv",
                     "output/experiments/t.py", "output/experiments/t.osexp",
                     "output/experiments/t.html"))
  expect_identical(ds$reproducibility$schema_path, "config/schema.yaml")
})

test_that("realised control records the pair, the role and the raw difference", {
  # Each entry names the two conditions it contrasts and gives the raw difference. A
  # report without roles, as a direct call of match_report() gives, takes them from the
  # design: a dimension whose define_by windows differ is manipulated, one in match_on
  # controlled and any other uncontrolled. Every unmatched dimension was
  # "manipulated/free". Pinned identically in test_datasheet.py.
  schema <- ds_schema()
  stim <- ds_stim()
  design <- ds_design()
  design$conditions <- list(list(name = "hi", define_by = list(frequency = c(5, 7))),
                            list(name = "lo", define_by = list(frequency = c(2, 4))))
  report <- match_report(stim, c("length", "frequency", "n_density", "old20"), schema)
  ds <- build_datasheet(design, schema, report, stim, "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  rc <- stats::setNames(ds$realised_control,
                        vapply(ds$realised_control, function(r) r$dimension, character(1)))
  expect_identical(vapply(rc, function(r) r$role, character(1)),
                   c(length = "controlled", frequency = "manipulated",
                     n_density = "controlled", old20 = "controlled"))
  expect_identical(c(rc$frequency$condition, rc$frequency$reference), c("lo", "hi"))
  expect_identical(rc$frequency$mean_diff, 3)
  # A role the report carries is kept.
  report$comparisons$role <- "uncontrolled"
  kept <- build_datasheet(design, schema, report, stim, "x.csv",
                          list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_identical(unique(vapply(kept$realised_control, function(r) r$role, character(1))),
                   "uncontrolled")
})

# Only the label's first letter is raised. The Python twin's str.capitalize() lowered
# the rest, so a design labelled 'British English' drew from 'the British english
# lexicon' there. Pinned identically in test_datasheet.py.
test_that("the methods paragraph keeps the language label as written", {
  schema <- ds_schema()
  stim <- ds_stim()
  report <- match_report(stim, c("length", "frequency", "n_density", "old20"), schema)
  labels <- c("British English" = "British English", english = "English",
              "Chinese (Mandarin)" = "Chinese (Mandarin)")
  for (label in names(labels)) {
    design <- utils::modifyList(ds_design(), list(language = label))
    ds <- build_datasheet(design, schema, report, stim, "x.csv",
                          list(stimuli = NULL, experiments = list()), 2026, engine = "R")
    expect_true(grepl(paste0("from the ", labels[[label]], " lexicon"), methods_paragraph(ds),
                      fixed = TRUE), label = label)
  }
})

test_that("methods paragraph reads naturally and prereg template is emitted", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- ds_stim()
  report <- match_report(stim, c("length", "frequency"), schema)
  ds <- build_datasheet(ds_design(), schema, report, stim, "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  m <- methods_paragraph(ds)
  expect_true(grepl("matched item by item", m, fixed = TRUE))
  expect_true(grepl(paste("Two one-sided tests at a bound of 0.5 SD (alpha 0.05) supported",
                          "equivalence on 1 of 1 matched comparisons"), m, fixed = TRUE))
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
  # In POSIX form, as test_datasheet.py compares them: tempfile() gives backslashes on
  # Windows, and the record writes forward slashes.
  expect_identical(files, gsub("\\", "/", res$files, fixed = TRUE))
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
                          "participant number. Responses were collected"),
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

test_that("the datasheet names where the reaction time is timed from", {
  # The record called the outcome "reaction time or accuracy" without saying where a
  # reaction time starts, and the Methods text said nothing of the response window.
  # test_datasheet.py pins the same record and text.
  schema <- ds_schema()
  files <- list(stimuli = NULL, experiments = list())
  ds <- build_datasheet(ds_design(), schema, NULL, ds_stim(), "x.csv", files, 2026,
                        engine = "R")
  expect_identical(ds$presentation, list(response_windows = list(
    list(event = 3L, from = "onset", window_ms = 2800L))))
  expect_identical(ds$analysis$response, paste(
    "reaction time from the onset of `{word}`; responses collected for 2800 ms; a",
    "response ends the trial"))
  expect_true(grepl(paste("generated for PsychoPy, OpenSesame and jsPsych. Responses were",
                          "collected from target onset until 2800 ms after it, and a",
                          "response ended the trial. The selection"),
                    methods_paragraph(ds), fixed = TRUE))
  # A window that opens after the stimulus, for a design that delays the response.
  delayed <- utils::modifyList(ds_design(), list(events = list(
    list(type = "text", content = "{word}", duration_ms = 800L),
    list(type = "blank", duration_ms = 200L),
    list(type = "response", keys = c("f", "j"), timeout_ms = 1500L))))
  ds <- build_datasheet(delayed, schema, NULL, ds_stim(), "x.csv", files, 2026, engine = "R")
  expect_identical(ds$presentation$response_windows,
                   list(list(event = 3L, from = "offset", window_ms = 1500L)))
  expect_identical(ds$analysis$response, paste(
    "reaction time from the opening of a response window after the stimulus;",
    "responses collected for 1500 ms; a response ends the trial"))
  expect_true(grepl(paste(" Responses were collected in a 1500 ms window that opened after",
                          "the stimulus, and a response ended the trial."),
                    methods_paragraph(ds), fixed = TRUE))
  # A target whose duration varies by trial ends its window a fixed time after it goes.
  varying <- utils::modifyList(ds_design(), list(events = list(
    list(type = "text", content = "{word}", duration = list(from_column = "word_ms")),
    list(type = "response", keys = c("f", "j"), timeout_ms = 2000L))))
  stim <- ds_stim()
  stim$word_ms <- c(300L, 400L, 300L, 400L)
  ds <- build_datasheet(varying, schema, NULL, stim, "x.csv", files, 2026, engine = "R")
  expect_identical(ds$presentation$response_windows, list(
    list(event = 2L, from = "onset", window_ms = NA_integer_, duration_column = "word_ms",
         timeout_ms = 2000L)))
  expect_identical(ds$analysis$response, paste(
    "reaction time from the onset of `{word}`; responses collected until 2000 ms after",
    "its offset; a response ends the trial"))
  expect_true(grepl(paste(" Responses were collected from target onset until 2000 ms after",
                          "its offset, and a response ended the trial."),
                    methods_paragraph(ds), fixed = TRUE))
  # The JSON record writes the varying window as null, as the Python engine does, and the
  # paragraph reads the same from the record read back.
  out <- tempfile("ds"); dir.create(out)
  paths <- write_datasheet(ds, file.path(out, "d.json"), file.path(out, "d.md"))
  json <- paste(readLines(paths[1], warn = FALSE), collapse = "\n")
  expect_true(grepl('"window_ms": null', json, fixed = TRUE))
  back <- jsonlite::fromJSON(paths[1], simplifyVector = FALSE)
  expect_identical(methods_paragraph(back), methods_paragraph(ds))
  # Without a response event, as in self-paced reading, nothing is said, and a record
  # written before the field existed renders as it did.
  spr <- ds_table_design(paradigm = "self_paced_reading")
  ds <- build_datasheet(spr, schema, NULL, ds_priming_table(), "items/p.csv", files, 2026,
                        engine = "R")
  expect_identical(ds$presentation, list(response_windows = list()))
  expect_identical(ds$analysis$response, "the trial outcome (e.g. reaction time or accuracy)")
  expect_false(grepl("Responses were collected", methods_paragraph(ds), fixed = TRUE))
  old <- build_datasheet(ds_design(), schema, NULL, ds_stim(), "x.csv", files, 2026,
                         engine = "R")
  old$presentation <- NULL
  expect_false(grepl("Responses were collected", methods_paragraph(old), fixed = TRUE))
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
  # The realised spreads and the control windows are part of the record. Frequency
  # 2, 3, 4, 5 is an even spread, so its ratio is 1.
  expect_identical(ds$realised_control[[1]]$sd_ratio, 1)
  expect_true(all(c("sd", "sd_ratio", "window_low", "window_high") %in%
                    names(ds$realised_control[[2]])))
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
  expect_true(grepl("at a bound of 0.4 SD (alpha 0.05)", methods_paragraph(ds), fixed = TRUE))
})

test_that("an undefined d is reported as undefined", {
  # A controlled dimension constant at a different value in each condition has an
  # undefined d: the worst possible failure of the matching, not an excludable row.
  schema <- ds_schema()
  stim <- ds_stim()
  stim$length <- ifelse(stim$condition == "hi", 3, 4)
  report <- match_report(stim, c("length", "frequency"), schema)
  ds <- build_datasheet(ds_design(), schema, report, stim, "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  m <- methods_paragraph(ds)
  expect_true(grepl(paste("Cohen's d is undefined for every matched comparison, and the",
                          "realised-control table gives their raw differences"), m, fixed = TRUE))
  expect_true(grepl("supported equivalence on 0 of 1 matched comparisons", m, fixed = TRUE))
  expect_false(grepl("The largest difference", m, fixed = TRUE))
  # The undefined cells render as the ASCII placeholder, matching the Python engine.
  md <- lexsync:::render_datasheet_md(ds)
  expect_true(grepl("| lo | hi | length | controlled | -1.000 | -- | -- |", md, fixed = TRUE))
})

test_that("a failed TOST is counted and explained", {
  schema <- ds_schema()
  stim <- ds_stim()
  stim$length <- c(3, 9, 3, 4)  # defined d, but far too few items to pass a TOST
  report <- match_report(stim, c("length", "frequency"), schema)
  ds <- build_datasheet(ds_design(), schema, report, stim, "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  m <- methods_paragraph(ds)
  expect_true(grepl(paste("supported equivalence on 0 of 1 matched comparisons; with 2 items per",
                          "condition no dimension that varies can pass this test, however well",
                          "matched."), m, fixed = TRUE))
  expect_false(grepl("The realised control was close", m, fixed = TRUE))
})

test_that("the largest difference prints the signed d beside its signed CI", {
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
  expect_true(grepl("was -0.100 characters in length (hi against lo; d = -0.12, 90% CI [", m,
                    fixed = TRUE))
  expect_true(grepl("supported equivalence on 1 of 1 matched comparisons.", m, fixed = TRUE))
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
    list(condition = "lo", reference = "hi", dimension = "length", role = "controlled",
         cohens_d = 0.165, ci_low = -0.125, ci_high = 0.455, var_ratio = 0.0825,
         tost_p = 9e-04, equivalent = TRUE, mean_diff = 0.04),
    list(condition = "lo", reference = "hi", dimension = "old20", role = "controlled",
         cohens_d = 0.1, ci_low = -0.2, ci_high = 0.3, var_ratio = 1, tost_p = 0,
         equivalent = TRUE, mean_diff = 0.01),
    list(condition = "lo", reference = "hi", dimension = "frequency", role = "manipulated",
         cohens_d = 5.27, ci_low = 4.72, ci_high = 5.83, var_ratio = 0.21, tost_p = 1,
         equivalent = FALSE, mean_diff = 1.5))
}

test_that("decimal ties print the same in the Methods paragraph and the table", {
  ds <- build_datasheet(ds_design(), ds_schema(), NULL, ds_stim(), "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  ds$realised_control <- tie_rows()
  expect_true(grepl("was 0.040 characters in length (hi against lo; d = 0.17, 90% CI [-0.13, 0.46])",
                    methods_paragraph(ds), fixed = TRUE))
  md <- lexsync:::render_datasheet_md(ds)
  # The TOST p is printed to four places, and a stored 0 as a bound.
  expect_true(grepl("| lo | hi | length | controlled | 0.040 | 0.17 | [-0.13, 0.46] | 0.08 | 0.0009 |",
                    md, fixed = TRUE))
  expect_true(grepl("| lo | hi | old20 | controlled | 0.010 | 0.10 | [-0.20, 0.30] | 1.00 | < 0.0001 |",
                    md, fixed = TRUE))
  expect_true(grepl("| lo | hi | frequency | manipulated | 1.500 | 5.27 | [4.72, 5.83] | 0.21 | 1.0000 |",
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
  expect_true(grepl("to span frequency (a span of 0.17), for analysis", m, fixed = TRUE))
  expect_true(grepl("The largest predictor-control correlation was |r| = 0.083.", m,
                    fixed = TRUE))
  md <- lexsync:::render_datasheet_md(ds)
  expect_true(grepl("| frequency | predictor | -- | 0.165 |", md, fixed = TRUE))
  expect_true(grepl("| length | control | -0.083 | 0.165 |", md, fixed = TRUE))
})

ds_files <- function() list(stimuli = NULL, experiments = list())

test_that("the_datasheet_records_the_tie_break_rule", {
  # A matched design records the rule that broke exact ties, with its salt under hash,
  # the default. A design that runs no matcher records none. Twinned with
  # test_datasheet.py.
  schema <- ds_schema()
  ds <- build_datasheet(ds_design(), schema, NULL, ds_stim(), "x.csv", ds_files(), 2026)
  expect_identical(ds$selection[["tie_break"]], list(rule = "hash", salt = "lexsync-tie-v1"))
  as_0_1 <- ds_design()
  as_0_1$matching <- list(tie_break = "bytes")
  ds <- build_datasheet(as_0_1, schema, NULL, ds_stim(), "x.csv", ds_files(), 2026)
  expect_identical(ds$selection[["tie_break"]], list(rule = "bytes"))
  schema_bytes <- schema
  schema_bytes$matching$tie_break <- "bytes"
  joint <- ds_design()
  joint$matching <- list(method = "joint")
  ds <- build_datasheet(joint, schema_bytes, NULL, ds_stim(), "x.csv", ds_files(), 2026)
  expect_identical(ds$selection[["tie_break"]], list(rule = "bytes"))
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
  expect_true(grepl(paste(lead, "Exact ties between equally close candidates are broken by a",
                          "keyed hash of each word (salt lexsync-tie-v1), so no part of the",
                          "alphabet is favoured.", tail), md, fixed = TRUE))
  as_0_1 <- ds_design()
  as_0_1$matching <- list(tie_break = "bytes")
  md <- lexsync:::render_datasheet_md(build_datasheet(as_0_1, schema, NULL, ds_stim(),
                                                      "x.csv", ds_files(), 2026,
                                                      candidate_pool = cp))
  expect_true(grepl(paste(lead, "Exact ties between equally close candidates are broken by",
                          "spelling, in byte order, as lexsync 0.1 did, so every tie goes",
                          "to the spelling that sorts first.", tail), md, fixed = TRUE))
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

# ---- Realised control described before it is tested; a model that says what it is --
# The Methods text called the control close on the strength of equivalence tests that
# fewer than 23 items per condition can never pass, named no uncontrolled confound,
# stated the requested number of items and labelled every interval 90%. The suggested
# model left out the matched covariates, gave the Latin-square categorisation design no
# by-item slope and called its structure maximal whatever its slopes. The committed
# records below are read back as a reader would read them. test_datasheet.py pins the
# same strings.

ds_committed_record <- function(name) {
  base <- repo_path("output", "reports", name, message = "committed reports not available")
  jsonlite::fromJSON(paste0(base, ".json"), simplifyVector = FALSE)
}

# Identical lengths in both conditions, so only the number of items decides the TOST.
ds_matched_stim <- function(n) {
  i <- seq_len(n) - 1L
  data.frame(word = paste0("w", seq_len(2L * n) - 1L), condition = rep(c("hi", "lo"), each = n),
             set = rep(seq_len(n), 2L), length = rep(4 + i %% 3, 2L),
             frequency = c(6 + (i %% 2) / 10, 3 + (i %% 2) / 10), stringsAsFactors = FALSE)
}

ds_frequency_conditions <- function(design) {
  design$conditions <- list(list(name = "hi", define_by = list(frequency = c(5, 7))),
                            list(name = "lo", define_by = list(frequency = c(2, 4))))
  design
}

test_that("the methods text describes the realised control before testing it", {
  m <- methods_paragraph(ds_committed_record("en_freqcontrast_english_datasheet_R"))
  expect_true(grepl(paste0(
    "The largest difference on a matched dimension was 0.325 neighbours in ",
    "n_density (high_frequency against low_frequency; d = 0.06, 90% CI ",
    "[-0.21, 0.32]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) ",
    "supported equivalence on 3 of 3 matched comparisons. No uncontrolled ",
    "dimension differed by more than 0.5 SD."), m, fixed = TRUE))
  expect_false(grepl("The realised control was close", m, fixed = TRUE))
  expect_false(grepl("equivalence bound", m, fixed = TRUE))
})

test_that("with too few items the methods text says no dimension can pass", {
  nmin <- lexsync:::.tost_min_n
  expect_identical(c(nmin(0.5, 0.05), nmin(0.3, 0.05), nmin(0.5, 0.005)), c(23L, 62L, 56L))
  schema <- ds_schema()
  paragraph <- function(n) {
    stim <- ds_matched_stim(n)
    report <- match_report(stim, c("length", "frequency"), schema)
    design <- ds_frequency_conditions(utils::modifyList(ds_design(), list(n_per_condition = n)))
    methods_paragraph(build_datasheet(design, schema, report, stim, "x.csv", ds_files(), 2026))
  }
  expect_true(grepl(paste0(
    "supported equivalence on 0 of 1 matched comparisons; with 15 items per ",
    "condition no dimension that varies can pass this test, however well ",
    "matched."), paragraph(15L), fixed = TRUE))
  m <- paragraph(24L)
  expect_true(grepl("supported equivalence on 1 of 1 matched comparisons.", m, fixed = TRUE))
  expect_false(grepl("no dimension that varies can pass", m, fixed = TRUE))
})

test_that("a bound too small for any request still gets the caveat", {
  # Below a bound of about 5e-5 SD, no n_per_condition either engine accepts can pass.
  # This search returned NA there, with a warning, and the Methods text then stopped
  # with an error, while the Python engine searched on. At smaller bounds the search
  # never ended. Both now stop at the largest request and return infinity.
  nmin <- lexsync:::.tost_min_n
  expect_identical(nmin(1e-4, 0.05), 541108692L)
  expect_identical(nmin(1e-5, 0.05), Inf)
  tiny <- ds_schema()
  tiny$equivalence <- list(bound_d = 1e-5, alpha = 0.05)
  stim <- ds_matched_stim(30L)
  report <- match_report(stim, c("length", "frequency"), tiny)
  ds <- build_datasheet(ds_frequency_conditions(ds_design()), tiny, report, stim, "x.csv",
                        ds_files(), 2026)
  expect_true(grepl(paste0(
    "Two one-sided tests at a bound of 1e-05 SD (alpha 0.05) supported equivalence ",
    "on 0 of 1 matched comparisons; with 30 items per condition no dimension that ",
    "varies can pass this test, however well matched."), methods_paragraph(ds),
    fixed = TRUE))
})

test_that("the methods text names the uncontrolled dimensions that differ", {
  m <- methods_paragraph(ds_committed_record("en_ndensity_english_datasheet_R"))
  expect_true(grepl(paste0(
    "Dimensions the design did not control differed: old20 (dense_neighbourhood ",
    "against sparse_neighbourhood: -0.536 mean Levenshtein distance; d = -2.39, ",
    "90% CI [-2.73, -2.04]) and n_syllables (dense_neighbourhood against ",
    "sparse_neighbourhood: -0.288 syllables; d = -0.53, 90% CI ",
    "[-0.79, -0.26])."), m, fixed = TRUE))
})

test_that("a lexical decision reports what its pseudowords were not matched on", {
  m <- methods_paragraph(ds_committed_record("en_lexdec_english_datasheet_R"))
  expect_true(grepl(paste0(
    "Words and pseudowords were matched on length only, and the words differed ",
    "from the pseudowords in bigram frequency (d = -0.97, 90% CI [-1.29, -0.65]), ",
    "N (d = 0.01, 90% CI [-0.30, 0.31]) and OLD20 (d = -0.04, 90% CI ",
    "[-0.34, 0.27]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) ",
    "supported equivalence on 1 of 1 matched comparisons."), m, fixed = TRUE))
})

test_that("the interval is labelled by the configured alpha", {
  strict <- ds_schema()
  strict$equivalence <- list(bound_d = 0.5, alpha = 0.005)
  stim <- ds_matched_stim(30L)
  report <- match_report(stim, c("length", "frequency"), strict)
  ds <- build_datasheet(ds_frequency_conditions(ds_design()), strict, report, stim, "x.csv",
                        ds_files(), 2026)
  m <- methods_paragraph(ds)
  expect_true(grepl("(hi against lo; d = 0.00, 99% CI [", m, fixed = TRUE))
  expect_true(grepl("at a bound of 0.5 SD (alpha 0.005)", m, fixed = TRUE))
  expect_false(grepl("90%", m, fixed = TRUE))
  md <- lexsync:::render_datasheet_md(ds)
  expect_true(grepl("| Cohen's d | 99% CI | Var ratio |", md, fixed = TRUE))
  expect_false(grepl("90% CI", md, fixed = TRUE))
})

test_that("a shortfall states the items selected and the request", {
  # One item per condition under shortfall: allow. The text stated the 20 requested.
  schema <- ds_schema()
  stim <- data.frame(word = c("cat", "dog"), condition = c("hi", "lo"), set = c(1, 1),
                     length = c(3, 3), frequency = c(6, 3), stringsAsFactors = FALSE)
  design <- ds_frequency_conditions(utils::modifyList(ds_design(), list(
    n_per_condition = 20L, matching = list(shortfall = "allow"))))
  report <- match_report(stim, c("length", "frequency"), schema)
  ds <- build_datasheet(design, schema, report, stim, "x.csv", ds_files(), 2026)
  expect_identical(ds[["design"]][["n_per_condition"]], 20L)
  expect_identical(ds[["items"]][["n_per_condition_realised"]],
                   list(list(condition = "hi", n = 1L), list(condition = "lo", n = 1L)))
  m <- methods_paragraph(ds)
  expect_true(startsWith(m, paste0("1 item per condition (of 20 requested) was selected from ",
                                   "the English lexicon")))
  expect_true(grepl(paste0("Cohen's d is undefined for every matched comparison, and the ",
                           "realised-control table gives their raw differences"), m,
                    fixed = TRUE))
  expect_true(grepl("with 1 item per condition no dimension that varies can pass this test", m,
                    fixed = TRUE))
  # A single item has no TOST verdict either. The Python table printed None there, where
  # this renderer prints its placeholder.
  md <- lexsync:::render_datasheet_md(ds)
  expect_true(grepl("| lo | hi | length | controlled | 0.000 | -- | -- | -- | -- | -- |", md,
                    fixed = TRUE))
  expect_false(grepl("None", md, fixed = TRUE))
  # A design that leaves n_per_condition to the matcher records the matcher's 20, and
  # that is the request the two items here fall short of.
  unset <- ds_design()
  unset$n_per_condition <- NULL
  plain <- build_datasheet(unset, schema, NULL, ds_stim(), "x.csv", ds_files(), 2026)
  expect_identical(plain[["design"]][["n_per_condition"]], 20L)
  expect_true(startsWith(methods_paragraph(plain),
                         "2 items per condition (of 20 requested) were selected"))
})

test_that("the realised counts are per replicate when the design resamples", {
  reps <- do.call(rbind, lapply(c(2L, 1L), function(r) cbind(ds_stim(), replicate = r)))
  ds <- build_datasheet(utils::modifyList(ds_design(), list(resample = list(n_sets = 2L))),
                        ds_schema(), NULL, reps, "x.csv", ds_files(), 2026)
  expect_identical(ds[["items"]][["n_per_condition_realised"]], list(
    list(replicate = 1L, condition = "hi", n = 2L), list(replicate = 1L, condition = "lo", n = 2L),
    list(replicate = 2L, condition = "hi", n = 2L), list(replicate = 2L, condition = "lo", n = 2L)))
  expect_true(startsWith(methods_paragraph(ds), "2 items per condition were selected"))
})

test_that("a continuous methods text gives the spreads and the windows", {
  m <- methods_paragraph(ds_committed_record("en_freqcontinuous_english_datasheet_R"))
  expect_true(grepl(paste0(
    "80 English items were selected to span frequency (a span of 3.05 and an SD of ",
    "0.53, 0.59 times that of an even spread over the span), for analysis by ",
    "regression or a mixed model rather than a between-condition contrast (Kuperman, ",
    "2015; Liben-Nowell et al., 2019). The controls were banded within windows of ",
    "the mean \u00b1 1.5 SD of an initial selection spread over the ranks of ",
    "frequency (length 3.99 to 8.13, n_density -2.52 to 7.54 and old20 1.29 to ",
    "2.91), and their realised SDs were 0.76, 0.41 and 0.68 of the pool's. The ",
    "largest predictor-control correlation was |r| = 0.301."), m, fixed = TRUE))
  expect_false(grepl("near-constant", m, fixed = TRUE))
  # The first pass spreads over the predictor's ranks and follows the pool's skew, so
  # calling it an even spread contradicted the SD ratio given a sentence earlier.
  expect_false(grepl("initial even spread", m, fixed = TRUE))
})

test_that("a relaxed continuous selection says its windows were widened", {
  schema <- ds_schema()
  design <- list(name = "c", language = "english", n_per_condition = 4L,
                 continuous = list(predictor = "frequency", controls = list("length")),
                 match_on = list("length"), counterbalance = list(lists = 1))
  stim <- data.frame(word = c("a", "b", "c", "d"), condition = "continuous",
                     frequency = c(2, 3, 4, 5), length = c(3, 4, 3, 4), stringsAsFactors = FALSE)
  audit <- list(control_windows = list(list(dimension = "length", low = 3.2, high = 3.8,
                                            pool_sd = 1)))
  report <- match_report_continuous(stim, "frequency", "length", schema, audit = audit)
  banded <- methods_paragraph(build_datasheet(design, schema, report, stim, "x.csv",
                                              ds_files(), 2026))
  expect_true(grepl(paste0(
    " The control was banded within a window of the mean \u00b1 2 SD of an initial ",
    "selection spread over the ranks of frequency (length 3.20 to 3.80), and its ",
    "realised SD was 0.58 of the pool's."), banded, fixed = TRUE))
  relaxed <- list(window_relaxations = list(list(condition = "continuous",
                                                 n_within_tolerance = 0L, n_needed = 4L)))
  m <- methods_paragraph(build_datasheet(design, schema, report, stim, "x.csv", ds_files(),
                                         2026, selection_audit = relaxed))
  expect_true(grepl(paste0(
    " The control window, the mean \u00b1 2 SD of an initial selection spread over ",
    "the ranks of frequency (length 3.20 to 3.80), held too few items and was ",
    "widened to the whole pool, and its realised SD was 0.58 of the pool's."), m,
    fixed = TRUE))
})

test_that("the realised control table names the pair and the raw difference", {
  schema <- ds_schema()
  stim <- ds_stim()
  report <- match_report(stim, c("length", "frequency"), schema)
  md <- lexsync:::render_datasheet_md(build_datasheet(ds_design(), schema, report, stim,
                                                      "x.csv", ds_files(), 2026))
  expect_true(grepl(paste0("| Condition | Reference | Dimension | Role | Raw difference | ",
                           "Cohen's d | 90% CI | Var ratio | TOST p | Equivalent |"), md,
                    fixed = TRUE))
  expect_true(grepl(paste0("The raw difference and Cohen's d are the reference mean minus ",
                           "the condition mean"), md, fixed = TRUE))
  expect_true(grepl("| lo | hi | length | controlled | 0.000 | 0.00 | [0.00, 0.00] | 1.00 | < 0.0001 |",
                    md, fixed = TRUE))
  expect_true(grepl("| lo | hi | frequency | uncontrolled | 3.000 | -- | -- | 1.00 | 1.0000 |",
                    md, fixed = TRUE))
})

test_that("a matched design adds its matched dimensions as centred covariates", {
  # Length is the same for every item here, so it is left out of the model.
  stim <- ds_stim()
  stim$n_density <- c(1L, 2L, 3L, 4L)
  stim$old20 <- c(1.5, 1.6, 1.7, 1.8)
  a <- build_datasheet(ds_design(), ds_schema(), NULL, stim, "x.csv", ds_files(),
                       2026)[["analysis"]]
  expect_identical(a[["suggested_model"]], paste0(
    "response ~ condition + scale(n_density, scale = FALSE) + scale(old20, scale = FALSE)",
    " + (1 + condition | subject) + (1 | item)"))
  expect_true(grepl("(Sassenhagen & Alday, 2016)", a[["note"]], fixed = TRUE))
  expect_true(grepl(paste("The matched dimension length is constant among the selected items,",
                          "so it is left out."), a[["note"]], fixed = TRUE))
  # The covariates take no random slopes, so the structure is described, not called
  # maximal.
  expect_false(grepl("maximal", a[["note"]], fixed = TRUE))
  expect_true(grepl(paste0(
    "Begin with random slopes for condition, the manipulated factor, by subject and, ",
    "where it varies within items, by item (Barr et al., 2013); the matched ",
    "covariates enter as fixed effects only."), a[["note"]], fixed = TRUE))
  expect_true(grepl(paste0("If the model is singular or fails to converge, simplify it as ",
                           "Matuschek et al. (2017) describe."), a[["note"]], fixed = TRUE))
})

test_that("a lexical decision models the condition column", {
  a <- build_datasheet(ds_gen_design(), ds_schema(), NULL, ds_gen_stim(), "x.csv", ds_files(),
                       2026)[["analysis"]]
  expect_identical(a[["suggested_model"]],
                   "response ~ condition + (1 + condition | subject) + (1 | item)")
  expect_true(grepl("The condition column codes lexicality, word or pseudoword.", a[["note"]],
                    fixed = TRUE))
  expect_true(grepl("Begin with this maximal structure (Barr et al., 2013).", a[["note"]],
                    fixed = TRUE))
})

test_that("a Latin square gives items a slope for condition", {
  a <- build_datasheet(ds_table_design(paradigm = "categorisation"), ds_schema(), NULL,
                       ds_priming_table(c("narrow", "broad")), "items/p.csv", ds_files(),
                       2026)[["analysis"]]
  expect_identical(a[["suggested_model"]],
                   "response ~ condition + (1 + condition | subject) + (1 + condition | item)")
  expect_true(grepl("Begin with this maximal structure (Barr et al., 2013).", a[["note"]],
                    fixed = TRUE))
  # The recipe that ran decides, not the item source: a factorial item table keeps the
  # intercept alone.
  table <- data.frame(item = 1:4, set = c(1L, 1L, 2L, 2L),
                      condition = rep(c("word", "pseudoword"), 2L),
                      target = c("cat", "cag", "dog", "dop"), stringsAsFactors = FALSE)
  a <- build_datasheet(ds_table_design(paradigm = "factorial", counterbalance = list(lists = 2L)),
                       ds_schema(), NULL, table, "items/p.csv", ds_files(), 2026)[["analysis"]]
  expect_identical(a[["suggested_model"]],
                   "response ~ condition + (1 + condition | subject) + (1 | item)")
})

test_that("a continuous pair design models the condition and its interaction", {
  a <- build_datasheet(ds_pair_design(), ds_schema(), NULL, ds_pair_stim(), "items/p.csv",
                       ds_files(), 2026)[["analysis"]]
  expect_identical(a[["suggested_model"]], paste0(
    "response ~ condition * target.frequency + target.length + pair.overlap + ",
    "(1 + condition * target.frequency | subject) + (1 + condition | item)"))
  # The controls take no random slopes, so the structure is described, not called
  # maximal.
  expect_false(grepl("maximal", a[["note"]], fixed = TRUE))
  expect_true(grepl(paste0(
    "Begin with random slopes for condition, target.frequency and their interaction ",
    "by subject and for condition by item (Barr et al., 2013); the controls enter ",
    "as fixed effects only."), a[["note"]], fixed = TRUE))
  # A pair design with one condition has no condition term.
  stim <- ds_pair_stim()
  related <- stim[stim$condition == "related", , drop = FALSE]
  a <- build_datasheet(ds_pair_design(), ds_schema(), NULL, related, "items/p.csv",
                       ds_files(), 2026)[["analysis"]]
  expect_identical(a[["suggested_model"]], paste0(
    "response ~ target.frequency + target.length + pair.overlap + ",
    "(1 + target.frequency | subject) + (1 | item)"))
  expect_true(grepl(paste0("Begin with a random slope for target.frequency by subject ",
                           "(Barr et al., 2013); the controls enter as fixed effects only."),
                    a[["note"]], fixed = TRUE))
})

test_that("the committed records suggest the models their designs need", {
  # The categorisation design rotates its cues over its targets by a Latin square, the
  # continuous priming design crosses its condition with target frequency, and the
  # frequency contrast adds its matched covariates, so only the first is maximal.
  categorisation <- ds_committed_record("en_categorisation_english_datasheet_R")[["analysis"]]
  expect_true(endsWith(categorisation[["suggested_model"]], "+ (1 + condition | item)"))
  expect_true(grepl("Begin with this maximal structure", categorisation[["note"]], fixed = TRUE))
  priming <- ds_committed_record("en_priming_continuous_english_datasheet_R")[["analysis"]]
  expect_true(grepl("(1 + condition * target.frequency | subject)",
                    priming[["suggested_model"]], fixed = TRUE))
  expect_true(endsWith(priming[["suggested_model"]], "+ (1 + condition | item)"))
  contrast <- ds_committed_record("en_freqcontrast_english_datasheet_R")[["analysis"]]
  expect_true(grepl("scale(n_density, scale = FALSE)", contrast[["suggested_model"]],
                    fixed = TRUE))
  expect_false(grepl("maximal", contrast[["note"]], fixed = TRUE))
  expect_false(grepl("maximal", priming[["note"]], fixed = TRUE))
})

test_that("a design with more than two conditions is told how to recode", {
  four <- data.frame(word = letters[1:8],
                     condition = c("HF_l", "HF_l", "HF_s", "HF_s", "LF_l", "LF_l", "LF_s", "LF_s"),
                     set = rep(1:2, 4L), length = rep(c(3, 4), 4L),
                     n_density = rep(c(1, 2), 4L), old20 = rep(c(1.5, 1.6), 4L),
                     stringsAsFactors = FALSE)
  note <- build_datasheet(ds_design(), ds_schema(), NULL, four, "x.csv", ds_files(),
                          2026)[["analysis"]][["note"]]
  expect_true(grepl(paste0("If the conditions cross two or more factors, recode condition ",
                           "into those factors (for example frequency * neighbourhood) with ",
                           "sum coding."), note, fixed = TRUE))
  two <- build_datasheet(ds_design(), ds_schema(), NULL, ds_stim(), "x.csv", ds_files(), 2026)
  expect_false(grepl("recode condition", two[["analysis"]][["note"]], fixed = TRUE))
})
