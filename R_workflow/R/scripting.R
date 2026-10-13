# scripting.R -- export finalised, hardware-timed experiment scripts. Both targets
# render the same declarative trial-event sequence (see paradigms.R), so a new
# paradigm requires only a configuration change rather than new backend code. The PsychoPy script reads
# stimulus text as data from the conditions file and interprets an embedded EVENTS
# list; the OpenSesame .osexp is generated block by block. Generation imports
# neither psychopy nor pyserial: it only writes text. Mirrors scripting.py.

#' Locate a bundled template file
#' @keywords internal
find_template <- function(relpath) {
  opt <- getOption("lexsync.templates", "")
  cand <- c(
    if (nzchar(opt)) file.path(opt, relpath),
    system.file("templates", relpath, package = "lexsync"),
    file.path("templates", relpath),
    file.path("..", "templates", relpath)
  )
  cand <- cand[nzchar(cand) & file.exists(cand)]
  if (!length(cand)) stop(sprintf("lexsync: template '%s' not found.", relpath), call. = FALSE)
  cand[1]
}

#' Assign EEG trigger codes to stimuli
#'
#' Adds `condition_trigger` (101, 102, ... per condition) and `item_trigger`
#' (40-239 per item/`set`). Events reference these by the tokens "condition" and
#' "item", or carry their own codes, whole numbers from 1 to 255. Item codes follow
#' the code-point order of the set labels, so with sets 1 to 20, set 10 is 41 and set
#' 2 is 51. Decode an item code through the loop table, not from the set's label. The
#' item range holds 200 codes (an 8-bit-port constraint), so past 200 sets the codes
#' wrap and repeat, and a runtime notice says so.
#'
#' `events`, the design's event list, says which codes the experiment sends. When it
#' sends item codes together with condition codes, or with a code of its own from 40
#' to 239, the item codes skip 101 to 100 + k, the codes of the k conditions, and the
#' design's own codes, so that no item takes a code that marks something else. Sets
#' 65 and 66 of a 70-set design took 101 and 102, the condition codes. A design with
#' more item sets than free codes is then refused, unless `schema` sets
#' `triggers.allow_code_overlap: true`, which lets the item codes wrap and repeat
#' within the free codes. Every other design, and a call without `events`, gets the
#' item codes it had before. Each trigger in `events` is checked as
#' [render_events()] checks it.
#'
#' A notice is given for a code of the design's own that the stream already uses for
#' something else: 254 or 255, which the PsychoPy experiment sends when the session
#' starts and ends, a condition code the design sends, or a code within the range of
#' the item codes it sends.
#'
#' The condition codes follow `conditions` when it is given: its first entry is
#' 101, its second 102, and so on, whether or not every entry occurs in
#' `stimuli`, so the same condition keeps the same code in a subset such as a
#' practice block. A condition present in `stimuli` but missing from
#' `conditions` takes the next free codes, in code-point order of its label.
#' Either way the mapping depends only on the labels, never on the row order.
#' Without `conditions`, the codes follow the order in which the conditions first
#' appear in `stimuli`, as in lexsync 0.1.0. On a shuffled trial list that order
#' comes from the shuffle, so a different seed can swap two conditions' codes.
#' [export_experiments()] passes the design's order, and the pipeline passes the
#' order of the design's `conditions`, followed by any other condition in the
#' order the item source lists it.
#'
#' @param stimuli A stimuli data frame.
#' @param conditions Optional character vector of condition labels, in the order
#'   that assigns their codes from 101 upwards. `NULL` (the default) numbers the
#'   conditions in order of first appearance.
#' @param events Optional list of the design's events, as [resolve_events()] returns
#'   them, which says which codes the experiment sends. `NULL` (the default) allocates
#'   the item codes as for a design that sends no other code beside them.
#' @param schema Optional parsed global schema, read for
#'   `triggers.allow_code_overlap`, which must be `true` or `false` when given.
#' @return `stimuli` with trigger columns added.
#' @examples
#' stim <- data.frame(condition = c("low", "high", "low", "high"), set = c(1, 1, 2, 2))
#' # First appearance: low = 101, high = 102.
#' unique(assign_triggers(stim)[, c("condition", "condition_trigger")])
#' # The design's order: high = 101, low = 102, however the rows are shuffled.
#' unique(assign_triggers(stim, conditions = c("high", "low"))[
#'   , c("condition", "condition_trigger")])
#' # Item codes follow the code-point order of the set labels: set 2 is 51 here.
#' twenty <- assign_triggers(data.frame(condition = "a", set = 1:20))
#' stats::setNames(twenty$item_trigger, twenty$set)
#' @export
assign_triggers <- function(stimuli, conditions = NULL, events = NULL, schema = NULL) {
  res <- .allocate_codes(stimuli, conditions, events, schema)
  for (note in res$notes) message(note)
  res$stimuli
}

# The codes item markers are drawn from, 40 to 239. That leaves 1 to 39 for a design's
# own codes, such as the priming paradigm's 20, and keeps clear of the session markers
# 254 and 255. Must match _ITEM_CODES in scripting.py.
.ITEM_CODES <- 40:239

# assign_triggers() without its notices: list(stimuli = the stimuli with the codes,
# notes = the notices). run_pipeline() calls it before any file is written, so that a
# design whose item codes cannot be kept apart is refused there, and assign_triggers()
# gives the notices once, when the experiments are written. Must match _allocate_codes
# in scripting.py.
.allocate_codes <- function(stimuli, conditions = NULL, events = NULL, schema = NULL) {
  allow_overlap <- .allow_code_overlap(schema)
  present <- unique(as.character(stimuli$condition))
  if (is.null(conditions)) {
    conds <- present
  } else {
    conds <- unique(as.character(unlist(conditions, use.names = FALSE)))
    # Radix order is byte order, which for UTF-8 is code-point order, the same
    # order Python's sorted() gives, and it does not depend on the locale.
    extra <- setdiff(present, conds)
    conds <- c(conds, extra[order(extra, method = "radix")])
  }
  stimuli$condition_trigger <- 100L + match(as.character(stimuli$condition), conds)
  sets <- unique(stimuli$set)
  sets <- sets[order(as.character(sets), method = "radix")]
  sent <- .codes_sent(events)
  own <- sort(unique(vapply(sent$literals, function(l) l[["code"]], integer(1))))
  notes <- character(0)
  if (sent$item && (sent$condition || any(own %in% .ITEM_CODES))) {
    # The item codes share the stream with codes that mean something else, so they are
    # drawn only from the codes nothing else takes.
    free <- setdiff(.ITEM_CODES, c(100L + seq_along(conds), own))
    if (length(sets) > length(free)) {
      if (!(allow_overlap && length(free))) {
        stop(sprintf(paste("lexsync: %d item sets need %d item codes, but only %d of the codes",
                           "from 40 to 239 are free of the condition codes and the design's",
                           "own codes; send fewer kinds of code, or set",
                           "triggers.allow_code_overlap: true to let item codes repeat."),
                     length(sets), length(sets), length(free)), call. = FALSE)
      }
      notes <- c(notes, sprintf(
        "lexsync: %d item sets exceed the %d free item codes; item codes wrap and repeat.",
        length(sets), length(free)))
    }
    code <- free[(seq_along(sets) - 1L) %% length(free) + 1L]
  } else {
    # A wrapped code no longer identifies its item one to one, which the analyst
    # must hear about at generation time, not at decode time.
    if (length(sets) > 200L) {
      notes <- c(notes, sprintf(
        "lexsync: %d item sets exceed the 200-code trigger range; item codes wrap and repeat.",
        length(sets)))
    }
    code <- 40L + ((seq_along(sets) - 1L) %% 200L)
  }
  stimuli$item_trigger <- code[match(stimuli$set, sets)]
  list(stimuli = stimuli, notes = c(notes, .code_notes(sent, conds, code)))
}

# The schema's triggers.allow_code_overlap, FALSE when absent. Read strictly: a value
# that is not TRUE or FALSE is refused, since isTRUE() would quietly read "yes" as false
# where Python's truth test reads it as true. Must match _allow_code_overlap in
# scripting.py.
.allow_code_overlap <- function(schema) {
  value <- (schema[["triggers"]] %||% list())[["allow_code_overlap"]]
  if (is.null(value)) return(FALSE)
  if (!is.logical(value) || length(value) != 1L || is.na(value)) {
    stop("lexsync: triggers.allow_code_overlap must be true or false.", call. = FALSE)
  }
  value
}

# The codes a design's events send: `item` and `condition` say whether any event sends
# the item code or the condition code, and `literals` lists the design's own codes as
# list(event, code), the event counted from 1, in event order. A fixation, text or mask
# event sends its `trigger` and a region-by-region event its `critical_region_trigger`,
# the keys render_events() reads, and each is checked as it is there. Must match
# _codes_sent in scripting.py.
.codes_sent <- function(events) {
  sent <- list(item = FALSE, condition = FALSE, literals = list())
  for (i in seq_along(events)) {
    ev <- events[[i]]
    type <- ev[["type"]]
    key <- if (isTRUE(type %in% c("fixation", "text", "mask"))) "trigger" else
      if (identical(type, "region_by_region")) "critical_region_trigger" else NULL
    spec <- if (is.null(key)) NULL else trigger_spec(ev[[key]], i, key)
    if (is.null(spec)) next
    if (identical(spec, "@item_trigger")) {
      sent$item <- TRUE
    } else if (identical(spec, "@condition_trigger")) {
      sent$condition <- TRUE
    } else {
      sent$literals[[length(sent$literals) + 1L]] <- list(event = i, code = spec)
    }
  }
  sent
}

# The notices for the design's own codes that the stream already uses: a code of 254 or
# 255, which the PsychoPy experiment sends when the session starts and ends, a code
# equal to a condition code the design sends, and a code within the range of the item
# codes it sends. The allocation keeps every item code off the design's own codes, so
# the last is a warning for anyone who decodes item codes by their range. Must match
# _code_notes in scripting.py.
.code_notes <- function(sent, conds, item_codes) {
  notes <- character(0)
  for (l in sent$literals) {
    i <- l[["event"]]
    code <- l[["code"]]
    if (code %in% c(254L, 255L)) {
      notes <- c(notes, sprintf(paste("lexsync: event %d sends code %d, which the PsychoPy",
                                      "experiment also sends when the session %s."),
                                i, code, if (code == 254L) "starts" else "ends"))
    }
    if (sent$condition && code >= 101L && code <= 100L + length(conds)) {
      notes <- c(notes, sprintf(paste("lexsync: event %d sends code %d, which is also the",
                                      "condition code of '%s'."),
                                i, code, .shown(conds[code - 100L])))
    }
    if (sent$item && length(item_codes) && code >= min(item_codes) && code <= max(item_codes)) {
      notes <- c(notes, sprintf(paste("lexsync: event %d sends code %d, which lies inside the",
                                      "range of the item codes (%d to %d); decode item codes",
                                      "through the loop table."),
                                i, code, min(item_codes), max(item_codes)))
    }
  }
  notes
}

# The names of a design's declared conditions, in the order the design lists
# them, or NULL when it declares none (a generated lexical decision, an item
# table, a continuous design). Mirrors _design_condition_names in scripting.py.
.design_condition_names <- function(design) {
  conds <- design[["conditions"]]
  if (!is.list(conds) || !length(conds)) return(NULL)
  nm <- unlist(lapply(conds, function(cnd) if (is.list(cnd)) cnd[["name"]]), use.names = FALSE)
  if (length(nm)) as.character(nm) else NULL
}

# Translate a paradigm trigger token to a renderer spec (an integer or "@column"). A
# trigger is the token "condition" or "item", or a whole number from 1 to 255, written
# as a number or as a string of digits. Anything else is refused, naming the event by
# `index`, its place in the design counted from 1, and the `key` the value came from.
# as.integer() took 20.5 as 20 and let 300, 0 or -5 reach the port, which keeps only
# the low byte. It turned a misspelt token such as "conditon" into NA, which reached the
# OpenSesame experiment as send_trigger(NA), while the Python engine stopped. Must match
# _trigger_spec in scripting.py.
#' @keywords internal
trigger_spec <- function(value, index = NULL, key = "trigger") {
  if (is.null(value)) return(NULL)
  code <- NA_real_
  if (is.character(value) && length(value) == 1L && !is.na(value)) {
    if (identical(value, "condition")) return("@condition_trigger")
    if (identical(value, "item")) return("@item_trigger")
    # \z and not $, for the reason given beside .PORT_SHAPE in io_utils.R.
    if (grepl("^[0-9]+\\z", value, perl = TRUE)) code <- as.numeric(value)
  } else if (is.numeric(value) && length(value) == 1L && is.finite(value) &&
             value == trunc(value)) {
    code <- as.numeric(value)
  }
  if (is.na(code) || code < 1 || code > 255) {
    where <- if (is.null(index)) "an event" else sprintf("event %d", as.integer(index))
    stop(sprintf("lexsync: %s has %s '%s'; use 'condition', 'item' or a code from 1 to 255.",
                 where, key, .shown(value)), call. = FALSE)
  }
  as.integer(code)
}

# Frames to milliseconds at a given refresh rate. Multiplication comes first so
# both engines evaluate the same two IEEE-754 operations on the same doubles:
# `frames * 1000 / hz`, never `frames * (1000 / hz)`, which is a different
# computation and agrees with the first only by accident of the divisor.
# Must stay identical to .frames_to_ms in python_workflow/src/lexsync/scripting.py.
#' @keywords internal
frames_to_ms <- function(frames, hz) {
  as.integer(round(as.numeric(frames) * 1000 / as.numeric(hz)))
}

# The refresh rate a design's frame counts were authored for. Only ever used to
# convert `*_frames` to milliseconds; it is not the rate the experiment runs at.
#' @keywords internal
.refresh_hz <- function(schema) {
  hz <- (schema[["presentation"]] %||% list())[["assumed_refresh_hz"]] %||% 60
  hz <- as.numeric(hz)
  if (!is.finite(hz) || hz <= 0) {
    stop("lexsync: presentation.assumed_refresh_hz must be a positive number.", call. = FALSE)
  }
  hz
}

# How long the onset code is held before it is reset to 0, in milliseconds.
#
# `reset_after_frames: N` is still accepted, but converting it needs care: the old
# implementation queued the reset on flip N and callOnFlip runs on the FOLLOWING
# flip, so the code was actually held for N + 1 flip intervals. Converting N
# directly would silently shorten every trigger by one frame, so the +1 is part of
# the compatibility contract, not an off-by-one.
# Must stay identical to _trigger_hold_ms in python_workflow/src/lexsync/scripting.py.
#' @keywords internal
.trigger_hold_ms <- function(schema) {
  triggers <- schema[["triggers"]] %||% list()
  if (!is.null(triggers[["trigger_hold_ms"]])) {
    ms <- as.numeric(triggers[["trigger_hold_ms"]])
  } else if (!is.null(triggers[["reset_after_frames"]])) {
    ms <- as.numeric(frames_to_ms(as.integer(triggers[["reset_after_frames"]]) + 1L,
                                  .refresh_hz(schema)))
  } else {
    ms <- 50
  }
  if (!is.finite(ms) || ms <= 0) {
    stop("lexsync: triggers.trigger_hold_ms must be a positive number.", call. = FALSE)
  }
  ms
}

# A duration as a number, or NA when the value is not one. A number is taken as it is,
# and so is text that is a plain decimal number, as a design that quotes a duration
# carries it and as a column holding some text is read. A logical value is not a
# duration. Must match _as_duration in scripting.py.
.as_duration <- function(value) {
  if (is.list(value) || length(value) != 1L || is.logical(value)) return(NA_real_)
  if (is.numeric(value)) return(as.numeric(value))
  if (is.character(value) && !is.na(value) && grepl(.PLAIN_NUMBER, value, perl = TRUE)) {
    return(as.numeric(value))
  }
  NA_real_
}

# A duration the design fixes, checked: a finite number, not negative. `what` names the
# value in the refusal, as in "event 2 has duration_ms" or "timing.word_ms is". A
# negative value reached the OpenSesame experiment as clock.sleep(-50), and a NaN as
# clock.sleep(NA). Must match _fixed_duration in scripting.py.
.fixed_duration <- function(value, what) {
  number <- .as_duration(value)
  if (is.na(number) || !is.finite(number) || number < 0) {
    stop(sprintf("lexsync: %s '%s'; a duration must be a finite number, not negative.",
                 what, .shown(value)), call. = FALSE)
  }
  number
}

# Resolve one event's duration to whole milliseconds. Milliseconds are canonical;
# a frame count is accepted for backward compatibility and converted at the
# design's assumed refresh rate. An explicit `duration_ms` wins over
# `duration_frames` if a design carries both. Either must be a finite number, not
# negative, or the event is refused, named by `index`, its place in the design counted
# from 1. A fractional `duration_ms` is rounded with .round_dp, as a duration read from
# the items is. as.integer() truncated it, so 33.7 ms was presented as 33. The
# overrides come from the design's `timing` block, which .render_each() has already
# checked. Must match _event_ms in scripting.py.
#' @keywords internal
.event_ms <- function(ev, override_ms, override_frames, hz, default_frames = 1L,
                      index = NULL) {
  where <- if (is.null(index)) "an event" else sprintf("event %d", as.integer(index))
  if (!is.null(override_ms)) return(as.integer(.round_dp(as.numeric(override_ms), 0)))
  if (!is.null(override_frames)) return(frames_to_ms(override_frames, hz))
  if (!is.null(ev[["duration_ms"]])) {
    ms <- .fixed_duration(ev[["duration_ms"]], paste(where, "has duration_ms"))
    return(as.integer(.round_dp(ms, 0)))
  }
  frames <- ev[["duration_frames"]]
  if (is.null(frames)) return(frames_to_ms(default_frames, hz))
  frames_to_ms(.fixed_duration(frames, paste(where, "has duration_frames")), hz)
}


# A design's per-event `duration:` block, if it declares one.
#   duration: {from_column: soa_ms}                  read per trial from the items
#   duration: {jitter: [400, 800], as: isi_ms}       drawn per trial from the hash
# A jitter's bounds must be finite numbers and the lower one not negative, since every
# value drawn between them is a duration. Must match _duration_spec in scripting.py.
#' @keywords internal
.duration_spec <- function(ev, index) {
  d <- ev[["duration"]]
  if (is.null(d) || !is.list(d)) return(NULL)
  if (!is.null(d[["from_column"]])) {
    return(list(column = as.character(d[["from_column"]]), jitter = NULL))
  }
  if (!is.null(d[["jitter"]])) {
    bounds <- d[["jitter"]]
    if (length(bounds) != 2L) {
      stop("lexsync: duration jitter must be a two-element range [lo, hi].", call. = FALSE)
    }
    num <- vapply(as.list(bounds), .as_duration, numeric(1))
    if (anyNA(num) || !all(is.finite(num)) || num[1] < 0) {
      stop(sprintf(paste("lexsync: event %d has jitter %s; a jittered duration needs finite",
                         "bounds, the lower one not negative."), index, .shown(bounds)),
           call. = FALSE)
    }
    return(list(column = as.character(d[["as"]] %||% sprintf("event%d_ms", index)),
                jitter = as.integer(num)))
  }
  stop("lexsync: a duration block needs either 'from_column' or 'jitter'.", call. = FALSE)
}

# An event's response keys, validated. OpenSesame writes them into
# `set allowed_responses "a;b"`, one line of a line-oriented format, so a key holding a
# quote closed the string and a newline ended the line -- and the rest became new
# top-level items in the experiment, including an inline_script whose body runs.
#' @keywords internal
.keys_of <- function(ev, default) {
  keys <- ev[["keys"]] %||% default
  vapply(as.character(unlist(keys)), clean_key, character(1), USE.NAMES = FALSE)
}

#' Realise per-trial event durations onto the stimuli table
#'
#' An event may declare a duration that varies from trial to trial, either read
#' from an item column or drawn from a range. A drawn value is a pure function of
#' the keyed hash, so both engines realise the same milliseconds, and it is
#' written into the stimuli table as well as the generated script, because timing
#' that varies is a variable the analysis needs, not presentation detail.
#'
#' Every value read from a column must be a finite number of milliseconds, not
#' negative. The first that is not, a blank cell included, is refused, naming the
#' column and the trial's set and condition. A blank or negative value used to reach
#' the experiments, where OpenSesame and PsychoPy stopped at the blank and jsPsych
#' ended the trial at once. When a column holds fractional milliseconds, each of its
#' values is rounded once with the rounder both engines share and written back, so the
#' stimuli, the loop tables and every target carry the same whole milliseconds. A
#' column of whole numbers is left as it is.
#'
#' @param stimuli A counterbalanced stimuli data frame.
#' @param design A parsed design configuration.
#' @param schema The parsed global schema (provides the seed).
#' @return `stimuli` with one integer column per jittered event, and every column of
#'   fractional milliseconds rounded. Each column rounded is recorded in the
#'   `"duration_rounding"` attribute, as one `list(event, column, n_rounded)` entry,
#'   which [run_pipeline()] writes into the run log.
#' @export
resolve_trial_timing <- function(stimuli, design, schema) {
  events <- resolve_events(design)
  seed <- schema[["seed"]] %||% 1L
  # A record carried in from an earlier call describes that call, not this one.
  attr(stimuli, "duration_rounding") <- NULL
  rounding <- list()
  for (i in seq_along(events)) {
    spec <- .duration_spec(events[[i]], i)
    if (is.null(spec)) next
    if (is.null(spec$jitter)) {
      # from_column reads a column the items already carry, so it is checked here.
      if (!(spec$column %in% names(stimuli))) {
        stop(sprintf("lexsync: event %d reads its duration from column '%s', which the items do not have.",
                     i, spec$column), call. = FALSE)
      }
      checked <- .column_durations(stimuli, i, spec$column)
      if (checked$n_rounded > 0L) {
        stimuli[[spec$column]] <- checked$values
        rounding[[length(rounding) + 1L]] <- list(event = i, column = spec$column,
                                                  n_rounded = checked$n_rounded)
      }
      next
    }
    # The key names the column as well as the trial, so two jittered events in
    # one design draw independently, where a key naming only the trial would give
    # them one shared value.
    key <- paste(.key_part(seed), "jitter", spec$column,
                 .key_part(stimuli$list %||% 1L), .key_part(stimuli$set),
                 .key_part(stimuli$condition), sep = "|")
    stimuli[[spec$column]] <- hash_int_range(key, spec$jitter[1], spec$jitter[2])
  }
  if (length(rounding)) attr(stimuli, "duration_rounding") <- rounding
  stimuli
}

# Check the durations event `index` reads from `column`, and round fractional ones.
# Returns list(values, n_rounded): the column's values as numbers, rounded with
# .round_dp, and how many of them the rounding changed. A value given as text is read as
# a number when it is a plain decimal one, so the refusal names the cell that is not.
# Must match _column_durations in scripting.py.
.column_durations <- function(stimuli, index, column) {
  x <- stimuli[[column]]
  values <- numeric(length(x))
  for (row in seq_along(x)) {
    value <- x[[row]]
    blank <- length(value) == 1L && !is.list(value) && is.na(value)
    number <- if (blank) NA_real_ else .as_duration(value)
    if (is.na(number) || !is.finite(number) || number < 0) {
      what <- if (blank) "is blank" else sprintf("holds '%s'", .shown(value))
      stop(sprintf(paste("lexsync: event %d reads its duration from column '%s', which %s for",
                         "%s; a duration must be a finite number of milliseconds, not",
                         "negative."), index, column, what, .trial_named(stimuli, row)),
           call. = FALSE)
    }
    values[row] <- number
  }
  list(values = .round_dp(values, 0), n_rounded = sum(values != trunc(values)))
}

# A trial as a refusal names it: its set and condition, and its block when the trials
# carry one, or else its row, counted from 1. Must match _trial_named in scripting.py.
.trial_named <- function(stimuli, row) {
  if (!all(c("set", "condition") %in% names(stimuli))) return(sprintf("row %d", row))
  named <- sprintf("set %s in condition '%s'", .shown(stimuli[["set"]][[row]]),
                   .shown(stimuli[["condition"]][[row]]))
  if ("block" %in% names(stimuli)) {
    named <- paste0(named, sprintf(" of block '%s'", .shown(stimuli[["block"]][[row]])))
  }
  named
}

#' Translate paradigm events into backend-neutral rendering dictionaries
#'
#' Durations are emitted as whole milliseconds (`ms`), the unit every backend
#' consumes: OpenSesame and jsPsych schedule it directly, and the PsychoPy script
#' converts it back into whole flips against the refresh rate it measures at
#' start-up.
#'
#' A response collected from the onset of the text event before it (see
#' `.response_from()`) is rendered with that event, as its `respond` entry (`keys`
#' and `timeout`). The text keeps `ms` as its longest display time, and the window
#' runs from its onset for `ms` plus the timeout, so the total window is the one the
#' two events had. A response collected from the offset stays an event of its own.
#' Keys are rendered as lists, which jsonlite writes as arrays even for one key.
#' @keywords internal
render_events <- function(events, timing, hz = 60) {
  rendered <- .render_each(events, timing, hz)
  out <- list()
  for (i in seq_along(events)) {
    r <- rendered[[i]]
    if (identical(r[["type"]], "response") && identical(.response_from(events, i), "onset")) {
      text <- out[[length(out)]]
      # The merged event runs where the text runs, so a response restricted to other
      # blocks than its stimulus has no window to open.
      if (!identical(unlist(r[["blocks"]]), unlist(text[["blocks"]]))) {
        stop(sprintf(paste("lexsync: event %d collects its response from the onset of event",
                           "%d, so the two must run in the same blocks; give them the same",
                           "`blocks`, or use from: offset."), i, i - 1L), call. = FALSE)
      }
      text$respond <- list(keys = r[["keys"]], timeout = r[["timeout"]])
      out[[length(out)]] <- text
      next
    }
    out[[length(out) + 1L]] <- r
  }
  out
}

# Where response event `i`, counted from 1, opens its window: "onset" or "offset".
# From "onset", the window opens with the text event just before the response, so a
# key pressed while that stimulus is on screen counts and the reaction time runs from
# its onset. From "offset", it opens when the stimulus has gone, for a design that asks
# the participant to wait. A design says which with `from:`, and without it a response
# after a text event is collected from the onset and any other from the offset, so a
# response after a blank keeps the window it had. Must match _response_from in
# scripting.py.
.response_from <- function(events, i) {
  ev <- events[[i]]
  prev <- if (i > 1L) events[[i - 1L]] else NULL
  after_text <- !is.null(prev) && identical(prev[["type"]], "text")
  given <- ev[["from"]]
  if (is.null(given)) return(if (after_text) "onset" else "offset")
  if (!is.character(given) || length(given) != 1L || !(given %in% c("onset", "offset"))) {
    stop(sprintf(paste("lexsync: event %d gives `from: %s`, but a response event takes",
                       "from: onset or from: offset."), i, .shown(given)), call. = FALSE)
  }
  if (identical(given, "onset") && !after_text) {
    what <- if (is.null(prev)) "no event precedes it" else
      sprintf("event %d is a %s", i - 1L, .shown(prev[["type"]]))
    stop(sprintf(paste("lexsync: event %d collects its response from the onset of the",
                       "preceding stimulus, but %s; use from: offset."), i, what),
         call. = FALSE)
  }
  given
}

# A rendered timeout, in seconds, as the whole milliseconds the design declared.
# Rounded through .round_dp. as.integer() truncated 1.001 * 1000, which is
# 1000.9999999999999 in binary floating point, so a declared 1,001 ms was written as
# 1,000, and 95 of the whole-millisecond values from 1 to 10,000 came out one short.
# Must match _whole_ms in scripting.py.
.whole_ms <- function(seconds) as.integer(.round_dp(as.numeric(seconds) * 1000, 0))

# Each response event's window, as the datasheet records it: one list(event, from,
# window_ms) per response event, where `event` counts the design's events from 1. A
# window from the onset runs for the stimulus's duration and the timeout, and one from
# the offset for the timeout. When the stimulus's duration varies by trial, window_ms is
# NA (null in the JSON record) and the entry adds the duration_column and the timeout_ms
# that make it up. Whole milliseconds, as every target writes them. Mirrors
# _response_windows in scripting.py.
.response_windows <- function(events, timing, hz) {
  rendered <- .render_each(events, timing, hz)
  out <- list()
  for (i in seq_along(rendered)) {
    r <- rendered[[i]]
    if (!identical(r[["type"]], "response")) next
    start <- .response_from(events, i)
    timeout_ms <- .whole_ms(r[["timeout"]])
    entry <- list(event = i, from = start)
    stimulus <- if (identical(start, "onset")) rendered[[i - 1L]] else NULL
    if (is.null(stimulus)) {
      entry$window_ms <- timeout_ms
    } else if (!is.null(stimulus[["ms_column"]])) {
      entry <- c(entry, list(window_ms = NA_integer_,
                             duration_column = stimulus[["ms_column"]],
                             timeout_ms = timeout_ms))
    } else {
      entry$window_ms <- as.integer(stimulus[["ms"]]) + timeout_ms
    }
    out[[length(out) + 1L]] <- entry
  }
  out
}

# Each event rendered on its own, before a response joins its stimulus.
.render_each <- function(events, timing, hz) {
  timing <- timing %||% list()
  # A design's timing block was previously read key by key, so a typo such as
  # `fixation_frame` was silently ignored and the event kept a default duration.
  # Reject an unknown key instead: a mistimed experiment is not recoverable after
  # the data are collected. Must list the same names as scripting.py.
  known <- c("fixation_ms", "word_ms", "isi_ms",
             "fixation_frames", "word_frames", "isi_frames")
  unknown <- setdiff(names(timing), known)
  if (length(unknown)) {
    stop(sprintf("lexsync: unknown timing key(s) %s. Known keys: %s.",
                 paste(sprintf("'%s'", sort(unknown)), collapse = ", "),
                 paste(known, collapse = ", ")), call. = FALSE)
  }
  # Each value of the block is a fixed duration, checked as an event's own is, in the
  # order of `known` so that both engines name the same key first.
  checked <- list()
  for (key in known) {
    if (!is.null(timing[[key]])) {
      checked[[key]] <- .fixed_duration(timing[[key]], sprintf("timing.%s is", key))
    }
  }
  fix_ms <- checked[["fixation_ms"]];  fix <- checked[["fixation_frames"]]
  word_ms <- checked[["word_ms"]];    word <- checked[["word_frames"]]
  isi_ms <- checked[["isi_ms"]];      isi <- checked[["isi_frames"]]
  out <- list()
  # A feedback event scores the key the participant pressed, so something must have
  # collected one first. With no preceding response or question the OpenSesame runner
  # raises on the unset variable, PsychoPy compares against None and jsPsych finds no
  # scored row -- three different confusing failures at run time, for one design error
  # that is obvious here.
  seen_response <- FALSE
  for (i in seq_along(events)) {
    ty <- events[[i]][["type"]]
    if (ty %in% c("response", "question")) seen_response <- TRUE
    if (identical(ty, "feedback") && !seen_response) {
      stop(sprintf(paste("lexsync: event %d is a feedback event, but no response or",
                         "question event precedes it, so there is no response to score."),
                   i), call. = FALSE)
    }
  }
  for (i in seq_along(events)) {
    ev <- events[[i]]
    t <- ev[["type"]]
    r <- list(type = if (identical(t, "region_by_region")) "region" else t)
    if (t %in% c("fixation", "text", "mask")) {
      f <- content_field(ev[["content"]])
      if (!is.null(f)) r$field <- f else r$text <- as.character(ev[["content"]] %||% "")
      # The overrides are type-keyed, as before: `fixation_*` reaches every
      # fixation and `word_*` only a text event whose trigger is "condition",
      # which is why a priming prime (trigger 20) keeps its own duration.
      is_word <- t == "text" && identical(ev[["trigger"]], "condition")
      spec <- .duration_spec(ev, i)
      if (!is.null(spec)) {
        r$ms_column <- spec$column
      } else {
        r$ms <- .event_ms(
          ev,
          if (t == "fixation") fix_ms else if (is_word) word_ms else NULL,
          if (t == "fixation") fix else if (is_word) word else NULL,
          hz, index = i
        )
      }
      spec <- trigger_spec(ev[["trigger"]], i)
      if (!is.null(spec)) r$trigger <- spec
    } else if (t == "blank") {
      spec <- .duration_spec(ev, i)
      if (!is.null(spec)) {
        r$ms_column <- spec$column
      } else {
        r$ms <- .event_ms(ev, isi_ms, isi, hz, index = i)
      }
    } else if (t == "region_by_region") {
      r$field <- content_field(ev[["content"]])
      r$sep <- ev[["sep"]] %||% "|"
      r$key <- ev[["advance"]] %||% "space"
      spec <- trigger_spec(ev[["critical_region_trigger"]], i, "critical_region_trigger")
      if (!is.null(spec)) r$crit_trigger <- spec
    } else if (t == "response") {
      # A list, which jsonlite writes as an array even for one key, as the Python
      # engine writes it. A character vector of one became a bare string, and the
      # PsychoPy runner then split "space" into five one-letter keys.
      r$keys <- as.list(.keys_of(ev, c("left", "right")))
      # .round_dp, not round(): the timeout is written into experiment files both
      # engines emit as the same bytes, and the two languages' own rounders
      # disagree on 3-dp halfway cases (see .round_dp in io_utils.R).
      r$timeout <- .round_dp((ev[["timeout_ms"]] %||% 2000) / 1000, 3)
    } else if (t == "question") {
      r$field <- content_field(ev[["content"]])
      r$keys <- as.list(.keys_of(ev, c("f", "j")))
      r$timeout <- .round_dp((ev[["timeout_ms"]] %||% 5000) / 1000, 3)
    } else if (t == "feedback") {
      # Feedback compares the key the participant pressed against the key the item says
      # is correct, so `answer` names a loop-table column holding a KEY, not a label:
      # the runner then needs no mapping table and no notion of what the keys mean.
      r$answer <- as.character(ev[["answer"]] %||% "answer")
      r$correct <- as.character(ev[["correct"]] %||% "Correct")
      r$incorrect <- as.character(ev[["incorrect"]] %||% "Incorrect")
      r$no_response <- as.character(ev[["no_response"]] %||% "Too slow")
      r$ms <- .event_ms(ev, NULL, NULL, hz, default_frames = 36L, index = i)
    } else {
      stop(sprintf("lexsync: unknown event type '%s'.", t), call. = FALSE)
    }
    # An event may be restricted to named blocks. This is what lets feedback run during
    # practice and nowhere else: the event list is global to the design, so the
    # restriction has to travel with the event and be applied per trial at run time.
    # Generating a second event list would be the alternative, and a worse one.
    if (!is.null(ev[["blocks"]])) {
      r$blocks <- as.list(as.character(unlist(ev[["blocks"]], use.names = FALSE)))
    }
    out[[length(out) + 1L]] <- r
  }
  out
}

# The per-trial duration columns an event list reads, in event order.
.ms_columns <- function(events) {
  cols <- character(0)
  for (i in seq_along(events)) {
    s <- .duration_spec(events[[i]], i)
    if (!is.null(s) && !(s$column %in% cols)) cols <- c(cols, s$column)
  }
  cols
}

#' Per-trial table carrying exactly the fields the events reference
#'
#' The rows are in presentation order within each version: by replicate when the
#' table has one, then by list, then by trial. `trial` restarts at 1 in every list
#' and in every replicate, so ordering on it alone interleaved the versions. The
#' sort is stable, so rows that tie keep their incoming order and the two engines
#' write the same table.
#' @keywords internal
loop_table <- function(stimuli, events = NULL) {
  fields <- if (!is.null(events)) referenced_fields(events) else
    (if ("word" %in% names(stimuli)) "word" else character(0))
  # A per-trial duration is read from the loop table at run time, so its column
  # has to travel with the trials, and cannot stay behind in the stimuli file.
  ms_cols <- .ms_columns(events)
  # `block` travels with the trials because the runners need it: it is what an
  # event's `blocks:` restriction is matched against, and what a runner watches to
  # know a block boundary has been reached. Absent unless the design declares a
  # practice or filler block, so no existing loop table gains a column. `replicate`,
  # present only in a resampled design, is what tells its item samples apart, since
  # each is numbered from trial 1 and set 1.
  order_cols <- c("trial", "list", "replicate", "block", "set", "condition", fields,
                  ms_cols, "critical_region", "answer", "condition_trigger", "item_trigger")
  cols <- character(0)
  for (c in order_cols) if (c %in% names(stimuli) && !(c %in% cols)) cols <- c(cols, c)
  tab <- stimuli[, cols, drop = FALSE]
  keys <- intersect(c("replicate", "list", "trial"), names(tab))
  if (length(keys)) {
    tab <- tab[do.call(order, c(unname(as.list(tab[keys])), list(method = "radix"))), ,
               drop = FALSE]
  }
  rownames(tab) <- NULL
  tab
}

# Each row's replicate or list, as a whole number. A table without the column is one
# replicate, or one list, numbered 1, and so is a row that leaves it empty. Any other
# value that is not a whole number is refused, because a version is numbered by those
# whole numbers in order. A number is judged by its value, since as.character() keeps
# only 15 significant digits, and text only when it is a plain decimal number
# (.PLAIN_NUMBER): as.numeric() alone also takes "0x10", and Python's float() takes
# "1_0". A refused number is shown to 17 significant digits. Mirrors _version_key in
# scripting.py.
.version_key <- function(stimuli, column) {
  n <- nrow(stimuli)
  if (!column %in% names(stimuli)) return(rep(1L, n))
  x <- stimuli[[column]]
  if (is.numeric(x)) {
    number <- as.numeric(x)
    missing <- is.na(number)
    shown <- sprintf("%.17g", number)
  } else {
    shown <- trimws(as.character(x))
    missing <- is.na(shown) | !nzchar(shown)
    plain <- !missing & grepl(.PLAIN_NUMBER, shown, perl = TRUE)
    number <- rep(NA_real_, n)
    number[plain] <- as.numeric(shown[plain])
  }
  bad <- !missing & !(is.finite(number) & number == trunc(number))
  if (any(bad)) {
    stop(sprintf(paste("lexsync: the trials' `%s` column holds '%s', but a presentation",
                       "version is numbered by whole-number lists and replicates."),
                 column, shown[bad][1]), call. = FALSE)
  }
  out <- rep(1L, n)
  out[!missing] <- as.integer(number[!missing])
  out
}

# The presentation versions a set of trials holds, in the order they are numbered. A
# version is one (replicate, list) pair of the trials, and each participant is
# presented one version: version 1 is the first pair in (replicate, list) order,
# version 2 the next, and so on. A table without a `replicate` column is one replicate,
# numbered 1, and one without `list` is one list. Participant p runs version
# ((p - 1) mod V) + 1 of V unless another is chosen at launch, the rule
# participant_table() allocates by. Every generated experiment carries this list, and
# export_opensesame() writes one experiment per version when there is more than one.
# Returns a list of list(version, replicate, list, n_trials). Mirrors
# presentation_versions in scripting.py.
.presentation_versions <- function(stimuli) {
  reps <- .version_key(stimuli, "replicate")
  lists <- .version_key(stimuli, "list")
  if (!length(reps)) return(list())
  key <- unique(data.frame(replicate = reps, list = lists))
  key <- key[order(key$replicate, key$list, method = "radix"), , drop = FALSE]
  lapply(seq_len(nrow(key)), function(i) {
    list(version = i, replicate = key$replicate[i], list = key$list[i],
         n_trials = sum(reps == key$replicate[i] & lists == key$list[i]))
  })
}

# The rows of one presentation version, in their incoming order.
.version_rows <- function(stimuli, version) {
  keep <- .version_key(stimuli, "replicate") == version[["replicate"]] &
    .version_key(stimuli, "list") == version[["list"]]
  out <- stimuli[keep, , drop = FALSE]
  rownames(out) <- NULL
  out
}

# Whether the versions come from more than one replicate. A list then names no single
# version, so file names and launch options name the replicate as well.
.spans_replicates <- function(versions) {
  length(unique(vapply(versions, function(v) v[["replicate"]], integer(1)))) > 1L
}

# The loop-table columns the OpenSesame target carries as numbers, under the names its
# loop table gives them. OpenSesame evaluates every cell of a loop table. In 4.x, a cell
# holding a single `{` runs as a Python f-string, and in 3.3 a cell starting with `=` or
# holding `[=...]` runs as Python. Both versions retype a cell such as 'nan' or '007'.
# That loop table therefore holds numbers only, and the presented text travels in a
# companion table that the inline scripts read with the csv module. OpenSesame 4 also
# makes every loop column a global of the inline scripts, where `list` and `set` would
# shadow Python's builtins, so those two are renamed and `trial` with them. Must match
# _OS_NUMERIC in scripting.py.
.OS_NUMERIC <- c(trial = "lexsync_trial", list = "lexsync_list", replicate = "replicate",
                 set = "lexsync_set", critical_region = "critical_region",
                 condition_trigger = "condition_trigger", item_trigger = "item_trigger")
# A plain decimal number, which both OpenSesame versions store and read back as written.
# \z and not $, for the reason given beside .PORT_SHAPE in io_utils.R.
.PLAIN_NUMBER <- "^-?[0-9]+(\\.[0-9]+)?\\z"

# Refuse a numeric loop column holding anything but plain numbers and empty cells. The
# cells are checked as write_csv_utf8() renders them, so the check sees the bytes
# OpenSesame will read, and refuses exactly what the Python twin refuses.
.check_opensesame_numbers <- function(x, col) {
  one <- data.frame(x = x, stringsAsFactors = FALSE)
  .check_csv_writable(one)
  cells <- utils::read.csv(text = readr::format_csv(one, na = ""), colClasses = "character",
                           na.strings = character(0), quote = "\"", encoding = "UTF-8")$x
  bad <- which(nzchar(cells) & !grepl(.PLAIN_NUMBER, cells, perl = TRUE))
  if (length(bad)) {
    stop(sprintf(paste("lexsync: column '%s' holds '%s', and the OpenSesame loop table",
                       "holds numbers only, because OpenSesame evaluates the cells of a",
                       "loop table."), col, cells[bad[1]]), call. = FALSE)
  }
  invisible(x)
}

# The OpenSesame target's loop table and its companion text table. Both are the loop
# table, split by column and joined by `lexsync_row`, the trial's position in loop order
# (1..N). The loop table holds `lexsync_row` and the numeric columns of .OS_NUMERIC plus
# any per-trial duration. The text table holds `lexsync_row`, every presented field and
# every other column (`condition`, `block`, `answer`). A presented field that is also
# numeric goes to both. An empty numeric cell passes, since OpenSesame leaves it alone
# and a filler sentence may have no critical region. Must match _opensesame_tables in
# scripting.py.
.opensesame_tables <- function(stimuli, events) {
  tab <- loop_table(stimuli, events)
  presented <- referenced_fields(events)
  numeric <- c(names(.OS_NUMERIC), .ms_columns(events))
  rows <- seq_len(nrow(tab))
  numbers <- data.frame(lexsync_row = rows)
  text <- data.frame(lexsync_row = rows)
  for (col in names(tab)) {
    if (col %in% numeric) {
      .check_opensesame_numbers(tab[[col]], col)
      renamed <- if (col %in% names(.OS_NUMERIC)) .OS_NUMERIC[[col]] else col
      numbers[[renamed]] <- tab[[col]]
    }
    if (col %in% presented || !(col %in% numeric)) text[[col]] <- tab[[col]]
  }
  list(numbers = numbers, text = text)
}

#' Export a runnable PsychoPy script that interprets the event sequence
#'
#' The conditions file, `<base>_psychopy.csv`, holds every presentation version of
#' the design, one per (replicate, list) pair, and the script presents one per run:
#' the version given by `--version` (or `--list` when there are no replicates), else
#' the participant's by the rule `((participant - 1) mod V) + 1` from
#' `--participant`, else what a start-up dialogue asks for. A version the script does
#' not have stops the run with a message.
#'
#' Each run writes `data/<base>_p<participant>_v<version>_<date>-<time>.csv` beside
#' the script, without the `_p` part when no participant number is given, one row per
#' trial, each written as its trial ends. A row holds the run, the trial's fields and
#' trigger codes, the response and its reaction time from the onset of the stimulus it
#' answers, whether the window closed without one, whether the key was the trial's
#' `answer`, the self-paced reading times, the question's response and reaction time,
#' the measured refresh rate, and each event's realised flips and onset.
#'
#' @param stimuli Stimuli with trigger columns (see [assign_triggers()]).
#' @param design A parsed design configuration.
#' @param schema The parsed global schema (trigger and presentation settings).
#' @param outdir Output directory.
#' @param base Optional file-name stem. By default the design's [design_stem()].
#' @return The path to the generated `.py`, invisibly.
#' @importFrom jsonlite toJSON
#' @export
export_psychopy <- function(stimuli, design, schema, outdir, base = NULL) {
  invisible(.psychopy_files(stimuli, design, schema, outdir, base)[[1]])
}

# Write the PsychoPy script and its conditions file, and return both paths.
.psychopy_files <- function(stimuli, design, schema, outdir, base = NULL) {
  base <- base %||% design_stem(design)
  events <- resolve_events(design)
  rendered <- render_events(events, design[["timing"]] %||% list(), .refresh_hz(schema))
  versions <- .presentation_versions(stimuli)
  csv_name <- paste0(base, "_psychopy.csv")
  write_csv_utf8(loop_table(stimuli, events), file.path(outdir, csv_name))
  tmpl <- paste(readLines(find_template("psychopy/trial_runner_template.py"), warn = FALSE),
                collapse = "\n")
  triggers <- schema[["triggers"]] %||% list()
  presentation <- schema[["presentation"]] %||% list()
  subs <- list(
    DESIGN = clean_meta(design[["name"]], "the design's `name`"),
    LANGUAGE = clean_meta(design[["language"]], "the design's `language`"),
    CONDITIONS_FILE = csv_name,
    # The data files are named after the experiment, as data/<base>_p<n>_v<k>_...
    BASE = base,
    TRIGGER_ADDRESS = clean_port(triggers[["parallel_address"]] %||% "0x0378"),
    TRIGGER_HOLD_MS = sprintf("%.17g", .trigger_hold_ms(schema)),
    # Through %.17g like its neighbours, never default stringification: R's
    # as.character() and Python's str() part company on a non-integer quotient
    # (as.character(16.65 / 1000) gives "0.01665", str gives
    # "0.016649999999999998"), and this value lands in the generated script.
    INTER_TRIGGER_S = sprintf("%.17g", (triggers[["inter_trigger_ms"]] %||% 10) / 1000),
    WORD_FONT = clean_meta(design[["font"]] %||% presentation[["font"]] %||% "Courier New",
                           "the font"),
    FULLSCREEN = "False",
    # The fallback used only when the script cannot measure the display.
    ASSUMED_REFRESH_HZ = sprintf("%.17g", .refresh_hz(schema)),
    EVENTS_JSON = as.character(jsonlite::toJSON(rendered, auto_unbox = TRUE)),
    VERSIONS_JSON = as.character(jsonlite::toJSON(versions, auto_unbox = TRUE))
  )
  for (k in names(subs)) {
    tmpl <- gsub(sprintf("{{%s}}", k), as.character(subs[[k]]), tmpl, fixed = TRUE)
  }
  out <- file.path(outdir, paste0(base, "_psychopy.py"))
  write_lines_lf(tmpl, out)
  c(out, file.path(outdir, csv_name))
}

# ---- OpenSesame code generation ------------------------------------------

.pyq <- function(s) {
  # A newline had to be escaped as well as the backslash and the quote. An .osexp is a
  # line-oriented format whose inline scripts are delimited by their own lines, so a raw
  # newline in a value did not merely break the literal: it closed the script block and
  # let the rest of the value start a new top-level item in the emitted experiment.
  s <- gsub("\\", "\\\\", s, fixed = TRUE)
  s <- gsub("'", "\\'", s, fixed = TRUE)
  s <- gsub("\n", "\\n", s, fixed = TRUE)
  s <- gsub("\r", "\\r", s, fixed = TRUE)
  s <- gsub("\t", "\\t", s, fixed = TRUE)
  paste0("u'", s, "'")
}

# A trial's text for `field`, from its row of the companion table.
.text_expr <- function(field) sprintf("_lexsync_row()[%s]", .pyq(field))

# A trial's value of a numeric loop column, read without evaluation.
.number_expr <- function(column) sprintf("int(var.get(%s, _eval=False))", .pyq(column))

.content_expr <- function(ev) {
  if (!is.null(ev[["field"]])) .text_expr(ev[["field"]]) else .pyq(ev[["text"]] %||% "")
}

.trigger_expr <- function(spec) {
  if (is.null(spec)) return(NULL)
  if (is.character(spec) && startsWith(spec, "@")) return(.number_expr(substring(spec, 2)))
  as.character(as.integer(spec))
}

.inline_block <- function(name, desc, body) {
  c(sprintf("define inline_script %s", name),
    sprintf('\tset description "%s"', desc),
    '\tset _prepare ""', "\t___run__", paste0("\t", body), "\t__end__", "")
}

# The Python that OpenSesame's inline_script actually runs.
#
# Two spellings here are forced by OpenSesame's runtime and were both wrong at first:
#
# `str`, never `unicode`. OpenSesame 3.3 and later run inline scripts in a Python 3
# workspace and inject only a fixed set of globals (exp, var, pool, items, clock, log
# and a small API); `unicode` is a Python 2 builtin and is not among them, so every
# emitted guard and feedback script died with NameError on the first trial.
#
# `var.get(name, u'')`, never `var.get(name, None)`. OpenSesame's var_store.get ends
# `elif default is not None: val = default / else: raise VariableDoesNotExist(var)`, so
# passing None explicitly is indistinguishable from passing no default and RAISES rather
# than yielding None. A non-None sentinel is the only default that works.
#
# And no text from `var` at all. OpenSesame evaluates a loop cell when the loop sets it
# and again when a script reads it. The presented text, the block and the answer
# therefore come from the trial's row of the companion table (`_lexsync_row()`, defined
# by the setup script). What is still read from `var`, the numeric loop columns and the
# response, is read with `_eval=False`: an evaluated read in 4.x turns a timed-out
# response, stored as None, into the string 'None'.

# Restrict an inline script's body to the named blocks.
#
# The guard goes INSIDE the script rather than on the sequence's `run` line. OpenSesame
# does support a run condition, but its syntax and quoting could not be verified here
# without the application, and an emitter that generates an experiment nobody can open is
# worse than one that generates a slightly longer script.
#' @keywords internal
.osexp_block_guard <- function(body, blocks) {
  if (is.null(blocks) || !length(blocks)) return(body)
  wanted <- paste(vapply(as.character(unlist(blocks)), .pyq, character(1)), collapse = ", ")
  c(sprintf("if _lexsync_row().get(u'block', u'main') in [%s]:", wanted),
    paste0("    ", body))
}

# Lines that score the key held in `key` against the trial's `answer`: var.correct
# becomes 1 or 0, or stays empty when the trial names no answer. Computed here, not by
# OpenSesame's correct_response, whose variable syntax differs between 3.3 ([answer])
# and 4.x ({answer}), and whose answer would have to come from the variable store,
# which evaluates text. Must match _osexp_correct in scripting.py.
.osexp_correct <- function(key) {
  c("_want = str(_lexsync_row().get(u'answer', u'')).strip()",
    sprintf("_got = u'' if %s is None else str(%s).strip()", key, key),
    "var.correct = (1 if _got == _want else 0) if _want else u''")
}

# One rendered event's lines and run names. `scores` says whether a response or
# question this event collects is the one var.correct scores: the design's response
# events, or its questions when it has no response event. `feedback_scores` names the
# variable a feedback event reads, "response" or "question_response", after whichever
# collected a key last. Must match _osexp_event_block in scripting.py.
.osexp_event_block <- function(name, ev, scores = TRUE, feedback_scores = "response") {
  t <- ev[["type"]]
  blocks <- ev[["blocks"]]
  if (!is.null(blocks) && length(blocks) && t == "response") {
    # A keyboard_response is not an inline script, so the guard above cannot reach it.
    # Saying so beats emitting an experiment that ignores the restriction.
    stop(paste("lexsync: a `response` event cannot be restricted to blocks on the",
               "OpenSesame target. Restrict a feedback or stimulus event instead."),
         call. = FALSE)
  }
  # A fixed duration is a literal; one that varies per trial reads the loop-table
  # column, which OpenSesame exposes on `var`. Must match _osexp_event_block in
  # scripting.py, since the two engines write the same .osexp.
  # [[ ]], not $: `$` partial-matches on a list, so `ev$ms` would return the value
  # of `ms_column` for a per-trial duration and emit the column name as a literal.
  sleep_arg <- if (!is.null(ev[["ms_column"]]))
    sprintf("int(float(var.get(%s, _eval=False)))",
            .pyq(clean_column(ev[["ms_column"]], "a jittered duration's `as`"))) else
    sprintf("%d", as.integer(ev[["ms"]] %||% 0L))
  if (identical(t, "text") && !is.null(ev[["respond"]])) {
    # The stimulus collects its own response, from its onset. The keyboard is flushed
    # once the trigger is out, so nothing pressed before the stimulus counts, and polled
    # while the stimulus is shown. Without a key by its end, the screen blanks and the
    # keyboard is polled for the timeout, so the window is the one the stimulus and a
    # separate response event had. A key ends the event either way.
    respond <- ev[["respond"]]
    keylist <- paste(vapply(unlist(respond[["keys"]]), .pyq, character(1)), collapse = ", ")
    body <- c("c = Canvas()", sprintf("c.text(%s)", .content_expr(ev)), "_t0 = c.show()",
              "var.onset_time = _t0")
    trig <- .trigger_expr(ev[["trigger"]])
    if (!is.null(trig)) body <- c(body, sprintf("send_trigger(%s)", trig))
    body <- c(body,
              sprintf("_kb = Keyboard(keylist=[%s])", keylist),
              "_kb.flush()",
              sprintf("_key, _t = _kb.get_key(timeout=%s)", sleep_arg),
              "if _key is None:",
              "    c = Canvas()",
              "    c.show()",
              sprintf("    _key, _t = _kb.get_key(timeout=%d)", .whole_ms(respond[["timeout"]])),
              "var.response = _key",
              "var.response_time = u'' if _key is None else _t - _t0",
              "var.timed_out = 1 if _key is None else 0")
    if (isTRUE(scores)) body <- c(body, .osexp_correct("_key"))
    return(list(block = .inline_block(name, paste("Show the stimulus and collect the",
                                                  "response from its onset"),
                                      .osexp_block_guard(body, blocks)),
                run = name))
  }
  if (t %in% c("fixation", "text", "mask", "blank")) {
    body <- "c = Canvas()"
    if (t != "blank") body <- c(body, sprintf("c.text(%s)", .content_expr(ev)))
    body <- c(body, "var.onset_time = c.show()")
    trig <- .trigger_expr(ev[["trigger"]])
    if (!is.null(trig)) body <- c(body, sprintf("send_trigger(%s)", trig))
    body <- c(body, sprintf("clock.sleep(%s)", sleep_arg))
    return(list(block = .inline_block(name, "Show stimulus and send onset-aligned trigger",
                                      .osexp_block_guard(body, blocks)),
                run = name))
  }
  if (t == "region") {
    trig <- .trigger_expr(ev[["crit_trigger"]])
    # Each region is timed from its own onset, and the keyboard is flushed as it
    # appears, so a key pressed before it cannot advance it.
    body <- c(
      sprintf("_regions = [r for r in %s.split(%s) if r != u'']", .text_expr(ev[["field"]]),
              .pyq(ev[["sep"]] %||% "|")),
      # An empty cell, a sentence with no critical region, reads as 0: no trigger.
      "_crit = int(var.get(u'critical_region', 0, _eval=False) or 0)",
      sprintf("_kb = Keyboard(keylist=[%s], timeout=None)", .pyq(ev[["key"]] %||% "space")),
      "_rts = []",
      "for _i, _region in enumerate(_regions, start=1):",
      "    c = Canvas(); c.text(_region); _t0 = c.show()")
    if (!is.null(trig)) body <- c(body, sprintf("    if _i == _crit: send_trigger(%s)", trig))
    body <- c(body, "    _kb.flush()", "    _key, _t = _kb.get_key()",
              "    _rts.append(u'%.1f' % (_t - _t0))",
              "var.lexsync_region_rts = u'|'.join(_rts)")
    return(list(block = .inline_block(name, "Self-paced reading region by region",
                                      .osexp_block_guard(body, blocks)), run = name))
  }
  if (t == "question") {
    keys_list <- paste(vapply(unlist(ev[["keys"]] %||% c("f", "j")), .pyq, character(1)),
                       collapse = ", ")
    body <- c(
      sprintf("c = Canvas(); c.text(%s); _t0 = c.show()", .text_expr(ev[["field"]])),
      sprintf("_kb = Keyboard(keylist=[%s], timeout=%d)", keys_list,
              .whole_ms(ev[["timeout"]] %||% 5)),
      "_kb.flush()",
      "_key, _t = _kb.get_key()",
      "var.question_response = _key",
      "var.question_rt = u'' if _key is None else _t - _t0")
    if (isTRUE(scores)) body <- c(body, .osexp_correct("_key"))
    return(list(block = .inline_block(name, "Comprehension question",
                                      .osexp_block_guard(body, blocks)), run = name))
  }
  if (t == "feedback") {
    # The key comes from whichever response or question collected one last. The answer
    # column (or whichever column the event names) holds the KEY that is correct, so
    # scoring is a string comparison. A timeout is reported separately, because on a
    # timed task it means something different from a wrong key. OpenSesame 4.x stores it
    # as None and 3.3 as the string 'None', so both count as no response.
    body <- c(
      sprintf("_want = str(_lexsync_row().get(u'%s', u'')).strip()",
              clean_column(ev[["answer"]] %||% "answer", "a feedback event's `answer`")),
      sprintf("_got = var.get(u'%s', u'', _eval=False)", feedback_scores),
      "_got = u'' if _got is None else str(_got).strip()",
      sprintf("if _got in (u'', u'None'): _msg = %s", .pyq(ev[["no_response"]] %||% "Too slow")),
      sprintf("elif _got == _want: _msg = %s", .pyq(ev[["correct"]] %||% "Correct")),
      sprintf("else: _msg = %s", .pyq(ev[["incorrect"]] %||% "Incorrect")),
      "c = Canvas(); c.text(_msg); c.show()",
      sprintf("clock.sleep(%s)", sleep_arg))
    return(list(block = .inline_block(name, "Practice feedback",
                                      .osexp_block_guard(body, blocks)), run = name))
  }
  if (t == "response") {
    keys <- paste(unlist(ev[["keys"]] %||% c("left", "right")), collapse = ";")
    # A keyboard_response draws nothing, so the preceding canvas would stay up for
    # the whole response window. Blank it first, so the stimulus offsets at its own
    # duration as it does in the PsychoPy and jsPsych targets.
    block <- c(
      .inline_block(sprintf("%s_blank", name), "Clear the screen for the response window",
                    c("c = Canvas()", "c.show()")),
      sprintf("define keyboard_response %s", name),
      paste0("\tset timeout ", .whole_ms(ev[["timeout"]] %||% 2)),
      "\tset flush yes", "\tset duration keypress",
      '\tset description "Collect a response"',
      sprintf('\tset allowed_responses "%s"', keys), "")
    # The keyboard_response records the key and its time from the window's onset.
    # Whether it timed out, and whether the key was the trial's answer, are recorded
    # here, as the onset-locked script records them.
    score <- c("_key = var.get(u'response', u'', _eval=False)",
               "_timed_out = _key is None or str(_key).strip() in (u'', u'None')",
               "var.timed_out = 1 if _timed_out else 0",
               "if _timed_out:",
               "    _key = None",
               "    var.response_time = u''")
    if (isTRUE(scores)) score <- c(score, .osexp_correct("_key"))
    block <- c(block, .inline_block(sprintf("%s_score", name),
                                    "Record the timeout and the accuracy", score))
    return(list(block = block, run = c(sprintf("%s_blank", name), name,
                                       sprintf("%s_score", name))))
  }
  stop(sprintf("lexsync: unknown event type '%s'.", t), call. = FALSE)
}

# The inline script that opens every trial by clearing what the last one recorded.
# OpenSesame keeps a variable from one trial to the next, so a response event that does
# not run in a block would otherwise leave the previous trial's key in the log and for
# the feedback. Must match _osexp_trial_start in scripting.py.
.osexp_trial_start <- function() {
  vars <- c("response", "response_time", "timed_out", "correct", "question_response",
            "question_rt", "lexsync_region_rts")
  .inline_block("lexsync_trial_start", "Clear the previous trial's responses",
                sprintf("var.%s = u''", vars))
}

# The inline script that copies the trial's labels into the variables the logger
# writes. The labels stay out of the loop table, which OpenSesame evaluates, so the
# logger would not see them. Nothing reads these variables back, and both versions'
# loggers read without evaluation. Must match _osexp_record in scripting.py.
.osexp_record <- function() {
  .inline_block("lexsync_record", "Copy the trial's labels for the logger",
                c("_row = _lexsync_row()",
                  "var.lexsync_condition = _row.get(u'condition', u'')",
                  "var.lexsync_block = _row.get(u'block', u'')",
                  "var.lexsync_answer = _row.get(u'answer', u'')"))
}

# The inline script that checks the subject number against this file's version. A
# design with several presentation versions gets one experiment per version, and the
# experimenter opens the participant's. OpenSesame asks for a subject number at
# start-up, and participant p normally runs version ((p - 1) mod V) + 1. When the number
# belongs to another version, this shows a screen saying so and waits for a key. Space
# goes on with this file, and escape stops the session. It runs before the loop, so the
# experiment needs no run-if condition, a syntax that differs between OpenSesame 3.3
# and 4.x. Must match _osexp_version_check in scripting.py.
.osexp_version_check <- function(version, n_versions) {
  body <- c(
    sprintf("_version = %d", as.integer(version)),
    sprintf("_versions = %d", as.integer(n_versions)),
    "try:",
    "    _p = int(var.get(u'subject_nr', 0, _eval=False))",
    "except (TypeError, ValueError):",
    "    _p = 0",
    "_expected = (_p - 1) % _versions + 1",
    "if _expected != _version:",
    "    c = Canvas()",
    paste0("    c.text(u'Participant %d would normally run version %d, and this file runs ",
           "version %d. Press space to continue with this one or escape to stop.' ",
           "% (_p, _expected, _version))"),
    "    c.show()",
    "    _key, _t = Keyboard(keylist=[u'space', u'escape'], timeout=None).get_key()",
    "    if _key == u'escape':",
    paste0("        raise RuntimeError(u'lexsync: stopped at the version check, because ",
           "participant %d would normally run version %d.' % (_p, _expected))"))
  .inline_block("lexsync_version_check",
                "Warn when the subject number belongs to another version", body)
}

#' Build a complete plain-text OpenSesame experiment from rendered events
#'
#' The loop table and its companion text table are both looked up through OpenSesame's
#' file pool, which also searches the experiment's own folder. Mirrors `build_osexp`
#' in the Python engine.
#'
#' @param design A parsed design configuration.
#' @param conditions_file File name of the loop table.
#' @param schema The parsed global schema (trigger settings).
#' @param rendered Rendered events, from [render_events()].
#' @param font The font family OpenSesame draws text in.
#' @param text_file File name of the companion text table. `NULL` (the default) puts
#'   `_text` before the `.csv` of `conditions_file`.
#' @param version,n_versions The experiment is version `version` of `n_versions`. With
#'   more than one version, it checks OpenSesame's subject number against its own before
#'   the loop and warns when the participant would normally run another. `NULL` (the
#'   default) marks a design with one version, which needs no check.
#' @return The experiment's text, one string. Each trial starts by clearing the last
#'   trial's responses and ends with a logger item.
#' @keywords internal
build_osexp <- function(design, conditions_file, schema, rendered, font = "mono",
                        text_file = NULL, version = NULL, n_versions = NULL) {
  addr <- clean_port(schema[["triggers"]][["parallel_address"]] %||% "0x378")
  design_name <- clean_meta(design[["name"]], "the design's `name`")
  language <- clean_meta(design[["language"]], "the design's `language`")
  # `set font_family <font>` takes the value unquoted on its own line, so it is guarded
  # here rather than at the caller: an .osexp is line-oriented and a newline would add
  # items to the experiment.
  font <- clean_meta(font, "the font")
  text_file <- text_file %||% paste0(sub("\\.csv$", "", conditions_file), "_text.csv")
  setup <- c(
    # The trial texts, read as data with the csv module and keyed by the loop's
    # `lexsync_row` (not by the loop's position, which a user who switches the loop to
    # random order would change). utf-8-sig also reads a copy that a spreadsheet saved
    # with a byte-order mark.
    "import csv as _csv",
    sprintf("with open(pool[%s], encoding=u'utf-8-sig', newline=u'') as _f:", .pyq(text_file)),
    "    _LEXSYNC_ROWS = {int(_r[u'lexsync_row']): _r for _r in _csv.DictReader(_f)}",
    "def _lexsync_row():",
    "    return _LEXSYNC_ROWS[int(var.get(u'lexsync_row', _eval=False))]",
    "var.trigger_backend = u'parallel'",
    sprintf("var.parallel_port_address = %s", addr),
    "var.test_mode = u'no'",
    "import time",
    "def _printer(code):",
    "    print(u'[lexsync test trigger] %d' % int(code))",
    "    time.sleep(0.01)",
    "    print(u'[lexsync test trigger] 0')",
    "send_trigger = _printer",
    "try:",
    "    if var.trigger_backend == u'serial':",
    "        import serial",
    "        import serial.tools.list_ports",
    "        _ports = serial.tools.list_ports.comports()",
    "        if _ports:",
    "            _sp = serial.Serial(_ports[0].device)",
    "            def send_trigger(code):",
    "                _sp.write(int(code).to_bytes(1, 'big'))",
    "                time.sleep(0.01)",
    "                _sp.write((0).to_bytes(1, 'big'))",
    "        else:",
    "            var.test_mode = u'yes'",
    "    else:",
    "        from ctypes import windll",
    "        _io = windll.dlportio",
    "        _addr = int(var.parallel_port_address)",
    "        def send_trigger(code):",
    "            _io.DlPortWritePortUchar(_addr, int(code))",
    "            time.sleep(0.01)",
    "            _io.DlPortWritePortUchar(_addr, 0)",
    "except Exception as _exc:",
    "    var.test_mode = u'yes'",
    "    print(u'lexsync: trigger device unavailable; test mode.')",
    "send_trigger(0)"
  )

  # var.correct scores the response, or the question in a design with no response
  # event, as the PsychoPy data file does.
  collects <- function(ev) {
    if (identical(ev[["type"]], "response") || !is.null(ev[["respond"]])) "response"
    else if (identical(ev[["type"]], "question")) "question" else NA_character_
  }
  has_response <- any(vapply(rendered, collects, character(1)) %in% "response")
  event_blocks <- .osexp_trial_start(); run_names <- "lexsync_trial_start"
  last <- "response"
  for (i in seq_along(rendered)) {
    kind <- collects(rendered[[i]])
    eb <- .osexp_event_block(
      sprintf("lexsync_e%d", i - 1L), rendered[[i]],
      scores = identical(kind, if (has_response) "response" else "question"),
      feedback_scores = if (identical(last, "question")) "question_response" else "response")
    event_blocks <- c(event_blocks, eb$block)
    run_names <- c(run_names, eb$run)
    if (!is.na(kind)) last <- kind
  }
  # OpenSesame logs nothing without a logger item. This one runs last in every trial
  # and writes every variable, the labels copied in just before it included.
  event_blocks <- c(event_blocks, .osexp_record(),
                    "define logger lexsync_logger", '\tset description "Log the trial"',
                    "\tset auto_log yes", "")
  run_names <- c(run_names, "lexsync_record", "lexsync_logger")

  header <- c(
    "---", "API: 2.1", "OpenSesame: 3.3.14", "Platform: nt", "---",
    "set width 1024", "set uniform_coordinates yes",
    sprintf('set title "lexsync: %s (%s)"', design_name, language),
    "set subject_nr 0", "set start lexsync_experiment",
    "set sound_sample_size -16", "set sound_freq 48000", "set sound_channels 2",
    "set sound_buf_size 1024", "set sampler_backend legacy", "set round_decimals 2",
    "set mouse_backend legacy", "set keyboard_backend legacy", "set height 768",
    "set fullscreen no", "set foreground white", "set font_size 32",
    sprintf("set font_family %s", font), 'set description "Generated by lexsync"',
    "set coordinates uniform", "set compensation 0", "set color_backend legacy",
    "set clock_backend legacy", "set canvas_backend xpyriment", "set background black", "",
    "define inline_script lexsync_trigger_setup",
    paste('\tset description "Load the trial texts and open the trigger device with a',
          'test-mode fallback"'),
    '\tset _run ""', "\t___prepare__", paste0("\t", setup), "\t__end__", ""
  )
  checked <- !is.null(version) && !is.null(n_versions) && as.integer(n_versions) > 1L
  check <- if (checked) .osexp_version_check(version, n_versions) else character(0)
  trial <- c(
    "define sequence lexsync_trial",
    "\tset flush_keyboard yes",
    '\tset description "One trial: the paradigm event sequence"',
    sprintf("\trun %s always", run_names), "",
    "define loop lexsync_loop",
    sprintf('\tset source_file "%s"', conditions_file),
    # Sequential, so the loop presents the seeded trial order the CSV is sorted
    # by; OpenSesame's default (random) would discard it and diverge from the
    # PsychoPy and jsPsych targets.
    "\tset source file", "\tset repeat 1", "\tset order sequential",
    '\tset description "Present each item once"', "\trun lexsync_trial", "",
    "define sequence lexsync_experiment",
    "\tset flush_keyboard yes",
    '\tset description "Top-level experiment sequence"',
    "\trun lexsync_trigger_setup always",
    if (checked) "\trun lexsync_version_check always",
    "\trun lexsync_loop always", ""
  )
  paste(c(header, check, event_blocks, trial), collapse = "\n")
}

#' Export a complete plain-text OpenSesame experiment
#'
#' Writes `<base>.osexp` and the two tables it reads. Its loop runs over
#' `<base>_opensesame.csv`, which holds numbers only: `lexsync_row` (the trial's
#' position in loop order, from 1), `lexsync_trial`, `lexsync_list`, `lexsync_set`,
#' the trigger codes, `critical_region` and any per-trial duration. The presented
#' text, `condition`, `block` and `answer` are in `<base>_opensesame_text.csv`, which
#' the inline scripts read with Python's `csv` module, so OpenSesame never evaluates
#' them. Copy both tables with the experiment.
#'
#' Every trial is logged. A response after a text event is collected by that event's
#' script from the stimulus's onset, which sets `response`, `response_time`,
#' `timed_out` and `correct`. A response kept after the stimulus with `from: offset` is
#' a keyboard_response, and a script after it sets `timed_out` and `correct`.
#' Self-paced reading sets `lexsync_region_rts` and a question `question_response` and
#' `question_rt`. A script clears these as each trial starts, another copies the
#' trial's labels into `lexsync_condition`, `lexsync_block` and `lexsync_answer`, and a
#' logger item ends the trial.
#'
#' A design with more than one presentation version, one per (replicate, list) pair
#' of the trials, gets one experiment per version instead, each with its own two
#' tables holding only that version's trials: `<base>_list<k>.osexp`, or
#' `<base>_rep<r>_list<k>.osexp` when the versions span several replicates. Each one
#' checks OpenSesame's subject number at start-up and shows a warning when that
#' participant would normally run another version. [export_experiments()] lists every
#' file written.
#'
#' OpenSesame evaluates the cells of a loop table: in 4.x a cell holding `{` runs as a
#' Python f-string, and in 3.3 a cell starting with `=` or holding `[=...]` runs as
#' Python. A value in a numeric column that is not a plain number is therefore
#' refused, naming the column. An empty cell passes. These rules were checked against
#' the sources of OpenSesame 3.3.14 and 4.1.20.
#'
#' @inheritParams export_psychopy
#' @return The path to the generated `.osexp`, version 1's when there are several,
#'   invisibly.
#' @export
export_opensesame <- function(stimuli, design, schema, outdir, base = NULL) {
  invisible(.opensesame_files(stimuli, design, schema, outdir, base)$experiments[[1]])
}

# Write the OpenSesame experiments and their tables, one experiment per version.
# Returns list(experiments, tables): the .osexp paths in version order, and each
# version's loop table and text table in the same order. Every table is checked before
# anything is written, so a refused value leaves no partial set behind. Mirrors
# _opensesame_files in scripting.py.
.opensesame_files <- function(stimuli, design, schema, outdir, base = NULL) {
  base <- base %||% design_stem(design)
  events <- resolve_events(design)
  rendered <- render_events(events, design[["timing"]] %||% list(), .refresh_hz(schema))
  presentation <- schema[["presentation"]] %||% list()
  font <- design[["font"]] %||% presentation[["opensesame_font"]] %||% "mono"
  versions <- .presentation_versions(stimuli)
  parts <- if (length(versions) <= 1L) {
    # One version keeps the file names an experiment has always had.
    list(list(stem = base, rows = stimuli, version = NULL))
  } else {
    by_replicate <- .spans_replicates(versions)
    lapply(versions, function(v) {
      stem <- if (by_replicate) sprintf("%s_rep%d_list%d", base, v[["replicate"]], v[["list"]])
              else sprintf("%s_list%d", base, v[["list"]])
      list(stem = stem, rows = .version_rows(stimuli, v), version = v[["version"]])
    })
  }
  written <- lapply(parts, function(p) {
    csv_name <- paste0(p[["stem"]], "_opensesame.csv")
    text_name <- paste0(p[["stem"]], "_opensesame_text.csv")
    list(stem = p[["stem"]], csv_name = csv_name, text_name = text_name,
         tables = .opensesame_tables(p[["rows"]], events),
         osexp = build_osexp(design, csv_name, schema, rendered, font = font,
                             text_file = text_name, version = p[["version"]],
                             n_versions = length(versions)))
  })
  experiments <- character(0)
  tables <- character(0)
  for (w in written) {
    write_csv_utf8(w$tables$numbers, file.path(outdir, w$csv_name))
    write_csv_utf8(w$tables$text, file.path(outdir, w$text_name))
    out <- file.path(outdir, paste0(w$stem, ".osexp"))
    write_lines_lf(w$osexp, out)
    experiments <- c(experiments, out)
    tables <- c(tables, file.path(outdir, w$csv_name), file.path(outdir, w$text_name))
  }
  list(experiments = experiments, tables = tables)
}

# BCP 47 tags for the human-readable language labels the designs carry, covering the
# languages the corpus connectors derive lexica for (corpora/fetch_corpora.py).
.BCP47_TAGS <- c(english = "en", spanish = "es", french = "fr", german = "de",
                 dutch = "nl", italian = "it", portuguese = "pt",
                 chinese = "zh", `chinese (mandarin)` = "zh")

# The design's BCP 47 tag for the generated HTML lang attribute. `language` is a
# free-text label ("english"), which is not a valid tag, so it is mapped. A design
# may state `language_tag` outright, and a label that is already tag-shaped ("en",
# "en-GB") is taken as given. Anything else becomes "und" (BCP 47 "undetermined"):
# registered, and unlike lang="english" resolvable by a validator or a screen reader.
.language_tag <- function(design) {
  # The shape check applies to a STATED tag too. It used to be returned verbatim, so
  # `language_tag: 'en"><script>...'` reached the lang attribute of the generated HTML
  # intact -- the one input to this function that an attacker would actually choose.
  tag <- trimws(as.character(design[["language_tag"]] %||% ""))
  if (nzchar(tag)) {
    return(if (grepl("^[A-Za-z]{2,3}(-[A-Za-z0-9]{1,8})*$", tag, perl = TRUE)) tag else "und")
  }
  label <- trimws(as.character(design[["language"]] %||% ""))
  if (grepl("^[A-Za-z]{2,3}(-[A-Za-z0-9]{1,8})*$", label, perl = TRUE)) return(label)
  m <- .BCP47_TAGS[.lower_invariant(label)]
  if (is.na(m)) "und" else unname(m)
}

# Event-model key names (PsychoPy style) mapped to browser KeyboardEvent keys.
.JSPSYCH_KEYS <- c(left = "arrowleft", right = "arrowright", up = "arrowup",
                   down = "arrowdown", space = " ", "return" = "enter")

.map_keys_jspsych <- function(rendered) {
  # Keys given as a list stay a list, which jsonlite writes as an array even for one.
  mapk <- function(k) {
    v <- unlist(k, use.names = FALSE)
    m <- .JSPSYCH_KEYS[v]
    out <- unname(ifelse(is.na(m), v, m))
    if (is.list(k)) as.list(out) else out
  }
  lapply(rendered, function(e) {
    # [[ ]], not $: `$` partial-matches on a list, so `e$key` returns the value of
    # `keys` and the assignment then adds a `key` the Python engine never emits.
    if (!is.null(e[["keys"]])) e[["keys"]] <- mapk(e[["keys"]])
    if (!is.null(e[["key"]])) e[["key"]] <- mapk(e[["key"]])
    if (!is.null(e[["respond"]])) e[["respond"]][["keys"]] <- mapk(e[["respond"]][["keys"]])
    e
  })
}

.json_html <- function(x) {
  s <- as.character(x)
  s <- gsub("<", "\\u003c", s, fixed = TRUE)
  s <- gsub(">", "\\u003e", s, fixed = TRUE)
  s <- gsub("&", "\\u0026", s, fixed = TRUE)
  # U+2028 and U+2029 terminate a line in JavaScript but are not ASCII controls, so
  # clean_field passes them, and a raw one inside a <script> string literal is a
  # SyntaxError before ES2019. The Python twin escaped them and this did not, so the
  # same design produced different bytes from the two engines. Written as escape
  # sequences rather than literal characters so this file stays pure ASCII.
  s <- gsub("\u2028", "\\u2028", s, fixed = TRUE)
  gsub("\u2029", "\\u2029", s, fixed = TRUE)
}

#' Export a browser-runnable jsPsych experiment
#'
#' The rendered events and the trial data are embedded in one HTML file, so anyone
#' can reproduce the procedure online from the same materials. The jsPsych library
#' and stylesheet are loaded from a CDN, so the machine running the file needs an
#' internet connection; the trial data are embedded and the responses are saved
#' locally, so no server is required either to run it or to collect them. Onset
#' triggers are recorded in each trial's data (a browser cannot drive a parallel
#' port). A stimulus that collects its response is one trial, recorded as `target`:
#' it accepts the keys from its onset, shows the stimulus for its duration and stays
#' open for the timeout after it, a key ends it, and `rt` runs from the onset.
#'
#' The page embeds every presentation version of the design, one per (replicate,
#' list) pair, and runs one, named in its address: `?version=K`, `?list=K` when there
#' are no replicates, or `?participant=N`, whose version is `((N - 1) mod V) + 1`. A
#' page with more than one version, opened with none of these, shows a screen naming
#' them and runs nothing. The data rows carry the participant, the version, the list
#' and the replicate, and the data file is named after the participant and the
#' version.
#'
#' @inheritParams export_psychopy
#' @return The path to the generated `.html`, invisibly.
#' @importFrom jsonlite toJSON
#' @export
export_jspsych <- function(stimuli, design, schema, outdir, base = NULL) {
  base <- base %||% design_stem(design)
  events <- resolve_events(design)
  rendered <- .map_keys_jspsych(
    render_events(events, design[["timing"]] %||% list(), .refresh_hz(schema)))
  versions <- .presentation_versions(stimuli)
  trials <- loop_table(stimuli, events)
  presentation <- schema[["presentation"]] %||% list()
  font <- design[["font"]] %||% presentation[["font"]] %||% "Courier New"
  tmpl <- paste(readLines(find_template("jspsych/experiment_template.html"), warn = FALSE),
                collapse = "\n")
  subs <- list(
    DESIGN = clean_meta(design[["name"]], "the design's `name`"),
    LANGUAGE = clean_meta(design[["language"]], "the design's `language`"),
    LANGUAGE_TAG = .language_tag(design), WORD_FONT = clean_meta(font, "the font"),
    EVENTS_JSON = .json_html(jsonlite::toJSON(rendered, auto_unbox = TRUE)),
    # Each double to 15 significant digits, the digits the Python engine writes
    # (_fifteen_digits in scripting.py). The default of four decimal places wrote
    # 33.3333 for an item table's 33.333333, where Python wrote every digit, so the two
    # engines' pages differed. I(15), not digits = NA, which jsonlite 1.8.5 and 1.8.6
    # wrote to 17 digits; I(15) is "%.15g" in every version, and DESCRIPTION sets no
    # floor on jsonlite.
    TRIALS_JSON = .json_html(jsonlite::toJSON(trials, dataframe = "rows", digits = I(15))),
    VERSIONS_JSON = .json_html(jsonlite::toJSON(versions, auto_unbox = TRUE))
  )
  for (k in names(subs)) {
    tmpl <- gsub(sprintf("{{%s}}", k), as.character(subs[[k]]), tmpl, fixed = TRUE)
  }
  out <- file.path(outdir, paste0(base, ".html"))
  write_lines_lf(tmpl, out)
  invisible(out)
}

#' Export all presentation targets (PsychoPy, OpenSesame, jsPsych)
#'
#' Assigns the EEG trigger codes with [assign_triggers()] and then writes each
#' target. The condition codes follow `conditions`, which defaults to the order of
#' the design's `conditions` entries, so in a design that declares its conditions
#' the first is 101, the second 102, and so on, whatever order the counterbalanced
#' trials put them in. A design with no `conditions` block (a generated lexical
#' decision, an item table) falls back to the order of first appearance, unless
#' `conditions` is given. [assign_triggers()] is given the design's events and the
#' schema, so the item codes of a design that sends them alongside other codes are
#' kept apart from those codes, and a code of the design's own that the stream
#' already uses is reported.
#'
#' @inheritParams export_psychopy
#' @param conditions Optional character vector of condition labels in the order
#'   that assigns their trigger codes (see [assign_triggers()]). `NULL` (the
#'   default) takes the order of the design's `conditions`.
#' @return A named list of generated file paths: `psychopy`, `opensesame` (version 1's
#'   experiment when a design has several, see [export_opensesame()]) and `jspsych`.
#'   `files` lists every file written, in a fixed order: the PsychoPy script, each
#'   OpenSesame experiment in version order, the jsPsych page, the PsychoPy conditions
#'   file, and then each OpenSesame experiment's loop table and text table.
#' @export
export_experiments <- function(stimuli, design, schema, outdir, base = NULL,
                               conditions = NULL) {
  stimuli <- assign_triggers(stimuli, conditions %||% .design_condition_names(design),
                             events = resolve_events(design), schema = schema)
  psychopy <- .psychopy_files(stimuli, design, schema, outdir, base)
  opensesame <- .opensesame_files(stimuli, design, schema, outdir, base)
  jspsych <- export_jspsych(stimuli, design, schema, outdir, base)
  list(
    psychopy = psychopy[[1]],
    opensesame = opensesame$experiments[[1]],
    jspsych = jspsych,
    files = c(psychopy[[1]], opensesame$experiments, jspsych, psychopy[[2]],
              opensesame$tables)
  )
}
