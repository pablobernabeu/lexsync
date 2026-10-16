# Export a complete plain-text OpenSesame experiment

Writes `<base>.osexp` and the two tables it reads. Its loop runs over
`<base>_opensesame.csv`, which holds numbers only: `lexsync_row` (the
trial's position in loop order, from 1), `lexsync_trial`,
`lexsync_list`, `lexsync_set`, the trigger codes, `critical_region` and
any per-trial duration. The presented text, `condition`, `block` and
`answer` are in `<base>_opensesame_text.csv`, which the inline scripts
read with Python's `csv` module, so OpenSesame never evaluates them.
Copy both tables with the experiment.

## Usage

``` r
export_opensesame(stimuli, design, schema, outdir, base = NULL)
```

## Arguments

- stimuli:

  Stimuli with trigger columns (see
  [`assign_triggers()`](https://pablobernabeu.github.io/lexsync/r/reference/assign_triggers.md)).

- design:

  A parsed design configuration.

- schema:

  The parsed global schema (trigger and presentation settings).

- outdir:

  Output directory.

- base:

  Optional file-name stem. By default the design's
  [`design_stem()`](https://pablobernabeu.github.io/lexsync/r/reference/design_stem.md).

## Value

The path to the generated `.osexp`, version 1's when there are several,
invisibly.

## Details

Before the loop, an inline script, `lexsync_instructions`, shows the
design's `instructions`, or lexsync's for its task, and waits for the
space bar. Every trial is logged. A response after a text event is
collected by that event's script from the stimulus's onset, which sets
`response`, `response_time`, `timed_out` and `correct`. A response kept
after the stimulus with `from: offset` is a keyboard_response, and a
script after it sets `timed_out` and `correct`. Self-paced reading sets
`lexsync_region_rts` and a question `question_response` and
`question_rt`. A script clears these as each trial starts, another
copies the trial's labels into `lexsync_condition`, `lexsync_block` and
`lexsync_answer`, and a logger item ends the trial.

Every canvas a trial shows is built before the trial runs, in the
prepare phase of its script, and each event is timed from the onset its
display returns. An event ends half a frame before its duration is up,
so that the next display lands on the refresh that ends it. The frame
period is measured at start-up and logged as `lexsync_frame_ms`, with
`presentation.assumed_refresh_hz` as the fallback when the measurement
fails. Each trigger code is held for `triggers.trigger_hold_ms`, at
least 10 ms, through the events after it when its own is shorter, unless
the next onset's code replaces it first. The session markers, 254 and
255, are sent just before the first trial and just after the last, held
the same way.

The setup writes the codes to the parallel port at
`triggers.parallel_address` or, with `triggers.backend: serial`, as
single bytes to `triggers.serial_port` at `triggers.baudrate`. When that
device cannot be opened, `triggers.mode: auto` prints the codes instead.
An inline script, `lexsync_trigger_notice`, then says so before any
other screen and waits for the C key. `hardware` stops the experiment
there, and `mock` prints the codes without trying the device. Every
trial logs `lexsync_trigger_mode`, `hardware` or `mock`. Text is drawn
`presentation.text_height_px` pixels high, OpenSesame's `font_size`, and
OpenSesame takes full screen from the mode it is launched in.

A design with more than one presentation version, one per (replicate,
list) pair of the trials, gets one experiment per version instead, each
with its own two tables holding only that version's trials:
`<base>_list<k>.osexp`, or `<base>_rep<r>_list<k>.osexp` when the
versions span several replicates. Each one checks OpenSesame's subject
number at start-up and shows a warning when that participant would
normally run another version. A design with `counterbalance.orders: m`
gets one experiment per version and order,
`<base>_list<k>_order<j>.osexp` (`<base>_order<j>.osexp` for a single
version), each with tables sorted by its order, a `lexsync_order`
variable that every trial logs, and a check that compares the
participant's order too, order `(((p - 1) div V) mod m) + 1`.
[`export_experiments()`](https://pablobernabeu.github.io/lexsync/r/reference/export_experiments.md)
lists every file written.

OpenSesame evaluates the cells of a loop table: in 4.x a cell holding
`{` runs as a Python f-string, and in 3.3 a cell starting with `=` or
holding `[=...]` runs as Python. A value in a numeric column that is not
a plain number is therefore refused, naming the column. An empty cell
passes. These rules were checked against the sources of OpenSesame
3.3.14 and 4.1.20.
