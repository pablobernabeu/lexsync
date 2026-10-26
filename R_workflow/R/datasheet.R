# datasheet.R -- materials datasheet and pre-registration template. A machine- and
# human-readable provenance record for a design: where the items came from, how
# they were selected and matched, the realised control, how they were
# counterbalanced, and the seeds, versions and checksums needed to reproduce them
# exactly. The shareable materials record whose scarcity motivates lexsync
# (Bochynska et al., 2023; Roettger, 2019). Mirrors datasheet.py.

# 1.1 added `materials_source$norms` (the design's joined norm tables, with their
# checksums and per-column coverage) and, for a pair-keyed design, a `relational`
# block and a `selection$cross_engine` that states the pair path's guarantee. Both
# follow the rule that anything affecting item selection is recorded here: a norm
# table can carry the manipulated variable itself, and the pair path performs a real
# selection.
#
# 1.2 records the counterbalancing that ran. Each later field of 1.2 adds a line here.
#   counterbalancing$recipe     the recipe counterbalance() applied
#   counterbalancing$lists      the number of lists the stimuli table holds
#   counterbalancing$complete   whether a Latin-square rotation is complete
#   counterbalancing$issues     what leaves it incomplete
#   counterbalancing$cells      the trials per list and condition
#   materials_source$input_normalisation   what NFC normalisation did to the inputs
#                                          (changed, collapsed), present only when it
#                                          changed something
#   selection$incomplete_dropped  the candidates each condition lost for missing a
#                               matched dimension, present only when it lost any
#   counterbalancing$versions   the number of presentation versions, one per
#                               (replicate, list) pair
#   counterbalancing$assignment the rule that gives each participant one version
#   selection$neighbourhood_reference$applied_to
#                               the derived columns a supplied reference_words list
#                               recomputed. selection$neighbourhood_reference is written
#                               only when a recomputation ran.
#   selection$generation_exclude   the known-form lists a generated pseudoword was
#                                  checked against (source, sha256, n_forms each),
#                                  present only when the design names any
#   selection$tie_break        the rule that broke exact ties between equally close
#                               candidates (rule, salt; the salt only for hash),
#                               present for a matched corpus or pool design
#   presentation$response_windows  each response event's window, (event, from,
#                               window_ms); window_ms is null, with duration_column and
#                               timeout_ms, when the stimulus's duration varies by trial
#                               (with a window, analysis$response says where a reaction
#                               time starts)
#   materials_source$exclusions   the design's exclude_words (path, sha256, n_listed,
#                                  n_removed), present only when the design has the key
#   materials_source$provenance    for a corpus or generated design, the credit of the
#                                  lexicon read (see .lexicon_provenance)
#   reproducibility$schema_path   the schema file the run read, in POSIX form
#   realised_control[]$condition, realised_control[]$reference
#                               the pair a row compares. Every pair is reported, the
#                               anchor rows first
#   realised_control[]$mean_diff  the reference mean minus the condition mean, in the
#                               dimension's own unit
#   realised_control[]$role     manipulated, controlled or uncontrolled for the pair
#   realised_control[]$sd, $sd_ratio, $window_low, $window_high
#                               a continuous design's realised SDs, set against an even
#                               spread (the predictor) or the pool (a control), and each
#                               control's window
#   items$n_per_condition_realised  the items each condition holds, as (condition, n),
#                               or (replicate, condition, n) for resampled sets
#   design$n_per_condition      the request the selector applied, its default when the
#                               design gives none
#   presentation$response_mapping  the key each condition takes, (conditions, keys,
#                               rotate_by_list, source), present only when a mapping
#                               applies: the design's own or a lexical decision's default
#   materials_source$zipf_derivation   for a lexicon carrying freq_permillion, the
#                                      positive rates it holds and how many of them put
#                                      Zipf within 1e-9 of a rounding boundary
#                                      (n_values, near_boundary)
#   counterbalancing$max_run    the run limit (k, run_on, longest), longest giving the
#                               longest run realised in each presentation version as
#                               (replicate, list, longest_run), present only when the
#                               design sets counterbalance.max_run
#   counterbalancing$orders     the trial orders per list (m, rule), present only when
#                               the design sets counterbalance.orders above 1
#   counterbalancing$optimise$scale  the scale the balance optimiser quantised on,
#                               present only when it is not the default, mean (whose
#                               cost_unit names it)
DATASHEET_VERSION <- "1.2"

# Datasheet labels for the pseudoword generators in generation.R, keyed by the
# items.generation.method token. Kept character-for-character identical to
# _GENERATION_LABELS in datasheet.py so the two engines' records stay comparable.
.GENERATION_LABELS <- list(
  letter_substitution = "constrained letter substitution (deterministic pseudowords)",
  subsyllabic = "subsyllabic constituent swap (Wuggy-style, deterministic pseudowords)"
)

# What the Methods paragraph says of the balance optimiser's scale, keyed by
# counterbalance.scale. The default, mean, adds nothing. Kept character-for-character
# identical to _BALANCE_SCALE_NOTES in datasheet.py.
.BALANCE_SCALE_NOTES <- list(
  mad = paste(" on each dimension's deviations from its mean, in units of its mean",
              "absolute deviation")
)

# The credit the datasheet and the Methods paragraph give a lexicon lexsync ships. Kept
# character-for-character identical to the strings in datasheet.py.
.PROVENANCE_WORDFREQ <- paste0(
  "wordfreq (Speer, 2022), data CC BY-SA 4.0; full corpus licence and citation at ",
  "https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md")
.PROVENANCE_SCREENED <- paste0(
  "wordfreq (Speer, 2022) screened against SUBTLEX-US (Brysbaert & New, 2009), data ",
  "CC BY-SA 4.0; forms absent from SUBTLEX-US or beginning with a lower-case letter in ",
  "under 10% of their uses are marked nonstandard, and N and OLD20 count only the ",
  "unmarked forms; full corpus licence and citation at ",
  "https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md")
# The English example slice holds only forms that en_v2.csv keeps, so it marks none.
.PROVENANCE_SCREENED_SLICE <- paste0(
  "wordfreq (Speer, 2022) screened against SUBTLEX-US (Brysbaert & New, 2009), data ",
  "CC BY-SA 4.0; forms absent from SUBTLEX-US or beginning with a lower-case letter in ",
  "under 10% of their uses are left out, and N and OLD20 count neighbours only among ",
  "the forms the screen keeps; full corpus licence and citation at ",
  "https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md")

# The lexica lexsync ships, the repository's derived lexica and the example slices both
# packages bundle. Each is keyed by the SHA-256 of its bytes with CRLF line ends read as
# LF (see .lf_sha256) and maps to its file and its credit. A rebuilt file needs its new
# key here and in _BUNDLED_LEXICA in datasheet.py, and the tests in
# test-lexicon-provenance.R fail until it has one.
.BUNDLED_LEXICA <- list(
  "575833489e04d6a4001fda56a56e3daa383811dece1f819c44060ee79ca56976" =
    list(file = "corpora/derived/en.csv", provenance = .PROVENANCE_WORDFREQ),
  "46815cd56ac036cb841460a2ea6205ac374eddb6ca26275bb1a2fbafc7c5d626" =
    list(file = "corpora/derived/en_v2.csv", provenance = .PROVENANCE_SCREENED),
  "e9f93013c16ec9745c0d02f82c697f2488c328365b95b57c5f04ac2565c123ea" =
    list(file = "corpora/derived/es.csv", provenance = .PROVENANCE_WORDFREQ),
  "0f77aec3fe307ed38f1e69e69f7c80ee93e38ffb8c0622b817fd2c26d15114d5" =
    list(file = "corpora/derived/es_gender.csv", provenance = .PROVENANCE_WORDFREQ),
  "74666b257c1ad7bce4694a4b172796fbdc08c1414183bea5f28faa5ed3ab2fc4" =
    list(file = "corpora/derived/zh.csv", provenance = .PROVENANCE_WORDFREQ),
  "34a3c81cb559a42918864f5ecd2bcea93647cc4b0058dd03132ffe8723f4c310" =
    list(file = "en_example.csv", provenance = .PROVENANCE_SCREENED_SLICE),
  "7afbdd7db2d84e3f252a40baafe1e53fa4fde1e4ae5256497cb1ac79f28947ec" =
    list(file = "es_example.csv", provenance = .PROVENANCE_WORDFREQ),
  "d42f5afdc16d0f23ec5fc12dd58afbd1e639e9191f2c4611d9262eabbb982aca" =
    list(file = "zh_example.csv", provenance = .PROVENANCE_WORDFREQ)
)

# The SHA-256 of a file's bytes with every CRLF read as LF. Git stores the lexica with LF
# line ends. A checkout that converts them to CRLF, as one OneDrive copy of this
# repository did, holds the same lexicon under another checksum of its raw bytes.
# Mirrors _lf_sha256 in datasheet.py.
.lf_sha256 <- function(path) {
  bytes <- readBin(path, "raw", file.info(path)$size)
  n <- length(bytes)
  if (n > 1L) {
    cr <- which(bytes[-n] == as.raw(13L) & bytes[-1L] == as.raw(10L))
    if (length(cr)) bytes <- bytes[-cr]
  }
  if (!length(bytes)) return(digest::digest("", algo = "sha256", serialize = FALSE))
  digest::digest(bytes, algo = "sha256", serialize = FALSE)
}

.file_name <- function(path) basename(gsub("\\", "/", path, fixed = TRUE))

# The registry's citation for a lexicon fetch_corpus() put in the cache, or NULL. The
# file must lie in lexsync's cache, and its name less `.csv` must name a corpus in the
# registry, or be `<language>_wordfreq` for a language the wordfreq connector lists.
# Those are the names fetch_corpus() gives what it fetches, the second in the Python
# engine only. Mirrors _registry_citation in datasheet.py.
.registry_citation <- function(path) {
  name <- .file_name(path)
  if (!endsWith(name, ".csv")) return(NULL)
  where <- function(p) {
    p <- normalizePath(p, winslash = "/", mustWork = FALSE)
    if (identical(.Platform$OS.type, "windows")) tolower(p) else p
  }
  if (!identical(where(dirname(path)), where(path.expand(lexsync_cache_dir())))) return(NULL)
  reg <- tryCatch(.read_yaml_utf8(default_registry_path()), error = function(e) NULL)
  if (!.is_mapping(reg)) return(NULL)
  stem <- sub("\\.csv$", "", name)
  is_text <- function(x) is.character(x) && length(x) == 1L && !is.na(x)
  corpora <- reg[["corpora"]]
  entry <- if (.is_mapping(corpora)) corpora[[stem]] else NULL
  if (.is_mapping(entry) && is_text(entry[["citation"]])) return(entry[["citation"]])
  connector <- reg[["wordfreq_connector"]]
  if (.is_mapping(connector) && is_text(connector[["citation"]]) &&
      endsWith(stem, "_wordfreq") &&
      sub("_wordfreq$", "", stem) %in% unlist(connector[["languages"]], use.names = FALSE)) {
    return(connector[["citation"]])
  }
  NULL
}

# The credit for the lexicon a corpus or generated design read. A lexicon lexsync ships
# is recognised by the checksum .lf_sha256() gives, and is credited to wordfreq, or for
# en_v2.csv and the English example slice drawn from it to wordfreq screened against
# SUBTLEX-US with the screening rule stated. A corpus fetch_corpus() put in the cache is
# credited by the registry's citation. Any
# other file is the user's own and is named by its file name and the first twelve
# hexadecimal digits of its SHA-256, which materials_source$sha256 holds in full. A
# study selecting from SUBTLEX-US, or from a lexicon of its own, therefore does not cite
# wordfreq. Mirrors _lexicon_provenance in datasheet.py.
.lexicon_provenance <- function(path) {
  if (is.null(path) || length(path) != 1L || is.na(path) || !nzchar(path)) {
    return("a user-supplied lexicon")
  }
  name <- .file_name(path)
  if (!file.exists(path) || dir.exists(path)) {
    return(sprintf("a user-supplied lexicon (%s)", name))
  }
  bundled <- .BUNDLED_LEXICA[[.lf_sha256(path)]]
  if (!is.null(bundled)) return(bundled$provenance)
  cited <- .registry_citation(path)
  if (!is.null(cited)) return(cited)
  sprintf("a user-supplied lexicon (%s, sha256 %s)", name, substr(sha256_file(path), 1L, 12L))
}

.versions_R <- function(engine) {
  v <- list(engine = engine,
            lexsync = tryCatch(as.character(utils::packageVersion("lexsync")),
                               error = function(e) "0.1.1"),
            R = paste(R.version$major, R.version$minor, sep = "."))
  for (p in c("readr", "stringdist", "jsonlite", "digest", "yaml", "stringi")) {
    pv <- tryCatch(as.character(utils::packageVersion(p)), error = function(e) NULL)
    if (!is.null(pv)) v[[p]] <- pv
  }
  # The OS completes the environment record; per-engine, like the rest of the block.
  v$os <- paste(Sys.info()[["sysname"]], Sys.info()[["machine"]])
  v
}

# Whether the R and Python engines select byte-identical materials. The
# deterministic methods are byte-identical; mahalanobis and optimal are the
# exception (covariance inverse / assignment solver; see matching.R). Mirrors
# datasheet.py.
#
# `selected` distinguishes the two things an item table can mean. A plain table
# design does no selection, so there is nothing for the engines to agree on and "n/a"
# is the whole story. A pair-keyed continuous design selects over that table, and that
# selection was measured to be byte-identical, so answering "n/a" there would
# understate the guarantee on the one path where a reader most needs it.
.cross_engine <- function(method, source, selected = FALSE) {
  if (identical(source, "table") && !isTRUE(selected)) return("n/a (user-supplied items)")
  if (!is.null(method) && method %in% c("mahalanobis", "optimal"))
    return("approximate (platform linear algebra)")
  "byte-identical"
}

# The pair-keyed part of the record, or NULL for a design that is not pair-keyed.
#
# Derived from the design and the realised stimuli rather than passed in, so both
# engines compute it from the same two objects and cannot disagree about it.
#
# Three of these fields answer questions the rest of the datasheet gets wrong for a
# pair design. `n_pairs` is stated because `items$n_total` counts ROWS, which is one
# per pair per condition, so a reader comparing it against the design's
# `n_per_condition` would find it doubled. The member lexicon is named and checksummed
# because it is where every member-level control came from, and nothing else in the
# record mentions it. `materials_source` names the item table. And the member
# dimensions are separated from the relational ones because they are different kinds
# of variable: `target.frequency` is a property of one word, `pair.overlap` is a
# property of the pair, and only the second is unavailable from any word-level norm
# database. Mirrors datasheet.py.
.relational_record <- function(design, stimuli) {
  items_cfg <- design[["items"]] %||% list()
  members <- unlist(items_cfg[["members"]] %||% list(), use.names = FALSE)
  if (!length(members)) return(NULL)
  cols <- names(stimuli)
  # The union over members, not the first member's alone. .join_member_norms gives
  # every member the same dimensions, so the sets coincide in anything the pipeline
  # produced; taking the union means a hand-built frame cannot report an empty list
  # merely because the first member happens to carry no prefixed column.
  # startsWith, not a regex: a member name is user-supplied and may contain a
  # character a regex would read as syntax.
  member_dims <- unique(unlist(lapply(members, function(m) {
    prefix <- paste0(m, ".")
    substring(cols[startsWith(cols, prefix)], nchar(prefix) + 1L)
  }), use.names = FALSE))
  lexicon <- items_cfg[["lexicon"]] %||% design[["lexicon"]]
  list(members = as.list(members),
       n_pairs = length(unique(stimuli$set)),
       member_lexicon = lexicon,
       member_lexicon_sha256 = sha256_file(lexicon),
       member_dimensions = as.list(sort(member_dims, method = "radix")),
       relational_dimensions = as.list(sort(cols[startsWith(cols, "pair.")], method = "radix")))
}

# The tolerance windows recorded below come from .resolve_tolerance_k() in design.R,
# the resolver the matchers use, so the record cannot drift from the selection.

.controlled_dims <- function(design, source) {
  # A supplied pool goes through the same matcher as a corpus, so it controls the same
  # dimensions; only the origin of the candidate words differs.
  if (source %in% c("corpus", "pool")) unlist(design[["match_on"]], use.names = FALSE)
  else if (identical(source, "generate")) "length"
  else character(0)
}

# Whether two conditions' define_by entries on one dimension select alike. Absent from
# both is alike, and absent from one only is not. A two-number entry is a range
# compared bound by bound, numerically, so [5, 7] and [5.0, 7.0] are alike. Any other
# entry is a set of permitted values, compared as a set: numerically when both hold
# only numbers, and otherwise as text. Mirrors _same_window in datasheet.py.
.same_window <- function(a, b) {
  if (is.null(a) || is.null(b)) return(is.null(a) && is.null(b))
  a <- unlist(a, use.names = FALSE); b <- unlist(b, use.names = FALSE)
  if (length(a) != length(b)) return(FALSE)
  if (is.numeric(a) && is.numeric(b)) {
    a <- as.numeric(a); b <- as.numeric(b)
    if (length(a) != 2L) { a <- sort(a); b <- sort(b) }
    return(isTRUE(all(a == b)))
  }
  identical(sort(as.character(a), method = "radix"), sort(as.character(b), method = "radix"))
}

# The role of a realised-control row, as a function of (condition, reference,
# dimension). A row is "manipulated" when the two conditions' define_by entries on the
# dimension differ, or when the dimension is a continuous design's predictor. It is
# "controlled" when the dimension is among `controlled`, the dimensions the selection
# matched on (match_on, or length for generated pseudowords), and "uncontrolled"
# otherwise. In a 2 x 2 design, frequency is manipulated between a high- and a
# low-frequency cell but not between two cells that share its window. run_pipeline()
# passes this to match_report(), and build_datasheet() falls back on it for a report
# without roles. Mirrors _comparison_roles in datasheet.py.
.comparison_roles <- function(design, controlled) {
  windows <- list()
  for (cond in design[["conditions"]] %||% list()) {
    if (is.list(cond) && is.list(cond[["define_by"]])) {
      windows[[as.character(cond[["name"]])]] <- cond[["define_by"]]
    }
  }
  predictor <- if (is.list(design[["continuous"]])) design[["continuous"]][["predictor"]]
  controlled <- unlist(controlled, use.names = FALSE)
  function(condition, reference, dimension) {
    a <- windows[[as.character(condition)]] %||% list()
    b <- windows[[as.character(reference)]] %||% list()
    if (identical(dimension, predictor) || !.same_window(a[[dimension]], b[[dimension]])) {
      return("manipulated")
    }
    if (dimension %in% controlled) "controlled" else "uncontrolled"
  }
}

.r4 <- function(v) if (is.null(v) || is.na(v)) NULL else .round_dp(as.numeric(v), 4)

# The TOST p as the Markdown shows it: four places, the precision the comparisons
# report stores, through .fmt_dp like every other number. Printed raw, it would read
# 9e-04 and 1 here and 0.0009 and 1.0 in Python. A p that rounds to zero at
# four places is shown as the bound it is below. Mirrors _fmt_tost_p in datasheet.py.
.fmt_tost_p <- function(p) {
  s <- .fmt_dp(p, 4)
  if (identical(s, "0.0000")) "< 0.0001" else s
}

# The response the analysis models, with where its reaction time starts, from the first
# response window: a reaction time from the onset of the stimulus the response answers,
# or from the opening of a window after it. A design without a response event keeps the
# generic outcome. Mirrors _response_text in datasheet.py.
.response_text <- function(windows, events) {
  if (!length(windows)) return("the trial outcome (e.g. reaction time or accuracy)")
  w <- windows[[1]]
  if (identical(w[["from"]], "offset")) {
    return(sprintf(paste("reaction time from the opening of a response window after the",
                         "stimulus; responses collected for %d ms; a response ends the",
                         "trial"), as.integer(w[["window_ms"]])))
  }
  target <- as.character(events[[w[["event"]] - 1L]][["content"]] %||% "")
  span <- if (!is.na(w[["window_ms"]])) sprintf("for %d ms", as.integer(w[["window_ms"]])) else
    sprintf("until %d ms after its offset", as.integer(w[["timeout_ms"]]))
  sprintf(paste("reaction time from the onset of `%s`; responses collected %s; a response",
                "ends the trial"), target, span)
}

# The response window, for the Methods text, from the first response window the record
# holds. Empty without one, and for a record written before the field existed. A record
# read back from JSON gives a varying window as NULL, one built here as NA. Mirrors
# _response_note in datasheet.py.
.response_note <- function(ds) {
  windows <- ds[["presentation"]][["response_windows"]]
  if (is.null(windows) || !length(windows)) return("")
  w <- windows[[1]]
  window_ms <- w[["window_ms"]]
  if (identical(w[["from"]], "offset")) {
    return(sprintf(paste(" Responses were collected in a %d ms window that opened after the",
                         "stimulus, and a response ended the trial."), as.integer(window_ms)))
  }
  if (is.null(window_ms) || is.na(window_ms)) {
    return(sprintf(paste(" Responses were collected from target onset until %d ms after its",
                         "offset, and a response ended the trial."),
                   as.integer(w[["timeout_ms"]])))
  }
  sprintf(paste(" Responses were collected from target onset until %d ms after it, and a",
                "response ended the trial."), as.integer(window_ms))
}

# The response mapping the experiments score against, as the record keeps it:
# list(conditions, keys, rotate_by_list, source), the key each condition takes in list 1,
# the keys the response event allows in their order, whether the mapping rotates across
# lists and whether it is the design's own or a lexical decision's default. NULL when no
# mapping applies. The keys are a list, so jsonlite writes them as an array even when
# there is one. Mirrors _response_mapping_record in datasheet.py.
.response_mapping_record <- function(design) {
  mapping <- .response_mapping(design)
  if (is.null(mapping)) return(NULL)
  list(conditions = mapping, keys = as.list(.response_keys(design)),
       rotate_by_list = .rotates(design),
       source = if (is.null(design[["response_mapping"]])) "default" else "design")
}

# The response mapping, for the Methods text: which key the participants pressed for which
# condition, and how it rotated across lists. The keys come in the response event's order
# and the conditions that share a key in code-point order, so a record read back from
# either engine's JSON renders the same text, though the Python engine writes its objects
# with sorted keys. A rotation is mentioned only when the record holds more than one list.
# Empty without a mapping, and for a record written before the field existed. Mirrors
# _mapping_note in datasheet.py.
.mapping_note <- function(ds) {
  rec <- ds[["presentation"]][["response_mapping"]]
  if (is.null(rec) || !length(rec)) return("")
  conds <- names(rec[["conditions"]])
  keys <- vapply(rec[["conditions"]], function(k) as.character(k), character(1),
                 USE.NAMES = FALSE)
  named <- c(word = "words", pseudoword = "pseudowords")
  phrases <- character(0)
  for (key in unique(as.character(unlist(rec[["keys"]], use.names = FALSE)))) {
    group <- conds[keys == key]
    if (!length(group)) next
    group <- group[order(group, method = "radix")]
    what <- if (length(group) == 1L && group %in% names(named)) named[[group]]
            else paste(.and_join(group), "trials")
    phrases <- c(phrases, paste(.key_label(key), "for", what))
  }
  text <- paste0(" Participants pressed ", .and_join(phrases))
  lists <- as.integer(ds[["counterbalancing"]][["lists"]] %||% 1L)
  if (isTRUE(rec[["rotate_by_list"]]) && lists > 1L) {
    text <- paste0(text, if (length(rec[["keys"]]) == 2L)
      " in odd-numbered lists and the reverse in even-numbered lists"
      else " in list 1, and the keys rotated by one place in each further list")
  }
  paste0(text, ".")
}

# Words or phrases joined as a list in prose: "a", "a and b", "a, b and c". Mirrors
# _and_join in datasheet.py.
.and_join <- function(parts) {
  parts <- as.character(unlist(parts, use.names = FALSE))
  n <- length(parts)
  if (n < 2L) return(paste(parts, collapse = ""))
  paste0(paste(parts[-n], collapse = ", "), " and ", parts[n])
}

# The items per condition the selector was asked for: the design's n_per_condition, else
# the default of the selector that ran, the matcher's, the continuous selector's or the
# generator's. An item table without a continuous block selects nothing, so it has a
# request only when the design states one. Mirrors _requested_n in datasheet.py.
.requested_n <- function(design, source, is_continuous) {
  default <- if (isTRUE(is_continuous)) .N_DEFAULT_CONTINUOUS
             else if (source %in% c("corpus", "pool")) .N_DEFAULT_MATCHED
             else if (identical(source, "generate")) .N_DEFAULT_GENERATED
             else NULL
  .resolve_n(design, default)
}

# The items each condition holds in the stimuli, as (condition, n) records in the order
# of items$conditions. Resampled stimuli are counted per replicate, as (replicate,
# condition, n), replicates in ascending order, since each replicate is a set of its own.
# A pair design holds one row per pair in each condition, so it counts pairs. Mirrors
# _realised_counts in datasheet.py.
.realised_counts <- function(stimuli, conditions) {
  labels <- as.character(stimuli[["condition"]])
  if (!"replicate" %in% names(stimuli)) {
    return(lapply(conditions, function(cn) list(condition = cn, n = sum(labels == cn))))
  }
  out <- list()
  reps <- stimuli[["replicate"]]
  for (rep in sort(unique(reps))) {
    for (cn in conditions) {
      n <- sum(reps == rep & labels == cn, na.rm = TRUE)
      if (n > 0L) {
        out[[length(out) + 1L]] <- list(replicate = as.integer(rep), condition = cn, n = n)
      }
    }
  }
  out
}

# The matched dimensions the suggested model adjusts for, and those it leaves out. A
# corpus or pool design's match_on dimensions enter, in their order, when they vary among
# the selected items. One that is the same for every item, as length is among
# two-character Chinese words, would give the model a column of zeros, so it is left
# out, as is one the stimuli do not hold. Any other design has none. Mirrors _covariates
# in datasheet.py.
.covariates <- function(design, source, stimuli) {
  kept <- character(0)
  left_out <- character(0)
  if (!source %in% c("corpus", "pool")) return(list(kept = kept, left_out = left_out))
  for (dim in unlist(design[["match_on"]], use.names = FALSE)) {
    values <- if (dim %in% names(stimuli))
      unique(stats::na.omit(.numeric_values(stimuli[[dim]]))) else numeric(0)
    if (length(values) > 1L) kept <- c(kept, dim) else left_out <- c(left_out, dim)
  }
  list(kept = kept, left_out = left_out)
}

# The sentences the notes of the suggested models share. Kept character-for-character
# identical to the strings in _analysis in datasheet.py.
.NOTE_CROSSED <- paste0("Crossed random effects for subjects and items guard against the ",
                        "language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008).")
.NOTE_SIMPLIFY <- paste0("If the model is singular or fails to converge, simplify it as ",
                         "Matuschek et al. (2017) describe.")
.NOTE_SYNTAX <- paste0("The formula is lme4 syntax, for lme4 in R or pymer4 in Python; ",
                       "statsmodels MixedLM cannot take it directly and needs the random ",
                       "effects restated in its own arguments.")
.NOTE_DIAGNOSTICS <- paste0("The equivalence tests in the realised control are ",
                            "post-selection diagnostics on deterministically selected items, ",
                            "not inferential tests over a sample.")

# A suggested crossed mixed-model formula for the design, and a note on it. Handing the
# user an items-crossed model guards against the language-as-fixed-effect fallacy
# (Clark, 1973; Baayen et al., 2008): items are a random sample of the language, so an
# analysis that treats them as fixed over-generalises. The factor is the stimuli's
# `condition` column, which in a lexical decision codes lexicality. Every participant
# sees every condition, so subjects take a random slope for it. Items take one too when
# the counterbalancing recipe that ran rotates the conditions over the items by a Latin
# square, which shows each item in more than one condition across the lists. `covariates`
# are a matched design's matched dimensions that vary among its items, entered centred on
# the stimuli file's own columns, since matching leaves residual differences and
# Sassenhagen and Alday (2016) recommend adjusting for potential confounds; `left_out`
# are those that do not vary. A design with more than two conditions is told how to
# recode crossed factors.
#
# A continuous design regresses on its predictor and controls. A pair design with more
# than one condition crosses the condition with the predictor, and its items, which
# carry every condition, take the condition slope. The predictor is a property of the
# item, so they take no slope for it.
#
# The note calls the structure maximal (Barr et al., 2013) only when every fixed effect
# that varies within subjects or items has a random slope there. A covariate or a
# control varies within subjects and enters as a fixed effect only, so a design with one
# is described by its slopes. Mirrors _analysis in datasheet.py.
.analysis_R <- function(design, source,
                        response = "the trial outcome (e.g. reaction time or accuracy)",
                        recipe = "factorial", n_conditions = 2L, covariates = character(0),
                        left_out = character(0)) {
  cont <- design[["continuous"]]
  if (!is.null(cont)) {
    predictor <- cont[["predictor"]]
    controls <- unlist(cont[["controls"]], use.names = FALSE)
    tail <- paste0(vapply(controls, function(cc) paste0(" + ", cc), character(1)),
                   collapse = "")
    if (length(design[["items"]][["members"]]) && n_conditions > 1L) {
      model <- sprintf(paste0("response ~ condition * %s%s + (1 + condition * %s | subject)",
                              " + (1 + condition | item)"), predictor, tail, predictor)
      slopes <- paste0("Begin with random slopes for condition, ", predictor, " and their ",
                       "interaction by subject and for condition by item (Barr et al., ",
                       "2013); the controls enter as fixed effects only. Centre ",
                       predictor, " and sum-code condition, so that each main effect is ",
                       "estimated at the average of the other.")
    } else {
      model <- sprintf("response ~ %s%s + (1 + %s | subject) + (1 | item)", predictor, tail,
                       predictor)
      slopes <- paste0("Begin with a random slope for ", predictor, " by subject (Barr et al., ",
                       "2013); the controls enter as fixed effects only.")
    }
    note <- paste0("The predictor is kept continuous and analysed by regression or a mixed ",
                   "model rather than dichotomised (Kuperman, 2015; Liben-Nowell et al., ",
                   "2019); the controls enter as covariates. ", .NOTE_CROSSED, " ", slopes,
                   " ", .NOTE_SIMPLIFY)
    # A pair design's member-prefixed terms carry a dot, which R formulas accept
    # but Patsy reads as syntax, so the Python analyst needs the quoting stated.
    if (any(grepl(".", c(predictor, controls), fixed = TRUE)))
      note <- paste0(note, " Dotted dimension names are valid in R formulas but must ",
                     "be quoted as Q(\"...\") in Patsy-style Python interfaces.")
    return(list(response = response, suggested_model = model, note = note))
  }
  fixed <- paste0("condition", paste0(vapply(covariates, function(d)
    sprintf(" + scale(%s, scale = FALSE)", d), character(1)), collapse = ""))
  item_re <- if (identical(recipe, "latin_square_target")) "(1 + condition | item)"
             else "(1 | item)"
  note <- .NOTE_CROSSED
  if (identical(source, "generate") || identical(design[["paradigm"]], "lexical_decision"))
    note <- c(note, "The condition column codes lexicality, word or pseudoword.")
  if (length(covariates))
    note <- c(note, paste0("The matched dimensions enter as centred covariates, computed ",
                           "from the stimuli file's own columns, because matching leaves ",
                           "residual differences that the analysis can adjust for ",
                           "(Sassenhagen & Alday, 2016)."))
  if (length(left_out)) {
    one <- length(left_out) == 1L
    note <- c(note, sprintf(paste("The matched %s %s %s constant among the selected items,",
                                  "so %s left out."),
                            if (one) "dimension" else "dimensions", .and_join(left_out),
                            if (one) "is" else "are", if (one) "it is" else "they are"))
  }
  note <- c(note, if (length(covariates))
    paste0("Begin with random slopes for condition, the manipulated factor, by subject ",
           "and, where it varies within items, by item (Barr et al., 2013); the matched ",
           "covariates enter as fixed effects only.")
    else "Begin with this maximal structure (Barr et al., 2013).")
  note <- c(note, .NOTE_SIMPLIFY)
  if (n_conditions > 2L)
    note <- c(note, paste0("If the conditions cross two or more factors, recode condition ",
                           "into those factors (for example frequency * neighbourhood) with ",
                           "sum coding."))
  note <- c(note, .NOTE_SYNTAX, .NOTE_DIAGNOSTICS)
  list(response = response,
       suggested_model = sprintf("response ~ %s + (1 + condition | subject) + %s", fixed,
                                 item_re),
       note = paste(note, collapse = " "))
}

#' Assemble the materials datasheet for one design
#'
#' @param design A parsed design list.
#' @param schema The parsed global schema (`schema.yaml`).
#' @param report The match report, the list of `descriptives` and `comparisons` data
#'   frames that [match_report()] or [match_report_continuous()] returns, or `NULL`
#'   when the design has none, as for an item table without a continuous selection.
#' @param stimuli The selected stimulus data frame.
#' @param source_path Path of the lexicon or item table the stimuli came from.
#' @param artifacts Named list of the artifact paths written for the design:
#'   `stimuli`, `descriptives`, `comparisons` and `experiments`, the result of
#'   [export_experiments()]. Each file is recorded with its sha256: the three tables,
#'   then every file in `experiments$files`, the loop and text tables included, or the
#'   three experiment paths of a result that has no `files`.
#' @param seed The integer seed recorded for the counterbalanced trial order.
#' @param engine Engine label recorded in the record (default `"R"`).
#' @param candidate_pool Optional list of per-condition candidate-pool sizes
#'   (`list(condition, n_candidates)`) recording how many items satisfied each
#'   condition's window before matching, the size of the discretionary pool the
#'   selection drew from, reported so that item-selection bias is auditable
#'   (Forster, 2000; Simmons et al., 2011).
#' @param norms Optional list of norm-table provenance records, from the design's
#'   `norms:` block (see the pipeline). Each names a file, its sha256, the join key
#'   and the per-column coverage. Recorded because a norm table can supply the very
#'   variable a design manipulates, so a record that omitted it would describe a
#'   selection over columns of unstated origin.
#' @param balance Optional balance-optimiser report, from [balance_lists()].
#'   Recorded because it decides which items each participant sees.
#' @param blocks Optional practice/filler block report. Recorded because those
#'   trials are presented but not analysed, so the presented and analysed counts
#'   differ and the record must say why.
#' @param design_path,schema_path Optional paths of the design and schema files
#'   the run read; when given, their sha256 checksums complete the
#'   reproducibility record, because those two files decide everything the seed
#'   does not. The schema's path is recorded too, in POSIX form, since an unnamed
#'   schema is chosen from several candidates.
#' @param selection_audit Optional matcher audit record; its `window_relaxations`
#'   entries are recorded because a relaxed window changes what "matched" means
#'   for that condition. Its `incomplete_dropped` entries (`list(condition, n)`)
#'   count the candidates excluded for missing a matched dimension, which
#'   `candidate_pool` still includes. They are recorded because the selection drew
#'   on a smaller pool than the window holds.
#' @param neighbourhood_reference Optional record of a supplied reference the
#'   derived dimensions were recomputed against
#'   (`list(source, n_words, sha256, applied_to)`, where `applied_to` lists the
#'   recomputed columns), recorded verbatim.
#' @param counterbalance_check Optional report of the pipeline's rotation check on
#'   the counterbalanced table. Without it, the check is run here on `stimuli`. The
#'   record gives the recipe that ran and the lists the table holds, or for a table
#'   without a `list` column the lists [counterbalance()] would deal. It says whether
#'   a Latin-square rotation is complete and counts the trials per list and
#'   condition. It also gives the presentation versions, one per (replicate, list)
#'   pair, and the rule that assigns each participant one of them.
#' @param input_normalisation Optional `list(changed, collapsed)`: how many text
#'   keys the run's inputs held that Unicode NFC normalisation rewrote, and how many
#'   duplicates the rewriting created and removed. Recorded only when given, which
#'   the pipeline does only when either count is above zero, because a merged
#'   spelling changes the candidate pool.
#' @param generation_exclude Optional list of the known-form lists of a generated
#'   design's `items.generation.exclude`, each `list(source, sha256, n_forms)`. A
#'   pseudoword was refused for equalling any form in them, so they decide which
#'   pseudowords a run produces, as the lexicon does.
#' @param exclusions Optional record of a corpus, pool or generated design's
#'   `exclude_words`, as `list(path, sha256, n_listed, n_removed)`. It gives the file,
#'   or `"inline"` for a list in the design, its checksum, the number of distinct words
#'   it lists and the number of candidates it removed. Recorded as
#'   `materials_source$exclusions`, because the words decide which candidates the
#'   selection could draw.
#' @param zipf_derivation Optional `list(n_values, near_boundary)` for a lexicon
#'   carrying `freq_permillion`, as [normalise_lexicon()] writes one: how many positive
#'   rates it holds, and how many put Zipf = log10(per million) + 3 within 1e-9 of a
#'   three-place rounding boundary, where the two engines' `log10` could round a
#'   derived value apart. Recorded as `materials_source$zipf_derivation`.
#' @param trial_order Optional record of the trial-order settings on the presented
#'   trials, which the pipeline passes. Without it, the record is taken from `stimuli`.
#'   It gives `counterbalancing$max_run` (`list(k, run_on, longest)`, the longest run
#'   realised in each presentation version) when the design limits runs, and
#'   `counterbalancing$orders` (`list(m, rule)`) when it asks for more than one trial
#'   order.
#' @details For a corpus or generated design, `materials_source$provenance` credits the
#'   lexicon that `source_path` names. A lexicon lexsync ships is credited by its
#'   source, a corpus fetched into the cache by the registry's citation, and any other
#'   file by its file name and checksum.
#'
#'   `design$n_per_condition` is the request the selector applied, the selector's
#'   default when the design gives none, and `items$n_per_condition_realised` counts
#'   the items each condition holds in `stimuli`, per replicate for resampled sets, so
#'   a selection that fell short of the request under `shortfall: allow` shows it. The
#'   suggested analysis keys its by-item slope on the recipe that ran and adds a matched
#'   design's matched dimensions that vary among its items as covariates.
#' @references Forster, K. I. (2000). The potential for experimenter bias effects in word
#'   recognition experiments. *Memory & Cognition, 28*(7), 1109-1115.
#'   \doi{10.3758/BF03211812}
#'
#'   Simmons, J. P., Nelson, L. D., & Simonsohn, U. (2011). False-positive psychology:
#'   Undisclosed flexibility in data collection and analysis allows presenting anything
#'   as significant. *Psychological Science, 22*(11), 1359-1366.
#'   \doi{10.1177/0956797611417632}
#' @return The datasheet as a nested list, ready for [write_datasheet()].
#' @export
build_datasheet <- function(design, schema, report, stimuli, source_path, artifacts,
                            seed, engine = "R", candidate_pool = NULL, norms = NULL,
                            balance = NULL, blocks = NULL, design_path = NULL,
                            schema_path = NULL, selection_audit = NULL,
                            neighbourhood_reference = NULL, counterbalance_check = NULL,
                            input_normalisation = NULL, generation_exclude = NULL,
                            exclusions = NULL, zipf_derivation = NULL,
                            trial_order = NULL) {
  source <- design[["items"]][["source"]] %||% "corpus"
  is_continuous <- .is_continuous(design)
  controlled <- .controlled_dims(design, source)
  relational <- .relational_record(design, stimuli)
  conditions <- unique(as.character(stimuli$condition))
  covariates <- if (is_continuous) list(kept = character(0), left_out = character(0))
                else .covariates(design, source, stimuli)
  # The response windows the generated experiments open, and with them where a reaction
  # time starts, which the analysis has to know.
  events <- resolve_events(design)
  windows <- .response_windows(events, design[["timing"]] %||% list(), .refresh_hz(schema))
  incomplete <- selection_audit[["incomplete_dropped"]] %||% list()
  dropped <- stats::setNames(
    vapply(incomplete, function(d) as.integer(d[["n"]]), integer(1)),
    vapply(incomplete, function(d) as.character(d[["condition"]]), character(1)))

  realised <- list()
  if (!is.null(report)) {
    cmp <- report$comparisons
    # A report the pipeline wrote carries each row's role. One from a direct call of
    # match_report() may not, and its roles are then taken from the design.
    role_of <- .comparison_roles(design, controlled)
    for (i in seq_len(nrow(cmp))) {
      if (is_continuous) {
        realised[[length(realised) + 1L]] <- list(
          dimension = cmp$dimension[i], role = cmp$role[i],
          pearson_r = .r4(cmp$pearson_r[i]),
          predictor_span = .r4(cmp$predictor_span[i]),
          sd = .r4(cmp[["sd"]][i]), sd_ratio = .r4(cmp[["sd_ratio"]][i]),
          window_low = .r4(cmp[["window_low"]][i]),
          window_high = .r4(cmp[["window_high"]][i])
        )
      } else {
        role <- cmp[["role"]][i]
        if (is.null(role) || is.na(role)) {
          role <- role_of(cmp$condition[i], cmp$reference[i], cmp$dimension[i])
        }
        realised[[length(realised) + 1L]] <- list(
          condition = cmp$condition[i], reference = cmp$reference[i],
          dimension = cmp$dimension[i], role = as.character(role),
          cohens_d = .r4(cmp$cohens_d[i]),
          ci_low = .r4(cmp$d_ci_low[i]), ci_high = .r4(cmp$d_ci_high[i]),
          var_ratio = .r4(cmp$var_ratio[i]),
          tost_p = .r4(cmp$tost_p[i]),
          equivalent = if (is.na(cmp$equivalent[i])) NULL else isTRUE(cmp$equivalent[i]),
          mean_diff = .r4(cmp[["mean_diff"]][i])
        )
      }
    }
  }

  selection <- if (is_continuous) {
    # The controls are banded by the same tolerance windows the matcher uses, so
    # the record states them here too; without them the banding is unreproducible.
    list(method = "continuous even-spread (predictor spanned, controls banded)",
         predictor = design[["continuous"]][["predictor"]],
         controls = as.list(unlist(design[["continuous"]][["controls"]], use.names = FALSE)),
         tolerance_k = .resolve_tolerance_k(design, schema))
  } else if (source %in% c("corpus", "pool")) {
    method <- design[["matching"]][["method"]] %||% schema[["matching"]][["method"]] %||%
      "standardised_euclidean"
    sel <- list(method = method, match_on = as.list(controlled))
    if (method %in% c("joint", "optimal")) {
      # The pairwise methods rank whole pairs and never consult the tolerance
      # windows; recording tolerance_k here would claim a filter that was not
      # applied. They get the cap they do apply instead, with a per-condition
      # verdict on whether it fired. The candidates excluded for a missing matched
      # value never reach the cap, so the verdict counts the rest.
      entries <- Filter(function(x) !is.null(x$condition) && !is.null(x$n_candidates) &&
                          !is.na(x$n_candidates), candidate_pool %||% list())
      n_lost <- function(cond) {
        if (cond %in% names(dropped)) dropped[[cond]] else 0L
      }
      sel$candidate_cap <- list(
        cap = as.integer(.PAIRWISE_CAP),
        applied = stats::setNames(
          lapply(entries, function(x)
            isTRUE(x$n_candidates - n_lost(as.character(x$condition)) > .PAIRWISE_CAP)),
          vapply(entries, function(x) as.character(x$condition), character(1))))
    } else {
      sel$tolerance_k <- .resolve_tolerance_k(design, schema)
    }
    # Exact ties decide most picks when the matched dimensions are whole numbers, so
    # the rule that broke them is part of the selection. The salt goes with the hash,
    # which makes every tie key recomputable from the record.
    rule <- .resolve_tie_break(design, schema)
    sel$tie_break <- if (identical(rule, "hash")) list(rule = rule, salt = .TIE_SALT)
                     else list(rule = rule)
    sel
  } else if (identical(source, "generate")) {
    gen_method <- design[["items"]][["generation"]][["method"]] %||% "letter_substitution"
    list(method = .GENERATION_LABELS[[gen_method]] %||%
           paste0(gen_method, " (deterministic pseudowords)"),
         generation_method = gen_method,
         matched_on = list("length"))
  } else {
    list(method = "item table (user-supplied)")
  }
  if (!is.null(candidate_pool) && source %in% c("corpus", "pool", "generate"))
    selection$candidate_pool <- candidate_pool
  # A pair-keyed continuous design does select, over the item table.
  selection$cross_engine <- .cross_engine(selection$method, source,
                                          selected = is_continuous && !is.null(relational))
  # A relaxed window changes what "matched" means for that condition, so the
  # matcher's audit trail belongs in the record, not only in the run narration.
  # Integers only, so both engines serialise the counts identically.
  relaxations <- selection_audit$window_relaxations %||% list()
  if (length(relaxations)) {
    selection$window_relaxations <- lapply(relaxations, function(r)
      list(condition = r$condition,
           n_within_tolerance = as.integer(r$n_within_tolerance),
           n_needed = as.integer(r$n_needed)))
  }
  # The candidates excluded for missing a matched dimension, which candidate_pool
  # still counts: the selection drew on a smaller pool than the windows hold.
  if (length(incomplete)) {
    selection$incomplete_dropped <- lapply(incomplete, function(d)
      list(condition = d[["condition"]], n = as.integer(d[["n"]])))
  }
  if (!is.null(neighbourhood_reference))
    selection$neighbourhood_reference <- neighbourhood_reference
  if (length(generation_exclude) && identical(source, "generate")) {
    selection$generation_exclude <- lapply(generation_exclude, function(r)
      list(source = r$source, sha256 = r$sha256, n_forms = as.integer(r$n_forms)))
  }

  # The materials source's path, the stimuli file, every artefact below and the schema
  # path are written with forward slashes, whatever separator the caller used, as
  # datasheet.py's _posix writes them. So are the exclusion lists' paths, which are
  # converted where they are read. A Windows path would otherwise make the record
  # describe the machine that built it and disagree with the Python engine's record of
  # the same file. The other paths taken from the design
  # (materials_source$dimensions_from, relational$member_lexicon and the norm and block
  # tables' paths) are recorded as the design spells them, in both engines.
  materials_source <- list(
    type = source, path = .posix_path(source_path), sha256 = sha256_file(source_path),
    provenance = if (source %in% c("corpus", "generate"))
      .lexicon_provenance(source_path)
    else if (identical(source, "pool"))
      "user-supplied word pool, matched by lexsync"
    else "user-supplied item table")
  # A supplied pool usually draws its dimensions from a corpus lexicon, and that
  # lexicon is where every matched value came from, so it is named and checksummed
  # here: `path` above records only the word list itself.
  if (identical(source, "pool")) {
    dim_lex <- design[["items"]][["lexicon"]] %||% design[["lexicon"]]
    materials_source$dimensions_from <- if (is.null(dim_lex))
      "the supplied pool's own columns (no lexicon given)" else dim_lex
    if (!is.null(dim_lex)) materials_source$dimensions_sha256 <- sha256_file(dim_lex)
  }
  # Assigned here, because assigning NULL to a list element removes it, so a design
  # with no `norms:` block gets no key at all rather than a "norms": null that every
  # datasheet would then carry.
  if (length(norms)) materials_source$norms <- norms
  # The words the design took out of the candidates, after the norms and before the pool
  # filters. Integers as integers, so both engines write the same JSON.
  if (!is.null(exclusions) && source %in% c("corpus", "pool", "generate")) {
    materials_source$exclusions <- list(
      path = exclusions$path, sha256 = exclusions$sha256,
      n_listed = as.integer(exclusions$n_listed),
      n_removed = as.integer(exclusions$n_removed))
  }
  if (!is.null(input_normalisation)) {
    materials_source$input_normalisation <- list(
      changed = as.integer(input_normalisation$changed),
      collapsed = as.integer(input_normalisation$collapsed))
  }
  if (!is.null(zipf_derivation)) {
    materials_source$zipf_derivation <- list(
      n_values = as.integer(zipf_derivation$n_values),
      near_boundary = as.integer(zipf_derivation$near_boundary))
  }

  # A corpus or pool design draws on every schema dimension, and so does a pair-keyed
  # design: every lexicon dimension is joined onto each member. A generate or plain table
  # design reports only the ones it controlled, so the record does not claim
  # dimensions that played no part in the selection. Mirrors datasheet.py. The `[`
  # form keeps the names attribute, so an empty result is a named list() and
  # serialises as {} rather than [], matching Python.
  keep_dims <- if (source %in% c("corpus", "pool") || !is.null(relational))
    rep(TRUE, length(schema[["dimensions"]]))
  else names(schema[["dimensions"]]) %in% controlled

  # The recipe comes from the resolver counterbalance() dispatches on, and the lists
  # from the table, since a Latin square without counterbalance.lists deals one list per
  # condition. as.list() keeps a single issue a JSON array.
  recipe <- .cb_recipe(design)
  check <- counterbalance_check %||% .counterbalance_check(stimuli, design, recipe)
  versions <- .version_count(stimuli, as.integer(check$lists))
  counterbalancing <- list(
    recipe = recipe,
    lists = as.integer(check$lists),
    complete = isTRUE(check$complete),
    issues = as.list(check$issues),
    cells = check$cells,
    versions = versions,
    assignment = sprintf(paste("version = ((participant - 1) mod %d) + 1 unless a version",
                               "is given at launch"), versions))
  # The balance report is added only when the optimiser ran, for the same reason the
  # norms record is: a key that is null on every design that does not use the feature
  # is noise in a research artefact.
  if (!is.null(balance)) counterbalancing$optimise <- balance
  # Practice and filler trials change what a participant sees but not what is
  # analysed, so the record has to state both counts: a reader comparing the stimuli
  # file against the experiment would otherwise find them a different length with no
  # explanation.
  if (!is.null(blocks)) counterbalancing$blocks <- blocks
  # The run limit and the trial orders, recorded only when the design sets them.
  trial_order <- trial_order %||% .trial_order_record(stimuli, design)
  if (!is.null(trial_order$max_run)) counterbalancing$max_run <- trial_order$max_run
  if (!is.null(trial_order$orders)) {
    m <- as.integer(trial_order$orders)
    counterbalancing$orders <- list(
      m = m, rule = sprintf(paste("order = (((participant - 1) div %d) mod %d) + 1; a run",
                                  "without a participant number presents order 1"),
                            as.integer(versions), m))
  }

  # The equivalence settings the report's TOST verdicts were computed against,
  # recorded so the Methods prose can state the bound it actually ran with.
  equivalence <- list(bound_d = schema[["equivalence"]][["bound_d"]] %||% 0.5,
                      alpha = schema[["equivalence"]][["alpha"]] %||% 0.05)

  # The key the participants pressed for each condition, recorded only when a response
  # mapping applies: the design's own, or a lexical decision's default. Assigning NULL
  # leaves the field out, as the Python engine does.
  presentation <- list(response_windows = windows)
  presentation$response_mapping <- .response_mapping_record(design)

  reproducibility <- list(seed = seed, versions = .versions_R(engine))
  # The design and schema decide everything the seed does not, so their checksums
  # complete the reproducibility record when the pipeline names them.
  if (!is.null(design_path)) reproducibility$design_sha256 <- sha256_file(design_path)
  # The path as well as the checksum: when no schema was named, the run chose one of
  # several files, and the record has to say which.
  if (!is.null(schema_path)) {
    reproducibility$schema_path <- .posix_path(schema_path)
    reproducibility$schema_sha256 <- sha256_file(schema_path)
  }

  list(
    lexsync_datasheet_version = DATASHEET_VERSION,
    design = list(name = design[["name"]], language = design[["language"]],
                  paradigm = design[["paradigm"]] %||% "factorial", source = source,
                  description = design[["description"]],
                  n_per_condition = .requested_n(design, source, is_continuous)),
    materials_source = materials_source,
    dimensions = schema[["dimensions"]][keep_dims],
    selection = selection,
    relational = relational,
    analysis = .analysis_R(design, source, .response_text(windows, events), recipe = recipe,
                           n_conditions = length(conditions),
                           covariates = covariates[["kept"]],
                           left_out = covariates[["left_out"]]),
    equivalence = equivalence,
    realised_control = realised,
    counterbalancing = counterbalancing,
    presentation = presentation,
    resampling = if (!is.null(design[["resample"]]))
      list(n_sets = design[["resample"]][["n_sets"]], disjoint = TRUE) else NULL,
    items = list(n_total = nrow(stimuli), n_conditions = length(conditions),
                 conditions = as.list(conditions),
                 n_per_condition_realised = .realised_counts(stimuli, conditions),
                 stimuli_file = .posix_path(artifacts$stimuli),
                 stimuli_sha256 = sha256_file(artifacts$stimuli)),
    reproducibility = reproducibility,
    artifacts = lapply(Filter(Negate(is.null), .artifact_paths(artifacts)),
                       function(p) list(file = .posix_path(p), sha256 = sha256_file(p)))
  )
}

# The files the record checksums: the three tables, then every experiment file.
# export_experiments() lists every file it wrote under `files`, the loop and text tables
# that hold the trial order and the trigger codes among them. A result without `files`
# contributes its three experiment paths. Mirrors _artifact_paths in datasheet.py.
.artifact_paths <- function(artifacts) {
  exps <- artifacts[["experiments"]]
  files <- if (!is.null(exps[["files"]])) exps[["files"]] else unlist(exps, use.names = FALSE)
  c(artifacts[["stimuli"]], artifacts[["descriptives"]], artifacts[["comparisons"]], files)
}

# The presentation versions the trials give, one per (replicate, list) pair. A table
# without a `list` column has the lists counterbalance() would deal in each replicate,
# `lists` of them, as the record's `lists` does. Mirrors _version_count in datasheet.py.
.version_count <- function(stimuli, lists) {
  if ("list" %in% names(stimuli)) return(length(.presentation_versions(stimuli)))
  replicates <- if ("replicate" %in% names(stimuli))
    length(unique(stats::na.omit(stimuli$replicate))) else 1L
  as.integer(max(replicates, 1L) * lists)
}

# How participants met the presentation versions, for the Methods text. Empty for a
# single version, and for a record written before the field existed. Mirrors
# _versions_note in datasheet.py.
.versions_note <- function(ds) {
  n <- ds[["counterbalancing"]][["versions"]]
  if (is.null(n) || n < 2) return("")
  unit <- if (!is.null(ds[["resampling"]])) "presentation versions (one list of one item set)"
          else "lists"
  sprintf(paste(" Each participant was presented one of the %d %s, assigned in rotation",
                "by participant number."), as.integer(n), unit)
}

# The trial orders and the run limit, for the Methods text. Empty for a design with one
# order and no limit, and for a record written before the fields existed. Mirrors
# _trial_order_note in datasheet.py.
.trial_order_note <- function(ds) {
  cb <- ds[["counterbalancing"]]
  out <- ""
  orders <- cb[["orders"]]
  if (!is.null(orders)) {
    out <- paste0(out, sprintf(paste(" Each list was presented in %d trial orders, assigned",
                                     "in rotation by participant number."),
                               as.integer(orders[["m"]])))
  }
  limit <- cb[["max_run"]]
  if (!is.null(limit)) {
    what <- if (identical(limit[["run_on"]], "condition")) "condition" else
      paste("value of", limit[["run_on"]])
    out <- paste0(out, sprintf(paste(" Runs of consecutive trials with the same %s were",
                                     "limited to %d (van Casteren & Davis, 2006)."),
                               what, as.integer(limit[["k"]])))
  }
  out
}

# The norm tables named in the Methods prose. Basenames only: the full paths and
# checksums are in the datasheet, and a paper's Methods section wants the source, not
# the directory it happened to sit in on one machine. Mirrors datasheet.py.
.norms_note <- function(ds) {
  norms <- ds$materials_source$norms
  if (is.null(norms) || !length(norms)) return("")
  files <- paste(vapply(norms, function(x) basename(x$path), character(1)), collapse = ", ")
  sprintf(paste0(" Norm dimensions were joined from %s, whose checksums and per-column ",
                 "coverage are recorded in the datasheet."), files)
}

# The known-form lists a generated design checked its pseudowords against, for the
# Methods prose, by basename like the norm tables. Empty when it named none. Mirrors
# _known_forms_note in datasheet.py.
.known_forms_note <- function(ds) {
  recs <- ds$selection$generation_exclude
  if (is.null(recs) || !length(recs)) return("")
  parts <- vapply(recs, function(r) {
    n <- as.integer(r$n_forms)
    sprintf("%d known word form%s (%s)", n, if (n == 1L) "" else "s",
            basename(gsub("\\", "/", r$source, fixed = TRUE)))
  }, character(1))
  listed <- if (length(parts) == 1L) parts
            else paste0(paste(parts[-length(parts)], collapse = ", "), " and ",
                        parts[length(parts)])
  paste0(". Besides the lexicon, pseudowords were checked against ", listed)
}

# The design's exclusion list, for the Methods prose: how many candidates it removed, and
# its file by name like the norm tables. A sentence without its final full stop, or empty
# without a list. Mirrors _exclusions_note in datasheet.py.
.exclusions_note <- function(ds) {
  ex <- ds$materials_source$exclusions
  if (is.null(ex)) return("")
  n <- as.integer(ex$n_removed)
  where <- if (identical(ex$path, "inline")) "in the design"
           else sprintf("(%s)", .file_name(ex$path))
  sprintf("An exclusion list %s removed %d word%s from the candidates before selection",
          where, n, if (n == 1L) "" else "s")
}

# The Markdown datasheet's line for the exclusion list, or NULL without one. Mirrors the
# 'Excluded words' line of render_datasheet_md in datasheet.py.
.excluded_words_line <- function(ex) {
  if (is.null(ex)) return(NULL)
  n_listed <- as.integer(ex$n_listed)
  sprintf("- **Excluded words:** %s (%d word%s, %d removed, sha256 `%s...`)",
          if (identical(ex$path, "inline")) "the design's list" else sprintf("`%s`", ex$path),
          n_listed, if (n_listed == 1L) "" else "s", as.integer(ex$n_removed),
          substring(ex$sha256 %||% "", 1, 16))
}

# The counterbalancing recipe as the Methods text names it. A Latin square the check
# found incomplete is called incomplete, since the bare label would claim a rotation
# the lists or the item sets did not complete. A record without the check, written
# before datasheet 1.2, keeps the bare label. Mirrors _recipe_label in datasheet.py.
.recipe_label <- function(cb) {
  if (identical(cb$recipe, "latin_square_target")) {
    return(if (isFALSE(cb$complete)) "an incomplete Latin-square rotation"
           else "a Latin-square rotation")
  }
  switch(cb$recipe, factorial = "a factorial split", cb$recipe)
}

# The confidence level of the interval beside a TOST at `alpha`, 1 - 2 * alpha, as a
# percentage: "90" at .05 and "99" at .005. Mirrors _ci_pct in datasheet.py.
.ci_pct <- function(alpha) .fmt_g((1 - 2 * as.numeric(alpha)) * 100)

# The fewest items per condition with which two one-sided tests at `bound_d` and `alpha`
# can support equivalence, Inf when no request the engines accept would do, or NULL for
# a bound or an alpha that admits none. Two conditions of n items with equal means give
# the test its best case, a t of bound_d / sqrt(2 / n) on 2n - 2 degrees of freedom,
# which passes when it exceeds t(1 - alpha, 2n - 2). The fewest items with which a
# dimension that varies can pass is therefore the smallest n with
# t(1 - alpha, 2n - 2) * sqrt(2 / n) < bound_d: 23 at a bound of 0.5 and an alpha of .05.
# The left side falls as n grows, so the search doubles n until the test can pass and
# then bisects, `lo` never passing and `hi` always passing. It stops at the largest
# n_per_condition the engines accept, where R's integers end. Without that stop, a
# bound below about 5e-5 SD would give as.integer() an NA, which would stop the Methods
# text, and a smaller one a bisection that never ends, because doubles that large cannot
# hold the midpoint. Mirrors _tost_min_n in datasheet.py.
.tost_min_n <- function(bound_d, alpha) {
  b <- suppressWarnings(as.numeric(bound_d))
  a <- suppressWarnings(as.numeric(alpha))
  if (length(b) != 1L || length(a) != 1L || is.na(b) || is.na(a) || !(b > 0) ||
      !(a > 0 && a < 0.5)) return(NULL)
  passes <- function(n) stats::qt(1 - a, 2 * n - 2) * sqrt(2 / n) < b
  cap <- .Machine$integer.max
  # One item leaves the test no degrees of freedom, so 1 is the first n that fails.
  lo <- 1
  hi <- 2
  while (!passes(hi)) {
    if (hi >= cap) return(Inf)
    lo <- hi
    hi <- min(2 * hi, cap)
  }
  while (hi - lo > 1) {
    mid <- (lo + hi) %/% 2
    if (passes(mid)) hi <- mid else lo <- mid
  }
  as.integer(hi)
}

# A count as the Methods text prints it, or "NA" when there is none.
.int_text <- function(v) {
  if (is.null(v) || length(v) != 1L || is.na(v)) "NA" else sprintf("%d", as.integer(v))
}

# The fewest and the most items a condition holds, from items$n_per_condition_realised,
# or the request twice for a record written before that field existed. Mirrors
# _realised_range in datasheet.py.
.realised_range <- function(ds) {
  recs <- ds[["items"]][["n_per_condition_realised"]]
  if (length(recs)) {
    ns <- vapply(recs, function(r) as.numeric(r[["n"]]), numeric(1))
    return(list(lo = min(ns), hi = max(ns)))
  }
  n <- ds[["design"]][["n_per_condition"]]
  list(lo = n, hi = n)
}

# The items each condition holds over every replicate, the samples its equivalence tests
# compared, or the request for a record without the realised counts. Mirrors
# _pooled_counts in datasheet.py.
.pooled_counts <- function(ds) {
  recs <- ds[["items"]][["n_per_condition_realised"]]
  if (length(recs)) {
    conds <- vapply(recs, function(r) as.character(r[["condition"]]), character(1))
    ns <- vapply(recs, function(r) as.numeric(r[["n"]]), numeric(1))
    return(vapply(unique(conds), function(cn) sum(ns[conds == cn]), numeric(1),
                  USE.NAMES = FALSE))
  }
  n <- ds[["design"]][["n_per_condition"]]
  if (is.numeric(n) && length(n) == 1L && !is.na(n)) as.numeric(n) else numeric(0)
}

# A count, or a range when the conditions differ, with its noun: "1 item", "15 items",
# "18 to 20 items". Mirrors _count_text in datasheet.py.
.count_text <- function(lo, hi, noun) {
  paste0(if (isTRUE(lo != hi)) paste(.int_text(lo), "to", .int_text(hi)) else .int_text(lo),
         " ", noun, if (isTRUE(hi == 1)) "" else "s")
}

# The request, as " (of 20 requested)", when the conditions hold fewer items than the
# design asked for, which only shortfall: allow lets a run do. Empty otherwise. Mirrors
# _requested_note in datasheet.py.
.requested_note <- function(ds, lo) {
  req <- ds[["design"]][["n_per_condition"]]
  if (!length(ds[["items"]][["n_per_condition_realised"]]) || is.null(lo) ||
      length(lo) != 1L || is.na(lo) || !is.numeric(req) || length(req) != 1L ||
      is.na(req) || lo >= req) return("")
  sprintf(" (of %d requested)", as.integer(req))
}

# A dimension's unit as the Methods text gives it: the schema's unit, which the record's
# dimensions carry, less a closing parenthesis such as "(orthographic estimate)". Empty
# for a dimension the record gives no unit, such as a joined norm. Mirrors _unit in
# datasheet.py.
.unit <- function(ds, dim) {
  unit <- ds[["dimensions"]][[dim]][["unit"]]
  if (!is.character(unit) || length(unit) != 1L || is.na(unit)) return("")
  sub(" *\\([^()]*\\)$", "", unit)
}

.defined <- function(row) {
  d <- row[["cohens_d"]]
  !is.null(d) && length(d) == 1L && !is.na(d)
}

# A row's raw difference in its unit, or empty when the row has none. The comparisons
# store the difference to three places, so a bigram probability, whose differences lie
# in the fourth, can be stored as 0 beside a d that is not. That zero is a rounding
# residue and is given as "under 0.001". Mirrors _raw_text in datasheet.py.
.raw_text <- function(ds, row) {
  v <- row[["mean_diff"]]
  if (is.null(v) || length(v) != 1L || is.na(v)) return("")
  text <- .fmt_dp(v, 3)
  if (identical(text, "0.000") && .defined(row) && row[["cohens_d"]] != 0) {
    text <- "under 0.001"
  }
  unit <- .unit(ds, row[["dimension"]])
  if (nzchar(unit)) paste(text, unit) else text
}

# The pair a row compares, the reference first, since d and the raw difference are the
# reference mean minus the condition mean. Empty for a record without the pair. Mirrors
# _pair_text in datasheet.py.
.pair_text <- function(row) {
  ref <- row[["reference"]]
  cond <- row[["condition"]]
  if (is.null(ref) || is.null(cond)) "" else paste(ref, "against", cond)
}

.d_text <- function(row, pct) {
  sprintf("d = %s, %s%% CI [%s, %s]", .fmt_dp(row[["cohens_d"]], 2), pct,
          .fmt_dp(row[["ci_low"]], 2), .fmt_dp(row[["ci_high"]], 2))
}

# The names a lexical decision's Methods sentence gives the dimensions its report sets
# words against pseudowords on. Kept identical to _LEXDEC_NAMES in datasheet.py.
.LEXDEC_NAMES <- c(bigram_freq = "bigram frequency", n_density = "N", old20 = "OLD20")

# What the Methods text says about the realised control of a matched or generated
# design, as sentences each beginning with ". ". The description comes first. A matched
# design gives the largest difference on a matched dimension, in that dimension's unit,
# with its pair, d and interval. Raw differences in different units cannot be ranked
# against each other, so the largest is the one with the largest |d|. A generated
# lexical decision says that its words and pseudowords were matched on length only, and
# how they differ on the dimensions the generator does not hold. Comparisons whose d is
# undefined are counted. The two one-sided tests follow as a secondary check, with the
# number they passed, and say so when every condition holds fewer items than any test at
# the bound can pass with. A matched design then names, largest first, up to five
# comparisons of a dimension it did not control whose |d| exceeds the bound, or says that
# none does. Tests on a selected set describe a closed population, so the stimuli are
# described first (Sassenhagen & Alday, 2016). Mirrors _control_note in datasheet.py.
.control_note <- function(ds) {
  rows <- ds[["realised_control"]] %||% list()
  bound <- ds[["equivalence"]][["bound_d"]] %||% 0.5
  alpha <- ds[["equivalence"]][["alpha"]] %||% 0.05
  pct <- .ci_pct(alpha)
  ctrl <- Filter(function(r) identical(r[["role"]], "controlled"), rows)
  unc <- Filter(function(r) identical(r[["role"]], "uncontrolled"), rows)
  generated <- identical(ds[["materials_source"]][["type"]], "generate")
  out <- ""
  if (generated) {
    parts <- vapply(unc, function(r) {
      dim <- r[["dimension"]]
      name <- if (dim %in% names(.LEXDEC_NAMES)) .LEXDEC_NAMES[[dim]] else dim
      sprintf("%s (%s)", name, if (.defined(r)) .d_text(r, pct) else "d undefined")
    }, character(1))
    out <- paste0(out, ". Words and pseudowords were matched on length only")
    if (length(parts)) {
      out <- paste0(out, ", and the words differed from the pseudowords in ", .and_join(parts))
    }
  } else {
    known <- Filter(.defined, ctrl)
    if (length(known)) {
      # which.max() keeps the first of equal |d|, as Python's max() does.
      worst <- known[[which.max(vapply(known, function(r) abs(r[["cohens_d"]]), numeric(1)))]]
      raw <- .raw_text(ds, worst)
      inner <- paste(Filter(nzchar, c(.pair_text(worst), .d_text(worst, pct))), collapse = "; ")
      out <- paste0(out, sprintf(". The largest difference on a matched dimension was %s%s (%s)",
                                 if (nzchar(raw)) paste0(raw, " in ") else "in ",
                                 worst[["dimension"]], inner))
    }
  }
  undefined <- Filter(Negate(.defined), ctrl)
  if (length(undefined)) {
    share <- if (length(undefined) == length(ctrl)) "every matched comparison"
             else sprintf("%d of the %d matched comparisons", length(undefined), length(ctrl))
    out <- paste0(out, sprintf(paste0(". Cohen's d is undefined for %s, and the realised-control ",
                                      "table gives their raw differences"), share))
  }
  if (length(ctrl)) {
    passed <- sum(vapply(ctrl, function(r) isTRUE(r[["equivalent"]]), logical(1)))
    out <- paste0(out, sprintf(paste0(". Two one-sided tests at a bound of %s SD (alpha %s) ",
                                      "supported equivalence on %d of %d matched comparisons"),
                               .fmt_g(bound), .fmt_g(alpha), passed, length(ctrl)))
    counts <- .pooled_counts(ds)
    n_min <- .tost_min_n(bound, alpha)
    if (length(counts) && !is.null(n_min) && max(counts) < n_min) {
      out <- paste0(out, sprintf(paste0("; with %s per condition no dimension that varies can ",
                                        "pass this test, however well matched"),
                                 .count_text(min(counts), max(counts), "item")))
    }
  }
  if (!generated && length(unc)) {
    big <- Filter(function(r) .defined(r) && abs(r[["cohens_d"]]) > bound, unc)
    if (length(big)) {
      # order() is stable, so comparisons of equal |d| keep the record's order.
      big <- big[order(-vapply(big, function(r) abs(r[["cohens_d"]]), numeric(1)))]
      parts <- vapply(utils::head(big, 5L), function(r) {
        head_text <- paste(Filter(nzchar, c(.pair_text(r), .raw_text(ds, r))), collapse = ": ")
        inner <- paste(Filter(nzchar, c(head_text, .d_text(r, pct))), collapse = "; ")
        sprintf("%s (%s)", r[["dimension"]], inner)
      }, character(1))
      out <- paste0(out, ". Dimensions the design did not control differed: ", .and_join(parts))
      if (length(big) > 5L) {
        out <- paste0(out, sprintf(", and %d more in the realised-control table",
                                   length(big) - 5L))
      }
    } else if (all(vapply(unc, .defined, logical(1)))) {
      out <- paste0(out, sprintf(". No uncontrolled dimension differed by more than %s SD",
                                 .fmt_g(bound)))
    }
  }
  out
}

# The predictor's realised span and SD, the SD set against an even spread over the span,
# in parentheses, or empty for a record without them. Mirrors _spread_note in
# datasheet.py.
.spread_note <- function(rows) {
  span <- NULL
  pred <- NULL
  for (r in rows) {
    if (is.null(span) && !is.null(r[["predictor_span"]])) span <- r[["predictor_span"]]
    if (is.null(pred) && identical(r[["role"]], "predictor")) pred <- r
  }
  parts <- character(0)
  if (!is.null(span)) parts <- c(parts, paste0("a span of ", .fmt_dp(span, 2)))
  if (!is.null(pred[["sd"]])) {
    sd <- paste0("an SD of ", .fmt_dp(pred[["sd"]], 2))
    if (!is.null(pred[["sd_ratio"]])) {
      sd <- paste0(sd, ", ", .fmt_dp(pred[["sd_ratio"]], 2),
                   " times that of an even spread over the span")
    }
    parts <- c(parts, sd)
  }
  if (length(parts)) sprintf(" (%s)", paste(parts, collapse = " and ")) else ""
}

# A continuous design's control windows, the rule that set them and the realised SDs, as
# a sentence, or how the windows were widened when they held too few items. The windows
# are the mean +/- k SD of the controls in a first selection spread over the predictor's
# ranks, k from the resolved tolerance_k with the matcher's default of 2, and each
# realised SD is set against the pool's. That first selection follows the pool's
# distribution of the predictor, so it is not called an even spread, the phrase the text
# keeps for values spaced evenly over the span. Nor are the controls called
# near-constant, since the windows only trim their tails and a relaxation drops them.
# Mirrors _bands_note in datasheet.py.
.bands_note <- function(ds, rows) {
  sel <- ds[["selection"]]
  controls <- unlist(sel[["controls"]], use.names = FALSE)
  if (!length(controls)) return("")
  tol <- sel[["tolerance_k"]]
  ks <- vapply(controls, function(cc) as.numeric(tol[[cc]] %||% 2), numeric(1),
               USE.NAMES = FALSE)
  same_k <- all(ks == ks[1L])
  by <- list()
  for (r in rows) if (identical(r[["role"]], "control")) by[[r[["dimension"]]]] <- r
  windows <- character(0)
  for (i in seq_along(controls)) {
    r <- by[[controls[i]]]
    if (is.null(r[["window_low"]]) || is.null(r[["window_high"]])) next
    windows <- c(windows, sprintf("%s %s to %s%s", controls[i], .fmt_dp(r[["window_low"]], 2),
                                  .fmt_dp(r[["window_high"]], 2),
                                  if (same_k) "" else paste0(" at k = ", .fmt_g(ks[i]))))
  }
  ratios <- lapply(controls, function(cc) by[[cc]][["sd_ratio"]])
  many <- length(controls) > 1L
  rule <- sprintf("the mean \u00b1 %s SD of an initial selection spread over the ranks of %s",
                  if (same_k) .fmt_g(ks[1L]) else "k", sel[["predictor"]])
  win <- if (length(windows)) sprintf(" (%s)", .and_join(windows)) else ""
  sds <- ""
  if (all(vapply(ratios, Negate(is.null), logical(1)))) {
    sds <- sprintf(", and %s %s of the pool's",
                   if (many) "their realised SDs were" else "its realised SD was",
                   .and_join(vapply(ratios, function(x) .fmt_dp(x, 2), character(1))))
  }
  if (length(sel[["window_relaxations"]])) {
    return(sprintf(" The control %s, %s%s, held too few items and %s widened to the whole pool%s.",
                   if (many) "windows" else "window", rule, win, if (many) "were" else "was",
                   sds))
  }
  sprintf(" The %s banded within %s of %s%s%s.", if (many) "controls were" else "control was",
          if (many) "windows" else "a window", rule, win, sds)
}

#' A ready-to-adapt methods paragraph rendered from a datasheet
#'
#' Every number in the paragraph is printed by lexsync's own formatter, rounded
#' half away from zero from the value the datasheet stores, so the R and Python
#' engines write the same text from the same record, a record read back from its
#' JSON included.
#'
#' The paragraph states the items each condition holds, and the request beside them
#' when they fell short of it. It describes the realised control before testing it:
#' the largest difference on a matched dimension in that dimension's unit, with
#' Cohen's d and its interval, then the two one-sided tests, which it says cannot pass
#' when every condition holds fewer items than the bound needs, then, largest first,
#' up to five comparisons of an uncontrolled dimension whose |d| exceeds the bound.
#' Every interval is labelled by the schema's alpha. A continuous design's paragraph
#' gives the predictor's spread, the control windows and the controls' realised
#' spread. When a response mapping applies, the paragraph says which key the
#' participants pressed for which condition.
#'
#' @param ds A datasheet list, from [build_datasheet()].
#' @return A single character string describing the materials procedure.
#' @export
methods_paragraph <- function(ds) {
  d <- ds[["design"]]
  src <- ds[["materials_source"]][["type"]]
  lang <- paste0(toupper(substring(d[["language"]], 1, 1)), substring(d[["language"]], 2))
  sel <- ds[["selection"]]
  range <- .realised_range(ds)
  lo <- range[["lo"]]
  hi <- range[["hi"]]
  n <- if (isTRUE(lo != hi)) paste(.int_text(lo), "to", .int_text(hi)) else .int_text(lo)
  one <- isTRUE(hi == 1)
  were <- if (one) "was" else "were"
  req <- .requested_note(ds, lo)
  # What was selected. A pair design's unit is the pair, and its `n_per_condition`
  # counts pairs, so calling them "items" would misreport the size of the materials
  # by a factor of the number of conditions.
  rel <- ds[["relational"]]
  unit <- paste0(if (is.null(rel)) "item"
                 else paste0(paste(unlist(rel[["members"]]), collapse = "-"), " pair"),
                 if (one) "" else "s")
  if (!is.null(sel[["predictor"]])) {
    predictor <- sel[["predictor"]]
    rc <- ds[["realised_control"]] %||% list()
    rs <- numeric(0)
    for (r in rc) {
      if (!is.null(r[["pearson_r"]]) && !is.na(r[["pearson_r"]])) rs <- c(rs, abs(r[["pearson_r"]]))
    }
    # |r| is printed at three places, the precision of the comparisons report it
    # comes from (the record keeps up to four, see .r4), so the record holds the
    # digit shown. .fmt_dp prints it, as every number here, because sprintf() would
    # round a tie such as 0.0825 to 0.082 on Windows where Python gives 0.083.
    corr_str <- if (length(rs))
      paste0(" The largest predictor-control correlation was |r| = ", .fmt_dp(max(rs), 3),
             ".") else ""
    cb <- ds[["counterbalancing"]]
    recipe_label <- .recipe_label(cb)
    excluded <- .exclusions_note(ds)
    if (nzchar(excluded)) excluded <- paste0(" ", excluded, ".")
    return(paste0(n, " ", lang, " ", unit, req, " ", were, " selected to span ", predictor,
                  .spread_note(rc), ", for analysis by regression or a mixed model rather ",
                  "than a between-condition contrast (Kuperman, 2015; Liben-Nowell et al., ",
                  "2019).", .bands_note(ds, rc), corr_str, .norms_note(ds), excluded,
                  " Materials were counterbalanced into ", cb[["lists"]], " list(s) (",
                  recipe_label, ") and generated for PsychoPy, OpenSesame and jsPsych.",
                  .versions_note(ds), .trial_order_note(ds), .response_note(ds),
                  .mapping_note(ds), " The selection is deterministic ",
                  "and reproducible (lexsync ", ds[["reproducibility"]][["versions"]][["lexsync"]],
                  "), and the seed (", ds[["reproducibility"]][["seed"]],
                  ") fixes the trial order."))
  }
  items <- if (one) "item" else "items"
  if (identical(src, "corpus")) {
    ctrl <- paste(unlist(sel[["match_on"]]), collapse = ", ")
    lead <- paste0(n, " ", items, " per condition", req, " ", were, " selected from the ",
                   lang, " lexicon (", ds[["materials_source"]][["provenance"]],
                   ") and matched item by item on ", ctrl, " using lexsync's ",
                   sel[["method"]], " matcher")
  } else if (identical(src, "pool")) {
    # A supplied pool is matched exactly as a corpus is; what differs, and what the
    # Methods section has to say, is that the candidate words were chosen by the
    # researcher rather than drawn from the whole lexicon.
    ctrl <- paste(unlist(sel[["match_on"]]), collapse = ", ")
    lead <- paste0(n, " ", lang, " ", items, " per condition", req, " ", were,
                   " selected from a supplied candidate pool and matched item by item on ",
                   ctrl, " using lexsync's ", sel[["method"]], " matcher, with the matched ",
                   "dimensions taken from ", ds[["materials_source"]][["dimensions_from"]])
  } else if (identical(src, "generate")) {
    lead <- paste0(n, " real ", lang, " ", if (one) "word" else "words", req, " and ", n,
                   " length-matched ", if (one) "pseudoword" else "pseudowords",
                   " (generated by ", sel[["method"]], ") were assembled for a ",
                   "lexical-decision contrast", .known_forms_note(ds))
  } else {
    # An item table selects nothing, so it has the items it holds and no request. A
    # record written before the realised counts existed divides its rows.
    if (!length(ds[["items"]][["n_per_condition_realised"]])) {
      lo <- hi <- ds[["items"]][["n_total"]] %/% max(1L, ds[["items"]][["n_conditions"]])
    }
    lead <- sprintf("%s %s drawn from an item table for a %s design (%s)",
                    .count_text(lo, hi, "item"), if (isTRUE(hi == 1)) "was" else "were",
                    d[["paradigm"]], lang)
  }
  control <- .control_note(ds)
  resamp <- if (!is.null(ds$resampling))
    sprintf(". %s disjoint matched item sets were drawn, so items can be treated as a random factor",
            ds$resampling$n_sets) else ""
  cb <- ds$counterbalancing
  recipe_label <- .recipe_label(cb)
  tail <- sprintf(paste0(resamp, ". Materials were counterbalanced into %s list(s) (%s) and generated for ",
                         "PsychoPy, OpenSesame and jsPsych.%s%s%s%s The selection is deterministic and ",
                         "reproducible (lexsync %s), and the seed (%s) fixes the trial order."),
                  cb$lists, recipe_label, .versions_note(ds), .trial_order_note(ds),
                  .response_note(ds), .mapping_note(ds), ds$reproducibility$versions$lexsync,
                  ds$reproducibility$seed)
  bal <- ds$counterbalancing$optimise
  bal_note <- if (is.null(bal)) "" else sprintf(
    paste0(". Item sets were assigned to lists so as to equate the lists on %s rather ",
           "than by an arbitrary deal, by a deterministic integer search%s (%d swap(s); ",
           "imbalance reduced from %s to %s)"),
    paste(unlist(bal$dimensions), collapse = ", "),
    .BALANCE_SCALE_NOTES[[bal[["scale"]] %||% "mean"]] %||% "",
    bal$n_swaps, format(bal$cost_before, scientific = FALSE),
    format(bal$cost_after, scientific = FALSE))
  cp <- ds$selection$candidate_pool
  # The candidate pool counts the candidates excluded for a missing matched value,
  # which were never eligible, so they come off the count of the condition that lost
  # them. Mirrors methods_paragraph in datasheet.py.
  lost <- function(cond) {
    n <- 0
    for (d in ds[["selection"]][["incomplete_dropped"]] %||% list()) {
      if (identical(as.character(d[["condition"]]), as.character(cond))) {
        n <- n + as.numeric(d[["n"]])
      }
    }
    n
  }
  pool_note <- ""
  if (!is.null(cp) && length(cp)) {
    sizes <- vapply(cp, function(x) if (is.null(x$n_candidates)) NA_real_ else
      as.numeric(x$n_candidates) - lost(x$condition %||% NA_character_), numeric(1))
    sizes <- sizes[!is.na(sizes)]
    if (length(sizes))
      pool_note <- sprintf(paste0(". The smallest condition was selected from %d eligible ",
                                  "candidates, and the selection was deterministic and blind ",
                                  "to any outcome measure"), as.integer(min(sizes)))
  }
  cap_rec <- ds$selection$candidate_cap
  cap_note <- ""
  if (!is.null(cap_rec) && any(vapply(cap_rec$applied, isTRUE, logical(1))))
    cap_note <- sprintf(paste0(". Each candidate pool exceeding the pairwise cap was reduced to ",
                               "the %d candidates nearest the other condition's centroid ",
                               "before pairing"), as.integer(cap_rec$cap))
  ce <- ds$selection$cross_engine %||% ""
  ce_note <- if (startsWith(ce, "approximate"))
    paste0(". This design's matching method uses a covariance inverse or an assignment ",
           "solver, so the R and Python engines select equivalent but not byte-identical ",
           "materials") else ""
  # Placed before the pool size, which it shrank.
  excluded <- .exclusions_note(ds)
  if (nzchar(excluded)) excluded <- paste0(". ", excluded)
  paste0(lead, control, excluded, pool_note, cap_note, ce_note, bal_note, tail,
         .norms_note(ds))
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

# How the selection was made, as the Markdown's transparency section states it.
# Selection reads no seed, so the note names what it does depend on, and how exact ties
# were broken when the record gives the rule. It does not call the selection free of
# item-selection bias, since the spelling tie-break of tie_break: bytes skews tied
# conditions towards early-alphabet words. Mirrors _transparency_note in datasheet.py.
.transparency_note <- function(ds) {
  tb <- ds[["selection"]][["tie_break"]]
  rule <- tb[["rule"]] %||% ""
  ties <- if (identical(rule, "hash")) {
    sprintf(paste0(" Exact ties between equally close candidates are broken by a keyed ",
                   "hash of each word (salt %s), so no part of the alphabet is favoured."),
            tb[["salt"]])
  } else if (identical(rule, "bytes")) {
    paste0(" Exact ties between equally close candidates are broken by spelling, in ",
           "byte order, as lexsync 0.1 did, so every tie goes to the spelling that ",
           "sorts first.")
  } else ""
  paste0("Selection is a deterministic function of the materials source, the design ",
         "and the schema, blind to any outcome measure, and does not depend on the ",
         "seed, which fixes the trial order.", ties, " Automating the choice removes ",
         "the experimenter's discretion that Forster (2000) showed can bias item ",
         "selection.")
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
    # Where a supplied pool's matched values came from. Without this the record names
    # only the word list, and the numbers every control rests on have no stated origin.
    if (!is.null(ds$materials_source$dimensions_from))
      sprintf("- **Dimensions from:** `%s`%s", ds$materials_source$dimensions_from,
              if (is.null(ds$materials_source$dimensions_sha256)) ""
              else sprintf(" (sha256 `%s...`)",
                           substring(ds$materials_source$dimensions_sha256, 1, 16)))
    else NULL,
    # The design's exclusion list, which decided what the selection could draw on.
    .excluded_words_line(ds$materials_source$exclusions),
    if (!is.null(ds$materials_source$input_normalisation))
      sprintf("- **Input normalisation:** %d text form(s) rewritten to Unicode NFC, %d duplicate(s) removed",
              as.integer(ds$materials_source$input_normalisation$changed),
              as.integer(ds$materials_source$input_normalisation$collapsed))
    else NULL,
    if (!is.null(ds$materials_source$zipf_derivation))
      sprintf("- **Zipf from frequencies per million:** %d of %d value(s) within 1e-9 of a rounding boundary",
              as.integer(ds$materials_source$zipf_derivation$near_boundary),
              as.integer(ds$materials_source$zipf_derivation$n_values))
    else NULL,
    # The known-form lists a generated design's pseudowords were checked against: they
    # decide which pseudowords the run produced, as the lexicon does.
    vapply(ds$selection$generation_exclude %||% list(), function(r)
      sprintf("- **Known word forms:** `%s` (%d forms, sha256 `%s...`)", r$source,
              as.integer(r$n_forms), substring(r$sha256 %||% "", 1, 16)), character(1)),
    sprintf("- **Selection:** %s", ds$selection$method),
    sprintf("- **Cross-engine determinism:** %s", ds$selection$cross_engine %||% "byte-identical"),
    sprintf("- **Counterbalancing:** %s, %s list(s)", ds$counterbalancing$recipe,
            ds$counterbalancing$lists),
    # Said only where there is a choice to make, so a single-version record has no such
    # line.
    if ((ds$counterbalancing[["versions"]] %||% 1L) > 1L)
      sprintf("- **Presentation versions:** %s, assigned as %s",
              ds$counterbalancing[["versions"]], ds$counterbalancing[["assignment"]])
    else NULL,
    if (!is.null(ds$counterbalancing[["orders"]]))
      sprintf("- **Trial orders:** %d per list, assigned as %s",
              as.integer(ds$counterbalancing$orders$m), ds$counterbalancing$orders$rule)
    else NULL,
    if (!is.null(ds$counterbalancing[["max_run"]]))
      sprintf("- **Run limit:** at most %d consecutive trials with the same `%s` (longest realised: %d)",
              as.integer(ds$counterbalancing$max_run$k), ds$counterbalancing$max_run$run_on,
              as.integer(max(0L, vapply(ds$counterbalancing$max_run$longest,
                                        function(r) as.integer(r$longest_run), integer(1)))))
    else NULL,
    sprintf("- **Items:** %s rows across %s conditions (%s)", ds$items$n_total,
            ds$items$n_conditions, paste(unlist(ds$items$conditions), collapse = ", ")),
    sprintf("- **Seed:** %s  |  **Versions:** %s", ds$reproducibility$seed, versions), "")
  # Norm tables, with their checksums and coverage. A dimension covering only part of
  # the lexicon matters to a reader: an uncovered row carries NA, so a pool filter or a
  # condition's define_by on the dimension drops it, and when the dimension is matched
  # (or, in a continuous design, is the predictor or a control) the row is excluded
  # before anything is selected and counted in selection$incomplete_dropped. Coverage is
  # therefore part of how the pool was defined.
  nrm <- ds$materials_source$norms
  if (!is.null(nrm) && length(nrm)) {
    lines <- c(lines, "## Joined norms", "",
               "| File | Key | Column | Coverage | sha256 |", "|---|---|---|---|---|")
    for (t in nrm) {
      for (cl in t$columns) {
        lines <- c(lines, sprintf("| `%s` | %s | %s | %s / %s | `%s...` |", t$path, t$on,
                                  cl$column, cl$n_matched, cl$n_total,
                                  substring(t$sha256 %||% "", 1, 16)))
      }
    }
    lines <- c(lines, "")
  }
  # Balance-aware list assignment. Reported because it decides which items each
  # participant sees, and the before/after costs are what make the claim checkable
  # rather than a bare assertion that the lists are balanced.
  bal <- ds$counterbalancing$optimise
  if (!is.null(bal)) {
    lines <- c(lines, "## Balanced list assignment", "",
               sprintf("- **Balanced on:** %s", paste(unlist(bal$dimensions), collapse = ", ")),
               sprintf("- **Imbalance:** %s before, %s after, in %s swap(s)",
                       format(bal$cost_before, scientific = FALSE),
                       format(bal$cost_after, scientific = FALSE), bal$n_swaps),
               sprintf("- **Cost unit:** %s", bal$cost_unit),
               if (isTRUE(bal$max_passes_reached))
                 paste0("- The search stopped at its pass bound rather than at a local ",
                        "optimum, so a higher `counterbalance.max_passes` may balance ",
                        "the lists further.")
               else paste0("- The search ran to a local optimum: no single exchange of ",
                           "two item sets between lists would reduce the imbalance further."),
               paste0("- The search is a deterministic integer descent with a keyed-hash ",
                      "tie-break, so it uses no random number generator and the R and ",
                      "Python engines produce the same assignment."), "")
  }
  # The trials each list gives each condition, and whatever leaves a Latin-square
  # rotation incomplete, so a reader can check the rotation against the counts.
  # Mirrors render_datasheet_md in datasheet.py.
  issues <- unlist(ds$counterbalancing$issues)
  cells <- ds$counterbalancing$cells
  if (length(issues) || length(cells)) {
    lines <- c(lines, "## Counterbalanced lists", "")
    if (length(issues)) lines <- c(lines, paste0("- **Incomplete rotation:** ", issues), "")
    if (length(cells)) {
      with_rep <- any(vapply(cells, function(x) !is.null(x$replicate), logical(1)))
      lines <- c(lines,
                 if (with_rep) c("| Replicate | List | Condition | Trials |", "|---|---|---|---|")
                 else c("| List | Condition | Trials |", "|---|---|---|"),
                 vapply(cells, function(x) {
                   paste0(if (with_rep) sprintf("| %s | ", x$replicate) else "| ",
                          sprintf("%s | %s | %s |", x$list, x$condition, x$n_trials))
                 }, character(1)), "")
    }
  }
  rel <- ds$relational
  if (!is.null(rel)) {
    lines <- c(lines, "## Pair-keyed items", "",
               sprintf("- **Members:** %s  |  **Pairs:** %s",
                       paste(unlist(rel$members), collapse = ", "), rel$n_pairs),
               sprintf("- **Member lexicon:** `%s` (sha256 `%s...`)", rel$member_lexicon,
                       substring(rel$member_lexicon_sha256 %||% "", 1, 16)),
               sprintf("- **Member-level dimensions** (one word): %s",
                       paste(unlist(rel$member_dimensions), collapse = ", ")),
               sprintf("- **Relational dimensions** (the pair): %s",
                       paste(unlist(rel$relational_dimensions), collapse = ", ")),
               paste0("- Selection ran on one row per pair and the result was re-expanded, ",
                      "so every condition row of every chosen pair is present."), "")
  }
  cp <- ds$selection$candidate_pool
  if (!is.null(cp) && length(cp)) {
    parts <- paste(vapply(cp, function(x) sprintf("%s: %s", x$condition, x$n_candidates),
                          character(1)), collapse = ", ")
    lines <- c(lines, "## Selection transparency", "",
               sprintf(paste0("- **Candidate pool** (items satisfying each condition's window ",
                              "before matching): %s."), parts),
               paste0("- ", .transparency_note(ds)), "")
  }
  if (length(ds$realised_control) && !is.null(ds$selection$predictor)) {
    lines <- c(lines, "## Realised control (continuous predictor)", "",
               "| Dimension | Role | r with predictor | Predictor span |",
               "|---|---|---|---|")
    for (r in ds$realised_control) {
      lines <- c(lines, sprintf("| %s | %s | %s | %s |", r$dimension, r$role,
                                .fmt_dp(r$pearson_r, 3), .fmt_dp(r$predictor_span, 3)))
    }
    lines <- c(lines, "")
  } else if (length(ds$realised_control)) {
    # Each row names its pair and gives the raw difference, and the interval is labelled
    # by the schema's alpha (see .ci_pct).
    pct <- .ci_pct(ds[["equivalence"]][["alpha"]] %||% 0.05)
    lines <- c(lines, "## Realised control", "",
               paste0("Each row compares a condition with its reference. The raw difference ",
                      "and Cohen's d are the reference mean minus the condition mean, and the ",
                      "variance ratio is the condition's variance over the reference's."), "",
               paste0("| Condition | Reference | Dimension | Role | Raw difference | ",
                      "Cohen's d | ", pct, "% CI | Var ratio | TOST p | Equivalent |"),
               "|---|---|---|---|---|---|---|---|---|---|")
    for (r in ds$realised_control) {
      # A record written before the pair was recorded reaches the first two cells.
      ci <- if (!is.null(r[["ci_low"]]))
        sprintf("[%s, %s]", .fmt_dp(r[["ci_low"]], 2), .fmt_dp(r[["ci_high"]], 2)) else "--"
      lines <- c(lines, sprintf("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |",
                                r[["condition"]] %||% "--", r[["reference"]] %||% "--",
                                r[["dimension"]], r[["role"]], .fmt_dp(r[["mean_diff"]], 3),
                                .fmt_dp(r[["cohens_d"]], 2), ci, .fmt_dp(r[["var_ratio"]], 2),
                                .fmt_tost_p(r[["tost_p"]]), r[["equivalent"]] %||% "--"))
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

#' Write a datasheet to a JSON record and a Markdown rendering
#'
#' @param ds A datasheet list, from [build_datasheet()].
#' @param json_path Output path for the machine-readable JSON record.
#' @param md_path Output path for the human-readable Markdown rendering.
#' @return Invisibly, the two paths written.
#' @export
write_datasheet <- function(ds, json_path, md_path) {
  # write_lines_lf, not writeLines: a text-mode connection turns every newline into
  # CRLF on Windows, so the datasheet's own bytes would record which machine built it
  # and disagree with the Python engine's record of the same design. The datasheet is the
  # provenance artefact, and the last file that should depend on the platform.
  # digits = NA, not jsonlite's default of 4. The default silently truncated every
  # value that had not already been rounded on the way in: a design declaring
  # `tolerance_k: 0.1111111111111111` had it recorded as 0.1111, which does not
  # reproduce the run the record exists to describe. Most fields survived only because
  # they are rounded to four places deliberately (see .r4). NA means R's full display
  # precision, 15 significant digits, which the Python engine also writes. jsonlite
  # 1.8.5 and 1.8.6 write 17 instead, so a datasheet written with either of them
  # differs from the Python engine's.
  write_lines_lf(jsonlite::toJSON(ds, auto_unbox = TRUE, pretty = TRUE,
                                  null = "null", na = "null", digits = NA), json_path)
  write_lines_lf(render_datasheet_md(ds), md_path)
  invisible(c(json_path, md_path))
}
