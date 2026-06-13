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
#' @return A [tibble][tibble::tibble] data frame.
#' @importFrom readr read_csv locale
#' @keywords internal
read_csv_utf8 <- function(path) {
  if (!file.exists(path)) {
    stop(sprintf("lexsync: file not found: '%s'", path), call. = FALSE)
  }
  readr::read_csv(
    path,
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
  tolower(gsub("^_|_$", "", s))
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
