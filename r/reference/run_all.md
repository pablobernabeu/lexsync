# Run the lexsync pipeline for every design configuration

Run the lexsync pipeline for every design configuration

## Usage

``` r
run_all(
  config_dir = "config",
  schema_path = file.path(config_dir, "schema.yaml"),
  outdir = NULL,
  verbose = TRUE
)
```

## Arguments

- config_dir:

  Directory of `design_*.yaml` configurations.

- schema_path:

  Path to the global schema.

- outdir:

  Output directory supplied by the caller. It must be supplied; lexsync
  does not choose a default output location.

- verbose:

  Logical; print progress.

## Value

A named list of per-design results, invisibly.
