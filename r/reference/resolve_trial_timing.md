# Realise per-trial event durations onto the stimuli table

An event may declare a duration that varies from trial to trial, either
read from an item column or drawn from a range. A drawn value is a pure
function of the keyed hash, so both engines realise the same
milliseconds, and it is written into the stimuli table as well as the
generated script, because timing that varies is a variable the analysis
needs, not presentation detail.

## Usage

``` r
resolve_trial_timing(stimuli, design, schema)
```

## Arguments

- stimuli:

  A counterbalanced stimuli data frame.

- design:

  A parsed design configuration.

- schema:

  The parsed global schema (provides the seed).

## Value

`stimuli` with one integer column per jittered event, and every column
of fractional milliseconds rounded. Each column rounded is recorded in
the `"duration_rounding"` attribute, as one
`list(event, column, n_rounded)` entry, which
[`run_pipeline()`](https://pablobernabeu.github.io/lexsync/r/reference/run_pipeline.md)
writes into the run log.

## Details

Every value read from a column must be a finite number of milliseconds,
not negative. The first that is not, a blank cell included, is refused,
naming the column and the trial's set and condition. A blank or negative
value used to reach the experiments, where OpenSesame and PsychoPy
stopped at the blank and jsPsych ended the trial at once. When a column
holds fractional milliseconds, each of its values is rounded once with
the rounder both engines share and written back, so the stimuli, the
loop tables and every target carry the same whole milliseconds. A column
of whole numbers is left as it is.
