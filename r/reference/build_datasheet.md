# Assemble the materials datasheet for one design

Assemble the materials datasheet for one design

## Usage

``` r
build_datasheet(
  design,
  schema,
  report,
  stimuli,
  source_path,
  artifacts,
  seed,
  engine = "R",
  candidate_pool = NULL,
  norms = NULL,
  balance = NULL,
  blocks = NULL,
  design_path = NULL,
  schema_path = NULL,
  selection_audit = NULL,
  neighbourhood_reference = NULL
)
```

## Arguments

- design:

  A parsed design list.

- schema:

  The parsed global schema (`schema.yaml`).

- report:

  Match report data frame, from
  [`match_report()`](https://pablobernabeu.github.io/lexsync/r/reference/match_report.md)
  or
  [`match_report_continuous()`](https://pablobernabeu.github.io/lexsync/r/reference/match_report_continuous.md),
  or `NULL` for generated or tabled items.

- stimuli:

  The selected stimulus data frame.

- source_path:

  Path of the lexicon or item table the stimuli came from.

- artifacts:

  Named list of the artifact paths written for the design (stimuli,
  descriptives, comparisons, experiments).

- seed:

  The integer seed recorded for the counterbalanced trial order.

- engine:

  Engine label recorded in the record (default `"R"`).

- candidate_pool:

  Optional list of per-condition candidate-pool sizes
  (`list(condition, n_candidates)`) recording how many items satisfied
  each condition's window before matching; reported for selection
  transparency.

- norms:

  Optional list of norm-table provenance records, from the design's
  `norms:` block (see the pipeline). Each names a file, its sha256, the
  join key and the per-column coverage. Recorded because a norm table
  can supply the very variable a design manipulates, so a record that
  omitted it would describe a selection over columns of unstated origin.

- balance:

  Optional balance-optimiser report, from
  [`balance_lists()`](https://pablobernabeu.github.io/lexsync/r/reference/balance_lists.md).
  Recorded because it decides which items each participant sees.

- blocks:

  Optional practice/filler block report. Recorded because those trials
  are presented but not analysed, so the presented and analysed counts
  differ and the record must say why.

- design_path, schema_path:

  Optional paths of the design and schema files the run read; when
  given, their sha256 checksums complete the reproducibility record,
  because those two files decide everything the seed does not.

- selection_audit:

  Optional matcher audit record; its `window_relaxations` entries are
  recorded because a relaxed window changes what "matched" means for
  that condition.

- neighbourhood_reference:

  Optional record of the lexicon the neighbourhood dimensions were
  computed against (`list(source, n_words, sha256)`), recorded verbatim.

## Value

The datasheet as a nested list, ready for
[`write_datasheet()`](https://pablobernabeu.github.io/lexsync/r/reference/write_datasheet.md).
