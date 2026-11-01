# corpora.R -- access to the many-language corpus registry. The R package reads
# the bundled, pre-derived lexica for the demonstrations and can download a
# registered corpus file (Connector A) on demand into a user cache, normalising it
# into a lexicon. normalise_lexicon() does the same for a file a user downloaded.
# The wordfreq connector (Connector B, thirty registered languages; wordfreq covers
# 42) is provided by the Python package, and its pre-derived outputs are read here as
# ordinary lexica.

# Refuses a corpus name that could reach a file outside the cache. The name becomes a
# file name inside the cache, so a path separator, or the colon of a Windows drive or
# stream name, would let it reach a file other than the corpus's own. Both
# lexsync_cache_clear() and fetch_corpus() apply the rule, fetch_corpus() before it
# reads the registry, since an edited registry may name an entry '../../escaped'. The
# Python twin, _check_corpus_name in python_workflow/src/lexsync/corpora.py, refuses
# the same three characters.
.check_corpus_name <- function(name) {
  if (!is.character(name) || length(name) != 1L || is.na(name) || !nzchar(name) ||
      grepl("[/\\\\:]", name)) {
    stop("lexsync: 'name' must be a single corpus name, not a path.", call. = FALSE)
  }
  invisible(name)
}

#' Per-user cache directory for fetched corpora
#'
#' The directory `tools::R_user_dir("lexsync", "cache")` names for this package.
#' It is where [fetch_corpus()] puts a download unless told otherwise, and it is
#' the only place the package writes to without being handed a path. This
#' function only reports the path. The directory is created by the first
#' download into it, so until then it does not exist.
#'
#' The cache persists between sessions. A registered corpus is a delimited word
#' list, and a download is refused above 200 MB, so a cache holding several
#' large corpora can reach a few hundred megabytes. Each download into the cache
#' first deletes any partial download that an interrupted transfer left there
#' more than a day earlier, and fetching a corpus again replaces the earlier
#' copy. Downloaded corpora otherwise stay until [lexsync_cache_clear()] removes
#' them, one corpus at a time or all together. Nothing kept there is
#' irreplaceable, so the next call downloads afresh.
#'
#' @return The cache directory path, which need not exist yet.
#' @seealso [lexsync_cache_clear()] to empty the cache.
#' @examples
#' lexsync_cache_dir()
#' @importFrom tools R_user_dir
#' @export
lexsync_cache_dir <- function() {
  tools::R_user_dir("lexsync", "cache")
}

#' Remove fetched corpora from the cache
#'
#' Deletes what [fetch_corpus()] put in [lexsync_cache_dir()]. Given a `name`,
#' that is the corpus's `<name>.csv` and any `<name>.csv.part` that an
#' interrupted download left behind. With `name` left `NULL` it is the whole
#' cache directory. A corpus needed again is downloaded afresh by the next
#' [fetch_corpus()] call. A file that [fetch_corpus()] wrote to a `dest` of the
#' caller's choosing is not in the cache, and is never touched.
#'
#' @param name A corpus name as given to [fetch_corpus()], or `NULL` (the
#'   default) to remove the whole cache.
#' @return The paths of the files removed, invisibly. The vector is empty when
#'   there was nothing to remove.
#' @seealso [lexsync_cache_dir()] for where the cache lives.
#' @examples
#' # A throwaway cache stands in for yours, so running this leaves your own alone.
#' local({
#'   tmp <- tempfile("lexsync-")
#'   old <- Sys.getenv("R_USER_CACHE_DIR", unset = NA)
#'   on.exit({
#'     if (is.na(old)) Sys.unsetenv("R_USER_CACHE_DIR") else
#'       Sys.setenv(R_USER_CACHE_DIR = old)
#'     unlink(tmp, recursive = TRUE)
#'   })
#'   Sys.setenv(R_USER_CACHE_DIR = tmp)
#'   # Two corpora and an interrupted download
#'   dir.create(lexsync_cache_dir(), recursive = TRUE)
#'   invisible(file.create(file.path(lexsync_cache_dir(),
#'     c("subtlex_nl.csv", "subtlex_nl.csv.part", "lexique_fr.csv"))))
#'   # One corpus, with its partial download
#'   print(basename(lexsync_cache_clear("subtlex_nl")))
#'   # Everything else, and the directory itself
#'   print(basename(lexsync_cache_clear()))
#'   dir.exists(lexsync_cache_dir())
#' })
#' @export
lexsync_cache_clear <- function(name = NULL) {
  # Mirrors cache_clear() in python_workflow/src/lexsync/corpora.py, which also
  # removes the <name>_wordfreq.csv that only that engine builds. The tilde is
  # expanded here because unlink() below expands nothing, and R_user_dir() keeps a
  # leading '~' from R_USER_CACHE_DIR as it is.
  dir <- path.expand(lexsync_cache_dir())
  if (is.null(name)) {
    removed <- list.files(dir, recursive = TRUE, full.names = TRUE, all.files = TRUE)
    targets <- dir
  } else {
    .check_corpus_name(name)
    targets <- file.path(dir, paste0(name, c(".csv", ".csv.part")))
    # Files only, as the twin's os.path.isfile() has it.
    targets <- targets[file.exists(targets) & !dir.exists(targets)]
    removed <- targets
  }
  # With expand = FALSE a name or cache path holding *, ? or [ ] names itself and
  # nothing else; with the default, "*" would empty the cache. unlink() reports a
  # file it could not delete (one held open on Windows, say) only through its
  # return code, so what survives is checked for directly.
  unlink(targets, recursive = is.null(name), expand = FALSE)
  left <- targets[file.exists(targets)]
  if (length(left)) {
    stop(sprintf("lexsync: could not remove %s from the cache; check that no other process is using it.",
                 paste(left, collapse = ", ")), call. = FALSE)
  }
  invisible(removed)
}

# Readies the cache for a download into it. Mirrors _prepare_cache() in
# python_workflow/src/lexsync/corpora.py. A '.part' sidecar outlives its fetch
# only when the transfer was cut short in a way fetch_corpus()'s handlers never
# see: an interrupt reaches neither the error nor the warning branch, and a
# process that dies runs no handler at all. A sidecar can also belong to a
# download still running in another session, which writes to it as it goes and
# gives up on a stalled server after options(timeout). A day without a write
# therefore marks a sidecar as abandoned, and only those are deleted. A younger
# one is left to its download, and a retry of the same corpus truncates its own.
.prepare_cache <- function() {
  dir <- path.expand(lexsync_cache_dir())
  dir.create(dir, recursive = TRUE, showWarnings = FALSE)
  parts <- list.files(dir, pattern = "\\.part$", full.names = TRUE, all.files = TRUE)
  stale <- difftime(Sys.time(), file.mtime(parts), units = "secs") > .stale_part_seconds()
  unlink(parts[!is.na(stale) & stale], expand = FALSE)
  dir
}

# How long a sidecar may go unwritten before the sweep treats it as abandoned.
# Mirrors _STALE_PART_SECONDS in python_workflow/src/lexsync/corpora.py.
.stale_part_seconds <- function() 24 * 60 * 60

# The file the lexsync.registry option names, or "" when the option is unset or empty.
# A file that does not exist is refused, as a registry_path is, so a misspelt or stale
# option never falls through to the next registry. .registry_entry() and
# .registry_citation(), which treat an unreadable registry as absent, call this first
# and refuse such an option too. Mirrors _registry_env() in
# python_workflow/src/lexsync/corpora.py.
.registry_option <- function() {
  opt <- getOption("lexsync.registry", "")
  if (nzchar(opt) && !file.exists(opt)) {
    stop(sprintf("lexsync: registry not found: '%s' (the lexsync.registry option).", opt),
         call. = FALSE)
  }
  opt
}

#' Locate the corpus registry
#' @keywords internal
default_registry_path <- function() {
  cand <- c(
    .registry_option(),
    file.path("corpora", "registry.yaml"),
    file.path("..", "corpora", "registry.yaml"),
    system.file("extdata", "registry.yaml", package = "lexsync")
  )
  cand <- cand[nzchar(cand) & file.exists(cand)]
  if (!length(cand)) {
    stop("lexsync: could not locate 'registry.yaml'; set options(lexsync.registry = '...').",
         call. = FALSE)
  }
  cand[1]
}

# The registry a call reads. A path the caller names is read on its own, so a missing
# one is refused by name, not with the connection error file() gives. Mirrors
# _registry_path() in python_workflow/src/lexsync/corpora.py.
.registry_path <- function(registry_path = NULL) {
  if (is.null(registry_path)) return(default_registry_path())
  if (!file.exists(registry_path)) {
    stop(sprintf("lexsync: registry not found: '%s'.", registry_path), call. = FALSE)
  }
  registry_path
}

#' List the corpora known to the registry
#'
#' @param registry_path Optional path to `registry.yaml`. A path that does not exist
#'   is refused. `NULL` (the default) takes the file `getOption("lexsync.registry")`
#'   names, which must exist. With the option unset or empty, it takes the first that
#'   exists of `corpora/registry.yaml` and `../corpora/registry.yaml` relative to the
#'   working directory, and last the copy bundled with the package,
#'   `system.file("extdata", "registry.yaml", package = "lexsync")`.
#' @return A data frame with one row per entry under `corpora` in the registry and the
#'   columns `name`, `language` (the language's name), `iso` (its code), `status`
#'   (`validated`, `supported`, `manual` or `listed`, as the registry's header defines
#'   them), `connector` (`"openlexicon"` when the entry names none) and `citation`. The
#'   wordfreq connector and its languages have no row, and each entry's licence is in
#'   the registry file, not in the data frame.
#' @export
list_corpora <- function(registry_path = NULL) {
  reg <- .read_yaml_utf8(.registry_path(registry_path))
  corp <- reg[["corpora"]]
  data.frame(
    name = names(corp),
    language = vapply(corp, function(x) x[["language"]][["name"]] %||% NA_character_, character(1)),
    iso = vapply(corp, function(x) x[["language"]][["iso"]] %||% NA_character_, character(1)),
    status = vapply(corp, function(x) x[["status"]] %||% NA_character_, character(1)),
    connector = vapply(corp, function(x) x[["connector"]] %||% "openlexicon", character(1)),
    citation = vapply(corp, function(x) x[["citation"]] %||% NA_character_, character(1)),
    stringsAsFactors = FALSE, row.names = NULL
  )
}

# Does the file open with '<', i.e. an HTML or XML document? Mirrors
# _starts_with_markup() in python_workflow/src/lexsync/corpora.py. A delimited
# file opens on data; a login wall, a redirect stub or a 404 page served with a
# 200 status opens on a tag, and would otherwise be cached as <name>.csv and
# resurface much later as an unintelligible schema error.
.starts_with_markup <- function(path) {
  bytes <- readBin(path, "raw", n = 512L)
  bom <- as.raw(c(0xEF, 0xBB, 0xBF))
  if (length(bytes) >= 3L && identical(bytes[1:3], bom)) bytes <- bytes[-(1:3)]
  ws <- as.raw(c(0x20, 0x09, 0x0A, 0x0D, 0x0B, 0x0C))
  first <- which(!(bytes %in% ws))
  length(first) > 0L && identical(bytes[first[1]], as.raw(0x3C))
}

# Hard cap on a corpus download, in bytes. Mirrors _max_download_bytes() in
# python_workflow/src/lexsync/corpora.py. A function rather than a bare constant
# so the twin tests can lower it without writing 200 MB to disk; the message
# below names the real limit either way.
.max_download_bytes <- function() 200 * 1024^2

.stop_download <- function(name, url, detail, reg_path) {
  stop(sprintf(paste0("lexsync: could not download corpus '%s' from %s (%s). Check the URL ",
                      "in '%s', or download the file manually, convert it with ",
                      "normalise_lexicon() and pass the result to load_lexicon()."),
               name, url, detail, reg_path), call. = FALSE)
}

# The URL a registry entry is fetched from, its sha256, and whether to normalise it.
# A `derived` file, list(url, sha256), is a lexicon already normalised, so both engines
# can read the same bytes, and it is read first when an entry has one. Otherwise
# `openlexicon` names the corpus file in its publisher's layout, which
# normalise_lexicon() turns into a lexicon. `url` alone is a landing page, and
# downloading that would cache an HTML document as <name>.csv. Mirrors
# _download_source in python_workflow/src/lexsync/corpora.py.
.download_source <- function(name, entry, reg_path) {
  derived <- entry[["derived"]]
  if (!is.null(derived)) {
    if (!is.list(derived) || is.null(derived[["url"]])) {
      stop(sprintf("lexsync: corpus '%s' registers a 'derived' file without a url in '%s'.",
                   name, reg_path), call. = FALSE)
    }
    return(list(url = derived[["url"]], sha256 = derived[["sha256"]], normalise = FALSE))
  }
  if (!is.null(entry[["openlexicon"]])) {
    return(list(url = entry[["openlexicon"]], sha256 = entry[["sha256"]], normalise = TRUE))
  }
  if (!is.null(entry[["url"]])) {
    stop(sprintf(paste0("lexsync: corpus '%s' registers only a landing page (%s) in '%s'; ",
                        "lexsync cannot download it automatically. Retrieve the delimited ",
                        "file manually, convert it with normalise_lexicon() and pass the ",
                        "result to load_lexicon()."),
                 name, entry[["url"]], reg_path), call. = FALSE)
  }
  stop(sprintf(paste0("lexsync: corpus '%s' registers no download URL in '%s'; retrieve ",
                      "its file manually, convert it with normalise_lexicon() and pass the ",
                      "result to load_lexicon()."),
               name, reg_path), call. = FALSE)
}

#' Download a registered corpus into the cache
#'
#' Downloads the file a registry entry names and caches it as a lexicon that
#' [load_lexicon()] reads. `name` must be a single corpus name: one holding a slash, a
#' backslash or a colon is refused before the registry is read, since the name
#' becomes the cached file's name.
#'
#' An entry's `derived` file, a lexicon already normalised, is fetched when it has
#' one and cached as it arrives. Otherwise its `openlexicon` file is fetched and
#' converted by [normalise_lexicon()] with the entry's `columns` and `duplicates`, so
#' `fetch_corpus("subtlex_us")` caches SUBTLEX-US as a lexicon. The URL's scheme is
#' checked first. The transfer then lands in a sidecar file that is renamed into
#' place only after the size cap, the markup sniff, any `sha256` the registry entry
#' carries and the normalisation have all passed. A refusal of the registry entry, a
#' failed transfer and a checksum mismatch name the registry file read. On success, a
#' message gives the corpus's citation, which [list_corpora()] also lists, and a run
#' that reads the file from the cache credits that citation in its datasheet (see
#' [build_datasheet()]). The transfer uses [utils::download.file()], so it is subject
#' to `getOption("timeout")`, 60 seconds by default, which is often too short for a
#' large file. Raise it, for example with `options(timeout = 600)`, before fetching a
#' large corpus.
#'
#' The lexica of the wordfreq connector's languages are built by the Python package
#' (`lexsync fetch fr`), and this package reads the result with [load_lexicon()]. A
#' wordfreq language code given here is refused with that explanation.
#'
#' The file lands in [lexsync_cache_dir()] unless `dest` names somewhere else.
#' The cache directory is created only once the registry entry and its URL have
#' been accepted, so a refused call writes nothing. A download to the default
#' destination begins by deleting any `.part` sidecar in the cache that an
#' interrupted transfer left there more than a day earlier. The cache persists
#' between sessions, and one corpus may reach the 200 MB download cap, so several
#' of them add up. [lexsync_cache_clear()] removes one corpus or the whole cache,
#' and the next call downloads the corpus again. A `dest` the caller names, inside
#' the cache or not, is used as given. Its directory must already exist, no
#' sidecar is swept, and the only file beside it that lexsync writes or deletes is
#' the `<dest>.part` sidecar of the download itself.
#'
#' @param name A corpus name present in the registry.
#' @param registry_path Optional path to `registry.yaml`. A path that does not exist
#'   is refused. `NULL` (the default) finds the registry as [list_corpora()]
#'   describes.
#' @param dest Optional destination file; defaults to `<name>.csv` in
#'   [lexsync_cache_dir()].
#' @return The path to the downloaded file, invisibly.
#' @importFrom utils download.file
#' @export
fetch_corpus <- function(name, registry_path = NULL, dest = NULL) {
  .check_corpus_name(name)
  reg_path <- .registry_path(registry_path)
  reg <- .read_yaml_utf8(reg_path)
  entry <- reg[["corpora"]][[name]]
  if (is.null(entry) && name %in% unlist(reg[["wordfreq_connector"]][["languages"]])) {
    stop(sprintf(paste0("lexsync: '%s' is a wordfreq language; its lexicon is built by the ",
                        "Python package (`lexsync fetch %s`), and the R package reads the ",
                        "result with load_lexicon()."), name, name), call. = FALSE)
  }
  if (is.null(entry)) {
    stop(sprintf("lexsync: corpus '%s' is not in the registry '%s'.", name, reg_path),
         call. = FALSE)
  }
  src <- .download_source(name, entry, reg_path)
  url <- src$url
  # A registry is editable, and fetch_corpus() writes wherever it points, so a
  # 'file://' or 'ftp://' entry would read a local path under the guise of a
  # download. Only the two schemes a corpus is published over are honoured.
  if (!grepl("^https?://", url, ignore.case = TRUE)) {
    stop(sprintf("lexsync: corpus '%s' registers a non-http(s) URL (%s) in '%s'; refusing to download.",
                 name, url, reg_path), call. = FALSE)
  }
  # Only now, with every refusal behind it, does the call touch the disk, and only
  # the cache is swept: a caller's `dest` may sit beside files lexsync never wrote.
  if (is.null(dest)) dest <- file.path(.prepare_cache(), paste0(name, ".csv"))
  # The transfer lands in a sidecar and is renamed over `dest` only after every
  # check below has passed, so a truncated or unverified body can never sit at
  # the cache path, where a later run would trust it.
  part <- paste0(dest, ".part")
  # download.file() reports a failed transfer as a warning under some methods and
  # as an error under others, so both are branded. Called through the import
  # rather than utils:: so the tests can substitute an offline transport; it
  # honours options(timeout), where the Python engine passes its own.
  tryCatch(
    download.file(url, part, mode = "wb", quiet = TRUE),
    error = function(e) {
      unlink(part)
      .stop_download(name, url, conditionMessage(e), reg_path)
    },
    warning = function(w) {
      unlink(part)
      .stop_download(name, url, conditionMessage(w), reg_path)
    }
  )
  # download.file() cannot stop a transfer mid-stream as the Python engine's
  # chunked reader does, so the cap is enforced on the landed sidecar instead.
  if (file.size(part) > .max_download_bytes()) {
    unlink(part)
    stop(paste0("lexsync: corpus download exceeded the 200 MB size limit. Retrieve the ",
                "delimited file manually and pass it to load_lexicon()."),
         call. = FALSE)
  }
  if (.starts_with_markup(part)) {
    unlink(part)
    stop(sprintf(paste0("lexsync: corpus '%s' returned an HTML page, not a delimited file ",
                        "(%s); the registry URL may have rotted. Retrieve the delimited file ",
                        "manually and pass it to load_lexicon()."),
                 name, url), call. = FALSE)
  }
  # 'sha256' is optional per registry entry; when present the download must
  # match it before it may enter the cache.
  if (!is.null(src$sha256) && !identical(sha256_file(part), src$sha256)) {
    unlink(part)
    stop(sprintf(paste0("lexsync: checksum mismatch for corpus '%s'; the download does not ",
                        "match the registry's sha256. Retry the download, or verify the ",
                        "sha256 recorded in '%s'."),
                 name, reg_path), call. = FALSE)
  }
  if (src$normalise) {
    # The corpus file is read into memory and its sidecar then holds the lexicon, so a
    # file that cannot be normalised leaves nothing behind either.
    # The file's name and extension, without any query or fragment.
    named <- sub("[?#].*$", "", url)
    lex <- tryCatch(.normalise(part, NULL, entry, .delimiter_for(named), basename(named)),
                    finally = unlink(part))
    message(attr(lex, "message"))
    attr(lex, "message") <- NULL
    write_csv_utf8(lex, part)
  }
  # file.rename() will not overwrite an existing file on Windows.
  if (file.exists(dest)) unlink(dest)
  file.rename(part, dest)
  message(sprintf("lexsync: downloaded '%s'. Please cite: %s", name,
                  entry[["citation"]] %||% "(see registry)"))
  invisible(dest)
}

# ---- normalise_lexicon -------------------------------------------------------
# A corpus file in its publisher's layout, made into a lexicon load_lexicon() reads. The
# registry's `columns` map names a source's columns, and its `duplicates` rule says what
# a repeated form means. Mirrors normalise_lexicon in
# python_workflow/src/lexsync/corpora.py, and the twin tests hold both engines to the
# same output bytes.

# The lexsync columns a map may name, in the order they are written.
.NORMALISE_KEYS <- c("word", "freq_zipf", "freq_permillion", "pos")
.DUPLICATE_RULES <- c("first", "sum")

# "," or a tab from a file name's extension, or NULL when it says neither.
.delimiter_for <- function(name) {
  ext <- tolower(tools::file_ext(name))
  switch(ext, tsv = "\t", tab = "\t", csv = ",", NULL)
}

# A tab when the header line holds one, and a comma otherwise. Read as bytes, so the
# session's encoding plays no part.
.sniff_delimiter <- function(path) {
  bytes <- readBin(path, "raw", n = 65536L)
  lf <- which(bytes == as.raw(10L))
  head <- if (length(lf)) bytes[seq_len(lf[1])] else bytes
  if (any(head == as.raw(9L))) "\t" else ","
}

# A registry entry given as itself, or by its name in the registry found by default.
.corpus_entry <- function(entry) {
  if (is.null(entry)) return(list())
  if (is.character(entry) && length(entry) == 1L) {
    reg_path <- default_registry_path()
    found <- .read_yaml_utf8(reg_path)[["corpora"]][[entry]]
    if (is.null(found)) {
      stop(sprintf("lexsync: corpus '%s' is not in the registry '%s'.", entry, reg_path),
           call. = FALSE)
    }
    return(found)
  }
  if (is.list(entry)) return(entry)
  stop("lexsync: 'entry' must be a registry entry or the name of one.", call. = FALSE)
}

# normalise_lexicon()'s work: the lexicon, with the line that reports on it in the
# attribute "message".
.normalise <- function(path, columns, entry, delimiter, label) {
  entry <- .corpus_entry(entry)
  cmap <- as.list(columns %||% entry[["columns"]] %||% list())
  unknown <- setdiff(names(cmap), .NORMALISE_KEYS)
  if (length(unknown)) {
    stop(sprintf(paste("lexsync: unknown key '%s' in the column map; known keys: word,",
                       "freq_zipf, freq_permillion, pos."), unknown[1]), call. = FALSE)
  }
  if (all(c("freq_zipf", "freq_permillion") %in% names(cmap))) {
    stop(paste("lexsync: the column map names both frequency columns; name freq_zipf or",
               "freq_permillion, not both."), call. = FALSE)
  }
  rule <- entry[["duplicates"]] %||% "first"
  if (!(is.character(rule) && length(rule) == 1L && rule %in% .DUPLICATE_RULES)) {
    stop(sprintf("lexsync: duplicates must be 'first' or 'sum', not '%s'.",
                 paste(rule, collapse = ", ")), call. = FALSE)
  }
  if (is.null(delimiter)) delimiter <- .delimiter_for(path) %||% .sniff_delimiter(path)
  if (!(delimiter %in% c(",", "\t"))) {
    stop("lexsync: delimiter must be ',' or a tab.", call. = FALSE)
  }
  df <- as.data.frame(read_csv_utf8(path, as_character = TRUE, delim = delimiter),
                      stringsAsFactors = FALSE)
  nm <- names(df)
  if (any(c("freq_zipf", "freq_permillion") %in% names(cmap))) {
    freq_key <- if ("freq_zipf" %in% names(cmap)) "freq_zipf" else "freq_permillion"
    freq_col <- cmap[[freq_key]]
  } else if (any(c("freq_zipf", "freq_permillion") %in% nm)) {
    freq_key <- freq_col <- if ("freq_zipf" %in% nm) "freq_zipf" else "freq_permillion"
  } else {
    stop(sprintf(paste("lexsync: '%s' has no column named freq_zipf or freq_permillion, and",
                       "the column map names neither; map one of them to the file's",
                       "frequency column."), label), call. = FALSE)
  }
  word_col <- cmap[["word"]] %||% "word"
  pos_col <- cmap[["pos"]] %||% (if ("pos" %in% nm) "pos" else NULL)
  wanted <- c(word = word_col, stats::setNames(freq_col, freq_key),
              if (!is.null(pos_col)) c(pos = pos_col))
  for (target in names(wanted)) {
    if (!(wanted[[target]] %in% nm)) {
      stop(sprintf("lexsync: '%s' has no column '%s' (mapped to %s); its columns are %s.",
                   label, wanted[[target]], target,
                   paste(sprintf("'%s'", nm), collapse = ", ")), call. = FALSE)
    }
  }
  if (identical(rule, "sum") && !identical(freq_key, "freq_permillion")) {
    stop(paste("lexsync: duplicates: sum adds frequencies per million, so the column map",
               "must name freq_permillion; Zipf values cannot be added."), call. = FALSE)
  }
  n_read <- nrow(df)
  freq <- .type_column(df[[freq_col]])
  .require_numbers(freq, freq_col)
  keep <- !is.na(df[[word_col]]) & !is.na(freq)
  words <- .lower_invariant(.trim_invariant(df[[word_col]][keep]))
  values <- as.numeric(freq[keep])
  pos <- if (!is.null(pos_col)) df[[pos_col]][keep] else NULL
  nonempty <- nzchar(words)
  words <- .nfc(words[nonempty])
  values <- values[nonempty]
  if (!is.null(pos)) pos <- pos[nonempty]
  if (!length(words)) {
    stop(sprintf(paste("lexsync: '%s' has no usable rows: every row is missing its word or",
                       "its frequency."), label), call. = FALSE)
  }
  refuse <- function(v, w) {
    stop(sprintf(paste("lexsync: column '%s' holds %s for '%s', and a frequency per million",
                       "must be positive to have a Zipf value; remove such rows first."),
                 freq_col, .fmt_g(v), w), call. = FALSE)
  }
  if (identical(freq_key, "freq_permillion")) {
    bad <- which(values < 0)
    if (length(bad)) refuse(values[bad[1]], words[bad[1]])
  }
  # One row per form: the first in file order, or under `sum` the first row's other
  # cells with the frequencies of every row added in file order.
  rows <- which(!duplicated(words))
  resolved <- if (identical(rule, "sum")) {
    groups <- split(values, factor(words, levels = unique(words)))
    vapply(groups, .exact_sum, numeric(1), USE.NAMES = FALSE)
  } else {
    values[rows]
  }
  forms <- words[rows]
  derived <- identical(freq_key, "freq_permillion")
  if (derived) {
    bad <- which(resolved <= 0)
    if (length(bad)) refuse(resolved[bad[1]], forms[bad[1]])
    zp <- .zipf_from_permillion(resolved)
    zipf <- zp$zipf
    near <- zp$near_boundary
  } else {
    .check_zipf_range(resolved)
    zipf <- resolved
    near <- 0L
  }
  out <- data.frame(word = forms, freq_zipf = zipf, stringsAsFactors = FALSE)
  if (derived) out$freq_permillion <- resolved
  if (!is.null(pos)) out$pos <- pos[rows]
  # UTF-8 byte order, the order load_lexicon() gives a lexicon in both engines.
  out <- out[order(out$word, method = "radix"), , drop = FALSE]
  rownames(out) <- NULL
  attr(out, "normalisation") <- list(
    n_read = as.integer(n_read), n_forms = nrow(out),
    n_merged = as.integer(length(words) - nrow(out)), duplicates = rule,
    zipf_derived = derived, near_boundary = as.integer(near))
  attr(out, "message") <- paste0(
    sprintf("lexsync: normalised %d form%s from '%s'", nrow(out),
            if (nrow(out) == 1L) "" else "s", label),
    if (derived) sprintf(paste0("; %d of the Zipf values derived from frequencies per ",
                                "million lay within 1e-9 of a rounding boundary."),
                         as.integer(near))
    else ".")
  out
}

#' Turn a corpus file in its publisher's layout into a lexicon
#'
#' Reads a tab- or comma-separated corpus file, such as SUBTLEX-US or Lexique as they
#' are published, and returns a lexicon that [load_lexicon()] reads, writing it to
#' `out` when given.
#'
#' Words are trimmed, lower-cased and put in Unicode NFC, as [load_lexicon()] keys
#' them, and rows missing a word or a frequency are dropped. A form that then appears
#' more than once is resolved by the entry's `duplicates` rule: `"first"` (the
#' default) keeps the first row in file order, and `"sum"` adds its rows' frequencies
#' per million, as Lexique needs, since it splits a homograph's frequency between its
#' rows. Frequencies per million are converted with Zipf = log10(per million) + 3,
#' rounded to three places by lexsync's shared rounder. A value of 0 or below has no
#' Zipf value and is refused. Zipf values read as they are must lie between 0 and 9.
#'
#' A message gives the number of forms and, for derived Zipf values, the number that
#' lay within 1e-9 of a rounding boundary after scaling. That is the only step at which
#' the two engines' `log10` could round a value apart, and the count is expected to be
#' 0. A run over the lexicon records the count in its run log and datasheet.
#'
#' @param path Path to the corpus file.
#' @param columns Optional named list mapping lexsync's column names to the file's, as
#'   a registry entry's `columns` does: `word`, one of `freq_zipf` and
#'   `freq_permillion`, and optionally `pos`. Without a map, the entry's is used, and
#'   without either the file's own `word`, `freq_zipf` or `freq_permillion`, and `pos`
#'   columns are read.
#' @param entry Optional registry entry, as a list, or the name of one in the
#'   registry lexsync finds by default (see [list_corpora()]). It supplies the map
#'   when `columns` is `NULL`, and the `duplicates` rule.
#' @param delimiter `","` or a tab character. Left `NULL`, it is taken from the
#'   extension (`.tsv` and `.tab` are tab-separated, `.csv` comma-separated) and
#'   otherwise from the header line, which is tab-separated when it holds a tab. A
#'   tab-separated file is read with no quoting.
#' @param out Optional path to write the lexicon to, comma-separated with LF line
#'   endings.
#' @return The lexicon, invisibly when `out` is given: a data frame with `word`,
#'   `freq_zipf`, then `freq_permillion` when Zipf was derived from it, and `pos`
#'   when the file has one, in the UTF-8 byte order of `word`. Its attribute
#'   `normalisation` holds `list(n_read, n_forms, n_merged, duplicates,
#'   zipf_derived, near_boundary)`.
#' @seealso [fetch_corpus()], which downloads a registered corpus and normalises it
#'   the same way.
#' @examples
#' # A SUBTLEX-US-like table, written to a temporary file.
#' path <- tempfile(fileext = ".tsv")
#' writeLines(c("Word\tSUBTLWF\tDom_PoS_SUBTLEX", "the\t29449.18\tArticle",
#'              "Dog\t192.76\tNoun"), path)
#' normalise_lexicon(path, columns = list(word = "Word", freq_permillion = "SUBTLWF",
#'                                        pos = "Dom_PoS_SUBTLEX"))
#' unlink(path)
#' @export
normalise_lexicon <- function(path, columns = NULL, entry = NULL, delimiter = NULL,
                              out = NULL) {
  lex <- .normalise(path, columns, entry, delimiter, basename(path))
  message(attr(lex, "message"))
  attr(lex, "message") <- NULL
  if (is.null(out)) return(lex)
  write_csv_utf8(lex, out)
  invisible(lex)
}
