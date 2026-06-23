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
#' "item", or carry their own integer codes.
#'
#' @param stimuli A stimuli data frame.
#' @return `stimuli` with trigger columns added.
#' @export
assign_triggers <- function(stimuli) {
  conds <- unique(stimuli$condition)
  stimuli$condition_trigger <- 100L + match(stimuli$condition, conds)
  sets <- unique(stimuli$set)
  sets <- sets[order(as.character(sets), method = "radix")]
  code <- 40L + ((seq_along(sets) - 1L) %% 200L)
  stimuli$item_trigger <- code[match(stimuli$set, sets)]
  stimuli
}

#' @keywords internal
trigger_spec <- function(value) {
  if (is.null(value)) return(NULL)
  if (identical(value, "condition")) return("@condition_trigger")
  if (identical(value, "item")) return("@item_trigger")
  as.integer(value)
}

#' Translate paradigm events into backend-neutral rendering dictionaries
#' @keywords internal
render_events <- function(events, timing) {
  fix <- timing$fixation_frames
  word <- timing$word_frames
  isi <- timing$isi_frames
  out <- list()
  for (ev in events) {
    t <- ev$type
    r <- list(type = if (identical(t, "region_by_region")) "region" else t)
    if (t %in% c("fixation", "text", "mask")) {
      f <- content_field(ev$content)
      if (!is.null(f)) r$field <- f else r$text <- as.character(ev$content %||% "")
      frames <- ev$duration_frames %||% 1L
      if (t == "fixation" && !is.null(fix)) {
        frames <- fix
      } else if (t == "text" && identical(ev$trigger, "condition") && !is.null(word)) {
        frames <- word
      }
      r$frames <- as.integer(frames)
      spec <- trigger_spec(ev$trigger)
      if (!is.null(spec)) r$trigger <- spec
    } else if (t == "blank") {
      r$frames <- as.integer(if (!is.null(isi)) isi else (ev$duration_frames %||% 1L))
    } else if (t == "region_by_region") {
      r$field <- content_field(ev$content)
      r$sep <- ev$sep %||% "|"
      r$key <- ev$advance %||% "space"
      spec <- trigger_spec(ev$critical_region_trigger)
      if (!is.null(spec)) r$crit_trigger <- spec
    } else if (t == "response") {
      r$keys <- ev$keys %||% c("left", "right")
      r$timeout <- round((ev$timeout_ms %||% 2000) / 1000, 3)
    } else if (t == "question") {
      r$field <- content_field(ev$content)
      r$keys <- ev$keys %||% c("f", "j")
      r$timeout <- round((ev$timeout_ms %||% 5000) / 1000, 3)
    } else {
      stop(sprintf("lexsync: unknown event type '%s'.", t), call. = FALSE)
    }
    out[[length(out) + 1L]] <- r
  }
  out
}

#' Per-trial table carrying exactly the fields the events reference
#' @keywords internal
loop_table <- function(stimuli, events = NULL) {
  fields <- if (!is.null(events)) referenced_fields(events) else
    (if ("word" %in% names(stimuli)) "word" else character(0))
  order_cols <- c("trial", "list", "set", "condition", fields,
                  "critical_region", "answer", "condition_trigger", "item_trigger")
  cols <- character(0)
  for (c in order_cols) if (c %in% names(stimuli) && !(c %in% cols)) cols <- c(cols, c)
  tab <- stimuli[, cols, drop = FALSE]
  if ("trial" %in% names(tab)) tab <- tab[order(tab$trial), , drop = FALSE]
  rownames(tab) <- NULL
  tab
}

#' Export a runnable PsychoPy script that interprets the event sequence
#'
#' @param stimuli Stimuli with trigger columns (see [assign_triggers()]).
#' @param design A parsed design configuration.
#' @param schema The parsed global schema (trigger and presentation settings).
#' @param outdir Output directory.
#' @param base Optional file-name stem.
#' @return The path to the generated `.py`, invisibly.
#' @importFrom jsonlite toJSON
#' @export
export_psychopy <- function(stimuli, design, schema, outdir, base = NULL) {
  base <- base %||% slugify(design$name, design$language)
  events <- resolve_events(design)
  rendered <- render_events(events, design$timing %||% list())
  csv_name <- paste0(base, "_psychopy.csv")
  write_csv_utf8(loop_table(stimuli, events), file.path(outdir, csv_name))
  tmpl <- paste(readLines(find_template("psychopy/trial_runner_template.py"), warn = FALSE),
                collapse = "\n")
  triggers <- schema$triggers %||% list()
  presentation <- schema$presentation %||% list()
  subs <- list(
    DESIGN = design$name, LANGUAGE = design$language, CONDITIONS_FILE = csv_name,
    TRIGGER_ADDRESS = triggers$parallel_address %||% "0x0378",
    RESET_AFTER_FRAMES = triggers$reset_after_frames %||% 2,
    INTER_TRIGGER_S = (triggers$inter_trigger_ms %||% 10) / 1000,
    WORD_FONT = design$font %||% presentation$font %||% "Courier New",
    FULLSCREEN = "False",
    EVENTS_JSON = as.character(jsonlite::toJSON(rendered, auto_unbox = TRUE))
  )
  for (k in names(subs)) {
    tmpl <- gsub(sprintf("{{%s}}", k), as.character(subs[[k]]), tmpl, fixed = TRUE)
  }
  out <- file.path(outdir, paste0(base, "_psychopy.py"))
  writeLines(tmpl, out, useBytes = TRUE)
  invisible(out)
}

# ---- OpenSesame code generation ------------------------------------------

.pyq <- function(s) {
  s <- gsub("\\", "\\\\", s, fixed = TRUE)
  s <- gsub("'", "\\'", s, fixed = TRUE)
  paste0("u'", s, "'")
}

.content_expr <- function(ev) if (!is.null(ev$field)) paste0("var.", ev$field) else .pyq(ev$text %||% "")

.trigger_expr <- function(spec) {
  if (is.null(spec)) return(NULL)
  if (is.character(spec) && startsWith(spec, "@")) return(paste0("var.", substring(spec, 2)))
  as.character(as.integer(spec))
}

.inline_block <- function(name, desc, body) {
  c(sprintf("define inline_script %s", name),
    sprintf('\tset description "%s"', desc),
    '\tset _prepare ""', "\t___run__", paste0("\t", body), "\t__end__", "")
}

.osexp_event_block <- function(name, ev) {
  t <- ev$type
  ms <- as.integer(round((ev$frames %||% 1L) * 1000 / 60))
  if (t %in% c("fixation", "text", "mask", "blank")) {
    body <- "c = Canvas()"
    if (t != "blank") body <- c(body, sprintf("c.text(%s)", .content_expr(ev)))
    body <- c(body, "var.onset_time = c.show()")
    trig <- .trigger_expr(ev$trigger)
    if (!is.null(trig)) body <- c(body, sprintf("send_trigger(%s)", trig))
    body <- c(body, sprintf("clock.sleep(%d)", ms))
    return(list(block = .inline_block(name, "Show stimulus and send onset-aligned trigger", body),
                run = name))
  }
  if (t == "region") {
    trig <- .trigger_expr(ev$crit_trigger)
    body <- c(
      sprintf("_regions = [r for r in var.%s.split(%s) if r != u'']", ev$field, .pyq(ev$sep %||% "|")),
      "_crit = int(var.critical_region) if var.get(u'critical_region') is not None else 0",
      sprintf("_kb = Keyboard(keylist=[%s], timeout=None)", .pyq(ev$key %||% "space")),
      "for _i, _region in enumerate(_regions, start=1):",
      "    c = Canvas(); c.text(_region); c.show()")
    if (!is.null(trig)) body <- c(body, sprintf("    if _i == _crit: send_trigger(%s)", trig))
    body <- c(body, "    _kb.get_key()")
    return(list(block = .inline_block(name, "Self-paced reading region by region", body), run = name))
  }
  if (t == "question") {
    keys_list <- paste(vapply(ev$keys %||% c("f", "j"), .pyq, character(1)), collapse = ", ")
    body <- c(
      sprintf("c = Canvas(); c.text(var.%s); c.show()", ev$field),
      sprintf("_kb = Keyboard(keylist=[%s], timeout=%d)", keys_list,
              as.integer((ev$timeout %||% 5) * 1000)),
      "var.response, var.response_time = _kb.get_key()")
    return(list(block = .inline_block(name, "Comprehension question", body), run = name))
  }
  if (t == "response") {
    keys <- paste(ev$keys %||% c("left", "right"), collapse = ";")
    block <- c(
      sprintf("define keyboard_response %s", name),
      paste0("\tset timeout ", as.integer((ev$timeout %||% 2) * 1000)),
      "\tset flush yes", "\tset duration keypress",
      '\tset description "Collect a response"',
      sprintf('\tset allowed_responses "%s"', keys), "")
    return(list(block = block, run = name))
  }
  stop(sprintf("lexsync: unknown event type '%s'.", t), call. = FALSE)
}

#' Build a complete plain-text OpenSesame experiment from rendered events
#' @keywords internal
build_osexp <- function(design, conditions_file, schema, rendered, font = "mono") {
  addr <- schema$triggers$parallel_address %||% "0x378"
  design_name <- design$name; language <- design$language
  setup <- c(
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

  event_blocks <- character(0); run_names <- character(0)
  for (i in seq_along(rendered)) {
    eb <- .osexp_event_block(sprintf("lexsync_e%d", i - 1L), rendered[[i]])
    event_blocks <- c(event_blocks, eb$block)
    run_names <- c(run_names, eb$run)
  }

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
    '\tset description "Open the trigger device with a test-mode fallback"',
    '\tset _run ""', "\t___prepare__", paste0("\t", setup), "\t__end__", ""
  )
  trial <- c(
    "define sequence lexsync_trial",
    "\tset flush_keyboard yes",
    '\tset description "One trial: the paradigm event sequence"',
    sprintf("\trun %s always", run_names), "",
    "define loop lexsync_loop",
    sprintf('\tset source_file "%s"', conditions_file),
    "\tset source file", "\tset repeat 1", "\tset order random",
    '\tset description "Present each item once"', "\trun lexsync_trial", "",
    "define sequence lexsync_experiment",
    "\tset flush_keyboard yes",
    '\tset description "Top-level experiment sequence"',
    "\trun lexsync_trigger_setup always", "\trun lexsync_loop always", ""
  )
  paste(c(header, event_blocks, trial), collapse = "\n")
}

#' Export a complete plain-text OpenSesame experiment
#'
#' @inheritParams export_psychopy
#' @return The path to the generated `.osexp`, invisibly.
#' @export
export_opensesame <- function(stimuli, design, schema, outdir, base = NULL) {
  base <- base %||% slugify(design$name, design$language)
  events <- resolve_events(design)
  rendered <- render_events(events, design$timing %||% list())
  csv_name <- paste0(base, "_opensesame.csv")
  write_csv_utf8(loop_table(stimuli, events), file.path(outdir, csv_name))
  presentation <- schema$presentation %||% list()
  font <- design$font %||% presentation$opensesame_font %||% "mono"
  txt <- build_osexp(design, csv_name, schema, rendered, font = font)
  out <- file.path(outdir, paste0(base, ".osexp"))
  writeLines(txt, out, useBytes = TRUE)
  invisible(out)
}

# Event-model key names (PsychoPy style) mapped to browser KeyboardEvent keys.
.JSPSYCH_KEYS <- c(left = "arrowleft", right = "arrowright", up = "arrowup",
                   down = "arrowdown", space = " ", "return" = "enter")

.map_keys_jspsych <- function(rendered) {
  mapk <- function(k) { m <- .JSPSYCH_KEYS[k]; unname(ifelse(is.na(m), k, m)) }
  lapply(rendered, function(e) {
    if (!is.null(e$keys)) e$keys <- mapk(e$keys)
    if (!is.null(e$key)) e$key <- mapk(e$key)
    e
  })
}

.json_html <- function(x) {
  s <- as.character(x)
  s <- gsub("<", "\\u003c", s, fixed = TRUE)
  s <- gsub(">", "\\u003e", s, fixed = TRUE)
  gsub("&", "\\u0026", s, fixed = TRUE)
}

#' Export a self-contained, browser-runnable jsPsych experiment
#'
#' The rendered events and the trial data are embedded in one HTML file, so anyone
#' can reproduce the procedure online from the same materials. Onset triggers are
#' recorded in each trial's data (a browser cannot drive a parallel port).
#'
#' @inheritParams export_psychopy
#' @return The path to the generated `.html`, invisibly.
#' @importFrom jsonlite toJSON
#' @export
export_jspsych <- function(stimuli, design, schema, outdir, base = NULL) {
  base <- base %||% slugify(design$name, design$language)
  events <- resolve_events(design)
  rendered <- .map_keys_jspsych(render_events(events, design$timing %||% list()))
  trials <- loop_table(stimuli, events)
  presentation <- schema$presentation %||% list()
  font <- design$font %||% presentation$font %||% "Courier New"
  tmpl <- paste(readLines(find_template("jspsych/experiment_template.html"), warn = FALSE),
                collapse = "\n")
  subs <- list(
    DESIGN = design$name, LANGUAGE = design$language, WORD_FONT = font,
    EVENTS_JSON = .json_html(jsonlite::toJSON(rendered, auto_unbox = TRUE)),
    TRIALS_JSON = .json_html(jsonlite::toJSON(trials, dataframe = "rows"))
  )
  for (k in names(subs)) {
    tmpl <- gsub(sprintf("{{%s}}", k), as.character(subs[[k]]), tmpl, fixed = TRUE)
  }
  out <- file.path(outdir, paste0(base, ".html"))
  writeLines(tmpl, out, useBytes = TRUE)
  invisible(out)
}

#' Export all presentation targets (PsychoPy, OpenSesame, jsPsych)
#'
#' @inheritParams export_psychopy
#' @return A named list of generated file paths.
#' @export
export_experiments <- function(stimuli, design, schema, outdir, base = NULL) {
  stimuli <- assign_triggers(stimuli)
  list(
    psychopy = export_psychopy(stimuli, design, schema, outdir, base),
    opensesame = export_opensesame(stimuli, design, schema, outdir, base),
    jspsych = export_jspsych(stimuli, design, schema, outdir, base)
  )
}
