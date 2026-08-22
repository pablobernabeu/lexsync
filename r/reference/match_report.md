# Build the full match-quality report

Build the full match-quality report

## Usage

``` r
match_report(stimuli, dims, schema)
```

## Arguments

- stimuli:

  A matched-stimuli data frame (must contain `condition`).

- dims:

  Dimensions to summarise and compare.

- schema:

  The parsed global schema (equivalence settings).

## Value

A list with `descriptives` and `comparisons` data frames. Every
comparison is against the first condition in order of appearance, so a
design with a single condition has nothing to compare and `comparisons`
comes back with its columns and no rows.
