# Tests for the Shiny front-end in apps/r_shiny. The app is not part of the
# package, so these skip wherever it or its interface dependencies are absent
# (a package check run from a source tarball, for instance). The app is sourced,
# so it is taken only from the lexsync repository itself (see helper-repo.R).

app_env <- function() {
  skip_if_not_installed("shiny")
  skip_if_not_installed("bslib")
  skip_if_not_installed("DT")
  app <- repo_path("apps", "r_shiny", "app.R",
                   message = "The Shiny app source is not in this tree.")
  if (!file.exists(app)) skip("The Shiny app source is not in this tree.")
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

test_that("the bundle zip holds the run directory at its own relative paths", {
  e <- app_env()
  skip_if_not_installed("zip")
  # The bundle is the directory the run ran in, archived whole, so the exported code
  # finds the design, the schema and the outputs where it names them. The Streamlit
  # app's make_zip produces the same entries (test_apps.py).
  root <- tempfile("lexsync_zip_")
  dir.create(file.path(root, "config"), recursive = TRUE)
  dir.create(file.path(root, "output", "reports"), recursive = TRUE)
  writeLines("name: my_design", file.path(root, "my_design.yaml"))
  writeLines("seed: 1", file.path(root, "config", "schema.yaml"))
  writeLines("word\ncat", file.path(root, "output", "stimuli.csv"))
  writeLines("# datasheet", file.path(root, "output", "reports", "datasheet.md"))

  zf <- tempfile(fileext = ".zip")
  e$write_bundle_zip(zf, root)

  expect_equal(sort(zip::zip_list(zf)$filename),
               c("config/schema.yaml", "my_design.yaml", "output/reports/datasheet.md",
                 "output/stimuli.csv"))
})

test_that("the run directory is laid out like the bundle", {
  e <- app_env()
  # The design as displayed, the schema at config/schema.yaml and every input at the
  # path the design records, and nothing else. A bundled lexicon lives at a path that
  # resolves to nothing outside the checkout. Pinned identically in test_apps.py.
  src <- tempfile("lexsync_inputs_"); dir.create(src)
  lexicon <- file.path(src, "mine.csv")
  writeBin(charToRaw("word,freq_zipf\ncat,5.0\n"), lexicon)
  table <- file.path(src, "pairs.csv")
  writeBin(charToRaw("item,condition,prime,target\n1,rel,cat,dog\n"), table)
  design <- list(name = "my design (v2)", language = "english", lexicon = "corpora/mine.csv",
                 items = list(source = "table", path = "items/pairs.csv"))

  inputs <- e$staged_inputs(design, lexicon, table)
  expect_identical(inputs, list("corpora/mine.csv" = lexicon, "items/pairs.csv" = table))
  expect_identical(e$staged_inputs(list(name = "x"), NULL, NULL), list())

  root <- e$stage_run(design, "my design (v2).yaml", inputs)
  on.exit(unlink(root, recursive = TRUE), add = TRUE)
  expect_identical(sort(list.files(root, recursive = TRUE)),
                   c("config/schema.yaml", "corpora/mine.csv", "items/pairs.csv",
                     "my design (v2).yaml"))
  read <- function(rel) readBin(file.path(root, rel), "raw", file.info(file.path(root, rel))$size)
  # The file the pipeline hashes is the text the Reproducible code tab shows, with LF
  # endings on every platform.
  expect_identical(rawToChar(read("my design (v2).yaml")), e$clean_yaml(design))
  expect_identical(read("config/schema.yaml"),
                   readBin(e$SCHEMA_PATH, "raw", file.info(e$SCHEMA_PATH)$size))
  expect_identical(read("corpora/mine.csv"), readBin(lexicon, "raw", 100L))
  expect_identical(read("items/pairs.csv"), readBin(table, "raw", 100L))
})

# Paths that would put a file outside the run directory: the design's name reaches it.
# Pinned identically in test_apps.py.
ESCAPING <- c("../x.csv", "corpora/../../x.csv", "/x.csv", "\\x.csv", "C:/x.csv", "c:x.csv",
              "~/x.csv", "")

test_that("a path that leaves the run directory is refused", {
  e <- app_env()
  root <- tempfile("lexsync_root_")
  expect_identical(e$bundle_path(root, "corpora/derived/en.csv"),
                   file.path(root, "corpora/derived/en.csv"))
  for (rel in ESCAPING)
    expect_error(e$bundle_path(root, rel), "inside the bundle", label = rel)
  source <- tempfile(fileext = ".csv"); writeLines("word", source)
  before <- list.files(tempdir(), pattern = "^lexsync_app_")
  expect_error(e$stage_run(list(name = "x"), "x.yaml", list("../x.csv" = source)),
               "inside the bundle")
  expect_error(e$stage_run(list(name = "x"), "../x.yaml", list()), "inside the bundle")
  # A refused staging leaves no directory behind.
  expect_identical(setdiff(list.files(tempdir(), pattern = "^lexsync_app_"), before),
                   character(0))
})

# The downloads the Experiment scripts tab offers for a design with two lists, one per
# target, each with the files that target reads. Pinned identically in test_apps.py.
EXPERIMENT_FILES <- c("out/a_psychopy.py", "out/a_list1.osexp", "out/a_list2.osexp",
                      "out/a.html", "out/a_psychopy.csv", "out/a_list1_opensesame.csv",
                      "out/a_list1_opensesame_text.csv", "out/a_list2_opensesame.csv",
                      "out/a_list2_opensesame_text.csv")
EXPERIMENT_DOWNLOADS <- list(
  list(target = "PsychoPy", file_name = "a_psychopy.zip",
       files = c("out/a_psychopy.py", "out/a_psychopy.csv")),
  list(target = "OpenSesame", file_name = "a_opensesame.zip",
       files = c("out/a_list1.osexp", "out/a_list2.osexp", "out/a_list1_opensesame.csv",
                 "out/a_list1_opensesame_text.csv", "out/a_list2_opensesame.csv",
                 "out/a_list2_opensesame_text.csv")),
  list(target = "jsPsych", file_name = "a.html", files = "out/a.html"))

test_that("each experiment download carries the tables it loads", {
  e <- app_env()
  # The PsychoPy script loads its conditions file from its own folder and each
  # OpenSesame experiment its loop and text tables, but the tab offered each file on
  # its own, so a downloaded script could not run. The jsPsych page embeds its trials.
  expect_identical(e$experiment_downloads(EXPERIMENT_FILES, "a"), EXPERIMENT_DOWNLOADS)
  expect_identical(e$experiment_downloads(character(0), "a"), list())
})

# The notes on the Experiment scripts and Download tabs. Pinned identically in
# test_apps.py.
EXPERIMENT_NOTE <- paste0(
  "The same matched stimuli compile to three presentation targets. The PsychoPy ",
  "and OpenSesame downloads are archives that hold each experiment with the ",
  "tables it reads, so unzip one and run the experiment from that folder. The ",
  "jsPsych page holds its trials and runs on its own.")
DOWNLOAD_NOTE <- paste0(
  "The bundle is the folder the run ran in: the design, the schema at ",
  "config/schema.yaml, the lexicon or item table at the path the design names ",
  "and every output under output/. Running the exported code inside the unzipped ",
  "folder repeats the run.")

test_that("both apps word the download notes alike", {
  e <- app_env()
  expect_identical(e$EXPERIMENT_NOTE, EXPERIMENT_NOTE)
  expect_identical(e$DOWNLOAD_NOTE, DOWNLOAD_NOTE)
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
  expect_equal(sort(unname(e$PARADIGMS)),
               c("factorial", "lexical_decision", "priming", "self_paced_reading"))
})

test_that("the app offers exactly the pseudoword generators the engine implements", {
  e <- app_env()
  # The engine default first: the design only names a method when the other is
  # chosen. Pinned identically in tests/test_apps.py.
  expect_equal(e$GENERATION_METHODS, c("letter_substitution", "subsyllabic"))
})

test_that("the experiment tab offers every file the export wrote", {
  e <- app_env()
  # A design with several counterbalancing versions writes one OpenSesame experiment
  # per version, and each runs from its own tables, so the tab offers every file
  # export_experiments() lists, not only the three scripts. Pinned identically in
  # tests/test_apps.py.
  files <- c("a_psychopy.py", "a_list1.osexp", "a_list2.osexp", "a.html", "a_psychopy.csv")
  expect_identical(e$experiment_files(list(psychopy = files[1], opensesame = files[2],
                                           jspsych = files[4], files = files)), files)
  # A result without `files`, from an older lexsync, still offers its three scripts.
  expect_identical(e$experiment_files(list(psychopy = "a.py", opensesame = "a.osexp",
                                           jspsych = "a.html")),
                   c("a.py", "a.osexp", "a.html"))
  expect_identical(e$experiment_files(list()), character(0))
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

test_that("a conditions-table edit changes only the edited column", {
  e <- app_env()
  # DataTables numbers the displayed columns from 0, and the table is rendered
  # without row names, so column 0 is 'name'. DT::editData() assumes a row-name
  # column unless told otherwise, so it wrote every edit one column to the left.
  # An edit to 'name' renamed the row, an edit to 'upper' moved 'lower' and no
  # edit could reach 'upper2'. The first row of each preset is edited once per
  # column, with text that the row does not already hold.
  typed <- c(name = "edited", dimension = "old20", lower = "1.5", upper = "2.5",
             categories = "masc, fem", dimension2 = "old20", lower2 = "1.5",
             upper2 = "2.5")
  bounds <- c("lower", "upper", "lower2", "upper2")
  for (preset in c("High vs low frequency", "Dense vs sparse neighbourhood",
                   "2x2 frequency x neighbourhood", "Custom")) {
    before <- e$preset_df(preset)
    expect_identical(names(before), names(typed))
    shiny::testServer(e$server, {
      for (j in seq_along(typed)) {
        conds(before)
        column <- names(typed)[[j]]
        what <- sprintf("the '%s' table after an edit to '%s'", preset, column)
        # DT's cell_edit input: the 1-based row, the 0-based displayed column and
        # the text typed. DT warns when it cannot keep a column's type.
        edit <- data.frame(row = 1L, col = j - 1L, value = typed[[j]],
                           stringsAsFactors = FALSE)
        expect_no_warning(session$setInputs(cond_tbl_cell_edit = edit))
        after <- conds()
        changed <- names(before)[!mapply(identical, before, after)]
        expect_identical(changed, column, label = paste("the columns changed in", what))
        # A bound is a number, including a bound of the second factor that a
        # one-factor preset leaves empty.
        expected <- before
        expected[1, j] <- if (column %in% bounds) as.numeric(typed[[j]]) else typed[[j]]
        expect_equal(after, expected, label = what)
      }
    })
  }
})

# The two captions under the exported code. Which one a run shows is read from its
# datasheet's selection$cross_engine. Pinned identically in tests/test_apps.py.
BYTE_IDENTICAL <- paste0("The R and Python engines select byte-identical stimuli and trial ",
                         "order from this configuration.")
APPROXIMATE <- paste0("The R and Python engines select equivalent but not byte-identical ",
                      "stimuli for this matching method.")

test_that("the parity claim follows the run datasheet", {
  e <- app_env()
  # The caption used to claim byte identity whatever the method, although
  # mahalanobis and optimal agree only approximately and the run's own datasheet
  # says so.
  record <- function(cross) list(selection = list(cross_engine = cross))
  expect_identical(e$parity_claim(record("byte-identical")), BYTE_IDENTICAL)
  expect_identical(e$parity_claim(record("approximate (platform linear algebra)")),
                   APPROXIMATE)
  # An item-table design selects nothing, and both engines write the same files.
  expect_identical(e$parity_claim(record("n/a (user-supplied items)")), BYTE_IDENTICAL)
  # The datasheet's own renderer reads a missing field as byte-identical.
  expect_identical(e$parity_claim(list()), BYTE_IDENTICAL)
  expect_identical(e$parity_claim(NULL), BYTE_IDENTICAL)
})

test_that("the interval label follows the datasheet alpha", {
  e <- app_env()
  # Cohen's d carries the 1 - 2 alpha interval that goes with the TOST, and the
  # column was headed 90% whatever the schema's alpha.
  record <- function(alpha) list(equivalence = list(bound_d = 0.5, alpha = alpha))
  expect_identical(e$interval_label(record(0.05)), "90% CI")
  expect_identical(e$interval_label(record(0.025)), "95% CI")
  expect_identical(e$interval_label(record(0.005)), "99% CI")
  expect_identical(e$interval_label(record(0.1)), "80% CI")
  # A record without the field was written at the default alpha.
  expect_identical(e$interval_label(list()), "90% CI")
  expect_identical(e$interval_label(NULL), "90% CI")
})

# The repository root, for the tests that run the app over its bundled corpora.
app_repo <- function() {
  repo <- repo_path(message = "The bundled corpora are not in this tree.")
  if (!file.exists(file.path(repo, "corpora", "derived", "en_v2.csv")))
    skip("The bundled corpora are not in this tree.")
  repo
}

factorial_inputs <- function(session, ...) {
  inputs <- utils::modifyList(
    list(paradigm = "Factorial word contrast (corpus matching)", name = "my_design",
         language = "english", font = "Courier New", corpus = "en_v2",
         length = c(3L, 7L), frequency = c(3.5, 7.0), n = 10,
         method = "standardised_euclidean", nsets = 0,
         match_on = c("length", "old20"), lists = 1),
    list(...))
  do.call(session$setInputs, inputs)
}

test_that("the caption and the interval label come from the run datasheet", {
  e <- app_env()
  repo <- app_repo()
  # End to end: a Mahalanobis run records an approximate cross-engine agreement,
  # and the caption under its exported code says so. Pinned identically in
  # tests/test_apps.py for the Streamlit app.
  e$CORPORA <- stats::setNames(file.path(repo, "corpora", "derived", "en_v2.csv"), "en_v2")
  shiny::testServer(e$server, {
    factorial_inputs(session, method = "mahalanobis")
    session$setInputs(run = 1)
    b <- bundle()
    expect_null(b$error)
    expect_match(b$record$selection$cross_engine, "^approximate")
    expect_identical(e$parity_claim(b$record), APPROXIMATE)
    expect_identical(e$interval_label(b$record), "90% CI")
    expect_match(as.character(output$code_ui$html), APPROXIMATE, fixed = TRUE)
  })
})

sha256_of <- function(path) digest::digest(file = path, algo = "sha256")

# Runs `code` with `dir` as the working directory, and puts the old one back.
in_dir <- function(dir, code) {
  old <- setwd(dir)
  on.exit(setwd(old))
  force(code)
}

test_that("the download bundle reproduces its own record", {
  e <- app_env()
  skip_if_not_installed("zip")
  repo <- app_repo()
  # The app ran a temporary copy of the design with absolute paths and then bundled
  # the displayed design, so the bundled datasheet's design checksum matched no file
  # in the bundle, and the datasheet and run logs named the user's home and temporary
  # directories. Pinned identically in test_apps.py.
  e$CORPORA <- stats::setNames(file.path(repo, "corpora", "derived", "en_v2.csv"), "en_v2")
  shiny::testServer(e$server, {
    factorial_inputs(session)
    session$setInputs(run = 1)
    b <- bundle()
    expect_null(b$error)
    base <- sub("_stimuli_R\\.csv$", "", basename(b$paths$stimuli))
    unzipped <- tempfile("lexsync_unzipped_")
    zip::unzip(output$dl_zip, exdir = unzipped)
    on.exit(unlink(unzipped, recursive = TRUE), add = TRUE)
    at <- function(...) file.path(unzipped, ...)
    reports <- at("output", "reports")

    # The checksums name the files the bundle holds.
    record <- jsonlite::read_json(file.path(reports, paste0(base, "_datasheet_R.json")))
    expect_identical(record$reproducibility$design_sha256, sha256_of(at("my_design.yaml")))
    expect_identical(record$reproducibility$schema_path, "config/schema.yaml")
    expect_identical(record$reproducibility$schema_sha256, sha256_of(at("config", "schema.yaml")))
    expect_identical(record$materials_source$path, "corpora/derived/en_v2.csv")
    expect_identical(record$materials_source$sha256, sha256_of(at("corpora", "derived", "en_v2.csv")))
    expect_identical(record$items$stimuli_file, paste0("output/stimuli/", base, "_stimuli_R.csv"))
    files <- vapply(record$artifacts, function(a) a$file, character(1))
    expect_true(length(files) > 0 && all(startsWith(files, "output/")))
    for (a in record$artifacts) expect_identical(a$sha256, sha256_of(at(a$file)), label = a$file)

    # No path in the datasheet or the run logs is absolute.
    absolute <- "^([A-Za-z]:[\\\\/]|[\\\\/]|~)"
    strings <- function(x) as.character(unlist(x, use.names = FALSE))
    expect_identical(grep(absolute, strings(record), value = TRUE), character(0))
    log_lines <- readLines(file.path(reports, paste0(base, "_run_log_R.jsonl")), encoding = "UTF-8")
    for (line in log_lines)
      expect_identical(grep(absolute, strings(jsonlite::parse_json(line)), value = TRUE),
                       character(0))
    places <- c(b$root, tempdir(), path.expand("~"), repo)
    needles <- unique(c(places, gsub("\\", "/", places, fixed = TRUE),
                        normalizePath(places, winslash = "/", mustWork = FALSE)))
    # A home directory of "/" would match every path, so a lone separator is dropped.
    needles <- needles[nchar(needles) > 1L]
    for (name in paste0(base, c("_datasheet_R.json", "_datasheet_R.md", "_run_log_R.md",
                                "_run_log_R.jsonl"))) {
      text <- paste(readLines(file.path(reports, name), encoding = "UTF-8"), collapse = "\n")
      expect_identical(needles[vapply(needles, grepl, logical(1), x = text, fixed = TRUE)],
                       character(0), label = name)
    }

    # Running the exported R code from the unzipped bundle rewrites every output with
    # the same bytes. The run logs record the time of the run, so they differ.
    outputs <- function() {
      rel <- sort(list.files(at("output"), recursive = TRUE))
      rel <- rel[!grepl("_run_log_", rel, fixed = TRUE)]
      stats::setNames(lapply(rel, function(p) readBin(at("output", p), "raw",
                                                      file.info(at("output", p))$size)), rel)
    }
    shipped <- outputs()
    code <- e$reproduction_code(b$design, b$cfg)$r
    in_dir(unzipped, utils::capture.output(eval(parse(text = code), envir = new.env())))
    rerun <- outputs()
    expect_identical(names(rerun), names(shipped))
    expect_identical(names(shipped)[!mapply(identical, shipped, rerun[names(shipped)])],
                     character(0))

    # The PsychoPy and OpenSesame downloads hold the tables those experiments load.
    expect_identical(sort(zip::zip_list(output$dl_exp_psychopy)$filename),
                     paste0(base, c("_psychopy.csv", "_psychopy.py")))
    expect_identical(sort(zip::zip_list(output$dl_exp_opensesame)$filename),
                     paste0(base, c(".osexp", "_opensesame.csv", "_opensesame_text.csv")))
    page <- at("output", "experiments", paste0(base, ".html"))
    expect_identical(unname(tools::md5sum(output$dl_exp_jspsych)), unname(tools::md5sum(page)))
    expect_match(as.character(output$exp_ui$html), EXPERIMENT_NOTE, fixed = TRUE)
    expect_match(as.character(output$results$html), DOWNLOAD_NOTE, fixed = TRUE)
  })
})

test_that("a new run discards the previous run directory", {
  e <- app_env()
  repo <- app_repo()
  # Every run leaves a directory holding a copy of its inputs and every output, and a
  # long-lived app kept one per press of Run. Only the run on screen is read from.
  e$CORPORA <- stats::setNames(file.path(repo, "corpora", "derived", "en_v2.csv"), "en_v2")
  shiny::testServer(e$server, {
    factorial_inputs(session)
    session$setInputs(run = 1)
    first <- bundle()$root
    expect_true(dir.exists(first))
    session$setInputs(run = 2)
    second <- bundle()$root
    expect_false(identical(first, second))
    expect_false(dir.exists(first))
    expect_true(dir.exists(second))
    # A refused run takes the results off the screen, and their directory with them.
    factorial_inputs(session, match_on = character(0))
    session$setInputs(run = 3)
    expect_identical(bundle()$error, e$EMPTY_MATCH_ON)
    expect_false(dir.exists(second))
  })
})

# Each preset's rows (name, dimension, lower, upper, categories, dimension2, lower2,
# upper2; NA is an empty bound), its matched dimensions and its method, as the
# repository's design files match such contrasts. Pinned identically in
# tests/test_apps.py.
PRESETS <- list(
  "High vs low frequency" = list(
    rows = list(list("high_frequency", "frequency", 5.2, 7.0, "", "", NA_real_, NA_real_),
                list("low_frequency", "frequency", 3.8, 4.4, "", "", NA_real_, NA_real_)),
    match_on = c("length", "n_density", "old20"), method = "standardised_euclidean"),
  "Dense vs sparse neighbourhood" = list(
    rows = list(list("dense_neighbourhood", "n_density", 5.0, 100.0, "", "", NA_real_, NA_real_),
                list("sparse_neighbourhood", "n_density", 0.0, 1.0, "", "", NA_real_, NA_real_)),
    match_on = c("length", "frequency"), method = "joint"),
  "2x2 frequency x neighbourhood" = list(
    rows = list(list("HF_largeN", "frequency", 5.0, 7.0, "", "n_density", 9.0, 100.0),
                list("HF_smallN", "frequency", 5.0, 7.0, "", "n_density", 0.0, 5.0),
                list("LF_largeN", "frequency", 2.5, 4.2, "", "n_density", 9.0, 100.0),
                list("LF_smallN", "frequency", 2.5, 4.2, "", "n_density", 0.0, 5.0)),
    match_on = "length", method = "standardised_euclidean"),
  "Custom" = list(
    rows = list(list("condition_a", "frequency", 5.0, 7.0, "", "", NA_real_, NA_real_),
                list("condition_b", "frequency", 3.5, 4.5, "", "", NA_real_, NA_real_)),
    match_on = "length", method = "standardised_euclidean")
)

test_that("both apps pin the same presets", {
  e <- app_env()
  # The presets filled the conditions table and left 'Match on' and the method at
  # their general defaults, so the neighbourhood preset matched on N and OLD20 and
  # left length unequated, while the Streamlit preset of the same name matched on
  # length and frequency.
  expect_identical(names(e$PRESET_MATCHING), names(PRESETS))
  for (preset in names(PRESETS)) {
    df <- e$preset_df(preset)
    rows <- lapply(seq_len(nrow(df)), function(i) unname(as.list(df[i, ])))
    expect_identical(rows, PRESETS[[preset]]$rows, label = preset)
    expect_identical(e$PRESET_MATCHING[[preset]]$match_on, PRESETS[[preset]]$match_on)
    expect_identical(e$PRESET_MATCHING[[preset]]$method, PRESETS[[preset]]$method)
  }
})

test_that("no preset matches on a dimension it manipulates", {
  e <- app_env()
  for (preset in names(PRESETS)) {
    conditions <- e$conditions_from_table(e$preset_df(preset))
    expect_length(conditions, length(PRESETS[[preset]]$rows))
    expect_length(e$manipulated_matches(conditions, PRESETS[[preset]]$match_on), 0L)
  }
})

test_that("a preset sets the matched dimensions and the method", {
  e <- app_env()
  sent <- new.env()
  e$updateSelectizeInput <- function(session, inputId, ..., selected) sent[[inputId]] <- selected
  e$updateSelectInput <- function(session, inputId, ..., selected) sent[[inputId]] <- selected
  shiny::testServer(e$server, {
    # The chooser opens on the first preset, and the observer ignores that first
    # value, so the walk goes back up the list and changes it every time.
    session$setInputs(preset = names(PRESETS)[[1]])
    for (preset in rev(names(PRESETS))) {
      session$setInputs(preset = preset)
      expect_identical(sent$match_on, PRESETS[[preset]]$match_on, label = preset)
      expect_identical(sent$method, PRESETS[[preset]]$method, label = preset)
      expect_identical(nrow(conds()), length(PRESETS[[preset]]$rows))
    }
  })
})

test_that("manipulated_matches names the dimensions whose windows differ", {
  e <- app_env()
  # A matched dimension that defines the conditions with different windows works
  # against the contrast. A band every condition shares restricts the pool and is
  # legitimate. Pinned identically in tests/test_apps.py.
  freq <- list(list(name = "high", define_by = list(frequency = c(5.2, 7.0))),
               list(name = "low", define_by = list(frequency = c(3.8, 4.4))))
  expect_identical(e$manipulated_matches(freq, c("length", "frequency")), "frequency")
  expect_identical(e$manipulated_matches(freq, c("length", "old20")), character(0))
  expect_identical(e$manipulated_matches(freq, character(0)), character(0))
  shared <- list(
    list(name = "dense", define_by = list(frequency = c(4.0, 6.0), n_density = c(5.0, 100.0))),
    list(name = "sparse", define_by = list(frequency = c(4.0, 6.0), n_density = c(0.0, 1.0))))
  expect_identical(e$manipulated_matches(shared, c("frequency", "n_density", "length")),
                   "n_density")
  # A window on one condition alone leaves the others unrestricted on it.
  one_sided <- list(
    list(name = "a", define_by = list(frequency = c(5.0, 7.0), length = c(3.0, 5.0))),
    list(name = "b", define_by = list(frequency = c(3.0, 4.0))))
  expect_identical(e$manipulated_matches(one_sided, c("old20", "length")), "length")
  expect_identical(e$manipulated_matches(list(), "length"), character(0))

  expect_null(e$manipulation_warning(character(0)))
  expect_identical(e$manipulation_warning("frequency"), paste0(
    "'Match on' includes frequency, on which the conditions take different windows. ",
    "Matching on a dimension the conditions manipulate works against the contrast ",
    "they define."))
  expect_match(e$manipulation_warning(c("frequency", "n_density", "old20")),
               "^'Match on' includes frequency, n_density and old20, on which")
})

# The sentence that keeps Run disabled while 'Match on' is empty, and the Streamlit
# method help, which the Shiny selector now shows too. Pinned identically in
# tests/test_apps.py.
EMPTY_MATCH_ON <- "Choose at least one dimension to match on."
METHOD_HELP <- paste0(
  "joint/optimal pair two conditions (optimal selects the n pairs of ",
  "least summed distance, joint takes the closest pair at each step); ",
  "mahalanobis down-weights correlated dimensions. mahalanobis and ",
  "optimal use a covariance inverse / assignment solver, so the R and ",
  "Python engines agree closely but not byte-for-byte on them.")

test_that("the method selector carries the Streamlit help", {
  e <- app_env()
  expect_identical(e$METHOD_HELP, METHOD_HELP)
  shiny::testServer(e$server, {
    session$setInputs(paradigm = "Factorial word contrast (corpus matching)")
    expect_match(as.character(output$design_ui$html), METHOD_HELP, fixed = TRUE)
  })
})

test_that("an empty Match on disables Run, and a manipulated one draws a warning", {
  e <- app_env()
  # Emptying 'Match on' used to run and report success over a set matched on
  # nothing.
  e$CORPORA <- stats::setNames("nowhere/en_v2.csv", "en_v2")
  sent <- new.env()
  e$updateActionButton <- function(session, inputId, ..., disabled = NULL)
    sent[[inputId]] <- disabled
  expect_identical(e$EMPTY_MATCH_ON, EMPTY_MATCH_ON)
  shiny::testServer(e$server, {
    factorial_inputs(session, match_on = c("length", "old20"))
    expect_false(sent$run)
    expect_null(output$match_on_notes$html)

    factorial_inputs(session, match_on = c("length", "frequency"))
    expect_false(sent$run)
    expect_match(as.character(output$match_on_notes$html),
                 e$manipulation_warning("frequency"), fixed = TRUE)

    factorial_inputs(session, match_on = character(0))
    expect_true(sent$run)
    expect_match(as.character(output$match_on_notes$html), EMPTY_MATCH_ON, fixed = TRUE)
    # Refused on the server too, for a Shiny whose buttons cannot be disabled.
    session$setInputs(run = 1)
    expect_identical(bundle()$error, EMPTY_MATCH_ON)
  })
})

# The command lines under 'Reproducible code' for a design named "my design (v2)".
# Double quotes outside and single quotes inside run in bash, cmd.exe, Windows
# PowerShell and PowerShell 7, and clean_meta() refuses every character that would
# end such a string. Each comment has a line of its own, because cmd.exe reads a
# trailing # as one more argument. Pinned identically in tests/test_apps.py.
CLI <- paste0(
  "# R\n",
  "Rscript -e \"lexsync::run_pipeline('my design (v2).yaml', ",
  "schema_path = 'config/schema.yaml', outdir = 'output')\"\n",
  "# Python console script\n",
  "lexsync run \"my design (v2).yaml\"\n",
  "# Python (module form)\n",
  "python -m lexsync run \"my design (v2).yaml\"")

test_that("the command lines quote the design file and name the output", {
  e <- app_env()
  # The R line was quoted with single quotes outside, which cmd.exe and Windows
  # PowerShell break, and the Python lines left the file name unquoted.
  cli <- e$reproduction_code(list(name = "my design (v2)"), "my design (v2).yaml")$cli
  expect_identical(cli, CLI)
  r_line <- strsplit(cli, "\n", fixed = TRUE)[[1]][[2]]
  expr <- sub('^Rscript -e "(.*)"$', "\\1", r_line)
  call <- parse(text = expr)[[1]]
  expect_identical(deparse(call[[1]]), "lexsync::run_pipeline")
  expect_identical(call[[2]], "my design (v2).yaml")
  expect_identical(call$schema_path, "config/schema.yaml")
  expect_identical(call$outdir, "output")
})

# The lexicon both apps open on. Pinned identically in tests/test_apps.py.
DEFAULT_LEXICON <- "en_v2"

test_that("the pool filters screen marked forms when the lexicon marks them", {
  e <- app_env()
  # en_v2 marks the forms its SUBTLEX-US screen flags, and the shipped English
  # designs keep only the unmarked ones with nonstandard: [0, 0]. The apps offered
  # the unscreened en.csv first and no way to apply the screen. Pinned identically
  # in tests/test_apps.py.
  expect_identical(e$DEFAULT_LEXICON, DEFAULT_LEXICON)
  marked <- c("word", "freq_zipf", "nonstandard")
  expect_identical(e$pool_filters(c(3L, 7L), c(3.5, 7.0), marked, TRUE),
                   list(length = c(3L, 7L), frequency = c(3.5, 7.0), nonstandard = c(0L, 0L)))
  expect_identical(e$pool_filters(c(3L, 7L), c(3.5, 7.0), marked, FALSE),
                   list(length = c(3L, 7L), frequency = c(3.5, 7.0)))
  expect_identical(e$pool_filters(c(3L, 7L), c(3.5, 7.0), c("word", "freq_zipf"), TRUE),
                   list(length = c(3L, 7L), frequency = c(3.5, 7.0)))
})

test_that("the app opens on the screened lexicon", {
  e <- app_env()
  repo <- app_repo()
  lexica <- file.path(repo, "corpora", "derived", c("en.csv", "en_v2.csv"))
  e$CORPORA <- stats::setNames(lexica, c("en", "en_v2"))
  expect_true("nonstandard" %in% e$lexicon_columns(lexica[[2]]))
  expect_false("nonstandard" %in% e$lexicon_columns(lexica[[1]]))
  shiny::testServer(e$server, {
    session$setInputs(paradigm = "Factorial word contrast (corpus matching)")
    expect_match(as.character(output$design_ui$html),
                 '<option value="en_v2" selected>', fixed = TRUE)
    factorial_inputs(session)
    expect_match(as.character(output$screen_ui$html), "Screened forms only", fixed = TRUE)
    expect_identical(build_design()$design$pool_filters$nonstandard, c(0L, 0L))
    session$setInputs(screened = FALSE)
    expect_null(build_design()$design$pool_filters$nonstandard)
    factorial_inputs(session, corpus = "en")
    expect_null(output$screen_ui$html)
    expect_null(build_design()$design$pool_filters$nonstandard)
  })
})
