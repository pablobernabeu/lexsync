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

- **Practice and filler blocks.** A design may declare `practice:` and `fillers:` item
  tables. Those trials are presented but not analysed, so the pipeline splits: the
  stimuli file and the reports are written from the main rows, the generated experiments
  from every presented trial. Practice comes first as its own run. Fillers are
  INTERLEAVED with the main trials rather than appended, because a block of fillers at
  the end is not a filler but a second block a participant can tell apart. Both appear in
  every list, and both are recorded in the datasheet with their checksums. A design
  declaring neither is unaffected, down to not gaining a `block` column.
- A **`feedback` trial event**, and a **`blocks:`** key restricting any event to named
  blocks. Together they give feedback during practice and not during the task, which is
  the usual arrangement: feedback teaches the response mapping, and would contaminate the
  reaction times it is measuring. The item's `answer` column holds the correct *key*, so
  scoring is a string comparison with nothing to look up, and a timeout is reported
  separately from a wrong key because on a timed task they mean different things.
  Implemented for PsychoPy, OpenSesame and jsPsych: the PsychoPy runner now returns the
  pressed key so it can be scored, the OpenSesame emitter guards the restricted script
  inline, jsPsych reads the response from its own data store, and each pauses at a block
  boundary.
- New paradigm **`categorisation`**: a category cue, then the word to judge against it.
  The cue is a trial event rather than one-off instructions, because the category varies
  by trial, which is what separates a property of the word from the demands of the task.
  `answer` holds the correct response *key*, so the data are scoreable with a string
  comparison. Counterbalanced by Latin-square rotation, so a participant never sees the
  same target twice.
- **`counterbalance.optimise`** (off by default): item sets are assigned to
  counterbalancing lists so the lists are equated on the declared dimensions, rather than
  dealt by set rank, which balances nothing. The search is a steepest-descent exchange of
  set pairs with an all-integer objective and a keyed-hash tie-break, so it uses no
  random number generator and both engines produce the same assignment. On the shipped
  demo it takes the per-list spread in neighbourhood density from 113 to 1. Exported as
  `balance_lists()`.
- New item source **`pool`**: a supplied candidate word list goes through the matcher,
  validation and datasheet without having to masquerade as a corpus lexicon. Exported as
  `load_pool()`. The neighbourhood dimensions are computed against the *lexicon's* words
  rather than the supplied list, because a word's neighbours are its neighbours in the
  language and not among the hundred words a study happens to use.
- A **byte-level parity test** over every generated value artefact, plus a compensated
  summation shared by both engines. See Fixed.
- A design may name norm tables in a **`norms:` block**. They are joined onto the
  lexicon before the candidate pool is built, so a semantic dimension the corpus
  does not carry (concreteness, age of acquisition, valence) can be filtered on,
  matched on or spanned like any other dimension. No norm data is bundled: licences
  vary, and the citation is the user's to honour.
- **Datasheet version 1.1.** Every joined norm table is recorded with its checksum,
  its join key and its per-column coverage, because a norm table can supply the very
  variable a design manipulates and a selection over columns of unstated origin is
  not reproducible from the record that exists to make it so. Coverage is recorded
  because an uncovered word gets a missing value that the tolerance windows then
  drop from the pool. A pair-keyed design also gains a `relational` block: the
  members, the pair count (`items.n_total` counts rows, which is one per pair per
  condition), the member lexicon and its checksum, and the member-level dimensions
  listed separately from the relational ones.
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
  byte-identical materials. The datasheet records this per design (a new
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

- `selection.cross_engine` in the datasheet no longer reports "n/a (user-supplied
  items)" for a **pair-keyed continuous design**. That design does perform a
  selection over the item table, and the selection is byte-identical across engines,
  so the previous answer understated the guarantee on the one path where a reader
  most needs it. A plain item-table design, which selects nothing, still reports
  "n/a".
- `merge_norms()` returns the lexicon with the norm columns appended, in the
  lexicon's own row *and column* order, and looks the key up positionally rather than
  through a merge, so neither engine has any freedom left about the result's shape.
- **Breaking:** trial order within each counterbalancing list is now produced by
  a seeded, keyed-hash shuffle shared by both engines. Each row is ranked by the
  SHA-256 digest of `seed|replicate|list|set|condition`, a tuple that identifies
  the trial uniquely under either counterbalancing recipe, so the permutation is
  a pure function of the design: the same bytes from R and Python on any
  platform, and a different order for every seed. Previously R shuffled with
  `sample()` (Mersenne Twister) and Python with numpy's PCG64, so the same seed
  could never give the same permutation and the trial lists were the one
  engine-specific artefact. All 75 generated experiment files (the PsychoPy
  script, OpenSesame experiment, jsPsych page and both loop-table CSVs, for the
  15 designs bundled at the time) are now byte-identical across the engines, and the CI
  parity gate now compares the `trial` column of the stimuli CSVs as well.
  Stimulus selection, pairing and lists are unchanged, but every design's trial
  order changes relative to the previous artefacts, because the keyed-hash
  permutation differs from the ones the old generators drew. Trial order remains
  seeded and randomised in the sense that matters for position effects, and the
  package no longer touches any random-number generator, so there is no
  generator state to save or restore and a run cannot perturb the calling
  script's random stream.
- Repositioned the project as a general-purpose psycholinguistics toolkit rather
  than a generalisation of one study. The longitudinal EEG study it grew from is
  now presented as one of twelve worked examples it reproduces.
- Pinned the optional `wordfreq` connector to the frozen 3.x line and documented
  that it is a stable snapshot of language usage through roughly 2021 (see
  `corpora/ATTRIBUTION.md`).
- An unknown `matching.method`, and a candidate pool too small for the requested
  `n_per_condition`, now raise an actionable error in both engines instead of
  silently degrading to a default method or a short set. Code that relied on the
  old fallback will now stop.
- `stringi` is a new hard dependency of the R package (Imports). The canonical
  word key is case-folded with ICU at the root locale, so both engines derive it
  byte for byte alike whatever the machine's locale. `shiny`, `bslib`, `DT` and
  `zip` join Suggests for the Shiny app.
- Ten R functions are newly exported, matching the Python package's public
  surface: `PARADIGMS`, `build_datasheet`, `build_lexdec_stimuli`,
  `count_syllables`, `generate_pseudowords`, `make_pseudoword`,
  `methods_paragraph`, `required_fields`, `resolve_events` and `write_datasheet`.
- OpenSesame experiments now present trials in the seeded counterbalanced order.
  They were previously shuffled again at run time, so the order that ran was not
  the order the pipeline generated and recorded.
- R's `tost_equiv()` equivalence bound now defaults to `bound_d = 0.5`, matching
  the Python engine, which already used 0.5. The R default was 0.4, so the bound
  is wider and an R-side equivalence test is now easier to pass. Reported TOST
  verdicts can change for the same data.
- `describe_stimuli()` orders its rows by each group's first appearance in R, as
  pandas already did, so the two engines' descriptives files agree row for row.
  This changes the row order of R-generated descriptives.
- The Python engine pins LF line terminators when writing CSVs, which readr
  already did, so a datasheet's checksums no longer depend on the platform that
  wrote the file.
- Selected stimuli are byte-unchanged for all 15 designs bundled at the time.

### Security

- **A design file could execute code on the machine that ran it.** A design is meant to
  be shared, whether posted with a pre-registration, attached to a paper or handed to a
  collaborator running the other engine. The recipient runs it and then opens the
  generated PsychoPy script, OpenSesame experiment or jsPsych page, which is the only
  thing those files are for. Stimulus text was always safe, because it travels in the
  loop-table CSV the experiment reads at run time. Design *metadata* was not: the name,
  language label, font, parallel-port address and the column names on jitter and feedback
  events were substituted straight into code and markup positions, so a quote or an angle
  bracket there stopped being text and became syntax. A crafted design could therefore run
  arbitrary Python on a lab machine attached to EEG hardware and participant data, or
  arbitrary JavaScript in the origin of a hosted browser study, where it could read every
  response collected. The apps made it worse by exposing the design name, language and
  font as free-text fields.

  These values are now validated rather than escaped, in both engines: escaping correctly
  would mean three different rules for three targets in two engines, six places to get
  subtly wrong, whereas one rule leaves every legitimate value byte-identical. A port
  address must be an address, a column name must be an identifier, and a stated
  `language_tag` is shape-checked instead of being passed through verbatim. `.pyq()` also
  escapes newlines now: an `.osexp` is line-oriented, so a raw newline did not merely
  break a string literal, it closed the inline-script block and let the rest of the value
  start a new top-level item in the experiment. Pinned by `test_injection.py` and
  `test-injection.R`, which assert refusal for seven payload shapes across all three
  targets and confirm the shipped designs' own names, labels and fonts still pass. No
  generated artefact changed.
  Adversarially attacking that fix then found four ways through it, all now closed and
  pinned. The largest: a response event's `keys` were joined into OpenSesame's
  `set allowed_responses "a;b"` with no validation at all, and that is one line of a
  line-oriented format, so a key holding a double quote closed the string, a newline
  ended the line, and the rest of the value became new top-level items in the
  experiment, including an `inline_script` whose body OpenSesame runs. Keys are
  validated now. The shape guards were also anchored with `$`, which in both Python's
  `re` and R's PCRE matches just before a final newline, so a port address ending in
  one passed the check. They are anchored at end-of-string now. A scalar
  `keys: space` or `blocks: practice` was
  iterated character by character in Python and kept whole in R, so one design gave two
  different allowed-response lists and a block-restricted event ran everywhere in one
  engine and nowhere in the other. And R's HTML escape did not cover U+2028/U+2029,
  which end a line in JavaScript but are not ASCII controls: Python escaped them, R did
  not, so the same design produced different bytes and R's `<script>` was a syntax
  error before ES2019.

### Fixed

- **The R-versus-Python parity gate had not run since 15 July.** `setup-r-dependencies`
  is invoked with `working-directory: R_workflow` and also asked for
  `local::./R_workflow`, which resolved to `R_workflow/R_workflow` and failed. Because it
  failed at the dependency-install step, every step after it was *skipped* rather than
  run: the R suite, the reference regeneration, the drift check and the engine
  comparison. The badge went red, but the gate that enforces the headline byte-identity
  claim had simply stopped executing. Now `local::.`, which is what `docs.yml` always
  used.
- **A browser experiment could score a feedback screen against the previous trial's
  keypress.** The jsPsych feedback screen looked up "the last row marked scoreable",
  which is that trial's response only when the trial has one. An event may be restricted
  to a block, so a design that runs the response event in one block and feedback in
  another leaves a trial with no response row of its own, and the screen then reported a
  verdict computed from an earlier trial's key. Each trial's rows now carry its own
  identifier and the screen matches on it, so a trial with no response of its own reports
  none. The generated HTML changed for all 21 designs. No stimulus selection changed.
- **A large number in a user's own column was written differently by the two engines.**
  The CSV writer reproduced readr's format for small magnitudes and left the top end
  alone, on the grounds that nothing lexsync computes reaches it. Nothing lexsync
  computes does. A joined norm table, a supplied pool or an item table carries whatever
  columns the user has, and those go straight into the stimuli CSV. So the guarantee held
  for the shipped designs, which the byte-parity test covers, and failed silently for the
  user's own data, which nothing covers. The divergence started lower than assumed: readr
  writes 1e15 as `1e15` where the Python writer wrote it in full, and a value of exactly
  2^53 picked up a trailing `.0` in one engine only. readr's layout beyond 1e15 could not
  be reproduced. It writes 1.5e16 as `15e15`, the largest double as
  `17976931348623157e292`, and the double nearest 5e22 as `4.9999999999999996e+22`, and
  no rule fits all three, so both engines now refuse such a value, naming the column,
  rather than one accepting it and the two writing different bytes. A value with two
  equally short decimal forms is refused for the same reason: readr prints
  1000000000000000.25 as `...0.3` and Python as `...0.2`, and the digits themselves
  differ. Everything the two engines were verified to render identically, across 465
  values compared against readr's own output, still writes as before.
- **A generated OpenSesame experiment carrying a `feedback` event or a `blocks:`
  restriction would not run at all.** The emitter wrote `unicode(...)` into the inline
  script, a Python 2 builtin that OpenSesame 3.3's Python 3 workspace does not inject, so
  the experiment died with `NameError` on the first trial regardless of which block that
  trial belonged to. The same scripts passed `None` as a `var.get()` default, which
  OpenSesame's var_store cannot distinguish from no default and so raises on rather than
  returning. Both spellings are now pinned by a test in each engine, and a `feedback`
  event with no preceding `response` or `question` is refused at generation time rather
  than failing three different ways at run time.
- **The three rounding policies in play disagreed.** Measured over 210,000 values
  including every three-decimal halfway case in range: R's `round()` disagrees with
  Python's builtin `round()`, Python's builtin disagrees with `numpy.round()`, and even
  R's `sprintf("%.3f")` disagrees with Python's `"%.3f"` on 274 of them, because R's
  delegates to the platform C library. The descriptives path paired R's `round` with
  Python's builtin and the distance path paired it with numpy's, so no artefact value was
  safe. Both engines now use one rounder defined by its arithmetic. That arithmetic is to
  scale, truncate and step away from zero at a half, and IEEE-754 either mandates every
  one of those operations correctly rounded or makes it exact. Some reported values move
  by one in the last published digit. No selection changes.
- **A hash-key component that cannot be rendered identically is now refused.** A blank
  `condition` cell, a routine data error that neither reader rejects, rendered `"NA"` in R
  and `"nan"` in Python, so the two engines produced different trial orders from the same
  design, reproducibly and with nothing to signal it. `TRUE`/`True`, `Inf`/`inf` and
  `NA`/`None` diverged the same way. Booleans now get a pinned spelling. Missing and
  non-finite values raise, because a reproducible order over a meaningless key is worse
  than a stop.
- The overlap-cap centroid in the `joint` and `optimal` matchers used `colMeans` and
  numpy's `.mean`, not the compensated reduction the rest of the z-scoring uses. The cap
  fires for the shipped `en_ndensity` and `es_ndensity` designs, so it decides which
  candidates reach matching. Verified to change no design's selection.
- **`R CMD check --as-cran` had a WARNING and an undocumented NOTE**, while
  `cran-comments.md` claimed "0 errors | 0 warnings | 1 note". `select_continuous_stimuli()`
  documented four of its seven arguments. `head()` was called without an import, so a user
  who defined their own would have had it called by the package. Both fixed, and the check
  is now clean at 0/0/1.
- **The package's only example could never have worked.** It called `read_config()`, which
  is not exported, from inside a `\dontrun{}` that R CMD check therefore never ran. The
  example now uses only exported API, runs offline against bundled data, and the package
  has executable examples on its main entry points rather than none.
- Three factual corrections, each verified against the source. The SUBTLEX-PT registry
  entry cited `10.3758/s13428-014-0511-x`, which Crossref resolves to an unrelated
  psychometrics program by different authors. The matching vignette placed Zipf 7 at a
  thousand occurrences per million rather than ten thousand, contradicting its own lower
  anchor. A design comment attributed "840-prime materials" to Rastle et al. (2004).
  That paper used 150 prime-target pairs and the figure appears nowhere in it.
- **The Python engine embedded a bare `NaN` in the generated jsPsych experiment**, where
  a trial had no value for a field that another block supplies, as in a main-block trial
  in a design whose practice items carry an `answer`. `NaN` is not valid JSON, and the R
  engine dropped the key instead, so the two engines' experiments differed byte for byte.
  Both now drop it, which is also the honest rendering: a trial with no correct answer
  has none. Found by running the two engines into separate directories. Both write the
  shared experiment files to one path, so a normal run has the second silently overwrite
  the first.
- **The generated artefacts were not byte-identical across the engines, and the parity
  test could not see it.** It read both CSVs back with a parser and compared the values,
  under which `1` and `1.0` are the same number. Thirteen of the 18 shipped designs
  differed byte for byte while the gate stayed green. Three of the differences were
  matters of serialisation, namely a whole number written `1` by readr and `1.0` by
  pandas, a boolean written `FALSE` and `False`, a value below 1e-3 written `9e-4` and
  `0.0009`. The fourth was not. Two reported means differed in the last decimal the
  descriptives publish, because numpy sums pairwise and R's `mean()` uses a two-pass
  long-double algorithm, and the true value sat on a rounding boundary. Every reduction in
  the package now uses one Neumaier compensated summation written out in both engines, so
  their agreement follows from IEEE-754 requiring addition and subtraction to be correctly
  rounded rather than from a measurement of two libraries' internals. **No R golden
  moved:** R's two-pass mean was already the correctly-rounded one, so the fix brought the
  Python engine into line. Artefacts are now compared as bytes, not as parsed values.
- **A response key coded `f` was silently turned into `FALSE`.** `readr` reads a column
  whose values are all `f`, `t`, `T` or `F` as logical while pandas keeps the string, so
  an item table using the commonest two-choice key pair had its correct answer corrupted
  in the R engine and not the Python one. Measured on readr 2.2.0: `f`, `t`, `T` and `F`
  infer as logical; `j`, `y` and `n` do not. Item tables now read the condition label and
  the paradigm's presented fields as text in both engines.
- **The datasheet was truncating its own provenance.** `jsonlite::toJSON` defaults to four
  digits, so a design declaring `tolerance_k: 0.1111111111111111` had it recorded as
  `0.1111`, which does not reproduce the run the record exists to describe. Most fields
  escaped only because they are deliberately rounded on the way in. Both engines now
  write the JSON at 15 significant digits.
- The matcher's z-scoring centre and scale also go through the compensated reductions.
  Selection was robust to the difference for a structural reason. A distance is between
  z-vectors, so a shift in the centre cancels and a change of scale cannot reorder
  candidates. Robust-for-a-reason is not identical-by-construction, though, and the change
  was verified to move no design's selection.
- **`merge_norms()` column order differed between engines.** R's `merge()` hoists the
  join column to position 1 while `pandas.merge` keeps the left frame's order, so the
  two engines returned different column order whenever `on` was not already the first
  column. Measured on both engines, then removed structurally rather than repaired.
- **`merge_norms()` case-folded only one side of the join key.** A lexicon holding
  `Dog` against a norm table holding `dog` matched nothing, and the design carried on
  with an all-missing dimension. Both engines agreed on that wrong answer, which is
  why no parity test could have caught it. The lexicon's own spelling is preserved:
  `word` is the byte-order tie-break behind every selection.
- **A colliding norm column was silently renamed.** R's `merge()` produced
  `frequency.x` / `frequency.y` and pandas `frequency_x` / `frequency_y`, so a design
  matching on `frequency` found neither, in either engine. It is now an error naming
  the clash.
- **The R engine wrote its datasheet and Markdown run log with CRLF on Windows**
  while the Python engine wrote LF, because `write_datasheet()` and `write_run_log()`
  used a text-mode connection rather than the package's LF-pinning writer. The
  datasheet is the provenance artefact. Its bytes must not record which machine
  produced it.
- **`add_pair_overlap()` and `resolve_trial_timing()` were not exported from the R
  package.** Both were marked for export and documented, but `NAMESPACE` had not been
  regenerated, so `library(lexsync)` did not make them available.
- A word missing from a lexicon row became the literal string `"nan"` in Python
  while R dropped the row. Both engines now drop it before string coercion.
- `participant_table()` crosses its factors in `expand.grid()` order in both
  engines, so either allocates the same cell to a given participant number.
- `merge_norms()` preserves the lexicon's row order in R, as pandas does.
- Datasheets record the tolerance windows and the pseudoword generator that
  actually ran, filter dimensions identically in both engines, and report the
  running package version rather than a hardcoded string.
- The matcher raises rather than re-picking an already-used row when a relaxed
  window re-admits candidates that are missing a matched dimension. Such a
  candidate has no defined distance, so it ranks last and is never assigned, yet
  it still counted towards the pool-size guard. An NA-depleted pool could
  therefore pass the guard and go on to emit the same word in several sets.
- An anchor of a single item gives a tolerance window of NA, which left R's
  pre-filter undecided and indexed all-NA filler rows into the candidate set, so
  R selected an empty stimulus row where Python relaxed the window and selected a
  real word. R now resolves an undecided comparison to FALSE, as Python does.
- The generated PsychoPy script and OpenSesame experiment are now byte-identical
  across the two engines. Python's embedded event JSON padded its separators and
  wrote a whole-number timeout as `2.0` where jsonlite writes `2`. (The trial
  lists are covered by the keyed-hash shuffle under Changed, which makes every
  generated file byte-identical.)
- Documentation no longer describes the jsPsych output as self-contained. The
  jsPsych library loads from a CDN, so the machine running the file needs an
  internet connection.

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
