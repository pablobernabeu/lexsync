# Per-user cache directory for fetched corpora

The directory `tools::R_user_dir("lexsync", "cache")` names for this
package. It is where
[`fetch_corpus()`](https://pablobernabeu.github.io/lexsync/r/reference/fetch_corpus.md)
puts a download unless told otherwise, and it is the only place the
package writes to without being handed a path. This function only
reports the path. The directory is created by the first download into
it, so until then it does not exist.

## Usage

``` r
lexsync_cache_dir()
```

## Value

The cache directory path, which need not exist yet.

## Details

The cache persists between sessions. A registered corpus is a delimited
word list, and a download is refused above 200 MB, so a cache holding
several large corpora can reach a few hundred megabytes. Each download
into the cache first deletes any partial download that an interrupted
transfer left there more than a day earlier, and fetching a corpus again
replaces the earlier copy. Downloaded corpora otherwise stay until
[`lexsync_cache_clear()`](https://pablobernabeu.github.io/lexsync/r/reference/lexsync_cache_clear.md)
removes them, one corpus at a time or all together. Nothing kept there
is irreplaceable, so the next call downloads afresh.

## See also

[`lexsync_cache_clear()`](https://pablobernabeu.github.io/lexsync/r/reference/lexsync_cache_clear.md)
to empty the cache.

## Examples

``` r
lexsync_cache_dir()
#> [1] "/home/runner/.cache/R/lexsync"
```
