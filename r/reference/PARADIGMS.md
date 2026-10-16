# The paradigm registry: default event sequences and required fields

Each event is a list with `type` (fixation \| text \| mask \| blank \|
region_by_region \| response \| question \| feedback), `content` (a
literal or a `{field}` reference), an optional `trigger` (a whole-number
EEG code from 1 to 255 or the token "condition"/"item"), `onset_locked`,
response `keys`/`timeout_ms`, a response's `from` (where its window
opens: "onset", with the text event before it, which is the default
after a text event, or "offset", once that has gone), a text event's
`case` ("upper" or "lower", applied by the runners as they show the
text), a mask's `length_of` (the fields whose longest text, in
characters, sets how often its one-character content is repeated), and
an optional `blocks` restricting the event to named blocks.

## Usage

``` r
PARADIGMS
```

## Format

A named list with one entry per paradigm (`factorial`,
`lexical_decision`, `priming`, `masked_priming`, `categorisation`,
`self_paced_reading`), each holding `stimulus_fields`, a
`counterbalance` recipe and an `events` list.

## Value

A plain named list (class `"list"`; no package-specific class) of
built-in paradigm specifications. Each element contains
`stimulus_fields`, a character vector naming required item-table fields;
`counterbalance`, a character scalar naming the counterbalancing recipe;
and `events`, an ordered list of event-specification lists. The selected
entry supplies the default trial sequence, required item fields, and
counterbalancing rule inherited by a design that names that paradigm.

## Details

`priming` is backward-masked: a 50 ms prime, a 33 ms `#####` mask and
the target, with no forward mask and the item table's letter case.
`masked_priming` follows Forster and Davis (1984): a forward mask of
hash marks for 500 ms, a lower-case prime for three frames and an
upper-case target that stays on until the response or for 2,000 ms.

## References

Forster, K. I., & Davis, C. (1984). Repetition priming and frequency
attenuation in lexical access. *Journal of Experimental Psychology:
Learning, Memory, and Cognition, 10*(4), 680-698.
[doi:10.1037/0278-7393.10.4.680](https://doi.org/10.1037/0278-7393.10.4.680)
