# normalise_lexicon(): a corpus file in its publisher's layout, made into a lexicon.
#
# Neither engine could read a SUBTLEX-format file without renaming its columns, turning
# tabs into commas and converting frequencies per million to Zipf by hand, although the
# registry described every one of those steps. test_normalise.py holds the Python
# engine to the same tests, by the same names, and to the same bytes, which
# helper-corpus-files.R and its Python twin pin.

nl_dir <- function() {
  dir <- tempfile("normalise_")
  dir.create(dir)
  dir
}
nl_data <- function(name) system.file("extdata", name, package = "lexsync")
nl_schema <- function() yaml::read_yaml(nl_data("schema.yaml"))

test_that("normalise_lexicon_derives_zipf_from_a_subtlex_us_table", {
  dir <- nl_dir(); on.exit(unlink(dir, recursive = TRUE))
  src <- write_corpus_file(dir, "SUBTLEXus.tsv", SUBTLEX_US)
  out <- file.path(dir, "subtlex_us.csv")
  expect_message(
    lex <- normalise_lexicon(src, columns = SUBTLEX_US_MAP, out = out),
    paste0("lexsync: normalised 5 forms from 'SUBTLEXus.tsv'; 0 of the Zipf values ",
           "derived from frequencies per million lay within 1e-9 of a rounding boundary."),
    fixed = TRUE)
  expect_identical(read_corpus_file(out), SUBTLEX_US_LEXICON)
  expect_identical(attr(lex, "normalisation"),
                   list(n_read = 5L, n_forms = 5L, n_merged = 0L, duplicates = "first",
                        zipf_derived = TRUE, near_boundary = 0L))
  loaded <- load_lexicon(out, nl_schema())
  expect_identical(loaded$word, c("cat", "dog", "the", "you", "zebra"))
})

test_that("normalise_lexicon_reads_a_per_million_csv", {
  dir <- nl_dir(); on.exit(unlink(dir, recursive = TRUE))
  src <- write_corpus_file(dir, "esp.csv", PER_MILLION)
  out <- file.path(dir, "esp_lexicon.csv")
  lex <- suppressMessages(normalise_lexicon(src, columns = PER_MILLION_MAP, out = out))
  expect_identical(read_corpus_file(out), PER_MILLION_LEXICON)
  expect_identical(lex$word, c("caf\u00e9", "de", "ni\u00f1o", "\u00e1rbol"))
})

test_that("normalise_lexicon_detects_a_tab_separated_file", {
  dir <- nl_dir(); on.exit(unlink(dir, recursive = TRUE))
  src <- write_corpus_file(dir, "words.txt", TAB_ZIPF)
  out <- file.path(dir, "words.csv")
  expect_message(lex <- normalise_lexicon(src, out = out),
                 "^lexsync: normalised 2 forms from 'words.txt'\\.\n$")
  expect_identical(read_corpus_file(out), TAB_ZIPF_LEXICON)
  expect_false(attr(lex, "normalisation")$zipf_derived)
})

test_that("normalise_lexicon_sums_duplicate_forms", {
  dir <- nl_dir(); on.exit(unlink(dir, recursive = TRUE))
  src <- write_corpus_file(dir, "Lexique383.tsv", LEXIQUE)
  out <- file.path(dir, "lexique.csv")
  lex <- suppressMessages(normalise_lexicon(src, entry = LEXIQUE_ENTRY, out = out))
  expect_identical(read_corpus_file(out), LEXIQUE_SUM)
  expect_identical(attr(lex, "normalisation")$n_merged, 1L)
  expect_identical(attr(lex, "normalisation")$duplicates, "sum")
  # Without the entry's rule the first row of a repeated form is kept.
  suppressMessages(normalise_lexicon(src, columns = LEXIQUE_ENTRY$columns, out = out))
  expect_identical(read_corpus_file(out), LEXIQUE_FIRST)
})

test_that("normalise_lexicon_counts_values_near_a_rounding_boundary", {
  dir <- nl_dir(); on.exit(unlink(dir, recursive = TRUE))
  # Only the count is pinned: the value itself is the one the engines may round apart.
  lex <- suppressMessages(normalise_lexicon(write_corpus_file(dir, "edge.csv", NEAR_BOUNDARY)))
  expect_identical(attr(lex, "normalisation")$near_boundary, 1L)
})

test_that("normalise_lexicon_takes_a_registry_entry_by_name", {
  dir <- nl_dir(); on.exit(unlink(dir, recursive = TRUE))
  src <- write_corpus_file(dir, "SUBTLEXus.tsv", SUBTLEX_US)
  out <- file.path(dir, "subtlex_us.csv")
  old <- options(lexsync.registry = nl_data("registry.yaml")); on.exit(options(old), add = TRUE)
  suppressMessages(normalise_lexicon(src, entry = "subtlex_us", out = out))
  expect_identical(read_corpus_file(out), SUBTLEX_US_LEXICON)
})

test_that("normalise_lexicon_refuses_non_positive_frequencies", {
  dir <- nl_dir(); on.exit(unlink(dir, recursive = TRUE))
  for (value in c("0", "-1.5")) {
    src <- write_corpus_file(dir, "zero.csv",
                             sprintf("word,freq_permillion\ndog,12.5\ncat,%s\n", value))
    expect_error(normalise_lexicon(src),
                 sprintf("'freq_permillion' holds %s for 'cat'.*positive",
                         gsub(".", "\\.", value, fixed = TRUE)),
                 info = value)
  }
})

test_that("normalise_lexicon_refuses_an_unusable_map", {
  dir <- nl_dir(); on.exit(unlink(dir, recursive = TRUE))
  src <- write_corpus_file(dir, "SUBTLEXus.tsv", SUBTLEX_US)
  expect_error(normalise_lexicon(src, columns = list(word = "Word", freq_zipf = "Zipf")),
               "has no column 'Zipf'", fixed = TRUE)
  expect_error(normalise_lexicon(src, columns = list(word = "Word", freq_zipf = "Lg10WF",
                                                     freq_permillion = "SUBTLWF")),
               "freq_zipf or freq_permillion, not both", fixed = TRUE)
  expect_error(normalise_lexicon(src, columns = list(word = "Word", lemma = "Word",
                                                     freq_permillion = "SUBTLWF")),
               "unknown key 'lemma'", fixed = TRUE)
  expect_error(normalise_lexicon(src, entry = list(columns = list(word = "Word",
                                                                  freq_zipf = "Lg10WF"),
                                                   duplicates = "sum")),
               "duplicates: sum adds frequencies per million", fixed = TRUE)
  expect_error(normalise_lexicon(src, entry = list(columns = SUBTLEX_US_MAP,
                                                   duplicates = "mean")),
               "duplicates must be 'first' or 'sum'", fixed = TRUE)
  expect_error(normalise_lexicon(src, columns = list(word = "Word")),
               "no column named freq_zipf or freq_permillion", fixed = TRUE)
})

test_that("a_run_over_a_lexicon_with_frequencies_per_million_records_the_boundary_count", {
  dir <- nl_dir(); on.exit(unlink(dir, recursive = TRUE))
  # The example slice with a rate per million on every row, as normalise_lexicon()
  # writes one. log10(1.5) + 3 is 3.176..., far from a rounding boundary.
  lines <- strsplit(read_corpus_file(nl_data("en_example.csv")), "\n", fixed = TRUE)[[1]]
  lines <- lines[nzchar(lines)]
  body <- c(paste0(lines[1], ",freq_permillion"), paste0(lines[-1], ",1.5"))
  lexicon <- write_corpus_file(dir, "per_million.csv", paste0(paste(body, collapse = "\n"), "\n"))
  design <- list(name = "en_pm", language = "english", lexicon = gsub("\\", "/", lexicon, fixed = TRUE),
                 n_per_condition = 4L, pool_filters = list(length = c(4, 7)),
                 conditions = list(
                   list(name = "high", define_by = list(frequency = c(5.0, 7.0))),
                   list(name = "low", define_by = list(frequency = c(3.0, 4.0)))),
                 match_on = list("length"))
  path <- file.path(dir, "design.yaml")
  yaml::write_yaml(design, path)
  out <- file.path(dir, "out")
  run_pipeline(path, nl_data("schema.yaml"), out, verbose = FALSE)
  ds <- jsonlite::read_json(file.path(out, "reports", "en_pm_english_datasheet_R.json"))
  n <- length(body) - 1L
  expect_identical(ds$materials_source$zipf_derivation,
                   list(n_values = n, near_boundary = 0L))
  log <- read_corpus_file(file.path(out, "reports", "en_pm_english_run_log_R.md"))
  expect_true(grepl(sprintf(paste("freq_permillion: 0 of %d value(s) put Zipf within 1e-9 of",
                                  "a rounding boundary"), n), log, fixed = TRUE))
  md <- read_corpus_file(file.path(out, "reports", "en_pm_english_datasheet_R.md"))
  expect_true(grepl(sprintf(paste("- **Zipf from frequencies per million:** 0 of %d value(s)",
                                  "within 1e-9 of a rounding boundary"), n), md, fixed = TRUE))
  # A lexicon without the column, every shipped one included, carries no record.
  design$lexicon <- gsub("\\", "/", nl_data("en_example.csv"), fixed = TRUE)
  yaml::write_yaml(design, path)
  run_pipeline(path, nl_data("schema.yaml"), out, verbose = FALSE)
  ds <- jsonlite::read_json(file.path(out, "reports", "en_pm_english_datasheet_R.json"))
  expect_null(ds$materials_source$zipf_derivation)
})

test_that("normalise_lexicon_without_out_writes_nothing", {
  dir <- nl_dir(); on.exit(unlink(dir, recursive = TRUE))
  src <- write_corpus_file(dir, "Lexique383.tsv", LEXIQUE)
  lex <- suppressMessages(normalise_lexicon(src, entry = LEXIQUE_ENTRY))
  expect_true(is.data.frame(lex))
  expect_identical(names(lex), c("word", "freq_zipf", "freq_permillion"))
  expect_identical(lex$freq_zipf, c(4.756, 3.497, 3.722))
  expect_identical(list.files(dir), "Lexique383.tsv")
})
