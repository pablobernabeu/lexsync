# A pseudoword built by swapping whole subsyllabic constituents

Up to ceil(2k/3) constituents (codas and nuclei before onsets) are each
replaced by an attested constituent of the same role and length, keeping
every bigram legal and the form a novel non-word; length is preserved.
Returns NULL if no legal swap exists (the caller falls back to letter
substitution). Mirrors make_subsyllabic_pseudoword in generation.py.

## Usage

``` r
make_subsyllabic_pseudoword(word, inv, bigrams, lexset, usedset)
```
