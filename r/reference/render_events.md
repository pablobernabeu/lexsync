# Translate paradigm events into backend-neutral rendering dictionaries

A fixation, text or mask event's `trigger` and a region-by-region
event's `critical_region_trigger` (rendered as `crit_trigger`) must be
the token `"condition"` or `"item"`, rendered as `"@condition_trigger"`
or `"@item_trigger"`, or a whole number from 1 to 255, written as a
number or as a string of digits and rendered as an integer. Any other
value is refused, naming the event by its place in `events`, counted
from 1.

## Usage

``` r
render_events(events, timing, hz = 60)
```

## Arguments

- events:

  The design's event list, as
  [`resolve_events()`](https://pablobernabeu.github.io/lexsync/r/reference/resolve_events.md)
  returns it.

- timing:

  The design's `timing` block, a named list. `NULL` or an empty list
  overrides nothing.

- hz:

  The refresh rate, in Hz, at which `*_frames` durations are converted
  to milliseconds. The exporters pass the schema's
  `presentation.assumed_refresh_hz`, 60 when it is absent.

## Value

A list of rendered events, one per event of `events`, except that a
response collected from the onset of the text event before it is merged
into that event as its `respond` entry.

## Details

`timing` sets durations by event type, in place of an event's own
`duration_ms` or `duration_frames` but not of a `duration:` block:
`fixation_ms` or `fixation_frames` every fixation, `word_ms` or
`word_frames` every text event whose trigger is `"condition"` and
`isi_ms` or `isi_frames` every blank. Any other `timing` key is refused.
So is a duration that is not a finite number of at least 0, whether a
`timing` value or an event's own `duration_ms` or `duration_frames`
where it is used.

Other design errors refused here include an unknown event type, a
feedback event with no response or question event before it, `case` on
an event that is not a text event and `length_of` on one that is not a
mask. A response is refused when its `from` is other than `onset` or
`offset`, or when it is collected from the onset of an event that is not
a text event or that runs in other `blocks`.

A fixed duration is emitted as whole milliseconds (`ms`), the unit every
backend consumes: OpenSesame and jsPsych schedule it directly, and the
PsychoPy script converts it back into whole flips against the refresh
rate it measures at start-up. A duration read from the items or jittered
(a `duration:` block) is emitted as `ms_column`, the loop-table column
holding each trial's milliseconds. A response or question event's
`timeout` is in seconds, rounded to three places.

A response collected from the onset of the text event before it (see
`.response_from()`) is rendered with that event, as its `respond` entry
(`keys` and `timeout`). The text keeps its `ms` (or `ms_column`) as its
longest display time, and the window runs from its onset for `ms` plus
the timeout, so the total window is the one the two events had. A
response collected from the offset stays an event of its own. Keys are
rendered as lists, which jsonlite writes as arrays even for one key.

A text event's `case` is carried as it is, for the runners to apply. A
mask's `length_of` is carried too, with the one character to repeat as
its `text`, and the exporters write the mask out for their trials (see
`.sized_masks()`).
