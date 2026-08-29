# Cohen's d with a confidence interval, complementing the TOST verdict

The interval is the `(1 - 2 * alpha)` confidence interval for the
standardised mean difference; for `alpha = 0.05` this is the 90%
interval that corresponds exactly to a TOST decision at the .05 level
(Lakens, 2017). Reporting the interval, rather than only a binary
verdict, makes the realised imbalance and its sampling uncertainty
explicit, and keeps the dependence on the number of items visible. With
few items the interval is wide, so a small point estimate cannot be
over-read as evidence of a small true difference (Sassenhagen & Alday,
2016).

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

A list with `d`, `ci_low` and `ci_high`.
