# Select a set spanning a continuous predictor, holding controls constant

Instead of dichotomising the predictor into conditions and matching,
items are chosen to cover the predictor's range evenly while the control
dimensions are held within a tolerance band, so they stay near-constant
and near-uncorrelated with the predictor. The set is analysed by
regression / mixed models rather than between-condition contrasts
(Kuperman, 2015; Liben-Nowell et al., 2019). Two deterministic
even-spread passes make the R and Python engines select byte-identical
stimuli. Mirrors select_continuous_stimuli in matching.py.

## Usage

``` r
select_continuous_stimuli(
  pool,
  design,
  schema,
  verbose = FALSE,
  key = "word",
  label = "continuous",
  renumber_sets = TRUE
)
```

## Arguments

- pool:

  A candidate pool with the predictor and control dimensions present.

- design:

  A parsed design configuration carrying a `continuous` block.

- schema:

  The parsed global schema (tolerance windows).

- verbose:

  Logical; report a window relaxation.

- key:

  Column used as the selection unit and the byte-order tie-break, by
  default `"word"`. The pair-keyed path passes `"set"`: after a pair
  table is collapsed to one row per item set there is no `word` column,
  and `set` is unique per row, integer, and already derived
  deterministically.

- label:

  Value written into the result's `condition` column, or `NULL` to leave
  the existing conditions alone. The pair path passes `NULL`, because
  its rows already carry the design's own conditions and overwriting
  them would destroy the contrast the design exists to test.

- renumber_sets:

  Logical; renumber the selected rows `1..n`. The pair path passes
  `FALSE`, because its `set` ids have to survive selection for the
  result to be re-expanded back to the full pair table.

## Value

A data frame of selected stimuli (condition "continuous", set 1..n).
