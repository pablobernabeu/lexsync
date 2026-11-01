# querying.R -- load lexica, validate the column contract and compute the
# lexical dimensions on which stimuli are matched. Written in base R to keep the
# package's dependency surface small.

#' Validate a lexicon against the schema column contract
#'
#' @param df A candidate lexicon data frame.
#' @param schema The parsed schema, such as
#'   `yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))`.
#' @return `TRUE`, invisibly; stops with an informative error otherwise.
#' @keywords internal
validate_lexicon <- function(df, schema) {
  required <- unlist(schema[["lexicon_schema"]][["required"]], use.names = FALSE)
  missing <- setdiff(required, names(df))
  if (length(missing)) {
    stop(sprintf("lexsync: lexicon is missing required column(s): %s",
                 paste(sprintf("'%s'", missing), collapse = ", ")), call. = FALSE)
  }
  invisible(TRUE)
}

#' Lower-case a character vector under the Unicode default case mapping
#'
#' Base R's `tolower()` hands case mapping to the C library, so it is both
#' locale- and platform-dependent (see `?chartr`): under a C or 8-bit locale it
#' leaves accented capitals uncased, and even under a UTF-8 locale it applies
#' only the simple mappings, rendering Greek final sigma as U+03C3 and dropping
#' the dot of U+0130. Python's `str.lower()` always applies the Unicode default
#' *full* mapping, giving U+03C2 and i + U+0307 respectively. `word` is the
#' canonical key behind every byte-order tie-break, so the engines must fold
#' case identically; pinning ICU to the root locale ("und") reproduces Python's
#' mapping exactly and removes the ambient locale from the result.
#'
#' @param x A character vector, or a vector coercible to one.
#' @return A character vector, lower-cased; `NA` is preserved.
#' @keywords internal
.lower_invariant <- function(x) {
  stringi::stri_trans_tolower(as.character(x), locale = "und")
}

# Python's `str.strip()` removes every code point whose `str.isspace()` is true:
# the Unicode White_Space property plus the C0 information separators
# U+001C-U+001F, and nothing else (U+200B, being a format character, stays).
# ICU's `\p{WHITE_SPACE}` is that set less the four separators, so naming them
# alongside it reproduces Python's set exactly.
.WHITESPACE <- "[^\\p{WHITE_SPACE}\\x{1c}-\\x{1f}]"

#' Strip leading and trailing whitespace under the Unicode definition
#'
#' Base R's `trimws()` removes only space, tab, carriage return and line feed,
#' leaving a no-break space, a form feed or an ideographic space in place, where
#' Python's `str.strip()` removes all of them. `word` is the canonical key
#' behind every byte-order tie-break, so a lexicon padded with any of those
#' characters would otherwise key, sort and number differently in the two
#' engines. As with [.lower_invariant()], the fix is to pin R to Python's
#' Unicode semantics.
#'
#' @param x A character vector, or a vector coercible to one.
#' @return A character vector, trimmed; `NA` is preserved.
#' @keywords internal
.trim_invariant <- function(x) {
  stringi::stri_trim_both(as.character(x), pattern = .WHITESPACE)
}

#' Normalise text keys to Unicode Normalization Form C
#'
#' A precomposed letter such as U+00F3 and the base letter followed by a combining
#' accent are canonically equivalent, but they compare unequal and differ in
#' length. Unnormalised, the two spellings of one word would be two candidates,
#' which the matcher could place in opposite conditions of one matched set, and a
#' norm or member join would miss whichever spelling the lexicon did not use.
#' Applied after [.trim_invariant()] and [.lower_invariant()], because case mapping
#' does not guarantee normalised output. ICU (through stringi) and Python's `unicodedata`
#' agree on every character assigned in both engines' Unicode versions. Mirrors
#' `_nfc` in python_workflow/src/lexsync/querying.py.
#'
#' @param x A character vector, or a vector coercible to one.
#' @return A character vector in NFC; `NA` is preserved.
#' @keywords internal
.nfc <- function(x) {
  stringi::stri_trans_nfc(as.character(x))
}

# Normalise text keys and say what normalising did: the NFC values, the number of
# values it changed and the number of distinct values it merged into another, missing
# values counting for neither. Mirrors _nfc_count in querying.py.
.nfc_count <- function(x) {
  x <- as.character(x)
  y <- .nfc(x)
  ok <- !is.na(x)
  list(value = y,
       changed = sum(x[ok] != y[ok]),
       collapsed = length(unique(x[ok])) - length(unique(y[ok])))
}

# The `input_normalisation` record, or NULL when normalising changed nothing. NULL
# keeps the record off every frame and datasheet whose input was already NFC, which
# is every shipped one. Mirrors _nfc_record in querying.py.
.nfc_record <- function(changed, collapsed) {
  if (!changed && !collapsed) return(NULL)
  list(changed = as.integer(changed), collapsed = as.integer(collapsed))
}

# The syllable estimate counts maximal runs of Latin vowel letters. A word is first
# decomposed (NFD) and stripped of its combining marks, so every accented vowel counts
# as its base letter. That covers the Latin-1 vowels, those of Latin Extended-A and -B
# and the Vietnamese vowels of Latin Extended Additional. Four vowel letters do not
# decompose and are named: ae (U+00E6), o with stroke (U+00F8), dotless i (U+0131)
# and oe (U+0153).
#
# The estimate is defined only for words written wholly in Latin script. That is
# taken as four ranges of code points: U+0001-U+024F (ASCII to Latin Extended-B),
# U+02B0-U+036F (spacing modifier letters and combining marks), U+1E00-U+1EFF (Latin
# Extended Additional) and U+2000-U+206F (general punctuation, such as a typographic
# apostrophe). Any other code point makes it NA, so a Chinese, Russian or Greek word
# has no estimate rather than 0 syllables, which would report perfect balance on
# n_syllables. Testing code-point ranges keeps the result independent of the
# engines' Unicode tables, and Unicode's stability policy fixes a character's
# canonical decomposition once it is encoded.
#
# The patterns name the same code points as _SYLLABLE_SCRIPT, _SYLLABLE_MARKS and
# _SYLLABLE_VOWELS in python_workflow/src/lexsync/querying.py, escape for escape
# (\x{XXXX} here, which ICU reads through stringi, \uXXXX there), and the escapes keep
# the source ASCII for CRAN. The syllable_cases list in test-dimensions.R and its
# Python twin pin the counts. .SYLLABLE_VOWELS also serves the subsyllabic
# segmentation in generation.R.
.SYLLABLE_SCRIPT <- paste0("^[\\x{0001}-\\x{024f}\\x{02b0}-\\x{036f}",
                           "\\x{1e00}-\\x{1eff}\\x{2000}-\\x{206f}]*$")
.SYLLABLE_MARKS <- "[\\x{0300}-\\x{036f}]"
.SYLLABLE_VOWELS <- "[aeiouy\\x{00e6}\\x{00f8}\\x{0131}\\x{0153}]+"

#' Orthographic syllable estimate: the number of maximal vowel runs
#'
#' Counts the maximal runs of Latin vowel letters after decomposing the word and
#' setting its diacritics aside, so a vowel counts whatever its accent. The vowels
#' of Polish, Czech, Hungarian, Romanian, Turkish, Danish, Norwegian and Vietnamese
#' count as those of English, Spanish, French and German do. Hiatus (`idea` counts
#' 2) and syllabic consonants such as the Czech l in `vlk` and r in `krk` stay
#' undercounted.
#'
#' @param word Character vector of word forms.
#' @return Integer vector: the estimated syllable count of each word, or `NA` for a
#'   missing word and for a word holding a character outside the Latin script
#'   (Chinese, Cyrillic or Greek, for example), where the estimate is undefined.
#' @examples
#' count_syllables(c("cat", "table", "beautiful"))
#' @export
count_syllables <- function(word) {
  w <- stringi::stri_trans_nfd(.lower_invariant(word))
  latin <- stringi::stri_detect_regex(w, .SYLLABLE_SCRIPT)
  n <- stringi::stri_count_regex(stringi::stri_replace_all_regex(w, .SYLLABLE_MARKS, ""),
                                 .SYLLABLE_VOWELS)
  n <- as.integer(n)
  n[is.na(latin) | !latin] <- NA_integer_
  n
}

#' Refuse a lexicon column that the shared CSV rule did not read as numbers
#'
#' A value such as "1,000" leaves the whole column text under that rule. `as.numeric()`
#' would then turn it into `NA` with a warning, and pandas' float conversion would fail
#' in the Python engine, so both engines refuse the column here, naming the first value
#' that is not a plain decimal number. Mirrors `_require_numbers` in
#' python_workflow/src/lexsync/querying.py.
#'
#' @param x The column.
#' @param name Its name, for the message.
#' @return `NULL`, invisibly, or an error.
#' @keywords internal
.require_numbers <- function(x, name) {
  if (is.numeric(x)) return(invisible(NULL))
  v <- x[!is.na(x)]
  bad <- if (is.logical(v)) ifelse(v, "TRUE", "FALSE") else
    v[!grepl(.NUMERIC_CELL, v, perl = TRUE)]
  stop(sprintf(paste("lexsync: lexicon column '%s' must hold plain decimal numbers, but",
                     "it holds '%s'."), name, bad[1]), call. = FALSE)
}

# Refuses Zipf values outside 0 to 9, naming the likely cause. A Zipf value is log10 of
# a frequency per million plus 3 (van Heuven et al., 2014), so 9 is a word making up
# the whole corpus and 0 one in a thousand million words. A larger value is almost
# always a rate per million saved under the wrong name, which the frequency filters and
# the matcher would otherwise read on the wrong scale. A log count such as SUBTLEX-US's
# Lg10WF (at most 6.33) lies inside the range, so this check cannot catch it. Mirrors
# _check_zipf_range in python_workflow/src/lexsync/querying.py.
.check_zipf_range <- function(values) {
  v <- as.numeric(values)
  v <- v[!is.na(v)]
  if (!length(v)) return(invisible(NULL))
  if (max(v) > 9) {
    stop(sprintf(paste("lexsync: freq_zipf values reach %s, which looks like frequencies per",
                       "million; convert with Zipf = log10(per million) + 3 or use",
                       "normalise_lexicon()."), .fmt_g(max(v))), call. = FALSE)
  }
  if (min(v) < 0) {
    stop(sprintf(paste("lexsync: freq_zipf values fall to %s, below 0, where no Zipf value",
                       "lies; check which of the source's columns was saved as freq_zipf."),
                 .fmt_g(min(v))), call. = FALSE)
  }
  invisible(NULL)
}

# How near a rounding boundary a scaled Zipf value may lie before the two engines'
# log10 could round it apart. The engines' log and exp were measured to differ by one
# unit in the last place (see hash_unit in io_utils.R). One unit in the last place of a
# Zipf value times 1000 is under 2e-12, so 1e-9 is a wide margin. Mirrors
# _ZIPF_BOUNDARY in python_workflow/src/lexsync/querying.py.
.ZIPF_BOUNDARY <- 1e-9

# Zipf = log10(per million) + 3, rounded to three places by the shared rounder, with
# the number of values that lay within 1e-9 of a rounding boundary once scaled by 1000.
# log10 is the one operation here that IEEE-754 does not require to be correctly
# rounded, and R and Python call different implementations of it. A value that close to
# a boundary could therefore round one way in one engine and the other way in the other.
# Every other step is a correctly rounded operation. The count is expected to be 0. Mirrors
# _zipf_from_permillion in python_workflow/src/lexsync/querying.py.
.zipf_from_permillion <- function(pm) {
  z <- log10(as.numeric(pm)) + 3
  y <- z * 1000
  list(zipf = .round_dp(z, 3),
       near_boundary = sum(abs(abs(y - trunc(y)) - 0.5) < .ZIPF_BOUNDARY))
}

# The rounding-boundary record for a frame carrying freq_permillion, or NULL:
# list(n_values, near_boundary), how many positive rates per million the frame holds
# and how many of them put Zipf within 1e-9 of a three-place rounding boundary.
# normalise_lexicon() writes the column whenever it derives Zipf from it, so
# run_pipeline() records this for the lexicon a run reads. NULL for a frame without the
# column, which is every lexicon lexsync ships. Mirrors _zipf_derivation in
# python_workflow/src/lexsync/querying.py.
.zipf_derivation <- function(frame) {
  pm <- frame[["freq_permillion"]]
  if (is.null(pm) || !is.numeric(pm)) return(NULL)
  pm <- pm[is.finite(pm) & pm > 0]
  list(n_values = length(pm), near_boundary = .zipf_from_permillion(pm)$near_boundary)
}

#' Load a lexicon from a CSV file
#'
#' Reads a derived lexicon, validates the column contract, lower-cases the
#' orthographic form and normalises it to Unicode NFC, removes duplicates (keeping
#' the first row in file order) and attaches a stable integer `id` plus
#' the inexpensive dimensions `length` and `frequency`. The orthographic
#' neighbourhood dimensions are added later, on the experimental pool, by
#' [add_neighbourhood()], because they are quadratic in the size of the
#' reference set.
#'
#' A `freq_zipf` value outside 0 to 9 is refused: it is almost always a frequency per
#' million in the wrong column (convert it with [normalise_lexicon()]). A log count
#' such as SUBTLEX-US's `Lg10WF`, log10(count + 1) and at most 6.33, passes the check
#' and must still be converted, since it reads about 1.3 below Zipf.
#'
#' @param path Path to a derived lexicon CSV.
#' @param schema The parsed schema, such as
#'   `yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))`. Its
#'   `dimensions$frequency$column` names the frequency column.
#' @param language Optional language label to record in a `language` column.
#' @return A data frame with at least `word`, `length`, `n_syllables`,
#'   `frequency` and `id`, plus the frequency column the schema names (by default
#'   `freq_zipf`) and every other column the file carried. Rows are in byte order
#'   of `word` and `id` numbers them from 1. When normalisation changed or merged
#'   any word, the attribute `input_normalisation` holds `list(changed, collapsed)`:
#'   the words it rewrote and the duplicate rows it removed.
#' @examples
#' # Both inputs are bundled with the package, so this runs offline and touches
#' # nothing outside the installation.
#' schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
#' lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"),
#'                     schema)
#' head(lex[, c("word", "frequency", "length", "n_syllables")])
#' @export
load_lexicon <- function(path, schema, language = NULL) {
  df <- as.data.frame(read_csv_utf8(path), stringsAsFactors = FALSE)
  validate_lexicon(df, schema)
  freq_col <- schema[["dimensions"]][["frequency"]][["column"]] %||% "freq_zipf"
  .require_numbers(df[[freq_col]], freq_col)
  df$word <- .lower_invariant(.trim_invariant(df$word))
  keep <- !is.na(df$word) & nzchar(df$word) & !is.na(df[[freq_col]])
  df <- df[keep, , drop = FALSE]
  # The rows the lexicon keeps, before de-duplication, as the Python engine checks them.
  if (is.numeric(df[["freq_zipf"]])) .check_zipf_range(df[["freq_zipf"]])
  # NFC before de-duplication, so the two spellings of a word are one word and the
  # first row in file order is the one kept.
  nf <- .nfc_count(df$word)
  df$word <- nf$value
  df <- df[!duplicated(df$word), , drop = FALSE]
  # Every downstream step reads at least one row, and `df$language <- language`
  # below fails first with base R's "replacement has 1 row, data has 0", which
  # names neither the lexicon nor the cause. Say what is wrong while the path is
  # still in scope; the Python engine raises the same message here.
  if (!nrow(df)) {
    stop(sprintf(paste("lexsync: lexicon '%s' has no usable rows: it is empty,",
                       "or every row is missing 'word' or '%s'."),
                 path, freq_col), call. = FALSE)
  }
  # Byte-order ('radix') sort so the lexicon order is locale-independent and
  # therefore identical to the Python engine (which sorts by UTF-8 bytes).
  df <- df[order(df$word, method = "radix"), , drop = FALSE]
  df$id <- seq_len(nrow(df))
  df$length <- nchar(df$word)
  df$n_syllables <- count_syllables(df$word)
  df$frequency <- as.numeric(df[[freq_col]])
  if (!is.null(language)) df$language <- language
  rownames(df) <- NULL
  # Read by run_pipeline() for the run log and the datasheet.
  attr(df, "input_normalisation") <- .nfc_record(nf$changed, nf$collapsed)
  df
}

#' Compute orthographic-neighbourhood dimensions (Coltheart's N and OLD20)
#'
#' `n_density` is Coltheart's N: the number of reference words of the same
#' length differing by a single letter substitution (Hamming distance 1).
#' `old20` is the mean Levenshtein distance to the `n_old` (default 20) nearest other
#' reference words (Yarkoni et al., 2008). Both are computed against `reference`, which
#' should be a large word list (typically the whole lexicon), not just the
#' experimental pool.
#'
#' @references Yarkoni, T., Balota, D., & Yap, M. (2008). Moving beyond Coltheart's N:
#'   A new measure of orthographic similarity. *Psychonomic Bulletin & Review, 15*(5),
#'   971-979. \doi{10.3758/PBR.15.5.971}
#'
#' @param df A data frame with a `word` column.
#' @param reference A character vector of reference words, `df$word` by default.
#'   Duplicates count once.
#' @param n_old Neighbourhood size for OLD (default 20). The column is named `old20`
#'   whatever its value.
#' @return `df` with added integer `n_density` and numeric `old20` columns. A word with
#'   fewer than `n_old` other words in the reference has the mean over those it has, and
#'   `old20` is `NA` for a word with none.
#' @importFrom stringdist stringdist
#' @export
add_neighbourhood <- function(df, reference = df$word, n_old = 20L) {
  words <- as.character(df$word)
  reference <- unique(as.character(reference))
  ref_nchar <- nchar(reference)
  n_dens <- integer(length(words))
  old <- numeric(length(words))
  for (i in seq_along(words)) {
    w <- words[i]
    same_len <- reference[ref_nchar == nchar(w)]
    if (length(same_len)) {
      hd <- stringdist::stringdist(w, same_len, method = "hamming")
      n_dens[i] <- sum(hd == 1, na.rm = TRUE)
    }
    ld <- stringdist::stringdist(w, reference, method = "lv")
    ld <- ld[is.finite(ld) & ld > 0]
    if (length(ld)) {
      k <- min(n_old, length(ld))
      old[i] <- mean(sort(ld, partial = seq_len(k))[seq_len(k)])
    } else {
      old[i] <- NA_real_
    }
  }
  df$n_density <- n_dens
  df$old20 <- old
  df
}

# Both engines return identical values, and the reasons are worth stating because
# they are the constraints on any future relational dimension. The core is an
# integer edit distance, and stringdist(method = "lv") and rapidfuzz's
# Levenshtein.distance agree exactly, including on decomposed Unicode and CJK,
# which is the same cross-library agreement add_neighbourhood() already stakes
# old20 on. Length is counted in code points, nchar()'s default and Python's len(),
# never in bytes. The arithmetic uses only - and /, which IEEE-754 mandates be
# correctly rounded, and the result is rounded to nine decimal places, the constant
# used everywhere else in the package. A degenerate pair of two empty forms returns 0
# rather than 0/0, because a NaN would be sorted and compared and would then drop the
# row from one engine's control window but not the other's.
#' Orthographic overlap between the two members of each pair
#'
#' Adds two columns. `pair.lev` is the Levenshtein distance between the pair's two
#' orthographic forms, and `pair.overlap` is `1 - lev / max(nchar)`, the proportion
#' of the longer form the two share. Overlap is the standard confound control in a
#' priming design: a related pair that also shares letters confounds semantic
#' relatedness with orthographic similarity.
#'
#' The forms are trimmed, lower-cased and normalised to Unicode NFC before they are
#' compared, as [load_lexicon()] does to a lexicon's words, so `Dog` and `dog` are at
#' distance 0. Length is counted in code points. `pair.overlap` is rounded to nine
#' decimal places, and a pair of two empty forms gives 0. Both engines return
#' identical values.
#'
#' @param df A pair table.
#' @param prime,target Column names holding the two orthographic forms.
#' @return `df` with `pair.lev` and `pair.overlap` added.
#' @importFrom stringdist stringdist
#' @export
add_pair_overlap <- function(df, prime = "prime", target = "target") {
  for (col in c(prime, target)) {
    if (!(col %in% names(df))) {
      stop(sprintf("lexsync: add_pair_overlap needs column '%s'.", col), call. = FALSE)
    }
  }
  a <- .nfc(.lower_invariant(.trim_invariant(as.character(df[[prime]]))))
  b <- .nfc(.lower_invariant(.trim_invariant(as.character(df[[target]]))))
  lev <- as.integer(stringdist::stringdist(a, b, method = "lv"))
  den <- pmax(nchar(a), nchar(b))
  df[["pair.lev"]] <- lev
  df[["pair.overlap"]] <- ifelse(den == 0L, 0, .round_dp(1 - lev / den, 9))
  df
}

#' Mean bigram probability (type-based, non-positional), a phonotactic-probability proxy
#'
#' For each word, the mean over its adjacent letter bigrams of the corpus bigram
#' probability (count divided by the total bigram count). Computed from integer
#' counts and rounded, so it is identical in the R and Python engines.
#'
#' @param df A data frame with a `word` column.
#' @param reference A character vector of reference words (defaults to `df$word`).
#' @return `df` with an added numeric `bigram_freq` column.
#' @export
add_bigram_frequency <- function(df, reference = NULL) {
  ref <- as.character(if (is.null(reference)) df$word else reference)
  pairs <- unlist(lapply(ref, function(w) {
    n <- nchar(w)
    if (n < 2L) character(0) else substring(w, 1:(n - 1L), 2:n)
  }), use.names = FALSE)
  tab <- table(pairs)
  counts <- as.integer(tab); names(counts) <- names(tab)
  total <- max(1L, sum(counts))
  bf <- function(w) {
    n <- nchar(w)
    if (n < 2L) return(0)
    bgs <- substring(w, 1:(n - 1L), 2:n)
    v <- counts[bgs]; v[is.na(v)] <- 0L
    .round_dp(sum(v) / length(bgs) / total, 9)
  }
  df$bigram_freq <- vapply(as.character(df$word), bf, numeric(1), USE.NAMES = FALSE)
  df
}

# The join key, normalised identically on both sides of the join and in both
# engines: trimmed and case-folded under Python's Unicode semantics (see
# .trim_invariant and .lower_invariant), then put in NFC (.nfc), which is also
# exactly what load_lexicon does to `word`. A missing value stays missing, so it
# never joins: R's merge() pairs NA with NA, whereas a pandas NaN never compares
# equal to itself.
.norm_key <- function(x) .nfc(.lower_invariant(.trim_invariant(x)))

#' Left-join a norm table (e.g. concreteness, age of acquisition, valence)
#'
#' The connector for semantic dimensions: the norm data themselves are fetched
#' separately (licensing varies), then merged here so the matcher can equate on
#' them. The join is deterministic and identical across engines.
#'
#' The result is the lexicon itself with the norm columns appended, and the key is
#' looked up positionally rather than through `merge()`. That is what makes the two
#' engines agree by construction, with nothing to repair afterwards, because `merge()`
#' and `pandas.merge` were measured to diverge in three ways, each of them silent:
#' R hoists the `by` column to position 1 while pandas keeps the left frame's
#' order, so the column order differed whenever `on` was not already first; R
#' disambiguates a colliding column name with `.x`/`.y` and pandas with `_x`/`_y`,
#' and either way a dimension the design matches on disappears under a name
#' nothing looks for; and `merge(sort = FALSE)` leaves the row order unspecified, so
#' x's order is not carried through. A positional lookup has none of those degrees of
#' freedom: the output is the input plus columns, in both engines. A norm column
#' whose name the lexicon already has is refused.
#'
#' The key is trimmed, case-folded and normalised to NFC on *both* sides, so a
#' lexicon holding `Dog` matches a norm row for `dog`. The lexicon's own spelling is
#' preserved rather than folded in place: `word` is the byte-order tie-break behind
#' every selection, so the join must not rewrite it. A missing key never matches, and
#' when two rows of the norm table share a key once it is normalised, the first of
#' them is used.
#'
#' @param lexicon A lexicon data frame.
#' @param norms A data frame, or the path to a UTF-8 CSV, holding the `on` column and
#'   the norm columns.
#' @param on The join column (default "word").
#' @param columns Optional norm columns to keep.
#' @return `lexicon` with the norm columns appended, in the lexicon's own row and
#'   column order. Rows with no matching norm get `NA`.
#' @export
merge_norms <- function(lexicon, norms, on = "word", columns = NULL) {
  n <- if (is.data.frame(norms)) norms else as.data.frame(read_csv_utf8(norms), stringsAsFactors = FALSE)
  if (!(on %in% names(lexicon)))
    stop(sprintf("lexsync: merge_norms needs join column '%s' on the lexicon.", on),
         call. = FALSE)
  if (!(on %in% names(n)))
    stop(sprintf("lexsync: merge_norms needs join column '%s' on the norm table.", on),
         call. = FALSE)
  cols <- if (!is.null(columns)) unlist(columns, use.names = FALSE) else setdiff(names(n), on)
  absent <- setdiff(cols, names(n))
  if (length(absent))
    stop(sprintf("lexsync: the norm table has no column(s): %s.",
                 paste(sprintf("'%s'", absent), collapse = ", ")), call. = FALSE)
  # Silently renaming the clash, as both merges do, is the worst outcome available:
  # a design matching on `frequency` would find neither `frequency.x` nor
  # `frequency_x` and would fail far from the cause, or match on the norm table's
  # column believing it was the lexicon's.
  clash <- intersect(cols, names(lexicon))
  if (length(clash))
    stop(sprintf(paste("lexsync: norm column(s) %s already exist on the lexicon.",
                       "Rename them in the norm table, or name the ones you want",
                       "in `columns`."),
                 paste(sprintf("'%s'", clash), collapse = ", ")), call. = FALSE)
  key <- .norm_key(n[[on]])
  keep <- !is.na(key) & !duplicated(key)
  idx <- match(.norm_key(lexicon[[on]]), key[keep])
  add <- n[keep, cols, drop = FALSE]
  out <- lexicon
  # Indexing by NA yields NA of the column's own type, which is a left join.
  for (cl in cols) out[[cl]] <- add[[cl]][idx]
  rownames(out) <- NULL
  out
}

# ---- The design's `norms:` block --------------------------------------------
# A design may name norm tables to be joined onto the lexicon before the pool is
# built, so `pool_filters`, `match_on` and a continuous `predictor` can all refer to
# a semantic dimension lexsync does not compute:
#
#   norms:
#     - path: norms/en_concreteness.csv
#       join_on: word             # optional join key, default 'word'
#       columns: [concreteness]   # optional; default every column but the key
#
# The join itself is merge_norms(). What this adds is provenance, and that is not a
# nicety: a norm table can carry the very variable a design manipulates, so a
# datasheet that did not name the file and its checksum would describe a selection
# over columns whose origin is recorded nowhere. The loader hands the records back
# for build_datasheet() to write down.
#
# Coverage is recorded per column rather than per file, because one table can cover a
# dimension well and another badly, and an unmatched row becomes an NA that takes the
# word out of any selection that filters, matches or spans on the column.

# YAML gives a sequence of mappings as an unnamed list of named lists, and a single
# bare mapping as one named list. Writing one entry as a bare mapping is the obvious
# thing to do, so accept both shapes. Any named list is one entry, as any dict is in
# _norm_specs in querying.py. Testing for a `path` key instead split a bare mapping
# without one into its values, so a misspelt key went unreported here while the Python
# engine named it, and a mapping of named entries was joined here and refused there.
#' @keywords internal
.norm_specs <- function(design) {
  specs <- design[["norms"]] %||% list()
  # The length test keeps `norms: {}`, an empty named list, as no entries at all.
  if (length(specs) && .is_mapping(specs)) specs <- list(specs)
  specs
}

# The keys a norms entry may hold. `on` is the join key's earlier name, still read when
# it is quoted, and TRUE is the name YAML 1.1 gives a bare `on`. Must list the same
# names as _NORMS_KEYS in querying.py.
.NORMS_KEYS <- c("path", "join_on", "on", "TRUE", "columns")

.NORMS_ON_NOTE <- paste("lexsync: read `on:` in a norms entry as the join key; YAML reads a",
                        "bare `on` as true, so write `join_on:`.")

# The join key of one norms entry, once the entry's keys are checked. YAML 1.1 reads a
# bare `on` as the boolean true in both engines, so the documented `on: lemma` reached
# the join as a key named TRUE, and every join silently used `word`. `join_on` is read
# first, then a quoted 'on', then a key named TRUE, which comes back with a note for
# the run log. Any other key is refused, since a misspelt `join_on` would fall back to
# `word` just as silently. Returns list(on, note), the note NULL unless the bare `on`
# gave the key. Must stay identical to _norm_join_key in querying.py.
#' @keywords internal
.norm_join_key <- function(spec) {
  unknown <- setdiff(names(spec), .NORMS_KEYS)
  if (length(unknown)) {
    stop(sprintf(paste("lexsync: unknown key '%s' in a norms entry; known keys: path,",
                       "join_on, columns."), unknown[1]), call. = FALSE)
  }
  for (key in c("join_on", "on")) {
    if (!is.null(spec[[key]])) return(list(on = spec[[key]], note = NULL))
  }
  if (!is.null(spec[["TRUE"]])) return(list(on = spec[["TRUE"]], note = .NORMS_ON_NOTE))
  list(on = "word", note = NULL)
}

# `normalisation` in the result counts the norm-table keys that NFC changed and the
# duplicate keys it created, which the join then dropped, summed over the tables
# (see .nfc_count). `notes` holds a note for each entry whose join key was a bare
# `on`, for the run log. Mirrors apply_norms in querying.py.
#' @keywords internal
.apply_norms <- function(lex, design) {
  records <- list()
  notes <- character(0)
  changed <- collapsed <- 0L
  for (spec in .norm_specs(design)) {
    # A bare word or a list here would make the key check and the reads below fail
    # with R's own error, far from the cause.
    if (!.is_mapping(spec))
      stop("lexsync: every entry under `norms:` needs a `path`.", call. = FALSE)
    key <- .norm_join_key(spec)
    path <- spec[["path"]]
    if (is.null(path))
      stop("lexsync: every entry under `norms:` needs a `path`.", call. = FALSE)
    parts <- strsplit(gsub("\\\\", "/", path), "/", fixed = TRUE)[[1]]
    if (".." %in% parts)
      stop("lexsync: norms path must not contain '..'.", call. = FALSE)
    on <- key$on
    notes <- c(notes, key$note)
    cols <- if (is.null(spec[["columns"]])) NULL else unlist(spec[["columns"]], use.names = FALSE)
    before <- names(lex)
    table <- as.data.frame(read_csv_utf8(path), stringsAsFactors = FALSE)
    lex <- merge_norms(lex, table, on = on, columns = cols)
    # merge_norms() has checked that the key column exists.
    nf <- .nfc_count(.lower_invariant(.trim_invariant(table[[on]])))
    changed <- changed + nf$changed
    collapsed <- collapsed + nf$collapsed
    added <- setdiff(names(lex), before)
    records[[length(records) + 1L]] <- list(
      path = path, sha256 = sha256_file(path), on = on,
      columns = lapply(added, function(cl)
        list(column = cl, n_matched = sum(!is.na(lex[[cl]])), n_total = nrow(lex))))
  }
  list(lexicon = lex, provenance = records,
       normalisation = list(changed = changed, collapsed = collapsed), notes = notes)
}

# ---- The design's `exclude_words` -------------------------------------------
# Words the researcher has decided against, names and offensive words among them. No
# filter on the lexicon's columns can remove them, since a range filter on a norm table
# would also drop every word the table does not cover. A design lists them, or names a
# UTF-8 file with one per line:
#
#   exclude_words: [adams, dubai, espn]
#   exclude_words: {path: config/exclude_en.txt}
#
# run_pipeline() removes them from the candidates after the norms join and before
# pool_filters. Only from the candidates: the neighbourhood reference, and a generated
# design's list of real words, keep them, since an excluded word is still a word of the
# language. The datasheet records the list with its checksum.
#
# Mirrors _read_exclude_words / _apply_exclude_words in querying.py.

# A line holding one of these is a table row, which would be kept whole as one word and
# match nothing, so the list would exclude nothing while the datasheet counted it.
.EXCLUDE_SEPARATORS <- "[\t,;]"

# The words of a design's `exclude_words`, as .exclude_words() returns it. That is a
# character vector of words, or list(path = path) naming a UTF-8 file with one word per
# line, in which blank lines and lines beginning '#' are skipped. A file that cannot be
# read, that is not UTF-8 text, or that holds a tab, comma or semicolon in a word is
# refused. A NUL byte counts as not UTF-8 text: it marks a binary file or UTF-16 text
# saved without a byte-order mark, which rawToChar() cannot read and whose words would
# match nothing. Every word is trimmed, lower-cased and put in NFC, as a lexicon's
# words are.
#
# Returns list(words, record): the distinct words in UTF-8 byte order, and the record
# the datasheet keeps, list(path, sha256, n_listed). `path` is the file's path with '/'
# separators, or "inline" for a list in the design, and `sha256` is the file's
# checksum, or that of the distinct words joined by line feeds. Read as bytes, so the
# session's locale plays no part. Mirrors _read_exclude_words in querying.py.
#' @keywords internal
.read_exclude_words <- function(spec) {
  if (.is_mapping(spec)) {
    path <- spec[["path"]]
    if (!file.exists(path) || dir.exists(path)) {
      stop(sprintf("lexsync: exclude_words names '%s', which is not a readable file.", path),
           call. = FALSE)
    }
    bytes <- readBin(path, "raw", file.info(path)$size)
    bom <- as.raw(c(0xEF, 0xBB, 0xBF))
    if (length(bytes) >= 3L && identical(bytes[1:3], bom)) bytes <- bytes[-(1:3)]
    text <- if (any(bytes == as.raw(0L))) NA_character_ else rawToChar(bytes)
    if (is.na(text) || !validUTF8(text)) {
      stop(sprintf("lexsync: the exclude_words file '%s' is not UTF-8 text.", path),
           call. = FALSE)
    }
    Encoding(text) <- "UTF-8"
    v <- .norm_key(strsplit(text, "\n", fixed = TRUE)[[1]])
    keep <- !is.na(v) & nzchar(v) & !startsWith(v, "#")
    bad <- which(keep & grepl(.EXCLUDE_SEPARATORS, v, perl = TRUE))
    if (length(bad)) {
      stop(sprintf(paste0("lexsync: line %d of the exclude_words file '%s' holds a tab, ",
                          "comma or semicolon, so the file is a table. List one word per ",
                          "line."), bad[1], path), call. = FALSE)
    }
    words <- v[keep]
    record <- list(path = gsub("\\", "/", path, fixed = TRUE), sha256 = sha256_file(path))
  } else {
    v <- .norm_key(unlist(spec, use.names = FALSE))
    words <- v[!is.na(v) & nzchar(v)]
    record <- list(path = "inline")
  }
  words <- sort(unique(as.character(words)), method = "radix")
  if (is.null(record$sha256)) {
    record$sha256 <- digest::digest(enc2utf8(paste(words, collapse = "\n")), algo = "sha256",
                                    serialize = FALSE)
  }
  record$n_listed <- length(words)
  list(words = words, record = record)
}

# `frame` without the rows whose word is one of `words`, keyed as `word` is. The rows
# keep their order and their ids, as build_pool()'s filters leave them. Mirrors
# _apply_exclude_words in querying.py.
#' @keywords internal
.apply_exclude_words <- function(frame, words) {
  out <- frame[!(frame$word %in% words), , drop = FALSE]
  rownames(out) <- NULL
  out
}

# The words a lexicon offers as the reference for the derived dimensions: every word,
# unless the lexicon carries a `reference_member` column, in which case the rows
# marked 1. A lexicon that keeps proper names or acronyms for selection can so leave
# them out of the neighbourhoods. The column must hold 0 or 1 in every row and mark
# at least one word. Mirrors _neighbourhood_reference in querying.py.
.neighbourhood_reference <- function(lex) {
  if (!("reference_member" %in% names(lex))) return(lex$word)
  flags <- lex$reference_member
  if (!(is.numeric(flags) || is.logical(flags)) || anyNA(flags) ||
      !all(flags %in% c(0, 1))) {
    stop("lexsync: lexicon column 'reference_member' must hold 0 or 1 for every word.",
         call. = FALSE)
  }
  members <- lex$word[flags == 1]
  if (!length(members)) {
    stop(paste("lexsync: lexicon column 'reference_member' marks no word as a member",
               "of the neighbourhood reference."), call. = FALSE)
  }
  members
}

#' Load a supplied candidate pool of words and give it the matcher's dimensions
#'
#' A researcher who already has a curated word list (from a previous study, a norming
#' session, a colleague) should not have to dress it up as a corpus lexicon
#' to get lexsync's matching, validation and datasheet. This reads such a list and
#' returns something the matcher accepts.
#'
#' The list needs only a `word` column. Length and the syllable estimate are derived
#' from the form. Everything else is either supplied on the list itself or looked up:
#' with `lexicon` given, the corpus dimensions (frequency above all) are joined for
#' those words, and a word the lexicon does not have is a hard error rather than an
#' `NA`, because the tolerance windows drop `NA` rows silently and the pool would
#' then be smaller than the user believes it is.
#'
#' The returned `reference` matters as much as the pool. `n_density` and `old20` are
#' properties of a word in its *language*, not among the handful of words a study
#' happens to use, so computing them against a 200-word supplied list would give
#' numbers that mean nothing. When a lexicon is given, the reference is the lexicon's
#' words; only without one does it fall back to the pool itself. A
#' `reference_member` column on whichever of the two supplies the reference keeps
#' only the rows it marks 1.
#'
#' @param path Path to a UTF-8 CSV with at least a `word` column. A path with a `..`
#'   component is refused. Give it from the working directory, or as an absolute path.
#' @param schema The parsed schema (used when a lexicon is loaded).
#' @param lexicon Optional path to a derived lexicon to draw dimensions from.
#' @param language Optional language label recorded in a `language` column.
#' @return A list with `pool` (the data frame, carrying `word`, `id`, `length`,
#'   `n_syllables` and any joined or supplied dimensions) and `reference` (the word
#'   vector the neighbourhood dimensions should be computed against). Words are
#'   trimmed, lower-cased and normalised to Unicode NFC as in [load_lexicon()], and
#'   `pool` carries the same `input_normalisation` attribute when that changed or
#'   merged any word of the pool or the lexicon.
#' @export
load_pool <- function(path, schema, lexicon = NULL, language = NULL) {
  parts <- strsplit(gsub("\\\\", "/", path), "/", fixed = TRUE)[[1]]
  if (".." %in% parts) stop("lexsync: pool path must not contain '..'.", call. = FALSE)
  df <- as.data.frame(read_csv_utf8(path), stringsAsFactors = FALSE)
  if (!("word" %in% names(df))) {
    stop(sprintf("lexsync: supplied pool '%s' is missing the required 'word' column.",
                 path), call. = FALSE)
  }
  # The same normalisation load_lexicon applies, for the same reason: `word` is the
  # canonical key behind every byte-order tie-break, so the two engines must fold and
  # trim it identically before anything is sorted or numbered by it.
  df$word <- .lower_invariant(.trim_invariant(df$word))
  df <- df[!is.na(df$word) & nzchar(df$word), , drop = FALSE]
  nf <- .nfc_count(df$word)
  df$word <- nf$value
  df <- df[!duplicated(df$word), , drop = FALSE]
  if (!nrow(df)) {
    stop(sprintf("lexsync: supplied pool '%s' has no usable rows: it is empty, or every row is missing 'word'.",
                 path), call. = FALSE)
  }
  df <- df[order(df$word, method = "radix"), , drop = FALSE]
  rownames(df) <- NULL

  reference <- if (is.null(lexicon)) .neighbourhood_reference(df) else NULL
  if (!is.null(lexicon)) {
    lex <- load_lexicon(lexicon, schema, language = language)
    # The lexicon's own normalisation is reported with the pool's, since the run read
    # both.
    lex_record <- attr(lex, "input_normalisation")
    nf$changed <- nf$changed + (lex_record$changed %||% 0L)
    nf$collapsed <- nf$collapsed + (lex_record$collapsed %||% 0L)
    reference <- .neighbourhood_reference(lex)
    # `id` is the lexicon's own row number, meaningless once the pool is a subset.
    dims <- setdiff(names(lex), c("word", "language", "source", "id"))
    clash <- intersect(dims, names(df))
    if (length(clash)) {
      stop(sprintf(paste("lexsync: supplied pool '%s' already has column(s) %s, which the",
                         "lexicon would also supply. Rename or drop them, so it is",
                         "unambiguous which values the matcher used."),
                   path, paste(sprintf("'%s'", sort(clash, method = "radix")), collapse = ", ")),
           call. = FALSE)
    }
    absent <- setdiff(df$word, lex$word)
    if (length(absent)) {
      shown <- utils::head(sort(absent, method = "radix"), 5L)
      stop(sprintf("lexsync: %d word(s) of supplied pool '%s' are absent from lexicon '%s': %s%s.",
                   length(absent), path, lexicon,
                   paste(sprintf("'%s'", shown), collapse = ", "),
                   if (length(absent) > length(shown)) ", ..." else ""), call. = FALSE)
    }
    idx <- match(df$word, lex$word)
    for (d in dims) df[[d]] <- lex[[d]][idx]
  }
  # Derived after any join, so a lexicon cannot overwrite them with its own copies.
  df$length <- nchar(df$word)
  df$n_syllables <- count_syllables(df$word)
  if (!is.null(language)) df$language <- language
  df$id <- seq_len(nrow(df))
  rownames(df) <- NULL
  attr(df, "input_normalisation") <- .nfc_record(nf$changed, nf$collapsed)
  list(pool = df, reference = reference)
}

#' Load a paradigm item table (prime-target pairs, sentences, ...)
#'
#' The table must carry an `item` identifier, a `condition` label and the
#' paradigm's presented fields. Field values are validated (no control
#' characters; bounded length) so a crafted item cannot corrupt the generated
#' loop table or scripts. Items are mapped to a deterministic integer `set` id
#' (byte order), so counterbalancing matches the corpus path and the two engines.
#' The item id, the condition and the presented fields are normalised to Unicode
#' NFC. When that changed any cell, the attribute `input_normalisation` holds
#' `list(changed, collapsed)`, with `collapsed` always 0 since no row is removed.
#'
#' @param path Path to a UTF-8 CSV item table. A path with a `..` component is
#'   refused. Give it from the working directory, or as an absolute path.
#' @param required_fields Character vector of presented fields the paradigm needs.
#' @return A data frame with `set`, `condition` and the item fields.
#' @export
load_items <- function(path, required_fields) {
  parts <- strsplit(gsub("\\\\", "/", path), "/", fixed = TRUE)[[1]]
  if (".." %in% parts) stop("lexsync: items path must not contain '..'.", call. = FALSE)
  # The item id, the condition label and the paradigm's presented fields stay text.
  # Typed by their values, a column of response keys such as TRUE and FALSE would
  # become logical, and an `item` column of numbers would lose the zero of '01'. The
  # reader trims every cell and reads a blank, all-whitespace or 'NA' cell as
  # missing, in both engines (see read_csv_utf8).
  df <- as.data.frame(read_csv_utf8(path, as_character = c("item", "condition", required_fields)),
                      stringsAsFactors = FALSE)
  needed <- c("item", "condition", required_fields)
  missing <- setdiff(needed, names(df))
  if (length(missing)) {
    stop(sprintf("lexsync: items table '%s' is missing column(s): %s.",
                 path, paste(missing, collapse = ", ")), call. = FALSE)
  }
  # Missingness is tested before any coercion or cleaning: an NA left to flow on
  # fails far from here, and the Python engine (where str() would render it as the
  # literal 'nan') refuses at this same point with this same message.
  for (col in needed) {
    if (anyNA(df[[col]])) {
      stop(sprintf(paste("lexsync: the items table has missing value(s) in column '%s';",
                         "every item, condition and presented field must be filled."),
                   col), call. = FALSE)
    }
  }
  # The item id, the condition and the presented text in NFC, as every other text key
  # is, so one item spelt two ways is one set and its text one string. A merged
  # spelling removes no row here, so only the changed cells are counted.
  changed <- 0L
  for (col in unique(needed)) {
    nf <- .nfc_count(df[[col]])
    df[[col]] <- nf$value
    changed <- changed + nf$changed
  }
  item_key <- df$item
  # A repeated item-condition pair is a slip that would silently duplicate a trial
  # in every generated list; the first repeat in file order is reported. The key is
  # length-prefixed because a bare separator could recur inside a label and collide;
  # the Python engine compares the pair as a tuple, which has no such ambiguity.
  pair_key <- paste0(nchar(item_key), ":", item_key, ":", df$condition)
  dup <- duplicated(pair_key)
  if (any(dup)) {
    i <- which(dup)[1L]
    stop(sprintf(paste("lexsync: the items table repeats item '%s' for condition '%s';",
                       "each item and condition pair may appear once."),
                 item_key[i], df$condition[i]), call. = FALSE)
  }
  for (f in intersect(required_fields, names(df))) {
    df[[f]] <- vapply(df[[f]], function(v) clean_field(v, f), character(1))
  }
  items <- sort(unique(item_key), method = "radix")
  set_map <- stats::setNames(seq_along(items), items)
  df$set <- unname(set_map[item_key])
  rownames(df) <- NULL
  attr(df, "input_normalisation") <- .nfc_record(changed, 0L)
  df
}

#' Build an experimental candidate pool by filtering a lexicon
#'
#' A filter naming a column the frame does not have is silently skipped, because the
#' same function filters lexica, supplied pools and pair tables, and those carry
#' different columns. The cost is that a misspelt key silently widens a
#' selection, so every caller that takes its filters from a design checks the names
#' against the frame first: [run_pipeline()] for `pool_filters`, [match_stimuli()]
#' for a condition's `define_by`, and the pair selector for both.
#'
#' @param lexicon A lexicon data frame.
#' @param filters A named list mapping columns to filters. A numeric vector of two
#'   values is an inclusive range, `c(min, max)`, and any other vector a set of
#'   permitted values, compared as text. To permit exactly two numbers, write them as
#'   text, as in `c("1", "3")`.
#' @return The filtered lexicon, with row names dropped. A row missing the filtered
#'   column is dropped under either kind of filter, and a range with a reversed or
#'   non-finite bound is an error rather than an empty pool.
#' @examples
#' schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
#' lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"),
#'                     schema)
#' nrow(build_pool(lex, list(length = c(4, 6), frequency = c(4, 6))))
#' @export
build_pool <- function(lexicon, filters = NULL) {
  df <- lexicon
  if (!is.null(filters)) {
    for (col in names(filters)) {
      if (!col %in% names(df)) next
      rng <- unlist(filters[[col]], use.names = FALSE)
      if (is.numeric(rng) && length(rng) == 2) {
        # YAML's .inf and .nan arrive as ordinary doubles, and either one, like a
        # reversed range, silently empties the pool row by row. Non-finite
        # first: a NaN bound would make the reversal test meaningless. Equal
        # bounds stay legal (the zh design uses [2, 2]).
        if (any(!is.finite(rng))) {
          stop(sprintf(paste("lexsync: filter '%s' has a non-finite bound;",
                             "ranges need finite numbers."), col), call. = FALSE)
        }
        if (rng[1] > rng[2]) {
          stop(sprintf("lexsync: filter '%s' has a reversed range; give it as [low, high].",
                       col), call. = FALSE)
        }
        df <- df[!is.na(df[[col]]) & df[[col]] >= rng[1] & df[[col]] <= rng[2], , drop = FALSE]
      } else {
        df <- df[!is.na(df[[col]]) & as.character(df[[col]]) %in% as.character(rng), , drop = FALSE]
      }
    }
  }
  rownames(df) <- NULL
  df
}
