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

The forms are trimmed, lower-cased and normalised to Unicode NFC before
they are compared, as
[`load_lexicon()`](https://pablobernabeu.github.io/lexsync/r/reference/load_lexicon.md)
does to a lexicon's words, so `Dog` and `dog` are at distance 0. Length
is counted in code points. `pair.overlap` is rounded to nine decimal
places, and a pair of two empty forms gives 0. Both engines return
identical values.
