# Materials datasheet -- es_ndensity (spanish)

*lexsync datasheet v1.2; R engine.*

## Provenance

- **Paradigm:** factorial  |  **Item source:** corpus
- **Description:** Dense versus sparse orthographic neighbourhoods (Coltheart's N) in Spanish, matched on length and frequency.
- **Materials source:** `corpora/derived/es.csv` (sha256 `e9f93013c16ec974...`)
- **Selection:** joint
- **Cross-engine determinism:** byte-identical
- **Counterbalancing:** factorial, 1 list(s)
- **Items:** 160 rows across 2 conditions (dense_neighbourhood, sparse_neighbourhood)
- **Seed:** 2026  |  **Versions:** engine R, lexsync 0.1.1, R 4.6.1, readr 2.2.0, stringdist 0.9.17, jsonlite 2.0.0, digest 0.6.39, yaml 2.3.12, stringi 1.8.7, os Windows x86-64

## Counterbalanced lists

| List | Condition | Trials |
|---|---|---|
| 1 | dense_neighbourhood | 80 |
| 1 | sparse_neighbourhood | 80 |

## Selection transparency

- **Candidate pool** (items satisfying each condition's window before matching): dense_neighbourhood: 1324, sparse_neighbourhood: 1137.
- Selection is a deterministic function of the materials source, the design and the schema, blind to any outcome measure, and does not depend on the seed, which fixes the trial order. Exact ties between equally close candidates are broken by a keyed hash of each word (salt lexsync-tie-v1), so no part of the alphabet is favoured. Automating the choice removes the experimenter's discretion that Forster (2000) showed can bias item selection.

## Realised control

Each row compares a condition with its reference. The raw difference and Cohen's d are the reference mean minus the condition mean, and the variance ratio is the condition's variance over the reference's.

| Condition | Reference | Dimension | Role | Raw difference | Cohen's d | 90% CI | Var ratio | TOST p | Equivalent |
|---|---|---|---|---|---|---|---|---|---|
| sparse_neighbourhood | dense_neighbourhood | length | controlled | 0.000 | 0.00 | [-0.26, 0.26] | 1.00 | 0.0009 | TRUE |
| sparse_neighbourhood | dense_neighbourhood | frequency | controlled | 0.000 | 0.00 | [-0.26, 0.26] | 1.00 | 0.0009 | TRUE |
| sparse_neighbourhood | dense_neighbourhood | n_density | manipulated | 7.413 | 3.06 | [2.67, 3.44] | 0.02 | 1.0000 | FALSE |
| sparse_neighbourhood | dense_neighbourhood | old20 | uncontrolled | -0.519 | -2.57 | [-2.92, -2.22] | 1.12 | 1.0000 | FALSE |
| sparse_neighbourhood | dense_neighbourhood | n_syllables | uncontrolled | 0.025 | 0.05 | [-0.21, 0.31] | 3.50 | 0.0025 | TRUE |
| sparse_neighbourhood | dense_neighbourhood | bigram_freq | uncontrolled | 0.003 | 0.94 | [0.67, 1.22] | 1.18 | 0.9971 | FALSE |

## Suggested analysis

- **Model:** `response ~ condition + scale(length, scale = FALSE) + scale(frequency, scale = FALSE) + (1 + condition | subject) + (1 | item)` -- where the response is reaction time from the onset of `{word}`; responses collected for 2500 ms; a response ends the trial.
- Crossed random effects for subjects and items guard against the language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). The matched dimensions enter as centred covariates, computed from the stimuli file's own columns, because matching leaves residual differences that the analysis can adjust for (Sassenhagen & Alday, 2016). Begin with random slopes for condition, the manipulated factor, by subject and, where it varies within items, by item (Barr et al., 2013); the matched covariates enter as fixed effects only. If the model is singular or fails to converge, simplify it as Matuschek et al. (2017) describe. The formula is lme4 syntax, for lme4 in R or pymer4 in Python; statsmodels MixedLM cannot take it directly and needs the random effects restated in its own arguments. The equivalence tests in the realised control are post-selection diagnostics on deterministically selected items, not inferential tests over a sample.

## Methods paragraph

80 items per condition were selected from the Spanish lexicon (wordfreq (Speer, 2022), data CC BY-SA 4.0; full corpus licence and citation at https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md) and matched item by item on length, frequency using lexsync's joint matcher. The largest difference on a matched dimension was 0.000 characters in length (dense_neighbourhood against sparse_neighbourhood; d = 0.00, 90% CI [-0.26, 0.26]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) supported equivalence on 2 of 2 matched comparisons. Dimensions the design did not control differed: old20 (dense_neighbourhood against sparse_neighbourhood: -0.519 mean Levenshtein distance; d = -2.57, 90% CI [-2.92, -2.22]) and bigram_freq (dense_neighbourhood against sparse_neighbourhood: 0.003 mean bigram probability; d = 0.94, 90% CI [0.67, 1.22]). The smallest condition was selected from 1137 eligible candidates, and the selection was deterministic and blind to any outcome measure. Each candidate pool exceeding the pairwise cap was reduced to the 1200 candidates nearest the other condition's centroid before pairing. Materials were counterbalanced into 1 list(s) (a factorial split) and generated for PsychoPy, OpenSesame and jsPsych. Responses were collected from target onset until 2500 ms after it, and a response ended the trial. The selection is deterministic and reproducible (lexsync 0.1.1), and the seed (2026) fixes the trial order.

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
80 items per condition were selected from the Spanish lexicon (wordfreq (Speer, 2022), data CC BY-SA 4.0; full corpus licence and citation at https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md) and matched item by item on length, frequency using lexsync's joint matcher. The largest difference on a matched dimension was 0.000 characters in length (dense_neighbourhood against sparse_neighbourhood; d = 0.00, 90% CI [-0.26, 0.26]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) supported equivalence on 2 of 2 matched comparisons. Dimensions the design did not control differed: old20 (dense_neighbourhood against sparse_neighbourhood: -0.519 mean Levenshtein distance; d = -2.57, 90% CI [-2.92, -2.22]) and bigram_freq (dense_neighbourhood against sparse_neighbourhood: 0.003 mean bigram probability; d = 0.94, 90% CI [0.67, 1.22]). The smallest condition was selected from 1137 eligible candidates, and the selection was deterministic and blind to any outcome measure. Each candidate pool exceeding the pairwise cap was reduced to the 1200 candidates nearest the other condition's centroid before pairing. Materials were counterbalanced into 1 list(s) (a factorial split) and generated for PsychoPy, OpenSesame and jsPsych. Responses were collected from target onset until 2500 ms after it, and a response ended the trial. The selection is deterministic and reproducible (lexsync 0.1.1), and the seed (2026) fixes the trial order.

### Sampling plan
- Sample size and justification:
- Stopping rule:

### Analysis plan
- Statistical model: response ~ condition + scale(length, scale = FALSE) + scale(frequency, scale = FALSE) + (1 + condition | subject) + (1 | item)
  (Crossed random effects for subjects and items guard against the language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). The matched dimensions enter as centred covariates, computed from the stimuli file's own columns, because matching leaves residual differences that the analysis can adjust for (Sassenhagen & Alday, 2016). Begin with random slopes for condition, the manipulated factor, by subject and, where it varies within items, by item (Barr et al., 2013); the matched covariates enter as fixed effects only. If the model is singular or fails to converge, simplify it as Matuschek et al. (2017) describe. The formula is lme4 syntax, for lme4 in R or pymer4 in Python; statsmodels MixedLM cannot take it directly and needs the random effects restated in its own arguments. The equivalence tests in the realised control are post-selection diagnostics on deterministically selected items, not inferential tests over a sample.)
- Inference criteria:
- Treatment of items (e.g. items as a random factor):

