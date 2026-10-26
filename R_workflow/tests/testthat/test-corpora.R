registry_path <- function() system.file("extdata", "registry.yaml", package = "lexsync")

# The vocabulary registry.yaml's header defines and list_corpora() surfaces.
STATUSES <- c("validated", "supported", "manual", "listed")

# A one-entry registry pointing at `url`, so no test touches the network.
temp_registry <- function(url, sha256 = NULL) {
  path <- tempfile(fileext = ".yaml")
  entry <- list(
    language = list(name = "Test", iso = "xx"), connector = "openlexicon",
    status = "supported", openlexicon = url, citation = "Test (2026)."
  )
  if (!is.null(sha256)) entry$sha256 <- sha256
  yaml::write_yaml(list(corpora = list(fake = entry)), path)
  path
}

# Serves `bytes` in place of the network, through the download.file import seam.
mock_download <- function(bytes) {
  function(url, destfile, ...) {
    writeBin(bytes, destfile)
    0L
  }
}

# A directory the test owns outright, so leftovers are provable by listing it.
temp_cache <- function() {
  dir <- tempfile()
  dir.create(dir)
  dir
}

# Runs `code` with tools::R_user_dir() pointed at a fresh temporary root, so the
# default-destination path can be exercised without touching the real cache.
# withr is not among the suggested packages, so the restore is written out.
with_user_cache <- function(code) {
  old <- Sys.getenv("R_USER_CACHE_DIR", unset = NA)
  on.exit(if (is.na(old)) Sys.unsetenv("R_USER_CACHE_DIR") else
            Sys.setenv(R_USER_CACHE_DIR = old))
  Sys.setenv(R_USER_CACHE_DIR = tempfile("lexsync-cache-"))
  force(code)
}

# Fills the (temporary) cache with empty files of the given names.
seed_cache <- function(files) {
  dir.create(lexsync_cache_dir(), recursive = TRUE, showWarnings = FALSE)
  file.create(file.path(lexsync_cache_dir(), files))
  invisible(lexsync_cache_dir())
}

# Backdates cache files by two days, past the day after which the sweep treats a
# sidecar as abandoned.
age_files <- function(files) {
  Sys.setFileTime(file.path(lexsync_cache_dir(), files), Sys.time() - 2 * 24 * 60 * 60)
}

CSV_BODY <- charToRaw("word,freq_zipf\ndog,4.5\n")

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

# Pins the same contract as test_fetch_corpus_refuses_a_name_that_is_a_path in the
# Python engine's test_corpora.py. The name becomes the cached file's name, so an
# edited registry with an entry named '../../../escaped' made fetch_corpus() write
# three levels above the cache, where lexsync_cache_clear() then refused to look. The
# rule is lexsync_cache_clear()'s, applied before the registry is read and whether or
# not a `dest` is given.
test_that("fetch_corpus refuses a name that is a path", {
  dir <- temp_cache()
  entry <- list(language = list(name = "Test", iso = "xx"), status = "supported",
                openlexicon = "https://example.invalid/escaped.csv", citation = "Test (2026).")
  reg <- file.path(dir, "registry.yaml")
  yaml::write_yaml(list(corpora = list(`../../../escaped` = entry, `a/b` = entry)), reg)
  local_mocked_bindings(download.file = mock_download(CSV_BODY))
  with_user_cache({
    for (bad in list("../../../escaped", "..\\escaped", "a/b", "C:escaped", "",
                     NA_character_, c("a", "b"), 1)) {
      expect_error(fetch_corpus(bad, registry_path = reg),
                   "'name' must be a single corpus name, not a path", fixed = TRUE,
                   info = deparse(bad))
      expect_error(fetch_corpus(bad, registry_path = reg, dest = file.path(dir, "x.csv")),
                   "not a path", info = deparse(bad))
    }
    expect_false(dir.exists(lexsync_cache_dir()))
  })
  expect_identical(list.files(dir), "registry.yaml")
})

# Pins the same contract as test_fetch_corpus_refusals_name_the_registry_they_read in
# the Python engine's test_corpora.py. The refusals cited corpora/registry.yaml, a path
# that an installed package does not have, and called an entry with no URL at all a
# landing page.
test_that("fetch_corpus refusals name the registry they read", {
  shipped <- registry_path()
  expect_error(fetch_corpus("subtlex_uk", registry_path = shipped),
               sprintf("registers only a landing page .* in '%s'", shipped))
  expect_error(fetch_corpus("subtlex_klingon", registry_path = shipped),
               sprintf("not in the registry '%s'", shipped), fixed = TRUE)
  # subtlex_nl registers neither a landing page nor a file.
  expect_error(fetch_corpus("subtlex_nl", registry_path = shipped),
               sprintf("registers no download URL in '%s'", shipped), fixed = TRUE)
  path <- temp_registry("file:///etc/passwd")
  expect_error(fetch_corpus("fake", registry_path = path),
               sprintf("in '%s'; refusing to download", path), fixed = TRUE)
})

# This test has no Python twin, because that engine builds the lexicon. R's refusal
# said the language was "not in the registry", which lists it.
test_that("fetch_corpus explains that a wordfreq language is built by the Python package", {
  with_user_cache({
    expect_error(
      fetch_corpus("fr", registry_path = registry_path()),
      paste0("lexsync: 'fr' is a wordfreq language; its lexicon is built by the Python ",
             "package (`lexsync fetch fr`), and the R package reads the result with ",
             "load_lexicon()."),
      fixed = TRUE)
    expect_false(dir.exists(lexsync_cache_dir()))
  })
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
# honour through an 'openlexicon' key or a 'derived' file; conversely an entry
# carrying either advertises a download, so it may not claim a status that denies
# one. Pinning the equivalence keeps a rotted URL from being demoted in status alone.
download_url <- function(entry) entry[["derived"]][["url"]] %||% entry[["openlexicon"]]

test_that("the openlexicon key and 'supported' status agree", {
  reg <- yaml::read_yaml(registry_path())
  for (name in names(reg$corpora)) {
    url <- download_url(reg$corpora[[name]])
    has_file <- !is.null(url) && nzchar(url)
    expect_identical(has_file, identical(reg$corpora[[name]]$status, "supported"), info = name)
  }
})

registry_copies <- function() {
  paths <- registry_path()
  root <- repo_root()
  if (!is.null(root)) {
    paths <- c(paths, file.path(root, "corpora", "registry.yaml"),
               file.path(root, "python_workflow", "src", "lexsync", "data", "registry.yaml"))
  }
  paths
}

# Pins the same contract as test_every_supported_entry_has_a_download_url_and_a_sha256
# in the Python engine's test_corpora.py. A download is cached only once it matches
# the registry's digest, and an entry without one would cache whatever the server sent.
test_that("every supported entry has a download URL and a SHA-256", {
  supported <- character(0)
  for (path in registry_copies()) {
    entries <- yaml::read_yaml(path)$corpora
    for (name in names(entries)) {
      entry <- entries[[name]]
      if (!identical(entry$status, "supported")) next
      supported <- c(supported, name)
      sha <- if (is.null(entry$derived)) entry$sha256 else entry$derived$sha256
      expect_match(download_url(entry), "^https://", info = paste(path, name))
      expect_match(sha %||% "", "^[0-9a-f]{64}$", info = paste(path, name))
    }
  }
  expect_true("subtlex_us" %in% supported)
})

# Pins the same contract as test_registry_column_maps_are_not_log_counts in the
# Python engine's test_corpora.py. SUBTLEX-US's Lg10WF and SUBTLEX-DE's lgSUBTLEX
# are log10 word counts, which read about 1.3 and 1.6 below Zipf, and SUBTLEX-CH
# publishes no WCpmw column. A user who renamed columns as the registry said would
# filter and match on the wrong scale. Every copy of the registry that is around
# is read: all three in a checkout, the bundled one otherwise.
test_that("registry column maps are not log counts", {
  paths <- registry_path()
  root <- repo_root()
  if (!is.null(root)) {
    paths <- c(paths, file.path(root, "corpora", "registry.yaml"),
               file.path(root, "python_workflow", "src", "lexsync", "data", "registry.yaml"))
  }
  for (path in paths) {
    entries <- yaml::read_yaml(path)$corpora
    for (name in names(entries)) {
      zipf <- entries[[name]]$columns$freq_zipf
      expect_false(!is.null(zipf) && zipf %in% c("Lg10WF", "lgSUBTLEX", "WCpmw"),
                   info = paste(path, name))
    }
    expect_identical(entries$subtlex_us$columns$freq_permillion, "SUBTLWF", info = path)
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

# A URL answering 200 with an HTML page (a login wall, or a 404 page served with
# the wrong status) must not be cached as <name>.csv, where it would resurface as
# an unintelligible schema error. Pins the same contract as
# test_fetch_corpus_rejects_an_html_body_and_caches_nothing in the Python
# engine's test_corpora.py: the sniff now runs on the sidecar, so not even a
# '.part' file may remain.
test_that("an HTML body is refused and leaves nothing behind", {
  dir <- temp_cache()
  local_mocked_bindings(
    download.file = mock_download(charToRaw("<!DOCTYPE html>\n<html><body>Not Found</body></html>\n"))
  )
  expect_error(
    fetch_corpus("fake", registry_path = temp_registry("https://example.invalid/rotted.csv"),
                 dest = file.path(dir, "fake.csv")),
    "HTML page, not a delimited file"
  )
  expect_identical(list.files(dir), character(0))
})

# Pins the same contract as test_fetch_corpus_removes_the_sidecar_when_the_transfer_dies
# in the Python engine's test_corpora.py: the pre-sidecar implementation cached
# exactly such truncated bodies, to resurface later as schema errors.
test_that("a transfer that dies mid-stream leaves nothing behind", {
  dir <- temp_cache()
  local_mocked_bindings(download.file = function(url, destfile, ...) {
    writeBin(charToRaw("word,freq_zipf\ndog,4"), destfile)
    warning("connection reset")
  })
  expect_error(
    fetch_corpus("fake", registry_path = temp_registry("https://example.invalid/flaky.csv"),
                 dest = file.path(dir, "fake.csv")),
    "could not download corpus 'fake'"
  )
  expect_identical(list.files(dir), character(0))
})

# Pins the same contract as test_fetch_corpus_promotes_a_verified_download in the
# Python engine's test_corpora.py: the transfer lands in '<dest>.part' and is
# renamed into place only after every check has passed.
test_that("fetch_corpus promotes a verified download and removes the sidecar", {
  dir <- temp_cache()
  dest <- file.path(dir, "fake.csv")
  local_mocked_bindings(download.file = mock_download(CSV_BODY))
  expect_message(
    out <- fetch_corpus("fake", registry_path = temp_registry("https://example.invalid/good.csv"),
                        dest = dest),
    "downloaded 'fake'"
  )
  expect_identical(out, dest)
  expect_identical(list.files(dir), "fake.csv")
  expect_identical(readBin(dest, "raw", n = file.size(dest)), CSV_BODY)
})

# Pins the same contract as test_fetch_corpus_aborts_an_oversized_download in the
# Python engine's test_corpora.py. The cap is lowered through its seam because a
# genuine 200 MB fixture has no place in a test suite; the message names the real
# limit regardless.
test_that("an oversized download is aborted and leaves nothing behind", {
  dir <- temp_cache()
  local_mocked_bindings(
    download.file = mock_download(charToRaw(strrep("x", 64))),
    .max_download_bytes = function() 16
  )
  expect_error(
    fetch_corpus("fake", registry_path = temp_registry("https://example.invalid/big.csv"),
                 dest = file.path(dir, "fake.csv")),
    "exceeded the 200 MB size limit"
  )
  expect_identical(list.files(dir), character(0))
})

# Pins the same contract as test_fetch_corpus_refuses_a_checksum_mismatch in the
# Python engine's test_corpora.py. The field is optional in the code, so the contract
# is exercised through a temporary registry.
test_that("a checksum mismatch is refused and leaves nothing behind", {
  dir <- temp_cache()
  local_mocked_bindings(download.file = mock_download(CSV_BODY))
  expect_error(
    fetch_corpus("fake",
                 registry_path = temp_registry("https://example.invalid/good.csv",
                                               sha256 = strrep("0", 64)),
                 dest = file.path(dir, "fake.csv")),
    "checksum mismatch for corpus 'fake'"
  )
  expect_identical(list.files(dir), character(0))
})

# Pins the same contract as test_fetch_corpus_accepts_a_matching_checksum in the
# Python engine's test_corpora.py: both engines must derive the same digest from
# the same bytes.
test_that("a matching checksum is accepted", {
  dir <- temp_cache()
  dest <- file.path(dir, "fake.csv")
  local_mocked_bindings(download.file = mock_download(CSV_BODY))
  sha <- digest::digest(CSV_BODY, algo = "sha256", serialize = FALSE)
  expect_message(
    fetch_corpus("fake",
                 registry_path = temp_registry("https://example.invalid/good.csv", sha256 = sha),
                 dest = dest),
    "downloaded 'fake'"
  )
  expect_identical(list.files(dir), "fake.csv")
})

# Pins the same contract as test_a_mocked_fetch_of_subtlex_us_normalises_into_the_cache
# in the Python engine's test_corpora.py. The shipped entry names openlexicon's TSV and
# its SHA-256, which a fixture cannot match, so the fixture is first refused against the
# shipped entry and then served to a copy of the entry that carries its own digest.
test_that("a mocked fetch of subtlex_us normalises into the cache", {
  body <- charToRaw(enc2utf8(SUBTLEX_US))
  entry <- yaml::read_yaml(registry_path())$corpora$subtlex_us
  seen <- character(0)
  local_mocked_bindings(download.file = function(url, destfile, ...) {
    seen <<- c(seen, url)
    writeBin(body, destfile)
    0L
  })
  with_user_cache({
    expect_error(fetch_corpus("subtlex_us", registry_path = registry_path()),
                 "checksum mismatch for corpus 'subtlex_us'")
    expect_identical(seen, entry$openlexicon)
    expect_identical(list.files(lexsync_cache_dir()), character(0))
    entry$sha256 <- digest::digest(body, algo = "sha256", serialize = FALSE)
    reg <- tempfile(fileext = ".yaml")
    yaml::write_yaml(list(corpora = list(subtlex_us = entry)), reg)
    msgs <- character(0)
    dest <- withCallingHandlers(
      fetch_corpus("subtlex_us", registry_path = reg),
      message = function(m) {
        msgs <<- c(msgs, conditionMessage(m))
        invokeRestart("muffleMessage")
      })
    expect_identical(dest, file.path(lexsync_cache_dir(), "subtlex_us.csv"))
    expect_identical(list.files(lexsync_cache_dir()), "subtlex_us.csv")
    expect_identical(read_corpus_file(dest), SUBTLEX_US_LEXICON)
    expect_true(any(grepl("normalised 5 forms from 'SUBTLEXus74286wordstextversion.tsv'",
                          msgs, fixed = TRUE)))
    expect_true(any(grepl("downloaded 'subtlex_us'. Please cite: Brysbaert & New (2009)",
                          msgs, fixed = TRUE)))
  })
})

# Pins the same contract as
# test_a_download_that_cannot_be_normalised_leaves_nothing_behind in the Python
# engine's test_corpora.py: the normalisation is one more check the sidecar must pass
# before it may enter the cache.
test_that("a download that cannot be normalised leaves nothing behind", {
  entry <- list(language = list(name = "Test", iso = "xx"), status = "supported",
                openlexicon = "https://example.invalid/raw.tsv",
                columns = list(word = "Word", freq_permillion = "SUBTLWF"),
                citation = "Test (2026).")
  reg <- tempfile(fileext = ".yaml")
  yaml::write_yaml(list(corpora = list(fake = entry)), reg)
  local_mocked_bindings(download.file = mock_download(charToRaw("Word\tFREQcount\ndog\t9831\n")))
  with_user_cache({
    expect_error(fetch_corpus("fake", registry_path = reg), "has no column 'SUBTLWF'",
                 fixed = TRUE)
    expect_identical(list.files(lexsync_cache_dir()), character(0))
  })
})

# Pins the same contract as
# test_a_derived_file_is_fetched_in_place_of_the_openlexicon_file in the Python
# engine's test_corpora.py. A 'derived' file is a lexicon already normalised, which
# both engines then read byte for byte, so it is preferred and cached as it arrives.
test_that("a derived file is fetched in place of the openlexicon file", {
  body <- charToRaw("word,freq_zipf,freq_permillion\ncat,4.848,70.41\n")
  entry <- list(language = list(name = "Test", iso = "xx"), status = "supported",
                openlexicon = "https://example.invalid/raw.tsv",
                derived = list(url = "https://example.invalid/derived.csv",
                               sha256 = digest::digest(body, algo = "sha256",
                                                       serialize = FALSE)),
                columns = list(word = "Word", freq_permillion = "SUBTLWF"),
                citation = "Test (2026).")
  reg <- tempfile(fileext = ".yaml")
  yaml::write_yaml(list(corpora = list(fake = entry)), reg)
  seen <- character(0)
  local_mocked_bindings(download.file = function(url, destfile, ...) {
    seen <<- c(seen, url)
    writeBin(body, destfile)
    0L
  })
  with_user_cache({
    dest <- suppressMessages(fetch_corpus("fake", registry_path = reg))
    expect_identical(seen, "https://example.invalid/derived.csv")
    expect_identical(list.files(lexsync_cache_dir()), "fake.csv")
    expect_identical(readBin(dest, "raw", n = file.size(dest)), body)
  })
})

# Pins the same contract as test_cache_dir_only_reports_the_path in the Python
# engine's test_corpora.py. CRAN permits R_user_dir() storage only while its
# contents are kept small and actively managed, so asking where the cache is
# must not bring it into being.
test_that("lexsync_cache_dir reports the path without creating it", {
  with_user_cache({
    dir <- lexsync_cache_dir()
    expect_identical(dir, tools::R_user_dir("lexsync", "cache"))
    expect_true(startsWith(dir, Sys.getenv("R_USER_CACHE_DIR")))
    expect_false(dir.exists(dir))
  })
})

# Pins the same contract as test_a_refused_fetch_leaves_the_cache_uncreated in
# the Python engine's test_corpora.py: every refusal comes before the cache is
# created, so a call that downloads nothing writes nothing.
test_that("a refused fetch leaves the cache uncreated", {
  with_user_cache({
    expect_error(fetch_corpus("subtlex_klingon", registry_path = registry_path()),
                 "not in the registry")
    expect_error(fetch_corpus("subtlex_esp", registry_path = registry_path()),
                 "landing page")
    expect_error(fetch_corpus("fake", registry_path = temp_registry("file:///etc/passwd")),
                 "non-http")
    expect_false(dir.exists(lexsync_cache_dir()))
  })
})

# Pins the same contract as test_fetch_corpus_creates_the_cache_and_sweeps_stale_sidecars
# in the Python engine's test_corpora.py. An interrupt or a dead process leaves
# a '.part' that no handler removed; the next download into the cache deletes
# every such sidecar a day old or more, and nothing else. A younger one may be a
# download still running in another session, so it is left alone.
test_that("a default-destination fetch creates the cache and sweeps stale sidecars", {
  local_mocked_bindings(download.file = mock_download(CSV_BODY))
  with_user_cache({
    expect_message(
      out <- fetch_corpus("fake", registry_path = temp_registry("https://example.invalid/good.csv")),
      "downloaded 'fake'"
    )
    expect_identical(out, file.path(lexsync_cache_dir(), "fake.csv"))
    expect_identical(list.files(lexsync_cache_dir()), "fake.csv")

    seed_cache(c("fake.csv.part", "other.csv.part", "other.csv", "busy.csv.part"))
    age_files(c("fake.csv.part", "other.csv.part"))
    expect_message(
      fetch_corpus("fake", registry_path = temp_registry("https://example.invalid/good.csv")),
      "downloaded 'fake'"
    )
    expect_identical(list.files(lexsync_cache_dir()),
                     c("busy.csv.part", "fake.csv", "other.csv"))
  })
})

# Pins the same contract as
# test_stale_sidecars_are_swept_even_when_the_download_then_fails in the Python
# engine's test_corpora.py. The sweep happens as the download starts, so a
# transfer that then fails still leaves the cache free of the stale sidecars it
# found.
test_that("stale sidecars are swept even when the download then fails", {
  local_mocked_bindings(download.file = function(url, destfile, ...) {
    writeBin(charToRaw("word,freq_zipf\ndog,4"), destfile)
    warning("connection reset")
  })
  with_user_cache({
    seed_cache(c("other.csv.part", "other.csv"))
    age_files("other.csv.part")
    expect_error(
      fetch_corpus("fake", registry_path = temp_registry("https://example.invalid/flaky.csv")),
      "could not download corpus 'fake'"
    )
    expect_identical(list.files(lexsync_cache_dir()), "other.csv")
  })
})

# This test has no Python twin, because that engine's fetch_corpus() takes no
# dest. A caller's `dest` may sit beside files lexsync never wrote, so the sweep
# is confined to the cache, which such a call does not create either.
test_that("a fetch to a caller's dest sweeps nothing and leaves the cache alone", {
  dir <- temp_cache()
  file.create(file.path(dir, "unrelated.part"))
  local_mocked_bindings(download.file = mock_download(CSV_BODY))
  with_user_cache({
    expect_message(
      fetch_corpus("fake", registry_path = temp_registry("https://example.invalid/good.csv"),
                   dest = file.path(dir, "fake.csv")),
      "downloaded 'fake'"
    )
    expect_false(dir.exists(lexsync_cache_dir()))
  })
  expect_identical(list.files(dir), c("fake.csv", "unrelated.part"))
})

# Pins the same contract as test_cache_clear_removes_one_corpus in the Python
# engine's test_corpora.py.
test_that("lexsync_cache_clear removes one corpus and its sidecar", {
  with_user_cache({
    dir <- seed_cache(c("fake.csv", "fake.csv.part", "other.csv", "fake_extra.csv"))
    removed <- expect_invisible(lexsync_cache_clear("fake"))
    expect_identical(removed, file.path(dir, c("fake.csv", "fake.csv.part")))
    expect_identical(list.files(dir), c("fake_extra.csv", "other.csv"))
    expect_identical(lexsync_cache_clear("fake"), character(0))
  })
})

# Pins the same contract as test_cache_clear_removes_the_whole_cache in the
# Python engine's test_corpora.py.
test_that("lexsync_cache_clear() removes the whole cache", {
  with_user_cache({
    dir <- seed_cache(c("fake.csv", "other.csv", "other.csv.part"))
    removed <- expect_invisible(lexsync_cache_clear())
    expect_setequal(basename(removed), c("fake.csv", "other.csv", "other.csv.part"))
    expect_false(dir.exists(dir))
  })
})

# Pins the same contract as test_cache_clear_on_an_absent_cache_creates_nothing
# in the Python engine's test_corpora.py.
test_that("lexsync_cache_clear on an absent cache removes and creates nothing", {
  with_user_cache({
    expect_identical(lexsync_cache_clear(), character(0))
    expect_identical(lexsync_cache_clear("fake"), character(0))
    expect_false(dir.exists(lexsync_cache_dir()))
  })
})

# Pins the same contract as test_cache_clear_refuses_a_path in the Python
# engine's test_corpora.py: the name is joined onto the cache directory, so a
# separator, or the colon of a Windows drive, would reach outside it.
test_that("lexsync_cache_clear refuses a name that is not a single corpus name", {
  with_user_cache({
    dir <- seed_cache("fake.csv")
    # The file that "../outside" would reach, beside the cache directory.
    outside <- file.path(dirname(dir), "outside.csv")
    file.create(outside)
    for (bad in list("../outside", "..\\outside", "a/b", "C:outside", "a:b", "",
                     NA_character_, c("a", "b"), 1)) {
      expect_error(lexsync_cache_clear(bad), "not a path", info = deparse(bad))
    }
    expect_true(file.exists(outside))
    expect_identical(list.files(dir), "fake.csv")
  })
})

# Pins the same contract as test_cache_clear_takes_a_name_literally in the
# Python engine's test_corpora.py. unlink() expands wildcards unless told not
# to, so "*" once emptied the cache while reporting nothing removed. A name
# names one corpus's files, and a directory that happens to carry that name is
# not one of them.
test_that("lexsync_cache_clear takes a name literally", {
  with_user_cache({
    dir <- seed_cache(c("a.csv", "b.csv"))
    dir.create(file.path(dir, "d.csv"))
    for (pattern in c("*", "?", "[ab]")) {
      expect_identical(lexsync_cache_clear(pattern), character(0), info = pattern)
    }
    expect_identical(lexsync_cache_clear("d"), character(0))
    expect_identical(list.files(dir), c("a.csv", "b.csv", "d.csv"))
  })
})

# A cache path holding brackets must name itself. Globbed, <tmp>/a[1] matched
# <tmp>/a1, so clearing one cache deleted another. The Python engine joins paths
# literally, so this test has no twin.
test_that("lexsync_cache_clear() empties its own cache when the path holds brackets", {
  root <- tempfile("lexsync-")
  own <- file.path(root, "a[1]")
  sibling <- file.path(root, "a1", "R", "lexsync")
  dir.create(sibling, recursive = TRUE)
  file.create(file.path(sibling, "keep.csv"))
  old <- Sys.getenv("R_USER_CACHE_DIR", unset = NA)
  on.exit({
    if (is.na(old)) Sys.unsetenv("R_USER_CACHE_DIR") else Sys.setenv(R_USER_CACHE_DIR = old)
    unlink(root, recursive = TRUE)
  }, add = TRUE)
  Sys.setenv(R_USER_CACHE_DIR = own)
  seed_cache("fake.csv")
  expect_identical(basename(lexsync_cache_clear()), "fake.csv")
  expect_false(dir.exists(lexsync_cache_dir()))
  expect_true(file.exists(file.path(sibling, "keep.csv")))
})

test_that("list_corpora surfaces the registry status", {
  frame <- list_corpora(registry_path())
  status <- stats::setNames(frame$status, frame$name)
  expect_identical(unname(status[["subtlex_uk"]]), "manual")
  expect_identical(unname(status[["subtlex_esp"]]), "listed")
  expect_false("validated" %in% status)
})

# An explicit registry_path is read on its own. A missing one gave base R's connection
# error here, while the Python twin fell through to another registry and reported its
# corpora under the caller's path. Pinned identically in test_corpora.py.
test_that("a registry_path that does not exist is refused", {
  missing <- file.path(tempdir(), "no_such_registry.yaml")
  expect_error(list_corpora(missing), "lexsync: registry not found", fixed = TRUE)
  expect_error(fetch_corpus("subtlex_esp", registry_path = missing),
               "lexsync: registry not found", fixed = TRUE)
})

# The file the lexsync.registry option names is read on its own as well, so a misspelt
# or stale option is refused by name and cannot fall through to the checkout's registry
# or the bundled one. An empty option leaves the search as it is, and an explicit
# registry_path is read whatever the option says. Pinned identically in
# test_corpora.py, with LEXSYNC_REGISTRY.
test_that("a lexsync.registry option naming a missing file is refused", {
  missing <- file.path(tempdir(), "no_such_registry.yaml")
  old <- options(lexsync.registry = missing); on.exit(options(old))
  msg <- sprintf("lexsync: registry not found: '%s' (the lexsync.registry option).", missing)
  expect_error(list_corpora(), msg, fixed = TRUE)
  expect_error(fetch_corpus("subtlex_esp"), msg, fixed = TRUE)
  expect_gt(nrow(list_corpora(registry_path())), 0L)
  options(lexsync.registry = "")
  expect_gt(nrow(list_corpora()), 0L)
})
