# Two one-sided tests (TOST) of equivalence on a Cohen's d bound

Reports the larger of the two one-sided p-values; a value below `alpha`
supports equivalence within +/- `bound_d` standard deviations. A
non-significant difference test is not itself evidence of equivalence,
hence TOST is reported alongside the standardised mean difference
(Lakens, 2017).

## Usage

``` r
tost_equiv(x, y, bound_d = 0.5, alpha = 0.05)
```

## Arguments

- x, y:

  Numeric vectors.

- bound_d:

  Smallest effect size of interest (Cohen's d); defaults to the schema
  value of 0.5 (Lakens, 2017).

- alpha:

  Significance level.

## Value

A list with `p` and logical `equivalent`.
