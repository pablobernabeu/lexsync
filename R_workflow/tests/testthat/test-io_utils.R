# The Python engine pins LF to match readr's always-LF output; test_io_utils.py
# pins these same bytes and this same digest.
expected_bytes <- charToRaw("word,condition\ncat,high\ndog,low\n")
expected_sha256 <- "8084f4888fa65455ee56e7eca2954b07b114f5b962bb78c6e8c73c9928e66ad5"

make_frame <- function() {
  data.frame(
    word = c("cat", "dog"), condition = c("high", "low"),
    stringsAsFactors = FALSE
  )
}

test_that("write_csv_utf8 pins LF on every platform", {
  path <- file.path(tempfile("lexsync"), "s.csv")
  write_csv_utf8(make_frame(), path)
  expect_identical(readBin(path, "raw", file.size(path)), expected_bytes)
})

test_that("write_csv_utf8 digest is platform-independent", {
  # The datasheet advertises this digest as provenance, so it must be fixed by
  # the content alone -- not by the line terminator of the host platform.
  path <- file.path(tempfile("lexsync"), "s.csv")
  write_csv_utf8(make_frame(), path)
  expect_identical(sha256_file(path), expected_sha256)
})

test_that("write_csv_utf8 round-trips through read_csv_utf8", {
  path <- file.path(tempfile("lexsync"), "nested", "s.csv")
  write_csv_utf8(make_frame(), path)
  expect_equal(as.data.frame(read_csv_utf8(path)), make_frame())
})

# The CSV-reading fixture, built row by row exactly as test_io_utils.py builds it.
# 1,200 rows, so that a reader guessing types from the first 1,000 sees only numbers
# in `late` and misses the 'n/a' at row 1,101.
csv_fixture <- function() {
  i <- seq_len(1200L)
  pick <- function(map, default) {
    out <- rep(default, length(i))
    out[as.integer(names(map))] <- unname(map)
    out
  }
  rows <- paste(
    sprintf("w%04d", i),
    ifelse(i == 1L, " 3.25 ", "4.5"),
    pick(c("1" = '" NOUN "', "2" = "\tverb\t", "3" = ""), "noun"),
    ifelse(i %% 2L == 1L, "T", "F"),
    ifelse(i == 4L, "", ifelse(i %% 2L == 1L, "TRUE", "False")),
    ifelse(i == 1L, '"1,000"', "2"),
    ifelse(i == 1101L, "n/a", as.character(i)),
    "2026-10-02",
    pick(c("1" = " NA ", "2" = '"NA"'), "1.5"),
    as.character(i),
    pick(c("1" = "+1.5", "2" = ".5", "3" = "5.", "4" = "-2E-2", "5" = "1e3"), "0"),
    ifelse(i == 1L, "Inf", "1"),
    sep = ",")
  header <- "word , freq_zipf,pos,tf,flag,grouped,late,date,miss,n,num,inf"
  charToRaw(paste0(paste(c(header, rows), collapse = "\n"), "\n"))
}

# A column's type as the cross-engine contract names it. R has no separate integer
# type here: an integer column is a double whose every value is whole, which readr and
# Python's int64 both write as "3".
csv_kind <- function(col) {
  if (is.logical(col)) return("logical")
  if (is.double(col)) {
    v <- col[!is.na(col)]
    return(if (!anyNA(col) && length(v) && all(v == trunc(v))) "integer" else "number")
  }
  "text"
}

write_fixture <- function(bytes) {
  path <- tempfile("lexsync", fileext = ".csv")
  writeBin(bytes, path)
  path
}

# The same fixture, types and values are pinned by
# test_one_csv_fixture_reads_the_same_in_both_engines in test_io_utils.py.
test_that("one CSV fixture reads the same in both engines", {
  out <- as.data.frame(read_csv_utf8(write_fixture(csv_fixture())))
  expect_identical(names(out), c("word", "freq_zipf", "pos", "tf", "flag", "grouped",
                                 "late", "date", "miss", "n", "num", "inf"))
  expect_identical(vapply(out, csv_kind, ""), c(
    word = "text", freq_zipf = "number", pos = "text", tf = "text",
    flag = "logical", grouped = "text", late = "text", date = "text",
    miss = "number", n = "integer", num = "number", inf = "text"))
  expect_identical(nrow(out), 1200L)
  expect_identical(out$freq_zipf[1:2], c(3.25, 4.5))
  expect_identical(out$pos[1:4], c("NOUN", "verb", NA, "noun"))
  expect_identical(out$tf[1:2], c("T", "F"))
  expect_identical(out$flag[1:5], c(TRUE, FALSE, TRUE, NA, TRUE))
  expect_identical(out$grouped[1:2], c("1,000", "2"))
  expect_identical(out$late[c(1L, 1101L)], c("1", "n/a"))
  expect_identical(out$date[1], "2026-10-02")
  expect_identical(out$miss[1:3], c(NA, NA, 1.5))
  expect_identical(out$n, as.numeric(1:1200))
  expect_identical(out$num[1:6], c(1.5, 0.5, 5, -0.02, 1000, 0))
  expect_identical(out$inf[1:2], c("Inf", "1"))
})

test_that("read_csv_utf8 keeps as_character columns as trimmed text", {
  out <- read_csv_utf8(write_fixture(csv_fixture()),
                       as_character = c("n", "flag", "freq_zipf", "absent"))
  expect_identical(out$n[1:2], c("1", "2"))
  expect_identical(out$flag[1:4], c("TRUE", "False", "TRUE", NA))
  expect_identical(out$freq_zipf[1:2], c("3.25", "4.5"))
  expect_false("absent" %in% names(out))
})

test_that("read_csv_utf8 refuses a column name given twice", {
  # Trimming the header can make two names one, and either engine's reader would then
  # rename one of them by its own rule, so neither would know which is `word`.
  path <- write_fixture(charToRaw("word,freq_zipf,word \ncat,4,dog\n"))
  expect_error(read_csv_utf8(path), "names column 'word' more than once", fixed = TRUE)
})

test_that("read_csv_utf8 names an empty header cell by its position", {
  out <- read_csv_utf8(write_fixture(charToRaw("word,,freq_zipf,\ncat,x,4,\n")))
  expect_identical(names(out), c("word", "...2", "freq_zipf", "...4"))
})

test_that("read_csv_utf8 reads an empty file as no columns", {
  out <- read_csv_utf8(write_fixture(raw(0)))
  expect_identical(ncol(out), 0L)
  expect_identical(nrow(out), 0L)
})

# Pins the same bits as NUMBER_BITS in test_io_utils.py. Each value takes a path where
# one of R's parsers misses the nearest double: as.numeric() on the first and third,
# readr on the second, fourth and fifth. A negative zero is read as zero, which both
# writers print as "0". The bits are compared as hexadecimal text, since a double
# literal in this file would itself go through R's parser.
test_that("read_csv_utf8 parses a number to the double both engines reach", {
  cells <- c("0.586135918132", "50.768212762897100", "2.91e-11",
             "0.12345678901234567", "1e-400", "-0", "-0.00")
  bits <- c("3fe2c1a01cec6975", "40496254cbba81a5", "3dbffeebfc8b81b5",
            "3fbf9add3746f65e", "0000000000000000", "0000000000000000",
            "0000000000000000")
  hex <- function(x) vapply(x, function(v) paste(rev(as.character(
    writeBin(v, raw(), endian = "little"))), collapse = ""), "", USE.NAMES = FALSE)
  out <- read_csv_utf8(write_fixture(charToRaw(paste0(
    paste(c("x", cells), collapse = "\n"), "\n"))))
  expect_type(out$x, "double")
  expect_identical(hex(out$x), bits)
  written <- tempfile(fileext = ".csv")
  on.exit(unlink(written), add = TRUE)
  write_csv_utf8(read_csv_utf8(write_fixture(charToRaw("z\n-0.00\n1.5\n"))), written)
  expect_identical(readBin(written, "raw", 100L), charToRaw("z\n0\n1.5\n"))
})

# Every artefact-writing path must pin LF, not just the CSV one. write_datasheet and
# write_run_log used bare writeLines(), whose connection is opened in TEXT mode, so on
# Windows all three of their outputs came out CRLF while the Python engine's twins were
# LF: measured 109 CRLF against 0 in one datasheet. The datasheet is the provenance
# artefact of the whole package, so its bytes are the last that should depend on which
# machine happened to build it. The .jsonl run log was already binary and is included
# here so the whole set is covered by one assertion.
test_that("the datasheet and run log pin LF like every other artefact", {
  dir <- tempfile("lf"); dir.create(dir)
  # Fixtures are local: testthat runs each file in its own environment, so the ones in
  # test-datasheet.R are not in scope here.
  schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
  stim <- data.frame(word = c("cat", "dog"), condition = c("hi", "lo"), set = c(1, 1),
                     length = 3L, frequency = c(6, 3), stringsAsFactors = FALSE)
  design <- list(name = "lf", language = "english", match_on = list("length"),
                 n_per_condition = 1L, counterbalance = list(lists = 1))
  ds <- build_datasheet(design, schema, NULL, stim, "x.csv",
                        list(stimuli = NULL, experiments = list()), 2026, engine = "R")
  paths <- write_datasheet(ds, file.path(dir, "d.json"), file.path(dir, "d.md"))

  log <- new_run_log("lf", meta = list(design = "lf"))
  log <- log_step(log, "a step", list(n = 1L))
  write_run_log(log, file.path(dir, "log.md"), file.path(dir, "log.jsonl"))

  for (p in c(paths, file.path(dir, c("log.md", "log.jsonl")))) {
    raw <- readBin(p, "raw", file.size(p))
    expect_false(as.raw(13) %in% raw, info = basename(p))
    expect_true(as.raw(10) %in% raw, info = basename(p))
  }
})

test_that("read_config refuses a duplicated mapping key", {
  # yaml::read_yaml() rejects duplicate map keys by its libyaml parser default;
  # asserting the refusal here pins that default, so a future yaml-package
  # regression is caught rather than silently reopening the gap. The Python
  # engine's yaml.safe_load kept the last value, so read_config there now refuses
  # too (test_read_config_refuses_a_duplicated_mapping_key in test_io_utils.py).
  # The messages differ because this one comes from the C parser; behavioural
  # parity -- both engines refuse -- is the contract.
  path <- file.path(tempdir(), "dup.yaml")
  writeLines(c("name: a", "name: b"), path)
  expect_error(read_config(path), "Duplicate map key", fixed = TRUE)
  # A key repeated in a NESTED mapping must be caught too, not just at the top.
  writeLines(c("items:", "  source: table", "  source: pool"), path)
  expect_error(read_config(path), "Duplicate map key", fixed = TRUE)
  # And an ordinary config still loads.
  writeLines(c("name: a", "items:", "  source: pool"), path)
  expect_identical(read_config(path), list(name = "a", items = list(source = "pool")))
})

test_that("a continuous design over a supplied pool takes the continuous path", {
  # The predicate allowed corpus and table only, so a 'continuous' block over
  # items.source 'pool' fell through to the conditions matcher and failed with a
  # different obscure error in each engine, even though run_pipeline's corpus/pool
  # branch handles continuous selection generically. The Python twin
  # test_a_continuous_design_over_a_supplied_pool_takes_the_continuous_path in
  # test_io_utils.py pins the same outcomes.
  cont <- list(predictor = "frequency", controls = list("length"))
  expect_true(lexsync:::.is_continuous(list(continuous = cont,
                                            items = list(source = "pool"))))
  expect_true(lexsync:::.is_continuous(list(continuous = cont)))  # default: corpus
  expect_false(lexsync:::.is_continuous(list(items = list(source = "pool"))))
  expect_error(lexsync:::.is_continuous(list(continuous = cont,
                                             items = list(source = "generate"))),
               "cannot be combined with items.source 'generate'", fixed = TRUE)
})

# The datasheet's numbers used to go through sprintf(), which hands the rounding to
# the platform's C library. R 4.6.1 on Windows printed 0.0825 at three places as
# "0.082" and 0.165 at two as "0.16", where Python printed "0.083" and "0.17".
# .fmt_dp prints the integer that .round_dp's own arithmetic gives, so no printf
# rounds anything. test_io_utils.py pins the same strings for _fmt_dp.
test_that(".fmt_dp rounds half away from zero without the platform printf", {
  fmt <- lexsync:::.fmt_dp
  expect_identical(fmt(0.0825, 3), "0.083")
  expect_identical(fmt(0.1125, 3), "0.113")
  expect_identical(fmt(0.165, 2), "0.17")
  expect_identical(fmt(0.0005, 4), "0.0005")
  expect_identical(fmt(-0.0825, 3), "-0.083")
  expect_identical(fmt(-0.465, 2), "-0.47")
  expect_identical(fmt(1, 4), "1.0000")
  expect_identical(fmt(3.05, 3), "3.050")
  expect_identical(fmt(12.5, 0), "13")
  # A value that rounds to zero never prints as "-0".
  expect_identical(fmt(-0.0004, 3), "0.000")
  # The stored record keeps four places, so a display at three rounds twice: 0.08249
  # is stored as 0.0825 and shown as 0.083. This is the documented residual.
  expect_identical(fmt(lexsync:::.round_dp(0.08249, 4), 3), "0.083")
  # Missing values print the placeholder, and a vector is formatted elementwise.
  expect_identical(fmt(NULL, 2), "--")
  expect_identical(fmt(NA_real_, 2), "--")
  expect_identical(fmt(NA_real_, 2, na = "n/a"), "n/a")
  expect_identical(fmt(c(0.165, NA, -1.5), 2), c("0.17", "--", "-1.50"))
  expect_identical(fmt(c(Inf, -Inf), 2), c("Inf", "-Inf"))
})

test_that("clean_field rejects control characters but allows commas and quotes", {
  expect_error(clean_field("cat\ndog", "word"), "control characters")
  expect_identical(clean_field('the "big" cat, asleep', "word"), 'the "big" cat, asleep')
})

test_that("slugify is lower-case and path-safe", {
  expect_identical(slugify("En Lexdec", "English!"), "en_lexdec_english")
})

# Pins the same contract as test_slugify_is_locale_invariant in the Python
# engine's test_io_utils.py. Every artefact path in both engines is built from
# slugify(), so a locale-sensitive fold would write this design's files under a
# name the Python engine never produces. Base `tolower()` maps "I" to the
# dotless "i" under a Turkish or Azeri locale, taking the slug out of ASCII --
# and it does so after the reduction to [A-Za-z0-9_], which is why that
# reduction does not make the fold safe by itself.
test_that("slugify folds case whatever the locale", {
  expect_identical(slugify("STUDY_I"), "study_i")

  old <- Sys.getlocale("LC_CTYPE")
  # "Turkish" is the Windows spelling of this locale and resolves nowhere else, so
  # on a Linux runner the test skipped every time and guarded nothing -- which the
  # CI step's zero-skip assertion then reported as a failure. Try each platform's
  # name for the same locale; CI generates tr_TR.UTF-8, so the skip does not fire
  # there and the fold is actually exercised.
  turkish <- ""
  for (nm in c("Turkish", "tr_TR.UTF-8", "tr_TR.utf8", "tr_TR")) {
    turkish <- suppressWarnings(Sys.setlocale("LC_CTYPE", nm))
    if (nzchar(turkish)) break
  }
  skip_if(!nzchar(turkish), "cannot switch to a Turkish locale on this platform")
  on.exit(Sys.setlocale("LC_CTYPE", old), add = TRUE)
  expect_identical(slugify("STUDY_I"), "study_i")
  expect_identical(slugify("En Lexdec", "English!"), "en_lexdec_english")
})

# The two key vocabularies, joined by newlines and hashed. test_io_utils.py pins the
# same digests for DESIGN_KEYS and SCHEMA_KEYS, so a key added to one engine only
# fails both suites.
test_that("the_key_vocabularies_agree_across_engines", {
  digest_of <- function(keys) digest::digest(paste(keys, collapse = "\n"), algo = "sha256",
                                             serialize = FALSE)
  expect_identical(digest_of(.DESIGN_KEYS),
                   "796398d8b83714f232db2f6229bb08d16b109fec67e05422cc8c9a7eea777faa")
  expect_identical(digest_of(.SCHEMA_KEYS),
                   "a62e1a4f7cc410ef37d511e9758107b414bedec2c7ab008704c57171fc7f0e5c")
})

valid_design <- function(...) {
  c(list(name = "kt", language = "english",
         conditions = list(list(name = "high", define_by = list(frequency = c(5, 7))),
                           list(name = "low", define_by = list(frequency = c(1, 3)))),
         match_on = list("length")), list(...))
}

test_that("a_key_near_a_known_one_is_refused_and_any_other_is_noted", {
  # One edit is a typo for a key of up to five characters and two for a longer one;
  # a transposition counts as one edit. `notes` is two edits from `norms` and so is
  # only noted. Pinned identically in test_io_utils.py.
  refusals <- c(nmae = "'nmae' (did you mean 'name'?)",
                langauge = "'langauge' (did you mean 'language'?)",
                fonts = "'fonts' (did you mean 'font'?)")
  for (key in names(refusals)) {
    d <- valid_design()
    d[[key]] <- "x"
    expect_error(validate_design(d, list()),
                 paste0("lexsync: unknown design key ", refusals[[key]]), fixed = TRUE)
  }
  expect_error(validate_design(valid_design(counterbalance = list(list = 2L)), list()),
               paste("lexsync: unknown design key 'counterbalance.list'",
                     "(did you mean 'counterbalance.lists'?)"), fixed = TRUE)
  expect_error(validate_design(list(name = "kt", language = "english", match_on = list("length"),
                                    conditions = list(list(name = "a"), list(nmae = "b"))),
                               list()),
               paste("lexsync: unknown design key 'conditions[2].nmae'",
                     "(did you mean 'conditions[2].name'?)"), fixed = TRUE)
  expect_error(validate_design(valid_design(), list(matchin = list())),
               "lexsync: unknown schema key 'matchin' (did you mean 'matching'?)",
               fixed = TRUE)
  # The schema may set counterbalance.incomplete, which the counterbalancing reads,
  # so it is neither refused nor noted as ignored.
  expect_identical(validate_design(valid_design(),
                                   list(counterbalance = list(incomplete = "error"))),
                   character(0))
  expect_error(validate_design(valid_design(),
                               list(counterbalance = list(incomplet = "error"))),
               paste("lexsync: unknown schema key 'counterbalance.incomplet'",
                     "(did you mean 'counterbalance.incomplete'?)"), fixed = TRUE)
  notes <- validate_design(
    valid_design(notes = "x", date = "May", x_owner = "pb",
                 events = list(list(type = "blank", duration_ms = 100L, colour = "red"))),
    list(x_site = "Oxford", comment = "y"))
  tail <- paste("is not read by lexsync and is ignored; a later release will refuse it.",
                "Put annotations in `description` or a key beginning `x_`.")
  expect_identical(notes, c(
    sprintf("lexsync: design key '%s' %s", c("notes", "date", "events[1].colour"), tail),
    sprintf("lexsync: schema key 'comment' %s", tail)))
})

test_that("the_tie_break_key_is_read_in_a_design_and_a_schema", {
  # matching.tie_break is a setting in both files, so neither run notes it as ignored.
  # Pinned identically in test_io_utils.py.
  expect_identical(validate_design(valid_design(matching = list(tie_break = "hash")),
                                   list(matching = list(tie_break = "bytes"))),
                   character(0))
})

test_that("repeated_and_blank_names_are_judged_alike_in_both_engines", {
  # The first entry that repeats an earlier name is the one reported. Only spaces,
  # tabs and line breaks make a name blank: a no-break space is a name, and a vertical
  # tab is a control character. The Python engine's str.strip() called both blank.
  # Pinned identically in test_io_utils.py.
  expect_error(validate_design(list(name = "kt", language = "english", match_on = list("length"),
                                    conditions = lapply(c("a", "b", "b", "a"),
                                                        function(n) list(name = n))),
                               list()),
               "lexsync: condition name 'b' appears more than once", fixed = TRUE)
  expect_identical(validate_design(list(name = " ", language = "english"), list()),
                   character(0))
  expect_identical(design_stem(list(name = " ", language = "english")),
                   "english_fc0557ea")
  expect_error(validate_design(list(name = "\x0b", language = "english"), list()),
               "lexsync: the design's `name` contains control characters", fixed = TRUE)
  expect_error(validate_design(list(name = " \t\r\n", language = "english"), list()),
               "lexsync: the design has no `name`.", fixed = TRUE)
})

test_that("design_stem_keeps_ascii_names_and_checksums_others", {
  # Two designs with Chinese names and the language 'chinese' both wrote chinese_*,
  # and an all-Chinese name and language wrote files beginning with an underscore or
  # a dot. The suffix is over the NFC form, so canonically equivalent spellings share
  # a stem. Pinned identically in test_io_utils.py.
  expect_identical(design_stem(list(name = "En Lexdec", language = "english")),
                   "en_lexdec_english")
  expect_identical(design_stem(list(name = "\u8bcd\u9891", language = "chinese")),
                   "chinese_14aadfa7")
  expect_identical(design_stem(list(name = "\u7b14\u753b", language = "chinese")),
                   "chinese_444a1c5f")
  expect_identical(design_stem(list(name = "\u9891\u7387", language = "\u4e2d\u6587")),
                   "e525cb84")
  expect_identical(design_stem(list(name = "caf\u00e9", language = "french")),
                   "caf_french_b679d075")
  expect_identical(design_stem(list(name = "cafe\u0301", language = "french")),
                   "caf_french_b679d075")
  expect_error(design_stem(list(name = "!!", language = "--")), "hold no letter or digit")
  expect_error(design_stem(list(language = "english")), "the design has no `name`",
               fixed = TRUE)
})
