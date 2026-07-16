# Reproducibility and parity

Most stimulus sets are described rather than shared. A paper says the words were matched on length
and frequency, gives two tables of means, and the set itself either never appears or appears as a
spreadsheet with no account of where it came from. lexsync is built the other way round: the design
is a file, the selection is a function of that file, and the run emits the provenance record that
lets someone else arrive at the same words.

This guide sets out what the cross-engine guarantee actually promises, the specific engineering that
makes it hold, where it stops, how it is tested, and what a run writes down about itself.

## The guarantee

For the deterministic matching methods, the R and Python engines select byte-identical stimuli from
identical input. Not statistically equivalent sets, not sets that agree to several decimal places.
The same words, paired the same way, assigned to the same conditions.

That is a stronger claim than it may look, because the two engines share no code. They are separate
implementations, in different languages, on different linear-algebra stacks, and each is a package
in its own right. What they share is a specification: the same schema, the same design file, the
same algorithm, and the same rules about what to do at every point where an implementation could
legitimately choose either of two answers.

## What makes it hold

The guarantee is not a property that the code happens to have. It is a set of decisions, most of
which cost something, and each of which closes off a way for the two engines to drift apart.

There is no random number generator in the selection path. Not a seeded one, none at all. Wherever a
naive implementation would sample, lexsync spreads evenly. The matcher's anchor is an even spread
across the sorted subpool, the continuous selector is two even spreads, and `build_lexdec_stimuli`
draws its real words the same way. A seeded generator would be reproducible within an engine, but
R's and NumPy's differ, so it would not cross the gap.

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

Missing values are ranked last, explicitly. A relaxed tolerance window can readmit a row whose
matched dimension is missing, and its distance is then NaN. A bare `min()` over NaN keeps whichever
row it happened to see first, which makes the selection depend on pool row order. The matcher sorts
NaN last, as R's `order(na.last = TRUE)` does.

Text is read the same way by both engines. pandas treats `null`, `nan`, `none` and `true` as missing
by default, which would silently drop those real English words and leave the two engines with
different lexica, so `read_csv_utf8` sets `keep_default_na=False` and recognises only `""` and `NA`,
matching readr's default. `load_lexicon` also drops missing words before coercing types: `astype(str)`
renders a missing word as the literal string `"nan"`, which survives every guard downstream, while
R's `as.character(NA)` stays `NA` and drops the row. One extra row shifts every id after it.

Text is written the same way too. pandas defaults its line terminator to `os.linesep`, so the same
selection would carry a different SHA-256 on Windows than on Linux. The datasheet advertises those
digests as provenance, so they must depend on the content alone, and `write_csv_utf8` pins LF. Paths
in the datasheet are recorded in POSIX form for the same reason. A record meant to travel should not
describe the machine that happened to build it.

Derived quantities are computed from integers. Bigram probabilities come from integer counts and are
rounded, and the subsyllabic constituent inventory is integer counts keyed by role and length, so it
is order-independent. Neither depends on the order in which the corpus was accumulated.

The generated PsychoPy script and OpenSesame experiment are byte-identical as well. The place they
could drift is the event JSON embedded in the script, since jsonlite pads no separators and drops a
whole number's fractional part, serialising a 2000 ms timeout as `2` rather than `2.0`; Python is
the side that conforms. The trial lists are the exception. The loop tables, and the `TRIALS` array
the browser experiment embeds, carry the counterbalanced order, which each engine draws from its own
generator, so those files differ. The section below says why.

Some of these are visible in the design surface, and deliberately so. The tie-break order in the
matcher is fixed at distance, then word bytes, then id, and is not configurable, because it is
precisely what makes the two engines agree without an RNG. Making it an option would make the
guarantee an option.

## Where it stops

Three exceptions, all of them documented rather than incidental.

`mahalanobis` and `optimal` are not covered. The first inverts a covariance matrix and the second
solves a linear-assignment problem, and those are the two places where the R and Python
linear-algebra backends differ in their last bits, with the assignment solver's tie handling
differing outright. The engines agree closely. In practice `mahalanobis` usually still agrees
exactly, while `optimal` tends to select an equally optimal but different set, which is a
reasonable thing for an optimal matcher to do when several assignments share the minimum. Neither is
guaranteed byte-for-byte, and each run's datasheet records which case applies.

This is why neither is the default, despite both being defensible improvements on it. The roadmap
says as much: a covariance-aware distance is promoted to the default only if a determinism-safe
implementation is found. The guarantee is a hard constraint on which algorithms can be adopted, not
a nice property that the current defaults happen to have.

Trial order is not covered. It comes from each engine's own seeded generator, so it is reproducible
within an engine, given `schema.seed`, and not across the two. The parity contract covers which
items were selected, how they were paired and how they were assigned to conditions and lists.

Corpus versions are not magic. A design pins the lexicon file it reads, and the bundled corpora are
a fixed, checksummed snapshot, so the demonstrations reproduce with no download. The optional
wordfreq connector is pinned to its frozen 3.x line, a stable snapshot of usage through roughly
2021, which keeps a fetched lexicon reproducible instead of drifting under a live source.
Fetch a corpus from a URL that changes and lexsync cannot help you; the datasheet's SHA-256 of the
source file will at least tell you that it changed.

## How it is tested

The claim is checked rather than asserted. `tests/test_parity.py` carries fifteen cases, one per
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
agree too. `trial` is excluded, being outside the contract.

Continuous integration closes the loopholes that would let this pass without meaning anything.
`LEXSYNC_REQUIRE_PARITY=1` turns the graceful skip into a failure, so a job meant to run both
engines cannot pass by quietly skipping. `git diff --exit-code -- output/stimuli/` runs before the
parity suite, because otherwise the gate would only ever compare Python against a reference that
Python itself had just rewritten. And `git diff --exit-code -- output/experiments/` runs after,
since the Python engine has by then rewritten that directory, and the diff against the
R-generated files committed there is the only thing standing between a cross-engine divergence in
the generated scripts and a green tick.

The rest of the suite covers the parts hardware would otherwise gate: a mock-PsychoPy harness that
runs the generated script and asserts the onset trigger is flip-locked, a structural validator for
the generated OpenSesame experiment, and checks that the jsPsych export is well formed and escapes
HTML in stimulus data. The R package runs `R CMD check` on Ubuntu, macOS and Windows, and the Python
tests run on Python 3.10 to 3.13.

## The materials datasheet

Every run writes a datasheet, in JSON for machines and Markdown for people. It is the record that
travels with a set, and it exists because the reproducibility literature keeps asking for one
(Bochynska et al., 2023; Roettger, 2019).

```python
paths = lexsync.run_pipeline("config/design_en_freqcontrast.yaml")
# output/reports/en_freqcontrast_english_datasheet_py.json
# output/reports/en_freqcontrast_english_datasheet_py.md
```

The JSON carries `design`, `materials_source`, `selection`, `dimensions`, `items`,
`counterbalancing`, `realised_control`, `resampling`, `analysis`, `artifacts` and `reproducibility`,
plus a `lexsync_datasheet_version` marker so a reader knows which format it is looking at. The
Markdown renders the same content as prose and tables. From the committed datasheet for the English
frequency contrast:

```text
## Provenance

- **Paradigm:** factorial  |  **Item source:** corpus
- **Materials source:** `corpora/derived/en.csv` (sha256 `c20549b920d81680…`)
- **Selection:** standardised_euclidean
- **Cross-engine determinism:** byte-identical
- **Counterbalancing:** factorial, 1 list(s)
- **Items:** 160 rows across 2 conditions (low_frequency, high_frequency)
- **Seed:** 2026  |  **Versions:** engine python, lexsync 0.1.0, python 3.13.7, pandas 2.3.2, numpy 2.3.2, scipy 1.17.1
```

Four things in there are worth pointing at.

`Cross-engine determinism` is the caveat from the previous section, recorded per run rather than
left in prose. A design that uses `mahalanobis` or `optimal` says so here, so whoever receives the
materials learns it from the materials.

Selection transparency records how many items satisfied each condition's window before matching. For
this design the answer is 544 high-frequency candidates and 4295 low-frequency ones. That number is
the size of the discretionary pool the selection drew from, and reporting it makes item-selection
bias auditable (Forster, 2000; Simmons et al., 2011). A set of 80 chosen from 544 is
a different object from a set of 80 chosen from 85.

The realised control is a table, not a claim, giving each dimension its role, Cohen's *d*, the 90%
interval, the variance ratio, the TOST *p* and the verdict. The suggested analysis is a crossed
mixed-model formula, `response ~ condition + (1 + condition | subject) + (1 | item)`, which is there
to guard against the language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008): items are
a sample of the language, and an analysis that treats them as fixed over-generalises. The maximal
structure is suggested (Barr et al., 2013) with the advice to reduce it if it does not converge
(Matuschek et al., 2017).

`methods_paragraph` turns the datasheet into prose you can paste into a Methods section, filled from
the numbers above. The pipeline writes it into the Markdown datasheet, and you can call it on a
datasheet dictionary yourself with `lexsync.methods_paragraph(ds)`. For this design it reads:

> 80 items per condition were selected from the English lexicon (see corpora/ATTRIBUTION.md for
> corpus licence and citation) and matched item by item on length, n_density, old20 using lexsync's
> standardised_euclidean matcher. The realised control was close. The largest standardised
> difference on any matched dimension was 0.04 (90% CI [-0.22, 0.30]), within the 0.5-SD equivalence
> bound. The smallest condition was selected from 544 eligible candidates, and the selection was
> deterministic and blind to any outcome measure.

The Markdown datasheet also carries a pre-registration skeleton with its Materials section already
filled from the run and its analysis plan filled with the suggested model. The remaining sections
are yours to complete before data collection.

`build_datasheet` and `write_datasheet` are available if you are assembling a datasheet outside the
pipeline, though `run_pipeline` calls them for you.

## The run log

Alongside the datasheet, each run writes a log in Markdown and JSON Lines, with a timestamped entry
per stage: which lexicon was loaded and how many words it held, the pool size after filtering, which
dimensions were derived, how many items were matched, the equivalence verdict on each dimension, and
every artefact written with its row count and MD5.

```python
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
