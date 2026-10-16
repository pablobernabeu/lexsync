# Cohen's d with a confidence interval, complementing the TOST verdict

The interval is the `(1 - 2 * alpha)` confidence interval for the
standardised mean difference, so `alpha = 0.05` gives the 90% interval
that goes with a TOST decision at the .05 level (Lakens, 2017).
Reporting the interval, rather than only a binary verdict, makes the
realised imbalance and its sampling uncertainty explicit, and keeps the
dependence on the number of items visible. With few items the interval
is wide, whatever the point estimate. Both the interval and the TOST
treat the selected items as a sample, although a test on stimuli
concerns a closed population. Sassenhagen and Alday (2016) recommend
describing the stimuli and entering potential confounds in the analysis
as covariates.

## Usage

``` r
cohens_d_ci(x, y, alpha = 0.05)
```

## Arguments

- x, y:

  Numeric vectors.

- alpha:

  Significance level matching the TOST (default 0.05).

## Value

A list with `d`, `ci_low` and `ci_high`, all three `NA` when either
sample has fewer than two values, as for
[`cohens_d()`](https://pablobernabeu.github.io/lexsync/r/reference/cohens_d.md).

## Details

The limits are `d +/- t * SE(d)`, where `t` is the Student t quantile on
`nx + ny - 2` degrees of freedom and `SE(d)` is the large-sample
standard error of d, `sqrt(1/nx + 1/ny + d^2 / (2 * (nx + ny)))` (Hedges
& Olkin, 1985; Borenstein et al., 2009, eq. 4.20). The `d^2` term
carries the sampling error of the pooled standard deviation. It is
negligible for a well-matched control, where d is near zero, but it
dominates for a manipulated dimension and can more than double the width
of that interval. TOST tests the raw mean difference, so the interval is
slightly wider than the one its decision implies, and when a control's
limit lies close to the bound, `tost_p` gives the verdict.
