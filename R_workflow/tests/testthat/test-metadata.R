# DESCRIPTION is hand-maintained and other artefacts (the README, the sibling
# citation files) treat it as the source of truth, so these tests pin its
# contract: Imports names exactly the namespaces the R sources call
# unconditionally, the author record carries the same ORCID as
# codemeta.json, CITATION.cff and .zenodo.json, and the Copyright field names
# a notice file that R installs.

description_fields <- function() {
  path <- file.path("..", "..", "DESCRIPTION")
  if (!file.exists(path)) skip("The source DESCRIPTION is not in this tree.")
  as.list(read.dcf(path)[1, ])
}

parse_deps <- function(field) {
  # Strip version requirements such as "testthat (>= 3.0.0)".
  deps <- trimws(strsplit(field, ",")[[1]])
  sub("\\s*\\(.*\\)$", "", deps)
}

test_that("Imports matches the namespaces the R code uses unconditionally", {
  imports <- parse_deps(description_fields()$Imports)
  # stringi backs .lower_invariant(), the case fold behind every byte-order
  # tie-break; jsonlite and digest back the datasheet checksums. All are
  # called with :: outside any requireNamespace guard.
  expect_setequal(imports, c("readr", "yaml", "stringdist", "stringi",
                             "jsonlite", "digest", "stats", "tools", "utils"))
})

test_that("guarded and test-only packages are declared in Suggests, not Imports", {
  suggests <- parse_deps(description_fields()$Suggests)
  # clue is guarded by requireNamespace() in matching.R; zip, shiny, bslib and
  # DT are exercised only by test-apps.R, which skips when they are absent.
  expect_true(all(c("clue", "zip", "shiny", "bslib", "DT") %in% suggests))
  expect_false(any(c("dplyr", "tidyr", "stringr") %in% suggests))
})

test_that("the author record carries the ORCID shared by the citation files", {
  authors <- description_fields()[["Authors@R"]]
  expect_match(authors, "0000-0003-1083-2460", fixed = TRUE)
})

test_that("the README's R install line names every third-party Import", {
  # The quick start is the first thing a new user runs, and DESCRIPTION is the only
  # source of truth for what it must install. Adding an Import without amending the
  # README leaves a documented command that fails on a fresh library, which is how
  # stringi went missing; base packages ship with R and are excluded.
  readme <- repo_path("README.md", message = "The repository README is not in this tree.")
  if (!file.exists(readme)) skip("The repository README is not in this tree.")
  line <- grep("install.packages", readLines(readme, warn = FALSE), value = TRUE)[1]
  expect_true(!is.na(line))
  third_party <- setdiff(parse_deps(description_fields()$Imports),
                         c("stats", "tools", "utils", "methods", "grDevices", "graphics"))
  for (pkg in third_party) expect_match(line, sprintf("'%s'", pkg), fixed = TRUE)
})

test_that("the Title is short enough for CRAN and stable under toTitleCase", {
  # CRAN asks for fewer than 65 characters, and checks the title case with this
  # very function, so a title that toTitleCase would rewrite is a title CRAN will
  # query. The same string is carried by inst/CITATION, CITATION.cff,
  # codemeta.json, .zenodo.json and both packages' front pages.
  title <- description_fields()$Title
  expect_lt(nchar(title), 65L)
  expect_identical(tools::toTitleCase(title), title)
  expect_false(startsWith(title, "lexsync"))
})

test_that("the data terms are installed with the package and the LICENSE stub is untouched", {
  # The bundled example lexica are wordfreq derivatives under CC BY-SA 4.0, not
  # MIT, so a user who has only an installed copy must still be able to find the
  # terms. LICENSE stays the two-line CRAN template, which its own check
  # constrains and which GitHub's licence detector needs unadorned. R installs no
  # top-level file but INDEX, LICENSE or LICENCE and NEWS (Writing R Extensions,
  # section 1.1.5), so the terms used to sit in LICENSE.note, which binary
  # installations never carried. They now live in inst/COPYRIGHTS, the file
  # section 1.1.1 names for a Copyright field to point at, and LICENSE.note stays
  # in the sources as a pointer to it.
  # test_metadata.py::test_the_bundled_data_terms_ship_with_both_packages asserts
  # the same of the Python distribution.
  fields <- description_fields()
  expect_identical(fields$License, "MIT + file LICENSE")
  copyright <- gsub("\\s+", " ", fields$Copyright)
  expect_match(copyright, "COPYRIGHTS file installed with the package", fixed = TRUE)
  expect_match(copyright, "https://creativecommons.org/licenses/by-sa/4.0/", fixed = TRUE)
  expect_no_match(copyright, "LICENSE.note", fixed = TRUE)

  stub <- file.path("..", "..", "LICENSE")
  expect_identical(readLines(stub, warn = FALSE),
                   c("YEAR: 2026", "COPYRIGHT HOLDER: Pablo Bernabeu"))

  # The checks below read the sources. covr runs the tests inside the installed
  # package, where DESCRIPTION and LICENSE also sit two levels up but inst/ does
  # not exist, so the sources' inst/ folder marks a source tree. In a source tree
  # or tarball both files below are always present, so a missing one fails.
  if (!dir.exists(file.path("..", "..", "inst"))) {
    skip("The package sources are not in this tree.")
  }
  notice <- file.path("..", "..", "inst", "COPYRIGHTS")
  expect_true(file.exists(notice))
  text <- paste(readLines(notice, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
  expect_match(text, "CC BY-SA 4.0", fixed = TRUE)
  expect_match(text, "https://creativecommons.org/licenses/by-sa/4.0/", fixed = TRUE)
  expect_match(text, "SUBTLEX", fixed = TRUE)
  for (f in c("en_example.csv", "es_example.csv", "zh_example.csv")) {
    expect_match(text, f, fixed = TRUE)
  }
  # The English slice keeps only forms SUBTLEX-US lists in lower case often enough, so
  # the list is a direct source of it.
  expect_match(gsub("\\s+", " ", text), "is therefore a direct source of en_example.csv",
               fixed = TRUE)

  pointer <- paste(readLines(file.path("..", "..", "LICENSE.note"), warn = FALSE),
                   collapse = " ")
  expect_match(pointer, "inst/COPYRIGHTS", fixed = TRUE)
  expect_no_match(pointer, "SUBTLEX", fixed = TRUE)

  # The citation footer names the installed file too.
  footer <- paste(readLines(file.path("..", "..", "inst", "CITATION"), warn = FALSE),
                  collapse = " ")
  expect_match(footer, "COPYRIGHTS", fixed = TRUE)
  expect_no_match(footer, "LICENSE.note", fixed = TRUE)
})

test_that("an installed lexsync carries the data terms as COPYRIGHTS", {
  # The test above reads the sources, and this one reads whatever copy of lexsync
  # is loaded. Under R CMD check that is the installed package, and under
  # devtools::load_all() system.file() looks in inst/. Binary installations of
  # 0.1.1 carried the CC BY-SA lexica without the notice file their Copyright
  # field named, because R does not install LICENSE.note.
  skip_if_not(nzchar(system.file(package = "lexsync")), "lexsync is not installed")
  notice <- system.file("COPYRIGHTS", package = "lexsync")
  expect_true(nzchar(notice))
  if (nzchar(notice)) {
    text <- paste(readLines(notice, warn = FALSE, encoding = "UTF-8"), collapse = " ")
    expect_match(text, "https://creativecommons.org/licenses/by-sa/4.0/", fixed = TRUE)
  }
})
