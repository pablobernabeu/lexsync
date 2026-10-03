# Reproducibility and parity

Most stimulus sets are described rather than shared. A paper says the words were matched on length
and frequency, gives two tables of means, and the set itself either never appears or appears as a
spreadsheet with no account of where it came from. lexsync is built the other way round: the design
is a file, the selection is a function of that file, and the run emits the provenance record that
lets someone else arrive at the same words.

This guide sets out what the cross-engine guarantee promises, the specific engineering that makes
it hold, where it stops, how it is tested, and what a run writes down about itself.

## The guarantee

For the deterministic matching methods, the R and Python engines produce byte-identical output from
identical input, and the guarantee has three layers. The selection: the same words, paired the same
way, assigned to the same conditions and lists. The computed dimensions: every value an engine
derives at run time and writes into the stimuli CSV. And the full generated experiment: the
PsychoPy script, the OpenSesame experiment, the jsPsych page and the three tables the first two
read, trial order included. Not statistically equivalent sets, not files that agree to several
decimal places. The same bytes.

That is a stronger claim than it may look, because the two engines share no code. They are separate
implementations, in different languages, on different linear-algebra stacks, and each is a package
in its own right. What they share is a specification: the same schema, the same design file, the
same algorithm, and the same rules about what to do at every point where an implementation could
legitimately choose either of two answers.

## What makes it hold

The guarantee is not a property that the code happens to have. It is a set of decisions, most of
which cost something, and each of which closes off a way for the two engines to drift apart.

There is no random number generator anywhere in the package. Not a seeded one, none at all.
Wherever a naive implementation would sample, lexsync spreads evenly or hashes. The matcher's
anchor is an even spread across the sorted subpool, the continuous selector is two even spreads,
`build_lexdec_stimuli` draws its real words the same way, and trial order is a keyed hash of the
design, described below. A seeded generator would be reproducible within an engine, but R's and
NumPy's differ, so it would not cross the gap.

Every ordering is by UTF-8 bytes. The lexicon is sorted that way at load time, item tables are
mapped to set ids that way, pseudoword base words are processed that way, and the matcher's
tie-break is the word's bytes and then its lexicon id. Locale-collated sorting would put a German
laptop and an English continuous-integration runner in disagreement about which of two words comes
first, and one flipped tie-break at the top of a pool cascades through everything after it.

Distances are rounded to nine decimal places before they are compared: in the matcher, in the
`joint` cost matrix, in the overlap cap and in the continuous selector's Pearson correlations. Two
engines can compute the same distance and differ in the last bit, and if that bit decides a
comparison then a stable tie-break is not stable at all. Rounding first is what makes the tie-break
mean anything.

Missing values are kept out of the comparisons. A candidate missing a matched dimension, or in a
continuous design the predictor or a control, has no distance to rank. A bare `min()` over NaN keeps
whichever row it happened to see first, which makes the selection depend on pool row order. Both
engines therefore exclude such candidates before selecting, and the matcher still sorts a NaN
distance last, as R's `order(na.last = TRUE)` does.

CSV input is read by one rule in both engines. Each engine reads every cell as text and converts it
itself, because pandas and readr guess types by different heuristics. Header names and cells are
trimmed of spaces, tabs, carriage returns and line feeds. After trimming, an empty cell and `NA`
(quoted or not) are missing. Every other word is a value, `null`, `nan`, `none` and `true`
included, which pandas would otherwise have dropped as missing. A column is numeric only when every
value is a plain decimal number (an optional sign, digits, an optional point and exponent, and no
thousands separators). It is logical only when every value is TRUE or FALSE in upper, lower or
title case, so `T` and `F` stay text. Any other column is text, a date included. The columns a
paradigm presents, and an item table's `item` and `condition`, are always text. A header that names
a column twice is refused, and an empty header cell is named by its position (`...3`). Python
parses a number with `float()`, which returns the nearest double. readr's parser and R's
`as.numeric()` can each miss that double by one unit in the last place. For a number of up to 15
significant digits, with a power of ten within 10^22, R therefore multiplies or divides one exact
integer by one exact power of ten. That single operation is correctly rounded and gives Python's
double. Any other number goes through `as.numeric()`. It misses far less often than readr's
parser, but the engines may then differ in its last bit. A negative zero is read as zero, since the
two engines would otherwise write it as `-0` and `0`.

`load_lexicon` drops missing words before coercing types: `astype(str)` renders a missing word as
the literal string `"nan"`, which survives every guard downstream, while R's `as.character(NA)`
stays `NA` and drops the row. One extra row shifts every id after it.

Text is written the same way too. pandas defaults its line terminator to `os.linesep`, so the same
selection would carry a different SHA-256 on Windows than on Linux. The datasheet advertises those
digests as provenance, so they must depend on the content alone, and `write_csv_utf8` pins LF. Paths
in the datasheet are recorded in POSIX form for the same reason. A record meant to travel should not
describe the machine that happened to build it.

Derived quantities are computed from integers. Bigram probabilities come from integer counts and are
rounded, and the subsyllabic constituent inventory is integer counts keyed by role and length, so it
is order-independent. Neither depends on the order in which the corpus was accumulated.

The generated experiments are byte-identical as well, all of them: the PsychoPy script, the
OpenSesame experiment, the jsPsych page and the three tables the first two read, 126 files across
the 21 worked designs. One place they could drift is the event JSON embedded in the PsychoPy script, since
jsonlite pads no separators and drops a whole number's fractional part, serialising a 2000 ms
timeout as `2` rather than `2.0`. Python is the side that conforms.

The other place is trial order, which until recently was the one artefact the engines could not
share. Each shuffled with its own seeded generator, R with `sample()` and Python with NumPy's
PCG64, and the same seed could not give the same permutation, so the loop tables, and the `TRIALS`
array the browser experiment embeds, used to differ. Both engines now order the trials of a list by
a keyed hash instead: each row is ranked by the SHA-256 digest of
`seed|replicate|list|set|condition`, a tuple that identifies the trial uniquely under either
counterbalancing recipe. Distinct inputs to SHA-256 behave as independent uniform draws, so
ordering by the digest realises a seeded random permutation, but as a pure function of the design.
The same bytes come out of both engines on any platform, there is no generator state to save or
restore, a different seed still gives a different order, and the order remains random in the sense
a reviewer cares about, with no systematic position effects.

Some of these are visible in the design surface, and deliberately so. The tie-break order in the
matcher is fixed at distance, then word bytes, then id, and is not configurable, because it is
precisely what makes the two engines agree without an RNG. Making it an option would make the
guarantee an option.

## The Unicode input contract

Word matching, deduplication and the `length` dimension operate on Unicode code points, and every
text key is normalised to Unicode Normalization Form C (NFC). The words of a lexicon or a supplied
pool and both sides of a norm-table or pair-member join are first trimmed and lower-cased. The item
id, condition and presented fields of an item table, practice and filler tables included, and a
supplied reference list are normalised as read. A precomposed character such as é and its
decomposed counterpart, the base letter followed by a combining accent, are therefore one
character, and a lexicon that mixes the two conventions holds each word once, in the first row the
file gives it. Before this, the two spellings were two words of different lengths, and the
matcher could place them in opposite conditions of one matched set. When normalisation rewrites or
merges anything, the run log says how many forms it rewrote and how many duplicates it removed, and
the datasheet records the two counts as `materials_source.input_normalisation`. Input already in
NFC, the form most corpora distribute, leaves no trace.

Unicode's stability policy fixes the NFC form of every assigned character, so the two engines can
disagree only on a character that one engine's Unicode version assigns and the other's lacks.
Python's `unicodedata` follows the interpreter (Unicode 15.1 in Python 3.13), while R's stringi
uses the ICU it bundles or, on some Linux builds, the system's ICU, which may implement another
version.

The syllable estimator and the pseudoword generators carry a narrower contract still. The vowel
class behind `n_syllables` covers the Latin-1 vowels, and the pseudoword generators build their
candidates from lower-case a to z, so both are orthographic approximations defined for Latin
orthographies and unavailable for other scripts. The shipped Chinese design matches on `length`,
`n_density` and `old20` for exactly this reason.

## File names

Every file a run writes is named after a stem built from the design's `name` and `language`, which
`design_stem` computes in both engines. The stem keeps ASCII letters and digits only, so names that
differ only outside ASCII would share it, and two designs named 词频 and 笔画, both in `chinese`,
would write the same files, the second overwriting the first. Whenever the name or the language
holds a non-ASCII character, the stem therefore ends in an underscore and the first eight
hexadecimal digits of the SHA-256 of the NFC-normalised text `name|language`. The two designs
above write `chinese_14aadfa7` and `chinese_444a1c5f`. A name and language with no ASCII letter or
digit at all, which used to give file names beginning with an underscore or a dot, get the eight
digits alone, such as `e525cb84`. Normalising to NFC here keeps a precomposed and a decomposed
spelling of one name on one stem. Names in plain ASCII are unaffected. `run_all` also computes every design's stem before it runs any, and refuses two
designs that would write the same files, such as `en-lexdec` and `en_lexdec`.

## Where it stops

Two exceptions, and both are documented here.

`mahalanobis` and `optimal` are not covered. The first inverts a covariance matrix and the second
solves a linear-assignment problem, and those are the two places where the R and Python
linear-algebra backends differ in their last bits, with the assignment solver's tie handling
differing outright. The engines agree closely. `mahalanobis` usually still agrees exactly,
while `optimal` tends to select an equally optimal but different set, which is a
reasonable thing for an optimal matcher to do when several assignments share the minimum. Neither is
guaranteed byte-for-byte, and each run's datasheet records which case applies.

This is why neither is the default, despite both being defensible improvements on it. The roadmap
says as much: a covariance-aware distance is promoted to the default only if a determinism-safe
implementation is found. The guarantee is a hard constraint on which algorithms can be adopted, not
a nice property that the current defaults happen to have.

One further place is worth naming, though it is not an exception. Almost everything on the path to
a compared artefact is built from operations IEEE-754 either mandates correctly rounded or makes
exact, so the engines agree by construction rather than by measurement. The Student t quantile and
distribution behind the confidence interval and the TOST *p*-value are where that argument does
not reach: `scipy.stats.t` on one side, R's `qt` and `pt` on the other, two independent
implementations that were measured to disagree by up to about 1e-12 over the range these reports
use. The published values are rounded to three and four decimal places, which leaves 5e-4 and 5e-5
of headroom, so the comparisons files still come out byte-identical. The guarantee there rests on a
margin of some seven orders of magnitude rather than on the construction, and saying so is what
stops anyone widening the reported precision without checking the margin first.

Trial order is no longer on this list. Earlier versions drew it from each engine's own seeded
generator, reproducible within an engine, given `schema.seed`, and never across the two. The
keyed-hash shuffle retired that exception: the permutation is part of the byte-identical surface,
and the parity suite compares the `trial` column along with everything else.

Corpus versions are not magic. A design pins the lexicon file it reads, and the bundled corpora are
a fixed, checksummed snapshot, so the demonstrations reproduce with no download. The optional
wordfreq connector is pinned to its frozen 3.x line, a stable snapshot of usage through roughly
2021, which keeps a fetched lexicon reproducible where a live source would let it drift. Fetch a
corpus from a URL that changes and lexsync cannot help you. The datasheet's SHA-256 of the
source file will at least tell you that it changed.

## How it is tested

The claim is checked, not merely stated. `tests/test_parity.py` carries 21 cases, one per
worked design, spanning English, Spanish and Mandarin Chinese and covering every item source and
every paradigm: frequency and neighbourhood contrasts, lexical decision under both pseudoword
generators, the continuous design, resampling, priming, self-paced reading and three reproductions
of published designs.

Each case regenerates the Python selection and compares it against the committed R reference in
`output/stimuli/<base>_stimuli_R.csv`. The comparison is exact and it has two parts. The identity
columns, which are `word` or `target`, `condition` and `set`, must match as a set of rows. `set` is
in there deliberately: it records which item was matched to which, and without it the test would
place no constraint on the pairing at all. Then every other shared column is compared value by
value, because the dimensions each engine computes at run time end up in the stimuli CSV and must
agree too. `trial` is among them, now that the keyed-hash shuffle has brought order inside the
contract.

Continuous integration closes the loopholes that would let this pass without meaning anything.
`LEXSYNC_REQUIRE_PARITY=1` turns the graceful skip into a failure, so a job meant to run both
engines cannot pass by quietly skipping. `git diff --exit-code -- output/stimuli/` runs before the
parity suite, because otherwise the gate would only ever compare Python against a reference that
Python itself had just rewritten. And a final step runs each engine over every design into a
directory of its own and compares the two trees with `diff -r`, because both engines write the
generated experiments to the same paths, so a diff against the committed tree would only ever
compare the last engine to run against itself. Only the two per-engine provenance records, the
datasheet and the run log, are excluded from that comparison. It is the step standing between a
cross-engine divergence in any generated artefact and a green tick.

The shipped designs have clean inputs: every cell is in NFC, none is padded and the norms cover
every word. The gate above therefore never reaches the code that padded fields, missing values or
unusual YAML would take, and a defect both engines share would pass it, since they agree. The
twin-edge cases cover that ground. Each is a folder under `parity/twin_edge/` at the repository
root, holding a small `design.yaml`, its inputs (paths relative to the folder), an optional
`schema.yaml` and an `expect.yaml` that pins the outcome. An artefacts case keeps the files the
design must produce, byte for byte, in `expected/`, and may assert values in the datasheet. A
refusal case gives a substring of the error the design must raise. `tests/test_twin_edge.py` and
the R suite's `test-twin-edge.R` each hold their own engine to every case, and CI also runs
`tools/compare_engines.py --config parity/twin_edge`, which compares the two engines on the same
cases. Run without arguments, `python tools/compare_engines.py` repeats the whole-tree comparison
on your own machine, Windows included. It finds Rscript on the `PATH` or through
`LEXSYNC_RSCRIPT`. To add a case, create its folder with `design.yaml` and `expect.yaml` and write
`expected/` with `python tools/twin_edge.py --update <case>`. Read the pinned files to confirm they
are right, then run the R suite, which checks that the R engine writes the same bytes. A fix for an
input defect adds its case in the same commit, so the gate never lands red.

The rest of the suite covers the parts hardware would otherwise gate: a mock-PsychoPy harness that
runs the generated script and asserts the onset trigger is flip-locked, a structural validator for
the generated OpenSesame experiment, and checks that the jsPsych export is well formed and escapes
HTML in stimulus data. The R package runs `R CMD check` on Ubuntu, macOS and Windows, and the Python
tests run on Python 3.10 to 3.14.

## The materials datasheet

Every run writes a datasheet, in JSON for machines and Markdown for people. It is the record that
travels with a set, and it exists because the reproducibility literature keeps asking for one
([Bochynska et al., 2023](references.md#bochynska-2023); [Roettger, 2019](references.md#roettger-2019)).

```python
# illustrative: needs a clone's config directory and writes the run into the working tree
paths = lexsync.run_pipeline("config/design_en_freqcontrast.yaml")
# output/reports/en_freqcontrast_english_datasheet_py.json
# output/reports/en_freqcontrast_english_datasheet_py.md
```

The JSON carries `design`, `materials_source`, `selection`, `dimensions`, `items`,
`counterbalancing`, `realised_control`, `equivalence`, `relational`, `resampling`, `analysis`,
`artifacts` and `reproducibility`, plus a `lexsync_datasheet_version` marker so a reader knows
which format it is looking at. The
Markdown renders the same content as prose and tables. From the committed datasheet for the English
frequency contrast:

```text
## Provenance

- **Paradigm:** factorial  |  **Item source:** corpus
- **Materials source:** `corpora/derived/en.csv` (sha256 `575833489e04d6a4…`)
- **Selection:** standardised_euclidean
- **Cross-engine determinism:** byte-identical
- **Counterbalancing:** factorial, 1 list(s)
- **Items:** 160 rows across 2 conditions (low_frequency, high_frequency)
- **Seed:** 2026  |  **Versions:** engine python, lexsync 0.1.1, python 3.13.7, pandas 2.3.2, numpy 2.3.2, scipy 1.17.1, …
```

Four of those lines repay a second look.

`Cross-engine determinism` is the caveat from the previous section, recorded once per run. A design
that uses `mahalanobis` or `optimal` says so here, so whoever receives the materials learns it from
the materials.

Selection transparency records how many items satisfied each condition's window before matching. For
this design the answer is 544 high-frequency candidates and 4295 low-frequency ones. That number is
the size of the discretionary pool the selection drew from, and reporting it makes item-selection
bias auditable ([Forster, 2000](references.md#forster-2000);
[Simmons et al., 2011](references.md#simmons-2011)). A set of 80 chosen from 544 is a different
object from a set of 80 chosen from 85. A candidate missing a matched dimension satisfies its window
but cannot be matched. The JSON record counts such candidates per condition in
`selection.incomplete_dropped`, and the Methods paragraph leaves them out of its count of eligible
candidates.

The realised control is a table, not a claim, giving each dimension its role, Cohen's *d*, the 90%
interval, the variance ratio, the TOST *p* and the verdict. The JSON keeps each statistic as the
comparisons report rounded it, to three places and the TOST *p* to four. The Markdown and the
Methods paragraph show them at two or three places and the TOST *p* at four. The rounding is done
by lexsync's own formatter, half away from zero from that record, so both engines print the same
digits. A *d* of 0.1649 is stored as 0.165 and is therefore shown as 0.17.

The suggested analysis is a crossed mixed-model formula,
`response ~ condition + (1 + condition | subject) + (1 | item)`, which is there
to guard against the language-as-fixed-effect fallacy ([Clark, 1973](references.md#clark-1973);
[Baayen et al., 2008](references.md#baayen-2008)): items are a sample of the language, and an
analysis that treats them as fixed over-generalises. The maximal structure is suggested
([Barr et al., 2013](references.md#barr-2013)) with the advice to reduce it if it does not converge
([Matuschek et al., 2017](references.md#matuschek-2017)).

The `counterbalancing` record says how the items were dealt to lists. It gives the recipe that ran,
the number of lists in the stimuli table and the trials each list gives each condition. It also says
whether a Latin-square rotation is complete and, if not, what leaves it incomplete. The Markdown
renders the counts as a table, so a claim of a rotation can be checked against them, and the Methods
text calls an incomplete rotation incomplete
([Experiments and triggers](experiments-and-triggers.md#counterbalancing)).

`methods_paragraph` turns the datasheet into prose you can paste into a Methods section, filled from
the numbers above. The pipeline writes it into the Markdown datasheet, and you can call it on a
datasheet dictionary yourself with `lexsync.methods_paragraph(ds)`. For this design it reads:

> 80 items per condition were selected from the English lexicon (wordfreq (Speer, 2022), data
> CC BY-SA 4.0; full corpus licence and citation at
> https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md) and matched item by
> item on length, n_density, old20 using lexsync's standardised_euclidean matcher. The realised
> control was close. The largest standardised difference on any matched dimension was 0.04 (90% CI
> [-0.22, 0.30]), within the 0.5-SD equivalence bound. The smallest condition was selected from 544
> eligible candidates, and the selection was deterministic and blind to any outcome measure. […]

The Markdown datasheet also carries a pre-registration skeleton with its Materials section already
filled from the run and its analysis plan filled with the suggested model. The remaining sections
are yours to complete before data collection.

`build_datasheet` and `write_datasheet` are available if you are assembling a datasheet outside the
pipeline, though `run_pipeline` calls them for you.

## The run log

Alongside the datasheet, each run writes a log in Markdown and JSON Lines, with a timestamped entry
per stage: which lexicon was loaded and how many words it held, the pool size after filtering, which
dimensions were derived, how many items were matched, the equivalence verdict on each dimension, and
every artefact written with its row count and MD5. A design or schema key that lexsync does not read
is noted there too, since it changed nothing about the run.

```python
# illustrative: writes run_log.md and run_log.jsonl into the working tree
from lexsync import logging as runlog

log = runlog.new_run_log("my_design", meta={"seed": 2026})
runlog.log_step(log, "loaded lexicon", {"words": 3000})
runlog.write_run_log(log, "run_log.md", "run_log.jsonl")
```

The Markdown log is for reading afterwards and the JSON Lines log is for anything that needs to
parse it. Between the two of them, plus the datasheet's checksums and the design file, a run is
reconstructible from its own output.

## Reproducing the demonstrations

From a clone, the whole thing is one command:

```bash
python python_workflow/run_pipeline.py     # or: lexsync run
```

This regenerates every worked design into `output/`. Nothing in it needs PsychoPy, OpenSesame, a
parallel-port driver or an internet connection, since the bundled corpora are a checksummed snapshot
and generation writes text. If the regenerated stimuli differ from the committed ones, `git diff`
will say so, which is the same check continuous integration performs.
