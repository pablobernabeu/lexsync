# datasheet.R -- materials datasheet and pre-registration template. A machine- and
# human-readable provenance record for a design: where the items came from, how
# they were selected and matched, the realised control, how they were
# counterbalanced, and the seeds, versions and checksums needed to reproduce them
# exactly. The shareable materials record whose scarcity motivates lexsync
# (Bochynska et al., 2023; Roettger, 2019). Mirrors datasheet.py.

DATASHEET_VERSION <- "1.0"

.versions_R <- function(engine) {
  v <- list(engine = engine,
            lexsync = tryCatch(as.character(utils::packageVersion("lexsync")),
                               error = function(e) "0.1.0"),
            R = paste(R.version$major, R.version$minor, sep = "."))
  for (p in c("readr", "stringdist", "jsonlite", "digest")) {
    pv <- tryCatch(as.character(utils::packageVersion(p)), error = function(e) NULL)
    if (!is.null(pv)) v[[p]] <- pv
  }
  v
}

# Whether the R and Python engines select byte-identical materials. The
# deterministic methods are byte-identical; mahalanobis and optimal are the
# exception (covariance inverse / assignment solver; see matching.R). Mirrors
# datasheet.py.
.cross_engine <- function(method, source) {
  if (identical(source, "table")) return("n/a (user-supplied items)")
  if (!is.null(method) && method %in% c("mahalanobis", "optimal"))
    return("approximate (platform linear algebra)")
  "byte-identical"
}

.controlled_dims <- function(design, source) {
  if (identical(source, "corpus")) unlist(design$match_on, use.names = FALSE)
  else if (identical(source, "generate")) "length"
  else character(0)
}

.r4 <- function(v) if (is.null(v) || is.na(v)) NULL else round(as.numeric(v), 4)

# A suggested crossed mixed-model formula for the design. Handing the user an
# items-crossed model guards against the language-as-fixed-effect fallacy
# (Clark, 1973; Baayen et al., 2008): items are a random sample of the language,
# so an analysis that treats them as fixed over-generalises. Mirrors datasheet.py.
.analysis_R <- function(design, source) {
  paradigm <- design$paradigm %||% "factorial"
  if (identical(source, "generate") || identical(paradigm, "lexical_decision")) {
    factor <- "lexicality"; item_re <- "(1 | item)"
  } else if (paradigm %in% c("priming", "self_paced_reading")) {
    factor <- "condition"; item_re <- "(1 + condition | item)"
  } else {
    factor <- "condition"; item_re <- "(1 | item)"
  }
  list(
    response = "the trial outcome (e.g. reaction time or accuracy)",
    suggested_model = sprintf("response ~ %s + (1 + %s | subject) + %s", factor, factor, item_re),
    note = paste0("Crossed random effects for subjects and items guard against the ",
                  "language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). ",
                  "Begin with this maximal structure (Barr et al., 2013) and reduce it ",
                  "if the model does not converge (Matuschek et al., 2017); fit with ",
                  "lme4 in R or pymer4/statsmodels in Python.")
  )
}

#' Assemble the materials datasheet for one design
#' @param candidate_pool Optional list of per-condition candidate-pool sizes
#'   (`list(condition, n_candidates)`) recording how many items satisfied each
#'   condition's window before matching; reported for selection transparency.
#' @keywords internal
build_datasheet <- function(design, schema, report, stimuli, source_path, artifacts,
                            seed, engine = "R", candidate_pool = NULL) {
  source <- design$items$source %||% "corpus"
  controlled <- .controlled_dims(design, source)
  conditions <- unique(as.character(stimuli$condition))

  realised <- list()
  if (!is.null(report)) {
    cmp <- report$comparisons
    for (i in seq_len(nrow(cmp))) {
      realised[[length(realised) + 1L]] <- list(
        dimension = cmp$dimension[i],
        role = if (cmp$dimension[i] %in% controlled) "controlled" else "manipulated/free",
        cohens_d = .r4(cmp$cohens_d[i]),
        ci_low = .r4(cmp$d_ci_low[i]), ci_high = .r4(cmp$d_ci_high[i]),
        tost_p = .r4(cmp$tost_p[i]),
        equivalent = if (is.na(cmp$equivalent[i])) NULL else isTRUE(cmp$equivalent[i])
      )
    }
  }

  selection <- if (identical(source, "corpus")) {
    list(method = design$matching$method %||% schema$matching$method %||% "standardised_euclidean",
         match_on = as.list(controlled), tolerance_k = schema$matching$tolerance_k)
  } else if (identical(source, "generate")) {
    list(method = "constrained letter substitution (deterministic pseudowords)",
         matched_on = list("length"))
  } else {
    list(method = "item table (user-supplied)")
  }
  if (!is.null(candidate_pool) && source %in% c("corpus", "generate"))
    selection$candidate_pool <- candidate_pool
  selection$cross_engine <- .cross_engine(selection$method, source)

  list(
    lexsync_datasheet_version = DATASHEET_VERSION,
    design = list(name = design$name, language = design$language,
                  paradigm = design$paradigm %||% "factorial", source = source,
                  description = design$description,
                  n_per_condition = design$n_per_condition %||% design$n_per_cell),
    materials_source = list(
      type = source, path = source_path, sha256 = sha256_file(source_path),
      provenance = if (source %in% c("corpus", "generate"))
        "see corpora/ATTRIBUTION.md for corpus licence and citation"
      else "user-supplied item table"),
    dimensions = schema$dimensions,
    selection = selection,
    analysis = .analysis_R(design, source),
    realised_control = realised,
    counterbalancing = list(
      recipe = if (identical(source, "table")) "latin_square_target" else "factorial",
      lists = design$counterbalance$lists %||% 1L),
    resampling = if (!is.null(design$resample))
      list(n_sets = design$resample$n_sets, disjoint = TRUE) else NULL,
    items = list(n_total = nrow(stimuli), n_conditions = length(conditions),
                 conditions = as.list(conditions),
                 stimuli_file = artifacts$stimuli, stimuli_sha256 = sha256_file(artifacts$stimuli)),
    reproducibility = list(seed = seed, versions = .versions_R(engine)),
    artifacts = lapply(Filter(Negate(is.null), .artifact_paths(artifacts)),
                       function(p) list(file = p, sha256 = sha256_file(p)))
  )
}

.artifact_paths <- function(artifacts) {
  c(artifacts$stimuli, artifacts$descriptives, artifacts$comparisons,
    unlist(artifacts$experiments, use.names = FALSE))
}

#' @keywords internal
methods_paragraph <- function(ds) {
  d <- ds$design
  src <- ds$materials_source$type
  n <- d$n_per_condition
  lang <- paste0(toupper(substring(d$language, 1, 1)), substring(d$language, 2))
  if (identical(src, "corpus")) {
    ctrl <- paste(unlist(ds$selection$match_on), collapse = ", ")
    lead <- sprintf(paste0("%s items per condition were selected from the %s lexicon (%s) and ",
                           "matched item by item on %s using lexsync's %s matcher"),
                    n, lang, ds$materials_source$provenance, ctrl, ds$selection$method)
  } else if (identical(src, "generate")) {
    lead <- sprintf(paste0("%s real %s words and %s length-matched pseudowords (generated by %s) ",
                           "were assembled for a lexical-decision contrast"),
                    n, lang, n, ds$selection$method)
  } else {
    per <- ds$items$n_total %/% max(1L, ds$items$n_conditions)
    lead <- sprintf("%s items were drawn from an item table for a %s design (%s)",
                    per, d$paradigm, lang)
  }
  ctrl_rows <- Filter(function(r) identical(r$role, "controlled") && !is.null(r$ci_high), ds$realised_control)
  control <- ""
  if (length(ctrl_rows)) {
    worst <- ctrl_rows[[which.max(vapply(ctrl_rows, function(r) abs(r$cohens_d), numeric(1)))]]
    control <- sprintf(paste0(". The realised control was close. The largest standardised difference ",
                              "on any matched dimension was %.2f (90%% CI [%.2f, %.2f]), within the ",
                              "0.5-SD equivalence bound"),
                       abs(worst$cohens_d), worst$ci_low, worst$ci_high)
  }
  resamp <- if (!is.null(ds$resampling))
    sprintf(". %s disjoint matched item sets were drawn, so items can be treated as a random factor",
            ds$resampling$n_sets) else ""
  cb <- ds$counterbalancing
  recipe_label <- switch(cb$recipe,
                         latin_square_target = "a Latin-square rotation",
                         factorial = "a factorial split",
                         cb$recipe)
  tail <- sprintf(paste0(resamp, ". Materials were counterbalanced into %s list(s) (%s) and generated for ",
                         "PsychoPy, OpenSesame and jsPsych. The selection is deterministic and ",
                         "reproducible (seed %s; lexsync %s)."),
                  cb$lists, recipe_label, ds$reproducibility$seed, ds$reproducibility$versions$lexsync)
  cp <- ds$selection$candidate_pool
  pool_note <- ""
  if (!is.null(cp) && length(cp)) {
    sizes <- vapply(cp, function(x) if (is.null(x$n_candidates)) NA_real_ else as.numeric(x$n_candidates),
                    numeric(1))
    sizes <- sizes[!is.na(sizes)]
    if (length(sizes))
      pool_note <- sprintf(paste0(". The smallest condition was selected from %d eligible ",
                                  "candidates, and the selection was deterministic and blind ",
                                  "to any outcome measure"), as.integer(min(sizes)))
  }
  ce <- ds$selection$cross_engine %||% ""
  ce_note <- if (startsWith(ce, "approximate"))
    paste0(". This design's matching method uses a covariance inverse or an assignment ",
           "solver, so the R and Python engines select equivalent but not byte-identical ",
           "materials") else ""
  paste0(lead, control, pool_note, ce_note, tail)
}

#' @keywords internal
prereg_template <- function(ds) {
  paste0(
    "## Pre-registration template\n\n",
    "*Auto-generated by lexsync. The Materials section is filled from the datasheet; ",
    "complete the remaining sections before data collection.*\n\n",
    "### Study information\n- Title:\n- Authors:\n- Research questions:\n\n",
    "### Hypotheses\n- H1:\n\n",
    "### Design\n- Manipulated variable(s):\n- Measured variable(s):\n",
    sprintf("- Paradigm: %s\n\n", ds$design$paradigm),
    "### Materials (from the lexsync datasheet)\n", methods_paragraph(ds), "\n\n",
    "### Sampling plan\n- Sample size and justification:\n- Stopping rule:\n\n",
    sprintf("### Analysis plan\n- Statistical model: %s\n  (%s)\n",
            ds$analysis$suggested_model, ds$analysis$note),
    "- Inference criteria:\n",
    "- Treatment of items (e.g. items as a random factor):\n")
}

#' @keywords internal
render_datasheet_md <- function(ds) {
  d <- ds$design
  versions <- paste(vapply(names(ds$reproducibility$versions),
                           function(k) paste(k, ds$reproducibility$versions[[k]]), character(1)),
                    collapse = ", ")
  lines <- c(
    sprintf("# Materials datasheet -- %s (%s)", d$name, d$language), "",
    sprintf("*lexsync datasheet v%s; %s engine.*", ds$lexsync_datasheet_version,
            ds$reproducibility$versions$engine), "",
    "## Provenance", "",
    sprintf("- **Paradigm:** %s  |  **Item source:** %s", d$paradigm, d$source),
    sprintf("- **Description:** %s", d$description %||% "--"),
    sprintf("- **Materials source:** `%s` (sha256 `%s...`)", ds$materials_source$path,
            substring(ds$materials_source$sha256 %||% "", 1, 16)),
    sprintf("- **Selection:** %s", ds$selection$method),
    sprintf("- **Cross-engine determinism:** %s", ds$selection$cross_engine %||% "byte-identical"),
    sprintf("- **Counterbalancing:** %s, %s list(s)", ds$counterbalancing$recipe,
            ds$counterbalancing$lists),
    sprintf("- **Items:** %s rows across %s conditions (%s)", ds$items$n_total,
            ds$items$n_conditions, paste(unlist(ds$items$conditions), collapse = ", ")),
    sprintf("- **Seed:** %s  |  **Versions:** %s", ds$reproducibility$seed, versions), "")
  cp <- ds$selection$candidate_pool
  if (!is.null(cp) && length(cp)) {
    parts <- paste(vapply(cp, function(x) sprintf("%s: %s", x$condition, x$n_candidates),
                          character(1)), collapse = ", ")
    lines <- c(lines, "## Selection transparency", "",
               sprintf(paste0("- **Candidate pool** (items satisfying each condition's window ",
                              "before matching): %s."), parts),
               paste0("- Selection is deterministic given the seed and blind to any outcome ",
                      "measure, so it is reproducible and free of item-selection bias ",
                      "(Forster, 2000; Simmons et al., 2011)."), "")
  }
  if (length(ds$realised_control)) {
    lines <- c(lines, "## Realised control", "",
               "| Dimension | Role | Cohen's d | 90% CI | TOST p | Equivalent |",
               "|---|---|---|---|---|---|")
    for (r in ds$realised_control) {
      ci <- if (!is.null(r$ci_low)) sprintf("[%.2f, %.2f]", r$ci_low, r$ci_high) else "--"
      dstr <- if (is.null(r$cohens_d)) "--" else sprintf("%.2f", r$cohens_d)
      lines <- c(lines, sprintf("| %s | %s | %s | %s | %s | %s |", r$dimension, r$role,
                                dstr, ci, r$tost_p %||% "--", r$equivalent %||% "--"))
    }
    lines <- c(lines, "")
  }
  a <- ds$analysis
  if (!is.null(a)) {
    lines <- c(lines, "## Suggested analysis", "",
               sprintf("- **Model:** `%s` -- where the response is %s.", a$suggested_model, a$response),
               paste0("- ", a$note), "")
  }
  lines <- c(lines, "## Methods paragraph", "", methods_paragraph(ds), "", prereg_template(ds))
  paste(lines, collapse = "\n")
}

#' @keywords internal
write_datasheet <- function(ds, json_path, md_path) {
  dir.create(dirname(json_path), recursive = TRUE, showWarnings = FALSE)
  writeLines(jsonlite::toJSON(ds, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null"),
             json_path, useBytes = TRUE)
  writeLines(render_datasheet_md(ds), md_path, useBytes = TRUE)
  invisible(c(json_path, md_path))
}
