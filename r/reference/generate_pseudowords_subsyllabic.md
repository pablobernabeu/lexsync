# A subsyllabic pseudoword for each base word (with letter-substitution fallback)

The base words are taken in byte order, each given
[`make_subsyllabic_pseudoword()`](https://pablobernabeu.github.io/lexsync/r/reference/make_subsyllabic_pseudoword.md)'s
form or, when it has none,
[`make_pseudoword()`](https://pablobernabeu.github.io/lexsync/r/reference/make_pseudoword.md)'s,
and no two share a pseudoword. `exclude` is as for
[`generate_pseudowords()`](https://pablobernabeu.github.io/lexsync/r/reference/generate_pseudowords.md),
and so are the letters of the letter-substitution fallback and the
refusal of a logographic base word.

## Usage

``` r
generate_pseudowords_subsyllabic(base_words, reference_words, exclude = NULL)
```

## Arguments

- base_words:

  Character vector of words to derive pseudowords from.

- reference_words:

  Character vector (typically the full lexicon) that supplies the bigram
  statistics and the real word forms to avoid.

- exclude:

  Optional character vector of further word forms no pseudoword may
  equal, such as low-frequency words the reference lacks. They are
  trimmed, lower-cased and put in Unicode NFC, as a lexicon's words are,
  and play no part in the bigram statistics.

## Value

A data frame with columns `base_word` and `pseudoword`, in the order of
`base_words`. A base word for which neither generator finds a form is an
error.
