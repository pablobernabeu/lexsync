# Variance ratio: a distributional balance check

The ratio of a condition's variance to the reference's, complementing
the mean-based Cohen's d and TOST. Two conditions can share a mean yet
differ in spread and still confound, which a mean-based statistic misses
(Armstrong et al., 2012; Austin, 2009). A ratio near 1 is balanced; a
common heuristic flags ratios outside roughly 0.5 to 2.

## Usage

``` r
variance_ratio(cond, ref)
```

## Arguments

- cond, ref:

  Numeric vectors (condition and reference).

## Value

The variance ratio, or `NA` when a variance is undefined.

## Examples

``` r
variance_ratio(c(1, 2, 3, 4), c(1, 2, 3, 8))
#> [1] 0.1724138
```
