# Validate a lexicon against the schema column contract

Validate a lexicon against the schema column contract

## Usage

``` r
validate_lexicon(df, schema)
```

## Arguments

- df:

  A candidate lexicon data frame.

- schema:

  The parsed schema, such as
  `yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))`.

## Value

`TRUE`, invisibly; stops with an informative error otherwise.
