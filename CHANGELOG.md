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

- The experiment templates cannot drift between their three copies. `templates/` is
  the canonical set and both packages carry a mirror so an installed copy can reach
  one. Nothing checked that the three agreed, and no functional test could, because a
  stale mirror still renders and runs and simply produces a different experiment from
  the one
  documented. For the trigger templates that means code time-locking EEG markers to
  stimulus onset, where the failure is silent and the data unusable. Both engines now
  compare the bytes.
- The Python package runs a linter, under a rule set it states for itself: `E`, `F`,
  `W`, `I`, `UP` and `B`, with `UP031`, `E702` and `E741` ignored for the reasons
  `pyproject.toml` records, pinned there so a ruff release cannot move what CI checks.
  The Streamlit app is linted under the same configuration, having been the one Python
  source in the repository no linter looked at.
  The template trees are excluded because they are not modules: OpenSesame supplies
  `Canvas`, `var` and `clock` at run time, and the
  PsychoPy placeholders are substituted before anything executes, so reading them as
  importable Python reported every one of those names as undefined.
- Every `zip()` states the length invariant it relies on. All of them pair sequences
  equal in length by construction, so all now pass `strict=True`. It is a no-op while
  that holds and an exception the moment it stops, which matters most in
  `counterbalancing.py` and `scripting.py`, where the zipped values build the hash keys
  behind the deterministic shuffle and the jitter: silent truncation there would raise
  nothing and quietly deal a different experiment. No output changed: the suite passes,
  and a full pipeline run leaves all 242 artefacts byte-identical to the committed ones.

- The requested number of stimuli is now a contract. Every selector -- the anchored
  matcher, `joint` and `optimal` pairing, continuous selection (including pair-keyed
  continuous designs) and pseudoword generation -- previously returned fewer sets than
  `n_per_condition` when the pool ran short, disclosing it at most through a verbose
  console note. The datasheet and the generated Methods text state the requested n, so a
  silent shrink made the provenance record misstate the materials. A shortfall is now an
  error by default, and a design that can accept a smaller set opts in with `matching:
  shortfall: allow`. A second policy, `matching: on_insufficient_tolerance`, governs the
  tolerance window: the default `relax` keeps the old widening behaviour but now records
  it (see the datasheet entry below), and `error` refuses instead. No committed design
  experiences either condition, so no shipped stimulus changed.
- The datasheet records the matcher's decisions alongside the design's requests.
  `selection.window_relaxations` records every tolerance-window relaxation (condition,
  candidates within tolerance, candidates needed), which previously left no trace
  outside a verbose console line. `selection.candidate_cap` records the pairwise
  matchers' 1,200-candidate cap and whether it fired per condition. It does fire for
  the shipped neighbourhood-density designs, whose Methods paragraphs now say so.
  `tolerance_k` is omitted for `joint` and `optimal`, which never consult it. The
  `reproducibility` block gains the SHA-256 of the design YAML and of the schema, so an
  artefact set is pinned to the exact configuration that produced it, and a
  `reference_words` override, which changes the neighbourhood dimensions without
  touching any hashed input file, is recorded as `selection.neighbourhood_reference`.
  The environment record adds the value-relevant dependencies it omitted (rapidfuzz and
  PyYAML in Python; yaml and stringi in R) and the operating system. The datasheet also
  now states the equivalence bound it tested against (`equivalence: {bound_d, alpha}`).
- CI tests the installed package as well as the checkout. The Python matrix gains 3.14,
  and a new job installs the declared minimum dependency versions on Python 3.10, so
  the floors in `pyproject.toml` become tested claims. A weekly scheduled run catches
  upstream drift between pushes. The built wheel is installed into a clean environment
  and a design is run from outside the repository through the installed CLI. The parity
  job's final cross-engine diff widens from the experiments subtree to every freshly
  generated artefact except the per-engine provenance files. The CLI gains
  `--version` and falls back to the bundled schema when `config/schema.yaml` is not
  present, so the installed package runs outside a checkout.
- The parity job's two remaining gates cover what they were written for. The step
  that regenerates the R artefacts and diffs them against the committed tree looked
  at `output/stimuli/` alone, so a change to the descriptives, the comparisons or any
  of the five generated experiment files per design left the committed copies stale
  with every job green, and the documentation site publishes those committed
  experiments verbatim. It now diffs the whole of `output/`, less the run logs and
  datasheets, which record wall-clock times and the runner's package versions.
  `LEXSYNC_REQUIRE_PARITY`, which turns a comparison that found nothing to compare
  into a failure rather than a skip, reached `test_parity.py` alone and now reaches
  the byte-parity suite that makes the byte-identical claim checkable. A third test
  holds `test_parity.py`'s hand-written case list against `config/design_*.yaml`, so
  a design added without a case fails rather than going uncompared.
- The documentation is built on every pull request. `mkdocs build --strict` and
  `pkgdown::build_site` are the only checks it has, and the workflow ran on a push to
  main alone, so a broken link, a missing nav page or a reference that no longer
  resolves passed every check on the change that caused it and then turned main red at
  deploy time, leaving the published site on its previous version. Building and
  publishing are now separate jobs, and write access to the repository belongs to the
  second alone.
- Both front-ends are exercised through the layer a user meets. The two suites reached
  the helper functions the export path is built from and nothing else, so a paradigm
  branch that assembles a design the engine refuses would have surfaced only when
  someone opened the page. Every paradigm each app offers is now selected, run and
  asked for its result, under Streamlit's `AppTest` and `shiny::testServer`.
- A design may declare `practice:` and `fillers:` item tables. Those trials are
  presented but not analysed, so the pipeline splits: the
  stimuli file and the reports are written from the main rows, the generated experiments
  from every presented trial. Practice comes first as its own run. Fillers are
  *interleaved* with the main trials, because a block of fillers at the end is not a
  filler but a second block a participant can tell apart. Both appear in every list, and
  both are recorded in the datasheet with their checksums. A design declaring neither is
  unaffected, down to not gaining a `block` column.
- A `feedback` trial event, and a `blocks:` key restricting any event to named
  blocks. Together they confine feedback to practice, which is
  the usual arrangement: feedback teaches the response mapping, and would contaminate the
  reaction times it is measuring. The item's `answer` column holds the correct *key*, so
  scoring is a string comparison with nothing to look up, and a timeout is reported
  separately from a wrong key because on a timed task they mean different things.
  Implemented for PsychoPy, OpenSesame and jsPsych: the PsychoPy runner now returns the
  pressed key so it can be scored, the OpenSesame emitter guards the restricted script
  inline, jsPsych reads the response from its own data store, and each pauses at a block
  boundary.
- New paradigm `categorisation`: a category cue, then the word to judge against it. The
  cue is a trial event, shown afresh each time, because the category varies by trial,
  which is what separates a property of the word from the demands of the task. `answer`
  holds the correct response *key*, so the data are scoreable with a string comparison.
  Counterbalanced by Latin-square rotation, so a participant never sees the same target
  twice.
- `counterbalance.optimise` (off by default): item sets are assigned to counterbalancing
  lists so the lists are equated on the declared dimensions. Dealing them by set rank,
  the behaviour it replaces, balances nothing. The search is a steepest-descent exchange
  of set pairs with an all-integer objective and a keyed-hash tie-break, so it uses no
  random number generator and both engines produce the same assignment. On the shipped
  demo it takes the per-list spread in neighbourhood density from 113 to 1. Exported as
  `balance_lists()`.
- New item source `pool`: a supplied candidate word list goes through the matcher,
  validation and datasheet without having to masquerade as a corpus lexicon. Exported as
  `load_pool()`. The neighbourhood dimensions are computed against the *lexicon's*
  words, because a word's neighbours are its neighbours in the language, whatever
  hundred words a study happens to use.
- A byte-level parity test over every generated value artefact, plus a compensated
  summation shared by both engines. See Fixed.
- A design may name norm tables in a `norms:` block. They are joined onto the
  lexicon before the candidate pool is built, so a semantic dimension the corpus
  does not carry (concreteness, age of acquisition, valence) can be filtered on,
  matched on or spanned like any other dimension. No norm data is bundled: licences
  vary, and the citation is the user's to honour.
- Datasheet version 1.1 records every joined norm table with its checksum, its join
  key and its per-column coverage, because a norm table can supply the very
  variable a design manipulates and a selection over columns of unstated origin is
  not reproducible from the record that exists to make it so. Coverage is recorded
  because an uncovered word gets a missing value that the tolerance windows then
  drop from the pool. A pair-keyed design also gains a `relational` block: the
  members, the pair count (`items.n_total` counts rows, which is one per pair per
  condition), the member lexicon and its checksum, and the member-level dimensions
  listed separately from the relational ones.
- Materials datasheet now records selection transparency: the candidate-pool
  size per condition (how many items satisfied each condition's window before
  matching). Reporting the size of the discretionary pool makes item-selection
  bias auditable (Forster, 2000; Simmons et al., 2011).
- Materials datasheet now emits a suggested crossed mixed-model formula and
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
- Continuous (non-dichotomised) design mode: a design may replace its discrete
  `conditions` with a `continuous:` block, naming a predictor and the controls to hold
  constant, and lexsync selects a set that spans the predictor's range evenly while
  keeping the controls near-constant and near-uncorrelated with it, ready for regression
  or a mixed model (Kuperman, 2015; Liben-Nowell et al., 2019). The datasheet reports
  the predictor span and the predictor-control correlations and suggests a regression
  model. The selection is byte-identical across the R and Python engines. See
  `config/design_en_freqcontinuous.yaml`.
- Distributional balance diagnostic: the realised-control report and datasheet now
  carry a variance ratio per dimension (condition variance / reference
  variance) alongside Cohen's d and TOST, because two conditions can share a mean
  yet differ in spread and still confound (Armstrong, Watson & Plaut, 2012; Austin,
  2009).
- `codemeta.json` (machine-readable software metadata) and this changelog.
- Both applications offer the categorisation paradigm, wired to the bundled
  `items/categorisation_en.csv` exactly as priming and self-paced reading are. The
  engine registers five paradigms and ships a worked categorisation design, while the
  two choosers listed four, so the one paradigm a researcher could not reach from the
  interface was the one they would otherwise have had to write a design file for. The
  test that claimed the chooser was complete compared against a written-out list rather
  than the paradigm registry, and now compares against the registry in both suites.
- `fetch_corpus` takes a `dest` in Python as it always has in R, so a fetched lexicon
  can be written straight beside the design that reads it rather than copied out of
  `~/.lexsync/cache` by hand. `cache_dir`'s own description of the cache as where a
  download lands 'unless told otherwise' is true of this engine again. The two
  signatures now differ only by Python's `n_words`, which sizes a wordfreq-derived
  lexicon and is documented, with the reason it does not reach the cached file name.
- The Python API reference documents every object it renders, as the R reference
  always has. Twenty of the 47 entries carried no prose at all, among them
  `run_pipeline`, `counterbalance`, `export_experiments` and the four logging
  functions, and not one entry described a parameter, a default or a return value,
  although the site is configured to render them. The wording is taken from the R
  roxygen so the two references say the same thing. A new test reads the same source
  the site does and refuses an entry with no docstring, an undocumented argument or a
  name `api.md` does not render, which is the guard `R CMD check` already gives the R
  side.

### Changed

- Both apps take the lexsync accent, the deep violet the documentation site uses.
  The Shiny app took Bootswatch's cosmo blue, which reaches only 3.97:1 against the
  white label of the full-width 'Run design' button, short of the 4.5:1 that size
  calls for, and the Streamlit app declared no theme and rendered in Streamlit's
  default red, so two front-ends over one package looked unlike each other and
  unlike the package's own sites. The Streamlit accent is declared in
  `.streamlit/config.toml` at the repository root, which is where the documentation
  already tells the reader to launch the app from; neither app overrides the page
  background, so both follow the viewer's own light or dark setting.
- Every edit to the Shiny app's conditions table lands in the column the user edited.
  The table is rendered without rownames, so the client reports a zero-based column
  index, while `DT::editData` was called at its default `rownames = TRUE` and read one
  column to the left: an edit to `dimension` overwrote the condition's name, an edit to
  `lower` overwrote `dimension`, and an edit to the name itself was dropped from the
  frame altogether. The app ran and exported the altered design without saying
  anything. The optional `lower2` and `upper2` columns are also typed as numeric in
  both apps, where three of the Shiny presets left them logical and the first edit of
  such a cell coerced the whole column to text.
- The Shiny app no longer crashes on Run when it is launched from outside the
  checkout. With no `corpora/derived/` above the working directory the lexicon chooser
  was rendered empty and silent, and pressing Run indexed that empty vector before the
  'Choose a lexicon first.' guard could be reached, so the user was shown Shiny's
  generic error. The chooser is now replaced by a notice naming the cause, as the
  Streamlit app already printed one, and the guard does its job.
- A preset in either app sets the matched dimensions and the matching method that suit
  it. Only the Streamlit presets did: the Shiny presets filled the conditions table and
  left 'Match on' at its general default, so one click on 'Dense vs sparse
  neighbourhood' asked the engine to match on `n_density`, the dimension the preset
  manipulates, and on `old20`, which follows it closely. The run did not fail; it
  returned a much weaker manipulation with frequency and length uncontrolled. Both apps
  now read the same table, which the suites pin against each other.
- The datasheet an app produces describes the design the app hands over. Both apps ran
  a rewritten copy of the design, with the lexicon and any item table resolved to
  absolute paths, so the `design_sha256` recorded in the datasheet inside the
  downloaded bundle was the checksum of a file that bundle does not carry, and
  'Materials source' named a directory on the machine that ran the app, which for an
  uploaded lexicon was a temporary one. Each input is now placed at the path the
  exported design records and the pipeline runs there, over the design exactly as it
  is shown, exported and archived.
- The realised-control chart in both apps draws one bar per comparison. The report
  carries one row per non-anchor condition per dimension, so a 2x2 design's three
  comparisons of a dimension were merged into a single bar by the Streamlit chart and
  drawn by Shiny as three bars sharing one unexplained label, where they differ by as
  much as five standard deviations. The bars are now grouped by condition and labelled,
  and the caption in both apps names the anchor they are measured against.
- The parity claim under the exported code depends on the method that ran. Both apps
  printed 'The R and Python engines produce byte-identical stimuli and trial order
  from this configuration.' whatever was chosen, which the method chooser's own help
  text, `apps/README.md` and the datasheet's 'Cross-engine determinism' line all deny
  for `mahalanobis` and `optimal`. Those two now get a sentence saying the engines
  select equivalent but not byte-identical stimuli, and the apps' opening paragraphs
  qualify the guarantee as the package documentation already does.
- Both apps refuse a factorial run with nothing to match on. 'Match on' can be
  emptied, and the pipeline accepts `match_on: []` happily, so the run reported
  success over a set that was never matched on anything and a realised-control tab of
  large effects, which reads as a matching failure rather than as a design that asked
  for no matching.
- A condition bound the conditions editor holds as text drops the factor it belongs
  to rather than the page. Both apps read the table while the page is being drawn,
  above the handler that reports a pipeline error, so the Streamlit app raised
  `ValueError` on such a cell and lost the whole page, results already on screen
  included, while the Shiny app wrote `c(NA, NA)` into the design as if the window had
  been asked for.
- Rows can be added to and removed from the Shiny app's conditions table. It offered
  cell editing and nothing else, so a design could hold exactly as many conditions as
  the chosen preset supplies, and a three-level factor, a fifth 2x2 cell or a preset
  row the user did not want meant editing the YAML by hand. 'Add condition' and
  'Remove selected' sit under the table, which is what the Streamlit editor has
  always allowed through its dynamic rows.
- The Shiny 'Match on' chooser names its dimensions as the rest of the interface does.
  It listed the raw column names while the tolerance panel beside it and the Streamlit
  multiselect both use the human labels the app already defines, so the two front-ends
  offered the same six controlled dimensions under different names.
- The Shiny app previews the lexicon and the item table before a run. It showed a bare
  chooser and a sentence naming the bundled example, where the Streamlit app shows the
  first rows of each, so the R user committed to a run without seeing a row of the
  input. The realised-control plot also carries alt text now.
- The Streamlit sidebar keeps its four design fields together. 'Stimulus font' was
  created two hundred lines below the sidebar block, and Streamlit places a widget
  where the call is made, so the field was drawn under the rule and the version line
  that close the sidebar, which is not the order either doc page describes. The unused
  placeholder above the rule is gone.
- The Streamlit app passes `width` rather than the `use_container_width` Streamlit
  deprecated with a removal date of 2025-12-31. The dev extra names no upper bound, so
  the release that drops the argument would have raised `TypeError` on the first
  render at all eight call sites and the app would not have opened; the extra's floor
  is now the release that added the replacement.
- The Streamlit app writes an uploaded lexicon or item table once per file rather than
  once per rerun, and a new run reclaims the previous run's temporary tree. The script
  re-executes top to bottom on every widget interaction and the uploader keeps handing
  back the file it holds, so a session with an uploaded corpus rewrote about a
  megabyte for every keystroke and slider move, and each press of Run left a complete
  set of artefacts behind for the life of the process.
- The Streamlit realised-control chart marks the half a standard deviation its caption
  names. The Shiny chart drew that line and this one did not, so the same numbers
  reached the two readers marked differently.
- A row missing one of the `match_on` dimensions is no longer selected, which counts
  as a breaking change for any design whose pool has such a row. The row has no
  distance to anything, so the anchored matcher paired an unscoreable anchor with
  whichever candidate sorted first, and, where the row came later in the anchor,
  re-picked an already-used candidate and then aborted with a message about
  overlapping conditions that named the wrong cause. The pairwise `joint` and
  `optimal` matchers had no filter either, and would take a pair with no distance at
  all to reach `n`. The matched conditions already lost such rows to their tolerance
  window; the anchor condition and both pairwise subpools now lose them too, and a
  shortfall is reported where the remaining rows do not reach `n`. This is reachable
  through any `norms:` table that does not cover the whole lexicon, which is the
  ordinary case. No shipped design has a hole on a matched dimension, so no committed
  artefact changed.
- A design that declares `conditions` but no `match_on` is refused by both engines.
  Python died with a bare `KeyError`; R read it as no dimensions at all, scored every
  candidate at distance zero, let the byte-order tie-break choose the items and then
  wrote a datasheet and a Methods paragraph saying they had been matched item by item
  on nothing. Both now stop with the same message.
- A design that names a paradigm keeps that paradigm's counterbalancing recipe when
  it declares its own `events`, which counts as a breaking change for one shipped
  design. The recipe used to fall back to factorial whenever an `events` list was
  present, so `config/design_en_priming_jitter.yaml`, which names `priming` and
  adjusts two durations, dealt every target to each list twice, once related and once
  unrelated. It now rotates through the Latin square like the other priming designs,
  and its committed stimuli and experiments are regenerated in both engines. No other
  shipped design changes.
- The R package declares its version floor. `Depends: R (>= 4.0.0)`:
  `tools::R_user_dir` does not exist before 4.0.0, and `round()`'s post-4.0 algorithm
  shapes artefact bytes, so an older R would fail obscurely or, worse, write different
  bytes without complaint.
- The R command-line wrapper says which copy of the package it loaded.
  `R_workflow/run_pipeline.R` prefers an installed lexsync over the edited sources,
  the opposite of the Python wrapper, so edits under `R_workflow/R` silently did
  nothing until a reinstall. The header comment states the trap and the remedy, and the
  wrapper prints the loaded copy (version, installed versus source) to stderr at
  startup, where no artefact or redirected stdout captures it.
- The pairwise matchers refuse to reuse a word. With overlapping condition windows,
  `joint` and `optimal` could pair a word with itself at zero cost, or mirror a pair
  (x with y, then y with x), so the same word appeared in both conditions, confounding
  the comparison the matching exists to protect. Both now track used words as the
  anchored matcher always has, the optimal cost matrix penalises self-pairs, and every
  matcher asserts its output holds each word at most once. Every committed design has
  disjoint conditions, and for those the selection is bit-for-bit unchanged. For overlapping conditions it changes, and under this
  project's versioning rule that is a breaking change, which is why it lands before 1.0.
- The match-quality report covers every matched dimension. The report dimensions
  were a fixed list (length, frequency, n_density, old20, plus two built-ins), so a
  custom norm joined via `norms:` and named in `match_on` was matched on but absent from
  the descriptives, comparisons and realised-control record, precisely the dimension
  whose realised balance most needs stating. The set is now the first-occurrence-order
  union of that list with `match_on`. Every committed report reproduces byte-for-byte.
- Datasheet prose follows the recorded verdicts. The Methods paragraph claimed
  "within the 0.5-SD equivalence bound" whenever a controlled dimension had a confidence
  interval, without consulting the TOST verdicts, and the committed en_andrews datasheet
  said it while its own JSON recorded `equivalent: false`. The sentence is now
  conditional on the stored verdicts, prints the signed worst difference beside a signed
  interval where it used to print the absolute value, reads the bound from the
  configuration where it used to hard-code 0.5, and blocks the affirmative wording when
  the effect size is undefined. The analysis note states that the equivalence tests are
  post-selection diagnostics on deterministically selected items, names the suggested
  formula as lme4 syntax (lme4 in R, pymer4 in Python; statsmodels MixedLM needs the
  random effects restated), and warns that dotted pair-design names need `Q("...")`
  quoting in Patsy-style interfaces.
- Selection-path rounding goes through the shared decimal rule. The matcher's 9-dp
  distance and cost roundings and the generated scripts' timeout seconds used native
  `round()`/`np.round()`, pairing two rounders the project itself measured to disagree
  at boundaries. The shared half-away-from-zero rule (`.round_dp`/`_round_dp`, now with
  a vectorised numpy twin) replaces them, and a static test keeps native rounding out of
  the matcher. The two 0-dp even-spread sites and the frame-to-ms conversion keep native
  rounding deliberately: they are half-even on exactly representable halves in both
  engines and pinned by goldens. Regenerating all 21 designs moved no stimulus,
  descriptive, comparison or experiment byte.
- Two mislabelled dimensions are relabelled. `bigram_freq`'s unit read "mean
  positional bigram probability", but the measure pools adjacent bigrams across
  reference types with no position in the count key, so it now reads "mean bigram
  probability (type-based, non-positional)". `length`'s unit read "letters", where both
  engines count Unicode code points, which for the shipped Chinese corpus are
  characters, so the unit now says so. Values are untouched, and the reproducibility docs
  additionally state the input contract (no NFC normalisation is applied, and the
  syllable and pseudoword machinery is defined for Latin orthographies).
- The app export is self-contained. Both apps' reproduction bundles now include the
  schema the run used at `config/schema.yaml`, and any repository-bundled corpus or
  example item table at the path the exported design names, so the bundled reproduction
  code runs from the unzipped directory alone.
- The corpus fetcher downloads to a temporary file first. The download streams to
  `<name>.csv.part` with a timeout and a 200 MB cap, is checked (scheme allowlist,
  markup sniff, and an optional per-entry `sha256:` in the registry), and only then
  renamed into the cache, so a truncated transfer can no longer be mistaken for a
  corpus.
- `selection.cross_engine` in the datasheet no longer reports "n/a (user-supplied
  items)" for a pair-keyed continuous design. That design does perform a
  selection over the item table, and the selection is byte-identical across engines,
  so the previous answer understated the guarantee on the one path where a reader
  most needs it. A plain item-table design, which selects nothing, still reports
  "n/a".
- `merge_norms()` returns the lexicon with the norm columns appended, in the lexicon's
  own row *and column* order, and looks the key up positionally, with no merge involved,
  so neither engine has any freedom left about the result's shape.
- Trial order within each counterbalancing list is now produced by a seeded,
  keyed-hash shuffle shared by both engines, which moves every shipped list and so
  counts as a breaking change. Each row is ranked by the
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
  now presented as one of the twelve worked examples bundled at the time.
- Pinned the optional `wordfreq` connector to the frozen 3.x line and documented
  that it is a stable snapshot of language usage through roughly 2021 (see
  `corpora/ATTRIBUTION.md`).
- An unknown `matching.method`, and a candidate pool too small for the requested
  `n_per_condition`, now raise an actionable error in both engines. Each used to
  degrade silently, to a default method or to a short set, and code that relied on
  that fallback will now stop.
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

- A design file could execute code on the machine that ran it. A design is meant to
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

  Both engines now validate these values. Escaping them correctly would mean three
  different rules for three targets in two engines, six places to get subtly wrong,
  whereas one rule leaves every legitimate value byte-identical. A port
  address must be an address, a column name must be an identifier, and a stated
  `language_tag` is shape-checked before it is used. `.pyq()` also
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
- The two engines' run logs report the same TOST p. The value is stored at four
  places and Python wrote all of them while R rounded to three, so the same
  comparison was recorded as 0.0016 in one provenance record and 0.002 in the other,
  and 1.0 against 1.000. Both now write four places, and both spell an undefined p
  'NA'.
- `resample.n_sets` is validated as `n_per_condition` already was. Zero or a negative
  number produced pandas' 'No objects to concatenate' in Python and an empty result in
  R, which the pipeline then reported nothing about, and a fractional number was
  truncated in silence. Anything that is not a positive whole number is now refused by
  name in both engines.
- Two messages name the alternatives, as every other 'unknown X' message in the
  package does. An unrecognised event type in a design's `events:` list now ends
  'Known types: fixation, text, mask, blank, region_by_region, response, question,
  feedback.', and an unrecognised `items.generation.method` names the two generators.
  An event carrying no `type` at all reaches the same message rather than a bare
  KeyError in Python and 'argument is of length zero' in R.
- `balance_check` names a column's levels in byte order in both engines. Python
  ordered them by descending count and R by the session's collation, so the same
  stimuli produced two differently worded warnings, which reach the run log, and the
  R wording additionally depended on the locale.
- Deriving `n_density` and `old20` in the Python engine is roughly twenty times
  faster. The two dimensions were measured with a Python-level loop over the pool and
  a second pass for Hamming distance, which on a 30,000-word lexicon costs minutes for
  a realistic pool. One edit-distance matrix, computed in C by `rapidfuzz`'s
  `process.cdist` a chunk of pool words at a time, now answers both: for two words of
  the same length an edit distance of 1 is exactly a Hamming distance of 1. Every value
  is a small exact integer, so the numbers are unchanged bit for bit and the R engine
  needs no change. This is reached only by a corpus that does not already carry the two
  columns, which the distributed ones do.

### Fixed

- The Python README's headline example calls `export_experiments` directly, as the
  R vignette's equivalent does. It wrapped the stimuli in
  `lexsync.scripting.assign_triggers` first, a step `export_experiments` performs
  itself and that both `api.md` and the triggers guide tell the reader to skip, so
  the package's front door taught a call its own reference calls unnecessary. The
  README test now runs the export too, into a temporary directory, so no statement
  of the example goes unexercised.
- The documentation names the languages the wordfreq connector actually reaches.
  Both READMEs and the module's own header said 'roughly forty', which is what
  wordfreq supports, while `fetch_corpus` takes that path only for the thirty
  language codes the registry lists and answers anything else with 'corpus is not
  in the registry'. The getting-started page had it right, so the package's own
  documents disagreed. The registry's comments still say '~40', where the number
  describes wordfreq rather than what lexsync exposes.
- The shared schema's triggers block names the setting it actually has. Its header
  comment still said the trigger is reset after `reset_after_frames`, six lines above
  the comment explaining that the frame count was replaced by `trigger_hold_ms`
  because a count of frames is not a fixed interval, so a reader following the
  getting-started page's invitation to read the schema looked for a key that is not
  there and was told the wrong unit. All three copies carry the correction, and the
  42 datasheets were regenerated because each records the schema's sha256.
- `lexsync fetch <language>`, which the README and the getting-started page both
  advertise, says what is missing when the wordfreq connector is not installed. It
  died on a bare `ModuleNotFoundError` naming neither lexsync nor the `corpora`
  extra that supplies the connector, where every other refusal in that module is
  branded and actionable. The connector itself is now exercised in CI, under a job
  that installs the extra, so its version pin is resolved rather than merely
  declared.
- A malformed design or schema is refused by name. `read_config` returns whatever the
  parser produced, so an empty design file, one written as a list, or one missing
  `name` or `language` reached the pipeline and failed on a type rather than on the
  file: the R engine went further still and wrote a nameless design's artefacts under
  a base name taken from the language alone, which collides silently with any other
  nameless design in that language. Both engines now check both files as they are
  read, and `run_all` names the design a failure came from, which a quiet sweep over
  twenty-one of them did not.
- `describe_stimuli`, `match_report` and `match_report_continuous` refuse a
  dimension or a grouping column the stimuli do not carry. All three are exported
  and documented for use on a selection of the user's own, where a misspelt name was
  a bare `KeyError` naming only the string in Python and, in R, a full descriptives
  table of missing values with a Cohen's *d* of zero beside it: a report that looks
  complete and describes nothing. Both engines now say the same thing. The pipeline
  filters its dimensions to the columns present, so no design is affected.
- The generated OpenSesame experiment waits as long for a response as the PsychoPy
  and jsPsych experiments generated beside it. The rendered event carries the window
  in seconds and the OpenSesame emitters converted it back with a truncation, so
  `timeout_ms: 1001` became 1000 there and stayed 1001 in the other two: 187 of the
  first 20,000 whole millisecond values were one short. Both engines now convert
  through the package's own rounder, which is what wrote the seconds. The shipped
  paradigms use round windows, so no committed experiment changed.
- A filter that lists permitted values compares them as R compares them. The Python
  engine compared `str()` on both sides, which renders 2.0 as '2.0' where R's
  `as.character()` gives '2', so `pool_filters: {band: [1, 2, 3]}` matched nothing on
  a column held as floating point, and a column is floating point the moment one value
  is missing. The pool came back empty and the run stopped much later reporting that a
  condition had no candidates, which names the wrong cause. A boolean is spelt `TRUE`
  and `FALSE` on both sides for the same reason.
- A two-element boolean filter is a pair of permitted values, not a range. `bool` is a
  subclass of `int` in Python, so `pool_filters: {is_noun: [true, false]}` was read as
  a reversed range and refused, while the same design filtered as intended in R, whose
  `is.numeric()` is FALSE for a logical.
- A run whose Cohen's *d* is undefined on every comparison now finishes in both
  engines. The statistic is deliberately undefined when two conditions are each
  constant on a dimension at different constants, and when no comparison on that
  dimension is numeric the column carries no numeric type at all, so the Python
  engine stopped on the run log line with a bare `TypeError` where the R engine wrote
  `NA` and completed. Python now writes `NA` there as well, so the two logs report the
  run alike. No shipped design reaches it; a supplied pool split by a dimension its
  conditions hold constant does.
- The two engines write the same materials datasheet. Nothing compared them: the
  byte-parity test excludes the datasheets and named a coverage elsewhere that did not
  exist, and under that the two renderers drifted apart on 122 lines across the shipped
  designs. The Python renderer wrote an em dash for `--` in the title and the suggested
  model, a Unicode ellipsis for the `...` that truncates a checksum, `True`/`False` for
  `TRUE`/`FALSE` and `1.0` for `1`, none of which the datasheet's own placeholder rule
  or the house prose convention allows. The TOST *p* now goes through `%g` in both
  engines, which is neither R's `9e-04` nor Python's `0.0009` but one form both write.
  The committed datasheets are regenerated, and the comparison the exclusion assumed is
  now made, over the committed pair and over a fresh sweep in the workflow.
- Every fixed-decimal number in the datasheet is rounded by lexsync's own rounder
  before it is formatted. A bare `%.2f` leaves the half-way case to the C library, and
  the runtimes disagree there: `en_andrews_repro` stored a confidence bound of -0.465
  and published it as [-0.46, 0.66] from R and [-0.47, 0.66] from Python, on the same
  machine. The Methods paragraph the documentation invites users to paste into a paper
  used the same format, so a published sentence could differ by engine. Cohen's *d*,
  the interval, the variance ratio, the correlation and the predictor span all go
  through the half-away-from-zero rounder the matcher already relies on, so the two
  engines print the same digits by construction. Sixteen published numbers across seven
  designs move by one in the last decimal place shown; the stored values are unchanged.
- The Methods paragraph keeps the language label's own capitals. Python's
  `str.capitalize()` also lower-cases everything after the first character, so a design
  written for 'British English' or 'Chinese (Mandarin)' had its label rewritten, and
  differently from the R engine. Every shipped design uses an all-lower-case label,
  which is why the two agreed until now.
- The committed datasheets publish checksums this repository reproduces. 28 of them
  recorded the sha256 of a CRLF copy of an input that `.gitattributes` checks out as
  LF, so a recipient who followed the datasheet's own instructions and recomputed the
  digest of `corpora/derived/en.csv` was told the materials had been altered. The
  reproducibility documentation quoted one of the wrong values verbatim. All 42
  datasheets are regenerated, and both suites now check every path and digest a
  committed datasheet publishes against the files in the checkout.
- The neighbourhood and bigram dimensions are derived wherever the design asks for
  them. The trigger was `match_on` alone, so a design that filtered on `old20`,
  defined a condition by `n_density` or took either as a continuous predictor stopped
  with the dimension reported absent unless the lexicon happened to ship the column.
  The shipped corpora do ship them, which is why no demonstration design showed it,
  but a user's own word-frequency list satisfies the lexicon contract without them.
  Both engines now take the union of `match_on`, the pool filters, each condition's
  `define_by` and the continuous predictor and controls. A filter on a dimension the
  lexicon does not carry is answered after the filters it can carry, so the
  derivation still runs on the pool rather than on the whole lexicon, and a misspelt
  filter name is refused as before.
- A generated experiment presents one counterbalancing list rather than all of them.
  The loop table carries every list, because one experiment file serves the whole
  study, and all three runners presented that file whole: under a Latin square each
  target was then shown once in every condition, often on adjacent trials, which is
  the repetition the rotation exists to prevent. Each run now presents the list the
  participant is allocated, by the rule `participant_table` follows. The PsychoPy
  script takes the participant number from `--participant` or `LEXSYNC_PARTICIPANT`,
  the jsPsych page from its `?participant=` query and the OpenSesame experiment from
  the subject number it asks for at start-up, where the trial runs behind a condition
  because a sequence has nowhere to filter its rows. All three present the first list
  when no participant is given, and a design with one list runs exactly as before. The
  committed experiments are regenerated; the stimuli and the loop tables are
  unchanged.
- `counterbalance.lists` above what the design can fill is refused. The factorial
  recipe deals item sets to lists round-robin, so asking for more lists than there are
  item sets left the high-numbered lists empty and absent from the stimuli and the
  generated experiments, while the datasheet and the Methods paragraph went on stating
  the number requested. The Latin square has the mirror failure: its rotation repeats
  after as many lists as there are conditions, so a further list duplicated an earlier
  one item for item. Both recipes now stop with the same message in both engines. No
  shipped design asks for more lists than it can fill, so no committed artefact
  changed.
- The pairwise matchers' candidate cap kept rows the R engine dropped. The cap sorts
  a condition's subpool by distance to the other condition's centroid and keeps the
  nearest 1,200, and Python sorted on a plain comparison key, which treats a missing
  distance as incomparable and leaves such a row wherever it fell, while R's `order()`
  drops it to the end. On a 1,300-row subpool holding ten unscoreable rows the two
  engines kept 62 different candidates, against a parity guide that says missing
  values are ranked last. Python now ranks them last, and R's two copies of the cap
  are one shared function.
- The compensated sum disagreed with itself across the engines on missing input. It is
  the primitive both run so that means, standard deviations and variances agree bit
  for bit, and on a missing value Python's `abs(s) >= abs(v)` is False and returns
  NaN while R's is NA and stops with "missing value where TRUE/FALSE needed". With a
  partially covering norm table that made `matching: method: joint` run in one engine
  and fail in the other. R now propagates the missing value as Python does; the mean,
  variance and standard deviation inherit the contract, and the median keeps its
  stated exception of dropping missing values before it sorts.
- The datasheet records the counterbalancing recipe that ran. Both engines inferred
  it from `items.source` while `counterbalance()` dispatched on the paradigm, so a
  table-sourced design could be recorded as a Latin-square rotation it never had; the
  record and the dispatch now come from the same function.
- `INTER_TRIGGER_S` leaned on each language's default number-to-string rule. Its
  neighbours in the generated PsychoPy script, `TRIGGER_HOLD_MS` and
  `ASSUMED_REFRESH_HZ`, are pinned through `%.17g`, but the inter-trigger interval was
  interpolated directly, so a non-integer `inter_trigger_ms` would have put different
  bytes into the two engines' scripts: 16.65 renders "0.01665" through R's
  `as.character()` and "0.016649999999999998" through Python's `str()`. Both engines now
  substitute it through the same `%.17g`. The shipped default of 10 ms still renders
  "0.01", so no committed experiment byte moved.
- The R half of the two-shortest-forms CSV guard never fired. Between 2^49 and 1e15
  two different one-decimal strings can round-trip to the same double, which is why the
  writer refuses such a value in both engines. But R derived the digit count from
  `format(t, digits = 15)`, which never shows a fractional digit in that band, so R
  accepted every value Python refused (844424930131968.2 among them). R now tests the
  neighbouring one-decimal strings directly and refuses exactly what Python's
  `_readr_cell` refuses. The change only adds refusals, so no artefact byte moved.
- A 16-digit integer column was written by one engine and refused by the other. The
  Python writer's >= 1e15 refusal applied only to floats, and pandas keeps such a
  column as int64, so Python wrote data that readr, which reads it as a double, made
  the R engine refuse. The check now covers integers, with the same message.
- A condition without `define_by` crashed the Python engine. The R engine falls
  back to the whole pool as that condition's subpool and, for the anchor, to ordering
  by frequency. Python indexed the key directly and died with a bare KeyError in the
  matcher and again in the datasheet's candidate-pool record. Python now mirrors both
  fallbacks, and a twin test pins the same selected words in both suites.
- A pair design's tolerance-window relaxation vanished from the record. The
  continuous-pairs selector re-expands the collapsed selection as a row subset, which
  drops the audit attribute in both engines, so a relaxed window reached neither the
  run log nor the datasheet while the corpus continuous path records it. The audit now
  survives the re-expansion and flows through the same path. No shipped pair design
  relaxes, so no committed artefact changed.
- `run_pipeline(verbose=False)` still narrated every step in Python. `log_step`
  printed unconditionally, so an embedding front end (the Streamlit app) got a running
  commentary it never asked for. The printer now sits behind a module gate the pipeline
  sets from `verbose`, mirroring the R engine's `options(lexsync.verbose)`, and every
  step is still recorded on the log itself.
- Scalar `_round_dp` raised where both its twins passed through. `_round_dp(1e306,
  3)` scaled to infinity, on which `math.trunc` raises OverflowError, while the R
  `.round_dp` and the vectorised `_round_dp_vec` return the input unchanged there. The
  scalar now does the same.
- The published median was the one reduction outside the exact primitives.
  `describe_stimuli` still paired R's `stats::median`, which averages the two middle
  values through `mean()`'s long-double accumulator, with pandas' `.median()`, which
  reduces through numpy: on some platforms that is a last-bit divergence in exactly the
  values the module header claimed were computed identically. Both engines now use an
  exact median: sort, take the middle element for odd n, `(a + b) / 2` in plain double
  arithmetic for even n. Regenerating all 21 designs moved no byte. The parity vignette
  said every reduction went through one compensated-summation algorithm, which the
  median never did and still does not. It now describes the sort-and-middle rule
  alongside the summation.
- The counterbalancing hash keys did not pin their encoding. The shuffle and
  balance tie-break digests hashed `paste()`'s stored bytes where `hash_unit` has
  always converted through `enc2utf8` first, so a latin1-marked condition read from a
  user's CSV would have ranked by different digests in R than in Python. Both keys now
  convert. No artefact changed.
- Both apps overstated a difference and understated a hash. Their caption said the
  engines select byte-identical stimuli while "only the seeded trial order differs by
  ecosystem", contradicting the keyed-hash shuffle that makes trial order itself
  byte-identical. Both now say the engines produce byte-identical stimuli and trial
  order, in the same words. And both wrote the design YAML with platform line endings,
  in the run copy that the datasheet hashes into `design_sha256` and in the export copy
  in the download bundle, so the recorded provenance depended on the operating system.
  Both apps now pin LF.
- A missing item cell became the string 'nan' in Python and a cryptic error in R.
  The Python item loader stringified cells before checking them, so a blank `condition`
  arrived at the hash-key guard as the legitimate-looking string "nan" and sailed
  through the very check built to refuse it, a blank `item` cell float-promoted the
  whole column so numeric identifiers became "1.0", and a whitespace-only cell slipped
  past everything. R refused the same table, but through a bare
  "missing value where TRUE/FALSE needed". Both engines now check missingness before
  any coercion and refuse a blank or whitespace-only `item`, `condition` or presented
  field with the same message, `item` is read as text so identifiers survive as
  written, and a duplicated item-and-condition row is refused, where the Latin square
  used to take the first silently. A literal string "nan" remains a valid label in
  both readers, and the twin fixture set pins each case in both suites.
- Cohen's d reported perfect balance for two unequal constant vectors. With pooled
  SD zero and a real mean difference (say every length 3 in one condition and 4 in the
  other), both engines returned d = 0 with CI [0, 0] while the TOST verdict on the same
  row correctly said not equivalent, an internally contradictory report. The
  standardised difference is undefined there, and is now reported as missing (empty CSV
  cell, JSON null) in both engines. Equal constants keep d = 0, which the committed
  zh_freqcontrast golden pins. The markdown placeholder for a missing value is "--" in
  both engines, where Python previously printed an em dash.
- A `continuous` block over a supplied pool never selected continuously. The
  predicate gating the continuous selector recognised `corpus` and `table` but not
  `pool`, so the design fell through to the conditions matcher and crashed with a
  different obscure error in each engine. `pool` is now in the set, and the pipeline
  path behind it already worked. Its two table-side cousins are closed with refusals:
  a `continuous` block with `items.source: table` and no `members` loaded the rows,
  selected nothing, and still stamped continuous mode into the log and datasheet (a
  provenance lie), and `pool_filters` on a plain table design were consumed by nothing.
  Both are now errors with the same message in both engines.
- Pair overlap was computed from list positions, not the named columns. With
  `members: [prime, target]` the positional call was right by coincidence, and any
  member listed before them would have silently redirected `pair.lev` and
  `pair.overlap` to the wrong column pair. The call now names `prime` and `target`.
- Config mistakes that silently changed the design are now refusals. A misspelt
  `pool_filters` key left the pool unfiltered, and the guard that existed on the pair
  path is now on the corpus path too. A misspelt `define_by` column handed the
  condition the whole pool as its subpool, erasing the manipulated contrast while the
  datasheet recorded full-pool candidate counts. Duplicate condition names, a reversed
  or non-finite filter range, a negative `tolerance_k` and a non-integer
  `n_per_condition` each produced downstream nonsense. And Python's YAML loader kept
  the last of two duplicated mapping keys while R's parser refused the file, so the
  twin engines disagreed at the input step. All are now errors, message-identical
  across engines where the message is lexsync's own.
- The R-versus-Python parity gate had not run since 15 July. `setup-r-dependencies`
  is invoked with `working-directory: R_workflow` and also asked for
  `local::./R_workflow`, which resolved to `R_workflow/R_workflow` and failed. Because it
  failed at the dependency-install step, everything after it was *skipped*: the R
  suite, the reference regeneration, the drift check and the engine comparison. The
  badge went red, but the gate that enforces the headline byte-identity claim had
  simply stopped executing. Now `local::.`, which is what `docs.yml` always
  used.
- A browser experiment could score a feedback screen against the previous trial's
  keypress. The jsPsych feedback screen looked up "the last row marked scoreable",
  which is that trial's response only when the trial has one. An event may be restricted
  to a block, so a design that runs the response event in one block and feedback in
  another leaves a trial with no response row of its own, and the screen then reported a
  verdict computed from an earlier trial's key. Each trial's rows now carry its own
  identifier and the screen matches on it, so a trial with no response of its own reports
  none. The generated HTML changed for all 21 designs. No stimulus selection changed.
- A large number in a user's own column was written differently by the two engines.
  The CSV writer reproduced readr's format for small magnitudes and left the top end
  alone, on the grounds that nothing lexsync computes reaches it. Nothing lexsync
  computes does. A joined norm table, a supplied pool or an item table carries whatever
  columns the user has, and those go straight into the stimuli CSV. The guarantee
  therefore held for the shipped designs, which the byte-parity test covers, and failed
  silently for the user's own data, which nothing covers. The divergence started lower
  than assumed: readr writes 1e15 as `1e15` where the Python writer wrote it in full,
  and a value of exactly 2^53 picked up a trailing `.0` in one engine only. readr's
  layout beyond 1e15 could not be reproduced. It writes 1.5e16 as `15e15`, the largest
  double as `17976931348623157e292`, and the double nearest 5e22 as
  `4.9999999999999996e+22`, and no rule fits all three, so both engines now refuse such
  a value and name the column. One engine accepting it would leave the two writing
  different bytes. A value with two equally short decimal forms is refused for the same
  reason: readr prints 1000000000000000.25 as `...0.3` and Python as `...0.2`, and the
  digits
  themselves differ. Everything the two engines were verified to render identically,
  across 465 values compared against readr's own output, still writes as before.
- A generated OpenSesame experiment carrying a `feedback` event or a `blocks:`
  restriction would not run at all. The emitter wrote `unicode(...)` into the inline
  script, a Python 2 builtin that OpenSesame 3.3's Python 3 workspace does not inject, so
  the experiment died with `NameError` on the first trial regardless of which block that
  trial belonged to. The same scripts passed `None` as a `var.get()` default, which
  OpenSesame's var_store cannot distinguish from no default and so raises on where it
  should return. Both spellings are now pinned by a test in each engine, and a
  `feedback` event with no preceding `response` or `question` is refused at generation
  time, which is where it used to fail three different ways at run time.
- The three rounding policies in play disagreed. Measured over 210,000 values
  including every three-decimal halfway case in range: R's `round()` disagrees with
  Python's builtin `round()`, Python's builtin disagrees with `numpy.round()`, and even
  R's `sprintf("%.3f")` disagrees with Python's `"%.3f"` on 274 of them, because R's
  delegates to the platform C library. The descriptives path paired R's `round` with
  Python's builtin and the distance path paired it with numpy's, so no artefact value was
  safe. Both engines now use one rounder defined by its arithmetic. That arithmetic is to
  scale, truncate and step away from zero at a half, and IEEE-754 either mandates every
  one of those operations correctly rounded or makes it exact. Some reported values move
  by one in the last published digit. No selection changes.
- A hash-key component that cannot be rendered identically is now refused. A blank
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
- `R CMD check --as-cran` had a WARNING and an undocumented NOTE, while
  `cran-comments.md` claimed "0 errors | 0 warnings | 1 note". `select_continuous_stimuli()`
  documented four of its seven arguments. `head()` was called without an import, so a user
  who defined their own would have had it called by the package. Both fixed, and the check
  is now clean at 0/0/1.
- The package's only example could never have worked. It called `read_config()`, which
  is not exported, from inside a `\dontrun{}` that R CMD check therefore never ran. The
  example now uses only exported API, runs offline against bundled data, and every main
  entry point now carries an executable example.
- Three factual corrections, each verified against the source. The SUBTLEX-PT registry
  entry cited `10.3758/s13428-014-0511-x`, which Crossref resolves to an unrelated
  psychometrics program by different authors. The matching vignette placed Zipf 7 at a
  thousand occurrences per million where the correct figure is ten thousand,
  contradicting its own lower anchor. A design comment attributed "840-prime materials"
  to Rastle et al. (2004). That paper used 150 prime-target pairs, and the figure
  appears nowhere in it.
- The Python engine embedded a bare `NaN` in the generated jsPsych experiment, where
  a trial had no value for a field that another block supplies, as in a main-block trial
  in a design whose practice items carry an `answer`. `NaN` is not valid JSON, and the R
  engine dropped the key instead, so the two engines' experiments differed byte for byte.
  Both now drop it, which is also the honest rendering: a trial with no correct answer
  has none. Found by running the two engines into separate directories. Both write the
  shared experiment files to one path, so a normal run has the second silently overwrite
  the first.
- The generated artefacts were not byte-identical across the engines, and the parity
  test could not see it. It read both CSVs back with a parser and compared the values,
  under which `1` and `1.0` are the same number. Thirteen of the 18 shipped designs
  differed byte for byte while the gate stayed green. Three of the differences were
  matters of serialisation, namely a whole number written `1` by readr and `1.0` by
  pandas, a boolean written `FALSE` and `False`, a value below 1e-3 written `9e-4` and
  `0.0009`. The fourth was not. Two reported means differed in the last decimal the
  descriptives publish, because numpy sums pairwise and R's `mean()` uses a two-pass
  long-double algorithm, and the true value sat on a rounding boundary. Every reduction in
  the package now uses one Neumaier compensated summation written out in both engines, so
  their agreement follows from IEEE-754 requiring addition and subtraction to be correctly
  rounded, and no longer from a measurement of two libraries' internals. No R golden
  moved, because R's two-pass mean was already the correctly-rounded one, so the fix
  brought the Python engine into line. Artefacts are now compared as bytes, not as
  parsed values.
- A response key coded `f` was silently turned into `FALSE`. `readr` reads a column
  whose values are all `f`, `t`, `T` or `F` as logical while pandas keeps the string, so
  an item table using the commonest two-choice key pair had its correct answer corrupted
  in the R engine alone. Measured on readr 2.2.0: `f`, `t`, `T` and `F`
  infer as logical; `j`, `y` and `n` do not. Item tables now read the condition label and
  the paradigm's presented fields as text in both engines.
- The datasheet was truncating its own provenance. `jsonlite::toJSON` defaults to four
  digits, so a design declaring `tolerance_k: 0.1111111111111111` had it recorded as
  `0.1111`, which does not reproduce the run the record exists to describe. Most fields
  escaped only because they are deliberately rounded on the way in. Both engines now
  write the JSON at 15 significant digits.
- The matcher's z-scoring centre and scale also go through the compensated reductions.
  The difference could not have changed a selection, for a structural reason: a
  distance is between z-vectors, so a shift in the centre cancels and a change of scale
  cannot reorder candidates. That argument is weaker than identity by construction,
  which is what the package claims, and the change was verified to move no design's
  selection.
- `merge_norms()` column order differed between engines. R's `merge()` hoists the
  join column to position 1 while `pandas.merge` keeps the left frame's order, so the
  two engines returned different column order whenever `on` was not already the first
  column. Measured on both engines, then removed structurally, with no repair after
  the fact.
- `merge_norms()` case-folded only one side of the join key. A lexicon holding
  `Dog` against a norm table holding `dog` matched nothing, and the design carried on
  with an all-missing dimension. Both engines agreed on that wrong answer, which is
  why no parity test could have caught it. The lexicon's own spelling is preserved:
  `word` is the byte-order tie-break behind every selection.
- A colliding norm column was silently renamed. R's `merge()` produced
  `frequency.x` / `frequency.y` and pandas `frequency_x` / `frequency_y`, so a design
  matching on `frequency` found neither, in either engine. It is now an error naming
  the clash.
- The R engine wrote its datasheet and Markdown run log with CRLF on Windows
  while the Python engine wrote LF, because `write_datasheet()` and `write_run_log()`
  used a text-mode connection, bypassing the package's LF-pinning writer. The
  datasheet is the provenance artefact. Its bytes must not record which machine
  produced it.
- `add_pair_overlap()` and `resolve_trial_timing()` were not exported from the R
  package. Both were marked for export and documented, but `NAMESPACE` had not been
  regenerated, so `library(lexsync)` did not make them available.
- A word missing from a lexicon row became the literal string `"nan"` in Python
  while R dropped the row. Both engines now drop it before string coercion.
- `participant_table()` crosses its factors in `expand.grid()` order in both
  engines, so either allocates the same cell to a given participant number.
- `merge_norms()` preserves the lexicon's row order in R, as pandas does.
- Datasheets record the tolerance windows and the pseudoword generator that ran, filter
  dimensions identically in both engines, and report the running package version they
  were built by.
- The matcher raises where it used to re-pick an already-used row, when a relaxed
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
- The guides state what the engines do, leaving what they used to do to this file. The
  matching guide said an unknown `pool_filters` column is skipped silently, which is
  true of a direct `build_pool()` call but not of the pipeline, and said `verbose` was
  the only report of a relaxed tolerance window, which the matcher's audit record, the
  run log and the datasheet have since answered. `build_datasheet`'s `report` argument
  is the object `match_report` returns rather than a data frame, and it is supplied for
  generated items and pair-keyed tables too, and `fetch_corpus` prints the citation when
  the download completes rather than recording it.
- The Python documentation site's Demo pill answers keyboard focus. It inverted under
  the pointer but carried no `:focus-visible` state, and it is the only header control
  the brand restyles wholesale, so it was the one item a reader tabbing through the
  header could not locate. It now takes the same inversion plus an outline ring, as the
  R site's Demo link already did.
- A `registry_path` that does not exist is refused rather than quietly replaced. The
  Python engine put the caller's path at the head of the same search list as the
  environment variable, the two checkout locations and the bundled copy, so a stale or
  misspelt one fell through and `list_corpora` and `fetch_corpus` reported another
  registry's corpora under it. Both engines now refuse it by name, which is what the
  package already does for an explicit `--schema`.
- The `registry.yaml` bundled with each package is the repository's own again. Both
  mirrors are maintained by hand and both had fallen a line behind `corpora/registry.yaml`,
  the line documenting the optional `sha256` an entry may carry, so an installed copy of
  either package described the registry format less fully than a checkout did while
  README.md says that adding a corpus takes an entry in that one file. The suites now
  hold the mirrors to it, and the bundled example lexica to each other, as they already
  did for the schema.
- `corpora/fetch_corpora.py` writes the derived lexica with LF line endings whatever
  built them. pandas follows `os.linesep` unless told otherwise, so a rebuild on Windows
  wrote CRLF into `corpora/derived/*.csv` and both packages' example slices, and the
  datasheet publishes the SHA-256 of the lexicon a run read: a digest that depends on the
  machine that built the file tells a recipient the materials were altered when they were
  not. Its two siblings already pinned LF, and a check that the committed lexica carry no
  carriage return now catches one being committed.
- Two runs of the Streamlit app at once each read their own materials. The run makes
  its staging directory the working directory so the design's relative paths resolve
  there, and that directory belongs to the process rather than to the browser
  session, so two overlapping runs both read whichever staging directory came last
  and both reported success. One user with two tabs open was enough. The runs now
  take the directory one at a time.
- The Shiny app's realised-control chart leaves a gap where Cohen's d is undefined.
  The bars were summed into their cells, which writes a zero for a comparison that
  is absent or undefined, so a dimension on which both conditions are constant, the
  case the pipeline reports as `--`, drew the bar of a perfectly matched dimension.
  The Streamlit chart already omitted it.

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
  (Cohen's d, 90% CI and a TOST equivalence test), alongside a pre-registration
  template and a machine-readable corpus registry.
