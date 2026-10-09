# The English demonstrations select from the screened lexicon and leave out unsuitable
# words.
#
# The demonstrations read corpora/derived/en.csv, which keeps every form wordfreq
# returns, and broke exact ties by spelling. Their low-frequency conditions filled with
# names, acronyms and early-alphabet words, and their selections held taboo words (bitch,
# boobs and fuck). They now read en_v2.csv with `nonstandard: [0, 0]`, leave out the
# words of config/exclude_en_demo.txt, check generated pseudowords against wordfreq's
# fuller list of English forms, and break ties by the keyed hash. These tests hold the
# R engine's committed outputs to that. They read the repository's designs, lexica and
# outputs, so they skip on CRAN and outside a checkout. test_demonstrations.py holds the
# Python engine's outputs to the same tests, by the same names.

dm_v2 <- "corpora/derived/en_v2.csv"
dm_exclusions <- "config/exclude_en_demo.txt"
dm_known_forms <- "corpora/derived/en_known_forms.txt"
# The corpus and generated designs, which filter on `nonstandard` and name the exclusions.
dm_screened <- c("en_freqcontrast", "en_ndensity", "en_freqcontinuous", "en_balanced_lists",
                 "en_resample", "en_richdim", "en_andrews_repro", "en_lexdec",
                 "en_lexdec_blocks", "en_lexdec_wuggy")
dm_generated <- c("en_lexdec", "en_lexdec_blocks", "en_lexdec_wuggy")
# A supplied pool and a pair table, which read en_v2.csv for their dimensions.
dm_supplied <- c("en_supplied_pool", "en_priming_continuous")

# Every cell as text, read with base R and not through the package.
dm_csv <- function(path) {
  utils::read.csv(path, colClasses = "character", na.strings = character(0),
                  check.names = FALSE, encoding = "UTF-8")
}
dm_design <- function(name) {
  yaml::read_yaml(repo_path("config", paste0("design_", name, ".yaml")))
}
dm_stimuli <- function(name) {
  dm_csv(repo_path("output", "stimuli", paste0(name, "_english_stimuli_R.csv")))
}
dm_report <- function(name, kind) {
  dm_csv(repo_path("output", "reports", paste0(name, "_english_", kind, "_R.csv")))
}
dm_datasheet <- function(name) {
  jsonlite::read_json(repo_path("output", "reports", paste0(name, "_english_datasheet_R.json")))
}
dm_v2_rows <- local({
  cache <- NULL
  function() {
    if (is.null(cache)) cache <<- dm_csv(repo_path(dm_v2))
    cache
  }
})
# One word per line, blank lines and lines beginning '#' skipped, as the file states.
dm_excluded <- function() {
  lines <- tolower(trimws(readLines(repo_path(dm_exclusions), encoding = "UTF-8")))
  lines[nzchar(lines) & !startsWith(lines, "#")]
}
dm_marked <- function() {
  v2 <- dm_v2_rows()
  v2$word[v2$nonstandard == "1"]
}
# The real words a design presents: every selected word, the pseudowords of a lexical
# decision left out, and both members of every pair.
dm_presented <- function(name) {
  s <- dm_stimuli(name)
  if (!"word" %in% names(s)) return(c(s$prime, s$target))
  s$word[s$condition != "pseudoword"]
}
# en_v2's rows that the design's pool filters, its exclusions and the condition's window
# admit, computed from the files and not through the package.
dm_candidates <- function(design, condition) {
  v2 <- dm_v2_rows()
  rows <- v2[!v2$word %in% dm_excluded(), , drop = FALSE]
  cond <- Filter(function(cd) identical(cd$name, condition), design$conditions)[[1]]
  windows <- utils::modifyList(design$pool_filters, cond$define_by)
  for (dim in names(windows)) {
    values <- if (identical(dim, "length")) nchar(rows$word) else
      as.numeric(rows[[if (identical(dim, "frequency")) "freq_zipf" else dim]])
    rows <- rows[values >= windows[[dim]][[1]] & values <= windows[[dim]][[2]], , drop = FALSE]
  }
  rows
}
dm_initial_share <- function(words) mean(substr(words, 1L, 1L) %in% c("a", "b"))

test_that("the_english_demonstrations_read_the_screened_lexicon", {
  for (name in dm_screened) {
    design <- dm_design(name)
    lexicon <- if (name %in% dm_generated) design$items$lexicon else design$lexicon
    expect_identical(lexicon, dm_v2, info = name)
    expect_identical(as.numeric(unlist(design$pool_filters$nonstandard)), c(0, 0), info = name)
    expect_identical(design$exclude_words, list(path = dm_exclusions), info = name)
  }
  for (name in dm_generated) {
    expect_identical(unlist(dm_design(name)$items$generation$exclude), dm_known_forms,
                     info = name)
  }
  for (name in dm_supplied) expect_identical(dm_design(name)$items$lexicon, dm_v2, info = name)
})

test_that("the_exclusion_list_holds_only_forms_the_screen_keeps", {
  # A listed word that en_v2 lacks, or already marks, would exclude nothing.
  words <- dm_excluded()
  expect_gt(length(words), 0L)
  expect_false(anyDuplicated(words) > 0L)
  v2 <- dm_v2_rows()
  expect_true(all(words %in% v2$word))
  expect_true(all(v2$nonstandard[match(words, v2$word)] == "0"))
  expect_true(startsWith(readLines(repo_path(dm_exclusions), n = 1L), "#"))
})

test_that("no_english_demonstration_selects_a_marked_or_excluded_word", {
  marked <- dm_marked()
  excluded <- dm_excluded()
  known <- dm_v2_rows()$word
  for (name in c(dm_screened, dm_supplied)) {
    words <- unique(dm_presented(name))
    expect_identical(setdiff(words, known), character(0), info = name)
    expect_identical(intersect(words, marked), character(0), info = name)
    expect_identical(intersect(words, excluded), character(0), info = name)
  }
})

test_that("no_andrews_cell_holds_a_marked_or_excluded_form", {
  # In lexsync 0.1, 24 of the 36 low-frequency items were forms the screen marks (aclu,
  # adhd, bbq and bmx among them), against none of the 36 high-frequency items.
  flagged <- c(dm_marked(), dm_excluded())
  s <- dm_stimuli("en_andrews_repro")
  for (cell in c("HF_largeN", "HF_smallN", "LF_largeN", "LF_smallN")) {
    words <- s$word[s$condition == cell]
    expect_length(words, 18L)
    expect_identical(intersect(words, flagged), character(0), info = cell)
  }
})

test_that("freqcontrast_initials_follow_their_candidates", {
  # Spelling broke the ties in lexsync 0.1, and 61% of the low-frequency words began with
  # a or b, against 13% of the candidates.
  design <- dm_design("en_freqcontrast")
  s <- dm_stimuli("en_freqcontrast")
  for (condition in c("high_frequency", "low_frequency")) {
    share <- dm_initial_share(s$word[s$condition == condition])
    expect_lte(share, dm_initial_share(dm_candidates(design, condition)$word) + 0.1,
               label = condition)
  }
})

test_that("no_english_pseudoword_is_a_known_form", {
  known <- readLines(repo_path(dm_known_forms), encoding = "UTF-8")
  for (name in dm_generated) {
    s <- dm_stimuli(name)
    pseudowords <- unique(s$word[s$condition == "pseudoword"])
    expect_gt(length(pseudowords), 0L)
    expect_identical(intersect(pseudowords, known), character(0), info = name)
  }
})

test_that("freqcontrast_matched_dimensions_remain_equivalent", {
  design <- dm_design("en_freqcontrast")
  comp <- dm_report("en_freqcontrast", "comparisons")
  rows <- comp[comp$role == "controlled", , drop = FALSE]
  expect_identical(sort(rows$dimension), sort(unlist(design$match_on)))
  expect_true(all(rows$equivalent == "TRUE"))
  expect_true(all(abs(as.numeric(rows$cohens_d)) < 0.1))
})

test_that("the_demonstration_datasheets_record_the_screen", {
  sha <- digest::digest(file = repo_path(dm_exclusions), algo = "sha256")
  known_sha <- digest::digest(file = repo_path(dm_known_forms), algo = "sha256")
  for (name in dm_screened) {
    ds <- dm_datasheet(name)
    source <- ds$materials_source
    expect_true(grepl("screened against SUBTLEX-US", source$provenance, fixed = TRUE),
                info = name)
    expect_identical(source$exclusions$path, dm_exclusions, info = name)
    expect_identical(source$exclusions$sha256, sha, info = name)
    expect_identical(as.integer(source$exclusions$n_listed), length(dm_excluded()), info = name)
    if (name %in% dm_generated) {
      expect_identical(ds$selection$generation_exclude,
                       list(list(source = dm_known_forms, sha256 = known_sha,
                                 n_forms = 289023L)), info = name)
    } else if (is.null(dm_design(name)$continuous)) {
      expect_identical(ds$selection$tie_break, list(rule = "hash", salt = "lexsync-tie-v1"),
                       info = name)
    }
  }
})
