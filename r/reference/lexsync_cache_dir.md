# Per-user cache directory for fetched corpora

The directory `tools::R_user_dir("lexsync", "cache")` names for this
package, created on first use. It is where
[`fetch_corpus()`](https://pablobernabeu.github.io/lexsync/r/reference/fetch_corpus.md)
puts a download unless told otherwise, and it is the only place the
package writes to without being handed a path.

## Usage

``` r
lexsync_cache_dir()
```

## Value

A writable cache directory path (created if absent).

## Details

The cache persists between sessions and lexsync never prunes it. A
registered corpus is a delimited word list, and a download is refused
above 200 MB, so a cache holding several large corpora can reach a few
hundred megabytes. It holds nothing that cannot be fetched again, so it
may be deleted at any time, whole or file by file, and the next call
downloads afresh.
