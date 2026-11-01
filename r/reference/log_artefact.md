# Record a written artefact (path, rows, fingerprint) in the log

Record a written artefact (path, rows, fingerprint) in the log

## Usage

``` r
log_artefact(log, path, rows = NA_integer_)
```

## Arguments

- log:

  A run-log object.

- path:

  A file path that has just been written.

- rows:

  Optional row count.

## Value

The updated run-log object.

## Details

The step is added with
[`log_step()`](https://pablobernabeu.github.io/lexsync/r/reference/log_step.md),
so it is printed to the console as `[lexsync] wrote '<file>'` while the
option `lexsync.verbose` is `TRUE`.
