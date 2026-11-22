# Load a paradigm item table (such as prime-target pairs or sentences)

The table must carry an `item` identifier, a `condition` label and the
paradigm's presented fields. Field values are validated (no control
characters and a bounded length), so a crafted item cannot corrupt the
generated loop table or scripts. Items are mapped to deterministic
integer `set` ids in byte order, so counterbalancing works as it does
for a corpus design. The item id, the condition and the presented fields
are normalised to Unicode NFC. When that changed any cell, the attribute
`input_normalisation` holds `list(changed, collapsed)`, with `collapsed`
always 0 since no row is removed.

## Usage

``` r
load_items(path, required_fields)
```

## Arguments

- path:

  Path to a UTF-8 CSV item table. A path with a `..` component is
  refused. Give it from the working directory, or as an absolute path.

- required_fields:

  Character vector of presented fields the paradigm needs.

## Value

A data frame with `set`, `condition` and the item fields.
