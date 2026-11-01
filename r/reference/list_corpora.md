# List the corpora known to the registry

List the corpora known to the registry

## Usage

``` r
list_corpora(registry_path = NULL)
```

## Arguments

- registry_path:

  Optional path to `registry.yaml`. A path that does not exist is
  refused. `NULL` (the default) takes the file
  `getOption("lexsync.registry")` names, which must exist. With the
  option unset or empty, it takes the first that exists of
  `corpora/registry.yaml` and `../corpora/registry.yaml` relative to the
  working directory, and last the copy bundled with the package,
  `system.file("extdata", "registry.yaml", package = "lexsync")`.

## Value

A data frame with one row per entry under `corpora` in the registry and
the columns `name`, `language` (the language's name), `iso` (its code),
`status` (`validated`, `supported`, `manual` or `listed`, as the
registry's header defines them), `connector` (`"openlexicon"` when the
entry names none) and `citation`. The wordfreq connector and its
languages have no row, and each entry's licence is in the registry file,
not in the data frame.
