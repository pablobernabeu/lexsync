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

  Named integer vector of bigram counts: one element for each pair of
  adjacent characters in the reference words, named by the pair and
  holding the number of times it occurs. A candidate is legal only when
  every one of its bigrams is among the names.

- lexset:

  Environment used as a set of the real word forms a pseudoword must
  avoid: each form is the name of a variable in it, whatever its value.

- usedset:

  Environment used as a set of the pseudowords already taken, in the
  same way. The function only reads it, so a caller generating several
  pseudowords assigns each result into it.

- alphabet:

  Character vector of the letters substituted in, in UTF-8 byte order.
  The default, `NULL`, takes the letters of the bigram table's names,
  which hold every letter a legal candidate of two letters or more can
  use.
  [`generate_pseudowords()`](https://pablobernabeu.github.io/lexsync/r/reference/generate_pseudowords.md)
  passes the letters of the whole reference.

## Value

A single pseudoword string, or `NULL` if no legal candidate exists.

## Details

[`generate_pseudowords()`](https://pablobernabeu.github.io/lexsync/r/reference/generate_pseudowords.md)
builds `bigrams` and `lexset` from a reference word list and `usedset`
from the pseudowords it generates, and is the function for ordinary use.
