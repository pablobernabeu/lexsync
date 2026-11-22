# Left-join a norm table (such as concreteness, age of acquisition or valence)

Norm data, such as semantic dimensions, are fetched separately, since
their licences vary, and joined here so that the matcher can equate on
them. The join is deterministic.

## Usage

``` r
merge_norms(lexicon, norms, on = "word", columns = NULL)
```

## Arguments

- lexicon:

  A lexicon data frame.

- norms:

  A data frame, or the path to a UTF-8 CSV, holding the `on` column and
  the norm columns.

- on:

  The join column (default `"word"`).

- columns:

  Optional norm columns to keep.

## Value

`lexicon` with the norm columns appended, in the lexicon's own row and
column order. Rows with no matching norm get `NA`.

## Details

The result is the lexicon itself with the norm columns appended, so no
lexicon column is moved or renamed and no row is reordered. A norm
column whose name the lexicon already has is refused.

The key is trimmed, case-folded and normalised to NFC on both sides, so
a lexicon holding `Dog` matches a norm row for `dog`. The lexicon's own
spelling is preserved rather than folded in place: `word` is the
byte-order tie-break behind every selection, so the join must not
rewrite it. A missing key never matches, and when two rows of the norm
table share a key once it is normalised, the first of them is used.
