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

# The lexsync accent, taken from the documentation site (R_workflow/pkgdown/extra.scss).
# The Streamlit twin names the same hex in .streamlit/config.toml.
BRAND_PRIMARY <- "#7C4EA3"

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
  "Categorisation (item table)" = "categorisation",
  "Self-paced reading (item table)" = "self_paced_reading"
)
# The paradigms that take their trials from an item table rather than from the
# corpus, each with the bundled example table the app offers for it. Keeping the
# set in one place is what stops the chooser and the design builder from
# disagreeing about which paradigms need a table.
ITEM_TABLE_EXAMPLES <- c(
  priming = "priming_pairs_en.csv",
  categorisation = "categorisation_en.csv",
  self_paced_reading = "spr_sentences_en.csv"
)

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

# Each preset's matched dimensions and matching method. A preset that manipulates
# a dimension must not also ask the engine to match on it, so the neighbourhood
# contrast is matched on length and frequency rather than on the general default.
# The Streamlit app's PRESET_MATCHING holds the same table.
PRESET_MATCHING <- list(
  "High vs low frequency" = list(match_on = c("length", "n_density", "old20"),
                                 method = "standardised_euclidean"),
  "Dense vs sparse neighbourhood" = list(match_on = c("length", "frequency"),
                                         method = "joint"),
  "2x2 frequency x neighbourhood" = list(match_on = "length",
                                         method = "standardised_euclidean"),
  "Custom" = list(match_on = "length", method = "standardised_euclidean")
)

# The preset the chooser opens on, and so the one the controls start from.
DEFAULT_PRESET <- names(PRESET_MATCHING)[[1]]

preset_matching <- function(preset) {
  m <- PRESET_MATCHING[[preset]]
  if (is.null(m)) PRESET_MATCHING[["Custom"]] else m
}

preset_df <- function(preset) {
  blank <- function() data.frame(
    name = character(), dimension = character(), lower = numeric(), upper = numeric(),
    categories = character(), dimension2 = character(), lower2 = numeric(), upper2 = numeric(),
    stringsAsFactors = FALSE)
  # lo2/hi2 default to the numeric NA, not the logical one: a preset that leaves
  # the second factor empty must still hand DT a numeric column, or the first edit
  # of that cell coerces the whole column to character.
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

#' A row for a condition the user has still to describe
#'
#' The same columns and types a preset supplies, so `rbind` onto the table leaves
#' the optional second factor numeric rather than logical.
#'
#' @return A one-row data frame.
blank_condition_row <- function()
  data.frame(name = "", dimension = "", lower = NA_real_, upper = NA_real_,
             categories = "", dimension2 = "", lower2 = NA_real_, upper2 = NA_real_,
             stringsAsFactors = FALSE)

#' The first rows of an input file, as a table
#'
#' The app asked the user to commit to a run without showing a row of the lexicon
#' or of the item table it would read. The Streamlit app previews both.
#'
#' @param path Path of the CSV to preview, or NULL.
#' @param n Number of rows to read.
#' @return A DT widget, or NULL when there is no file to read.
preview_table <- function(path, n) {
  if (is.null(path) || !length(path) || !file.exists(path)) return(NULL)
  DT::datatable(utils::read.csv(path, nrows = n, check.names = FALSE), rownames = FALSE,
                options = list(dom = "t", ordering = FALSE, scrollX = TRUE))
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

#' One end of a condition's window as a number, or NULL when the cell holds none
#'
#' `as.numeric` on a cell the editor let through as text gives NA and a warning,
#' and the caller then wrote `c(NA, NA)` into the design as if the user had asked
#' for that window. Returning NULL instead drops the factor the cell belongs to.
#' The Streamlit app's _bound reads a cell the same way.
#'
#' @param x One cell of the conditions table.
#' @return A length-one numeric, or NULL.
bound <- function(x) {
  if (is.null(x) || length(x) != 1L || is.na(x) || !nzchar(trimws(as.character(x))))
    return(NULL)
  v <- suppressWarnings(as.numeric(x))
  if (is.na(v)) NULL else v
}

#' Read the conditions table's rows into the design's `conditions` list
#'
#' A row contributes a condition when it names one and defines at least one
#' window, either a category list or a pair of numeric bounds. The optional second
#' factor is added only when both of its bounds are numbers. The Streamlit app's
#' conditions_from_table reads the same table the same way.
#'
#' @param df The edited conditions table.
#' @return A list of `list(name =, define_by =)` entries, one per usable row.
conditions_from_table <- function(df) {
  conditions <- list()
  for (i in seq_len(nrow(df))) {
    nm <- trimws(as.character(df$name[i])); dim <- trimws(as.character(df$dimension[i]))
    if (is.na(nm) || is.na(dim) || !nzchar(nm) || !nzchar(dim)) next
    define_by <- list()
    cats <- trimws(as.character(df$categories[i]))
    lower <- bound(df$lower[i]); upper <- bound(df$upper[i])
    if (!is.na(cats) && nzchar(cats)) {
      define_by[[dim]] <- trimws(strsplit(cats, ",")[[1]])
    } else if (!is.null(lower) && !is.null(upper)) {
      define_by[[dim]] <- c(lower, upper)
    }
    dim2 <- trimws(as.character(df$dimension2[i]))
    lower2 <- bound(df$lower2[i]); upper2 <- bound(df$upper2[i])
    if (!is.na(dim2) && nzchar(dim2) && dim2 != "NA" &&
        !is.null(lower2) && !is.null(upper2))
      define_by[[dim2]] <- c(lower2, upper2)
    if (length(define_by))
      conditions[[length(conditions) + 1]] <- list(name = nm, define_by = define_by)
  }
  conditions
}

#' The sentence under the exported code, conditioned on the matching method
#'
#' `mahalanobis` and `optimal` use a covariance inverse and an assignment solver,
#' whose last bits differ between the two linear-algebra backends, so the
#' unqualified claim contradicted the method chooser's own help text and the
#' 'Cross-engine determinism' line of the datasheet one tab away. The Streamlit app
#' words both cases the same way.
#'
#' @param design The design that ran.
#' @return A one-line character string.
parity_claim <- function(design) {
  if (isTRUE(design$matching$method %in% c("mahalanobis", "optimal")))
    paste0("This design's matching method uses a covariance inverse or an ",
           "assignment solver, so the R and Python engines select equivalent ",
           "but not byte-identical stimuli. The datasheet's 'Cross-engine ",
           "determinism' line records which case applies.")
  else
    paste0("The R and Python engines produce byte-identical stimuli and ",
           "trial order from this configuration.")
}

#' The realised-control bar chart's data, one bar per comparison
#'
#' `comparisons` carries one row per non-anchor condition per dimension, so a 2x2
#' design contributes three comparisons to every dimension. A plain barplot over
#' `comp$dimension` repeated each label once per comparison with nothing saying
#' which bar belonged to which condition. Grouping by condition labels them, and
#' the Streamlit app groups the same rows.
#'
#' The cells are filled directly rather than summed through `stats::xtabs`, which
#' writes a zero wherever it has nothing to add. An undefined d, which the engine
#' reports as NA when both conditions are constant on a dimension, would then draw
#' a bar at zero and read as perfect matching; left as NA, `barplot` draws a gap,
#' which is what the datasheet writes as '--'. The Streamlit chart keeps the NaN
#' and Vega-Lite omits the bar.
#'
#' @param comp The comparisons table from the run.
#' @return A condition-by-dimension matrix of |Cohen's d|, NA where the comparison
#'   is absent or undefined.
control_chart <- function(comp) {
  conditions <- as.character(comp$condition)
  dimensions <- as.character(comp$dimension)
  conds <- sort(unique(conditions))
  dims <- sort(unique(dimensions))
  m <- matrix(NA_real_, length(conds), length(dims), dimnames = list(conds, dims))
  m[cbind(match(conditions, conds), match(dimensions, dims))] <- abs(comp$cohens_d)
  m
}

#' The sentence under that chart, naming the anchor the bars are measured against
#'
#' Every comparison is against one anchor condition, which the chart itself does
#' not show. The Streamlit app words this the same way.
#'
#' @param comp The comparisons table from the run.
#' @return A one-line character string.
control_caption <- function(comp) {
  anchor <- if (length(comp$reference)) paste0(" ", as.character(comp$reference)[[1]]) else ""
  paste0("Absolute standardised mean difference by dimension, one bar per ",
         "condition against the anchor", anchor, ". Manipulated dimensions ",
         "stand high; matched dimensions sit near zero (below the 0.5-SD line).")
}

#' Map each input the design names to the file the run should read it from
#'
#' @param design The design as shown to the user, carrying repository-relative paths.
#' @param lexicon_abs Absolute path of the chosen or uploaded lexicon, or NULL.
#' @param items_abs Absolute path of the chosen or uploaded item table, or NULL.
#' @return Named list: design-relative path -> absolute path of the file to place
#'   there. A design that already names an absolute path needs no staging and is
#'   omitted. The Streamlit app's staged_inputs makes the same map.
staged_inputs <- function(design, lexicon_abs, items_abs) {
  relative <- function(p) is.character(p) && length(p) == 1L &&
    !grepl("^(/|~|[A-Za-z]:[/\\\\])", p)
  out <- list()
  if (!is.null(lexicon_abs) && relative(design$lexicon))
    out[[design$lexicon]] <- lexicon_abs
  if (!is.null(items_abs) && relative(design$items$path))
    out[[design$items$path]] <- items_abs
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

reproduction_code <- function(design, cfg) {
  list(
    yaml = clean_yaml(design),
    r = paste0("# R\nlibrary(lexsync)\n\nrun_pipeline(\"", cfg,
               "\", schema_path = \"config/schema.yaml\", outdir = \"output\")"),
    python = paste0("# Python\nfrom lexsync import run_pipeline\n\nrun_pipeline(\"", cfg,
                    "\", schema_path=\"config/schema.yaml\", outdir=\"output\")"),
    cli = paste0("# Command line\n",
                 "Rscript -e 'lexsync::run_pipeline(\"", cfg, "\")'    # R\n",
                 "lexsync run ", cfg, "                              # Python console script\n",
                 "python -m lexsync run ", cfg, "                    # Python (module form)")
  )
}

ui <- page_sidebar(
  title = "lexsync",
  # The documentation site's accent, so the two apps and the two sites look like one
  # family. Cosmo's own blue also falls short of AA against the white label of the
  # full-width Run button, where this violet reaches 6.04:1.
  theme = bs_theme(version = 5, preset = "cosmo", primary = BRAND_PRIMARY,
                   "link-color" = BRAND_PRIMARY),
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
    "The two engines select byte-identical stimuli under the deterministic",
    "matching methods."
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
    # The matched dimensions travel with the preset: leaving them behind would
    # ask the engine to match on the dimension the preset manipulates.
    m <- preset_matching(input$preset)
    updateSelectizeInput(session, "match_on", selected = m$match_on)
    updateSelectInput(session, "method", selected = m$method)
  }, ignoreInit = TRUE)
  observeEvent(input$cond_add, conds(rbind(conds(), blank_condition_row())))
  observeEvent(input$cond_remove, {
    i <- input$cond_tbl_rows_selected
    if (!length(i)) return()
    kept <- conds()[-i, , drop = FALSE]
    # Renumbered, so a later cell edit reaches the row the client names.
    rownames(kept) <- NULL
    conds(kept)
  })
  observeEvent(input$cond_tbl_cell_edit, {
    # rownames = FALSE, as the table is rendered: editData otherwise reads the
    # client's column index one column to the left of the edited cell.
    conds(DT::editData(conds(), input$cond_tbl_cell_edit, "cond_tbl", rownames = FALSE))
  })
  bundle <- reactiveVal(NULL)

  output$design_ui <- renderUI({
    p <- PARADIGMS[[input$paradigm]]
    tagList(
      if (p %in% c("factorial", "lexical_decision")) tagList(
        h4("Corpus"),
        if (length(CORPORA)) fluidRow(
          column(5, selectInput("corpus", "Lexicon", choices = names(CORPORA))),
          column(7, DT::DTOutput("corpus_preview"))
        )
        else div(class = "alert alert-warning",
                 "No bundled corpora were found under corpora/derived/. Launch the app ",
                 "from the lexsync repository root."),
        fluidRow(
          column(6, sliderInput("length", "Length (letters/characters)", 1, 20, c(3, 7))),
          column(6, sliderInput("frequency", "Frequency (Zipf)", 1, 8, c(3.5, 7.0), step = 0.1))
        )
      ),
      if (p == "factorial") tagList(
        h4("Conditions"),
        helpText("Set the first factor with dimension/lower/upper (or categories for a ",
                 "categorical column such as gender). The optional dimension2/lower2/upper2 ",
                 "add a second factor for a 2x2 cell."),
        selectInput("preset", "Start from a preset", names(PRESET_MATCHING)),
        DT::DTOutput("cond_tbl"),
        div(class = "mt-2",
            actionButton("cond_add", "Add condition", class = "btn-sm btn-outline-secondary"),
            actionButton("cond_remove", "Remove selected", class = "btn-sm btn-outline-secondary")),
        br(),
        fluidRow(
          column(4, numericInput("n", "Items per condition", 80, 4, 400, 2)),
          column(4, selectInput("method", "Matching method",
                                c("standardised_euclidean", "joint", "mahalanobis", "optimal"),
                                selected = preset_matching(DEFAULT_PRESET)$method)),
          column(4, numericInput("nsets", "Resampled disjoint sets (0 = off)", 0, 0, 20, 1))
        ),
        # Labelled by DIM_LABEL, as the tolerance panel below and the Streamlit
        # multiselect are: the values sent to build_design are the column names.
        selectizeInput("match_on", "Match on (controlled dimensions)",
                       choices = stats::setNames(DIMENSIONS, unname(DIM_LABEL[DIMENSIONS])),
                       selected = preset_matching(DEFAULT_PRESET)$match_on,
                       multiple = TRUE),
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
      if (p %in% names(ITEM_TABLE_EXAMPLES)) tagList(
        h4("Item table"),
        {
          ex <- ITEM_TABLE_EXAMPLES[[p]]
          tagList(
            helpText(sprintf("Using the bundled example: items/%s", ex)),
            DT::DTOutput("items_preview"),
            br(),
            numericInput("lists", "Counterbalancing lists", 2, 1, 16, 1)
          )
        }
      )
    )
  })

  output$cond_tbl <- DT::renderDT({
    # selection = "single" is what 'Remove selected' reads: a click marks the row
    # to drop, a double click still opens the cell for editing.
    DT::datatable(conds(), editable = TRUE, rownames = FALSE, selection = "single",
                  options = list(dom = "t", ordering = FALSE, pageLength = 8))
  })

  # The chosen lexicon's file. NULL when no corpus was found, and on the first
  # pass, before the chooser has a value: the run observer turns a NULL lexicon
  # into 'Choose a lexicon first.'
  lexicon_path <- function() {
    if (!length(CORPORA) || is.null(input$corpus) || !nzchar(input$corpus) ||
        !input$corpus %in% names(CORPORA)) return(NULL)
    unname(CORPORA[[input$corpus]])
  }

  output$corpus_preview <- DT::renderDT(req(preview_table(lexicon_path(), 5)))

  output$items_preview <- DT::renderDT({
    p <- PARADIGMS[[input$paradigm]]
    req(p %in% names(ITEM_TABLE_EXAMPLES))
    req(preview_table(file.path(ITEMS_DIR, ITEM_TABLE_EXAMPLES[[p]]), 8))
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
      d$pool_filters <- list(length = as.integer(input$length), frequency = input$frequency)
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
    } else if (p %in% names(ITEM_TABLE_EXAMPLES)) {
      d$paradigm <- p
      ex <- ITEM_TABLE_EXAMPLES[[p]]
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
    # 'Match on' can be emptied, and the pipeline accepts match_on: [] happily: the
    # run then reports success over a set that was never matched on anything.
    if (p == "factorial" && !length(d$match_on)) {
      bundle(list(error = "Choose at least one dimension to match on.")); return()
    }
    # The run uses the design exactly as it is shown, exported and archived: the
    # pipeline hashes the design file it ran into the datasheet's design_sha256 and
    # records the lexicon path it was given as the materials source, so rewriting
    # those paths to absolute ones would give the recipient of a bundle a datasheet
    # whose checksum names no file in it and a materials line naming a directory on
    # the machine that ran the app. Each input is placed at the path the design
    # records instead, inside a temporary directory the pipeline runs from.
    tmp <- tempfile("lexsync_app_"); dir.create(tmp)
    write_yaml_lf(d, file.path(tmp, "design.yaml"))
    staged <- staged_inputs(d, spec$lexicon_abs, spec$items_abs)
    for (rel in names(staged)) {
      dest <- file.path(tmp, rel)
      dir.create(dirname(dest), recursive = TRUE, showWarnings = FALSE)
      file.copy(staged[[rel]], dest, overwrite = TRUE)
    }
    out <- file.path(tmp, "output")
    wd <- setwd(tmp); on.exit(setwd(wd), add = TRUE)
    res <- tryCatch(
      withCallingHandlers(
        run_pipeline("design.yaml", schema_path = SCHEMA_PATH, outdir = out, verbose = FALSE),
        message = function(m) invokeRestart("muffleMessage")),
      error = function(e) structure(list(), error = conditionMessage(e)))
    setwd(wd)
    if (!is.null(attr(res, "error"))) { bundle(list(error = attr(res, "error"))); return() }
    base <- sub("_stimuli_R\\.csv$", "", basename(res$stimuli))
    ds_md <- file.path(out, "reports", paste0(base, "_datasheet_R.md"))
    bundle(list(design = d, cfg = paste0(input$name, ".yaml"), outdir = out, paths = res,
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
      h5("Effect size and equivalence per controlled dimension"),
      DT::renderDT({
        c <- b$comparisons
        c$`90% CI` <- sprintf("[%.2f, %.2f]", c$d_ci_low, c$d_ci_high)
        cols <- intersect(c("condition", "reference", "dimension", "cohens_d", "90% CI",
                            "var_ratio", "tost_p", "equivalent"), names(c))
        DT::datatable(c[, cols], rownames = FALSE, options = list(dom = "t"))
      }),
      renderPlot({
        m <- control_chart(b$comparisons)
        op <- par(mar = c(4, 4, 1, 1)); on.exit(par(op))
        # Headroom for the legend, which names the condition each bar belongs to.
        barplot(m, beside = TRUE, ylab = "|Cohen's d|", las = 1,
                ylim = c(0, max(m, 0.6, na.rm = TRUE) * 1.3),
                col = grDevices::hcl.colors(nrow(m), "Dark 3"),
                legend.text = rownames(m),
                args.legend = list(x = "top", horiz = TRUE, bty = "n", cex = 0.8))
        abline(h = 0.5, lty = 2, col = "grey50")
      }, height = 240,
      alt = "Absolute standardised mean difference per controlled dimension, one bar per condition."),
      helpText(control_caption(b$comparisons)),
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
    b <- bundle(); exps <- b$paths$experiments
    tagList(
      helpText("The same matched stimuli compile to three presentation targets."),
      lapply(names(exps), function(k) {
        p <- exps[[k]]
        if (is.null(p) || !file.exists(p)) return(NULL)
        id <- paste0("dl_exp_", k)
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
      helpText(parity_claim(b$design))
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
