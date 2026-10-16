# Check a design and its schema before anything is selected or written

[`run_pipeline()`](https://pablobernabeu.github.io/lexsync/r/reference/run_pipeline.md)
calls this right after reading the two files, so a design that cannot be
honoured is refused before any output exists, with the same message in
both engines. It first refuses a key within one or two edits of a key
lexsync reads at that level, naming the key it was probably meant to be
(one edit for a known key of up to five characters, two for a longer
one). It then refuses a missing, empty or non-text `name` or `language`,
an `n_per_condition`, `n_per_cell` or `resample.n_sets` that is not a
whole number of at least 1, a `counterbalance.optimise` that is not true
or false, a `counterbalance.scale` other than `mean` or `mad`, a
`counterbalance.max_run` or `counterbalance.orders` that is not a whole
number of at least 1, and a `counterbalance.run_on` that is not the name
of a column. It refuses a name, language or font that cannot be written
into the generated experiments, a trigger port that is not an address,
and an event list the renderer refuses, such as one with an unknown
timing key, a bad response key or a response key that YAML reads as a
boolean (an unquoted `yes`, `no`, `on` or `off`). It refuses a
`presentation.fullscreen` that is not true or false and a
`presentation.text_height_px` that is not a whole number from 8 to 400.
It refuses a `triggers.mode` other than `auto`, `hardware` or `mock`, a
`triggers.backend` other than `parallel` or `serial`, and a
`triggers.baudrate` that is not a positive whole number. A serial
backend needs a `triggers.serial_port`, with a name the experiments can
carry. Last, it refuses a condition without a name, with a name that is
not text or with a repeated name, a corpus or pool design with
conditions but no `match_on`, and a name and language that leave no file
stem. It also refuses an `exclude_words` that is neither a list of words
nor a mapping whose `path` names a file, and one that a design with an
item table names.

## Usage

``` r
validate_design(design, schema)
```

## Arguments

- design:

  A parsed design configuration.

- schema:

  The parsed global schema.

## Value

A character vector of notes on unknown keys, in the order the keys were
written, then the note on `triggers.inter_trigger_ms`; empty when there
are none.

## Details

Any other key lexsync does not read is not refused yet. It is returned
as a note, which
[`run_pipeline()`](https://pablobernabeu.github.io/lexsync/r/reference/run_pipeline.md)
writes into the run log, and a later release will refuse it.
`description` and keys beginning `x_` are annotations and are never
noted. A schema that still sets `triggers.inter_trigger_ms`, which no
longer does anything, gets a note too.

The experiments' instructions and response mapping are checked here too.
It refuses `instructions` that are not text, are empty or hold a control
character other than a line break. It refuses a `response_mapping` that
is not a mapping of conditions to single keys, names a key the response
event does not allow, or comes with no response event. And it refuses a
`rotate_mapping_by_list` that is not true or false, or that has no
mapping to rotate.

## Examples

``` r
validate_design(list(name = "demo", language = "english", x_note = "pilot"), list())
#> character(0)
```
