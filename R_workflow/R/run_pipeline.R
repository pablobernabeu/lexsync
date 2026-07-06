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
  items_cfg <- design$items %||% list()
  source <- items_cfg$source %||% "corpus"
  paradigm <- design$paradigm %||% "factorial"
  is_continuous <- identical(source, "corpus") && !is.null(design$continuous)

  log <- new_run_log(design$name, meta = list(
    design = design$name, language = design$language,
    paradigm = paradigm, source = source, seed = schema$seed %||% NA,
    mode = if (is_continuous) "continuous" else "conditions"
  ))

  report <- NULL
  if (source %in% c("corpus", "generate")) {
    lexicon <- items_cfg$lexicon %||% design$lexicon
    log <- log_step(log, sprintf("loading lexicon '%s'", lexicon))
    lex <- load_lexicon(lexicon, schema, language = design$language)
    log <- log_step(log, sprintf("lexicon loaded: %d words", nrow(lex)), list(words = nrow(lex)))
    pool <- build_pool(lex, design$pool_filters)
    log <- log_step(log, sprintf("pool after filters: %d words", nrow(pool)), list(pool = nrow(pool)))
  }

  if (source == "corpus") {
    match_on <- unlist(design$match_on, use.names = FALSE)
    ref <- reference_words %||% lex$word
    needed <- intersect(c("n_density", "old20"), match_on)
    if (length(needed) && any(!needed %in% names(pool))) {
      log <- log_step(log, "computing orthographic neighbourhood (N, OLD20)")
      pool <- add_neighbourhood(pool, reference = ref)
    }
    if ("bigram_freq" %in% match_on && !("bigram_freq" %in% names(pool))) {
      log <- log_step(log, "computing bigram frequency (phonotactic-probability proxy)")
      pool <- add_bigram_frequency(pool, reference = ref)
    }
    if (is_continuous) {
      predictor <- design$continuous$predictor
      controls <- unlist(design$continuous$controls, use.names = FALSE)
      stim <- select_continuous_stimuli(pool, design, schema, verbose = verbose)
      log <- log_step(log, sprintf("selected %d items spanning '%s' (continuous design)",
                                   nrow(stim), predictor), list(predictor = predictor))
      report <- match_report_continuous(stim, predictor, controls, schema)
    } else {
      if (!is.null(design$resample)) {
        stim <- resample_stimuli(pool, design, schema, design$resample$n_sets %||% 2L, verbose = verbose)
        log <- log_step(log, sprintf("resampled %d disjoint matched sets (%d items total)",
                                     length(unique(stim$replicate)), nrow(stim)),
                        list(conditions = paste(unique(stim$condition), collapse = ", ")))
      } else {
        stim <- match_stimuli(pool, design, schema, verbose = verbose)
        log <- log_step(log, sprintf("matched %d items across %d conditions",
                                     nrow(stim), length(unique(stim$condition))),
                        list(conditions = paste(unique(stim$condition), collapse = ", ")))
      }
      std <- c("length", "frequency", "n_density", "old20")
      extra <- intersect(c("n_syllables", "bigram_freq"), match_on)
      dims <- intersect(c(std, extra), names(stim))
      report <- match_report(stim, dims, schema)
    }
  } else if (source == "generate") {
    n <- design$n_per_condition %||% design$n_per_cell %||% 40L
    stim <- build_lexdec_stimuli(pool, n, reference_words = lex$word)
    log <- log_step(log, sprintf("generated %d items (words + pseudowords)", nrow(stim)),
                    list(conditions = paste(unique(stim$condition), collapse = ", ")))
    report <- match_report(stim, "length", schema)
  } else if (source == "table") {
    path <- items_cfg$path
    log <- log_step(log, sprintf("loading items '%s'", path))
    stim <- load_items(path, required_fields(design))
    log <- log_step(log, sprintf("loaded %d items across %d conditions",
                                 length(unique(stim$set)), length(unique(stim$condition))),
                    list(conditions = paste(unique(stim$condition), collapse = ", ")))
  } else {
    stop(sprintf("lexsync: unknown item source '%s'.", source), call. = FALSE)
  }

  if (!is.null(report)) {
    for (msg in balance_check(stim, "condition")) log <- log_step(log, paste("balance:", msg))
    if (is_continuous) {
      for (i in seq_len(nrow(report$comparisons))) {
        cr <- report$comparisons[i, ]
        if (identical(cr$role, "control"))
          log <- log_step(log, sprintf("continuous: '%s' correlation with the predictor r = %s",
                                       cr$dimension, format(cr$pearson_r)))
      }
    } else {
      for (i in seq_len(nrow(report$comparisons))) {
        cr <- report$comparisons[i, ]
        ci <- if (!is.na(cr$d_ci_low) && !is.na(cr$d_ci_high))
          sprintf(" [%.2f, %.2f]", cr$d_ci_low, cr$d_ci_high) else ""
        log <- log_step(log, sprintf("equivalence %s vs %s on '%s': d = %.2f%s, TOST p = %.3f (%s)",
                                     cr$condition, cr$reference, cr$dimension, cr$cohens_d, ci, cr$tost_p,
                                     if (isTRUE(cr$equivalent)) "equivalent" else "not shown equivalent"))
      }
    }
  }

  stim <- counterbalance(stim, design, schema)

  base <- slugify(design$name, design$language)
  for (sub in c("stimuli", "reports", "experiments")) {
    dir.create(file.path(outdir, sub), recursive = TRUE, showWarnings = FALSE)
  }

  stim_path <- file.path(outdir, "stimuli", paste0(base, "_stimuli_R.csv"))
  write_csv_utf8(stim, stim_path); log <- log_artefact(log, stim_path, nrow(stim))

  desc_path <- comp_path <- NULL
  if (!is.null(report)) {
    desc_path <- file.path(outdir, "reports", paste0(base, "_descriptives_R.csv"))
    write_csv_utf8(report$descriptives, desc_path); log <- log_artefact(log, desc_path, nrow(report$descriptives))
    comp_path <- file.path(outdir, "reports", paste0(base, "_comparisons_R.csv"))
    write_csv_utf8(report$comparisons, comp_path); log <- log_artefact(log, comp_path, nrow(report$comparisons))
  }

  exps <- export_experiments(stim, design, schema, file.path(outdir, "experiments"), base)
  for (p in exps) log <- log_artefact(log, p)

  # A materials datasheet (machine + human readable) and a pre-registration
  # template: the shareable provenance record the reproducibility literature asks
  # for (Bochynska et al., 2023; Roettger, 2019).
  source_path <- items_cfg$path %||% items_cfg$lexicon %||% design$lexicon
  artifacts <- list(stimuli = stim_path, descriptives = desc_path,
                    comparisons = comp_path, experiments = exps)
  candidate_pool <- NULL
  if (is_continuous) {
    candidate_pool <- list(list(condition = "continuous", n_candidates = nrow(pool)))
  } else if (identical(source, "corpus")) {
    candidate_pool <- lapply(design$conditions, function(cnd)
      list(condition = cnd$name, n_candidates = nrow(build_pool(pool, cnd$define_by))))
  } else if (identical(source, "generate")) {
    candidate_pool <- list(list(condition = "words in band", n_candidates = nrow(pool)))
  }
  ds <- build_datasheet(design, schema, report, stim, source_path, artifacts,
                        schema$seed, engine = "R", candidate_pool = candidate_pool)
  ds_json <- file.path(outdir, "reports", paste0(base, "_datasheet_R.json"))
  ds_md <- file.path(outdir, "reports", paste0(base, "_datasheet_R.md"))
  write_datasheet(ds, ds_json, ds_md)
  log <- log_artefact(log, ds_json); log <- log_artefact(log, ds_md)

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
