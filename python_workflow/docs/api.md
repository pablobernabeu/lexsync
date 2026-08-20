# API reference

Every public name in `lexsync` is documented here, grouped along the path a study takes: reach a
corpus, derive the dimensions, build a pool and match it, describe a trial, counterbalance it,
report what the matching achieved, generate the experiment, and write down the provenance. The
groups are the same ones the [R package's reference index](https://pablobernabeu.github.io/lexsync/r/reference/)
uses, so a name can be found in the same place on either site.

Everything listed under a group heading is importable straight from `lexsync`, with a handful of
exceptions that are noted where they appear and are reached through their own module. Guides with
worked examples are linked from the [home page](index.md), and the published work that these entries
cite is listed in full on the [references page](references.md).

## Corpora and lexica

Languages are supplied through a corpus registry, so reaching a new one takes a registry entry and
no code. These functions find a corpus, fetch it if it is not already local, and read a
derived lexicon or a prepared item table into the frame everything else expects.

::: lexsync.list_corpora

::: lexsync.fetch_corpus

::: lexsync.corpora.cache_dir

::: lexsync.load_lexicon

::: lexsync.load_items

::: lexsync.load_pool

::: lexsync.merge_norms

## Lexical dimensions

Two dimensions arrive with the lexicon and the rest are derived from the orthographic forms. Derive
them before matching, and compute the neighbourhood measures against the full lexicon rather than the
pool, since a word's neighbours do not stop existing because a design excluded them.

::: lexsync.add_neighbourhood

::: lexsync.add_bigram_frequency

::: lexsync.add_pair_overlap

::: lexsync.count_syllables

## Pools and matching

The pool is the set of candidates a design will consider at all, and the matcher works only on what
it is given. `match_stimuli` never reads a design's `pool_filters`, so `build_pool` is a required
step.

::: lexsync.build_pool

::: lexsync.match_stimuli

::: lexsync.resample_stimuli

## Continuous designs

Dichotomising a continuous predictor costs power and can introduce selection artefacts. A design may
instead span the predictor evenly while holding its controls near-constant, and be analysed by
regression or a mixed model.

::: lexsync.select_continuous_stimuli

::: lexsync.match_report_continuous

## Pseudoword generation

Non-words are generated deterministically, with no sampling anywhere, preserving length exactly
and keeping every letter bigram attested in the corpus. Both methods select byte-identical stimuli
in the R and Python engines.

::: lexsync.generate_pseudowords

::: lexsync.make_pseudoword

::: lexsync.build_lexdec_stimuli

## Paradigms and trial events

A trial is a list of event dictionaries rather than backend code, which is what lets one engine serve
five paradigms and three presentation targets. A design either names a paradigm and inherits its
event sequence, or supplies its own `events`.

::: lexsync.PARADIGMS

::: lexsync.resolve_events

::: lexsync.resolve_trial_timing

::: lexsync.required_fields

## Counterbalancing

Two recipes are available, and the paradigm chooses between them. Trial order comes from a seeded,
keyed-hash shuffle, a pure function of the design with no generator behind it, so the same seed
gives the same order in both engines. `balance_lists` is the optional search for a list assignment
whose lists are equated on the item dimensions, where the plain deal goes by set rank.

::: lexsync.counterbalance

::: lexsync.balance_lists

::: lexsync.participant_table

## Validation and equivalence

A matched design claims that its controls do not differ, and a non-significant test of difference
does not establish that. These functions report the realised control instead: the standardised
difference with its interval, an equivalence test against a declared bound, and the variance ratio
that a mean-based statistic would miss.

::: lexsync.match_report

::: lexsync.describe_stimuli

::: lexsync.balance_check

::: lexsync.variance_ratio

::: lexsync.cohens_d

::: lexsync.cohens_d_ci

::: lexsync.tost_equiv

## Experiment generation

All three targets are rendered from the same event list. Generation imports neither PsychoPy nor
pyserial, so it needs no laboratory hardware. The `experiment` extra is for running the result.
`assign_triggers` is reached as `lexsync.scripting.assign_triggers`, and `export_experiments` calls
it for you.

::: lexsync.export_experiments

::: lexsync.export_psychopy

::: lexsync.export_opensesame

::: lexsync.export_jspsych

::: lexsync.scripting.assign_triggers

## Materials datasheet

The datasheet is the provenance record that travels with a stimulus set: where the items came from,
how they were selected, the realised control, the candidate-pool sizes, the checksums and the
versions. `run_pipeline` builds and writes one for every run.

::: lexsync.build_datasheet

::: lexsync.write_datasheet

::: lexsync.methods_paragraph

## Pipeline and logging

`run_pipeline` is the orchestrator behind `lexsync run`, and `run_all` loops it over a directory of
designs. The logging functions are reached as `lexsync.logging.*`, which does not shadow the standard
library's `logging` for absolute imports.

::: lexsync.run_pipeline

::: lexsync.run_all

::: lexsync.logging.new_run_log

::: lexsync.logging.log_step

::: lexsync.logging.log_artefact

::: lexsync.logging.write_run_log
