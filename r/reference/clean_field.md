# Validate a single stimulus value for safe inclusion in generated files

Rejects control characters (including tab/newline) and over-long
strings, so a crafted item cannot corrupt the generated loop table or
experiment scripts. Commas and quotation marks are allowed: presented
strings are written as data into a properly quoted CSV the experiment
reads at run time, never interpolated into generated code. Mirrors the
Python `clean_field`.

## Usage

``` r
clean_field(value, field = "field", max_len = 1000L)
```

## Arguments

- value:

  A value coerced to a single string.

- field:

  Field name, for error messages.

- max_len:

  Maximum permitted length in characters.

## Value

The value as a plain string.
