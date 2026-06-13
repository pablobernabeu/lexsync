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

  method <- design$matching$method %||% schema$matching$method %||% "standardised_euclidean"
  if (identical(method, "joint") && length(conditions) == 2L) {
    return(match_joint(subpools, cond_names, match_on, center, scale_, n))
  }

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

#' Joint nearest-pair matching for a two-condition design
#'
#' Selects the `n` best-matched pairs across the two conditions, keeping only
#' items that have a good counterpart. This equates the control dimensions more
#' tightly than per-anchor matching when the manipulation is confounded with them
#' (for example neighbourhood density with word length). Deterministic and
#' identical to the Python engine (rounded costs; byte-rank tie-breaks).
#'
#' @keywords internal
match_joint <- function(subpools, cond_names, match_on, center, scale_, n, cap = 1200L) {
  s0 <- subpools[[1]]
  s1 <- subpools[[2]]
  if (nrow(s0) == 0 || nrow(s1) == 0) {
    stop("lexsync: a condition has no candidates for joint matching.", call. = FALSE)
  }
  zof <- function(df) {
    m <- as.matrix(df[, match_on, drop = FALSE])
    sweep(sweep(m, 2, center, "-"), 2, scale_, "/")
  }
  cap_overlap <- function(df, z, centroid) {
    if (nrow(df) <= cap) return(list(df = df, z = z))
    d <- round(sqrt(rowSums(sweep(z, 2, centroid, "-")^2)), 9)
    ord <- order(d, seq_len(nrow(df)), method = "radix")[seq_len(cap)]
    keep <- sort(ord)
    list(df = df[keep, , drop = FALSE], z = z[keep, , drop = FALSE])
  }
  z0 <- zof(s0); z1 <- zof(s1)
  o0 <- cap_overlap(s0, z0, colMeans(z1)); s0 <- o0$df; z0 <- o0$z
  o1 <- cap_overlap(s1, z1, colMeans(z0)); s1 <- o1$df; z1 <- o1$z
  m0 <- nrow(z0); m1 <- nrow(z1)
  cost <- matrix(0, m0, m1)
  for (d in seq_len(ncol(z0))) cost <- cost + outer(z0[, d], z1[, d], "-")^2
  cost <- round(sqrt(cost), 9)
  rows <- as.vector(row(cost)); cols <- as.vector(col(cost)); vals <- as.vector(cost)
  ord <- order(vals, rows, cols, method = "radix")
  used0 <- logical(m0); used1 <- logical(m1)
  pick0 <- integer(0); pick1 <- integer(0)
  for (t in ord) {
    i <- rows[t]; j <- cols[t]
    if (used0[i] || used1[j]) next
    used0[i] <- TRUE; used1[j] <- TRUE
    pick0 <- c(pick0, i); pick1 <- c(pick1, j)
    if (length(pick0) >= n) break
  }
  a <- s0[pick0, , drop = FALSE]; a$condition <- cond_names[1]
  b <- s1[pick1, , drop = FALSE]; b$condition <- cond_names[2]
  common <- intersect(names(a), names(b))
  out <- rbind(a[, common, drop = FALSE], b[, common, drop = FALSE])
  out$set <- rep(seq_len(length(pick0)), times = 2)
  rownames(out) <- NULL
  out
}

#' Produce several disjoint matched item sets (items as a random factor)
#'
#' Each replicate is an independent, fully matched set drawn from the pool with the
#' items of earlier replicates removed, so no item is reused. This lets a study
#' treat its items as a random factor -- running different item samples across
#' participant groups, or showing an effect holds across samples -- rather than as
#' a fixed set (Clark, 1973; Yarkoni, 2020). Deterministic and identical to the
#' Python engine.
#'
#' @param pool A candidate pool with the `match_on` dimensions present.
#' @param design A parsed design configuration.
#' @param schema The parsed global schema.
#' @param n_sets Number of disjoint matched sets to draw.
#' @param verbose Logical; passed to [match_stimuli()].
#' @return A data frame of matched stimuli with an added `replicate` column.
#' @export
resample_stimuli <- function(pool, design, schema, n_sets, verbose = FALSE) {
  used <- character(0)
  parts <- list()
  for (k in seq_len(as.integer(n_sets))) {
    pk <- pool[!(pool$word %in% used), , drop = FALSE]
    sk <- match_stimuli(pk, design, schema, verbose = verbose)
    sk$replicate <- k
    used <- c(used, sk$word)
    parts[[k]] <- sk
  }
  out <- do.call(rbind, parts)
  rownames(out) <- NULL
  out
}
