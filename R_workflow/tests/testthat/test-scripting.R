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
  expect_true(all(stim$target_word_trigger >= 40 & stim$target_word_trigger <= 239))
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
