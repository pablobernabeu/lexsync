# scripting.R -- export finalised, hardware-timed experiment scripts. Two
# targets are produced from the same matched stimuli: a runnable PsychoPy script
# whose onset trigger is bound to the stimulus flip via win.callOnFlip, and a
# complete plain-text OpenSesame .osexp (built programmatically so its
# tab-sensitive format is always valid). Generation imports neither psychopy nor
# pyserial: it only writes text. The drivers are needed only at experiment run
# time.

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
  if (!length(cand)) {
    stop(sprintf("lexsync: template '%s' not found.", relpath), call. = FALSE)
  }
  cand[1]
}

#' Assign EEG trigger codes to matched stimuli
#'
#' Adds `condition_trigger` (101, 102, ... per condition) and a unique
#' `target_word_trigger` per word (40-239), mirroring the trigger scheme of the
#' original workflow.
#'
#' @param stimuli A matched-stimuli data frame.
#' @return `stimuli` with trigger columns added.
#' @export
assign_triggers <- function(stimuli) {
  conds <- unique(stimuli$condition)
  stimuli$condition_trigger <- 100L + match(stimuli$condition, conds)
  uw <- unique(stimuli$word)
  code <- 40L + ((seq_along(uw) - 1L) %% 200L)
  stimuli$target_word_trigger <- code[match(stimuli$word, uw)]
  stimuli
}

#' Select and order the loop-table columns an experiment reads
#' @keywords internal
loop_table <- function(stimuli) {
  cols <- intersect(
    c("trial", "list", "word", "condition", "set", "length", "frequency",
      "n_density", "old20", "target_word_trigger", "condition_trigger"),
    names(stimuli)
  )
  tab <- stimuli[, cols, drop = FALSE]
  if ("trial" %in% names(tab)) tab <- tab[order(tab$trial), , drop = FALSE]
  rownames(tab) <- NULL
  tab
}

#' Export a runnable PsychoPy script with onset-locked triggers
#'
#' @param stimuli Matched stimuli (with trigger columns; see [assign_triggers()]).
#' @param design A parsed design configuration.
#' @param schema The parsed global schema (trigger settings).
#' @param outdir Output directory.
#' @param base Optional file-name stem.
#' @return The path to the generated `.py`, invisibly.
#' @export
export_psychopy <- function(stimuli, design, schema, outdir, base = NULL) {
  base <- base %||% slugify(design$name, design$language)
  csv_name <- paste0(base, "_psychopy.csv")
  py_name <- paste0(base, "_psychopy.py")
  write_csv_utf8(loop_table(stimuli), file.path(outdir, csv_name))

  tmpl <- paste(readLines(find_template("psychopy/trial_runner_template.py"), warn = FALSE),
                collapse = "\n")
  timing <- design$timing %||% list()
  word_font <- design$font %||% schema$presentation$font %||% "Courier New"
  subs <- list(
    DESIGN = design$name, LANGUAGE = design$language, CONDITIONS_FILE = csv_name,
    TRIGGER_ADDRESS = schema$triggers$parallel_address %||% "0x0378",
    RESET_AFTER_FRAMES = schema$triggers$reset_after_frames %||% 2,
    WORD_DURATION_FRAMES = timing$word_frames %||% 30,
    FIXATION_FRAMES = timing$fixation_frames %||% 30,
    ISI_FRAMES = timing$isi_frames %||% 15,
    INTER_TRIGGER_S = (schema$triggers$inter_trigger_ms %||% 10) / 1000,
    WORD_FONT = word_font,
    FULLSCREEN = "False"
  )
  for (k in names(subs)) {
    tmpl <- gsub(sprintf("{{%s}}", k), as.character(subs[[k]]), tmpl, fixed = TRUE)
  }
  out <- file.path(outdir, py_name)
  writeLines(tmpl, out, useBytes = TRUE)
  invisible(out)
}

#' Build a complete plain-text OpenSesame experiment
#' @keywords internal
build_osexp <- function(design_name, language, conditions_file, schema, font = "mono") {
  addr <- schema$triggers$parallel_address %||% "0x378"
  tb <- function(x) paste0("\t", x)
  setup <- c(
    "var.trigger_backend = u'parallel'",
    sprintf("var.parallel_port_address = %s", addr),
    "var.test_mode = u'no'",
    "var.word_duration_ms = 500",
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
  present <- c(
    "# Draw the word, show it (this blocks until the display refresh and returns",
    "# the onset time) and then send the onset-aligned triggers immediately. This",
    "# is the OpenSesame-recommended way to time-lock a marker to stimulus onset.",
    "c = Canvas()",
    "c.text(var.word)",
    "var.onset_time = c.show()",
    "send_trigger(var.target_word_trigger)",
    "send_trigger(var.condition_trigger)",
    "clock.sleep(var.word_duration_ms)"
  )
  lines <- c(
    "---", "API: 2.1", "OpenSesame: 3.3.14", "Platform: nt", "---",
    "set width 1024", "set uniform_coordinates yes",
    sprintf("set title \"lexsync: %s (%s)\"", design_name, language),
    "set subject_nr 0", "set start lexsync_experiment",
    "set sound_sample_size -16", "set sound_freq 48000", "set sound_channels 2",
    "set sound_buf_size 1024", "set sampler_backend legacy", "set round_decimals 2",
    "set mouse_backend legacy", "set keyboard_backend legacy", "set height 768",
    "set fullscreen no", "set foreground white", "set font_size 32",
    sprintf("set font_family %s", font), "set description \"Generated by lexsync\"",
    "set coordinates uniform", "set compensation 0", "set color_backend legacy",
    "set clock_backend legacy", "set canvas_backend xpyriment", "set background black", "",
    "define inline_script lexsync_trigger_setup",
    tb("set description \"Open the trigger device with a test-mode fallback\""),
    tb("set _run \"\""), tb("___prepare__"), tb(setup), tb("__end__"), "",
    "define sketchpad lexsync_fixation",
    tb("set duration 500"), tb("set description \"Fixation cross\""),
    tb("draw textline center=1 color=white font_family=mono font_size=40 html=yes show_if=always text=\"+\" x=0 y=0 z_index=0"), "",
    "define inline_script lexsync_word",
    tb("set description \"Show the word and send onset-aligned triggers\""),
    tb("set _prepare \"\""), tb("___run__"), tb(present), tb("__end__"), "",
    "define keyboard_response lexsync_response",
    tb("set timeout 2000"), tb("set flush yes"), tb("set duration keypress"),
    tb("set description \"Collect a response\""), tb("set allowed_responses \"left;right\""), "",
    "define sequence lexsync_trial",
    tb("set flush_keyboard yes"),
    tb("set description \"Fixation, word with onset-aligned triggers, response\""),
    tb("run lexsync_fixation always"), tb("run lexsync_word always"),
    tb("run lexsync_response always"), "",
    "define loop lexsync_loop",
    tb(sprintf("set source_file \"%s\"", conditions_file)),
    tb("set source file"), tb("set repeat 1"), tb("set order random"),
    tb("set description \"Present each stimulus once\""), tb("run lexsync_trial"), "",
    "define sequence lexsync_experiment",
    tb("set flush_keyboard yes"),
    tb("set description \"Top-level experiment sequence\""),
    tb("run lexsync_trigger_setup always"), tb("run lexsync_loop always"), ""
  )
  paste(lines, collapse = "\n")
}

#' Export a complete OpenSesame experiment and its loop table
#'
#' @inheritParams export_psychopy
#' @return The path to the generated `.osexp`, invisibly.
#' @export
export_opensesame <- function(stimuli, design, schema, outdir, base = NULL) {
  base <- base %||% slugify(design$name, design$language)
  csv_name <- paste0(base, "_opensesame.csv")
  osexp_name <- paste0(base, ".osexp")
  write_csv_utf8(loop_table(stimuli), file.path(outdir, csv_name))
  os_font <- design$font %||% schema$presentation$opensesame_font %||% "mono"
  txt <- build_osexp(design$name, design$language, csv_name, schema, font = os_font)
  out <- file.path(outdir, osexp_name)
  writeLines(txt, out, useBytes = TRUE)
  invisible(out)
}

#' Export both presentation targets
#'
#' @inheritParams export_psychopy
#' @return A named list of generated file paths.
#' @export
export_experiments <- function(stimuli, design, schema, outdir, base = NULL) {
  stimuli <- assign_triggers(stimuli)
  list(
    psychopy = export_psychopy(stimuli, design, schema, outdir, base),
    opensesame = export_opensesame(stimuli, design, schema, outdir, base)
  )
}
