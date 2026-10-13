# Instructions, the response mapping and the answers it gives every trial.
#
# No generated experiment said which key meant what. jsPsych named the keys and nothing
# more, PsychoPy and OpenSesame started the trials at once, and a generated lexical
# decision had no `answer` column, so its main trials could not be scored. The practice
# table presented the word 'plank' as a pseudoword, and every categorisation item was a
# 'yes' trial, so pressing f on every trial scored 100%.
#
# A design may now give `instructions`, `response_mapping` and `rotate_mapping_by_list`.
# A lexical decision maps word to the response event's first key and pseudoword to its
# second by default, and lexsync writes English instructions for the tasks it knows. The
# loop tables carry each trial's correct key in `answer`, derived when the experiments
# are exported, and the stimuli file does not change. test_instructions.py holds the
# Python engine to the same tests, by the same names. The runners' start gate is tested
# in the Python suite, since each template is one shared file.

instr_schema <- function() {
  yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
}
instr_out <- function() {
  d <- tempfile("lexsync-")
  dir.create(d, recursive = TRUE, showWarnings = FALSE)
  d
}
instr_read <- function(path) {
  utils::read.csv(path, colClasses = "character", na.strings = character(0),
                  encoding = "UTF-8", check.names = FALSE)
}
# One of the JSON blobs a jsPsych page embeds, read back.
instr_page <- function(path, name) {
  html <- paste(readLines(path, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
  found <- regmatches(html, regexec(sprintf("const %s = (.*?);\\n", name), html))[[1]][2]
  jsonlite::fromJSON(found, simplifyDataFrame = FALSE)
}

INSTR_LEXDEC <- list(name = "t", language = "english", paradigm = "lexical_decision")
# The events of en_lexdec_blocks: keys f and j, and feedback during practice only.
INSTR_EVENTS <- list(
  list(type = "fixation", content = "+", duration_ms = 500L),
  list(type = "text", content = "{target}", duration_ms = 800L, trigger = "condition"),
  list(type = "response", keys = c("f", "j"), timeout_ms = 2000L),
  list(type = "feedback", answer = "answer", duration_ms = 600L, blocks = list("practice")),
  list(type = "blank", duration_ms = 250L))
INSTR_BLOCKS <- utils::modifyList(INSTR_LEXDEC, list(events = INSTR_EVENTS))

lexdec_text <- function(word, pseudoword) {
  sprintf(paste("You will see a string of letters. Press %s if it is a real English word",
                "and %s if it is not. Respond as quickly and accurately as you can."),
          word, pseudoword)
}
language_note <- function(language) {
  sprintf(paste("lexsync: the design gives no `instructions` and its language is '%s', so",
                "the experiments show lexsync's instructions in English; give `instructions`",
                "in the participants' language."), language)
}
task_note <- function(paradigm) {
  sprintf(paste("lexsync: the design gives no `instructions`, and lexsync cannot tell what the",
                "response keys of a %s design mean, so the experiments only name the keys;",
                "give `instructions` that say what each key means."), paradigm)
}

# Two words and two pseudowords in one list, with no answer of their own, as the
# generator writes them.
instr_lexdec_stim <- function() {
  data.frame(target = c("cat", "dog", "cag", "dop"),
             condition = c("word", "word", "pseudoword", "pseudoword"),
             set = c(1L, 2L, 1L, 2L), trial = 1:4, list = rep(1L, 4),
             stringsAsFactors = FALSE)
}

# Practice rows that name their answer, then main rows that do not, in each list.
instr_blocks_stim <- function(lists = 1L) {
  one <- function(lst) {
    data.frame(target = c("clock", "plang", "cat", "cag", "dog", "dop"),
               condition = rep(c("word", "pseudoword"), 3),
               answer = c("f", "j", NA, NA, NA, NA),
               set = c(3L, 4L, 1L, 1L, 2L, 2L),
               block = c("practice", "practice", rep("main", 4)),
               list = lst, trial = 1:6, stringsAsFactors = FALSE)
  }
  out <- do.call(rbind, lapply(lists, one))
  rownames(out) <- NULL
  out
}

main_answers <- function(stim) {
  main <- stim[stim$block == "main", , drop = FALSE]
  out <- list()
  for (lst in sort(unique(main$list))) {
    for (cond in c("word", "pseudoword")) {
      out[[sprintf("%d %s", lst, cond)]] <-
        sort(unique(main$answer[main$list == lst & main$condition == cond]))
    }
  }
  out
}

test_that("a_lexical_decision_takes_its_answers_from_the_response_mapping", {
  # The paradigm's events allow left and right, so word takes left and pseudoword
  # right, and every main trial can be scored.
  out <- instr_out()
  export_experiments(instr_lexdec_stim(), INSTR_LEXDEC, instr_schema(), out)
  loop <- instr_read(file.path(out, "t_english_psychopy.csv"))
  expect_identical(names(loop), c("trial", "list", "set", "condition", "target", "answer",
                                  "condition_trigger", "item_trigger"))
  expect_identical(loop$answer, c("left", "left", "right", "right"))
  text <- instr_read(file.path(out, "t_english_opensesame_text.csv"))
  expect_identical(text$answer, c("left", "left", "right", "right"))
  # The jsPsych page names them as the browser does (see the test below).
  trials <- instr_page(file.path(out, "t_english.html"), "TRIALS")
  expect_identical(vapply(trials, function(t) t$answer, character(1)),
                   c("arrowleft", "arrowleft", "arrowright", "arrowright"))
  # The answers are derived for the export, so the frame passed in is unchanged.
  stim <- instr_lexdec_stim()
  export_experiments(stim, INSTR_LEXDEC, instr_schema(), out)
  expect_false("answer" %in% names(stim))
})

test_that("main_trials_follow_the_keys_of_the_practice_table", {
  # en_lexdec_blocks's events allow f and j, and its practice table codes word as f, so
  # its main trials take f for a word and j for a pseudoword. Rows that name their own
  # answer keep it.
  res <- .assign_answers(instr_blocks_stim(), INSTR_BLOCKS)
  expect_identical(res$notes, character(0))
  expect_identical(main_answers(res$stimuli), list(`1 word` = "f", `1 pseudoword` = "j"))
  expect_identical(res$stimuli$answer[res$stimuli$block == "practice"], c("f", "j"))
  out <- instr_out()
  export_experiments(instr_blocks_stim(), INSTR_BLOCKS, instr_schema(), out)
  loop <- instr_read(file.path(out, "t_english_psychopy.csv"))
  expect_identical(loop$answer, unname(c(word = "f", pseudoword = "j")[loop$condition]))
})

test_that("the_jspsych_page_names_each_answer_as_the_browser_does", {
  # jsPsych records a key by the browser's name for it, arrowleft for the left arrow,
  # and the page's events name the keys so, but its trials named each answer as the
  # other targets do, left. No correct response then equalled its trial's answer, and a
  # feedback screen called every correct response incorrect. The page now names an
  # answer as it names the keys, and the loop tables keep the other targets' names.
  out <- instr_out()
  res <- export_experiments(instr_lexdec_stim(), INSTR_LEXDEC, instr_schema(), out)
  respond <- Filter(Negate(is.null), lapply(instr_page(res$jspsych, "EVENTS"),
                                            function(e) e$respond))
  expect_identical(lapply(respond, function(r) unlist(r$keys)),
                   list(c("arrowleft", "arrowright")))
  expect_identical(vapply(instr_page(res$jspsych, "TRIALS"), function(t) t$answer,
                          character(1)),
                   c("arrowleft", "arrowleft", "arrowright", "arrowright"))
  expect_identical(instr_read(file.path(out, "t_english_psychopy.csv"))$answer,
                   c("left", "left", "right", "right"))
  # A trial's own answer is mapped as well, around the spaces a runner ignores, and a
  # key the browser names as lexsync does is left alone.
  events <- lapply(INSTR_EVENTS, function(e) {
    if (identical(e$type, "response")) utils::modifyList(e, list(keys = c("space", "return")))
    else e
  })
  stim <- instr_blocks_stim()
  stim$answer <- c(" space", "j", NA, NA, NA, NA)
  res <- export_experiments(stim, utils::modifyList(INSTR_LEXDEC, list(events = events)),
                            instr_schema(), instr_out())
  got <- vapply(instr_page(res$jspsych, "TRIALS"),
                function(t) paste(t$block, t$condition, t$answer, sep = "|"), character(1))
  expect_setequal(got, c("practice|word| ", "practice|pseudoword|j", "main|word| ",
                         "main|pseudoword|enter"))
})

test_that("an_answer_read_as_a_number_keeps_the_text_of_its_cell", {
  # A practice table that codes its answers as number keys is read with a numeric
  # answer column, which the Python engine holds as floats once the main trials'
  # missing answers join it. It compared the answer 1.0 with the key 1 as '1.0' and
  # wrote it into the page as a number, where this engine wrote text. Both engines now
  # take such an answer as the text its loop-table cell holds.
  events <- lapply(INSTR_EVENTS, function(e) {
    if (identical(e$type, "response")) utils::modifyList(e, list(keys = c(1L, 2L))) else e
  })
  design <- utils::modifyList(INSTR_LEXDEC, list(events = events))
  stim <- instr_blocks_stim()
  stim$answer <- c(1, 2, NA, NA, NA, NA)
  res <- .assign_answers(stim, design)
  expect_identical(res$notes, character(0))
  expect_identical(res$stimuli$answer, c("1", "2", "1", "2", "1", "2"))
  page <- export_experiments(stim, design, instr_schema(), instr_out())$jspsych
  expect_identical(sort(unique(vapply(instr_page(page, "TRIALS"), function(t) t$answer,
                                      character(1)))), c("1", "2"))
  # The text is what both engines' CSV writers write: 100000, not as.character()'s 1e+05.
  expect_identical(.answer_text(c(100000, 2.5, NA)), c("100000", "2.5", NA))
  expect_identical(.answer_text(c(TRUE, NA)), c("TRUE", NA))
  expect_identical(.answer_text(c(" f ", NA)), c(" f ", NA))
})

test_that("a_mapping_naming_a_key_the_response_does_not_allow_is_refused", {
  schema <- instr_schema()
  expect_error(validate_design(utils::modifyList(INSTR_BLOCKS, list(
    response_mapping = list(word = "k", pseudoword = "j"))), schema),
    "lexsync: response_mapping maps 'word' to 'k', but the response event allows only f and j.",
    fixed = TRUE)
  shape <- paste("lexsync: response_mapping must map each condition to one response key, as",
                 "in {word: f, pseudoword: j}.")
  for (bad in list(stats::setNames(list(), character(0)), list("f", "j"),
                   list(word = list("f", "j")), list(word = NULL), list(word = TRUE))) {
    design <- INSTR_BLOCKS
    design["response_mapping"] <- list(bad)
    expect_error(validate_design(design, schema), shape, fixed = TRUE)
  }
  passive <- list(name = "t", language = "english", events = INSTR_EVENTS[1:2],
                  response_mapping = list(word = "f"))
  expect_error(validate_design(passive, schema),
               paste("lexsync: the design gives `response_mapping`, but none of its events is",
                     "a response whose keys it could name."), fixed = TRUE)
  # A key the response allows passes, and the default needs no key at all.
  expect_identical(validate_design(utils::modifyList(INSTR_BLOCKS, list(
    response_mapping = list(word = "j", pseudoword = "f"))), schema), character(0))
  expect_identical(validate_design(INSTR_BLOCKS, schema), character(0))
})

test_that("a_declared_mapping_must_cover_the_trials_conditions", {
  stim <- instr_lexdec_stim()
  stim$condition[stim$condition == "pseudoword"] <- "nonword"
  expect_error(.assign_answers(stim, utils::modifyList(INSTR_BLOCKS, list(
    response_mapping = list(word = "f")))),
    paste("lexsync: response_mapping gives no key for condition 'nonword', and 2 trial(s)",
          "of it have no answer of their own."), fixed = TRUE)
  expect_error(export_experiments(instr_lexdec_stim(), utils::modifyList(INSTR_BLOCKS, list(
    response_mapping = list(word = "f", pseudoword = "j", pseudowrod = "j"))),
    instr_schema(), instr_out()),
    paste("lexsync: response_mapping names condition 'pseudowrod', which no trial has; the",
          "trials' conditions are word and pseudoword."), fixed = TRUE)
  # The default maps word and pseudoword only, and says so for any other condition.
  res <- .assign_answers(stim, INSTR_BLOCKS)
  expect_identical(res$stimuli$answer, c("f", "f", NA, NA))
  expect_identical(res$notes, paste(
    "lexsync: 2 trial(s) of condition 'nonword' have no answer, since the lexical-decision",
    "default maps only word and pseudoword; give `response_mapping`."))
})

test_that("rotation_swaps_the_keys_on_list_two", {
  # List k moves each key k - 1 places along the response event's keys, a swap on every
  # even-numbered list when there are two.
  design <- utils::modifyList(INSTR_BLOCKS, list(rotate_mapping_by_list = TRUE))
  res <- .assign_answers(instr_blocks_stim(1:2), design)
  expect_identical(main_answers(res$stimuli), list(`1 word` = "f", `1 pseudoword` = "j",
                                                   `2 word` = "j", `2 pseudoword` = "f"))
  # The practice table keeps its answers, which list 2's mapping contradicts.
  expect_identical(res$notes, c(
    paste("lexsync: 1 practice trial(s) of condition 'word' in list 2 keep their answer 'f',",
          "where the response mapping gives 'j'."),
    paste("lexsync: 1 practice trial(s) of condition 'pseudoword' in list 2 keep their answer",
          "'j', where the response mapping gives 'f'.")))
  # Each version's instructions name its own keys.
  versions <- .presentation_versions(instr_blocks_stim(1:2))
  expect_identical(.instruction_texts(design, versions),
                   c(lexdec_text("F", "J"), lexdec_text("J", "F")))
  # A declared mapping rotates the same way.
  declared <- utils::modifyList(design, list(response_mapping = list(word = "j",
                                                                     pseudoword = "f")))
  res <- .assign_answers(instr_blocks_stim(1:2), declared)
  expect_identical(main_answers(res$stimuli), list(`1 word` = "j", `1 pseudoword` = "f",
                                                   `2 word` = "f", `2 pseudoword` = "j"))
})

test_that("rotate_mapping_by_list_takes_true_or_false", {
  schema <- instr_schema()
  for (bad in list("yes", 1L, "true", list(TRUE))) {
    design <- INSTR_BLOCKS
    design["rotate_mapping_by_list"] <- list(bad)
    expect_error(validate_design(design, schema),
                 "lexsync: rotate_mapping_by_list must be true or false.", fixed = TRUE)
  }
  expect_error(validate_design(list(name = "t", language = "english",
                                    rotate_mapping_by_list = TRUE), schema),
               paste("lexsync: rotate_mapping_by_list rotates a response mapping, and the",
                     "design has none; give `response_mapping`."), fixed = TRUE)
  expect_identical(validate_design(utils::modifyList(INSTR_BLOCKS,
                                                     list(rotate_mapping_by_list = FALSE)),
                                   schema), character(0))
})

test_that("the_instructions_reach_all_three_targets", {
  text <- "Lies jedes Wort, é & \"<b>\".\nThen press f or j."
  design <- utils::modifyList(INSTR_BLOCKS, list(instructions = paste0(text, "\n")))
  out <- export_experiments(instr_lexdec_stim(), design, instr_schema(), instr_out())
  py <- paste(readLines(out$psychopy, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
  found <- regmatches(py, regexec('INSTRUCTIONS = json\\.loads\\(r"""(.*)"""\\)', py))[[1]][2]
  # Carried as JSON data, one text per version, the closing line break trimmed.
  expect_identical(jsonlite::fromJSON(found), text)
  html <- paste(readLines(out$jspsych, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
  page <- regmatches(html, regexec("const INSTRUCTIONS = (.*?);\\n", html))[[1]][2]
  expect_identical(jsonlite::fromJSON(page), text)
  expect_false(grepl("<b>", page, fixed = TRUE))
  lines <- readLines(out$opensesame, warn = FALSE, encoding = "UTF-8")
  at <- match("define inline_script lexsync_instructions", lines)
  expect_identical(lines[at:(at + 11L)], c(
    "define inline_script lexsync_instructions",
    '\tset description "Show the instructions and wait for the space bar"',
    '\tset _prepare ""',
    "\t___run__",
    "\tc = Canvas()",
    paste0("\tc.text(u'Lies jedes Wort, é &amp; \"&lt;b&gt;\".<br />Then press f or j.",
           "<br /><br />Press the space bar to begin.')"),
    "\tc.show()",
    "\t_key, _t = Keyboard(keylist=[u'space', u'escape'], timeout=None).get_key()",
    "\tif _key == u'escape':",
    "\t    raise RuntimeError(u'lexsync: stopped at the instructions.')",
    "\t__end__",
    ""))
  runs <- grep("^\trun lexsync_", lines, value = TRUE)
  expect_identical(utils::tail(runs, 6L), c("\trun lexsync_trigger_setup always",
                                            "\trun lexsync_trigger_notice always",
                                            "\trun lexsync_instructions always",
                                            "\trun lexsync_session_start always",
                                            "\trun lexsync_loop always",
                                            "\trun lexsync_session_end always"))
})

test_that("lexsync_writes_instructions_for_the_tasks_it_knows", {
  one <- list(list(version = 1L, replicate = 1L, list = 1L, n_trials = 4L))
  expect_identical(.instruction_texts(INSTR_LEXDEC, one),
                   lexdec_text("the left arrow key", "the right arrow key"))
  expect_identical(.instruction_texts(INSTR_BLOCKS, one), lexdec_text("F", "J"))
  expect_identical(.instruction_texts(list(name = "c", language = "english",
                                           paradigm = "categorisation"), one),
                   paste("You will see a category and then a word. Press F for yes if the",
                         "word belongs to the category and J for no if it does not. Respond",
                         "as quickly and accurately as you can."))
  expect_identical(.instruction_texts(list(name = "s", language = "english",
                                           paradigm = "self_paced_reading"), one),
                   paste("You will read each sentence one part at a time. Press the space bar",
                         "to see the next part. Answer each question by pressing F for yes",
                         "and J for no."))
  for (paradigm in c("factorial", "priming")) {
    expect_identical(.instruction_texts(list(name = "f", language = "english",
                                             paradigm = paradigm), one),
                     paste("When a response is needed, press the left arrow key or the right",
                           "arrow key. Respond as quickly and accurately as you can."))
  }
  passive <- list(name = "p", language = "english", events = INSTR_EVENTS[1:2])
  expect_identical(.instruction_texts(passive, one),
                   "You will see items presented one at a time on the screen.")
  # A design's own text wins, whatever the paradigm.
  expect_identical(.instruction_texts(utils::modifyList(INSTR_LEXDEC,
                                                        list(instructions = "Go.")), one),
                   "Go.")
  expect_identical(vapply(c("f", "space", "left", "return", "1", "lshift"), .key_label,
                          character(1), USE.NAMES = FALSE),
                   c("F", "the space bar", "the left arrow key", "the Enter key", "1",
                     "the lshift key"))
})

test_that("a_design_in_another_language_without_instructions_is_warned", {
  spanish <- list(name = "e", language = "spanish", paradigm = "lexical_decision")
  expect_identical(.instruction_notes(spanish), language_note("spanish"))
  expect_identical(.instruction_notes(utils::modifyList(spanish,
                                                        list(instructions = "Pulse la tecla."))),
                   character(0))
  for (english in c("english", "English", "en-GB")) {
    expect_identical(.instruction_notes(utils::modifyList(spanish, list(language = english))),
                     character(0))
  }
  # The run log says so, before anything is selected.
  dir <- instr_out()
  old <- setwd(dir)
  on.exit(setwd(old), add = TRUE)
  writeLines(c("item,condition,word", "1,alta,casa", "1,baja,cosa", "2,alta,mesa",
               "2,baja,masa"), "items.csv")
  writeLines(c("name: es_demo", "language: spanish",
               "items: {source: table, path: items.csv}", "counterbalance: {lists: 1}"),
             "design.yaml")
  res <- run_pipeline("design.yaml", system.file("extdata", "schema.yaml", package = "lexsync"),
                      outdir = file.path(dir, "out"), verbose = FALSE)
  log <- paste(readLines(res$log, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
  expect_true(grepl(language_note("spanish"), log, fixed = TRUE))
  expect_true(grepl(task_note("factorial"), log, fixed = TRUE))
})

test_that("a_factorial_design_without_instructions_is_warned", {
  expect_identical(.instruction_notes(list(name = "f", language = "english")),
                   task_note("factorial"))
  expect_identical(.instruction_notes(list(name = "p", language = "english",
                                           paradigm = "priming")), task_note("priming"))
  # A task lexsync knows, a design with no response and a design's own text are not.
  for (design in list(INSTR_LEXDEC,
                      list(name = "c", language = "english", paradigm = "categorisation"),
                      list(name = "s", language = "english", paradigm = "self_paced_reading"),
                      list(name = "p", language = "english", events = INSTR_EVENTS[1:2]),
                      list(name = "f", language = "english", instructions = "Press f."))) {
    expect_identical(.instruction_notes(design), character(0))
  }
  # A mapping rotated across lists is noted when the design's own text cannot follow it.
  rotated <- utils::modifyList(INSTR_BLOCKS, list(rotate_mapping_by_list = TRUE))
  expect_identical(.instruction_notes(rotated), character(0))
  expect_identical(.instruction_notes(utils::modifyList(rotated,
                                                        list(instructions = "Press the keys."))),
                   paste("lexsync: the response keys rotate across lists, but the design's",
                         "`instructions` are the same in every list, so they should not name",
                         "the keys."))
})

test_that("instructions_must_be_text_without_control_characters", {
  schema <- instr_schema()
  for (bad in list(42, list("Press f."), list(en = "Press f."))) {
    design <- INSTR_LEXDEC
    design["instructions"] <- list(bad)
    expect_error(validate_design(design, schema),
                 "lexsync: the design's `instructions` must be text.", fixed = TRUE)
  }
  cases <- list(c("Press\tf.", "0009"), c("Press\rf.", "000D"), c("Press\x7ff.", "007F"),
                c("Press\u0085f.", "0085"), c("Press f.", "2028"))
  for (case in cases) {
    expect_error(validate_design(utils::modifyList(INSTR_LEXDEC, list(instructions = case[1])),
                                 schema),
                 sprintf(paste("lexsync: the design's `instructions` contain the control",
                               "character U+%s; only line breaks are allowed."), case[2]),
                 fixed = TRUE)
  }
  for (empty in c("", " \n ")) {
    expect_error(validate_design(utils::modifyList(INSTR_LEXDEC, list(instructions = empty)),
                                 schema),
                 paste("lexsync: the design's `instructions` are empty; write the text or",
                       "leave the key out."), fixed = TRUE)
  }
  expect_identical(validate_design(utils::modifyList(INSTR_LEXDEC, list(
    instructions = "Press f.\n\nPress j.")), schema), character(0))
})

test_that("the_methods_paragraph_states_the_response_mapping", {
  rec <- .response_mapping_record(INSTR_LEXDEC)
  expect_identical(rec, list(conditions = list(word = "left", pseudoword = "right"),
                             keys = list("left", "right"), rotate_by_list = FALSE,
                             source = "default"))
  ds <- list(presentation = list(response_mapping = rec), counterbalancing = list(lists = 1L))
  expect_identical(.mapping_note(ds), paste(" Participants pressed the left arrow key for",
                                            "words and the right arrow key for pseudowords."))
  # The Python engine writes the record's JSON with sorted keys, and the record read back
  # renders the same text.
  read_back <- ds
  read_back$presentation$response_mapping$conditions <- list(pseudoword = "right",
                                                             word = "left")
  expect_identical(.mapping_note(read_back), .mapping_note(ds))
  rotated <- .response_mapping_record(utils::modifyList(INSTR_BLOCKS,
                                                        list(rotate_mapping_by_list = TRUE)))
  expect_true(rotated$rotate_by_list)
  expect_identical(.mapping_note(list(presentation = list(response_mapping = rotated),
                                      counterbalancing = list(lists = 2L))),
                   paste(" Participants pressed F for words and J for pseudowords in",
                         "odd-numbered lists and the reverse in even-numbered lists."))
  # One list has nothing to rotate.
  expect_identical(.mapping_note(list(presentation = list(response_mapping = rotated),
                                      counterbalancing = list(lists = 1L))),
                   " Participants pressed F for words and J for pseudowords.")
  declared <- .response_mapping_record(list(
    name = "p", language = "english", paradigm = "priming",
    response_mapping = list(related = "left", unrelated = "left")))
  expect_identical(declared$source, "design")
  expect_identical(.mapping_note(list(presentation = list(response_mapping = declared),
                                      counterbalancing = list(lists = 2L))),
                   " Participants pressed the left arrow key for related and unrelated trials.")
  # Without a mapping there is nothing to record or say.
  expect_null(.response_mapping_record(list(name = "f", language = "english")))
  expect_identical(.mapping_note(list(presentation = list())), "")
})

# ---- The shipped demonstrations --------------------------------------------------------

test_that("the_shipped_lexical_decisions_carry_an_answer_on_every_trial", {
  folder <- repo_path("output", "experiments", message = "the demonstrations live in the repository")
  loop <- instr_read(file.path(folder, "en_lexdec_english_psychopy.csv"))
  expect_identical(nrow(loop), 120L)
  expect_identical(loop$answer, unname(c(word = "left", pseudoword = "right")[loop$condition]))
  practice <- instr_read(repo_path("items", "practice_en_lexdec.csv"))
  keys <- stats::setNames(practice$answer, practice$condition)
  keys <- keys[!duplicated(names(keys))]
  expect_identical(keys, c(word = "f", pseudoword = "j"))
  blocks <- instr_read(file.path(folder, "en_lexdec_blocks_english_psychopy.csv"))
  expect_identical(sum(blocks$block == "main"), 40L)
  expect_identical(blocks$answer, unname(keys[blocks$condition]))
  # The datasheet and its Methods text state the mapping.
  ds <- jsonlite::fromJSON(repo_path("output", "reports", "en_lexdec_english_datasheet_R.json"),
                           simplifyVector = FALSE)
  expect_identical(ds$presentation$response_mapping$conditions,
                   list(word = "left", pseudoword = "right"))
  md <- paste(readLines(repo_path("output", "reports", "en_lexdec_english_datasheet_R.md"),
                        warn = FALSE, encoding = "UTF-8"), collapse = "\n")
  sentence <- paste("Participants pressed the left arrow key for words and the right arrow",
                    "key for pseudowords.")
  expect_true(grepl(sentence, md, fixed = TRUE))
  # The record read back from its JSON, and the Python engine's, render the same sentence.
  expect_true(grepl(sentence, methods_paragraph(ds), fixed = TRUE))
  py <- jsonlite::fromJSON(repo_path("output", "reports", "en_lexdec_english_datasheet_py.json"),
                           simplifyVector = FALSE)
  expect_true(grepl(sentence, methods_paragraph(py), fixed = TRUE))
})

test_that("no_practice_pseudoword_is_a_known_form", {
  known <- readLines(repo_path("corpora", "derived", "en_known_forms.txt",
                               message = "the demonstrations live in the repository"),
                     warn = FALSE, encoding = "UTF-8")
  practice <- instr_read(repo_path("items", "practice_en_lexdec.csv"))
  pseudowords <- practice$target[practice$condition == "pseudoword"]
  expect_length(pseudowords, 4L)
  expect_identical(intersect(pseudowords, known), character(0))
})

test_that("the_categorisation_experiment_presents_both_answers", {
  design <- read_config(repo_path("config", "design_en_categorisation.yaml",
                                  message = "the demonstrations live in the repository"))
  expect_identical(design$fillers, list(path = "items/categorisation_foils_en.csv"))
  foils <- instr_read(repo_path("items", "categorisation_foils_en.csv"))
  members <- instr_read(repo_path("items", "categorisation_en.csv"))
  expect_identical(names(foils), names(members))
  expect_identical(nrow(foils), 16L)
  expect_identical(unique(foils$answer), "j")
  expect_identical(as.vector(table(foils$condition)[c("narrow", "broad")]), c(8L, 8L))
  # Judged against the members' own cues, and no foil is a member target.
  expect_true(all(foils$category %in% members$category))
  expect_identical(intersect(foils$target, members$target), character(0))
  loop <- instr_read(repo_path("output", "experiments", "en_categorisation_english_psychopy.csv"))
  for (lst in sort(unique(loop$list))) {
    rows <- loop[loop$list == lst, , drop = FALSE]
    expect_identical(as.vector(table(rows$answer)[c("f", "j")]), c(16L, 16L), info = lst)
    # Neither cue type predicts the answer.
    for (cue in c("narrow", "broad")) {
      expect_identical(sort(unique(rows$answer[rows$condition == cue])), c("f", "j"),
                       info = paste(lst, cue))
    }
  }
})
