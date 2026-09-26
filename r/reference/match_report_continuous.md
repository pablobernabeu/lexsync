# Realised-control report for a continuous design

Returns the same list shape as
[`match_report()`](https://pablobernabeu.github.io/lexsync/r/reference/match_report.md)
(`descriptives` + `comparisons`), but the comparisons describe a
continuous predictor: its realised span and, for each control, the
Pearson correlation with the predictor (near zero when the control is
held constant). Mirrors match_report_continuous in validation.py.

## Usage

``` r
match_report_continuous(stimuli, predictor, controls, schema)
```

## Arguments

- stimuli:

  A stimuli data frame (a single "continuous" group).

- predictor:

  The spanned predictor dimension.

- controls:

  Character vector of control dimensions.

- schema:

  The parsed global schema.

## Value

A list with `descriptives` and `comparisons` data frames.
