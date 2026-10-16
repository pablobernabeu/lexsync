# Normalise text keys to Unicode Normalization Form C

A precomposed letter such as U+00F3 and the base letter followed by a
combining accent are canonically equivalent, but they compare unequal
and differ in length. Unnormalised, the two spellings of one word were
two candidates, which the matcher could place in opposite conditions of
one matched set, and a norm or member join missed whichever spelling the
lexicon did not use. Applied after
[`.trim_invariant()`](https://pablobernabeu.github.io/lexsync/r/reference/dot-trim_invariant.md)
and
[`.lower_invariant()`](https://pablobernabeu.github.io/lexsync/r/reference/dot-lower_invariant.md),
because case mapping does not guarantee normalised output. ICU (through
stringi) and Python's `unicodedata` agree on every character assigned in
both engines' Unicode versions. Mirrors `_nfc` in
python_workflow/src/lexsync/querying.py.

## Usage

``` r
.nfc(x)
```

## Arguments

- x:

  A character vector, or a vector coercible to one.

## Value

A character vector in NFC; `NA` is preserved.
