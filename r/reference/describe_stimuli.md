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

A long data frame with n, mean, sd, min, median and max per group.
