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

test_that("condition codes follow the given order, not the row order", {
  # After counterbalance() shuffles the trials, first appearance depends on the
  # seed, so it cannot be what fixes a condition's code. Pinned identically in
  # test_scripting.py.
  stim <- data.frame(condition = c("low", "high", "low", "high"), set = c(1, 1, 2, 2),
                     stringsAsFactors = FALSE)
  code_of <- function(s) {
    u <- unique(s[, c("condition", "condition_trigger")])
    stats::setNames(u$condition_trigger, u$condition)[c("high", "low")]
  }
  # The default keeps the 0.1.0 behaviour: order of first appearance.
  expect_equal(unname(code_of(assign_triggers(stim))), c(102, 101))
  given <- assign_triggers(stim, conditions = c("high", "low"))
  expect_equal(unname(code_of(given)), c(101, 102))
  expect_equal(unname(code_of(assign_triggers(stim[4:1, ], conditions = c("high", "low")))),
               c(101, 102))
  # A listed condition absent from the rows keeps its code; an unlisted one takes
  # the next free code in code-point order of its label.
  sub <- assign_triggers(stim[stim$condition == "low", ], conditions = c("high", "low"))
  expect_equal(unique(sub$condition_trigger), 102)
  extra <- rbind(stim, data.frame(condition = c("zeta", "Mid"), set = c(3, 3)))
  extra <- assign_triggers(extra[nrow(extra):1, ], conditions = "high")
  u <- unique(extra[, c("condition", "condition_trigger")])
  expect_equal(u$condition_trigger[match(c("high", "Mid", "low", "zeta"), u$condition)],
               c(101, 102, 103, 104))
})

test_that("export_experiments numbers conditions in the design's order", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- data.frame(word = c("cat", "dog", "car", "cap"), condition = c("a", "b", "a", "b"),
                     set = c(1, 1, 2, 2), trial = 1:4, stringsAsFactors = FALSE)
  design <- list(name = "t", language = "english", timing = list(),
                 conditions = list(list(name = "b"), list(name = "a")))
  expect_identical(.design_condition_names(design), c("b", "a"))
  expect_null(.design_condition_names(list(name = "t")))
  out <- tempfile("lexsync"); dir.create(out)
  on.exit(unlink(out, recursive = TRUE), add = TRUE)
  export_experiments(stim, design, schema, out)
  loop <- utils::read.csv(file.path(out, "t_english_psychopy.csv"), stringsAsFactors = FALSE)
  expect_equal(unique(loop$condition_trigger[loop$condition == "b"]), 101)
  expect_equal(unique(loop$condition_trigger[loop$condition == "a"]), 102)
  # An explicit order overrides the design's.
  export_experiments(stim, design, schema, out, conditions = c("a", "b"))
  loop <- utils::read.csv(file.path(out, "t_english_psychopy.csv"), stringsAsFactors = FALSE)
  expect_equal(unique(loop$condition_trigger[loop$condition == "a"]), 101)
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

test_that("inter_trigger_ms is accepted and no longer used", {
  # The self-paced reading critical-region code was held for inter_trigger_ms, 10 ms,
  # where every other code is held for trigger_hold_ms, and nothing else read the key.
  # A schema that still sets it is accepted, and the run log says the key is not used.
  # test_scripting.py asserts the same.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  design <- list(name = "t", language = "english", timing = list())
  out <- tempfile("lexsync"); dir.create(out)
  old <- schema
  old$triggers$inter_trigger_ms <- 16.65
  pytxt <- paste(readLines(export_psychopy(make_stim(), design, old, out), warn = FALSE),
                 collapse = "\n")
  expect_false(grepl("INTER_TRIGGER", pytxt, fixed = TRUE))
  expect_identical(validate_design(design, old), paste(
    "lexsync: triggers.inter_trigger_ms is no longer used; the self-paced reading",
    "critical-region code is held for triggers.trigger_hold_ms, as every other code is."))
  # The shipped schema no longer sets it.
  expect_null(schema$triggers[["inter_trigger_ms"]])
  expect_identical(validate_design(design, schema), character(0))
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

FIX <- list(type = "fixation", content = "+", duration_ms = 500L)
TEXT <- list(type = "text", content = "{target}", duration_ms = 800L, trigger = "condition")
BLANK <- list(type = "blank", duration_ms = 200L)
RESP <- list(type = "response", keys = c("f", "j"), timeout_ms = 2000L)

test_that("a response after a text event is collected from its onset", {
  # The window used to open only when the target had gone. After a text event a
  # response is now collected from the text's onset, as one rendered event: the text
  # stays up for its 800 ms at most, and the window runs 2,800 ms, the total it had.
  # test_scripting.py pins the same rules and messages.
  r <- render_events(list(FIX, TEXT, RESP), list(), 60)
  expect_identical(r, list(
    list(type = "fixation", text = "+", ms = 500L),
    list(type = "text", field = "target", ms = 800L, trigger = "@condition_trigger",
         respond = list(keys = list("f", "j"), timeout = 2))))
  expect_identical(vapply(render_events(resolve_events(list(paradigm = "factorial")),
                                        list(), 60), function(e) e$type, character(1)),
                   c("fixation", "text", "blank"))
  # After anything else, and with from: offset, the window opens after the stimulus,
  # as it did, for designs that delay the response.
  offset <- utils::modifyList(RESP, list(from = "offset"))
  for (events in list(list(TEXT, BLANK, RESP), list(TEXT, offset), list(TEXT, BLANK, offset))) {
    rendered <- render_events(events, list(), 60)
    expect_identical(rendered[[length(rendered)]],
                     list(type = "response", keys = list("f", "j"), timeout = 2))
    expect_null(rendered[[1]][["respond"]])
  }
  # from: onset needs a text event before the response.
  onset <- utils::modifyList(RESP, list(from = "onset"))
  expect_error(render_events(list(TEXT, BLANK, onset), list(), 60),
               paste("lexsync: event 3 collects its response from the onset of the preceding",
                     "stimulus, but event 2 is a blank; use from: offset."), fixed = TRUE)
  expect_error(render_events(list(onset), list(), 60),
               paste("lexsync: event 1 collects its response from the onset of the preceding",
                     "stimulus, but no event precedes it; use from: offset."), fixed = TRUE)
  expect_error(render_events(list(TEXT, utils::modifyList(RESP, list(from = "start"))),
                             list(), 60),
               paste("lexsync: event 2 gives `from: start`, but a response event takes",
                     "from: onset or from: offset."), fixed = TRUE)
  expect_error(render_events(list(TEXT, utils::modifyList(RESP, list(from = TRUE))),
                             list(), 60),
               paste("lexsync: event 2 gives `from: true`, but a response event takes",
                     "from: onset or from: offset."), fixed = TRUE)
  # The merged event runs where the text runs, so the two must name the same blocks.
  practice <- utils::modifyList(TEXT, list(blocks = list("practice")))
  merged <- render_events(list(practice, utils::modifyList(RESP, list(blocks = "practice"))),
                          list(), 60)[[1]]
  expect_identical(merged, c(render_events(list(practice), list(), 60)[[1]],
                             list(respond = list(keys = list("f", "j"), timeout = 2))))
  expect_error(render_events(list(practice, RESP), list(), 60),
               paste("lexsync: event 2 collects its response from the onset of event 1, so the",
                     "two must run in the same blocks; give them the same `blocks`, or use",
                     "from: offset."), fixed = TRUE)
})

test_that("a single response key is written as a list", {
  # One key is still a list of keys in every generated experiment, as the runners read
  # it. jsonlite wrote a lone key as a bare string where the Python engine wrote a list,
  # so the two engines' EVENTS differed and the PsychoPy runner split "space" into five
  # one-letter keys. test_scripting.py pins the same JSON.
  events <- list(TEXT, utils::modifyList(RESP, list(keys = "space")), BLANK,
                 utils::modifyList(RESP, list(keys = list("space"))),
                 list(type = "question", content = "{target}", keys = "f"))
  expect_identical(
    as.character(jsonlite::toJSON(render_events(events, list(), 60), auto_unbox = TRUE)),
    paste0('[{"type":"text","field":"target","ms":800,"trigger":"@condition_trigger",',
           '"respond":{"keys":["space"],"timeout":2}},{"type":"blank","ms":200},',
           '{"type":"response","keys":["space"],"timeout":2},',
           '{"type":"question","field":"target","keys":["f"],"timeout":5}]'))
})

# The events of a design whose response keys are written `keys` in YAML, read as
# run_pipeline() reads them, so the test covers the YAML reader as well.
events_from_yaml <- function(keys) {
  path <- tempfile(fileext = ".yaml")
  writeLines(c("events:",
               "  - {type: text, content: '{target}', duration_ms: 800}",
               sprintf("  - {type: response, keys: %s}", keys)), path)
  read_config(path)$events
}

test_that("unquoted_y_and_n_are_response_keys_y_and_n", {
  # This engine's YAML reader took an unquoted y and n for TRUE and FALSE, so
  # `keys: [y, n]` gave it experiments waiting for keys named TRUE and FALSE, which no
  # participant can press. Pinned identically in test_scripting.py.
  expect_identical(render_events(events_from_yaml("[y, n]"), list(), 60)[[1]]$respond$keys,
                   list("y", "n"))
  expect_identical(render_events(events_from_yaml("[Y, N]"), list(), 60)[[1]]$respond$keys,
                   list("Y", "N"))
})

test_that("a_yaml_boolean_response_key_is_refused", {
  # YAML 1.1 reads an unquoted yes, no, on, off, true or false as a boolean in both
  # engines. This engine rendered it as the key TRUE and the Python engine as True, two
  # different experiments that no participant could answer. Pinned identically in
  # test_scripting.py.
  refusal <- "lexsync: response key %s is a YAML boolean; quote it ('%s') or choose another key."
  expect_error(render_events(events_from_yaml("[yes, no]"), list(), 60),
               sprintf(refusal, "TRUE", "yes"), fixed = TRUE)
  expect_error(render_events(events_from_yaml("[f, off]"), list(), 60),
               sprintf(refusal, "FALSE", "no"), fixed = TRUE)
  expect_error(render_events(events_from_yaml("on"), list(), 60),
               sprintf(refusal, "TRUE", "yes"), fixed = TRUE)
  question <- list(type = "question", content = "{target}", keys = list(FALSE, "j"))
  expect_error(render_events(list(question), list(), 60),
               sprintf(refusal, "FALSE", "no"), fixed = TRUE)
})

test_that("a delayed response still opens after the stimulus", {
  # from: offset keeps the window that opens when the stimulus has gone. PsychoPy runs
  # it as its own event, and OpenSesame blanks the screen, collects the key with a
  # keyboard_response and then scores it.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  design <- list(name = "t", language = "english", timing = list(), events = list(
    list(type = "fixation", content = "+", duration_frames = 30L),
    list(type = "text", content = "{word}", duration_frames = 48L, trigger = "condition"),
    list(type = "response", keys = c("left", "right"), timeout_ms = 2000L, from = "offset"),
    list(type = "blank", duration_frames = 15L)))
  out <- tempfile("lexsync"); dir.create(out)
  pytxt <- paste(readLines(export_psychopy(make_stim(), design, schema, out), warn = FALSE),
                 collapse = "\n")
  json <- regmatches(pytxt, regexec('EVENTS = json\\.loads\\(r"""(.*?)"""\\)', pytxt))[[1]][2]
  events <- jsonlite::fromJSON(json, simplifyDataFrame = FALSE)
  expect_identical(vapply(events, function(e) e$type, character(1)),
                   c("fixation", "text", "response", "blank"))
  os <- readLines(export_opensesame(make_stim(), design, schema, out), warn = FALSE)
  expect_true("define inline_script lexsync_e2_blank" %in% os)
  expect_true("define keyboard_response lexsync_e2" %in% os)
  expect_true("define inline_script lexsync_e2_score" %in% os)
  expect_identical(grep("^\trun lexsync_e", os, value = TRUE),
                   c("\trun lexsync_e0 always", "\trun lexsync_e1 always",
                     "\trun lexsync_e2_blank always", "\trun lexsync_e2 always",
                     "\trun lexsync_e2_score always", "\trun lexsync_e3 always"))
})

# The items a sequence runs, in order, by default those of the trial sequence.
trial_runs <- function(lines, name = "lexsync_trial") {
  at <- match(sprintf("define sequence %s", name), lines)
  rest <- lines[(at + 1L):length(lines)]
  rest <- rest[seq_len(match("", rest) - 1L)]
  sub("^\trun (\\S+).*$", "\\1", grep("^\trun ", rest, value = TRUE))
}

# One phase of an inline script, "run" or "prepare", without the leading tab, or
# character(0) when the script leaves that phase empty.
script_phase <- function(lines, name, phase = "run") {
  at <- match(sprintf("define inline_script %s", name), lines)
  rest <- lines[(at + 1L):length(lines)]
  rest <- rest[seq_len(match("", rest) - 1L)]
  start <- match(sprintf("\t___%s__", phase), rest)
  if (is.na(start)) return(character(0))
  end <- start + match("\t__end__", rest[(start + 1L):length(rest)])
  substring(rest[seq_len(end - start - 1L) + start], 2L)
}
run_phase <- function(lines, name) script_phase(lines, name, "run")

test_that("an onset-locked response runs in its stimulus script", {
  # The target and its response window are one inline script, which shows the target,
  # sends its trigger and polls the keyboard through it and then a blank. A
  # keyboard_response flushed every key pressed while the target was on screen and
  # timed the response from the blank that followed it. test_osexp_validator.py pins
  # the same lines and runs them under both variable stores.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- make_stim()
  names(stim)[names(stim) == "word"] <- "target"
  out <- tempfile("lexsync"); dir.create(out)
  os <- readLines(export_opensesame(stim, list(name = "t", language = "english",
                                               paradigm = "lexical_decision"),
                                    schema, out), warn = FALSE)
  expect_false(any(startsWith(os, "define keyboard_response")))
  expect_identical(trial_runs(os), c("lexsync_trial_start", "lexsync_e0", "lexsync_e1",
                                     "lexsync_e2", "lexsync_record", "lexsync_logger"))
  # The target and the blank after it are built before the trial runs.
  expect_identical(script_phase(os, "lexsync_e1", "prepare"), c(
    "_lexsync_c_e1 = Canvas()",
    "_lexsync_c_e1.text(_lexsync_row()[u'target'])",
    "_lexsync_c_e1_blank = Canvas()"))
  # The window is timed from the target's onset: the keyboard is polled until half a
  # frame before the target's 800 ms are up, so that the blank lands on the refresh
  # that ends them, and then until 2,000 ms after that.
  expect_identical(run_phase(os, "lexsync_e1"), c(
    "_t0 = _lexsync_c_e1.show()",
    "var.onset_time = _t0",
    "_lexsync_onset(int(var.get(u'condition_trigger', _eval=False)), _t0)",
    "_kb = Keyboard(keylist=[u'left', u'right'])",
    "_kb.flush()",
    "_key, _t = _lexsync_key(_kb, _t0 + 800 - _LEXSYNC_HALF_FRAME)",
    "if _key is None:",
    "    _lexsync_c_e1_blank.show()",
    "    _key, _t = _lexsync_key(_kb, _t0 + 800 + 2000)",
    "var.response = _key",
    "var.response_time = u'' if _key is None else _t - _t0",
    "var.timed_out = 1 if _key is None else 0",
    "_want = str(_lexsync_row().get(u'answer', u'')).strip()",
    "_got = u'' if _key is None else str(_key).strip()",
    "var.correct = (1 if _got == _want else 0) if _want else u''"))
  # The logger runs last in every trial, after the labels are copied in for it.
  at <- match("define logger lexsync_logger", os)
  expect_identical(os[at + 1:2], c('\tset description "Log the trial"', "\tset auto_log yes"))
})

test_that("OpenSesame timeouts are written in whole milliseconds as declared", {
  # 1.001 s times 1000 is 1000.9999999999999 in binary floating point, so as.integer()
  # wrote a declared 1,001 ms as 1,000: 95 of the whole-millisecond timeouts from 1 to
  # 10,000 came out one short. test_osexp_validator.py pins the same lines.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  out <- tempfile("lexsync"); dir.create(out)
  delayed <- list(name = "d", language = "english", events = list(
    list(type = "text", content = "{word}", duration_ms = 300L),
    list(type = "blank", duration_ms = 100L),
    list(type = "response", keys = c("f", "j"), timeout_ms = 1001L),
    list(type = "question", content = "{word}", keys = c("f", "j"), timeout_ms = 1003L)))
  os <- readLines(export_opensesame(make_stim(), delayed, schema, out), warn = FALSE)
  expect_true("\tset timeout 1001" %in% os)
  expect_true("\t_key, _t = _lexsync_key(_kb, _t0 + 1003)" %in% os)
  onset <- list(name = "o", language = "english", events = list(
    list(type = "text", content = "{word}", duration_ms = 300L),
    list(type = "response", keys = c("f", "j"), timeout_ms = 1001L)))
  os <- readLines(export_opensesame(make_stim(), onset, schema, out), warn = FALSE)
  expect_true("\t    _key, _t = _lexsync_key(_kb, _t0 + 300 + 1001)" %in% os)
})

# The tests below pin when each display appears and how long each code is held.
# OpenSesame prepares every item of a sequence before it runs any, and its inline
# scripts share one workspace. The generated scripts built each canvas while the trial
# ran and slept each event's full duration after a blocking 10 ms pulse, so every event
# overran: at 60 Hz the 50 ms prime lasted about 67 ms. The experiment also ignored
# triggers.trigger_hold_ms and sent neither session marker. test_osexp_validator.py
# pins the same structure and runs the timing on a simulated display.

# One event of every type: a triggered prime and mask, a target with its response,
# feedback, a sentence region by region, a question, a delayed response and a per-trial
# interval.
every_event_design <- function() {
  list(name = "every", language = "english", events = list(
    list(type = "fixation", content = "+", duration_ms = 500L),
    list(type = "text", content = "{word}", duration_ms = 50L, trigger = 20L),
    list(type = "mask", content = "#####", duration_ms = 33L),
    list(type = "text", content = "{word}", duration_ms = 300L, trigger = "condition"),
    list(type = "response", keys = c("f", "j"), timeout_ms = 2000L),
    list(type = "feedback", answer = "answer", duration_ms = 600L),
    list(type = "region_by_region", content = "{sentence}",
         critical_region_trigger = "item"),
    list(type = "question", content = "{question}", keys = c("f", "j"), timeout_ms = 4000L),
    list(type = "blank", duration_ms = 200L),
    list(type = "response", keys = c("f", "j"), timeout_ms = 1000L),
    list(type = "blank", duration = list(from_column = "iti_ms"))))
}

every_event_experiment <- function(schema) {
  stim <- assign_triggers(data.frame(
    word = c("cat", "dog"), sentence = c("The|cat|sat.", "A|dog|ran."),
    question = c("Sat?", "Ran?"), condition = c("a", "b"), set = c(1, 2), list = 1L,
    trial = 1:2, critical_region = 2L, answer = c("f", "j"), iti_ms = c(400L, 425L),
    stringsAsFactors = FALSE))
  out <- tempfile("lexsync"); dir.create(out)
  readLines(export_opensesame(stim, every_event_design(), schema, out), warn = FALSE)
}

is_inline_script <- function(lines, name) sprintf("define inline_script %s", name) %in% lines

test_that("each canvas is prepared under its own name", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  os <- every_event_experiment(schema)
  prepared <- list()
  for (name in trial_runs(os)) {
    if (!is_inline_script(os, name)) next
    run <- run_phase(os, name)
    # Nothing is built while the trial runs: every canvas a script shows was built in
    # its prepare phase, before the sequence ran its first item.
    expect_false(any(grepl("Canvas(", run, fixed = TRUE)), info = name)
    prep <- script_phase(os, name, "prepare")
    own <- unique(sub("^(_lexsync_c_\\w+) = .*$", "\\1",
                      grep("^_lexsync_c_\\w+ = ", prep, value = TRUE, perl = TRUE),
                      perl = TRUE))
    used <- unique(unlist(regmatches(run, gregexpr("_lexsync_c_\\w+", run, perl = TRUE))))
    expect_true(all(used %in% own), info = name)
    # The workspace is shared, so a canvas is named after its item. A shared name would
    # show, in every item, the canvas the sequence prepared last.
    suffix <- paste0("_lexsync_c_", sub("^lexsync_", "", name))
    expect_true(all(own == suffix | startsWith(own, paste0(suffix, "_"))), info = name)
    prepared[[name]] <- own
  }
  all_names <- unlist(prepared, use.names = FALSE)
  expect_false(anyDuplicated(all_names) > 0L)
  expect_identical(
    sort(names(Filter(length, prepared)), method = "radix"),
    c("lexsync_e0", "lexsync_e1", "lexsync_e2", "lexsync_e3", "lexsync_e4", "lexsync_e5",
      "lexsync_e6", "lexsync_e7", "lexsync_e8_blank", "lexsync_e9"))
})

test_that("no event sleeps its full duration after a trigger", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  os <- every_event_experiment(schema)
  for (name in Filter(function(n) is_inline_script(os, n), trial_runs(os))) {
    run <- run_phase(os, name)
    # Every wait is timed from an onset through the setup's helpers, which also reset
    # the code when its hold is up. No script sleeps or writes to the port.
    expect_false(any(grepl("clock.sleep", run, fixed = TRUE) |
                       grepl("send_trigger(", run, fixed = TRUE)), info = name)
  }
  # A timed event shows its canvas, sends its code and waits until half a frame before
  # its end, measured from its onset, so that the next display lands on the refresh
  # that ends it.
  expect_identical(run_phase(os, "lexsync_e1"), c(
    "_t0 = _lexsync_c_e1.show()", "var.onset_time = _t0", "_lexsync_onset(20, _t0)",
    "_lexsync_wait(_t0 + 50 - _LEXSYNC_HALF_FRAME)"))
  expect_identical(run_phase(os, "lexsync_e2"), c(
    "_t0 = _lexsync_c_e2.show()", "var.onset_time = _t0",
    "_lexsync_wait(_t0 + 33 - _LEXSYNC_HALF_FRAME)"))
  e9 <- run_phase(os, "lexsync_e9")
  expect_identical(e9[length(e9)], paste(
    "_lexsync_wait(_t0 + int(float(var.get(u'iti_ms', _eval=False)))",
    "- _LEXSYNC_HALF_FRAME)"))
  # The trigger device writes a code and returns.
  setup <- script_phase(os, "lexsync_trigger_setup", "prepare")
  expect_false(any(grepl("time.sleep", setup, fixed = TRUE)))
})

test_that("the session markers are sent and held", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  os <- every_event_experiment(schema)
  # The setup runs first, and the markers enclose the loop: 254 just before it and 255
  # just after it, whatever the experiment shows before the trials.
  sequence <- trial_runs(os, "lexsync_experiment")
  loop <- match("lexsync_loop", sequence)
  expect_identical(sequence[1], "lexsync_trigger_setup")
  expect_identical(sequence[(loop - 1L):length(sequence)],
                   c("lexsync_session_start", "lexsync_loop", "lexsync_session_end"))
  expect_identical(run_phase(os, "lexsync_session_start"), "_lexsync_marker(254)")
  expect_identical(run_phase(os, "lexsync_session_end"), "_lexsync_marker(255)")
  setup <- script_phase(os, "lexsync_trigger_setup", "prepare")
  # The hold is the schema's, and the frame period falls back to the assumed rate.
  expect_true("_LEXSYNC_HOLD = 50" %in% setup)
  expect_true("    _LEXSYNC_FRAME = 1000.0 / 60" %in% setup)
  # A hold below the 10 ms most recorders need is raised to it.
  short <- schema
  short$triggers$trigger_hold_ms <- 4
  short$presentation$assumed_refresh_hz <- 144
  out <- tempfile("lexsync"); dir.create(out)
  os <- readLines(export_opensesame(make_stim(), list(name = "s", language = "english"),
                                    short, out), warn = FALSE)
  setup <- script_phase(os, "lexsync_trigger_setup", "prepare")
  expect_true("_LEXSYNC_HOLD = 10" %in% setup)
  expect_true("    _LEXSYNC_FRAME = 1000.0 / 144" %in% setup)
})

test_that("a key window resets a code whose hold ends with it", {
  # _lexsync_wait() resets a code whose hold ends with its wait, and _lexsync_key() must
  # do the same. It reset the code only once its hold had ended before the window did,
  # so at 120 Hz, where the legacy clock measures the frame as 8 ms, a 54 ms target that
  # collects its own response kept its code on the port until the blank appeared,
  # 58.3 ms after the onset. test_osexp_validator.py runs that case on a simulated
  # display.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  setup <- script_phase(every_event_experiment(schema), "lexsync_trigger_setup", "prepare")
  expect_true("    if _lexsync_due[0] is not None and _lexsync_due[0] <= t:" %in% setup)
  expect_true(paste("    if _lexsync_due[0] is not None and",
                    "(t is None or _lexsync_due[0] <= t):") %in% setup)
})

test_that("the PsychoPy script holds every code for the hold, the markers included", {
  # The 254 and 255 markers were cleared by the statement after their flip, a code on an
  # event shorter than the hold was cleared as soon as the event's last flip returned,
  # and the 10 ms floor was applied before the hold was rounded to flips, so a 10 ms
  # hold lasted 6.9 ms at 144 Hz. The script is the template both engines fill, and
  # test_psychopy_export.py runs every committed one against a fake PsychoPy at 60, 144
  # and 240 Hz. Here the script this engine writes is checked for the lines that hold
  # the codes.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  out <- tempfile("lexsync"); dir.create(out)
  on.exit(unlink(out, recursive = TRUE), add = TRUE)
  py <- readLines(export_psychopy(make_stim(), list(name = "t", language = "english"),
                                  schema, out), warn = FALSE)
  # The floor is rounded up to whole flips, the hold to the nearest.
  expect_true(paste("    floor = int(math.ceil(float(MIN_TRIGGER_HOLD_MS) * float(hz)",
                    "/ 1000.0))") %in% py)
  expect_true("    return max(1, hold, floor)" %in% py)
  # Every flip counts the hold down. The onset codes, the critical region's included,
  # and the two markers go through the same count.
  expect_true("    count_flip(win)" %in% py)
  expect_true("        send_code(win, port, trigger)" %in% py)
  expect_true("                send_code(win, port, trig)" %in% py)
  expect_true("    send_marker(win, port, BLOCK_START_TRIGGER)" %in% py)
  expect_true("    send_marker(win, port, BLOCK_END_TRIGGER)" %in% py)
  # The port is set to 0 only when it opens, on a flip queued by send_code() or
  # count_flip(), and by end_code() once a hold has been waited out.
  expect_identical(grep("setData(\\(|, )0\\)", py, value = TRUE), c(
    "        port.setData(0)  # the dummy backend raises NotImplementedError here",
    "        win.callOnFlip(PULSE[\"port\"].setData, 0)",
    "            win.callOnFlip(PULSE[\"port\"].setData, 0)",
    "        PULSE[\"port\"].setData(0)"))
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

# ---- One counterbalancing version per participant ----------------------------------
# A presentation version is one (replicate, list) pair of the presented trials, numbered
# from 1 in that order. test_scripting.py pins the same files, names and texts, and the
# Python suite runs the generated PsychoPy script and jsPsych page themselves.

# Two targets, each related in one list and unrelated in the other.
two_list_stim <- function(schema) {
  stim <- data.frame(prime = c("hot", "sky", "sun", "big"),
                     target = c("cold", "cold", "moon", "moon"),
                     condition = rep(c("related", "unrelated"), 2), set = c(1, 1, 2, 2),
                     stringsAsFactors = FALSE)
  design <- list(name = "t", language = "english", paradigm = "priming",
                 counterbalance = list(lists = 2L))
  list(stimuli = assign_triggers(counterbalance(stim, design, schema)), design = design)
}

# Three disjoint item samples, each dealt into one list, as en_resample is.
three_replicates <- function(schema) {
  stim <- data.frame(word = sprintf("w%02d", 0:11), condition = rep(c("hi", "lo"), 6),
                     set = rep(c(1, 1, 2, 2), 3), replicate = rep(1:3, each = 4),
                     stringsAsFactors = FALSE)
  design <- list(name = "r", language = "english", counterbalance = list(lists = 1L))
  list(stimuli = assign_triggers(counterbalance(stim, design, schema)), design = design)
}

test_that("one OpenSesame experiment per version", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  out <- tempfile("lexsync"); dir.create(out)
  two <- two_list_stim(schema)
  first <- export_opensesame(two$stimuli, two$design, schema, out)
  expect_identical(basename(first), "t_english_list1.osexp")
  expect_identical(sort(list.files(out), method = "radix"), c(
    "t_english_list1.osexp", "t_english_list1_opensesame.csv",
    "t_english_list1_opensesame_text.csv", "t_english_list2.osexp",
    "t_english_list2_opensesame.csv", "t_english_list2_opensesame_text.csv"))
  for (k in 1:2) {
    numbers <- utils::read.csv(file.path(out, sprintf("t_english_list%d_opensesame.csv", k)))
    expect_identical(unique(numbers$lexsync_list), k)
    expect_identical(numbers$lexsync_row, 1:2)
    text <- utils::read.csv(file.path(out, sprintf("t_english_list%d_opensesame_text.csv", k)),
                            stringsAsFactors = FALSE)
    expect_identical(sort(text$target), c("cold", "moon"))
    lines <- readLines(file.path(out, sprintf("t_english_list%d.osexp", k)), warn = FALSE)
    expect_true(sprintf('\tset source_file "t_english_list%d_opensesame.csv"', k) %in% lines)
    expect_true(sprintf(paste0("\twith open(pool[u't_english_list%d_opensesame_text.csv'], ",
                               "encoding=u'utf-8-sig', newline=u'') as _f:"), k) %in% lines)
    # Each experiment checks the subject number against its own version before the
    # loop, then shows its instructions, and no run line carries a condition. The
    # session markers come after the instructions, just before and after the loop.
    expect_true("define inline_script lexsync_version_check" %in% lines)
    expect_true(sprintf("\t_version = %d", k) %in% lines)
    expect_true("\t_versions = 2" %in% lines)
    runs <- grep("^\trun ", lines, value = TRUE)
    expect_identical(utils::tail(runs, 6),
                     c("\trun lexsync_trigger_setup always",
                       "\trun lexsync_version_check always",
                       "\trun lexsync_instructions always",
                       "\trun lexsync_session_start always", "\trun lexsync_loop always",
                       "\trun lexsync_session_end always"))
    expect_false(any(grepl('"', runs, fixed = TRUE)))
  }
})

test_that("single-version designs keep their file names", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  out <- tempfile("lexsync"); dir.create(out)
  res <- export_experiments(make_stim(), list(name = "t", language = "english",
                                              timing = list()), schema, out)
  # The three elements callers read are unchanged, and `files` lists every file written.
  expect_identical(names(res), c("psychopy", "opensesame", "jspsych", "files"))
  expect_identical(basename(res$files), c(
    "t_english_psychopy.py", "t_english.osexp", "t_english.html",
    "t_english_psychopy.csv", "t_english_opensesame.csv", "t_english_opensesame_text.csv"))
  expect_identical(res$files[1:3], c(res$psychopy, res$opensesame, res$jspsych))
  expect_identical(sort(list.files(out), method = "radix"),
                   sort(basename(res$files), method = "radix"))
  expect_false(any(grepl("lexsync_version_check", readLines(res$opensesame, warn = FALSE),
                         fixed = TRUE)))
})

test_that("export_experiments lists every version file", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  out <- tempfile("lexsync"); dir.create(out)
  two <- two_list_stim(schema)
  res <- export_experiments(two$stimuli, two$design, schema, out)
  expect_identical(basename(res$files), c(
    "t_english_psychopy.py", "t_english_list1.osexp", "t_english_list2.osexp",
    "t_english.html", "t_english_psychopy.csv",
    "t_english_list1_opensesame.csv", "t_english_list1_opensesame_text.csv",
    "t_english_list2_opensesame.csv", "t_english_list2_opensesame_text.csv"))
  expect_identical(res$opensesame, res$files[2])
  expect_identical(sort(list.files(out), method = "radix"),
                   sort(basename(res$files), method = "radix"))
})

test_that("resampled replicates are separate versions", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  three <- three_replicates(schema)
  expect_identical(.presentation_versions(three$stimuli), lapply(1:3, function(r)
    list(version = r, replicate = r, list = 1L, n_trials = 4L)))
  # The loop table carries the replicate and keeps each replicate's trials together, in
  # trial order. Trials are numbered within a replicate, so sorting on the trial alone
  # interleaved the replicates.
  loop <- loop_table(three$stimuli)
  expect_identical(names(loop)[1:3], c("trial", "list", "replicate"))
  expect_identical(paste(loop$replicate, loop$trial),
                   paste(rep(1:3, each = 4), rep(1:4, 3)))
  out <- tempfile("lexsync"); dir.create(out)
  res <- export_experiments(three$stimuli, three$design, schema, out)
  expect_identical(basename(grep("\\.osexp$", res$files, value = TRUE)),
                   c("r_english_rep1_list1.osexp", "r_english_rep2_list1.osexp",
                     "r_english_rep3_list1.osexp"))
  numbers <- utils::read.csv(file.path(out, "r_english_rep2_list1_opensesame.csv"))
  expect_identical(unique(numbers$replicate), 2L)
})

test_that("the PsychoPy script and the page carry the versions", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  out <- tempfile("lexsync"); dir.create(out)
  two <- two_list_stim(schema)
  versions <- paste0('[{"version":1,"replicate":1,"list":1,"n_trials":2},',
                     '{"version":2,"replicate":1,"list":2,"n_trials":2}]')
  py <- paste(readLines(export_psychopy(two$stimuli, two$design, schema, out), warn = FALSE),
              collapse = "\n")
  expect_true(grepl(sprintf('VERSIONS = json.loads(r"""%s""")', versions), py, fixed = TRUE))
  html <- paste(readLines(export_jspsych(two$stimuli, two$design, schema, out), warn = FALSE),
                collapse = "\n")
  expect_true(grepl(sprintf("const VERSIONS = %s;", versions), html, fixed = TRUE))
  for (text in c(py, html)) expect_false(grepl("{{", text, fixed = TRUE))
})

test_that("a presentation version is numbered by whole-number lists", {
  # A table without `list` or `replicate` is one list of one replicate.
  expect_identical(.presentation_versions(data.frame(word = c("a", "b"))),
                   list(list(version = 1L, replicate = 1L, list = 1L, n_trials = 2L)))
  # Lists are put in numeric order, so list 10 follows list 9.
  v <- .presentation_versions(data.frame(list = c(10, 9, 10)))
  expect_identical(vapply(v, function(x) x$list, integer(1)), c(9L, 10L))
  expect_identical(vapply(v, function(x) x$n_trials, integer(1)), c(1L, 2L))
  expect_error(.presentation_versions(data.frame(list = c("1", "A"))),
               paste("lexsync: the trials' `list` column holds 'A', but a presentation",
                     "version is numbered by whole-number lists and replicates."),
               fixed = TRUE)
  expect_error(.presentation_versions(data.frame(replicate = 1.5)), "column holds '1.5'",
               fixed = TRUE)
  # Both engines read a list by one rule: a number by its value, and text as a plain
  # decimal number. as.numeric() alone took "0x10", Python's float() took "1_0" and other
  # scripts' digits, and as.character() rounded 1.0000000000000002 to 1.
  for (odd in list("1_0", "0x10", intToUtf8(0xFF11), "1e1", 1.0000000000000002)) {
    expect_error(.presentation_versions(data.frame(list = odd)),
                 "presentation version is numbered", fixed = TRUE)
  }
  expect_error(.presentation_versions(data.frame(list = 1.0000000000000002)),
               "holds '1.0000000000000002'", fixed = TRUE)
  v <- .presentation_versions(data.frame(list = c(" 2 ", "2.0", "10", "3")))
  expect_identical(lapply(v, function(x) c(x$list, x$n_trials)),
                   list(c(2L, 2L), c(3L, 1L), c(10L, 1L)))
})

# ---- Trigger codes are checked when the experiment is generated -------------------
#
# A literal code was never range-checked: 300 reached the parallel port, which keeps
# only the low byte, and the serial port's to_bytes(1) raised during the session. A
# misspelt token such as `conditon` made this engine write send_trigger(NA) into the
# OpenSesame experiment, while the Python engine stopped with int()'s own error.
# test_scripting.py pins the same rules, codes and messages.

fix_ev <- list(type = "fixation", content = "+", duration_ms = 500L)
word_ev <- function(trigger) {
  list(type = "text", content = "{word}", duration_ms = 800L, trigger = trigger)
}
with_trigger <- function(ev, trigger) {
  ev$trigger <- trigger
  ev
}
region_item <- list(type = "region_by_region", content = "{sentence}",
                    critical_region_trigger = "item")
# Two conditions crossed with sets 1 to n.
sets_of <- function(n) {
  data.frame(condition = rep(c("a", "b"), n), set = rep(seq_len(n), each = 2L),
             stringsAsFactors = FALSE)
}
item_codes <- function(stim) {
  u <- unique(stim[, c("set", "item_trigger")])
  stats::setNames(u$item_trigger, u$set)
}

test_that("a trigger is condition, item or a code from 1 to 255", {
  spec <- function(trigger) {
    render_events(list(fix_ev, word_ev(trigger)), list(), 60)[[2]]$trigger
  }
  expect_identical(spec("condition"), "@condition_trigger")
  expect_identical(spec("item"), "@item_trigger")
  # A whole number, written as a number or as a string of digits.
  expect_identical(lapply(list(1L, 255L, "20", 20), spec), list(1L, 255L, 20L, 20L))
  bad <- list(list(300L, "300"), list(0L, "0"), list(-5L, "-5"), list("conditon", "conditon"),
              list(20.5, "20.5"), list(TRUE, "true"), list("20 ", "20 "))
  for (case in bad) {
    expect_error(render_events(list(fix_ev, word_ev(case[[1]])), list(), 60),
                 sprintf(paste("lexsync: event 2 has trigger '%s'; use 'condition', 'item' or",
                               "a code from 1 to 255."), case[[2]]),
                 fixed = TRUE)
  }
  region <- region_item
  region$critical_region_trigger <- 256L
  expect_error(render_events(list(region), list(), 60),
               paste("lexsync: event 1 has critical_region_trigger '256'; use 'condition',",
                     "'item' or a code from 1 to 255."), fixed = TRUE)
})

test_that("a literal trigger of 254 or 255 is logged", {
  stim <- sets_of(2)
  expect_identical(
    capture_messages(assign_triggers(stim, events = list(with_trigger(fix_ev, 254L),
                                                         word_ev("condition")))),
    paste("lexsync: event 1 sends code 254, which the PsychoPy and OpenSesame experiments",
          "also send when the session starts.\n"))
  expect_identical(
    capture_messages(assign_triggers(stim, events = list(fix_ev, word_ev(255L)))),
    paste("lexsync: event 2 sends code 255, which the PsychoPy and OpenSesame experiments",
          "also send when the session ends.\n"))
  # export_experiments hands the design's events to assign_triggers.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  out <- tempfile("lexsync"); dir.create(out)
  on.exit(unlink(out, recursive = TRUE), add = TRUE)
  design <- list(name = "t", language = "english",
                 events = list(with_trigger(fix_ev, 254L), word_ev("condition")))
  full <- stim
  full$word <- "cat"
  full$trial <- 1:4
  expect_message(export_experiments(full, design, schema, out),
                 "lexsync: event 1 sends code 254", fixed = TRUE)
})

test_that("a literal trigger that shares a code in use is logged", {
  # A code equal to a condition code the design sends.
  msgs <- capture_messages(out <- assign_triggers(
    sets_of(2), events = list(with_trigger(fix_ev, 102L), word_ev("condition"))))
  expect_identical(msgs,
                   "lexsync: event 1 sends code 102, which is also the condition code of 'b'.\n")
  expect_setequal(unname(item_codes(out)), c(40L, 41L))
  # A code among the item codes the design sends: no item takes it, but a reader who
  # decoded item codes by their range would.
  msgs <- capture_messages(out <- assign_triggers(
    sets_of(10), events = list(with_trigger(fix_ev, 45L), region_item)))
  expect_identical(msgs, paste("lexsync: event 1 sends code 45, which lies inside the range of",
                               "the item codes (40 to 50); decode item codes through the loop",
                               "table.\n"))
  expect_false(45L %in% item_codes(out))
  # A design that sends neither kind of code hears nothing about them.
  expect_silent(assign_triggers(sets_of(10),
                                events = list(with_trigger(fix_ev, 45L), word_ev(102L))))
})

test_that("a 70-set design sending both code kinds has no overlap", {
  expect_silent(out <- assign_triggers(sets_of(70),
                                       events = list(word_ev("condition"), region_item)))
  codes <- item_codes(out)
  expect_false(any(codes %in% c(101L, 102L)))
  expect_identical(length(unique(codes)), 70L)
  # Item codes follow the code-point order of the set labels, so set 10 is 41 and set 2
  # is 51. Sets 65 and 66, which took 101 and 102, take the next free codes.
  expect_identical(unname(codes[c("10", "2", "64", "65", "66")]),
                   c(41L, 51L, 100L, 103L, 104L))
})

test_that("item codes are allocated as before unless both kinds are sent", {
  for (events in list(NULL, list(word_ev("condition")), list(region_item),
                      list(with_trigger(fix_ev, 20L), region_item))) {
    codes <- item_codes(assign_triggers(sets_of(70), events = events))
    expect_identical(unname(codes[c("10", "2", "65", "66")]), c(41L, 51L, 101L, 102L))
  }
})

test_that("item codes beyond the free codes are refused unless overlap is allowed", {
  events <- list(word_ev("condition"), region_item)
  expect_error(assign_triggers(sets_of(199), events = events),
               paste("lexsync: 199 item sets need 199 item codes, but only 198 of the codes",
                     "from 40 to 239 are free of the condition codes and the design's own",
                     "codes; send fewer kinds of code, or set triggers.allow_code_overlap: true",
                     "to let item codes repeat."), fixed = TRUE)
  expect_identical(length(unique(item_codes(assign_triggers(sets_of(198), events = events)))),
                   198L)
  msgs <- capture_messages(out <- assign_triggers(
    sets_of(199), events = events, schema = list(triggers = list(allow_code_overlap = TRUE))))
  expect_identical(msgs, paste("lexsync: 199 item sets exceed the 198 free item codes; item",
                               "codes wrap and repeat.\n"))
  codes <- item_codes(out)
  expect_false(any(codes %in% c(101L, 102L)))
  # The first set's code is the one used twice.
  expect_identical(sum(codes == 40L), 2L)
  expect_identical(length(unique(codes)), 198L)
  expect_error(assign_triggers(sets_of(2), events = events,
                               schema = list(triggers = list(allow_code_overlap = "yes"))),
               "lexsync: triggers.allow_code_overlap must be true or false.", fixed = TRUE)
})

test_that("the trials JSON carries 15 significant digits", {
  # jsonlite wrote four decimal places of a fractional number here and the Python engine
  # every digit, so the page differed between the engines. Both now write 15 significant
  # digits. test_scripting.py pins the same line.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  out <- tempfile("lexsync"); dir.create(out)
  on.exit(unlink(out, recursive = TRUE), add = TRUE)
  stim <- data.frame(word = c("cat", "dog"), condition = c("a", "b"), set = c(1, 1),
                     trial = 1:2, word_ms = c(33.333333, 1000 / 30), stringsAsFactors = FALSE)
  design <- list(name = "t", language = "english", events = list(
    list(type = "text", content = "{word}", duration = list(from_column = "word_ms"))))
  html <- paste(readLines(export_jspsych(assign_triggers(stim), design, schema, out),
                          warn = FALSE), collapse = "\n")
  expect_true(grepl(paste0(
    'const TRIALS = [{"trial":1,"set":1,"condition":"a","word":"cat",',
    '"word_ms":33.333333,"condition_trigger":101,"item_trigger":40},',
    '{"trial":2,"set":1,"condition":"b","word":"dog","word_ms":33.3333333333333,',
    '"condition_trigger":102,"item_trigger":40}];'), html, fixed = TRUE))
})
