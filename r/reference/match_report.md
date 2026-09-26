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

Each row of `comparisons` names that first condition in `reference` and
the condition compared with it in `condition`. The signed statistics run
from the reference to the other condition: `cohens_d`, `d_ci_low` and
`d_ci_high` are the reference mean minus the `condition` mean, in pooled
standard deviations, so a positive d means the reference scores higher.
`var_ratio` is the other way up, the `condition` variance over the
reference variance.
