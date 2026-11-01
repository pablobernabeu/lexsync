# Per-trial table of the columns the experiments read

The columns are those of `stimuli`, where present, in this order:
`trial`, `list`, `replicate`, `block`, `set`, `condition`, `order_1` to
`order_m` (with two or more orders), the fields the events' content
references
([`referenced_fields()`](https://pablobernabeu.github.io/lexsync/r/reference/referenced_fields.md)),
or `word` when `events` is `NULL`, the per-trial duration columns the
events read, `critical_region`, `answer`, `condition_trigger` and
`item_trigger`. Every other column of `stimuli` is left out.

## Usage

``` r
loop_table(stimuli, events = NULL)
```

## Arguments

- stimuli:

  The trials, a data frame.

- events:

  The design's event list, as
  [`resolve_events()`](https://pablobernabeu.github.io/lexsync/r/reference/resolve_events.md)
  returns it, or `NULL`.

## Value

A data frame with those columns, in that row order, its row names reset.

## Details

The rows are in presentation order within each version: by replicate
when the table has one, then by list, then by trial. `trial` restarts at
1 in every list and in every replicate, so ordering on it alone would
interleave the versions. The sort is stable, so rows that tie keep their
incoming order and the two engines write the same table. A design with
`counterbalance.orders` carries `order_1` to `order_m` after the columns
that place a trial, each trial's position in each order, which the
experiments sort a version by.
