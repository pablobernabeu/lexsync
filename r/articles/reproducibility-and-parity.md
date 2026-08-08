# Reproducibility, parity and the materials datasheet

A stimulus set is usually described rather than shared. The methods
section says the words were matched on length and frequency, and the set
itself, the criteria that produced it and the code that applied them are
not recoverable from the paper. `lexsync` treats the set as an artefact
instead of a description: the selection and the trial order are
deterministic, the R and Python engines produce the same artefacts from
the same input, and each run emits a provenance record with the
checksums needed to verify it.

This vignette explains the guarantee and its limits, the mechanisms that
achieve it, the continuous-integration test that keeps it honest, and
the two records a run leaves behind.

``` r

library(lexsync)
schema <- yaml::read_yaml(
  system.file("extdata", "schema.yaml", package = "lexsync")
)
lex <- load_lexicon(
  system.file("extdata", "en_example.csv", package = "lexsync"),
  schema, language = "english"
)
pool <- build_pool(lex, list(length = c(3, 7), frequency = c(3.8, 7.0)))

design <- list(
  name = "vignette_repro", language = "english", n_per_condition = 15,
  conditions = list(
    list(name = "high", define_by = list(frequency = c(5.2, 7.0))),
    list(name = "low",  define_by = list(frequency = c(3.8, 4.4)))
  ),
  match_on = list("length", "n_density", "old20"),
  counterbalance = list(lists = 1)
)
```

## What is guaranteed

The claim is worth stating exactly. Given the same lexicon and the same
design, the R and Python engines produce byte-identical stimuli under
the `standardised_euclidean` and `joint` matching methods, under
continuous selection, and under both pseudoword generators. The claim
covers which items are chosen, how they are paired and the order they
are presented in, so the generated experiments are byte-identical in
full. The only exceptions are the `mahalanobis` and `optimal` matching
methods.

‘Byte-identical’ is meant literally, and stating it that way turned out
to matter. The parity test originally read both engines’ stimuli files
back with a CSV parser and compared the values, under which `1` and
`1.0` are the same number. On that test 13 of the shipped designs passed
while differing byte for byte. Three of the differences were
serialisation: a whole number written `1` by one writer and `1.0` by the
other, a boolean written `FALSE` and `False`, and a small value written
`9e-4` and `0.0009`. One was not: two reported means differed in the
last decimal published, because one engine’s summation was pairwise and
the other’s was not. Every reduction in the package now uses a single
compensated-summation algorithm written out in both engines, whose
agreement follows from IEEE-754 requiring addition and subtraction to be
correctly rounded, and the artefacts are compared as bytes rather than
as parsed values.

Two files sit outside the claim by design, because each records the
engine that produced it: the materials datasheet names its engine and
that engine’s package versions, and the run log adds wall-clock
timestamps. Their contents are compared field by field instead.

Within one engine, selection is a pure function of its input.

``` r

a <- match_stimuli(pool, design, schema)
b <- match_stimuli(pool, design, schema)
identical(a, b)
```

    [1] TRUE

That is not a small claim to make about an R function. Repeated calls
agree because nothing in the selection path consults a random number
generator, and because every operation that could depend on the ambient
environment has been pinned. The interesting question is why the
*Python* engine also agrees, since the two implementations share no
code.

## How byte-identical output is achieved

Cross-engine identity is not an accident of two careful translations.
Each mechanism below closes a specific way the engines could otherwise
drift.

The first is that there is no random number generator anywhere. The
obvious way to choose 15 items from 700 is to sample them, and `lexsync`
never does. The anchor condition is chosen by an even spread across its
sorted subpool, taking positions along the whole range rather than a
random subset, and every later item is determined by a distance. A
seeded RNG would not help here, because R’s Mersenne-Twister stream and
NumPy’s are different streams: the same seed gives different draws, so
any sampling step would break parity by construction. Determinism
through absence is the only option that survives two languages, and it
now extends to trial order, whose shuffle is described below.

``` r

anchor_pool <- pool[pool$frequency >= 5.2 & pool$frequency <= 7.0, ]
anchor_pool <- anchor_pool[
  order(anchor_pool$frequency, anchor_pool$word, method = "radix"),
]
idx <- unique(round(seq(1, nrow(anchor_pool), length.out = 15)))
idx
```

     [1]  1  6 11 16 21 26 31 36 41 46 51 56 61 66 71

The spread is [`seq()`](https://rdrr.io/r/base/seq.html) over the row
positions, rounded to integers. Both engines compute the same positions
from the same row count, and the rounding is specified rather than
incidental.

Sorting is by byte order everywhere. R’s default string sort is
locale-collated, and a French locale, a C locale and a Windows locale
can order the same words differently, while any of those orders would
differ from Python’s, which sorts by code point. Every sort on the
selection path therefore passes `method = "radix"`, which sorts by
bytes.

``` r

words <- c("zebra", "Apple", "apple", "Zebra")
sort(words, method = "radix")
```

    [1] "Apple" "Zebra" "apple" "zebra"

Uppercase sorts before lowercase because that is the byte order, and
this is what Python’s `sorted()` produces. A locale-collated sort would
typically interleave them. Case folding is pinned for the same reason:
[`load_lexicon()`](https://pablobernabeu.github.io/lexsync/r/reference/load_lexicon.md)
lower-cases through ICU at the root locale rather than through
[`tolower()`](https://rdrr.io/r/base/chartr.html), whose behaviour
depends on the C library and the locale, and which differs from Python’s
on Greek final sigma and the dotted Turkish capital I.

Frequencies of bigrams and of subsyllabic constituents are accumulated
as integers, never as running floating-point sums, so the counts cannot
depend on summation order.

Rounding comes before the tie-break, which is the subtle one of these
mechanisms. Two candidate words can sit at genuinely equal distance from
an anchor, and the last bits of a square root can differ between two
linear-algebra implementations. If the engines compared raw doubles, an
inconsequential difference in the fifteenth decimal would make one
engine call a tie and the other not, and they would pick different
words. Distances are therefore rounded to nine decimal places before
ranking, which puts both engines on the same side of every comparison
that matters.

Rounding creates ties rather than removing them, so the ties in turn
need a rule that both engines can apply identically, and that rule is a
total order. Candidates are ordered by distance, then by the word’s
bytes, then by its integer `id`. That is the comparison the matcher
makes, and it is reproduced here on three imaginary candidates.

``` r

distance <- c(0.5, 0.5, 0.2)
word     <- c("beta", "alpha", "gamma")
id       <- c(1L, 2L, 3L)
word[order(distance, word, id, method = "radix")]
```

    [1] "gamma" "alpha" "beta" 

`gamma` wins on distance. `alpha` and `beta` are tied on distance to the
ninth decimal, and the word’s bytes settle it, identically in both
engines. Since `word` is unique within a lexicon the order is total, so
there is always exactly one winner and never a coin to flip. The schema
notes that this order is fixed in the code and deliberately not
configurable, because it is the mechanism of parity rather than a
preference.

The even-spread rounding is shared as well. `unique(round(seq(...)))` is
used identically in both engines, including the
[`unique()`](https://rdrr.io/r/base/unique.html), which matters when the
pool is smaller than the requested n and the rounding produces a
repeated index.

### Trial order: a seeded shuffle without a generator

Trial order used to be the honest exception. Each engine drew the order
from its own seeded generator, R’s Mersenne-Twister against NumPy’s
PCG64, and the same seed could not give the same permutation, so an
order was reproducible within an engine and different between the
engines. That exception is retired. Order is now decided by a keyed
hash: each row of a list is ranked by the SHA-256 digest of
`seed|replicate|list|set|condition`, a tuple that identifies the trial
uniquely under either counterbalancing recipe. Distinct inputs to
SHA-256 behave as independent uniform draws, so sorting rows by their
digests realises a seeded random permutation, and because a digest is a
pure function of its input, the permutation is a pure function of the
design: the same bytes from both engines on any platform, no generator
state to save or restore, and a different order for every seed. The
implementation is `.shuffle_deterministic()` in `R/counterbalancing.R`,
mirrored in the Python engine’s `counterbalancing.py`.

``` r

stim <- counterbalance(match_stimuli(pool, design, schema), design, schema)
head(stim[, c("trial", "condition", "word")], 4)
```

      trial condition   word
    1     1       low   myth
    2     2      high   with
    3     3      high  local
    4     4      high street

``` r

same <- counterbalance(match_stimuli(pool, design, schema), design, schema)
identical(stim$trial, same$trial)
```

    [1] TRUE

The order is still randomised in the sense a study needs: an item’s
properties bear no systematic relation to its position, and a different
seed gives a different order. What changed is that the permutation is
engine-invariant, so it sits inside the cross-engine contract rather
than outside it, and the guarantee reaches the generated experiments
whole: for every shipped design, the PsychoPy script, the OpenSesame
file, the jsPsych page and both loop-table CSVs are byte-identical
across the engines.

One detail worth noting for anyone embedding `lexsync` in a longer
script: counterbalancing no longer touches the random number generator
at all, since nothing in the package consults one, so calling it cannot
disturb the stream your own code is drawing from.

## The Unicode input contract

Word matching, deduplication and the `length` dimension operate on
Unicode code points exactly as supplied. Beyond the pinned lower-casing
described above, the orthographic form is never rewritten, and in
particular no canonical normalisation is applied, neither NFC nor NFD. A
precomposed character such as é and its decomposed counterpart, the base
letter followed by a combining accent, are therefore distinct items that
differ in length, and a lexicon mixing the two conventions carries
apparent duplicates that never match one another. Supply NFC-normalised
text, which is the form most corpora already distribute.

The syllable estimator and the pseudoword generators carry a narrower
contract still. The vowel class behind `n_syllables` covers the Latin-1
vowels, and the pseudoword generators build their candidates from
lower-case a to z, so both are orthographic approximations defined for
Latin orthographies and unavailable for other scripts. The shipped
Chinese design matches on `length`, `n_density` and `old20` for exactly
this reason.

## The documented exceptions

`mahalanobis` and `optimal` are equivalent to their byte-identical
siblings in what they compute and not in what they select, and the
reason is worth understanding rather than merely noting.

`mahalanobis` needs the inverse of the pool’s correlation matrix. A
matrix inverse is computed by LAPACK, and R’s LAPACK is not necessarily
the one NumPy is built against. The two may differ in blocking, in
vectorisation and in the order they accumulate sums. The results agree
to well within any tolerance you would care about and they need not
agree in their last bits, and the rounding that saves the Euclidean path
cannot save this one: the distance is now a function of a matrix whose
entries already differ below the rounding threshold, so the rounding can
land on either side.

`optimal` solves a linear assignment problem. Where several assignments
have the same total cost, which one a solver returns is an
implementation detail of the solver, and R’s
[`clue::solve_LSAP()`](https://rdrr.io/pkg/clue/man/solve_LSAP.html) and
SciPy’s implementation resolve those ties differently. Both return a
genuinely optimal assignment. They need not return the same one.

Neither is a bug that a determined engineer could fix. Guaranteeing them
would mean shipping a bit-exact matrix inverse and a tie-canonical
assignment solver in both languages, which is a large amount of
numerical code to maintain for a modest gain. The chosen trade-off is to
keep the byte-identical methods as the defaults, document the exception,
and record it per run.

``` r

maha <- design
maha$matching <- list(method = "mahalanobis")
maha_stim <- match_stimuli(pool, maha, schema)
maha_ds <- build_datasheet(
  maha, schema, NULL, maha_stim,
  system.file("extdata", "en_example.csv", package = "lexsync"),
  list(stimuli = NA_character_), schema$seed
)
maha_ds$selection$cross_engine
```

    [1] "approximate (platform linear algebra)"

Every datasheet carries this field, so a reader of the record does not
have to know the rule. It reads `byte-identical` for the default methods
and `approximate (platform linear algebra)` for these two, and the
generated methods paragraph adds a sentence stating the caveat in prose
when it applies. The constraint also shapes the roadmap: a
covariance-aware distance would arguably be the better default, and it
stays optional precisely because it cannot carry the guarantee.

## The parity test

A guarantee that is not tested is a comment. The parity gate in
continuous integration runs the R pipeline over the shipped designs,
regenerates each with the Python engine and compares the two, across
designs covering both engines’ matching methods, continuous selection,
both pseudoword generators, resampling, priming and self-paced reading,
three languages including a logographic script, and three reproductions
of published designs.

The comparison is on identity columns: the word or target, the condition
and the `set` index. Including `set` is what makes the test meaningful
rather than cosmetic, since without it the engines could select the same
items and pair them differently and still pass. Having matched on those,
the test then checks every other shared column, so the `trial` position
and the dimensions each engine computes at run time (`n_density`,
`old20`, `n_syllables`, `bigram_freq`) must also agree.

Three details keep the gate from passing vacuously. The test skips when
the R reference output is absent, since the Python package can be
installed on its own, so CI sets `LEXSYNC_REQUIRE_PARITY=1` to turn
those skips into failures: a job meant to run both engines cannot pass
by quietly skipping. The R references are regenerated and then checked
with `git diff --exit-code`, so an R-engine regression fails the build
instead of being compared against a stale snapshot it matches. And the R
suite is run once from the source tree with a check that nothing
skipped, because the repository-coupled tests silently skip when run
from an installed copy.

## The materials datasheet

Each run emits a datasheet in two forms, a JSON record for machines and
a Markdown rendering for people. It exists because the reproducibility
literature in linguistics keeps finding the same gap: materials are
described but rarely deposited in a form that permits reuse or
verification (Bochynska et al., 2023), and the degrees of freedom in
preparing them are large enough to matter (Roettger, 2019). A datasheet
is the FAIR-style record of one selection (Wilkinson et al., 2016).

``` r

out <- file.path(tempdir(), "lexsync_repro")
dir.create(out, showWarnings = FALSE)
report <- match_report(
  stim, c("frequency", "length", "n_density", "old20"), schema
)
stim_path <- file.path(out, "stimuli.csv")
write.csv(stim, stim_path, row.names = FALSE)

ds <- build_datasheet(
  design, schema, report, stim,
  source_path = system.file("extdata", "en_example.csv", package = "lexsync"),
  artifacts = list(stimuli = stim_path),
  seed = schema$seed,
  candidate_pool = lapply(design$conditions, function(cnd)
    list(
      condition = cnd$name,
      n_candidates = nrow(build_pool(pool, cnd$define_by))
    ))
)
names(ds)
```

     [1] "lexsync_datasheet_version" "design"                   
     [3] "materials_source"          "dimensions"               
     [5] "selection"                 "relational"               
     [7] "analysis"                  "equivalence"              
     [9] "realised_control"          "counterbalancing"         
    [11] "resampling"                "items"                    
    [13] "reproducibility"           "artifacts"                

The record answers the questions a sceptical reader would ask. Where the
words came from, and whether this is the same file, is settled by
`materials_source`, which carries the path and its SHA-256. What was
applied is recorded in `selection`, covering the method, the matched
dimensions and the tolerance windows that were actually resolved, which
is the design’s overrides merged onto the schema’s defaults rather than
the defaults a design may have replaced. What the selection achieved is
in `realised_control`, as the effect sizes, intervals, variance ratios
and TOST verdicts. What it could have chosen instead is in
`candidate_pool`, which records how many items satisfied each condition
before matching.

``` r

ds$materials_source$sha256
```

    [1] "939ee46015bc03cdb3fa12e2598f763b818c941118a8170bb408386277945e01"

``` r

str(ds$selection$tolerance_k)
```

    List of 4
     $ length   : num 2
     $ frequency: num 1
     $ n_density: num 2
     $ old20    : num 2

``` r

do.call(rbind, lapply(ds$selection$candidate_pool, as.data.frame))
```

      condition n_candidates
    1      high           71
    2       low          480

The candidate-pool counts do a job that is easy to miss. Here the high
condition was drawn from a few dozen eligible words and the low
condition from several hundred, which are different epistemic
situations: choosing 15 items from a large candidate set invites the
concern that a selection could be steered towards almost any result,
whereas a condition with barely more candidates than items had little
freedom to be steered. Recording the counts, alongside the fact that the
selection is deterministic and blind to any outcome measure, lets a
reader judge that rather than take it on trust.

Note that the resolved windows include a `frequency` entry even though
this design matches on the three orthographic dimensions only. The
record reports the windows as resolved from the schema and the design,
and a window is applied only to a dimension named in `match_on`.

``` r

str(ds$reproducibility)
```

    List of 2
     $ seed    : int 2026
     $ versions:List of 10
      ..$ engine    : chr "R"
      ..$ lexsync   : chr "0.1.0"
      ..$ R         : chr "4.6.1"
      ..$ readr     : chr "2.2.0"
      ..$ stringdist: chr "0.9.17"
      ..$ jsonlite  : chr "2.0.0"
      ..$ digest    : chr "0.6.39"
      ..$ yaml      : chr "2.3.12"
      ..$ stringi   : chr "1.8.9"
      ..$ os        : chr "Linux x86_64"

The reproducibility block records the seed and the versions of the
engine and its dependencies, since a bug fix in a dependency can change
a selection and the record should say which versions produced this one.

### The methods paragraph and the pre-registration template

The datasheet renders itself into prose, which is a small feature that
removes a common source of error: a methods section transcribed by hand
from numbers on a screen.

``` r

cat(strwrap(methods_paragraph(ds), width = 76), sep = "\n")
```

    15 items per condition were selected from the English lexicon (wordfreq
    (Speer, 2022), data CC BY-SA 4.0; full corpus licence and citation at
    https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md)
    and matched item by item on length, n_density, old20 using lexsync's
    standardised_euclidean matcher. Equivalence was not confirmed on every
    matched dimension; the per-dimension differences are reported in the
    realised-control table. The smallest condition was selected from 71
    eligible candidates, and the selection was deterministic and blind to any
    outcome measure. Materials were counterbalanced into 1 list(s) (a factorial
    split) and generated for PsychoPy, OpenSesame and jsPsych. The selection is
    deterministic and reproducible (seed 2026; lexsync 0.1.0).

The paragraph is generated from the record, so it cannot disagree with
the stimuli. It reports the largest standardised difference on any
matched dimension with its interval rather than a selective best case,
states the candidate-pool size, and adds the cross-engine caveat when
the design’s method warrants it.

It is a draft to adapt rather than a paragraph to paste unread, and this
run shows why. The phrase ‘within the 0.5-SD equivalence bound’
describes the point estimate, while the interval printed beside it
reaches well past that bound in both directions. Both statements are
true and they are not the same claim. The interval is wide because this
demonstration matches only 15 items per condition, which is precisely
the dependence on set size that the matching vignette warns against
reading past. A real study would either match enough items to narrow the
interval or say plainly that the control is established at the point
estimate and not at the bound.

[`write_datasheet()`](https://pablobernabeu.github.io/lexsync/r/reference/write_datasheet.md)
writes both forms, and the Markdown rendering carries a pre-registration
skeleton with its materials section already filled in.

``` r

paths <- write_datasheet(
  ds, file.path(out, "datasheet.json"), file.path(out, "datasheet.md")
)
md <- readLines(file.path(out, "datasheet.md"))
grep("^#", md, value = TRUE)
```

     [1] "# Materials datasheet -- vignette_repro (english)"
     [2] "## Provenance"                                    
     [3] "## Selection transparency"                        
     [4] "## Realised control"                              
     [5] "## Suggested analysis"                            
     [6] "## Methods paragraph"                             
     [7] "## Pre-registration template"                     
     [8] "### Study information"                            
     [9] "### Hypotheses"                                   
    [10] "### Design"                                       
    [11] "### Materials (from the lexsync datasheet)"       
    [12] "### Sampling plan"                                
    [13] "### Analysis plan"                                

The sections left blank are the ones no tool can fill: the hypotheses,
the sampling plan and the inference criteria. The analysis plan arrives
with a suggested model rather than empty, and the suggestion is
opinionated on purpose.

``` r

ds$analysis$suggested_model
```

    [1] "response ~ condition + (1 + condition | subject) + (1 | item)"

The model crosses random effects for subjects and items because items
are a sample of the language rather than the population of interest, and
an analysis treating them as fixed generalises only to the words that
were used (Clark, 1973; Yarkoni, 2022). The accompanying note recommends
beginning with the maximal structure and reducing it if it does not
converge. It is a starting point for a design of this shape and not a
substitute for thinking about the analysis.

## The run log

The datasheet records what a run produced. The run log records what it
did.

``` r

log <- new_run_log(
  "vignette_repro",
  meta = list(seed = schema$seed, language = "english")
)
log <- log_step(
  log,
  sprintf("lexicon loaded: %d words", nrow(lex)),
  list(words = nrow(lex))
)
```

    [lexsync] lexicon loaded: 3000 words

``` r

log <- log_step(log, sprintf("pool after filters: %d words", nrow(pool)))
```

    [lexsync] pool after filters: 782 words

``` r

log <- log_artefact(log, stim_path, rows = nrow(stim))
```

    [lexsync] wrote 'stimuli.csv'

``` r

log_md <- write_run_log(log, file.path(out, "run_log.md"),
                        file.path(out, "run_log.jsonl"))
cat(readLines(log_md), sep = "\n")
```

    # lexsync run log: vignette_repro

    - Engine: R 4.6.1
    - Started: 2026-08-08 18:33:02.411567
    - Finished: 2026-08-08 18:33:02.414181

    ## Run metadata

    - seed: 2026
    - language: english

    ## Steps

    - **2026-08-08 18:33:02.412476**: lexicon loaded: 3000 words
        - words: 3000
    - **2026-08-08 18:33:02.412997**: pool after filters: 782 words
    - **2026-08-08 18:33:02.413464**: wrote 'stimuli.csv'
        - path: /tmp/RtmptJTbNO/lexsync_repro/stimuli.csv
        - rows: 30
        - md5: 7aa533be3e1a4bcd22146d0adb023c3e

The pipeline builds this log as it goes, recording each stage with its
parameters, the equivalence verdict on every dimension, any balance
warning, and an entry per file written with its row count and MD5. Both
a Markdown log and a JSON Lines log are emitted, the latter so that a
run can be checked by a script. The MD5 here is a content fingerprint
for spotting drift between runs, whereas the datasheet’s SHA-256 is the
stronger one that belongs in a permanent record.

## Reproducing this in practice

The pipeline does all of the above in one call, and
[`run_pipeline()`](https://pablobernabeu.github.io/lexsync/r/reference/run_pipeline.md)
on a design configuration is the reproducible unit: it writes the
stimuli, the reports, the three experiments, the datasheet and the log.
Sharing the design file and the corpus is then enough for someone else
to regenerate the materials and verify the checksums, in either
language.

Two habits make that work. Pin the corpus, since a selection is only
reproducible against a fixed lexicon, which is why the bundled corpora
are a checksummed snapshot and why the `wordfreq` connector draws on a
source frozen in 2024 rather than a live one. And prefer the default
matching methods when cross-engine reproducibility matters, since they
are the ones that carry the guarantee.

## References

Bochynska, A., Keeble, L., Halfacre, C., Casillas, J. V., Champagne,
I.-A., Chen, K., Röthlisberger, M., Buchanan, E. M., & Roettger, T. B.
(2023). Reproducible research practices and transparency across
linguistics. *Glossa Psycholinguistics*, *2*(1).
<https://doi.org/10.5070/G6011239>

Clark, H. H. (1973). The language-as-fixed-effect fallacy: A critique of
language statistics in psychological research. *Journal of Verbal
Learning and Verbal Behavior*, *12*(4), 335–359.
<https://doi.org/10.1016/S0022-5371(73)80014-3>

Roettger, T. B. (2019). Researcher degrees of freedom in phonetic
research. *Laboratory Phonology*, *10*(1), Article 1.
<https://doi.org/10.5334/labphon.147>

Wilkinson, M. D., Dumontier, M., Aalbersberg, IJ. J., Appleton, G.,
Axton, M., Baak, A., Blomberg, N., Boiten, J.-W., da Silva Santos, L.
B., Bourne, P. E., Bouwman, J., Brookes, A. J., Clark, T., Crosas, M.,
Dillo, I., Dumon, O., Edmunds, S., Evelo, C. T., Finkers, R., … Mons, B.
(2016). The FAIR Guiding Principles for scientific data management and
stewardship. *Scientific Data*, *3*, Article 160018.
<https://doi.org/10.1038/sdata.2016.18>

Yarkoni, T. (2022). The generalizability crisis. *Behavioral and Brain
Sciences*, *45*, Article e1. <https://doi.org/10.1017/S0140525X20001685>
