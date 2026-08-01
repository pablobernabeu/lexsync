# lexsync <span class="mrd-lang">(Python)</span>

Multidimensional lexical optimisation and hardware-timed experiment generation.
{ .mrd-tagline }

lexsync builds psycholinguistic stimulus sets and the experiments that present
them. Give it a word-frequency corpus in any of dozens of languages and a short
design file, and it selects items matched in parallel across several lexical
dimensions, counterbalances them across conditions and lists, and writes the
experiment that runs them on PsychoPy, OpenSesame or in the browser through
jsPsych, with EEG triggers bound to the flip on which the stimulus appears. A
trial is described declaratively, so factorial word studies, lexical decision with
generated pseudowords, priming, self-paced reading and cued categorisation all come
out of the same engine and the same configuration file, as do the practice and
filler blocks that run but are not analysed.

This is the feature-parity twin of [the R package](https://pablobernabeu.github.io/lexsync/r/) of
the same name, which offers the same workflow in R. The two are documented separately but built
from one repository and released under one version.

[Get started](getting-started.md){ .md-button .md-button--primary }
[API reference](api.md){ .md-button }

## The two engines produce the same experiment

The R and Python engines produce byte-identical output: the same stimuli, and the
same generated experiment down to the trial order. Nothing in the package draws a
random number, so neither the platform's locale nor the last bit of a
floating-point sum can change what comes out. A laboratory can run the R package
and a collaborator the Python one, and the materials will agree rather than merely
resemble each other. Continuous integration checks this on 21 worked designs
across English, Spanish and Mandarin Chinese.

Two matching methods are a documented exception: `mahalanobis` and `optimal` rely
on a covariance-matrix inverse and an assignment solver whose last bits differ
between the two linear-algebra backends, so there the engines select equivalent
sets rather than identical ones. Each run's materials datasheet records which case
applies. [Reproducibility and parity](reproducibility-and-parity.md) sets out what
the guarantee promises, how it is enforced and where it stops.

## Install

lexsync is not yet on PyPI, so install it from the repository:

```bash
pip install "git+https://github.com/pablobernabeu/lexsync.git#subdirectory=python_workflow"
```

Once a release is published, `pip install lexsync` will do the same. Generating an experiment needs
neither PsychoPy nor a parallel-port driver, only the core dependencies above. See
[Getting started](getting-started.md) for the optional extras and for the clone-based install that
the 21 worked designs expect.

## Sixty seconds

The package bundles a 3000-word slice of an English lexicon and a copy of the global schema, so the
example below runs immediately after installation, with no corpus to download and nothing to
configure. It contrasts high- with low-frequency words while equating them, item by item, on length,
orthographic neighbourhood density and OLD20.

```python exec="1" source="material-block" result="text" session="index"
from importlib.resources import files

import yaml

import lexsync

data = files("lexsync") / "data"
schema = yaml.safe_load((data / "schema.yaml").read_text(encoding="utf-8"))

design = {
    "name": "sixty_seconds",
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

lexicon = lexsync.load_lexicon(
    str(data / "en_example.csv"), schema, language="english"
)
pool = lexsync.build_pool(lexicon, design["pool_filters"])
stimuli = lexsync.match_stimuli(pool, design, schema)

report = lexsync.match_report(
    stimuli, ["length", "frequency", "n_density", "old20"], schema
)
print(report["comparisons"].to_string(index=False))
```

The report is the point of the exercise, because it states what the matching
achieved rather than asserting that it worked. Frequency, the manipulation,
separates the conditions by nearly six standard deviations. Each control dimension
passes a two one-sided tests procedure against a bound of *d* = 0.5, so it is
shown to be equivalent rather than merely failing to differ significantly.
[Matching and designs](matching-and-designs.md) reads the report column by
column.

Adding the experiment is two more calls. `counterbalance` assigns lists and a seeded trial order,
and `export_experiments` writes all three targets from the same event list:

```python
# illustrative: writes the generated experiment files into the working directory
import os

stimuli = lexsync.counterbalance(stimuli, design, schema)
paths = lexsync.export_experiments(
    stimuli, design, schema, outdir="output/experiments"
)
print(sorted(os.path.basename(p) for p in paths.values()))
```

```text
['sixty_seconds_english.html', 'sixty_seconds_english.osexp', 'sixty_seconds_english_psychopy.py']
```

The jsPsych file is self-contained apart from the library itself, so opening it in
a browser runs the experiment. Every worked design in the repository is published
that way, and the Demo link in the header opens the generated lexical-decision
task.

## Where to go next

[Getting started](getting-started.md) covers installation, the command-line
interface and the anatomy of a design file, which is where most of the work is
done. From there the three guides follow the arc of a study.

- [Matching and designs](matching-and-designs.md): the pool, whether drawn from a
  lexicon or supplied as a list of your own, the four matching methods, the
  continuous alternative to dichotomising a predictor, resampling items as a random
  factor, and pseudoword generation.
- [Experiments and triggers](experiments-and-triggers.md): the declarative trial
  model, the five paradigms, counterbalancing, practice and filler blocks, and the
  three presentation targets, including where the EEG trigger is written and why
  that placement matters.
- [Reproducibility and parity](reproducibility-and-parity.md): what the
  byte-identical guarantee promises, how it is enforced, and the materials
  datasheet that carries a set's provenance.

Every public name is documented in the [API reference](api.md), grouped as the R
package's reference index is, and the works cited throughout are listed under
[References](references.md).
