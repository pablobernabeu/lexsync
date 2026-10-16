# Write a data frame to a BOM-free UTF-8 CSV file

Write a data frame to a BOM-free UTF-8 CSV file

## Usage

``` r
write_csv_utf8(x, path)
```

## Arguments

- x:

  A data frame.

- path:

  Output path; parent directories are created as needed.

## Value

`path`, invisibly.

## Details

A value the two engines cannot render alike is refused, naming the
column: a magnitude at or above 1e15, where readr has three incompatible
layouts and no rule fits all of them, and a value with two equally short
decimal forms, where the two writers pick opposite ones.
