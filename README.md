# lexsync

<!-- badges: start -->
[![R-CMD-check](https://github.com/pablobernabeu/lexsync/actions/workflows/R-CMD-check.yaml/badge.svg)](https://github.com/pablobernabeu/lexsync/actions/workflows/R-CMD-check.yaml)
[![python-tests](https://github.com/pablobernabeu/lexsync/actions/workflows/python-tests.yaml/badge.svg)](https://github.com/pablobernabeu/lexsync/actions/workflows/python-tests.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
<!-- badges: end -->

**Multidimensional lexical optimisation and hardware-timed experiment generation, in R and Python.**

`lexsync` is a research-grade, cross-platform toolkit for building psycholinguistic
stimulus sets and the experiments that present them. From a word-frequency corpus in
any of dozens of languages it will select stimuli that are matched in parallel across
several lexical dimensions (length, frequency, orthographic neighbourhood density and
more), counterbalance them across conditions and lists, and then *generate the
presentation script* for 'PsychoPy' or 'OpenSesame' with hardware triggers injected at
stimulus onset for EEG/ERP synchronisation. The trial is described declaratively as a
sequence of events, so the same engine builds **factorial word studies, lexical
decision with deterministically generated pseudowords, priming and self-paced
reading** from configuration rather than code, with word, pseudoword, paired and
sentence stimuli. It ships as two structurally identical, independently installable
packages — a CRAN-ready R package and a PyPI-ready Python package — so a laboratory can
adopt it in whichever ecosystem it already uses.

`lexsync` generalises the FAIR artificial-grammar workflow of González Alonso et al.
(2025) into a reusable tool.

## Why lexsync

Existing tools are powerful but fragmented. Stimulus-control packages such as 'LexOPS',
'LIBRA' and 'LASTU' match words but stop short of building the experiment; experiment
builders such as 'PsychoPy' and 'OpenSesame' present stimuli but do not match them; the
R and Python ecosystems rarely meet; and most matching tools target a single language.
`lexsync` closes this gap by spanning the whole path — *many-language corpus → parallel
multidimensional matching → counterbalancing → genuinely flip-locked, cross-platform
experiment scripts* — identically in R and Python.

A concrete methodological gain: the PsychoPy backend binds each onset trigger to the
exact buffer flip on which the stimulus appears, using `win.callOnFlip`, rather than
sending it from a later, sequence-ordered item.

## Repository layout

```
lexsync/
├── R_workflow/        CRAN-ready R package 'lexsync'
├── python_workflow/   PyPI-ready Python package 'lexsync'
├── corpora/           many-language corpus registry + ingestion + attribution
├── config/            global schema + per-design configurations
├── output/            generated stimuli, reports and experiment scripts
└── manuscript/        reproducible Quarto manuscript for Behavior Research Methods
```

Both packages expose the same modules — `querying`, `matching`, `counterbalancing`,
`scripting`, `validation`, `logging`, `corpora` — and the same orchestrator,
`run_pipeline`.

## Quick start

### R

```r
install.packages(c('dplyr','tidyr','stringr','readr','yaml','stringdist'))
# from the repository root:
source('R_workflow/run_pipeline.R')          # runs the demonstrations
# or, once installed:  lexsync::run_pipeline('config/design_en_freqcontrast.yaml')
```

### Python

```bash
python -m pip install -e "python_workflow[dev]"
python python_workflow/run_pipeline.py        # runs the demonstrations
# or, once installed:  lexsync run config/design_en_freqcontrast.yaml
```

Neither the generation step nor its tests require 'PsychoPy', 'OpenSesame' or any
parallel-port driver — those are needed only when the generated experiment is actually
run on hardware. The whole demonstration therefore reproduces with no special equipment.

## Corpora

Languages are supplied through `corpora/registry.yaml`. Two connectors are provided: a
curated SUBTLEX-family/'openlexicon' connector (individually citable corpora under
CC BY-SA 4.0) and an optional 'wordfreq' connector that unlocks roughly forty languages
through a single dependency. English, Spanish and Mandarin Chinese are bundled and
demonstrated end to end — the last as a logographic-script example, showing that the
matching and script generation are not limited to alphabetic writing — and further
languages are fetched on demand into a user cache. Every corpus is cited, with its
licence and retrieval date, in `corpora/ATTRIBUTION.md`.

## Extending lexsync

- **Add a paradigm** — add an entry to the `PARADIGMS` registry in
  `R_workflow/R/paradigms.R` and `python_workflow/src/lexsync/paradigms.py`, giving its
  default trial-event sequence, required fields and counterbalancing recipe; both
  backends then render it with no further code.
- **Add a lexical dimension** — edit `compute_dimensions()` in `R_workflow/R/querying.R`
  and `python_workflow/src/lexsync/querying.py`, then list it under `dimensions` in
  `config/schema.yaml`.
- **Add a presentation target** — add an `export_<target>()` function in
  `R_workflow/R/scripting.R` and `python_workflow/src/lexsync/scripting.py` that walks
  the same rendered event list.
- **Add a corpus or language** — add an entry to `corpora/registry.yaml`; no code change
  is required for SUBTLEX-family or 'wordfreq' sources.

## Tests and continuous integration

The R package carries a `testthat` suite and the Python package a `pytest` suite,
the latter including a mock-'PsychoPy' harness that checks the onset trigger is
flip-locked, a structural validator for the generated 'OpenSesame' experiment and
an R-versus-Python parity test. GitHub Actions run `R CMD check` on Ubuntu, macOS
and Windows (R release and development) and the Python tests on Python 3.10–3.13.

## Licensing and citation

Source code is under the MIT License (`LICENSE`). Bundled corpus derivatives are under
CC BY-SA 4.0 (`LICENSE-DATA`, `corpora/ATTRIBUTION.md`). If you use `lexsync`, please
cite the software (`CITATION.cff`) and the accompanying article.
