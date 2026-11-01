# Integer counts of adjacent character bigrams across a word list

Every pair of adjacent characters in every word is counted, each
occurrence once and as written: case is kept, and a hyphen, an
apostrophe or a digit forms bigrams as a letter does.

## Usage

``` r
bigram_counts(words)
```

## Arguments

- words:

  Character vector of words, typically the whole reference lexicon.

## Value

A named integer vector with one count per distinct bigram, named by it.
