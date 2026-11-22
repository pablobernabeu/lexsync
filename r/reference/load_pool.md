# Load a supplied candidate pool of words and give it the matcher's dimensions

A curated word list, such as one from a previous study, a norming
session or a colleague, can be matched, validated and documented without
first being made into a corpus lexicon. This function reads such a list
and returns a pool the matcher accepts.

## Usage

``` r
load_pool(path, schema, lexicon = NULL, language = NULL)
```

## Arguments

- path:

  Path to a UTF-8 CSV with at least a `word` column. A path with a `..`
  component is refused. Give it from the working directory, or as an
  absolute path.

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
against). Words are trimmed, lower-cased and normalised to Unicode NFC
as in
[`load_lexicon()`](https://pablobernabeu.github.io/lexsync/r/reference/load_lexicon.md),
and `pool` carries the same `input_normalisation` attribute when that
changed or merged any word of the pool or the lexicon.

## Details

The list needs only a `word` column. Length and the syllable estimate
are derived from the form. Every other dimension is either supplied on
the list itself or looked up. With `lexicon` given, the corpus
dimensions (frequency above all) are joined for those words, and a word
the lexicon does not have is an error rather than an `NA`, because a
word missing a value would be left out of the candidates and the pool
would then be smaller than the user believes it is.

The returned `reference` matters as much as the pool. `n_density` and
`old20` describe a word within its language, not within the few words a
study uses, so computing them against a 200-word supplied list would
give meaningless numbers. When a lexicon is given, the reference is the
lexicon's words. Without one, it is the pool itself. A
`reference_member` column on whichever of the two supplies the reference
keeps only the rows it marks 1.
