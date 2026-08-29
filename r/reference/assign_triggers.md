# Assign EEG trigger codes to stimuli

Adds `condition_trigger` (101, 102, ... per condition) and
`item_trigger` (40-239 per item/`set`). Events reference these by the
tokens "condition" and "item", or carry their own integer codes. The
item range holds 200 codes (an 8-bit-port constraint), so past 200 sets
the codes wrap and repeat, and a runtime notice says so.

## Usage

``` r
assign_triggers(stimuli)
```

## Arguments

- stimuli:

  A stimuli data frame.

## Value

`stimuli` with trigger columns added.
