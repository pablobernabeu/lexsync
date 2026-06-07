# matching.R -- the multidimensional constraint-matching engine. A deterministic
# two-stage procedure: a per-dimension tolerance pre-filter (generalising the
# original workflow's mean +/- k*SD windows) followed by standardised
# nearest-neighbour assignment with a stable tie-break. Because no random number
# generator is used, the R and Python engines return identical selections from
# identical input.

#' Match stimuli across conditions on several lexical dimensions
#'
#' The first condition is the anchor; its items are chosen by an even spread
#' across the sorted candidate subpool. Every other condition is then matched to
#' the anchor item by item, on the `match_on` dimensions, using standardised
#' Euclidean distance under a tolerance window derived from the anchor.
#'
#' @param pool A lexicon/pool with all `match_on` dimensions present (see
#'   [add_neighbourhood()]).
#' @param design A parsed design configuration (conditions, `match_on`,
#'   `n_per_condition`/`n_per_cell`).
#' @param schema The parsed global schema (tolerances live here).
#' @param verbose Logical; report tolerance relaxations.
#' @return A data frame of selected stimuli with a `condition` label and a `set`
#'   index pairing matched items across conditions.
#' @importFrom stats sd
#' @export
match_stimuli <- function(pool, design, schema, verbose = FALSE) {
  conditions <- design$conditions
  match_on <- unlist(design$match_on, use.names = FALSE)
  n <- design$n_per_condition %||% design$n_per_cell %||% 20L
  tol_k <- schema$matching$tolerance_k

  for (d in match_on) {
    if (!d %in% names(pool)) {
      stop(sprintf("lexsync: dimension '%s' is absent from the pool.", d), call. = FALSE)
    }
  }

  # Standardisation statistics taken from the whole pool, so scaling is stable
  # and identical across conditions.
  center <- vapply(match_on, function(d) mean(pool[[d]], na.rm = TRUE), numeric(1))
  scale_ <- vapply(match_on, function(d) stats::sd(pool[[d]], na.rm = TRUE), numeric(1))
  scale_[is.na(scale_) | scale_ == 0] <- 1
  zmat <- function(df) {
    m <- as.matrix(df[, match_on, drop = FALSE])
    sweep(sweep(m, 2, center, "-"), 2, scale_, "/")
  }

  subpools <- lapply(conditions, function(cd) build_pool(pool, cd$define_by))
  cond_names <- vapply(conditions, function(cd) cd$name, character(1))

  # --- Anchor condition: deterministic even spread -------------------------
  anchor_pool <- subpools[[1]]
  if (nrow(anchor_pool) == 0) {
    stop(sprintf("lexsync: anchor condition '%s' has no candidates.", cond_names[1]), call. = FALSE)
  }
  ord_dim <- names(conditions[[1]]$define_by)[1]
  if (is.null(ord_dim) || !ord_dim %in% names(anchor_pool)) ord_dim <- "frequency"
  anchor_pool <- anchor_pool[order(anchor_pool[[ord_dim]], anchor_pool$word, method = "radix"), , drop = FALSE]
  n_take <- min(n, nrow(anchor_pool))
  idx <- unique(round(seq(1, nrow(anchor_pool), length.out = n_take)))
  anchor <- anchor_pool[idx, , drop = FALSE]
  anchor$condition <- cond_names[1]
  n_take <- nrow(anchor)
  z_anchor <- zmat(anchor)

  # Tolerance windows from the anchor distribution (Stage 1 pre-filter).
  win <- lapply(match_on, function(d) {
    m <- mean(anchor[[d]], na.rm = TRUE)
    s <- stats::sd(anchor[[d]], na.rm = TRUE)
    k <- tol_k[[d]] %||% 2
    c(m - k * s, m + k * s)
  })
  names(win) <- match_on

  selected <- list(anchor)
  used_words <- anchor$word

  for (ci in seq_along(conditions)[-1]) {
    cname <- cond_names[ci]
    cand <- subpools[[ci]]
    cand <- cand[!cand$word %in% used_words, , drop = FALSE]
    if (nrow(cand) == 0) {
      stop(sprintf("lexsync: condition '%s' has no candidates left to match.", cname), call. = FALSE)
    }
    # Stage 1: tolerance pre-filter.
    keep <- rep(TRUE, nrow(cand))
    for (d in match_on) keep <- keep & cand[[d]] >= win[[d]][1] & cand[[d]] <= win[[d]][2]
    cand_f <- cand[keep, , drop = FALSE]
    if (nrow(cand_f) < n_take) {
      if (verbose) {
        message(sprintf("lexsync: condition '%s' has %d candidates within tolerance (< %d needed); relaxing the window.",
                        cname, nrow(cand_f), n_take))
      }
      cand_f <- cand
    }
    # Stage 2: standardised nearest-neighbour assignment, greedy, no replacement.
    z_cand <- zmat(cand_f)
    used <- rep(FALSE, nrow(cand_f))
    pick <- integer(n_take)
    for (a in seq_len(n_take)) {
      # Round to absorb last-ULP floating-point differences between engines, so
      # the stable tie-break below is itself reproducible across R and Python.
      dvec <- round(sqrt(rowSums(sweep(z_cand, 2, z_anchor[a, ], "-")^2)), 9)
      dvec[used] <- Inf
      best <- order(dvec, cand_f$word, cand_f$id, method = "radix")[1]  # stable, locale-independent tie-break
      pick[a] <- best
      used[best] <- TRUE
    }
    sel <- cand_f[pick, , drop = FALSE]
    sel$condition <- cname
    used_words <- c(used_words, sel$word)
    selected[[length(selected) + 1]] <- sel
  }

  common <- Reduce(intersect, lapply(selected, names))
  out <- do.call(rbind, lapply(selected, function(x) x[, common, drop = FALSE]))
  out$set <- rep(seq_len(n_take), times = length(conditions))
  rownames(out) <- NULL
  out
}
