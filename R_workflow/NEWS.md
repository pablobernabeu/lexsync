# lexsync (development version)

* The materials datasheet now reports the candidate-pool size per condition
  (selection transparency, making item-selection bias auditable) and a suggested
  crossed mixed-model formula that guards against the language-as-fixed-effect
  fallacy.
* Browser (jsPsych) experiments gain a welcome/instructions screen, per-row item
  metadata (condition, item id, list), and a completion screen that saves the
  collected data as a CSV download.
* See the top-level `CHANGELOG.md` for the full, cross-language history and the
  planned methodological roadmap.

# lexsync 0.1.0

* First release: multilingual corpus access, parallel multidimensional matching,
  counterbalancing, item resampling, deterministic pseudoword generation, and
  generation of hardware-timed PsychoPy, OpenSesame and jsPsych experiments. The
  R and Python engines select byte-identical stimuli, and every run ships a
  materials datasheet (provenance, checksums, realised control) and a
  pre-registration template.
