# Launcher for the lexsync Shiny app.
#
#   Rscript apps/r_shiny/run.R [port]
#
# It fixes the host and port and never tries to open a browser, so the server
# starts identically in a terminal, a container, or a headless preview/CI sandbox.
# (A server started with an auto-launched browser or an unbound port can exit
# immediately when it is backgrounded, which is the usual cause of a Shiny app
# that "won't stay up" in an automated environment.) The app is run from the
# repository root so it finds corpora/derived and items/.

args <- commandArgs(trailingOnly = TRUE)
port <- if (length(args) >= 1L && nzchar(args[[1]])) as.integer(args[[1]]) else 8502L

all_args <- commandArgs(FALSE)
file_arg <- sub("^--file=", "", all_args[grepl("^--file=", all_args)])
app_dir <- if (length(file_arg)) dirname(normalizePath(file_arg[[1]])) else "apps/r_shiny"

root <- normalizePath(file.path(app_dir, "..", ".."), mustWork = FALSE)
if (dir.exists(file.path(root, "corpora", "derived"))) setwd(root)

options(shiny.launch.browser = FALSE, shiny.host = "127.0.0.1", shiny.port = port)
cat(sprintf("[lexsync] Shiny app starting on http://127.0.0.1:%d (Ctrl-C to stop)\n", port))
shiny::runApp(app_dir, port = port, host = "127.0.0.1", launch.browser = FALSE)
