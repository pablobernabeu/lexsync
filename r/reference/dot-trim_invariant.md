# Strip leading and trailing whitespace under the Unicode definition

Base R's [`trimws()`](https://rdrr.io/r/base/trimws.html) removes only
space, tab, carriage return and line feed, leaving a no-break space, a
form feed or an ideographic space in place, where Python's `str.strip()`
removes all of them. `word` is the canonical key behind every byte-order
tie-break, so a lexicon padded with any of those characters would
otherwise key, sort and number differently in the two engines. As with
[`.lower_invariant()`](https://pablobernabeu.github.io/lexsync/r/reference/dot-lower_invariant.md),
the fix is to pin R to Python's Unicode semantics.

## Usage

``` r
.trim_invariant(x)
```

## Arguments

- x:

  A character vector, or a vector coercible to one.

## Value

A character vector, trimmed; `NA` is preserved.
