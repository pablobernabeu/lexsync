# Split a word into ordered (role, text) subsyllabic constituents

Nuclei are the maximal runs of vowels, a vowel being a letter whose base
letter is in the vowel class of
[`count_syllables()`](https://pablobernabeu.github.io/lexsync/r/reference/count_syllables.md),
so an accented vowel counts. Consonants before the first nucleus form
the first onset, those after the last nucleus the final coda, and a
consonant run between two nuclei is split at its midpoint (floor(m/2) to
the left coda). Segmentation is on characters, so accented letters are
handled identically in the two engines. A word with a character that is
not a letter (a hyphen, an apostrophe, a digit) or with no vowel, such
as a Cyrillic word, returns an empty list, and the caller falls back to
letter substitution. Mirrors segment_subsyllabic in generation.py.

## Usage

``` r
segment_subsyllabic(word)
```
