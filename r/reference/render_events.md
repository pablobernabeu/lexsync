# Translate paradigm events into backend-neutral rendering dictionaries

Durations are emitted as whole milliseconds (`ms`), the unit every
backend consumes: OpenSesame and jsPsych schedule it directly, and the
PsychoPy script converts it back into whole flips against the refresh
rate it measures at start-up.

## Usage

``` r
render_events(events, timing, hz = 60)
```
