# querying.R -- load lexica, validate the column contract and compute the
# lexical dimensions on which stimuli are matched. Written in base R to keep the
# package's dependency surface small.

#' Validate a lexicon against the schema column contract
#'
#' @param df A candidate lexicon data frame.
#' @param schema The parsed schema (see `config/schema.yaml`).
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
#' length. Unnormalised, the two spellings of one word were two candidates, which
#' the matcher could place in opposite conditions of one matched set, and a norm
#' or member join missed whichever spelling the lexicon did not use. Applied after
#' [.trim_invariant()] and [.lower_invariant()], because case mapping does not
#' guarantee normalised output. ICU (through stringi) and Python's `unicodedata`
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

# Maximal runs of (possibly accented) Latin vowels approximate syllable nuclei.
# Accented code points are built with intToUtf8 so the R source stays ASCII (CRAN).
.VOWELS <- paste0("[aeiouy", intToUtf8(c(
  0xe0, 0xe1, 0xe2, 0xe3, 0xe4, 0xe5, 0xe8, 0xe9, 0xea, 0xeb, 0xec, 0xed, 0xee,
  0xef, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf8, 0xf9, 0xfa, 0xfb, 0xfc, 0xfd, 0xff)),
  "]+")                          # y with acute/diaeresis

#' Orthographic syllable estimate: the number of maximal vowel runs
#'
#' @param word Character vector of word forms.
#' @return Integer vector: the estimated syllable count of each word.
#' @examples
#' count_syllables(c("cat", "table", "beautiful"))
#' @export
count_syllables <- function(word) {
  word <- .lower_invariant(word)
  vapply(word, function(w) {
    m <- gregexpr(.VOWELS, w, perl = TRUE)[[1]]
    if (length(m) == 1L && m[1] == -1L) 0L else length(m)
  }, integer(1), USE.NAMES = FALSE)
}

#' Refuse a lexicon column that the shared CSV rule did not read as numbers
#'
#' A value such as "1,000" leaves the whole column text under that rule. `as.numeric()`
#' would then turn it into `NA` with a warning, while the Python engine failed inside
#' pandas' float conversion, so the refusal is spelled out, naming the first value that
#' is not a plain decimal number. Mirrors `_require_numbers` in
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
#' @param path Path to a derived lexicon CSV.
#' @param schema The parsed schema (see `config/schema.yaml`).
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
#' `old20` is the mean Levenshtein distance to the 20 nearest reference words
#' (Yarkoni et al., 2008). Both are computed against `reference`, which
#' should be a large word list (typically the whole lexicon), not just the
#' experimental pool.
#'
#' @param df A data frame with a `word` column.
#' @param reference A character vector of reference words.
#' @param n_old Neighbourhood size for OLD (default 20).
#' @return `df` with added integer `n_density` and numeric `old20` columns.
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

#' Orthographic overlap between the two members of each pair
#'
#' Adds two columns. `pair.lev` is the Levenshtein distance between the pair's two
#' orthographic forms, and `pair.overlap` is `1 - lev / max(nchar)`, the proportion
#' of the longer form the two share. Overlap is the standard confound control in a
#' priming design: a related pair that also shares letters confounds semantic
#' relatedness with orthographic similarity.
#'
#' Both engines return identical values, and the reasons are worth stating because
#' they are the constraints on any future relational dimension. The core is an
#' integer edit distance, and `stringdist(method = "lv")` and rapidfuzz's
#' `Levenshtein.distance` agree exactly, including on decomposed Unicode and CJK,
#' which is the same cross-library agreement `add_neighbourhood()` already stakes
#' `old20` on. Length is counted in code points, `nchar()`'s default and Python's
#' `len()`, never in bytes. The arithmetic uses only `-` and `/`, which IEEE-754
#' mandates be correctly rounded, and the result is rounded to nine decimal places,
#' the constant used everywhere else in the package. A degenerate pair of two empty
#' forms returns 0 rather than `0/0`, because a NaN would be sorted and compared and
#' would then drop the row from one engine's control window but not the other's.
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
#' freedom: the output is the input plus columns, in both engines. A colliding
#' name is now an error instead.
#'
#' The key is trimmed, case-folded and normalised to NFC on *both* sides. Only the
#' norm table's side was trimmed and case-folded before, so a lexicon holding `Dog`
#' matched nothing and the design carried on with an all-`NA` dimension. Because both engines agreed on that wrong
#' answer, no parity test could have caught it. The lexicon's own spelling is
#' preserved rather than folded in place: `word` is the byte-order tie-break behind
#' every selection, so the join must not rewrite it.
#'
#' @param lexicon A lexicon data frame.
#' @param norms A data frame or the path to a CSV with a word column and norms.
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
#       on: word                  # optional join key, default 'word'
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
# thing to do, so accept both shapes. `names()` of an unnamed list is NULL and
# `"path" %in% NULL` is FALSE, which distinguishes them without indexing an unnamed
# list by name (an error, not NULL).
#' @keywords internal
.norm_specs <- function(design) {
  specs <- design[["norms"]] %||% list()
  if (length(specs) && "path" %in% names(specs)) specs <- list(specs)
  specs
}

# `normalisation` in the result counts the norm-table keys that NFC changed and the
# duplicate keys it created, which the join then dropped, summed over the tables
# (see .nfc_count). Mirrors apply_norms in querying.py.
#' @keywords internal
.apply_norms <- function(lex, design) {
  records <- list()
  changed <- collapsed <- 0L
  for (spec in .norm_specs(design)) {
    path <- spec[["path"]]
    if (is.null(path))
      stop("lexsync: every entry under `norms:` needs a `path`.", call. = FALSE)
    parts <- strsplit(gsub("\\\\", "/", path), "/", fixed = TRUE)[[1]]
    if (".." %in% parts)
      stop("lexsync: norms path must not contain '..'.", call. = FALSE)
    on <- spec[["on"]] %||% "word"
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
       normalisation = list(changed = changed, collapsed = collapsed))
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
#' words; only without one does it fall back to the pool itself.
#'
#' @param path Path to a UTF-8 CSV with at least a `word` column.
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

  reference <- df$word
  if (!is.null(lexicon)) {
    lex <- load_lexicon(lexicon, schema, language = language)
    # The lexicon's own normalisation is reported with the pool's, since the run read
    # both.
    lex_record <- attr(lex, "input_normalisation")
    nf$changed <- nf$changed + (lex_record$changed %||% 0L)
    nf$collapsed <- nf$collapsed + (lex_record$collapsed %||% 0L)
    reference <- lex$word
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
#' @param path Path to a UTF-8 CSV item table.
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
#' @param filters A named list mapping columns to either a numeric `c(min, max)`
#'   range or a vector of permitted values.
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
