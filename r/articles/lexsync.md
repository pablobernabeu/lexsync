# Getting started with lexsync

`lexsync` selects stimuli that are matched in parallel across several
lexical dimensions and then generates the experiment scripts that
present them. This vignette runs a small high- versus low-frequency
contrast on the bundled English example lexicon.

The selection is deterministic, and it ships as two independent
packages, one for R and one for Python, which select byte-identical
stimuli from the same lexicon and design. No random number generator is
involved: the engines agree because every ordering is by byte and every
tie is broken by a rule both apply. This holds for the default matching
methods. The optional `mahalanobis` and `optimal` methods are equivalent
but not byte-identical, because a covariance inverse and an assignment
solver differ in their last bits between the two platforms.

The package is on [CRAN](https://CRAN.R-project.org/package=lexsync),
and the
[README](https://pablobernabeu.github.io/lexsync/r/index.html#installation)
also covers installing the development version.

``` r

install.packages("lexsync")
```

``` r

library(lexsync)
schema <- yaml::read_yaml(
  system.file("extdata", "schema.yaml", package = "lexsync")
)
lex <- load_lexicon(
  system.file("extdata", "en_example.csv", package = "lexsync"),
  schema, language = "english"
)
nrow(lex)
```

    [1] 3000

## Define and run a design

A design names the conditions, the dimensions to match and the number of
items, together with the filters that narrow the lexicon to a candidate
pool. The pool is built first, exactly as the pipeline does, and
matching then runs over it.

``` r

design <- list(
  name = "quick_start", language = "english", n_per_condition = 60,
  pool_filters = list(length = c(3, 8), frequency = c(3.8, 7.0)),
  conditions = list(
    list(name = "high_frequency", define_by = list(frequency = c(5.2, 7.0))),
    list(name = "low_frequency",  define_by = list(frequency = c(3.8, 4.4)))
  ),
  match_on = list("length", "n_density", "old20"),
  counterbalance = list(lists = 1)
)
pool <- build_pool(lex, design$pool_filters)
stim <- match_stimuli(pool, design, schema)
head(stim[, c(
  "word", "condition", "length", "frequency", "n_density", "old20"
)])
```

         word      condition length frequency n_density old20
    1 perfect high_frequency      7      5.20         0  2.55
    2 include high_frequency      7      5.21         0  2.65
    3     sex high_frequency      3      5.22        11  1.30
    4   issue high_frequency      5      5.23         0  2.35
    5  mother high_frequency      6      5.24         1  1.85
    6   seems high_frequency      5      5.24         5  1.65

## Anatomy of a design file

The list above is convenient in a vignette, but a real study writes its
design as YAML. That is what makes a design portable:
`config/schema.yaml` holds everything global and every numeric default,
the design holds what is specific to the study, and both are read
identically by the R and the Python package, so a design file can be
attached to a pre-registration and handed to someone running the other
engine. Here is the English frequency contrast in full, from
`config/design_en_freqcontrast.yaml` in the repository.

``` yaml
name: en_freqcontrast
language: english
lexicon: corpora/derived/en_v2.csv
description: 'High versus low frequency English words, matched on length, neighbourhood density and OLD20.'
n_per_condition: 80
pool_filters:
  length: [3, 8]
  frequency: [3.8, 7.0]
  # Keeps only the forms the SUBTLEX-US screen leaves unmarked (see corpora/ATTRIBUTION.md).
  nonstandard: [0, 0]
# Leaves out the unsuitable forms the screen lets through (see the file's header).
exclude_words: {path: config/exclude_en_demo.txt}
conditions:
  - name: high_frequency
    define_by:
      frequency: [5.2, 7.0]
  - name: low_frequency
    define_by:
      frequency: [3.8, 4.4]
match_on: [length, n_density, old20]
counterbalance:
  lists: 1
timing:
  fixation_frames: 30
  word_frames: 30
  isi_frames: 15
```

### The keys

`name` and `language` are required, and together they form the slug
every written file is named after. `en_freqcontrast` plus `english`
becomes `en_freqcontrast_english`, and from that come
`en_freqcontrast_english_stimuli_R.csv`, `en_freqcontrast_english.osexp`
and the rest. A name or language holding a character outside ASCII also
adds an eight-character checksum to the stem, as *Reproducibility,
parity and the materials datasheet* explains. `language` is a free-text
label rather than a code, because it is what the experiment displays.
When the browser target needs a real BCP 47 tag it maps the common
labels and falls back to `und`, or you can state `language_tag`
outright.

`lexicon` names the derived corpus to read. It may also be written as
`items.lexicon`, which is the form the lexical-decision designs use,
since they also have to say where the items come from.

`items` selects where the stimuli come from, and there are four sources.

| `items.source` | Where stimuli come from | Also needs |
|----|----|----|
| `corpus` (the default) | Words selected from the lexicon by matching, or by spanning a predictor. | `lexicon`, `conditions` or `continuous`, `match_on` |
| `generate` | Real words plus a deterministically generated pseudoword for each. | `lexicon`, optionally `items.generation.method` |
| `table` | A CSV of prepared items (prime-target pairs, sentences). Add `items.members` to make it pair-keyed. | `items.path` |
| `pool` | A candidate word list of your own, matched over as if it were a pool. | `items.path`, normally `items.lexicon`, plus `conditions` and `match_on` as for `corpus` |

`pool_filters` narrows the lexicon to the candidates the design will
consider at all. Each key is a column and each value an inclusive
`[min, max]` range for a numeric column, or a set of permitted values
otherwise. This is a real step and not a formality:
[`match_stimuli()`](https://pablobernabeu.github.io/lexsync/r/reference/match_stimuli.md)
never reads `pool_filters` itself, so a script that skips
[`build_pool()`](https://pablobernabeu.github.io/lexsync/r/reference/build_pool.md)
matches over the whole lexicon and quietly ignores the design’s bands.
Here `nonstandard: [0, 0]` keeps the forms the screened lexicon leaves
unmarked, and `exclude_words` leaves out the words a file lists, as
*Matching, dimensions and designs* explains.

`conditions` is a list, each entry with a `name` and a `define_by` block
that carves the condition out of the pool by the same filter syntax. Two
conditions make a contrast. Four make the 2 × 2 that
`design_en_andrews_repro.yaml` uses to reproduce Andrews (1989). A
design may instead declare a `continuous` block and dispense with
conditions altogether.

`match_on` lists the dimensions to equate across conditions, and a
design that matches its conditions must name at least one.
`n_per_condition` is how many items each should hold, a whole number
written as `80` or `80.0`. Both are the heart of the design and both are
covered at length in *Matching, dimensions and designs*.

`matching` overrides the schema defaults for this design alone:
`matching.method` picks one of the four methods, and
`matching.tolerance_k` sets the half-width, in standard deviations, of
the tolerance window on each dimension. Overriding a single dimension is
common when reproducing a published study’s exact windows.

`counterbalance.lists` sets the number of lists, and
`counterbalance.optimise` asks for an assignment whose lists are equated
on the item dimensions rather than dealt by set rank. `practice` and
`fillers` each name an item table whose trials are presented but not
analysed. `timing` sets the fixation, critical-word and inter-stimulus
durations. Milliseconds are canonical (`fixation_ms`, `word_ms`,
`isi_ms`), which is why a design means the same interval on any display.
This design predates that change and still uses the `*_frames` form
above, which is accepted and converted on load at the schema’s
`presentation.assumed_refresh_hz`, so its 30 frames become the 500 ms
they were written for. `font` overrides the presentation font, which
matters for a non-Latin script: `design_zh_freqcontrast.yaml` sets
`SimHei`, because the Latin default has no glyphs for Han characters.

`paradigm` names one of the six registered paradigms and inherits its
trial-event sequence and its counterbalancing recipe. Omitting it gives
`factorial`. A design may instead supply an explicit `events` list and
describe its own trial. Both routes are covered in *Experiments,
paradigms and EEG triggers*.

### What is checked before a run

Before it reads a lexicon or writes a file,
[`run_pipeline()`](https://pablobernabeu.github.io/lexsync/r/reference/run_pipeline.md)
checks the design and the schema with
[`validate_design()`](https://pablobernabeu.github.io/lexsync/r/reference/validate_design.md),
and a design that cannot be honoured is refused with the same message in
both engines. Every key is looked up in the vocabulary of keys lexsync
reads at its level. A key one edit from a known key of up to five
characters, or two edits from a longer one, is taken for a typo. It is
refused with the key it was probably meant to be. `n_per_conditon: 8`
now stops with
`unknown design key 'n_per_conditon' (did you mean 'n_per_condition'?)`,
where it used to leave the design on the default of twenty items. Any
other unknown key is noted in the run log and otherwise ignored, and a
later release will refuse it. Notes and comments therefore belong in
`description` or in a key beginning `x_`, which are never checked.

The same step checks the values. It refuses a missing or non-text `name`
or `language` (quote a code such as `'no'`, which YAML reads as false)
and an `n_per_condition` that is not a whole number of at least 1. It
refuses a name, language or font that cannot be written safely into the
generated experiments, a trigger port that is not an address, and an
unknown timing key or malformed response key. Last, it refuses a
condition name that is not text or appears twice, and a corpus or pool
design with conditions but no `match_on`. These used to surface at
export, after the stimuli and reports had been written, or at a
different point in each engine.

### Running one

[`run_pipeline()`](https://pablobernabeu.github.io/lexsync/r/reference/run_pipeline.md)
takes a design path and does everything this vignette has done by hand,
plus the datasheet and the run log. From a clone of the repository:

``` r

out_one <- tempfile("lexsync_one_")
run_pipeline("config/design_en_freqcontrast.yaml", outdir = out_one)
out_all <- tempfile("lexsync_all_")
run_all(outdir = out_all)  # every design_*.yaml in config/
```

Paths inside a design are resolved relative to the working directory, so
run these from the root of a checkout.

## Inspect the match quality

Matching always returns a set, so the report is what tells you whether
the set is any good. It belongs before anything is generated from the
stimuli.

``` r

report <- match_report(
  stim, c("length", "frequency", "n_density", "old20"), schema
)
knitr::kable(
  report$descriptives,
  caption = "Descriptive statistics per condition"
)
```

| group          | dimension |   n |  mean |    sd | min | median |   max |
|:---------------|:----------|----:|------:|------:|----:|-------:|------:|
| high_frequency | length    |  60 | 4.650 | 1.313 | 3.0 |   4.00 |  8.00 |
| high_frequency | frequency |  60 | 5.604 | 0.418 | 5.2 |   5.42 |  6.85 |
| high_frequency | n_density |  60 | 5.600 | 6.304 | 0.0 |   3.00 | 23.00 |
| high_frequency | old20     |  60 | 1.738 | 0.486 | 1.0 |   1.70 |  2.80 |
| low_frequency  | length    |  60 | 4.633 | 1.275 | 3.0 |   4.00 |  7.00 |
| low_frequency  | frequency |  60 | 4.060 | 0.169 | 3.8 |   4.05 |  4.40 |
| low_frequency  | n_density |  60 | 5.233 | 5.400 | 0.0 |   3.50 | 17.00 |
| low_frequency  | old20     |  60 | 1.736 | 0.477 | 1.0 |   1.75 |  2.70 |

Descriptive statistics per condition {.table}

``` r

knitr::kable(
  report$comparisons,
  caption = paste(
    "Standardised mean differences with 90% confidence intervals, plus the",
    "complementary TOST equivalence test"
  )
)
```

| condition | reference | dimension | cohens_d | d_ci_low | d_ci_high | var_ratio | tost_p | equivalent | mean_diff | role |
|:---|:---|:---|---:|---:|---:|---:|---:|:---|---:|:---|
| low_frequency | high_frequency | length | 0.013 | -0.290 | 0.316 | 0.944 | 0.0044 | TRUE | 0.017 | NA |
| low_frequency | high_frequency | frequency | 4.840 | 4.240 | 5.440 | 0.164 | 1.0000 | FALSE | 1.545 | NA |
| low_frequency | high_frequency | n_density | 0.062 | -0.240 | 0.365 | 0.734 | 0.0091 | TRUE | 0.367 | NA |
| low_frequency | high_frequency | old20 | 0.005 | -0.297 | 0.308 | 0.963 | 0.0039 | TRUE | 0.002 | NA |

Standardised mean differences with 90% confidence intervals, plus the
complementary TOST equivalence test {.table style="width:100%;"}

The manipulated dimension (frequency) differs strongly, while on the
controlled dimensions (length, neighbourhood density and OLD20) the
differences are small and each passes the equivalence test. Showing
equivalence needs enough items: at the default bound and alpha no
dimension that varies can pass with fewer than 23 items per condition.
The report leads with the standardised mean difference (`cohens_d`) and
its 90% confidence interval (`d_ci_low`, `d_ci_high`). A non-significant
difference test is not evidence of matching, and its outcome depends on
the number of items. The effect size and its interval, whose upper limit
is the largest imbalance still consistent with the stimuli, are
therefore the primary summary. The TOST equivalence test is reported
alongside as a bound-referenced verdict.

## Generate the experiment scripts

The trial is described once, as a sequence of events, and each
presentation target renders that same description. One call therefore
produces all three.

``` r

out <- file.path(tempdir(), "lexsync_demo")
dir.create(out, showWarnings = FALSE)
files <- export_experiments(stim, design, schema, out)
basename(files$files)
```

    [1] "quick_start_english_psychopy.py"        
    [2] "quick_start_english.osexp"              
    [3] "quick_start_english.html"               
    [4] "quick_start_english_psychopy.csv"       
    [5] "quick_start_english_opensesame.csv"     
    [6] "quick_start_english_opensesame_text.csv"

Three experiments are generated from one description of the trial, with
the tables the PsychoPy and OpenSesame targets read. The PsychoPy script
binds each onset trigger to the stimulus flip with `win.callOnFlip`. The
OpenSesame `.osexp` draws and shows the word inside an `inline_script`
and sends the marker immediately after `show()` returns, which it does
at the display refresh. The jsPsych HTML runs the same procedure in a
browser and records the trigger codes in the trial data, since a browser
cannot address a parallel port. Neither the matching nor the script
generation requires PsychoPy, OpenSesame or any hardware to be
installed.

## Where next

The pipeline does all of the above in one call.
[`run_pipeline()`](https://pablobernabeu.github.io/lexsync/r/reference/run_pipeline.md)
on a design configuration writes the stimuli, the reports, the three
experiments, a materials datasheet recording the provenance and realised
control of the run, and a run log.

Four further articles go into depth. *Matching, dimensions and designs*
covers the lexical dimensions and their units, the four matching methods
and when each one suits, tolerance windows, continuous designs and how
to read the validation report. *Experiments, paradigms and EEG triggers*
covers the trial-event model, the paradigm registry, the three
presentation targets and the flip-locked trigger timing.
*Reproducibility, parity and the materials datasheet* covers the
cross-engine guarantee, how it is achieved and where it stops. *The app*
covers the Shiny front-end in the repository, which assembles a design
through a browser tab, runs this same pipeline and exports the code that
reproduces the run.
