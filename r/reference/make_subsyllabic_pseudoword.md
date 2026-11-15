# A pseudoword built by swapping whole subsyllabic constituents

The word is split with
[`segment_subsyllabic()`](https://pablobernabeu.github.io/lexsync/r/reference/segment_subsyllabic.md)
into k constituents. A constituent is eligible when the reference
attests at least two forms of its role and length. The first ceil(2k/3)
eligible constituents, codas first, then nuclei, then onsets, each in
word order, are tried one at a time: each is replaced by the attested
form of the same role and length that keeps every bigram legal and the
form a novel non-word and has the highest summed bigram count, ties
broken by byte order, and is left as it is when there is none. Length is
preserved. Returns NULL when no constituent was replaced (the caller
falls back to letter substitution). Mirrors make_subsyllabic_pseudoword
in generation.py.

## Usage

``` r
make_subsyllabic_pseudoword(word, inv, bigrams, lexset, usedset)
```

## Arguments

- word:

  The base word.

- inv:

  The constituent inventory, from
  [`build_constituent_inventory()`](https://pablobernabeu.github.io/lexsync/r/reference/build_constituent_inventory.md).

- bigrams, lexset, usedset:

  As for
  [`make_pseudoword()`](https://pablobernabeu.github.io/lexsync/r/reference/make_pseudoword.md).

## Value

A single pseudoword string, or `NULL`.
