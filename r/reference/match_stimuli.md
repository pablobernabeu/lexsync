# Match stimuli across conditions on several lexical dimensions

The first condition is the anchor; its items are chosen by an even
spread across the sorted candidate subpool. Every other condition is
then matched to the anchor item by item, on the `match_on` dimensions,
using standardised Euclidean distance under a tolerance window derived
from the anchor.

## Usage

``` r
match_stimuli(pool, design, schema, verbose = FALSE)
```

## Arguments

- pool:

  A lexicon/pool with all `match_on` dimensions present (see
  [`add_neighbourhood()`](https://pablobernabeu.github.io/lexsync/r/reference/add_neighbourhood.md)).

- design:

  A parsed design configuration (conditions, `match_on`,
  `n_per_condition`/`n_per_cell`). `match_on` must name at least one
  dimension, and the number of items is a whole number of at least 1, 20
  when neither key is given.

- schema:

  The parsed global schema (tolerances live here).

- verbose:

  Logical; report tolerance relaxations and a shrunk anchor.

## Value

A data frame of selected stimuli with a `condition` label and a `set`
index pairing matched items across conditions.

## Details

Two policies govern degraded selections, each read from the design's
`matching` block with the schema as fallback: `shortfall` (`"error"`,
the default, refuses to return fewer sets than requested; `"allow"`
accepts the shrink) and `on_insufficient_tolerance` (`"relax"`, the
default, widens an undersupplied tolerance window to the full condition
subpool and records the relaxation in an `"audit"` attribute; `"error"`
refuses instead).

A candidate missing any `match_on` dimension cannot be scored, so every
method excludes it before selecting, and the number excluded per
condition is recorded in the `"audit"` attribute's `incomplete_dropped`
entry. The shortfall policy then applies to what remains, and a
condition left with no complete candidate is refused.

`tie_break`, read in the same way, decides between candidates at exactly
the same rounded distance, which integer dimensions make common:
`"hash"`, the default, prefers the smaller SHA-256 of `lexsync-tie-v1|`
followed by the word, which favours no part of the alphabet, and
`"bytes"` prefers the spelling that sorts first and reproduces lexsync
0.1. The rule also orders the tied pairs of `joint` and `optimal` and
the tied rows at their candidate cap. The anchor's even spread keeps its
byte-order tie-break under both rules.
