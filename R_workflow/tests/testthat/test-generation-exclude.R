# Known-form lists for generated pseudowords, and the eligible-candidate count.
#
# The generators checked a candidate only against the reference lexicon, whose English
# and Spanish forms stop at Zipf 2.95 and 3.11, so genuine low-frequency words (crier,
# pall; in Spanish renos, esteras) passed as pseudowords. `items.generation.exclude`
# names further word forms no pseudoword may equal. test_generation_exclude.py holds
# the Python engine to the same tests, by the same names.

ge_lex <- c("cat", "cap", "car", "can", "cab", "bat", "bad", "bag", "ban",
            "rat", "ran", "ram", "rag", "tan", "tap", "tar", "mat", "map", "man")
ge_ref <- c("planet", "bridge", "strength", "brake", "grape", "plane", "clip", "drum",
            "garden", "market", "basket", "winter", "silver", "butter", "letter", "better",
            "bitter", "banner", "dinner", "manner")
ge_band <- list(length = c(4, 7), frequency = c(3.5, 6.0))

ge_write <- function(text, path) writeBin(charToRaw(enc2utf8(text)), path)
ge_sha256 <- function(path) digest::digest(file = path, algo = "sha256")
ge_posix <- function(path) gsub("\\", "/", path, fixed = TRUE)
ge_schema <- function() yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
ge_es <- function() system.file("extdata", "es_example.csv", package = "lexsync")

test_that("an_exclusion_forces_the_next_best_candidate", {
  # Without the list, 'cat' becomes 'cag'. Excluding it, written as a user might
  # (padded, upper case), leaves the next-best candidate, and 'man' keeps its own.
  before <- generate_pseudowords(c("cat", "man"), ge_lex)
  expect_identical(before$pseudoword, c("cag", "mag"))
  after <- generate_pseudowords(c("cat", "man"), ge_lex, exclude = " CAG ")
  expect_identical(after$pseudoword, c("tat", "mag"))
  # An excluded form that was never chosen changes nothing.
  expect_identical(generate_pseudowords(c("cat", "man"), ge_lex, exclude = "zzz"), before)
})

test_that("an_exclusion_reaches_the_subsyllabic_generator", {
  before <- generate_pseudowords_subsyllabic(c("garden", "winter"), ge_ref)
  expect_identical(before$pseudoword, c("gerder", "wittet"))
  after <- generate_pseudowords_subsyllabic(c("garden", "winter"), ge_ref, exclude = "gerder")
  expect_identical(after$pseudoword, c("garder", "wittet"))
})

test_that("build_lexdec_stimuli_passes_the_exclusion_on", {
  pool <- data.frame(word = c("cat", "man"), length = c(3L, 3L), stringsAsFactors = FALSE)
  base <- build_lexdec_stimuli(pool, 2L, reference_words = ge_lex)
  expect_identical(base$target[base$condition == "pseudoword"], c("cag", "mag"))
  out <- build_lexdec_stimuli(pool, 2L, reference_words = ge_lex, exclude = "cag")
  expect_identical(out$target[out$condition == "pseudoword"], c("tat", "mag"))
})

test_that("known_forms_are_read_from_text_and_csv_files", {
  dir <- tempfile("known_"); dir.create(dir); on.exit(unlink(dir, recursive = TRUE))
  txt <- file.path(dir, "known.txt")
  # A byte-order mark, CRLF line ends, a comment, a blank line, padding, upper case
  # and a decomposed accent, all of which the reader normalises as a lexicon is read.
  ge_write(paste0("\ufeff# known forms\r\nCrier\r\n\r\n  pall \r\nrene\u0301\r\npall\r\n"), txt)
  table <- file.path(dir, "extra.csv")
  ge_write("word,freq\ntiter,1.2\nCrier,2\n", table)
  got <- .read_known_forms(list(txt, table))
  expect_identical(got$forms, c("crier", "pall", "ren\u00e9", "titer"))
  expect_identical(got$records, list(
    list(source = ge_posix(txt), sha256 = ge_sha256(txt), n_forms = 3L),
    list(source = ge_posix(table), sha256 = ge_sha256(table), n_forms = 2L)))
  # A single path is a list of one.
  expect_identical(.read_known_forms(table)$forms, c("crier", "titer"))
})

test_that("a_known_form_csv_without_a_word_column_is_refused", {
  table <- tempfile(fileext = ".csv"); on.exit(unlink(table))
  ge_write("form\ncrier\n", table)
  expect_error(.read_known_forms(list(table)), "has no 'word' column", fixed = TRUE)
})

test_that("a_known_form_list_that_is_a_table_or_not_utf8_is_refused", {
  dir <- tempfile("known_"); dir.create(dir); on.exit(unlink(dir, recursive = TRUE))
  # A tab-separated .txt (SUBTLEX-US's layout) was read whole, one row per form, so it
  # excluded nothing while the datasheet counted its rows. A comment may hold a comma;
  # a form may not.
  table <- file.path(dir, "subtlex.txt")
  ge_write("# rows, as served\nWord\tFREQcount\ncrier\t17\n", table)
  expect_error(.read_known_forms(list(table)),
               "line 2 of the known-form list .* holds a tab")
  commas <- file.path(dir, "commas.txt")
  ge_write("crier\npall,23\n", commas)
  expect_error(.read_known_forms(list(commas)), "line 2 of the known-form list",
               fixed = TRUE)
  # A Latin-1 file was misread in one engine and read as no forms in the other.
  latin <- file.path(dir, "latin.txt")
  writeBin(as.raw(c(0x63, 0x61, 0x66, 0xE9, 0x0A)), latin)
  expect_error(.read_known_forms(list(latin)), "is not UTF-8 text", fixed = TRUE)
})

test_that("a_known_form_entry_that_names_nothing_is_refused", {
  expect_error(.read_known_forms(list(file.path(tempdir(), "missing.txt"))),
               "neither a readable file nor a corpus in the registry", fixed = TRUE)
  expect_error(.read_known_forms(list(3)),
               "must list file paths or registry corpus names", fixed = TRUE)
})

test_that("a_registry_name_without_a_cached_corpus_is_refused_with_the_fetch_hint", {
  tmp <- tempfile("lexsync-cache-")
  old <- Sys.getenv("R_USER_CACHE_DIR", unset = NA)
  on.exit({
    if (is.na(old)) Sys.unsetenv("R_USER_CACHE_DIR") else Sys.setenv(R_USER_CACHE_DIR = old)
    unlink(tmp, recursive = TRUE)
  })
  Sys.setenv(R_USER_CACHE_DIR = tmp)
  expect_error(.read_known_forms(list("subtlex_us")), "fetch_corpus('subtlex_us')",
               fixed = TRUE)
  # Once fetched, the corpus's registered word column is read: SUBTLEX-US names it
  # 'Word', and openlexicon serves it tab-separated.
  dir.create(lexsync_cache_dir(), recursive = TRUE)
  cached <- file.path(lexsync_cache_dir(), "subtlex_us.csv")
  ge_write("Word\tFREQcount\nCrier\t17\npall\t23\n", cached)
  got <- .read_known_forms(list("subtlex_us"))
  expect_identical(got$forms, c("crier", "pall"))
  expect_identical(got$records, list(list(source = "subtlex_us", sha256 = ge_sha256(cached),
                                          n_forms = 2L)))
})

# How many of the words are written wholly in letters, by ICU's letter class.
ge_in_letters <- function(words) sum(stringi::stri_detect_regex(words, "^\\p{L}+$"), na.rm = TRUE)

test_that("a_band_counts_the_words_written_in_attested_letters_as_eligible", {
  # Every word of the Spanish band is written in letters the lexicon attests, its
  # accented words included, which the a-z filter left out.
  lex <- load_lexicon(ge_es(), ge_schema(), "spanish")
  band <- build_pool(lex, ge_band)
  eligible <- .lexdec_eligible(band, lex$word)
  expect_identical(eligible$word, band$word)
  expect_identical(ge_in_letters(band$word), nrow(band))
  expect_true(any(grepl("[^\\x01-\\x7f]", eligible$word, perl = TRUE)))
  # A hyphen, a digit or a letter the reference lacks still leaves a word out.
  pool <- data.frame(word = c("a\u00f1o", "e-mail", "mar2", "\u00fcber", "casa"),
                     stringsAsFactors = FALSE)
  got <- .lexdec_eligible(pool, c("a\u00f1o", "casa", "mar", "email"))
  expect_identical(got$word, c("a\u00f1o", "casa"))
})

ge_design <- function(dir, exclude = NULL) {
  design <- list(name = "es_lexdec_count", language = "spanish",
                 paradigm = "lexical_decision",
                 items = list(source = "generate", lexicon = ge_es()),
                 n_per_condition = 6L, pool_filters = ge_band)
  if (!is.null(exclude)) design$items$generation <- list(exclude = as.list(exclude))
  path <- file.path(dir, "design.yaml")
  yaml::write_yaml(design, path)
  path
}

ge_datasheet <- function(outdir) {
  jsonlite::read_json(file.path(outdir, "reports", "es_lexdec_count_spanish_datasheet_R.json"))
}

ge_pseudowords <- function(outdir) {
  st <- read_csv_utf8(file.path(outdir, "stimuli", "es_lexdec_count_spanish_stimuli_R.csv"))
  sort(st$target[st$condition == "pseudoword"], method = "radix")
}

test_that("a_generated_design_reports_the_words_the_generator_could_use", {
  # The record counted the band before the letter filter. It now counts the words
  # written in letters the lexicon attests, which in this band, accents and all, is
  # every word. parity/twin_edge/generation_exclude holds both engines to a band with a
  # hyphenated word, which the filter leaves out.
  band <- build_pool(load_lexicon(ge_es(), ge_schema(), "spanish"), ge_band)
  dir <- tempfile("gen_count_"); dir.create(dir); on.exit(unlink(dir, recursive = TRUE))
  out <- file.path(dir, "out")
  run_pipeline(ge_design(dir), system.file("extdata", "schema.yaml", package = "lexsync"),
               out, verbose = FALSE)
  ds <- ge_datasheet(out)
  expect_identical(ds$selection$candidate_pool,
                   list(list(condition = "words in band",
                             n_candidates = ge_in_letters(band$word))))
  expect_gt(ge_in_letters(band$word), sum(grepl("^[a-z]+$", band$word, perl = TRUE)))
  expect_null(ds$selection$generation_exclude)
})

test_that("a_generated_design_records_its_known_form_lists", {
  dir <- tempfile("gen_exclude_"); dir.create(dir); on.exit(unlink(dir, recursive = TRUE))
  schema <- system.file("extdata", "schema.yaml", package = "lexsync")
  plain <- file.path(dir, "plain")
  run_pipeline(ge_design(dir), schema, plain, verbose = FALSE)
  first <- ge_pseudowords(plain)[1]
  known <- file.path(dir, "known.txt")
  ge_write(paste0(first, "\n"), known)
  out <- file.path(dir, "out")
  run_pipeline(ge_design(dir, known), schema, out, verbose = FALSE)
  ds <- ge_datasheet(out)
  expect_identical(ds$selection$generation_exclude,
                   list(list(source = ge_posix(known), sha256 = ge_sha256(known), n_forms = 1L)))
  expect_false(first %in% ge_pseudowords(out))
  expect_identical(ds$selection$candidate_pool, ge_datasheet(plain)$selection$candidate_pool)
  expect_true(grepl(paste0("Besides the lexicon, pseudowords were checked against 1 known ",
                           "word form (known.txt)."), methods_paragraph(ds), fixed = TRUE))
  expect_false(grepl("known word form", methods_paragraph(ge_datasheet(plain)), fixed = TRUE))
})
