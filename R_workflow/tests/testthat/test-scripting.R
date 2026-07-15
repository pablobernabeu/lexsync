make_stim <- function() {
  stim <- data.frame(
    word = c("cat", "dog", "car", "cap"), condition = c("a", "a", "b", "b"),
    set = c(1, 2, 1, 2), trial = 1:4, length = 3L, frequency = 5,
    n_density = 2L, old20 = 1.5, stringsAsFactors = FALSE
  )
  assign_triggers(stim)
}

test_that("assign_triggers produces valid EEG codes", {
  stim <- make_stim()
  expect_true(all(stim$item_trigger >= 40 & stim$item_trigger <= 239))
  expect_setequal(unique(stim$condition_trigger), c(101, 102))
})

test_that("PsychoPy export is frame-locked and OpenSesame export is internally consistent", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- make_stim()
  design <- list(name = "t", language = "english", timing = list())
  out <- tempfile("lexsync"); dir.create(out)

  py <- export_psychopy(stim, design, schema, out)
  pytxt <- paste(readLines(py, warn = FALSE), collapse = "\n")
  expect_true(grepl("win.callOnFlip(port.setData", pytxt, fixed = TRUE))
  expect_false(grepl("{{", pytxt, fixed = TRUE))   # all placeholders substituted

  osexp <- export_opensesame(stim, design, schema, out)
  os <- readLines(osexp, warn = FALSE)
  expect_true(any(grepl("set start lexsync_experiment", os, fixed = TRUE)))
  runs <- unique(sub("^\\s*run\\s+(\\S+).*$", "\\1", grep("^\\s*run\\s", os, value = TRUE)))
  defs <- sub("^define\\s+\\S+\\s+(\\S+).*$", "\\1", grep("^define\\s", os, value = TRUE))
  expect_true(all(runs %in% defs))                 # every run resolves to a definition
})

test_that("the OpenSesame export carries both trigger backends and a test-mode fallback", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  os <- paste(readLines(export_opensesame(make_stim(),
                                          list(name = "t", language = "english"),
                                          schema, tempdir()), warn = FALSE), collapse = "\n")
  expect_true(grepl("dlportio", os, fixed = TRUE))     # parallel-port backend
  expect_true(grepl("serial.Serial", os, fixed = TRUE)) # serial backend
  expect_true(grepl("test_mode", os, fixed = TRUE))     # no-hardware fallback
})

test_that("the OpenSesame loop follows the computed trial order", {
  # The loop table is sorted on the seeded `trial` column, and all three targets
  # must present that order; OpenSesame's default (`order random`) would reshuffle.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  out <- tempfile("lexsync"); dir.create(out)
  os <- readLines(export_opensesame(make_stim(), list(name = "t", language = "english"),
                                    schema, out), warn = FALSE)
  expect_true("\tset order sequential" %in% os)
  expect_false("\tset order random" %in% os)
})

test_that("all targets offset the stimulus before the response window", {
  # The stimulus offsets at its own duration, not at the participant's keypress:
  # PsychoPy flips an empty window and OpenSesame shows an empty canvas, both
  # before the response is collected, matching jsPsych's empty `response` stimulus.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  design <- list(name = "t", language = "english", timing = list())
  out <- tempfile("lexsync"); dir.create(out)

  pytxt <- paste(readLines(export_psychopy(make_stim(), design, schema, out), warn = FALSE),
                 collapse = "\n")
  expect_true(grepl("        win.flip()\n        keys = event.waitKeys(", pytxt, fixed = TRUE))

  os <- readLines(export_opensesame(make_stim(), design, schema, out), warn = FALSE)
  expect_true("define inline_script lexsync_e2_blank" %in% os)
  expect_true("define keyboard_response lexsync_e2" %in% os)
  expect_identical(grep("^\trun lexsync_e", os, value = TRUE),
                   c("\trun lexsync_e0 always", "\trun lexsync_e1 always",
                     "\trun lexsync_e2_blank always", "\trun lexsync_e2 always",
                     "\trun lexsync_e3 always"))
})

test_that("a per-design font overrides the Latin default for logographic scripts", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- assign_triggers(data.frame(
    word = c("自然", "回来", "三亚", "东盟"),
    condition = c("a", "a", "b", "b"), set = c(1, 2, 1, 2), trial = 1:4,
    length = 2L, frequency = 5, n_density = 80L, old20 = 1.0, stringsAsFactors = FALSE
  ))
  design <- list(name = "zh", language = "chinese", font = "SimHei", timing = list())
  out <- tempfile("lexsync"); dir.create(out)

  pytxt <- paste(readLines(export_psychopy(stim, design, schema, out), warn = FALSE), collapse = "\n")
  expect_true(grepl('WORD_FONT = "SimHei"', pytxt, fixed = TRUE))
  expect_false(grepl("{{", pytxt, fixed = TRUE))

  os <- readLines(export_opensesame(stim, design, schema, out), warn = FALSE)
  expect_true(any(os == "set font_family SimHei"))

  # The default remains a Latin font when no per-design font is given.
  pytxt2 <- paste(readLines(export_psychopy(make_stim(),
                                            list(name = "t", language = "english", timing = list()),
                                            schema, out), warn = FALSE), collapse = "\n")
  expect_true(grepl('WORD_FONT = "Courier New"', pytxt2, fixed = TRUE))
})
