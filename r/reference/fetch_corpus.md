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

  Optional destination file; defaults to `<name>.csv` in
  [`lexsync_cache_dir()`](https://pablobernabeu.github.io/lexsync/r/reference/lexsync_cache_dir.md).

## Value

The path to the downloaded file, invisibly.

## Details

The file lands in
[`lexsync_cache_dir()`](https://pablobernabeu.github.io/lexsync/r/reference/lexsync_cache_dir.md)
unless `dest` names somewhere else. The cache directory is created only
once the registry entry and its URL have been accepted, so a refused
call writes nothing. A download to the default destination begins by
deleting any `.part` sidecar in the cache that an interrupted transfer
left there more than a day earlier. The cache persists between sessions,
and one corpus may reach the 200 MB download cap, so several of them add
up.
[`lexsync_cache_clear()`](https://pablobernabeu.github.io/lexsync/r/reference/lexsync_cache_clear.md)
removes one corpus or the whole cache, and the next call downloads the
corpus again. A `dest` the caller names, inside the cache or not, is
used as given. Its directory must already exist, no sidecar is swept,
and the only file beside it that lexsync writes or deletes is the
`<dest>.part` sidecar of the download itself.
