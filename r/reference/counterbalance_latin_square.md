# One row per item per list, condition rotated across lists (Latin square)

Each item (`set`) contributes exactly one trial to a list, so its target
is never repeated within a list. The conditions are balanced when the
lists and the item sets are both multiples of the number of conditions,
and `.counterbalance_check()` reports a rotation that is not. With
`lists` unset the number of lists equals the number of conditions.
Mirrors the Python recipe (byte-order condition list, zero-based
rotation), so the two engines assign the same condition to each item per
list.

## Usage

``` r
counterbalance_latin_square(stimuli, design, schema)
```
