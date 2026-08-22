# Export all presentation targets (PsychoPy, OpenSesame, jsPsych)

Export all presentation targets (PsychoPy, OpenSesame, jsPsych)

## Usage

``` r
export_experiments(stimuli, design, schema, outdir, base = NULL)
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

A named list of generated file paths.
