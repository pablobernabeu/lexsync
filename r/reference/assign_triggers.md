# Assign EEG trigger codes to stimuli

Adds `condition_trigger` (101, 102, ... per condition) and
`item_trigger` (40-239 per item/`set`). Events reference these by the
tokens "condition" and "item", or carry their own codes, whole numbers
from 1 to 255. Item codes follow the code-point order of the set labels,
so with sets 1 to 20, set 10 is 41 and set 2 is 51. Decode an item code
through the loop table, not from the set's label. The item range holds
200 codes (an 8-bit-port constraint), so past 200 sets the codes wrap
and repeat, and a runtime notice says so.

## Usage

``` r
assign_triggers(stimuli, conditions = NULL, events = NULL, schema = NULL)
```

## Arguments

- stimuli:

  A stimuli data frame.

- conditions:

  Optional character vector of condition labels, in the order that
  assigns their codes from 101 upwards. `NULL` (the default) numbers the
  conditions in order of first appearance.

- events:

  Optional list of the design's events, as
  [`resolve_events()`](https://pablobernabeu.github.io/lexsync/r/reference/resolve_events.md)
  returns them, which says which codes the experiment sends. `NULL` (the
  default) allocates the item codes as for a design that sends no other
  code beside them.

- schema:

  Optional parsed global schema, read for `triggers.allow_code_overlap`,
  which must be `true` or `false` when given.

## Value

`stimuli` with trigger columns added.

## Details

`events`, the design's event list, says which codes the experiment
sends. When it sends item codes together with condition codes, or with a
code of its own from 40 to 239, the item codes skip 101 to 100 + k, the
codes of the k conditions, and the design's own codes, so that no item
takes a code that marks something else. Sets 65 and 66 of a 70-set
design took 101 and 102, the condition codes. A design with more item
sets than free codes is then refused, unless `schema` sets
`triggers.allow_code_overlap: true`, which lets the item codes wrap and
repeat within the free codes. Every other design, and a call without
`events`, gets the item codes it had before. Each trigger in `events` is
checked as
[`render_events()`](https://pablobernabeu.github.io/lexsync/r/reference/render_events.md)
checks it.

A notice is given for a code of the design's own that the stream already
uses for something else: 254 or 255, which the PsychoPy and OpenSesame
experiments send when the session starts and ends, a condition code the
design sends, or a code within the range of the item codes it sends.

The condition codes follow `conditions` when it is given: its first
entry is 101, its second 102, and so on, whether or not every entry
occurs in `stimuli`, so the same condition keeps the same code in a
subset such as a practice block. A condition present in `stimuli` but
missing from `conditions` takes the next free codes, in code-point order
of its label. Either way the mapping depends only on the labels, never
on the row order. Without `conditions`, the codes follow the order in
which the conditions first appear in `stimuli`, as in lexsync 0.1.0. On
a shuffled trial list that order comes from the shuffle, so a different
seed can swap two conditions' codes.
[`export_experiments()`](https://pablobernabeu.github.io/lexsync/r/reference/export_experiments.md)
passes the design's order, and the pipeline passes the order of the
design's `conditions`, followed by any other condition in the order the
item source lists it.

## Examples

``` r
stim <- data.frame(condition = c("low", "high", "low", "high"), set = c(1, 1, 2, 2))
# First appearance: low = 101, high = 102.
unique(assign_triggers(stim)[, c("condition", "condition_trigger")])
#>   condition condition_trigger
#> 1       low               101
#> 2      high               102
# The design's order: high = 101, low = 102, however the rows are shuffled.
unique(assign_triggers(stim, conditions = c("high", "low"))[
  , c("condition", "condition_trigger")])
#>   condition condition_trigger
#> 1       low               102
#> 2      high               101
# Item codes follow the code-point order of the set labels: set 2 is 51 here.
twenty <- assign_triggers(data.frame(condition = "a", set = 1:20))
stats::setNames(twenty$item_trigger, twenty$set)
#>  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 
#> 40 51 53 54 55 56 57 58 59 41 42 43 44 45 46 47 48 49 50 52 
```
