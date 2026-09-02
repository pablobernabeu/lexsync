# Contracts for the shipped configuration files. The bundled copies of
# config/schema.yaml and corpora/registry.yaml must stay byte-identical to the
# repository's own, and the schema must not advertise
# keys that no code reads: a key that parses but is never consulted invites
# users to edit the one setting (the tie-break) that underpins the
# byte-identical R<->Python parity guarantee. Repository-level checks skip
# gracefully when the package is checked in isolation.

bundled_file <- function(name) system.file("extdata", name, package = "lexsync")
bundled_schema <- function() bundled_file("schema.yaml")
EXAMPLE_LEXICA <- c("en_example.csv", "es_example.csv", "zh_example.csv")

expect_same_bytes <- function(a, b) {
  expect_identical(readBin(a, "raw", file.size(a)), readBin(b, "raw", file.size(b)))
}

repo_file <- function(...) {
  path <- testthat::test_path("..", "..", "..", ...)
  testthat::skip_if_not(file.exists(path), "repository configuration not available")
  path
}

test_that("bundled schema is byte-identical to config/schema.yaml", {
  expect_same_bytes(repo_file("config", "schema.yaml"), bundled_schema())
})

# The registry is mirrored into both packages by hand, and README.md tells the
# reader that adding a corpus takes an entry in corpora/registry.yaml and no code
# change. Both mirrors had already fallen a line behind that file, so an
# installed copy of either package documented the registry format less fully than
# a checkout did.
test_that("bundled registry is byte-identical to corpora/registry.yaml", {
  expect_same_bytes(repo_file("corpora", "registry.yaml"), bundled_file("registry.yaml"))
})

# corpora/fetch_corpora.py writes the example slices into both packages at once,
# so a hand-edit or a partial rebuild reaching only one of them would leave the
# two engines demonstrating on different lexica.
test_that("bundled example lexica are byte-identical across the engines", {
  for (name in EXAMPLE_LEXICA) {
    expect_same_bytes(repo_file("python_workflow", "src", "lexsync", "data", name),
                      bundled_file(name))
  }
})

# Every key in the schema must be read by the code; the tie-break order, the
# TOST choice and the trigger reset value are fixed in matching/validation/
# scripting, so they live in comments, not as (inert) configurable keys.
test_that("schema carries no inert keys", {
  schema <- yaml::read_yaml(bundled_schema())
  expect_false("tie_break" %in% names(schema$matching))
  expect_false("test" %in% names(schema$equivalence))
  expect_false("reset_value" %in% names(schema$triggers))
})

# Pins the same contract as
# test_es_gender_repro_frequency_tolerance_is_exactly_one_ninth in the Python
# engine's test_config.py. The truncated 0.111 gave a window 0.1% narrower than
# the criterion the design claims to reproduce.
test_that("the reproduction design encodes the origin study's SD/9 window exactly", {
  design <- yaml::read_yaml(repo_file("config", "design_es_gender_repro.yaml"))
  expect_identical(design$matching$tolerance_k$frequency, 1 / 9)
})

# A datasheet publishes the sha256 of everything the run consumed and produced so a
# recipient can verify the materials, which is worth nothing if the digests do not
# match the files the repository ships. 28 committed datasheets recorded digests of
# CRLF copies of inputs that .gitattributes checks out as LF, so anyone who followed
# the instructions and recomputed one concluded the materials had been altered.
# Twinned in the Python engine's test_config.py.
recorded_digests <- function(ds) {
  pairs <- list(list(ds$materials_source$path, ds$materials_source$sha256),
                list(ds$materials_source$dimensions_from,
                     ds$materials_source$dimensions_sha256),
                list(ds$relational$member_lexicon, ds$relational$member_lexicon_sha256),
                list(ds$items$stimuli_file, ds$items$stimuli_sha256))
  for (table in ds$materials_source$norms) pairs <- c(pairs, list(list(table$path, table$sha256)))
  for (art in ds$artifacts) pairs <- c(pairs, list(list(art$file, art$sha256)))
  Filter(function(p) !is.null(p[[1]]) && !is.null(p[[2]]), pairs)
}

test_that("committed datasheets record digests this checkout reproduces", {
  reports <- repo_file("output", "reports")
  root <- testthat::test_path("..", "..", "..")
  names <- sort(list.files(reports, pattern = "_datasheet_.*\\.json$"))
  skip_if_not(length(names) > 0, "generated reports not available")
  expect_gte(length(names), 40)
  wrong <- character(0)
  checked <- 0L
  for (name in names) {
    ds <- jsonlite::fromJSON(file.path(reports, name), simplifyVector = FALSE)
    for (pair in recorded_digests(ds)) {
      full <- file.path(root, gsub("\\\\", "/", pair[[1]]))
      if (!file.exists(full)) next
      checked <- checked + 1L
      if (!identical(sha256_file(full), pair[[2]])) {
        wrong <- c(wrong, sprintf("%s: %s", name, pair[[1]]))
      }
    }
  }
  expect_gt(checked, length(names))
  # A digest no checkout can reproduce tells a reader verifying the materials that
  # they have been altered.
  expect_identical(sort(unique(wrong)), character(0))
})
