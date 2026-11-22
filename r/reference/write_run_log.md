# Write the run log to Markdown (and optionally JSON Lines)

Write the run log to Markdown (and optionally JSON Lines)

## Usage

``` r
write_run_log(log, md_path, jsonl_path = NULL)
```

## Arguments

- log:

  A run-log object.

- md_path:

  Output path for the Markdown log.

- jsonl_path:

  Optional output path for the JSON Lines log: one JSON object per step,
  with its `time`, `message` and `data` (`null` for a step without
  details). The run's name, engine, times and metadata are in the
  Markdown log only. Unlike `md_path`'s, its directory is not created.

## Value

`md_path`, invisibly.
