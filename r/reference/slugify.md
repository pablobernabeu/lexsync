# Build a filesystem-safe slug

Joins the fragments with underscores, turns every run of characters
other than ASCII letters and digits into one underscore, trims
underscores from both ends and lower-cases the result without regard to
the locale. The slug carries no spaces or punctuation, but its length is
not limited: long fragments give a long slug.

## Usage

``` r
slugify(...)
```

## Arguments

- ...:

  Character fragments to join.

## Value

A lower-case, underscore-separated slug of ASCII letters and digits,
empty when the fragments hold none.
