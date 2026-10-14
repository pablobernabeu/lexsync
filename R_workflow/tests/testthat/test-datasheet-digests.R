# The committed datasheets publish the SHA-256 of every file a run read and wrote,
# so that a reader can confirm the materials are the ones described. That is worth
# something only if a fresh checkout reproduces each digest. 28 of the 42 committed
# datasheets once recorded the digest of corpora/derived/en.csv or es.csv as one
# machine had converted them to CRLF, and two recorded a CRLF copy of
# config/design_en_priming_continuous.yaml. Git stores and .gitattributes checks
# out all three with LF, so recomputing the digest told the reader the lexicon
# had been altered. The tests recompute every digest from the bytes in this
# checkout, hashed here with digest so that a fault in the package's own
# sha256_file() cannot hide one. Twinned in test_datasheet_digests.py.

digest_reports <- function() {
  reports <- repo_path("output", "reports", message = "committed reports not available")
  names <- sort(list.files(reports, pattern = "_datasheet_.*\\.json$"))
  skip_if(length(names) == 0, "committed reports not available")
  # 22 shipped designs, one datasheet per engine. A sweep that finds far fewer has
  # lost its inputs, and passing it would prove nothing.
  expect_gte(length(names), 40)
  stats::setNames(file.path(reports, names), names)
}

read_datasheet <- function(path) jsonlite::fromJSON(path, simplifyVector = FALSE)

checkout_sha256 <- function(...) digest::digest(file = repo_path(...), algo = "sha256")

# Every (path, sha256) pair a datasheet records, with the path relative to the
# repository root.
recorded_digests <- function(ds) {
  ms <- ds$materials_source
  pairs <- list(list(ms$path, ms$sha256),
                list(ms$dimensions_from, ms$dimensions_sha256),
                list(ds$relational$member_lexicon, ds$relational$member_lexicon_sha256),
                list(ds$items$stimuli_file, ds$items$stimuli_sha256))
  for (table in ms$norms) pairs <- c(pairs, list(list(table$path, table$sha256)))
  # An exclusion list written in the design has no file, and its digest is the list's.
  excluded <- ms$exclusions
  if (!is.null(excluded) && !identical(excluded$path, "inline")) {
    pairs <- c(pairs, list(list(excluded$path, excluded$sha256)))
  }
  for (art in ds$artifacts) pairs <- c(pairs, list(list(art$file, art$sha256)))
  Filter(function(p) !is.null(p[[1]]) && !is.null(p[[2]]), pairs)
}

test_that("committed datasheets record digests this checkout reproduces", {
  sheets <- digest_reports()
  wrong <- character(0)
  checked <- 0L
  for (name in names(sheets)) {
    for (pair in recorded_digests(read_datasheet(sheets[[name]]))) {
      path <- gsub("\\\\", "/", pair[[1]])
      full <- repo_path(path)
      checked <- checked + 1L
      if (!file.exists(full)) {
        wrong <- c(wrong, sprintf("%s: %s (no such file in the checkout)", name, path))
      } else if (!identical(checkout_sha256(path), pair[[2]])) {
        wrong <- c(wrong, sprintf("%s: %s", name, path))
      }
    }
  }
  # Each datasheet names at least its lexicon and its stimuli file.
  expect_gte(checked, 2L * length(sheets))
  expect_identical(wrong, character(0))
})

# The design and schema digests carry no path. The pipeline reads the design from
# config/design_<name>.yaml and the schema from config/schema.yaml.
test_that("committed datasheets record the digests of the shipped design and schema", {
  sheets <- digest_reports()
  schema <- checkout_sha256("config", "schema.yaml")
  wrong <- character(0)
  for (name in names(sheets)) {
    ds <- read_datasheet(sheets[[name]])
    design <- file.path("config", paste0("design_", ds$design$name, ".yaml"))
    if (!file.exists(repo_path(design))) {
      wrong <- c(wrong, sprintf("%s: %s (no such file in the checkout)", name, design))
    } else if (!identical(ds$reproducibility$design_sha256, checkout_sha256(design))) {
      wrong <- c(wrong, sprintf("%s: %s", name, design))
    }
    if (!identical(ds$reproducibility$schema_sha256, schema)) {
      wrong <- c(wrong, sprintf("%s: config/schema.yaml", name))
    }
  }
  expect_identical(wrong, character(0))
})
