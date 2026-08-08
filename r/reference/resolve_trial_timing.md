# Realise per-trial event durations onto the stimuli table

An event may declare a duration that varies from trial to trial, either
read from an item column or drawn from a range. A drawn value is a pure
function of the keyed hash, so both engines realise the same
milliseconds, and it is written into the stimuli table rather than only
into the generated script: timing that varies is a variable the analysis
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

`stimuli` with one integer column per jittered event.
