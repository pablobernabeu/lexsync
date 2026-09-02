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

test_that("more than 200 item sets discloses the trigger wrap", {
  stim <- data.frame(condition = "a", set = seq_len(201), stringsAsFactors = FALSE)
  expect_message(
    stim <- assign_triggers(stim),
    "lexsync: 201 item sets exceed the 200-code trigger range; item codes wrap and repeat.",
    fixed = TRUE
  )
  expect_true(all(stim$item_trigger >= 40 & stim$item_trigger <= 239))
  # 201 sets into 200 codes: exactly one code is reused, and it is the first.
  expect_identical(sum(duplicated(stim$item_trigger)), 1L)
  expect_identical(stim$item_trigger[duplicated(stim$item_trigger)], 40L)
})

test_that("exactly 200 item sets stays silent", {
  stim <- data.frame(condition = "a", set = seq_len(200), stringsAsFactors = FALSE)
  expect_silent(stim <- assign_triggers(stim))
  expect_identical(sum(duplicated(stim$item_trigger)), 0L)
})

# An explicit `events:` list is the documented way to depart from a paradigm, so
# the message that refuses one has to say what a type may be. test_scripting.py pins
# the same three sentences.
KNOWN_TYPES_SENTENCE <- paste("Known types: fixation, text, mask, blank,",
                             "region_by_region, response, question, feedback.")

test_that("an unknown event type names the known ones", {
  expect_error(render_events(list(list(type = "fixaton", content = "+", duration_ms = 500L)),
                             list(), 60),
               paste("lexsync: unknown event type 'fixaton'.", KNOWN_TYPES_SENTENCE),
               fixed = TRUE)
  expect_error(lexsync:::.osexp_event_block("e1", list(type = "fixaton")),
               paste("lexsync: unknown event type 'fixaton'.", KNOWN_TYPES_SENTENCE),
               fixed = TRUE)
})

test_that("an event with no type is refused by name", {
  expect_error(render_events(list(list(content = "+", duration_ms = 500L)), list(), 60),
               paste("lexsync: unknown event type ''.", KNOWN_TYPES_SENTENCE),
               fixed = TRUE)
})

test_that("response and question timeouts round through the shared rule", {
  # An integer timeout_ms divides to at most three decimals, so rounding is the
  # identity and no committed experiment byte moves.
  r <- render_events(list(list(type = "response", timeout_ms = 1500L)), list(), 60)
  expect_identical(r[[1]]$timeout, 1.5)
  # A fractional timeout goes through .round_dp, the rounder both engines share;
  # 7812.5 ms lands on a 3-dp halfway case where the engines' own rounders differ.
  r <- render_events(list(list(type = "response", timeout_ms = 1500.0005)), list(), 60)
  expect_identical(r[[1]]$timeout, .round_dp(1500.0005 / 1000, 3))
  r <- render_events(list(list(type = "question", timeout_ms = 7812.5)), list(), 60)
  expect_identical(r[[1]]$timeout, .round_dp(7812.5 / 1000, 3))
  expect_false(identical(r[[1]]$timeout, round(7812.5 / 1000, 3)))
})

test_that("the OpenSesame timeout matches the other two backends", {
  # 1.001 * 1000 is 1000.9999999999999, and as.integer() truncated it, so a 1001 ms
  # window reached OpenSesame as 1000 while PsychoPy used the seconds directly and
  # jsPsych rounded. Mirrored in test_scripting.py.
  r <- render_events(list(list(type = "response", timeout_ms = 1001L),
                          list(type = "question", content = "q", timeout_ms = 1001L)),
                     list(), 60)
  expect_identical(vapply(r, function(ev) ev$timeout, numeric(1)), c(1.001, 1.001))
  resp <- lexsync:::.osexp_event_block("t", r[[1]])$block
  expect_true("\tset timeout 1001" %in% resp)
  quest <- lexsync:::.osexp_event_block("q", r[[2]])$block
  expect_true(any(grepl("timeout=1001)", quest, fixed = TRUE)))
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

test_that("INTER_TRIGGER_S goes through %.17g like its neighbouring substitutions", {
  # as.character(16.65 / 1000) gives "0.01665" while Python's str() gives
  # "0.016649999999999998", so the substitution is pinned through %.17g in both
  # engines. test_scripting.py asserts these same generated lines.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  design <- list(name = "t", language = "english", timing = list())
  out <- tempfile("lexsync"); dir.create(out)
  schema$triggers$inter_trigger_ms <- 16.65
  pytxt <- paste(readLines(export_psychopy(make_stim(), design, schema, out), warn = FALSE),
                 collapse = "\n")
  expect_true(grepl("INTER_TRIGGER_S = 0.016649999999999998\n", pytxt, fixed = TRUE))
  # The shipped default still renders as "0.01", so no committed experiment
  # byte moves.
  schema$triggers$inter_trigger_ms <- NULL
  pytxt <- paste(readLines(export_psychopy(make_stim(), design, schema, out), warn = FALSE),
                 collapse = "\n")
  expect_true(grepl("INTER_TRIGGER_S = 0.01\n", pytxt, fixed = TRUE))
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

# Pins the same verdict as _language_tag in the Python engine's scripting.py on a
# label whose folding the two case mappings disagree about. Base R's tolower()
# applies only the simple mapping, folding U+0130 to a bare "i" so the lookup hits
# and the tag becomes "it"; Python's str.lower() applies the Unicode default full
# mapping, giving i + U+0307, which misses and yields "und". Routing the lookup
# through .lower_invariant() (ICU, root locale) reproduces Python here, and under a
# Turkish or Azeri locale, where tolower("I") would otherwise give a dotless "i"
# and lose "ITALIAN" too. The label is built with intToUtf8 so the source stays
# ASCII (CRAN).
test_that("the BCP 47 lookup folds case as the Python engine does", {
  expect_identical(.language_tag(list(language = "ITALIAN")), "it")
  expect_identical(.language_tag(list(language = paste0(intToUtf8(0x130), "TALIAN"))), "und")
})

two_list_stim <- function() {
  stim <- data.frame(
    prime = c("hot", "sky", "sun", "big"), target = c("cold", "cold", "moon", "moon"),
    condition = rep(c("related", "unrelated"), 2), set = c(1, 1, 2, 2),
    length = 4L, frequency = 5, n_density = 2L, old20 = 1.5, stringsAsFactors = FALSE)
  design <- list(name = "t", language = "english", paradigm = "priming",
                 counterbalance = list(lists = 2L))
  list(stimuli = assign_triggers(counterbalance(stim, design, list(seed = 1))),
       design = design)
}

test_that("a multi-list OpenSesame experiment runs only the participant's list", {
  # The loop presents every row of the conditions file, so without a gate a
  # participant saw each target once per list, which under a Latin square is once in
  # every condition. A sequence has nowhere to filter its rows, so the trial runs
  # behind a condition instead. Pinned in test_osexp_validator.py too.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  out <- tempfile("lexsync"); dir.create(out)
  two <- two_list_stim()
  os <- readLines(export_opensesame(two$stimuli, two$design, schema, out), warn = FALSE)
  expect_true("\trun lexsync_trial_gate" %in% os)
  expect_true('\trun lexsync_trial "[lexsync_present] = 1"' %in% os)
  expect_true("\t_lists = [u'1', u'2']" %in% os)
  expect_true(any(grepl("var.lexsync_present = 1 if", os, fixed = TRUE)))

  # A design with one list keeps the ungated loop.
  single <- readLines(export_opensesame(make_stim(), list(name = "t", language = "english"),
                                        schema, out), warn = FALSE)
  expect_true("\trun lexsync_trial" %in% single)
  expect_false(any(grepl("lexsync_trial_gate", single, fixed = TRUE)))
})

test_that("the PsychoPy runner presents one counterbalancing list", {
  # The conditions file carries every list, because one script serves every
  # participant. Presenting it whole showed each target once per list, on adjacent
  # trials: the repetition the rotation exists to prevent. The Python suite runs the
  # generated script against a mock PsychoPy and checks the trials it selects.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  out <- tempfile("lexsync"); dir.create(out)
  two <- two_list_stim()
  py <- paste(readLines(export_psychopy(two$stimuli, two$design, schema, out), warn = FALSE),
              collapse = "\n")
  expect_true(grepl("trials = trials_for_participant(load_trials(CONDITIONS_FILE), participant)",
                    py, fixed = TRUE))
  conditions <- read.csv(file.path(out, "t_english_psychopy.csv"), stringsAsFactors = FALSE)
  expect_identical(sort(unique(conditions$list)), 1:2)
})
