registry_path <- function() system.file("extdata", "registry.yaml", package = "lexsync")

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
  expect_identical(reg$corpora$subtlex_uk$status, "supported")
  expect_identical(reg$corpora$subtlex_esp$status, "listed")
  expect_false(any(vapply(reg$corpora, function(x) identical(x$status, "validated"), logical(1))))
  expect_false(any(vapply(reg$corpora, function(x) "bundled" %in% names(x), logical(1))))
})

# 'supported' means fetchable into the user cache, which fetch_corpus() can only
# honour through an 'openlexicon' key.
test_that("supported corpora expose a downloadable file", {
  reg <- yaml::read_yaml(registry_path())
  for (name in names(reg$corpora)) {
    entry <- reg$corpora[[name]]
    if (identical(entry$status, "supported")) {
      expect_true(!is.null(entry$openlexicon) && nzchar(entry$openlexicon),
                  info = sprintf("%s is 'supported' but has no openlexicon file", name))
    }
  }
})

test_that("list_corpora surfaces the registry status", {
  frame <- list_corpora(registry_path())
  status <- stats::setNames(frame$status, frame$name)
  expect_identical(unname(status[["subtlex_uk"]]), "supported")
  expect_identical(unname(status[["subtlex_esp"]]), "listed")
  expect_false("validated" %in% status)
})
