# Tests for the Shiny front-end in apps/r_shiny. The app is not part of the
# package, so these skip wherever it or its interface dependencies are absent
# (a package check run from a source tarball, for instance).

app_env <- function() {
  skip_if_not_installed("shiny")
  skip_if_not_installed("bslib")
  skip_if_not_installed("DT")
  app <- NULL
  for (cand in c("apps/r_shiny/app.R", "../../../apps/r_shiny/app.R",
                 "../../../../apps/r_shiny/app.R")) {
    if (file.exists(cand)) { app <- cand; break }
  }
  if (is.null(app)) skip("The Shiny app source is not in this tree.")
  e <- new.env(parent = globalenv())
  ok <- tryCatch({ source(app, local = e); TRUE },
                 error = function(err) conditionMessage(err))
  if (!isTRUE(ok)) skip(paste("The Shiny app could not be sourced:", ok))
  e
}

test_that("positive_tolerances keeps only the dimensions given a positive k", {
  e <- app_env()
  # A k of zero must not reach the design: it means "use the schema default", not
  # "match to a zero-width window". Pinned identically in tests/test_apps.py.
  expect_equal(
    e$positive_tolerances(list(length = 0, frequency = 0.111, n_density = 2)),
    list(frequency = 0.111, n_density = 2)
  )
  # Empty, so build_design writes no tolerance_k key at all and the schema stands.
  expect_length(e$positive_tolerances(list(length = 0, old20 = 0)), 0)
  expect_length(e$positive_tolerances(list()), 0)
  expect_equal(e$positive_tolerances(list(length = NA_real_, frequency = 1)),
               list(frequency = 1))
})

test_that("positive_tolerances preserves the order the dimensions are matched on", {
  e <- app_env()
  expect_equal(names(e$positive_tolerances(list(old20 = 2, length = 1, frequency = 0.5))),
               c("old20", "length", "frequency"))
})

test_that("the bundle zip holds the design and every artefact at outdir-relative paths", {
  e <- app_env()
  skip_if_not_installed("zip")
  outdir <- file.path(tempfile("lexsync_zip_"), "output")
  dir.create(file.path(outdir, "reports"), recursive = TRUE)
  writeLines("name: my_design", file.path(outdir, "my_design.yaml"))
  writeLines("word\ncat", file.path(outdir, "stimuli.csv"))
  writeLines("# datasheet", file.path(outdir, "reports", "datasheet.md"))

  zf <- tempfile(fileext = ".zip")
  e$write_bundle_zip(zf, outdir)

  # The same three entries the Streamlit app's make_zip produces (test_apps.py):
  # names are relative to outdir and subdirectories survive.
  expect_equal(sort(zip::zip_list(zf)$filename),
               c("my_design.yaml", "reports/datasheet.md", "stimuli.csv"))
})

test_that("the bundle zip needs no external zip executable", {
  e <- app_env()
  skip_if_not_installed("zip")
  outdir <- tempfile("lexsync_zip_"); dir.create(outdir)
  writeLines("word\ncat", file.path(outdir, "stimuli.csv"))
  zf <- tempfile(fileext = ".zip")

  # utils::zip shells out to R_ZIPCMD, which a stock R for Windows does not ship.
  # Pointing it at a name that cannot resolve proves the export no longer uses it.
  old <- Sys.getenv("R_ZIPCMD", unset = NA)
  on.exit(if (is.na(old)) Sys.unsetenv("R_ZIPCMD") else Sys.setenv(R_ZIPCMD = old))
  Sys.setenv(R_ZIPCMD = "lexsync-no-such-zip-tool")
  expect_no_warning(e$write_bundle_zip(zf, outdir))
  expect_true(file.exists(zf))
  expect_equal(zip::zip_list(zf)$filename, "stimuli.csv")
})

test_that("the app offers exactly the paradigms the engine implements", {
  e <- app_env()
  # Against the registry, not a written-out list: a paradigm added to the engine
  # must reach the chooser, and a hard-coded expectation would simply pin
  # whatever the app happened to offer. Pinned identically in tests/test_apps.py.
  expect_equal(sort(unname(e$PARADIGMS)), sort(names(lexsync::PARADIGMS)))
})

test_that("every item-table paradigm the app offers has a bundled example table", {
  e <- app_env()
  # The app writes items/<example> into the design and runs the pipeline against
  # it, so a named table that is not in the repository would fail at run time.
  # The app's own REPO_ROOT walks up from the working directory, which from
  # tests/testthat does not reach the checkout, so the tree is found here the
  # same way the app source is.
  items_dir <- NULL
  for (cand in c("items", "../../../items", "../../../../items")) {
    if (dir.exists(cand)) { items_dir <- cand; break }
  }
  if (is.null(items_dir)) skip("The bundled item tables are not in this tree.")
  expect_gt(length(e$ITEM_TABLE_EXAMPLES), 0L)
  expect_true(all(names(e$ITEM_TABLE_EXAMPLES) %in% unname(e$PARADIGMS)))
  for (p in names(e$ITEM_TABLE_EXAMPLES)) {
    expect_true(p %in% names(lexsync::PARADIGMS))
    expect_true(file.exists(file.path(items_dir, e$ITEM_TABLE_EXAMPLES[[p]])))
  }
})

test_that("the app offers exactly the pseudoword generators the engine implements", {
  e <- app_env()
  # The engine default first: the design only names a method when the other is
  # chosen. Pinned identically in tests/test_apps.py.
  expect_equal(e$GENERATION_METHODS, c("letter_substitution", "subsyllabic"))
})

test_that("the design YAML is written with LF endings on every platform", {
  e <- app_env()
  # The pipeline hashes the design file it ran into the datasheet's
  # design_sha256, so the bytes must not record which operating system wrote
  # them; yaml::write_yaml and writeLines both open text-mode connections,
  # which on Windows turn every newline into CRLF. tests/test_apps.py pins the
  # same property for the Streamlit app's _write_design_yaml.
  path <- tempfile(fileext = ".yaml")
  e$write_yaml_lf(list(name = "t", n_per_condition = 10L), path)
  raw <- readBin(path, "raw", file.info(path)$size)
  expect_false(any(raw == as.raw(0x0d)))
  expect_identical(raw[length(raw)], as.raw(0x0a))
  expect_identical(yaml::read_yaml(path)$name, "t")
})

test_that("a cell edit lands in the column the user edited", {
  e <- app_env()
  skip_if_not_installed("DT")
  # The table is rendered with rownames = FALSE, so the client's column index is
  # zero-based over the displayed columns. DT::editData defaults to rownames =
  # TRUE and then reads one column to the left, which silently rewrote 'name'
  # from an edit to 'dimension' and dropped an edit to 'name' altogether.
  shiny::testServer(e$server, {
    session$setInputs(cond_tbl_cell_edit =
                        data.frame(row = 1L, col = 1L, value = "n_density"))
    expect_equal(conds()$name[1], "high_frequency")
    expect_equal(conds()$dimension[1], "n_density")

    session$setInputs(cond_tbl_cell_edit =
                        data.frame(row = 1L, col = 0L, value = "renamed"))
    expect_equal(conds()$name[1], "renamed")
    expect_equal(rownames(conds()), c("1", "2"))
  })
})

test_that("every preset leaves the optional second-factor columns numeric", {
  e <- app_env()
  # DT coerces the whole column to character when it edits a logical cell, so a
  # preset that leaves the second factor empty must still type it as numeric.
  for (preset in names(e$PRESET_MATCHING)) {
    df <- e$preset_df(preset)
    expect_type(df$lower2, "double")
    expect_type(df$upper2, "double")
  }
})

test_that("a preset sets the matched dimensions and the method that suit it", {
  e <- app_env()
  skip_if_not_installed("DT")
  # Filling only the conditions table left 'Match on' at its general default, so
  # the neighbourhood preset asked the engine to match on the dimension it
  # manipulates. The table is pinned against the Streamlit one in test_apps.py.
  sent <- new.env()
  e$updateSelectizeInput <- function(session, inputId, ..., selected) sent[[inputId]] <- selected
  e$updateSelectInput <- function(session, inputId, ..., selected) sent[[inputId]] <- selected
  shiny::testServer(e$server, {
    # The chooser starts at the first preset and the client echoes that value, so
    # the observer ignores it; walking back up the list changes it every time.
    session$setInputs(preset = e$DEFAULT_PRESET)
    for (preset in rev(names(e$PRESET_MATCHING))) {
      session$setInputs(preset = preset)
      m <- e$PRESET_MATCHING[[preset]]
      expect_equal(sent$match_on, m$match_on)
      expect_equal(sent$method, m$method)
      manipulated <- setdiff(unique(c(conds()$dimension, conds()$dimension2)), "")
      expect_length(intersect(m$match_on, manipulated), 0L)
    }
  })
})

test_that("a condition bound that is not a number drops that factor", {
  e <- app_env()
  # as.numeric on a cell the editor let through as text gives NA and a warning, and
  # the design then carried define_by = c(NA, NA) as if the user had asked for it.
  # Pinned identically in tests/test_apps.py.
  df <- data.frame(
    name = c("a", "b", "c", ""),
    dimension = c("frequency", "frequency", "gender", "frequency"),
    lower = c("5.0", "3.0", NA, "1.0"), upper = c("7.0", "4.0", NA, "2.0"),
    categories = c("", "", "m, f", ""),
    dimension2 = c("n_density", "", "", ""),
    lower2 = c("9 or more", NA, NA, NA), upper2 = c("100", NA, NA, NA),
    stringsAsFactors = FALSE)

  expect_warning(conds <- e$conditions_from_table(df), NA)
  expect_equal(conds, list(
    list(name = "a", define_by = list(frequency = c(5, 7))),
    list(name = "b", define_by = list(frequency = c(3, 4))),
    list(name = "c", define_by = list(gender = c("m", "f")))))
})

test_that("the parity claim under the exported code depends on the matching method", {
  e <- app_env()
  # mahalanobis and optimal use a covariance inverse and an assignment solver, so
  # the unqualified claim contradicted the method chooser's own help text and the
  # datasheet's 'Cross-engine determinism' line. Both wordings are pinned against
  # the Streamlit app's in tests/test_apps.py.
  deterministic <- paste0("The R and Python engines produce byte-identical stimuli and ",
                          "trial order from this configuration.")
  for (method in c("standardised_euclidean", "joint"))
    expect_equal(e$parity_claim(list(matching = list(method = method))), deterministic)
  expect_equal(e$parity_claim(list()), deterministic)
  for (method in c("mahalanobis", "optimal"))
    expect_match(e$parity_claim(list(matching = list(method = method))),
                 "not byte-identical stimuli", fixed = TRUE)
})

test_that("the realised-control chart draws one bar per comparison", {
  e <- app_env()
  # comparisons holds one row per non-anchor condition per dimension, and the plot
  # drew abs(cohens_d) named by dimension alone, so a 2x2 design repeated each
  # label three times with nothing saying which bar belonged to which condition.
  # Pinned identically in tests/test_apps.py.
  comp <- data.frame(condition = c("HF_smallN", "HF_smallN", "LF_largeN", "LF_largeN"),
                     reference = "HF_largeN",
                     dimension = c("length", "old20", "length", "old20"),
                     cohens_d = c(-0.627, -4.824, 0, -0.094), stringsAsFactors = FALSE)
  m <- e$control_chart(comp)
  expect_length(m, nrow(comp))
  expect_equal(rownames(m), c("HF_smallN", "LF_largeN"))
  expect_equal(colnames(m), c("length", "old20"))
  expect_equal(as.vector(m["HF_smallN", ]), c(0.627, 4.824))
  expect_equal(as.vector(m["LF_largeN", ]), c(0, 0.094))
  expect_match(e$control_caption(comp), "one bar per condition against the anchor HF_largeN",
               fixed = TRUE)

  # An undefined d, which the engine reports when two conditions are each constant
  # on a matched dimension at different constants, has to stay undefined: summing
  # the cells through xtabs wrote a 0 there, so the chart drew the bar of a
  # perfectly matched dimension. Pinned identically in tests/test_apps.py.
  comp$cohens_d[[2]] <- NA_real_
  m <- e$control_chart(comp)
  expect_true(is.na(m["HF_smallN", "old20"]))
  expect_equal(as.vector(m["LF_largeN", ]), c(0, 0.094))
})

test_that("staged_inputs places each input at the path the design names", {
  e <- app_env()
  # Keyed by the design's own path string, so an uploaded lexicon under corpora/
  # and an item table under items/ each reach the run at the path the exported
  # design records. Pinned identically in tests/test_apps.py.
  d <- list(lexicon = "corpora/mine.csv",
            items = list(source = "table", path = "items/pairs.csv"))
  expect_equal(e$staged_inputs(d, "/abs/mine.csv", "/abs/pairs.csv"),
               list("corpora/mine.csv" = "/abs/mine.csv", "items/pairs.csv" = "/abs/pairs.csv"))
  expect_length(e$staged_inputs(d, NULL, NULL), 0L)
  # Nothing to stage for a design that already names an absolute path.
  expect_length(e$staged_inputs(list(lexicon = "/elsewhere/mine.csv"), "/abs/mine.csv", NULL), 0L)
})

test_that("the datasheet records the design the bundle ships", {
  e <- app_env()
  skip_if_not_installed("DT")
  skip_if_not_installed("jsonlite")
  # The run used to rewrite the design's lexicon to an absolute path, so the
  # datasheet's design_sha256 identified a file that is in no bundle and the
  # 'Materials source' line named a directory on the machine that ran the app.
  # Pinned identically in tests/test_apps.py for the Streamlit app.
  lexicon <- NULL
  for (cand in c("corpora/derived/en.csv", "../../../corpora/derived/en.csv",
                 "../../../../corpora/derived/en.csv")) {
    if (file.exists(cand)) { lexicon <- normalizePath(cand); break }
  }
  if (is.null(lexicon)) skip("The bundled corpora are not in this tree.")
  e$CORPORA <- stats::setNames(lexicon, "en")
  shiny::testServer(e$server, {
    session$setInputs(paradigm = "Factorial word contrast (corpus matching)",
                      name = "my_design", language = "english", font = "Courier New",
                      corpus = "en", length = c(3L, 7L), frequency = c(3.5, 7.0),
                      n = 20, method = "standardised_euclidean", nsets = 0,
                      match_on = "length", lists = 1)
    session$setInputs(run = 1)
    b <- bundle()
    expect_null(b$error)
    base <- sub("_stimuli_R\\.csv$", "", basename(b$paths$stimuli))
    ds <- jsonlite::fromJSON(file.path(b$outdir, "reports", paste0(base, "_datasheet_R.json")))
    # The bytes the download handler writes into the archive.
    shipped <- tempfile(fileext = ".yaml")
    e$write_yaml_lf(b$design, shipped)
    expect_equal(ds$reproducibility$design_sha256,
                 digest::digest(file = shipped, algo = "sha256"))
    expect_equal(ds$materials_source$path, "corpora/derived/en.csv")
  })
})

test_that("a factorial run with nothing to match on is refused", {
  e <- app_env()
  skip_if_not_installed("DT")
  # The pipeline accepts match_on: [] happily, so emptying the chooser used to
  # report success over a set that was never matched on anything. The wording is
  # pinned against the Streamlit app's in tests/test_apps.py.
  e$CORPORA <- stats::setNames("nowhere/en.csv", "en")
  shiny::testServer(e$server, {
    session$setInputs(paradigm = "Factorial word contrast (corpus matching)",
                      name = "my_design", language = "english", font = "Courier New",
                      corpus = "en", length = c(3L, 7L), frequency = c(3.5, 7.0),
                      n = 80, method = "standardised_euclidean", nsets = 0,
                      match_on = character(0), lists = 1)
    session$setInputs(run = 1)
    expect_equal(bundle()$error, "Choose at least one dimension to match on.")
  })
})

test_that("with no corpora found the app says so and refuses the run", {
  e <- app_env()
  skip_if_not_installed("DT")
  # Launched from outside the checkout the lexicon chooser has nothing to offer.
  # Pressing Run used to reach CORPORA[[input$corpus]] on an empty vector, which
  # threw before the friendly guard below could be reached.
  e$CORPORA <- stats::setNames(character(0), character(0))
  shiny::testServer(e$server, {
    session$setInputs(paradigm = "Factorial word contrast (corpus matching)",
                      name = "my_design", language = "english", font = "Courier New",
                      length = c(3L, 7L), frequency = c(3.5, 7.0), n = 80,
                      method = "standardised_euclidean", nsets = 0,
                      match_on = "length", lists = 1)
    expect_match(as.character(output$design_ui$html),
                 "No bundled corpora were found", fixed = TRUE)
    session$setInputs(run = 1)
    expect_equal(bundle()$error, "Choose a lexicon first.")
  })
})

test_that("conditions can be added to and removed from the table", {
  e <- app_env()
  skip_if_not_installed("DT")
  # The table offered cell editing and nothing else, so a design needed exactly as
  # many conditions as the chosen preset supplies: a three-level factor or a fifth
  # 2x2 cell could not be built in the app at all. The Streamlit editor takes rows
  # through num_rows = "dynamic".
  shiny::testServer(e$server, {
    n <- nrow(conds())
    session$setInputs(cond_add = 1)
    expect_equal(nrow(conds()), n + 1L)
    expect_equal(conds()$name[n + 1L], "")
    # rbind must leave the optional second factor numeric, as every preset does.
    expect_type(conds()$lower2, "double")
    expect_type(conds()$upper2, "double")

    session$setInputs(cond_tbl_rows_selected = 1L)
    session$setInputs(cond_remove = 1)
    expect_equal(nrow(conds()), n)
    expect_equal(conds()$name[1], "low_frequency")
    # Renumbered, so a later cell edit reaches the row the client names.
    expect_equal(rownames(conds()), as.character(seq_len(n)))

    # Nothing selected removes nothing.
    session$setInputs(cond_tbl_rows_selected = integer(0))
    session$setInputs(cond_remove = 2)
    expect_equal(nrow(conds()), n)
  })
})

test_that("the matched dimensions are offered under their human labels", {
  e <- app_env()
  skip_if_not_installed("DT")
  # The app defines DIM_LABEL and used it only for the tolerance panel, so the
  # chooser named raw columns where the Streamlit multiselect names 'Neighbourhood
  # N' and 'Frequency (Zipf)', and the vignette described the Streamlit wording.
  shiny::testServer(e$server, {
    session$setInputs(paradigm = "Factorial word contrast (corpus matching)")
    # A chosen option carries a selected attribute; dropping it lets one pattern
    # cover the six.
    html <- gsub(" selected>", ">", as.character(output$design_ui$html), fixed = TRUE)
    for (d in e$DIMENSIONS)
      expect_match(html, sprintf('value="%s">%s<', d, e$DIM_LABEL[[d]]), fixed = TRUE)
  })
})

test_that("the chosen corpus and the bundled item table are previewed", {
  e <- app_env()
  skip_if_not_installed("DT")
  # The user committed to a run without seeing a row of the input, where the
  # Streamlit app shows the first rows beside the lexicon selector and under the
  # item-table notice.
  items_dir <- NULL
  for (cand in c("items", "../../../items", "../../../../items")) {
    if (dir.exists(cand)) { items_dir <- normalizePath(cand); break }
  }
  if (is.null(items_dir)) skip("The bundled item tables are not in this tree.")
  lexicon <- tempfile(fileext = ".csv")
  utils::write.csv(data.frame(word = letters[1:9], freq_zipf = seq(1, 9)),
                   lexicon, row.names = FALSE)
  expect_equal(nrow(e$preview_table(lexicon, 5)$x$data), 5L)
  expect_null(e$preview_table(file.path(items_dir, "no_such_table.csv"), 8))
  expect_null(e$preview_table(NULL, 8))

  e$CORPORA <- stats::setNames(lexicon, "toy")
  e$ITEMS_DIR <- items_dir
  shiny::testServer(e$server, {
    session$setInputs(paradigm = "Factorial word contrast (corpus matching)", corpus = "toy")
    expect_match(as.character(output$design_ui$html), "corpus_preview", fixed = TRUE)
    expect_match(as.character(output$corpus_preview), "freq_zipf", fixed = TRUE)

    session$setInputs(paradigm = "Priming (item table)")
    expect_match(as.character(output$design_ui$html), "items_preview", fixed = TRUE)
    expect_match(as.character(output$items_preview), "prime", fixed = TRUE)
  })
})

test_that("every paradigm the app offers runs to a bundle", {
  e <- app_env()
  skip_if_not_installed("DT")
  # The suite reached the helpers the export path is built from and nothing else,
  # so a paradigm branch that assembles a design the engine refuses would have
  # shown up only when someone opened the page. Each paradigm is run and asked for
  # its result, as tests/test_apps.py drives the Streamlit twin.
  repo <- NULL
  for (cand in c(".", "../../..", "../../../..")) {
    if (dir.exists(file.path(cand, "corpora/derived")) && dir.exists(file.path(cand, "items"))) {
      repo <- normalizePath(cand); break
    }
  }
  if (is.null(repo)) skip("The bundled corpora and item tables are not in this tree.")
  e$CORPORA <- stats::setNames(file.path(repo, "corpora/derived/en.csv"), "en")
  e$ITEMS_DIR <- file.path(repo, "items")

  for (label in names(e$PARADIGMS)) {
    shiny::testServer(e$server, {
      # Enough rows to matter and few enough to keep the sweep quick; the
      # item-table paradigms take their trials from the table and offer no such
      # field.
      session$setInputs(paradigm = label, name = "my_design", language = "english",
                        font = "Courier New", corpus = "en", length = c(3L, 7L),
                        frequency = c(3.5, 7.0), n = 8, method = "standardised_euclidean",
                        nsets = 0, match_on = "length", lists = 1,
                        gen_method = e$GENERATION_METHODS[[1]])
      session$setInputs(run = 1)
      b <- bundle()
      expect_null(b$error, label = label)
      expect_gt(nrow(b$stimuli), 0)
      # The results are on the page, not merely computed.
      expect_match(as.character(output$status$html), "Selected", fixed = TRUE)
      expect_match(as.character(output$results$html), "Realised control", fixed = TRUE)
    })
  }
})
