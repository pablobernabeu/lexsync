# Masked priming, the letter case of a text event, and the reproductions that use them.
#
# The `priming` paradigm shows the prime, a '#####' mask and the target, with no forward
# mask and both strings in the item table's case, and it ends in a separate response
# window. It is backward-masked priming, yet it drove the Rastle, Davis and New (2004)
# reproduction, and without a forward mask a brief prime is usually visible (Forster &
# Davis, 1984). The Andrews (1989) reproduction had no nonwords, so neither ran as the
# lexical decision it reproduces.
#
# `masked_priming` shows a forward mask of hash marks as long as the longest prime or
# target, a lower-case prime for three frames and an upper-case target that stays until
# the response. The mask is sized from the trials when the experiments are written, and
# the case is applied by the runners as they show the text, because R's toupper() leaves
# the German sharp s as it is where Python and JavaScript give 'SS'. test_masked_priming.py
# holds the Python engine to the same tests, by the same names. The runners themselves
# are tested in the Python suite, since each template is one shared file.

mp_schema <- function() {
  yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
}
mp_out <- function() {
  d <- tempfile("lexsync-")
  dir.create(d, recursive = TRUE, showWarnings = FALSE)
  d
}
mp_csv <- function(path) {
  utils::read.csv(path, colClasses = "character", na.strings = character(0),
                  check.names = FALSE, encoding = "UTF-8")
}
mp_text <- function(path) {
  paste(readLines(path, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
}
mp_embedded <- function(path, pattern) {
  text <- mp_text(path)
  jsonlite::fromJSON(regmatches(text, regexec(pattern, text))[[1]][2],
                     simplifyVector = FALSE)
}
mp_psychopy_events <- function(path) mp_embedded(path, 'EVENTS = json\\.loads\\(r"""(.*?)"""\\)')
mp_page_events <- function(path) mp_embedded(path, "const EVENTS = (.*?);\\n")

# The registry as both engines serialise it: each paradigm by name, in byte order, with
# its fields, its recipe and its events. test_masked_priming.py pins the same digest, so
# a paradigm changed in one engine only fails both suites.
mp_registry_json <- function() {
  as.character(jsonlite::toJSON(lapply(sort(names(PARADIGMS), method = "radix"), function(name) {
    p <- PARADIGMS[[name]]
    list(name = name, stimulus_fields = as.list(p$stimulus_fields),
         counterbalance = p$counterbalance, events = p$events)
  }), auto_unbox = TRUE))
}

test_that("the_paradigm_registry_is_the_same_in_both_engines", {
  expect_identical(digest::digest(mp_registry_json(), algo = "sha256", serialize = FALSE),
                   "caa39a2fba929cb8279de523db3d023b4db1fb0b60c24c39cf7e48bd245b090c")
})

test_that("masked_priming_shows_a_forward_mask_a_prime_and_an_upper_case_target", {
  p <- PARADIGMS[["masked_priming"]]
  expect_identical(p$stimulus_fields, c("prime", "target"))
  expect_identical(p$counterbalance, "latin_square_target")
  expect_identical(required_fields(list(paradigm = "masked_priming")), c("prime", "target"))
  rendered <- render_events(resolve_events(list(paradigm = "masked_priming")), list(), 60)
  expect_identical(
    as.character(jsonlite::toJSON(rendered, auto_unbox = TRUE)),
    paste0('[{"type":"mask","text":"#","length_of":["prime","target"],"ms":500},',
           '{"type":"text","field":"prime","ms":50,"trigger":20,"case":"lower"},',
           '{"type":"text","field":"target","ms":2000,"trigger":"@condition_trigger",',
           '"case":"upper","respond":{"keys":["left","right"],"timeout":0}},',
           '{"type":"blank","ms":250}]'))
  # The backward-masked paradigm is as it was.
  expect_identical(vapply(PARADIGMS[["priming"]]$events, function(e) e$type, character(1)),
                   c("fixation", "text", "mask", "text", "response", "blank"))
  expect_false(any(vapply(PARADIGMS[["priming"]]$events, function(e) !is.null(e$case),
                          logical(1))))
})

test_that("a_text_event_carries_its_case_to_the_runners", {
  events <- list(
    list(type = "text", content = "{prime}", duration_ms = 50L, case = "lower"),
    list(type = "text", content = "{target}", duration_ms = 500L, case = "upper"),
    list(type = "text", content = "{target}", duration_ms = 500L))
  expect_identical(lapply(render_events(events, list(), 60), function(e) e[["case"]]),
                   list("lower", "upper", NULL))
  for (bad in c("Upper", "title")) {
    expect_error(
      render_events(list(list(type = "text", content = "{target}", case = bad)), list(), 60),
      sprintf(paste("lexsync: event 1 has case '%s'; a text event takes case: upper or",
                    "case: lower."), bad), fixed = TRUE)
  }
  expect_error(
    render_events(list(list(type = "mask", content = "#####", case = "upper")), list(), 60),
    "lexsync: event 1 is a mask event, and only a text event takes `case`.", fixed = TRUE)
})

test_that("a_mask_sized_from_the_trials_needs_one_character_and_named_fields", {
  # A scalar names one field, as a YAML scalar `length_of: target` would.
  expect_identical(render_events(list(list(type = "mask", content = "#", length_of = "target")),
                                 list(), 60)[[1]][["length_of"]], list("target"))
  for (content in c("##", "{prime}", "")) {
    expect_error(
      render_events(list(list(type = "mask", content = content, length_of = list("prime"))),
                    list(), 60),
      paste("lexsync: event 1 repeats its content to the length of the longest text of the",
            "trials, so its content must be one character, such as '#'."), fixed = TRUE)
  }
  expect_error(
    render_events(list(list(type = "mask", content = "#", length_of = "two words")), list(), 60),
    paste("lexsync: event 1 has length_of 'two words'; name the fields whose longest text",
          "sets the mask's length, as in [prime, target]."), fixed = TRUE)
  expect_error(
    render_events(list(list(type = "text", content = "x", length_of = list("prime"))),
                  list(), 60),
    "lexsync: event 1 is a text event, and only a mask event takes `length_of`.",
    fixed = TRUE)
})

# Two targets over two lists. The prime "Naivete", with its diaeresis and acute accent,
# has seven characters and nine UTF-8 bytes, so a mask counted in bytes would be two
# marks too long, and the sharp s of the target "strasse" upper-cases differently in R.
mp_primed <- function() {
  items <- data.frame(prime = c("Naïveté", "cat", "dog", "sun"),
                      target = c("straße", "straße", "moon", "moon"),
                      condition = rep(c("related", "unrelated"), 2), set = c(1L, 1L, 2L, 2L),
                      stringsAsFactors = FALSE)
  design <- list(name = "mp", language = "english", paradigm = "masked_priming",
                 counterbalance = list(lists = 2L))
  list(stim = counterbalance(items, design, mp_schema()), design = design)
}

test_that("the_experiments_carry_the_forward_mask_and_the_case", {
  p <- mp_primed()
  out <- mp_out()
  res <- export_experiments(p$stim, p$design, mp_schema(), out)
  for (events in list(mp_psychopy_events(res$psychopy), mp_page_events(res$jspsych))) {
    expect_identical(events[[1]], list(type = "mask", text = "#######", ms = 500L))
    expect_identical(lapply(events, function(e) e[["case"]]),
                     list(NULL, "lower", "upper", NULL))
    # The item text travels unchanged: the runner applies the case as it shows it.
    expect_identical(events[[3]][["field"]], "target")
  }
  experiments <- grep("\\.osexp$", res$files, value = TRUE)
  expect_length(experiments, 2L)
  for (path in experiments) {
    osexp <- mp_text(path)
    # One mask for every version, sized from all the trials.
    expect_true(grepl("\t_lexsync_c_e0.text(u'#######')", osexp, fixed = TRUE))
    expect_true(grepl("\t_lexsync_c_e1.text(_lexsync_row()[u'prime'].lower())", osexp,
                      fixed = TRUE))
    expect_true(grepl("\t_lexsync_c_e2.text(_lexsync_row()[u'target'].upper())", osexp,
                      fixed = TRUE))
  }
  # The loop table keeps each item as it was written.
  table <- mp_csv(file.path(out, "mp_english_psychopy.csv"))
  expect_identical(sort(unique(table$target), method = "radix"), c("moon", "straße"))
  expect_true("Naïveté" %in% table$prime)
})

test_that("a_mask_needs_the_fields_it_is_sized_from", {
  p <- mp_primed()
  design <- list(name = "mp", language = "english", counterbalance = list(lists = 2L),
                 events = list(
                   list(type = "mask", content = "#", length_of = list("cue"),
                        duration_ms = 500L),
                   list(type = "text", content = "{target}", duration_ms = 500L,
                        trigger = "condition")))
  expect_error(export_experiments(p$stim, design, mp_schema(), mp_out()),
               "lexsync: a mask takes its length from field 'cue', which the trials do not have.",
               fixed = TRUE)
})

# ---- The reproductions -----------------------------------------------------------------

test_that("the_reproductions_run_as_lexical_decisions", {
  rastle <- yaml::read_yaml(repo_path("config", "design_en_rastle_repro.yaml"))
  expect_identical(rastle$paradigm, "masked_priming")
  expect_identical(rastle$fillers, list(path = "items/rastle_nonword_fillers_en.csv"))
  expect_identical(rastle$response_mapping, list(related = "left", unrelated = "left"))
  andrews <- yaml::read_yaml(repo_path("config", "design_en_andrews_repro.yaml"))
  expect_identical(andrews$fillers, list(path = "items/andrews_pseudoword_fillers_en.csv"))
  expect_identical(unique(unlist(andrews$response_mapping)), "left")
  cases <- list(list(stem = "en_rastle_repro", n = 12L, filler = "nonword"),
                list(stem = "en_andrews_repro", n = 72L, filler = "pseudoword"))
  for (case in cases) {
    table <- mp_csv(repo_path("output", "experiments",
                              paste0(case$stem, "_english_psychopy.csv")))
    for (lst in unique(table$list)) {
      rows <- table[table$list == lst, , drop = FALSE]
      main <- rows[rows$block == "main", , drop = FALSE]
      fillers <- rows[rows$block == "filler", , drop = FALSE]
      expect_identical(c(nrow(main), nrow(fillers)), c(case$n, case$n))
      # Every trial is scored: a word takes the left arrow, a nonword the right.
      expect_identical(unique(main$answer), "left")
      expect_identical(unique(fillers$answer), "right")
      expect_identical(unique(fillers$condition), case$filler)
      # The fillers are interleaved with the words, not appended to them.
      expect_length(unique(rows$block[seq_len(case$n)]), 2L)
    }
  }
  script <- repo_path("output", "experiments", "en_rastle_repro_english_psychopy.py")
  events <- mp_psychopy_events(script)
  table <- mp_csv(repo_path("output", "experiments", "en_rastle_repro_english_psychopy.csv"))
  longest <- max(nchar(c(table$prime, table$target), type = "chars"))
  expect_identical(events[[1]], list(type = "mask", text = strrep("#", longest), ms = 500L))
  expect_identical(lapply(events, function(e) e[["case"]]), list(NULL, "lower", "upper", NULL))
})

test_that("the_reproductions_nonwords_are_new_forms_of_their_words_lengths", {
  known <- readLines(repo_path("corpora", "derived", "en_known_forms.txt"), encoding = "UTF-8")
  v2 <- mp_csv(repo_path("corpora", "derived", "en_v2.csv"))
  items <- mp_csv(repo_path("items", "rastle_priming_en.csv"))
  fillers <- mp_csv(repo_path("items", "rastle_nonword_fillers_en.csv"))
  expect_identical(names(fillers), c("item", "condition", "prime", "target", "answer"))
  words <- unique(items$target)
  expect_identical(c(nrow(fillers), length(words)), c(12L, 12L))
  expect_identical(sort(nchar(fillers$target)), sort(nchar(words)))
  expect_length(intersect(fillers$target, known), 0L)
  # Each nonword target has a real, screened word as its prime, used nowhere else.
  expect_false(anyDuplicated(fillers$prime) > 0)
  expect_length(intersect(fillers$prime, c(items$prime, items$target)), 0L)
  expect_true(all(v2$nonstandard[match(fillers$prime, v2$word)] == "0"))
  andrews <- mp_csv(repo_path("items", "andrews_pseudoword_fillers_en.csv"))
  expect_identical(names(andrews), c("item", "condition", "word", "answer"))
  selected <- mp_csv(repo_path("output", "stimuli",
                               "en_andrews_repro_english_stimuli_R.csv"))$word
  expect_identical(c(nrow(andrews), length(selected)), c(72L, 72L))
  expect_identical(sort(nchar(andrews$word)), sort(nchar(selected)))
  expect_false(anyDuplicated(andrews$word) > 0)
  expect_length(intersect(andrews$word, known), 0L)
})
