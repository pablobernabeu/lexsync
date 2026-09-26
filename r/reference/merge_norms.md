# Left-join a norm table (e.g. concreteness, age of acquisition, valence)

The connector for semantic dimensions: the norm data themselves are
fetched separately (licensing varies), then merged here so the matcher
can equate on them. The join is deterministic and identical across
engines.

## Usage

``` r
merge_norms(lexicon, norms, on = "word", columns = NULL)
```

## Arguments

- lexicon:

  A lexicon data frame.

- norms:

  A data frame or the path to a CSV with a word column and norms.

- on:

  The join column (default "word").

- columns:

  Optional norm columns to keep.

## Value

`lexicon` with the norm columns appended, in the lexicon's own row and
column order. Rows with no matching norm get `NA`.

## Details

The result is the lexicon itself with the norm columns appended, and the
key is looked up positionally rather than through
[`merge()`](https://rdrr.io/r/base/merge.html). That is what makes the
two engines agree by construction, with nothing to repair afterwards,
because [`merge()`](https://rdrr.io/r/base/merge.html) and
`pandas.merge` were measured to diverge in three ways, each of them
silent: R hoists the `by` column to position 1 while pandas keeps the
left frame's order, so the column order differed whenever `on` was not
already first; R disambiguates a colliding column name with `.x`/`.y`
and pandas with `_x`/`_y`, and either way a dimension the design matches
on disappears under a name nothing looks for; and `merge(sort = FALSE)`
leaves the row order unspecified, so x's order is not carried through. A
positional lookup has none of those degrees of freedom: the output is
the input plus columns, in both engines. A colliding name is now an
error instead.

The key is trimmed and case-folded on *both* sides. Only the norm
table's side was normalised before, so a lexicon holding `Dog` matched
nothing and the design carried on with an all-`NA` dimension. Because
both engines agreed on that wrong answer, no parity test could have
caught it. The lexicon's own spelling is preserved rather than folded in
place: `word` is the byte-order tie-break behind every selection, so the
join must not rewrite it.
