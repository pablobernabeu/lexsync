# generation.R -- deterministic, orthographically-controlled pseudoword generation.
# For each real base word a pseudoword is produced by constrained letter
# substitution: change the fewest letters so that every resulting bigram is
# attested in the corpus, the form is not in the reference word list, and the
# length is preserved. Among the legal candidates the most bigram-typical is
# chosen, with byte-order (radix) tie-breaks, so the R and Python engines generate
# the identical pseudoword from the identical corpus. Mirrors generation.py.
#
# A real word is anything in the reference list, so a low-frequency word below the
# lexicon's floor (Zipf 2.95 in the bundled English lexicon) is not one. The
# generators therefore take an `exclude` list of further known word forms, which a
# pseudoword must not equal either, and .read_known_forms() reads such lists for a
# design's items.generation.exclude. Lexicality is checked against those forms
# only, so a form missing from all of them may still be a word: crier, pall and
# titer have come through with the English lexicon and no exclusion list. Because
# the scoring picks the most typical candidate and does not match the base word,
# pseudowords are more bigram-typical than their base words (d about -1.0, words
# minus pseudowords, in en_lexdec). The subsyllabic method is an orthographic
# approximation of Wuggy (Keuleers & Brysbaert, 2010) and differs from it: Wuggy
# matches the template's transition frequencies, matches letter length by default
# and has orthographic language plugins, and by default keeps two thirds of the
# segments, whereas lexsync replaces up to ceil(2k/3) of a word's k constituents.

# The forms a pseudoword must not equal, as an environment used as a set: the
# reference words and `exclude`. The excluded forms are trimmed, lower-cased and put
# in NFC, as a lexicon's words are, so a list written in another case or spelling
# still matches. They only widen this set. The bigram statistics and the constituent
# inventory still come from the reference words alone, so an exclusion list removes
# candidates without changing how the others are scored. Mirrors _known_set in
# generation.py.
.known_set <- function(reference_words, exclude = NULL) {
  known <- unique(as.character(reference_words))
  if (!is.null(exclude)) {
    ex <- .norm_key(unlist(exclude, use.names = FALSE))
    known <- unique(c(known, ex[!is.na(ex) & nzchar(ex)]))
  }
  known <- known[!is.na(known) & nzchar(known)]
  list2env(stats::setNames(as.list(rep(TRUE, length(known))), known),
           envir = new.env(hash = TRUE, parent = emptyenv()))
}

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
#'
#' @param word The base word to derive the pseudoword from.
#' @param bigrams Named integer vector of bigram counts, from [bigram_counts()].
#' @param lexset Environment used as a set of the real word forms a pseudoword
#'   must avoid.
#' @param usedset Environment used as a set of the pseudowords already taken.
#' @return A single pseudoword string, or `NULL` if no legal candidate exists.
#' @export
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
#'
#' @param base_words Character vector of words to derive pseudowords from.
#' @param reference_words Character vector (typically the full lexicon) that
#'   supplies the bigram statistics and the real word forms to avoid.
#' @param exclude Optional character vector of further word forms no pseudoword
#'   may equal, such as low-frequency words the reference lacks. They are trimmed,
#'   lower-cased and put in Unicode NFC, as a lexicon's words are, and play no part
#'   in the bigram statistics.
#' @return A data frame with columns `base_word` and `pseudoword`.
#' @export
generate_pseudowords <- function(base_words, reference_words, exclude = NULL) {
  base <- as.character(base_words)
  bigrams <- bigram_counts(reference_words)
  lexset <- .known_set(reference_words, exclude)
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

# Order in which subsyllabic constituents are considered for substitution: codas
# and nuclei vary more freely than onsets. Mirrors generation.py _ROLE_ORDER.
.ROLE_ORDER <- c(coda = 0L, nucleus = 1L, onset = 2L)

#' Split a word into ordered (role, text) subsyllabic constituents
#'
#' Nuclei are the maximal vowel runs; consonants before the first nucleus form the
#' first onset, those after the last nucleus the final coda, and a consonant run
#' between two nuclei is split at its midpoint (floor(m/2) to the left coda). An
#' orthographic model for Latin a-z words only: any word with a character outside
#' a-z (accented, hyphenated, digit) returns an empty list, as does a word with no
#' vowel, and the caller falls back to letter substitution. Mirrors
#' segment_subsyllabic in generation.py.
#' @keywords internal
segment_subsyllabic <- function(word) {
  w <- .lower_invariant(word)
  # Subsyllabic segmentation is an orthographic model for Latin a-z words; any word
  # with a character outside a-z returns an empty list so the caller falls back to
  # letter substitution (keeps the engines in step; avoids multi-byte edge cases).
  if (!grepl("^[a-z]+$", w, perl = TRUE)) return(list())   # perl: locale-independent ASCII a-z
  L <- nchar(w)
  loc <- stringi::stri_locate_all_regex(w, .SYLLABLE_VOWELS)[[1]]
  if (is.na(loc[1L, 1L])) return(list())
  starts <- as.integer(loc[, "start"])
  ends <- as.integer(loc[, "end"])
  out <- list()
  add <- function(role, text) out[[length(out) + 1L]] <<- list(role = role, text = text)
  if (starts[1] > 1L) add("onset", substr(w, 1L, starts[1] - 1L))
  ns <- length(starts)
  for (si in seq_len(ns)) {
    add("nucleus", substr(w, starts[si], ends[si]))
    run_start <- ends[si] + 1L
    run_end <- if (si < ns) starts[si + 1L] - 1L else L
    run <- if (run_end >= run_start) substr(w, run_start, run_end) else ""
    mrun <- nchar(run)
    if (si < ns) {
      cut <- mrun %/% 2L
      if (cut > 0L) add("coda", substr(run, 1L, cut))
      if (mrun - cut > 0L) add("onset", substr(run, cut + 1L, mrun))
    } else if (mrun > 0L) {
      add("coda", run)
    }
  }
  out
}

#' Attested subsyllabic constituents keyed by "role|length" with integer counts
#' @keywords internal
build_constituent_inventory <- function(reference_words) {
  inv <- new.env(hash = TRUE, parent = emptyenv())
  for (w in as.character(reference_words)) {
    for (cst in segment_subsyllabic(w)) {
      key <- paste0(cst$role, "|", nchar(cst$text))
      bucket <- if (exists(key, envir = inv, inherits = FALSE)) get(key, envir = inv) else integer(0)
      bucket[cst$text] <- (if (cst$text %in% names(bucket)) bucket[[cst$text]] else 0L) + 1L
      assign(key, bucket, envir = inv)
    }
  }
  inv
}

#' A pseudoword built by swapping whole subsyllabic constituents
#'
#' Up to ceil(2k/3) constituents (codas and nuclei before onsets) are each replaced
#' by an attested constituent of the same role and length, keeping every bigram legal
#' and the form a novel non-word; length is preserved. Returns NULL if no legal swap
#' exists (the caller falls back to letter substitution). Mirrors
#' make_subsyllabic_pseudoword in generation.py.
#' @keywords internal
make_subsyllabic_pseudoword <- function(word, inv, bigrams, lexset, usedset) {
  segs <- segment_subsyllabic(word)
  roles <- vapply(segs, function(c) c$role, character(1))
  if (!("nucleus" %in% roles)) return(NULL)
  k <- length(segs)
  target <- as.integer(ceiling(2 * k / 3))
  texts <- vapply(segs, function(c) c$text, character(1))
  bucket_of <- function(i) {
    key <- paste0(segs[[i]]$role, "|", nchar(texts[i]))
    if (exists(key, envir = inv, inherits = FALSE)) get(key, envir = inv) else integer(0)
  }
  elig <- Filter(function(i) length(bucket_of(i)) >= 2L, seq_len(k))
  if (length(elig)) {
    elig <- elig[order(vapply(elig, function(i) .ROLE_ORDER[[segs[[i]]$role]], integer(1)),
                       elig, method = "radix")]
  }
  changed <- 0L
  for (i in elig[seq_len(min(length(elig), target))]) {
    alts <- names(bucket_of(i)); alts <- alts[alts != texts[i]]
    cands <- character(0); scores <- integer(0); trials <- list()
    for (alt in alts) {
      trial <- texts; trial[i] <- alt
      cand <- paste0(trial, collapse = "")
      if (exists(cand, envir = lexset, inherits = FALSE)) next
      if (exists(cand, envir = usedset, inherits = FALSE)) next
      if (!.bg_legal(cand, bigrams)) next
      cands <- c(cands, cand); scores <- c(scores, .bg_score(cand, bigrams))
      trials[[length(trials) + 1L]] <- trial
    }
    if (length(cands)) {
      best <- order(-scores, cands, method = "radix")[1]
      texts <- trials[[best]]; changed <- changed + 1L
    }
  }
  if (changed == 0L) return(NULL)
  final <- paste0(texts, collapse = "")
  if (exists(final, envir = lexset, inherits = FALSE)) return(NULL)
  if (exists(final, envir = usedset, inherits = FALSE)) return(NULL)
  if (!.bg_legal(final, bigrams)) return(NULL)
  final
}

#' A subsyllabic pseudoword for each base word (with letter-substitution fallback)
#'
#' `exclude` is as for [generate_pseudowords()].
#' @keywords internal
generate_pseudowords_subsyllabic <- function(base_words, reference_words, exclude = NULL) {
  base <- as.character(base_words)
  bigrams <- bigram_counts(reference_words)
  lexset <- .known_set(reference_words, exclude)
  inv <- build_constituent_inventory(reference_words)
  usedset <- new.env(hash = TRUE, parent = emptyenv())
  pseudo <- character(length(base))
  for (i in order(base, method = "radix")) {
    pw <- make_subsyllabic_pseudoword(base[i], inv, bigrams, lexset, usedset)
    if (is.null(pw)) pw <- make_pseudoword(base[i], bigrams, lexset, usedset)
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
#' length-matched pseudoword is generated for each. The pool is first filtered to
#' lower-case a-z forms, the only ones the pseudoword generators are defined for,
#' so the eligible pool can be smaller than the request; the pipeline's shortfall
#' policy then decides whether that errors. `reference_words` (the full
#' lexicon) supplies the bigram statistics and the real-word list a pseudoword
#' must avoid. The presented string is the `target` column; conditions are `word`
#' and `pseudoword` and `set` pairs them.
#'
#' @param pool Data frame of candidate words, e.g. from [build_pool()].
#' @param n Number of real words to select.
#' @param reference_words Character vector supplying the bigram statistics and
#'   the real word forms a pseudoword must avoid; defaults to the pool's words.
#' @param method Pseudoword generator: `"letter_substitution"` (default) or
#'   `"subsyllabic"` (Wuggy-style; Keuleers & Brysbaert, 2010).
#' @param exclude Optional character vector of further known word forms a
#'   pseudoword must not equal, which the reference may lack; see
#'   [generate_pseudowords()].
#' @return A stimulus data frame with `target`, `condition` and `set` columns.
#'   `base` gives the word each pseudoword was made from, a word's own form for a
#'   word, and `edit_distance` the Levenshtein distance from `target` to `base`, 0
#'   for a word.
#' @export
build_lexdec_stimuli <- function(pool, n, reference_words = NULL, method = "letter_substitution",
                                 exclude = NULL) {
  pool <- pool[order(pool$word, method = "radix"), , drop = FALSE]
  # The pseudoword generators are defined for Latin a-z words; skip others.
  pool <- .lexdec_eligible(pool)
  if (nrow(pool) == 0L) stop("lexsync: lexical-decision pool has no a-z words.", call. = FALSE)
  n_take <- min(n, nrow(pool))
  idx <- unique(round(seq(1, nrow(pool), length.out = n_take)))
  words <- pool[idx, , drop = FALSE]
  ref <- if (!is.null(reference_words)) as.character(reference_words) else pool$word
  gen <- if (identical(method, "subsyllabic")) {
    generate_pseudowords_subsyllabic(words$word, ref, exclude = exclude)
  } else if (identical(method, "letter_substitution")) {
    generate_pseudowords(words$word, ref, exclude = exclude)
  } else {
    stop(sprintf("lexsync: unknown pseudoword generation method '%s'.", method), call. = FALSE)
  }
  pw_map <- stats::setNames(gen$pseudoword, gen$base_word)
  forms <- unname(pw_map[words$word])
  real <- data.frame(target = words$word, word = words$word, condition = "word",
                     length = words$length, set = seq_len(nrow(words)),
                     base = words$word, edit_distance = 0, stringsAsFactors = FALSE)
  # stringdist's "lv" equals rapidfuzz's distance in the Python engine, the agreement
  # add_neighbourhood() already rests OLD20 on.
  pseudo <- data.frame(target = forms, word = forms,
                       condition = "pseudoword", length = words$length,
                       set = seq_len(nrow(words)), base = words$word,
                       edit_distance = stringdist::stringdist(forms, words$word, method = "lv"),
                       stringsAsFactors = FALSE)
  out <- rbind(real, pseudo)
  rownames(out) <- NULL
  out
}

# The rows of a pool the pseudoword generators can use, in the pool's order. The
# generators are orthographic and defined for Latin a-z words, so a word with any
# other character (an accent, a hyphen, a digit) is left out. The pipeline counts
# these rows as a generated design's candidates: counting the whole band reported,
# for a Spanish band, accented words the generator never sees. Mirrors
# _lexdec_eligible in generation.py.
.lexdec_eligible <- function(pool) {
  keep <- !is.na(pool$word) & grepl("^[a-z]+$", pool$word, perl = TRUE)
  out <- pool[keep, , drop = FALSE]
  rownames(out) <- NULL
  out
}

# A registry corpus is named by a bare token; anything else in an exclusion list is a
# path. Mirrors _REGISTRY_NAME in generation.py.
.REGISTRY_NAME <- "^[A-Za-z0-9_-]+$"
.EXCLUDE_MESSAGE <- paste("lexsync: items.generation.exclude must list file paths or",
                          "registry corpus names.")

# The registry's `corpora` entry for a bare name, or NULL. A registry that cannot be
# found or read leaves the name to be read as a path.
.registry_entry <- function(name) {
  if (!grepl(.REGISTRY_NAME, name, perl = TRUE)) return(NULL)
  reg <- tryCatch(yaml::read_yaml(default_registry_path()), error = function(e) NULL)
  entry <- reg[["corpora"]][[name]]
  if (is.list(entry)) entry else NULL
}

# The lines of a UTF-8 file, without a byte-order mark or line feeds. Read as bytes,
# so the session's locale plays no part. A file in another encoding is refused,
# because its accented forms would be misread, and strsplit() would find no forms in
# it at all.
.read_utf8_lines <- function(path) {
  bytes <- readBin(path, "raw", file.info(path)$size)
  bom <- as.raw(c(0xEF, 0xBB, 0xBF))
  if (length(bytes) >= 3L && identical(bytes[1:3], bom)) bytes <- bytes[-(1:3)]
  text <- rawToChar(bytes)
  if (!validUTF8(text)) {
    stop(sprintf("lexsync: known-form list '%s' is not UTF-8 text.", path), call. = FALSE)
  }
  Encoding(text) <- "UTF-8"
  strsplit(text, "\n", fixed = TRUE)[[1]]
}

# A line of a one-form-per-line list that holds one of these is a table row, which
# would be kept whole as one form and match no pseudoword, so the list would exclude
# nothing while the datasheet counted its rows. SUBTLEX-US, for one, is distributed as
# a tab-separated .txt file. Mirrors _TABLE_SEPARATORS in generation.py.
.TABLE_SEPARATORS <- "[\t,;]"

# Word forms from a one-form-per-line list. Blank lines and lines beginning '#' are
# skipped, and every form is trimmed, lower-cased and put in NFC. A line that holds a
# tab, a comma or a semicolon is refused, since the file is then a table.
.forms_from_lines <- function(lines, path) {
  v <- .norm_key(lines)
  keep <- !is.na(v) & nzchar(v) & !startsWith(v, "#")
  bad <- which(keep & grepl(.TABLE_SEPARATORS, v, perl = TRUE))
  if (length(bad)) {
    stop(sprintf(paste0("lexsync: line %d of the known-form list '%s' holds a tab, comma ",
                        "or semicolon, so the file is a table. List one form per line, ",
                        "or give a CSV file with a 'word' column."), bad[1], path),
         call. = FALSE)
  }
  v[keep]
}

# One column of a tab-separated table, the layout openlexicon serves. Read by
# splitting each line, with no quoting rule, so both engines read the same cells.
.forms_from_tab_table <- function(path, column) {
  lines <- .read_utf8_lines(path)
  lines <- lines[grepl("[^ \t\r\n]", lines)]
  if (!length(lines)) return(character(0))
  header <- gsub(.CSV_TRIM, "", strsplit(lines[1], "\t", fixed = TRUE)[[1]])
  j <- match(column, header)
  if (is.na(j)) {
    stop(sprintf("lexsync: known-form table '%s' has no '%s' column.", path, column),
         call. = FALSE)
  }
  cells <- vapply(strsplit(lines[-1], "\t", fixed = TRUE),
                  function(f) if (length(f) >= j) f[j] else "", character(1))
  v <- .norm_key(cells)
  v[!is.na(v) & nzchar(v)]
}

.forms_from_csv <- function(path, column) {
  table <- read_csv_utf8(path, as_character = column)
  if (!column %in% names(table)) {
    stop(sprintf("lexsync: known-form table '%s' has no '%s' column.", path, column),
         call. = FALSE)
  }
  v <- .norm_key(table[[column]])
  v[!is.na(v) & nzchar(v)]
}

# Read the word-form lists of a design's items.generation.exclude. Each entry is a path
# or the name of a corpus in the registry. A path ending in .csv is a table whose
# `word` column holds the forms; any other path is a UTF-8 text file with one form per
# line, in which blank lines and lines beginning '#' are skipped and a line holding a
# tab, comma or semicolon is refused as a table row. A registry name is
# read from the copy fetch_corpus() put in the cache, by the column the registry maps
# to `word`, and is refused with the fetch command when no copy is there. Every form
# is trimmed, lower-cased and put in NFC, as a lexicon's words are.
#
# Returns list(forms, records): the distinct forms of all the lists in UTF-8 byte
# order, and for each list its `source` (the path with '/' separators, or the
# registry name), the `sha256` of the file read and `n_forms`, the number of distinct
# forms it holds. Mirrors _read_known_forms in generation.py.
.read_known_forms <- function(entries) {
  if (is.null(entries)) entries <- list()
  if (is.character(entries)) entries <- as.list(entries)
  # A mapping is refused, as the Python twin refuses a dict.
  if (!is.list(entries) || !is.null(names(entries))) stop(.EXCLUDE_MESSAGE, call. = FALSE)
  forms <- character(0)
  records <- list()
  for (entry in entries) {
    if (!is.character(entry) || length(entry) != 1L || is.na(entry) ||
        !grepl("[^ \t\r\n]", entry)) {
      stop(.EXCLUDE_MESSAGE, call. = FALSE)
    }
    reg <- .registry_entry(entry)
    if (!is.null(reg)) {
      path <- file.path(path.expand(lexsync_cache_dir()), paste0(entry, ".csv"))
      if (!file.exists(path) || dir.exists(path)) {
        stop(sprintf(paste0("lexsync: items.generation.exclude names the registry corpus ",
                            "'%s', which is not in the cache (%s). Fetch it first with ",
                            "fetch_corpus('%s'), or list a word-form file instead."),
                     entry, path, entry), call. = FALSE)
      }
      column <- as.character(reg[["columns"]][["word"]] %||% "word")
      first <- .read_utf8_lines(path)
      first <- if (length(first)) first[1] else ""
      got <- if (grepl("\t", first, fixed = TRUE)) .forms_from_tab_table(path, column)
             else .forms_from_csv(path, column)
      source <- entry
    } else {
      if (!file.exists(entry) || dir.exists(entry)) {
        stop(sprintf(paste0("lexsync: items.generation.exclude names '%s', which is ",
                            "neither a readable file nor a corpus in the registry."),
                     entry), call. = FALSE)
      }
      path <- entry
      got <- if (grepl("\\.csv$", tolower(entry))) .forms_from_csv(path, "word")
             else .forms_from_lines(.read_utf8_lines(path), entry)
      source <- gsub("\\", "/", entry, fixed = TRUE)
    }
    distinct <- unique(got)
    forms <- c(forms, distinct)
    records[[length(records) + 1L]] <- list(source = source, sha256 = sha256_file(path),
                                            n_forms = length(distinct))
  }
  list(forms = sort(unique(forms), method = "radix"), records = records)
}
