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

- `counterbalance.max_run` caps runs of one condition, or of one value of any column named
  in `counterbalance.run_on`, in the trial order, in both engines. `counterbalance`
  repairs the seeded order deterministically, taking at each step the earliest trial in it
  that keeps the limit and leaves the rest of the list able to keep it, so it refuses only
  a limit no order can meet, with a message giving the counts. A missing value counts as a
  value of its own. With fillers, the limit applies to the order they are interleaved in,
  and the practice trials keep it on their own. The datasheet records the limit and the
  longest run realised in each presentation version as `counterbalancing.max_run`, a field
  of datasheet format 1.2, and the Methods text states it, citing van Casteren and Davis
  (2006). The shipped designs hold runs of up to eleven trials of one condition, and the
  lexical decisions up to seven consecutive trials with the same correct key. Both new
  keys are off by default, so no shipped design changes.
- `counterbalance.orders: m` gives each list m trial orders, in both engines.
  `counterbalance` adds `order_1` to `order_m`, each trial's position in each order, to
  the stimuli and the loop tables. Order 1 is the seeded order, and order j from 2 is
  ranked by the SHA-256 of `seed|order<j>|replicate|list|set|condition`. Participant p
  runs version `((p - 1) mod V) + 1` in order `(((p - 1) div V) mod m) + 1`: the
  PsychoPy script and the jsPsych page sort the version's trials by that order and
  record it in every data row, and OpenSesame gets one experiment per version and order,
  `<base>_list<k>_order<j>.osexp`, whose start-up check compares the order too.
  Participants on one list no longer all meet the same order. The datasheet records
  `counterbalancing.orders` (the number of orders and the rule), a field of datasheet
  format 1.2.
- `counterbalance.scale: mad` balances lists on each dimension's deviations from its mean
  in units of its mean absolute deviation, so a dimension's weight no longer depends on
  where its scale starts. The values are rounded to hundredths by the shared rounder
  before the integer mean and the unit are taken, so adding a constant that is a whole
  number of hundredths leaves the lists unchanged. The default, `mean`, divides by the
  dimension's mean, which suits ratio scales only: Zipf frequency, whose scale starts
  near 3, carried the least weight of the four dimensions in `en_balanced_lists`, and
  re-expressing it as Zipf - 3 moved 22 of 40 sets to another list. The default is
  unchanged so running studies keep their lists. Under `mad`, the `balance_lists` report
  and the datasheet's `counterbalancing.optimise` record give `scale`, a field of
  datasheet format 1.2, `cost_unit` names the unit and the Methods paragraph names the
  scale. `validate_design` refuses any other scale, and the key joins the design
  vocabulary in both engines, whose suites pin the new digest. The optimiser's
  exact-integer guard now bounds the sum of the absolute set totals, since signed
  deviations can sum to near zero, and gives the same answer as before for values of
  one sign. The schema's comments describe the option in all three copies. The edit
  changes `config/schema.yaml`, so every committed datasheet records a new schema
  digest and every run log a new datasheet checksum. The twin-edge cases `scale_mad`
  and `scale_unknown` pin both engines to one outcome.
- `normalise_lexicon` turns a delimited corpus file into a lexicon `load_lexicon` reads,
  in both engines. It applies a column map, reads tab-separated files, derives Zipf values
  from frequencies per million (Zipf = log10(per million) + 3) and writes `word` and
  `freq_zipf`, with `freq_permillion` and `pos` when the file has them. Words are
  lower-cased and put in NFC, and a form listed more than once keeps its first row or,
  under a registry entry's `duplicates: sum`, the sum of its rows' frequencies, as Lexique
  needs. A line on standard output counts the derived values that lay within 1e-9 of a
  rounding boundary, the one step at which the two engines' `log10` could round a value
  apart, and a run over a lexicon carrying `freq_permillion` records the count in its run
  log and as `materials_source.zipf_derivation`, a field of datasheet format 1.2.
  `fetch_corpus("subtlex_us")` downloads SUBTLEX-US from openlexicon, checks its SHA-256
  and normalises it in either engine. No registered corpus could be fetched before. An
  entry may also name a `derived` file, a lexicon already normalised, which is fetched in
  its place. The registry header describes this route where it said that the column maps
  were not yet applied. Lexique 3.83 stays a listed entry: the manual confirms that it
  splits a homograph's frequency between rows, so the entry records `duplicates: sum`,
  but the forms its film corpus never attests carry a frequency of 0, which has no Zipf
  value.
- `lexsync fetch NAME --n-words N` sets the size of a lexicon the wordfreq connector
  builds, 10,000 forms by default as before. The getting-started guide and the README give
  the commands that built the committed lexica (30,000 forms for English and Spanish,
  20,000 for Chinese), and the usage line of `corpora/fetch_corpora.py` now gives them
  too.
- A `masked_priming` paradigm presents a forward mask of hash marks for 500 ms, a
  lower-case prime for three frames and an upper-case target that stays until the
  response, the procedure of Forster and Davis (1984). Without a forward mask, a prime
  this brief is usually visible. The target collects its response from its onset and
  stays on screen for the whole 2,000 ms window. A text event's `case: upper` or
  `case: lower` is applied by the runners when they display it, with `str.upper()` and
  `str.lower()` in PsychoPy and OpenSesame and `toUpperCase()` and `toLowerCase()` in
  jsPsych, so the loop tables and the data files keep each item as it was written.
  lexsync does not change the case itself, because R's `toupper()` leaves "ß" as it is
  where Python gives "SS". A mask's `length_of` names the fields whose longest value
  sets its length. Its one character is repeated as many times as that value has
  characters, not bytes, counted over every trial when the experiments are written, so
  each target and each list shows the same mask. `validate_design` refuses a case other
  than upper or lower and a `case` on any event but a text event. It also refuses
  `length_of` on any event but a mask and on a mask whose content is not one character.
  `export_experiments` refuses a `length_of` field the trials do not have. The two keys
  join the design vocabulary in both engines, whose suites pin the new digest, and the
  schema's comments describe them. The `priming` paradigm is unchanged and is
  documented as backward-masked, as is its label in the demos index. The registry is
  pinned by a digest that both suites compute, so a paradigm changed in one engine only
  fails both. Every demonstration's experiments, datasheets and run logs change,
  because the PsychoPy and jsPsych templates do. The twin-edge case
  `masked_priming_text` pins both engines to one outcome.
- Generated experiments show task instructions before the first trial and wait for the
  space bar, so the experimenter can start the run when the participant is ready. A
  design sets the text with `instructions`. It may hold line breaks and no other control
  character, and every target carries it as data. Without it, a lexical decision, a
  categorisation and a design with comprehension questions get English instructions that
  say what their keys mean. The run log notes a design in another language that gives no
  text of its own, and a design whose keys the instructions can only name, as in every
  factorial and priming demonstration. A lexical-decision design states its response
  mapping: word on the response event's first key and pseudoword on its second, unless
  the design gives `response_mapping`, and `rotate_mapping_by_list: true` rotates the
  keys across lists. A mapping that names a key the response event does not allow, or
  leaves a condition's trials without an answer, is refused. The loop tables carry each
  trial's correct key in `answer`, so accuracy can be scored on every trial of a lexical
  decision, where it could be scored only on practice and filler trials. jsPsych records
  a key by the browser's name for it, so the jsPsych page names each answer that way,
  `arrowleft` for `left`, as it already named the keys, and in every target a correct
  response equals its trial's answer. `export_experiments` derives the answers as it
  assigns the trigger codes, so the stimuli file does not change. A practice or filler
  table keeps its own answers, and the run log notes any that the mapping contradicts.
  The datasheet records the mapping as `presentation.response_mapping`, a field of
  datasheet format 1.2, and its Methods text says which key the participants pressed for
  which condition. The schema's comments describe the three keys. Every demonstration's
  experiments, datasheets and run logs change, and the loop tables of the three lexical
  decisions carry an answer on every trial. The twin-edge cases `mapping_rotated` and
  `instructions_text` pin both engines to one outcome. No design selects different
  items.
- `items.generation.exclude` lists further word forms that a generated pseudoword
  must not equal: files with one form per line, CSV files with a `word` column, or
  corpora fetched into the cache with `fetch_corpus`. The forms are normalised as
  a lexicon's words are, and the datasheet records each list with its checksum as
  `selection.generation_exclude`, a field of datasheet format 1.2. The Methods
  paragraph names the lists. The generators checked only the lexicon, whose
  English and Spanish forms stop at Zipf 2.95 and 3.11, so real words such as
  crier and pall, and in Spanish renos and esteras, passed as pseudowords.
  `generate_pseudowords` and `build_lexdec_stimuli` take the list as `exclude`.
  The repository's `corpora/fetch_corpora.py --known-forms` writes wordfreq's
  fuller word lists for this purpose (289,023 English and 334,625 Spanish forms),
  and neither package ships them. No shipped design uses the key yet, so no
  stimulus moves. The schema's comments describe it, so the 42 committed
  datasheets, which record the schema's SHA-256, and their run logs are
  regenerated. The twin-edge case `generation_exclude` pins both engines to one
  outcome.
- Lexical-decision generation works with accented letters, in both engines. The
  generators' alphabet is the set of letters the reference lexicon attests, in UTF-8
  byte order. A Spanish design therefore keeps its accented words, 16.5% of a typical
  band (1,368 of the 8,305 words of length 4-7 and Zipf 3.5-6, among them 261
  preterites in `-ó`), and can generate accented pseudowords. The generators
  substituted only the letters a to z and left those words out. A word is now eligible
  when every character in it is a letter the reference attests, so a word with a
  hyphen, an apostrophe or a digit is still left out. The subsyllabic segmenter finds
  its nuclei among accented vowels too, and `make_pseudoword` gains an `alphabet`
  parameter. A word in a logographic script, such as Chinese, is refused with a
  message. Unicode counts its characters as letters, but a form made by swapping one
  for another is of unknown validity as a pseudoword. A generated design's datasheet
  counts the eligible words, so the Spanish band above now counts all 8,305. A new
  example, `es_lexdec`, checks its pseudowords against wordfreq's Spanish word list.
  English selections and every other committed output are unchanged. The twin-edge
  case `generation_exclude` gains a hyphenated word, which the count leaves out, and
  its known-form list now names the forms its new selection would otherwise produce.
  The new case `lexdec_logographic` pins the refusal in both engines.
- A screened English lexicon, `corpora/derived/en_v2.csv`, holds the same 30,000
  wordfreq forms as `en.csv` with columns from SUBTLEX-US (Brysbaert & New,
  2009): `in_subtlex_us`, `lowercase_share` and `nonstandard`, which marks forms
  absent from SUBTLEX-US or beginning with a lower-case letter in under a tenth of
  their uses (names, acronyms and many internet forms, 6,565 in all). Its N and
  OLD20 are computed against the 23,435 unmarked forms only, so the marked forms
  no longer count as neighbours (`cat` has 21 where `en.csv` gives 32), and
  `n_density_raw` and `old20_raw` keep the old values. Filter with
  `pool_filters: {nonstandard: [0, 0]}`.
  `en.csv` is unchanged, so designs that must reproduce earlier selections keep
  working. `corpora/fetch_corpora.py --screen-en` rebuilds the file byte for byte
  from a SUBTLEX-US copy whose checksum it verifies, and `corpora/ATTRIBUTION.md`
  and `LICENSE-DATA` credit SUBTLEX-US as its direct source. This is repository
  data, and the package example slices follow later.
- A design can exclude words with `exclude_words`, a list or a file with one word
  per line, applied before the pool filters and recorded in the datasheet with
  its checksum. The words are keyed as a lexicon's are and leave the candidates
  of a corpus, pool or generated design after the norms join. The neighbourhood
  reference, and the words a generated pseudoword must not equal, keep them. The
  datasheet records the list as `materials_source.exclusions` (its path or
  `inline`, checksum, words listed and candidates removed), a field of datasheet
  format 1.2, the run log notes the removal, and the Methods paragraph reports
  it. A design with an item table refuses the key. The twin-edge case
  `exclude_words_inline` pins both engines to one outcome.

- `matching.tie_break` chooses how exact ties between equally close candidates are
  broken. `bytes` breaks them by spelling, as lexsync 0.1 did, and reproduces its
  selections. `hash` breaks them by a keyed SHA-256 of each word
  (salt `lexsync-tie-v1`), which favours no part of the alphabet and does not
  depend on the seed. Ties decide most picks because lengths and neighbourhood
  counts are whole numbers and frequencies have two decimals. In `en_freqcontrast`,
  71 of the 80 anchored picks had another candidate at the chosen distance, and
  breaking them by spelling filled conditions with early-alphabet words. In its
  low-frequency condition, 61% of the words began with a or b, against 13% of the
  candidates, and in `en_ndensity`'s dense condition and the `en_andrews_repro`
  low-frequency cells every word did, an initial-letter confound the
  realised-control report cannot see. Under `hash`, the low-frequency share fell to
  12.5% and the dense share to 17.5%, against 13% and 12% among the candidates,
  and Cohen's d on every matched dimension of every shipped matched design was
  unchanged. The rule decides the anchored picks, the order of tied pairs in
  `joint` and `optimal` matching and the rows tied at their candidate cap. The even
  spreads that pick the anchor's items and a continuous design's items keep the
  byte order. Under either rule, `standardised_euclidean` and `joint` select
  identical items in the two engines. The datasheet records the rule as
  `selection.tie_break`, a 1.2 field, with the salt under `hash`. Its Markdown no
  longer says that selection is deterministic given the seed and free of
  item-selection bias. Selection does not depend on the seed, which fixes the
  trial order, and the Markdown and the Methods paragraph now say so. The Methods
  sentence that read 'deterministic and reproducible (seed 2026; lexsync 0.1.1)'
  now reads 'deterministic and reproducible (lexsync 0.1.1), and the seed (2026)
  fixes the trial order'. The schema gains `tie_break`, and the twin-edge case
  `tie_hash_small` pins the `hash` rule in both engines.
- `triggers.mode` (`auto`, `hardware` or `mock`) decides what the PsychoPy and
  OpenSesame experiments do when the trigger device cannot be opened. `hardware`
  refuses to start: the PsychoPy script stops before its window opens, and the
  OpenSesame experiment stops in its setup. `auto`, the default, falls back to
  printing the codes as before, but now says so on screen before the first trial,
  where the experimenter presses C to go on, and records the mode with every trial,
  as `trigger_mode` in the PsychoPy data file and as `lexsync_trigger_mode` in the
  OpenSesame log. Both experiments used to run on without triggers and with no
  notice on screen, and only the OpenSesame log said so, in its `test_mode` column.
  `mock` prints the codes without trying the device, after the same notice.
  `triggers.backend: serial`, with `triggers.serial_port` and `triggers.baudrate`
  (115200 by default), sends each code as one byte over a serial port in both
  experiments. The OpenSesame setup had a serial branch that ran only once the
  script was edited by hand, and it then opened the first serial port it found. The
  OpenSesame snippet `templates/opensesame/inline_trigger_setup.py` took the first
  serial port too, and now opens the one named at its top. `validate_design`
  refuses a serial backend without a port, a port name that cannot be written into
  the experiments, a mode or backend lexsync does not know, and a baud rate, text
  height or full-screen setting of the wrong kind, before anything is written. The
  experiments guide describes the delay a USB-serial adapter adds. The twin-edge
  case `trigger_serial` pins both engines to one outcome.

### Changed

- Every generated PsychoPy script and jsPsych page carries `ORDERS` and the code that
  picks an order (see `counterbalance.orders` above), so their bytes change, and so do the
  checksums the datasheets record of them and of the schema, whose comments describe the
  new keys. No stimulus, loop table or OpenSesame experiment moves.
- The `en_rastle_repro` example uses masked priming with nonword targets, and
  `en_andrews_repro` gains pseudowords, so both run as lexical-decision tasks.
  `en_rastle_repro` interleaves twelve nonword targets, each with a word prime, as
  fillers (`items/rastle_nonword_fillers_en.csv`), and `en_andrews_repro` one
  pseudoword per selected word (`items/andrews_pseudoword_fillers_en.csv`). The
  nonwords were made once with the package's letter-substitution generator and checked
  against wordfreq's known English forms, and each design's comment gives the command
  and lists what still differs from the original study. Each design puts its word
  conditions on the left arrow key, gives its fillers the right and shows its own
  instructions. Their stimuli files gain a `block` column and their trials are
  renumbered, since the fillers are interleaved with the words. The items, sets, lists
  and conditions are the same, and no descriptives or comparisons change.
- `CITATION.cff` and `codemeta.json`, which describe the repository and so both
  packages, give the Zenodo concept DOI,
  <https://doi.org/10.5281/zenodo.22906962>, which
  archives every GitHub release of both. They gave the DOI that CRAN assigned to
  the R package as the DOI of the whole of lexsync. `CITATION.cff` now lists each
  package's identifiers, marked with the package they name: the CRAN DOI and the
  CRAN page for the R package and the PyPI page for the Python package. Its
  single `repository-artifact`, which named CRAN alone, is gone.
  `codemeta.json` gives both packages' references, each with its own DOI. Each
  package's own citation is unchanged: the R package's gives the CRAN DOI, and
  the Python package's gives the Zenodo DOI, since PyPI assigns no DOI.
- The CRAN DOI and the Zenodo DOI are shown as full links in the READMEs, on both
  sites and in this file. The Python home page ends with the Zenodo concept DOI,
  <https://doi.org/10.5281/zenodo.22906962>, and the footer of every page no
  longer carries the Zenodo badge. The R package's README gains a badge for the
  DOI CRAN assigned, which the R home page leaves out of its sidebar, where the
  DOI is already given under Citation. Each README's badge row ends with its DOI
  badge.
- The parity gate also runs both engines over small edge-case designs (padded
  fields, missing values, unusual YAML) and compares each with a pinned expected
  result, so a defect the two engines share can no longer pass because they
  agree. The cases live in `parity/twin_edge/`, and each suite holds its own
  engine to them (`test_twin_edge.py`, `test-twin-edge.R`).
  `tools/compare_engines.py` runs the whole-tree comparison locally, and
  `tools/twin_edge.py --update` writes a case's pinned files.
- Both engines read CSV input by one rule. Header names and fields are trimmed,
  and an empty field or `NA` is missing. A column is numeric only when every
  value is a plain decimal number (no thousands separators), logical only when
  every value is TRUE or FALSE (in upper, lower or title case), and text
  otherwise. The Python engine did not trim, so a padded category or header made
  it refuse a design the R engine ran. The R engine guessed types from the first
  1,000 rows and read `T` and `F` as logical, `1,000` as a number and ISO dates
  as dates, so a pass-through column could be written `F` by one engine and
  `FALSE` by the other. A header that names a column twice is now refused, an
  empty header cell is named by its position (`...3`), and `load_lexicon`
  refuses a frequency column that is not numeric, naming the first value that is
  not a plain number. The R engine parses every plain decimal number to the
  nearest double, as Python's `float()` does, because readr's parser could miss
  it by one unit in the last place (`50.768212762897100`, for instance). A number
  of up to 15 significant digits, with a power of ten within 10^22, takes one
  exact operation, and any other is rounded in exact integer arithmetic, because
  R's `as.numeric()` misses as well, now and then on x86-64 and far more often on
  Apple Silicon, where R CMD check read `0.12345678901234567` one unit away.
  R wrote a negative zero as `-0` and Python as `0`, so both engines now read it
  as zero. Every demonstration's stimuli and reports are unchanged. Three
  twin-edge cases pin the outcome: `padded_pos`, `padded_header` and `tf_column`.
- Changes list assignment: a paradigm's Latin-square recipe now applies when a
  design lists its own `events`. Any `events:` list made `counterbalance()` deal
  the items factorially, so a priming, categorisation or self-paced reading design
  with per-trial timing showed every target in both conditions of each list (in
  `en_priming_jitter`, six targets per list, each twice), while the datasheet and
  the Methods text described a Latin square. `counterbalance.recipe` (`factorial`
  or `latin_square_target`) overrides the paradigm's recipe, and
  `counterbalance.optimise` is now refused for these designs, as for every
  Latin-square design. Of the shipped examples only `en_priming_jitter` moves: each
  of its two lists now shows all twelve targets once, and its stimuli, experiments
  and datasheets are regenerated in both engines.
- The datasheet, now format 1.2, records the counterbalancing that ran. It takes
  the recipe from the resolver that `counterbalance()` dispatches on, and no longer
  infers it from the item source, which recorded a table-sourced lexical-decision
  design as a Latin square. It records the lists the counterbalancing realised, in
  place of `counterbalance.lists` with a default of 1, and gives per-list cell
  counts. An incomplete Latin-square rotation (a single list, or lists or item sets
  not a multiple of the number of conditions) is reported in the run log and the
  datasheet and described as incomplete in the Methods text, and
  `counterbalance.incomplete: error`, in the design or the schema, refuses it. A
  factorial design asking for more lists than item sets is refused, because the
  surplus lists would be empty. Every committed datasheet and run log is
  regenerated, and no other stimulus moves. Two twin-edge cases pin the new
  behaviour in both engines, `latin_no_lists` and `events_priming_latin`.
- The `en_priming_jitter` example names its per-trial column `prime_ms`. It was
  called `soa_ms`, but a 33 ms mask follows the prime, so the stimulus-onset
  asynchrony is `prime_ms` plus 33 ms.
- Designs are checked before anything is selected or written, by the new
  `validate_design`, which `run_pipeline` calls right after reading the design and
  the schema. A key one edit from a known key of up to five characters, or two
  edits from a longer one, is refused as a probable typo and named with the key it
  was probably meant to be (`n_per_conditon` silently gave the default 20 items).
  Any other unknown key is reported in the run log and will be refused in a later
  release, so annotations belong in `description` or a key beginning `x_`. A
  missing or non-text `name` or `language`, an unsafe name or font, a bad trigger
  address or response key, a non-text or repeated condition name and a missing or
  empty `match_on` are refused with one message in both engines. They used to fail at
  export, after four files had been written, or at different points in each
  engine, and without `match_on` the R engine paired the alphabetically first
  words.
- A design whose name or language has non-ASCII characters writes its files under
  a stem with an eight-character checksum suffix, given by the new `design_stem`,
  so designs named 词频 and 笔画 no longer overwrite each other's files and an
  all-Chinese name no longer gives files whose names begin with a dot or
  underscore. `run_all` refuses two designs that would write the same files, such
  as `en-lexdec` and `en_lexdec`.
- The schema gains comments on the key check and on a `null` tolerance, so the 42
  committed datasheets, which record its SHA-256, and the run logs, which record
  the datasheets' MD5, are regenerated. No stimulus, report table or experiment
  changes.
- Both engines normalise text keys to Unicode NFC. Lexicon and pool words and
  norm-table and pair-member keys are normalised after the trimming and
  case-folding they already received. The item id, condition and presented fields
  of an item table, practice and filler tables included, and a `reference_words`
  list passed to `run_pipeline` are normalised as read. The two encodings of an
  accented letter, precomposed or with a combining accent, used to make two words
  of one. Both could then be selected, into opposite conditions of one matched set
  and with different lengths, and a norm or member join missed whichever spelling
  the lexicon did not use. De-duplication keeps the first row in file order. When
  normalisation rewrites or merges any form, the run log says how many, and the
  datasheet records the counts as `materials_source.input_normalisation`, a field
  of datasheet format 1.2. Every demonstration's output is unchanged, and the
  twin-edge case `nfd_pool` pins the new outcome.
- The realised-control report covers every dimension lexsync knows for the items,
  not only the standard four and `match_on`: syllables, bigram frequency, every
  joined norm column and every `define_by` dimension, each with a role
  (manipulated, controlled or uncontrolled), and it compares every pair of
  conditions, the anchor rows first. Uncontrolled differences used to go
  unreported while the Methods text called the control close: in `en_ndensity`
  the dense words had fewer estimated syllables than the sparse ones (d = -0.83),
  and a norm used to define the conditions did not appear in the report at all.
  Each comparison also gives the raw mean difference in the dimension's own unit
  (`mean_diff`). The comparisons gain rows, and two columns, `mean_diff` and
  `role`, after the existing ones. A dimension is manipulated in a pair whose
  `define_by` windows on it differ, so in `en_andrews_repro` frequency is
  uncontrolled between the two high-frequency cells. `match_report` takes the
  roles as `roles`, a function of the condition, reference and dimension that
  `run_pipeline` derives from the design, and leaves out a dimension with no
  numeric value, such as `n_syllables` for Chinese. Bigram frequency is computed
  for the report on a copy of the stimuli, so no stimuli file or selection
  changes. The datasheet's `realised_control` entries gain `condition`,
  `reference` and `mean_diff`, fields of datasheet format 1.2, and their roles
  replace 'manipulated/free', the label every unmatched dimension was given. Both
  apps show each row's role and raw difference and label each bar of the chart by
  dimension and pair. The comparisons, datasheets and run logs of the eleven
  demonstrations that match conditions change in both engines, and so do the
  descriptives of all of them but `en_richdim`, whose report had syllables and
  bigram frequency already. The twin-edge cases' pinned reports are regenerated,
  and the new case `four_conditions` pins the pairs and roles in both engines.
- A generated lexical-decision design reports bigram frequency, N and OLD20 for
  the words against the pseudowords, marked uncontrolled. Its stimuli give the
  base word of each pseudoword and the edit distance from it, as the `base` and
  `edit_distance` columns `build_lexdec_stimuli` now returns. Its pseudowords were
  more bigram-typical than their words (d about -1.5 in `en_lexdec`), which no
  report showed. The reports, datasheets and run logs of the three
  lexical-decision demonstrations change and their stimuli gain the two columns,
  while no pseudoword, trial order or experiment changes.
- A continuous design's report gives the predictor's SD against that of as many
  values spread evenly over its range, each control's SD against the pool's, and
  the control windows (`sd`, `sd_ratio`, `window_low` and `window_high`). An even
  spread has a predictor ratio of 1 whatever its size. In `en_freqcontinuous`, the
  frequency SD is 0.60 of that of an even spread. `select_continuous_stimuli`
  records the windows and the pool's SDs in `attrs["audit"]["control_windows"]`.
  `match_report_continuous` reads them there, or takes them as `audit`, and the
  datasheet's continuous entries gain the four fields, in datasheet format 1.2.
  The comparisons, datasheets and run logs of `en_freqcontinuous` and
  `en_priming_continuous` change.
- The Methods text reports the realised control descriptively: the largest
  difference on a matched dimension, in its own unit and with its pair, d and
  interval, and then the equivalence tests as a secondary check that says when the
  number of items is too small for them ever to pass (fewer than 23 per condition
  at the default bound). It called the control close, or not confirmed, on the
  tests alone. It names, largest first, up to five comparisons of an uncontrolled
  dimension that differ by more than the bound, and a generated lexical decision
  says how its words and pseudowords differ in bigram frequency, N and OLD20. It
  states the number of items each condition holds, with the request beside it when a
  `shortfall: allow` run fell short, where it stated the request. It
  labels the interval by the configured alpha, where it always said 90%, and for a
  continuous design it reports the realised spreads, the control windows and any
  widened window in place of 'near-constant'. The Markdown table of the realised
  control gains the pair and the raw difference of each row. The datasheet records
  the items each condition holds as `items.n_per_condition_realised`, a field of
  datasheet format 1.2, and `design.n_per_condition` gives the request the selector
  applied, its default when the design gives none, where it was null. The
  datasheets and run logs of every demonstration change, and no stimulus, report
  table or experiment does. The twin-edge case `shortfall_one` pins the new fields.
- The suggested model uses the stimuli's `condition` column, where a lexical
  decision named a `lexicality` column the stimuli do not have. It adds a matched
  design's matched dimensions as centred covariates on the stimuli file's own
  columns (Sassenhagen & Alday, 2016), leaving out one that does not vary among the
  items. It gives items a random slope for condition whenever the counterbalancing
  recipe rotates the conditions over the items by a Latin square (the
  categorisation design had none), crosses the condition with the predictor in a
  continuous pair design, with by-subject slopes for both and their interaction,
  and says how to recode a crossed design into its factors. Its note calls the
  random-effects structure maximal (Barr et al., 2013) only when it is, and
  describes the slopes of a design whose covariates or controls enter as fixed
  effects only.
- Exact ties between equally close candidates are broken by the keyed hash by
  default (`matching.tie_break: hash`), and `tie_break: bytes` reproduces the
  selections of lexsync 0.1. Every design whose matched dimensions tie selects
  different items, which the rule above counts as a breaking change, and a design
  or schema that names `bytes` selects what it did. The schema sets
  `tie_break: hash` in all three copies. Of the shipped designs, the Spanish and
  Chinese ones (`es_freqcontrast`, `es_ndensity`, `es_gender_repro` and
  `zh_freqcontrast`) change their stimuli, reports, experiments and datasheets for
  this reason alone, and the English ones for the change below as well. Four
  twin-edge cases whose picks ties decided are pinned anew (`four_conditions`,
  `joint_nan`, `nfd_pool` and `user_lexicon_provenance`), `baseline_small` pins
  the hash rule in its datasheet, and the new case `tie_bytes_small` holds both
  engines to the rule of lexsync 0.1.
- The English demonstrations select from the screened lexicon,
  `corpora/derived/en_v2.csv`, with `pool_filters: {nonstandard: [0, 0]}`, leave
  out the words of `config/exclude_en_demo.txt` through `exclude_words`, and check
  their generated pseudowords against wordfreq's fuller English list,
  `corpora/derived/en_known_forms.txt`. Every English demonstration that draws its
  items from a lexicon or a supplied pool selects different items, a breaking
  change. The selections no longer hold a form the screen marks. The
  `en_andrews_repro` low-frequency cells held 24 such forms among their 36 items
  (aclu, adhd, bbq and bmx among them), where its high-frequency cells held none.
  The screen lets through taboo words and some forms that are not standard English
  words, such as abbreviations that subtitles write in lower case (mph, msg, yrs),
  and the exclusion list leaves them out. Its 53 forms were found by reading the
  demonstrations' selections until a run selected none of them, and its header
  states the criteria. They include the
  taboo forms the 0.1 demonstrations selected: bitch and boobs in `en_ndensity`,
  fuck in `en_freqcontrast`, ass, damn and hell in `en_andrews_repro`, and asses
  and shit in `en_resample`. The maintainer signs off the list's content. No
  generated pseudoword is a known English word now. The check leaves the
  generators fewer candidates, so more pseudowords are ill-formed at an edge or
  lack a vowel, as fdes, gngs and ntena do. The matching guides count 13 of the
  140, against 5 when the same designs skip the check. `en_supplied_pool`
  and `en_priming_continuous` read their norms from `en_v2.csv`, whose N and OLD20
  count only the unmarked forms, so `en_supplied_pool` selects different words and
  `en_priming_continuous` keeps its pairs while its stimuli gain the members'
  screening columns. The documentation quotes the new figures. In `en_ndensity`, the
  dense words have fewer estimated syllables than the sparse ones by d = -0.53,
  where the unscreened selection gave -0.83, and in `en_lexdec` the pseudowords
  are more bigram-typical than their words by d = -0.97, where they were by -1.47.
- The English example lexicon bundled with both packages, `en_example.csv`, holds
  3,000 of the forms `en_v2.csv` keeps, with its frequencies, N and OLD20. It was a
  slice of `en.csv`, a quarter of it forms the screen marks, mostly names and
  acronyms. Examples and tests that use it give different numbers: in the quick
  start, frequency separates the conditions by d = 4.84, where it gave 5.92. The
  datasheet credits the slice as screened against SUBTLEX-US, and both
  `LICENSE.note` files and `LICENSE-DATA` credit SUBTLEX-US as a direct source of
  it. The repository's `corpora/fetch_corpora.py --slice-en` rebuilds it from the
  committed `en_v2.csv`, as `--screen-en` now does too. The script writes the
  slices with LF line ends on every platform, and rebuilding `en.csv` no longer
  overwrites the English slice.
- The generated PsychoPy experiment runs full screen (`presentation.fullscreen`,
  true by default), as PsychoPy advises for frame timing. It always ran in a
  1280 × 1024 window, which `fullscreen: false` keeps. Text is 48 pixels high in all
  three targets (`presentation.text_height_px`, a whole number from 8 to 400), where
  the OpenSesame experiment used 32. In OpenSesame, the setting is the experiment's
  `font_size`, so its instructions grow with it. OpenSesame takes full screen from
  the mode it is launched in, as the experiments guide now says. Every committed
  experiment changes, and so do the datasheets and run logs, which record the
  checksums of the experiments and the schema. No stimulus moves.

### Fixed

- The apps' download bundles reproduce their own record. The apps ran a temporary copy of
  the design with absolute paths and then bundled the displayed design, so the bundled
  datasheet's design checksum matched no file in the bundle, and the datasheet and run logs
  exposed the user's home and temporary directories. They now run the exported command in a
  folder laid out like the bundle, with the design under its exported name, the schema at
  `config/schema.yaml` and each input at the path the design names, and the Download tab
  archives that folder. The outputs therefore sit under `output/` in the archive, where
  they used to sit at its root, and rerunning the exported code in the unzipped folder
  rewrites them with the same bytes, run logs apart. The Streamlit app runs the command as
  a separate process, since the working directory belongs to every session, and the Shiny
  app moves it for the call alone. The PsychoPy and OpenSesame downloads are zip archives
  holding the tables those experiments load. Each app removes a run's folder once its
  results leave the screen, and refuses a design name or uploaded file name that would
  place a file outside the folder. The R engine's datasheet records the materials source,
  the stimuli file and every artefact with forward slashes, as the Python engine's does.
- The Shiny app's presets set the matched dimensions and the matching method, as the
  Streamlit app's presets do. Its neighbourhood preset matched on N, the dimension it
  manipulates, and on OLD20, a close correlate of N, and it left length unmatched. Both
  apps now warn when 'Match on' names a dimension whose windows differ between
  conditions, and neither runs a factorial design with nothing to match on. Their
  command lines quote the design file's name and run in `cmd.exe` and Windows PowerShell,
  and the Streamlit app's R line now passes the `outdir` that `run_pipeline()` requires.
  The interval column is labelled by the configured alpha, and the sentence under the
  exported code says that the engines agree byte for byte only when the run's datasheet
  says so. The Shiny method selector carries the Streamlit app's note on `mahalanobis`
  and `optimal`. Both apps open on `en_v2`, the English lexicon screened against
  SUBTLEX-US, and keep only its unmarked forms unless 'Screened forms only' is cleared,
  as the shipped English designs do. A session left at its defaults therefore selects
  different words from before. The Streamlit app no longer passes
  `use_container_width`, an argument Streamlit is removing, and needs Streamlit 1.49 or
  later, which the `dev` extra now requires.
- The documentation said that practice trials are shuffled so that participants meet them
  in different orders. Every participant given a list meets them in one fixed order, as
  the design intends, and the text now says so. The parity notes now say that the
  keyed-hash order shows no systematic position effects across seeds, since one seed gives
  each list one order.
- `load_lexicon` refuses Zipf values outside 0 to 9, which are frequencies per million in
  the wrong column. A log count such as SUBTLEX-US's `Lg10WF` lies inside that range and
  must still be converted.
- `fetch_corpus` refuses a corpus name containing a path before it reads the registry, so
  an edited registry cannot make it write outside the cache. Its refusals name the
  registry they read and say when an entry registers no download address, and R's
  `fetch_corpus()` explains that a wordfreq language is built by the Python package,
  where it said the language was not in the registry.
- The lexical-decision practice table no longer presents the English word 'plank' as a
  pseudoword. Its replacement, 'plang', came from the package's own generator and is not
  among wordfreq's English forms, and `design_en_lexdec_blocks.yaml` records the command.
  The categorisation example adds 16 non-member foils as fillers
  (`items/categorisation_foils_en.csv`), nouns that do not belong to the category they
  appear under, so pressing the 'yes' key on every trial no longer scores perfectly. Each
  list now holds 16 'yes' and 16 'no' trials. The foils are interleaved with the members,
  so the example's stimuli file gains a `block` column and its trials are renumbered,
  while the same items stay in the same lists and conditions.
- The PsychoPy and jsPsych experiments paused wherever the block changed. Fillers are
  interleaved with the main trials so that nothing sets them apart, yet a pause came
  before and after every filler, and each pause after one said that the practice had
  ended. Fillers now run with the main trials, and the one pause comes where the
  practice trials end, in `design_en_lexdec_blocks.yaml` and in the categorisation
  example, whose foils are fillers.
- Under pandas 3 with pyarrow installed, the Python engine lower-cased the words
  of a lexicon or a supplied pool by Unicode's simple case mapping, because pandas
  then hands `.str.lower()` to Arrow. A final capital sigma became σ where
  Python's `str.lower()` and the R engine give ς, and İ became a bare i where they
  give i followed by U+0307, so the two engines keyed, sorted and measured such
  words differently. The words are now folded by `str.strip()` and `str.lower()`
  themselves. pandas 2, and pandas 3 without pyarrow, folded them correctly
  already, and no shipped design holds such a word. The twin-edge case
  `casefold_pool` pins both engines to one outcome. The suite also passes under
  pandas 3, which pip installs on Python 3.11 and later: one test compared a
  frame read from CSV, whose text columns are object, with one that pandas 3
  built with its `str` dtype.
- 28 of the committed datasheets recorded the SHA-256 of a copy of
  `corpora/derived/en.csv` or `es.csv` whose line endings one machine had
  converted to CRLF, so the digest could not be reproduced from a checkout and
  read as altered materials. Two of them also recorded such a copy of
  `config/design_en_priming_continuous.yaml`. The datasheets are regenerated from
  the committed bytes, and a test in both engines recomputes every recorded
  digest, the design and schema digests included. No stimulus, report table or
  experiment changes. The run logs of the 14 designs concerned change with their
  datasheets, whose MD5 they record.
- The Shiny app writes an edit to the conditions table into the cell that was
  edited. Every edit landed one column to the left, because `DT::editData()` was
  called without `rownames = FALSE`, so a custom condition could not be entered.
  The bounds of the second factor, which the one-factor presets leave empty, are
  now numeric columns, so a bound typed there is kept as a number. They were
  logical columns, on which DT warned and stored the typed text.
- The R engine no longer reads a design key by partial matching. R's `$`
  accepts the start of a name when no name matches in full, so a key that began
  another key's name stood in for that key when it was absent. `font_size: 40`
  set the font of all three generated experiments to '40', `language_tag` served
  as `language`, and an annotation named `continuous_notes` made a factorial
  design fail. Design, schema and corpus-registry entries are now read by exact
  name, so a design carrying `font_size` or `continuous_notes` runs as it does in
  Python, and one that gives `language_tag` without `language` stops, as it does
  in Python. The Python engine was never affected.
- The R engine reads an unquoted `y` or `n` in a design as text, as the Python
  engine does. It read them as TRUE and FALSE, so `keys: [y, n]` generated
  experiments that waited for keys named TRUE and FALSE, which no participant can
  press. A YAML boolean given as a response key (an unquoted `yes`, `no`, `on` or
  `off`) is refused with a hint to quote it, and `validate_design` refuses a
  `counterbalance.optimise` that is not `true` or `false`, since `optimise: n` or
  `1` balanced the lists in the Python engine only. The twin-edge cases `yn_keys`,
  `yes_no_keys`, `optimise_n` and `language_no` pin both engines to these
  outcomes.
- A norms entry's join key is written `join_on:`. Both engines' YAML readers took
  the documented `on:` for the boolean true, so every join silently used `word`. A
  bare `on:` is now read as the join key, with a note in the run log, and any other
  key in a norms entry is refused, so a misspelt `join_on` no longer falls back to
  `word`. An entry that is not a mapping, such as a bare file name, is refused as
  needing a `path`, where it used to stop the run with each language's own error.
  The R engine also joined each entry of a `norms:` block written as a mapping of
  named entries, such as `conc: {path: norms.csv}`, which the Python engine
  refused. Both engines now refuse it and name `conc` as an unknown key. The
  datasheet still records the key as `on`. The schema's comment now shows
  `join_on:`. The 42 committed datasheets record the schema's SHA-256 and the run
  logs record each datasheet's MD5, so both are regenerated. No stimulus, report
  table or experiment changes. The twin-edge case `norms_on_bare` pins the join on
  `lemma`.
- Numbers in the Markdown datasheet and the Methods paragraph are formatted by
  lexsync itself, not by each language's printf, which rounds decimal ties
  differently: R on Windows printed 0.0825 as 0.082 where Python printed 0.083.
  A displayed value is rounded half away from zero from the value the JSON record
  stores, so a statistic stored as 0.745 now shows as 0.75 in both engines, where
  both printed 0.74. Some two-place cells in the committed datasheets of 10 designs
  change for this reason, and the Methods paragraph of `es_freqcontrast` now gives
  the interval as [-0.19, 0.34]. A cell in which the R datasheet of
  `en_andrews_repro` disagreed with Python's (-0.46 against -0.47) now agrees. The
  TOST p column is printed to four places in both engines, and a p that rounds to
  zero is shown as < 0.0001. R wrote such a column as 9e-04 and 1, Python as
  0.0009 and 1.0. No JSON record, stimulus, report table or experiment changes.
  The run logs of the 10 designs change with their datasheets, whose MD5 they
  record.
- `n_per_condition` is resolved by one rule everywhere. A whole number written as
  `4.0` is accepted, and 0 is refused by `match_stimuli` and
  `select_continuous_stimuli`, which returned their default size in Python. A
  `null` tolerance is read as R's `modifyList()` reads it, and a schema without a
  `matching:` block works in Python.
- Matching excludes candidates that lack a matched dimension, in every method and
  before anything is selected, and the run log and the datasheet record how many
  each condition lost (`selection.incomplete_dropped`, a 1.2 field present only
  when a condition lost any). An anchor item missing a matched value used to be
  paired with the alphabetically first candidate in its window, or to re-pick a
  used candidate and stop the run with a false 'overlapping conditions' error.
  `joint` filled a shortfall with incomplete pairs, `optimal` failed with a solver
  error that differed between the engines, and `select_continuous_stimuli`
  selected items without the predictor (4 of 10 when 40% of the pool lacked it).
  The documentation already promised the exclusion. The shortfall policy applies
  to what remains, a condition left without a complete candidate is refused by
  name, and a word repeated within one condition, which used to be reported as
  overlapping conditions, is reported as an internal error. The datasheet's
  verdict on whether the pairwise cap fired, and the Methods text's count of
  eligible candidates, leave the excluded candidates out. For a design whose pool
  has such candidates the selection changes, which the rule above counts as a
  breaking change. No shipped design has one, so no stimulus, report table or
  experiment moves. The schema's note on norm coverage, corrected in all three
  copies, changes `config/schema.yaml`, so every committed datasheet records a new
  schema digest and every run log a new datasheet checksum. Three twin-edge cases
  pin the outcome: `anchor_nan`, `joint_nan` and `cont_nan_predictor`.
- `resample_stimuli` records the candidates its first replicate excluded for a
  missing matched value, those of the whole pool, so the run log and the
  datasheet of a resampled design report them as well. Its `attrs["audit"]` had
  been present only when all the replicates held the same one, and in the R
  engine it was that of the first replicate. A selection no longer passes on an
  audit its pool already carried. This engine did so whatever the method, and the
  R engine in `select_continuous_stimuli`.
- `mahalanobis` matching estimates the correlations from the rows complete on the
  matched dimensions, and refuses a pool with fewer than k + 2 of them for k
  dimensions. A dimension with any missing value used to lose all its
  correlations and enter the distance as an independent term.
- In the R engine, joint matching on a dimension with missing values over more
  than 1,200 candidates failed ('missing value where TRUE/FALSE needed') where
  Python ran. The R engine's compensated sum now returns NA for such input, as the
  Python engine's returns NaN. It also returns NaN where opposite infinities make
  the running sum NaN, a case in which it stopped in the same way.
- Generated experiments present one counterbalancing version to each participant.
  The PsychoPy, OpenSesame and jsPsych experiments used to present every list in one
  session, interleaved, so in a Latin-square design each target appeared in both
  conditions (in `en_priming`, all 12 targets twice, three of them on consecutive
  trials), and in a resampled design every participant saw all the replicates. The
  0.1.0 notes said that a categorisation participant never sees the same target
  twice. That held within a list only. A version is one (replicate, list) pair of
  the presented trials, numbered from 1 in that order, and participant *p* runs
  version ((*p* - 1) mod *V*) + 1 of *V*, the rule `participant_table` uses. The
  PsychoPy script reads `--participant` and `--version`, or `--list` without
  replicates, from its command line. Launched with neither, it asks for them in a
  dialogue, which a design with one version also shows and runs on blank answers. It
  stops on a version it does not have. The jsPsych page reads
  `?participant=`, `?version=` or `?list=` from its address, and a page with several
  versions opened without one says how to open it and runs nothing. Every page names
  its data file after the participant and the version, so a page with one version
  saves `<title>_v1.csv`. The OpenSesame target writes one experiment per version
  (`<base>_list<k>.osexp`, or `<base>_rep<r>_list<k>.osexp` with replicates), each
  with its own tables, and each warns when the subject number belongs to another
  version. A design with one list and no replicates keeps its file names.
  `lexsync.scripting.presentation_versions` lists the versions of a set of trials,
  and `export_experiments` lists every file it wrote under `files`, so code that
  iterates over the result's values must now skip that list. The exporters refuse a
  `list` or `replicate` value that is not a whole number, read by one rule in both
  engines, since the versions are numbered by those values. In a resampled design
  with practice or filler trials, each version has its own copy of them, and fillers
  no longer stop such a design with an error about a missing hash-key component.
  The loop tables carry `replicate` and keep each version's trials together. The
  datasheet records `counterbalancing.versions` and `counterbalancing.assignment`,
  and its Methods text says that each participant was presented one version. Its
  artefact list and the run log include the loop and text tables, which hold the
  trial order and the trigger codes. Every demonstration's experiments, datasheets
  and run logs change, and the seven multi-list designs and `en_resample` have one
  OpenSesame experiment per version in place of `<base>.osexp`. The demos index
  links each version of a page, and the landing page links version 1 of the
  self-paced reading demonstration. One twin-edge case, `resample_two_lists`, pins
  the four versions of a resampled two-list design in both engines. No stimulus
  changes.
- A design can refer to a derived dimension (`n_density`, `old20`, `bigram_freq`)
  in a condition's `define_by`, in `pool_filters`, as a continuous predictor or
  control, or in `counterbalance.balance_on`, as well as in `match_on`. When the
  lexicon lacks the dimension, `run_pipeline` computes it against the lexicon,
  after the filters the lexicon can answer and before those on the derived
  dimension. A high- against low-bigram contrast, a continuous design with
  `bigram_freq` as its predictor, or an N design on a lexicon built by
  `lexsync fetch` used to fail with 'absent from the pool'. Two twin-edge cases,
  `bigram_contrast` and `fetched_es_ndensity`, pin the result in both engines.
- The `reference_words` argument of `run_pipeline` takes effect. For a corpus or
  pool design, the pipeline recomputes N and OLD20, and bigram frequency where the
  lexicon carries it or the design uses it, against the supplied list, overriding
  the lexicon's columns, and logs the step. The datasheet's
  `selection.neighbourhood_reference` gains `applied_to`, the columns recomputed,
  and is written only when the list was applied. Every bundled lexicon carries N
  and OLD20, so the argument was ignored while the datasheet recorded it as
  applied. A generate or table design does not use the argument, and its run log
  now says that it was ignored. The 0.1.0 notes said the override changes the
  neighbourhood dimensions, which held only for a lexicon without them. A list
  that is empty or holds a missing value is refused, since it would set every N
  to 0 and every OLD20 to missing, and a lone string is read as one word, as R
  reads it, not as a list of letters. A lexicon may mark the forms that make up
  the neighbourhood reference with a `reference_member` column of 0 and 1, which
  `load_pool` honours too.
- (Python) `add_neighbourhood` computes N and OLD20 from a rapidfuzz distance
  matrix, block by block, about 20 times faster than the word-by-word loop (0.9 s
  against 19 s for 500 words against the 30,000-word English lexicon), with
  identical values.
- The schema documents `reference_member` and when the derived dimensions are
  computed, so the committed datasheets, which record its SHA-256, and the run
  logs, which record the datasheets' MD5, are regenerated. No stimulus, report
  table or experiment changes.
- A generated lexical-decision design reports the number of words the generator
  could use. It reported the band before the a-z filter, 8,305 words where 6,937
  were eligible in a Spanish band of length 4-7 and Zipf 3.5-6. The English
  demonstrations' counts do not change, since their bands hold only a-z words.
- `count_syllables` counts the vowels of Polish, Czech, Hungarian, Romanian,
  Turkish, Danish, Norwegian and Vietnamese (æ, œ and Latin Extended vowels such
  as ą, ě, ő, ă and ı), and returns a missing value for a word in another script
  (`None` from `count_syllables`, NaN in the `n_syllables` column), where it
  returned 0. It now decomposes a word and sets its diacritics aside, so a vowel
  counts whatever its accent. Every Chinese, Russian or Greek word counted 0
  syllables, so a design could match on `n_syllables` and report perfect balance.
  `run_pipeline` refuses a design that refers to `n_syllables` when a word
  without it passes the other filters the lexicon can answer. The documentation
  said the vowel class covered the Latin-1 vowels, but it lacked æ. The
  `n_syllables` column of `zh_freqcontrast`'s stimuli is now empty, and its
  datasheets and run logs change with it. No selection changes.
- Responses are collected from the onset of the stimulus they answer, and every
  target records them. The response window used to open only when the target had
  gone, 800 ms after its onset in lexical decision, and each target discarded a key
  pressed while the target was on screen: jsPsych showed the target with no keys
  allowed, PsychoPy's `waitKeys()` cleared earlier presses and OpenSesame's keyboard
  item flushed them. jsPsych timed the reaction from the blank response screen, and
  the PsychoPy and OpenSesame targets recorded no response at all, so no accuracy,
  reaction time or reading time reached a data file. The 0.1.0 notes said that a
  categorisation design's data were scoreable. That held for jsPsych only. A
  response event after a text event now opens its window at that stimulus's onset,
  for the same total window, and a response ends the trial. `from: offset` on a
  response event keeps the delayed window, which is also the default after any other
  event, and `from: onset` after such an event is refused. A response collected from
  the onset runs where its stimulus runs, so a design that gives the two different
  `blocks` is refused. The PsychoPy script writes
  `data/<base>_p<participant>_v<version>_<date>-<time>.csv`, one row per trial,
  written as it goes, with the response, its reaction time from the stimulus's onset,
  timeouts, accuracy when the item names its answer, self-paced reading times, the
  question's response, and each event's realised flips and onset. The OpenSesame
  experiment collects the response in the stimulus's own script, clears the response
  variables as each trial starts and logs every trial with a logger item. The jsPsych
  page saves its CSV as before, and its target is now one trial whose `rt` runs from
  the onset. The datasheet records each response window as
  `presentation.response_windows`, says in `analysis.response` where a reaction time
  starts, and its Methods text says when responses were collected. Every
  demonstration's experiments, datasheets and run logs change. The twin-edge case
  `os_hostile_text` gains a response that keeps the delayed window. No stimulus
  moves.
- OpenSesame response and question timeouts are written in whole milliseconds as
  declared. A timeout of 1,001 ms was written as 1,000, because the value went
  through seconds and back, and 95 of the whole-millisecond values from 1 to 10,000
  came out a millisecond short. The demonstrations' timeouts were not affected.
- The datasheet and the Methods text credit wordfreq only for the lexica lexsync
  ships. A user's own lexicon was described as wordfreq data, so a study selecting
  from SUBTLEX would have cited the wrong corpus. It is now named by its file name
  and checksum, and a corpus fetched into the cache by the registry's citation. A
  shipped lexicon is recognised by its checksum with CRLF line endings read as
  LF, and the credit for `en_v2.csv` states its screening rule. The shipped
  designs' credits do not change, and the twin-edge case
  `user_lexicon_provenance` pins both engines. The schema's comments describe the
  new key and columns, so the 42 committed datasheets, which record the schema's
  SHA-256, and their run logs are regenerated. No stimulus, report table or
  experiment changes.
- The documentation now states what the lexica derived from wordfreq contain:
  proper names, acronyms and other non-standard forms among the most frequent
  forms, spread unevenly over frequency bands, with N and OLD20 computed over
  them. It says that a continuous design spreads items over the predictor's
  ranks and not over its range, so the selection follows the pool's
  distribution and the tolerance windows trim the controls' tails without
  holding them constant, which the 0.1.0 entry for continuous designs misstated.
  It also says that generated pseudowords are more bigram-typical than their
  base words, that the `priming` paradigm is backward-masked, that
  `en_rastle_repro` and `en_andrews_repro` reproduce item selection and not a
  lexical-decision task, and how each presentation target times its events.
- The corpus registry no longer maps `freq_zipf` to the SUBTLEX-US and
  SUBTLEX-DE log-count columns or to a SUBTLEX-CH column that does not exist. It
  says that its column maps are not yet applied and that no entry can yet be
  downloaded by `fetch_corpus`. The wordfreq connector's reach is given as the
  thirty registered languages (wordfreq covers 42) in place of roughly forty, the
  README says the Python package is on PyPI, and the claims of byte-identical
  output name the deterministic matching methods, which include the default.
- The documentation of `cohens_d_ci` and of the equivalence test cites
  Sassenhagen and Alday (2016) and Lakens (2017) for what they argue, and calls
  the 0.5 bound a convention. The R quick start uses 60 items per condition, as
  the Python one does, in place of 15: at the default bound and alpha, no
  dimension that varies can pass the equivalence test with fewer than 23 items
  per condition. No stimulus, report table or experiment changes. Every JSON
  datasheet records the new schema digest, the five demonstrations whose design
  files were corrected record new design digests, and the Markdown datasheets of
  the four whose descriptions changed (`en_andrews_repro`, `en_freqcontinuous`,
  `en_priming_continuous` and `en_rastle_repro`) change with them, as do the run
  logs.
- `optimal` matching minimises the summed distance of the n pairs it selects. It
  solved a complete assignment over both candidate pools and kept the n cheapest
  assigned pairs, which is not the optimum and was consistently worse than greedy
  `joint`: 1.15 to 2.5 times the optimal summed distance in tests where `joint`
  came within 3.4%. It now solves the cardinality-constrained problem exactly with
  a padded assignment (Volgenant, 2004). In R a problem at the 1,200-candidate cap
  takes about 4 s, where the complete assignment took 34 s on the same machine,
  and in Python about 1 s. Both capped pools are put in tie-break order before
  the solve, by spelling under `bytes` as well as by key under `hash`, so the
  solver's choice among equally cheap pairs no longer depends on the order in
  which the rows arrive. When the conditions overlap, a word cannot be paired
  with itself or used twice. A pair the solve loses that way is replaced by
  solving again over the unused words, and the selection is then no longer
  guaranteed to have the least summed distance. Designs using `optimal` select
  different items, which
  the rule above counts as a breaking change. No shipped design uses it, so no
  stimulus moves. The schema's description of the method, corrected in all three
  copies, changes `config/schema.yaml`, so every committed datasheet records a new
  schema digest and every run log a new datasheet checksum.
- `lexsync run --config-dir DIR` reads `DIR/schema.yaml`, as `run_all()` does in
  both engines. It silently ran the bundled schema whenever the working directory
  had no `config/schema.yaml`, so a study's own seed and tolerances were ignored.
  The command line, `run_pipeline()` and `run_all()` share one resolver,
  `lexsync.paths.resolve_schema`, say which schema they use when none was named
  and record its path in the run log (`schema_path`) and the datasheet
  (`reproducibility.schema_path`). Every committed datasheet and run log gains
  that field. No stimulus, report table or experiment changes.
- `run_pipeline()` and `run_all()` fall back to the schema bundled with the
  package when none is named and none is found beside the designs, as the command
  line already did, so the one-call pipeline works outside a clone. Before the
  bundled copy, `run_pipeline()` looks for `config/schema.yaml` and then for
  `schema.yaml` beside the design, and `run_all()` looks in `config_dir` and then
  in `config/`. The first place each function looks is its old default, so a call
  that worked before reads the same file. A named schema that does not exist is
  still an error, and the message gives the bundled copy's location.
- The command line prints lexsync's own error messages without a Python traceback
  and exits with status 1. `lexsync --traceback` shows the traceback, and a usage
  error keeps argparse's status 2.
- `cohens_d` and `cohens_d_ci` return None when a condition has fewer than two
  items, where they returned 0, a perfect balance. The pipeline no longer fails
  while formatting the missing interval: it raised a TypeError writing the run log,
  which now prints NA, as the R engine's does. The twin-edge case `shortfall_one`
  pins the result in both engines.
- The Python engine's `build_pool` compares a categorical filter as the R engine
  does. A 0/1 column with a missing value is held as floats, and the filter
  compared '1.0' with '1'. A condition defined on a norm that leaves some words
  uncovered therefore selected nothing in Python, while the R engine selected. A
  YAML boolean filter such as `[true, false]` was taken for a numeric range and
  refused as reversed. A list of numbers is now compared with a numeric column as
  numbers, and any other value is compared as text, written as the R engine
  writes it, a boolean as TRUE or FALSE. A boolean filter on a 0/1 column thus
  selects nothing in either engine. The only categorical filter in a shipped
  design, `gender` in `es_gender_repro`, compares text, so no stimulus moves. The
  twin-edge cases `animacy_norm`, `float_categorical` and `bool_filter` pin both
  engines to one outcome, and the R engine is unchanged.
- (Python) The wordfreq connector keeps the words a language spells with
  combining vowel signs and viramas, a zero-width non-joiner or joiner, or an
  apostrophe or middle dot inside the word. Its filter admitted only Python's
  word characters, a class without combining marks or the zero-width characters.
  Asked for 10,000 forms, `lexsync fetch hi` therefore returned 3,207, of which
  2,287 held Latin letters ('and', 'bjp') and none was है or में, and the
  Bengali lexicon held 1,591 forms, 871 of them Latin. Persian lexica held no
  form spelt with a zero-width non-joiner, Ukrainian ones no form with an
  apostrophe, such as п'ять, and Catalan ones none with l·l, such as
  pel·lícula. The Hindi and Bengali lexica now reach 10,000 forms, 525 and 137
  of them with Latin letters, and the Persian, Ukrainian and Catalan ones hold
  340, 103 and 61 such forms among their 10,000. Every form is put in NFC, so
  six Greek forms that wordfreq gives decomposed, such as μαΐου, are kept as
  well. An apostrophe passes only between two letters of a Ukrainian or
  Belarusian word, and a middle dot only between two l's of a Catalan one, so
  English contractions and French elisions stay out, as do digits and every
  other punctuation mark. A 10,000-form lexicon for any of the other 24
  registered languages is unchanged byte for byte, while one fetched earlier for
  the six languages above differs from one fetched now. A build left with fewer
  forms than requested says so on standard output. `fetch_corpus` and
  `lexsync.corpora.build_wordfreq_lexicon` gain `strict`, to make such a
  shortfall an error, and `exclude_latin`, to drop every form holding a Latin
  letter. The guide's fetch section says that length, N and OLD20 count code
  points in both packages, so a vowel sign, a virama or a zero-width non-joiner
  is a character of its own.
- Durations that `resolve_trial_timing` reads from an item column must be present,
  finite and not negative. Fractional milliseconds are rounded once and recorded.
  A blank or negative value used to produce experiments that stopped at
  the blank in OpenSesame and PsychoPy or showed the stimulus for no time in
  jsPsych. A fractional one made the R and Python jsPsych pages differ, because the
  R engine's jsonlite kept four decimal places of it. A blank, negative or
  non-numeric value is now refused, naming the column and the trial's set and
  condition. A column of fractional milliseconds is rounded with the rounder both
  engines share and written back to the stimuli and the loop tables, so 82.5 ms is
  presented as 83 in every target. The returned frame records how many values
  were rounded in `attrs["duration_rounding"]`, and `run_pipeline` writes the
  count into the run log. Fixed durations are checked the same way. A
  negative `duration_ms`, `duration_frames` or `timing` value reached OpenSesame as
  `clock.sleep(-50)`, and a NaN as `clock.sleep(NA)` from the R engine, and both
  are now refused, naming the event or the key. A fractional `duration_ms` is
  rounded where it was truncated, so 33.7 ms is presented as 34, and the lower
  bound of a jitter must not be negative. Both engines write each trial's numbers on the
  jsPsych page to 15 significant digits. No shipped design reads a fractional or
  blank duration, so no stimulus or experiment changes. The twin-edge case
  `fractional_soa` pins both engines to one outcome.
- Trigger codes are checked when the experiment is generated. A literal must be a
  whole number from 1 to 255, written as a number or as a string of digits, and
  anything else is refused with a message naming the event. A misspelt token such
  as `conditon` stopped this engine with `int()`'s own error, while the R engine
  wrote `send_trigger(NA)` into the OpenSesame experiment. Codes such as 300, 0 and
  -5 reached the parallel port, which keeps only the low byte, and 20.5 was taken
  as 20. A literal of 254 or 255, which the PsychoPy experiment sends when the
  session starts and ends, is reported on standard output, and so is one equal to a
  condition code the design sends or one within the range of the item codes it
  sends. A design that sends item codes together with condition codes, or with a
  code of its own from 40 to 239, gets item codes that never coincide with those
  codes. Sets 65 and 66 of a 70-set design took 101 and 102, the condition codes.
  Such a design is refused before any file is written when it has more item sets
  than free codes, unless the schema sets the new
  `triggers.allow_code_overlap: true`, which lets the item codes wrap and repeat
  within the free codes. `assign_triggers` gains `events` and `schema` for this,
  and `export_experiments` passes them. Any other design keeps its item codes, so
  no shipped loop table changes. The guide now says that item codes follow the
  code-point order of the set labels, so that with sets 1 to 20 set 10 is 41 and
  set 2 is 51, and that they are decoded through the loop table. The R vignette
  said that condition codes stay unique regardless. The codes did, but the marker
  stream did not once both kinds were sent. The OpenSesame snippet
  `templates/opensesame/inline_send_triggers.py` sends only the condition code at
  the word's onset. It sent the item code first, whose 10 ms pulse delayed the
  condition code. The schema's comments describe the new key, so the 42 committed
  datasheets, which record the schema's SHA-256, and their run logs are
  regenerated. No stimulus, report table or experiment changes. The twin-edge case
  `trigger_typo` pins the refusal in both engines.
- Generated OpenSesame experiments build every stimulus before the trial runs and
  time each event from its onset. Each inline script built its canvas while the
  trial ran and slept the event's full duration after a trigger pulse that blocked
  for 10 ms, the pattern OpenSesame's timing manual shows as the way not to time a
  display, so every event overran: at 60 Hz the 50 ms prime was predicted to last
  about 67 ms and the 83 ms stimulus-onset asynchrony from prime to target about
  117 ms. Each event now ends half a frame before its duration is up, so that the
  next display lands on the refresh that ends it. On a simulated display at 60, 120
  and 144 Hz, the prime and the mask then last the flips the PsychoPy script gives
  them, and the asynchrony stays 83.3 ms. These figures are predictions, and both
  experiments guides now give a photodiode checklist for measuring them. The
  experiment measures the display's frame period at start-up and logs it as
  `lexsync_frame_ms`. It holds each trigger code for `trigger_hold_ms`, which it
  ignored, without delaying any display. A response kept after the stimulus with
  `from: offset` opens its window once a code still held has been reset, since
  OpenSesame's `keyboard_response` runs none of lexsync's code. The experiment also
  sends the 254 and 255 session markers, as the PsychoPy script does. The 32
  committed `.osexp` files change, and so do the datasheets and run logs that
  record their checksums. No stimulus moves.
- Trigger codes in the PsychoPy script last the hold, and never less than 10 ms.
  The 254 and 255 session markers were cleared by the statement after their flip,
  and a code on an event shorter than the hold was cleared as soon as the event's
  last flip returned, so the markers and a one-flip prime's code lasted no time at
  all. A hold set to 10 ms was rounded to 6.9 ms at 144 Hz and 8.3 ms at 240 Hz.
  The default 50 ms hold was not affected. Every code is now counted down flip by
  flip and reset on the flip that ends its hold, in a later event when its own is
  shorter. Only the next onset's code ends it sooner, and a key that ends a
  stimulus early no longer cuts its code short. The self-paced reading
  critical-region code is held the same way. It was held for `inter_trigger_ms`,
  10 ms, which is accepted and no longer used: `validate_design` returns a note for
  the run log when a schema sets it, and the shipped schema no longer does. A
  literal code of 254 or 255 is reported as a code both laboratory targets send.
  The 21 committed PsychoPy scripts change, and the datasheets and run logs are
  regenerated. No stimulus moves.

### Security

- Generated OpenSesame experiments no longer pass stimulus text through
  OpenSesame's variable store, which evaluates it. In OpenSesame 4.x, a loop cell
  containing `{` runs as a Python f-string, and in 3.3 a leading `=` or `[=...]`
  runs Python, so an item table shared with a laboratory could execute code on
  the machine that presents it. Ordinary words in the English lexicon, such as
  'infinity' and 'nan', could stop an OpenSesame 4.x session, though no
  demonstration design selected one. The loop table now holds only numbers:
  `lexsync_row`, the trial's position in loop order, with
  `lexsync_trial`, `lexsync_list`, `lexsync_set`, the trigger codes,
  `critical_region` and any per-trial duration. The prefix stops the columns from
  shadowing Python's built-in `list` and `set` in OpenSesame 4's inline scripts.
  The inline scripts read the presented text, `condition`, `block` and `answer`
  from a companion file, `<base>_opensesame_text.csv`, to be copied with the
  experiment. `export_opensesame` refuses a value in one of the numeric columns
  that is not a plain number, naming the column. A practice timeout is reported
  as 'Too slow'. Both versions scored it as a wrong key, because the response
  came back as the string 'None'. The 0.1.0 notes said stimulus text was always
  safe. That held for PsychoPy and jsPsych but not for OpenSesame. Every
  demonstration's `.osexp` and OpenSesame loop table change, and each
  demonstration gains a text table. The datasheets and run logs change with them,
  since they record the experiment's checksum. No stimulus moves.
- The jsPsych page loads jsPsych, its keyboard plugin and its stylesheet from unpkg
  with Subresource Integrity, each file's SHA-384 and `crossorigin="anonymous"`, so
  a browser refuses a modified copy. The page loaded them with no integrity check,
  and the first two from bare package addresses that the CDN answers with a
  redirect. The page's comment says how to run it offline, since a page opened from
  a `file://` address cannot check the hash of a local copy.

### Planned

The state-of-the-art roadmap from the initial competitor and literature review is
now delivered (covariance-aware and optimal matching, a distributional balance
diagnostic, continuous designs and Wuggy-style pseudowords). Further norm
dimensions (concreteness, age of acquisition, English Lexicon Project behavioural
measures) are supported today through the `merge_norms` connector, which joins any
word-keyed norm table so the matcher can equate on it. Future directions include
more bundled languages and, should a determinism-safe implementation be found,
promoting a covariance-aware distance to the default.

## [0.1.1] - 2026-09-25

lexsync 0.1.1 fixes the test failure CRAN reported for 0.1.0 on its Linux check
hosts, together with the condition-code order and the interval on Cohen's d.
The corpus cache is now created only when a download needs it, and both engines
gain a function that clears it. No stimulus moves. The generated experiments of
12 of the 21 demonstration designs change their EEG condition codes, as
described under Changed. CRAN published the R package on 2026-09-25, and this is
the first version of the Python package on PyPI.

### Added

- Both engines can empty the corpus cache. R's `lexsync_cache_clear(name = NULL)`
  and Python's `lexsync.corpora.cache_clear(name=None)` remove one corpus, with
  any partial download of it, or the whole cache, and return the paths removed.
  The Python function also removes the `<name>_wordfreq.csv` lexicon that its
  wordfreq connector builds.

### Changed

- The corpus cache is created only when a fetch needs it, and kept free of
  partial downloads. `lexsync_cache_dir` (R) and `cache_dir` (Python) created the
  directory each time they were called, so asking where the cache was left an
  empty directory in the user's home filespace. Both now only report the path.
  `fetch_corpus` creates the directory once the registry entry and its URL have
  been accepted, or the wordfreq lexicon has been built, so a refused call writes
  nothing. Each fetch into the cache begins by deleting any `.part` sidecar there
  that has gone a day without a write. An interrupt or a process that died
  mid-transfer leaves one behind, and neither engine's handlers remove it. A
  younger sidecar may belong to a download still running in another process, so
  it is left alone. R's `fetch_corpus` sweeps nothing when given a `dest`.
- The EEG condition codes follow the design, not the trial order.
  `assign_triggers` numbered the conditions from 101 in the order they first
  appeared in the table it received, which after `counterbalance` is the shuffled
  trial order, so a different seed could swap two conditions' codes. Both engines'
  `assign_triggers` gain an optional `conditions` argument that fixes the order,
  and `export_experiments` gains one that defaults to the order of the design's
  `conditions`. The pipeline passes the design's order, followed by any other
  condition in the order the item source lists it (the words before the
  pseudowords of a generated lexical decision). A condition missing from the
  order takes the next free code, in code-point order of its label. The generated
  experiments of 12 of the 21 demonstration designs change their condition codes;
  `en_freqcontrast`, for instance, now gives `high_frequency`, the condition its
  design lists first, 101 in place of 102. Calling `assign_triggers` without
  `conditions` behaves as before. No stimulus moves.

### Fixed

- The confidence interval on Cohen's d was far too narrow for a large effect.
  `cohens_d_ci` computed the margin as `t * sqrt(1/nx + 1/ny)`, which treats the
  pooled standard deviation as known. Both engines now use the large-sample
  standard error of d, `sqrt(1/nx + 1/ny + d^2 / (2 * (nx + ny)))` (Hedges &
  Olkin, 1985; Borenstein et al., 2009), with the same t quantile. In the English
  frequency contrast the manipulated dimension, d = 5.27, had the interval
  [5.01, 5.53] and now has [4.72, 5.83]. A matched control, whose d is near zero,
  moves by at most 0.002 across the demonstration designs, and no d, TOST p-value
  or equivalence verdict changes. The interval is now fractionally wider than the
  one the TOST decision implies, which the documentation states. The comparisons
  files stay byte-identical across the engines.
- `match_report` did not say which way its signed statistics run. Both engines now
  document that `cohens_d` and its interval are the reference (first) condition's
  mean minus the other condition's, and that `var_ratio` is the other condition's
  variance over the reference's.
- The Python install instructions gave `pip install lexsync` before the package
  was on PyPI, where 0.1.0 was never uploaded, so the command failed. From 0.1.1
  the package is on PyPI and the command works. The development version still
  installs from the repository's `python_workflow` subdirectory. The wordfreq
  error message now names the package to install instead of the extra.
- The R `CITATION` entry names CRAN as its publisher, and its text version is the
  APA reference for software, with the version, "[Computer software]", CRAN and
  the DOI.
- The tests of both engines could take an unrelated directory for the lexsync
  repository. The R tests failed on CRAN's r-devel and r-patched Debian hosts and
  on r-devel Fedora clang. The test holding the R package's bundled templates to
  the repository's `templates/` looked three directories up from its own, and on
  those hosts that directory holds the unpacked sources of other CRAN packages, so
  it compared the templates with the unrelated 'templates' package. Nothing the R
  check runs writes outside the session's temporary directory. The Python tests
  walked up the same way, and the sdist ships `tests/`, so a build from it could
  have met the same fate wherever it was unpacked. In both engines a test that
  reads repository files now accepts a root only if it holds lexsync's own
  `DESCRIPTION` under `R_workflow/` and `python_workflow/` beside it, and skips
  elsewhere. The R tests also skip on CRAN, and the R check in CI runs beside
  stand-in neighbours of the same names. Several Python tests had no guard at all
  and failed outside a checkout, and those that needed only the schema now read
  the bundled copy and run anywhere.
- The R package suggests testthat 3.1.8, the first release that mocks an imported
  function, as the corpus download tests do.

## [0.1.0] - 2026-09-22

lexsync 0.1.0 is the first public release. CRAN published the R package on
2026-09-22 and assigned it the DOI <https://doi.org/10.32614/CRAN.package.lexsync>.
Zenodo archives the release tagged v0.1.0 under the concept DOI
<https://doi.org/10.5281/zenodo.22906962>.
The Python package's upload to PyPI from that release did not go through, so its
first version on PyPI is 0.1.1. The CRAN build predates the CRAN DOI, so its
`citation("lexsync")` gives the repository's address.

The first three entries under Added summarise the release. The others follow the
package through its development, so they describe each change against the state
it replaced.

### Added

- Initial dual-language (R + Python) release: many-language corpus access,
  parallel multidimensional matching (standardised-Euclidean and joint methods),
  counterbalancing, item resampling (items as a random factor), deterministic
  pseudoword generation, and generation of hardware-timed PsychoPy, OpenSesame
  and jsPsych experiments with the onset trigger flip-locked to stimulus onset.
- Cross-engine byte-identical stimulus selection, verified on the 21 worked
  designs across English, Spanish and Mandarin Chinese.
- Materials datasheet with provenance, checksums and a realised-control report
  (Cohen's d, 90% CI and a TOST equivalence test), alongside a pre-registration
  template and a machine-readable corpus registry.
- The experiment templates cannot drift between their three copies. `templates/` is
  the canonical set and both packages carry a mirror so an installed copy can reach
  one. Nothing checked that the three agreed, and no functional test could, because a
  stale mirror still renders and runs and simply produces a different experiment from
  the one
  documented. For the trigger templates that means code time-locking EEG markers to
  stimulus onset, where the failure is silent and the data unusable. Both engines now
  compare the bytes.
- The Python package runs a linter, under a rule set it states for itself. It ran none
  before, and now enforces `E`, `F`, `W`, `I`, `UP` and `B`, the bug-catching families
  alongside the style, import-order and modernisation rules its four sibling packages
  already answer to, pinned in `pyproject.toml` so a ruff release cannot move what CI
  checks. Three rules are turned off, each because the thing it objects to is carrying
  meaning. `UP031` would rewrite the `%`-formats that sit opposite the R twin's
  `sprintf` calls, some of which decide artefact bytes. `E702` objects to the semicolon
  in a symmetric pair written on one line. `E741` objects to `l`, which is the list
  number in `counterbalancing.py` and the same loop variable in the R twin.
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

### Changed

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

### Fixed

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

[Unreleased]: https://github.com/pablobernabeu/lexsync/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/pablobernabeu/lexsync/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/pablobernabeu/lexsync/releases/tag/v0.1.0
