# The paradigm registry: default event sequences and required fields

Each event is a list with `type` (fixation \| text \| mask \| blank \|
region_by_region \| response \| question \| feedback), `content` (a
literal or a `{field}` reference), an optional `trigger` (an integer EEG
code or the token "condition"/"item"), `onset_locked`, response
`keys`/`timeout_ms`, and an optional `blocks` restricting the event to
named blocks.

## Usage

``` r
PARADIGMS
```

## Format

A named list with one entry per paradigm (`factorial`,
`lexical_decision`, `priming`, `categorisation`, `self_paced_reading`),
each holding `stimulus_fields`, a `counterbalance` recipe and an
`events` list.
