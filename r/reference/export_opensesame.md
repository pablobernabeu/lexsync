# Export a complete plain-text OpenSesame experiment

Export a complete plain-text OpenSesame experiment

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

  Optional file-name stem.

## Value

The path to the generated `.osexp`, invisibly.
