# Select a set spread over a continuous predictor, with windows on the controls

Instead of dichotomising the predictor into conditions and matching,
items are spread evenly over the predictor's ranks in the pool, so the
selection follows the pool's distribution of the predictor and does not
cover its range evenly. The control dimensions are held within a
tolerance band, which trims their tails without holding them constant,
so read each control's correlation with the predictor in
[`match_report_continuous()`](https://pablobernabeu.github.io/lexsync/r/reference/match_report_continuous.md)
before relying on it. Tightening `tolerance_k` does not reliably lower
those correlations. The set is analysed by regression / mixed models
rather than between-condition contrasts (Kuperman, 2015; Liben-Nowell et
al., 2019). Two deterministic even-spread passes make the R and Python
engines select byte-identical stimuli. Mirrors select_continuous_stimuli
in matching.py.

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

A data frame of the selected stimuli. Unless `label` is `NULL` the
`condition` column is set to it, `"continuous"` by default, and unless
`renumber_sets` is `FALSE` the `set` column is renumbered `1..n`.

## Details

The design is checked before anything is selected, so a design that
cannot be honoured is refused outright. `continuous.controls` must be
non-empty and must not name the predictor, `match_on` must name exactly
the same dimensions as `continuous.controls`, every dimension named and
the `key` column must be present in the pool, no `tolerance_k` may be
negative, and the pool must not be empty.

A row missing the predictor or a control is excluded before the first
pass, and the number excluded is recorded in the `"audit"` attribute's
`incomplete_dropped` entry under the condition `continuous`. A pool with
no complete row is refused.

The `"audit"` attribute's `control_windows` entry records, for each
control, the window the first pass set (`low`, `high`) and the SD of the
complete pool (`pool_sd`), which
[`match_report_continuous()`](https://pablobernabeu.github.io/lexsync/r/reference/match_report_continuous.md)
sets the realised SD against. A relaxed window is recorded as computed,
and the relaxation in `window_relaxations`.
