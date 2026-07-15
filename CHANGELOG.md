# Changelog

All notable changes to lexsync are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to
adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). The R and
Python packages are released in lockstep under the same version. Because lexsync
is a data-bearing scientific tool, a change that alters *which stimuli are
selected* for the same inputs and seed is treated as a breaking change even when
no function signature changes.

## [Unreleased]

### Added

- Materials datasheet now records **selection transparency**: the candidate-pool
  size per condition (how many items satisfied each condition's window before
  matching). Reporting the size of the discretionary pool makes item-selection
  bias auditable (Forster, 2000; Simmons et al., 2011).
- Materials datasheet now emits a **suggested crossed mixed-model formula** and
  fills the pre-registration analysis plan with it, guarding against the
  language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008; Barr et
  al., 2013; reduce the structure if it fails to converge, Matuschek et al.,
  2017).
- Browser (jsPsych) experiments now open with a welcome/instructions screen,
  attach each item's design fields (condition, item id, counterbalancing list) to
  every recorded row, and end with a completion screen that saves the collected
  data as a CSV download, so a generated experiment gathers usable,
  self-describing data with no server.
- Two new matching methods (set with `matching.method`): `mahalanobis`, a
  covariance-aware distance that down-weights correlated control dimensions
  (Rubin, 1980; Stuart, 2010), and `optimal`, a globally optimal assignment for
  two-condition designs (Gu & Rosenbaum, 1993; Hansen & Klopfer, 2006). Unlike the
  deterministic default methods, these use a covariance-matrix inverse and an
  assignment solver, so the R and Python engines select equivalent but not
  byte-identical materials; the datasheet records this per design (a new
  `cross_engine` field). Adds the `clue` package to the R Suggests.
- Wuggy-style subsyllabic pseudoword generation, opt-in via
  `items.generation.method: subsyllabic` (the default `letter_substitution` is
  unchanged). Each word is split into onset/nucleus/coda constituents and whole
  constituents are swapped for attested same-role, same-length alternatives, so
  the pseudowords preserve syllabic structure (a deterministic orthographic
  approximation of Wuggy; Keuleers & Brysbaert, 2010). Length is preserved, a
  word with no legal swap falls back to letter substitution, and the selection is
  byte-identical across the R and Python engines. See
  `config/design_en_lexdec_wuggy.yaml`.
- Continuous (non-dichotomised) design mode: declare a `continuous:` block (a
  predictor and the controls to hold constant) instead of discrete `conditions`,
  and lexsync selects a set that spans the predictor's range evenly while keeping
  the controls near-constant and near-uncorrelated with it, for regression or
  mixed-model analysis rather than a matched dichotomy (Kuperman, 2015;
  Liben-Nowell et al., 2019). The datasheet reports the predictor span and the
  predictor-control correlations and suggests a regression model. The selection is
  byte-identical across the R and Python engines. See
  `config/design_en_freqcontinuous.yaml`.
- Distributional balance diagnostic: the realised-control report and datasheet now
  carry a **variance ratio** per dimension (condition variance / reference
  variance) alongside Cohen's d and TOST, because two conditions can share a mean
  yet differ in spread and still confound (Armstrong, Watson & Plaut, 2012; Austin,
  2009).
- `codemeta.json` (machine-readable software metadata) and this changelog.

### Changed

- Repositioned the project as a general-purpose psycholinguistics toolkit rather
  than a generalisation of one study. The longitudinal EEG study it grew from is
  now presented as one of twelve worked examples it reproduces.
- Pinned the optional `wordfreq` connector to the frozen 3.x line and documented
  that it is a stable snapshot of language usage through roughly 2021 (see
  `corpora/ATTRIBUTION.md`).

### Planned

The state-of-the-art roadmap from the initial competitor and literature review is
now delivered (covariance-aware and optimal matching, a distributional balance
diagnostic, continuous designs and Wuggy-style pseudowords). Further norm
dimensions (concreteness, age of acquisition, English Lexicon Project behavioural
measures) are supported today through the `merge_norms` connector, which joins any
word-keyed norm table so the matcher can equate on it. Future directions include
more bundled languages and, should a determinism-safe implementation be found,
promoting a covariance-aware distance to the default.

## [0.1.0] - 2026-06-07

### Added

- Initial dual-language (R + Python) release: many-language corpus access,
  parallel multidimensional matching (standardised-Euclidean and joint methods),
  counterbalancing, item resampling (items as a random factor), deterministic
  pseudoword generation, and generation of hardware-timed PsychoPy, OpenSesame
  and jsPsych experiments with the onset trigger flip-locked to stimulus onset.
- Cross-engine byte-identical stimulus selection, verified on twelve worked
  examples across English, Spanish and Mandarin Chinese.
- Materials datasheet with provenance, checksums and a realised-control report
  (Cohen's d, 90% CI and a TOST equivalence test); a pre-registration template;
  and a machine-readable corpus registry.
