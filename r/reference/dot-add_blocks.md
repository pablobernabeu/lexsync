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
a `block` column when more than one block exists) and `report`
(per-block counts and the item tables' checksums, or `NULL` when the
design declares no extra block).
