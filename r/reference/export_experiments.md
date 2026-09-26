# Export all presentation targets (PsychoPy, OpenSesame, jsPsych)

Assigns the EEG trigger codes with
[`assign_triggers()`](https://pablobernabeu.github.io/lexsync/r/reference/assign_triggers.md)
and then writes each target. The condition codes follow `conditions`,
which defaults to the order of the design's `conditions` entries, so in
a design that declares its conditions the first is 101, the second 102,
and so on, whatever order the counterbalanced trials put them in. A
design with no `conditions` block (a generated lexical decision, an item
table) falls back to the order of first appearance, unless `conditions`
is given.

## Usage

``` r
export_experiments(
  stimuli,
  design,
  schema,
  outdir,
  base = NULL,
  conditions = NULL
)
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

- conditions:

  Optional character vector of condition labels in the order that
  assigns their trigger codes (see
  [`assign_triggers()`](https://pablobernabeu.github.io/lexsync/r/reference/assign_triggers.md)).
  `NULL` (the default) takes the order of the design's `conditions`.

## Value

A named list of generated file paths.
