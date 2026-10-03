jspsych_stim <- function() {
  assign_triggers(data.frame(
    word = c("cat", "dog", "car", "cap"), condition = c("a", "a", "b", "b"),
    set = c(1, 2, 1, 2), trial = 1:4, length = 3L, frequency = 5,
    n_density = 2L, old20 = 1.5, stringsAsFactors = FALSE))
}

test_that("jsPsych export is structurally valid and maps keys to browser names", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  out <- tempfile("lx"); dir.create(out)
  path <- export_jspsych(jspsych_stim(), list(name = "t", language = "english", timing = list()),
                         schema, out)
  html <- paste(readLines(path, warn = FALSE), collapse = "\n")
  expect_true(startsWith(trimws(html), "<!DOCTYPE html>"))
  expect_true(grepl("jspsych@", html, fixed = TRUE))
  expect_true(grepl("jsPsych.run(timeline)", html, fixed = TRUE))

  ev <- regmatches(html, regexec("const EVENTS = (.*?);\\n", html))[[1]][2]
  tr <- regmatches(html, regexec("const TRIALS = (.*?);\\n", html))[[1]][2]
  events <- jsonlite::fromJSON(ev, simplifyDataFrame = FALSE)
  trials <- jsonlite::fromJSON(tr, simplifyDataFrame = FALSE)
  expect_gt(length(events), 0)
  expect_equal(length(trials), 4)
  resp <- Filter(function(e) e$type == "response", events)[[1]]
  expect_identical(unlist(resp$keys), c("arrowleft", "arrowright"))
})

test_that("the jsPsych lang attribute is a valid BCP 47 tag", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  out <- tempfile("lx"); dir.create(out)
  for (pair in list(c("english", "en"), c("spanish", "es"), c("chinese", "zh"))) {
    html <- paste(readLines(export_jspsych(jspsych_stim(),
                                           list(name = "t", language = pair[1], timing = list()),
                                           schema, out, base = pair[1]), warn = FALSE),
                  collapse = "\n")
    expect_true(grepl(sprintf('<html lang="%s">', pair[2]), html, fixed = TRUE))
  }
})

test_that("a language label maps to a tag and falls back to undetermined", {
  expect_identical(.language_tag(list(language = "english")), "en")
  expect_identical(.language_tag(list(language = "Chinese (Mandarin)")), "zh")
  expect_identical(.language_tag(list(language = "en-GB")), "en-GB")   # already a tag
  expect_identical(.language_tag(list(language = "english", language_tag = "en-US")), "en-US")
  expect_identical(.language_tag(list(language = "klingon")), "und")
  expect_identical(.language_tag(list(language = "")), "und")
})

test_that("jsPsych export escapes HTML in stimulus data", {
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- assign_triggers(data.frame(
    word = "</script><b>x", condition = "a", set = 1, trial = 1,
    length = 3L, frequency = 5, n_density = 2L, old20 = 1.5, stringsAsFactors = FALSE))
  out <- tempfile("lx"); dir.create(out)
  html <- paste(readLines(export_jspsych(stim, list(name = "t", language = "english", timing = list()),
                                         schema, out), warn = FALSE), collapse = "\n")
  expect_false(grepl("</script><b>x", html, fixed = TRUE))
})

test_that("key mapping does not invent a 'key' element on a response event", {
  # `$` partial-matches on a list, so `e$key` returns the value of `keys`, and the
  # guarded assignment then adds a `key` the Python engine never emits: the two
  # engines' jsPsych timelines diverged on every response event. Exact-match [[ ]]
  # is what keeps them in step; test_scripting.py pins the same shape.
  ev <- list(list(type = "response", keys = c("left", "right"), timeout = 2))
  mapped <- lexsync:::.map_keys_jspsych(ev)[[1]]
  expect_identical(names(mapped), c("type", "keys", "timeout"))
  expect_identical(mapped$keys, c("arrowleft", "arrowright"))
  # A region event does carry a real `key`, which must still be mapped.
  reg <- list(list(type = "region", field = "sentence", sep = "|", key = "space"))
  expect_identical(lexsync:::.map_keys_jspsych(reg)[[1]][["key"]], " ")
})

test_that("the page carries the versions and selects one", {
  # The page embeds every version's trials, because one page serves every participant,
  # and its timeline used to run them all. test_jspsych_export.py pins the same page
  # and runs its script.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  out <- tempfile("lx"); dir.create(out)
  stim <- data.frame(prime = c("hot", "sky", "sun", "big"),
                     target = c("cold", "cold", "moon", "moon"),
                     condition = rep(c("related", "unrelated"), 2), set = c(1, 1, 2, 2),
                     stringsAsFactors = FALSE)
  design <- list(name = "t", language = "english", paradigm = "priming",
                 counterbalance = list(lists = 2L))
  stim <- assign_triggers(counterbalance(stim, design, schema))
  html <- paste(readLines(export_jspsych(stim, design, schema, out), warn = FALSE),
                collapse = "\n")
  vs <- regmatches(html, regexec("const VERSIONS = (.*?);\\n", html))[[1]][2]
  versions <- jsonlite::fromJSON(vs, simplifyDataFrame = FALSE)
  expect_equal(versions, list(list(version = 1L, replicate = 1L, list = 1L, n_trials = 2L),
                              list(version = 2L, replicate = 1L, list = 2L, n_trials = 2L)))
  expect_true(grepl("const RUN_TRIALS = TRIALS.filter(", html, fixed = TRUE))
  tr <- regmatches(html, regexec("const TRIALS = (.*?);\\n", html))[[1]][2]
  trials <- jsonlite::fromJSON(tr, simplifyDataFrame = FALSE)
  # The page's filter keeps a trial whose replicate and list are the version's, a trial
  # without either column counting as replicate 1 or list 1.
  for (v in versions) {
    rows <- Filter(function(t) {
      identical(as.integer(t[["replicate"]] %||% 1L), v[["replicate"]]) &&
        identical(as.integer(t[["list"]] %||% 1L), v[["list"]])
    }, trials)
    expect_length(rows, v[["n_trials"]])
    expect_identical(sort(vapply(rows, function(t) t[["target"]], character(1))),
                     c("cold", "moon"))
  }
})
