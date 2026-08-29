# lexsync <img src="R_workflow/man/figures/logo.svg" align="right" height="139" alt="" />

<!-- badges: start -->
[![R-CMD-check](https://github.com/pablobernabeu/lexsync/actions/workflows/R-CMD-check.yaml/badge.svg)](https://github.com/pablobernabeu/lexsync/actions/workflows/R-CMD-check.yaml)
[![python-tests](https://github.com/pablobernabeu/lexsync/actions/workflows/python-tests.yaml/badge.svg)](https://github.com/pablobernabeu/lexsync/actions/workflows/python-tests.yaml)
[![Lifecycle: experimental](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://lifecycle.r-lib.org/articles/stages.html#experimental)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/license/MIT)
<!-- badges: end -->

Lexical optimisation and hardware-timed experiment generation, in
R and Python.

`lexsync` is a cross-platform toolkit for building psycholinguistic stimulus sets
and the experiments that present them. From a word-frequency corpus in any of dozens
of languages it will select stimuli that are matched in parallel across several
lexical dimensions (length, frequency, orthographic neighbourhood density and more)
and counterbalance them across conditions and lists. It then generates the
presentation experiment for 'PsychoPy', 'OpenSesame' or the browser ('jsPsych'). The
laboratory targets carry hardware triggers injected at stimulus onset for EEG/ERP
synchronisation, and the web target is a single shareable HTML file (the jsPsych
library itself loads from a CDN, so the machine running it needs an internet
connection).

The trial is described declaratively as a sequence of events, so the same engine
builds factorial word studies, lexical decision with deterministically generated
pseudowords, priming, self-paced reading and cued categorisation from configuration
rather than code, with word, pseudoword, paired and sentence stimuli, and with
practice and filler blocks that run but are not analysed. It ships as two structurally identical,
independently installable packages, a CRAN-ready R package and a PyPI-ready Python
package, so a laboratory can adopt it in whichever ecosystem it already uses.

Beyond matching, `lexsync` treats the stimulus set as a reproducible research
artefact. Every run is deterministic and seeded, and under the two deterministic
matching methods it selects byte-identical stimuli from either engine. Each run
also ships a machine- and human-readable materials
datasheet: its provenance, checksums, the realised control (effect size, confidence
interval and equivalence test) and a pre-registration skeleton. A design can
therefore be shared and reproduced rather than only described in prose.

## Documentation

The documentation for both packages is published at
[pablobernabeu.github.io/lexsync](https://pablobernabeu.github.io/lexsync/):

- R package (pkgdown): <https://pablobernabeu.github.io/lexsync/r/>
- Python package (mkdocs): <https://pablobernabeu.github.io/lexsync/python/>

Each site carries the complete function reference alongside guides to matching and
designs, to experiments and triggers, and to reproducibility and parity. Every worked
design in this repository also ships as a browser experiment, published beside the
documentation. The [lexical-decision
demonstration](https://pablobernabeu.github.io/lexsync/demos/en_lexdec_english.html)
runs with nothing to install.

## Why lexsync

Existing tools are capable but fragmented. Stimulus-control packages such as 'LexOPS',
'LIBRA' and 'LASTU' match words but stop short of building the experiment, while
experiment builders such as 'PsychoPy' and 'OpenSesame' present stimuli but do not
match them. The R and Python ecosystems rarely meet, and most matching tools target a
single language. `lexsync` spans the whole path in both languages, from a
many-language corpus through parallel multidimensional matching and counterbalancing
to flip-locked, cross-platform experiment scripts. Under the two deterministic
matching methods the two engines select byte-identical stimuli, deal them into the
same lists and conditions, and order the trials identically, so the generated
experiment files themselves match byte for byte. The two linear-algebra methods
agree closely without carrying that guarantee, and each run's datasheet records
which case applies. Nothing in the package draws a random number: trial order comes
from a keyed hash of the design and the seed, which is what lets a seeded shuffle
mean the same thing in both languages.

The PsychoPy backend offers one concrete methodological gain: it binds each onset
trigger to the exact buffer flip on which the stimulus appears, using `win.callOnFlip`,
rather than sending it from a later, sequence-ordered item.

## Repository layout

The two packages sit side by side, with the corpora, configurations, item tables and
generated output they share held at the root:

```
lexsync/
├── R_workflow/        CRAN-ready R package 'lexsync'
├── python_workflow/   PyPI-ready Python package 'lexsync'
├── corpora/           many-language corpus registry + ingestion + attribution
├── config/            global schema + per-design configurations
├── items/             example item tables (priming pairs, SPR sentences)
├── templates/         experiment script templates (PsychoPy, OpenSesame, jsPsych)
├── output/            generated stimuli, reports and experiment scripts
└── apps/              browser apps (Streamlit + Shiny) that export reproducible code
```

Both packages expose parallel modules, including `querying`, `matching`,
`counterbalancing`, `scripting`, `validation`, `logging` and `corpora`, and the same
orchestrator, `run_pipeline`.

## Quick start

The two blocks below run the bundled demonstration designs end to end from a checkout
of this repository, writing the matched stimuli, the reports and the generated
experiments into `output/`. Either engine produces the same result, so run whichever
language you work in.

In R:

```bash
Rscript -e "install.packages(c('readr','yaml','stringdist','stringi','jsonlite','digest'))"
# from the repository root:
Rscript R_workflow/run_pipeline.R             # runs the demonstrations
# or, once installed:  Rscript -e "lexsync::run_pipeline('config/design_en_freqcontrast.yaml')"
```

In Python:

```bash
python -m pip install -e "python_workflow[dev]"
python python_workflow/run_pipeline.py        # runs the demonstrations
# or, once installed:  lexsync run config/design_en_freqcontrast.yaml
```

The R line above installs that package's required dependencies. One matching method,
`optimal`, additionally needs `clue` for its assignment solver. The Python engine
reaches the same solver through `scipy`, which it requires anyway.

To install the packages themselves rather than run them from a checkout, see
[`R_workflow/README.md`](R_workflow/README.md) and
[`python_workflow/README.md`](python_workflow/README.md).

Neither the generation step nor its tests require 'PsychoPy', 'OpenSesame' or any
parallel-port driver. These are needed only when the generated experiment is run on
hardware. The whole demonstration therefore reproduces with no special equipment.

## Web apps

Two browser front-ends in `apps/` let a researcher assemble a design without writing
code, run the verified pipeline and view the matched stimuli, the realised-control
report and the materials datasheet. Each one also exports the design configuration
and the one-line R, Python and command-line code that reproduces the operation, so
what the interface yields is a shareable artefact a reader can retrace.
A Streamlit app wraps the Python engine and a Shiny app wraps the R engine, and the
two select byte-identical stimuli. See `apps/README.md` for details.

```bash
streamlit run apps/python_streamlit/lexsync_app.py             # Python
Rscript -e "shiny::runApp('apps/r_shiny', port = 8502)"        # R
```

## Corpora

Languages are supplied through `corpora/registry.yaml`. Two connectors are
provided: a curated SUBTLEX-family/'openlexicon' connector (individually citable
corpora under CC BY-SA 4.0) and a 'wordfreq' connector that reaches roughly
forty languages through a single dependency. English, Spanish and Mandarin
Chinese are bundled and demonstrated end to end (the last a logographic-script
example, showing that the matching and script generation are not limited to
alphabetic writing). Those three come from 'wordfreq', not from the openlexicon
connector, and carry its CC BY-SA 4.0 data terms. The registry's SUBTLEX entries
are separate corpora a user loads directly. Further languages are fetched on
demand into a user cache, though not equally from both engines. The
'openlexicon' connector is available in R and Python alike, whereas 'wordfreq'
is Python-only: `lexsync fetch <language>` derives those lexica from the Python
package, and the R package can read the result as an ordinary corpus but cannot
build one itself. An R-only laboratory therefore reaches the wider language set
only through lexica derived elsewhere. Every corpus is cited, with its licence
and retrieval date, in `corpora/ATTRIBUTION.md`. The bundled corpora are a
fixed, checksummed snapshot, so the demonstrations reproduce with no download.
'wordfreq' itself was frozen in 2024, giving a stable snapshot of usage through
roughly 2021, which keeps fetched corpora reproducible where a live source would
let them drift.

## Extending lexsync

Each extension point is a pair of parallel edits, one in each engine, and the rest of
the pipeline picks the addition up without further change.

To add a paradigm, add an entry to the `PARADIGMS` registry in
`R_workflow/R/paradigms.R` and `python_workflow/src/lexsync/paradigms.py`, giving its
default trial-event sequence, required fields and counterbalancing recipe. Both
backends then render it with no further code.

To add a lexical dimension, add the computation in `R_workflow/R/querying.R` and
`python_workflow/src/lexsync/querying.py`, alongside `add_neighbourhood()` and
`add_bigram_frequency()`, then list it under `dimensions` in `config/schema.yaml`.

To add a presentation target, add an `export_<target>()` function in
`R_workflow/R/scripting.R` and `python_workflow/src/lexsync/scripting.py` that walks
the same rendered event list.

To add a corpus or language, add an entry to `corpora/registry.yaml`. No code change
is required for SUBTLEX-family or 'wordfreq' sources.

## Tests and continuous integration

The R package carries a `testthat` suite and the Python package a `pytest` suite,
the latter including a mock-'PsychoPy' harness that checks the onset trigger is
flip-locked, a structural validator for the generated 'OpenSesame' experiment and
an R-versus-Python parity test. GitHub Actions run `R CMD check` on Ubuntu, macOS
and Windows under the current R release, on Ubuntu and Windows under R-devel and on
Ubuntu under the previous release, and the Python tests on Python 3.10–3.14.

## Matching methods

Four matching methods are available, set with `matching.method` in a design: the
default `standardised_euclidean` (greedy nearest-neighbour on z-scored
dimensions), `joint` (optimal-greedy pairing for a two-condition design),
`mahalanobis` (a covariance-aware distance that down-weights correlated
dimensions; Rubin, 1980; Stuart, 2010) and `optimal` (globally optimal
assignment for two conditions; Gu & Rosenbaum, 1993). The R and Python engines
select byte-identical stimuli for `standardised_euclidean` and `joint`. The
`mahalanobis` and `optimal` methods are not guaranteed byte-identical across
engines, because they use a covariance-matrix inverse and an assignment solver
whose last bits can differ between the two linear-algebra backends.
`mahalanobis` usually still agrees exactly, while `optimal` selects an
equally-optimal but often different set. Each run's datasheet records which case
applies.

## Continuous designs

A design may replace its discrete `conditions` with a `continuous:` block,
naming a predictor and the controls to hold constant. lexsync then selects a set
that spans the predictor's range evenly while keeping the controls near-constant
and near-uncorrelated with it, ready for analysis by regression or a mixed model
(Kuperman, 2015; Liben-Nowell et al., 2019). The datasheet reports the
predictor's span, the predictor-control correlations and a suggested regression
model, and the two engines select byte-identical stimuli. See
`config/design_en_freqcontinuous.yaml`.

## Pseudoword generation

The lexical-decision paradigm generates a length-matched pseudoword for each word.
Two methods are available via `items.generation.method`: the default
`letter_substitution` (change the fewest single letters, keeping every bigram
attested) and `subsyllabic` (split each word into onset/nucleus/coda constituents
and swap whole constituents for attested same-role, same-length alternatives, so
the pseudowords keep their syllabic structure, a deterministic orthographic
approximation of Wuggy; Keuleers & Brysbaert, 2010). Both preserve length and
select byte-identical stimuli across the two engines. See
`config/design_en_lexdec_wuggy.yaml`.

## Roadmap

lexsync sits within an established ecosystem of stimulus tools: LexOPS, Match, SOS
and LIBRA for matching, and Wuggy for pseudowords. The roadmap drawn from that
initial competitor and literature review is now delivered, covering covariance-aware
and optimal matching, a distributional balance diagnostic, continuous designs and
Wuggy-style pseudowords. Further norm dimensions (concreteness, age of acquisition, English
Lexicon Project behavioural measures) are supported today through the `merge_norms`
connector, which joins any word-keyed norm table so the matcher can equate on it.
Future directions (tracked in `CHANGELOG.md`) are more bundled languages and, should
a determinism-safe implementation be found, promoting a covariance-aware distance to
the default. The cross-engine byte-identical guarantee for the deterministic methods
is a hard constraint on which algorithms can be adopted as defaults.

## Citation

If you use `lexsync`, please cite the software. The authoritative record is
[`CITATION.cff`](CITATION.cff), which GitHub renders into several formats through its
'Cite this repository' button, and each package's About page carries the same citation
as a formatted reference. A manuscript describing lexsync is in preparation.

Cite the corpus as well as the software. The corpora are third-party work with their
own terms, and each is credited, with its licence and retrieval date, in
[`corpora/ATTRIBUTION.md`](corpora/ATTRIBUTION.md). Each run's datasheet records which
source file it read, and its SHA-256.

## Licence

The source code is under the MIT licence ([`LICENSE`](LICENSE)). The bundled corpus
derivatives are not covered by it: they are released under CC BY-SA 4.0, as recorded
in [`LICENSE-DATA`](LICENSE-DATA).

## Contributing

Issues and pull requests are welcome, on the [issue
tracker](https://github.com/pablobernabeu/lexsync/issues). A report that includes the
design YAML and the run log is one someone can act on, since between them they pin the
inputs and every step that ran.

## References

Gu, X. S., & Rosenbaum, P. R. (1993). Comparison of multivariate matching methods:
Structures, distances, and algorithms. *Journal of Computational and Graphical
Statistics*, *2*(4), 405–420. https://doi.org/10.1080/10618600.1993.10474623

Keuleers, E., & Brysbaert, M. (2010). Wuggy: A multilingual pseudoword generator.
*Behavior Research Methods*, *42*(3), 627–633. https://doi.org/10.3758/BRM.42.3.627

Kuperman, V. (2015). Virtual experiments in megastudies: A case study of language
and emotion. *Quarterly Journal of Experimental Psychology*, *68*(8), 1693–1710.
https://doi.org/10.1080/17470218.2014.989865

Liben-Nowell, D., Strand, J., Sharp, A., Wexler, T., & Woods, K. (2019). The danger
of testing by selecting controlled subsets, with applications to spoken-word
recognition. *Journal of Cognition*, *2*(1), Article 2. https://doi.org/10.5334/joc.51

Rubin, D. B. (1980). Bias reduction using Mahalanobis-metric matching. *Biometrics*,
*36*(2), 293–298. https://doi.org/10.2307/2529981

Stuart, E. A. (2010). Matching methods for causal inference: A review and a look
forward. *Statistical Science*, *25*(1), 1–21. https://doi.org/10.1214/09-STS313
