# A length-matched pseudoword for each base word (byte-order processing)

A length-matched pseudoword for each base word (byte-order processing)

## Usage

``` r
generate_pseudowords(base_words, reference_words)
```

## Arguments

- base_words:

  Character vector of words to derive pseudowords from.

- reference_words:

  Character vector (typically the full lexicon) that supplies the bigram
  statistics and the real word forms to avoid.

## Value

A data frame with columns `base_word` and `pseudoword`.
