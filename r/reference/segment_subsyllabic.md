# Split a word into ordered (role, text) subsyllabic constituents

Nuclei are the maximal vowel runs; consonants before the first nucleus
form the first onset, those after the last nucleus the final coda, and a
consonant run between two nuclei is split at its midpoint (floor(m/2) to
the left coda). An orthographic model for Latin a-z words only: any word
with a character outside a-z (accented, hyphenated, digit) returns an
empty list, as does a word with no vowel, and the caller falls back to
letter substitution. Mirrors segment_subsyllabic in generation.py.

## Usage

``` r
segment_subsyllabic(word)
```
