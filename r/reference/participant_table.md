# Build a participant counterbalancing table

Crosses the factors with
[`expand.grid()`](https://rdrr.io/r/base/expand.grid.html), whose first
factor varies fastest, and gives participant p row ((p - 1) mod n) + 1
of the n crossed cells, cycling through the cells as often as
`n_participants` needs.
`participant_table(list(version = 1:V, order = 1:m), N)` therefore
reproduces the version and order a generated experiment assigns
participant p when none is chosen at launch.

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

A data frame with one row per participant: one column per factor, then
`participant`.

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
