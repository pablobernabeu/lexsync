# lexsync <span class="mrd-lang">(Python)</span>

Multidimensional lexical optimisation and hardware-timed experiment generation.
{ .mrd-tagline }

lexsync builds psycholinguistic stimulus sets and the experiments that present them. Give it a
word-frequency corpus in any of dozens of languages and a short design file, and it will select
items that are matched in parallel across several lexical dimensions, counterbalance them across
conditions and lists, and write the experiment that runs them on PsychoPy, OpenSesame or in the
browser through jsPsych. The two laboratory targets carry EEG triggers bound to the flip on which
the stimulus appears. A trial is described declaratively, as a sequence of events, so a factorial
word study, lexical decision with generated pseudowords, priming and self-paced reading all come
out of the same engine and the same configuration file.

This is the Python member of a pair. A structurally identical R package ships alongside it, and the
two are documented separately but built from one repository and released under one version.

[Get started](getting-started.md){ .md-button .md-button--primary }
[API reference](api.md){ .md-button }
[The R package](https://pablobernabeu.github.io/lexsync/r/){ .md-button }

## The two engines produce the same experiment

The headline property is that the R and Python engines produce byte-identical output: the same
stimuli, and the same generated experiment down to the trial order. Nothing in the package draws a
random number. Distances are rounded before they are compared, ties are broken by UTF-8 byte order
and then by row id, the lexicon itself is sorted by byte order at load time, and trial order comes
from a keyed hash of the design rather than from a generator, so neither the platform's locale nor
the last bit of a floating-point sum can change what comes out. A laboratory can therefore run the
R package and a collaborator the Python one, and the materials will agree rather than merely
resemble each other. Continuous integration checks this on fifteen worked designs across English,
Spanish and Mandarin Chinese, comparing the regenerated Python output against the committed R
reference.

!!! note "Two documented exceptions"

    The guarantee covers the deterministic matching methods, `standardised_euclidean` (the default)
    and `joint`. It does not cover `mahalanobis` or `optimal`, which rely on a covariance-matrix
    inverse and a linear-assignment solver whose last bits differ between the R and Python
    linear-algebra backends. On those two the engines select equivalent sets rather than identical
    ones. In practice `mahalanobis` usually still agrees exactly, while `optimal` tends to pick an
    equally optimal but different set. Every run's materials datasheet records which case applies,
    so the distinction travels with the stimuli instead of living only in this paragraph.

Trial order used to be the one exception, drawn from each engine's own seeded generator and never
the same across the two. It is now ranked by the SHA-256 digest of each trial's seed, replicate,
list, set and condition, a pure function of the design, so both engines emit the same permutation
byte for byte while the order stays seed-dependent and free of systematic position effects. The
parity contract covers the whole generated experiment, not only the selection.

## Install

lexsync is not yet on PyPI, so install it from the repository:

```bash
pip install "git+https://github.com/pablobernabeu/lexsync.git#subdirectory=python_workflow"
```

Once a release is published, `pip install lexsync` will do the same. Generating an experiment needs
neither PsychoPy nor a parallel-port driver, only the core dependencies above. See
[Getting started](getting-started.md) for the optional extras and for the clone-based install that
the fifteen worked designs expect.

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

The report is the point of the exercise. It states what the matching actually achieved rather than
asserting that it worked:

Frequency, the manipulation, separates the conditions by nearly six standard deviations and is not
equivalent, which is what a frequency contrast is for. The three control dimensions each pass a
two one-sided tests procedure against a bound of *d* = 0.5, so they are shown to be equivalent
rather than merely failing to differ significantly. The variance ratio is reported next to the mean
difference because two conditions can share a mean and still differ in spread.

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

The jsPsych file is self-contained apart from the library itself, which it loads from a content
delivery network, so opening it in a browser runs the experiment. Every worked design in the
repository is published that way, and the Demo link in the header opens the generated
lexical-decision task.

## Where to go next

The three guides follow the arc of a study, from choosing items to presenting them and then to the
guarantees that hold across both engines.

- [Getting started](getting-started.md) covers installation, the command-line interface and the
  anatomy of a design file, which is where most of the work is done.
- [Matching and designs](matching-and-designs.md) covers the pool, the four matching methods, the
  continuous alternative to dichotomising a predictor, resampling items as a random factor and
  pseudoword generation.
- [Experiments and triggers](experiments-and-triggers.md) covers the declarative trial model, the
  four paradigms, counterbalancing and the three presentation targets, including where the EEG
  trigger is written and why that placement matters.
- [Reproducibility and parity](reproducibility-and-parity.md) covers what the byte-identical
  guarantee does and does not promise, how it is enforced and tested, and the materials datasheet
  that carries the provenance of a set.
- [API reference](api.md) documents every public name, grouped the same way as the R package's
  reference index.
