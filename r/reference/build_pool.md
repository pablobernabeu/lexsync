# Build an experimental candidate pool by filtering a lexicon

Build an experimental candidate pool by filtering a lexicon

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

The filtered lexicon.

## Examples

``` r
schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"),
                    schema)
nrow(build_pool(lex, list(length = c(4, 6), frequency = c(4, 6))))
#> [1] 406
```
