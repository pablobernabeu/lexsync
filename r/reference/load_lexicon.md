# Load a lexicon from a CSV file

Reads a derived lexicon, validates the column contract, lower-cases the
orthographic form and normalises it to Unicode NFC, removes duplicates
(keeping the first row in file order) and attaches a stable integer `id`
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

A data frame with at least `word`, `length`, `n_syllables`, `frequency`
and `id`, plus the frequency column the schema names (by default
`freq_zipf`) and every other column the file carried. Rows are in byte
order of `word` and `id` numbers them from 1. When normalisation changed
or merged any word, the attribute `input_normalisation` holds
`list(changed, collapsed)`: the words it rewrote and the duplicate rows
it removed.

## Details

A `freq_zipf` value outside 0 to 9 is refused: it is almost always a
frequency per million in the wrong column (convert it with
[`normalise_lexicon()`](https://pablobernabeu.github.io/lexsync/r/reference/normalise_lexicon.md)).
A log count such as SUBTLEX-US's `Lg10WF`, log10(count + 1) and at most
6.33, passes the check and must still be converted, since it reads about
1.3 below Zipf.

## Examples

``` r
# Both inputs are bundled with the package, so this runs offline and touches
# nothing outside the installation.
schema <- yaml::read_yaml(system.file("extdata", "schema.yaml", package = "lexsync"))
lex <- load_lexicon(system.file("extdata", "en_example.csv", package = "lexsync"),
                    schema)
head(lex[, c("word", "frequency", "length", "n_syllables")])
#>        word frequency length n_syllables
#> 1       aaa      3.77      3           1
#> 2       aba      3.32      3           2
#> 3     aback      2.99      5           2
#> 4   abandon      4.02      7           3
#> 5 abandoned      4.40      9           4
#> 6   abdomen      3.56      7           3
```
