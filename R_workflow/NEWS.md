# lexsync (development version)

## Upgrading from the previous release (0.1.1)

### Changed results

* `matching.tie_break` defaults to `hash`, a keyed hash of each word, where
  spelling broke ties in favour of early-alphabet words, so designs with ties
  select different items. `matching.tie_break: bytes` restores the 0.1.1
  tie-break, except under `optimal`.
* Generated experiments present one counterbalancing version to each
  participant, where every list ran in one session, so each Latin-square target
  appeared in both conditions and a resampled design showed every replicate.
* A response event after a text event opens its window at the text's onset, and
  a response ends the trial, where the window opened once the text had gone and
  earlier keys were discarded. `from: offset` restores the delayed window.
* The PsychoPy and OpenSesame experiments record each reading time and each
  response with its reaction time and, when the trial has an `answer`, its
  accuracy, where they recorded none.
* In all three targets, a reaction time runs from the stimulus's onset, or from
  the response window under `from: offset`, where jsPsych timed it from the
  blank response screen.
* The loop tables give each `word` and `pseudoword` trial of a lexical decision
  its correct key in `answer`, by default the response event's first key for
  word and its second for pseudoword, where the main trials could not be scored.
* The jsPsych page names each trial's `answer` as the browser names the key,
  such as `arrowleft` for `left`, where its feedback called a correct arrow-key
  press incorrect.
* Matching leaves out candidates that lack a matched value, in every method,
  where an anchor without one was paired with the alphabetically first
  candidate, `joint` filled a shortfall with incomplete pairs and continuous
  selection took items without the predictor.
* `counterbalance()` applies the paradigm's Latin square to a design that lists
  its own `events`, where it dealt the items factorially and so showed each
  target in both conditions of a list. `counterbalance.recipe: factorial`
  restores the old lists.
* `optimal` matching selects the n pairs of least summed distance when the
  conditions do not overlap (Volgenant, 2004), where it kept the n cheapest
  pairs of a complete assignment, which did not minimise their summed distance.
* `mahalanobis` matching estimates the correlations from the rows complete on
  the matched dimensions, where a dimension with any missing value lost all its
  correlations and entered the distance as an independent term.
* `run_pipeline()` applies `reference_words` to a corpus or pool design,
  recomputing N, OLD20 and any bigram frequency against the list, where it kept
  the lexicon's own columns while the datasheet recorded the list as applied.
* A norms entry's `on:` is read as its join key, with a note in the run log,
  where YAML read a bare `on` as true and every join used `word`. Write
  `join_on:`.
* Under the C locale, design, schema and registry files are read in full, where
  a file was cut at its first accented letter with a warning, so a design could
  run without its later keys, such as `match_on`.
* Generated OpenSesame experiments prepare each display before the trial and
  time each event from its onset, where every event overran its duration. They
  log the frame period and send the 254 and 255 session markers.
* Generated OpenSesame experiments show stimulus text as written, where
  OpenSesame converted the loop table's cells, so '007' was shown as 7 and, in
  OpenSesame 4, 'True' as 1.
* The PsychoPy and OpenSesame experiments hold each trigger code for
  `triggers.trigger_hold_ms`, and at least 10 ms, unless the next onset's code
  replaces it, where OpenSesame sent a 10 ms pulse.
* In PsychoPy, the session markers and the code of an event shorter than the
  hold last the whole hold, where the markers were cleared at once and the
  event's code was cut short.
* The PsychoPy experiment holds the self-paced reading critical-region code for
  `triggers.trigger_hold_ms`, where it held it for `triggers.inter_trigger_ms`,
  10 ms by default.
* When item codes go with condition codes or a design's own codes from 40 to
  239, they skip those codes, where they could coincide, as sets 65 and 66 of a
  70-set design took condition codes 101 and 102.
* A response or question key given alone is written as a list of one key, where
  jsonlite wrote a bare string, which the PsychoPy runner split into letters.
* An unquoted `y` or `n` in a design is text, where it was TRUE or FALSE, so
  `keys: [y, n]` waited for keys named TRUE and FALSE.
* YAML keys are read by exact name, where a longer key was read in place of an
  absent one, so a design with `font_size: 40` and no `font` set the font of all
  three experiments to '40'.
* The PsychoPy experiment runs full screen, and OpenSesame text is 48 pixels
  high, where it was 32. In the schema, `presentation.fullscreen: false`
  restores the 1280 by 1024 window, and `presentation.text_height_px` sets the
  text height of all three targets.
* The English example lexicon `en_example.csv` holds 3,000 forms screened
  against SUBTLEX-US, with N and OLD20 counted over the forms kept, where a
  quarter of its forms were non-standard, mostly names and acronyms, so code
  that reads it gives different numbers.
* The English demonstration designs select from the screened `en_v2.csv`, leave
  out a list of taboo words and abbreviations and check their pseudowords
  against wordfreq's fuller English list, so they select different items.
* Both apps open on the screened `en_v2` lexicon and keep its unmarked forms, so
  their defaults select different words. Choosing `en` under 'Lexicon' restores
  the old lexicon.
* The Shiny app's presets set their matched dimensions and method, where
  choosing a preset left 'Match on' at length, N and OLD20, so the neighbourhood
  and 2x2 presets matched on N, which they manipulate.
* The Shiny app writes a conditions-table edit into the edited cell, where it
  wrote it one column to the left, so a condition ran with values that were not
  typed. A typed second-factor bound is kept as a number.
* Pseudoword generation substitutes every letter the reference attests, where it
  used a to z and skipped words with other letters, so a generated Spanish
  design, for example, selects different items. An `alphabet` of a to z restores
  `make_pseudoword()`'s old letters.
* The words and keys of lexica, pools, norm tables and item tables are put in
  Unicode NFC as read, so an accented word's precomposed and decomposed
  spellings are one word, where both could be selected.
* CSV values such as `t`, `T`, `F`, `1,000` and ISO dates are text, as in the
  Python engine, where they were logical, numeric or dates.
* Each plain decimal in a CSV file is read as its nearest double, which readr
  could miss by one unit in the last place, and `-0` as 0.
* CSV columns are typed from every row, where readr typed them from the first
  1,000 rows, so a later value of another type was read as missing with a
  warning.
* Under the C locale, non-ASCII condition labels give the trial order, list
  balancing and jitter of the Python engine, where they were hashed as escape
  text.
* A fractional `duration_ms` is rounded where it was truncated, so 33.7 ms is
  presented as 34 ms, and fractional durations read from an item column are
  rounded in the stimuli and loop tables and counted in the run log.
* `cohens_d()`, and the `d` of `cohens_d_ci()`, are `NA` for a condition with
  fewer than two items, where they were 0, a perfect balance.
* `count_syllables()` counts the vowels of further Latin-script languages, such
  as Polish, Czech and Vietnamese, whatever their accents, and returns `NA` for
  a word in another script, where it returned 0.
* The suggested model uses the stimuli's `condition` column, where a lexical
  decision named a `lexicality` column the stimuli lack. Its note calls the
  random effects maximal only when they are, where it called them maximal in
  every factorial design.
* The suggested model enters a matched design's matched dimensions as centred
  covariates, where it had none, and gives items a condition slope whenever a
  Latin square ran, where categorisation had none.
* For a continuous pair design, the suggested model crosses condition with the
  predictor, where it had no condition term.
* For a user's own registry entry with an `openlexicon` address,
  `fetch_corpus()` caches the download as a lexicon made by
  `normalise_lexicon()` with the entry's `columns` and `duplicates`, where it
  cached the file as published, so the cached lexicon can differ.
* OpenSesame response and question timeouts are written in whole milliseconds as
  declared, where 1,001 ms became 1,000, and a practice timeout is reported as
  'Too slow', where it was scored as a wrong key.
* The OpenSesame snippet `inline_send_triggers.py` sends only the condition code
  at the word's onset, where the item code went first and delayed it, and
  `inline_trigger_setup.py` opens the serial port named at its top, where it
  took the first one found.
* The `en_rastle_repro` example uses masked priming, where its prime had no
  forward mask, and it and `en_andrews_repro` run as lexical decisions with
  nonword fillers, where they had no nonwords.
* The categorisation example adds 16 non-member foils as fillers, where pressing
  'yes' on every trial scored perfectly.
* The lexical-decision practice table presents 'plang' where it presented
  'plank', an English word.

### Changed interface

* `run_pipeline()` refuses a probable design or schema key typo, such as
  `n_per_conditon`, where the key was ignored and the default count applied.
* `run_pipeline()` and `match_stimuli()` refuse a matched design with a missing
  or empty `match_on`, where they paired the alphabetically first words.
* A design's `name`, `language`, font and condition names must be text, so a
  number or an unquoted `no` is refused, where a design with `name: 2026` or
  `language: no` ran and named its files after 2026 or `false`.
* A design whose `name` and `language` both hold only ASCII punctuation and
  spaces is refused, where it ran and named its files with a leading underscore.
* lexsync requires jsonlite 1.8.7 or later, since 1.8.5 and 1.8.6 write
  datasheets that differ from the Python engine's.
* Matching refuses a condition left without a candidate complete on the matched
  dimensions, and `mahalanobis` refuses a pool with fewer than k + 2 complete
  rows for k dimensions.
* `resample_stimuli()` and `run_pipeline()` refuse a `resample.n_sets` that is
  not a whole number of at least 1, where a fraction was truncated, a boolean or
  quoted number was taken as a count and zero gave an empty selection.
* Counterbalancing refuses a `counterbalance.optimise` other than `true` or
  `false`, which balanced lists in Python only, and
  `counterbalance.optimise: true` on a Latin-square design that lists its own
  `events`. It refuses a factorial design with more lists than item sets.
* A literal trigger code must be a whole number from 1 to 255, where 300 was
  sent as its low byte and 20.5 as 20. An unknown token such as `conditon` is
  refused, where `send_trigger(NA)` was written for OpenSesame.
* A design that sends item codes with condition codes, or with its own codes
  from 40 to 239, and has more item sets than the codes left free is refused
  unless the schema sets `triggers.allow_code_overlap: true`.
* A duration, fixed or read from an item column, must be present, finite and not
  negative, as must a jitter's lower bound, where a blank or negative duration
  stopped the experiment or showed the stimulus for no time.
* The exporters refuse a `list` or `replicate` that is not a whole number, and
  `export_opensesame()` refuses a non-numeric value in a numeric loop column.
* A response event after a text event must share that event's `blocks` unless it
  sets `from: offset`, and a YAML boolean response key, such as an unquoted
  `yes`, is refused.
* A jsPsych page holding several versions runs nothing until its address gives
  `?participant=`, `?version=` or `?list=`.
* The result of `export_experiments()` gains `files`, the paths of every file
  written, so a loop over its values also gets that vector and its `unlist()`
  holds the PsychoPy script, the jsPsych page and version 1's OpenSesame
  experiment twice.
* With several versions, `export_opensesame()` and the `opensesame` path of
  `export_experiments()` give version 1's experiment, where they gave the one
  experiment that held every version.
* A design giving `language_tag` without `language` stops, where `language_tag`
  was read as `language`.
* A design, schema or registry file that is not UTF-8 is refused, where it was
  cut short with a warning.
* A norms entry with an unknown key is refused, where such a key was ignored,
  and so is a `norms:` block written as a mapping of named entries, which was
  accepted.
* `run_pipeline()` refuses a `reference_words` list that is empty or holds a
  missing value.
* lexsync refuses a `lexsync.registry` option or `registry_path` that names a
  missing file, where it read another registry, except that a missing
  `registry_path` failed with a connection error.
* `load_lexicon()` refuses a non-numeric frequency column and a Zipf value
  outside 0 to 9, and a CSV header that names a column twice is refused.
  `run_pipeline()` refuses a design using `n_syllables` when a candidate lacks a
  syllable count.
* `describe_stimuli()`, `match_report()` and `match_report_continuous()` refuse
  a dimension or grouping column the stimuli lack, where they returned a table
  of missing values with an `n` of 0.
* Lexical-decision generation refuses words in a logographic script, such as
  Chinese, where it left them out.
* `run_all()` refuses two designs that would write the same files, such as
  `en-lexdec` and `en_lexdec`.
* `run_pipeline()` and `run_all()` default to `schema_path = NULL`, where they
  named the schema file they still read first when it exists.
* Neither app runs a factorial design with nothing under 'Match on'.
* For a user's own registry entry with an `openlexicon` address,
  `fetch_corpus()` refuses a download without a frequency column it can map,
  where it cached it as published.
* `fetch_corpus()` refuses a corpus name holding a slash, backslash or colon
  before it reads the registry, where an edited registry could make it write
  outside the cache.
* The `en_priming_jitter` item table `items/priming_pairs_en_soa.csv` names its
  per-trial column `prime_ms`, where it was `soa_ms`, since a 33 ms mask follows
  the prime.

### Changed output

* The OpenSesame loop table holds only numbers, adds `lexsync_row` and renames
  `trial`, `list` and `set` to `lexsync_trial`, `lexsync_list` and
  `lexsync_set`.
* An OpenSesame experiment's presented text, `condition`, `block` and `answer`
  move to a text table named after it, such as `<base>_opensesame_text.csv`,
  which must be copied with the experiment.
* A design with several versions gets one OpenSesame experiment per version,
  such as `<base>_list<k>.osexp`, which warns and waits for space or escape
  when the subject number belongs to another version.
* The jsPsych page saves `<title>_v<version>.csv`, or
  `<title>_p<participant>_v<version>.csv` when its address names a participant,
  where it saved `<title>.csv`. The PsychoPy script writes
  `data/<base>_v<version>_<date>-<time>.csv`, with `_p<participant>` before
  `_v` when a participant number is given.
* In the jsPsych data, a response collected from its stimulus's onset is
  recorded on that stimulus's row, with `lexsync_event` 'target', where it had
  its own 'response' row. Every row gives the run's `version`, `replicate` and
  `list`, with `participant` when known.
* Launched without arguments, the PsychoPy experiment asks for the participant
  and the version in a start-up dialogue, even for a design with one version,
  where it started at once.
* In a resampled design, the loop tables carry `replicate` and each version's
  own copy of the practice and filler trials, and every loop table keeps each
  version's trials together.
* After a `matching.shortfall: allow` run falls short, the Methods paragraph
  states the number of items each condition holds, with the request beside it,
  where it stated the request.
* The datasheet and Methods paragraph give the counterbalancing recipe and the
  number of lists that ran, where they inferred the recipe from the item source,
  calling a table-sourced lexical decision a Latin square, and gave
  `counterbalance.lists`, 1 by default.
* The Methods paragraph and the Markdown datasheet's realised-control table
  label the interval by the configured alpha, where they said 90% whatever the
  alpha, and the Methods paragraph gives a continuous design's realised spreads
  and control windows in place of 'near-constant'.
* The Methods paragraph and Markdown datasheet say that the seed fixes only the
  trial order, where they tied the selection to the seed, and the datasheet no
  longer calls the selection free of item-selection bias.
* The datasheet and Methods paragraph credit wordfreq only for the lexica
  lexsync ships, where a user's own lexicon was described as wordfreq data. They
  name it by file name and checksum, and a fetched corpus by its registry
  citation.
* The datasheet and Methods paragraph credit `en_example.csv` to wordfreq
  screened against SUBTLEX-US and state the screening rule, where they credited
  wordfreq alone.
* The PsychoPy and OpenSesame experiments show instructions and wait for the
  space bar before the first trial, where they started at once, and jsPsych
  shows them in place of its general welcome, in English unless the design sets
  `instructions`.
* When the trigger device cannot be opened, the PsychoPy and OpenSesame
  experiments say so on screen and wait for C under the default
  `triggers.mode: auto`, where they ran on without notice, and they log the mode
  on every trial.
* The PsychoPy and jsPsych experiments treat fillers as main trials when they
  place pauses, where they paused before and after every filler. A design whose
  only blocks are practice, filler and main trials pauses once, where the
  practice trials end.
* The Methods paragraph describes the realised control by its largest matched
  difference and then the equivalence tests, where it judged the control on the
  tests alone, and names large uncontrolled differences.
* The Methods paragraph also says that each participant was presented one
  version, when responses were collected and, in a lexical decision, which key
  answered each condition.
* The realised-control report covers every dimension lexsync knows and every
  pair of conditions. `match_report()` adds rows and the columns `mean_diff` and
  `role` after the existing ones and leaves out a dimension with no numeric
  value.
* `match_report_continuous()` adds `sd`, `sd_ratio`, `window_low` and
  `window_high`, comparing the predictor's spread with an even spread and each
  control's with the pool's.
* A generated lexical decision's report compares the words with the pseudowords
  on bigram frequency, N and OLD20, and `build_lexdec_stimuli()` returns `base`
  and `edit_distance` columns.
* Datasheets use format 1.2, which adds fields for this release's features,
  per-list counts and the schema's path. `design.n_per_condition` gives the
  default applied when the design gives no count, where it was null.
* The datasheet's artefact list and the run log include the loop and text
  tables.
* The datasheet's realised-control entries give each dimension's role as
  manipulated, controlled or uncontrolled, where every unmatched dimension was
  'manipulated/free', and the Markdown table adds each row's pair and raw
  difference.
* An incomplete Latin-square rotation is reported in the run log, datasheet and
  Methods paragraph.
* The Markdown datasheet and Methods paragraph round numbers half away from zero
  from the stored values, so some two-place values change, and print a TOST p to
  four places, with `< 0.0001` for one that rounds to zero.
* A generated design's datasheet counts only the words the generator can use,
  where it counted the whole band.
* A design whose name or language has non-ASCII characters writes its files
  under a stem with an eight-character checksum suffix, given by
  `design_stem()`, where two Chinese-named designs could overwrite each other's
  files.
* The apps' download bundles hold the outputs under `output/`, where they sat at
  the archive's root, and reproduce their own record without local paths. The
  PsychoPy and OpenSesame downloads are zip archives holding the tables those
  experiments load.
* Both apps warn when 'Match on' names a dimension whose windows differ between
  conditions and label intervals by the configured alpha. They show each
  comparison's role and raw difference and label each bar of the chart by
  dimension and pair.
* Under the exported code, both apps say that the engines select byte-identical
  stimuli only when the run's datasheet says so, where they said so under every
  matching method.
* When no schema is named, `run_pipeline()` and `run_all()` say which one they
  use.
* `list_corpora()` gives SUBTLEX-US the status 'supported', where it was
  'listed', since `fetch_corpus()` can download it.
* The run log notes settings that have no effect: an event's
  `onset_locked: false`, a schema's `triggers.inter_trigger_ms` and
  `reference_words` given for a generate or table design, which the datasheet no
  longer records as applied.
* The run log notes a design in another language without its own `instructions`,
  a design whose instructions can only name its keys, practice or filler answers
  the response mapping contradicts and trials the lexical-decision default
  leaves without an answer.
* lexsync reports a literal trigger code of 254 or 255, which the laboratory
  targets send as session markers, or one that equals a condition code or lies
  within the range of item codes the design sends.
* The jsPsych page writes each trial's numbers to 15 significant digits, where
  it kept four decimal places.
* The datasheet records paths with forward slashes, where Windows paths kept
  their backslashes.
* A literal block that ends a design, schema or registry file keeps its final
  line break, as in the Python engine, so a `description` written that way ends
  with one in the datasheet.

## New features

* `validate_design()` checks a design's keys and values, and `run_pipeline()`
  calls it before anything is selected or written.
* `counterbalance.max_run` caps runs of one condition, or of one value of a
  column named in `counterbalance.run_on`, in the trial order, and refuses only
  a limit no order can meet (van Casteren & Davis, 2006). It is off by default.
* `counterbalance.orders: m` gives each list m trial orders, each with its own
  practice order, which participants take by participant number. The loop tables
  gain `order_1` to `order_m`, and OpenSesame gets one experiment per version
  and order. The PsychoPy and jsPsych data record the order each run used.
* `counterbalance.scale: mad` balances lists in units of each dimension's mean
  absolute deviation, so a dimension's weight does not depend on where its scale
  starts. The default stays `mean`.
* `counterbalance.incomplete: error`, in the design or the schema, refuses an
  incomplete Latin-square rotation.
* `counterbalance.recipe` (`factorial` or `latin_square_target`) overrides the
  counterbalancing recipe of the design's paradigm.
* `normalise_lexicon()` turns a delimited corpus file into a lexicon, deriving
  Zipf values from frequencies per million and summing a form's rows under a
  registry entry's `duplicates: sum`. `fetch_corpus("subtlex_us")` downloads and
  normalises SUBTLEX-US, and a registry entry may name a `derived` file, already
  normalised, to fetch instead.
* `masked_priming` presents a forward mask of hash marks, a lower-case prime and
  an upper-case target (Forster & Davis, 1984). A text event's `case` sets the
  case shown, and a mask's `length_of` sets its length.
* A design sets its instruction text with `instructions`, and `response_mapping`
  and `rotate_mapping_by_list` set the key that answers each condition and
  rotate the keys across lists.
* `items.generation.exclude` lists word forms a generated pseudoword must not
  equal, from files or fetched corpora, and `generate_pseudowords()` and
  `build_lexdec_stimuli()` take them as `exclude`. The datasheet records each
  list with its checksum.
* `exclude_words` lists words a design leaves out of its candidates, inline or
  in a file, and the datasheet records the list with its checksum.
* `en_v2.csv`, a screened English lexicon in the repository, marks the forms
  absent from SUBTLEX-US or seldom written in lower case (Brysbaert & New, 2009)
  and counts N and OLD20 over the unmarked forms, keeping the unscreened values
  in `n_density_raw` and `old20_raw`. `pool_filters: {nonstandard: [0, 0]}`
  keeps the unmarked forms.
* The `es_lexdec` example generates a Spanish lexical decision and checks its
  pseudowords against wordfreq's Spanish word list.
* In the schema, `triggers.mode: hardware` stops an experiment whose trigger
  device cannot be opened, and `triggers.mode: mock` prints the codes without
  trying it. `triggers.backend: serial` sends each code as one byte to
  `triggers.serial_port` at `triggers.baudrate`, 115200 by default.
* A design can use a derived dimension (`n_density`, `old20` or `bigram_freq`)
  in `define_by`, `pool_filters`, `counterbalance.balance_on` or a continuous
  design's predictor or controls, and `run_pipeline()` computes any the lexicon
  lacks.
* A lexicon or pool may mark the forms that make up the neighbourhood reference
  with a `reference_member` column of 0 and 1.
* The PsychoPy script takes `--participant`, `--version` or `--list`, and the
  jsPsych page reads `?participant=`, `?version=` or `?list=` from its address.
  Both refuse a list when the versions span several replicates.

## Minor improvements

* When no schema is named and none is found where 0.1.1 looked, `run_pipeline()`
  tries a `schema.yaml` beside the design and `run_all()` tries
  `config/schema.yaml` in the working directory. Both then fall back to the
  schema bundled with the package, where they stopped.
* `run_pipeline()` refuses a missing `name` or `language`, an unsafe name or
  font, a bad trigger address or response key and a repeated condition name
  before anything is written, where these failed later, some at export after
  four files had been written.
* `assign_triggers()` gains `events` and `schema`, which `export_experiments()`
  passes so that item codes avoid the design's other codes.
* `build_datasheet()` gains `counterbalance_check`, `input_normalisation`,
  `generation_exclude`, `exclusions`, `zipf_derivation` and `trial_order`, which
  `run_pipeline()` passes for the format 1.2 fields.
* `match_report()` gains `roles`, a function giving each comparison's role,
  which `run_pipeline()` derives from the design, and
  `match_report_continuous()` gains `audit`, the selector's record of the
  control windows, which it reads from the stimuli by default.
* `match_stimuli()` and `select_continuous_stimuli()` refuse
  `n_per_condition: 0` as not a positive whole number, where they failed with an
  unrelated error.
* `optimal` matching runs much faster on large pools.
* `fetch_corpus()` refusals name the registry they read and say when an entry
  registers no download address. It explains that the Python package builds a
  wordfreq lexicon, where it said the language was not in the registry.
* A norms entry that is not a mapping, such as a bare file name, is refused as
  needing a `path`, where it failed with R's own error.
* The Shiny method selector carries the Streamlit app's note on `mahalanobis`
  and `optimal`, and each app removes a run's folder once the next run's results
  or an error replace its results.

## Fixes

* Generated OpenSesame experiments no longer pass stimulus text through
  OpenSesame's variable store, which evaluates it, so a shared item table can no
  longer run code on the presenting machine.
* The jsPsych page loads jsPsych, its keyboard plugin and its stylesheet from
  unpkg with Subresource Integrity, so a browser refuses a modified copy.
* A resampled design with filler trials runs, where it stopped with an error.
* Generated OpenSesame experiments run with words such as 'nan' and 'infinity'
  in the stimuli, where these could stop an OpenSesame 4 session.
* A factorial design with a key whose name begins with another key's, such as
  `continuous_notes`, runs, where it stopped.
* Joint matching over more than 1,200 candidates on a dimension with missing
  values no longer fails.
* `list_corpora()` and `fetch_corpus()` read the bundled registry under the C
  locale, where they failed.
* Both apps leave out a factor whose bound is not a number, where they stopped
  with an error.
* Both apps' exported command lines quote the design file's name and run in
  `cmd.exe` and Windows PowerShell.
* The Streamlit app's exported R line passes the `outdir` that `run_pipeline()`
  requires.
* lexsync installs the licence notice for its CC BY-SA lexica as `COPYRIGHTS`,
  so binary installations carry it.

## Deprecated

* A design or schema key lexsync does not read is noted in the run log and will
  be refused in a later release. Annotations belong in `description` or a key
  beginning `x_`.

## Documentation

* The experiments vignette is substantially extended, with new sections on when
  a response is collected, instructions and the response mapping, trial orders,
  running a counterbalanced experiment and checking the timing with a
  photodiode. The matching vignette adds a section on choosing and screening a
  lexicon, which says that the wordfreq lexica hold names, acronyms and other
  non-standard forms, and covers ties between equally close candidates. The
  reproducibility vignette sets out the CSV and YAML input contracts and the
  file names.
* The experiments vignette says that every participant given a list and trial
  order meets the practice trials in one fixed order, where it said that the
  practice trials were shuffled so that participants meet them in different
  orders.
* The documentation says that a continuous design spreads its items over the
  predictor's ranks, so the selection follows the pool's distribution, and that
  the tolerance windows trim the controls' tails without holding them constant,
  which the matching vignette and the 0.1.0 notes misstated.
* The matching vignette says that a generated pseudoword is a non-word only
  relative to the reference words, so it can be a real word too rare for the
  lexicon, such as crier or pall, where it said it could not be a real word.
* The experiments vignette says that item trigger codes follow the code-point
  order of the set labels, so that, with sets 1 to 20, set 10 is 41 and set 2 is
  51, and that they are decoded through the loop table.
* The schema's comments say that the trigger settings, and the presentation
  settings other than `font`, apply to every design run with the schema, where
  they said that a design could override them.
* The Get started vignette says that the `timing` keys reach every fixation,
  every text event whose `trigger` is `condition` and every blank, but not an
  event with a per-trial `duration` block, where it named only the fixation,
  critical-word and inter-stimulus durations.
* The vignettes say that a pool filter given two numbers is an inclusive range
  whatever the column, that `standardised_euclidean` is the one default matching
  method and that list balancing runs at most `counterbalance.max_passes`
  passes, 500 by default.
* `resample_stimuli()` says that its selections match the other engine's only
  under `standardised_euclidean` and `joint`.
* The documentation calls the 0.5 equivalence bound a convention, where the
  schema and the help page of `tost_equiv()` credited it to Lakens (2017), and
  the quick start in the README and the Get started vignette uses 60 items per
  condition, where it used 15, too few for any varying dimension to pass the
  equivalence test.
* The corpus registry no longer gives the SUBTLEX-US and SUBTLEX-DE log-count
  columns, or a SUBTLEX-CH column that does not exist, as the source of
  `freq_zipf`.
* The app vignette and both apps' tolerance panels give the frequency k of
  González Alonso et al. (2025) as 0.1111111111111111, since 0.111 gives a
  window narrower than a ninth of a standard deviation.

# lexsync 0.1.1

* `assign_triggers()` gains a `conditions` argument that fixes the order of the
  condition codes, and `export_experiments()` gains one that defaults to the
  order of the design's `conditions`. The codes used to follow the order in which
  the conditions first appeared in the counterbalanced trials, so a different
  seed could swap them, and `low_frequency` was 101 in a design that lists
  `high_frequency` first. The pipeline now passes the design's order, followed by
  any other condition in the order the item source lists it, so the first
  condition the design lists is 101. The condition codes of 12 of the 21
  demonstration designs change with it. `assign_triggers()` called without
  `conditions` behaves as before.
* `cohens_d_ci()` uses the large-sample standard error of d,
  `sqrt(1/nx + 1/ny + d^2 / (2 * (nx + ny)))` (Hedges & Olkin, 1985; Borenstein
  et al., 2009). It left out the `d^2` term, which treated the pooled SD as known
  and made the interval on a manipulated dimension far too narrow. In the English
  frequency contrast, d = 5.27 had the interval [5.01, 5.53] and now has
  [4.72, 5.83]. A matched control, whose d is near zero, moves by at most 0.002
  across the 21 demonstration designs, and no d, TOST p-value or verdict changes.
  The comparisons, datasheets and run logs of the designs with a manipulated
  dimension change with it. No stimulus moves.
* `match_report()` documents the direction of its signed statistics. `cohens_d`
  and its interval are the reference (first) condition's mean minus the mean of
  the condition in that row, and `var_ratio` is that condition's variance over
  the reference's.
* New `lexsync_cache_clear()` removes a fetched corpus from the cache, together
  with any partial download of it, or with no argument removes the whole cache.
  It returns the paths it removed, invisibly.
* `lexsync_cache_dir()` only reports the cache's path. It created the directory
  on every call, so asking where the cache was left an empty directory behind.
  `fetch_corpus()` now creates the cache when a download into it starts, once
  the registry entry and its URL have been accepted, so a refused call writes
  nothing. That download begins by deleting any `.part` sidecar in the cache
  that has gone a day without a write. An interrupt or a process that died
  mid-transfer leaves one behind, and no handler removes it. A younger sidecar
  may belong to a download still running in another session, so it is left
  alone. A `dest` of the caller's choosing behaves as before.
* `citation("lexsync")` gives the DOI that CRAN assigned to the package,
  <https://doi.org/10.32614/CRAN.package.lexsync>, with the CRAN page as its
  URL. The 0.1.0 build
  on CRAN predates the DOI and gives the repository's address. The entry names
  CRAN as its publisher, and its text version is the APA reference for software:
  author, year, title, version, "[Computer software]", CRAN and the DOI.
* The tests no longer take another package's sources for the lexsync repository.
  CRAN's Linux hosts check each package beside the unpacked sources of the others,
  and the test holding the bundled templates to the repository's `templates/`
  directory found the unrelated 'templates' package there and failed. A test that
  compares the package with repository files now accepts a root only if it holds
  lexsync's own `DESCRIPTION` under `R_workflow/` and the Python package beside it,
  and skips on CRAN.
* Suggests now asks for testthat 3.1.8, the first release whose
  `local_mocked_bindings()` can replace an imported function, as the corpus
  download tests do with `download.file()`.

# lexsync 0.1.0

* First release: multilingual corpus access, parallel multidimensional matching,
  counterbalancing, item resampling, deterministic pseudoword generation, and
  generation of hardware-timed PsychoPy, OpenSesame and jsPsych experiments. The
  R and Python engines select byte-identical stimuli, and every run ships a
  materials datasheet (provenance, checksums, realised control) and a
  pre-registration template.
* See the top-level `CHANGELOG.md` for the full, cross-language history and the
  planned methodological roadmap.

## Changes made before the release

These notes follow the package through its development up to the release, so
they describe each change against the state it replaced.

* The package now declares `Depends: R (>= 4.0.0)`. `tools::R_user_dir` does not
  exist before 4.0.0, and `round()`'s post-4.0 algorithm shapes artefact bytes, so an
  older R would fail obscurely or write different bytes without complaint.
* The published median goes through the exact reductions. `describe_stimuli()` was
  the one reduction still on `stats::median`, which averages the two middle values
  through `mean()`'s long-double accumulator while the Python engine reduced through
  numpy. Both engines now sort and take the exact middle, with `(a + b) / 2` in plain
  double arithmetic for even n, and regenerating every design moved no byte.
  *Reproducibility and parity* claimed that every reduction shared one
  compensated-summation algorithm,
  which the median never did, and now describes the sort-and-middle rule beside it.
* The dead half of the two-shortest-forms CSV guard now fires. Between 2^49 and
  1e15 two one-decimal strings can round-trip to the same double, and the R check
  derived its digit count from a 15-digit format that never shows a fractional digit
  there, so R accepted values (844424930131968.2 among them) that the Python writer
  refused. R now refuses exactly the same values, and the change only adds refusals.
* A condition without `define_by` selects identically in both engines. This engine
  always fell back to the whole pool. The Python engine crashed with a bare KeyError on
  the same design and now mirrors the fallback, pinned by twin tests.
* A pair design's tolerance-window relaxation reaches the run log and datasheet.
  The continuous-pairs selector's re-expansion dropped the audit in both engines, so a
  relaxed window left no trace outside the console. No shipped pair design relaxes, so
  no committed artefact changed.
* `INTER_TRIGGER_S` is substituted through `%.17g` like its neighbours in the
  generated PsychoPy script. It used `as.character()`, whose rendering of a
  non-integer quotient differs from Python's `str()`. The shipped default still renders
  "0.01", so no committed experiment byte moved.
* The counterbalancing hash keys convert to UTF-8 before hashing, as `hash_unit()`
  always has, so a latin1-marked condition read from a user's CSV can no longer rank by
  different digests in the two engines.
* The command-line wrapper reports which copy of the package it loaded.
  `R_workflow/run_pipeline.R` prefers an installed lexsync over the edited sources, so
  edits silently did nothing until a reinstall. It now states the loaded copy and the
  remedy on stderr at startup.
* The Shiny app writes its design YAML with LF endings through a binary connection
  (the datasheet hashes that file into `design_sha256`, which must not depend on the
  operating system), and its parity caption now matches the keyed-hash guarantee: the
  engines produce byte-identical stimuli and trial order, where the caption used to
  promise only the stimuli. The
  Python engine's twin fixes land in the same release: its writer refuses 16-digit
  integer columns as this engine always has, its scalar rounder passes an overflowing
  scale through, and `run_pipeline(verbose = FALSE)` keeps its console silent.
* A selection that cannot honour `n_per_condition` is now an error. Every selector
  used to clip the request to the available pool and said so at most
  through a verbose message, while the datasheet and the generated Methods text kept
  stating the requested n. The new `matching: shortfall` policy defaults to `error`,
  and `allow` accepts the shrink. Its sibling `matching: on_insufficient_tolerance` (default
  `relax`) can likewise turn the silent tolerance-window widening into a refusal, and a
  relaxation that does happen is now recorded in the run log and the datasheet
  (`selection.window_relaxations`), where before it was only narrated to the console. No
  committed design experiences either condition.
* `joint` and `optimal` matching can no longer select the same word twice. With
  overlapping condition windows a word could be paired with itself at zero cost, or
  mirrored across two sets, appearing in both conditions. Both matchers now track used
  words as the anchored matcher always has, and every matcher asserts its output holds
  each word at most once. Every committed design has disjoint conditions, and those
  select identically, byte for byte.
* The item-table loader refuses missing cells in both engines. A blank `condition`
  reached Python's hash-key guard as the string "nan" and passed the very check built
  to refuse it, a blank `item` cell turned numeric identifiers into "1.0", and R failed
  on the same table with a bare "missing value where TRUE/FALSE needed". Missingness is
  now checked before any coercion, `item` is read as text, empties after trimming and
  duplicated item-and-condition rows are refused, and both engines say the same thing.
* Cohen's d no longer reports perfect balance for two unequal constant vectors. The
  standardised difference is undefined when the pooled SD is zero and the means differ,
  so it is now reported as missing. The old 0 with CI [0, 0] contradicted the TOST
  verdict on the same row.
* The datasheet's Methods prose follows the recorded verdicts. The claim of being
  "within the 0.5-SD equivalence bound" was printed for any controlled dimension with a
  confidence interval, even where the datasheet's own JSON recorded `equivalent: false`.
  The sentence is now conditional on the stored verdicts, prints the signed worst
  difference and the configurable bound, and the analysis note names the suggested
  formula as `lme4` syntax, where it used to imply that `statsmodels` accepts it. The
  datasheet also gains the SHA-256 of the design and schema, the pairwise matchers'
  candidate cap and whether it fired, the equivalence bound tested against, and the
  `yaml`, `stringi` and operating-system entries the environment record omitted.
* A `continuous` block now works over a supplied pool, and two silent table-mode gaps
  are refusals. `source: pool` reaches the continuous selector (it previously fell
  through to the conditions matcher and crashed). A continuous table without `members`
  is an error now, as is `pool_filters` on a plain table design, where each used to do
  nothing silently while the provenance recorded otherwise. Misspelt `pool_filters` or
  `define_by` columns, duplicate condition names, reversed or non-finite ranges,
  negative tolerances and non-integer n are likewise refusals now.
* Selection-path rounding goes through the shared decimal rule (`.round_dp` and a
  new vectorised numpy twin), replacing a pairing of R's `round()` with numpy's, two
  rounders the project measured to disagree at boundaries. Regenerating all 21 designs
  moved no stimulus, report or experiment byte. A custom norm named in `match_on` now
  also reaches the descriptives, comparisons and realised-control record, which
  previously listed only the built-in dimensions.
* A design file could execute code on the machine that ran it. A design is meant to
  be shared, and the recipient runs it and then opens the generated PsychoPy script,
  OpenSesame experiment or jsPsych page. Stimulus text was always safe: it travels in
  the loop-table CSV the experiment reads at run time. Design *metadata* was not. The
  name, language label, font, parallel-port address and the column names on jitter and
  feedback events were substituted straight into code and markup positions, so a quote
  or an angle bracket there stopped being text and became syntax, and a crafted design
  could run arbitrary code on a lab machine or in the origin of a hosted browser study.
  Both engines now validate these values, under one rule that leaves every legitimate
  value byte-identical. A port address must be an address, a column name must be an
  identifier, and a stated `language_tag` is shape-checked before it is used. Escaping
  them correctly would have taken three rules per engine.
  `.pyq()` escapes newlines now as well: an `.osexp` is line-oriented, so a raw
  newline closed the inline-script block and let the rest of the value start a new
  top-level item. Pinned by `test-injection.R`. No generated artefact changed.
  Adversarially attacking that fix then found four ways through it, all now closed and
  pinned. The largest: a response event's `keys` were joined into OpenSesame's `set
  allowed_responses "a;b"` with no validation at all, and that is one line of a
  line-oriented format, so a key holding a double quote closed the string, a newline
  ended the line, and the rest of the value became new top-level items in the
  experiment, including an `inline_script` whose body OpenSesame runs. Keys are
  validated now. The shape guards were also anchored with `$`, which in both Python's
  `re` and R's PCRE matches just before a final newline, so a port address ending in one
  passed the check. They are anchored at end-of-string now. A scalar `keys: space` or
  `blocks: practice` was iterated character by character in Python and kept whole in R,
  so one design gave two different allowed-response lists and a block-restricted event
  ran everywhere in one engine and nowhere in the other. And R's HTML escape did not
  cover U+2028/U+2029, which end a line in JavaScript but are not ASCII controls: Python
  escaped them, R did not, so the same design produced different bytes and R's
  `<script>` was a syntax error before ES2019.
* A browser experiment could score a feedback screen against the previous trial's
  keypress. The jsPsych feedback screen looked up "the last row marked scoreable",
  which is that trial's response only when the trial has one. An event may be restricted
  to a block, so a design running the response event in one block and feedback in another
  leaves a trial with no response row of its own, and the screen then reported a verdict
  computed from an earlier trial's key. Each trial's rows now carry its own identifier and
  the screen matches on it. The generated HTML changed for all 21 designs. No stimulus
  selection changed.
* A large number in a user's own column was written differently by the two engines.
  `write_csv_utf8()` reproduced readr's format for small magnitudes and left the top end
  alone, since nothing lexsync computes reaches it. Nothing lexsync computes does. A
  joined norm table, a supplied pool or an item table carries whatever columns the user
  has, and those go straight into the stimuli CSV, so the guarantee held for the shipped
  designs and failed silently for the user's own data. readr's layout above 1e15 could not
  be reproduced in Python, which writes 1.5e16 as `15e15`, the largest double as
  `17976931348623157e292`, and the double nearest 5e22 as `4.9999999999999996e+22`. Both
  engines now refuse such a value and name the column. One engine accepting it would
  leave the two writing different bytes. A value with two equally short decimal forms is
  refused for the same reason. Everything verified to render identically, across 465
  values compared against readr's own output, writes as before.
* A generated OpenSesame experiment with a `feedback` event or a `blocks:` restriction
  would not run. The emitter wrote `unicode(...)`, a Python 2 builtin that
  OpenSesame's Python 3 inline workspace does not provide, so the experiment died with
  `NameError` on the first trial. It also passed `None` as a `var.get()` default, which
  OpenSesame cannot distinguish from no default, so it raises where it should return.
  Both are fixed, both spellings are now pinned by a test, and a `feedback` event with
  no preceding `response` or `question` is refused at generation time. Left to run time,
  that one design error would surface as three different failures, one per target.
* Reported statistics are rounded by an arithmetic definition both engines compute
  identically, because no pairing of built-ins agreed. Measured over 210,000 values,
  including every three-decimal halfway case in range, R's `round()` disagrees with
  Python's builtin, Python's builtin disagrees with numpy's, and even R's
  `sprintf("%.3f")` disagrees with Python's `"%.3f"` on 274 of them. Some values move by
  one in the last published digit. No selection changes.
* A hash-key component that cannot be rendered identically in both engines is now
  refused rather than hashed. A blank `condition` cell, a routine data error neither
  reader rejects, rendered `"NA"` in R and `"nan"` in Python, so the two engines
  produced different trial orders from the same design, reproducibly and with nothing to
  signal it. Booleans get a pinned spelling and are still accepted.
* The overlap-cap centroid in the `joint` and `optimal` matchers goes through the
  compensated reduction. The cap does fire on shipped designs, so it decides which
  candidates reach matching. It was verified to change no design's selection.
* `R CMD check --as-cran` is clean: 0 errors, 0 warnings, 1 note (the standard
  new-submission note). Fixed on the way: three undocumented arguments on
  `select_continuous_stimuli()`, an unqualified `utils::head()`, and the package's only
  example, which called an unexported function from inside `\dontrun{}` and so could
  never have worked if a user copied it. The package now has executable, offline
  examples, and `cran-comments.md` no longer misstates the check result.
* Three factual corrections. The SUBTLEX-PT registry entry cited a DOI that resolves to
  an unrelated psychometrics paper. The matching vignette put Zipf 7 at a thousand
  occurrences per million where the correct figure is ten thousand, contradicting its
  own lower anchor.
  A design comment attributed "840-prime materials" to Rastle et al. (2004), a figure
  that appears nowhere in that paper.
* A design may declare `practice:` and `fillers:` item tables. Those trials are
  presented but not analysed, so the stimuli file and the
  reports are written from the main rows while the generated experiments run every
  trial. Practice comes first. Fillers are interleaved with the main trials, because a
  block of fillers at the end is not a filler but a second block a participant can tell
  apart. A design declaring neither is unaffected, down to not gaining a `block` column.
* A `feedback` trial event, and a `blocks:` key that restricts any event to named
  blocks. Together these confine feedback to practice, which is the usual arrangement:
  feedback teaches the mapping, and would contaminate the reaction times it is
  measuring. Implemented for PsychoPy, OpenSesame and jsPsych alike. The
  PsychoPy runner now returns the pressed key so it can be scored, and each runner pauses
  at a block boundary.
* The Python engine embedded a bare `NaN` in the generated jsPsych experiment where a
  trial had no value for a field another block supplies (a main-block trial in a design
  whose practice items carry an `answer`). That is not valid JSON, and the R engine
  dropped the key instead, so the two engines' experiments differed. Both now drop it.
* The generated artefacts were not byte-identical across the engines, and the parity
  test could not see it. It read both CSVs back with a parser and compared the values,
  under which `1` and `1.0` are the same number. Thirteen of the 18 shipped designs differed
  byte for byte while the gate stayed green. Three differences were serialisation (a
  whole number written `1` and `1.0`, a boolean written `FALSE` and `False`, a small
  value written `9e-4` and `0.0009`) and one was not: two reported means differed in the
  last decimal published, because numpy sums pairwise and R's `mean()` does not. Every
  reduction in the package now uses one compensated-summation algorithm written out in
  both engines, whose agreement follows from IEEE-754 and no longer from measurement.
  The writers agree on every value, and the artefacts are now compared as bytes. No R
  golden moved, because R's two-pass mean was already the correctly-rounded one.
* A response key coded `f` was silently turned into `FALSE`. `readr` reads a column
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
  equated on the declared dimensions, where the old deal went by set rank. The search is
  a deterministic integer descent with a keyed-hash tie-break, so it uses no random
  number generator and both engines produce the same assignment. `balance_lists()` is
  exported.
* New item source `pool`: a supplied word list goes through the matcher without having
  to masquerade as a corpus lexicon. `load_pool()` is exported. The neighbourhood
  dimensions are computed against the lexicon's words, because a word's neighbours are
  its neighbours in the language.
* A design may name norm tables in a `norms:` block. They are joined onto the
  lexicon before the candidate pool is built, so a semantic dimension the corpus
  does not carry (concreteness, age of acquisition, valence) can be filtered on,
  matched on or spanned like any other. No norm data is bundled. Every joined table
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
  join key is now case- and whitespace-folded on the lexicon's side too, where only
  the norm table's was folded before: a lexicon holding `Dog` used to match nothing and
  leave an all-`NA` dimension. A norm column whose name already exists on the lexicon
  is now an error. Renaming it to `frequency.x` / `frequency.y`, as `merge()` did, left
  the matched dimension under a name nothing looks for.
* `write_datasheet()` and `write_run_log()` now write LF on every platform. They
  used a text-mode connection, so on Windows the datasheet, its Markdown rendering
  and the Markdown run log came out CRLF while the Python engine's twins were LF.
  The datasheet is the provenance record. Its bytes no longer depend on the machine
  that built it.
* `add_pair_overlap()` and `resolve_trial_timing()` are now exported in fact as well as
  in the documentation. Both were marked for export and documented, but the `NAMESPACE`
  had not been regenerated, so `library(lexsync)` did not make them available.
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
  Byte-identical across engines, and the default letter-substitution generator is
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
  `n_per_condition`, now raise an actionable error. Each used to fall back silently,
  to a default method or to a short set. The Python engine raises the
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
* Datasheets record the tolerance windows and pseudoword generator that ran, filter
  dimensions as the Python engine does, and report the installed package version they
  were built by.
* `match_stimuli()` raises where it used to re-pick an already-used row, when a
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
* Every vignette now turns console colour off and fixes the console width while it
  renders. pkgdown passes the calling terminal's colour support into its build
  subprocess, so a coloured message or error would otherwise reach the reader as
  escape sequences in the middle of the text.
