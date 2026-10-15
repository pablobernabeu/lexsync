# lexsync web applications

Two browser front-ends for lexsync, one per language, mirroring the dual-language
package. Each assembles a design through the interface, runs the same verified
pipeline that the package and command line use, displays the matched stimuli, the
realised-control report and the materials datasheet, and exports the reproducible
R, Python and command-line code that reproduces the operation. The applications are
front-ends only: every result they show is produced by the installed lexsync
package, and the design they build is an ordinary YAML configuration file. Under
the deterministic matching methods, which include the default, the two engines
select byte-identical stimuli, so a design built in either application runs the
same way in either ecosystem.

Both cover the corpus-matching workflow (conditions defined by numeric windows or by
a categorical column, including full 2 × 2 cells), the lexical-decision paradigm with
generated pseudowords, and the item-table paradigms (priming and self-paced
reading), along with the four matching methods (standardised Euclidean, joint,
Mahalanobis and optimal), per-dimension tolerance windows, counterbalancing and item
resampling.

## Python (Streamlit)

Requirements: `lexsync` and `streamlit` 1.49 or later. The first of the three
commands below installs lexsync from this checkout, the second installs Streamlit
and the third starts the app.

```bash
pip install -e python_workflow
pip install "streamlit>=1.49"
streamlit run apps/python_streamlit/lexsync_app.py
```

The app opens at <http://localhost:8501>.

## R (Shiny)

Requirements: the `lexsync` package and `shiny`, `bslib`, `DT`. The downloads also
want `zip`. Without it the app falls back to an external zip tool, and refuses the
download when none is on the path.

```r
install.packages(c("shiny", "bslib", "DT", "zip"))
# install lexsync first, with install.packages("lexsync") from CRAN or, to
# match this checkout, with devtools::install("R_workflow")
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
- Both applications open on `en_v2`, the English lexicon screened against
  SUBTLEX-US, and keep only the forms it leaves unmarked until 'Screened forms only'
  is cleared. A preset sets the conditions, the matched dimensions and the matching
  method together. Both applications warn when 'Match on' names a dimension whose
  windows differ between conditions, and neither runs a factorial design with
  nothing to match on.
- The reproducible-code panel writes repository-relative paths (for example
  `corpora/derived/en.csv`), so the exported configuration and one-line call run
  unchanged from the repository root. The command lines quote the design file's
  name and run in bash, `cmd.exe` and PowerShell.
- Each application runs that code in a temporary folder laid out like its download:
  the design, `config/schema.yaml`, the lexicon or item table at the path the design
  names, and the outputs under `output/`. The Download tab archives that folder, so
  the datasheet in it checksums the design beside it, names no path outside it, and
  the exported code reruns in the unzipped folder. The PsychoPy and OpenSesame
  downloads are archives holding each experiment with the tables it loads.
- The `standardised_euclidean` and `joint` methods select byte-identical stimuli in
  both engines. `mahalanobis` and `optimal` use a covariance inverse or an assignment
  solver, so the two engines agree closely but not byte-for-byte, and both the
  reproducible-code panel and the datasheet tab report which case applies, from the
  run's datasheet. The `optimal` method needs the R `clue` package.
