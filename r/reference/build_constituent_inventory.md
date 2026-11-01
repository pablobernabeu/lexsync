# Attested subsyllabic constituents keyed by "role\|length" with integer counts

Attested subsyllabic constituents keyed by "role\|length" with integer
counts

## Usage

``` r
build_constituent_inventory(reference_words)
```

## Arguments

- reference_words:

  Character vector of reference words.

## Value

An environment whose names are "role\|length" keys, such as "onset\|2",
each holding a named integer vector counting every attested constituent
of that role and length.
