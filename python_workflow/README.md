# lexsync (Python)

<!-- badges: start -->
[![python-tests](https://github.com/pablobernabeu/lexsync/actions/workflows/python-tests.yaml/badge.svg)](https://github.com/pablobernabeu/lexsync/actions/workflows/python-tests.yaml)
[![Lifecycle: experimental](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://lifecycle.r-lib.org/articles/stages.html#experimental)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/license/MIT)
<!-- badges: end -->

Multidimensional lexical optimisation and hardware-timed experiment generation.

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

lexsync is not on PyPI yet, so install it from the repository, where the Python
package sits in the `python_workflow/` subdirectory:

```bash
pip install "git+https://github.com/pablobernabeu/lexsync.git#subdirectory=python_workflow"
```

The `corpora` extra adds the 'wordfreq' connector, which reaches roughly forty
languages through a single dependency, and the `experiment` extra adds
'PsychoPy' and 'pyserial'. Note that the `experiment` extra is needed only to run
a generated experiment on hardware, never to generate one:

```bash
pip install "lexsync[corpora] @ git+https://github.com/pablobernabeu/lexsync.git#subdirectory=python_workflow"
```

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
page](https://pablobernabeu.github.io/lexsync/python/about/) carries the same
citation as a formatted reference. A manuscript describing lexsync is in
preparation.

Cite the corpus as well as the software. The corpora are third-party work with
their own terms, and each is credited, with its licence and retrieval date, in
[`corpora/ATTRIBUTION.md`](https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md).

## Licence

MIT. The bundled corpus derivatives are not covered by it: they are released
under CC BY-SA 4.0, as recorded in
[`LICENSE-DATA`](https://github.com/pablobernabeu/lexsync/blob/main/LICENSE-DATA).

## Contributing

Issues and pull requests are welcome, on the [issue
tracker](https://github.com/pablobernabeu/lexsync/issues) of the repository that
holds both twins. A report that includes the design YAML and the run log is one
someone can act on, since between them they pin the inputs and every step that
ran.
