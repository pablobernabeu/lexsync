# Load a lexicon from a CSV file

Reads a derived lexicon, validates the column contract, lower-cases the
orthographic form, removes duplicates and attaches a stable integer `id`
plus the inexpensive dimensions `length` and `frequency`. The
orthographic neighbourhood dimensions are added later, on the
experimental pool, by
[`add_neighbourhood()`](https://pablobernabeu.github.io/lexsync/r/reference/add_neighbourhood.md),
because they are quadratic in the size of the reference set.

## Usage

``` r
load_lexicon(path, schema, language = NULL)
```

## Arguments

- path:

  Path to a derived lexicon CSV.

- schema:

  The parsed schema (see `config/schema.yaml`).

- language:

  Optional language label to record in a `language` column.

## Value

A data frame with at least `word`, `freq_zipf`, `length`, `frequency`
and `id`.

## Examples

``` r
# Both inputs are bundled with the package, so this runs offline and touches
# nothing outside the installation.
schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"),
                    schema)
head(lex[, c("word", "frequency", "length", "n_syllables")])
#>      word frequency length n_syllables
#> 1     aaa      3.77      3           1
#> 2     aac      3.00      3           1
#> 3     aap      3.47      3           1
#> 4   aaron      4.23      5           2
#> 5     aba      3.32      3           2
#> 6 abandon      4.02      7           3
```
