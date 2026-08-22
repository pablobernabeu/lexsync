# Orthographic syllable estimate: the number of maximal vowel runs

Orthographic syllable estimate: the number of maximal vowel runs

## Usage

``` r
count_syllables(word)
```

## Arguments

- word:

  Character vector of word forms.

## Value

Integer vector: the estimated syllable count of each word.

## Examples

``` r
count_syllables(c("cat", "table", "beautiful"))
#> [1] 1 2 3
```
