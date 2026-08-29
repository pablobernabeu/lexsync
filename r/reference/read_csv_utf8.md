# Read a UTF-8 CSV file

Read a UTF-8 CSV file

## Usage

``` r
read_csv_utf8(path, as_character = character(0))
```

## Arguments

- path:

  Path to a CSV file.

- as_character:

  Character vector of column names whose type must not be guessed, read
  as text instead. A name the file's header does not carry is ignored,
  since readr warns about a parser for a column that is not there.

## Value

A data frame (a tibble), as returned by
[`readr::read_csv()`](https://readr.tidyverse.org/reference/read_delim.html).
