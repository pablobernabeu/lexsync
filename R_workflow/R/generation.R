# generation.R -- deterministic, orthographically-controlled pseudoword generation.
# For each real base word a pseudoword is produced by constrained letter
# substitution: change the fewest letters so that every resulting bigram is
# attested in the corpus, the form is not a real word, and the length is
# preserved. Among the legal non-word neighbours the most bigram-plausible is
# chosen, with byte-order (radix) tie-breaks, so the R and Python engines generate
# the identical pseudoword from the identical corpus. A deterministic orthographic
# cousin of Wuggy (Keuleers & Brysbaert, 2010). Mirrors generation.py.

#' Integer counts of adjacent letter bigrams across a word list
#' @keywords internal
bigram_counts <- function(words) {
  words <- as.character(words)
  pairs <- unlist(lapply(words, function(w) {
    n <- nchar(w)
    if (n < 2L) character(0) else substring(w, 1:(n - 1L), 2:n)
  }), use.names = FALSE)
  tab <- table(pairs)
  out <- as.integer(tab)
  names(out) <- names(tab)
  out
}

.bg_of <- function(w) {
  n <- nchar(w)
  if (n < 2L) character(0) else substring(w, 1:(n - 1L), 2:n)
}

.bg_legal <- function(cand, bigrams) all(.bg_of(cand) %in% names(bigrams))

.bg_score <- function(cand, bigrams) {
  v <- bigrams[.bg_of(cand)]
  sum(ifelse(is.na(v), 0L, v))
}

#' The most bigram-plausible legal non-word at the smallest edit distance
#'
#' Searches single-letter substitutions first, then two-letter substitutions;
#' candidates are ranked by summed bigram frequency with a byte-order tie-break,
#' so the choice is deterministic and identical across engines.
#' @keywords internal
make_pseudoword <- function(word, bigrams, lexset, usedset) {
  word <- as.character(word)
  L <- nchar(word)
  chars <- strsplit(word, "", fixed = TRUE)[[1]]
  cands <- character(0)
  for (pos in seq_len(L)) {
    for (ch in letters) {
      if (ch == chars[pos]) next
      cand <- word
      substr(cand, pos, pos) <- ch
      if (exists(cand, envir = lexset, inherits = FALSE)) next
      if (exists(cand, envir = usedset, inherits = FALSE)) next
      if (.bg_legal(cand, bigrams)) cands <- c(cands, cand)
    }
  }
  if (length(cands) == 0L) {
    for (i in seq_len(L)) for (j in seq_len(L)) {
      if (j <= i) next
      for (ci in letters) {
        if (ci == chars[i]) next
        for (cj in letters) {
          if (cj == chars[j]) next
          cand <- word
          substr(cand, i, i) <- ci
          substr(cand, j, j) <- cj
          if (exists(cand, envir = lexset, inherits = FALSE)) next
          if (exists(cand, envir = usedset, inherits = FALSE)) next
          if (.bg_legal(cand, bigrams)) cands <- c(cands, cand)
        }
      }
    }
  }
  if (length(cands) == 0L) return(NULL)
  scores <- vapply(cands, .bg_score, integer(1), bigrams = bigrams)
  cands[order(-scores, cands, method = "radix")[1]]
}

#' A length-matched pseudoword for each base word (byte-order processing)
#' @keywords internal
generate_pseudowords <- function(base_words, reference_words) {
  base <- as.character(base_words)
  bigrams <- bigram_counts(reference_words)
  lexset <- new.env(hash = TRUE, parent = emptyenv())
  for (w in unique(as.character(reference_words))) assign(w, TRUE, envir = lexset)
  usedset <- new.env(hash = TRUE, parent = emptyenv())
  pseudo <- character(length(base))
  for (i in order(base, method = "radix")) {
    pw <- make_pseudoword(base[i], bigrams, lexset, usedset)
    if (is.null(pw)) {
      stop(sprintf("lexsync: could not generate a pseudoword for '%s'.", base[i]), call. = FALSE)
    }
    assign(pw, TRUE, envir = usedset)
    pseudo[i] <- pw
  }
  data.frame(base_word = base, pseudoword = pseudo, stringsAsFactors = FALSE)
}

#' Assemble a word-vs-pseudoword lexical-decision set from a candidate pool
#'
#' Real words are drawn by an even spread across the byte-ordered pool, then a
#' length-matched pseudoword is generated for each. `reference_words` (the full
#' lexicon) supplies the bigram statistics and the real-word list a pseudoword
#' must avoid. The presented string is the `target` column; conditions are `word`
#' and `pseudoword` and `set` pairs them.
#' @keywords internal
build_lexdec_stimuli <- function(pool, n, reference_words = NULL) {
  pool <- pool[order(pool$word, method = "radix"), , drop = FALSE]
  if (nrow(pool) == 0L) stop("lexsync: lexical-decision pool is empty.", call. = FALSE)
  n_take <- min(n, nrow(pool))
  idx <- unique(round(seq(1, nrow(pool), length.out = n_take)))
  words <- pool[idx, , drop = FALSE]
  ref <- if (!is.null(reference_words)) as.character(reference_words) else pool$word
  gen <- generate_pseudowords(words$word, ref)
  pw_map <- stats::setNames(gen$pseudoword, gen$base_word)
  real <- data.frame(target = words$word, word = words$word, condition = "word",
                     length = words$length, set = seq_len(nrow(words)), stringsAsFactors = FALSE)
  pseudo <- data.frame(target = unname(pw_map[words$word]), word = unname(pw_map[words$word]),
                       condition = "pseudoword", length = words$length,
                       set = seq_len(nrow(words)), stringsAsFactors = FALSE)
  out <- rbind(real, pseudo)
  rownames(out) <- NULL
  out
}
