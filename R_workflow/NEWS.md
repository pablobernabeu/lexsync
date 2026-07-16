# lexsync (development version)

* The materials datasheet now reports the candidate-pool size per condition
  (selection transparency, making item-selection bias auditable) and a suggested
  crossed mixed-model formula that guards against the language-as-fixed-effect
  fallacy.
* Browser (jsPsych) experiments gain a welcome/instructions screen, per-row item
  metadata (condition, item id, list), and a completion screen that saves the
  collected data as a CSV download.
* The realised-control report and datasheet gain a variance ratio per dimension,
  a distributional balance check that complements Cohen's d and TOST.
* Wuggy-style subsyllabic pseudoword generation (opt-in `items.generation.method:
  subsyllabic`): whole onset/nucleus/coda constituents are swapped for attested
  same-role, same-length alternatives, preserving syllabic structure and length.
  Byte-identical across engines; the default letter-substitution generator is
  unchanged.
* Continuous (non-dichotomised) design mode: declare a `continuous` block and
  `select_continuous_stimuli()` spans a predictor's range evenly while holding the
  controls near-constant, with predictor-control correlations and a regression
  suggested-model in the datasheet. Byte-identical across the R and Python engines.
* Two new matching methods: `mahalanobis` (a covariance-aware distance that
  down-weights correlated dimensions) and `optimal` (a globally optimal assignment
  for two-condition designs, using the suggested `clue` package). Unlike the
  default methods, these use a covariance inverse and an assignment solver, so the
  R and Python engines agree closely but not byte-for-byte on them.
* An unknown `matching.method`, and a candidate pool too small for the requested
  `n_per_condition`, now raise an actionable error rather than silently falling
  back to a default method or returning a short set. The Python engine raises the
  same message, and code that relied on the old fallback will now stop.
* `stringi` is a new hard dependency (Imports). The canonical word key is
  case-folded with ICU at the root locale, so the key no longer depends on the
  machine's locale and matches the Python engine byte for byte. `shiny`, `bslib`,
  `DT` and `zip` are new Suggests, for the Shiny app.
* Ten functions are newly exported, matching the Python package's public surface:
  `PARADIGMS()`, `build_datasheet()`, `build_lexdec_stimuli()`,
  `count_syllables()`, `generate_pseudowords()`, `make_pseudoword()`,
  `methods_paragraph()`, `required_fields()`, `resolve_events()` and
  `write_datasheet()`.
* `tost_equiv()` now defaults to `bound_d = 0.5`, the value the Python engine
  already used. The R default was 0.4, so the equivalence bound is wider and a
  comparison is easier to declare equivalent. Reported verdicts can change for the
  same data.
* `describe_stimuli()` now orders rows by each group's first appearance, matching
  pandas. This changes the row order of generated descriptives.
* OpenSesame experiments now present trials in the seeded counterbalanced order.
  The order was previously randomised again at run time, so what ran was not what
  the pipeline generated and recorded.
* Breaking change: trial order within each counterbalancing list now comes from
  a seeded, keyed-hash shuffle shared with the Python engine. Each row is ranked
  by the SHA-256 digest of `seed|replicate|list|set|condition`, a tuple that
  identifies the trial uniquely under either counterbalancing recipe, so the
  permutation is a pure function of the design: byte-identical from both engines
  on any platform, and different for every seed. Previously the order was drawn
  from `sample()`, which could never match numpy's generator for the same seed,
  so the trial lists were the one engine-specific artefact. All 75 generated
  experiment files across the 15 bundled designs are now byte-identical across
  the engines, and the parity gate now compares the `trial` column of the
  stimuli CSVs. Stimulus selection, pairing and lists are unchanged, but every
  design's trial order changes relative to the previous artefacts. The package
  no longer uses R's random-number generator at all, so a seeded run cannot
  perturb the calling script's random stream and there is no RNG state to save
  or restore.
* `merge_norms()` preserves the lexicon's row order, and `participant_table()`
  crosses factors in `expand.grid()` order in both engines.
* Datasheets record the tolerance windows and pseudoword generator that actually
  ran, filter dimensions as the Python engine does, and report the installed
  package version rather than a hardcoded string.
* `match_stimuli()` raises rather than re-picking an already-used row when a
  relaxed window re-admits candidates missing a matched dimension. Such a
  candidate has no defined distance and is never assigned, yet it still counted
  towards the pool-size guard. An NA-depleted pool could therefore pass the guard
  and go on to emit the same word in several sets.
* `match_stimuli()` and `select_continuous_stimuli()` no longer select an all-NA
  row when the tolerance window is NA (an anchor of a single item gives `sd = NA`).
  An undecided comparison now resolves to `FALSE`, as it does in Python, so the
  window is relaxed and a real word is selected.
* The generated PsychoPy script, OpenSesame experiment and jsPsych page are now
  byte-identical to the Python engine's, trial lists included (see the keyed-hash
  shuffle entry above).
* Selected stimuli are unchanged for all 15 bundled designs.
* See the top-level `CHANGELOG.md` for the full, cross-language history and the
  planned methodological roadmap.

# lexsync 0.1.0

* First release: multilingual corpus access, parallel multidimensional matching,
  counterbalancing, item resampling, deterministic pseudoword generation, and
  generation of hardware-timed PsychoPy, OpenSesame and jsPsych experiments. The
  R and Python engines select byte-identical stimuli, and every run ships a
  materials datasheet (provenance, checksums, realised control) and a
  pre-registration template.
