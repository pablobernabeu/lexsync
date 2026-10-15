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
#' something else: 254 or 255, which the PsychoPy and OpenSesame experiments send when
#' the session starts and ends, a condition code the design sends, or a code within the
#' range of the item codes it sends.
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
# 255, which the PsychoPy and OpenSesame experiments send when the session starts and
# ends, a code equal to a condition code the design sends, and a code within the range
# of the item codes it sends. The allocation keeps every item code off the design's own
# codes, so the last is a warning for anyone who decodes item codes by their range. Must
# match _code_notes in scripting.py.
.code_notes <- function(sent, conds, item_codes) {
  notes <- character(0)
  for (l in sent$literals) {
    i <- l[["event"]]
    code <- l[["code"]]
    if (code %in% c(254L, 255L)) {
      notes <- c(notes, sprintf(paste("lexsync: event %d sends code %d, which the PsychoPy",
                                      "and OpenSesame experiments also send when the",
                                      "session %s."),
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

# A text event's `case`, "upper" or "lower", checked. The case travels with the rendered
# event and the runners apply it as they show the text: str.upper() and str.lower() in
# PsychoPy and OpenSesame, toUpperCase() and toLowerCase() in jsPsych. The generators
# never change the text, because toupper() leaves the German sharp s as it is where
# Python gives "SS", and the two engines must write the same files. Must match _case_of
# in scripting.py.
.case_of <- function(ev, index) {
  value <- ev[["case"]]
  if (!is.character(value) || length(value) != 1L || is.na(value) ||
      !(value %in% c("upper", "lower"))) {
    stop(sprintf(paste("lexsync: event %d has case '%s'; a text event takes case: upper or",
                       "case: lower."), as.integer(index), .shown(value)), call. = FALSE)
  }
  value
}

# A mask's `length_of`, the fields whose longest text sets its length, checked. A scalar
# names one field, and each must be a name a {field} reference could give. The mask's
# content must be one character, which .sized_masks() repeats once the trials are known.
# Must match _length_of in scripting.py.
.length_of <- function(ev, index) {
  value <- ev[["length_of"]]
  fields <- if (is.list(value)) value else as.list(value)
  ok <- is.null(names(value)) && length(fields) > 0L &&
    all(vapply(fields, function(f) {
      is.character(f) && length(f) == 1L && !is.na(f) &&
        grepl("^[A-Za-z_][A-Za-z0-9_]*\\z", f, perl = TRUE)
    }, logical(1)))
  if (!ok) {
    stop(sprintf(paste("lexsync: event %d has length_of '%s'; name the fields whose longest",
                       "text sets the mask's length, as in [prime, target]."),
                 as.integer(index), .shown(value)), call. = FALSE)
  }
  content <- ev[["content"]]
  if (!is.character(content) || length(content) != 1L || is.na(content) ||
      nchar(content, type = "chars") != 1L) {
    stop(sprintf(paste("lexsync: event %d repeats its content to the length of the longest",
                       "text of the trials, so its content must be one character, such as",
                       "'#'."), as.integer(index)), call. = FALSE)
  }
  as.list(unlist(fields, use.names = FALSE))
}

# The rendered events with each `length_of` mask written out for these trials. Such a
# mask's character is repeated as many times as the longest text of its fields has
# characters (code points, so a word of seven letters with two accents counts 7 where
# UTF-8 gives 9 bytes), among all the trials of every version, so each target and each
# version shows the same mask. A missing cell is passed over. The mask then travels as
# literal text, as any other mask does. Must match _sized_masks in scripting.py.
.sized_masks <- function(rendered, stimuli) {
  lapply(rendered, function(ev) {
    fields <- ev[["length_of"]]
    if (is.null(fields)) return(ev)
    longest <- 1L
    for (field in unlist(fields, use.names = FALSE)) {
      if (!(field %in% names(stimuli))) {
        stop(sprintf(paste("lexsync: a mask takes its length from field '%s', which the",
                           "trials do not have."), field), call. = FALSE)
      }
      values <- stimuli[[field]]
      values <- values[!is.na(values)]
      if (length(values)) {
        longest <- max(longest, nchar(enc2utf8(as.character(values)), type = "chars"))
      }
    }
    ev[["length_of"]] <- NULL
    ev[["text"]] <- strrep(ev[["text"]], longest)
    ev
  })
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

# The shortest hold either laboratory target gives a code, in milliseconds: a pulse
# shorter than this may not register on a recorder at all. The PsychoPy template applies
# the same floor as MIN_TRIGGER_HOLD_MS. Must match _MIN_HOLD_MS in scripting.py.
.MIN_HOLD_MS <- 10

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

# Whether a setting is a whole number from `low` to `high`, written as 48 or 48.0. A
# logical value is not one, and neither is text. Must match _whole_number in
# scripting.py.
.whole_number <- function(value, low, high) {
  is.numeric(value) && length(value) == 1L && !is.na(value) && is.finite(value) &&
    value == trunc(value) && value >= low && value <= high
}

# Whether the PsychoPy script runs full screen, presentation.fullscreen. TRUE by
# default, as PsychoPy advises for frame timing. OpenSesame takes full screen from the
# mode it is launched in. Must match _fullscreen in scripting.py.
.fullscreen <- function(schema) {
  value <- (schema[["presentation"]] %||% list())[["fullscreen"]]
  if (is.null(value)) return(TRUE)
  .require_bool(value, "presentation.fullscreen")
  isTRUE(value)
}

# The height of the stimulus text in pixels, presentation.text_height_px. 48 by default,
# the PsychoPy and jsPsych size, and the size of every text the OpenSesame experiment
# shows, since it sets OpenSesame's font_size. Must match _text_height_px in
# scripting.py.
.text_height_px <- function(schema) {
  value <- (schema[["presentation"]] %||% list())[["text_height_px"]]
  if (is.null(value)) return(48L)
  if (!.whole_number(value, 8, 400)) {
    stop(paste("lexsync: presentation.text_height_px must be a whole number of pixels",
               "from 8 to 400."), call. = FALSE)
  }
  as.integer(value)
}

# The values triggers.mode and triggers.backend take, the default first. Must match
# _TRIGGER_MODES and _TRIGGER_BACKENDS in scripting.py.
.TRIGGER_MODES <- c("auto", "hardware", "mock")
.TRIGGER_BACKENDS <- c("parallel", "serial")

# A setting that names one of `choices`, the first when it is absent.
.one_of <- function(value, key, choices) {
  if (is.null(value)) return(choices[1])
  if (!is.character(value) || length(value) != 1L || is.na(value) || !(value %in% choices)) {
    n <- length(choices)
    allowed <- paste0(paste(choices[-n], collapse = ", "), " or ", choices[n])
    stop(sprintf("lexsync: %s must be %s, not '%s'.", key, allowed, .shown(value)),
         call. = FALSE)
  }
  value
}

# The trigger device the laboratory targets write to, and what they do without it.
# `mode` is triggers.mode: "auto" prints the codes when the device cannot be opened and
# says so before the first trial, "hardware" stops instead, and "mock" prints them
# without trying the device. `backend` is triggers.backend: the parallel port at
# triggers.parallel_address, or "serial", which writes each code as one byte to
# triggers.serial_port at triggers.baudrate (115200 by default). A serial backend must
# name its port. Taking the first port found could send the codes to another device.
# The port is checked whatever the backend, since the PsychoPy script carries it either
# way. Must match _trigger_settings in scripting.py.
.trigger_settings <- function(schema) {
  triggers <- schema[["triggers"]] %||% list()
  mode <- .one_of(triggers[["mode"]], "triggers.mode", .TRIGGER_MODES)
  backend <- .one_of(triggers[["backend"]], "triggers.backend", .TRIGGER_BACKENDS)
  port <- triggers[["serial_port"]]
  if (!is.null(port)) {
    port <- clean_serial_port(port)
  } else if (identical(backend, "serial")) {
    stop(paste("lexsync: triggers.backend is serial, so triggers.serial_port must name the",
               "serial device, such as COM3 or /dev/ttyUSB0."), call. = FALSE)
  }
  baudrate <- triggers[["baudrate"]]
  if (is.null(baudrate)) {
    baudrate <- 115200L
  } else if (!.whole_number(baudrate, 1, .Machine$integer.max)) {
    stop(paste("lexsync: triggers.baudrate must be a whole number of bits per second,",
               "such as 115200."), call. = FALSE)
  }
  list(mode = mode, backend = backend, serial_port = port %||% "",
       baudrate = as.integer(baudrate))
}

# The trigger device as the experiments' messages name it. Must match _trigger_device
# in scripting.py.
.trigger_device <- function(settings, address) {
  if (identical(settings$backend, "serial")) {
    paste0("the serial port ", settings$serial_port)
  } else {
    paste0("the parallel port at ", address)
  }
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
# A YAML boolean is refused before that. Both engines read an unquoted yes, no, true,
# false, on or off as a boolean. as.character() then made the key TRUE here, and the
# Python engine wrote True, so neither experiment could register a response. Each key
# is tested on its own, since unlist() would turn TRUE beside a text key into "TRUE".
# Must match _keys_of in scripting.py.
#' @keywords internal
.keys_of <- function(ev, default) {
  keys <- ev[["keys"]] %||% default
  for (key in as.list(keys)) {
    if (is.logical(key) && length(key) == 1L && !is.na(key)) {
      stop(sprintf(paste("lexsync: response key %s is a YAML boolean; quote it ('%s') or",
                         "choose another key."),
                   if (key) "TRUE" else "FALSE", if (key) "yes" else "no"), call. = FALSE)
    }
  }
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
#'
#' A text event's `case` is carried as it is, for the runners to apply. A mask's
#' `length_of` is carried too, with the one character to repeat as its `text`, and the
#' exporters write the mask out for their trials (see `.sized_masks()`).
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
    if (!is.null(ev[["case"]]) && !identical(t, "text")) {
      stop(sprintf("lexsync: event %d is a %s event, and only a text event takes `case`.",
                   i, .shown(t)), call. = FALSE)
    }
    if (!is.null(ev[["length_of"]]) && !identical(t, "mask")) {
      stop(sprintf("lexsync: event %d is a %s event, and only a mask event takes `length_of`.",
                   i, .shown(t)), call. = FALSE)
    }
    if (t %in% c("fixation", "text", "mask")) {
      f <- content_field(ev[["content"]])
      if (!is.null(f)) r$field <- f else r$text <- as.character(ev[["content"]] %||% "")
      if (!is.null(ev[["length_of"]])) r$length_of <- .length_of(ev, i)
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
      if (!is.null(ev[["case"]])) r$case <- .case_of(ev, i)
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
#' write the same table. A design with `counterbalance.orders` carries `order_1` to
#' `order_m` after the columns that place a trial, each trial's position in each
#' order, which the experiments sort a version by.
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
  order_cols <- c("trial", "list", "replicate", "block", "set", "condition",
                  .order_columns(stimuli), fields, ms_cols, "critical_region", "answer",
                  "condition_trigger", "item_trigger")
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

# The trial-order columns order_1 to order_m the trials carry, in order. counterbalance()
# writes them when a design asks for more than one order. The numbering runs from
# order_1 without a gap, so a column of another name, such as an item table's own
# order_9, is not taken for one. Mirrors _order_columns in scripting.py.
.order_columns <- function(stimuli) {
  out <- character(0)
  while (paste0("order_", length(out) + 1L) %in% names(stimuli)) {
    out <- c(out, paste0("order_", length(out) + 1L))
  }
  if (length(out) > 1L) out else character(0)
}

# The number of trial orders the trials carry, 1 when they carry none.
.n_orders <- function(stimuli) max(1L, length(.order_columns(stimuli)))

# One version's rows in trial order `order`, with `trial` set to each trial's position
# in it, so a table written from them numbers the trials as presented. Mirrors
# _rows_in_order in scripting.py.
.rows_in_order <- function(rows, order) {
  key <- paste0("order_", order)
  out <- rows[order(rows[[key]], method = "radix"), , drop = FALSE]
  out$trial <- out[[key]]
  rownames(out) <- NULL
  out
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
#' not have stops the run with a message. With `counterbalance.orders: m` the
#' conditions file holds each trial's position in each of m orders, and the script
#' presents the version in order `(((participant - 1) div V) mod m) + 1`, or in order 1
#' without a participant number. The data file then records the order.
#'
#' Before the first trial, the script shows the version's instructions, the design's
#' `instructions` or lexsync's for its task, and waits for the space bar, which also
#' lets the experimenter start the run. Escape there stops the run before anything is
#' recorded. The text is embedded as JSON data, one text per version.
#'
#' Each run writes `data/<base>_p<participant>_v<version>_<date>-<time>.csv` beside
#' the script, without the `_p` part when no participant number is given, one row per
#' trial, each written as its trial ends. A row holds the run, the trial's fields and
#' trigger codes, the response and its reaction time from the onset of the stimulus it
#' answers, whether the window closed without one, whether the key was the trial's
#' `answer`, the self-paced reading times, the question's response and reaction time,
#' the measured refresh rate, the trigger mode the run used, and each event's realised
#' flips and onset.
#'
#' Each trigger code goes out on its stimulus's first flip and is held for
#' `triggers.trigger_hold_ms`, in whole flips at the measured refresh and never under
#' 10 ms, through the events after it when its own is shorter, unless the next onset's
#' code replaces it first. The session markers, 254 before the first trial and 255 after
#' the last, are held the same way.
#'
#' The script runs full screen unless `presentation.fullscreen` is false, when it opens
#' a 1280 x 1024 window, and draws its stimuli `presentation.text_height_px` pixels
#' high, 48 by default. It writes the codes to the parallel port at
#' `triggers.parallel_address` or, with `triggers.backend: serial`, as single bytes to
#' `triggers.serial_port` at `triggers.baudrate`. `triggers.mode` decides what happens
#' when that device cannot be opened. Under `auto`, the script prints the codes instead
#' and, before the instructions, shows a notice that the experimenter dismisses with the
#' C key. Under `hardware`, it stops before its window opens, and under `mock` it prints
#' the codes without trying the device. The data file's `trigger_mode` column records
#' `hardware` or `mock`.
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
  rendered <- .sized_masks(
    render_events(events, design[["timing"]] %||% list(), .refresh_hz(schema)), stimuli)
  versions <- .presentation_versions(stimuli)
  csv_name <- paste0(base, "_psychopy.csv")
  write_csv_utf8(loop_table(stimuli, events), file.path(outdir, csv_name))
  tmpl <- paste(readLines(find_template("psychopy/trial_runner_template.py"), warn = FALSE),
                collapse = "\n")
  triggers <- schema[["triggers"]] %||% list()
  presentation <- schema[["presentation"]] %||% list()
  address <- clean_port(triggers[["parallel_address"]] %||% "0x0378")
  device <- .trigger_settings(schema)
  subs <- list(
    DESIGN = clean_meta(design[["name"]], "the design's `name`"),
    LANGUAGE = clean_meta(design[["language"]], "the design's `language`"),
    CONDITIONS_FILE = csv_name,
    # The data files are named after the experiment, as data/<base>_p<n>_v<k>_...
    BASE = base,
    TRIGGER_ADDRESS = address,
    TRIGGER_BACKEND = device$backend,
    SERIAL_PORT = device$serial_port,
    SERIAL_BAUDRATE = as.character(device$baudrate),
    TRIGGER_DEVICE = .trigger_device(device, address),
    TRIGGER_MODE = device$mode,
    TRIGGER_HOLD_MS = sprintf("%.17g", .trigger_hold_ms(schema)),
    WORD_FONT = clean_meta(design[["font"]] %||% presentation[["font"]] %||% "Courier New",
                           "the font"),
    FULLSCREEN = if (.fullscreen(schema)) "True" else "False",
    TEXT_HEIGHT_PX = as.character(.text_height_px(schema)),
    # The fallback used only when the script cannot measure the display.
    ASSUMED_REFRESH_HZ = sprintf("%.17g", .refresh_hz(schema)),
    EVENTS_JSON = as.character(jsonlite::toJSON(rendered, auto_unbox = TRUE)),
    VERSIONS_JSON = as.character(jsonlite::toJSON(versions, auto_unbox = TRUE)),
    ORDERS = as.character(.n_orders(stimuli)),
    # A list, which jsonlite writes as an array even for one version.
    INSTRUCTIONS_JSON = as.character(jsonlite::toJSON(
      as.list(.instruction_texts(design, versions)), auto_unbox = TRUE))
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

# The text an event shows, as the inline script computes it. A text event's `case` is
# applied there, with Python's str.upper() or str.lower(), as the text is shown. Must
# match _content_expr in scripting.py.
.content_expr <- function(ev) {
  expr <- if (!is.null(ev[["field"]])) .text_expr(ev[["field"]]) else .pyq(ev[["text"]] %||% "")
  case <- ev[["case"]]
  if (identical(case, "upper")) return(paste0(expr, ".upper()"))
  if (identical(case, "lower")) return(paste0(expr, ".lower()"))
  expr
}

.trigger_expr <- function(spec) {
  if (is.null(spec)) return(NULL)
  if (is.character(spec) && startsWith(spec, "@")) return(.number_expr(substring(spec, 2)))
  as.character(as.integer(spec))
}

# An inline_script item whose run phase is `body` and whose prepare phase is `prepare`.
# A sequence runs the prepare phase of every item it holds before it runs any, so
# `prepare` is where a script builds what it shows. Must match _inline_block in
# scripting.py.
.inline_block <- function(name, desc, body, prepare = NULL) {
  head <- c(sprintf("define inline_script %s", name), sprintf('\tset description "%s"', desc))
  head <- if (length(prepare)) {
    c(head, "\t___prepare__", paste0("\t", prepare), "\t__end__")
  } else {
    c(head, '\tset _prepare ""')
  }
  c(head, "\t___run__", paste0("\t", body), "\t__end__", "")
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
#
# Every canvas an event shows is built in its script's prepare phase, which OpenSesame
# runs for every item of the trial sequence before it runs any, so building and drawing
# take no time between one display and the next. The canvas is named after its script,
# `_lexsync_c_e<i>`, because all inline scripts share one workspace and a shared name
# would show, in every script, the canvas prepared last. The run phase shows it and
# times everything from the onset that show() returns, through the helpers the setup
# script defines (see .osexp_timing): `_lexsync_onset` sends the event's code,
# `_lexsync_wait` sleeps and `_lexsync_key` polls the keyboard until a time measured from
# the onset, each resetting a code whose hold has run out.
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
  canvas <- paste0("_lexsync_c_", sub("^lexsync_", "", name))
  # A fixed duration is a literal; one that varies per trial reads the loop-table
  # column, which OpenSesame exposes on `var`. Must match _osexp_event_block in
  # scripting.py, since the two engines write the same .osexp.
  # [[ ]], not $: `$` partial-matches on a list, so `ev$ms` would return the value
  # of `ms_column` for a per-trial duration and emit the column name as a literal.
  ms <- if (!is.null(ev[["ms_column"]]))
    sprintf("int(float(var.get(%s, _eval=False)))",
            .pyq(clean_column(ev[["ms_column"]], "a jittered duration's `as`"))) else
    sprintf("%d", as.integer(ev[["ms"]] %||% 0L))
  # The event ends half a frame before its duration is up. The next show() then waits
  # for the refresh that ends the duration, and lands on it, where sleeping the whole
  # duration made it miss that refresh and wait for the next (OpenSesame's Timing
  # manual advises asking for slightly less than the interval wanted).
  end <- sprintf("_t0 + %s - _LEXSYNC_HALF_FRAME", ms)
  trig <- .trigger_expr(ev[["trigger"]])
  onset <- if (is.null(trig)) character(0) else sprintf("_lexsync_onset(%s, _t0)", trig)
  if (identical(t, "text") && !is.null(ev[["respond"]])) {
    # The stimulus collects its own response, from its onset. The keyboard is flushed
    # once the trigger is out, so nothing pressed before the stimulus counts, and polled
    # while the stimulus is shown. Without a key by its end, the screen blanks and the
    # keyboard is polled until the timeout has passed after it, so the window is the one
    # the stimulus and a separate response event had, timed from the onset. A key ends
    # the event either way, and does not cut its code short.
    respond <- ev[["respond"]]
    keylist <- paste(vapply(unlist(respond[["keys"]]), .pyq, character(1)), collapse = ", ")
    prepare <- c(sprintf("%s = Canvas()", canvas),
                 sprintf("%s.text(%s)", canvas, .content_expr(ev)),
                 sprintf("%s_blank = Canvas()", canvas))
    body <- c(sprintf("_t0 = %s.show()", canvas), "var.onset_time = _t0", onset,
              sprintf("_kb = Keyboard(keylist=[%s])", keylist),
              "_kb.flush()",
              sprintf("_key, _t = _lexsync_key(_kb, %s)", end),
              "if _key is None:",
              sprintf("    %s_blank.show()", canvas),
              sprintf("    _key, _t = _lexsync_key(_kb, _t0 + %s + %d)", ms,
                      .whole_ms(respond[["timeout"]])),
              "var.response = _key",
              "var.response_time = u'' if _key is None else _t - _t0",
              "var.timed_out = 1 if _key is None else 0")
    if (isTRUE(scores)) body <- c(body, .osexp_correct("_key"))
    return(list(block = .inline_block(name, paste("Show the stimulus and collect the",
                                                  "response from its onset"),
                                      .osexp_block_guard(body, blocks),
                                      prepare = .osexp_block_guard(prepare, blocks)),
                run = name))
  }
  if (t %in% c("fixation", "text", "mask", "blank")) {
    prepare <- sprintf("%s = Canvas()", canvas)
    if (t != "blank") prepare <- c(prepare, sprintf("%s.text(%s)", canvas, .content_expr(ev)))
    body <- c(sprintf("_t0 = %s.show()", canvas), "var.onset_time = _t0", onset,
              sprintf("_lexsync_wait(%s)", end))
    return(list(block = .inline_block(name, "Show stimulus and send onset-aligned trigger",
                                      .osexp_block_guard(body, blocks),
                                      prepare = .osexp_block_guard(prepare, blocks)),
                run = name))
  }
  if (t == "region") {
    trig <- .trigger_expr(ev[["crit_trigger"]])
    # One canvas per region, in a list. Each region is timed from its own onset, and
    # the keyboard is flushed as it appears, so a key pressed before it cannot advance
    # it.
    prepare <- c(
      sprintf("%s = []", canvas),
      sprintf("for _r in [r for r in %s.split(%s) if r != u'']:", .text_expr(ev[["field"]]),
              .pyq(ev[["sep"]] %||% "|")),
      "    _c = Canvas()",
      "    _c.text(_r)",
      sprintf("    %s.append(_c)", canvas))
    body <- c(
      # An empty cell, a sentence with no critical region, reads as 0: no trigger.
      "_crit = int(var.get(u'critical_region', 0, _eval=False) or 0)",
      sprintf("_kb = Keyboard(keylist=[%s], timeout=None)", .pyq(ev[["key"]] %||% "space")),
      "_rts = []",
      sprintf("for _i, _c in enumerate(%s, start=1):", canvas),
      "    _t0 = _c.show()")
    if (!is.null(trig)) {
      body <- c(body, sprintf("    if _i == _crit: _lexsync_onset(%s, _t0)", trig))
    }
    body <- c(body, "    _kb.flush()", "    _key, _t = _lexsync_key(_kb, None)",
              "    _rts.append(u'%.1f' % (_t - _t0))",
              "var.lexsync_region_rts = u'|'.join(_rts)")
    return(list(block = .inline_block(name, "Self-paced reading region by region",
                                      .osexp_block_guard(body, blocks),
                                      prepare = .osexp_block_guard(prepare, blocks)),
                run = name))
  }
  if (t == "question") {
    keys_list <- paste(vapply(unlist(ev[["keys"]] %||% c("f", "j")), .pyq, character(1)),
                       collapse = ", ")
    prepare <- c(sprintf("%s = Canvas()", canvas),
                 sprintf("%s.text(%s)", canvas, .text_expr(ev[["field"]])))
    body <- c(
      sprintf("_t0 = %s.show()", canvas),
      sprintf("_kb = Keyboard(keylist=[%s])", keys_list),
      "_kb.flush()",
      sprintf("_key, _t = _lexsync_key(_kb, _t0 + %d)", .whole_ms(ev[["timeout"]] %||% 5)),
      "var.question_response = _key",
      "var.question_rt = u'' if _key is None else _t - _t0")
    if (isTRUE(scores)) body <- c(body, .osexp_correct("_key"))
    return(list(block = .inline_block(name, "Comprehension question",
                                      .osexp_block_guard(body, blocks),
                                      prepare = .osexp_block_guard(prepare, blocks)),
                run = name))
  }
  if (t == "feedback") {
    # The key comes from whichever response or question collected one last. The answer
    # column (or whichever column the event names) holds the KEY that is correct, so
    # scoring is a string comparison. A timeout is reported separately, because on a
    # timed task it means something different from a wrong key. OpenSesame 4.x stores it
    # as None and 3.3 as the string 'None', so both count as no response. The response
    # is not known until the trial runs, so all three messages are prepared and the run
    # phase shows one.
    messages <- c(correct = ev[["correct"]] %||% "Correct",
                  incorrect = ev[["incorrect"]] %||% "Incorrect",
                  no_response = ev[["no_response"]] %||% "Too slow")
    prepare <- c(
      sprintf("%s = {u'correct': Canvas(), u'incorrect': Canvas(), u'no_response': Canvas()}",
              canvas),
      sprintf("%s[u'%s'].text(%s)", canvas, names(messages),
              vapply(messages, .pyq, character(1), USE.NAMES = FALSE)))
    body <- c(
      sprintf("_want = str(_lexsync_row().get(u'%s', u'')).strip()",
              clean_column(ev[["answer"]] %||% "answer", "a feedback event's `answer`")),
      sprintf("_got = var.get(u'%s', u'', _eval=False)", feedback_scores),
      "_got = u'' if _got is None else str(_got).strip()",
      "if _got in (u'', u'None'): _msg = u'no_response'",
      "elif _got == _want: _msg = u'correct'",
      "else: _msg = u'incorrect'",
      sprintf("_t0 = %s[_msg].show()", canvas),
      sprintf("_lexsync_wait(%s)", end))
    return(list(block = .inline_block(name, "Practice feedback",
                                      .osexp_block_guard(body, blocks),
                                      prepare = .osexp_block_guard(prepare, blocks)),
                run = name))
  }
  if (t == "response") {
    keys <- paste(unlist(ev[["keys"]] %||% c("left", "right")), collapse = ";")
    # A keyboard_response draws nothing, so the preceding canvas would stay up for
    # the whole response window. Blank it first, so the stimulus offsets at its own
    # duration as it does in the PsychoPy and jsPsych targets. The keyboard_response
    # runs no code of lexsync's, so a code still held is held out first.
    block <- c(
      .inline_block(sprintf("%s_blank", name), "Clear the screen for the response window",
                    c(sprintf("%s_blank.show()", canvas), "_lexsync_end_hold()"),
                    prepare = sprintf("%s_blank = Canvas()", canvas)),
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

# The setup's lines that measure the display and time the events and their codes.
#
# The frame period is measured once, as the median interval between 20 flips of a blank
# canvas. A median outside 1 to 50 ms, a refresh rate outside 20 to 1000 Hz, is a failed
# measurement, such as a backend without a blocking flip gives, and
# presentation.assumed_refresh_hz stands in for it. The period is logged as
# lexsync_frame_ms. An event ends half a period before its duration is up (see
# .osexp_event_block).
#
# The trigger device writes a code and returns. A code is held for
# triggers.trigger_hold_ms, never less than .MIN_HOLD_MS, from the onset it marks:
# `_lexsync_onset` writes it and notes when it is due to be reset, and `_lexsync_wait`
# and `_lexsync_key` reset it on the way when that time comes no later than the time
# they wait for. A code that outlasts its event is therefore reset in a later event,
# without delaying any display, unless the next onset's code replaces it first, with a 0
# written just before. Before a wait that runs no code of lexsync's, a
# keyboard_response, `_lexsync_end_hold` waits out the rest of the hold.
# `_lexsync_marker` sends a session marker and holds it. The legacy clock the experiment
# selects counts and sleeps whole milliseconds, so a hold that ends during a wait lasts
# within a millisecond of what is asked. One that ends while show() waits for the next
# refresh lasts until that display, up to a frame longer. One that ends after the last
# wait of a trial lasts until the next trial's first display. Must match _osexp_timing
# in scripting.py.
.osexp_timing <- function(schema) {
  c("_c = Canvas()",
    "_d = [_c.show() for _i in range(21)]",
    "_d = sorted(_b - _a for _a, _b in zip(_d, _d[1:]))",
    "_LEXSYNC_FRAME = (_d[9] + _d[10]) / 2.0",
    "if not 1.0 < _LEXSYNC_FRAME < 50.0:",
    sprintf("    _LEXSYNC_FRAME = 1000.0 / %s", sprintf("%.17g", .refresh_hz(schema))),
    "var.lexsync_frame_ms = _LEXSYNC_FRAME",
    "_LEXSYNC_HALF_FRAME = _LEXSYNC_FRAME / 2.0",
    sprintf("_LEXSYNC_HOLD = %s", sprintf("%.17g", max(.trigger_hold_ms(schema), .MIN_HOLD_MS))),
    "_lexsync_due = [None]",
    "def _lexsync_until(t):",
    "    _left = t - clock.time()",
    "    if _left > 0:",
    "        clock.sleep(_left)",
    "def _lexsync_onset(code, t0):",
    "    if _lexsync_due[0] is not None:",
    "        send_trigger(0)",
    "    send_trigger(code)",
    "    _lexsync_due[0] = t0 + _LEXSYNC_HOLD",
    "def _lexsync_reset():",
    "    send_trigger(0)",
    "    _lexsync_due[0] = None",
    "def _lexsync_wait(t):",
    "    if _lexsync_due[0] is not None and _lexsync_due[0] <= t:",
    "        _lexsync_until(_lexsync_due[0])",
    "        _lexsync_reset()",
    "    _lexsync_until(t)",
    "def _lexsync_key(kb, t):",
    "    if _lexsync_due[0] is not None and (t is None or _lexsync_due[0] <= t):",
    "        _left = _lexsync_due[0] - clock.time()",
    "        if _left > 0:",
    "            _key, _t = kb.get_key(timeout=_left)",
    "            if _key is not None:",
    "                return _key, _t",
    "        _lexsync_reset()",
    "    return kb.get_key(timeout=None if t is None else max(0, t - clock.time()))",
    "def _lexsync_end_hold():",
    "    if _lexsync_due[0] is not None:",
    "        _lexsync_until(_lexsync_due[0])",
    "        _lexsync_reset()",
    "def _lexsync_marker(code):",
    "    _lexsync_onset(code, clock.time())",
    "    _lexsync_end_hold()")
}

# The setup's lines that open the trigger device, as triggers.mode and triggers.backend
# ask (see .trigger_settings). Only the configured backend's branch is written, and a
# serial device is opened by the name the schema gives. The setup used to set the backend
# to parallel on the line before a serial branch that took the first serial port it
# found. When the device cannot be opened, "hardware" stops the experiment before
# anything is shown, and "auto" falls back to printing the codes. `_lexsync_no_codes` is
# left holding the reason no codes will be sent, or None when they go to the device, for
# the notice (.osexp_trigger_notice). `lexsync_trigger_mode`, which the logger writes
# with every trial, says "hardware" or "mock", and `test_mode` says "yes" with the mock,
# as it did. Must match _osexp_trigger_device in scripting.py.
.osexp_trigger_device <- function(settings, address) {
  if (identical(settings$backend, "serial")) {
    record <- "var.trigger_backend = u'serial'"
    opening <- c("        import serial",
                 sprintf("        _sp = serial.Serial(%s, %d)", .pyq(settings$serial_port),
                         settings$baudrate),
                 "        def send_trigger(code):",
                 "            _sp.write(int(code).to_bytes(1, 'big'))")
  } else {
    record <- c("var.trigger_backend = u'parallel'",
                sprintf("var.parallel_port_address = %s", address))
    opening <- c("        from ctypes import windll",
                 "        _io = windll.dlportio",
                 "        _addr = int(var.parallel_port_address)",
                 "        def send_trigger(code):",
                 "            _io.DlPortWritePortUchar(_addr, int(code))")
  }
  c(record,
    "var.test_mode = u'no'",
    "def _printer(code):",
    "    print(u'[lexsync test trigger] %d' % int(code))",
    "send_trigger = _printer",
    sprintf("_lexsync_mode = %s", .pyq(settings$mode)),
    sprintf("_lexsync_device = %s", .pyq(.trigger_device(settings, address))),
    "_lexsync_no_codes = None",
    "if _lexsync_mode == u'mock':",
    "    _lexsync_no_codes = u'triggers.mode is mock'",
    "else:",
    "    try:",
    opening,
    "        send_trigger(0)",
    "    except Exception as _exc:",
    "        if _lexsync_mode == u'hardware':",
    paste0("            raise RuntimeError(u'lexsync: %s could not be opened (%s: %s). ",
           "triggers.mode is hardware, so the experiment does not run without it.' % ",
           "(_lexsync_device, type(_exc).__name__, _exc))"),
    paste0("        print(u'lexsync: %s could not be opened (%s: %s).' % ",
           "(_lexsync_device, type(_exc).__name__, _exc))"),
    "        send_trigger = _printer",
    "        _lexsync_no_codes = u'%s could not be opened' % _lexsync_device",
    "var.lexsync_trigger_mode = u'hardware' if _lexsync_no_codes is None else u'mock'",
    "if _lexsync_no_codes is not None:",
    "    var.test_mode = u'yes'",
    paste0("    print(u'lexsync: no trigger codes will be sent, because %s. Each code is ",
           "printed here instead.' % _lexsync_no_codes)"))
}

# The inline script that tells the experimenter that no trigger codes will be sent. It
# runs just after the setup, before any screen the participant sees, shows the reason
# the setup found and waits for C. Escape stops the session. When the codes go to the
# device, it shows nothing. The reason is a device name the schema's check allows or the
# mode, so it holds nothing OpenSesame's canvas would read as markup. Must match
# _osexp_trigger_notice in scripting.py.
.osexp_trigger_notice <- function() {
  body <- c(
    "if _lexsync_no_codes is not None:",
    "    c = Canvas()",
    paste0("    c.text(u'No trigger codes will be sent, because %s. Each code is printed in ",
           "the console instead.<br /><br />Press C to continue without triggers, or escape ",
           "to stop.' % _lexsync_no_codes)"),
    "    c.show()",
    "    _key, _t = Keyboard(keylist=[u'c', u'escape'], timeout=None).get_key()",
    "    if _key == u'escape':",
    paste0("        raise RuntimeError(u'lexsync: stopped at the trigger notice, because no ",
           "trigger codes would be sent.')"))
  .inline_block("lexsync_trigger_notice", "Say when no trigger codes will be sent", body)
}

# The two inline scripts that send the session markers, 254 just before the loop and
# 255 just after it, each held for the hold, as the PsychoPy script sends them. Must
# match _osexp_markers in scripting.py.
.osexp_markers <- function() {
  c(.inline_block("lexsync_session_start", "Mark the start of the trials with 254",
                  "_lexsync_marker(254)"),
    .inline_block("lexsync_session_end", "Mark the end of the trials with 255",
                  "_lexsync_marker(255)"))
}

# The inline script that checks the subject number against this file's version. A
# design with several presentation versions gets one experiment per version, and the
# experimenter opens the participant's. OpenSesame asks for a subject number at
# start-up, and participant p normally runs version ((p - 1) mod V) + 1. When the number
# belongs to another version, this shows a screen saying so and waits for a key. Space
# goes on with this file, and escape stops the session. It runs before the loop, so the
# experiment needs no run-if condition, a syntax that differs between OpenSesame 3.3
# and 4.x. With `n_orders` above 1, each experiment is one order of one version, and
# participant p normally runs order (((p - 1) div V) mod m) + 1, which the check compares
# too. Must match _osexp_version_check in scripting.py.
.osexp_version_check <- function(version, n_versions, order = 1L, n_orders = 1L) {
  if (n_orders > 1L) {
    body <- c(
      sprintf("_version = %d", as.integer(version)),
      sprintf("_versions = %d", as.integer(n_versions)),
      sprintf("_order = %d", as.integer(order)),
      sprintf("_orders = %d", as.integer(n_orders)),
      "try:",
      "    _p = int(var.get(u'subject_nr', 0, _eval=False))",
      "except (TypeError, ValueError):",
      "    _p = 0",
      "_expected = (_p - 1) % _versions + 1",
      "_expected_order = (_p - 1) // _versions % _orders + 1",
      "if (_expected, _expected_order) != (_version, _order):",
      "    c = Canvas()",
      paste0("    c.text(u'Participant %d would normally run version %d in order %d, and ",
             "this file runs version %d in order %d. Press space to continue with this ",
             "one or escape to stop.' % (_p, _expected, _expected_order, _version, ",
             "_order))"),
      "    c.show()",
      "    _key, _t = Keyboard(keylist=[u'space', u'escape'], timeout=None).get_key()",
      "    if _key == u'escape':",
      paste0("        raise RuntimeError(u'lexsync: stopped at the version check, because ",
             "participant %d would normally run version %d in order %d.' % (_p, ",
             "_expected, _expected_order))"))
    return(.inline_block("lexsync_version_check",
                         "Warn when the subject number belongs to another version or order",
                         body))
  }
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

# Text for OpenSesame's canvas, which reads a subset of HTML: &, < and > escaped, and
# each line break written as <br />. Mirrors _osexp_html in scripting.py.
.osexp_html <- function(text) {
  text <- gsub("&", "&amp;", text, fixed = TRUE)
  text <- gsub("<", "&lt;", text, fixed = TRUE)
  text <- gsub(">", "&gt;", text, fixed = TRUE)
  gsub("\n", "<br />", text, fixed = TRUE)
}

# The inline script that shows the instructions and waits for the space bar. It runs once,
# before the loop, so the participant reads at their own pace and the first trial starts
# on the space bar, which also lets the experimenter start the run. Escape stops the
# session, as it does at the version check. The text is written into the script as a
# .pyq literal, which escapes its line breaks, so it cannot add a line to the experiment.
# Must match _osexp_instructions in scripting.py.
.osexp_instructions <- function(text) {
  body <- c(
    "c = Canvas()",
    sprintf("c.text(%s)", .pyq(paste0(.osexp_html(text), "<br /><br />", .START_PROMPT))),
    "c.show()",
    "_key, _t = Keyboard(keylist=[u'space', u'escape'], timeout=None).get_key()",
    "if _key == u'escape':",
    "    raise RuntimeError(u'lexsync: stopped at the instructions.')")
  .inline_block("lexsync_instructions", "Show the instructions and wait for the space bar",
                body)
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
#' @param instructions The text the experiment shows before the loop, waiting for the
#'   space bar. `NULL` (the default) takes list 1's, the design's own `instructions` or
#'   lexsync's for its task.
#' @param order,n_orders The experiment presents trial order `order` of `n_orders`.
#'   With more than one order, the check compares the participant's order too, and the
#'   experiment sets `lexsync_order`, which every trial logs.
#' @return The experiment's text, one string. Each trial starts by clearing the last
#'   trial's responses and ends with a logger item. The setup script opens the trigger
#'   device the schema names, measures the frame period and defines the helpers that
#'   time the events and hold their codes. A notice follows it when no codes will be
#'   sent, and the session markers 254 and 255 are sent just before and after the loop.
#'   Every text is drawn at `presentation.text_height_px`.
#' @keywords internal
build_osexp <- function(design, conditions_file, schema, rendered, font = "mono",
                        text_file = NULL, version = NULL, n_versions = NULL,
                        instructions = NULL, order = 1L, n_orders = 1L) {
  instructions <- instructions %||% .instructions(design, .response_mapping(design))
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
    # The device writes a code and returns. The scripts reset it when its hold is up
    # (see .osexp_timing). It used to sleep 10 ms and reset the code itself, so every
    # triggered event overran by those 10 ms and the schema's hold was ignored.
    .osexp_trigger_device(.trigger_settings(schema), addr),
    .osexp_timing(schema)
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
    # OpenSesame takes full screen from the mode it is launched in, whatever this line
    # says. font_size is the size of every text the experiment shows.
    "set fullscreen no", "set foreground white",
    sprintf("set font_size %d", .text_height_px(schema)),
    sprintf("set font_family %s", font), 'set description "Generated by lexsync"',
    "set coordinates uniform", "set compensation 0", "set color_backend legacy",
    "set clock_backend legacy", "set canvas_backend xpyriment", "set background black",
    # The trial order this experiment presents, logged with every trial.
    if (n_orders > 1L) sprintf("set lexsync_order %d", as.integer(order)), "",
    "define inline_script lexsync_trigger_setup",
    '\tset description "Load the trial texts and open the trigger device"',
    '\tset _run ""', "\t___prepare__", paste0("\t", setup), "\t__end__", ""
  )
  checked <- !is.null(version) && !is.null(n_versions) &&
    (as.integer(n_versions) > 1L || n_orders > 1L)
  check <- if (checked) .osexp_version_check(version, n_versions, order, n_orders) else
    character(0)
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
    "\trun lexsync_trigger_notice always",
    if (checked) "\trun lexsync_version_check always",
    "\trun lexsync_instructions always",
    "\trun lexsync_session_start always",
    "\trun lexsync_loop always",
    "\trun lexsync_session_end always", ""
  )
  paste(c(header, .osexp_trigger_notice(), check, .osexp_instructions(instructions),
          .osexp_markers(), event_blocks, trial), collapse = "\n")
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
#' Before the loop, an inline script, `lexsync_instructions`, shows the design's
#' `instructions`, or lexsync's for its task, and waits for the space bar. Every trial
#' is logged. A response after a text event is collected by that event's
#' script from the stimulus's onset, which sets `response`, `response_time`,
#' `timed_out` and `correct`. A response kept after the stimulus with `from: offset` is
#' a keyboard_response, and a script after it sets `timed_out` and `correct`.
#' Self-paced reading sets `lexsync_region_rts` and a question `question_response` and
#' `question_rt`. A script clears these as each trial starts, another copies the
#' trial's labels into `lexsync_condition`, `lexsync_block` and `lexsync_answer`, and a
#' logger item ends the trial.
#'
#' Every canvas a trial shows is built before the trial runs, in the prepare phase of its
#' script, and each event is timed from the onset its display returns. An event ends
#' half a frame before its duration is up, so that the next display lands on the refresh
#' that ends it. The frame period is measured at start-up and logged as
#' `lexsync_frame_ms`, with `presentation.assumed_refresh_hz` as the fallback when the
#' measurement fails. Each trigger code is held for `triggers.trigger_hold_ms`, at least
#' 10 ms, through the events after it when its own is shorter, unless the next onset's
#' code replaces it first. The session markers, 254 and 255, are sent just before the
#' first trial and just after the last, held the same way.
#'
#' The setup writes the codes to the parallel port at `triggers.parallel_address` or,
#' with `triggers.backend: serial`, as single bytes to `triggers.serial_port` at
#' `triggers.baudrate`. When that device cannot be opened, `triggers.mode: auto` prints
#' the codes instead. An inline script, `lexsync_trigger_notice`, then says so before
#' any other screen and waits for the C key. `hardware` stops the experiment there, and
#' `mock` prints the codes without trying the device. Every trial logs
#' `lexsync_trigger_mode`, `hardware` or `mock`. Text is drawn
#' `presentation.text_height_px` pixels high, OpenSesame's `font_size`, and OpenSesame
#' takes full screen from the mode it is launched in.
#'
#' A design with more than one presentation version, one per (replicate, list) pair
#' of the trials, gets one experiment per version instead, each with its own two
#' tables holding only that version's trials: `<base>_list<k>.osexp`, or
#' `<base>_rep<r>_list<k>.osexp` when the versions span several replicates. Each one
#' checks OpenSesame's subject number at start-up and shows a warning when that
#' participant would normally run another version. A design with
#' `counterbalance.orders: m` gets one experiment per version and order,
#' `<base>_list<k>_order<j>.osexp` (`<base>_order<j>.osexp` for a single version), each
#' with tables sorted by its order, a `lexsync_order` variable that every trial logs,
#' and a check that compares the participant's order too, order
#' `(((p - 1) div V) mod m) + 1`. [export_experiments()] lists every file written.
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
  # Sized from every version's trials, so each version's experiment shows one mask.
  rendered <- .sized_masks(
    render_events(events, design[["timing"]] %||% list(), .refresh_hz(schema)), stimuli)
  presentation <- schema[["presentation"]] %||% list()
  font <- design[["font"]] %||% presentation[["opensesame_font"]] %||% "mono"
  versions <- .presentation_versions(stimuli)
  texts <- .instruction_texts(design, versions)
  n_orders <- .n_orders(stimuli)
  parts <- if (length(versions) <= 1L && n_orders == 1L) {
    # One version keeps the file names an experiment has always had.
    list(list(stem = base, rows = stimuli, version = NULL,
              instructions = if (length(texts)) texts[[1]] else NULL, order = 1L))
  } else {
    by_replicate <- .spans_replicates(versions)
    unlist(lapply(seq_along(versions), function(k) {
      v <- versions[[k]]
      stem <- if (length(versions) == 1L) base
              else if (by_replicate) sprintf("%s_rep%d_list%d", base, v[["replicate"]], v[["list"]])
              else sprintf("%s_list%d", base, v[["list"]])
      rows <- .version_rows(stimuli, v)
      if (n_orders == 1L) {
        return(list(list(stem = stem, rows = rows, version = v[["version"]],
                         instructions = texts[[k]], order = 1L)))
      }
      # OpenSesame's loop presents its table in file order, so each order of a version
      # is an experiment of its own, its tables sorted by that order.
      lapply(seq_len(n_orders), function(j) {
        list(stem = sprintf("%s_order%d", stem, j), rows = .rows_in_order(rows, j),
             version = v[["version"]], instructions = texts[[k]], order = j)
      })
    }), recursive = FALSE)
  }
  written <- lapply(parts, function(p) {
    csv_name <- paste0(p[["stem"]], "_opensesame.csv")
    text_name <- paste0(p[["stem"]], "_opensesame_text.csv")
    list(stem = p[["stem"]], csv_name = csv_name, text_name = text_name,
         tables = .opensesame_tables(p[["rows"]], events),
         osexp = build_osexp(design, csv_name, schema, rendered, font = font,
                             text_file = text_name, version = p[["version"]],
                             n_versions = length(versions),
                             instructions = p[["instructions"]], order = p[["order"]],
                             n_orders = n_orders))
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

# The loop table with each trial's `answer` named as the browser names the key. jsPsych
# records the key pressed by the browser's name for it, so a press of the left arrow is
# recorded as `arrowleft`, the name the page's events give the key (see
# .map_keys_jspsych()). The loop tables name it `left`, as PsychoPy and OpenSesame record
# it. The page's answers are named as its keys are, so a correct response equals its
# trial's answer, in the data rows and on the feedback screen. The spaces the runners
# ignore around an answer are ignored here too. Mirrors _map_answers_for_jspsych in
# scripting.py.
.map_answers_jspsych <- function(trials) {
  answer <- trials[["answer"]]
  if (!is.character(answer)) return(trials)
  browser <- .JSPSYCH_KEYS[trimws(answer)]
  trials[["answer"]] <- ifelse(is.na(answer) | is.na(browser), answer, unname(browser))
  trials
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
#' locally, so no server is required either to run it or to collect them. Each of the
#' three files carries its SHA-384 as Subresource Integrity, so a browser refuses a copy
#' that differs from the published release. Stimuli are drawn
#' `presentation.text_height_px` pixels high, 48 by default. Onset
#' triggers are recorded in each trial's data (a browser cannot drive a parallel
#' port). A stimulus that collects its response is one trial, recorded as `target`:
#' it accepts the keys from its onset, shows the stimulus for its duration and stays
#' open for the timeout after it, a key ends it, and `rt` runs from the onset.
#'
#' The page embeds every presentation version of the design, one per (replicate,
#' list) pair, and runs one, named in its address: `?version=K`, `?list=K` when there
#' are no replicates, or `?participant=N`, whose version is `((N - 1) mod V) + 1`. A
#' page with more than one version, opened with none of these, shows a screen naming
#' them and runs nothing. With `counterbalance.orders: m` the page presents the version
#' in order `(((N - 1) div V) mod m) + 1`, or in order 1 without a participant number,
#' and every data row carries the order. Its welcome screen shows the version's
#' instructions, the
#' design's `instructions` or lexsync's for its task, and waits for the space bar. The
#' data rows carry the participant, the version, the list and the replicate, and the
#' data file is named after the participant and the version. The page names the keys
#' as the browser does, `arrowleft` for `left`, in its events and in each trial's
#' `answer`, so a recorded response can be compared with the answer as it stands.
#'
#' @inheritParams export_psychopy
#' @return The path to the generated `.html`, invisibly.
#' @importFrom jsonlite toJSON
#' @export
export_jspsych <- function(stimuli, design, schema, outdir, base = NULL) {
  base <- base %||% design_stem(design)
  events <- resolve_events(design)
  rendered <- .map_keys_jspsych(.sized_masks(
    render_events(events, design[["timing"]] %||% list(), .refresh_hz(schema)), stimuli))
  versions <- .presentation_versions(stimuli)
  trials <- .map_answers_jspsych(loop_table(stimuli, events))
  presentation <- schema[["presentation"]] %||% list()
  font <- design[["font"]] %||% presentation[["font"]] %||% "Courier New"
  tmpl <- paste(readLines(find_template("jspsych/experiment_template.html"), warn = FALSE),
                collapse = "\n")
  subs <- list(
    DESIGN = clean_meta(design[["name"]], "the design's `name`"),
    LANGUAGE = clean_meta(design[["language"]], "the design's `language`"),
    LANGUAGE_TAG = .language_tag(design), WORD_FONT = clean_meta(font, "the font"),
    TEXT_HEIGHT_PX = as.character(.text_height_px(schema)),
    EVENTS_JSON = .json_html(jsonlite::toJSON(rendered, auto_unbox = TRUE)),
    # Each double to 15 significant digits, the digits the Python engine writes
    # (_fifteen_digits in scripting.py). The default of four decimal places wrote
    # 33.3333 for an item table's 33.333333, where Python wrote every digit, so the two
    # engines' pages differed. I(15), not digits = NA, which jsonlite 1.8.5 and 1.8.6
    # wrote to 17 digits; I(15) is "%.15g" in every version, and DESCRIPTION sets no
    # floor on jsonlite.
    TRIALS_JSON = .json_html(jsonlite::toJSON(trials, dataframe = "rows", digits = I(15))),
    VERSIONS_JSON = .json_html(jsonlite::toJSON(versions, auto_unbox = TRUE)),
    ORDERS = as.character(.n_orders(stimuli)),
    INSTRUCTIONS_JSON = .json_html(jsonlite::toJSON(as.list(.instruction_texts(design, versions)),
                                                    auto_unbox = TRUE))
  )
  for (k in names(subs)) {
    tmpl <- gsub(sprintf("{{%s}}", k), as.character(subs[[k]]), tmpl, fixed = TRUE)
  }
  out <- file.path(outdir, paste0(base, ".html"))
  write_lines_lf(tmpl, out)
  invisible(out)
}

# ---- Instructions and the response mapping ----------------------------------------
#
# Every experiment shows instructions and waits for the space bar before its first trial.
# A design may give its own text, which travels as data: JSON in the PsychoPy script and
# the jsPsych page, and a .pyq literal in the OpenSesame script. Without one, lexsync
# writes English instructions for the tasks it knows. The loop tables carry each trial's
# correct key in `answer`, taken from the response mapping where the trial names none.
# Mirrors the section of the same name in scripting.py.

# The prompt every target shows below the instructions. It and the runners' other
# messages are in English. Must match both templates and _START_PROMPT in scripting.py.
.START_PROMPT <- "Press the space bar to begin."

# The names the instructions give the keys that are more than one character.
.KEY_LABELS <- c(space = "the space bar", left = "the left arrow key",
                 right = "the right arrow key", up = "the up arrow key",
                 down = "the down arrow key", "return" = "the Enter key")

.MAPPING_SHAPE <- paste("lexsync: response_mapping must map each condition to one response",
                        "key, as in {word: f, pseudoword: j}.")

# A response key as the instructions and the Methods text name it. A single character is
# upper-cased, as a keyboard prints it (F, J, 1), and the arrow keys, the space bar and
# Enter are named. Any other key is "the <name> key". Key names are ASCII (see
# clean_key()), so the two engines upper-case them alike. Mirrors _key_label in
# scripting.py.
.key_label <- function(key) {
  key <- as.character(key)
  if (key %in% names(.KEY_LABELS)) return(unname(.KEY_LABELS[[key]]))
  if (nchar(key) == 1L) toupper(key) else sprintf("the %s key", key)
}

# Words joined as a list in prose: "a", "a or b", "a, b or c". Mirrors _join_words in
# scripting.py.
.join_words <- function(parts, conjunction) {
  parts <- as.character(unlist(parts, use.names = FALSE))
  n <- length(parts)
  if (n < 2L) return(paste(parts, collapse = ""))
  paste(paste(parts[-n], collapse = ", "), conjunction, parts[n])
}

# The first event of a type, or NULL.
.first_event <- function(events, kind) {
  for (ev in events) if (identical(ev[["type"]], kind)) return(ev)
  NULL
}

# The keys the design's first response event allows, or NULL without one.
.response_keys <- function(design) {
  ev <- .first_event(resolve_events(design), "response")
  if (is.null(ev)) NULL else .keys_of(ev, c("left", "right"))
}

# The design's own `instructions`, checked, or NULL when it gives none. Free text, which
# may hold line breaks and no other control character: not the C0 and C1 controls, and
# not the two Unicode separators, which end a line in JavaScript before ES2019 and in
# Python's str.splitlines(), so they could split the OpenSesame script the text is
# written into. The code points are read with utf8ToInt(), so the check does not depend
# on the locale. Spaces and line breaks at either end are trimmed, so the closing line
# break of a YAML block scalar adds no empty line. Must stay identical to
# _design_instructions in scripting.py.
.design_instructions <- function(design) {
  value <- design[["instructions"]]
  if (is.null(value)) return(NULL)
  if (!is.character(value) || length(value) != 1L || is.na(value)) {
    stop("lexsync: the design's `instructions` must be text.", call. = FALSE)
  }
  codes <- utf8ToInt(enc2utf8(value))
  bad <- codes[(codes <= 0x1fL & codes != 0x0aL) | (codes >= 0x7fL & codes <= 0x9fL) |
                 codes %in% c(0x2028L, 0x2029L)]
  if (length(bad)) {
    stop(sprintf(paste("lexsync: the design's `instructions` contain the control character",
                       "U+%04X; only line breaks are allowed."), bad[1]), call. = FALSE)
  }
  text <- sub("[ \n]+$", "", sub("^[ \n]+", "", value))
  if (!nzchar(text)) {
    stop(paste("lexsync: the design's `instructions` are empty; write the text or leave the",
               "key out."), call. = FALSE)
  }
  text
}

# The design's response mapping, list(condition = key), or NULL when it has none. A
# design's own `response_mapping` maps each condition to a key that its first response
# event allows. Without one, a lexical decision maps word to that event's first key and
# pseudoword to its second, the order in which its practice table codes them, so its
# main trials can be scored. No other paradigm has a default. Must stay identical to
# _response_mapping in scripting.py.
.response_mapping <- function(design) {
  keys <- .response_keys(design)
  given <- design[["response_mapping"]]
  if (is.null(given)) {
    if (identical(design[["paradigm"]], "lexical_decision") && !is.null(keys) &&
        length(keys) >= 2L) {
      return(list(word = keys[[1]], pseudoword = keys[[2]]))
    }
    return(NULL)
  }
  if (!.is_mapping(given) || !length(given)) stop(.MAPPING_SHAPE, call. = FALSE)
  if (is.null(keys)) {
    stop(paste("lexsync: the design gives `response_mapping`, but none of its events is a",
               "response whose keys it could name."), call. = FALSE)
  }
  out <- list()
  for (i in seq_along(given)) {
    key <- given[[i]]
    if (is.null(key) || is.list(key) || is.logical(key) || length(key) != 1L ||
        is.na(key) || !(is.character(key) || is.numeric(key))) {
      stop(.MAPPING_SHAPE, call. = FALSE)
    }
    key <- clean_key(key, "a key in response_mapping")
    cond <- names(given)[i]
    if (!(key %in% keys)) {
      stop(sprintf(paste("lexsync: response_mapping maps '%s' to '%s', but the response",
                         "event allows only %s."), cond, key, .join_words(keys, "and")),
           call. = FALSE)
    }
    out[[cond]] <- key
  }
  out
}

# Whether the design rotates its response mapping across lists, checked.
.rotates <- function(design) {
  value <- design[["rotate_mapping_by_list"]]
  if (is.null(value)) return(FALSE)
  if (!is.logical(value) || length(value) != 1L || is.na(value)) {
    stop("lexsync: rotate_mapping_by_list must be true or false.", call. = FALSE)
  }
  value
}

# The response mapping in list `lst`. Rotated, list k moves each key k - 1 places along
# the response event's keys, so with two keys every even-numbered list swaps them.
# Mirrors _list_mapping in scripting.py.
.list_mapping <- function(design, mapping, lst) {
  if (is.null(mapping) || !.rotates(design)) return(mapping)
  keys <- .response_keys(design)
  lapply(mapping, function(k) {
    keys[[((match(k, keys) - 1L + as.integer(lst) - 1L) %% length(keys)) + 1L]]
  })
}

# Refuse instructions, a response mapping or a rotation the experiments cannot carry.
# validate_design() calls this. Mirrors _check_instructions_and_mapping in scripting.py.
.check_instructions_and_mapping <- function(design) {
  .design_instructions(design)
  mapping <- .response_mapping(design)
  if (.rotates(design) && is.null(mapping)) {
    stop(paste("lexsync: rotate_mapping_by_list rotates a response mapping, and the design",
               "has none; give `response_mapping`."), call. = FALSE)
  }
  invisible(NULL)
}

# lexsync's English instructions for a design that gives none, as list(text, explained):
# the text, and whether it says what every key the participant presses means. A lexical
# decision names the keys its mapping gives word and pseudoword. A categorisation says
# that the first key of its response means yes and the second no, and a comprehension
# question says the same of its keys. Self-paced reading names the key that shows the
# next part. Any other response is only named, so the text cannot say what its keys
# mean, which is all a factorial or priming design gets. A design with neither a
# response nor a question is told what it will see. Must stay identical to
# _default_instructions in scripting.py.
.default_instructions <- function(design, mapping) {
  events <- resolve_events(design)
  paradigm <- design[["paradigm"]] %||% "factorial"
  keys <- .response_keys(design)
  region <- .first_event(events, "region_by_region")
  question <- .first_event(events, "question")
  key_labels <- function(k) vapply(k, .key_label, character(1), USE.NAMES = FALSE)
  parts <- character(0)
  explained <- TRUE
  if (identical(paradigm, "lexical_decision") && !is.null(mapping) &&
      !is.null(mapping[["word"]]) && !is.null(mapping[["pseudoword"]])) {
    parts <- c(parts, sprintf(paste("You will see a string of letters. Press %s if it is a",
                                    "real English word and %s if it is not."),
                              .key_label(mapping[["word"]]), .key_label(mapping[["pseudoword"]])))
  } else if (identical(paradigm, "categorisation") && !is.null(keys) && length(keys) == 2L) {
    parts <- c(parts, sprintf(paste("You will see a category and then a word. Press %s for",
                                    "yes if the word belongs to the category and %s for no",
                                    "if it does not."),
                              .key_label(keys[[1]]), .key_label(keys[[2]])))
  } else if (!is.null(keys)) {
    parts <- c(parts, sprintf("When a response is needed, press %s.",
                              .join_words(key_labels(keys), "or")))
    explained <- FALSE
  }
  if (!is.null(region)) {
    parts <- c(parts, sprintf(paste("You will read each sentence one part at a time. Press",
                                    "%s to see the next part."),
                              .key_label(region[["advance"]] %||% "space")))
  }
  if (!is.null(question)) {
    qkeys <- .keys_of(question, c("f", "j"))
    if (length(qkeys) == 2L) {
      parts <- c(parts, sprintf("Answer each question by pressing %s for yes and %s for no.",
                                .key_label(qkeys[[1]]), .key_label(qkeys[[2]])))
    } else {
      parts <- c(parts, sprintf("Answer each question by pressing %s.",
                                .join_words(key_labels(qkeys), "or")))
      explained <- FALSE
    }
  }
  if (!is.null(keys)) parts <- c(parts, "Respond as quickly and accurately as you can.")
  if (!length(parts)) parts <- "You will see items presented one at a time on the screen."
  list(text = paste(parts, collapse = " "), explained = explained)
}

# The instructions shown with `mapping`, one list's response mapping: the design's own
# text, or lexsync's.
.instructions <- function(design, mapping) {
  .design_instructions(design) %||% .default_instructions(design, mapping)$text
}

# The instructions each presentation version shows, in version order, as a character
# vector. A mapping rotated across lists names each list's keys, so the texts can differ
# from one version to the next. Mirrors _instruction_texts in scripting.py.
.instruction_texts <- function(design, versions) {
  mapping <- .response_mapping(design)
  vapply(versions, function(v) .instructions(design, .list_mapping(design, mapping, v[["list"]])),
         character(1))
}

# The run-log notes on a design's instructions, in the order the run log gives them. A
# design that gives none shows lexsync's, which are in English, so a design in another
# language is told so. One whose response keys lexsync cannot explain is told that its
# experiments only name them, as a factorial or priming design's do. A design that
# rotates its mapping across lists and gives its own text is reminded that the text is
# the same in every list. Mirrors _instruction_notes in scripting.py.
.instruction_notes <- function(design) {
  notes <- character(0)
  if (is.null(.design_instructions(design))) {
    primary <- tolower(strsplit(.language_tag(design), "-", fixed = TRUE)[[1]][1])
    if (!identical(primary, "en")) {
      notes <- c(notes, sprintf(paste(
        "lexsync: the design gives no `instructions` and its language is '%s', so the",
        "experiments show lexsync's instructions in English; give `instructions` in the",
        "participants' language."), design[["language"]]))
    }
    if (!.default_instructions(design, .response_mapping(design))$explained) {
      notes <- c(notes, sprintf(paste(
        "lexsync: the design gives no `instructions`, and lexsync cannot tell what the",
        "response keys of a %s design mean, so the experiments only name the keys; give",
        "`instructions` that say what each key means."),
        design[["paradigm"]] %||% "factorial"))
    }
  } else if (.rotates(design) && !is.null(.response_mapping(design))) {
    notes <- c(notes, paste("lexsync: the response keys rotate across lists, but the",
                            "design's `instructions` are the same in every list, so they",
                            "should not name the keys."))
  }
  notes
}

# A trial's own answer as the text its loop-table cell holds, or NA when it names none. A
# table's answer column is typed by its values, so a practice table that codes its
# answers as number keys is read as numbers. Such an answer is the text
# write_csv_utf8() gives it, 100000 where as.character() gives 1e+05, and so the text the
# Python engine gives it. Text is kept as it is. Mirrors _answer_text in scripting.py.
.answer_text <- function(x) {
  if (is.character(x)) return(x)
  if (!length(x)) return(character(0))
  one <- data.frame(answer = x)
  .check_csv_writable(one)
  # One line per cell: a number or a logical needs no quoting, and strsplit() drops only
  # the piece after the last line's end, so a missing answer stays an empty line.
  cells <- strsplit(readr::format_csv(one, na = "", col_names = FALSE), "\n",
                    fixed = TRUE)[[1]]
  cells[!nzchar(cells)] <- NA_character_
  cells
}

# A trial's own answer, trimmed, or NA when it names none. trimws() removes the
# characters _answer_given in scripting.py strips.
.answer_given <- function(x) {
  s <- trimws(.answer_text(x))
  s[!is.na(s) & !nzchar(s)] <- NA_character_
  s
}

# Fill each trial's `answer` from the response mapping, where the trial names none.
# Returns list(stimuli, notes), the trials with their answers and the run-log notes. A
# trial that names its own answer, such as a practice or filler trial, keeps it as text
# (see .answer_text()), and a note counts the trials whose answer contradicts the mapping
# for their condition and list. With rotation, each trial takes its list's mapping. A
# design's own mapping is refused when it gives no key for a condition whose trials name
# no answer, or names a condition no trial has, since both are typing errors that would
# leave trials unscored. The lexical-decision default maps word and pseudoword only, and
# a note counts the trials of any other condition it leaves without an answer. Without a
# mapping, the trials come back as they came. export_experiments() applies this as it
# assigns the trigger codes, so the stimuli file does not change. Must stay identical to
# _assign_answers in scripting.py.
.assign_answers <- function(stimuli, design) {
  mapping <- .response_mapping(design)
  if (is.null(mapping)) return(list(stimuli = stimuli, notes = character(0)))
  n <- nrow(stimuli)
  lists <- .version_key(stimuli, "list")
  conditions <- as.character(stimuli[["condition"]])
  own <- .answer_text(if ("answer" %in% names(stimuli)) stimuli[["answer"]]
                      else rep(NA_character_, n))
  have <- .answer_given(own)
  blocks <- if ("block" %in% names(stimuli)) as.character(stimuli[["block"]])
            else rep(NA_character_, n)
  by_list <- stats::setNames(lapply(unique(lists), function(l) .list_mapping(design, mapping, l)),
                             as.character(unique(lists)))
  want <- vapply(seq_len(n), function(i) {
    key <- by_list[[as.character(lists[i])]][[conditions[i]]]
    if (is.null(key)) NA_character_ else key
  }, character(1))
  answers <- ifelse(is.na(have), want, own)
  conflict <- !is.na(have) & !is.na(want) & have != want
  missing <- is.na(have) & is.na(want)
  if (!is.null(design[["response_mapping"]])) {
    if (any(missing)) {
      cond <- conditions[missing][1]
      stop(sprintf(paste("lexsync: response_mapping gives no key for condition '%s', and %d",
                         "trial(s) of it have no answer of their own."),
                   cond, sum(missing & conditions == cond)), call. = FALSE)
    }
    present <- unique(conditions)
    stray <- setdiff(names(mapping), present)
    if (length(stray)) {
      stop(sprintf(paste("lexsync: response_mapping names condition '%s', which no trial has;",
                         "the trials' conditions are %s."),
                   stray[1], .join_words(present, "and")), call. = FALSE)
    }
  }
  several <- length(unique(lists)) > 1L
  notes <- character(0)
  if (any(conflict)) {
    key <- paste(blocks, lists, conditions, have, want, sep = "\x1f")[conflict]
    rows <- which(conflict)
    for (j in which(!duplicated(key))) {
      i <- rows[j]
      notes <- c(notes, sprintf(paste("lexsync: %d %strial(s) of condition '%s'%s keep their",
                                      "answer '%s', where the response mapping gives '%s'."),
                                sum(key == key[j]),
                                if (is.na(blocks[i])) "" else paste0(blocks[i], " "),
                                conditions[i],
                                if (several) sprintf(" in list %d", lists[i]) else "",
                                have[i], want[i]))
    }
  }
  for (cond in unique(conditions[missing])) {
    notes <- c(notes, sprintf(paste("lexsync: %d trial(s) of condition '%s' have no answer,",
                                    "since the lexical-decision default maps only word and",
                                    "pseudoword; give `response_mapping`."),
                              sum(missing & conditions == cond), cond))
  }
  stimuli$answer <- answers
  list(stimuli = stimuli, notes = notes)
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
#' Each trial that names no `answer` of its own takes the key the design's response
#' mapping gives its condition in its list, so the loop tables can score every trial.
#' A lexical decision maps word to its response event's first key and pseudoword to
#' its second unless the design gives `response_mapping`, and
#' `rotate_mapping_by_list: true` rotates the keys across lists. A practice or filler
#' trial keeps the answer its table gives. The stimuli passed in are not changed. Every
#' target shows the design's `instructions`, or lexsync's English instructions for its
#' task, and waits for the space bar before the first trial.
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
  stimuli <- .assign_answers(stimuli, design)$stimuli
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
