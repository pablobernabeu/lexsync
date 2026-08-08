# Orthographic overlap between the two members of each pair

Adds two columns. `pair.lev` is the Levenshtein distance between the
pair's two orthographic forms, and `pair.overlap` is
`1 - lev / max(nchar)`, the proportion of the longer form the two share.
Overlap is the standard confound control in a priming design: a related
pair that also shares letters confounds semantic relatedness with
orthographic similarity.

## Usage

``` r
add_pair_overlap(df, prime = "prime", target = "target")
```

## Arguments

- df:

  A pair table.

- prime, target:

  Column names holding the two orthographic forms.

## Value

`df` with `pair.lev` and `pair.overlap` added.

## Details

Both engines return identical values, and the reasons are worth stating
because they are the constraints on any future relational dimension. The
core is an integer edit distance, and `stringdist(method = "lv")` and
rapidfuzz's `Levenshtein.distance` agree exactly, including on
decomposed Unicode and CJK, which is the same cross-library agreement
[`add_neighbourhood()`](https://pablobernabeu.github.io/lexsync/r/reference/add_neighbourhood.md)
already stakes `old20` on. Length is counted in code points,
[`nchar()`](https://rdrr.io/r/base/nchar.html)'s default and Python's
`len()`, never in bytes. The arithmetic uses only `-` and `/`, which
IEEE-754 mandates be correctly rounded, and the result is rounded to
nine decimal places, the constant used everywhere else in the package. A
degenerate pair of two empty forms returns 0 rather than `0/0`, because
a NaN would be sorted and compared and would then drop the row from one
engine's control window but not the other's.
