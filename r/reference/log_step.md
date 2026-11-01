# Append a step to a run log

Append a step to a run log

## Usage

``` r
log_step(log, message, data = NULL)
```

## Arguments

- log:

  A run-log object.

- message:

  A short description of the step.

- data:

  An optional named list of step details.

## Value

The updated run-log object.

## Details

While the option `lexsync.verbose` is `TRUE`, its default, the message
is also printed to the console as `[lexsync] <message>` with
[`cat()`](https://rdrr.io/r/base/cat.html), so
[`suppressMessages()`](https://rdrr.io/r/base/message.html) does not
silence it. Set `options(lexsync.verbose = FALSE)` to keep it quiet.
[`run_pipeline()`](https://pablobernabeu.github.io/lexsync/r/reference/run_pipeline.md)
sets the option from its `verbose` argument for the length of the run
and restores it afterwards.
