# counterbalancing.R -- assign stimuli to presentation lists and orders, and build
# participant counterbalancing tables. Two recipes: the original `factorial` one
# (every matched item shown, lists split the matched sets) and
# `latin_square_target` for paired/sentence paradigms (each item appears once per
# list in one rotated condition, so a target is never repeated within a list).
# Trial order within a list is shuffled with a seeded generator. Mirrors
# python_workflow/src/lexsync/counterbalancing.py.

.cb_recipe <- function(design) {
  if (!is.null(design$events) && length(design$events)) return("factorial")
  name <- design$paradigm %||% "factorial"
  p <- tryCatch(get_paradigm(name), error = function(e) NULL)
  if (is.null(p)) "factorial" else (p$counterbalance %||% "factorial")
}

#' Assign stimuli to lists and a randomised, reproducible trial order
#'
#' Dispatches on the design's paradigm: the factorial recipe for matched word
#' lists, or a Latin square over conditions for paired/sentence paradigms.
#'
#' @param stimuli A stimuli data frame (matched set or loaded item table).
#' @param design A parsed design configuration.
#' @param schema The parsed global schema (provides the seed).
#' @return `stimuli` with added `list` and `trial` columns.
#' @export
counterbalance <- function(stimuli, design, schema) {
  if (identical(.cb_recipe(design), "latin_square_target")) {
    return(counterbalance_latin_square(stimuli, design, schema))
  }
  counterbalance_factorial(stimuli, design, schema)
}

#' @keywords internal
counterbalance_factorial <- function(stimuli, design, schema) {
  n_lists <- design$counterbalance$lists %||% 1L
  seed <- schema$seed %||% 1L

  stimuli$list <- 1L
  if (n_lists > 1) {
    sets <- sort(unique(stimuli$set))
    list_of_set <- ((sets - 1L) %% n_lists) + 1L
    stimuli$list <- list_of_set[match(stimuli$set, sets)]
  }

  set.seed(seed)
  order_within <- function(df) {
    df <- df[sample(nrow(df)), , drop = FALSE]
    df$trial <- seq_len(nrow(df))
    df
  }
  parts <- split(stimuli, stimuli$list)
  stimuli <- do.call(rbind, lapply(parts, order_within))
  rownames(stimuli) <- NULL
  stimuli
}

#' One row per item per list, condition rotated across lists (Latin square)
#'
#' Each item (`set`) contributes exactly one trial to a list, so its target is
#' never repeated within a list; conditions are balanced because items rotate
#' through them. With `lists` unset the number of lists equals the number of
#' conditions. Mirrors the Python recipe (byte-order condition list, zero-based
#' rotation), so the two engines assign the same condition to each item per list.
#' @keywords internal
counterbalance_latin_square <- function(stimuli, design, schema) {
  seed <- schema$seed %||% 1L
  conds <- sort(unique(as.character(stimuli$condition)), method = "radix")
  n_cond <- length(conds)
  n_lists <- design$counterbalance$lists %||% n_cond
  sets <- sort(unique(stimuli$set))

  set.seed(seed)
  parts <- list()
  for (li in seq_len(n_lists) - 1L) {
    rows <- vector("list", length(sets))
    for (si in seq_along(sets) - 1L) {
      s <- sets[si + 1L]
      cond <- conds[((si + li) %% n_cond) + 1L]
      sel <- stimuli[stimuli$set == s & stimuli$condition == cond, , drop = FALSE]
      if (nrow(sel) == 0L) {
        stop(sprintf("lexsync: item set %s has no row for condition '%s'.", s, cond), call. = FALSE)
      }
      rows[[si + 1L]] <- sel[1, , drop = FALSE]
    }
    df <- do.call(rbind, rows)
    df$list <- li + 1L
    df <- df[sample(nrow(df)), , drop = FALSE]
    df$trial <- seq_len(nrow(df))
    parts[[length(parts) + 1L]] <- df
  }
  out <- do.call(rbind, parts)
  rownames(out) <- NULL
  out
}

#' Build a participant counterbalancing table
#'
#' Crosses the supplied counterbalancing factors and replicates the cells to
#' cover `n_participants`, generalising the `expand.grid()` + replication pattern
#' of the original workflow's `participant_parameters.R`.
#'
#' @param factors A named list of factors, each a vector of levels.
#' @param n_participants Number of participants to allocate.
#' @return A data frame with one row per participant.
#' @export
participant_table <- function(factors, n_participants) {
  grid <- expand.grid(factors, stringsAsFactors = FALSE)
  reps <- ceiling(n_participants / nrow(grid))
  idx <- rep(seq_len(nrow(grid)), reps)[seq_len(n_participants)]
  tab <- grid[idx, , drop = FALSE]
  tab$participant <- seq_len(n_participants)
  rownames(tab) <- NULL
  tab
}
