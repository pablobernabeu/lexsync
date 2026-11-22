# Compute orthographic-neighbourhood dimensions (Coltheart's N and OLD20)

`n_density` is Coltheart's N: the number of reference words of the same
length differing by a single letter substitution (Hamming distance 1).
`old20` is the mean Levenshtein distance to the `n_old` (default 20)
nearest other reference words (Yarkoni et al., 2008). Both are computed
against `reference`, which should be a large word list (typically the
whole lexicon), not just the experimental pool.

## Usage

``` r
add_neighbourhood(df, reference = df$word, n_old = 20L)
```

## Arguments

- df:

  A data frame with a `word` column.

- reference:

  A character vector of reference words, `df$word` by default.
  Duplicates count once.

- n_old:

  Neighbourhood size for OLD (default 20). The column is named `old20`
  whatever its value.

## Value

`df` with added integer `n_density` and numeric `old20` columns. A word
with fewer than `n_old` other words in the reference has the mean over
those it has, and `old20` is `NA` for a word with none.

## References

Yarkoni, T., Balota, D., & Yap, M. (2008). Moving beyond Coltheart's N:
A new measure of orthographic similarity. *Psychonomic Bulletin &
Review, 15*(5), 971-979.
[doi:10.3758/PBR.15.5.971](https://doi.org/10.3758/PBR.15.5.971)
