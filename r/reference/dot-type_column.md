# Type one column by the rule both engines share

Numeric when every non-missing value is a plain decimal number, parsed
by
[`.parse_decimal()`](https://pablobernabeu.github.io/lexsync/r/reference/dot-parse_decimal.md).
Logical when every non-missing value is TRUE, FALSE, true, false, True
or False. Text otherwise. A column with no values at all is numeric, all
missing. Dates are never parsed.

## Usage

``` r
.type_column(x)
```

## Arguments

- x:

  A character vector of trimmed cells, `NA` for missing.

## Value

A double, logical or character vector.
