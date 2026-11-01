# Changelog

All notable changes to lexsync are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to
adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). The R and
Python packages are released in lockstep under the same version. Because lexsync
is a data-bearing scientific tool, a change that alters *which stimuli are
selected* for the same inputs and seed is treated as a breaking change even when
no function signature changes.

## [Unreleased]

### Upgrading from 0.1.1

#### Changed results

- `matching.tie_break` defaults to `hash`, a keyed hash of each word, where
  spelling broke ties in favour of early-alphabet words, so designs with ties
  select different items. `matching.tie_break: bytes` restores the 0.1.1
  tie-break, except under `optimal`.
- Generated experiments present one counterbalancing version to each
  participant, where every list ran in one session, so each Latin-square target
  appeared in both conditions and a resampled design showed every replicate.
- A response event after a text event opens its window at the text's onset, and
  a response ends the trial, where the window opened once the text had gone and
  earlier keys were discarded. `from: offset` restores the delayed window.
- The PsychoPy and OpenSesame experiments record each reading time and each
  response with its reaction time and, when the trial has an `answer`, its
  accuracy, where they recorded none.
- In all three targets, a reaction time runs from the stimulus's onset, or from
  the response window under `from: offset`, where jsPsych timed it from the
  blank response screen.
- The loop tables give each `word` and `pseudoword` trial of a lexical decision
  its correct key in `answer`, by default the response event's first key for
  word and its second for pseudoword, where the main trials could not be scored.
- The jsPsych page names each trial's `answer` as the browser names the key,
  such as `arrowleft` for `left`, where its feedback called a correct arrow-key
  press incorrect.
- Matching leaves out candidates that lack a matched value, in every method,
  where an anchor without one was paired with the alphabetically first
  candidate, `joint` filled a shortfall with incomplete pairs and continuous
  selection took items without the predictor.
- `counterbalance` applies the paradigm's Latin square to a design that lists
  its own `events`, where it dealt the items factorially and so showed each
  target in both conditions of a list. `counterbalance.recipe: factorial`
  restores the old lists.
- `optimal` matching selects the n pairs of least summed distance when the
  conditions do not overlap (Volgenant, 2004), where it kept the n cheapest
  pairs of a complete assignment, which did not minimise their summed distance.
- `mahalanobis` matching estimates the correlations from the rows complete on
  the matched dimensions, where a dimension with any missing value lost all its
  correlations and entered the distance as an independent term.
- `run_pipeline` applies `reference_words` to a corpus or pool design,
  recomputing N, OLD20 and any bigram frequency against the list, where it kept
  the lexicon's own columns while the datasheet recorded the list as applied.
- A norms entry's `on:` is read as its join key, with a note in the run log,
  where YAML read a bare `on` as true and every join used `word`. Write
  `join_on:`.
- In Python, without `--schema`, `lexsync run --config-dir DIR` reads
  `DIR/schema.yaml` first, where it read the working directory's
  `config/schema.yaml` or else the bundled schema. Passing
  `--schema config/schema.yaml` restores the 0.1.1 choice when that file exists.
- In Python, without `--schema`, `lexsync run DESIGN` tries a `schema.yaml`
  beside the design before the bundled schema, where it read the bundled one
  when the working directory had no `config/schema.yaml`.
- In R under the C locale, design, schema and registry files are read in full,
  where a file was cut at its first accented letter with a warning, so a design
  could run without its later keys, such as `match_on`.
- Generated OpenSesame experiments prepare each display before the trial and
  time each event from its onset, where every event overran its duration. They
  log the frame period and send the 254 and 255 session markers.
- Generated OpenSesame experiments show stimulus text as written, where
  OpenSesame converted the loop table's cells, so '007' was shown as 7 and, in
  OpenSesame 4, 'True' as 1.
- The PsychoPy and OpenSesame experiments hold each trigger code for
  `triggers.trigger_hold_ms`, and at least 10 ms, unless the next onset's code
  replaces it, where OpenSesame sent a 10 ms pulse.
- In PsychoPy, the session markers and the code of an event shorter than the
  hold last the whole hold, where the markers were cleared at once and the
  event's code was cut short.
- The PsychoPy experiment holds the self-paced reading critical-region code for
  `triggers.trigger_hold_ms`, where it held it for `triggers.inter_trigger_ms`,
  10 ms by default.
- When item codes go with condition codes or a design's own codes from 40 to
  239, they skip those codes, where they could coincide, as sets 65 and 66 of a
  70-set design took condition codes 101 and 102.
- In R, a response or question key given alone is written as a list of one key,
  where jsonlite wrote a bare string, which the PsychoPy runner split into
  letters.
- In R, an unquoted `y` or `n` in a design is text, where it was TRUE or FALSE,
  so `keys: [y, n]` waited for keys named TRUE and FALSE.
- In R, YAML keys are read by exact name, where a longer key was read in place
  of an absent one, so a design with `font_size: 40` and no `font` set the font
  of all three experiments to '40'.
- The PsychoPy experiment runs full screen, and OpenSesame text is 48 pixels
  high, where it was 32. In the schema, `presentation.fullscreen: false`
  restores the 1280 by 1024 window, and `presentation.text_height_px` sets the
  text height of all three targets.
- The English example lexicon `en_example.csv` holds 3,000 forms screened
  against SUBTLEX-US, with N and OLD20 counted over the forms kept, where a
  quarter of its forms were non-standard, mostly names and acronyms, so code
  that reads it gives different numbers.
- The English demonstration designs select from the screened `en_v2.csv`, leave
  out a list of taboo words and abbreviations and check their pseudowords
  against wordfreq's fuller English list, so they select different items.
- Both apps open on the screened `en_v2` lexicon and keep its unmarked forms, so
  their defaults select different words. Choosing `en` under 'Lexicon' restores
  the old lexicon.
- The Shiny app's presets set their matched dimensions and method, where
  choosing a preset left 'Match on' at length, N and OLD20, so the neighbourhood
  and 2x2 presets matched on N, which they manipulate.
- The Shiny app writes a conditions-table edit into the edited cell, where it
  wrote it one column to the left, so a condition ran with values that were not
  typed. A typed second-factor bound is kept as a number.
- Pseudoword generation substitutes every letter the reference attests, where it
  used a to z and skipped words with other letters, so a generated Spanish
  design, for example, selects different items. An `alphabet` of a to z restores
  `make_pseudoword`'s old letters.
- The words and keys of lexica, pools, norm tables and item tables are put in
  Unicode NFC as read, so an accented word's precomposed and decomposed
  spellings are one word, where both could be selected.
- In Python, `build_pool` compares a categorical filter as R does, so a 0/1
  column with missing values matches its filter, where it matched nothing.
- In Python, a filter of two YAML booleans keeps no row of a 0/1 column, as in
  R, where it was read as a numeric range, so `[false, false]` kept rows holding
  0 and `[true, false]` was refused as reversed.
- In R, CSV values such as `t`, `T`, `F`, `1,000` and ISO dates are text, as in
  Python, where they were logical, numeric or dates.
- In R, each plain decimal in a CSV file is read as its nearest double, which
  readr could miss by one unit in the last place, and `-0` as 0.
- In R, CSV columns are typed from every row, where readr typed them from the
  first 1,000 rows, so a later value of another type was read as missing with a
  warning.
- In Python, CSV fields and headers are trimmed, as in R, where a padded
  category or header stopped a design that R ran, and an empty header cell is
  named by its position, such as `...3`.
- In R under the C locale, non-ASCII condition labels give the trial order, list
  balancing and jitter of the Python engine, where R hashed them as escape text.
- A fractional `duration_ms` is rounded where it was truncated, so 33.7 ms is
  presented as 34 ms, and fractional durations read from an item column are
  rounded in the stimuli and loop tables and counted in the run log.
- `cohens_d`, and the `d` of `cohens_d_ci`, are `None` in Python and `NA` in R
  for a condition with fewer than two items, where they were 0, a perfect
  balance. Python's `cohens_d_ci` limits are `None` too, where they were NaN.
- `count_syllables` counts the vowels of further Latin-script languages, such as
  Polish, Czech and Vietnamese, whatever their accents, and returns a missing
  value for a word in another script, where it returned 0.
- The suggested model uses the stimuli's `condition` column, where a lexical
  decision named a `lexicality` column the stimuli lack. Its note calls the
  random effects maximal only when they are, where it called them maximal in
  every factorial design.
- The suggested model enters a matched design's matched dimensions as centred
  covariates, where it had none, and gives items a condition slope whenever a
  Latin square ran, where categorisation had none.
- For a continuous pair design, the suggested model crosses condition with the
  predictor, where it had no condition term.
- In Python, the wordfreq connector puts every form in NFC and keeps forms with
  combining marks or zero-width (non-)joiners, Ukrainian forms with an
  apostrophe and Catalan forms with l·l, so its Hindi, Bengali, Persian,
  Ukrainian, Catalan and Greek lexica change.
- For a user's own registry entry with an `openlexicon` address, `fetch_corpus`
  caches the download as a lexicon made by `normalise_lexicon` with the entry's
  `columns` and `duplicates`, where it cached the file as published, so the
  cached lexicon can differ.
- In Python under pandas 3 with pyarrow, lexicon and pool words are lower-cased
  by `str.lower()`, as in R, where a final capital sigma became σ and İ became a
  bare i.
- OpenSesame response and question timeouts are written in whole milliseconds as
  declared, where 1,001 ms became 1,000, and a practice timeout is reported as
  'Too slow', where it was scored as a wrong key.
- The OpenSesame snippet `inline_send_triggers.py` sends only the condition code
  at the word's onset, where the item code went first and delayed it, and
  `inline_trigger_setup.py` opens the serial port named at its top, where it
  took the first one found.
- The `en_rastle_repro` example uses masked priming, where its prime had no
  forward mask, and it and `en_andrews_repro` run as lexical decisions with
  nonword fillers, where they had no nonwords.
- The categorisation example adds 16 non-member foils as fillers, where pressing
  'yes' on every trial scored perfectly.
- The lexical-decision practice table presents 'plang' where it presented
  'plank', an English word.

#### Changed interface

- `run_pipeline` refuses a probable design or schema key typo, such as
  `n_per_conditon`, where the key was ignored and the default count applied.
- `run_pipeline` and `match_stimuli` refuse a matched design with a missing or
  empty `match_on`, where both engines paired the alphabetically first words for
  an empty one, as R did for a missing one.
- A design's `name`, `language`, font and condition names must be text, so a
  number or an unquoted `no` is refused, where a design with `name: 2026` or
  `language: no` ran and named its files after 2026 or `false`.
- A design whose `name` and `language` both hold only ASCII punctuation and
  spaces is refused, where it ran and wrote files named only by their suffix,
  such as `_stimuli_py.csv` and a hidden `.osexp` and `.html`.
- The R package requires jsonlite 1.8.7 or later, since 1.8.5 and 1.8.6 write
  datasheets that differ from the Python engine's.
- The Streamlit app needs Streamlit 1.49 or later.
- The Python package's `requirements.txt` pins pandas 2.3.2 and numpy 2.3.2,
  which produced the committed demonstrations, where it pinned 3.0.3 and 2.4.6,
  and installs from wheels on Python 3.11 to 3.13 only.
  `requirements-experiment.txt` requires PsychoPy 2024.1 and pyserial 3.5 or
  later.
- Matching refuses a condition left without a candidate complete on the matched
  dimensions, and `mahalanobis` refuses a pool with fewer than k + 2 complete
  rows for k dimensions.
- In Python, `match_stimuli` and `select_continuous_stimuli` refuse
  `n_per_condition: 0`, where they returned their default size.
- In Python, `lexsync run --schema config/schema.yaml` stops when that file is
  missing, where it ran the bundled schema.
- `resample_stimuli` and `run_pipeline` refuse a `resample.n_sets` that is not a
  whole number of at least 1, where a fraction was truncated, a boolean or
  quoted number was taken as a count and, in R, zero gave an empty selection.
- Counterbalancing refuses a `counterbalance.optimise` other than `true` or
  `false`, which balanced lists in Python only, and
  `counterbalance.optimise: true` on a Latin-square design that lists its own
  `events`. It refuses a factorial design with more lists than item sets.
- A literal trigger code must be a whole number from 1 to 255, where 300 was
  sent as its low byte and 20.5 as 20. An unknown token such as `conditon` is
  refused, where R wrote `send_trigger(NA)` for OpenSesame.
- A design that sends item codes with condition codes, or with its own codes
  from 40 to 239, and has more item sets than the codes left free is refused
  unless the schema sets `triggers.allow_code_overlap: true`.
- A duration, fixed or read from an item column, must be present, finite and not
  negative, as must a jitter's lower bound, where a blank or negative duration
  stopped the experiment or showed the stimulus for no time.
- The exporters refuse a `list` or `replicate` that is not a whole number, and
  `export_opensesame` refuses a non-numeric value in a numeric loop column.
- A response event after a text event must share that event's `blocks` unless it
  sets `from: offset`, and a YAML boolean response key, such as an unquoted
  `yes`, is refused.
- A jsPsych page holding several versions runs nothing until its address gives
  `?participant=`, `?version=` or `?list=`.
- The result of `export_experiments` gains `files`, the paths of every file
  written, so a loop over its values also gets that list and, in R, its
  `unlist()` holds the PsychoPy script, the jsPsych page and version 1's
  OpenSesame experiment twice.
- With several versions, `export_opensesame` and the `opensesame` path of
  `export_experiments` give version 1's experiment, where they gave the one
  experiment that held every version.
- In R, a design giving `language_tag` without `language` stops, where
  `language_tag` was read as `language`.
- In R, a design, schema or registry file that is not UTF-8 is refused, where it
  was cut short with a warning.
- A norms entry with an unknown key is refused, where such a key was ignored,
  and so is a `norms:` block written as a mapping of named entries, which R
  accepted.
- `run_pipeline` refuses a `reference_words` list that is empty or holds a
  missing value, and Python reads a lone string as one word, as R does, where it
  read a list of letters.
- lexsync refuses a `LEXSYNC_REGISTRY` variable (Python), `lexsync.registry`
  option (R) or `registry_path` that names a missing file, where it read another
  registry, except that R failed on a missing `registry_path` with a connection
  error.
- `load_lexicon` refuses a non-numeric frequency column and a Zipf value outside
  0 to 9, and a CSV header that names a column twice is refused. `run_pipeline`
  refuses a design using `n_syllables` when a candidate lacks a syllable count.
- `describe_stimuli`, `match_report` and `match_report_continuous` refuse a
  dimension or grouping column the stimuli lack, where R returned a table of
  missing values with an `n` of 0 and Python raised a bare `KeyError`.
- Lexical-decision generation refuses words in a logographic script, such as
  Chinese, where it left them out.
- `run_all` refuses two designs that would write the same files, such as
  `en-lexdec` and `en_lexdec`.
- In R, `run_pipeline` and `run_all` default to `schema_path = NULL` and, in
  Python, `run_pipeline` defaults to `schema_path=None`, where they named the
  schema file they still read first when it exists.
- Neither app runs a factorial design with nothing under 'Match on'.
- For a user's own registry entry with an `openlexicon` address, `fetch_corpus`
  refuses a download without a frequency column it can map, where it cached it
  as published.
- `fetch_corpus` refuses a corpus name holding a slash, backslash or colon
  before it reads the registry, where an edited registry could make it write
  outside the cache.
- The `en_priming_jitter` item table `items/priming_pairs_en_soa.csv` names its
  per-trial column `prime_ms`, where it was `soa_ms`, since a 33 ms mask follows
  the prime.

#### Changed output

- The OpenSesame loop table holds only numbers, adds `lexsync_row` and renames
  `trial`, `list` and `set` to `lexsync_trial`, `lexsync_list` and
  `lexsync_set`.
- An OpenSesame experiment's presented text, `condition`, `block` and `answer`
  move to a text table named after it, such as `<base>_opensesame_text.csv`,
  which must be copied with the experiment.
- A design with several versions gets one OpenSesame experiment per version,
  such as `<base>_list<k>.osexp`, which warns and waits for space or escape
  when the subject number belongs to another version.
- The jsPsych page saves `<title>_v<version>.csv`, or
  `<title>_p<participant>_v<version>.csv` when its address names a participant,
  where it saved `<title>.csv`. The PsychoPy script writes
  `data/<base>_v<version>_<date>-<time>.csv`, with `_p<participant>` before
  `_v` when a participant number is given.
- In the jsPsych data, a response collected from its stimulus's onset is
  recorded on that stimulus's row, with `lexsync_event` 'target', where it had
  its own 'response' row. Every row gives the run's `version`, `replicate` and
  `list`, with `participant` when known.
- Launched without arguments, the PsychoPy experiment asks for the participant
  and the version in a start-up dialogue, even for a design with one version,
  where it started at once.
- In a resampled design, the loop tables carry `replicate` and each version's
  own copy of the practice and filler trials, and every loop table keeps each
  version's trials together.
- After a `matching.shortfall: allow` run falls short, the Methods paragraph
  states the number of items each condition holds, with the request beside it,
  where it stated the request.
- The datasheet and Methods paragraph give the counterbalancing recipe and the
  number of lists that ran, where they inferred the recipe from the item source,
  calling a table-sourced lexical decision a Latin square, and gave
  `counterbalance.lists`, 1 by default.
- The Methods paragraph and the Markdown datasheet's realised-control table
  label the interval by the configured alpha, where they said 90% whatever the
  alpha, and the Methods paragraph gives a continuous design's realised spreads
  and control windows in place of 'near-constant'.
- The Methods paragraph and Markdown datasheet say that the seed fixes only the
  trial order, where they tied the selection to the seed, and the datasheet no
  longer calls the selection free of item-selection bias.
- The datasheet and Methods paragraph credit wordfreq only for the lexica
  lexsync ships, where a user's own lexicon was described as wordfreq data. They
  name it by file name and checksum, and a fetched corpus by its registry
  citation.
- The datasheet and Methods paragraph credit `en_example.csv` to wordfreq
  screened against SUBTLEX-US and state the screening rule, where they credited
  wordfreq alone.
- The PsychoPy and OpenSesame experiments show instructions and wait for the
  space bar before the first trial, where they started at once, and jsPsych
  shows them in place of its general welcome, in English unless the design sets
  `instructions`.
- When the trigger device cannot be opened, the PsychoPy and OpenSesame
  experiments say so on screen and wait for C under the default
  `triggers.mode: auto`, where they ran on without notice, and they log the mode
  on every trial.
- The PsychoPy and jsPsych experiments treat fillers as main trials when they
  place pauses, where they paused before and after every filler. A design whose
  only blocks are practice, filler and main trials pauses once, where the
  practice trials end.
- The Methods paragraph describes the realised control by its largest matched
  difference and then the equivalence tests, where it judged the control on the
  tests alone, and names large uncontrolled differences.
- The Methods paragraph also says that each participant was presented one
  version, when responses were collected and, in a lexical decision, which key
  answered each condition.
- The realised-control report covers every dimension lexsync knows and every
  pair of conditions. `match_report` adds rows and the columns `mean_diff` and
  `role` after the existing ones and leaves out a dimension with no numeric
  value.
- `match_report_continuous` adds `sd`, `sd_ratio`, `window_low` and
  `window_high`, comparing the predictor's spread with an even spread and each
  control's with the pool's.
- A generated lexical decision's report compares the words with the pseudowords
  on bigram frequency, N and OLD20, and `build_lexdec_stimuli` returns `base`
  and `edit_distance` columns.
- Datasheets use format 1.2, which adds fields for this release's features,
  per-list counts and the schema's path. `design.n_per_condition` gives the
  default applied when the design gives no count, where it was null.
- The datasheet's artefact list and the run log include the loop and text
  tables.
- The datasheet's realised-control entries give each dimension's role as
  manipulated, controlled or uncontrolled, where every unmatched dimension was
  'manipulated/free', and the Markdown table adds each row's pair and raw
  difference.
- An incomplete Latin-square rotation is reported in the run log, datasheet and
  Methods paragraph.
- The Markdown datasheet and Methods paragraph round numbers half away from zero
  from the stored values, so some two-place values change, and print a TOST p to
  four places, with `< 0.0001` for one that rounds to zero.
- A generated design's datasheet counts only the words the generator can use,
  where it counted the whole band.
- A design whose name or language has non-ASCII characters gets a file stem
  ending in an eight-character checksum, given by `design_stem`, where
  Chinese-named designs could share a stem and one with no ASCII letter or digit
  in either wrote hidden `.osexp` and `.html` files.
- The apps' download bundles hold the outputs under `output/`, where they sat at
  the archive's root, and reproduce their own record without local paths. The
  PsychoPy and OpenSesame downloads are zip archives holding the tables those
  experiments load.
- Both apps warn when 'Match on' names a dimension whose windows differ between
  conditions and label intervals by the configured alpha. They show each
  comparison's role and raw difference and label each bar of the chart by
  dimension and pair.
- Under the exported code, both apps say that the engines select byte-identical
  stimuli only when the run's datasheet says so, where they said so under every
  matching method.
- When no schema is named, `run_pipeline`, `run_all` and `lexsync run` say which
  one they use.
- `list_corpora` gives SUBTLEX-US the status 'supported', where it was 'listed',
  since `fetch_corpus` can download it.
- The run log notes settings that have no effect: an event's
  `onset_locked: false`, a schema's `triggers.inter_trigger_ms` and
  `reference_words` given for a generate or table design, which the datasheet no
  longer records as applied.
- The run log notes a design in another language without its own `instructions`,
  a design whose instructions can only name its keys, a practice or filler
  answer the response mapping contradicts and a trial the lexical-decision
  default leaves without an answer.
- lexsync reports a literal trigger code of 254 or 255, which the laboratory
  targets send as session markers, or one that equals a condition code or lies
  within the range of item codes the design sends.
- The jsPsych page writes each trial's numbers to 15 significant digits, where R
  kept four decimal places and Python up to 17.
- In R, the datasheet records paths with forward slashes, where Windows paths
  kept their backslashes.
- In R, a block scalar (`|` or `>`) that ends a design, schema or registry file
  keeps its final line break, as in Python, so a `description` written that way
  ends with one in the datasheet.
- In Python, the Methods paragraph keeps the design's language label as written,
  raising only its first letter, where 'British English' became 'British
  english'.
- In Python, a wordfreq lexicon built with fewer forms than requested says so on
  standard output.

### Added

- `validate_design` checks a design's keys and values, and `run_pipeline` calls
  it before anything is selected or written.
- `counterbalance.max_run` caps runs of one condition, or of one value of a
  column named in `counterbalance.run_on`, in the trial order, and refuses only
  a limit no order can meet (van Casteren & Davis, 2006). It is off by default.
- `counterbalance.orders: m` gives each list m trial orders, each with its own
  practice order, which participants take by participant number. The loop tables
  gain `order_1` to `order_m`, and OpenSesame gets one experiment per version
  and order. The PsychoPy and jsPsych data record the order each run used.
- `counterbalance.scale: mad` balances lists in units of each dimension's mean
  absolute deviation, so a dimension's weight does not depend on where its scale
  starts. The default stays `mean`.
- `counterbalance.incomplete: error`, in the design or the schema, refuses an
  incomplete Latin-square rotation.
- `counterbalance.recipe` (`factorial` or `latin_square_target`) overrides the
  counterbalancing recipe of the design's paradigm.
- `normalise_lexicon` turns a delimited corpus file into a lexicon, deriving
  Zipf values from frequencies per million and summing a form's rows under a
  registry entry's `duplicates: sum`. `fetch_corpus("subtlex_us")` downloads and
  normalises SUBTLEX-US, and a registry entry may name a `derived` file, already
  normalised, to fetch instead.
- In Python, `lexsync fetch NAME --n-words N` sets the size of a wordfreq
  lexicon, 10,000 forms by default.
- In Python, `lexsync.paths.resolve_schema` gives the schema a run would use,
  and `lexsync.paths.bundled_schema` gives the path of the copy shipped with the
  package.
- `masked_priming` presents a forward mask of hash marks, a lower-case prime and
  an upper-case target (Forster & Davis, 1984). A text event's `case` sets the
  case shown, and a mask's `length_of` sets its length.
- A design sets its instruction text with `instructions`, and `response_mapping`
  and `rotate_mapping_by_list` set the key that answers each condition and
  rotate the keys across lists.
- `items.generation.exclude` lists word forms a generated pseudoword must not
  equal, from files or fetched corpora, and `generate_pseudowords` and
  `build_lexdec_stimuli` take them as `exclude`. The datasheet records each list
  with its checksum.
- `exclude_words` lists words a design leaves out of its candidates, inline or
  in a file, and the datasheet records the list with its checksum.
- `en_v2.csv`, a screened English lexicon in the repository, marks the forms
  absent from SUBTLEX-US or seldom written in lower case (Brysbaert & New, 2009)
  and counts N and OLD20 over the unmarked forms, keeping the unscreened values
  in `n_density_raw` and `old20_raw`. `pool_filters: {nonstandard: [0, 0]}`
  keeps the unmarked forms.
- The `es_lexdec` example generates a Spanish lexical decision and checks its
  pseudowords against wordfreq's Spanish word list.
- In the schema, `triggers.mode: hardware` stops an experiment whose trigger
  device cannot be opened, and `triggers.mode: mock` prints the codes without
  trying it. `triggers.backend: serial` sends each code as one byte to
  `triggers.serial_port` at `triggers.baudrate`, 115200 by default.
- A design can use a derived dimension (`n_density`, `old20` or `bigram_freq`)
  in `define_by`, `pool_filters`, `counterbalance.balance_on` or a continuous
  design's predictor or controls, and `run_pipeline` computes any the lexicon
  lacks.
- A lexicon or pool may mark the forms that make up the neighbourhood reference
  with a `reference_member` column of 0 and 1.
- The PsychoPy script takes `--participant`, `--version` or `--list`, and the
  jsPsych page reads `?participant=`, `?version=` or `?list=` from its address.
  Both refuse a list when the versions span several replicates. In Python,
  `lexsync.scripting.presentation_versions` lists the versions a set of trials
  holds.

### Changed

- When no schema is named and none is found where 0.1.1 looked, `run_pipeline`
  tries a `schema.yaml` beside the design and `run_all` tries
  `config/schema.yaml` in the working directory. Both then fall back to the
  schema bundled with the package, where they stopped.
- `run_pipeline` refuses a missing `name` or `language`, an unsafe name or font,
  a bad trigger address or response key and a repeated condition name before
  anything is written, where these failed later, some at export after four
  files had been written.
- `assign_triggers` gains `events` and `schema`, which `export_experiments`
  passes so that item codes avoid the design's other codes.
- `build_datasheet` gains `counterbalance_check`, `input_normalisation`,
  `generation_exclude`, `exclusions`, `zipf_derivation` and `trial_order`, which
  `run_pipeline` passes for the format 1.2 fields.
- `match_report` gains `roles`, a function giving each comparison's role, which
  `run_pipeline` derives from the design, and `match_report_continuous` gains
  `audit`, the selector's record of the control windows, which it reads from the
  stimuli by default.
- In R, `match_stimuli` and `select_continuous_stimuli` refuse
  `n_per_condition: 0` as not a positive whole number, where they failed with an
  unrelated error.
- In Python, `fetch_corpus` and `lexsync.corpora.build_wordfreq_lexicon` gain
  `strict`, which refuses a lexicon with fewer forms than requested, and
  `exclude_latin`, which drops forms holding a Latin letter.
- In Python, `add_neighbourhood` computes N and OLD20 much faster, with
  identical values.
- In R, `optimal` matching runs much faster on large pools.
- In Python, the command line prints lexsync's own errors without a traceback
  and exits with status 1, and `lexsync --traceback` shows the traceback.
- `fetch_corpus` refusals name the registry they read and say when an entry
  registers no download address. In R, it explains that the Python package
  builds a wordfreq lexicon, where it said the language was not in the registry.
- A norms entry that is not a mapping, such as a bare file name, is refused as
  needing a `path`, where it failed with each language's own error.
- The Shiny method selector carries the Streamlit app's note on `mahalanobis`
  and `optimal`, and each app removes a run's folder once the next run's results
  or an error replace its results.

### Deprecated

- A design or schema key lexsync does not read is noted in the run log and will
  be refused in a later release. Annotations belong in `description` or a key
  beginning `x_`.

### Fixed

- A resampled design with filler trials runs, where it stopped with an error.
- Generated OpenSesame experiments run with words such as 'nan' and 'infinity'
  in the stimuli, where these could stop an OpenSesame 4 session.
- In R, a factorial design with a key whose name begins with another key's, such
  as `continuous_notes`, runs, where it stopped.
- In R, joint matching over more than 1,200 candidates on a dimension with
  missing values no longer fails.
- In R, `list_corpora` and `fetch_corpus` read the bundled registry under the C
  locale, where they failed.
- In Python, `n_per_condition` accepts a whole number written as `4.0`, and a
  `null` tolerance or a schema without a `matching:` block no longer stops a
  run.
- Both apps leave out a factor whose bound is not a number, where they stopped
  with an error.
- The Streamlit app writes an uploaded file once, where it wrote a copy on every
  rerun, and shows 'Stimulus font' with the other design fields.
- Both apps' exported command lines quote the design file's name and run in
  `cmd.exe` and Windows PowerShell.
- The Streamlit app's exported `Rscript` command passes the `outdir` that
  `run_pipeline` requires.
- The R package installs the licence notice for its CC BY-SA lexica as
  `COPYRIGHTS`, so binary installations carry it.

### Security

- Generated OpenSesame experiments no longer pass stimulus text through
  OpenSesame's variable store, which evaluates it, so a shared item table can no
  longer run code on the presenting machine.
- The jsPsych page loads jsPsych, its keyboard plugin and its stylesheet from
  unpkg with Subresource Integrity, so a browser refuses a modified copy.

### Documentation

- The experiments guides are substantially extended, with new sections on when
  a response is collected, instructions and the response mapping, trial orders,
  running a counterbalanced experiment and checking the timing with a
  photodiode. The matching guides add a section on choosing and screening a
  lexicon, which says that the wordfreq lexica hold names, acronyms and other
  non-standard forms, and cover ties between equally close candidates. The
  reproducibility guides set out the CSV and YAML input contracts and the file
  names.
- The experiments guides say that every participant given a list and trial
  order meets the practice trials in one fixed order, where they said that the
  practice trials were shuffled so that participants meet them in different
  orders.
- The documentation says that a continuous design spreads its items over the
  predictor's ranks, so the selection follows the pool's distribution, and that
  the tolerance windows trim the controls' tails without holding them constant,
  which the matching guides and the 0.1.0 notes misstated.
- The matching guides say that a generated pseudoword is a non-word only
  relative to the reference words, so it can be a real word too rare for the
  lexicon, such as crier or pall, where they said it could not be a real word.
- The experiments guides say that item trigger codes follow the code-point order
  of the set labels, so that, with sets 1 to 20, set 10 is 41 and set 2 is 51,
  and that they are decoded through the loop table.
- The schema's comments and the Python experiments guide say that the trigger
  settings, and the presentation settings other than `font`, apply to every
  design run with the schema, where they said that a design could override them.
- The getting-started guides say that the `timing` keys reach every fixation,
  every text event whose `trigger` is `condition` and every blank, but not an
  event with a per-trial `duration` block, where they named only the fixation,
  critical-word and inter-stimulus durations.
- The guides say that a pool filter given two numbers is an inclusive range
  whatever the column, that `standardised_euclidean` is the one default matching
  method and that list balancing runs at most `counterbalance.max_passes`
  passes, 500 by default.
- `resample_stimuli` says that its selections match the other engine's only
  under `standardised_euclidean` and `joint`, and the repository README says the
  same of the two apps.
- The documentation calls the 0.5 equivalence bound a convention, where the
  schema and the R help page of `tost_equiv` credited it to Lakens (2017), and
  the quick starts in the R README and the R Get started vignette use 60 items
  per condition, where they used 15, too few for any varying dimension to pass
  the equivalence test.
- The corpus registry no longer gives the SUBTLEX-US and SUBTLEX-DE log-count
  columns, or a SUBTLEX-CH column that does not exist, as the source of
  `freq_zipf`.
- The app guides and both apps' tolerance panels give the frequency k of
  González Alonso et al. (2025) as 0.1111111111111111, since 0.111 gives a
  window narrower than a ninth of a standard deviation.

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
