ds_stim <- function() {
  data.frame(word = c("cat", "dog", "car", "cap"), condition = c("hi", "hi", "lo", "lo"),
             set = c(1, 2, 1, 2), length = 3L, frequency = c(6, 6, 3, 3),
             n_density = 2L, old20 = 1.5, stringsAsFactors = FALSE)
}
ds_design <- function() {
  list(name = "t", language = "english", match_on = list("length", "n_density", "old20"),
       n_per_condition = 2L, counterbalance = list(lists = 1))
}

test_that("datasheet captures structure and realised control", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- ds_stim()
  report <- match_report(stim, c("length", "frequency", "n_density", "old20"), schema)
  ds <- build_datasheet(ds_design(), schema, report, stim, "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  expect_identical(ds$lexsync_datasheet_version, "1.0")
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
  expect_identical(loaded$lexsync_datasheet_version, "1.0")
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
})
