# The paradigm registry: default event sequences and required fields

Each event is a list with a `type` (fixation \| text \| mask \| blank \|
region_by_region \| response \| question \| feedback) and the keys its
type reads. `content` is a literal or a `{field}` reference. An event's
length, where it has one, is `duration_ms`, or `duration_frames`
converted at the schema's `presentation.assumed_refresh_hz`, and a
fixation, text, mask or blank event may instead take a per-trial
`duration` block (`from_column`, or `jitter` with an optional `as`, see
[`resolve_trial_timing()`](https://pablobernabeu.github.io/lexsync/r/reference/resolve_trial_timing.md)).
A fixation, text or mask event takes an optional `trigger` (a
whole-number EEG code from 1 to 255 or the token "condition"/"item"). A
response takes `keys`, `timeout_ms` and `from` (where its window opens:
"onset", with the text event before it, which is the default after a
text event, or "offset", once that has gone), and a question takes
`keys` and `timeout_ms`. A text event takes `case` ("upper" or "lower",
applied by the runners as they show the text), and a mask takes
`length_of` (the fields whose longest text, in characters, sets how
often its one-character content is repeated). A region-by-region event
takes `sep` (the region separator in its content, `"|"` by default),
`advance` (the key that shows the next region, `"space"` by default) and
`critical_region_trigger` (a code as for `trigger`, sent at the region
the item's `critical_region` names). A feedback event takes `answer`
(the field holding the correct key, `"answer"` by default) and its texts
`correct`, `incorrect` and `no_response`. Any event may take `blocks`,
restricting it to named blocks. Every event's `trigger` is written on
that event's onset flip, and `onset_locked`, which the built-in
paradigms set, is accepted but does not change this.

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
`masked_priming` has the arrangement of Forster and Davis (1984): a
forward mask of hash marks, a brief lower-case prime and an upper-case
target. Its defaults show the mask for 500 ms, the prime for three
frames and the target until the response or for 2,000 ms.

## References

Forster, K. I., & Davis, C. (1984). Repetition priming and frequency
attenuation in lexical access. *Journal of Experimental Psychology:
Learning, Memory, and Cognition, 10*(4), 680-698.
[doi:10.1037/0278-7393.10.4.680](https://doi.org/10.1037/0278-7393.10.4.680)
