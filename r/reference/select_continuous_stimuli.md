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

  A parsed design configuration carrying a `continuous` block
  (`predictor` and `controls`). The number of items is
  `n_per_condition`, else `n_per_cell`, and either must be a whole
  number of at least 1. It is 60 when neither key is given.
  `tolerance_k`, `shortfall` and `on_insufficient_tolerance` are read
  from its `matching` block with the schema as fallback, as for
  [`match_stimuli()`](https://pablobernabeu.github.io/lexsync/r/reference/match_stimuli.md),
  and a relaxed window widens to the whole complete pool.

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

## References

Kuperman, V. (2015). Virtual experiments in megastudies: A case study of
language and emotion. *Quarterly Journal of Experimental Psychology,
68*(8), 1693-1710.
[doi:10.1080/17470218.2014.989865](https://doi.org/10.1080/17470218.2014.989865)

Liben-Nowell, D., Strand, J., Sharp, A., Wexler, T., & Woods, K. (2019).
The danger of testing by selecting controlled subsets, with applications
to spoken-word recognition. *Journal of Cognition, 2*(1), Article 2.
[doi:10.5334/joc.51](https://doi.org/10.5334/joc.51)
