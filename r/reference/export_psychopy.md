# Export a runnable PsychoPy script that interprets the event sequence

The conditions file, `<base>_psychopy.csv`, holds every presentation
version of the design, one per (replicate, list) pair, and the script
presents one per run: the version given by `--version` (or `--list` when
there are no replicates), else the participant's by the rule
`((participant - 1) mod V) + 1` from `--participant`, else what a
start-up dialogue asks for. A version the script does not have stops the
run with a message. With `counterbalance.orders: m` the conditions file
holds each trial's position in each of m orders, and the script presents
the version in order `(((participant - 1) div V) mod m) + 1`, or in
order 1 without a participant number. The data file then records the
order.

## Usage

``` r
export_psychopy(stimuli, design, schema, outdir, base = NULL)
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

The path to the generated `.py`, invisibly.

## Details

Before the first trial, the script shows the version's instructions, the
design's `instructions` or lexsync's for its task, and waits for the
space bar, which also lets the experimenter start the run. Escape there
stops the run before anything is recorded. The text is embedded as JSON
data, one text per version.

Each run writes
`data/<base>_p<participant>_v<version>_<date>-<time>.csv` beside the
script, without the `_p` part when no participant number is given, one
row per trial, each written as its trial ends. A row holds the run, the
trial's fields and trigger codes, the response and its reaction time
from the onset of the stimulus it answers, whether the window closed
without one, whether the key was the trial's `answer`, the self-paced
reading times, the question's response and reaction time, the measured
refresh rate, the trigger mode the run used, and each event's realised
flips and onset.

Each trigger code goes out on its stimulus's first flip and is held for
`triggers.trigger_hold_ms`, in whole flips at the measured refresh and
never under 10 ms, through the events after it when its own is shorter,
unless the next onset's code replaces it first. The session markers, 254
before the first trial and 255 after the last, are held the same way.

The script runs full screen unless `presentation.fullscreen` is false,
when it opens a 1280 x 1024 window, and draws its stimuli
`presentation.text_height_px` pixels high, 48 by default. It writes the
codes to the parallel port at `triggers.parallel_address` or, with
`triggers.backend: serial`, as single bytes to `triggers.serial_port` at
`triggers.baudrate`. `triggers.mode` decides what happens when that
device cannot be opened. Under `auto`, the script prints the codes
instead and, before the instructions, shows a notice that the
experimenter dismisses with the C key. Under `hardware`, it stops before
its window opens, and under `mock` it prints the codes without trying
the device. The data file's `trigger_mode` column records `hardware` or
`mock`.
