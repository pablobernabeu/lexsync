# Load a paradigm item table (prime-target pairs, sentences, ...)

The table must carry an `item` identifier, a `condition` label and the
paradigm's presented fields. Field values are validated (no control
characters; bounded length) so a crafted item cannot corrupt the
generated loop table or scripts. Items are mapped to a deterministic
integer `set` id (byte order), so counterbalancing matches the corpus
path and the two engines.

## Usage

``` r
load_items(path, required_fields)
```

## Arguments

- path:

  Path to a UTF-8 CSV item table.

- required_fields:

  Character vector of presented fields the paradigm needs.

## Value

A data frame with `set`, `condition` and the item fields.
