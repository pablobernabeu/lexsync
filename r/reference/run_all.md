# Run the lexsync pipeline for every design configuration

Run the lexsync pipeline for every design configuration

## Usage

``` r
run_all(
  config_dir = "config",
  schema_path = NULL,
  outdir = NULL,
  verbose = TRUE
)
```

## Arguments

- config_dir:

  Directory of `design_*.yaml` configurations.

- schema_path:

  Path to the global schema, or `NULL` (the default) to resolve it:
  `schema.yaml` in `config_dir`, then `config/schema.yaml` in the
  working directory, then the copy bundled with the package,
  `system.file("extdata", "schema.yaml", package = "lexsync")`. A
  message names the file chosen. A named schema that does not exist is
  an error, raised before any design runs.

- outdir:

  Output directory supplied by the caller. It must be supplied; lexsync
  does not choose a default output location.

- verbose:

  Logical; print progress.

## Value

A named list of per-design results, invisibly.
