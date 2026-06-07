# run_pipeline.R -- the orchestrator. For each design it loads a lexicon, builds
# the candidate pool, computes any missing dimensions, matches stimuli across
# conditions, counterbalances, writes the descriptive-statistics report and the
# run log, and exports the PsychoPy and OpenSesame scripts. run_all() loops over
# every design configuration, automating the work across languages and designs.

#' Run the lexsync pipeline for one design
#'
#' @param design_path Path to a design configuration (YAML).
#' @param schema_path Path to the global schema (YAML).
#' @param outdir Output directory (subdirectories `stimuli`, `reports`,
#'   `experiments` are created).
#' @param reference_words Optional reference word list for neighbourhood
#'   computation; defaults to the whole lexicon.
#' @param verbose Logical; print progress.
#' @return A named list of output paths, invisibly.
#' @export
run_pipeline <- function(design_path, schema_path = "config/schema.yaml",
                         outdir = "output", reference_words = NULL, verbose = TRUE) {
  options(lexsync.verbose = verbose)
  schema <- read_config(schema_path)
  design <- read_config(design_path)

  log <- new_run_log(design$name, meta = list(
    design = design$name, language = design$language, lexicon = design$lexicon,
    seed = schema$seed %||% NA, match_on = paste(unlist(design$match_on), collapse = ", ")
  ))

  log <- log_step(log, sprintf("loading lexicon '%s'", design$lexicon))
  lex <- load_lexicon(design$lexicon, schema, language = design$language)
  log <- log_step(log, sprintf("lexicon loaded: %d words", nrow(lex)), list(words = nrow(lex)))

  pool <- build_pool(lex, design$pool_filters)
  log <- log_step(log, sprintf("pool after filters: %d words", nrow(pool)), list(pool = nrow(pool)))

  match_on <- unlist(design$match_on, use.names = FALSE)
  needed <- intersect(c("n_density", "old20"), match_on)
  if (length(needed) && any(!needed %in% names(pool))) {
    log <- log_step(log, "computing orthographic neighbourhood (N, OLD20)")
    pool <- add_neighbourhood(pool, reference = reference_words %||% lex$word)
  }

  stim <- match_stimuli(pool, design, schema, verbose = verbose)
  log <- log_step(log, sprintf("matched %d items across %d conditions",
                               nrow(stim), length(unique(stim$condition))),
                  list(conditions = paste(unique(stim$condition), collapse = ", ")))

  # The match report is computed on the matched set before counterbalancing, so
  # the reference condition is always the matching anchor (the first condition).
  dims <- unique(c("length", "frequency", match_on))
  report <- match_report(stim, dims, schema)
  for (msg in balance_check(stim, "condition")) log <- log_step(log, paste("balance:", msg))
  for (i in seq_len(nrow(report$comparisons))) {
    cr <- report$comparisons[i, ]
    log <- log_step(log, sprintf("equivalence %s vs %s on '%s': d = %.2f, TOST p = %.3f (%s)",
                                 cr$condition, cr$reference, cr$dimension, cr$cohens_d, cr$tost_p,
                                 if (isTRUE(cr$equivalent)) "equivalent" else "not shown equivalent"))
  }

  stim <- counterbalance(stim, design, schema)

  base <- slugify(design$name, design$language)
  for (sub in c("stimuli", "reports", "experiments")) {
    dir.create(file.path(outdir, sub), recursive = TRUE, showWarnings = FALSE)
  }

  stim_path <- file.path(outdir, "stimuli", paste0(base, "_stimuli_R.csv"))
  write_csv_utf8(stim, stim_path); log <- log_artefact(log, stim_path, nrow(stim))

  desc_path <- file.path(outdir, "reports", paste0(base, "_descriptives_R.csv"))
  write_csv_utf8(report$descriptives, desc_path); log <- log_artefact(log, desc_path, nrow(report$descriptives))

  comp_path <- file.path(outdir, "reports", paste0(base, "_comparisons_R.csv"))
  write_csv_utf8(report$comparisons, comp_path); log <- log_artefact(log, comp_path, nrow(report$comparisons))

  exps <- export_experiments(stim, design, schema, file.path(outdir, "experiments"), base)
  for (p in exps) log <- log_artefact(log, p)

  log_md <- file.path(outdir, "reports", paste0(base, "_run_log_R.md"))
  write_run_log(log, log_md, file.path(outdir, "reports", paste0(base, "_run_log_R.jsonl")))

  if (verbose) cat(sprintf("[lexsync] design '%s' complete.\n", base))
  invisible(list(stimuli = stim_path, descriptives = desc_path, comparisons = comp_path,
                 experiments = exps, log = log_md))
}

#' Run the lexsync pipeline for every design configuration
#'
#' @param config_dir Directory of `design_*.yaml` configurations.
#' @param schema_path Path to the global schema.
#' @param outdir Output directory.
#' @param verbose Logical; print progress.
#' @return A named list of per-design results, invisibly.
#' @export
run_all <- function(config_dir = "config", schema_path = file.path(config_dir, "schema.yaml"),
                    outdir = "output", verbose = TRUE) {
  designs <- list.files(config_dir, pattern = "^design_.*\\.ya?ml$", full.names = TRUE)
  if (!length(designs)) stop(sprintf("lexsync: no design_*.yaml files in '%s'.", config_dir), call. = FALSE)
  results <- list()
  for (d in designs) {
    if (verbose) cat(sprintf("\n=== lexsync: design '%s' ===\n", basename(d)))
    results[[basename(d)]] <- run_pipeline(d, schema_path, outdir, verbose = verbose)
  }
  if (verbose) cat(sprintf("\n[lexsync] all %d designs complete.\n", length(designs)))
  invisible(results)
}
