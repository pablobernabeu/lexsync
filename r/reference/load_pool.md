# Load a supplied candidate pool of words and give it the matcher's dimensions

A researcher who already has a curated word list – from a previous
study, a norming session, a colleague – should not have to dress it up
as a corpus lexicon to get lexsync's matching, validation and datasheet.
This reads such a list and returns something the matcher accepts.

## Usage

``` r
load_pool(path, schema, lexicon = NULL, language = NULL)
```

## Arguments

- path:

  Path to a UTF-8 CSV with at least a `word` column.

- schema:

  The parsed schema (used when a lexicon is loaded).

- lexicon:

  Optional path to a derived lexicon to draw dimensions from.

- language:

  Optional language label recorded in a `language` column.

## Value

A list with `pool` (the data frame, carrying `word`, `id`, `length`,
`n_syllables` and any joined or supplied dimensions) and `reference`
(the word vector the neighbourhood dimensions should be computed
against).

## Details

The list needs only a `word` column. Length and the syllable estimate
are derived from the form. Everything else is either supplied on the
list itself or looked up: with `lexicon` given, the corpus dimensions
(frequency above all) are joined for those words, and a word the lexicon
does not have is a hard error rather than an `NA`, because the tolerance
windows drop `NA` rows silently and the pool would then be smaller than
the user believes it is.

The returned `reference` matters as much as the pool. `n_density` and
`old20` are properties of a word in its *language*, not among the
handful of words a study happens to use, so computing them against a
200-word supplied list would give numbers that mean nothing. When a
lexicon is given, the reference is the lexicon's words; only without one
does it fall back to the pool itself.
