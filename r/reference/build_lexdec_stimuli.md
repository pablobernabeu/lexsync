# Assemble a word-vs-pseudoword lexical-decision set from a candidate pool

Real words are drawn by an even spread across the byte-ordered pool,
then a length-matched pseudoword is generated for each. The pool is
first filtered to lower-case a-z forms, the only ones the pseudoword
generators are defined for, so the eligible pool can be smaller than the
request; the pipeline's shortfall policy then decides whether that
errors. `reference_words` (the full lexicon) supplies the bigram
statistics and the real-word list a pseudoword must avoid. The presented
string is the `target` column; conditions are `word` and `pseudoword`
and `set` pairs them.

## Usage

``` r
build_lexdec_stimuli(
  pool,
  n,
  reference_words = NULL,
  method = "letter_substitution"
)
```

## Arguments

- pool:

  Data frame of candidate words, e.g. from
  [`build_pool()`](https://pablobernabeu.github.io/lexsync/r/reference/build_pool.md).

- n:

  Number of real words to select.

- reference_words:

  Character vector supplying the bigram statistics and the real word
  forms a pseudoword must avoid; defaults to the pool's words.

- method:

  Pseudoword generator: `"letter_substitution"` (default) or
  `"subsyllabic"` (Wuggy-style; Keuleers & Brysbaert, 2010).

## Value

A stimulus data frame with `target`, `condition` and `set` columns.
