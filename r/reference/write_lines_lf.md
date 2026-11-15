# Write text to a file with LF line endings on every platform

`writeLines(x, path)` opens the path in text mode, so on Windows R turns
every newline into CRLF. The generated experiment scripts are compared
against the Python engine's byte for byte, and their checksums are
published in the materials datasheet, so their bytes must not record
which operating system produced them. A binary connection writes the
string as given.

## Usage

``` r
write_lines_lf(x, path)
```

## Arguments

- x:

  A character vector of lines.

- path:

  Output path; parent directories are created as needed.

## Value

`path`, invisibly.
