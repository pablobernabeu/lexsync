# About

## Citing lexsync

If lexsync contributes to published work, please cite it. Nothing has
been deposited on Zenodo yet, so the citation is a software reference
pointing at the repository rather than at a DOI.

> Bernabeu, P. (2026). lexsync: Multidimensional lexical optimisation
> and hardware-timed experiment generation. R package version 0.1.0.
> <https://github.com/pablobernabeu/lexsync>

```
@Manual{lexsync,
  title  = {{lexsync}: Multidimensional lexical optimisation and hardware-timed experiment generation},
  author = {Pablo Bernabeu},
  year   = {2026},
  note   = {R package version 0.1.0},
  url    = {https://github.com/pablobernabeu/lexsync},
}
```

Copy BibTeX [Download
.bib](data:application/x-bibtex;charset=utf-8,%40Manual%7Blexsync%2C%0A%20%20title%20%20%3D%20%7B%7Blexsync%7D%3A%20Multidimensional%20lexical%20optimisation%20and%20hardware-timed%20experiment%20generation%7D%2C%0A%20%20author%20%3D%20%7BPablo%20Bernabeu%7D%2C%0A%20%20year%20%20%20%3D%20%7B2026%7D%2C%0A%20%20note%20%20%20%3D%20%7BR%20package%20version%200.1.0%7D%2C%0A%20%20url%20%20%20%20%3D%20%7Bhttps%3A%2F%2Fgithub.com%2Fpablobernabeu%2Flexsync%7D%2C%0A%7D)

R users can also retrieve this citation directly with
`citation("lexsync")`. The repository carries a machine-readable
[`CITATION.cff`](https://github.com/pablobernabeu/lexsync/blob/main/CITATION.cff)
as well, which GitHub turns into a ready-made citation through its ‘Cite
this repository’ button and which reference managers can import.

A manuscript describing lexsync is in preparation, under the title
*lexsync: A cross-platform pipeline for multidimensional lexical
optimisation and hardware-timed experiment generation*. It is
unpublished and has no venue as yet. `CITATION.cff` already names it as
the preferred citation for the day it appears, and until then the
software reference above is the one to use.

## Citing the corpus

The software citation covers the tool, not the data your items came
from. The corpora are third-party work with terms of their own, and
every one is credited, with its licence and its retrieval date, in
[`corpora/ATTRIBUTION.md`](https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md).
Each run’s materials datasheet records the source file the run read and
its SHA-256, so the corpus behind a published stimulus set stays
identifiable long after the run, and a reader can check that the file
they hold is the file the selection was made from.

## The developer

[Pablo Bernabeu](https://pablobernabeu.github.io) is a researcher in the
Department of Education at the University of Oxford, with hands-on
experience of behavioural experiments, EEG, corpus analysis,
computational modelling and statistics. He develops open, reproducible
research software in R and Python, and is a Fellow of the Software
Sustainability Institute. His [ORCID
record](https://orcid.org/0000-0003-1083-2460) lists his other work.

lexsync has a feature-parity twin in Python, documented at [its own
site](https://pablobernabeu.github.io/lexsync/python/). The two packages
are built from one repository and released in step under one version,
and under the deterministic matching methods they select byte-identical
stimuli from the same lexicon and design. A group can therefore work in
whichever language suits it without the materials diverging.

## Licence

The source code is released under the [MIT
licence](https://pablobernabeu.github.io/lexsync/r/LICENSE.html). The
corpus derivatives bundled with the package are not covered by it. They
inherit share-alike terms from the corpora they were built from, so they
are distributed under CC BY-SA 4.0 instead, for the reasons
[`LICENSE-DATA`](https://github.com/pablobernabeu/lexsync/blob/main/LICENSE-DATA)
sets out, with the sources and retrieval dates recorded in
[`corpora/ATTRIBUTION.md`](https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md).
The distinction becomes practical if you redistribute a lexicon derived
from the bundled data, since that means crediting the original corpus
authors, saying what was changed and passing the same licence on.
Nothing of the sort applies to the code you write with the package.

## Versioning and archival

lexsync follows semantic versioning, and the R and Python packages share
one version number so that a citation identifies the same state of both.
Releases are tagged on GitHub, and the
[changelog](https://pablobernabeu.github.io/lexsync/r/news/index.html)
records what changed in each of them.

Archival is prepared but not yet done. The deposition metadata sits in
[`.zenodo.json`](https://github.com/pablobernabeu/lexsync/blob/main/.zenodo.json),
waiting on the first published release, and no version has been
archived, so there is no concept DOI to cite. The package is not on CRAN
either. Cite the version, as the reference above does, until an archive
exists to point at.

## Contributing and support

Bugs and feature requests are welcome on the [issue
tracker](https://github.com/pablobernabeu/lexsync/issues), which is also
where questions about a design or a generated experiment are best
raised. The [contributing
guide](https://github.com/pablobernabeu/lexsync/blob/main/.github/CONTRIBUTING.md)
describes the development setup for both engines and the parity rule
that governs every change, and everyone taking part is asked to honour
the [Code of
Conduct](https://github.com/pablobernabeu/lexsync/blob/main/.github/CODE_OF_CONDUCT.md).

A report worth acting on carries the design YAML that was run alongside
the run log that
[`run_pipeline()`](https://pablobernabeu.github.io/lexsync/r/reference/run_pipeline.md)
wrote beside the results. Between them they pin the inputs and every
step that ran, which is usually enough to reproduce a problem without a
further round of questions. Where a corpus is involved, the materials
datasheet from the same run identifies it by path and checksum.
