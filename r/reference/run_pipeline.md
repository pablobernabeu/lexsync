# Run the lexsync pipeline for one design

Run the lexsync pipeline for one design

## Usage

``` r
run_pipeline(
  design_path,
  schema_path = "config/schema.yaml",
  outdir = "output",
  reference_words = NULL,
  verbose = TRUE
)
```

## Arguments

- design_path:

  Path to a design configuration (YAML).

- schema_path:

  Path to the global schema (YAML).

- outdir:

  Output directory (subdirectories `stimuli`, `reports`, `experiments`
  are created).

- reference_words:

  Optional reference word list for neighbourhood computation; defaults
  to the whole lexicon.

- verbose:

  Logical; print progress.

## Value

A named list of output paths, invisibly.
