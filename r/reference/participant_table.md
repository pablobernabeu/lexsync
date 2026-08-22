# Build a participant counterbalancing table

Crosses the supplied counterbalancing factors and replicates the cells
to cover `n_participants`, generalising the
[`expand.grid()`](https://rdrr.io/r/base/expand.grid.html) + replication
pattern of the original workflow's `participant_parameters.R`.

## Usage

``` r
participant_table(factors, n_participants)
```

## Arguments

- factors:

  A named list of factors, each a vector of levels.

- n_participants:

  Number of participants to allocate.

## Value

A data frame with one row per participant.

## Examples

``` r
participant_table(list(list = 1:2, order = c("a", "b")), 6)
#>   list order participant
#> 1    1     a           1
#> 2    2     a           2
#> 3    1     b           3
#> 4    2     b           4
#> 5    1     a           5
#> 6    2     a           6
```
