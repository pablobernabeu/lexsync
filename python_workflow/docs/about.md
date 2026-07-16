# About

lexsync is a cross-platform toolkit for psycholinguistics. It selects stimuli matched or controlled
across several lexical dimensions, counterbalances them, and generates the experiment that presents
them, with EEG triggers bound to stimulus onset on the laboratory targets. It ships as two
structurally identical packages, one for R and one for Python, and the two select byte-identical
stimuli under the deterministic matching methods.

## What it is for

The tools in this area are good and fragmented. Stimulus-control packages such as LexOPS, LIBRA and
LASTU match words but stop before the experiment exists. Experiment builders such as PsychoPy and
OpenSesame present stimuli but do not match them. The R and Python ecosystems rarely meet, and most
matching tools target a single language. lexsync spans the whole path, from a many-language corpus
through parallel multidimensional matching and counterbalancing to flip-locked experiment scripts,
identically in both languages.

Beyond matching, it treats the stimulus set as a research artefact rather than a by-product. Each run
emits a materials datasheet carrying its provenance, its checksums, the realised control with an
effect size, a confidence interval and an equivalence test, and a pre-registration skeleton. A
design can therefore be shared and reproduced rather than only described in prose.

## The two packages

This site documents the Python package. The R package is documented at its own site, and the two are
built from one repository and released in lockstep under one version.

[The R package](https://pablobernabeu.github.io/lexsync/r/){ .md-button }
[Source on GitHub](https://github.com/pablobernabeu/lexsync){ .md-button }

Two browser front-ends also live in the repository, a Streamlit app over the Python engine and a
Shiny app over the R engine. Each lets a researcher assemble a design without writing code and then
exports the configuration and the one-line R, Python and command-line code that reproduces the run,
so the interface produces shareable artefacts rather than a black box. Both call their engine
directly and need a local install, so neither is published beside this site. See
[`apps/README.md`](https://github.com/pablobernabeu/lexsync/blob/main/apps/README.md).

## How to cite

Cite the software. The authoritative record is
[`CITATION.cff`](https://github.com/pablobernabeu/lexsync/blob/main/CITATION.cff) at the root of the
repository, which GitHub also renders into several formats through the "Cite this repository" button.
Rendered as a reference, version 0.1.0 is:

> Bernabeu, P. (2026). *lexsync: multidimensional lexical optimisation and hardware-timed experiment
> generation* (Version 0.1.0) [Computer software]. https://github.com/pablobernabeu/lexsync

A manuscript describing lexsync is in preparation. `CITATION.cff` lists it as the preferred citation
once it exists, under the title *lexsync: a cross-platform pipeline for multidimensional lexical
optimisation and hardware-timed experiment generation*, but it is unpublished and has no venue, so
until it does the software reference above is the one to use. There is no deposited DOI.

Cite the corpus as well. The software citation covers the tool, not the data it drew your items
from, and the corpora are third-party work with their own terms. Every one is cited, with its
licence and retrieval date, in
[`corpora/ATTRIBUTION.md`](https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md),
and each run's datasheet records which source file it read and its SHA-256.

## Licence

The source code is under the MIT licence. The bundled corpus derivatives are under CC BY-SA 4.0 and
are not covered by it. See [Licence](licence.md) for the text and the distinction.

## Author

lexsync is developed by [Pablo Bernabeu](https://pablobernabeu.github.io)
([ORCID 0000-0003-1083-2460](https://orcid.org/0000-0003-1083-2460)). Authorship on the forthcoming
manuscript is provisional and will be settled before submission.

Bug reports and feature requests belong on the
[issue tracker](https://github.com/pablobernabeu/lexsync/issues). A report that includes the design
YAML and the run log is one someone can act on, since between them they pin the inputs and every step
that ran.
