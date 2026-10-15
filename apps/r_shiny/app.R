# lexsync web application (R / Shiny).
#
# A browser front-end for the lexsync R package. The user assembles a design
# through the interface; the app writes the corresponding design configuration,
# runs the same verified pipeline that the package and command line use, displays
# the matched stimuli, the realised-control report and the materials datasheet, and
# exports the reproducible R, Python and command-line code that performs the
# identical operation. The application is a front-end only: every result it shows is
# produced by the installed lexsync package, and the design it builds is an ordinary
# YAML configuration file.
#
# Run from the repository root:
#   Rscript -e "shiny::runApp('apps/r_shiny', port = 8502, host = '127.0.0.1')"

library(shiny)
library(bslib)
library(DT)
library(lexsync)

DIMENSIONS <- c("length", "frequency", "n_density", "old20", "n_syllables", "bigram_freq")
# The engine's pseudoword generators (items.generation.method). The first is the
# engine default, so the design only names a method when the other is chosen.
GENERATION_METHODS <- c("letter_substitution", "subsyllabic")
DIM_LABEL <- c(length = "Length", frequency = "Frequency (Zipf)", n_density = "Neighbourhood N",
               old20 = "OLD20", n_syllables = "Syllables", bigram_freq = "Bigram frequency")
PARADIGMS <- c(
  "Factorial word contrast (corpus matching)" = "factorial",
  "Lexical decision (generated pseudowords)" = "lexical_decision",
  "Priming (item table)" = "priming",
  "Self-paced reading (item table)" = "self_paced_reading"
)
# The lexicon the app opens on: English screened against SUBTLEX-US, the lexicon the
# shipped English designs use. The Streamlit app opens on the same one.
DEFAULT_LEXICON <- "en_v2"
SCREEN_HELP <- paste0(
  "Adds nonstandard: [0, 0] to the pool filters, which keeps only the forms ",
  "the lexicon leaves unmarked. In en_v2, a form is marked when SUBTLEX-US ",
  "lacks it or when under a tenth of its uses begin with a lower-case letter.")
# Each preset's matched dimensions and matching method, as the repository's design
# files match such contrasts (design_en_freqcontrast.yaml, design_en_ndensity.yaml,
# design_en_andrews_repro.yaml). A preset never matches on a dimension it
# manipulates. The Streamlit app's PRESET_MATCHING holds the same table, and
# tests/test_apps.py and test-apps.R pin both.
PRESET_MATCHING <- list(
  "High vs low frequency" = list(match_on = c("length", "n_density", "old20"),
                                 method = "standardised_euclidean"),
  "Dense vs sparse neighbourhood" = list(match_on = c("length", "frequency"),
                                         method = "joint"),
  "2x2 frequency x neighbourhood" = list(match_on = "length",
                                         method = "standardised_euclidean"),
  "Custom" = list(match_on = "length", method = "standardised_euclidean")
)
# The preset the chooser opens on, and so the one the matching controls start from.
DEFAULT_PRESET <- names(PRESET_MATCHING)[[1]]
METHOD_HELP <- paste0(
  "joint/optimal pair two conditions (optimal selects the n pairs of ",
  "least summed distance, joint takes the closest pair at each step); ",
  "mahalanobis down-weights correlated dimensions. mahalanobis and ",
  "optimal use a covariance inverse / assignment solver, so the R and ",
  "Python engines agree closely but not byte-for-byte on them.")
EMPTY_MATCH_ON <- "Choose at least one dimension to match on."
# The caption under the exported code, chosen by the run's datasheet. Word-identical
# to the Streamlit app's.
BYTE_IDENTICAL <- paste0("The R and Python engines select byte-identical stimuli and trial ",
                         "order from this configuration.")
APPROXIMATE <- paste0("The R and Python engines select equivalent but not byte-identical ",
                      "stimuli for this matching method.")

find_repo_root <- function() {
  here <- normalizePath(getwd(), winslash = "/", mustWork = FALSE)
  for (cand in c(here, dirname(here), dirname(dirname(here)))) {
    if (dir.exists(file.path(cand, "corpora", "derived"))) return(cand)
  }
  here
}
REPO_ROOT <- find_repo_root()
CORPORA_DIR <- file.path(REPO_ROOT, "corpora", "derived")
ITEMS_DIR <- file.path(REPO_ROOT, "items")
SCHEMA_PATH <- system.file("extdata", "schema.yaml", package = "lexsync")

list_corpora <- function() {
  if (!dir.exists(CORPORA_DIR)) return(character(0))
  f <- list.files(CORPORA_DIR, pattern = "\\.csv$")
  stats::setNames(file.path(CORPORA_DIR, f), sub("\\.csv$", "", f))
}
CORPORA <- list_corpora()

#' The column names of a lexicon CSV
#'
#' @param path Path of the lexicon, or NULL.
#' @return A character vector, empty when there is no file to read.
lexicon_columns <- function(path) {
  if (is.null(path) || !length(path) || !file.exists(path)) return(character(0))
  tryCatch(names(utils::read.csv(path, nrows = 1, check.names = FALSE)),
           error = function(e) character(0))
}

#' The design's pool filters from the two sliders and the screen checkbox
#'
#' A lexicon with a `nonstandard` column marks the forms its screen flags, and
#' `nonstandard: [0, 0]` keeps only the unmarked ones, as the shipped English designs
#' do. Mirrors pool_filters() in the Streamlit app.
#'
#' @param length_range,frequency_range The two ends of each slider.
#' @param columns The chosen lexicon's column names.
#' @param screened Whether 'Screened forms only' is ticked.
#' @return The `pool_filters` list.
pool_filters <- function(length_range, frequency_range, columns, screened) {
  filters <- list(length = as.integer(length_range), frequency = frequency_range)
  if (isTRUE(screened) && "nonstandard" %in% columns) filters$nonstandard <- c(0L, 0L)
  filters
}

#' A preset's matched dimensions and method, the Custom ones for any other name
#'
#' @param preset A preset name.
#' @return A list with `match_on` and `method`.
preset_matching <- function(preset) {
  m <- if (is.character(preset) && length(preset) == 1L) PRESET_MATCHING[[preset]]
  if (is.null(m)) PRESET_MATCHING[["Custom"]] else m
}

preset_df <- function(preset) {
  blank <- function() data.frame(
    name = character(), dimension = character(), lower = numeric(), upper = numeric(),
    categories = character(), dimension2 = character(), lower2 = numeric(), upper2 = numeric(),
    stringsAsFactors = FALSE)
  # The second factor's bounds default to a numeric NA. DT::editData() keeps a
  # column's type only for types it knows, and on a logical column it warns and
  # stores the typed text, which turns the whole column into character.
  r <- function(name, dim, lo, hi, cats = "", dim2 = "", lo2 = NA_real_, hi2 = NA_real_)
    data.frame(name = name, dimension = dim, lower = lo, upper = hi, categories = cats,
               dimension2 = dim2, lower2 = lo2, upper2 = hi2, stringsAsFactors = FALSE)
  switch(preset,
    "High vs low frequency" = rbind(blank(),
      r("high_frequency", "frequency", 5.2, 7.0),
      r("low_frequency", "frequency", 3.8, 4.4)),
    "Dense vs sparse neighbourhood" = rbind(blank(),
      r("dense_neighbourhood", "n_density", 5, 100),
      r("sparse_neighbourhood", "n_density", 0, 1)),
    "2x2 frequency x neighbourhood" = rbind(blank(),
      r("HF_largeN", "frequency", 5.0, 7.0, "", "n_density", 9, 100),
      r("HF_smallN", "frequency", 5.0, 7.0, "", "n_density", 0, 5),
      r("LF_largeN", "frequency", 2.5, 4.2, "", "n_density", 9, 100),
      r("LF_smallN", "frequency", 2.5, 4.2, "", "n_density", 0, 5)),
    rbind(blank(),
      r("condition_a", "frequency", 5.0, 7.0),
      r("condition_b", "frequency", 3.5, 4.5)))
}

clean_yaml <- function(design) yaml::as.yaml(design, indent = 2)

#' Write a design as YAML with LF line endings on every platform
#'
#' yaml::write_yaml and writeLines both open text-mode connections, which on
#' Windows turn every newline into CRLF. The pipeline hashes the design file it
#' ran into the datasheet's design_sha256, so its bytes must depend on the
#' content alone, never on the operating system; a binary connection writes the
#' string as given. The Streamlit app pins the same convention with
#' newline="\\n".
#'
#' @param x The design list to serialise.
#' @param path Output path.
#' @return `path`, invisibly.
write_yaml_lf <- function(x, path) {
  con <- file(path, open = "wb")
  on.exit(close(con))
  writeLines(sub("\n$", "", enc2utf8(clean_yaml(x))), con, sep = "\n", useBytes = TRUE)
  invisible(path)
}

#' Keep the dimensions the user gave a positive tolerance k
#'
#' A k of zero means "leave the schema default for this dimension alone". Carried
#' into the design it would instead pin the pre-filter window to zero width and
#' admit no candidate at all, so it is dropped here rather than written out.
#'
#' @param values Named list of dimension -> k, in the order the dimensions are matched on.
#' @return The subset with k > 0, order preserved.
positive_tolerances <- function(values)
  Filter(function(k) length(k) == 1L && !is.na(k) && k > 0, values)

#' Every experiment file a run wrote, for the Experiment tab
#'
#' A design with several counterbalancing versions writes one OpenSesame experiment
#' per version, each with its own tables, and export_experiments() lists them all
#' under `files`. A result without `files`, from an older lexsync, offers its three
#' scripts. Mirrors experiment_files() in the Streamlit app.
#'
#' @param experiments The `experiments` element of run_pipeline()'s result.
#' @return A character vector of paths, in the order the export wrote them.
experiment_files <- function(experiments) {
  if (!is.null(experiments[["files"]])) return(as.character(experiments[["files"]]))
  paths <- lapply(c("psychopy", "opensesame", "jspsych"), function(k) experiments[[k]])
  as.character(unlist(paths, use.names = FALSE))
}

#' Map each repository-bundled input the design names to its source file
#'
#' A design built from a bundled corpus or example item table records the
#' repository-relative path (corpora/derived/<x>.csv, items/<x>.csv). Outside the
#' repository that path resolves to nothing, so the export carries the file at
#' exactly the path the design records.
#'
#' @param design The design as shown to the user, carrying repository-relative paths.
#' @return Named list: design-relative path -> absolute path under the repository root.
bundled_inputs <- function(design) {
  out <- list()
  lexicon <- design$lexicon
  if (is.character(lexicon) && length(lexicon) == 1L && startsWith(lexicon, "corpora/derived/")) {
    full <- file.path(REPO_ROOT, lexicon)
    if (file.exists(full)) out[[lexicon]] <- full
  }
  items_path <- design$items$path
  if (is.character(items_path) && length(items_path) == 1L && startsWith(items_path, "items/")) {
    full <- file.path(REPO_ROOT, items_path)
    if (file.exists(full)) out[[items_path]] <- full
  }
  out
}

#' Archive the contents of `outdir` into `file`
#'
#' Prefers the zip package, which is pure C: utils::zip shells out to the binary
#' named by R_ZIPCMD, which a stock R for Windows does not ship (it arrives with
#' Rtools) and which reports failure only as a warning, so an unguarded call turns
#' the download into a silently empty archive. The fallback keeps the app working
#' where the zip package is absent but a zip tool is on the path.
#'
#' @param file Path the archive is written to.
#' @param outdir Directory whose contents are archived, relative to its own root.
#' @return `file`, invisibly.
write_bundle_zip <- function(file, outdir) {
  if (requireNamespace("zip", quietly = TRUE)) {
    # include_directories = FALSE keeps the entry list to files alone, matching the
    # archive the Streamlit app builds by walking its output directory.
    zip::zipr(file, files = list.files(outdir), root = outdir, include_directories = FALSE)
    return(invisible(file))
  }
  if (!nzchar(Sys.which(Sys.getenv("R_ZIPCMD", "zip"))))
    stop("Cannot build the download: no zip tool is available. Install the zip ",
         "package (install.packages(\"zip\")), or set R_ZIPCMD to a zip executable ",
         "(on Windows, Rtools supplies one).", call. = FALSE)
  wd <- getwd(); on.exit(setwd(wd))
  setwd(outdir)
  status <- utils::zip(file, files = list.files(".", recursive = TRUE))
  if (!identical(as.integer(status), 0L))
    stop("Cannot build the download: the zip tool at '",
         Sys.which(Sys.getenv("R_ZIPCMD", "zip")), "' exited with status ", status,
         ". Install the zip package (install.packages(\"zip\")) to remove the ",
         "dependency on an external zip tool.", call. = FALSE)
  invisible(file)
}

#' Read the conditions table's rows into the design's `conditions` list
#'
#' A row contributes a condition when it names one and defines at least one window,
#' a category list or a pair of numeric bounds. The optional second factor is added
#' only when both of its bounds are given. Mirrors conditions_from_table() in the
#' Streamlit app.
#'
#' @param df The edited conditions table.
#' @return A list of `list(name =, define_by =)` entries, one per usable row.
conditions_from_table <- function(df) {
  conditions <- list()
  isnum <- function(x) !is.null(x) && !is.na(x) && nzchar(as.character(x))
  for (i in seq_len(nrow(df))) {
    nm <- trimws(as.character(df$name[i])); dim <- trimws(as.character(df$dimension[i]))
    if (!nzchar(nm) || !nzchar(dim)) next
    define_by <- list()
    cats <- trimws(as.character(df$categories[i]))
    if (!is.na(cats) && nzchar(cats)) {
      define_by[[dim]] <- trimws(strsplit(cats, ",")[[1]])
    } else if (isnum(df$lower[i]) && isnum(df$upper[i])) {
      define_by[[dim]] <- c(as.numeric(df$lower[i]), as.numeric(df$upper[i]))
    }
    dim2 <- trimws(as.character(df$dimension2[i]))
    if (nzchar(dim2) && dim2 != "NA" && isnum(df$lower2[i]) && isnum(df$upper2[i]))
      define_by[[dim2]] <- c(as.numeric(df$lower2[i]), as.numeric(df$upper2[i]))
    if (length(define_by)) conditions[[length(conditions) + 1]] <-
      list(name = nm, define_by = define_by)
  }
  conditions
}

#' The matched dimensions on which the conditions take different windows
#'
#' Matching on such a dimension works against the contrast the windows define. A
#' band that every condition shares only restricts the pool, so it is not listed. A
#' dimension that one condition restricts and another leaves open is listed.
#' Mirrors manipulated_matches() in the Streamlit app.
#'
#' @param conditions The design's `conditions`.
#' @param match_on The dimensions chosen under 'Match on'.
#' @return The listed dimensions, in `match_on` order.
manipulated_matches <- function(conditions, match_on) {
  dims <- as.character(unlist(match_on))
  differs <- function(d) {
    windows <- lapply(conditions, function(cond) cond[["define_by"]][[d]])
    any(!vapply(windows, is.null, logical(1))) &&
      !all(vapply(windows, identical, logical(1), windows[[1]]))
  }
  dims[vapply(dims, differs, logical(1))]
}

#' The warning shown under 'Match on' for manipulated_matches(), or NULL
#'
#' @param dims The dimensions manipulated_matches() listed.
#' @return A one-line character string, or NULL when there are none.
manipulation_warning <- function(dims) {
  n <- length(dims)
  if (!n) return(NULL)
  named <- if (n == 1L) dims else paste0(paste(dims[-n], collapse = ", "), " and ", dims[[n]])
  paste0("'Match on' includes ", named, ", on which the conditions take different ",
         "windows. Matching on a dimension the conditions manipulate works against ",
         "the contrast they define.")
}

#' The caption under the exported code, from the run's datasheet record
#'
#' `selection$cross_engine` says whether the two engines select byte-identical
#' materials for the run: `mahalanobis` and `optimal` agree only approximately,
#' because their linear algebra differs in the last bits between the engines. A
#' record without the field is read as the datasheet's own renderer reads it.
#' Mirrors parity_claim() in the Streamlit app.
#'
#' @param record The run's datasheet, as read from its JSON file, or NULL.
#' @return A one-line character string.
parity_claim <- function(record) {
  cross <- record[["selection"]][["cross_engine"]]
  if (is.character(cross) && length(cross) == 1L && startsWith(cross, "approximate"))
    APPROXIMATE
  else
    BYTE_IDENTICAL
}

#' The heading of the d interval column, from the run's datasheet record
#'
#' The interval beside a TOST at alpha is the 1 - 2 alpha interval, so 90% at the
#' default alpha of .05. Mirrors interval_label() in the Streamlit app.
#'
#' @param record The run's datasheet, as read from its JSON file, or NULL.
#' @return A label such as "90% CI".
interval_label <- function(record) {
  alpha <- record[["equivalence"]][["alpha"]]
  if (is.null(alpha)) alpha <- 0.05
  sprintf("%g%% CI", (1 - 2 * as.numeric(alpha)) * 100)
}

#' Enable or disable the Run button
#'
#' Older releases of shiny lack updateActionButton()'s `disabled` argument. There
#' the button stays enabled, and the run observer refuses the run with the message
#' the page already shows.
#'
#' @param session The Shiny session.
#' @param enabled Whether the button should accept a press.
set_run_enabled <- function(session, enabled) {
  if ("disabled" %in% names(formals(updateActionButton)))
    updateActionButton(session, "run", disabled = !enabled)
}

reproduction_code <- function(design, cfg) {
  list(
    yaml = clean_yaml(design),
    r = paste0("# R\nlibrary(lexsync)\n\nrun_pipeline(\"", cfg,
               "\", schema_path = \"config/schema.yaml\", outdir = \"output\")"),
    python = paste0("# Python\nfrom lexsync import run_pipeline\n\nrun_pipeline(\"", cfg,
                    "\", schema_path=\"config/schema.yaml\", outdir=\"output\")"),
    # Double quotes outside and single quotes inside, which bash, cmd.exe and both
    # PowerShells pass on unchanged: clean_meta() refuses every character in a
    # design's name that would end either string. Each comment has a line of its
    # own, because cmd.exe passes a trailing # on as one more argument.
    # Word-identical to the Streamlit app's block.
    cli = paste0("# R\n",
                 "Rscript -e \"lexsync::run_pipeline('", cfg,
                 "', schema_path = 'config/schema.yaml', outdir = 'output')\"\n",
                 "# Python console script\n",
                 "lexsync run \"", cfg, "\"\n",
                 "# Python (module form)\n",
                 "python -m lexsync run \"", cfg, "\"")
  )
}

ui <- page_sidebar(
  title = "lexsync",
  theme = bs_theme(version = 5, preset = "cosmo"),
  sidebar = sidebar(
    width = 320,
    h5("Design"),
    selectInput("paradigm", "Paradigm", choices = names(PARADIGMS)),
    textInput("name", "Design name", "my_design"),
    textInput("language", "Language label", "english"),
    textInput("font", "Stimulus font", "Courier New"),
    hr(),
    helpText(sprintf("lexsync %s. The app runs the installed package, not a re-implementation.",
                     as.character(utils::packageVersion("lexsync"))))
  ),
  markdown(paste(
    "Reproducible psycholinguistic stimulus design, running on the R engine.",
    "Assemble a design, run the verified lexsync pipeline, and export the design",
    "file together with the R, Python and command-line code that reproduces it.",
    "Under the deterministic matching methods, which include the default, the two",
    "engines select byte-identical stimuli."
  )),
  uiOutput("design_ui"),
  actionButton("run", "Run design", class = "btn-primary btn-lg w-100"),
  uiOutput("status"),
  uiOutput("results")
)

server <- function(input, output, session) {
  conds <- reactiveVal(preset_df(DEFAULT_PRESET))
  observeEvent(input$preset, {
    conds(preset_df(input$preset))
    # The matched dimensions and the method travel with the preset, as in the
    # Streamlit app. Left at their general defaults, they had the neighbourhood
    # preset match on the dimension it manipulates and leave length unequated.
    m <- preset_matching(input$preset)
    updateSelectizeInput(session, "match_on", selected = m$match_on)
    updateSelectInput(session, "method", selected = m$method)
  }, ignoreInit = TRUE)
  observeEvent(input$cond_tbl_cell_edit, {
    # The table is rendered without row names, so the client numbers its columns
    # from 0 at 'name'. editData() assumes a row-name column unless told
    # otherwise, and it would write every edit one column to the left.
    conds(DT::editData(conds(), input$cond_tbl_cell_edit, "cond_tbl", rownames = FALSE))
  })
  bundle <- reactiveVal(NULL)

  # The paradigm's key, or NA before the chooser has a value.
  paradigm <- reactive({
    label <- input$paradigm
    if (is.character(label) && length(label) == 1L && label %in% names(PARADIGMS))
      PARADIGMS[[label]] else NA_character_
  })

  # The chosen lexicon's file, or NULL when there is none to read.
  lexicon_path <- function() {
    corpus <- input$corpus
    if (!is.character(corpus) || length(corpus) != 1L || !corpus %in% names(CORPORA))
      return(NULL)
    unname(CORPORA[[corpus]])
  }

  # A factorial design with nothing under 'Match on' cannot run: every distance
  # would be zero and the tie-break alone would choose the words, so the engines
  # refuse it. The message, or NULL when the design can run.
  run_blocked <- reactive(
    if (identical(paradigm(), "factorial") && !length(input$match_on)) EMPTY_MATCH_ON)
  observe(set_run_enabled(session, is.null(run_blocked())))

  output$match_on_notes <- renderUI({
    blocked <- run_blocked()
    if (!is.null(blocked)) return(div(class = "alert alert-warning mt-2", blocked))
    if (!identical(paradigm(), "factorial")) return(NULL)
    note <- manipulation_warning(
      manipulated_matches(conditions_from_table(conds()), input$match_on))
    if (!is.null(note)) div(class = "alert alert-warning mt-2", note)
  })

  output$screen_ui <- renderUI({
    if (!"nonstandard" %in% lexicon_columns(lexicon_path())) return(NULL)
    tagList(checkboxInput("screened", "Screened forms only", TRUE), helpText(SCREEN_HELP))
  })

  output$design_ui <- renderUI({
    p <- PARADIGMS[[input$paradigm]]
    tagList(
      if (p %in% c("factorial", "lexical_decision")) tagList(
        h4("Corpus"),
        selectInput("corpus", "Lexicon", choices = names(CORPORA),
                    selected = if (DEFAULT_LEXICON %in% names(CORPORA)) DEFAULT_LEXICON),
        fluidRow(
          column(6, sliderInput("length", "Length (letters/characters)", 1, 20, c(3, 7))),
          column(6, sliderInput("frequency", "Frequency (Zipf)", 1, 8, c(3.5, 7.0), step = 0.1))
        ),
        uiOutput("screen_ui")
      ),
      if (p == "factorial") tagList(
        h4("Conditions"),
        helpText("Set the first factor with dimension/lower/upper (or categories for a ",
                 "categorical column such as gender). The optional dimension2/lower2/upper2 ",
                 "add a second factor for a 2x2 cell."),
        selectInput("preset", "Start from a preset", names(PRESET_MATCHING)),
        DT::DTOutput("cond_tbl"),
        br(),
        fluidRow(
          column(4, numericInput("n", "Items per condition", 80, 4, 400, 2)),
          column(4, selectInput("method", "Matching method",
                                c("standardised_euclidean", "joint", "mahalanobis", "optimal"),
                                selected = preset_matching(DEFAULT_PRESET)$method)),
          column(4, numericInput("nsets", "Resampled disjoint sets (0 = off)", 0, 0, 20, 1))
        ),
        helpText(METHOD_HELP),
        selectizeInput("match_on", "Match on (controlled dimensions)", choices = DIMENSIONS,
                       selected = preset_matching(DEFAULT_PRESET)$match_on, multiple = TRUE),
        uiOutput("match_on_notes"),
        uiOutput("tolerance_ui"),
        numericInput("lists", "Counterbalancing lists", 1, 1, 16, 1)
      ),
      if (p == "lexical_decision") tagList(
        numericInput("n", "Items per condition (words = pseudowords)", 60, 4, 200, 2),
        selectInput("gen_method", "Pseudoword generation method", GENERATION_METHODS),
        helpText("Real words in the band are paired with deterministically generated, ",
                 "orthographically legal pseudowords matched on length. ",
                 "letter_substitution changes the fewest single letters, keeping every ",
                 "bigram attested; subsyllabic swaps whole onset/nucleus/coda ",
                 "constituents (Wuggy-style; Keuleers & Brysbaert, 2010).")
      ),
      if (p %in% c("priming", "self_paced_reading")) tagList(
        h4("Item table"),
        {
          ex <- if (p == "priming") "priming_pairs_en.csv" else "spr_sentences_en.csv"
          tagList(
            helpText(sprintf("Using the bundled example: items/%s", ex)),
            numericInput("lists", "Counterbalancing lists", 2, 1, 16, 1)
          )
        }
      )
    )
  })

  output$cond_tbl <- DT::renderDT({
    DT::datatable(conds(), editable = TRUE, rownames = FALSE,
                  options = list(dom = "t", ordering = FALSE, pageLength = 8))
  })

  output$tolerance_ui <- renderUI({
    dims <- input$match_on
    if (!length(dims)) return(NULL)
    accordion(
      open = FALSE,
      accordion_panel(
        "Advanced: per-dimension tolerance windows (mean ± k·SD)",
        helpText("Override the schema defaults; e.g. frequency 0.111 reproduces the ",
                 "mean ± SD/9 window of González Alonso et al. (2025). Zero leaves the ",
                 "schema default for that dimension in place."),
        lapply(dims, function(d)
          numericInput(paste0("tol_", d), sprintf("k for %s", DIM_LABEL[[d]]),
                       0, 0, 10, 0.05))
      )
    )
  })

  tolerance_k <- function()
    positive_tolerances(stats::setNames(
      lapply(input$match_on, function(d) input[[paste0("tol_", d)]]), input$match_on))

  build_design <- function() {
    p <- PARADIGMS[[input$paradigm]]
    d <- list(name = input$name, language = input$language)
    if (!is.null(input$font) && nzchar(input$font) && input$font != "Courier New")
      d$font <- input$font
    lexicon_abs <- NULL; items_abs <- NULL
    if (p %in% c("factorial", "lexical_decision")) {
      lexicon_abs <- lexicon_path()
      d$lexicon <- paste0("corpora/derived/", input$corpus, ".csv")
      # The checkbox is drawn only for a lexicon that marks forms, and it starts
      # ticked, so a value not yet sent counts as ticked.
      d$pool_filters <- pool_filters(input$length, input$frequency,
                                     lexicon_columns(lexicon_abs), !isFALSE(input$screened))
    }
    if (p == "factorial") {
      d$paradigm <- "factorial"
      d$conditions <- conditions_from_table(conds())
      d$n_per_condition <- as.integer(input$n)
      d$match_on <- as.list(input$match_on)
      d$matching <- list(method = input$method)
      tol <- tolerance_k()
      if (length(tol)) d$matching$tolerance_k <- tol
      if (!is.null(input$nsets) && input$nsets >= 2) d$resample <- list(n_sets = as.integer(input$nsets))
      d$counterbalance <- list(lists = as.integer(input$lists))
    } else if (p == "lexical_decision") {
      d$paradigm <- "lexical_decision"
      d$items <- list(source = "generate")
      if (!is.null(input$gen_method) && input$gen_method != GENERATION_METHODS[[1]])
        d$items$generation <- list(method = input$gen_method)
      d$n_per_condition <- as.integer(input$n)
      d$counterbalance <- list(lists = 1L)
    } else if (p %in% c("priming", "self_paced_reading")) {
      d$paradigm <- p
      ex <- if (p == "priming") "priming_pairs_en.csv" else "spr_sentences_en.csv"
      items_abs <- file.path(ITEMS_DIR, ex)
      d$items <- list(source = "table", path = paste0("items/", ex))
      d$counterbalance <- list(lists = as.integer(input$lists))
    }
    list(design = d, lexicon_abs = lexicon_abs, items_abs = items_abs)
  }

  observeEvent(input$run, {
    spec <- build_design(); d <- spec$design
    p <- PARADIGMS[[input$paradigm]]
    if (p %in% c("factorial", "lexical_decision") && is.null(spec$lexicon_abs)) {
      bundle(list(error = "Choose a lexicon first.")); return()
    }
    if (p == "factorial" && length(d$conditions) < 2) {
      bundle(list(error = "Define at least two conditions.")); return()
    }
    # Run is disabled while this holds, except under a shiny too old to disable it.
    if (!is.null(run_blocked())) {
      bundle(list(error = run_blocked())); return()
    }
    run_d <- d
    if (!is.null(spec$lexicon_abs)) run_d$lexicon <- spec$lexicon_abs
    if (!is.null(spec$items_abs)) run_d$items$path <- spec$items_abs
    tmp <- tempfile("lexsync_app_"); dir.create(tmp)
    dp <- file.path(tmp, "design.yaml"); write_yaml_lf(run_d, dp)
    out <- file.path(tmp, "output")
    res <- tryCatch(
      withCallingHandlers(
        run_pipeline(dp, schema_path = SCHEMA_PATH, outdir = out, verbose = FALSE),
        message = function(m) invokeRestart("muffleMessage")),
      error = function(e) structure(list(), error = conditionMessage(e)))
    if (!is.null(attr(res, "error"))) { bundle(list(error = attr(res, "error"))); return() }
    base <- sub("_stimuli_R\\.csv$", "", basename(res$stimuli))
    ds_md <- file.path(out, "reports", paste0(base, "_datasheet_R.md"))
    # The machine-readable datasheet, which the caption under the exported code and
    # the interval heading are read from.
    ds_json <- file.path(out, "reports", paste0(base, "_datasheet_R.json"))
    bundle(list(design = d, cfg = paste0(input$name, ".yaml"), outdir = out, paths = res,
                record = if (file.exists(ds_json)) jsonlite::read_json(ds_json) else NULL,
                stimuli = utils::read.csv(res$stimuli, check.names = FALSE),
                comparisons = if (!is.null(res$comparisons) && file.exists(res$comparisons))
                  utils::read.csv(res$comparisons) else NULL,
                descriptives = if (!is.null(res$descriptives) && file.exists(res$descriptives))
                  utils::read.csv(res$descriptives) else NULL,
                datasheet = if (file.exists(ds_md)) paste(readLines(ds_md, warn = FALSE), collapse = "\n") else NULL))
  })

  output$status <- renderUI({
    b <- bundle()
    if (is.null(b)) return(div(class = "alert alert-info mt-3",
                               "Configure a design above, then press Run design."))
    if (!is.null(b$error)) return(div(class = "alert alert-danger mt-3", b$error))
    div(class = "alert alert-success mt-3", sprintf("Selected %d rows.", nrow(b$stimuli)))
  })

  output$results <- renderUI({
    b <- bundle(); if (is.null(b) || !is.null(b$error)) return(NULL)
    navset_tab(
      nav_panel("Stimuli", DT::DTOutput("stim_tbl")),
      nav_panel("Realised control", uiOutput("control_ui")),
      nav_panel("Datasheet", uiOutput("ds_ui")),
      nav_panel("Experiment scripts", uiOutput("exp_ui")),
      nav_panel("Reproducible code", uiOutput("code_ui")),
      nav_panel("Download", br(), downloadButton("dl_zip", "Download everything (design + outputs)",
                                                 class = "btn-primary"))
    )
  })

  output$stim_tbl <- DT::renderDT(DT::datatable(bundle()$stimuli, rownames = FALSE,
                                                options = list(pageLength = 15, scrollX = TRUE)))

  output$control_ui <- renderUI({
    b <- bundle()
    # Word-identical to the Streamlit app's notice. tests/test_apps.py pins the two
    # against each other, as it does the parity claim under Reproducible code.
    if (is.null(b$comparisons))
      return(div(class = "alert alert-info",
                 "This paradigm draws from an item table, so no corpus-matching ",
                 "control report is produced."))
    tagList(
      h5("Realised control for every pair of conditions and every dimension"),
      DT::renderDT({
        c <- b$comparisons
        # The interval goes with the TOST at the schema's alpha, so its heading comes
        # from the run's datasheet.
        ci <- interval_label(b$record)
        c[[ci]] <- sprintf("[%.2f, %.2f]", c$d_ci_low, c$d_ci_high)
        cols <- intersect(c("condition", "reference", "dimension", "role", "mean_diff",
                            "cohens_d", ci, "var_ratio", "tost_p", "equivalent"),
                          names(c))
        DT::datatable(c[, cols], rownames = FALSE, options = list(dom = "t"))
      }),
      renderPlot({
        # One bar per dimension and pair: a design with more than two conditions
        # compares every pair, and bars sharing a dimension's label could not be told
        # apart.
        c <- b$comparisons; v <- abs(c$cohens_d)
        names(v) <- sprintf("%s (%s vs %s)", c$dimension, c$condition, c$reference)
        op <- par(mar = c(9, 4, 1, 1)); on.exit(par(op))
        # d is NA where a condition has a single item, and when every bar is NA,
        # barplot() cannot choose an axis and fails, so the axis is fixed for that case.
        barplot(v, ylab = "|Cohen's d|", col = ifelse(v > 1, "#d95f02", "#1b9e77"), las = 2,
                cex.names = 0.8, ylim = if (all(is.na(v))) c(0, 1))
        abline(h = 0.5, lty = 2, col = "grey50")
      }, height = 320),
      helpText("Absolute standardised mean difference by dimension and pair. Manipulated ",
               "dimensions stand high; matched dimensions sit near zero (below the 0.5-SD ",
               "line), and uncontrolled ones may sit anywhere."),
      if (!is.null(b$descriptives)) tagList(h5("Per-condition descriptive statistics"),
        renderTable(b$descriptives))
    )
  })

  output$ds_ui <- renderUI({
    b <- bundle()
    if (is.null(b$datasheet)) return(div(class = "alert alert-info", "No datasheet for this design."))
    markdown(b$datasheet)
  })

  output$exp_ui <- renderUI({
    b <- bundle(); files <- experiment_files(b$paths$experiments)
    tagList(
      helpText("The same matched stimuli compile to three presentation targets. A ",
               "PsychoPy or OpenSesame experiment reads the tables that share its name, ",
               "so download them together."),
      lapply(seq_along(files), function(i) {
        p <- files[[i]]
        if (!file.exists(p)) return(NULL)
        id <- paste0("dl_exp_", i)
        output[[id]] <- downloadHandler(
          filename = function() basename(p),
          content = function(file) file.copy(p, file, overwrite = TRUE))
        div(downloadButton(id, basename(p)), style = "margin-bottom:6px")
      })
    )
  })

  output$code_ui <- renderUI({
    b <- bundle(); code <- reproduction_code(b$design, b$cfg)
    tagList(
      h5(sprintf("Design configuration — save as %s", b$cfg)),
      tags$pre(tags$code(code$yaml)),
      h5("Reproduce in R"), tags$pre(tags$code(code$r)),
      h5("Reproduce in Python"), tags$pre(tags$code(code$python)),
      h5("Reproduce from the command line"), tags$pre(tags$code(code$cli)),
      helpText(parity_claim(b$record))
    )
  })

  output$dl_zip <- downloadHandler(
    filename = function() paste0(bundle()$design$name, "_lexsync.zip"),
    content = function(file) {
      b <- bundle()
      write_yaml_lf(b$design, file.path(b$outdir, b$cfg))
      # The exported reproduction code passes schema_path = "config/schema.yaml",
      # so the archive carries the schema the run actually used (the installed
      # package copy) at that path, plus any repository-bundled input the design
      # names at its design-relative path. Copied under outdir, where the zip
      # walk picks them up like any other artefact.
      extras <- c(list("config/schema.yaml" = SCHEMA_PATH), bundled_inputs(b$design))
      for (rel in names(extras)) {
        dest <- file.path(b$outdir, rel)
        dir.create(dirname(dest), recursive = TRUE, showWarnings = FALSE)
        file.copy(extras[[rel]], dest, overwrite = TRUE)
      }
      write_bundle_zip(file, b$outdir)
    }
  )
}

shinyApp(ui, server)
