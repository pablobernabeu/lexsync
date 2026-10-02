# paths.R -- which schema a run reads. run_pipeline() and run_all() resolve the
# schema here, as the Python command line and API do in paths.py, so the entry
# points cannot disagree about which file a run used. Mirrors paths.py.

# The schema shipped inside the package. It is byte-identical to the repository's
# config/schema.yaml (test-config.R enforces the identity), so an installed package
# runs anywhere.
.bundled_schema <- function() system.file("extdata", "schema.yaml", package = "lexsync")

# Resolve the schema for a run, returning list(path, origin).
#
# A named `schema_path` is used as given and must exist. It is never replaced by
# another file, since that would run a different schema from the one the caller
# chose. With no schema named, the candidates are tried in order: for a folder of
# designs (`config_dir` given), <config_dir>/schema.yaml and then config/schema.yaml
# in the working directory; for a single design, config/schema.yaml in the working
# directory and then schema.yaml in the design's own directory; in both cases, last,
# the bundled copy. The first candidate in each list is the default these functions
# had before, so a call that worked then reads the same file now. Whenever no schema
# was named, message() reports the path chosen. The run log and the datasheet record
# it as well, for a caller whose messages are suppressed.
#
# `origin` is one of "named", "config_dir", "working_directory", "design_directory"
# or "bundled".
.resolve_schema <- function(schema_path = NULL, design_path = NULL, config_dir = NULL) {
  if (!is.null(schema_path)) {
    if (!file.exists(schema_path) || dir.exists(schema_path)) {
      stop(sprintf(paste0("lexsync: schema not found: '%s'. The schema bundled with ",
                          "lexsync is system.file(\"extdata\", \"schema.yaml\", ",
                          "package = \"lexsync\"), at '%s'."),
                   schema_path, .bundled_schema()), call. = FALSE)
    }
    return(list(path = schema_path, origin = "named"))
  }
  cwd_config <- list(path = file.path("config", "schema.yaml"), origin = "working_directory")
  candidates <- if (!is.null(config_dir)) {
    list(list(path = .join_path(config_dir, "schema.yaml"), origin = "config_dir"), cwd_config)
  } else {
    c(list(cwd_config),
      if (!is.null(design_path))
        list(list(path = file.path(dirname(design_path), "schema.yaml"),
                  origin = "design_directory")))
  }
  candidates <- c(candidates, list(list(path = .bundled_schema(), origin = "bundled")))
  for (cand in candidates) {
    if (nzchar(cand$path) && file.exists(cand$path) && !dir.exists(cand$path)) {
      # In POSIX form, as the run log and the datasheet record it.
      message(sprintf("lexsync: using the schema at '%s'", .posix_path(cand$path)))
      return(cand)
    }
  }
  stop(paste0("lexsync: no schema found, and the copy bundled with lexsync is ",
              "missing; reinstall the package."), call. = FALSE)
}

# A path in POSIX form, as the datasheet and run log record it. file.path() already
# joins with "/", but a caller on Windows can name a path with backslashes.
.posix_path <- function(path) if (is.null(path)) NULL else gsub("\\", "/", path, fixed = TRUE)

# Join a directory and a file name as Python's os.path.join does: a directory that
# already ends in a separator gains none, so `run_all("study/")` records
# "study/schema.yaml" in both engines where file.path() would give "study//schema.yaml".
.join_path <- function(dir, file) {
  if (grepl("[/\\\\]$", dir)) paste0(dir, file) else file.path(dir, file)
}
