# Run the lexsync pipeline for one design

A design may refer to a derived dimension (`n_density`, `old20`,
`bigram_freq`) in `match_on`, a condition's `define_by`, `pool_filters`,
a continuous predictor or control, or `counterbalance.balance_on`. When
the lexicon lacks it, the pipeline computes it on the pool against the
neighbourhood reference, after the filters the lexicon can answer and
before those on the derived dimension.

## Usage

``` r
run_pipeline(
  design_path,
  schema_path = NULL,
  outdir = NULL,
  reference_words = NULL,
  verbose = TRUE
)
```

## Arguments

- design_path:

  Path to a design configuration (YAML).

- schema_path:

  Path to the global schema (YAML), or `NULL` (the default) to resolve
  it: `config/schema.yaml` in the working directory, then `schema.yaml`
  beside the design, then the copy bundled with the package,
  `system.file("extdata", "schema.yaml", package = "lexsync")`. A
  message names the file chosen. A named schema that does not exist is
  an error. The path used is recorded in the run log and in the
  datasheet's `reproducibility$schema_path`.

- outdir:

  Output directory supplied by the caller (subdirectories `stimuli`,
  `reports`, `experiments` are created). It must be supplied; lexsync
  does not choose a default output location.

- reference_words:

  Optional character vector of words to compute the derived dimensions
  against. By default they are computed against the lexicon, or against
  its rows marked 1 in a `reference_member` column. For a corpus or pool
  design, a supplied list recomputes `n_density` and `old20`, and
  `bigram_freq` when the lexicon carries it or the design refers to it,
  overriding the lexicon's columns. The datasheet then records the
  list's size and checksum and the columns it was applied to. A generate
  or table design does not use it, and the run log says so. A list that
  is empty or holds a missing value is refused. Its words are normalised
  to Unicode NFC before use, like every other text key the pipeline
  reads.

- verbose:

  Logical; print progress.

## Value

A named list of output paths, invisibly.

## Details

A design that refers to `n_syllables` in any of those places is refused
when a word that passes the other filters the lexicon can answer has no
syllable estimate, which is the case for every word outside the Latin
script (see
[`count_syllables()`](https://pablobernabeu.github.io/lexsync/r/reference/count_syllables.md)).

A corpus, pool or generate design may list words to leave out under
`exclude_words`, or name a file of them with
`exclude_words: {path: ...}`. They are removed from the candidates after
any `norms:` join and before the pool filters, and the datasheet records
the list with its checksum. The neighbourhood reference, and the words a
generated pseudoword must not equal, keep them.

The run log notes a design in a language other than English that gives
no `instructions`, since lexsync's own are in English, and a design
whose response keys lexsync's instructions only name, such as a
factorial or priming design. It also notes every practice or filler
answer that the response mapping contradicts. A `response_mapping` that
would leave a trial without an answer is refused before anything is
written.
