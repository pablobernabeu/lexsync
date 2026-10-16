# Translate paradigm events into backend-neutral rendering dictionaries

Durations are emitted as whole milliseconds (`ms`), the unit every
backend consumes: OpenSesame and jsPsych schedule it directly, and the
PsychoPy script converts it back into whole flips against the refresh
rate it measures at start-up.

## Usage

``` r
render_events(events, timing, hz = 60)
```

## Details

A response collected from the onset of the text event before it (see
`.response_from()`) is rendered with that event, as its `respond` entry
(`keys` and `timeout`). The text keeps `ms` as its longest display time,
and the window runs from its onset for `ms` plus the timeout, so the
total window is the one the two events had. A response collected from
the offset stays an event of its own. Keys are rendered as lists, which
jsonlite writes as arrays even for one key.

A text event's `case` is carried as it is, for the runners to apply. A
mask's `length_of` is carried too, with the one character to repeat as
its `text`, and the exporters write the mask out for their trials (see
`.sized_masks()`).
