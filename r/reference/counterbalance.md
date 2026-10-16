# Assign stimuli to lists and a randomised, reproducible trial order

The recipe is `counterbalance.recipe` when the design names one, and
otherwise the recipe of the paradigm it names. That is the factorial
recipe for matched word lists, or a Latin square over conditions for the
paired and sentence paradigms. A design's own `events` list has no say
in the recipe. The factorial recipe refuses more lists than item sets,
since the surplus lists would be empty.

## Usage

``` r
counterbalance(stimuli, design, schema, list_of_set = NULL)
```

## Arguments

- stimuli:

  A stimuli data frame (matched set or loaded item table).

- design:

  A parsed design configuration. Reads `paradigm`,
  `counterbalance.recipe`, `counterbalance.lists`,
  `counterbalance.max_run`, `counterbalance.run_on`,
  `counterbalance.orders` and `fillers`.

- schema:

  The parsed global schema (provides the seed).

- list_of_set:

  Optional named integer vector mapping each `set` to a list, from
  [`balance_lists()`](https://pablobernabeu.github.io/lexsync/r/reference/balance_lists.md).
  Supplied by the pipeline when `counterbalance.optimise` is on; when
  `NULL` the factorial recipe deals sets to lists by rank as before.

## Value

`stimuli` with added `list` and `trial` columns, and the order columns
when there is more than one order.

## Details

Each list's trials are ordered by the seeded keyed hash.
`counterbalance.max_run` repairs that order so that no run of one
`counterbalance.run_on` value (by default the condition) is longer than
the limit, and refuses a limit no order can meet. A design with fillers
has the limit applied when the fillers are interleaved, to that order.
`counterbalance.orders: m` adds `order_1` to `order_m`, each trial's
position in each of m orders of its list, `order_1` being the order
`trial` gives.
