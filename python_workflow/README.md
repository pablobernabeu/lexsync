# lexsync (Python)

<!-- badges: start -->
[![PyPI](https://img.shields.io/pypi/v/lexsync)](https://pypi.org/project/lexsync/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22906962.svg)](https://doi.org/10.5281/zenodo.22906962)
[![python-tests](https://github.com/pablobernabeu/lexsync/actions/workflows/python-tests.yaml/badge.svg)](https://github.com/pablobernabeu/lexsync/actions/workflows/python-tests.yaml)
[![Lifecycle: experimental](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://lifecycle.r-lib.org/articles/stages.html#experimental)
[![Code: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](https://opensource.org/license/MIT)
[![Data: CC BY-SA 4.0](https://img.shields.io/badge/data-CC_BY--SA_4.0-blue.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
<!-- badges: end -->

Lexical optimisation and hardware-timed experiment generation.

lexsync selects stimuli matched in parallel across several lexical dimensions
(length, frequency, orthographic neighbourhood density and OLD20),
counterbalances them across conditions and lists, and generates the 'PsychoPy',
'OpenSesame' and 'jsPsych' scripts that present them. The two laboratory targets
carry hardware triggers injected at stimulus onset for EEG/ERP synchronisation,
and the browser target is a single shareable HTML file.

This is the feature-parity twin of [the R
package](https://pablobernabeu.github.io/lexsync/r/) of the same name, which
offers the same workflow in R. The two engines select byte-identical stimuli
under the deterministic matching methods, and are built from one repository and
released under one version.

Documentation, including the guides and the full API reference, is at
<https://pablobernabeu.github.io/lexsync/python/>.

## Install

The package is not on PyPI yet, so install it from the repository, where the
Python package sits in the `python_workflow/` subdirectory:

```bash
pip install "git+https://github.com/pablobernabeu/lexsync.git#subdirectory=python_workflow"
```

The `corpora` extra adds the 'wordfreq' connector, which reaches roughly forty
languages through a single dependency, and the `experiment` extra adds
'PsychoPy' and 'pyserial'. Note that the `experiment` extra is needed only to run
a generated experiment on hardware, never to generate one. An extra goes in
brackets after the package name:

```bash
pip install "lexsync[corpora] @ git+https://github.com/pablobernabeu/lexsync.git#subdirectory=python_workflow"
pip install "lexsync[experiment] @ git+https://github.com/pablobernabeu/lexsync.git#subdirectory=python_workflow"
```

## Quick start

The package bundles a 3000-word slice of an English lexicon and a copy of the
global schema, so the example below runs straight after installation, from any
working directory, with no corpus to download and nothing to configure. It
contrasts high- with low-frequency words while equating them, item by item, on
length, orthographic neighbourhood density and OLD20.

```python
from importlib.resources import files

import yaml

import lexsync

data = files("lexsync") / "data"
schema = yaml.safe_load((data / "schema.yaml").read_text(encoding="utf-8"))

design = {
    "name": "quick_start",
    "language": "english",
    "n_per_condition": 60,
    "pool_filters": {"length": [3, 8], "frequency": [3.8, 7.0]},
    "conditions": [
        {"name": "high_frequency", "define_by": {"frequency": [5.2, 7.0]}},
        {"name": "low_frequency", "define_by": {"frequency": [3.8, 4.4]}},
    ],
    "match_on": ["length", "n_density", "old20"],
    "counterbalance": {"lists": 1},
}

lexicon = lexsync.load_lexicon(str(data / "en_example.csv"), schema, language="english")
pool = lexsync.build_pool(lexicon, design["pool_filters"])
stimuli = lexsync.match_stimuli(pool, design, schema)

report = lexsync.match_report(
    stimuli, ["length", "frequency", "n_density", "old20"], schema
)
print(report["comparisons"].to_string(index=False))
```

The report is the point of the exercise, because it measures what the matching
achieved. Frequency, the manipulation, separates the conditions by nearly six
standard deviations, while each control dimension passes a two one-sided tests
procedure against a bound of *d* = 0.5, so it is shown to be equivalent and not
merely to have escaped a significance test. The [Matching and designs
guide](https://pablobernabeu.github.io/lexsync/python/matching-and-designs/)
reads the report column by column.

## Use

The example below builds a matched stimulus set from a design file and writes
the experiment scripts for it. It reads the schema, the derived corpus and the
design from the repository, so run it from a checkout rather than from an
arbitrary directory.

```python
import yaml, lexsync

schema = yaml.safe_load(open("config/schema.yaml"))
lex = lexsync.load_lexicon("corpora/derived/en.csv", schema, "english")

design = yaml.safe_load(open("config/design_en_freqcontrast.yaml"))
pool = lexsync.build_pool(lex, design["pool_filters"])
stim = lexsync.match_stimuli(pool, design, schema)
# Not optional: this assigns the counterbalancing lists and draws the trial
# order. Exporting without it writes every trial of one condition and then every
# trial of the next, with no `trial` column and no `list` column.
stim = lexsync.counterbalance(stim, design, schema)

report = lexsync.match_report(stim, ["length", "frequency", "n_density", "old20"], schema)
lexsync.export_experiments(
    lexsync.scripting.assign_triggers(stim), design, schema, "output/experiments"
)
```

The same operations are available from the command line, which runs a whole
design end to end, lists the registered corpora and derives a new lexicon:

```bash
lexsync run config/design_en_freqcontrast.yaml
lexsync corpora list
lexsync fetch fr            # build a French lexicon via wordfreq
```

## Citation

Cite the software. The authoritative record is
[`CITATION.cff`](https://github.com/pablobernabeu/lexsync/blob/main/CITATION.cff)
at the root of the repository, which GitHub renders into several formats through
its 'Cite this repository' button. The [About
page](https://pablobernabeu.github.io/lexsync/python/about/) carries a formatted
reference for this package, which gives its version and the concept DOI of the
Zenodo archive, [10.5281/zenodo.22906962](https://doi.org/10.5281/zenodo.22906962). The first DOI in
`CITATION.cff` is the one CRAN assigned to the R package, so it does not
identify the Python package. A manuscript describing lexsync is in preparation.

Cite the corpus as well as the software. The corpora are third-party work with
their own terms, and each is credited, with its licence and retrieval date, in
[`corpora/ATTRIBUTION.md`](https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md).

## Licence

MIT for the code. The bundled corpus derivatives are not covered by it. The
three example lexica, installed as `lexsync/data/en_example.csv`,
`lexsync/data/es_example.csv` and `lexsync/data/zh_example.csv`, are derived from
'wordfreq' and are released under CC BY-SA 4.0, which asks anyone who
redistributes them to credit the corpus authors, say that changes were made and
keep the same terms on any adaptation. `LICENSE.note` states this inside the
distribution itself, alongside `LICENSE`, so the terms travel with the installed
package. The repository keeps the fuller record, including the retrieval date
and checksum of every derived file, in
[`LICENSE-DATA`](https://github.com/pablobernabeu/lexsync/blob/main/LICENSE-DATA).

## Contributing

Issues and pull requests are welcome, on the [issue
tracker](https://github.com/pablobernabeu/lexsync/issues) of the repository that
holds both twins. A report that includes the design YAML and the run log is one
someone can act on, since between them they pin the inputs and every step that
ran.
