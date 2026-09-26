# Export a runnable PsychoPy script that interprets the event sequence

Export a runnable PsychoPy script that interprets the event sequence

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

  Optional file-name stem.

## Value

The path to the generated `.py`, invisibly.
