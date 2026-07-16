registry_path <- function() system.file("extdata", "registry.yaml", package = "lexsync")

# The vocabulary registry.yaml's header defines and list_corpora() surfaces.
STATUSES <- c("validated", "supported", "manual", "listed")

# A one-entry registry pointing at `url`, so no test touches the network.
temp_registry <- function(url) {
  path <- tempfile(fileext = ".yaml")
  yaml::write_yaml(list(corpora = list(fake = list(
    language = list(name = "Test", iso = "xx"), connector = "openlexicon",
    status = "supported", openlexicon = url, citation = "Test (2026)."
  ))), path)
  path
}

write_head <- function(bytes) {
  path <- tempfile()
  writeBin(bytes, path)
  path
}

BOM <- as.raw(c(0xEF, 0xBB, 0xBF))

# Pins the same contract as test_fetch_corpus_refuses_landing_page_only_entry in
# the Python engine's test_corpora.py: 'url' is the human-facing page and
# 'openlexicon' the delimited file, so falling back to 'url' would cache an HTML
# document as <name>.csv and fail later as a confusing schema error.
test_that("fetch_corpus refuses an entry that registers only a landing page", {
  expect_error(fetch_corpus("subtlex_esp", registry_path = registry_path()),
               "landing page")
})

test_that("fetch_corpus rejects a corpus absent from the registry", {
  expect_error(fetch_corpus("subtlex_klingon", registry_path = registry_path()),
               "not in the registry")
})

# The registry's own header defines 'validated' as a bundled example slice
# demonstrated end to end. Every bundled lexicon is wordfreq-derived, so no
# SUBTLEX entry may claim it; list_corpora() shows 'status' to users.
test_that("registry status reflects what is actually shipped", {
  reg <- yaml::read_yaml(registry_path())
  expect_identical(reg$corpora$subtlex_uk$status, "manual")
  expect_identical(reg$corpora$subtlex_esp$status, "listed")
  expect_false(any(vapply(reg$corpora, function(x) identical(x$status, "validated"), logical(1))))
  expect_false(any(vapply(reg$corpora, function(x) "bundled" %in% names(x), logical(1))))
})

test_that("registry statuses come from the documented vocabulary", {
  reg <- yaml::read_yaml(registry_path())
  for (name in names(reg$corpora)) {
    expect_true(reg$corpora[[name]]$status %in% STATUSES, info = name)
  }
})

# Pins the same contract as
# test_subtlex_uk_advertises_a_landing_page_not_a_dead_download in the Python
# engine's test_corpora.py. SUBTLEX-UK's openlexicon path 404s, and openlexicon
# has never hosted the corpus; van Heuven's own distribution publishes it only as
# zip archives, which the delimited-file connector cannot ingest. The entry must
# therefore send a human to the landing page rather than advertise a dead download.
test_that("subtlex_uk advertises a landing page, not a dead download", {
  reg <- yaml::read_yaml(registry_path())
  entry <- reg$corpora$subtlex_uk
  expect_null(entry$openlexicon)
  expect_match(entry$url, "^https://")
  expect_error(fetch_corpus("subtlex_uk", registry_path = registry_path()),
               "landing page")
})

# 'supported' means fetchable into the user cache, which fetch_corpus() can only
# honour through an 'openlexicon' key; conversely an entry carrying that key
# advertises a download, so it may not claim a status that denies one. Pinning the
# equivalence keeps a rotted URL from being demoted in status alone.
test_that("the openlexicon key and 'supported' status agree", {
  reg <- yaml::read_yaml(registry_path())
  for (name in names(reg$corpora)) {
    entry <- reg$corpora[[name]]
    has_file <- !is.null(entry$openlexicon) && nzchar(entry$openlexicon)
    expect_identical(has_file, identical(entry$status, "supported"), info = name)
  }
})

# Pins the same contract as test_fetch_corpus_refuses_a_non_http_url in the Python
# engine's test_corpora.py. A registry is editable and fetch_corpus() writes
# wherever it points, so 'file://' must not be read under the guise of a download.
test_that("fetch_corpus refuses a non-http(s) URL", {
  for (url in c("file:///etc/passwd", "ftp://example.invalid/x.csv", "corpora/local.csv")) {
    expect_error(fetch_corpus("fake", registry_path = temp_registry(url)),
                 "non-http", info = url)
  }
})

# Pins the same decision table as test_starts_with_markup_decision_table in the
# Python engine's test_corpora.py: identical bytes must give an identical verdict
# in both engines, so a rotted URL is caught on the same byte by each.
test_that("a body opening on a tag is recognised as markup", {
  expect_true(.starts_with_markup(write_head(charToRaw("<!DOCTYPE html>\n<html>404</html>"))))
  expect_true(.starts_with_markup(write_head(charToRaw("\n\r\t <html>"))))
  expect_true(.starts_with_markup(write_head(c(BOM, charToRaw("<html>")))))
})

test_that("a delimited body is not mistaken for markup", {
  expect_false(.starts_with_markup(write_head(charToRaw("word,freq_zipf\ndog,4.5\n"))))
  expect_false(.starts_with_markup(write_head(c(BOM, charToRaw("word,freq_zipf\n")))))
  expect_false(.starts_with_markup(write_head(raw(0))))
  expect_false(.starts_with_markup(write_head(charToRaw("   "))))
})

test_that("list_corpora surfaces the registry status", {
  frame <- list_corpora(registry_path())
  status <- stats::setNames(frame$status, frame$name)
  expect_identical(unname(status[["subtlex_uk"]]), "manual")
  expect_identical(unname(status[["subtlex_esp"]]), "listed")
  expect_false("validated" %in% status)
})
