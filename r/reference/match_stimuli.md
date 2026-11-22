# Match stimuli across conditions on several lexical dimensions

Under the default method, the first condition is the anchor. Its items
are chosen by an even spread across the sorted candidate subpool. Every
other condition is then matched to the anchor item by item, on the
`match_on` dimensions, using standardised Euclidean distance under a
tolerance window derived from the anchor.

## Usage

``` r
match_stimuli(pool, design, schema, verbose = FALSE)
```

## Arguments

- pool:

  A lexicon or pool with every `match_on` dimension present (see
  [`add_neighbourhood()`](https://pablobernabeu.github.io/lexsync/r/reference/add_neighbourhood.md)).

- design:

  A parsed design configuration (conditions, `match_on` and
  `n_per_condition` or `n_per_cell`). `match_on` must name at least one
  dimension. The number of items must be a whole number of at least 1
  and is 20 when neither key is given.

- schema:

  The parsed global schema, which holds the tolerances.

- verbose:

  Whether to report tolerance relaxations and an anchor set smaller than
  requested.

## Value

A data frame of selected stimuli with a `condition` label and a `set`
index pairing matched items across conditions.

## Details

`method`, read from the design's `matching` block with the schema as
fallback, chooses the matcher. `"standardised_euclidean"` (the default)
is the anchored procedure above. `"mahalanobis"` is the same procedure
with distances weighted by the inverse of the pool's correlation matrix,
which, with two or more matched dimensions, needs at least k + 2 pool
rows complete on the k dimensions. `"joint"` and `"optimal"` need
exactly two conditions. They drop the anchor and pair the two
conditions' candidates directly: `joint` takes the cheapest disjoint
pairs first, and `optimal` takes the `n` pairs of least summed distance
(exactly so for disjoint conditions) and needs the 'clue' package.
Neither consults `tolerance_k` or `on_insufficient_tolerance`, and each
first keeps at most 1,200 candidates per condition, those nearest the
other condition's centroid. The Python package selects the same stimuli
under `standardised_euclidean` and `joint`. Under `mahalanobis` and
`optimal`, the two agree closely but not byte for byte, and `optimal`
may return a different set of pairs with the same summed distance.

Two policies, each read from the design's `matching` block with the
schema as fallback, govern a selection that cannot be made in full.
Under `shortfall`, `"error"`, the default, refuses to return fewer sets
than requested, and `"allow"` accepts fewer. Under
`on_insufficient_tolerance`, `"relax"`, the default, widens an
undersupplied tolerance window to the full condition subpool and records
the relaxation in an `"audit"` attribute, and `"error"` refuses instead.

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
