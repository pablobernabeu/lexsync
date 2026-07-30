# About

lexsync is a cross-platform toolkit for psycholinguistics. It selects stimuli matched or controlled
across several lexical dimensions, counterbalances them, and generates the experiment that presents
them, with EEG triggers bound to stimulus onset on the laboratory targets. It ships as two
structurally identical packages, one for R and one for Python, and the two select byte-identical
stimuli under the deterministic matching methods.

## What it is for

The tools in this area are capable but fragmented. Stimulus-control packages such as LexOPS, LIBRA
and LASTU match words but stop before the experiment exists. Experiment builders such as PsychoPy
and OpenSesame present stimuli but do not match them. The R and Python ecosystems rarely meet, and
most matching tools target a single language. lexsync spans the whole path, from a many-language
corpus through parallel multidimensional matching and counterbalancing to flip-locked experiment
scripts, identically in both languages.

Beyond matching, it treats the stimulus set as a research artefact rather than a by-product. Each run
emits a materials datasheet carrying its provenance, its checksums, the realised control with an
effect size, a confidence interval and an equivalence test, and a pre-registration skeleton. A
design can therefore be shared and reproduced rather than only described in prose.

## How to cite

Cite the software. The authoritative record is
[`CITATION.cff`](https://github.com/pablobernabeu/lexsync/blob/main/CITATION.cff) at the root of the
repository, which GitHub also renders into several formats through the 'Cite this repository' button.
Rendered as a reference, version 0.1.0 is:

> Bernabeu, P. (2026). lexsync: Multidimensional lexical optimisation and hardware-timed experiment
> generation. Python package version 0.1.0. https://github.com/pablobernabeu/lexsync

<!-- The reference above follows the family form used on every other About page in this family,
     "R package version X" / "Python package version X", so that the two twins read alike and both
     agree with what citation("lexsync") prints on the R side.

     The version string is hard-coded here, as it is on the other mkdocs About pages, because a
     Markdown page cannot read the installed version the way the R twin's vignette does. On release,
     bump the version in each of the three places it appears on this page: once in the reference
     above, once in the `note` field of the BibTeX entry below, and once inside the download URI,
     where it is percent-encoded (`version%20...`). That URI is the entry itself, so the download
     needs no .bib file shipped beside the site. -->

<div class="mrd-cite-bibtex">
<pre id="lexsync-bibtex"><code>@Manual{lexsync,
  title  = {{lexsync}: Multidimensional lexical optimisation and hardware-timed experiment generation},
  author = {Pablo Bernabeu},
  year   = {2026},
  note   = {Python package version 0.1.0},
  url    = {https://github.com/pablobernabeu/lexsync},
}</code></pre>
<p class="mrd-cite-actions">
<button type="button" class="md-button" onclick="lexsyncCopyBibtex(this)">Copy BibTeX</button>
<a class="md-button" download="lexsync.bib" href="data:application/x-bibtex;charset=utf-8,%40Manual%7Blexsync%2C%0A%20%20title%20%20%3D%20%7B%7Blexsync%7D%3A%20Multidimensional%20lexical%20optimisation%20and%20hardware-timed%20experiment%20generation%7D%2C%0A%20%20author%20%3D%20%7BPablo%20Bernabeu%7D%2C%0A%20%20year%20%20%20%3D%20%7B2026%7D%2C%0A%20%20note%20%20%20%3D%20%7BPython%20package%20version%200.1.0%7D%2C%0A%20%20url%20%20%20%20%3D%20%7Bhttps%3A%2F%2Fgithub.com%2Fpablobernabeu%2Flexsync%7D%2C%0A%7D">Download .bib</a>
</p>
</div>
<script>
function lexsyncCopyBibtex(btn) {
  var code = document.getElementById("lexsync-bibtex");
  navigator.clipboard.writeText(code.innerText).then(function () {
    var label = btn.textContent;
    btn.textContent = "Copied";
    setTimeout(function () { btn.textContent = label; }, 1500);
  });
}
</script>

A manuscript describing lexsync is in preparation. `CITATION.cff` lists it as the preferred citation
once it exists, under the title *lexsync: A cross-platform pipeline for multidimensional lexical
optimisation and hardware-timed experiment generation*, but it is unpublished and has no venue, so
until it does the software reference above is the one to use. There is no deposited DOI.

Cite the corpus as well. The software citation covers the tool, not the data it drew your items
from, and the corpora are third-party work with their own terms. Every one is cited, with its
licence and retrieval date, in
[`corpora/ATTRIBUTION.md`](https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md),
and each run's datasheet records which source file it read and its SHA-256.

## The developer

lexsync is developed by [Pablo Bernabeu](https://pablobernabeu.github.io), a researcher in the
Department of Education at the University of Oxford, with hands-on experience of behavioural
experiments, EEG, corpus analysis, computational modelling and statistics. He develops open,
reproducible research software in R and Python, and is a Fellow of the Software Sustainability
Institute. His [ORCID record](https://orcid.org/0000-0003-1083-2460) lists his other work.
Authorship on the forthcoming manuscript is provisional and will be settled before submission.

## The two packages

This site documents the Python package. The R package is documented at
[its own site](https://pablobernabeu.github.io/lexsync/r/), and the two are built from one
repository and released in lockstep under one version.

[The R package](https://pablobernabeu.github.io/lexsync/r/){ .md-button }
[Source on GitHub](https://github.com/pablobernabeu/lexsync){ .md-button }

Two browser front-ends also live in the repository, a Streamlit app over the Python engine and a
Shiny app over the R engine. Each lets a researcher assemble a design without writing code and then
exports the configuration and the one-line R, Python and command-line code that reproduces the run,
so the interface produces shareable artefacts rather than a black box. Both call their engine
directly and need a local install, so neither is published beside this site. See
[`apps/README.md`](https://github.com/pablobernabeu/lexsync/blob/main/apps/README.md).

## Licence

The source code is under the MIT licence. The bundled corpus derivatives are under CC BY-SA 4.0 and
are not covered by it. See [Licence](licence.md) for the text and the distinction.

## Versioning and archival

lexsync follows semantic versioning, and each release is tagged on GitHub, with the R and the Python
package carrying the same version. Archival on Zenodo has been prepared but not yet carried out, so
although a `.zenodo.json` sits at the root of the repository, nothing has been deposited and no DOI
has been minted. There is therefore no concept DOI to cite, and until a deposit exists the software
reference above, which names the version and the repository, is the one to use. The
[changelog](changelog.md) records what changed in each release.

## Contributing and support

Bug reports and feature requests belong on the
[issue tracker](https://github.com/pablobernabeu/lexsync/issues). A report that includes the design
YAML and the run log is one someone can act on, since between them they pin the inputs and every step
that ran. The [contributing guide](https://github.com/pablobernabeu/lexsync/blob/main/.github/CONTRIBUTING.md) describes the development setup for both
engines and the parity rule that governs every change, and everyone taking part is asked to honour
the [Code of Conduct](https://github.com/pablobernabeu/lexsync/blob/main/.github/CODE_OF_CONDUCT.md).
