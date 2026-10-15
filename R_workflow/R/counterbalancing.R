# counterbalancing.R -- assign stimuli to presentation lists and orders, and build
# participant counterbalancing tables. Two recipes: the original `factorial` one
# (every matched item shown, lists split the matched sets) and
# `latin_square_target` for paired/sentence paradigms (each item appears once per
# list in one rotated condition, so a target is never repeated within a list). The
# design's paradigm chooses between them, and `counterbalance.recipe` overrides it.
# Trial order within a list comes from a seeded, keyed-hash shuffle, so the R and
# Python engines produce the same order byte for byte. .counterbalance_check()
# reports a rotation that the lists or the item sets leave incomplete. Mirrors
# python_workflow/src/lexsync/counterbalancing.py.

# The recipes counterbalance() knows, which counterbalance.recipe may name, and the
# policies counterbalance.incomplete accepts. Both are closed sets, so a misspelt
# value is refused, and the error names it.
.CB_RECIPES <- c("factorial", "latin_square_target")
.CB_INCOMPLETE_POLICIES <- c("allow", "error")

# The recipe counterbalance() applies to a design: counterbalance.recipe when the
# design names one, else the recipe of the paradigm it names, else factorial. An
# `events` list has no say in it. It used to switch the recipe to factorial. A
# priming design that read its prime's duration from the items then showed every
# target in both conditions of each list, the repetition the paradigm's Latin square
# exists to prevent. The datasheet takes its recipe from here too, so the record
# names the recipe that ran. Mirrors _recipe in counterbalancing.py.
.cb_recipe <- function(design) {
  named <- design[["counterbalance"]][["recipe"]]
  if (!is.null(named)) {
    if (!is.character(named) || length(named) != 1L || !named %in% .CB_RECIPES) {
      stop(sprintf("lexsync: unknown counterbalance.recipe '%s'. Known recipes: %s.",
                   paste(named, collapse = ", "), paste(.CB_RECIPES, collapse = ", ")),
           call. = FALSE)
    }
    return(named)
  }
  name <- design[["paradigm"]] %||% "factorial"
  p <- tryCatch(get_paradigm(name), error = function(e) NULL)
  if (is.null(p)) "factorial" else (p[["counterbalance"]] %||% "factorial")
}

# Resolve counterbalance.incomplete: the design's, else the schema's, else "allow".
# This is the cascade of matching.shortfall, and %||% takes any value that is present,
# as the Python twin does. Mirrors _incomplete_policy in counterbalancing.py.
.cb_incomplete_policy <- function(design, schema) {
  val <- design[["counterbalance"]][["incomplete"]] %||%
    schema[["counterbalance"]][["incomplete"]] %||% "allow"
  if (!is.character(val) || length(val) != 1L || !val %in% .CB_INCOMPLETE_POLICIES) {
    stop(sprintf("lexsync: unknown counterbalance.incomplete policy '%s'. Known policies: %s.",
                 paste(val, collapse = ", "), paste(.CB_INCOMPLETE_POLICIES, collapse = ", ")),
         call. = FALSE)
  }
  val
}

# The lists counterbalance() deals when the frame does not say: the declared
# counterbalance.lists, else one per condition for a Latin square and one list for
# the factorial recipe.
.cb_default_lists <- function(design, recipe, n_cond) {
  lists <- design[["counterbalance"]][["lists"]]
  if (is.null(lists)) return(if (identical(recipe, "latin_square_target")) n_cond else 1L)
  as.integer(lists)
}

# Whether a counterbalanced table rotates its conditions completely.
#
# A Latin square is complete when every item takes each of its conditions in the same
# number of lists and every list holds each condition equally often. Four things
# break that, and each one is reported in a sentence that both engines word
# identically. One list shows every participant an item in the same condition, which
# confounds item and condition fully. Fewer lists than conditions leave each item out
# of some of its conditions. More lists than conditions, but not a multiple of them,
# give an item some conditions in more lists than others. And item sets that are not
# a multiple of the conditions leave the conditions within a list one trial apart. The
# factorial recipe raises none of these: it shows every item in every condition, and
# counterbalance() refuses lists it would leave empty.
#
# `stimuli` is the table counterbalance() returned. Without a `list` column, the lists
# are the ones counterbalance() would deal. `conditions` names the conditions the
# design rotates through, by default those the table holds. The pipeline passes them
# from the table it counterbalanced, since a Latin square with fewer item sets than
# conditions can leave a condition out of every list.
#
# Returns list(complete, issues, lists, cells). `complete` says whether no issue was
# found and `issues` gives the sentences. `lists` is the number of lists, and `cells`
# counts the trials in each cell of (replicate, when the table has one) by list by
# condition, empty cells included. Mirrors counterbalance_check in
# counterbalancing.py.
.counterbalance_check <- function(stimuli, design, recipe = .cb_recipe(design),
                                  conditions = NULL) {
  conds <- sort(unique(as.character(conditions %||% stimuli$condition)), method = "radix")
  n_cond <- length(conds)
  has_list <- "list" %in% names(stimuli)
  n_lists <- if (has_list) length(unique(stimuli$list))
             else .cb_default_lists(design, recipe, n_cond)
  has_rep <- "replicate" %in% names(stimuli)
  reps <- if (has_rep) sort(unique(stimuli$replicate)) else NA
  part_of <- function(r) {
    if (has_rep) stimuli[stimuli$replicate == r, , drop = FALSE] else stimuli
  }

  issues <- character(0)
  if (identical(recipe, "latin_square_target") && n_cond > 1L) {
    if (n_lists == 1L) {
      issues <- c(issues, paste0("With one list, every participant sees each item in the ",
                                 "same condition, so item and condition are fully ",
                                 "confounded."))
    } else if (n_lists < n_cond) {
      issues <- c(issues, sprintf(paste0("With %d lists and %d conditions, each item ",
                                         "appears in only %d of its %d conditions."),
                                  n_lists, n_cond, n_lists, n_cond))
    } else if (n_lists %% n_cond != 0L) {
      issues <- c(issues, sprintf(paste0("With %d lists and %d conditions, the lists are ",
                                         "not a multiple of the conditions, so each item ",
                                         "appears in some conditions in more lists than ",
                                         "in others."), n_lists, n_cond))
    }
    # Each replicate is rotated on its own, so each is checked on its own. Replicates
    # of one size give one sentence between them.
    for (r in reps) {
      n_sets <- length(unique(part_of(r)$set))
      if (n_sets %% n_cond != 0L) {
        issues <- union(issues, sprintf(
          paste0("With %d item %s and %d conditions, the item sets are not a multiple ",
                 "of the conditions, so the conditions within each list differ by one ",
                 "trial."),
          n_sets, if (n_sets == 1L) "set" else "sets", n_cond))
      }
    }
  }

  cells <- list()
  if (has_list) {
    lists <- sort(unique(as.integer(stimuli$list)))
    for (r in reps) {
      part <- part_of(r)
      labels <- as.character(part$condition)
      for (l in lists) {
        in_list <- part$list == l
        for (cnd in conds) {
          cell <- list(list = l, condition = cnd,
                       n_trials = as.integer(sum(in_list & labels == cnd)))
          if (has_rep) cell <- c(list(replicate = as.integer(r)), cell)
          cells[[length(cells) + 1L]] <- cell
        }
      }
    }
  }
  list(complete = !length(issues), issues = issues, lists = as.integer(n_lists),
       cells = cells)
}

# Refuse an incomplete rotation when counterbalance.incomplete is "error". Must stay
# identical to _check_incomplete in python_workflow/src/lexsync/counterbalancing.py.
.check_incomplete <- function(check, policy) {
  if (isTRUE(check$complete) || !identical(policy, "error")) return(invisible(NULL))
  stop(paste0("lexsync: the Latin-square rotation is incomplete and ",
              "counterbalance.incomplete is 'error'. ", paste(check$issues, collapse = " "),
              " Make the lists and the item sets multiples of the number of conditions, ",
              "or set counterbalance.incomplete: allow."), call. = FALSE)
}

# A trial's position within its list is decided by a keyed hash, not a random
# number generator: each row is ranked by the SHA-256 digest of
# "seed|replicate|list|set|condition", a tuple that identifies the trial uniquely
# under either recipe. Distinct inputs to SHA-256 behave as independent uniform
# draws, so ordering by the digest realises a seeded random permutation, but as a
# pure function of the design: the same bytes from the R and Python engines on any
# platform, no generator state to save or restore, and a different order for every
# seed. R's own sample() and numpy's PCG64 could never agree on a permutation,
# which used to be the one engine-specific artefact in an otherwise byte-identical
# pipeline. The replicate term keeps independently counterbalanced item sets from
# sharing one permutation pattern.
.shuffle_deterministic <- function(df, seed) {
  df <- df[order(.order_ranks(df, seed), method = "radix"), , drop = FALSE]
  df$trial <- seq_len(nrow(df))
  df
}

# Each row's SHA-256 rank in trial order `order` of its list. Order 1 hashes
# "seed|replicate|list|set|condition", the key every order had before
# counterbalance.orders existed, so a design with one order keeps its order. Order j
# from 2 hashes "seed|order<j>|replicate|list|set|condition". Mirrors _order_ranks in
# counterbalancing.py.
.order_ranks <- function(df, seed, order = 1L) {
  rep_id <- if ("replicate" %in% names(df)) df$replicate else 0L
  head <- if (order == 1L) .key_part(seed) else paste(.key_part(seed), paste0("order", order),
                                                      sep = "|")
  # Every component is formatted explicitly rather than interpolated. Default
  # stringification is where the two engines silently part company: R renders the
  # double 42 as "42" and Python as "42.0", and a pandas column is promoted to
  # float64 by a single missing value, which would change every digest, every
  # trial order and every generated artefact with nothing to signal it. The
  # values are integers today, so this changes no output; it removes a trap.
  # enc2utf8 because digest(serialize = FALSE) hashes the stored bytes, as
  # hash_unit already does: a latin1-marked condition read from a user's CSV
  # would otherwise give a different digest from the same characters in Python.
  key <- enc2utf8(paste(head, .key_part(rep_id), .key_part(df$list),
                        .key_part(df$set), .key_part(df$condition), sep = "|"))
  vapply(key, function(k) digest::digest(k, algo = "sha256", serialize = FALSE),
         character(1), USE.NAMES = FALSE)
}

# ---- Trial-order constraints (counterbalance.max_run, run_on, orders) --------
#
# The keyed-hash order is a uniform shuffle, and a uniform shuffle gives long runs of
# one condition: over seeds 1 to 1000 of a 60 + 60 lexical decision the longest run
# had a median of 7 and a maximum of 21. `max_run: k` repairs the seeded order so that
# no run of one `run_on` value is longer than k, the kind of sequence constraint that
# pseudorandomisation programs such as Mix impose (van Casteren & Davis, 2006). The
# repair is deterministic and identical in both engines, and it refuses only a
# constraint that no order can meet. `orders: m` gives each list m orders, the first
# being the order the list has without the key, so that participants on one list need
# not all meet one order. Mirrors python_workflow/src/lexsync/counterbalancing.py.

# Whether a design value is a whole number from 1, written as 2 or 2.0, within the
# range as.integer() holds. Must match _whole_at_least_one in counterbalancing.py.
.whole_at_least_one <- function(value) {
  is.numeric(value) && length(value) == 1L && !is.na(value) && is.finite(value) &&
    value == trunc(value) && value >= 1 && value <= .Machine$integer.max
}

# counterbalance.max_run, run_on and orders, checked. Returns list(max_run, run_on,
# orders): max_run is NULL when the design sets no limit, run_on defaults to
# "condition" and orders to 1. A limit or a number of orders that is not a whole
# number from 1 is refused, and so is a run_on that is not the name of a column.
# Mirrors _trial_order_settings in counterbalancing.py.
.trial_order_settings <- function(design) {
  cb <- if (is.list(design)) design[["counterbalance"]] else NULL
  if (!is.list(cb)) cb <- list()
  k <- cb[["max_run"]]
  if (!is.null(k) && !.whole_at_least_one(k)) {
    stop("lexsync: counterbalance.max_run must be a whole number of at least 1.",
         call. = FALSE)
  }
  run_on <- cb[["run_on"]]
  if (is.null(run_on)) {
    run_on <- "condition"
  } else if (!is.character(run_on) || length(run_on) != 1L || is.na(run_on) ||
             !nzchar(trimws(run_on))) {
    stop("lexsync: counterbalance.run_on must name a column of the trials.", call. = FALSE)
  }
  m <- cb[["orders"]]
  if (is.null(m)) {
    m <- 1L
  } else if (!.whole_at_least_one(m)) {
    stop("lexsync: counterbalance.orders must be a whole number of at least 1.",
         call. = FALSE)
  }
  list(max_run = if (is.null(k)) NULL else as.integer(k), run_on = run_on,
       orders = as.integer(m))
}

# The list a frame of trials belongs to, as the refusals name it: "list 2", or "list 2
# of replicate 3" when the frame carries a replicate.
.unit_label <- function(df) {
  label <- paste("list", .key_part(df$list[1]))
  if ("replicate" %in% names(df)) label <- paste(label, "of replicate", .key_part(df$replicate[1]))
  label
}

# A missing run_on value: NA, or text that is empty once trimws() has stripped it.
# Every missing value forms one category.
.missing_category <- function(x) {
  if (is.character(x) || is.factor(x)) {
    x <- as.character(x)
    return(is.na(x) | !nzchar(trimws(x)))
  }
  is.na(x)
}

# Each row's run_on value as a category: NA for a missing value, else the value as the
# hash key renders it, so 1 and 1.0 are one category in both engines.
.run_categories <- function(df, run_on, unit) {
  if (!run_on %in% names(df)) {
    stop(sprintf("lexsync: counterbalance.run_on names '%s', a column that %s does not have.",
                 run_on, unit), call. = FALSE)
  }
  x <- df[[run_on]]
  missing <- .missing_category(x)
  out <- rep(NA_character_, length(x))
  if (any(!missing)) out[!missing] <- .key_part(x[!missing])
  out
}

# Whether the trials still to place can follow the current run with no run longer than
# k. Category c can be split by the others into at most (others + 1) runs of k, and its
# first run continues the current run when c is the current run's category:
# remaining(c) <= k * (others + 1), less the current run's length for that category.
# `remaining` is a named integer vector over category codes, `current` a code or 0L.
# Must match _run_feasible in counterbalancing.py.
.run_feasible <- function(remaining, current, run, k) {
  total <- sum(remaining)
  limit <- k * (total - remaining + 1L) - ifelse(seq_along(remaining) == current, run, 0L)
  !any(remaining > 0L & remaining > limit)
}

# Category codes 1..C for the categories, NA (a missing value) a code of its own.
.category_codes <- function(categories) {
  key <- ifelse(is.na(categories), "\001NA", paste0("\002", categories))
  match(key, unique(key))
}

# Refuse a limit no order of these trials can meet. At most one category can break it,
# the one holding more than half the trials, so the message names it.
.check_run_limit <- function(categories, k, run_on, unit) {
  codes <- .category_codes(categories)
  counts <- tabulate(codes)
  if (.run_feasible(counts, 0L, 0L, k)) return(invisible(NULL))
  total <- length(codes)
  worst <- which(counts > k * (total - counts + 1L))[1]
  n <- counts[worst]
  value <- categories[match(worst, codes)]
  label <- if (is.na(value)) sprintf("trials with no '%s'", run_on) else
    sprintf("'%s' trials", value)
  stop(sprintf("lexsync: no order of %s keeps runs of '%s' to %d or fewer: %d %s against %d others.",
               unit, run_on, as.integer(k), as.integer(n), label, as.integer(total - n)),
       call. = FALSE)
}

# The seeded order `perm` (row indices in rank order), repaired so that no run of one
# category is longer than k. Each step takes the earliest trial still unplaced in the
# seeded order that neither extends the current run beyond k nor leaves the rest
# infeasible (see .run_feasible). A trial that keeps both is always there once the
# start is feasible, which .check_run_limit has established. Taking the earliest trial
# that does not extend the run, without the look-ahead, refused 931 of 1,000 seeds of a
# feasible 40 + 80 design at k = 2 near the end of the list. Mirrors _repair_runs in
# counterbalancing.py.
.repair_runs <- function(perm, categories, k) {
  codes <- .category_codes(categories)
  remaining <- tabulate(codes)
  left <- perm
  out <- integer(0)
  current <- 0L
  run <- 0L
  while (length(left)) {
    verdict <- rep(NA, length(remaining))
    pick <- 0L
    for (pos in seq_along(left)) {
      c <- codes[left[pos]]
      if (c == current && run >= k) next
      if (is.na(verdict[c])) {
        remaining[c] <- remaining[c] - 1L
        verdict[c] <- .run_feasible(remaining, c, if (c == current) run + 1L else 1L, k)
        remaining[c] <- remaining[c] + 1L
      }
      if (verdict[c]) {
        pick <- pos
        break
      }
    }
    if (!pick) stop("lexsync: the trial-order repair found no trial to place.", call. = FALSE)
    c <- codes[left[pick]]
    out <- c(out, left[pick])
    left <- left[-pick]
    remaining[c] <- remaining[c] - 1L
    run <- if (c == current) run + 1L else 1L
    current <- c
  }
  out
}

# Order one list's trials, and add each trial's position in every order. The rows come
# back in order 1 with `trial` numbered from 1. With settings$orders above 1, order_1 to
# order_m give each trial's position in each order, order_1 equal to `trial`. With
# settings$max_run set and `max_run` TRUE, every order is repaired so that no run of
# one run_on value is longer than the limit. Without either setting this is
# .shuffle_deterministic(). Mirrors _order_trials in counterbalancing.py.
.order_trials <- function(df, seed, settings, unit, max_run = TRUE) {
  k <- if (isTRUE(max_run)) settings$max_run else NULL
  m <- settings$orders %||% 1L
  categories <- NULL
  if (!is.null(k)) {
    categories <- .run_categories(df, settings$run_on, unit)
    .check_run_limit(categories, k, settings$run_on, unit)
  }
  perms <- lapply(seq_len(m), function(j) {
    perm <- order(.order_ranks(df, seed, j), method = "radix")
    if (!is.null(k)) perm <- .repair_runs(perm, categories, k)
    perm
  })
  out <- df[perms[[1]], , drop = FALSE]
  n <- nrow(df)
  out$trial <- seq_len(n)
  if (m > 1L) {
    for (j in seq_len(m)) {
      position <- integer(n)
      position[perms[[j]]] <- seq_len(n)
      out[[paste0("order_", j)]] <- position[perms[[1]]]
    }
  }
  out
}

# The longest run of one run_on value in a version's presented trials, over every
# order. A pause separates the practice trials from the rest, so a run does not
# continue across it.
.longest_runs <- function(trials, run_on, orders) {
  if (!run_on %in% names(trials) || !nrow(trials)) return(0L)
  best <- 0L
  for (j in seq_len(orders)) {
    column <- if (orders > 1L) paste0("order_", j) else "trial"
    ordered <- trials[order(trials[[column]], method = "radix"), , drop = FALSE]
    practice <- if ("block" %in% names(ordered)) ordered$block %in% "practice" else
      rep(FALSE, nrow(ordered))
    cats <- .run_categories(ordered, run_on, "")
    key <- paste(practice, ifelse(is.na(cats), "\001NA", paste0("\002", cats)))
    runs <- rle(key)$lengths
    best <- max(best, runs)
  }
  as.integer(best)
}

# What the datasheet records of the trial-order settings, from the presented trials:
# list(max_run = list(k, run_on, longest)) when the design sets a limit, `longest`
# giving the longest run realised in each presentation version, and list(orders = m)
# when it asks for more than one order. Empty for a design with neither. Mirrors
# _trial_order_record in counterbalancing.py.
.trial_order_record <- function(presented, design) {
  settings <- .trial_order_settings(design)
  record <- list()
  if (!is.null(settings$max_run)) {
    longest <- lapply(.presentation_versions(presented), function(v) {
      row <- list(list = as.integer(v$list))
      if ("replicate" %in% names(presented)) row <- c(list(replicate = as.integer(v$replicate)), row)
      row$longest_run <- .longest_runs(.version_rows(presented, v), settings$run_on,
                                       settings$orders)
      row
    })
    record$max_run <- list(k = settings$max_run, run_on = settings$run_on, longest = longest)
  }
  if (settings$orders > 1L) record$orders <- settings$orders
  record
}

# ---- Balance-aware list assignment (counterbalance.optimise) ----------------
#
# The factorial recipe deals item sets to lists by rank: set 1 to list 1, set 2 to
# list 2, and so on. That is reproducible but arbitrary with respect to the items
# themselves, so one list can end up holding systematically shorter or more frequent
# words than another. Where lists are given to different participants, that
# difference is confounded with the between-subjects factor.
#
# `counterbalance.optimise: true` searches for an assignment whose lists match on the
# declared dimensions instead. It is off by default: switching it on changes which
# items a participant sees, so it must be an explicit choice rather than something
# that happens to a design on upgrade.
#
# The search obeys the package's two hard rules, and both shape the code below more
# than is obvious.
#
# No RNG. The order of the search and every tie in it is decided by the seeded keyed
# hash already used for trial order, so the result is a pure function of the design.
#
# An ALL-INTEGER objective. This is not fastidiousness. Cohen's d computed in the two
# engines was measured to differ by about 3e-16 on average, which at nine decimal
# places leaves roughly a one-in-three chance over a full run that a comparison of
# two candidate swaps resolves differently in R than in Python -- and the failure is
# silent and total, different words rather than different last bits. The values are
# quantised to integers ONCE, and the search then uses only +, -, * and
# comparison, all of which are exact on integers held in doubles below 2^53. There is
# no division anywhere in the objective.

# Each dimension is quantised to its own unit, the mean's or the mean absolute
# deviation's as counterbalance.scale says (see .quantise_dim). Expressing all
# dimensions in such a unit is what lets their imbalances be added without a
# per-dimension float weight: a word's length and its Zipf frequency differ by orders
# of magnitude in raw units, and summing raw deviations would silently optimise almost
# entirely for whichever dimension has the larger numbers.
#
# Under the mean scale the constant is 1000 times the 100 that `unit` already
# carries, so a value at the dimension's mean quantises to 1000, a milli-unit of the
# mean. That factor is not cosmetic: at 1000 here, a value at the mean quantised to
# 10, which left only about ten distinguishable levels across a dimension's whole
# range, and imbalances smaller than a tenth of the mean were invisible to the
# objective. The search then traded away a dimension it could not see in order to
# improve one it could. Under the mad scale the deviation and the unit are both in
# hundredths, so a deviation of one mean absolute deviation quantises to 100000.
.BALANCE_UNIT_SCALE <- 100000L

# Guard on the objective's magnitude. The arithmetic is exact only while every
# intermediate stays below 2^53; past that a sum would round and the two engines
# could disagree. Nothing near this is reachable with realistic designs (the bound is
# some four orders of magnitude above a 200-set, six-dimension design), so this is a
# tripwire rather than a limit, and it fails loudly where quiet rounding would hide
# the problem.
.BALANCE_MAX_MAGNITUDE <- 2^50

# The scales counterbalance.scale may name. A closed set, so a misspelt value is
# refused, and the error names it.
.BALANCE_SCALES <- c("mean", "mad")

# What the report's cost is counted in, under each scale. The mean scale's wording is
# that of every release before counterbalance.scale, so a record of the default reads
# as it did. Must stay identical to _BALANCE_COST_UNITS in counterbalancing.py.
.BALANCE_COST_UNITS <- c(
  mean = paste("summed absolute deviation of each list's dimension total from its fair",
               "share, in milli-units of the dimension's mean, scaled by the number of",
               "item sets"),
  mad = paste("summed absolute deviation of each list's dimension total from its fair",
              "share, in hundred-thousandths of the dimension's mean absolute deviation",
              "about its mean, scaled by the number of item sets")
)

# The scale balance_lists() quantises each dimension on: counterbalance.scale when the
# design names one, else "mean", the rule of every release before the option, so a
# design that names no scale keeps its lists. %||% takes any value that is present, as
# the Python twin does, so the two engines refuse the same values. validate_design()
# calls this too, so an unknown scale is refused before anything is selected. Mirrors
# _balance_scale in counterbalancing.py.
.balance_scale <- function(design) {
  val <- design[["counterbalance"]][["scale"]]
  if (is.null(val)) return("mean")
  if (!is.character(val) || length(val) != 1L || is.na(val) || !val %in% .BALANCE_SCALES) {
    stop(sprintf("lexsync: unknown counterbalance.scale '%s'. Known scales: %s.",
                 .shown(val), paste(.BALANCE_SCALES, collapse = ", ")), call. = FALSE)
  }
  val
}

.balance_dims <- function(design) {
  cb <- design[["counterbalance"]] %||% list()
  dims <- unlist(cb[["balance_on"]] %||% list(), use.names = FALSE)
  if (!length(dims)) dims <- unlist(design[["match_on"]] %||% list(), use.names = FALSE)
  if (!length(dims) && !is.null(design[["continuous"]])) {
    dims <- c(design[["continuous"]][["predictor"]],
              unlist(design[["continuous"]][["controls"]] %||% list(), use.names = FALSE))
  }
  unique(as.character(dims))
}

# Quantise one dimension to integers, on the scale counterbalance.scale names.
#
# Under "mean", each value in milli-units of the dimension's own mean. The only
# floating-point steps in the whole optimiser are here, and each is a single IEEE
# operation that the standard requires to be correctly rounded, so both engines hold
# the same double before it is truncated. Truncation of a double is exact, so no
# rounding mode is involved. `round()` would have agreed on every case measured, but
# truncation removes the question rather than answering it.
#
# The mean is computed from INTEGER counts, never as a float sum: summing 20000
# doubles was measured to give three different answers across R's sum(), math.fsum,
# numpy's pairwise sum and a naive loop, so a float mean here could put the two
# engines on different search paths from the first step.
#
# Dividing by the mean weights a dimension by its SD / mean, which depends on where its
# scale starts: Zipf frequency, which starts near 3, counted for least of the four
# dimensions in en_balanced_lists. That suits ratio scales only. "mad" quantises
# deviations from the mean instead (see .quantise_mad).
.quantise_dim <- function(values, name, scale = "mean") {
  if (any(is.na(values))) {
    stop(sprintf(paste("lexsync: dimension '%s' has missing values, so it cannot be",
                       "balanced across lists. Fill or drop those items."), name),
         call. = FALSE)
  }
  if (identical(scale, "mad")) return(.quantise_mad(values, name))
  # Integer magnitudes first, so the unit is reproducible without a float reduction.
  # sum() over an integer vector accumulates in a 64-bit integer and returns a double
  # if the total leaves int range (measured on R 4.6.1: no warning, no NA), so the
  # total is exact either way while it stays under 2^53, which the per-value bound
  # below and any realistic number of items keep it well inside.
  scaled <- trunc(abs(as.numeric(values)) * 100)
  if (max(scaled, 0) > .Machine$integer.max) {
    stop(sprintf("lexsync: dimension '%s' has values too large to balance on.", name),
         call. = FALSE)
  }
  unit <- max(1L, sum(as.integer(scaled)) %/% length(scaled))
  trunc(as.numeric(values) * .BALANCE_UNIT_SCALE / unit)
}

# Quantise one dimension's deviations from its mean, in hundred-thousandths of its mean
# absolute deviation.
#
# Each value becomes a whole number of hundredths by the shared rounder, the integer
# mean is the floor of their sum over their count, and the unit is the integer mean of
# the absolute deviations from it, at least 1. The values are rounded, not truncated,
# because a shifted value can scale to a hair below a whole hundredth ((5.26 - 3) * 100
# is 225.99999999999997), and truncation would move it by one. Adding a constant that
# is a whole number of hundredths then moves every value, and the mean with them, by
# the same whole number, and leaves the deviations and the unit as they were. The
# division by the unit is a single IEEE operation and the truncation is exact, so both
# engines hold the same integers. Mirrors _quantise_mad in counterbalancing.py.
.quantise_mad <- function(values, name) {
  # An infinite value passes through the rounder unchanged and is refused here, with
  # any finite value too large for its hundredths to be summed exactly.
  hundredths <- .round_dp_scaled(as.numeric(values) * 100)
  if (max(abs(hundredths), 0) > .Machine$integer.max) {
    stop(sprintf("lexsync: dimension '%s' has values too large to balance on.", name),
         call. = FALSE)
  }
  n <- length(hundredths)
  # Whole numbers held in doubles, exact below 2^53, which the bound above and any
  # realistic number of items keep the sums well inside. %/% on doubles is floor
  # division, as Python's // is, so a negative sum rounds down in both engines.
  centre <- sum(hundredths) %/% n
  deviations <- hundredths - centre
  unit <- max(1, sum(abs(deviations)) %/% n)
  trunc(deviations * .BALANCE_UNIT_SCALE / unit)
}

# One integer per set per dimension: the set's total, because a list receives whole
# sets. Rows are grouped by set in byte order so the two engines build the same
# matrix from the same frame.
.balance_values <- function(stimuli, dims, scale = "mean") {
  sets <- sort(unique(stimuli$set))
  V <- matrix(0, nrow = length(dims), ncol = length(sets),
              dimnames = list(dims, as.character(sets)))
  for (i in seq_along(dims)) {
    q <- .quantise_dim(stimuli[[dims[i]]], dims[i], scale)
    # A plain integer sum per set: exact, so grouping order cannot matter.
    for (j in seq_along(sets)) V[i, j] <- sum(q[stimuli$set == sets[j]])
  }
  V
}

# Total absolute deviation of each list's dimension total from its fair share,
# scaled by the number of sets so the fair share stays an integer. Every term is an
# exact integer; there is no division.
.balance_cost <- function(V, assign, n_lists) {
  n_sets <- ncol(V)
  cost <- 0
  for (i in seq_len(nrow(V))) {
    total <- sum(V[i, ])
    for (l in seq_len(n_lists)) {
      in_l <- assign == l
      cost <- cost + abs(sum(V[i, in_l]) * n_sets - total * sum(in_l))
    }
  }
  cost
}

#' Assign item sets to counterbalancing lists so the lists match on the item dimensions
#'
#' The factorial recipe's default deal is by set rank, which balances nothing. This
#' searches instead for an assignment whose lists have near-equal totals on each
#' declared dimension, by steepest-descent pairwise swaps between lists. List sizes
#' are preserved, because a swap exchanges one set for another.
#'
#' The search is deterministic and identical in the R and Python engines: the
#' objective is all-integer (see the notes in this file), the descent takes the single
#' best swap each pass, and ties are broken by the seeded keyed hash rather than by
#' position, so no list is favoured by being numbered first. Because the cost is a
#' non-negative integer that strictly decreases, the search terminates; `max_passes`
#' bounds it anyway and the report says whether the bound was reached.
#'
#' `counterbalance.scale` sets each dimension's unit. `mean`, the default, divides by
#' the dimension's mean, which suits ratio scales only. `mad` balances deviations from
#' the mean in units of the mean absolute deviation, so adding a constant to a
#' dimension, such as writing Zipf frequency as Zipf - 3, leaves the lists unchanged.
#' The report then gives `scale` too, and `cost_unit` names the unit under either
#' scale.
#'
#' Five situations are refused rather than answered with an assignment that would
#' mislead. A Latin-square design is refused because every item already appears in
#' every list there, so there is nothing left to equate, and fewer than two lists
#' leaves no pair of lists to exchange sets between. A design with no resolvable
#' balance dimension is refused, as is one naming a dimension the stimuli do not
#' carry, and the message names the columns. The last refusal is arithmetic: the
#' search stops if the integer objective would leave the range a double represents
#' exactly, since past that point the two engines could disagree.
#'
#' @param stimuli A stimuli data frame with a `set` column and the balance dimensions.
#' @param design A parsed design configuration. Reads `counterbalance.lists`,
#'   `counterbalance.balance_on` (defaulting to `match_on`, then to the continuous
#'   predictor and controls), `counterbalance.max_passes` and `counterbalance.scale`
#'   (`mean` or `mad`, defaulting to `mean`).
#' @param schema The parsed global schema (provides the seed).
#' @return A list with `list_of_set` (a named integer vector mapping each set to a
#'   list) and `report` (the dimensions, the integer cost before and after, the number
#'   of swaps taken, whether the pass bound was reached, the unit the cost is counted
#'   in and, under the `mad` scale, the scale).
#' @export
balance_lists <- function(stimuli, design, schema) {
  n_lists <- as.integer(design[["counterbalance"]][["lists"]] %||% 1L)
  seed <- schema[["seed"]] %||% 1L
  if (identical(.cb_recipe(design), "latin_square_target")) {
    stop(paste("lexsync: counterbalance.optimise does not apply to a Latin-square",
               "design. Every item already appears in every list there, so the lists",
               "are balanced on the items by construction; the rotation decides only",
               "which condition each item takes."), call. = FALSE)
  }
  if (n_lists < 2L) {
    stop("lexsync: counterbalance.optimise needs counterbalance.lists to be 2 or more.",
         call. = FALSE)
  }
  dims <- .balance_dims(design)
  if (!length(dims)) {
    stop(paste("lexsync: counterbalance.optimise has no dimensions to balance. Name",
               "them in counterbalance.balance_on, or give the design a match_on."),
         call. = FALSE)
  }
  absent <- setdiff(dims, names(stimuli))
  if (length(absent)) {
    stop(sprintf("lexsync: cannot balance on column(s) the stimuli do not have: %s.",
                 paste(sprintf("'%s'", sort(absent, method = "radix")), collapse = ", ")),
         call. = FALSE)
  }

  scale <- .balance_scale(design)
  sets <- sort(unique(stimuli$set))
  n_sets <- length(sets)
  V <- .balance_values(stimuli, dims, scale)
  totals <- rowSums(V)
  # Bounded on the sum of the absolute set totals, which bounds every list's total.
  # Under mad the values are deviations whose total is near zero, so a bound on the
  # total would bound nothing. For values of one sign the two bounds are the same.
  if (max(rowSums(abs(V))) * n_sets > .BALANCE_MAX_MAGNITUDE) {
    stop("lexsync: the balance objective would exceed the exact-integer range.",
         call. = FALSE)
  }

  # Start from the default deal, so the search improves on the shipped behaviour
  # rather than starting somewhere unrelated to it.
  assign <- ((seq_len(n_sets) - 1L) %% n_lists) + 1L
  cost0 <- .balance_cost(V, assign, n_lists)

  # Every unordered pair of set POSITIONS, built once. The per-pass work is then
  # vectorised over pairs; a scalar loop over 5000 pairs for a few hundred passes is
  # minutes of R rather than milliseconds.
  if (n_sets > 1L) {
    pairs_i <- rep(seq_len(n_sets - 1L), times = rev(seq_len(n_sets - 1L)))
    pairs_j <- unlist(lapply(seq_len(n_sets - 1L), function(i) (i + 1L):n_sets),
                      use.names = FALSE)
  } else {
    pairs_i <- integer(0); pairs_j <- integer(0)
  }

  max_passes <- as.integer(design[["counterbalance"]][["max_passes"]] %||% 500L)
  n_swaps <- 0L
  cost <- cost0
  hit_bound <- FALSE
  for (pass in seq_len(max(0L, max_passes))) {
    li <- assign[pairs_i]; lj <- assign[pairs_j]
    keep <- which(li != lj)
    if (!length(keep)) break
    a <- pairs_i[keep]; b <- pairs_j[keep]
    la <- li[keep]; lb <- lj[keep]
    # Per-list totals and fair shares, recomputed each pass on integers.
    n_in <- tabulate(assign, nbins = n_lists)
    delta <- numeric(length(keep))
    for (i in seq_len(nrow(V))) {
      Sl <- vapply(seq_len(n_lists), function(l) sum(V[i, assign == l]), numeric(1))
      share <- totals[i] * n_in
      va <- V[i, a]; vb <- V[i, b]
      Sa <- Sl[la]; Sb <- Sl[lb]
      delta <- delta +
        abs((Sa - va + vb) * n_sets - share[la]) +
        abs((Sb - vb + va) * n_sets - share[lb]) -
        abs(Sa * n_sets - share[la]) -
        abs(Sb * n_sets - share[lb])
    }
    best <- min(delta)
    if (best >= 0) break
    tied <- which(delta == best)
    if (length(tied) > 1L) {
      # Hash tie-break, not position: taking the first tied pair would
      # systematically prefer low-numbered sets, and the digest is the package's
      # established way of choosing without a generator. enc2utf8 for the same
      # reason as the shuffle key: digest hashes the stored bytes.
      key <- enc2utf8(paste(.key_part(seed), "balance", .key_part(sets[a[tied]]),
                            .key_part(sets[b[tied]]), sep = "|"))
      h <- vapply(key, function(k) digest::digest(k, algo = "sha256", serialize = FALSE),
                  character(1), USE.NAMES = FALSE)
      pick <- tied[order(h, method = "radix")[1]]
    } else {
      pick <- tied[1]
    }
    swap_a <- a[pick]; swap_b <- b[pick]
    tmp <- assign[swap_a]; assign[swap_a] <- assign[swap_b]; assign[swap_b] <- tmp
    cost <- cost + best
    n_swaps <- n_swaps + 1L
    if (pass == max_passes) hit_bound <- TRUE
  }

  report <- list(dimensions = as.list(dims), cost_before = cost0, cost_after = cost,
                 n_swaps = n_swaps, max_passes_reached = hit_bound,
                 cost_unit = .BALANCE_COST_UNITS[[scale]])
  # Recorded only off the default, so the record of a design that names no scale reads
  # as it did before the option. Its cost_unit names the mean.
  if (!identical(scale, "mean")) report$scale <- scale
  list(list_of_set = stats::setNames(as.integer(assign), as.character(sets)),
       report = report)
}

#' Assign stimuli to lists and a randomised, reproducible trial order
#'
#' The recipe is `counterbalance.recipe` when the design names one, and otherwise
#' the recipe of the paradigm it names. That is the factorial recipe for matched word
#' lists, or a Latin square over conditions for the paired and sentence paradigms. A
#' design's own `events` list has no say in the recipe. The factorial recipe refuses
#' more lists than item sets, since the surplus lists would be empty.
#'
#' Each list's trials are ordered by the seeded keyed hash. `counterbalance.max_run`
#' repairs that order so that no run of one `counterbalance.run_on` value (by default
#' the condition) is longer than the limit, and refuses a limit no order can meet. A
#' design with fillers has the limit applied when the fillers are interleaved, to that
#' order. `counterbalance.orders: m` adds `order_1` to `order_m`, each trial's position
#' in each of m orders of its list, `order_1` being the order `trial` gives.
#'
#' @param stimuli A stimuli data frame (matched set or loaded item table).
#' @param design A parsed design configuration. Reads `paradigm`,
#'   `counterbalance.recipe`, `counterbalance.lists`, `counterbalance.max_run`,
#'   `counterbalance.run_on`, `counterbalance.orders` and `fillers`.
#' @param schema The parsed global schema (provides the seed).
#' @param list_of_set Optional named integer vector mapping each `set` to a list,
#'   from [balance_lists()]. Supplied by the pipeline when
#'   `counterbalance.optimise` is on; when `NULL` the factorial recipe deals sets to
#'   lists by rank as before.
#' @return `stimuli` with added `list` and `trial` columns, and the order columns
#'   when there is more than one order.
#' @export
counterbalance <- function(stimuli, design, schema, list_of_set = NULL) {
  .trial_order_settings(design)
  # Resampled designs counterbalance each replicate (an independent item set) on
  # its own, so trial order is numbered within each replicate.
  if ("replicate" %in% names(stimuli) && length(unique(stimuli$replicate)) > 1L) {
    parts <- lapply(split(stimuli, stimuli$replicate), function(g) {
      rownames(g) <- NULL
      .counterbalance_one(g, design, schema, list_of_set)
    })
    out <- do.call(rbind, parts); rownames(out) <- NULL
    return(out)
  }
  .counterbalance_one(stimuli, design, schema, list_of_set)
}

.counterbalance_one <- function(stimuli, design, schema, list_of_set = NULL) {
  if (identical(.cb_recipe(design), "latin_square_target")) {
    return(counterbalance_latin_square(stimuli, design, schema))
  }
  counterbalance_factorial(stimuli, design, schema, list_of_set)
}

#' @keywords internal
counterbalance_factorial <- function(stimuli, design, schema, list_of_set = NULL) {
  n_lists <- design[["counterbalance"]][["lists"]] %||% 1L
  seed <- schema[["seed"]] %||% 1L

  stimuli$list <- rep(1L, nrow(stimuli))
  sets <- sort(unique(stimuli$set))
  if (n_lists > length(sets)) {
    # Each list receives whole item sets, so lists beyond the number of sets would be
    # empty, and the datasheet would describe lists that do not exist. Must stay
    # identical to the refusal in counterbalance_factorial in counterbalancing.py.
    n_sets <- length(sets)
    have <- if (n_sets == 1L) "there is only 1 item set"
            else sprintf("there are only %d item sets", n_sets)
    empty <- if (n_lists == n_sets + 1L) sprintf("list %d", n_sets + 1L)
             else sprintf("lists %d to %d", n_sets + 1L, as.integer(n_lists))
    stop(sprintf(paste0("lexsync: counterbalance.lists is %d but %s, so %s would be ",
                        "empty; lower lists or add items."), as.integer(n_lists), have, empty),
         call. = FALSE)
  }
  if (n_lists > 1) {
    if (!is.null(list_of_set)) {
      # A balanced assignment from balance_lists(). Looked up by set VALUE, since the
      # map is keyed by it; a set the map does not name is a caller error rather than
      # a silent fall-back to list 1.
      key <- as.character(stimuli$set)
      missing <- setdiff(unique(key), names(list_of_set))
      if (length(missing)) {
        stop(sprintf("lexsync: the balanced list assignment does not cover set(s) %s.",
                     paste(sort(missing, method = "radix"), collapse = ", ")),
             call. = FALSE)
      }
      stimuli$list <- as.integer(list_of_set[key])
    } else {
      # Deal by set RANK, not by set value, so the deal does not depend on `set`
      # being contiguous and starting at 1 (Python's enumerate() does the same).
      deal <- ((seq_along(sets) - 1L) %% n_lists) + 1L
      stimuli$list <- deal[match(stimuli$set, sets)]
    }
  }

  settings <- .trial_order_settings(design)
  # With fillers, .add_blocks() draws the order again over the main trials and the
  # fillers together, and the limit belongs to that order: the main trials alone may be
  # all one condition, as a lexical decision's words are when its pseudowords are
  # fillers.
  limit <- is.null(design[["fillers"]])
  parts <- split(stimuli, stimuli$list)
  stimuli <- do.call(rbind, lapply(parts, function(df) {
    .order_trials(df, seed, settings, .unit_label(df), max_run = limit)
  }))
  rownames(stimuli) <- NULL
  stimuli
}

#' One row per item per list, condition rotated across lists (Latin square)
#'
#' Each item (`set`) contributes exactly one trial to a list, so its target is
#' never repeated within a list. The conditions are balanced when the lists and the
#' item sets are both multiples of the number of conditions, and
#' `.counterbalance_check()` reports a rotation that is not. With `lists` unset the
#' number of lists equals the number of conditions. Mirrors the Python recipe
#' (byte-order condition list, zero-based rotation), so the two engines assign the
#' same condition to each item per list.
#' @keywords internal
counterbalance_latin_square <- function(stimuli, design, schema) {
  seed <- schema[["seed"]] %||% 1L
  conds <- sort(unique(as.character(stimuli$condition)), method = "radix")
  n_cond <- length(conds)
  n_lists <- design[["counterbalance"]][["lists"]] %||% n_cond
  sets <- sort(unique(stimuli$set))
  settings <- .trial_order_settings(design)
  limit <- is.null(design[["fillers"]])

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
    df <- .order_trials(df, seed, settings, .unit_label(df), max_run = limit)
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
#' @examples
#' participant_table(list(list = 1:2, order = c("a", "b")), 6)
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
