# The datasheet credits the lexicon a design selected from for what it is.
#
# The datasheet and the Methods paragraph credited wordfreq (Speer, 2022) for every
# lexicon a corpus or generated design read, whatever file the design named. A study
# selecting from SUBTLEX-US, or from a lexicon of its own, would have cited the wrong
# corpus. A lexicon lexsync ships is now recognised by the checksum of its bytes with
# CRLF line ends read as LF. A corpus fetched into the cache is credited by the
# registry's citation, and any other file is named by its file name and checksum.
# test_lexicon_provenance.py holds the Python engine to the same tests, by the same
# names.

lp_wordfreq <- paste0("wordfreq (Speer, 2022), data CC BY-SA 4.0; full corpus licence and ",
                      "citation at https://github.com/pablobernabeu/lexsync/blob/main/corpora/",
                      "ATTRIBUTION.md")
# The screened lexicon's credit states its rule, since the datasheet records it.
lp_screened <- paste0("wordfreq (Speer, 2022) screened against SUBTLEX-US (Brysbaert & New, ",
                      "2009), data CC BY-SA 4.0; forms absent from SUBTLEX-US or beginning ",
                      "with a lower-case letter in under 10% of their uses are marked ",
                      "nonstandard, and N and OLD20 count only the unmarked forms; full corpus ",
                      "licence and citation at ",
                      "https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md")
# The English example slice holds only forms the screen keeps, so it marks none.
lp_screened_slice <- paste0("wordfreq (Speer, 2022) screened against SUBTLEX-US (Brysbaert ",
                            "& New, 2009), data CC BY-SA 4.0; forms absent from SUBTLEX-US ",
                            "or beginning with a lower-case letter in under 10% of their ",
                            "uses are left out, and N and OLD20 count neighbours only among ",
                            "the forms the screen keeps; full corpus licence and citation at ",
                            "https://github.com/pablobernabeu/lexsync/blob/main/corpora/",
                            "ATTRIBUTION.md")
lp_slice_credit <- c(en_example.csv = lp_screened_slice, es_example.csv = lp_wordfreq,
                     zh_example.csv = lp_wordfreq)
lp_slices <- names(lp_slice_credit)
lp_derived <- c(en.csv = lp_wordfreq, en_v2.csv = lp_screened, es.csv = lp_wordfreq,
                es_gender.csv = lp_wordfreq, zh.csv = lp_wordfreq)

lp_data <- function(name) system.file("extdata", name, package = "lexsync")
lp_posix <- function(path) gsub("\\", "/", path, fixed = TRUE)
lp_read <- function(path) readBin(path, "raw", file.info(path)$size)
lp_sha256 <- function(path) digest::digest(file = path, algo = "sha256")
# The bytes with every line feed preceded by a carriage return.
lp_crlf <- function(bytes) {
  charToRaw(gsub("\n", "\r\n", rawToChar(bytes), fixed = TRUE, useBytes = TRUE))
}
lp_lf_sha256 <- function(bytes) {
  text <- gsub("\r\n", "\n", rawToChar(bytes), fixed = TRUE, useBytes = TRUE)
  digest::digest(charToRaw(text), algo = "sha256", serialize = FALSE)
}

test_that("a_user_lexicon_is_named_by_file_and_checksum", {
  dir <- tempfile("provenance_"); dir.create(dir); on.exit(unlink(dir, recursive = TRUE))
  # The example slice less its last row: the same columns, but not a file lexsync ships.
  data <- lp_read(lp_data("en_example.csv"))
  lfs <- which(data == as.raw(10L))
  lexicon <- file.path(dir, "my_lexicon.csv")
  writeBin(data[seq_len(lfs[length(lfs) - 1L])], lexicon)
  design <- list(name = "en_own", language = "english", lexicon = lp_posix(lexicon),
                 n_per_condition = 4L, pool_filters = list(length = c(4, 7)),
                 conditions = list(
                   list(name = "high", define_by = list(frequency = c(5.0, 7.0))),
                   list(name = "low", define_by = list(frequency = c(3.0, 4.0)))),
                 match_on = list("length"))
  path <- file.path(dir, "design.yaml")
  yaml::write_yaml(design, path)
  out <- file.path(dir, "out")
  run_pipeline(path, lp_data("schema.yaml"), out, verbose = FALSE)
  ds <- jsonlite::read_json(file.path(out, "reports", "en_own_english_datasheet_R.json"))
  own <- sprintf("a user-supplied lexicon (my_lexicon.csv, sha256 %s)",
                 substr(lp_sha256(lexicon), 1L, 12L))
  expect_identical(ds$materials_source$provenance, own)
  text <- methods_paragraph(ds)
  expect_true(grepl(sprintf("selected from the English lexicon (%s)", own), text, fixed = TRUE))
  expect_false(grepl("wordfreq", text, fixed = TRUE))
})

test_that("a_bundled_lexicon_is_recognised_whatever_its_line_endings", {
  dir <- tempfile("provenance_"); dir.create(dir); on.exit(unlink(dir, recursive = TRUE))
  for (name in lp_slices) {
    data <- lp_read(lp_data(name))
    expect_false(any(data == as.raw(13L)))
    crlf <- file.path(dir, paste0("crlf_", name))
    writeBin(lp_crlf(data), crlf)
    renamed <- file.path(dir, paste0("renamed_", name))
    writeBin(data, renamed)
    credit <- lp_slice_credit[[name]]
    expect_identical(.lexicon_provenance(lp_data(name)), credit, info = name)
    expect_identical(.lexicon_provenance(crlf), credit, info = name)
    expect_identical(.lexicon_provenance(renamed), credit, info = name)
  }
  # One byte more and the file is the user's own.
  changed <- file.path(dir, "changed.csv")
  writeBin(c(lp_read(lp_data("en_example.csv")), charToRaw("zzzz,1.0,en,mine,0,1.0\n")),
           changed)
  expect_identical(.lexicon_provenance(changed),
                   sprintf("a user-supplied lexicon (changed.csv, sha256 %s)",
                           substr(lp_sha256(changed), 1L, 12L)))
})

test_that("the_repository_lexica_are_recognised_with_crlf_line_endings", {
  dir <- tempfile("provenance_"); dir.create(dir); on.exit(unlink(dir, recursive = TRUE))
  # This OneDrive checkout once held en.csv and es.csv with CRLF line ends, which a key
  # on the raw bytes would not have recognised.
  for (name in names(lp_derived)) {
    path <- repo_path("corpora", "derived", name)
    crlf <- file.path(dir, name)
    writeBin(lp_crlf(lp_read(path)), crlf)
    expect_identical(.lexicon_provenance(path), lp_derived[[name]], info = name)
    expect_identical(.lexicon_provenance(crlf), lp_derived[[name]], info = name)
  }
})

test_that("every_bundled_lexicon_is_in_the_provenance_table", {
  named <- vapply(.BUNDLED_LEXICA, function(entry) entry$file, character(1))
  expect_setequal(unname(named), c(paste0("corpora/derived/", names(lp_derived)), lp_slices))
  for (name in lp_slices) {
    expect_identical(names(named)[named == name], lp_lf_sha256(lp_read(lp_data(name))),
                     info = name)
  }
  for (name in names(lp_derived)) {
    data <- lp_read(repo_path("corpora", "derived", name))
    expect_identical(names(named)[named == paste0("corpora/derived/", name)],
                     lp_lf_sha256(data), info = name)
  }
})

test_that("the_english_example_slice_holds_unmarked_rows_of_en_v2", {
  # The slice both packages bundle is 3,000 of the forms the screened lexicon keeps, each
  # with the cells en_v2.csv gives it, N and OLD20 among them. It used to be a slice of
  # en.csv, a quarter of it names, acronyms and other marked forms.
  as_text <- function(path) {
    utils::read.csv(path, colClasses = "character", na.strings = character(0),
                    encoding = "UTF-8")
  }
  v2 <- as_text(repo_path("corpora", "derived", "en_v2.csv"))
  sl <- as_text(lp_data("en_example.csv"))
  expect_identical(names(sl), c("word", "freq_zipf", "language", "source", "n_density",
                                "old20"))
  expect_identical(nrow(sl), 3000L)
  expect_false(anyDuplicated(sl$word) > 0L)
  rows <- v2[match(sl$word, v2$word), , drop = FALSE]
  expect_true(all(rows$nonstandard == "0"))
  for (col in names(sl)[-1L]) expect_identical(rows[[col]], sl[[col]], info = col)
})

test_that("a_registry_corpus_in_the_cache_is_credited_by_its_citation", {
  tmp <- tempfile("lexsync-cache-")
  old <- Sys.getenv("R_USER_CACHE_DIR", unset = NA)
  on.exit({
    if (is.na(old)) Sys.unsetenv("R_USER_CACHE_DIR") else Sys.setenv(R_USER_CACHE_DIR = old)
    unlink(tmp, recursive = TRUE)
  })
  Sys.setenv(R_USER_CACHE_DIR = tmp)
  cache <- lexsync_cache_dir()
  dir.create(cache, recursive = TRUE)
  reg <- yaml::read_yaml(default_registry_path())
  body <- charToRaw("word,freq_zipf\ncat,4.5\ndog,4.6\n")
  cached <- file.path(cache, "subtlex_us.csv")
  writeBin(body, cached)
  expect_identical(.lexicon_provenance(cached), reg$corpora$subtlex_us$citation)
  # A lexicon the wordfreq connector built is credited to wordfreq.
  built <- file.path(cache, "fr_wordfreq.csv")
  writeBin(body, built)
  expect_identical(.lexicon_provenance(built), reg$wordfreq_connector$citation)
  # The same file outside the cache, or a cached file no registry entry names, is the
  # user's own.
  sha <- substr(digest::digest(body, algo = "sha256", serialize = FALSE), 1L, 12L)
  elsewhere <- file.path(tmp, "subtlex_us.csv")
  writeBin(body, elsewhere)
  expect_identical(.lexicon_provenance(elsewhere),
                   sprintf("a user-supplied lexicon (subtlex_us.csv, sha256 %s)", sha))
  mine <- file.path(cache, "mine.csv")
  writeBin(body, mine)
  expect_identical(.lexicon_provenance(mine),
                   sprintf("a user-supplied lexicon (mine.csv, sha256 %s)", sha))
})

test_that("a_cached_corpus_with_a_missing_registry_setting_is_refused", {
  # A lexsync.registry option that names a missing file is refused by name, and the
  # corpus is not credited as the user's own.
  tmp <- tempfile("lexsync-cache-")
  old <- Sys.getenv("R_USER_CACHE_DIR", unset = NA)
  old_opt <- options(lexsync.registry = file.path(tmp, "no_such_registry.yaml"))
  on.exit({
    options(old_opt)
    if (is.na(old)) Sys.unsetenv("R_USER_CACHE_DIR") else Sys.setenv(R_USER_CACHE_DIR = old)
    unlink(tmp, recursive = TRUE)
  })
  Sys.setenv(R_USER_CACHE_DIR = tmp)
  cache <- lexsync_cache_dir()
  dir.create(cache, recursive = TRUE)
  cached <- file.path(cache, "subtlex_esp.csv")
  writeBin(charToRaw("word,freq_zipf\nhola,5\n"), cached)
  msg <- sprintf("lexsync: registry not found: '%s' (the lexsync.registry option).",
                 file.path(tmp, "no_such_registry.yaml"))
  expect_error(.lexicon_provenance(cached), msg, fixed = TRUE)
})

test_that("a_lexicon_that_cannot_be_read_is_still_the_users_own", {
  missing <- file.path(tempfile("provenance_"), "missing.csv")
  expect_identical(.lexicon_provenance(missing), "a user-supplied lexicon (missing.csv)")
  expect_identical(.lexicon_provenance(NULL), "a user-supplied lexicon")
})
