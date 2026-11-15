# Cohen's d (pooled-SD standardised mean difference)

Cohen's d (pooled-SD standardised mean difference)

## Usage

``` r
cohens_d(x, y)
```

## Arguments

- x, y:

  Numeric vectors.

## Value

The standardised mean difference. It is 0 when both samples share one
constant, and `NA` when either sample has fewer than two values (one
value has no spread, so the pooled SD is undefined) or when the pooled
SD is zero but the means differ (the standardised difference is then
unbounded, not zero).

## Examples

``` r
cohens_d(c(5, 6, 7, 8), c(5, 6, 7, 9))
#> [1] -0.1651446
```
