# Package index

## Corpora and lexica

Reach a word-frequency corpus in any registered language, and read it
in.

- [`list_corpora()`](https://pablobernabeu.github.io/lexsync/r/reference/list_corpora.md)
  : List the corpora known to the registry
- [`fetch_corpus()`](https://pablobernabeu.github.io/lexsync/r/reference/fetch_corpus.md)
  : Download a CSV-format registered corpus into the cache
- [`lexsync_cache_dir()`](https://pablobernabeu.github.io/lexsync/r/reference/lexsync_cache_dir.md)
  : Per-user cache directory for fetched corpora
- [`load_lexicon()`](https://pablobernabeu.github.io/lexsync/r/reference/load_lexicon.md)
  : Load a lexicon from a CSV file
- [`load_items()`](https://pablobernabeu.github.io/lexsync/r/reference/load_items.md)
  : Load a paradigm item table (prime-target pairs, sentences, ...)
- [`load_pool()`](https://pablobernabeu.github.io/lexsync/r/reference/load_pool.md)
  : Load a supplied candidate pool of words and give it the matcher's
  dimensions
- [`merge_norms()`](https://pablobernabeu.github.io/lexsync/r/reference/merge_norms.md)
  : Left-join a norm table (e.g. concreteness, age of acquisition,
  valence)

## Lexical dimensions

Derive the dimensions that stimuli are later matched or controlled on.

- [`add_neighbourhood()`](https://pablobernabeu.github.io/lexsync/r/reference/add_neighbourhood.md)
  : Compute orthographic-neighbourhood dimensions (Coltheart's N and
  OLD20)
- [`add_bigram_frequency()`](https://pablobernabeu.github.io/lexsync/r/reference/add_bigram_frequency.md)
  : Mean bigram probability (type-based, non-positional), a
  phonotactic-probability proxy
- [`add_pair_overlap()`](https://pablobernabeu.github.io/lexsync/r/reference/add_pair_overlap.md)
  : Orthographic overlap between the two members of each pair
- [`count_syllables()`](https://pablobernabeu.github.io/lexsync/r/reference/count_syllables.md)
  : Orthographic syllable estimate: the number of maximal vowel runs

## Pools and matching

Filter a lexicon to a candidate pool, then match conditions across
dimensions in parallel.

- [`build_pool()`](https://pablobernabeu.github.io/lexsync/r/reference/build_pool.md)
  : Build an experimental candidate pool by filtering a lexicon
- [`match_stimuli()`](https://pablobernabeu.github.io/lexsync/r/reference/match_stimuli.md)
  : Match stimuli across conditions on several lexical dimensions
- [`resample_stimuli()`](https://pablobernabeu.github.io/lexsync/r/reference/resample_stimuli.md)
  : Produce several disjoint matched item sets (items as a random
  factor)

## Continuous designs

Span a predictor instead of dichotomising it, holding the control
dimensions constant.

- [`select_continuous_stimuli()`](https://pablobernabeu.github.io/lexsync/r/reference/select_continuous_stimuli.md)
  : Select a set spanning a continuous predictor, holding controls
  constant
- [`match_report_continuous()`](https://pablobernabeu.github.io/lexsync/r/reference/match_report_continuous.md)
  : Realised-control report for a continuous design

## Pseudoword generation

Deterministic non-words, and the lexical-decision sets built from them.

- [`generate_pseudowords()`](https://pablobernabeu.github.io/lexsync/r/reference/generate_pseudowords.md)
  : A length-matched pseudoword for each base word (byte-order
  processing)
- [`make_pseudoword()`](https://pablobernabeu.github.io/lexsync/r/reference/make_pseudoword.md)
  : The most bigram-plausible legal non-word at the smallest edit
  distance
- [`build_lexdec_stimuli()`](https://pablobernabeu.github.io/lexsync/r/reference/build_lexdec_stimuli.md)
  : Assemble a word-vs-pseudoword lexical-decision set from a candidate
  pool

## Paradigms and trial events

The declarative trial model, and the fields a design must supply to it.

- [`PARADIGMS`](https://pablobernabeu.github.io/lexsync/r/reference/PARADIGMS.md)
  : The paradigm registry: default event sequences and required fields

- [`resolve_events()`](https://pablobernabeu.github.io/lexsync/r/reference/resolve_events.md)
  :

  The design's trial event list: its own `events`, else its paradigm's

- [`resolve_trial_timing()`](https://pablobernabeu.github.io/lexsync/r/reference/resolve_trial_timing.md)
  : Realise per-trial event durations onto the stimuli table

- [`required_fields()`](https://pablobernabeu.github.io/lexsync/r/reference/required_fields.md)
  : Trial fields a design needs present in its items (paradigm + events)

## Counterbalancing

Rotate items across lists and assign participants to them.

- [`counterbalance()`](https://pablobernabeu.github.io/lexsync/r/reference/counterbalance.md)
  : Assign stimuli to lists and a randomised, reproducible trial order
- [`balance_lists()`](https://pablobernabeu.github.io/lexsync/r/reference/balance_lists.md)
  : Assign item sets to counterbalancing lists so the lists match on the
  item dimensions
- [`participant_table()`](https://pablobernabeu.github.io/lexsync/r/reference/participant_table.md)
  : Build a participant counterbalancing table

## Validation and equivalence

Report the realised control, testing for equivalence rather than for a
null result.

- [`match_report()`](https://pablobernabeu.github.io/lexsync/r/reference/match_report.md)
  : Build the full match-quality report
- [`describe_stimuli()`](https://pablobernabeu.github.io/lexsync/r/reference/describe_stimuli.md)
  : Per-group descriptive statistics for several dimensions
- [`balance_check()`](https://pablobernabeu.github.io/lexsync/r/reference/balance_check.md)
  : Check that the levels of given columns occur equally often
- [`variance_ratio()`](https://pablobernabeu.github.io/lexsync/r/reference/variance_ratio.md)
  : Variance ratio: a distributional balance check
- [`cohens_d()`](https://pablobernabeu.github.io/lexsync/r/reference/cohens_d.md)
  : Cohen's d (pooled-SD standardised mean difference)
- [`cohens_d_ci()`](https://pablobernabeu.github.io/lexsync/r/reference/cohens_d_ci.md)
  : Cohen's d with a confidence interval, complementing the TOST verdict
- [`tost_equiv()`](https://pablobernabeu.github.io/lexsync/r/reference/tost_equiv.md)
  : Two one-sided tests (TOST) of equivalence on a Cohen's d bound

## Experiment generation

Render the events into runnable experiments, with EEG triggers on the
laboratory targets.

- [`export_experiments()`](https://pablobernabeu.github.io/lexsync/r/reference/export_experiments.md)
  : Export all presentation targets (PsychoPy, OpenSesame, jsPsych)
- [`export_psychopy()`](https://pablobernabeu.github.io/lexsync/r/reference/export_psychopy.md)
  : Export a runnable PsychoPy script that interprets the event sequence
- [`export_opensesame()`](https://pablobernabeu.github.io/lexsync/r/reference/export_opensesame.md)
  : Export a complete plain-text OpenSesame experiment
- [`export_jspsych()`](https://pablobernabeu.github.io/lexsync/r/reference/export_jspsych.md)
  : Export a browser-runnable jsPsych experiment
- [`assign_triggers()`](https://pablobernabeu.github.io/lexsync/r/reference/assign_triggers.md)
  : Assign EEG trigger codes to stimuli

## Materials datasheet

The provenance, checksums and realised control that travel with a
stimulus set.

- [`build_datasheet()`](https://pablobernabeu.github.io/lexsync/r/reference/build_datasheet.md)
  : Assemble the materials datasheet for one design
- [`write_datasheet()`](https://pablobernabeu.github.io/lexsync/r/reference/write_datasheet.md)
  : Write a datasheet to a JSON record and a Markdown rendering
- [`methods_paragraph()`](https://pablobernabeu.github.io/lexsync/r/reference/methods_paragraph.md)
  : A ready-to-adapt methods paragraph rendered from a datasheet

## Pipeline and logging

Run a design end to end, and log every step and artefact as it is
written.

- [`run_pipeline()`](https://pablobernabeu.github.io/lexsync/r/reference/run_pipeline.md)
  : Run the lexsync pipeline for one design
- [`run_all()`](https://pablobernabeu.github.io/lexsync/r/reference/run_all.md)
  : Run the lexsync pipeline for every design configuration
- [`new_run_log()`](https://pablobernabeu.github.io/lexsync/r/reference/new_run_log.md)
  : Start a new run log
- [`log_step()`](https://pablobernabeu.github.io/lexsync/r/reference/log_step.md)
  : Append a step to a run log
- [`log_artefact()`](https://pablobernabeu.github.io/lexsync/r/reference/log_artefact.md)
  : Record a written artefact (path, rows, fingerprint) in the log
- [`write_run_log()`](https://pablobernabeu.github.io/lexsync/r/reference/write_run_log.md)
  : Write the run log to Markdown (and optionally JSON Lines)
