# lexsync web applications

Two browser front-ends for lexsync, one per language, mirroring the dual-language
package. Each assembles a design through the interface, runs the same verified
pipeline that the package and command line use, displays the matched stimuli, the
realised-control report and the materials datasheet, and exports the reproducible
R, Python and command-line code that reproduces the operation. The applications are
front-ends only: every result they show is produced by the installed lexsync
package, and the design they build is an ordinary YAML configuration file. The two
engines select byte-identical stimuli, so a design built in either application runs
the same way in either ecosystem.

Both cover the corpus-matching workflow (conditions defined by numeric windows or by
a categorical column, including full 2 × 2 cells), the lexical-decision paradigm with
generated pseudowords, and the item-table paradigms (priming, categorisation and
self-paced reading), along with the four matching methods (standardised Euclidean,
joint, Mahalanobis and optimal), per-dimension tolerance windows, counterbalancing
and item resampling.

## Python (Streamlit)

Requirements: `lexsync` and `streamlit`.

```bash
pip install -e python_workflow        # the lexsync package
pip install streamlit
streamlit run apps/python_streamlit/lexsync_app.py
```

The app opens at <http://localhost:8501>.

## R (Shiny)

Requirements: the `lexsync` package and `shiny`, `bslib`, `DT`. The Download tab also
wants `zip`. Without it the app falls back to an external zip tool, and refuses the
download when none is on the path.

```r
install.packages(c("shiny", "bslib", "DT", "zip"))
# install lexsync from R_workflow first (e.g. devtools::install("R_workflow"))
shiny::runApp("apps/r_shiny", port = 8502)
```

The app opens at <http://localhost:8502>.

## Notes

- Launch either application from the repository root so it can find the bundled
  corpora under `corpora/derived/` and the example item tables under `items/`. The
  Streamlit app also accepts an uploaded lexicon or item-table CSV.
- The corpus-matching dimensions (length, frequency, Coltheart's N, OLD20, syllable
  count, bigram frequency) are computed by the package, and N and OLD20 are
  pre-computed in the bundled corpora, so a run is fast.
- The reproducible-code panel writes repository-relative paths (for example
  `corpora/derived/en.csv`), so the exported configuration and one-line call run
  unchanged from the repository root.
- The `standardised_euclidean` and `joint` methods select byte-identical stimuli in
  both engines. `mahalanobis` and `optimal` use a covariance inverse or an assignment
  solver, so the two engines agree closely but not byte-for-byte, and the datasheet
  tab reports which case applies. The `optimal` method needs the R `clue` package.
