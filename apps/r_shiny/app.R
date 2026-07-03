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
DIM_LABEL <- c(length = "Length", frequency = "Frequency (Zipf)", n_density = "Neighbourhood N",
               old20 = "OLD20", n_syllables = "Syllables", bigram_freq = "Bigram frequency")
PARADIGMS <- c(
  "Factorial word contrast (corpus matching)" = "factorial",
  "Lexical decision (generated pseudowords)" = "lexical_decision",
  "Priming (item table)" = "priming",
  "Self-paced reading (item table)" = "self_paced_reading"
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

preset_df <- function(preset) {
  blank <- function() data.frame(
    name = character(), dimension = character(), lower = numeric(), upper = numeric(),
    categories = character(), dimension2 = character(), lower2 = numeric(), upper2 = numeric(),
    stringsAsFactors = FALSE)
  r <- function(name, dim, lo, hi, cats = "", dim2 = "", lo2 = NA, hi2 = NA)
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
    "**Reproducible psycholinguistic stimulus design — R engine.**",
    "Assemble a design, run the verified lexsync pipeline, and export the design",
    "file together with the R, Python and command-line code that reproduces it.",
    "The two engines select byte-identical stimuli."
  )),
  uiOutput("design_ui"),
  actionButton("run", "Run design", class = "btn-primary btn-lg w-100"),
  uiOutput("status"),
  uiOutput("results")
)

server <- function(input, output, session) {
  conds <- reactiveVal(preset_df("High vs low frequency"))
  observeEvent(input$preset, conds(preset_df(input$preset)), ignoreInit = TRUE)
  observeEvent(input$cond_tbl_cell_edit, {
    conds(DT::editData(conds(), input$cond_tbl_cell_edit, "cond_tbl"))
  })
  bundle <- reactiveVal(NULL)

  output$design_ui <- renderUI({
    p <- PARADIGMS[[input$paradigm]]
    tagList(
      if (p %in% c("factorial", "lexical_decision")) tagList(
        h4("Corpus"),
        selectInput("corpus", "Lexicon", choices = names(CORPORA)),
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
        selectInput("preset", "Start from a preset",
                    c("High vs low frequency", "Dense vs sparse neighbourhood",
                      "2x2 frequency x neighbourhood", "Custom")),
        DT::DTOutput("cond_tbl"),
        br(),
        fluidRow(
          column(4, numericInput("n", "Items per condition", 80, 4, 400, 2)),
          column(4, selectInput("method", "Matching method",
                                c("standardised_euclidean", "joint", "mahalanobis", "optimal"))),
          column(4, numericInput("nsets", "Resampled disjoint sets (0 = off)", 0, 0, 20, 1))
        ),
        selectizeInput("match_on", "Match on (controlled dimensions)", choices = DIMENSIONS,
                       selected = c("length", "n_density", "old20"), multiple = TRUE),
        numericInput("lists", "Counterbalancing lists", 1, 1, 16, 1)
      ),
      if (p == "lexical_decision") tagList(
        numericInput("n", "Items per condition (words = pseudowords)", 60, 4, 200, 2),
        helpText("Real words in the band are paired with deterministically generated, ",
                 "orthographically legal pseudowords matched on length.")
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

  build_design <- function() {
    p <- PARADIGMS[[input$paradigm]]
    d <- list(name = input$name, language = input$language)
    if (!is.null(input$font) && nzchar(input$font) && input$font != "Courier New")
      d$font <- input$font
    lexicon_abs <- NULL; items_abs <- NULL
    if (p %in% c("factorial", "lexical_decision")) {
      lexicon_abs <- unname(CORPORA[[input$corpus]])
      d$lexicon <- paste0("corpora/derived/", input$corpus, ".csv")
      d$pool_filters <- list(length = as.integer(input$length), frequency = input$frequency)
    }
    if (p == "factorial") {
      d$paradigm <- "factorial"
      df <- conds(); conditions <- list()
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
      d$conditions <- conditions
      d$n_per_condition <- as.integer(input$n)
      d$match_on <- as.list(input$match_on)
      d$matching <- list(method = input$method)
      if (!is.null(input$nsets) && input$nsets >= 2) d$resample <- list(n_sets = as.integer(input$nsets))
      d$counterbalance <- list(lists = as.integer(input$lists))
    } else if (p == "lexical_decision") {
      d$paradigm <- "lexical_decision"
      d$items <- list(source = "generate")
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
    run_d <- d
    if (!is.null(spec$lexicon_abs)) run_d$lexicon <- spec$lexicon_abs
    if (!is.null(spec$items_abs)) run_d$items$path <- spec$items_abs
    tmp <- tempfile("lexsync_app_"); dir.create(tmp)
    dp <- file.path(tmp, "design.yaml"); yaml::write_yaml(run_d, dp)
    out <- file.path(tmp, "output")
    res <- tryCatch(
      withCallingHandlers(
        run_pipeline(dp, schema_path = SCHEMA_PATH, outdir = out, verbose = FALSE),
        message = function(m) invokeRestart("muffleMessage")),
      error = function(e) structure(list(), error = conditionMessage(e)))
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
    div(class = "alert alert-success mt-3", sprintf("Done — %d rows selected.", nrow(b$stimuli)))
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
    if (is.null(b$comparisons))
      return(div(class = "alert alert-info",
                 "This paradigm draws from an item table, so no corpus-matching report is produced."))
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
        c <- b$comparisons; v <- abs(c$cohens_d); names(v) <- c$dimension
        op <- par(mar = c(4, 4, 1, 1)); on.exit(par(op))
        barplot(v, ylab = "|Cohen's d|", col = ifelse(v > 1, "#d95f02", "#1b9e77"), las = 1)
        abline(h = 0.5, lty = 2, col = "grey50")
      }, height = 240),
      helpText("Absolute standardised mean difference by dimension. Manipulated dimensions ",
               "stand high; matched dimensions sit near zero (below the 0.5-SD line)."),
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
      helpText("The R and Python engines select byte-identical stimuli from this ",
               "configuration; only the seeded trial order differs by ecosystem.")
    )
  })

  output$dl_zip <- downloadHandler(
    filename = function() paste0(bundle()$design$name, "_lexsync.zip"),
    content = function(file) {
      b <- bundle(); wd <- getwd(); on.exit(setwd(wd))
      cfgfile <- file.path(b$outdir, b$cfg)
      writeLines(clean_yaml(b$design), cfgfile)
      setwd(b$outdir)
      utils::zip(file, files = list.files(".", recursive = TRUE))
    }
  )
}

shinyApp(ui, server)
