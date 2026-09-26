# Assign stimuli to lists and a randomised, reproducible trial order

Dispatches on the design's paradigm: the factorial recipe for matched
word lists, or a Latin square over conditions for paired/sentence
paradigms.

## Usage

``` r
counterbalance(stimuli, design, schema, list_of_set = NULL)
```

## Arguments

- stimuli:

  A stimuli data frame (matched set or loaded item table).

- design:

  A parsed design configuration.

- schema:

  The parsed global schema (provides the seed).

- list_of_set:

  Optional named integer vector mapping each `set` to a list, from
  [`balance_lists()`](https://pablobernabeu.github.io/lexsync/r/reference/balance_lists.md).
  Supplied by the pipeline when `counterbalance.optimise` is on; when
  `NULL` the factorial recipe deals sets to lists by rank as before.

## Value

`stimuli` with added `list` and `trial` columns.
