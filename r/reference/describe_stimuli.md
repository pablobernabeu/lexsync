# Per-group descriptive statistics for several dimensions

A grouping column or a dimension the stimuli do not carry is refused.

## Usage

``` r
describe_stimuli(stimuli, dims, by = "condition")
```

## Arguments

- stimuli:

  A stimuli data frame.

- dims:

  Character vector of dimension columns.

- by:

  Grouping column (default `"condition"`).

## Value

A long data frame with one row per group and dimension, the groups in
order of first appearance. Its columns are `group`, `dimension`, `n`
(the non-missing values), `mean`, `sd`, `min`, `median` and `max`, the
last five rounded to three decimal places. A value that is not a number
counts as missing.
