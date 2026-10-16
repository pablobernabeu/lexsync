# Build the full match-quality report

Build the full match-quality report

## Usage

``` r
match_report(stimuli, dims, schema, roles = NULL)
```

## Arguments

- stimuli:

  A matched-stimuli data frame (must contain `condition`).

- dims:

  Dimensions to summarise and compare.

- schema:

  The parsed global schema (equivalence settings).

- roles:

  Optional function of `condition`, `reference` and `dimension` that
  returns the row's `role`: `"manipulated"` when the design sets the two
  conditions apart on the dimension, `"controlled"` when it matches them
  on it and `"uncontrolled"` otherwise.
  [`run_pipeline()`](https://pablobernabeu.github.io/lexsync/r/reference/run_pipeline.md)
  derives it from the design. Without it, `role` is `NA`.

## Value

A list with `descriptives` and `comparisons` data frames. Every pair of
conditions is compared on every dimension. The rows against the first
condition in order of appearance, the anchor, come first, then every
further pair in condition order, so a design with a single condition has
nothing to compare and `comparisons` comes back with its columns and no
rows. A dimension with no numeric value among the stimuli, such as
`n_syllables` for Chinese or a text label, is left out of both frames.

Each row of `comparisons` names the earlier condition of its pair in
`reference` and the later one in `condition`. The signed statistics run
from the reference to the other condition: `cohens_d`, `d_ci_low` and
`d_ci_high` are the reference mean minus the `condition` mean, in pooled
standard deviations, so a positive d means the reference scores higher.
`mean_diff` is the same difference in the dimension's own unit, to three
places. `var_ratio` is the other way up, the `condition` variance over
the reference variance.
