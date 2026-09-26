# Write a datasheet to a JSON record and a Markdown rendering

Write a datasheet to a JSON record and a Markdown rendering

## Usage

``` r
write_datasheet(ds, json_path, md_path)
```

## Arguments

- ds:

  A datasheet list, from
  [`build_datasheet()`](https://pablobernabeu.github.io/lexsync/r/reference/build_datasheet.md).

- json_path:

  Output path for the machine-readable JSON record.

- md_path:

  Output path for the human-readable Markdown rendering.

## Value

Invisibly, the two paths written.
