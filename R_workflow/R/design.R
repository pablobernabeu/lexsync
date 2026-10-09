# design.R -- check a design and its schema before anything is selected or written.
#
# A design file is read key by key all over the package, so a key it misspells is not
# an error anywhere: `n_per_conditon: 8` left the design on the default twenty items
# per condition and nothing said so. Metadata were checked only at export, after the
# stimuli and both reports were on disk, and a missing `name` failed differently in
# each engine. This file holds the vocabulary of keys lexsync reads and the checks
# that run_pipeline() applies right after reading the configuration, so a design that
# cannot be honoured is refused before the output directory is touched, with one
# message in both engines. It also resolves the three values each selector used to
# resolve by its own rule: the number of items per condition, the tolerance windows
# and the file stem every artefact is named after. Mirrors
# python_workflow/src/lexsync/design.py.

# Every key lexsync reads from a design, as dotted paths. `[]` marks a list whose
# entries are mappings. A key whose value holds names the user chooses is listed
# without children (pool_filters, define_by, tolerance_k, timing, norms), so nothing
# below it is checked here: timing checks its own keys in render_events(), and the
# keys of a norms entry are checked where the norms are joined. Seeded from every key
# the shipped designs, both engines, both apps and the tests read. Must list the same
# paths in the same order as DESIGN_KEYS in design.py, and both test suites pin a
# digest of the list.
.DESIGN_KEYS <- c(
  "name", "language", "language_tag", "description", "paradigm", "lexicon",
  "items", "items.source", "items.path", "items.lexicon", "items.members",
  "items.generation", "items.generation.method", "items.generation.exclude",
  "items.anchor_condition",
  "pool_filters",
  "conditions", "conditions[].name", "conditions[].define_by",
  "match_on", "n_per_condition", "n_per_cell",
  "matching", "matching.method", "matching.tolerance_k", "matching.shortfall",
  "matching.on_insufficient_tolerance", "matching.tie_break",
  "resample", "resample.n_sets",
  "counterbalance", "counterbalance.lists", "counterbalance.optimise",
  "counterbalance.balance_on", "counterbalance.max_passes", "counterbalance.recipe",
  "counterbalance.incomplete",
  "continuous", "continuous.predictor", "continuous.controls",
  "norms",
  "events", "events[].type", "events[].content", "events[].duration_ms",
  "events[].duration_frames", "events[].duration", "events[].duration.from_column",
  "events[].duration.jitter", "events[].duration.as", "events[].trigger",
  "events[].onset_locked", "events[].keys", "events[].timeout_ms", "events[].from",
  "events[].advance",
  "events[].sep", "events[].critical_region_trigger", "events[].answer",
  "events[].correct", "events[].incorrect", "events[].no_response", "events[].blocks",
  "timing", "font",
  "practice", "practice.path",
  "fillers", "fillers.path"
)

# The same for the global schema. `dimensions` holds the dimension names.
.SCHEMA_KEYS <- c(
  "seed",
  "lexicon_schema", "lexicon_schema.required", "lexicon_schema.optional",
  "dimensions",
  "matching", "matching.method", "matching.tolerance_k", "matching.shortfall",
  "matching.on_insufficient_tolerance", "matching.tie_break",
  "equivalence", "equivalence.bound_d", "equivalence.alpha",
  "triggers", "triggers.parallel_address", "triggers.trigger_hold_ms",
  "triggers.reset_after_frames", "triggers.inter_trigger_ms",
  "presentation", "presentation.font", "presentation.opensesame_font",
  "presentation.assumed_refresh_hz",
  "counterbalance", "counterbalance.incomplete"
)

.N_MESSAGE <- "lexsync: n_per_condition must be a positive whole number."

# A mapping read from YAML is a named list, and a sequence of mappings an unnamed one.
.is_mapping <- function(x) is.list(x) && !is.null(names(x))

.is_annotation <- function(key) identical(key, "description") || startsWith(key, "x_")

# The keys directly below `prefix` ("" for the top level), in vocabulary order.
.vocab_children <- function(vocabulary, prefix) {
  rest <- if (nzchar(prefix)) {
    under <- startsWith(vocabulary, paste0(prefix, "."))
    substring(vocabulary[under], nchar(prefix) + 2L)
  } else vocabulary
  rest[!grepl(".", rest, fixed = TRUE)]
}

.vocab_has_children <- function(vocabulary, prefix) {
  any(startsWith(vocabulary, paste0(prefix, ".")))
}

# The known key a typo was probably meant to be, or NULL. One edit is a typo for a
# known key of up to five characters, two for a longer one. The distance is optimal
# string alignment, Levenshtein's with an adjacent transposition counted as one edit,
# so `nmae` is one edit from `name`. Without the shorter limit, `notes`, a natural
# annotation, would be refused as a misspelling of `norms`, two edits away. stringdist's
# "osa" here and rapidfuzz's OSA in the Python twin agree on these integer distances.
# Ties go to the earlier key in the vocabulary.
.nearest_key <- function(key, known) {
  if (!length(known)) return(NULL)
  d <- stringdist::stringdist(key, known, method = "osa")
  limit <- ifelse(nchar(known) <= 5L, 1, 2)
  ok <- which(d <= limit)
  if (!length(ok)) return(NULL)
  known[ok[which.min(d[ok])]]
}

# Refuse a near-miss key and return a note for every other unknown one. The walk
# follows the document's own key order, so the first near-miss is the one reported and
# the notes come in the order the keys were written. A list entry is named by its
# position counted from 1, as in `events[3].durration`. Must stay identical to
# _check_keys in design.py.
.check_keys <- function(config, vocabulary, kind) {
  notes <- character(0)
  walk <- function(node, vprefix, dprefix) {
    siblings <- NULL
    for (i in seq_along(node)) {
      key <- names(node)[i]
      value <- node[[i]]
      if (.is_annotation(key)) next
      vpath <- if (nzchar(vprefix)) paste0(vprefix, ".", key) else key
      dpath <- if (nzchar(dprefix)) paste0(dprefix, ".", key) else key
      if (vpath %in% vocabulary) {
        if (.is_mapping(value) && .vocab_has_children(vocabulary, vpath)) {
          walk(value, vpath, dpath)
        } else if (is.list(value) && is.null(names(value)) &&
                   .vocab_has_children(vocabulary, paste0(vpath, "[]"))) {
          for (j in seq_along(value)) {
            if (.is_mapping(value[[j]])) {
              walk(value[[j]], paste0(vpath, "[]"), sprintf("%s[%d]", dpath, j))
            }
          }
        }
        next
      }
      if (is.null(siblings)) siblings <- .vocab_children(vocabulary, vprefix)
      near <- .nearest_key(key, siblings)
      if (!is.null(near)) {
        want <- if (nzchar(dprefix)) paste0(dprefix, ".", near) else near
        stop(sprintf("lexsync: unknown %s key '%s' (did you mean '%s'?)", kind, dpath, want),
             call. = FALSE)
      }
      notes <<- c(notes, sprintf(paste(
        "lexsync: %s key '%s' is not read by lexsync and is ignored; a later release",
        "will refuse it. Put annotations in `description` or a key beginning `x_`."),
        kind, dpath))
    }
  }
  if (.is_mapping(config)) walk(config, "", "")
  notes
}

# A scalar as the user typed it, near enough to quote back in a message.
.shown <- function(value) {
  if (is.logical(value)) return(if (isTRUE(value)) "true" else "false")
  if (is.numeric(value)) return(.key_part(value))
  as.character(value)
}

# A required text value of the design, or a refusal naming the key. trimws() strips
# spaces, tabs and line breaks only, and _text in design.py strips the same set.
.design_text <- function(design, key, hint) {
  value <- design[[key]]
  if (is.null(value) || (is.character(value) && length(value) == 1L &&
                         !is.na(value) && !nzchar(trimws(value)))) {
    stop(sprintf("lexsync: the design has no `%s`.", key), call. = FALSE)
  }
  if (!is.character(value) || length(value) != 1L || is.na(value)) {
    stop(sprintf("lexsync: the design's `%s` must be text; %s", key, hint), call. = FALSE)
  }
  value
}

.name_and_language <- function(design) {
  if (!.is_mapping(design)) {
    stop("lexsync: a design must be a mapping of keys to values.", call. = FALSE)
  }
  list(name = .design_text(design, "name", "quote it in the design file."),
       language = .design_text(design, "language",
                               "quote it if it is a code such as 'no'."))
}

# The number of items per condition, by one rule everywhere: `n_per_condition`, then
# `n_per_cell`, then `default`, each taken when it is present. A present value must
# be a whole number of at least 1, written as 4 or 4.0, and comes back as an integer.
# The finiteness test matters: trunc(Inf) equals Inf, so an infinite request once
# passed the whole-number test here and selected the whole pool. The upper bound is
# where as.integer() would give NA. `default` may be NULL, for a caller that only
# checks. Must stay identical to _resolve_n in design.py.
.resolve_n <- function(design, default) {
  n <- design[["n_per_condition"]] %||% design[["n_per_cell"]]
  if (is.null(n)) return(default)
  if (!is.numeric(n) || length(n) != 1L || !is.finite(n) || n < 1 ||
      n != trunc(n) || n > .Machine$integer.max) {
    stop(.N_MESSAGE, call. = FALSE)
  }
  as.integer(n)
}

# The tolerance windows, k per dimension, as modifyList() resolves them. The schema's
# map is the base and the design's overrides it per dimension. A null in the schema's
# map is dropped, and a null in the design's deletes that dimension from the merged
# map, so k falls back to the matcher's default of 2. The nearest-neighbour methods
# apply these windows. The pairwise joint and optimal methods never consult them,
# which is why the datasheet attaches this block only for the methods that do. Must
# stay identical to _resolve_tolerance_k in design.py.
.resolve_tolerance_k <- function(design, schema) {
  base <- schema[["matching"]][["tolerance_k"]]
  base <- if (is.list(base)) base[!vapply(base, is.null, logical(1))] else list()
  over <- design[["matching"]][["tolerance_k"]]
  if (is.list(over) && length(over)) base <- utils::modifyList(base, over)
  base
}

# The dimensions a matched design equates its conditions on, or a refusal. Without
# any, every candidate scores distance zero and the tie-break alone picks the
# byte-first words, which the datasheet would still call matched.
.require_match_on <- function(design) {
  match_on <- unlist(design[["match_on"]], use.names = FALSE)
  if (!length(match_on)) {
    stop("lexsync: a matched design needs `match_on` naming at least one dimension.",
         call. = FALSE)
  }
  match_on
}

# Every dimension the design names, in first-mention order: `match_on`, each
# condition's `define_by` keys, the `pool_filters` keys, the continuous predictor and
# controls, and `counterbalance.balance_on`, in that order and without repeats. The
# pipeline derives any of `n_density`, `old20` and `bigram_freq` in this list that the
# lexicon lacks. Only `match_on` used to trigger the derivation, so a design that
# manipulated, filtered on or regressed on a derived dimension stopped with "absent
# from the pool". Must stay identical to _referenced_dimensions in design.py.
.referenced_dimensions <- function(design) {
  as_names <- function(x) as.character(unlist(x, use.names = FALSE))
  out <- as_names(design[["match_on"]])
  for (cond in design[["conditions"]] %||% list()) {
    if (.is_mapping(cond) && .is_mapping(cond[["define_by"]])) {
      out <- c(out, names(cond[["define_by"]]))
    }
  }
  if (.is_mapping(design[["pool_filters"]])) out <- c(out, names(design[["pool_filters"]]))
  continuous <- design[["continuous"]]
  if (.is_mapping(continuous)) {
    out <- c(out, as_names(continuous[["predictor"]]), as_names(continuous[["controls"]]))
  }
  counterbalance <- design[["counterbalance"]]
  if (.is_mapping(counterbalance)) out <- c(out, as_names(counterbalance[["balance_on"]]))
  unique(out)
}

#' The stem every file a design writes is named after
#'
#' The slug of the design's `name` and `language`, which keeps letters and digits
#' only. Two designs whose names differ only outside ASCII (two Chinese names, both
#' with the language `chinese`) would share a slug and overwrite each other's files,
#' and an all-Chinese name and language would give no slug at all. Whenever the name
#' or the language holds a non-ASCII character, the stem therefore gains `_` and the
#' first eight hexadecimal digits of the SHA-256 of the NFC-normalised UTF-8 text
#' `name|language`. An empty slug is replaced by those eight digits. NFC keeps a
#' precomposed and a decomposed accented letter on one stem. A design whose name and
#' language hold no letter or digit at all is refused. Mirrors `design_stem()` in the
#' Python package.
#'
#' @param design A parsed design configuration.
#' @return The file stem, such as `"en_lexdec_english"` or `"chinese_14aadfa7"`.
#' @examples
#' design_stem(list(name = "en_lexdec", language = "english"))
#' # Two Chinese characters, written as code points to keep this file ASCII.
#' design_stem(list(name = intToUtf8(c(0x8bcd, 0x9891)), language = "chinese"))
#' @export
design_stem <- function(design) {
  nl <- .name_and_language(design)
  name <- stringi::stri_trans_nfc(nl$name)
  language <- stringi::stri_trans_nfc(nl$language)
  stem <- slugify(name, language)
  joined <- stringi::stri_trans_nfc(paste0(name, "|", language))
  if (!stringi::stri_enc_isascii(joined)) {
    # enc2utf8 because digest(serialize = FALSE) hashes the stored bytes, as in
    # hash_unit().
    h <- substr(digest::digest(enc2utf8(joined), algo = "sha256", serialize = FALSE), 1L, 8L)
    stem <- if (nzchar(stem)) paste0(stem, "_", h) else h
  }
  if (!nzchar(stem)) {
    stop(paste("lexsync: the design's `name` and `language` hold no letter or digit to",
               "name its files after; use letters or digits in the name."), call. = FALSE)
  }
  stem
}

.check_conditions <- function(design) {
  conds <- design[["conditions"]]
  if (is.null(conds)) return(invisible(NULL))
  missing_name <- "lexsync: every entry under `conditions` needs a `name`."
  if (!is.list(conds) || .is_mapping(conds)) stop(missing_name, call. = FALSE)
  nm <- character(0)
  for (cond in conds) {
    if (!.is_mapping(cond) || is.null(cond[["name"]])) stop(missing_name, call. = FALSE)
    name <- cond[["name"]]
    if (!is.character(name) || length(name) != 1L || is.na(name)) {
      stop(sprintf("lexsync: condition names must be text; quote '%s'.",
                   .shown(name)[1]), call. = FALSE)
    }
    nm <- c(nm, name)
  }
  # The first entry that repeats an earlier name is reported, in both engines.
  dup <- nm[duplicated(nm)]
  if (length(dup)) {
    stop(sprintf(paste("lexsync: condition name '%s' appears more than once; condition",
                       "names must be unique."), dup[1]), call. = FALSE)
  }
  invisible(NULL)
}

#' Check a design and its schema before anything is selected or written
#'
#' [run_pipeline()] calls this right after reading the two files, so a design that
#' cannot be honoured is refused before any output exists, with the same message in
#' both engines. It first refuses a key within one or two edits of a key lexsync
#' reads at that level, naming the key it was probably meant to be (one edit for a
#' known key of up to five characters, two for a longer one). It then refuses a
#' missing, empty or non-text `name` or `language`, and an `n_per_condition` or
#' `n_per_cell` that is not a whole number of at least 1. It refuses a name, language
#' or font that cannot be written into the generated experiments, a trigger port that
#' is not an address, and an event list the renderer refuses, such as one with an
#' unknown timing key or a bad response key. Last, it refuses a condition without a
#' name, with a name that is not text or with a repeated name, a corpus or pool
#' design with conditions but no `match_on`, and a name and language that leave no
#' file stem.
#'
#' Any other key lexsync does not read is not refused yet. It is returned as a note,
#' which [run_pipeline()] writes into the run log, and a later release will refuse
#' it. `description` and keys beginning `x_` are annotations and are never noted.
#'
#' @param design A parsed design configuration.
#' @param schema The parsed global schema.
#' @return A character vector of notes on unknown keys, in the order the keys were
#'   written; empty when there are none.
#' @examples
#' validate_design(list(name = "demo", language = "english", x_note = "pilot"), list())
#' @export
validate_design <- function(design, schema) {
  schema <- schema %||% list()
  if (!.is_mapping(design)) {
    stop("lexsync: a design must be a mapping of keys to values.", call. = FALSE)
  }
  notes <- c(.check_keys(design, .DESIGN_KEYS, "design"),
             .check_keys(schema, .SCHEMA_KEYS, "schema"))
  .name_and_language(design)
  .resolve_n(design, NULL)

  clean_meta(design[["name"]], "the design's `name`")
  clean_meta(design[["language"]], "the design's `language`")
  font <- design[["font"]]
  if (!is.null(font) && (!is.character(font) || length(font) != 1L || is.na(font))) {
    stop("lexsync: the design's `font` must be text; quote it in the design file.",
         call. = FALSE)
  }
  presentation <- schema[["presentation"]] %||% list()
  # The PsychoPy and jsPsych targets fall back to presentation.font, OpenSesame to its
  # own font token, so both effective fonts are checked.
  clean_meta(font %||% presentation[["font"]] %||% "Courier New", "the font")
  clean_meta(font %||% presentation[["opensesame_font"]] %||% "mono", "the font")
  clean_port(schema[["triggers"]][["parallel_address"]] %||% "0x0378")
  render_events(resolve_events(design), design[["timing"]] %||% list(), .refresh_hz(schema))

  .check_conditions(design)
  source <- design[["items"]][["source"]] %||% "corpus"
  if (source %in% c("corpus", "pool") && is.null(design[["continuous"]]) &&
      length(design[["conditions"]])) {
    .require_match_on(design)
  }
  design_stem(design)
  notes
}
