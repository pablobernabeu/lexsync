# lexsync (development version)

* **A design file could execute code on the machine that ran it.** A design is meant to
  be shared, and the recipient runs it and then opens the generated PsychoPy script,
  OpenSesame experiment or jsPsych page. Stimulus text was always safe: it travels in the
  loop-table CSV the experiment reads at run time. Design *metadata* was not. The name,
  language label, font, parallel-port address and the column names on jitter and feedback
  events were substituted straight into code and markup positions, so a quote or an angle
  bracket there stopped being text and became syntax, and a crafted design could run
  arbitrary code on a lab machine or in the origin of a hosted browser study. These are
  now validated rather than escaped -- one rule in both engines, which leaves every
  legitimate value byte-identical -- a port address must be an address, a column name must
  be an identifier, and a stated `language_tag` is shape-checked rather than passed
  through. `.pyq()` escapes newlines now as well: an `.osexp` is line-oriented, so a raw
  newline closed the inline-script block and let the rest of the value start a new
  top-level item. Pinned by `test-injection.R`. No generated artefact changed.
  Adversarially attacking that fix then found four ways through it, all now closed and
  pinned. The largest: a response event's `keys` were joined into OpenSesame's
  `set allowed_responses "a;b"` with no validation at all, and that is one line of a
  line-oriented format -- so a key holding a double quote closed the string, a newline
  ended the line, and the rest of the value became new top-level items in the
  experiment, including an `inline_script` whose body OpenSesame runs. Keys are
  validated now. The shape guards were also anchored with `$`, which in both Python's
  `re` and R's PCRE matches just before a final newline, so a port address ending in
  one passed the check; they are anchored at end-of-string now. A scalar
  `keys: space` or `blocks: practice` was
  iterated character by character in Python and kept whole in R, so one design gave two
  different allowed-response lists and a block-restricted event ran everywhere in one
  engine and nowhere in the other. And R's HTML escape did not cover U+2028/U+2029,
  which end a line in JavaScript but are not ASCII controls: Python escaped them, R did
  not, so the same design produced different bytes and R's `<script>` was a syntax
  error before ES2019.
* **A browser experiment could score a feedback screen against the previous trial's
  keypress.** The jsPsych feedback screen looked up "the last row marked scoreable",
  which is that trial's response only when the trial has one. An event may be restricted
  to a block, so a design running the response event in one block and feedback in another
  leaves a trial with no response row of its own, and the screen then reported a verdict
  computed from an earlier trial's key. Each trial's rows now carry its own identifier and
  the screen matches on it. The generated HTML changed for all 21 designs; no stimulus
  selection changed.
* **A large number in a user's own column was written differently by the two engines.**
  `write_csv_utf8()` reproduced readr's format for small magnitudes and left the top end
  alone, since nothing lexsync computes reaches it. Nothing lexsync computes does; a
  joined norm table, a supplied pool or an item table carries whatever columns the user
  has, and those go straight into the stimuli CSV, so the guarantee held for the shipped
  designs and failed silently for the user's own data. readr's layout above 1e15 could not
  be reproduced in Python -- it writes 1.5e16 as `15e15`, the largest double as
  `17976931348623157e292`, and the double nearest 5e22 as `4.9999999999999996e+22` -- so
  both engines now refuse such a value, naming the column, rather than one accepting it
  and the two writing different bytes. A value with two equally short decimal forms is
  refused for the same reason. Everything verified to render identically, across 465
  values compared against readr's own output, writes as before.
* **A generated OpenSesame experiment with a `feedback` event or a `blocks:` restriction
  would not run.** The emitter wrote `unicode(...)`, a Python 2 builtin that OpenSesame's
  Python 3 inline workspace does not provide, so the experiment died with `NameError` on
  the first trial. It also passed `None` as a `var.get()` default, which OpenSesame
  cannot distinguish from no default and so raises on rather than returning. Both are
  fixed, both spellings are now pinned by a test, and a `feedback` event with no
  preceding `response` or `question` is refused at generation time instead of failing
  three different ways at run time.
* **One decimal rounder, shared by both engines.** No pairing of built-ins agreed:
  measured over 210,000 values including every three-decimal halfway case in range, R's
  `round()` disagrees with Python's builtin, Python's builtin disagrees with numpy's, and
  even R's `sprintf("%.3f")` disagrees with Python's `"%.3f"` on 274 of them. Reported
  statistics are now rounded by an arithmetic definition both engines compute
  identically. Some values move by one in the last published digit; no selection changes.
* A hash-key component that cannot be rendered identically in both engines is now
  refused rather than hashed. A blank `condition` cell — a routine data error neither
  reader rejects — rendered `"NA"` in R and `"nan"` in Python, so the two engines
  produced different trial orders from the same design, reproducibly and with nothing to
  signal it. Booleans get a pinned spelling rather than a refusal.
* The overlap-cap centroid in the `joint` and `optimal` matchers goes through the
  compensated reduction. The cap really fires on shipped designs, so it decides which
  candidates reach matching; verified to change no design's selection.
* `R CMD check --as-cran` is clean: **0 errors, 0 warnings, 1 note** (the standard
  new-submission note). Fixed on the way: three undocumented arguments on
  `select_continuous_stimuli()`, an unqualified `utils::head()`, and the package's only
  example, which called an unexported function from inside `\dontrun{}` and so could
  never have worked if a user copied it. The package now has executable, offline
  examples, and `cran-comments.md` no longer misstates the check result.
* Three factual corrections. The SUBTLEX-PT registry entry cited a DOI that resolves to
  an unrelated psychometrics paper. The matching vignette put Zipf 7 at a thousand
  occurrences per million rather than ten thousand, contradicting its own lower anchor.
  A design comment attributed "840-prime materials" to Rastle et al. (2004), a figure
  that appears nowhere in that paper.

* Practice and filler blocks. A design may declare `practice:` and `fillers:` item
  tables; those trials are presented but not analysed, so the stimuli file and the
  reports are written from the main rows while the generated experiments run every
  trial. Practice comes first; fillers are interleaved with the main trials rather than
  appended, because a block of fillers at the end is not a filler but a second block a
  participant can tell apart. A design declaring neither is unaffected, down to not
  gaining a `block` column.
* A `feedback` trial event, and a `blocks:` key that restricts any event to named
  blocks. Together these give feedback during practice and not during the task, which is
  the usual arrangement: feedback teaches the mapping, and would contaminate the reaction
  times it is measuring. Implemented for PsychoPy, OpenSesame and jsPsych alike. The
  PsychoPy runner now returns the pressed key so it can be scored, and each runner pauses
  at a block boundary.
* **The Python engine embedded a bare `NaN` in the generated jsPsych experiment** where a
  trial had no value for a field another block supplies (a main-block trial in a design
  whose practice items carry an `answer`). That is not valid JSON, and the R engine
  dropped the key instead, so the two engines' experiments differed. Both now drop it.
* **The generated artefacts were not byte-identical across the engines, and the parity
  test could not see it.** It read both CSVs back with a parser and compared the values,
  under which `1` and `1.0` are the same number; 13 of the 18 shipped designs differed
  byte for byte while the gate stayed green. Three differences were serialisation (a
  whole number written `1` and `1.0`, a boolean written `FALSE` and `False`, a small
  value written `9e-4` and `0.0009`) and one was not: two reported means differed in the
  last decimal published, because numpy sums pairwise and R's `mean()` does not. Every
  reduction in the package now uses one compensated-summation algorithm written out in
  both engines, whose agreement follows from IEEE-754 rather than from measurement; the
  writers agree on every value; and the artefacts are now compared as bytes. No R
  golden moved: R's two-pass mean was already the correctly-rounded one.
* **A response key coded `f` was silently turned into `FALSE`.** `readr` reads a column
  whose values are all `f`, `t`, `T` or `F` as logical, while pandas keeps the string, so
  an item table using the commonest two-choice key pair had its correct answer corrupted
  in one engine. Item tables now read the condition label and the paradigm's presented
  fields as text in both engines.
* `jsonlite`'s default of four digits was truncating the datasheet: a design declaring
  `tolerance_k: 0.1111111111111111` had it recorded as `0.1111`, which does not reproduce
  the run the record exists to describe. The JSON is now written at full display
  precision, and the Python engine writes the same precision.
* New paradigm `categorisation`: a category cue, then the word to judge against it, with
  `answer` holding the correct response key so the data are scoreable. Counterbalanced by
  Latin-square rotation, so a participant never sees the same target twice.
* `counterbalance.optimise` (off by default) assigns item sets to lists so the lists are
  equated on the declared dimensions, instead of dealing them by rank. The search is a
  deterministic integer descent with a keyed-hash tie-break, so it uses no random number
  generator and both engines produce the same assignment. `balance_lists()` is exported.
* New item source `pool`: a supplied word list goes through the matcher without having
  to masquerade as a corpus lexicon. `load_pool()` is exported. The neighbourhood
  dimensions are computed against the lexicon's words rather than the supplied list,
  because a word's neighbours are its neighbours in the language.
* A design may name norm tables in a `norms:` block. They are joined onto the
  lexicon before the candidate pool is built, so a semantic dimension the corpus
  does not carry (concreteness, age of acquisition, valence) can be filtered on,
  matched on or spanned like any other. No norm data is bundled; every joined table
  is recorded in the materials datasheet with its checksum and its per-column
  coverage, because a norm table can supply the very variable a design manipulates.
* Datasheet version 1.1. It adds `materials_source$norms` and, for a pair-keyed
  design, a `relational` block naming the members, the pair count, the member
  lexicon and its checksum, and the member-level dimensions separately from the
  relational ones. `selection$cross_engine` no longer reports
  "n/a (user-supplied items)" for a pair-keyed continuous design: that design does
  perform a selection, and it is byte-identical across engines.
* `merge_norms()` returns the lexicon with the norm columns appended, in the
  lexicon's own row *and column* order. It previously used `merge()`, which hoists
  the join column to position 1 where pandas keeps the left frame's order, so the
  two engines disagreed on column order whenever `on` was not already first. The
  join key is now also case- and whitespace-folded on the lexicon's side, not only
  the norm table's: a lexicon holding `Dog` used to match nothing and leave an
  all-`NA` dimension. A norm column whose name already exists on the lexicon is now
  an error rather than being renamed to `frequency.x` / `frequency.y`, which left
  the matched dimension under a name nothing looks for.
* `write_datasheet()` and `write_run_log()` now write LF on every platform. They
  used a text-mode connection, so on Windows the datasheet, its Markdown rendering
  and the Markdown run log came out CRLF while the Python engine's twins were LF.
  The datasheet is the provenance record; its bytes no longer depend on the machine
  that built it.
* `add_pair_overlap()` and `resolve_trial_timing()` are now actually exported. Both
  were marked for export and documented, but the `NAMESPACE` had not been
  regenerated, so `library(lexsync)` did not make them available.
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
  experiment files across the 15 designs bundled at the time are now byte-identical across
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
* Selected stimuli are unchanged for all 15 designs bundled at the time.
* See the top-level `CHANGELOG.md` for the full, cross-language history and the
  planned methodological roadmap.

# lexsync 0.1.0

* First release: multilingual corpus access, parallel multidimensional matching,
  counterbalancing, item resampling, deterministic pseudoword generation, and
  generation of hardware-timed PsychoPy, OpenSesame and jsPsych experiments. The
  R and Python engines select byte-identical stimuli, and every run ships a
  materials datasheet (provenance, checksums, realised control) and a
  pre-registration template.
