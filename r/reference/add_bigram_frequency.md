# Mean bigram probability (type-based, non-positional), a phonotactic-probability proxy

For each word, the mean over its adjacent letter bigrams of the corpus
bigram probability (count divided by the total bigram count). It is
computed from integer counts and then rounded.

## Usage

``` r
add_bigram_frequency(df, reference = NULL)
```

## Arguments

- df:

  A data frame with a `word` column.

- reference:

  A character vector of reference words (defaults to `df$word`).

## Value

`df` with an added numeric `bigram_freq` column.
