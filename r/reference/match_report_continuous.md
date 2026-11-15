# Realised-control report for a continuous design

Returns the same list shape as
[`match_report()`](https://pablobernabeu.github.io/lexsync/r/reference/match_report.md)
(`descriptives` + `comparisons`), but the comparisons describe a
continuous predictor: its realised span and, for each control, the
Pearson correlation with the predictor (near zero when the control is
held constant). Mirrors match_report_continuous in validation.py.

## Usage

``` r
match_report_continuous(
  stimuli,
  predictor,
  controls,
  schema,
  audit = attr(stimuli, "audit")
)
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

- audit:

  The selector's audit record, by default the `"audit"` attribute
  [`select_continuous_stimuli()`](https://pablobernabeu.github.io/lexsync/r/reference/select_continuous_stimuli.md)
  attaches to its result. Its `control_windows` give each control's
  window and pool SD. Without them, a control's `sd_ratio` and window
  are `NA`.

## Value

A list with `descriptives` and `comparisons` data frames.

## Details

`sd` is each dimension's realised SD. For the predictor, `sd_ratio` sets
it against the SD of as many values spaced evenly over the same range,
`(max - min) * sqrt(n * (n + 1) / 12) / (n - 1)` with the n - 1 that
`sd` uses, so an even spread has a ratio of 1 whatever its size and a
selection that follows a skewed pool a ratio below 1. That benchmark
tends to `(max - min) / sqrt(12)`, the SD of a uniform distribution over
the range, as n grows. For a control, `sd_ratio` sets the realised SD
against the SD of the pool the selector drew from, and `window_low` and
`window_high` give the window the selector banded it to, before any
relaxation. Both come from `audit`, the selector's record.
