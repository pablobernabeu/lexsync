# Read a YAML configuration file

An unquoted `y`, `Y`, `n` or `N` is read as text, as the Python engine
reads it, though YAML 1.1 lists them among its booleans. The other
boolean spellings (`yes`, `no`, `true`, `false`, `on` and `off`) are
booleans in both engines. The file is read as UTF-8 whatever the session
locale, and a file that is not UTF-8 is refused.

## Usage

``` r
read_config(path)
```

## Arguments

- path:

  Path to a YAML file.

## Value

A named list.
