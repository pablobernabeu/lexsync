# The most bigram-plausible legal non-word at the smallest edit distance

Searches single-letter substitutions first, then two-letter
substitutions; candidates are ranked by summed bigram frequency with a
byte-order tie-break, so the choice is deterministic and identical
across engines.

## Usage

``` r
make_pseudoword(word, bigrams, lexset, usedset, alphabet = NULL)
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

- alphabet:

  Character vector of the letters substituted in, in UTF-8 byte order.
  The default, `NULL`, takes the letters of the bigram table's names,
  which hold every letter a legal candidate of two letters or more can
  use.
  [`generate_pseudowords()`](https://pablobernabeu.github.io/lexsync/r/reference/generate_pseudowords.md)
  passes the letters of the whole reference.

## Value

A single pseudoword string, or `NULL` if no legal candidate exists.
