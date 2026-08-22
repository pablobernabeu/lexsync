# Export a browser-runnable jsPsych experiment

The rendered events and the trial data are embedded in one HTML file, so
anyone can reproduce the procedure online from the same materials. The
jsPsych library and stylesheet are loaded from a CDN, so the machine
running the file needs an internet connection; the trial data are
embedded and the responses are saved locally, so no server is required
either to run it or to collect them. Onset triggers are recorded in each
trial's data (a browser cannot drive a parallel port).

## Usage

``` r
export_jspsych(stimuli, design, schema, outdir, base = NULL)
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

  Optional file-name stem.

## Value

The path to the generated `.html`, invisibly.
