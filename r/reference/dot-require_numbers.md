# Refuse a lexicon column that the shared CSV rule did not read as numbers

A value such as "1,000" leaves the whole column text under that rule.
[`as.numeric()`](https://rdrr.io/r/base/numeric.html) would then turn it
into `NA` with a warning, while the Python engine failed inside pandas'
float conversion, so the refusal is spelled out, naming the first value
that is not a plain decimal number. Mirrors `_require_numbers` in
python_workflow/src/lexsync/querying.py.

## Usage

``` r
.require_numbers(x, name)
```

## Arguments

- x:

  The column.

- name:

  Its name, for the message.

## Value

`NULL`, invisibly, or an error.
