# Compute orthographic-neighbourhood dimensions (Coltheart's N and OLD20)

`n_density` is Coltheart's N: the number of reference words of the same
length differing by a single letter substitution (Hamming distance 1).
`old20` is the mean Levenshtein distance to the 20 nearest reference
words (Yarkoni et al., 2008). Both are computed against `reference`,
which should be a large word list (typically the whole lexicon), not
just the experimental pool.

## Usage

``` r
add_neighbourhood(df, reference = df$word, n_old = 20L)
```

## Arguments

- df:

  A data frame with a `word` column.

- reference:

  A character vector of reference words.

- n_old:

  Neighbourhood size for OLD (default 20).

## Value

`df` with added integer `n_density` and numeric `old20` columns.
