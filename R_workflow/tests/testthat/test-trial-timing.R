# Per-trial event durations: jittered, or read from an item column.
#
# A fixed duration is a property of the design; one that varies from trial to
# trial is a property of the trial, and therefore a variable the analysis needs.
# Both forms are resolved into the stimuli table before anything is generated, so
# the realised milliseconds travel with the stimuli rather than living only inside
# the presentation script.
#
# The jitter draws no random number. It is a uniform integer keyed on the seed,
# the column name, the list, the set and the condition, so the two engines realise
# the same milliseconds and a rerun reproduces them. Naming the column in the key
# is what makes two jittered events in one design draw independently instead of
# sharing a value.
#
# python_workflow/tests/test_trial_timing.py asserts the same values.

schema <- list(seed = 42L)

events <- list(
  list(type = "fixation", content = "+", duration_ms = 500L),
  list(type = "text", content = "{prime}", duration = list(from_column = "soa_ms"), trigger = 20L),
  list(type = "text", content = "{target}", duration_ms = 800L, trigger = "condition"),
  list(type = "blank", duration = list(jitter = c(400L, 800L), as = "isi_ms"))
)

stim <- data.frame(
  set = 1:4,
  condition = c("related", "unrelated", "related", "unrelated"),
  list = c(1L, 1L, 2L, 2L),
  prime = c("cat", "sun", "dog", "car"),
  target = c("pet", "sky", "pet", "van"),
  soa_ms = c(60L, 250L, 1200L, 60L),
  trial = 1:4,
  stringsAsFactors = FALSE
)

test_that("a jittered duration lands in the stimuli table within its range", {
  out <- resolve_trial_timing(stim, list(events = events), schema)
  expect_true("isi_ms" %in% names(out))
  expect_true(all(out$isi_ms >= 400 & out$isi_ms <= 800))
  # Deterministic: the same inputs give the same milliseconds every time.
  expect_equal(out$isi_ms, resolve_trial_timing(stim, list(events = events), schema)$isi_ms)
})

test_that("the realised values match the Python engine", {
  out <- resolve_trial_timing(stim, list(events = events), schema)
  expect_equal(out$isi_ms, c(537L, 583L, 764L, 594L))
})

test_that("the seed changes the draw", {
  a <- resolve_trial_timing(stim, list(events = events), list(seed = 42L))$isi_ms
  b <- resolve_trial_timing(stim, list(events = events), list(seed = 43L))$isi_ms
  expect_false(identical(a, b))
})

test_that("two jittered events draw independently", {
  ev <- list(
    list(type = "blank", duration = list(jitter = c(0L, 1000L), as = "gap_a_ms")),
    list(type = "blank", duration = list(jitter = c(0L, 1000L), as = "gap_b_ms"))
  )
  out <- resolve_trial_timing(stim, list(events = ev), schema)
  # Sharing a key would make these identical; the column name is in the key.
  expect_false(identical(out$gap_a_ms, out$gap_b_ms))
  expect_equal(out$gap_a_ms, c(76L, 51L, 593L, 690L))
  expect_equal(out$gap_b_ms, c(460L, 499L, 442L, 125L))
})

test_that("a column duration is referenced rather than baked in", {
  rendered <- render_events(events, list(), 60)
  expect_equal(rendered[[1]]$ms, 500L)              # fixed, resolved at build time
  expect_equal(rendered[[2]]$ms_column, "soa_ms")   # per trial, resolved at run time
  # [[ ]], not $: `$` would partial-match `ms_column` and return it.
  expect_null(rendered[[2]][["ms"]])
  expect_equal(rendered[[4]]$ms_column, "isi_ms")
})

test_that("the loop table carries every per-trial duration column", {
  out <- resolve_trial_timing(stim, list(events = events), schema)
  tab <- lexsync:::loop_table(out, events)
  expect_true(all(c("soa_ms", "isi_ms") %in% names(tab)))
})

test_that("a missing source column is an error, not a silent default", {
  ev <- list(list(type = "blank", duration = list(from_column = "not_there")))
  expect_error(resolve_trial_timing(stim, list(events = ev), schema),
               "which the items do not have")
})

test_that("a malformed duration block is rejected", {
  expect_error(render_events(list(list(type = "blank", duration = list(jitter = 400L))), list(), 60),
               "two-element range")
  expect_error(render_events(list(list(type = "blank", duration = list(nonsense = 1L))), list(), 60),
               "from_column' or 'jitter'")
})

test_that("an unnamed jitter column falls back to the event index", {
  ev <- list(type = "blank", duration = list(jitter = c(10L, 20L)))
  expect_equal(lexsync:::.duration_spec(ev, 2L)$column, "event2_ms")
})

test_that("key parts render integral doubles the way Python does", {
  # The hazard this guards: a pandas column promoted to float64 by one missing
  # value would otherwise key on "3.0" in Python and "3" in R.
  expect_equal(lexsync:::.key_part(3L), "3")
  expect_equal(lexsync:::.key_part(3.0), "3")
  expect_equal(lexsync:::.key_part(-7.0), "-7")
  expect_equal(lexsync:::.key_part("related"), "related")
  expect_equal(lexsync:::.key_part(2.5), "2.5")
})


test_that("a hash-key component that cannot be rendered identically is refused", {
  # Measured divergence before this: a missing value rendered "NA" here and "nan" in
  # Python, TRUE/FALSE against True/False, Inf against inf. A blank `condition` cell is a
  # routine data error that neither reader rejects, and it produced a DIFFERENT trial
  # order in each engine -- reproducibly, with nothing to signal it.
  expect_error(lexsync:::.key_part(NA), "missing")
  expect_error(lexsync:::.key_part(c(1, NA)), "missing")
  expect_error(lexsync:::.key_part(NA_character_), "missing")
  expect_error(lexsync:::.key_part(Inf), "not finite")
  # Booleans are legitimate, so they get a pinned spelling rather than a refusal.
  # test_trial_timing.py asserts the same two strings.
  expect_identical(lexsync:::.key_part(TRUE), "TRUE")
  expect_identical(lexsync:::.key_part(FALSE), "FALSE")
  # A value past the integer range would make as.integer() return NA, which would put
  # an empty component into the key.
  expect_identical(lexsync:::.key_part(3e9), "3000000000")
})

# ---- A duration read from the items is checked, and a fractional one rounded --------
#
# A blank or negative value used to reach the experiments, where OpenSesame's int('')
# and PsychoPy's float('') raised during the session and jsPsych ended the trial at
# once. A fractional value kept all its digits, which jsonlite cut to four decimal
# places here, so the two engines' jsPsych pages differed. test_trial_timing.py pins the
# same values and messages.

with_soa <- function(values) {
  out <- stim
  out$soa_ms <- values
  out
}

test_that("a fractional column duration is rounded once and recorded", {
  # A frame at 60 Hz lasts 1000/60 ms, which an item table carries to six places.
  out <- resolve_trial_timing(with_soa(c(33.333333, 250, 82.5, 66.666667)),
                              list(events = events), schema)
  # The shared rounder takes 82.5 away from zero, where R's round() gives 82.
  expect_equal(out$soa_ms, c(33, 250, 83, 67))
  expect_identical(attr(out, "duration_rounding"),
                   list(list(event = 2L, column = "soa_ms", n_rounded = 3L)))
  expect_equal(lexsync:::loop_table(out, events)$soa_ms, c(33, 250, 83, 67))
  # Rounded once: the realised table has nothing left to round, and the record of the
  # first call does not carry over to the second.
  again <- resolve_trial_timing(out, list(events = events), schema)
  expect_equal(again$soa_ms, c(33, 250, 83, 67))
  expect_null(attr(again, "duration_rounding"))
})

test_that("whole column durations are left as they are", {
  out <- resolve_trial_timing(stim, list(events = events), schema)
  expect_identical(out$soa_ms, stim$soa_ms)
  expect_null(attr(out, "duration_rounding"))
})

test_that("a column duration that is blank, negative or not a number is refused", {
  cases <- list(list(NaN, "is blank"), list(NA, "is blank"), list(-50, "holds '-50'"),
                list(Inf, "holds 'Inf'"))
  for (case in cases) {
    expect_error(
      resolve_trial_timing(with_soa(c(60, case[[1]], 1200, 60)), list(events = events), schema),
      sprintf(paste("lexsync: event 2 reads its duration from column 'soa_ms', which %s for",
                    "set 2 in condition 'unrelated'; a duration must be a finite number of",
                    "milliseconds, not negative."), case[[2]]),
      fixed = TRUE)
  }
  # A column holding text is read as numbers where it can be, so the refusal names the
  # cell that is not one.
  expect_error(
    resolve_trial_timing(with_soa(c("60", "fast", "1200", "60")), list(events = events), schema),
    "which holds 'fast' for set 2 in condition 'unrelated'", fixed = TRUE)
  # A column of booleans is not a duration either, although Python counts True as 1.
  expect_error(
    resolve_trial_timing(with_soa(c(TRUE, FALSE, TRUE, FALSE)), list(events = events), schema),
    "which holds 'true' for set 1 in condition 'related'", fixed = TRUE)
})

test_that("a refused column duration names the block of its trial", {
  blocked <- with_soa(c(60, 250, -1, 60))
  blocked$block <- c("practice", "main", "main", "main")
  expect_error(resolve_trial_timing(blocked, list(events = events), schema),
               "which holds '-1' for set 3 in condition 'related' of block 'main'",
               fixed = TRUE)
})

test_that("a jitter range must start at zero or more", {
  bad <- list(list(c(-100L, 200L), "[-100, 200]"), list(c(0, NaN), "[0, NaN]"))
  for (case in bad) {
    ev <- list(list(type = "blank", duration = list(jitter = case[[1]])))
    expect_error(render_events(ev, list(), 60),
                 sprintf(paste("lexsync: event 1 has jitter %s; a jittered duration needs",
                               "finite bounds, the lower one not negative."), case[[2]]),
                 fixed = TRUE)
  }
  # Zero is a duration like any other.
  ok <- render_events(list(list(type = "blank", duration = list(jitter = c(0L, 200L)))),
                      list(), 60)
  expect_identical(ok[[1]]$ms_column, "event1_ms")
})
