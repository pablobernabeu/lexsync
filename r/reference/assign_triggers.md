# Assign EEG trigger codes to stimuli

Adds `condition_trigger` (101, 102, ... per condition) and
`item_trigger` (40-239 per item/`set`). Events reference these by the
tokens "condition" and "item", or carry their own integer codes. The
item range holds 200 codes (an 8-bit-port constraint), so past 200 sets
the codes wrap and repeat, and a runtime notice says so.

## Usage

``` r
assign_triggers(stimuli, conditions = NULL)
```

## Arguments

- stimuli:

  A stimuli data frame.

- conditions:

  Optional character vector of condition labels, in the order that
  assigns their codes from 101 upwards. `NULL` (the default) numbers the
  conditions in order of first appearance.

## Value

`stimuli` with trigger columns added.

## Details

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
```
