# Orthographic syllable estimate: the number of maximal vowel runs

Counts the maximal runs of Latin vowel letters after decomposing the
word and setting its diacritics aside, so a vowel counts whatever its
accent. The vowels of Polish, Czech, Hungarian, Romanian, Turkish,
Danish, Norwegian and Vietnamese count as those of English, Spanish,
French and German do. Hiatus (`idea` counts 2) and syllabic consonants
such as the Czech l in `vlk` and r in `krk` stay undercounted.

## Usage

``` r
count_syllables(word)
```

## Arguments

- word:

  Character vector of word forms.

## Value

Integer vector: the estimated syllable count of each word, or `NA` for a
missing word and for a word holding a character outside the Latin script
(Chinese, Cyrillic or Greek, for example), where the estimate is
undefined.

## Examples

``` r
count_syllables(c("cat", "table", "beautiful"))
#> [1] 1 2 3
```
