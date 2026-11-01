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
[`assign_triggers()`](https://pablobernabeu.github.io/lexsync/r/reference/assign_triggers.md)
is given the design's events and the schema, so the item codes of a
design that sends them alongside other codes are kept apart from those
codes, and a code of the design's own that the stream already uses is
reported.

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

  Optional file-name stem. By default the design's
  [`design_stem()`](https://pablobernabeu.github.io/lexsync/r/reference/design_stem.md).

- conditions:

  Optional character vector of condition labels in the order that
  assigns their trigger codes (see
  [`assign_triggers()`](https://pablobernabeu.github.io/lexsync/r/reference/assign_triggers.md)).
  `NULL` (the default) takes the order of the design's `conditions`.

## Value

A named list of generated file paths: `psychopy`, `opensesame` (version
1's experiment when a design has several, see
[`export_opensesame()`](https://pablobernabeu.github.io/lexsync/r/reference/export_opensesame.md))
and `jspsych`. `files` lists every file written, in a fixed order: the
PsychoPy script, each OpenSesame experiment in version order, the
jsPsych page, the PsychoPy conditions file, and then each OpenSesame
experiment's loop table and text table.

## Details

Each trial that names no `answer` of its own takes the key the design's
response mapping gives its condition in its list, so the loop tables can
score every trial. A lexical decision maps word to its response event's
first key and pseudoword to its second unless the design gives
`response_mapping`, and `rotate_mapping_by_list: true` rotates the keys
across lists. A practice or filler trial keeps the answer its table
gives. The stimuli passed in are not changed. Every target shows the
design's `instructions`, or lexsync's English instructions for its task,
and waits for the space bar before the first trial.
