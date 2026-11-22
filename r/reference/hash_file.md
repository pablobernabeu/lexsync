# MD5 digest of a file, for provenance logging

MD5 (from base tools) is used as a lightweight content fingerprint. It
is a provenance aid, not a security measure. The Python package uses the
same algorithm, so the run logs of the two engines can be compared.

## Usage

``` r
hash_file(path)
```

## Arguments

- path:

  File path.

## Value

A hex digest string, or `NA` when the file is absent.
