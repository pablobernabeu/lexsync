# Download a registered corpus into the cache

Downloads the file a registry entry names and caches it as a lexicon
that
[`load_lexicon()`](https://pablobernabeu.github.io/lexsync/r/reference/load_lexicon.md)
reads. `name` must be a single corpus name: one holding a slash, a
backslash or a colon is refused before the registry is read, since the
name becomes the cached file's name.

## Usage

``` r
fetch_corpus(name, registry_path = NULL, dest = NULL)
```

## Arguments

- name:

  A corpus name present in the registry.

- registry_path:

  Optional path to `registry.yaml`. A path that does not exist is
  refused.

- dest:

  Optional destination file; defaults to `<name>.csv` in
  [`lexsync_cache_dir()`](https://pablobernabeu.github.io/lexsync/r/reference/lexsync_cache_dir.md).

## Value

The path to the downloaded file, invisibly.

## Details

An entry's `derived` file, a lexicon already normalised, is fetched when
it has one and cached as it arrives. Otherwise its `openlexicon` file is
fetched and converted by
[`normalise_lexicon()`](https://pablobernabeu.github.io/lexsync/r/reference/normalise_lexicon.md)
with the entry's `columns` and `duplicates`, so
`fetch_corpus("subtlex_us")` caches SUBTLEX-US as a lexicon. The URL's
scheme is checked first. The transfer then lands in a sidecar file that
is renamed into place only after the size cap, the markup sniff, any
`sha256` the registry entry carries and the normalisation have all
passed. Every refusal names the registry file it read. The download is
recorded so it can be cited; consult
[`list_corpora()`](https://pablobernabeu.github.io/lexsync/r/reference/list_corpora.md)
for the citation.

The lexica of the wordfreq connector's languages are built by the Python
package (`lexsync fetch fr`), and this package reads the result with
[`load_lexicon()`](https://pablobernabeu.github.io/lexsync/r/reference/load_lexicon.md).
A wordfreq language code given here is refused with that explanation.

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
