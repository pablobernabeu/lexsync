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
  required <- unlist(schema$lexicon_schema$required, use.names = FALSE)
  missing <- setdiff(required, names(df))
  if (length(missing)) {
    stop(sprintf("lexsync: lexicon is missing required column(s): %s",
                 paste(sprintf("'%s'", missing), collapse = ", ")), call. = FALSE)
  }
  invisible(TRUE)
}

# Maximal runs of (possibly accented) Latin vowels approximate syllable nuclei.
# Accented code points are built with intToUtf8 so the R source stays ASCII (CRAN).
.VOWELS <- paste0("[aeiouy", intToUtf8(c(
  0xe0, 0xe1, 0xe2, 0xe3, 0xe4, 0xe5, 0xe8, 0xe9, 0xea, 0xeb, 0xec, 0xed, 0xee,
  0xef, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf8, 0xf9, 0xfa, 0xfb, 0xfc, 0xfd, 0xff)),
  "]+")                          # y with acute/diaeresis

#' Orthographic syllable estimate: the number of maximal vowel runs
#' @keywords internal
count_syllables <- function(word) {
  word <- tolower(as.character(word))
  vapply(word, function(w) {
    m <- gregexpr(.VOWELS, w, perl = TRUE)[[1]]
    if (length(m) == 1L && m[1] == -1L) 0L else length(m)
  }, integer(1), USE.NAMES = FALSE)
}

#' Load a lexicon from a CSV file
#'
#' Reads a derived lexicon, validates the column contract, lower-cases the
#' orthographic form, removes duplicates and attaches a stable integer `id` plus
#' the inexpensive dimensions `length` and `frequency`. The orthographic
#' neighbourhood dimensions are added later, on the experimental pool, by
#' [add_neighbourhood()], because they are quadratic in the size of the
#' reference set.
#'
#' @param path Path to a derived lexicon CSV.
#' @param schema The parsed schema (see `config/schema.yaml`).
#' @param language Optional language label to record in a `language` column.
#' @return A data frame with at least `word`, `freq_zipf`, `length`,
#'   `frequency` and `id`.
#' @examples
#' \dontrun{
#' schema <- read_config(system.file("extdata", "schema.yaml", package = "lexsync"))
#' lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"), schema)
#' }
#' @export
load_lexicon <- function(path, schema, language = NULL) {
  df <- as.data.frame(read_csv_utf8(path), stringsAsFactors = FALSE)
  validate_lexicon(df, schema)
  freq_col <- schema$dimensions$frequency$column %||% "freq_zipf"
  df$word <- tolower(trimws(as.character(df$word)))
  keep <- !is.na(df$word) & nzchar(df$word) & !is.na(df[[freq_col]])
  df <- df[keep, , drop = FALSE]
  df <- df[!duplicated(df$word), , drop = FALSE]
  # Byte-order ('radix') sort so the lexicon order is locale-independent and
  # therefore identical to the Python engine (which sorts by UTF-8 bytes).
  df <- df[order(df$word, method = "radix"), , drop = FALSE]
  df$id <- seq_len(nrow(df))
  df$length <- nchar(df$word)
  df$n_syllables <- count_syllables(df$word)
  df$frequency <- as.numeric(df[[freq_col]])
  if (!is.null(language)) df$language <- language
  rownames(df) <- NULL
  df
}

#' Compute orthographic-neighbourhood dimensions (Coltheart's N and OLD20)
#'
#' `n_density` is Coltheart's N: the number of reference words of the same
#' length differing by a single letter substitution (Hamming distance 1).
#' `old20` is the mean Levenshtein distance to the 20 nearest reference words
#' (Yarkoni, Balota & Yap, 2008). Both are computed against `reference`, which
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

#' Mean positional bigram probability, a phonotactic-probability proxy
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
    round(sum(v) / length(bgs) / total, 9)
  }
  df$bigram_freq <- vapply(as.character(df$word), bf, numeric(1), USE.NAMES = FALSE)
  df
}

#' Left-join a norm table (e.g. concreteness, age of acquisition, valence)
#'
#' The connector for semantic dimensions: the norm data themselves are fetched
#' separately (licensing varies), then merged here so the matcher can equate on
#' them. The join is deterministic and identical across engines.
#'
#' @param lexicon A lexicon data frame.
#' @param norms A data frame or the path to a CSV with a word column and norms.
#' @param on The join column (default "word").
#' @param columns Optional norm columns to keep.
#' @return `lexicon` with the norm columns joined on.
#' @export
merge_norms <- function(lexicon, norms, on = "word", columns = NULL) {
  n <- if (is.data.frame(norms)) norms else as.data.frame(read_csv_utf8(norms), stringsAsFactors = FALSE)
  cols <- if (!is.null(columns)) columns else setdiff(names(n), on)
  n <- n[, c(on, cols), drop = FALSE]
  n[[on]] <- tolower(trimws(as.character(n[[on]])))
  n <- n[!duplicated(n[[on]]), , drop = FALSE]
  merge(lexicon, n, by = on, all.x = TRUE, sort = FALSE)
}

#' Load a paradigm item table (prime-target pairs, sentences, ...)
#'
#' The table must carry an `item` identifier, a `condition` label and the
#' paradigm's presented fields. Field values are validated (no control
#' characters; bounded length) so a crafted item cannot corrupt the generated
#' loop table or scripts. Items are mapped to a deterministic integer `set` id
#' (byte order), so counterbalancing matches the corpus path and the two engines.
#'
#' @param path Path to a UTF-8 CSV item table.
#' @param required_fields Character vector of presented fields the paradigm needs.
#' @return A data frame with `set`, `condition` and the item fields.
#' @export
load_items <- function(path, required_fields) {
  parts <- strsplit(gsub("\\\\", "/", path), "/", fixed = TRUE)[[1]]
  if (".." %in% parts) stop("lexsync: items path must not contain '..'.", call. = FALSE)
  df <- as.data.frame(read_csv_utf8(path), stringsAsFactors = FALSE)
  needed <- c("item", "condition", required_fields)
  missing <- setdiff(needed, names(df))
  if (length(missing)) {
    stop(sprintf("lexsync: items table '%s' is missing column(s): %s.",
                 path, paste(missing, collapse = ", ")), call. = FALSE)
  }
  for (f in intersect(required_fields, names(df))) {
    df[[f]] <- vapply(df[[f]], function(v) clean_field(v, f), character(1))
  }
  items <- sort(unique(as.character(df$item)), method = "radix")
  set_map <- stats::setNames(seq_along(items), items)
  df$set <- unname(set_map[as.character(df$item)])
  df$condition <- as.character(df$condition)
  rownames(df) <- NULL
  df
}

#' Build an experimental candidate pool by filtering a lexicon
#'
#' @param lexicon A lexicon data frame.
#' @param filters A named list mapping columns to either a numeric `c(min, max)`
#'   range or a vector of permitted values.
#' @return The filtered lexicon.
#' @export
build_pool <- function(lexicon, filters = NULL) {
  df <- lexicon
  if (!is.null(filters)) {
    for (col in names(filters)) {
      if (!col %in% names(df)) next
      rng <- unlist(filters[[col]], use.names = FALSE)
      if (is.numeric(rng) && length(rng) == 2) {
        df <- df[!is.na(df[[col]]) & df[[col]] >= rng[1] & df[[col]] <= rng[2], , drop = FALSE]
      } else {
        df <- df[!is.na(df[[col]]) & as.character(df[[col]]) %in% as.character(rng), , drop = FALSE]
      }
    }
  }
  rownames(df) <- NULL
  df
}
