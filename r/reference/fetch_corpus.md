# Download a CSV-format registered corpus into the cache

Suitable for Connector A corpora that expose a delimited file. The URL's
scheme is checked first; the transfer then lands in a sidecar file that
is renamed into place only after the size cap, the markup sniff and any
`sha256` the registry entry carries have all passed. The download is
recorded so it can be cited; consult
[`list_corpora()`](https://pablobernabeu.github.io/lexsync/r/reference/list_corpora.md)
for the citation.

## Usage

``` r
fetch_corpus(name, registry_path = NULL, dest = NULL)
```

## Arguments

- name:

  A corpus name present in the registry.

- registry_path:

  Optional path to `registry.yaml`.

- dest:

  Optional destination path; defaults to the cache.

## Value

The path to the downloaded file, invisibly.
