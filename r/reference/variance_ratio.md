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

The variance ratio. Missing values are dropped first. The ratio is `NA`
when either vector has fewer than two non-missing values, or when the
reference's variance is zero and the condition's is not. It is 1 when
both variances are zero.

## References

Armstrong, B. C., Watson, C. E., & Plaut, D. C. (2012). SOS! An
algorithm and software for the stochastic optimization of stimuli.
*Behavior Research Methods, 44*(3), 675-705.
[doi:10.3758/s13428-011-0182-9](https://doi.org/10.3758/s13428-011-0182-9)

Austin, P. C. (2009). Balance diagnostics for comparing the distribution
of baseline covariates between treatment groups in propensity-score
matched samples. *Statistics in Medicine, 28*(25), 3083-3107.
[doi:10.1002/sim.3697](https://doi.org/10.1002/sim.3697)

## Examples

``` r
variance_ratio(c(1, 2, 3, 4), c(1, 2, 3, 8))
#> [1] 0.1724138
```
