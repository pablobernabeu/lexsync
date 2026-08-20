# Contributing to lexsync

Thank you for considering a contribution. Issues and pull requests are both
welcome, whether they fix a bug, improve the documentation or add a feature.

## Reporting a problem or suggesting a feature

Please open an issue at <https://github.com/pablobernabeu/lexsync/issues>. For a
bug, the design YAML and the run log from `output/reports/` are the two things
that make a report actionable, since between them they pin the inputs and every
step that ran.

## The layout

lexsync is one repository holding two packages that must behave identically. The
R package is in `R_workflow/`, the Python package in `python_workflow/`, and the
design configurations, corpora, item tables and generated output they share sit at
the root. The experiment templates exist in three copies, one canonical set under
`templates/` and a mirror inside each package. Keep all three byte-identical.

## Setting up for development

```r
# R, from the repository root
install.packages("R_workflow", repos = NULL, type = "source")
devtools::document("R_workflow")   # after editing roxygen comments
devtools::test("R_workflow")
devtools::check("R_workflow")
```

```bash
# Python, from python_workflow/
pip install -e ".[dev]"
pytest
mkdocs build --strict
```

Running `Rscript R_workflow/run_pipeline.R` and `python python_workflow/run_pipeline.py`
regenerates every artefact under `output/`. Run both, and commit the result of
both together: the two engines write the same experiment files, so regenerating
with only one leaves the repository in a state where they disagree.

## The one convention that governs everything

The two engines must produce byte-identical artefacts, and nothing may draw a
random number. Anything that looks stochastic, such as trial order, is a pure
function of a keyed SHA-256 digest and the seed. The point of the rule is that a
laboratory can run the R package while a collaborator runs the Python one, and the
two of them end up with the same materials down to the byte.

That rules out several ordinary things. Do not call `sample()`,
`numpy.random` or any generator. Do not let a floating-point comparison decide an
outcome without rounding first and breaking ties explicitly, because R and Python
disagree in the last bits: their `exp`, `log` and `**` differ by one unit in the
last place, and `sum()`, `numpy.sum` and a hand-written loop give three different
answers over the same doubles. Do not interpolate a number into a hash key
without formatting it explicitly, since R renders `42.0` as `42` and Python as
`42.0`. When in doubt, compute the value once and read it from a file both engines
share, as the corpora do.

Other conventions: British spelling in prose, durations declared in milliseconds,
and tests that run offline against the bundled example lexicons.

## Submitting a pull request

Base your work on `main` and keep the change focused. Every feature needs a
cross-engine regression test that would fail if the two engines diverged. Add it
to both `R_workflow/tests/testthat/` and `python_workflow/tests/`, and prefer a
shared golden digest computed independently in each, so the two suites fail
together. Update `config/schema.yaml` and the design YAMLs in step with any
configuration change. Continuous integration checks both engines on every push,
including a parity job that regenerates the Python output and compares it to the
committed R reference.

<!-- The Code of Conduct link is absolute on purpose. pkgdown builds a page only
from a file at the R package root, and only this guide is mirrored there, so a
relative CODE_OF_CONDUCT.html would 404 on the R site. An absolute URL resolves
from GitHub, from the R site and from the Python site alike. -->

By contributing you agree that your contribution is licensed under the same MIT
licence as the package, and that you will follow the
[Code of Conduct](https://github.com/pablobernabeu/lexsync/blob/main/.github/CODE_OF_CONDUCT.md).
