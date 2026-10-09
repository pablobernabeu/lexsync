# Materials datasheet -- zh_freqcontrast (chinese)

*lexsync datasheet v1.2; R engine.*

## Provenance

- **Paradigm:** factorial  |  **Item source:** corpus
- **Description:** High versus low frequency Mandarin Chinese two-character words, matched on character-length and character-level neighbourhood (N, OLD20).
- **Materials source:** `corpora/derived/zh.csv` (sha256 `74666b257c1ad7bc...`)
- **Selection:** standardised_euclidean
- **Cross-engine determinism:** byte-identical
- **Counterbalancing:** factorial, 1 list(s)
- **Items:** 160 rows across 2 conditions (low_frequency, high_frequency)
- **Seed:** 2026  |  **Versions:** engine R, lexsync 0.1.1, R 4.6.1, readr 2.2.0, stringdist 0.9.17, jsonlite 2.0.0, digest 0.6.39, yaml 2.3.12, stringi 1.8.7, os Windows x86-64

## Counterbalanced lists

| List | Condition | Trials |
|---|---|---|
| 1 | high_frequency | 80 |
| 1 | low_frequency | 80 |

## Selection transparency

- **Candidate pool** (items satisfying each condition's window before matching): high_frequency: 948, low_frequency: 9183.
- Selection is a deterministic function of the materials source, the design and the schema, blind to any outcome measure, and does not depend on the seed, which fixes the trial order. Exact ties between equally close candidates are broken by spelling, in byte order, as lexsync 0.1 did, so every tie goes to the spelling that sorts first. Automating the choice removes the experimenter's discretion that Forster (2000) showed can bias item selection.

## Realised control

Each row compares a condition with its reference. The raw difference and Cohen's d are the reference mean minus the condition mean, and the variance ratio is the condition's variance over the reference's.

| Condition | Reference | Dimension | Role | Raw difference | Cohen's d | 90% CI | Var ratio | TOST p | Equivalent |
|---|---|---|---|---|---|---|---|---|---|
| low_frequency | high_frequency | length | controlled | 0.000 | 0.00 | [0.00, 0.00] | 1.00 | < 0.0001 | TRUE |
| low_frequency | high_frequency | frequency | manipulated | 1.514 | 6.00 | [5.39, 6.62] | 0.47 | 1.0000 | FALSE |
| low_frequency | high_frequency | n_density | controlled | 4.163 | 0.07 | [-0.19, 0.33] | 0.65 | 0.0037 | TRUE |
| low_frequency | high_frequency | old20 | controlled | 0.010 | 0.11 | [-0.16, 0.37] | 0.44 | 0.0069 | TRUE |
| low_frequency | high_frequency | bigram_freq | uncontrolled | 0.000 | 0.77 | [0.50, 1.04] | 0.07 | 0.9563 | FALSE |

## Suggested analysis

- **Model:** `response ~ condition + scale(n_density, scale = FALSE) + scale(old20, scale = FALSE) + (1 + condition | subject) + (1 | item)` -- where the response is reaction time from the onset of `{word}`; responses collected for 2500 ms; a response ends the trial.
- Crossed random effects for subjects and items guard against the language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). The matched dimensions enter as centred covariates, computed from the stimuli file's own columns, because matching leaves residual differences that the analysis can adjust for (Sassenhagen & Alday, 2016). The matched dimension length is constant among the selected items, so it is left out. Begin with random slopes for condition, the manipulated factor, by subject and, where it varies within items, by item (Barr et al., 2013); the matched covariates enter as fixed effects only. If the model is singular or fails to converge, simplify it as Matuschek et al. (2017) describe. The formula is lme4 syntax, for lme4 in R or pymer4 in Python; statsmodels MixedLM cannot take it directly and needs the random effects restated in its own arguments. The equivalence tests in the realised control are post-selection diagnostics on deterministically selected items, not inferential tests over a sample.

## Methods paragraph

80 items per condition were selected from the Chinese lexicon (wordfreq (Speer, 2022), data CC BY-SA 4.0; full corpus licence and citation at https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md) and matched item by item on length, n_density, old20 using lexsync's standardised_euclidean matcher. The largest difference on a matched dimension was 0.010 mean Levenshtein distance in old20 (high_frequency against low_frequency; d = 0.11, 90% CI [-0.16, 0.37]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) supported equivalence on 3 of 3 matched comparisons. Dimensions the design did not control differed: bigram_freq (high_frequency against low_frequency: under 0.001 mean bigram probability; d = 0.77, 90% CI [0.50, 1.04]). The smallest condition was selected from 948 eligible candidates, and the selection was deterministic and blind to any outcome measure. Materials were counterbalanced into 1 list(s) (a factorial split) and generated for PsychoPy, OpenSesame and jsPsych. Responses were collected from target onset until 2500 ms after it, and a response ended the trial. The selection is deterministic and reproducible (lexsync 0.1.1), and the seed (2026) fixes the trial order.

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
80 items per condition were selected from the Chinese lexicon (wordfreq (Speer, 2022), data CC BY-SA 4.0; full corpus licence and citation at https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md) and matched item by item on length, n_density, old20 using lexsync's standardised_euclidean matcher. The largest difference on a matched dimension was 0.010 mean Levenshtein distance in old20 (high_frequency against low_frequency; d = 0.11, 90% CI [-0.16, 0.37]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) supported equivalence on 3 of 3 matched comparisons. Dimensions the design did not control differed: bigram_freq (high_frequency against low_frequency: under 0.001 mean bigram probability; d = 0.77, 90% CI [0.50, 1.04]). The smallest condition was selected from 948 eligible candidates, and the selection was deterministic and blind to any outcome measure. Materials were counterbalanced into 1 list(s) (a factorial split) and generated for PsychoPy, OpenSesame and jsPsych. Responses were collected from target onset until 2500 ms after it, and a response ended the trial. The selection is deterministic and reproducible (lexsync 0.1.1), and the seed (2026) fixes the trial order.

### Sampling plan
- Sample size and justification:
- Stopping rule:

### Analysis plan
- Statistical model: response ~ condition + scale(n_density, scale = FALSE) + scale(old20, scale = FALSE) + (1 + condition | subject) + (1 | item)
  (Crossed random effects for subjects and items guard against the language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). The matched dimensions enter as centred covariates, computed from the stimuli file's own columns, because matching leaves residual differences that the analysis can adjust for (Sassenhagen & Alday, 2016). The matched dimension length is constant among the selected items, so it is left out. Begin with random slopes for condition, the manipulated factor, by subject and, where it varies within items, by item (Barr et al., 2013); the matched covariates enter as fixed effects only. If the model is singular or fails to converge, simplify it as Matuschek et al. (2017) describe. The formula is lme4 syntax, for lme4 in R or pymer4 in Python; statsmodels MixedLM cannot take it directly and needs the random effects restated in its own arguments. The equivalence tests in the realised control are post-selection diagnostics on deterministically selected items, not inferential tests over a sample.)
- Inference criteria:
- Treatment of items (e.g. items as a random factor):

