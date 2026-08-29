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
  name = "vignette_demo", language = "english", n_per_condition = 15,
  pool_filters = list(length = c(3, 7), frequency = c(3.8, 7)),
  conditions = list(
    list(name = "high", define_by = list(frequency = c(5.2, 7.0))),
    list(name = "low",  define_by = list(frequency = c(3.8, 4.4)))
  ),
  match_on = list("length", "n_density", "old20")
)
pool <- build_pool(lex, design$pool_filters)
stim <- match_stimuli(pool, design, schema)
head(stim[, c(
  "word", "condition", "length", "frequency", "n_density", "old20"
)])
```

        word condition length frequency n_density old20
    1   knew      high      4      5.20         3  1.75
    2 points      high      6      5.23         5  1.65
    3  field      high      5      5.24         3  1.75
    4 street      high      6      5.28         1  1.90
    5    low      high      3      5.33        24  1.00
    6   lost      high      4      5.39        12  1.25

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
lexicon: corpora/derived/en.csv
description: 'High versus low frequency English words, matched on length, neighbourhood density and OLD20.'
n_per_condition: 80
pool_filters:
  length: [3, 8]
  frequency: [3.8, 7.0]
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
and the rest. `language` is a free-text label rather than a code,
because it is what the experiment displays. When the browser target
needs a real BCP 47 tag it maps the common labels and falls back to
`und`, or you can state `language_tag` outright.

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

`conditions` is a list, each entry with a `name` and a `define_by` block
that carves the condition out of the pool by the same filter syntax. Two
conditions make a contrast. Four make the 2 × 2 that
`design_en_andrews_repro.yaml` uses to reproduce Andrews (1989). A
design may instead declare a `continuous` block and dispense with
conditions altogether.

`match_on` lists the dimensions to equate across conditions and
`n_per_condition` how many items each should hold. Both are the heart of
the design and both are covered at length in *Matching, dimensions and
designs*.

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

`paradigm` names one of the five registered paradigms and inherits its
trial-event sequence and its counterbalancing recipe. Omitting it gives
`factorial`. A design may instead supply an explicit `events` list and
describe its own trial. Both routes are covered in *Experiments,
paradigms and EEG triggers*.

### Running one

[`run_pipeline()`](https://pablobernabeu.github.io/lexsync/r/reference/run_pipeline.md)
takes a design path and does everything this vignette has done by hand,
plus the datasheet and the run log. From a clone of the repository:

``` r

run_pipeline("config/design_en_freqcontrast.yaml")   # schema_path defaults to config/schema.yaml
run_all()                                            # every design_*.yaml in config/
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

| group | dimension |   n |  mean |    sd | min | median |   max |
|:------|:----------|----:|------:|------:|----:|-------:|------:|
| high  | length    |  15 | 4.533 | 0.915 | 3.0 |   4.00 |  6.00 |
| high  | frequency |  15 | 5.589 | 0.424 | 5.2 |   5.49 |  6.85 |
| high  | n_density |  15 | 7.800 | 6.190 | 1.0 |   5.00 | 24.00 |
| high  | old20     |  15 | 1.467 | 0.286 | 1.0 |   1.55 |  1.90 |
| low   | length    |  15 | 4.533 | 0.915 | 3.0 |   4.00 |  6.00 |
| low   | frequency |  15 | 4.146 | 0.203 | 3.8 |   4.14 |  4.40 |
| low   | n_density |  15 | 7.867 | 5.604 | 1.0 |   5.00 | 20.00 |
| low   | old20     |  15 | 1.473 | 0.293 | 1.0 |   1.60 |  1.90 |

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

| condition | reference | dimension | cohens_d | d_ci_low | d_ci_high | var_ratio | tost_p | equivalent |
|:---|:---|:---|---:|---:|---:|---:|---:|:---|
| low | high | length | 0.000 | -0.621 | 0.621 | 1.000 | 0.0909 | FALSE |
| low | high | frequency | 4.343 | 3.722 | 4.964 | 0.229 | 1.0000 | FALSE |
| low | high | n_density | -0.011 | -0.632 | 0.610 | 0.820 | 0.0958 | FALSE |
| low | high | old20 | -0.023 | -0.644 | 0.598 | 1.044 | 0.1010 | FALSE |

Standardised mean differences with 90% confidence intervals, plus the
complementary TOST equivalence test {.table}

The manipulated dimension (frequency) differs strongly, while the
controlled dimensions (length, neighbourhood density and OLD20) are
closely equated. The report leads with the standardised mean difference
(`cohens_d`) and its 90% confidence interval (`d_ci_low`, `d_ci_high`).
A non-significant difference test is not evidence of matching, and its
outcome depends on the number of items. The effect size and its
interval, whose upper limit is the largest imbalance still consistent
with the stimuli, are therefore the primary summary. The TOST
equivalence test is reported alongside as a bound-referenced verdict.

## Generate the experiment scripts

The trial is described once, as a sequence of events, and each
presentation target renders that same description. One call therefore
produces all three.

``` r

out <- file.path(tempdir(), "lexsync_demo")
dir.create(out, showWarnings = FALSE)
files <- export_experiments(stim, design, schema, out)
basename(unlist(files))
```

    [1] "vignette_demo_english_psychopy.py" "vignette_demo_english.osexp"      
    [3] "vignette_demo_english.html"       

Three experiments are generated from one description of the trial. The
PsychoPy script binds each onset trigger to the stimulus flip with
`win.callOnFlip`. The OpenSesame `.osexp` draws and shows the word
inside an `inline_script` and sends the marker immediately after
`show()` returns, which it does at the display refresh. The jsPsych HTML
runs the same procedure in a browser and records the trigger codes in
the trial data, since a browser cannot address a parallel port. Neither
the matching nor the script generation requires PsychoPy, OpenSesame or
any hardware to be installed.

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
