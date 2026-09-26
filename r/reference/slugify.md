# Build a short, filesystem-safe slug

Keeps generated file names short and space-free, which avoids the
Windows `MAX_PATH` limit inside deeply nested, cloud-synced directories.

## Usage

``` r
slugify(...)
```

## Arguments

- ...:

  Character fragments to join.

## Value

A lower-case, underscore-separated slug.
