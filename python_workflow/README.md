# lexsync (Python)

Multidimensional lexical optimisation and hardware-timed experiment generation.

`lexsync` selects stimuli matched in parallel across several lexical dimensions
(length, frequency, orthographic neighbourhood density and OLD20), counterbalances
them and generates the 'PsychoPy' and 'OpenSesame' scripts that present them, with
hardware triggers injected at stimulus onset for EEG/ERP synchronisation. It is the
Python member of a dual-language pair; a structurally identical R package is also
provided, and the two engines produce identical matched stimuli (byte-identical
for the deterministic matching methods; see the repository README).

## Install

```bash
pip install lexsync                 # core
pip install "lexsync[corpora]"      # + wordfreq connector (~40 languages)
```

The `experiment` extra (`psychopy`, `pyserial`) is needed only to *run* a generated
experiment, never to generate one.

## Use

```python
import yaml, lexsync
schema = yaml.safe_load(open("config/schema.yaml"))
lex = lexsync.load_lexicon("corpora/derived/en.csv", schema, "english")
design = yaml.safe_load(open("config/design_en_freqcontrast.yaml"))
pool = lexsync.build_pool(lex, design["pool_filters"])
stim = lexsync.match_stimuli(pool, design, schema)
report = lexsync.match_report(stim, ["length", "frequency", "n_density", "old20"], schema)
lexsync.export_experiments(lexsync.scripting.assign_triggers(stim), design, schema, "output/experiments")
```

Or from the command line:

```bash
lexsync run config/design_en_freqcontrast.yaml
lexsync corpora list
lexsync fetch fr            # build a French lexicon via wordfreq
```

See the repository root for the full project, corpora registry and the
accompanying manuscript. Source code is MIT-licensed; bundled corpora are under
CC BY-SA 4.0 (see the repository's `LICENSE-DATA` and `corpora/ATTRIBUTION.md`).
