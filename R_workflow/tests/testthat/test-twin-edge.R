# Twin-edge parity: small edge-case designs held to a pinned outcome.
#
# The parity gates compare the engines on the shipped designs, whose inputs are clean.
# Inputs that are not (padded fields, missing values, unusual YAML) take code paths the
# shipped designs never reach, and two engines that agree can still both be wrong. Each
# case under parity/twin_edge/ at the repository root therefore pins what the engine
# must do: write these artefacts byte for byte, or raise this refusal. The layout of a
# case and of its expect.yaml is described in python_workflow/tests/test_twin_edge.py,
# which holds the Python engine to the same expectations. tools/twin_edge.py writes a
# case's expected/ folder from the Python engine, and this file confirms it for R.
#
# Every test here needs the repository, so all of them skip on CRAN. The source-tree
# run in CI fails on any skip, which is what pins both engines there.

te_kinds <- c("stimuli", "descriptives", "comparisons", "experiments")
te_expect_keys <- c("outcome", "refusal", "compare", "datasheet")

te_cases <- function() {
  root <- repo_path("parity", "twin_edge")
  if (!dir.exists(root)) return(character())
  sort(basename(list.dirs(root, recursive = FALSE)))
}

# The artefact kind of a path relative to an output directory or to expected/, with or
# without the engine tag, or NA for provenance (datasheets and run logs), which no case
# pins.
te_kind <- function(rel) {
  folder <- sub("/.*$", "", rel)
  name <- sub("^[^/]*/", "", rel)
  ifelse(folder == "stimuli", "stimuli",
  ifelse(folder == "experiments", "experiments",
  ifelse(grepl("_descriptives(_(R|py))?\\.[^.]+$", name), "descriptives",
  ifelse(grepl("_comparisons(_(R|py))?\\.[^.]+$", name), "comparisons", NA_character_))))
}

# Every file under `root`, as a named list of raw vectors keyed by relative path.
te_tree <- function(root) {
  if (!dir.exists(root)) return(list())
  rel <- sort(list.files(root, recursive = TRUE, all.files = TRUE, no.. = TRUE))
  stats::setNames(lapply(rel, function(r) {
    f <- file.path(root, r)
    readBin(f, "raw", file.info(f)$size)
  }), rel)
}

# The run's artefacts of the compared kinds, keyed as expected/ names them, with the
# engine tag stripped from the value artefacts. The experiments carry none.
te_pinned <- function(outdir, compare) {
  tree <- te_tree(outdir)
  keep <- names(tree)[te_kind(names(tree)) %in% compare]
  stats::setNames(tree[keep], sub("_(R|py)(\\.[^.]+)$", "\\2", keep))
}

# Everything wrong with a case folder's layout and expect.yaml, as messages.
te_problems <- function(case_dir) {
  if (!file.exists(file.path(case_dir, "design.yaml"))) return("design.yaml is missing")
  if (!file.exists(file.path(case_dir, "expect.yaml"))) return("expect.yaml is missing")
  expect <- tryCatch(yaml::read_yaml(file.path(case_dir, "expect.yaml")),
                     error = function(e) e)
  if (inherits(expect, "error")) {
    return(paste("expect.yaml does not parse:", conditionMessage(expect)))
  }
  if (!is.list(expect) || is.null(names(expect))) return("expect.yaml must be a mapping")
  out <- character()
  unknown <- setdiff(names(expect), te_expect_keys)
  if (length(unknown)) out <- c(out, paste("unknown keys", paste(unknown, collapse = ", ")))
  outcome <- expect[["outcome"]]
  expected <- file.path(case_dir, "expected")
  if (!is.character(outcome) || length(outcome) != 1L ||
      !outcome %in% c("artefacts", "refusal")) {
    out <- c(out, "outcome must be one of artefacts, refusal")
  } else if (identical(outcome, "refusal")) {
    refusal <- expect[["refusal"]]
    if (!is.character(refusal) || length(refusal) != 1L || !nzchar(trimws(refusal))) {
      out <- c(out, "outcome refusal needs a non-empty refusal string")
    }
    # By name, not by value: the YAML reader keeps `key: ~` as a NULL element.
    for (key in c("compare", "datasheet")) {
      if (key %in% names(expect)) out <- c(out, paste(key, "applies only to outcome artefacts"))
    }
    if (file.exists(expected)) out <- c(out, "a refusal case has no expected/ folder")
  } else {
    if ("refusal" %in% names(expect)) out <- c(out, "refusal applies only to outcome refusal")
    compare <- unlist(expect[["compare"]], use.names = FALSE)
    if (!is.character(compare) || !length(compare) || !all(compare %in% te_kinds) ||
        anyDuplicated(compare)) {
      out <- c(out, paste("compare must list distinct kinds from",
                          paste(te_kinds, collapse = ", ")))
      compare <- character()
    }
    datasheet <- expect[["datasheet"]]
    if ("datasheet" %in% names(expect) &&
        (!is.list(datasheet) || (length(datasheet) && is.null(names(datasheet))))) {
      out <- c(out, "datasheet must map dotted paths to values")
    }
    pinned <- names(te_tree(expected))
    nested <- grepl("/", pinned, fixed = TRUE)
    kinds <- te_kind(pinned[nested])
    for (kind in compare) {
      if (!kind %in% kinds) {
        out <- c(out, sprintf("expected/ holds no %s file (run tools/twin_edge.py --update)",
                              kind))
      }
    }
    stray <- pinned[!nested | !te_kind(pinned) %in% compare]
    if (length(stray)) {
      out <- c(out, paste("expected/ holds files no compared kind covers:",
                          paste(stray, collapse = ", ")))
    }
  }
  out
}

# A list element is addressed by its position counted from 0, as in the Python twin.
te_lookup <- function(record, dotted) {
  node <- record
  for (part in strsplit(dotted, ".", fixed = TRUE)[[1]]) {
    node <- if (is.null(names(node))) node[[as.integer(part) + 1L]] else node[[part]]
  }
  node
}

te_run <- function(case_dir, outdir) {
  schema <- file.path(case_dir, "schema.yaml")
  if (!file.exists(schema)) schema <- repo_path("config", "schema.yaml")
  run_pipeline("design.yaml", schema, outdir, verbose = FALSE)
}

test_that("twin_edge_cases_have_valid_expectations", {
  root <- repo_path("parity", "twin_edge")
  cases <- te_cases()
  expect_true(length(cases) > 0L, info = paste("no twin-edge cases under", root))
  for (case in cases) {
    expect_identical(te_problems(file.path(root, case)), character(), info = case)
  }
})

test_that("twin_edge_case_matches_its_pinned_outcome", {
  root <- repo_path("parity", "twin_edge")
  cases <- te_cases()
  expect_true(length(cases) > 0L, info = paste("no twin-edge cases under", root))
  for (case in cases) {
    case_dir <- normalizePath(file.path(root, case), winslash = "/")
    expect_identical(te_problems(case_dir), character(), info = case)
    expect <- yaml::read_yaml(file.path(case_dir, "expect.yaml"))
    before <- te_tree(case_dir)
    outdir <- file.path(tempfile("twin_edge_"), "out")
    old <- setwd(case_dir)
    if (identical(expect$outcome, "refusal")) {
      msg <- tryCatch({ te_run(case_dir, outdir); NA_character_ },
                      error = function(e) conditionMessage(e))
      setwd(old)
      expect_false(is.na(msg), info = paste(case, ": the run did not refuse"))
      expect_true(grepl(expect$refusal, msg, fixed = TRUE),
                  info = sprintf("%s: refused with '%s'", case, msg))
    } else {
      res <- tryCatch({ te_run(case_dir, outdir); NULL }, error = function(e) e)
      setwd(old)
      expect_null(res, info = case)
      if (!is.null(res)) next
      compare <- unlist(expect$compare, use.names = FALSE)
      got <- te_pinned(outdir, compare)
      want <- te_tree(file.path(case_dir, "expected"))
      expect_identical(sort(names(got)), sort(names(want)),
                       info = paste(case, ": the run wrote a different set of files"))
      differing <- Filter(function(r) !identical(got[[r]], want[[r]]), names(want))
      expect_identical(differing, character(),
                       info = paste(case, ": these artefacts differ from the pinned ones"))
      ds <- grep("^reports/.*_datasheet_R\\.json$", names(te_tree(outdir)), value = TRUE)
      expect_length(ds, 1L)
      record <- jsonlite::read_json(file.path(outdir, ds[1]))
      for (dotted in names(expect$datasheet)) {
        expect_equal(unlist(te_lookup(record, dotted)),
                     unlist(expect$datasheet[[dotted]]),
                     info = paste(case, ": datasheet", dotted))
      }
    }
    unlink(dirname(outdir), recursive = TRUE)
    # The inputs are fixtures: a run that wrote beside them would change the next run.
    expect_identical(te_tree(case_dir), before,
                     info = paste(case, ": the run wrote into the case folder"))
  }
})
