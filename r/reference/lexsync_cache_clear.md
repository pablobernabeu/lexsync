# Remove fetched corpora from the cache

Deletes what
[`fetch_corpus()`](https://pablobernabeu.github.io/lexsync/r/reference/fetch_corpus.md)
put in
[`lexsync_cache_dir()`](https://pablobernabeu.github.io/lexsync/r/reference/lexsync_cache_dir.md).
Given a `name`, that is the corpus's `<name>.csv` and any
`<name>.csv.part` that an interrupted download left behind. With `name`
left `NULL` it is the whole cache directory. A corpus needed again is
downloaded afresh by the next
[`fetch_corpus()`](https://pablobernabeu.github.io/lexsync/r/reference/fetch_corpus.md)
call. A file that
[`fetch_corpus()`](https://pablobernabeu.github.io/lexsync/r/reference/fetch_corpus.md)
wrote to a `dest` of the caller's choosing is not in the cache, and is
never touched.

## Usage

``` r
lexsync_cache_clear(name = NULL)
```

## Arguments

- name:

  A corpus name as given to
  [`fetch_corpus()`](https://pablobernabeu.github.io/lexsync/r/reference/fetch_corpus.md),
  or `NULL` (the default) to remove the whole cache.

## Value

The paths of the files removed, invisibly. The vector is empty when
there was nothing to remove.

## See also

[`lexsync_cache_dir()`](https://pablobernabeu.github.io/lexsync/r/reference/lexsync_cache_dir.md)
for where the cache lives.

## Examples

``` r
# A throwaway cache stands in for yours, so running this leaves your own alone.
local({
  tmp <- tempfile("lexsync-")
  old <- Sys.getenv("R_USER_CACHE_DIR", unset = NA)
  on.exit({
    if (is.na(old)) Sys.unsetenv("R_USER_CACHE_DIR") else
      Sys.setenv(R_USER_CACHE_DIR = old)
    unlink(tmp, recursive = TRUE)
  })
  Sys.setenv(R_USER_CACHE_DIR = tmp)
  # Two corpora and an interrupted download
  dir.create(lexsync_cache_dir(), recursive = TRUE)
  invisible(file.create(file.path(lexsync_cache_dir(),
    c("subtlex_nl.csv", "subtlex_nl.csv.part", "lexique_fr.csv"))))
  # One corpus, with its partial download
  print(basename(lexsync_cache_clear("subtlex_nl")))
  # Everything else, and the directory itself
  print(basename(lexsync_cache_clear()))
  dir.exists(lexsync_cache_dir())
})
#> [1] "subtlex_nl.csv"      "subtlex_nl.csv.part"
#> [1] "lexique_fr.csv"
#> [1] FALSE
```
