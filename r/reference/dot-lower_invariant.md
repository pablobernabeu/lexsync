# Lower-case a character vector under the Unicode default case mapping

Base R's [`tolower()`](https://rdrr.io/r/base/chartr.html) hands case
mapping to the C library, so it is both locale- and platform-dependent
(see [`?chartr`](https://rdrr.io/r/base/chartr.html)): under a C or
8-bit locale it leaves accented capitals uncased, and even under a UTF-8
locale it applies only the simple mappings, rendering Greek final sigma
as U+03C3 and dropping the dot of U+0130. Python's `str.lower()` always
applies the Unicode default *full* mapping, giving U+03C2 and i + U+0307
respectively. `word` is the canonical key behind every byte-order
tie-break, so the engines must fold case identically; pinning ICU to the
root locale ("und") reproduces Python's mapping exactly and removes the
ambient locale from the result.

## Usage

``` r
.lower_invariant(x)
```

## Arguments

- x:

  A character vector, or a vector coercible to one.

## Value

A character vector, lower-cased; `NA` is preserved.
