# Run the lexsync pipeline for every design configuration

Run the lexsync pipeline for every design configuration

## Usage

``` r
run_all(
  config_dir = "config",
  schema_path = file.path(config_dir, "schema.yaml"),
  outdir = "output",
  verbose = TRUE
)
```

## Arguments

- config_dir:

  Directory of `design_*.yaml` configurations.

- schema_path:

  Path to the global schema.

- outdir:

  Output directory.

- verbose:

  Logical; print progress.

## Value

A named list of per-design results, invisibly.
