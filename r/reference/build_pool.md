# Build an experimental candidate pool by filtering a lexicon

A filter naming a column the frame does not have is silently skipped,
because the same function filters lexica, supplied pools and pair
tables, and those carry different columns. The cost is that a misspelt
key silently widens a selection, so every caller that takes its filters
from a design checks the names against the frame first:
[`run_pipeline()`](https://pablobernabeu.github.io/lexsync/r/reference/run_pipeline.md)
for `pool_filters`,
[`match_stimuli()`](https://pablobernabeu.github.io/lexsync/r/reference/match_stimuli.md)
for a condition's `define_by`, and the pair selector for both.

## Usage

``` r
build_pool(lexicon, filters = NULL)
```

## Arguments

- lexicon:

  A lexicon data frame.

- filters:

  A named list mapping columns to either a numeric `c(min, max)` range
  or a vector of permitted values.

## Value

The filtered lexicon, with row names dropped. A row missing the filtered
column is dropped under either kind of filter, and a range with a
reversed or non-finite bound is an error rather than an empty pool.

## Examples

``` r
schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"),
                    schema)
nrow(build_pool(lex, list(length = c(4, 6), frequency = c(4, 6))))
#> [1] 406
```
