# Durations are canonically milliseconds, and both engines must convert alike.
#
# Event durations used to be frame counts that the OpenSesame and jsPsych paths
# converted at a hard-coded 60 Hz, so a design presented different real durations
# on a 120 or 144 Hz monitor depending on which target ran it. Milliseconds are
# now canonical and the PsychoPy script derives flips from the refresh it
# measures.
#
# The conversion is pinned here rather than left implicit because it has to agree
# bit for bit with python_workflow/src/lexsync/scripting.py: the multiplication
# comes first (`frames * 1000 / hz`), which is a different floating-point
# computation from `frames * (1000 / hz)` and agrees with it only by accident of
# the divisor being 60.

priming_events <- list(
  list(type = "fixation", content = "+", duration_frames = 30L),
  list(type = "text", content = "{prime}", duration_frames = 3L, trigger = 20L),
  list(type = "mask", content = "#####", duration_frames = 2L),
  list(type = "text", content = "{target}", duration_frames = 48L, trigger = "condition"),
  list(type = "blank", duration_frames = 15L)
)

ms_of <- function(rendered) vapply(rendered, function(e) as.integer(e$ms), integer(1))

test_that("frames convert at 60 Hz to the documented milliseconds", {
  # The durations the committed OpenSesame goldens time their events by.
  expect_equal(ms_of(render_events(priming_events, list(), 60)),
               c(500L, 50L, 33L, 800L, 250L))
})

test_that("individual frame counts convert as documented", {
  expect_equal(frames_to_ms(30, 60), 500L)
  expect_equal(frames_to_ms(48, 60), 800L)
  expect_equal(frames_to_ms(15, 60), 250L)
  expect_equal(frames_to_ms(3, 60), 50L)
  expect_equal(frames_to_ms(2, 60), 33L)
  expect_equal(frames_to_ms(1, 60), 17L)
})

test_that("a duration declared in milliseconds is independent of the refresh rate", {
  ev <- list(list(type = "fixation", content = "+", duration_ms = 500L))
  for (hz in c(60, 75, 100, 120, 144, 165, 240)) {
    expect_equal(ms_of(render_events(ev, list(), hz)), 500L)
  }
})

test_that("milliseconds win over frames when a design declares both", {
  ev <- list(list(type = "fixation", content = "+", duration_frames = 30L, duration_ms = 123L))
  expect_equal(ms_of(render_events(ev, list(), 60)), 123L)
})

test_that("the timing block overrides by event type in either unit", {
  # word_* reaches only a text event whose trigger is "condition", so the priming
  # prime (trigger 20) keeps its own duration.
  out <- render_events(priming_events,
                       list(fixation_ms = 250L, word_ms = 400L, isi_ms = 900L), 60)
  expect_equal(ms_of(out), c(250L, 50L, 33L, 400L, 900L))
  out <- render_events(priming_events, list(fixation_frames = 15L, word_frames = 24L), 60)
  expect_equal(ms_of(out), c(250L, 50L, 33L, 400L, 250L))
})

test_that("an unknown timing key is rejected rather than ignored", {
  expect_error(render_events(priming_events, list(fixation_frame = 30L), 60),
               "unknown timing key")
})

test_that("the assumed refresh rate is read from the schema and must be positive", {
  expect_equal(lexsync:::.refresh_hz(list()), 60)
  expect_equal(lexsync:::.refresh_hz(list(presentation = list(assumed_refresh_hz = 144))), 144)
  expect_error(lexsync:::.refresh_hz(list(presentation = list(assumed_refresh_hz = 0))),
               "positive")
})

test_that("conversion matches the Python engine over the whole reachable surface", {
  # A golden digest over frames 1..600 at every plausible refresh rate.
  # python_workflow/tests/test_timing.py computes the same digest, so the two
  # suites fail together if either engine's arithmetic drifts. Regenerate both
  # together, never one.
  parts <- character(0)
  for (hz in c(60, 75, 100, 120, 144, 165, 240)) {
    for (frames in 1:600) {
      parts <- c(parts, sprintf("%d:%d:%d", as.integer(hz), frames, frames_to_ms(frames, hz)))
    }
  }
  digest <- digest::digest(paste(parts, collapse = "|"), algo = "sha256", serialize = FALSE)
  expect_equal(digest, "b57787d6860cff4956e5aaa3e5951584c5e55d8064f6cabb2eb9feb66f7a2c13")
})

test_that("the trigger hold is declared in milliseconds", {
  expect_equal(lexsync:::.trigger_hold_ms(list(triggers = list(trigger_hold_ms = 50))), 50)
  expect_equal(lexsync:::.trigger_hold_ms(list()), 50)
  expect_error(lexsync:::.trigger_hold_ms(list(triggers = list(trigger_hold_ms = 0))),
               "positive")
})

test_that("reset_after_frames converts with the off-by-one it actually had", {
  # `reset_after_frames: N` held the code for N + 1 flip intervals, not N: the
  # reset was queued on flip N and callOnFlip fires on the FOLLOWING flip. So
  # converting N directly would silently shorten every trigger by one frame, and
  # the default of 2 must land on 50 ms at 60 Hz rather than 33 ms.
  expect_equal(lexsync:::.trigger_hold_ms(list(triggers = list(reset_after_frames = 2L))), 50)
  expect_equal(lexsync:::.trigger_hold_ms(list(triggers = list(reset_after_frames = 2L))),
               lexsync:::.trigger_hold_ms(list(triggers = list(trigger_hold_ms = 50))))
  # An explicit hold wins over the legacy key.
  expect_equal(lexsync:::.trigger_hold_ms(
    list(triggers = list(trigger_hold_ms = 20, reset_after_frames = 2L))), 20)
})

# ---- A fixed duration is a finite number that is not negative --------------------
#
# duration_ms: -50 was written into the OpenSesame experiment as clock.sleep(-50), this
# engine wrote clock.sleep(NA) for a NaN, and both truncated 33.7 ms to 33.
# test_timing.py pins the same rules and messages.

duration_rule <- "; a duration must be a finite number, not negative."

test_that("a negative or non-finite fixed duration is refused", {
  cases <- list(
    list(list(type = "fixation", content = "+", duration_ms = -50),
         "lexsync: event 1 has duration_ms '-50'"),
    list(list(type = "fixation", content = "+", duration_ms = NaN),
         "lexsync: event 1 has duration_ms 'NaN'"),
    list(list(type = "blank", duration_frames = -2L), "lexsync: event 1 has duration_frames '-2'"),
    list(list(type = "blank", duration_frames = Inf),
         "lexsync: event 1 has duration_frames 'Inf'"),
    list(list(type = "fixation", content = "+", duration_ms = "500ms"),
         "lexsync: event 1 has duration_ms '500ms'"),
    list(list(type = "fixation", content = "+", duration_ms = TRUE),
         "lexsync: event 1 has duration_ms 'true'"))
  for (case in cases) {
    expect_error(render_events(list(case[[1]]), list(), 60), paste0(case[[2]], duration_rule),
                 fixed = TRUE)
  }
})

test_that("a timing block duration is checked like an event's own", {
  expect_error(render_events(priming_events, list(word_ms = -50), 60),
               paste0("lexsync: timing.word_ms is '-50'", duration_rule), fixed = TRUE)
  expect_error(render_events(priming_events, list(isi_frames = NaN), 60),
               paste0("lexsync: timing.isi_frames is 'NaN'", duration_rule), fixed = TRUE)
  # A feedback event is numbered where it stands in the design.
  feedback <- list(list(type = "response"), list(type = "feedback", duration_ms = -1))
  expect_error(render_events(feedback, list(), 60),
               paste0("lexsync: event 2 has duration_ms '-1'", duration_rule), fixed = TRUE)
})

test_that("a fractional fixed duration is rounded, not truncated", {
  ev <- list(list(type = "fixation", content = "+", duration_ms = 33.7),
             list(type = "text", content = "{w}", duration_ms = 82.5, trigger = "condition"),
             list(type = "blank", duration_ms = "250"))
  # The shared rounder takes 82.5 away from zero. A duration written as a plain number
  # in quotes is read as that number, as before.
  expect_identical(ms_of(render_events(ev, list(), 60)), c(34L, 83L, 250L))
  expect_identical(render_events(ev, list(word_ms = 400.5), 60)[[2]]$ms, 401L)
  # A null duration_frames is absent, so the default of one frame applies.
  expect_identical(render_events(list(list(type = "blank", duration_frames = NULL)), list(),
                                 60)[[1]]$ms, 17L)
})
