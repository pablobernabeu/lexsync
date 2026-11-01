# Parse plain decimal numbers to the correctly rounded double

Python's `float()` returns the double nearest the decimal, and neither
of R's own parsers does in every case: measured over 200,000 random
decimals, readr's `parse_double()` missed by one unit in the last place
on 26,706 and [`as.numeric()`](https://rdrr.io/r/base/numeric.html) on
35, among them `0.586135918132` and `2.91e-11`. A value with at most 15
significant digits and a power of ten within 10^22 is therefore computed
as one exact integer times or divided by one exact power of ten. That is
a single IEEE-754 operation, which is correctly rounded, so both engines
reach the same double. Every value in the shipped lexica is of that
kind. Any other value is rounded by exact integer arithmetic
(`.decimal_to_double()`).
[`as.numeric()`](https://rdrr.io/r/base/numeric.html) is not used there,
because it accumulates the digits in `long double`. Where that type is
wider than a double, as on x86-64, it missed the nearest double on 25 of
60,008 such values. Where it is no wider, as on Apple Silicon, it misses
far more often. R CMD check on macOS read `0.12345678901234567` one unit
away, and an emulation of the parser in double precision missed on about
one in ten of the values Python's `repr()` writes for computed doubles.
readr's parser missed on 21,644 of the 60,008, and it read `1e400` as
1e307 and `1e-400` as 1e-307, where `float()` gives `Inf` and 0. A
negative zero is read as zero, because the two engines' writers would
print it as `-0` and `0`.

## Usage

``` r
.parse_decimal(x)
```

## Arguments

- x:

  A character vector whose non-missing values match `.NUMERIC_CELL`.

## Value

A double vector.
