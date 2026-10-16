# Assemble the presented trial sequence from the main, filler and practice blocks

Assemble the presented trial sequence from the main, filler and practice
blocks

## Usage

``` r
.add_blocks(stimuli, design, schema)
```

## Arguments

- stimuli:

  The counterbalanced main stimuli (with `list` and `trial`).

- design:

  A parsed design configuration; reads `practice` and `fillers`.

- schema:

  The parsed global schema (provides the seed).

## Value

A list with `presented` (every trial the experiment runs, in order, with
a `block` column when more than one block exists), `report` (per-block
counts and the item tables' checksums, or `NULL` when the design
declares no extra block) and `normalisation`
(`list(changed, collapsed)`, what Unicode NFC normalisation did to the
practice and filler tables; see
[`load_items()`](https://pablobernabeu.github.io/lexsync/r/reference/load_items.md)).
Trials are numbered from 1 within each list, or within each (replicate,
list) pair of a resampled design, and the counts are per list or pair.
`counterbalance.max_run` applies to the main and filler trials together
and to the practice trials on their own. With
`counterbalance.orders: m`, `order_1` to `order_m` give each trial's
position in each order, the practice trials first in every one.
