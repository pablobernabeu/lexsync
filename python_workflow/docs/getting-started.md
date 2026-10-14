# Getting started

This page covers the three things you need before any of the rest is useful: getting the package
installed with the right extras, driving it from the command line, and reading a design file. The
design file is where nearly all of the work happens. Almost nothing about a study is expressed in
Python code, which is deliberate, because a YAML file can be attached to a pre-registration and
handed to someone running the other engine.

## Install

```bash
pip install lexsync
```

That gives you the library and the `lexsync` console script. The `corpora` and `experiment` extras go
in brackets after the package name, either on their own or together:

```bash
pip install "lexsync[corpora]"
pip install "lexsync[corpora,experiment]"
```

The development version comes straight from the repository, where the Python package sits in the
`python_workflow/` subdirectory:

```bash
pip install "git+https://github.com/pablobernabeu/lexsync.git#subdirectory=python_workflow"
```

If you want the 21 worked designs, the derived corpora and the committed outputs as well, clone the
repository and install the package in editable mode from inside it:

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
| `experiment` | `psychopy>=2024.1`, `pyserial>=3.5` | Running a generated laboratory experiment on hardware. |
| `dev` | `pytest`, `build`, `twine`, `streamlit` | The test suite, including the tests that cover the Streamlit app. |

The `experiment` extra deserves emphasis because it is easy to assume otherwise. It is needed only
to *run* a generated experiment, never to generate one. Script generation imports neither PsychoPy
nor pyserial. It writes text. The whole demonstration therefore reproduces on a laptop with no
parallel port, no EEG amplifier and no PsychoPy installation, and the test suite runs the same way
in continuous integration.

The floor on PsychoPy is there because the extra tracks PsychoPy's own supported range of Python
versions, which trails the newest interpreter by a release or two. PsychoPy currently declares 3.10
up to 3.12, so on Python 3.13 there is nothing for pip to install and it stops with a message naming
psychopy. That is the intended outcome. Without the floor pip would keep looking further back until
it reached a 2022 release whose dependencies no longer build, and the install would die part-way
through a compilation having installed nothing. On Windows with Python 3.12 the resolve succeeds,
but pyWinhook, which PsychoPy requires there, publishes no wheel for that version and is built from
source, so swig has to be on the path. Python 3.11 avoids both and is the easiest interpreter to use
for hardware work. None of this touches the rest of the package, which runs on any version from 3.10
onwards.

The `corpora` extra pins wordfreq to its frozen 3.x line, which is a stable snapshot of language
usage through roughly 2021. That is deliberate. A lexicon derived from a live, drifting source
would quietly stop reproducing.

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
lexsync fetch fr --n-words 30000                  # the same, with 30,000 forms
lexsync fetch subtlex_us                          # download and normalise SUBTLEX-US
```

`lexsync run` is the orchestrator. It reads the schema and the design, loads the lexicon, derives
whatever dimensions the design matches on, selects and counterbalances the items, then writes the
stimuli, the realised-control report, the materials datasheet, the run log and the three experiment
scripts. Its flags:

| Flag | Default | Meaning |
| --- | --- | --- |
| `--schema` | resolved | The global schema and defaults, resolved as described below when left out. |
| `--config-dir` | `config` | Where to look for designs when no design is named. |
| `--outdir` | `output` | Root of the written artefacts (`stimuli/`, `reports/`, `experiments/`). |

Paths in a design are resolved relative to the working directory, so run these from the root of a
clone. With no design argument, `lexsync run` globs `design_*.yaml` and `design_*.yml` from
`--config-dir`, sorts them and runs each in turn.

A schema named with `--schema` is used as given, and one that does not exist is an error. When the
flag is left out, the schema is resolved in order. Running every design, `lexsync run` reads
`schema.yaml` in `--config-dir` and then `config/schema.yaml` in the working directory. Running one
design, it reads `config/schema.yaml` in the working directory and then `schema.yaml` beside the
design. Either way the copy bundled with the package comes last, and a line on standard error names
the file chosen. The run log records it as `schema_path` and the datasheet as
`reproducibility.schema_path`. `run_pipeline()` and `run_all()` resolve a schema they are not given
in the same way, through `lexsync.paths.resolve_schema`.

A failing command prints lexsync's own message to standard error and exits with status 1.
`lexsync --traceback run ...` shows the Python traceback as well. A mistyped flag exits with
argparse's usage status, 2.

`lexsync corpora list` prints the registry as a table of name, language, ISO code, status,
connector and citation. `lexsync fetch` takes either a registry entry name or a language code. If
the name is one of the thirty language codes registered for the wordfreq connector, a lexicon is
built with wordfreq and cached under `~/.lexsync/cache`. Otherwise the registered delimited file is
downloaded there, checked against the SHA-256 the registry records and normalised into a lexicon,
as `normalise_lexicon` does below. Either way the path is printed and the citation for the source
goes to standard output with it. A name holding `/`, `\` or `:` is refused, since it becomes the
cached file's name, and every refusal names the registry file it read. The cache persists between
sessions. `lexsync.corpora.cache_clear("fr")` removes one corpus from it, and `cache_clear()` with
no name removes the whole cache. Building a wordfreq lexicon is Python-only. The R package can read
the result as an ordinary corpus but cannot build one, so an R laboratory reaches the wider
language set through lexica derived here. Registered corpora fetched from R go to a separate cache
under `tools::R_user_dir("lexsync", "cache")`, which `lexsync_cache_clear()` empties.

A corpus file downloaded by hand, such as SUBTLEX-UK from its own page, is made into a lexicon by
`normalise_lexicon`, which both packages export:

```python
import lexsync
lexsync.normalise_lexicon("SUBTLEX-UK.txt", entry="subtlex_uk", out="subtlex_uk.csv")
```

It reads a tab- or comma-separated file and takes the column names from the registry entry's
`columns` map (or from `columns=`). A frequency per million is converted with Zipf =
log10(per million) + 3, rounded to three places, and the words are lower-cased and put in NFC. A
form listed twice is resolved by the entry's `duplicates` rule: the first row by default, or the
sum of its rates per million, which Lexique needs because it splits a homograph's frequency
between its rows. A rate of 0 has no Zipf value and is refused. The line it prints counts the Zipf
values that lay within 1e-9 of a rounding boundary, the one step at which the two packages'
`log10` could round a value apart. The count is expected to be 0, and a run over the lexicon
records it in its run log and datasheet. `load_lexicon` refuses a `freq_zipf` column with values
outside 0 to 9, which are frequencies per million under the wrong name. A log count such as
SUBTLEX-US's `Lg10WF` lies inside that range, so it has to be converted all the same.

A wordfreq lexicon holds the language's most frequent forms that are spelt with letters, 10,000 of
them unless `fetch_corpus` is given another `n_words` or `lexsync fetch` another `--n-words`. The
lexica committed under `corpora/derived/` hold more: they were built with `python
corpora/fetch_corpora.py --languages en es --n-words 30000` and, for Chinese, `--languages zh
--n-words 20000`. Each form is lower-cased and put in Unicode
NFC. Combining marks are part of the spelling, so the vowel signs and viramas of Hindi and Bengali
are kept, and so is the zero-width non-joiner that Persian spells many words with. A Ukrainian
word may also hold an apostrophe between two letters, as п'ять does, and a Catalan word a middle dot
between two l's, as pel·lícula does. No other punctuation mark and no digit is part of a spelling,
so English contractions and French elisions stay out. When fewer forms pass than were requested, a
line on standard output says so. `fetch_corpus(..., strict=True)` raises an error at
such a shortfall, and `exclude_latin=True` drops every form holding a Latin letter, such as the
English tokens of a Hindi list.

Length, N and OLD20 count code points in both packages. A vowel sign, a virama or a zero-width
non-joiner is therefore a character of its own, which adds one to the word's length and takes one
edit to change. `n_syllables` is missing for every word outside the Latin script, and `run_pipeline`
refuses a design that refers to it when such a word passes the design's other filters.

## Anatomy of a design

A design is a YAML file. `config/schema.yaml` holds everything global and every numeric default,
while the design holds what is specific to the study. Both are read identically by the R and Python
packages, which is what lets a design travel. Here is the English frequency contrast in full, from
`config/design_en_freqcontrast.yaml`:

```yaml
name: en_freqcontrast
language: english
lexicon: corpora/derived/en_v2.csv
description: 'High versus low frequency English words, matched on length, neighbourhood density and OLD20.'
n_per_condition: 80
pool_filters:
  length: [3, 8]
  frequency: [3.8, 7.0]
  # Keeps only the forms the SUBTLEX-US screen leaves unmarked (see corpora/ATTRIBUTION.md).
  nonstandard: [0, 0]
# Leaves out the unsuitable forms the screen lets through (see the file's header).
exclude_words: {path: config/exclude_en_demo.txt}
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
`en_freqcontrast_english_stimuli_py.csv`, `en_freqcontrast_english.osexp` and the rest. A name or
language holding a character outside ASCII also adds an eight-character checksum to the stem, as
[Reproducibility and parity](reproducibility-and-parity.md) explains. `language` is a free-text
label rather than a code, because it is what the experiment displays. When the browser target needs
a real BCP 47 tag it maps the common labels and falls back to `und`, or you can state
`language_tag` outright.

`lexicon` names the derived corpus to read. It may also be written as `items.lexicon`, which is the
form the lexical-decision designs use, since they also need to say where the items come from.

`items` selects the source of the stimuli, and there are four of them:

| `items.source` | Where stimuli come from | Also needs |
| --- | --- | --- |
| `corpus` (the default) | Words selected from the lexicon by matching or by spanning a predictor. | `lexicon`, `conditions` or `continuous`, `match_on` |
| `generate` | Real words plus a deterministically generated pseudoword for each. | `lexicon`, optionally `items.generation.method` |
| `table` | A CSV of prepared items (prime-target pairs, sentences). | `items.path` |
| `pool` | A candidate word list of your own, matched over as if it were a pool. | `items.path`, normally `items.lexicon` |

`pool_filters` narrows the lexicon to the candidates a design will consider at all. Each key is a
column and each value a `[min, max]` range for a numeric column, or a set of allowed values for a
categorical one. This is a step that matters. The matcher never reads `pool_filters` itself, so a
script that omits `build_pool` matches over the entire lexicon and quietly ignores the design's
bands. Here `nonstandard: [0, 0]` keeps the forms the screened lexicon leaves unmarked, and
`exclude_words` leaves out the words a file lists, as
[Matching and designs](matching-and-designs.md#choosing-and-screening-a-lexicon) explains.

`conditions` is a list, each with a `name` and a `define_by` block that carves the condition out of
the pool by the same filter syntax. Two conditions make a contrast. Four make the 2 × 2 that
`config/design_en_andrews_repro.yaml` uses to reproduce
[Andrews (1989)](references.md#andrews-1989). A design may instead declare
a `continuous` block and dispense with conditions altogether, which
[Matching and designs](matching-and-designs.md) covers.

`match_on` lists the dimensions to equate across conditions, and a design that matches its
conditions must name at least one. `n_per_condition` is how many items you want in each, a whole number written as
`80` or `80.0`. Both are the heart of the design, and both are discussed at length in the matching
guide.

`matching` overrides the schema defaults for this design alone. `matching.method` picks one of the
four methods, and `matching.tolerance_k` sets the half-width, in standard deviations, of the
tolerance window on each dimension. Overriding a single dimension is common when reproducing a
published study's exact windows.

`counterbalance.lists` sets the number of lists, and `counterbalance.optimise` asks for an assignment
whose lists are equated on the item dimensions, where the plain deal goes by set rank. `practice` and
`fillers` each name an item table whose trials run but are not analysed. `timing` overrides the fixation, critical-word and
inter-stimulus durations in milliseconds (`fixation_ms`, `word_ms`, `isi_ms`), the older
`*_frames` forms still being accepted and converted at `presentation.assumed_refresh_hz`. `font` overrides
the presentation font, which matters for a non-Latin script: `config/design_zh_freqcontrast.yaml`
sets `SimHei`, because the Latin default has no glyphs for Han characters.

`paradigm` names one of the six registered paradigms and inherits its trial-event sequence and its
counterbalancing recipe. Omitting it gives `factorial`. A design may instead supply an explicit
`events` list and describe its own trial. Both routes are covered in
[Experiments and triggers](experiments-and-triggers.md).

### What is checked before a run

Before it reads a lexicon or writes a file, `run_pipeline` checks the design and the schema with
`validate_design`, and a design that cannot be honoured is refused with the same message in both
engines. Every key is looked up in the vocabulary of keys lexsync reads at its level, which
`lexsync.design` holds as `DESIGN_KEYS` and `SCHEMA_KEYS`. A key one edit from a known key of up to
five characters, or two edits from a longer one, is taken for a typo. It is refused with the key it
was probably meant to be. `n_per_conditon: 8` now stops with
`unknown design key 'n_per_conditon' (did you mean 'n_per_condition'?)`, where it used to leave
the design on the default of twenty items. Any other unknown key is noted in the run log and
otherwise ignored, and a later release will refuse it. Notes and comments therefore belong in `description` or in a key beginning `x_`, which
are never checked.

The same step checks the values. It refuses a missing or non-text `name` or `language` (quote a
code such as `'no'`, which YAML reads as false) and an `n_per_condition` that is not a whole number
of at least 1. It refuses a name, language or font that cannot be written safely into the
generated experiments, a trigger port that is not an address, and an unknown timing key or
malformed response key. Last, it refuses a condition name that is not text or appears twice, and a
corpus or pool design with conditions but no `match_on`. These used to surface at export, after the stimuli and
reports had been written, or at a different point in each engine.

### The schema

`config/schema.yaml` is the other half, and it is worth reading once. It fixes the seed, states the
column contract that a derived lexicon must satisfy (`word` and `freq_zipf` are required), declares
the six lexical dimensions and how each is obtained, and sets the defaults a design may override:
the matching method, the per-dimension tolerance windows, the equivalence bound and alpha, the
parallel-port address and trigger timing, and the presentation fonts. A schema holding only the
seed and the column contract is enough, since every other block falls back to the defaults the code
carries.

One thing in it is deliberately not configurable. Equivalence is assessed by two one-sided tests,
and only the bound and alpha are settings.

The rule that breaks exact ties in the matcher is a setting, `matching.tie_break`, and it matters,
because whole-number lengths and neighbourhood counts make ties decide most picks. `hash`, the
default, gives a tie to the smaller keyed SHA-256 of the word, which favours no part of the
alphabet. `bytes` gives it to the spelling that sorts first, as lexsync 0.1 did, and reproduces that
version's selections, but it fills a condition decided by ties with early-alphabet words. Under
either rule, the two default methods give the same selection in the two engines without an RNG
([Matching and designs](matching-and-designs.md#how-matching-works)).

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
