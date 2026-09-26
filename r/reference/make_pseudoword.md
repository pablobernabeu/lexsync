# The most bigram-plausible legal non-word at the smallest edit distance

Searches single-letter substitutions first, then two-letter
substitutions; candidates are ranked by summed bigram frequency with a
byte-order tie-break, so the choice is deterministic and identical
across engines.

## Usage

``` r
make_pseudoword(word, bigrams, lexset, usedset)
```

## Arguments

- word:

  The base word to derive the pseudoword from.

- bigrams:

  Named integer vector of bigram counts, from
  [`bigram_counts()`](https://pablobernabeu.github.io/lexsync/r/reference/bigram_counts.md).

- lexset:

  Environment used as a set of the real word forms a pseudoword must
  avoid.

- usedset:

  Environment used as a set of the pseudowords already taken.

## Value

A single pseudoword string, or `NULL` if no legal candidate exists.
