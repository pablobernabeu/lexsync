# A design's `exclude_words`: words taken out of the candidates before the pool filters.
#
# A lexicon holds forms a study may not want, names and offensive words among them. No
# filter on its columns can remove a word the researcher has simply decided against,
# since a range filter on a norm table drops every word the table does not cover as well.
# `exclude_words` lists such words in the design, or names a file of them, one per line.
# Both engines remove them after the norms join and before the pool filters, from the
# candidates only: the neighbourhood reference, and a generated design's list of real
# words, keep them. The datasheet records the list with its checksum and the run log the
# removal. test_exclude_words.py holds the Python engine to the same tests, by the same
# names.

# The words of the letter-substitution tests in test-generation-exclude.R. Against these
# alone, 'cat' becomes the pseudoword 'cag'.
ew_lex <- c("cat", "cap", "car", "can", "cab", "bat", "bad", "bag", "ban",
            "rat", "ran", "ram", "rag", "tan", "tap", "tar", "mat", "map", "man")
ew_name <- "en_exclude"

ew_schema_path <- function() system.file("extdata", "schema.yaml", package = "lexsync")
ew_schema <- function() yaml::read_yaml(ew_schema_path())
ew_en <- function() system.file("extdata", "en_example.csv", package = "lexsync")
ew_posix <- function(path) gsub("\\", "/", path, fixed = TRUE)
ew_write <- function(text, path) writeBin(charToRaw(enc2utf8(text)), path)
ew_sha256_text <- function(text) digest::digest(enc2utf8(text), algo = "sha256", serialize = FALSE)
ew_sha256_file <- function(path) digest::digest(file = path, algo = "sha256")

ew_design <- function(dir, exclude = NULL, lexicon = NULL, match_on = "length",
                      tag = "design") {
  design <- list(name = ew_name, language = "english",
                 lexicon = ew_posix(if (is.null(lexicon)) ew_en() else lexicon),
                 n_per_condition = 6L,
                 pool_filters = list(length = c(4, 7)),
                 conditions = list(
                   list(name = "high", define_by = list(frequency = c(5.0, 7.0))),
                   list(name = "low", define_by = list(frequency = c(3.0, 4.0)))),
                 match_on = as.list(match_on))
  if (!is.null(exclude)) design$exclude_words <- exclude
  path <- file.path(dir, paste0(tag, ".yaml"))
  yaml::write_yaml(design, path)
  path
}

ew_run <- function(dir, tag, ...) {
  out <- file.path(dir, tag)
  run_pipeline(ew_design(dir, tag = tag, ...), ew_schema_path(), out, verbose = FALSE)
  out
}

ew_datasheet <- function(outdir) {
  jsonlite::read_json(file.path(outdir, "reports", paste0(ew_name, "_english_datasheet_R.json")))
}

ew_rows <- function(outdir) {
  read_csv_utf8(file.path(outdir, "stimuli", paste0(ew_name, "_english_stimuli_R.csv")))
}

ew_stimuli_bytes <- function(outdir) {
  path <- file.path(outdir, "stimuli", paste0(ew_name, "_english_stimuli_R.csv"))
  readBin(path, "raw", file.info(path)$size)
}

# The selected words of each condition, in the order of the stimuli file.
ew_selected <- function(outdir) {
  st <- ew_rows(outdir)
  split(st$word, st$condition)
}

ew_candidates <- function(ds) {
  cp <- ds$selection$candidate_pool
  stats::setNames(lapply(cp, function(x) x$n_candidates),
                  vapply(cp, function(x) x$condition, character(1)))
}

ew_log <- function(outdir) {
  path <- file.path(outdir, "reports", paste0(ew_name, "_english_run_log_R.md"))
  rawToChar(readBin(path, "raw", file.info(path)$size))
}

# The example lexicon's lines, the header first.
ew_en_lines <- function() strsplit(rawToChar(readBin(ew_en(), "raw", file.info(ew_en())$size)),
                                   "\n", fixed = TRUE)[[1]]

test_that("exclude_words_as_a_list_removes_exactly_the_listed_words", {
  dir <- tempfile("exclude_"); dir.create(dir); on.exit(unlink(dir, recursive = TRUE))
  plain <- ew_run(dir, "plain")
  chosen <- ew_selected(plain)
  high <- chosen$high[1]
  low <- chosen$low[1]
  # Written as a user might: padded and in upper case, with a word the lexicon lacks.
  out <- ew_run(dir, "out", exclude = c(paste0("  ", toupper(high), " "), low, "zzzz"))
  ds <- ew_datasheet(out)
  listed <- sort(c(high, low, "zzzz"), method = "radix")
  expect_identical(ds$materials_source$exclusions,
                   list(path = "inline", sha256 = ew_sha256_text(paste(listed, collapse = "\n")),
                        n_listed = 3L, n_removed = 2L))
  got <- unlist(ew_selected(out), use.names = FALSE)
  expect_false(high %in% got)
  expect_false(low %in% got)
  # Each word was a candidate of the condition it had been selected for, so each
  # condition lost one candidate and no other.
  before <- ew_candidates(ew_datasheet(plain))
  expect_identical(ew_candidates(ds), list(high = before$high - 1L, low = before$low - 1L))
  expect_true(grepl("exclude_words: removed 2 of the 3 listed word(s) from the candidates (inline)",
                    ew_log(out), fixed = TRUE))
  # Excluding the words selects what a lexicon without them selects. The ids differ,
  # since they number the lexicon's rows, so the rows are compared without them.
  lines <- ew_en_lines()
  keep <- c(TRUE, !(sub(",.*$", "", lines[-1]) %in% c(high, low)))
  smaller <- file.path(dir, "smaller.csv")
  ew_write(paste0(paste(lines[keep], collapse = "\n"), "\n"), smaller)
  alone <- ew_run(dir, "alone", lexicon = smaller)
  strip <- function(st) st[, setdiff(names(st), "id"), drop = FALSE]
  expect_identical(strip(ew_rows(out)), strip(ew_rows(alone)))
})

test_that("exclude_words_from_a_file_selects_as_the_inline_list_does", {
  dir <- tempfile("exclude_"); dir.create(dir); on.exit(unlink(dir, recursive = TRUE))
  plain <- ew_run(dir, "plain")
  chosen <- ew_selected(plain)
  high <- chosen$high[1]
  low <- chosen$low[1]
  inline <- ew_run(dir, "inline", exclude = c(high, low, "zzzz"))
  listing <- file.path(dir, "leave_out.txt")
  # A byte-order mark, CRLF line ends, a comment, a blank line, padding, upper case and
  # a repeat, all of which the reader normalises as a lexicon's words are read.
  ew_write(paste0("\ufeff# words to leave out, one per line\r\n", toupper(high),
                  "\r\n\r\n  ", low, " \r\nzzzz\r\n", low, "\r\n"), listing)
  out <- ew_run(dir, "file", exclude = list(path = ew_posix(listing)))
  expect_identical(ew_stimuli_bytes(out), ew_stimuli_bytes(inline))
  ds <- ew_datasheet(out)
  expect_identical(ds$materials_source$exclusions,
                   list(path = ew_posix(listing), sha256 = ew_sha256_file(listing),
                        n_listed = 3L, n_removed = 2L))
  expect_true(grepl(paste0("An exclusion list (leave_out.txt) removed 2 words from the ",
                           "candidates before selection."), methods_paragraph(ds), fixed = TRUE))
  expect_true(grepl(paste0("An exclusion list in the design removed 2 words from the ",
                           "candidates before selection."),
                    methods_paragraph(ew_datasheet(inline)), fixed = TRUE))
  expect_false(grepl("exclusion list", methods_paragraph(ew_datasheet(plain)), fixed = TRUE))
  expect_null(ew_datasheet(plain)$materials_source$exclusions)
  expect_true(grepl(sprintf("- **Excluded words:** `%s` (3 words, 2 removed, sha256 `%s",
                            ew_posix(listing), substr(ew_sha256_file(listing), 1L, 16L)),
                    render_datasheet_md(ds), fixed = TRUE))
})

test_that("exclude_words_is_refused_for_an_item_table", {
  design <- list(name = "t", language = "english", paradigm = "priming",
                 items = list(source = "table", path = "items/priming_pairs_en.csv"),
                 exclude_words = "dog")
  expect_error(validate_design(design, ew_schema()),
               "exclude_words has no effect for items.source 'table'", fixed = TRUE)
  # A corpus design may name it.
  corpus <- list(name = "c", language = "english", exclude_words = "dog")
  expect_identical(validate_design(corpus, ew_schema()), character(0))
})

test_that("exclude_words_must_list_words_or_name_a_file", {
  # The values YAML gives for [dog, true], [3], 5, {file: words.txt},
  # {path: [a.txt, b.txt]}, {path: '  '} and {}, the last a mapping without a path in
  # both engines' YAML readers, not an empty list.
  for (value in list(list("dog", TRUE), 3L, 5, list(file = "words.txt"),
                     list(path = c("a.txt", "b.txt")), list(path = "  "),
                     yaml::yaml.load("{}"))) {
    design <- list(name = "c", language = "english", exclude_words = value)
    expect_error(validate_design(design, ew_schema()),
                 "exclude_words must be a list of words", fixed = TRUE)
  }
})

test_that("exclude_words_refuses_a_path_it_must_not_follow", {
  design <- list(name = "c", language = "english",
                 exclude_words = list(path = "../words.txt"))
  expect_error(validate_design(design, ew_schema()),
               "exclude_words path must not contain '..'", fixed = TRUE)
  design$exclude_words <- list(paht = "words.txt")
  expect_error(validate_design(design, ew_schema()),
               "did you mean 'exclude_words.path'", fixed = TRUE)
})

test_that("an_exclude_words_file_must_be_readable_utf8_text_with_one_word_a_line", {
  dir <- tempfile("exclude_"); dir.create(dir); on.exit(unlink(dir, recursive = TRUE))
  missing <- ew_posix(file.path(dir, "missing.txt"))
  expect_error(.read_exclude_words(list(path = missing)),
               sprintf("exclude_words names '%s', which is not a readable file", missing),
               fixed = TRUE)
  latin <- file.path(dir, "latin.txt")
  writeBin(as.raw(c(0x63, 0x61, 0x66, 0xe9, 0x0a)), latin)
  expect_error(.read_exclude_words(list(path = ew_posix(latin))), "is not UTF-8 text",
               fixed = TRUE)
  # UTF-16 saved without a byte-order mark decodes as UTF-8 with a NUL after every
  # letter, so its words would match nothing while the datasheet counted them.
  utf16 <- file.path(dir, "utf16.txt")
  writeBin(as.raw(c(0x64, 0x00, 0x6f, 0x00, 0x67, 0x00, 0x0a, 0x00,
                    0x63, 0x00, 0x61, 0x00, 0x74, 0x00, 0x0a, 0x00)), utf16)
  expect_error(.read_exclude_words(list(path = ew_posix(utf16))), "is not UTF-8 text",
               fixed = TRUE)
  # A table read one row a word would exclude nothing while the datasheet counted its
  # rows. A comment may hold a comma, but a word may not.
  table <- file.path(dir, "table.txt")
  ew_write("# word, reason\ndog\ncat,taboo\n", table)
  expect_error(.read_exclude_words(list(path = ew_posix(table))),
               "line 3 of the exclude_words file", fixed = TRUE)
})

test_that("a_lone_word_is_a_list_of_one", {
  one <- .read_exclude_words(" Dog ")
  expect_identical(one$words, "dog")
  expect_identical(one$record, list(path = "inline", sha256 = ew_sha256_text("dog"),
                                    n_listed = 1L))
  empty <- .read_exclude_words(character(0))
  expect_identical(empty, list(words = character(0),
                               record = list(path = "inline", sha256 = ew_sha256_text(""),
                                             n_listed = 0L)))
})

test_that("a_generated_design_keeps_excluded_words_out_of_its_pseudowords", {
  dir <- tempfile("exclude_"); dir.create(dir); on.exit(unlink(dir, recursive = TRUE))
  # 'cag' is a word of this lexicon. Removed from the base words, it must still be one
  # the pseudowords avoid: against the other words alone, 'cat' would become 'cag'.
  words <- c(ew_lex, "cag")
  freq <- ifelse(words %in% c("cat", "man", "cag"), "5.0", "3.0")
  lexicon <- file.path(dir, "lexicon.csv")
  ew_write(paste0("word,freq_zipf\n", paste0(words, ",", freq, "\n", collapse = "")), lexicon)
  design <- list(name = ew_name, language = "english", paradigm = "lexical_decision",
                 items = list(source = "generate", lexicon = ew_posix(lexicon)),
                 n_per_condition = 2L, pool_filters = list(frequency = c(4.5, 6.0)),
                 exclude_words = list("cag"))
  path <- file.path(dir, "design.yaml")
  yaml::write_yaml(design, path)
  out <- file.path(dir, "out")
  run_pipeline(path, ew_schema_path(), out, verbose = FALSE)
  rows <- ew_rows(out)
  real <- sort(rows$target[rows$condition == "word"], method = "radix")
  pseudo <- sort(rows$target[rows$condition == "pseudoword"], method = "radix")
  expect_identical(real, c("cat", "man"))
  expect_false("cag" %in% pseudo)
  want <- build_lexdec_stimuli(data.frame(word = c("cat", "man"), length = c(3L, 3L),
                                          stringsAsFactors = FALSE),
                               2L, reference_words = words)
  expect_identical(pseudo, sort(want$target[want$condition == "pseudoword"], method = "radix"))
  ds <- ew_datasheet(out)
  expect_identical(ds$materials_source$exclusions$n_removed, 1L)
  expect_identical(ds$selection$candidate_pool,
                   list(list(condition = "words in band", n_candidates = 2L)))
})

test_that("excluded_words_stay_in_the_neighbourhood_reference", {
  dir <- tempfile("exclude_"); dir.create(dir); on.exit(unlink(dir, recursive = TRUE))
  # A lexicon without N and OLD20, so the run derives OLD20 for the pool. Every word
  # beginning with b is excluded, and the selected words' OLD20 must still count them
  # among the neighbours.
  lines <- ew_en_lines()
  bare <- file.path(dir, "bare.csv")
  ew_write(paste0(paste(sub("^([^,]*,[^,]*).*$", "\\1", lines), collapse = "\n"), "\n"), bare)
  all_words <- sub(",.*$", "", lines[-1])
  gone <- sort(all_words[startsWith(all_words, "b")], method = "radix")
  out <- ew_run(dir, "out", lexicon = bare, exclude = gone, match_on = c("length", "old20"))
  rows <- ew_rows(out)
  expect_gt(nrow(rows), 0L)
  expect_false(any(startsWith(rows$word, "b")))
  lex <- load_lexicon(bare, ew_schema(), language = "english")
  chosen <- data.frame(word = rows$word, stringsAsFactors = FALSE)
  whole <- add_neighbourhood(chosen, reference = lex$word)
  without <- add_neighbourhood(chosen, reference = lex$word[!(lex$word %in% gone)])
  got <- round(as.numeric(rows$old20), 6)
  expect_identical(got, round(whole$old20, 6))
  # The check has teeth: against the reference without them, some OLD20 differs.
  expect_false(identical(got, round(without$old20, 6)))
  # The candidates lost them all the same.
  pool <- build_pool(lex[!(lex$word %in% gone), , drop = FALSE], list(length = c(4, 7)))
  expect_identical(ew_candidates(ew_datasheet(out)),
                   list(high = nrow(build_pool(pool, list(frequency = c(5.0, 7.0)))),
                        low = nrow(build_pool(pool, list(frequency = c(3.0, 4.0))))))
})
