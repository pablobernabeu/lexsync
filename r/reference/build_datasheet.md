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
  neighbourhood_reference = NULL,
  counterbalance_check = NULL,
  input_normalisation = NULL,
  generation_exclude = NULL,
  exclusions = NULL,
  zipf_derivation = NULL,
  trial_order = NULL
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

  Named list of the artifact paths written for the design: `stimuli`,
  `descriptives`, `comparisons` and `experiments`, the result of
  [`export_experiments()`](https://pablobernabeu.github.io/lexsync/r/reference/export_experiments.md).
  Each file is recorded with its sha256: the three tables, then every
  file in `experiments$files`, the loop and text tables included, or the
  three experiment paths of a result that has no `files`.

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
  because those two files decide everything the seed does not. The
  schema's path is recorded too, in POSIX form, since an unnamed schema
  is chosen from several candidates.

- selection_audit:

  Optional matcher audit record; its `window_relaxations` entries are
  recorded because a relaxed window changes what "matched" means for
  that condition. Its `incomplete_dropped` entries
  (`list(condition, n)`) count the candidates excluded for missing a
  matched dimension, which `candidate_pool` still includes. They are
  recorded because the selection drew on a smaller pool than the window
  holds.

- neighbourhood_reference:

  Optional record of a supplied reference the derived dimensions were
  recomputed against (`list(source, n_words, sha256, applied_to)`, where
  `applied_to` lists the recomputed columns), recorded verbatim.

- counterbalance_check:

  Optional report of the pipeline's rotation check on the
  counterbalanced table. Without it, the check is run here on `stimuli`.
  The record gives the recipe that ran and the lists the table holds, or
  for a table without a `list` column the lists
  [`counterbalance()`](https://pablobernabeu.github.io/lexsync/r/reference/counterbalance.md)
  would deal. It says whether a Latin-square rotation is complete and
  counts the trials per list and condition. It also gives the
  presentation versions, one per (replicate, list) pair, and the rule
  that assigns each participant one of them.

- input_normalisation:

  Optional `list(changed, collapsed)`: how many text keys the run's
  inputs held that Unicode NFC normalisation rewrote, and how many
  duplicates the rewriting created and removed. Recorded only when
  given, which the pipeline does only when either count is above zero,
  because a merged spelling changes the candidate pool.

- generation_exclude:

  Optional list of the known-form lists of a generated design's
  `items.generation.exclude`, each `list(source, sha256, n_forms)`. A
  pseudoword was refused for equalling any form in them, so they decide
  which pseudowords a run produces, as the lexicon does.

- exclusions:

  Optional record of a corpus, pool or generated design's
  `exclude_words`, as `list(path, sha256, n_listed, n_removed)`. It
  gives the file, or `"inline"` for a list in the design, its checksum,
  the number of distinct words it lists and the number of candidates it
  removed. Recorded as `materials_source$exclusions`, because the words
  decide which candidates the selection could draw.

- zipf_derivation:

  Optional `list(n_values, near_boundary)` for a lexicon carrying
  `freq_permillion`, as
  [`normalise_lexicon()`](https://pablobernabeu.github.io/lexsync/r/reference/normalise_lexicon.md)
  writes one: how many positive rates it holds, and how many put Zipf =
  log10(per million) + 3 within 1e-9 of a three-place rounding boundary,
  where the two engines' `log10` could round a derived value apart.
  Recorded as `materials_source$zipf_derivation`.

- trial_order:

  Optional record of the trial-order settings on the presented trials,
  which the pipeline passes. Without it, the record is taken from
  `stimuli`. It gives `counterbalancing$max_run`
  (`list(k, run_on, longest)`, the longest run realised in each
  presentation version) when the design limits runs, and
  `counterbalancing$orders` (`list(m, rule)`) when it asks for more than
  one trial order.

## Value

The datasheet as a nested list, ready for
[`write_datasheet()`](https://pablobernabeu.github.io/lexsync/r/reference/write_datasheet.md).

## Details

For a corpus or generated design, `materials_source$provenance` credits
the lexicon that `source_path` names. A lexicon lexsync ships is
credited by its source, a corpus fetched into the cache by the
registry's citation, and any other file by its file name and checksum.

`design$n_per_condition` is the request the selector applied, the
selector's default when the design gives none, and
`items$n_per_condition_realised` counts the items each condition holds
in `stimuli`, per replicate for resampled sets, so a selection that fell
short of the request under `shortfall: allow` shows it. The suggested
analysis keys its by-item slope on the recipe that ran and adds a
matched design's matched dimensions that vary among its items as
covariates.
