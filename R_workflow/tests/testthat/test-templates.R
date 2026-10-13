# The experiment templates are mirrored into both packages; the mirrors must match.
#
# templates/ at the repository root is the canonical copy. Both packages carry
# their own so an installed copy can reach one without the repository: the R
# package under inst/templates/, the Python package under src/lexsync/templates/,
# and each resolves its own through .lexsync_template() / find_template().
#
# Nothing enforced that the three agree, and no functional test can. A stale
# mirror is still a perfectly valid template: it renders, it runs, and the
# experiment it produces is simply not the one the repository documents. For the
# trigger templates that is worse than ordinary staleness, because what drifts is
# the code time-locking EEG markers to stimulus onset, and an experiment that
# records the wrong onset does not fail -- it quietly collects unusable data.
#
# Comparing the bytes is the check that catches it. Twinned with
# python_workflow/tests/test_templates.py.
# Repository-level checks skip when the package is checked away from its
# repository; helper-repo.R says why a directory named templates/ is not enough.

repo_templates_dir <- function() {
  path <- repo_path("templates", message = "repository templates not available")
  testthat::skip_if_not(dir.exists(path), "repository templates not available")
  path
}

packaged_templates_dir <- function() {
  path <- system.file("templates", package = "lexsync")
  testthat::skip_if_not(nzchar(path) && dir.exists(path), "packaged templates not available")
  path
}

relative_tree <- function(root) {
  sort(list.files(root, recursive = TRUE, all.files = FALSE))
}

read_raw <- function(path) readBin(path, "raw", file.size(path))

test_that("the packaged mirror holds the same files as the repository", {
  canonical <- relative_tree(repo_templates_dir())
  expect_gt(length(canonical), 0)
  expect_identical(relative_tree(packaged_templates_dir()), canonical)
})

test_that("each packaged template is byte-identical to the repository copy", {
  canonical_dir <- repo_templates_dir()
  packaged_dir <- packaged_templates_dir()
  for (rel in relative_tree(canonical_dir)) {
    # A template missing from the mirror is a failure in its own right; reading it
    # would only add an unrelated connection error and warning to the report.
    packaged <- file.path(packaged_dir, rel)
    expect_true(file.exists(packaged), info = rel)
    if (!file.exists(packaged)) next
    expect_identical(read_raw(packaged), read_raw(file.path(canonical_dir, rel)), info = rel)
  }
})

test_that("every script and stylesheet from a CDN carries its integrity", {
  # The jsPsych page loaded jsPsych, its keyboard plugin and its stylesheet from unpkg
  # with no integrity attribute, so a copy altered on the CDN would run in the page that
  # collects the participants' responses. Each tag now names its file in full and
  # carries the file's SHA-384 and crossorigin="anonymous", without which a browser
  # cannot check the hash of a file from another origin. Twinned with
  # test_templates.py.
  html <- paste(readLines(file.path(repo_templates_dir(), "jspsych",
                                    "experiment_template.html"), warn = FALSE,
                          encoding = "UTF-8"), collapse = "\n")
  tags <- regmatches(html, gregexpr("<(script|link)\\b[^>]*>", html, perl = TRUE))[[1]]
  attr_of <- function(tag, name) {
    m <- regmatches(tag, regexec(sprintf('\\s%s="([^"]*)"', name), tag, perl = TRUE))[[1]]
    if (length(m)) m[2] else NA_character_
  }
  address <- vapply(tags, function(tag) {
    if (startsWith(tag, "<script")) attr_of(tag, "src")
    else if (identical(attr_of(tag, "rel"), "stylesheet")) attr_of(tag, "href")
    else NA_character_
  }, character(1), USE.NAMES = FALSE)
  fetched <- !is.na(address) & grepl("^https?://", address)
  expect_identical(paste(sub("^<(\\w+).*$", "\\1", tags[fetched]),
                         sub("^.*\\.", "", address[fetched])),
                   c("script js", "script js", "link css"))
  for (tag in tags[fetched]) {
    expect_true(grepl("^sha384-[A-Za-z0-9+/]{64}$", attr_of(tag, "integrity")), info = tag)
    expect_identical(attr_of(tag, "crossorigin"), "anonymous", info = tag)
  }
  # The files themselves: a bare package address is answered with a redirect.
  expect_true(all(grepl("@[0-9.]+/(dist|css)/[a-z.]+\\.(js|css)$", address[fetched])))
  # The SHA-384 of each published file, which the files unpkg serves and the npm
  # registry's tarballs of these releases both give. A wrong hash would stop the page
  # from loading jsPsych at all.
  integrity <- vapply(tags[fetched], attr_of, character(1), name = "integrity",
                      USE.NAMES = FALSE)
  expect_identical(stats::setNames(integrity, address[fetched]), c(
    "https://unpkg.com/jspsych@7.3.4/dist/index.browser.min.js" =
      "sha384-XAUySaEe2MZZhTzbstOfwmVuzWlsblgOwTje2VO+r73k+MzUbgzn/AwQlxq7OdCi",
    "https://unpkg.com/@jspsych/plugin-html-keyboard-response@1.1.3/dist/index.browser.min.js" =
      "sha384-dY7LWgOfoIq6dkJslZMW+KMzvwcrQwzIbqPqWm/vQdrc+2o69tyPWHsIZQUQ1NYi",
    "https://unpkg.com/jspsych@7.3.4/css/jspsych.css" =
      "sha384-F1pvd1ZCaxuJalclhLrJj8A5LWkFVuFinaHeIgOZXnnCGt7HAbSPzTw7fO3qeJ8F"))
})

test_that("the OpenSesame snippet opens the serial port it names", {
  # The snippet's serial branch opened the first port pyserial listed, at pyserial's
  # default rate, and that port could be another device. It now opens the port named at
  # its top, at the rate named there, as the generated setup opens the one the schema
  # names. test_templates.py runs it with a fake pyserial that lists another port first.
  lines <- readLines(file.path(repo_templates_dir(), "opensesame", "inline_trigger_setup.py"),
                     warn = FALSE, encoding = "UTF-8")
  expect_true(any(grepl("^var\\.serial_port = u'[^']+'", lines)))
  expect_true(any(grepl("^var\\.serial_baudrate = [0-9]+", lines)))
  expect_true(any(grepl("_sp = serial.Serial(var.serial_port, int(var.serial_baudrate))",
                        lines, fixed = TRUE)))
  expect_false(any(grepl("comports|_ports\\[0\\]", lines)))
})
