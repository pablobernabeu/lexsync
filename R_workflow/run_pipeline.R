#!/usr/bin/env Rscript
# Thin command-line wrapper that runs every lexsync demonstration design.
# Usage (from the repository root):  Rscript R_workflow/run_pipeline.R
# It uses the installed 'lexsync' package if available, otherwise it sources the
# package sources directly, so it works before installation too.

local({
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", args, value = TRUE)
  script_dir <- if (length(file_arg)) {
    dirname(normalizePath(sub("^--file=", "", file_arg[1])))
  } else {
    getwd()
  }
  repo <- normalizePath(file.path(script_dir, ".."), mustWork = FALSE)

  if (requireNamespace("lexsync", quietly = TRUE)) {
    library(lexsync)
  } else {
    src <- list.files(file.path(script_dir, "R"), pattern = "[.][Rr]$", full.names = TRUE)
    invisible(lapply(src, source))
  }

  old <- setwd(repo)
  on.exit(setwd(old), add = TRUE)
  run_all(config_dir = "config", schema_path = "config/schema.yaml", outdir = "output")
})
