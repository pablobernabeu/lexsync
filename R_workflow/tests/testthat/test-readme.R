# The README's Quick start is executable documentation of the package API, and
# nothing runs it: R_workflow/README.md is a plain .md, so the vignette build that
# R CMD check performs never reaches it. The step that has to survive an edit is
# build_pool: match_stimuli never reads a design's pool_filters, so an example that
# drops the pool step silently matches over the whole lexicon and demonstrates a
# selection nobody could reproduce from the design it shows. The Python twin pins its
# own README the same way in tests/test_readme.py.
#
# Repository-coupled, so it skips when the file is absent (a check run from a source
# tarball, for instance).

readme_quick_start <- function() {
  path <- "../../README.md"
  if (!file.exists(path)) skip("The R package README is not in this tree.")
  lines <- readLines(path, warn = FALSE)
  head <- grep("^## Quick start", lines)
  if (length(head) != 1L) skip("The README has no single Quick start section.")
  opens <- grep("^``` r$", lines)
  opens <- opens[opens > head]
  if (!length(opens)) skip("The Quick start section holds no R fence.")
  start <- opens[1]
  closes <- grep("^```$", lines)
  closes <- closes[closes > start]
  paste(lines[seq(start + 1L, closes[1] - 1L)], collapse = "\n")
}

test_that("the README's Quick start applies pool_filters through build_pool", {
  snippet <- readme_quick_start()
  # Without this step the design's pool_filters are inert.
  expect_true(grepl("build_pool", snippet, fixed = TRUE))

  e <- new.env(parent = globalenv())
  eval(parse(text = snippet), envir = e)

  expect_true(all(e$pool$length >= 3 & e$pool$length <= 7))
  expect_true(all(e$pool$frequency >= 3.8 & e$pool$frequency <= 7))
  expect_equal(nrow(e$stim), 30L)
  expect_true(all(e$stim$length <= 7))
  # Passing the raw lexicon silently drops the filter: longer words become
  # eligible and the selection changes.
  unfiltered <- match_stimuli(e$lex, e$design, e$schema)
  expect_false(identical(sort(unfiltered$word), sort(e$stim$word)))
})

test_that("the Get started vignette builds its pool the same way", {
  path <- "../../vignettes/lexsync.Rmd"
  if (!file.exists(path)) skip("The vignettes are not in this tree.")
  text <- paste(readLines(path, warn = FALSE), collapse = "\n")
  # The vignette's code runs when the vignette is built, so what needs pinning here
  # is only that it still demonstrates the filtered pool the README does.
  expect_true(grepl("build_pool(lex, design$pool_filters)", text, fixed = TRUE))
})
