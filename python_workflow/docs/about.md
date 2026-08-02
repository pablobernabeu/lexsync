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
Rendered as a reference, the current version is:

<!-- The reference below follows the family form used on every other About page in this family,
     "R package version X" / "Python package version X", so that the two twins read alike and both
     agree with what citation("lexsync") prints on the R side.

     The version used to be written out by hand three times on this page, in the reference, in the
     `note` field of the BibTeX entry and percent-encoded inside the download URI. That is how a page
     in this family fell a whole minor version behind its release without anyone noticing. All three
     copies now come from the installed package, so they can no longer disagree with each other or
     with the release. Two copies stay out of reach of the block below, because neither file can run
     code, and both still have to be bumped by hand when a release is cut: the `extra.version` chip
     in mkdocs.yml and the `version` field in CITATION.cff.

     The download URI is the entry itself, so the download needs no .bib file shipped beside the
     site. -->

````python exec="1"
import urllib.parse

from lexsync import __version__ as version

bibtex = (
    "@Manual{lexsync,\n"
    "  title  = {{lexsync}: Multidimensional lexical optimisation and hardware-timed experiment generation},\n"
    "  author = {Pablo Bernabeu},\n"
    "  year   = {2026},\n"
    f"  note   = {{Python package version {version}}},\n"
    "  url    = {https://github.com/pablobernabeu/lexsync},\n"
    "}"
)

# The download link encodes the very string the fenced block below shows, so the
# two can never disagree. safe="" is deliberate: the default would leave the
# slashes in the repository URL unescaped.
data_uri = "data:application/x-bibtex;charset=utf-8," + urllib.parse.quote(bibtex, safe="")

print(
    "> Bernabeu, P. (2026). lexsync: Multidimensional lexical optimisation and hardware-timed experiment\n"
    f"> generation. Python package version {version}. https://github.com/pablobernabeu/lexsync\n"
)

# The entry is printed as a real fenced block rather than as ready-made HTML, so
# that Material gives it BibTeX highlighting and a copy button of its own. Printing
# a fence from inside a fence is why the enclosing one takes four backticks. The id
# is where the Copy BibTeX button below reads the entry from.
print("```{ .bibtex #lexsync-bibtex }")
print(bibtex)
print("```")

print(
    '\n<p class="mrd-cite-actions">\n'
    '<button type="button" class="md-button" onclick="lexsyncCopyBibtex(this)">Copy BibTeX</button>\n'
    f'<a class="md-button" download="lexsync.bib" href="{data_uri}">Download .bib</a>\n'
    '</p>'
)
````

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
directly and need a local install, so neither is published beside this site. [The app](the-app.md)
walks through the Streamlit one control by control, and
[`apps/README.md`](https://github.com/pablobernabeu/lexsync/blob/main/apps/README.md) covers
launching either of them.

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
