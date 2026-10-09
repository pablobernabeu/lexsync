# Materials datasheet -- en_supplied_pool (english)

*lexsync datasheet v1.2; R engine.*

## Provenance

- **Paradigm:** factorial  |  **Item source:** pool
- **Description:** Concrete nouns from a supplied candidate pool, split by frequency and matched item by item on length, neighbourhood density and OLD20.
- **Materials source:** `items/pool_en_concrete_nouns.csv` (sha256 `09d0706a853b4bb3...`)
- **Dimensions from:** `corpora/derived/en.csv` (sha256 `575833489e04d6a4...`)
- **Selection:** standardised_euclidean
- **Cross-engine determinism:** byte-identical
- **Counterbalancing:** factorial, 1 list(s)
- **Items:** 40 rows across 2 conditions (lower_frequency, higher_frequency)
- **Seed:** 2026  |  **Versions:** engine R, lexsync 0.1.1, R 4.6.1, readr 2.2.0, stringdist 0.9.17, jsonlite 2.0.0, digest 0.6.39, yaml 2.3.12, stringi 1.8.7, os Windows x86-64

## Counterbalanced lists

| List | Condition | Trials |
|---|---|---|
| 1 | higher_frequency | 20 |
| 1 | lower_frequency | 20 |

## Selection transparency

- **Candidate pool** (items satisfying each condition's window before matching): higher_frequency: 31, lower_frequency: 95.
- Selection is a deterministic function of the materials source, the design and the schema, blind to any outcome measure, and does not depend on the seed, which fixes the trial order. Exact ties between equally close candidates are broken by spelling, in byte order, as lexsync 0.1 did, so every tie goes to the spelling that sorts first. Automating the choice removes the experimenter's discretion that Forster (2000) showed can bias item selection.

## Realised control

Each row compares a condition with its reference. The raw difference and Cohen's d are the reference mean minus the condition mean, and the variance ratio is the condition's variance over the reference's.

| Condition | Reference | Dimension | Role | Raw difference | Cohen's d | 90% CI | Var ratio | TOST p | Equivalent |
|---|---|---|---|---|---|---|---|---|---|
| lower_frequency | higher_frequency | length | controlled | -0.050 | -0.11 | [-0.64, 0.42] | 0.89 | 0.1121 | FALSE |
| lower_frequency | higher_frequency | frequency | manipulated | 1.023 | 3.53 | [2.68, 4.38] | 0.83 | 1.0000 | FALSE |
| lower_frequency | higher_frequency | n_density | controlled | 0.300 | 0.13 | [-0.40, 0.66] | 0.83 | 0.1245 | FALSE |
| lower_frequency | higher_frequency | old20 | controlled | -0.058 | -0.24 | [-0.78, 0.29] | 0.62 | 0.2093 | FALSE |
| lower_frequency | higher_frequency | n_syllables | uncontrolled | 0.050 | 0.12 | [-0.42, 0.65] | 0.74 | 0.1166 | FALSE |
| lower_frequency | higher_frequency | bigram_freq | uncontrolled | 0.001 | 0.28 | [-0.25, 0.82] | 0.76 | 0.2486 | FALSE |

## Suggested analysis

- **Model:** `response ~ condition + scale(length, scale = FALSE) + scale(n_density, scale = FALSE) + scale(old20, scale = FALSE) + (1 + condition | subject) + (1 | item)` -- where the response is reaction time from the onset of `{word}`; responses collected for 2500 ms; a response ends the trial.
- Crossed random effects for subjects and items guard against the language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). The matched dimensions enter as centred covariates, computed from the stimuli file's own columns, because matching leaves residual differences that the analysis can adjust for (Sassenhagen & Alday, 2016). Begin with random slopes for condition, the manipulated factor, by subject and, where it varies within items, by item (Barr et al., 2013); the matched covariates enter as fixed effects only. If the model is singular or fails to converge, simplify it as Matuschek et al. (2017) describe. The formula is lme4 syntax, for lme4 in R or pymer4 in Python; statsmodels MixedLM cannot take it directly and needs the random effects restated in its own arguments. The equivalence tests in the realised control are post-selection diagnostics on deterministically selected items, not inferential tests over a sample.

## Methods paragraph

20 English items per condition were selected from a supplied candidate pool and matched item by item on length, n_density, old20 using lexsync's standardised_euclidean matcher, with the matched dimensions taken from corpora/derived/en.csv. The largest difference on a matched dimension was -0.058 mean Levenshtein distance in old20 (higher_frequency against lower_frequency; d = -0.24, 90% CI [-0.78, 0.29]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) supported equivalence on 0 of 3 matched comparisons; with 20 items per condition no dimension that varies can pass this test, however well matched. No uncontrolled dimension differed by more than 0.5 SD. The smallest condition was selected from 31 eligible candidates, and the selection was deterministic and blind to any outcome measure. Materials were counterbalanced into 1 list(s) (a factorial split) and generated for PsychoPy, OpenSesame and jsPsych. Responses were collected from target onset until 2500 ms after it, and a response ended the trial. The selection is deterministic and reproducible (lexsync 0.1.1), and the seed (2026) fixes the trial order.

## Pre-registration template

*Auto-generated by lexsync. The Materials section is filled from the datasheet; complete the remaining sections before data collection.*

### Study information
- Title:
- Authors:
- Research questions:

### Hypotheses
- H1:

### Design
- Manipulated variable(s):
- Measured variable(s):
- Paradigm: factorial

### Materials (from the lexsync datasheet)
20 English items per condition were selected from a supplied candidate pool and matched item by item on length, n_density, old20 using lexsync's standardised_euclidean matcher, with the matched dimensions taken from corpora/derived/en.csv. The largest difference on a matched dimension was -0.058 mean Levenshtein distance in old20 (higher_frequency against lower_frequency; d = -0.24, 90% CI [-0.78, 0.29]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) supported equivalence on 0 of 3 matched comparisons; with 20 items per condition no dimension that varies can pass this test, however well matched. No uncontrolled dimension differed by more than 0.5 SD. The smallest condition was selected from 31 eligible candidates, and the selection was deterministic and blind to any outcome measure. Materials were counterbalanced into 1 list(s) (a factorial split) and generated for PsychoPy, OpenSesame and jsPsych. Responses were collected from target onset until 2500 ms after it, and a response ended the trial. The selection is deterministic and reproducible (lexsync 0.1.1), and the seed (2026) fixes the trial order.

### Sampling plan
- Sample size and justification:
- Stopping rule:

### Analysis plan
- Statistical model: response ~ condition + scale(length, scale = FALSE) + scale(n_density, scale = FALSE) + scale(old20, scale = FALSE) + (1 + condition | subject) + (1 | item)
  (Crossed random effects for subjects and items guard against the language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). The matched dimensions enter as centred covariates, computed from the stimuli file's own columns, because matching leaves residual differences that the analysis can adjust for (Sassenhagen & Alday, 2016). Begin with random slopes for condition, the manipulated factor, by subject and, where it varies within items, by item (Barr et al., 2013); the matched covariates enter as fixed effects only. If the model is singular or fails to converge, simplify it as Matuschek et al. (2017) describe. The formula is lme4 syntax, for lme4 in R or pymer4 in Python; statsmodels MixedLM cannot take it directly and needs the random effects restated in its own arguments. The equivalence tests in the realised control are post-selection diagnostics on deterministically selected items, not inferential tests over a sample.)
- Inference criteria:
- Treatment of items (e.g. items as a random factor):

