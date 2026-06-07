# corpora.R -- access to the many-language corpus registry. The R package reads
# the bundled, pre-derived lexica for the demonstrations and can download
# CSV-format corpora (Connector A) on demand into a user cache. The wordfreq
# connector (Connector B, ~40 languages) is provided by the Python package; its
# pre-derived outputs are read here as ordinary lexica.

#' Per-user cache directory for fetched corpora
#'
#' @return A writable cache directory path (created if absent).
#' @importFrom tools R_user_dir
#' @export
lexsync_cache_dir <- function() {
  d <- tools::R_user_dir("lexsync", "cache")
  dir.create(d, recursive = TRUE, showWarnings = FALSE)
  d
}

#' Locate the corpus registry
#' @keywords internal
default_registry_path <- function() {
  cand <- c(
    getOption("lexsync.registry", ""),
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

#' List the corpora known to the registry
#'
#' @param registry_path Optional path to `registry.yaml`.
#' @return A data frame describing each registered corpus.
#' @importFrom yaml read_yaml
#' @export
list_corpora <- function(registry_path = NULL) {
  reg <- yaml::read_yaml(registry_path %||% default_registry_path())
  corp <- reg$corpora
  data.frame(
    name = names(corp),
    language = vapply(corp, function(x) x$language$name %||% NA_character_, character(1)),
    iso = vapply(corp, function(x) x$language$iso %||% NA_character_, character(1)),
    status = vapply(corp, function(x) x$status %||% NA_character_, character(1)),
    connector = vapply(corp, function(x) x$connector %||% "openlexicon", character(1)),
    citation = vapply(corp, function(x) x$citation %||% NA_character_, character(1)),
    stringsAsFactors = FALSE, row.names = NULL
  )
}

#' Download a CSV-format registered corpus into the cache
#'
#' Suitable for Connector A corpora that expose a delimited file. The download
#' is recorded so it can be cited; consult [list_corpora()] for the citation.
#'
#' @param name A corpus name present in the registry.
#' @param registry_path Optional path to `registry.yaml`.
#' @param dest Optional destination path; defaults to the cache.
#' @return The path to the downloaded file, invisibly.
#' @importFrom yaml read_yaml
#' @importFrom utils download.file
#' @export
fetch_corpus <- function(name, registry_path = NULL, dest = NULL) {
  reg <- yaml::read_yaml(registry_path %||% default_registry_path())
  entry <- reg$corpora[[name]]
  if (is.null(entry)) {
    stop(sprintf("lexsync: corpus '%s' is not in the registry.", name), call. = FALSE)
  }
  url <- entry$openlexicon %||% entry$url
  if (is.null(url)) {
    stop(sprintf("lexsync: corpus '%s' has no downloadable URL; see corpora/registry.yaml.", name),
         call. = FALSE)
  }
  dest <- dest %||% file.path(lexsync_cache_dir(), paste0(name, ".csv"))
  utils::download.file(url, dest, mode = "wb", quiet = TRUE)
  message(sprintf("lexsync: downloaded '%s'. Please cite: %s", name, entry$citation %||% "(see registry)"))
  invisible(dest)
}
