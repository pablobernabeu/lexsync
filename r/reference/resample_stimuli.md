# Produce several disjoint matched item sets (items as a random factor)

Each replicate is an independent, fully matched set drawn from the pool
with the items of earlier replicates removed, so no item is reused. This
lets a study treat its items as a random factor (running different item
samples across participant groups, or showing an effect holds across
samples) instead of treating them as a fixed set (Clark, 1973; Yarkoni,
2022). Deterministic, and identical to the Python engine under the
`standardised_euclidean` and `joint` methods.

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

  Number of disjoint matched sets to draw, a whole number of at least 1.

- verbose:

  Logical; passed to
  [`match_stimuli()`](https://pablobernabeu.github.io/lexsync/r/reference/match_stimuli.md).

## Value

A data frame of matched stimuli with an added `replicate` column. The
first replicate draws on the whole pool, so its count of the candidates
excluded for a missing matched value is the one recorded in the
`"audit"` attribute's `incomplete_dropped` entry, as
[`match_stimuli()`](https://pablobernabeu.github.io/lexsync/r/reference/match_stimuli.md)
records it. A relaxed tolerance window inside a replicate is not
recorded: it reaches the console under `verbose` but not the run log or
the datasheet.

## References

Clark, H. H. (1973). The language-as-fixed-effect fallacy: A critique of
language statistics in psychological research. *Journal of Verbal
Learning and Verbal Behavior, 12*(4), 335-359.
[doi:10.1016/S0022-5371(73)80014-3](https://doi.org/10.1016/S0022-5371%2873%2980014-3)

Yarkoni, T. (2022). The generalizability crisis. *Behavioral and Brain
Sciences, 45*, Article e1.
[doi:10.1017/S0140525X20001685](https://doi.org/10.1017/S0140525X20001685)
