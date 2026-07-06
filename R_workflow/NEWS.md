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
* See the top-level `CHANGELOG.md` for the full, cross-language history and the
  planned methodological roadmap.

# lexsync 0.1.0

* First release: multilingual corpus access, parallel multidimensional matching,
  counterbalancing, item resampling, deterministic pseudoword generation, and
  generation of hardware-timed PsychoPy, OpenSesame and jsPsych experiments. The
  R and Python engines select byte-identical stimuli, and every run ships a
  materials datasheet (provenance, checksums, realised control) and a
  pre-registration template.
