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
    # loop, and no run line carries a condition.
    expect_true("define inline_script lexsync_version_check" %in% lines)
    expect_true(sprintf("\t_version = %d", k) %in% lines)
    expect_true("\t_versions = 2" %in% lines)
    runs <- grep("^\trun ", lines, value = TRUE)
    expect_identical(utils::tail(runs, 3),
                     c("\trun lexsync_trigger_setup always",
                       "\trun lexsync_version_check always", "\trun lexsync_loop always"))
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
