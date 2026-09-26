# Produce several disjoint matched item sets (items as a random factor)

Each replicate is an independent, fully matched set drawn from the pool
with the items of earlier replicates removed, so no item is reused. This
lets a study treat its items as a random factor (running different item
samples across participant groups, or showing an effect holds across
samples) instead of treating them as a fixed set (Clark, 1973; Yarkoni,
2022). Deterministic and identical to the Python engine.

## Usage

``` r
resample_stimuli(pool, design, schema, n_sets, verbose = FALSE)
```

## Arguments

- pool:

  A candidate pool with the `match_on` dimensions present.

- design:

  A parsed design configuration.

- schema:

  The parsed global schema.

- n_sets:

  Number of disjoint matched sets to draw.

- verbose:

  Logical; passed to
  [`match_stimuli()`](https://pablobernabeu.github.io/lexsync/r/reference/match_stimuli.md).

## Value

A data frame of matched stimuli with an added `replicate` column. The
replicates are bound together, which drops the `"audit"` attribute
[`match_stimuli()`](https://pablobernabeu.github.io/lexsync/r/reference/match_stimuli.md)
uses to report a relaxed tolerance window, so a relaxation inside a
replicate reaches the console under `verbose` but not the run log or the
datasheet.
