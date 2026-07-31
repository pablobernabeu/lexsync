# io_utils.R -- robust UTF-8 input/output and provenance helpers.
# Centralising these guards against the encoding pitfalls that arise with
# multilingual stimuli on Windows, and provides the hashing used by the run log.

#' Null-coalescing operator
#'
#' Returns `a` unless it is `NULL`, in which case it returns `b`.
#' @param a,b Values; `a` is returned unless `NULL`.
#' @return `a` or `b`.
#' @name grapes-or-or-grapes
#' @keywords internal
`%||%` <- function(a, b) if (is.null(a)) b else a

#' Read a UTF-8 CSV file
#'
#' @param path Path to a CSV file.
#' @return A data frame (a tibble), as returned by [readr::read_csv()].
#' @importFrom readr read_csv locale
#' @keywords internal
read_csv_utf8 <- function(path, as_character = character(0)) {
  if (!file.exists(path)) {
    stop(sprintf("lexsync: file not found: '%s'", path), call. = FALSE)
  }
  # `as_character` names columns whose type must NOT be guessed. readr reads a column
  # whose values are all `f`, `t`, `T` or `F` as LOGICAL, so an item table coding its
  # two response keys as f and j had `answer` turned into FALSE -- while pandas kept the
  # string "f". Measured, not supposed: readr 2.2.0 reads f and t as logical and j, y
  # and n as character, which is the worst possible split because f/j and t/f are the
  # two commonest key pairs in a two-choice task. The paradigm's presented fields are
  # therefore read as text; every other column keeps its inferred type, so a numeric
  # column a design filters on still arrives numeric.
  col_types <- NULL
  if (length(as_character)) {
    # Only name columns the file actually has: readr warns about a parser for a column
    # that is not there, and a caller naming a paradigm's required fields cannot know
    # whether the table supplies them -- reporting the missing column is load_items's
    # job, and its message says which ones. Reading the header alone costs one line.
    header <- names(readr::read_csv(path, n_max = 0, show_col_types = FALSE,
                                    progress = FALSE,
                                    locale = readr::locale(encoding = "UTF-8")))
    want <- intersect(as_character, header)
    if (length(want)) {
      col_types <- do.call(readr::cols, c(stats::setNames(
        replicate(length(want), readr::col_character(), simplify = FALSE),
        want), list(.default = readr::col_guess())))
    }
  }
  readr::read_csv(
    path,
    col_types = col_types,
    show_col_types = FALSE,
    progress = FALSE,
    locale = readr::locale(encoding = "UTF-8")
  )
}

#' Write a data frame to a BOM-free UTF-8 CSV file
#'
#' @param x A data frame.
#' @param path Output path; parent directories are created as needed.
#' @return `path`, invisibly.
#' @importFrom readr write_csv
#' @keywords internal
write_csv_utf8 <- function(x, path) {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  readr::write_csv(x, path, na = "")
  invisible(path)
}

#' Write text to a file with LF line endings on every platform
#'
#' `writeLines(x, path)` opens the path in text mode, so on Windows R turns every
#' newline into CRLF. The generated experiment scripts are compared against the
#' Python engine's byte for byte, and their checksums are published in the
#' materials datasheet, so their bytes must not record which operating system
#' produced them. A binary connection writes the string as given.
#'
#' @param x A character vector of lines.
#' @param path Output path; parent directories are created as needed.
#' @return `path`, invisibly.
#' @keywords internal
write_lines_lf <- function(x, path) {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  con <- file(path, open = "wb")
  on.exit(close(con), add = TRUE)
  writeLines(x, con, useBytes = TRUE, sep = "\n")
  invisible(path)
}

# ---- Reproducible reductions -----------------------------------------------
# A sum, mean and variance that give the same bits in the R and Python engines.
#
# This is not pedantry; it was a live bug. Two designs' reported means differed between
# the engines in the last decimal place the descriptives publish -- 1.448 against 1.447
# -- because R's mean() uses a two-pass long-double algorithm while numpy sums
# pairwise, and the true value happened to sit on a rounding boundary. Summing 20000
# identical doubles was measured to give three different answers across R's sum(),
# math.fsum, numpy's pairwise sum and a naive loop, so no language's built-in reduction
# can be relied on for a cross-engine artefact.
#
# Neumaier compensated summation is used instead, written out in plain double
# arithmetic in both engines. Every operation is +, -, abs or a comparison, and
# IEEE-754 requires + and - to be correctly rounded, so the two engines execute the
# same sequence of exactly-specified operations and cannot disagree. That is an
# argument rather than a measurement, which is what relying on R's long-double
# accumulator amounted to. Mirrors io_utils.py.

#' @keywords internal
.exact_sum <- function(x) {
  s <- 0; comp <- 0
  for (v in as.numeric(x)) {
    t <- s + v
    # The larger magnitude keeps its low bits; the smaller one's are what get lost, so
    # the correction is computed from whichever term is smaller.
    comp <- comp + if (abs(s) >= abs(v)) ((s - t) + v) else ((v - t) + s)
    s <- t
  }
  s + comp
}

#' @keywords internal
.exact_mean <- function(x) {
  x <- as.numeric(x)
  if (!length(x)) return(NA_real_)
  .exact_sum(x) / length(x)
}

# Two-pass variance: the mean first, then the compensated sum of squared deviations.
# The textbook one-pass form (sum of squares minus n times the squared mean) is
# catastrophically cancelling for data far from zero and would differ between engines
# by far more than a last bit.
#' @keywords internal
.exact_var <- function(x) {
  x <- as.numeric(x)
  n <- length(x)
  if (n < 2L) return(NA_real_)
  d <- x - .exact_mean(x)
  .exact_sum(d * d) / (n - 1L)
}

#' @keywords internal
.exact_sd <- function(x) {
  v <- .exact_var(x)
  # sqrt is correctly rounded under IEEE-754, so it adds no divergence.
  if (is.na(v)) NA_real_ else sqrt(v)
}

# ---- One decimal rounder, shared by both engines ---------------------------
#
# No pairing of built-ins works. Measured over 210,000 values including every 3-dp
# halfway case in range: R's round() disagrees with Python's builtin round(), Python's
# builtin disagrees with numpy's round(), and even R's sprintf("%.3f") disagrees with
# Python's "%.3f" on 274 of them, because R's delegates to the platform C library while
# Python's is correctly rounded. So a value rounded for an artefact cannot be handed to
# any language's own rounder.
#
# This one is defined by its arithmetic instead: scale, truncate toward zero, then step
# away from zero when the remainder reaches a half. Every operation is *, -, /, trunc,
# abs or a comparison, all of which IEEE-754 either mandates correctly rounded or makes
# exact, so both engines compute the same double from the same input by construction.
#
# It rounds the SCALED double rather than the true decimal value, which for a tie that
# is not exactly representable is a choice rather than a theorem. That is the same
# trade-off the balance optimiser's quantisation already makes, and it is the right way
# round: reproducible across engines matters more here than agreeing with what a
# calculator would say about a value that was never exactly a half.
# Must stay identical to _round_dp in python_workflow/src/lexsync/io_utils.py.
#' @keywords internal
.round_dp <- function(x, dp) {
  p <- 10^dp
  y <- as.numeric(x) * p
  t <- trunc(y)
  r <- y - t
  # sign(y) rather than 1: a negative value must step away from zero too.
  adj <- ifelse(is.finite(r) & abs(r) >= 0.5, sign(y), 0)
  out <- (t + adj) / p
  out[!is.finite(y)] <- as.numeric(x)[!is.finite(y)]
  out
}

#' MD5 digest of a file, for provenance logging
#'
#' MD5 (from base \pkg{tools}) is used as a lightweight content fingerprint; it
#' is a provenance aid, not a security measure. The Python package uses the same
#' algorithm so that run logs are comparable across engines.
#'
#' @param path File path.
#' @return A hex digest string, or `NA` when the file is absent.
#' @importFrom tools md5sum
#' @keywords internal
hash_file <- function(path) {
  if (!file.exists(path)) return(NA_character_)
  unname(tools::md5sum(path))
}

#' SHA-256 digest of a file, the stronger fingerprint used by the datasheet
#'
#' @param path File path.
#' @return A hex digest string, or `NA` when the file is absent.
#' @importFrom digest digest
#' @keywords internal
sha256_file <- function(path) {
  if (is.null(path) || is.na(path) || !file.exists(path)) return(NA_character_)
  digest::digest(file = path, algo = "sha256")
}

# Is this design a continuous (non-dichotomised) selection?
#
# One predicate rather than four copies of the same expression. It was repeated
# verbatim in run_pipeline.R, datasheet.R and both Python twins, which is how a
# `continuous:` block under `items.source: table` came to be silently inert in all
# four places at once. `generate` stays excluded deliberately: a continuous block
# there would push a word/pseudoword frame into the selector.
# Must stay identical to _is_continuous in python_workflow/src/lexsync/io_utils.py.
#' @keywords internal
.is_continuous <- function(design) {
  src <- (design$items$source %||% "corpus")
  if (!is.null(design$continuous) && identical(src, "generate")) {
    stop("lexsync: a 'continuous' block cannot be combined with items.source 'generate'.",
         call. = FALSE)
  }
  !is.null(design$continuous) && src %in% c("corpus", "table")
}

# Render one component of a hash key. Never interpolate a number directly: R
# prints 42.0 as "42" and Python as "42.0", and a pandas column silently promoted
# to float64 by a single missing value would otherwise change every digest and so
# every realised duration. Integral values go through %d in both engines.
# Must stay identical to _key_part in python_workflow/src/lexsync/io_utils.py.
#' @keywords internal
.key_part <- function(x) {
  # A component that cannot be rendered identically in both engines must never be
  # silently hashed. Measured: a missing value rendered "NA" here and "nan" in Python,
  # TRUE/FALSE against True/False, Inf against inf. A blank `condition` cell is a
  # routine data error that neither reader rejects, and it produced a DIFFERENT trial
  # order in each engine -- reproducibly, and with nothing to signal it.
  #
  # Raising beats picking a spelling. A missing condition, set or list is always a data
  # error, and a reproducible order computed over a meaningless key is worse than a
  # stop. Booleans do get a pinned spelling, because they are legitimate: R's
  # as.character gives "TRUE" and Python's str gives "True", so the spelling is fixed
  # here rather than left to each language.
  # Must stay identical to _key_part in python_workflow/src/lexsync/io_utils.py.
  if (anyNA(x)) {
    stop(paste("lexsync: a hash-key component is missing, so the trial order cannot be",
               "made identical across engines. Check the items table for a blank",
               "condition, set or list cell."), call. = FALSE)
  }
  if (is.logical(x)) return(ifelse(x, "TRUE", "FALSE"))
  if (is.numeric(x)) {
    if (any(!is.finite(x))) {
      stop("lexsync: a hash-key component is not finite, so it cannot be keyed.",
           call. = FALSE)
    }
    # The integer bound matters: as.integer() beyond it yields NA with a warning, which
    # would put an empty component into the key.
    ok <- x == floor(x) & abs(x) <= .Machine$integer.max
    out <- character(length(x))
    out[ok] <- sprintf("%d", as.integer(x[ok]))
    out[!ok] <- sprintf("%.17g", x[!ok])
    return(out)
  }
  as.character(x)
}

# A uniform variate in [0, 1) derived from a keyed SHA-256 digest.
#
# This is how lexsync gets anything that looks stochastic without a generator:
# jittered durations, and any future search that needs a candidate order. The
# scheme is chosen for exact reproducibility across the two engines rather than
# for elegance, and every part of it is load-bearing.
#
# Thirteen hex digits give a 52-bit integer, which a double represents exactly;
# dividing by 2^52 is exact because the divisor is a power of two. The result is
# therefore the same bits in R and Python rather than merely close. Fourteen
# digits or more would round up to exactly 1.0, and `lo + floor(u * n)` would
# then silently return `hi + 1`. R needs two chunks because `strtoi` returns NA
# above 2^31 - 1.
#
# Only +, -, * and / are used downstream. IEEE-754 mandates those to be
# correctly rounded, so they agree on any conforming platform; `exp`, `log` and
# `^` do not, and were measured to differ between R and Python by one unit in
# the last place. Must stay identical to hash_unit() in
# python_workflow/src/lexsync/io_utils.py.
#' @importFrom digest digest
#' @keywords internal
hash_unit <- function(key) {
  # enc2utf8 because digest(serialize = FALSE) hashes the stored bytes: a
  # latin1-marked string read from a user's CSV would otherwise give a different
  # digest from the same characters in Python.
  h <- vapply(enc2utf8(as.character(key)),
              function(k) digest::digest(k, algo = "sha256", serialize = FALSE),
              character(1), USE.NAMES = FALSE)
  (strtoi(substr(h, 1L, 7L), 16L) * 16777216 + strtoi(substr(h, 8L, 13L), 16L)) /
    4503599627370496
}

# A uniform integer in [lo, hi], both ends included, from a keyed digest.
#' @keywords internal
hash_int_range <- function(key, lo, hi) {
  lo <- as.integer(lo); hi <- as.integer(hi)
  if (any(hi < lo)) stop("lexsync: jitter range must have hi >= lo.", call. = FALSE)
  as.integer(lo + floor(hash_unit(key) * (hi - lo + 1)))
}

#' Build a short, filesystem-safe slug
#'
#' Keeps generated file names short and space-free, which avoids the Windows
#' `MAX_PATH` limit inside deeply nested, cloud-synced directories.
#'
#' @param ... Character fragments to join.
#' @return A lower-case, underscore-separated slug.
#' @keywords internal
slugify <- function(...) {
  s <- paste(c(...), collapse = "_")
  s <- gsub("[^A-Za-z0-9]+", "_", s)
  s <- gsub("_+", "_", s)
  # Reducing to ASCII first does not make base `tolower()` safe here: under a
  # Turkish or Azeri locale it maps "I" to the dotless i (U+0131), so the slug
  # would leave ASCII and this design's artifacts would be written under a name
  # the Python engine never produces. Case-fold as [.lower_invariant()] does.
  .lower_invariant(gsub("^_|_$", "", s))
}

#' Read a YAML configuration file
#'
#' @param path Path to a YAML file.
#' @return A named list.
#' @importFrom yaml read_yaml
#' @keywords internal
read_config <- function(path) {
  if (!file.exists(path)) {
    stop(sprintf("lexsync: configuration not found: '%s'", path), call. = FALSE)
  }
  yaml::read_yaml(path)
}

#' Validate a single stimulus value for safe inclusion in generated files
#'
#' Rejects control characters (including tab/newline) and over-long strings, so a
#' crafted item cannot corrupt the generated loop table or experiment scripts.
#' Commas and quotation marks are allowed: presented strings are written as data
#' into a properly quoted CSV the experiment reads at run time, never interpolated
#' into generated code. Mirrors the Python `clean_field`.
#'
#' @param value A value coerced to a single string.
#' @param field Field name, for error messages.
#' @param max_len Maximum permitted length in characters.
#' @return The value as a plain string.
#' @keywords internal
clean_field <- function(value, field = "field", max_len = 1000L) {
  s <- as.character(value)
  # R character strings cannot themselves contain a nul byte, so guarding the
  # remaining C0 controls and DEL covers every reachable case.
  if (grepl("[\x01-\x1f\x7f]", s, perl = TRUE)) {
    stop(sprintf("lexsync: stimulus '%s' contains control characters: %s", field, s),
         call. = FALSE)
  }
  if (nchar(s) > max_len) {
    stop(sprintf("lexsync: stimulus '%s' exceeds %d characters.", field, max_len), call. = FALSE)
  }
  s
}
