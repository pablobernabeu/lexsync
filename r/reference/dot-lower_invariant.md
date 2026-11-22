# Lower-case a character vector under the Unicode default case mapping

Base R's [`tolower()`](https://rdrr.io/r/base/chartr.html) leaves case
mapping to the C library, so it depends on the locale and the platform
(see [`?chartr`](https://rdrr.io/r/base/chartr.html)). Under a C or
8-bit locale, it leaves accented capitals uncased, and even under a
UTF-8 locale, it applies only the simple mappings, rendering Greek final
sigma as U+03C3 and dropping the dot of U+0130. Python's `str.lower()`
always applies the Unicode default full mapping, giving U+03C2 and i +
U+0307 respectively. `word` is the canonical key behind every byte-order
tie-break, so the engines must fold case identically. ICU set to the
root locale (`und`) reproduces Python's mapping exactly and makes the
result independent of the session's locale.

## Usage

``` r
.lower_invariant(x)
```

## Arguments

- x:

  A character vector, or a vector coercible to one.

## Value

A character vector, lower-cased. `NA` is preserved.
