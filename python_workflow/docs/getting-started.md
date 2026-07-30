# Getting started

This page covers the three things you need before any of the rest is useful: getting the package
installed with the right extras, driving it from the command line, and reading a design file. The
design file is where nearly all of the work happens. Almost nothing about a study is expressed in
Python code, which is deliberate, because a YAML file can be attached to a pre-registration and
handed to someone running the other engine.

## Install

lexsync is not yet on PyPI. Until a release is published, install it straight from the repository:

```bash
pip install "git+https://github.com/pablobernabeu/lexsync.git#subdirectory=python_workflow"
```

That gives you the library and the `lexsync` console script. If you want the fifteen worked designs,
the derived corpora and the committed outputs as well, clone the repository and install the package
in editable mode from inside it:

```bash
git clone https://github.com/pablobernabeu/lexsync.git
cd lexsync
python -m pip install -e "python_workflow[dev]"
python python_workflow/run_pipeline.py     # runs every demonstration design
```

Python 3.10 or newer is required. The core dependencies are pandas, NumPy, PyYAML, rapidfuzz and
SciPy, and they are enough to select stimuli and generate every experiment target.

### Extras

Three optional extras are declared in `pyproject.toml`. Only the first is likely to matter to you
early on.

| Extra | Installs | What it unlocks |
| --- | --- | --- |
| `corpora` | `wordfreq>=3.0,<4` | The wordfreq connector, which derives a lexicon for a language that is not bundled. |
| `experiment` | `psychopy`, `pyserial` | Running a generated laboratory experiment on hardware. |
| `dev` | `pytest`, `build`, `twine`, `streamlit` | The test suite, including the tests that cover the Streamlit app. |

The `experiment` extra deserves emphasis because it is easy to assume otherwise. It is needed only
to *run* a generated experiment, never to generate one. Script generation imports neither PsychoPy
nor pyserial. It writes text. The whole demonstration therefore reproduces on a laptop with no
parallel port, no EEG amplifier and no PsychoPy installation, and the test suite runs the same way
in continuous integration.

The `corpora` extra pins wordfreq to its frozen 3.x line, which is a stable snapshot of language
usage through roughly 2021. That is a feature rather than an oversight. A lexicon derived from a
live, drifting source would quietly stop reproducing.

### Check that it worked

```python exec="1" source="material-block" result="text" session="getting-started"
import lexsync

print(lexsync.__version__)
print(lexsync.list_corpora().to_string(index=False))
```

`list_corpora` reads the corpus registry. It looks for `corpora/registry.yaml` relative to the
working directory first, then one level up, then falls back to the copy bundled inside the package,
so it answers whether or not you are standing in a clone. Setting `LEXSYNC_REGISTRY` overrides the
search.

## The command line

Installing the package puts a `lexsync` command on the path. `python -m lexsync` is an alias for it
and takes the same arguments. There are three subcommands.

```bash
lexsync run config/design_en_freqcontrast.yaml    # one design, end to end
lexsync run                                       # every design_*.yaml in --config-dir
lexsync corpora list                              # the registry, as a table
lexsync fetch fr                                  # derive a French lexicon via wordfreq
```

`lexsync run` is the orchestrator. It reads the schema and the design, loads the lexicon, derives
whatever dimensions the design matches on, selects and counterbalances the items, then writes the
stimuli, the realised-control report, the materials datasheet, the run log and the three experiment
scripts. Its flags:

| Flag | Default | Meaning |
| --- | --- | --- |
| `--schema` | `config/schema.yaml` | The global schema and defaults. |
| `--config-dir` | `config` | Where to look for designs when no design is named. |
| `--outdir` | `output` | Root of the written artefacts (`stimuli/`, `reports/`, `experiments/`). |

Paths in a design are resolved relative to the working directory, so run these from the root of a
clone. With no design argument, `lexsync run` globs `design_*.yaml` and `design_*.yml` from
`--config-dir`, sorts them and runs each in turn.

`lexsync corpora list` prints the registry as a table of name, language, ISO code, status,
connector and citation. `lexsync fetch` takes either a registry entry name or a language code. If
the name is one of the thirty language codes registered for the wordfreq connector, a lexicon is
built with wordfreq and cached under `~/.lexsync/cache`; otherwise the registered delimited file is
downloaded there. Either way the path is printed and the citation for the source goes to standard
output with it. Fetching is Python-only. The R package can read the result as an ordinary corpus but
cannot build one, so an R laboratory reaches the wider language set through lexica derived here.

## Anatomy of a design

A design is a YAML file. `config/schema.yaml` holds everything global and every numeric default;
the design holds what is specific to the study. Both are read identically by the R and Python
packages, which is what lets a design travel. Here is the English frequency contrast in full, from
`config/design_en_freqcontrast.yaml`:

```yaml
name: en_freqcontrast
language: english
lexicon: corpora/derived/en.csv
description: 'High versus low frequency English words, matched on length, neighbourhood density and OLD20.'
n_per_condition: 80
pool_filters:
  length: [3, 8]
  frequency: [3.8, 7.0]
conditions:
  - name: high_frequency
    define_by:
      frequency: [5.2, 7.0]
  - name: low_frequency
    define_by:
      frequency: [3.8, 4.4]
match_on: [length, n_density, old20]
counterbalance:
  lists: 1
timing:
  fixation_frames: 30
  word_frames: 30
  isi_frames: 15
```

### The keys

`name` and `language` are required, and together they form the slug that every written file is
named after. `en_freqcontrast` plus `english` becomes `en_freqcontrast_english`, and from that come
`en_freqcontrast_english_stimuli_py.csv`, `en_freqcontrast_english.osexp` and the rest. `language`
is a free-text label rather than a code, because it is what the experiment displays; when the
browser target needs a real BCP 47 tag it maps the common labels and falls back to `und`, or you
can state `language_tag` outright.

`lexicon` names the derived corpus to read. It may also be written as `items.lexicon`, which is the
form the lexical-decision designs use, since they also need to say where the items come from.

`items` selects the source of the stimuli, and there are three of them:

| `items.source` | Where stimuli come from | Also needs |
| --- | --- | --- |
| `corpus` (the default) | Words selected from the lexicon by matching or by spanning a predictor. | `lexicon`, `conditions` or `continuous`, `match_on` |
| `generate` | Real words plus a deterministically generated pseudoword for each. | `lexicon`, optionally `items.generation.method` |
| `table` | A CSV of prepared items (prime-target pairs, sentences). | `items.path` |

`pool_filters` narrows the lexicon to the candidates a design will consider at all. Each key is a
column and each value a `[min, max]` range for a numeric column, or a set of allowed values for a
categorical one. This is a real step rather than a formality: the matcher never reads `pool_filters`
itself, so a script that omits `build_pool` matches over the entire lexicon and quietly ignores the
design's bands.

`conditions` is a list, each with a `name` and a `define_by` block that carves the condition out of
the pool by the same filter syntax. Two conditions make a contrast; four make the 2 × 2 that
`config/design_en_andrews_repro.yaml` uses to reproduce
[Andrews (1989)](references.md#andrews-1989). A design may instead declare
a `continuous` block and dispense with conditions altogether, which
[Matching and designs](matching-and-designs.md) covers.

`match_on` lists the dimensions to equate across conditions. `n_per_condition` is how many items you
want in each. Both are the heart of the design, and both are discussed at length in the matching
guide.

`matching` overrides the schema defaults for this design alone. `matching.method` picks one of the
four methods, and `matching.tolerance_k` sets the half-width, in standard deviations, of the
tolerance window on each dimension. Overriding a single dimension is common when reproducing a
published study's exact windows.

`counterbalance.lists` sets the number of lists. `timing` overrides the fixation, critical-word and
inter-stimulus durations in milliseconds (`fixation_ms`, `word_ms`, `isi_ms`; the older
`*_frames` forms are still accepted and converted at `presentation.assumed_refresh_hz`). `font` overrides
the presentation font, which matters for a non-Latin script: `config/design_zh_freqcontrast.yaml`
sets `SimHei`, because the Latin default has no glyphs for Han characters.

`paradigm` names one of the four registered paradigms and inherits its trial-event sequence and its
counterbalancing recipe. Omitting it gives `factorial`. A design may instead supply an explicit
`events` list and describe its own trial. Both routes are covered in
[Experiments and triggers](experiments-and-triggers.md).

### The schema

`config/schema.yaml` is the other half, and it is worth reading once. It fixes the seed, states the
column contract that a derived lexicon must satisfy (`word` and `freq_zipf` are required), declares
the six lexical dimensions and how each is obtained, and sets the defaults a design may override:
the matching method, the per-dimension tolerance windows, the equivalence bound and alpha, the
parallel-port address and trigger timing, and the presentation fonts.

Two things in it are deliberately not configurable. Equivalence is assessed by two one-sided tests,
and only the bound and alpha are settings. The tie-break order in the matcher is fixed at
distance, then word bytes, then id, because that byte-order tie-break is precisely what lets the two
engines agree without an RNG. Making it an option would make the guarantee an option.

A copy of the schema and of a small English, Spanish and Chinese lexicon is bundled inside the
installed package, which is how the examples throughout these guides run without a clone:

```python exec="1" source="material-block" result="text" session="getting-started"
from importlib.resources import files

import yaml

data = files("lexsync") / "data"
schema = yaml.safe_load((data / "schema.yaml").read_text(encoding="utf-8"))
print(sorted(p.name for p in data.iterdir()))
```

The bundled lexica are 3000-word slices meant for examples and tests. The full derived corpora live
in `corpora/derived/` in the repository, and that is what the worked designs read.

## What a run writes

Running a design produces more than a stimulus list. Under `--outdir` you get the counterbalanced
stimuli, the descriptives and comparisons that make up the realised-control report, a materials
datasheet in both JSON and Markdown, a run log in both Markdown and JSON Lines, and the three
experiment scripts with their loop tables.

```python
# illustrative: needs a clone with config/, and writes files under output/
import lexsync

paths = lexsync.run_pipeline("config/design_en_freqcontrast.yaml")
print(paths["stimuli"])
print(paths["experiments"]["jspsych"])
```

The Python engine suffixes its stimuli and reports with `_py`, so an R run and a Python run of the
same design leave both selections side by side in one directory rather than overwriting each other.
That is not a filing convenience. `output/stimuli/en_freqcontrast_english_stimuli_R.csv` is the
committed reference that the parity test regenerates the Python selection against. The experiment
scripts are the exception and carry no engine suffix, because the two engines emit the same bytes
there and a byte-for-byte diff of that directory is itself a continuous-integration step.
