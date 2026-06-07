# counterbalancing.R -- assign matched stimuli to presentation lists and orders,
# and build participant counterbalancing tables. Property-defined conditions
# (e.g. high vs low frequency) cannot be rotated across conditions the way a
# grammaticality manipulation can, so counterbalancing here concerns list
# splitting, trial order and participant-level factor crossing.

#' Assign stimuli to lists and a randomised, reproducible trial order
#'
#' @param stimuli A matched-stimuli data frame from [match_stimuli()].
#' @param design A parsed design configuration.
#' @param schema The parsed global schema (provides the seed).
#' @return `stimuli` with added `list` and `trial` columns.
#' @export
counterbalance <- function(stimuli, design, schema) {
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
