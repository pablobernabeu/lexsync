# Read a UTF-8 CSV file by the rule both engines share

Every header name and cell is trimmed of spaces, tabs, carriage returns
and line feeds. After trimming, an empty cell and `NA` (quoted or not)
are missing, and every other word, `null`, `nan` and `none` included, is
a value. Each column not named in `as_character` then takes its type
from all of its values: numeric when every value is a plain decimal
number (no thousands separators), logical when every value is TRUE or
FALSE in upper, lower or title case, and text otherwise. Dates are never
parsed. A UTF-8 byte-order mark is ignored.

## Usage

``` r
read_csv_utf8(path, as_character = character(0), delim = ",")
```

## Arguments

- path:

  Path to a CSV file.

- as_character:

  Character vector of column names that stay text, trimmed. A name the
  file's header does not carry is ignored, and `TRUE` keeps every column
  as text.

- delim:

  `","`, or a tab character for a tab-separated file, which is read with
  no quoting, as tab-separated corpora such as SUBTLEX-US and Lexique
  are written: a quotation mark there is part of the cell. Mirrors the
  Python twin's `delim`.

## Value

A data frame (a tibble). An empty file gives one with no columns.
