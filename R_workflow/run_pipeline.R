#!/usr/bin/env Rscript
# Thin command-line wrapper that runs every lexsync demonstration design.
# Usage (from the repository root):  Rscript R_workflow/run_pipeline.R
# It uses the installed 'lexsync' package if available, otherwise it sources the
# package sources directly, so it works before installation too.
#
# That preference is a trap when editing the package: with lexsync installed,
# edits under R_workflow/R are silently ignored until the package is
# reinstalled (install.packages("R_workflow", repos = NULL, type = "source")
# from the repository root) or the installed copy is removed
# (remove.packages("lexsync")). The Python wrapper prefers the source tree, so
# the two engines can quietly run different code. The startup message below
# says which copy this run loaded.

local({
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", args, value = TRUE)
  script_path <- if (length(file_arg)) {
    sub("^--file=", "", file_arg[1])
  } else {
    # source() never sets --file=; it records the path as `ofile` in its own
    # frame, so scan the call stack for the innermost source() frame.
    of <- NULL
    for (i in seq_len(sys.nframe())) {
      o <- tryCatch(get("ofile", envir = sys.frame(i)), error = function(e) NULL)
      if (is.character(o) && length(o) == 1L) of <- o
    }
    of
  }
  script_dir <- if (!is.null(script_path)) dirname(normalizePath(script_path)) else getwd()
  repo <- normalizePath(file.path(script_dir, ".."), mustWork = FALSE)
  if (!file.exists(file.path(repo, "config", "schema.yaml"))) {
    # Last resort: the caller's working directory may itself be the repo root.
    if (file.exists(file.path(getwd(), "config", "schema.yaml"))) {
      repo <- getwd()
      script_dir <- file.path(repo, "R_workflow")
    } else {
      stop("run_pipeline.R cannot locate the lexsync repository root from here.\n",
           "  Run it from the repository root as:  Rscript R_workflow/run_pipeline.R",
           call. = FALSE)
    }
  }

  if (requireNamespace("lexsync", quietly = TRUE)) {
    library(lexsync)
    # message(), not cat(): stderr, so no artefact or redirected stdout captures it.
    message(sprintf(paste0("run_pipeline.R: using the INSTALLED lexsync %s, not the ",
                           "sources under R_workflow/R; reinstall after editing them, ",
                           "or remove the installed package to run from source."),
                    as.character(utils::packageVersion("lexsync"))))
  } else {
    src <- list.files(file.path(script_dir, "R"), pattern = "[.][Rr]$", full.names = TRUE)
    invisible(lapply(src, source))
    message("run_pipeline.R: no installed lexsync; running from the sources under R_workflow/R.")
  }

  old <- setwd(repo)
  on.exit(setwd(old), add = TRUE)
  run_all(config_dir = "config", schema_path = "config/schema.yaml", outdir = "output")
})
