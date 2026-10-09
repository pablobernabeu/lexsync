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

# ---- One CSV reading rule, shared by both engines ----------------------------
#
# readr and pandas each guess a column's type by their own heuristics, and the two
# disagreed on ordinary input. readr trimmed fields and headers and pandas trimmed
# nothing, so a padded category made the Python engine refuse a design this engine ran.
# readr guessed types from the first 1,000 rows, read T and F as logical, "1,000" as a
# number and ISO dates as dates, so a pass-through column was written `FALSE` here and
# `F` by the Python engine. Both engines therefore read every cell as text and convert
# it here, by one rule written out in each. Must stay identical to read_csv_utf8 and
# _type_column in python_workflow/src/lexsync/io_utils.py.
#
# The characters trimmed from every header name and cell: the ASCII whitespace readr's
# trim_ws removed. A no-break space is data in both engines.
.CSV_TRIM <- "^[ \t\r\n]+|[ \t\r\n]+$"
# A plain decimal number: an optional sign, digits with an optional point, and an
# optional exponent. No thousands separators and no Inf or NaN.
.NUMERIC_CELL <- "^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)([eE][+-]?[0-9]+)?$"
# Not T and F, which readr took as logical: a design coding its two response keys as
# f and t had them turned into FALSE and TRUE (see NEWS for 0.1.0).
.LOGICAL_TRUE <- c("TRUE", "true", "True")
.LOGICAL_FALSE <- c("FALSE", "false", "False")
# 10^0 to 10^22, each built by an exact multiplication: every one of them is a double.
.POW10 <- Reduce(function(p, i) p * 10, seq_len(22L), accumulate = TRUE, 1)

# Trimmed cells, with "" and "NA" (quoted or not) as NA.
.csv_cells <- function(x) {
  x <- gsub(.CSV_TRIM, "", x)
  x[is.na(x) | x %in% c("", "NA")] <- NA_character_
  x
}

# Trimmed header names. An empty name is named by its position, as readr names it
# ("...3"), and a name given twice is refused: each reader would otherwise rename one
# copy by its own rule, and neither would know which of them is `word`.
.csv_names <- function(header, path) {
  nm <- gsub(.CSV_TRIM, "", header)
  nm[is.na(nm)] <- ""
  empty <- !nzchar(nm)
  nm[empty] <- paste0("...", which(empty))
  dup <- nm[duplicated(nm)]
  if (length(dup)) {
    stop(sprintf(paste("lexsync: the header of '%s' names column '%s' more than once",
                       "(after trimming whitespace); each column name may appear",
                       "once."), path, dup[1]), call. = FALSE)
  }
  nm
}

#' Parse plain decimal numbers to the correctly rounded double
#'
#' Python's `float()` returns the double nearest the decimal, and neither of R's own
#' parsers does in every case: measured over 200,000 random decimals, readr's
#' `parse_double()` missed by one unit in the last place on 26,706 and `as.numeric()`
#' on 35, among them `0.586135918132` and `2.91e-11`. A value with at most 15
#' significant digits and a power of ten within 10^22 is therefore computed as one
#' exact integer times or divided by one exact power of ten. That is a single IEEE-754
#' operation, which is correctly rounded, so both engines reach the same double. Every
#' value in the shipped lexica is of that kind. Any other value falls back to
#' `as.numeric()`, and the engines may then differ in its last bit. readr's parser is
#' not used there: over 60,008 random values of that kind it missed the nearest double on 21,644 and
#' `as.numeric()` on 25, and it read `1e400` as 1e307 and `1e-400` as 1e-307, where
#' `as.numeric()` and `float()` give `Inf` and 0. A negative zero is read as zero,
#' because the two engines' writers would print it as `-0` and `0`.
#'
#' @param x A character vector whose non-missing values match `.NUMERIC_CELL`.
#' @return A double vector.
#' @keywords internal
.parse_decimal <- function(x) {
  out <- rep(NA_real_, length(x))
  ok <- which(!is.na(x))
  if (!length(ok)) return(out)
  s <- x[ok]
  neg <- startsWith(s, "-")
  body <- sub("^[+-]", "", s)
  has_exp <- grepl("[eE]", body)
  mant <- sub("[eE].*$", "", body)
  ex <- rep(0, length(s))
  ex[has_exp] <- as.numeric(sub("^[^eE]*[eE]", "", body[has_exp]))
  has_point <- grepl(".", mant, fixed = TRUE)
  frac <- ifelse(has_point, sub("^[^.]*[.]", "", mant), "")
  digits <- sub("^0+", "", paste0(sub("[.].*$", "", mant), frac))
  # Trailing zeros move into the exponent, so 1.50000000000000000 is 15 times 10^-1.
  kept <- sub("0+$", "", digits)
  e10 <- ex - nchar(frac) + (nchar(digits) - nchar(kept))
  m <- ifelse(nzchar(kept), as.numeric(ifelse(nzchar(kept), kept, "0")), 0)
  fast <- nchar(kept) <= 15L & abs(e10) <= 22
  v <- rep(NA_real_, length(s))
  up <- fast & e10 >= 0
  down <- fast & e10 < 0
  v[up] <- m[up] * .POW10[e10[up] + 1]
  v[down] <- m[down] / .POW10[-e10[down] + 1]
  v[fast & !nzchar(kept)] <- 0
  v[fast & neg] <- -v[fast & neg]
  if (any(!fast)) v[!fast] <- as.numeric(s[!fast])
  v[which(v == 0)] <- 0
  out[ok] <- v
  out
}

#' Type one column by the rule both engines share
#'
#' Numeric when every non-missing value is a plain decimal number, parsed by
#' [.parse_decimal()]. Logical when every non-missing value is TRUE, FALSE, true,
#' false, True or False. Text otherwise. A column with no values at all is numeric,
#' all missing. Dates are never parsed.
#'
#' @param x A character vector of trimmed cells, `NA` for missing.
#' @return A double, logical or character vector.
#' @keywords internal
.type_column <- function(x) {
  v <- x[!is.na(x)]
  if (all(grepl(.NUMERIC_CELL, v, perl = TRUE))) return(.parse_decimal(x))
  if (all(v %in% c(.LOGICAL_TRUE, .LOGICAL_FALSE))) {
    out <- x %in% .LOGICAL_TRUE
    out[is.na(x)] <- NA
    return(out)
  }
  x
}

#' Read a UTF-8 CSV file by the rule both engines share
#'
#' Every header name and cell is trimmed of spaces, tabs, carriage returns and line
#' feeds. After trimming, an empty cell and `NA` (quoted or not) are missing, and
#' every other word, `null`, `nan` and `none` included, is a value. Each column not named in
#' `as_character` then takes its type from all of its values: numeric when every value
#' is a plain decimal number (no thousands separators), logical when every value is
#' TRUE or FALSE in upper, lower or title case, and text otherwise. Dates are never
#' parsed. A UTF-8 byte-order mark is ignored.
#'
#' @param path Path to a CSV file.
#' @param as_character Character vector of column names that stay text, trimmed. A
#'   name the file's header does not carry is ignored.
#' @return A data frame (a tibble). An empty file gives one with no columns.
#' @importFrom readr read_csv locale
#' @keywords internal
read_csv_utf8 <- function(path, as_character = character(0)) {
  if (!file.exists(path)) {
    stop(sprintf("lexsync: file not found: '%s'", path), call. = FALSE)
  }
  # The header row is read as data, so that the names are seen before readr repairs a
  # duplicate, and every cell as text with nothing trimmed or treated as missing, so
  # that the rule below is the only one applied.
  raw <- readr::read_csv(
    path,
    col_names = FALSE,
    col_types = readr::cols(.default = readr::col_character()),
    na = character(0),
    trim_ws = FALSE,
    show_col_types = FALSE,
    progress = FALSE,
    locale = readr::locale(encoding = "UTF-8")
  )
  if (!nrow(raw)) return(raw)
  nm <- .csv_names(unlist(raw[1L, ], use.names = FALSE), path)
  out <- raw[-1L, , drop = FALSE]
  names(out) <- nm
  for (j in seq_along(nm)) {
    cells <- .csv_cells(out[[j]])
    out[[j]] <- if (nm[j] %in% as_character) cells else .type_column(cells)
  }
  out
}

# Where readr leaves fixed notation. Beyond it readr's layout could not be reproduced
# in Python: it writes 1.5e16 as "15e15", the largest double as "17976931348623157e292",
# and the double nearest 5e22 as "4.9999999999999996e+22", and no single rule fits all
# three. Above 2^49 consecutive doubles are more than 0.1 apart, so two different
# one-decimal strings can round-trip to the same double and the engines print different
# ones: readr writes 1000000000000000.25 as "...0.3" where Python gives "...0.2".
.READR_BIG <- 1e15
.READR_TIE <- 2^49

#' Refuse a value the two engines could not write identically
#'
#' Nothing lexsync computes reaches these magnitudes (frequencies are Zipf values under
#' 8, counts and durations under 1e6), but a joined norm table, a supplied pool
#' or an item table may carry any column the user likes, and those columns go straight
#' into the stimuli CSV. The guard lives in both engines so that each refuses the same
#' design; one engine accepting what the other rejects is a difference of its own.
#'
#' @param x A data frame about to be written.
#' @return `x`, invisibly, or an error.
#' @keywords internal
.check_csv_writable <- function(x) {
  for (nm in names(x)) {
    col <- x[[nm]]
    if (!is.numeric(col) || is.integer(col)) next
    v <- col[is.finite(col)]
    if (!length(v)) next
    big <- v[abs(v) >= .READR_BIG]
    if (length(big)) {
      stop(sprintf(paste("lexsync: column '%s' holds %s, which is too large to write",
                         "identically from both engines. Above 1e15 readr's number",
                         "format could not be reproduced in Python, so the R and Python",
                         "CSVs would differ with nothing to signal it. Scale the column,",
                         "or carry it as text."), nm, format(big[1], digits = 17)),
           call. = FALSE)
    }
    # The shortest decimal is unique below 2^49, so only this band needs the check.
    tie <- v[abs(v) >= .READR_TIE & v != trunc(v)]
    for (t in tie) {
      a <- abs(t)
      # Between 2^49 and 1e15 consecutive doubles are exactly 0.125 apart, so a
      # non-integral double's shortest round-tripping decimal has exactly one
      # fractional digit, and the form is ambiguous precisely when two neighbouring
      # one-decimal strings parse back to the same double. `ip + d/10` IS that
      # parse: ip is an exact double (below 2^53), the error of d/10 is under
      # 2^-56, and no candidate sits nearer a rounding boundary than 1/80, so the
      # sum rounds to the same double the decimal string does. Must refuse exactly
      # what _shortest_digits_ambiguous refuses in io_utils.py.
      ip <- trunc(a)
      if (sum(ip + (1:9) / 10 == a) >= 2L) {
        stop(sprintf(paste("lexsync: column '%s' holds %s, which has more than one",
                           "shortest decimal form. The R and Python engines print",
                           "different ones, so the two CSVs would differ with nothing to",
                           "signal it. Round the column, or carry it as text."),
                     nm, format(t, digits = 16)), call. = FALSE)
      }
    }
  }
  invisible(x)
}

#' Write a data frame to a BOM-free UTF-8 CSV file
#'
#' @param x A data frame.
#' @param path Output path; parent directories are created as needed.
#' @return `path`, invisibly.
#' @details A value the two engines cannot render alike is refused, naming the column:
#'   a magnitude at or above 1e15, where readr has three incompatible layouts and no
#'   rule fits all of them, and a value with two equally short decimal forms, where the
#'   two writers pick opposite ones.
#' @importFrom readr write_csv
#' @keywords internal
write_csv_utf8 <- function(x, path) {
  .check_csv_writable(x)
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
# A sum, mean, variance and median that give the same bits in the R and Python
# engines.
#
# This is not pedantry; it was a live bug. Two designs' reported means differed between
# the engines in the last decimal place the descriptives publish, 1.448 from R against
# 1.447 from numpy, because R's mean() uses a two-pass long-double algorithm while
# numpy sums pairwise, and the true value happened to sit on a rounding boundary.
# Summing 20000 identical doubles was measured to give three different answers across
# R's sum(), math.fsum, numpy's pairwise sum and a naive loop, so no language's
# built-in reduction can be relied on for a cross-engine artefact.
#
# Neumaier compensated summation is used instead, written out in plain double
# arithmetic in both engines. Every operation is +, -, abs or a comparison, and
# IEEE-754 requires + and - to be correctly rounded, so the two engines execute the
# same sequence of exactly-specified operations and cannot disagree. That is an
# argument. Relying on R's long-double accumulator amounted only to a measurement.
# Mirrors io_utils.py.

#' @keywords internal
.exact_sum <- function(x) {
  x <- as.numeric(x)
  # A missing value propagates, which is the contract the Python engine keeps: there
  # `abs(s) >= abs(v)` on a NaN is False and the sum comes back NaN, while here the
  # same comparison is NA and R would stop. The mean, variance and standard deviation
  # are built on this sum and inherit the contract. The median is the deliberate
  # exception, dropping missing values before it sorts.
  if (anyNA(x)) return(NA_real_)
  s <- 0; comp <- 0
  for (v in x) {
    t <- s + v
    # The larger magnitude keeps its low bits; the smaller one's are what get lost, so
    # the correction is computed from whichever term is smaller. Opposite infinities
    # make the running sum NaN, and isTRUE() then takes the branch Python's False
    # takes, where a bare comparison would be NA and stop.
    comp <- comp + if (isTRUE(abs(s) >= abs(v))) ((s - t) + v) else ((v - t) + s)
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

# Median via a sort and the exact middle. stats::median averages the two middle
# values through mean(), whose long-double accumulator is platform-dependent;
# (a + b) / 2 in plain double arithmetic is one correctly-rounded IEEE addition
# and one exact halving, so both engines compute the same double from the same
# input. Must stay identical to _exact_median in
# python_workflow/src/lexsync/io_utils.py.
#' @keywords internal
.exact_median <- function(x) {
  x <- as.numeric(x)
  x <- x[!is.na(x)]
  n <- length(x)
  if (!n) return(NA_real_)
  x <- sort(x, method = "radix")
  if (n %% 2L == 1L) return(x[(n + 1L) %/% 2L])
  (x[n %/% 2L] + x[n %/% 2L + 1L]) / 2
}

# ---- One decimal rounder, shared by both engines ---------------------------
#
# No pairing of built-ins works. Measured over 210,000 values including every 3-dp
# halfway case in range: R's round() disagrees with Python's builtin round(), Python's
# builtin disagrees with numpy's round(), and even R's sprintf("%.3f") disagrees with
# Python's "%.3f" on 274 of them, because R's delegates to the platform C library while
# Python's is correctly rounded. No value rounded for an artefact can safely be handed
# to any language's own rounder.
#
# This one is defined by its arithmetic instead: scale, truncate toward zero, then step
# away from zero when the remainder reaches a half. Every operation is *, -, /, trunc,
# abs or a comparison, all of which IEEE-754 either mandates correctly rounded or makes
# exact, so both engines compute the same double from the same input by construction.
#
# It rounds the SCALED double. For a tie that is not exactly representable, the true
# decimal value would give a different answer, so this is a choice the package makes
# and arithmetic does not force. It is the same trade-off the balance optimiser's
# quantisation already makes, and it is the right way
# round: reproducible across engines matters more here than agreeing with what a
# calculator would say about a value that was never exactly a half.
# Must stay identical to _round_dp in python_workflow/src/lexsync/io_utils.py. This
# function is already vectorised, so it is also the twin of the Python engine's
# _round_dp_vec, which applies the same arithmetic over a whole numpy array; a
# change here must land in both of them.
#' @keywords internal
.round_dp <- function(x, dp) {
  y <- as.numeric(x) * 10^dp
  out <- .round_dp_scaled(y) / 10^dp
  out[!is.finite(y)] <- as.numeric(x)[!is.finite(y)]
  out
}

# The integer .round_dp divides back down: y = x * 10^dp, truncated toward zero and
# stepped away from zero at a remainder of a half. Shared with .fmt_dp, so a printed
# number and a rounded one cannot disagree. Twin of _round_dp_scaled in io_utils.py.
.round_dp_scaled <- function(y) {
  t <- trunc(y)
  r <- y - t
  # sign(y), because a negative value must step away from zero too.
  t + ifelse(is.finite(r) & abs(r) >= 0.5, sign(y), 0)
}

# ---- One number formatter, shared by both engines --------------------------
#
# sprintf("%.3f") hands the rounding to the platform's C library, which is the
# disagreement described above: R 4.6.1 on Windows prints 0.0825 as "0.082" where
# Python prints "0.083". Every number shown in the Markdown datasheet and the
# Methods paragraph therefore comes from here. It takes the scaled integer from
# .round_dp's own arithmetic, prints that integer's digits and places the decimal
# point by string operations. sprintf("%.0f") of an integer-valued double involves
# no rounding and is exact below 2^53, far beyond any statistic shown at four places.
# The sign is taken from the rounded integer, so a value that rounds to zero prints
# without a minus sign. Missing values print `na`, and infinities print as "Inf" and
# "-Inf". It is vectorised, and must stay identical to _fmt_dp in
# python_workflow/src/lexsync/io_utils.py.
#' @keywords internal
.fmt_dp <- function(x, dp, na = "--") {
  if (is.null(x) || !length(x)) return(na)
  x <- as.numeric(x)
  y <- x * 10^dp
  t <- .round_dp_scaled(y)
  digits <- sprintf("%.0f", abs(t))
  short <- nchar(digits) < dp + 1L
  digits[short] <- paste0(strrep("0", dp + 1L - nchar(digits[short])), digits[short])
  n <- nchar(digits)
  out <- if (dp > 0)
    paste0(substr(digits, 1L, n - dp), ".", substr(digits, n - dp + 1L, n))
  else digits
  out <- paste0(ifelse(t < 0, "-", ""), out)
  # An infinite scaled value, from an infinite input or one too large to scale.
  out[is.infinite(y)] <- ifelse(y[is.infinite(y)] > 0, "Inf", "-Inf")
  out[is.na(x)] <- na
  out
}

# A setting as the datasheet prints it: an alpha, a bound, a tolerance k, or the
# confidence level an alpha gives. The shared rounder takes the value to six places
# first, so the floating-point error in 1 - 2 * 0.05 cannot reach the text, and %g then
# drops the trailing zeros: 90, 0.05, 1.5. A setting needs no fixed number of places,
# and a bound that YAML reads as 1.0 in Python and 1 in R prints as 1 in both. Six
# significant digits leave %g nothing to round in a setting written by hand. Must stay
# identical to _fmt_g in python_workflow/src/lexsync/io_utils.py.
#' @keywords internal
.fmt_g <- function(x) sprintf("%g", .round_dp(as.numeric(x), 6))

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
# One predicate, where there were four copies of the same expression. It was repeated
# verbatim in run_pipeline.R, datasheet.R and both Python twins, which is how a
# `continuous:` block under `items.source: table` came to be silently inert in all
# four places at once. `pool` belongs in the allowed set because run_pipeline's
# corpus/pool branch handles continuous selection generically; leaving it out sent a
# continuous design over a supplied pool to the conditions matcher, which then failed
# with a different obscure error in each engine. `generate` stays excluded
# deliberately: a continuous block there would push a word/pseudoword frame into the
# selector.
# Must stay identical to _is_continuous in python_workflow/src/lexsync/io_utils.py.
#' @keywords internal
.is_continuous <- function(design) {
  src <- (design[["items"]][["source"]] %||% "corpus")
  if (!is.null(design[["continuous"]]) && identical(src, "generate")) {
    stop("lexsync: a 'continuous' block cannot be combined with items.source 'generate'.",
         call. = FALSE)
  }
  !is.null(design[["continuous"]]) && src %in% c("corpus", "pool", "table")
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
  # order in each engine, reproducibly and with nothing to signal it.
  #
  # Raising beats picking a spelling. A missing condition, set or list is always a data
  # error, and a reproducible order computed over a meaningless key is worse than a
  # stop. Booleans do get a pinned spelling, because they are legitimate: R's
  # as.character gives "TRUE" and Python's str gives "True", so the spelling is fixed
  # here, so neither language chooses it.
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
# scheme is chosen for exact reproducibility across the two engines, and every
# step of it is there for a reason.
#
# Thirteen hex digits give a 52-bit integer, which a double represents exactly;
# dividing by 2^52 is exact because the divisor is a power of two. The result is
# therefore identical bits in R and Python, to the last one. Fourteen
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
  # would leave ASCII and this design's artefacts would be written under a name
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
#' Commas, quotation marks, braces and brackets are allowed. Presented strings are
#' written as data into a properly quoted CSV the experiment reads at run time,
#' never interpolated into generated code, and no target evaluates them.
#' OpenSesame, which evaluates the cells of its loop table, reads stimulus text
#' from a companion table with Python's `csv` module. Mirrors the Python
#' `clean_field`.
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

# Characters that can leave a data position and start a code one. A stimulus may hold
# any of these, because a stimulus is written to a CSV the experiment reads at run time;
# a value INTERPOLATED INTO the generated script or markup may not.
#   ' " \ backtick  end a Python or JavaScript string literal
#   < > &           open a tag or entity in the generated HTML
#   { } ;           end a CSS declaration, or a template placeholder
#   $               begins a JavaScript template substitution
.UNSAFE_META <- "['\"\\\\`<>&{};$]"
# \z and not $: in PCRE (and in Python's re) `$` also matches just BEFORE a final
# newline, so a value ending in one satisfied a `$`-anchored shape check and carried
# that newline into a line-oriented .osexp, splitting the inline script it landed in.
# Anchoring at end-of-string is the whole guard here.
.PORT_SHAPE <- "^(0[xX][0-9A-Fa-f]{1,8}|[0-9]{1,10})\\z"
.COLUMN_SHAPE <- "^[A-Za-z_][A-Za-z0-9_]*\\z"
# A response key is written into OpenSesame's `set allowed_responses "a;b"`, into a
# PsychoPy key list and into a jsPsych `choices` array. Key names are short tokens.
.KEY_SHAPE <- "^[A-Za-z0-9_ +]{1,20}\\z"

#' Validate a metadata value interpolated into generated code or markup
#'
#' A design's name, language label and font are not stimuli. They do not travel in the
#' loop table the experiment reads at run time; they are substituted straight into the
#' PsychoPy script, the OpenSesame inline Python and the jsPsych HTML, so a quote or an
#' angle bracket there stops being text and becomes syntax. A design file is meant to be
#' shared and re-run by someone else, which is what makes an unvalidated one an
#' executable payload as much as a configuration.
#'
#' Refusing beats escaping. Escaping correctly would mean three different escapes for
#' three targets in two engines, six places to get subtly wrong, and it would change the
#' bytes the two engines write; refusing is one rule that leaves every legitimate value
#' ("en_lexdec", "english", "Courier New", "SimHei") byte-identical. Mirrors the Python
#' `clean_meta`.
#'
#' @param value A value coerced to a single string.
#' @param field Field name, for error messages.
#' @param max_len Maximum permitted length in characters.
#' @return The value as a plain string.
#' @keywords internal
clean_meta <- function(value, field = "value", max_len = 200L) {
  s <- as.character(value)
  if (grepl("[\x01-\x1f\x7f]", s, perl = TRUE)) {
    stop(sprintf(paste("lexsync: %s contains control characters, and it is written into",
                       "the generated experiment scripts: %s"), field, s), call. = FALSE)
  }
  if (nchar(s) > max_len) {
    stop(sprintf("lexsync: %s exceeds %d characters.", field, max_len), call. = FALSE)
  }
  if (grepl(.UNSAFE_META, s, perl = TRUE)) {
    bad <- regmatches(s, regexpr(.UNSAFE_META, s, perl = TRUE))
    stop(sprintf(paste("lexsync: %s contains '%s', which cannot be written safely into",
                       "the generated PsychoPy, OpenSesame and jsPsych files, because it",
                       "would end a string literal or open a tag there. Use letters,",
                       "digits, spaces and -_.() in a design's name, language and font.",
                       "Offending value: %s"), field, bad, s), call. = FALSE)
  }
  s
}

#' Validate a parallel-port address, which is written into the script unquoted
#'
#' @param value A value coerced to a single string.
#' @param field Field name, for error messages.
#' @return The value as a plain string.
#' @keywords internal
clean_port <- function(value, field = "triggers.parallel_address") {
  s <- as.character(value)
  if (!grepl(.PORT_SHAPE, s, perl = TRUE)) {
    stop(sprintf(paste("lexsync: %s must be a port address such as 0x0378 or 888, not",
                       "'%s'. It is written into the generated experiment as a bare",
                       "number."), field, s), call. = FALSE)
  }
  s
}

#' Validate one response key, which is written into the generated experiments
#'
#' OpenSesame takes the keys as `set allowed_responses "a;b"` on one line of a
#' line-oriented format, so a key containing a quote closed the string and a newline
#' ended the line, and the rest of the value became new top-level items in the
#' experiment, including an inline_script whose body runs.
#'
#' @param value A value coerced to a single string.
#' @param field Field name, for error messages.
#' @return The value as a plain string.
#' @keywords internal
clean_key <- function(value, field = "an event's `keys`") {
  s <- as.character(value)
  if (!grepl(.KEY_SHAPE, s, perl = TRUE)) {
    stop(sprintf(paste("lexsync: %s must be a key name such as 'f', 'space' or 'left',",
                       "not '%s'. Keys are written into the generated experiments as an",
                       "allowed-response list."), field, s), call. = FALSE)
  }
  s
}

#' Validate a loop-table column name, which is written into generated code
#'
#' @param value A value coerced to a single string.
#' @param field Field name, for error messages.
#' @return The value as a plain string.
#' @keywords internal
clean_column <- function(value, field = "column") {
  s <- as.character(value)
  if (!grepl(.COLUMN_SHAPE, s, perl = TRUE)) {
    stop(sprintf(paste("lexsync: %s must be a plain column name (letters, digits and",
                       "underscore, not starting with a digit), not '%s'. It is written",
                       "into the generated experiment as a variable reference."),
                 field, s), call. = FALSE)
  }
  s
}
