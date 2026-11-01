# Check that the levels of given columns occur equally often

Check that the levels of given columns occur equally often

## Usage

``` r
balance_check(stimuli, columns)
```

## Arguments

- stimuli:

  A stimuli data frame.

- columns:

  Columns whose level counts should be equal. A name the stimuli do not
  carry is skipped without a warning, so check the names first.

## Value

A character vector of human-readable balance warnings (empty if none).
