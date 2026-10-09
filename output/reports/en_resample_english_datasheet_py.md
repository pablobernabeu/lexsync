# Materials datasheet — en_resample (english)

*lexsync datasheet v1.2; python engine.*

## Provenance

- **Paradigm:** factorial  |  **Item source:** corpus
- **Description:** High versus low frequency English words in three disjoint matched item sets (items as a random factor).
- **Materials source:** `corpora/derived/en.csv` (sha256 `575833489e04d6a4…`)
- **Selection:** standardised_euclidean
- **Cross-engine determinism:** byte-identical
- **Counterbalancing:** factorial, 1 list(s)
- **Presentation versions:** 3, assigned as version = ((participant - 1) mod 3) + 1 unless a version is given at launch
- **Items:** 240 rows across 2 conditions (low_frequency, high_frequency)
- **Seed:** 2026  |  **Versions:** engine python, lexsync 0.1.1, python 3.13.7, pandas 2.3.2, numpy 2.3.2, scipy 1.17.1, rapidfuzz 3.14.5, pyyaml 6.0.3, os Windows AMD64

## Counterbalanced lists

| Replicate | List | Condition | Trials |
|---|---|---|---|
| 1 | 1 | high_frequency | 40 |
| 1 | 1 | low_frequency | 40 |
| 2 | 1 | high_frequency | 40 |
| 2 | 1 | low_frequency | 40 |
| 3 | 1 | high_frequency | 40 |
| 3 | 1 | low_frequency | 40 |

## Selection transparency

- **Candidate pool** (items satisfying each condition's window before matching): high_frequency: 462, low_frequency: 7479.
- Selection is a deterministic function of the materials source, the design and the schema, blind to any outcome measure, and does not depend on the seed, which fixes the trial order. Exact ties between equally close candidates are broken by spelling, in byte order, as lexsync 0.1 did, so every tie goes to the spelling that sorts first. Automating the choice removes the experimenter's discretion that Forster (2000) showed can bias item selection.

## Realised control

Each row compares a condition with its reference. The raw difference and Cohen's d are the reference mean minus the condition mean, and the variance ratio is the condition's variance over the reference's.

| Condition | Reference | Dimension | Role | Raw difference | Cohen's d | 90% CI | Var ratio | TOST p | Equivalent |
|---|---|---|---|---|---|---|---|---|---|
| low_frequency | high_frequency | length | controlled | 0.050 | 0.04 | [-0.17, 0.26] | 0.86 | 0.0002 | True |
| low_frequency | high_frequency | frequency | manipulated | 1.642 | 5.38 | [4.92, 5.84] | 0.59 | 1.0000 | False |
| low_frequency | high_frequency | n_density | controlled | 0.158 | 0.03 | [-0.18, 0.25] | 0.87 | 0.0002 | True |
| low_frequency | high_frequency | old20 | controlled | 0.008 | 0.02 | [-0.20, 0.23] | 0.90 | 0.0001 | True |
| low_frequency | high_frequency | n_syllables | uncontrolled | -0.242 | -0.34 | [-0.56, -0.13] | 0.96 | 0.1091 | False |
| low_frequency | high_frequency | bigram_freq | uncontrolled | 0.000 | -0.03 | [-0.24, 0.18] | 0.98 | 0.0002 | True |

## Suggested analysis

- **Model:** `response ~ condition + scale(length, scale = FALSE) + scale(n_density, scale = FALSE) + scale(old20, scale = FALSE) + (1 + condition | subject) + (1 | item)` — where the response is reaction time from the onset of `{word}`; responses collected for 2500 ms; a response ends the trial.
- Crossed random effects for subjects and items guard against the language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). The matched dimensions enter as centred covariates, computed from the stimuli file's own columns, because matching leaves residual differences that the analysis can adjust for (Sassenhagen & Alday, 2016). Begin with random slopes for condition, the manipulated factor, by subject and, where it varies within items, by item (Barr et al., 2013); the matched covariates enter as fixed effects only. If the model is singular or fails to converge, simplify it as Matuschek et al. (2017) describe. The formula is lme4 syntax, for lme4 in R or pymer4 in Python; statsmodels MixedLM cannot take it directly and needs the random effects restated in its own arguments. The equivalence tests in the realised control are post-selection diagnostics on deterministically selected items, not inferential tests over a sample.

## Methods paragraph

40 items per condition were selected from the English lexicon (wordfreq (Speer, 2022), data CC BY-SA 4.0; full corpus licence and citation at https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md) and matched item by item on length, n_density, old20 using lexsync's standardised_euclidean matcher. The largest difference on a matched dimension was 0.050 characters in length (high_frequency against low_frequency; d = 0.04, 90% CI [-0.17, 0.26]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) supported equivalence on 3 of 3 matched comparisons. No uncontrolled dimension differed by more than 0.5 SD. The smallest condition was selected from 462 eligible candidates, and the selection was deterministic and blind to any outcome measure. 3 disjoint matched item sets were drawn, so items can be treated as a random factor. Materials were counterbalanced into 1 list(s) (a factorial split) and generated for PsychoPy, OpenSesame and jsPsych. Each participant was presented one of the 3 presentation versions (one list of one item set), assigned in rotation by participant number. Responses were collected from target onset until 2500 ms after it, and a response ended the trial. The selection is deterministic and reproducible (lexsync 0.1.1), and the seed (2026) fixes the trial order.

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
40 items per condition were selected from the English lexicon (wordfreq (Speer, 2022), data CC BY-SA 4.0; full corpus licence and citation at https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md) and matched item by item on length, n_density, old20 using lexsync's standardised_euclidean matcher. The largest difference on a matched dimension was 0.050 characters in length (high_frequency against low_frequency; d = 0.04, 90% CI [-0.17, 0.26]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) supported equivalence on 3 of 3 matched comparisons. No uncontrolled dimension differed by more than 0.5 SD. The smallest condition was selected from 462 eligible candidates, and the selection was deterministic and blind to any outcome measure. 3 disjoint matched item sets were drawn, so items can be treated as a random factor. Materials were counterbalanced into 1 list(s) (a factorial split) and generated for PsychoPy, OpenSesame and jsPsych. Each participant was presented one of the 3 presentation versions (one list of one item set), assigned in rotation by participant number. Responses were collected from target onset until 2500 ms after it, and a response ended the trial. The selection is deterministic and reproducible (lexsync 0.1.1), and the seed (2026) fixes the trial order.

### Sampling plan
- Sample size and justification:
- Stopping rule:

### Analysis plan
- Statistical model: response ~ condition + scale(length, scale = FALSE) + scale(n_density, scale = FALSE) + scale(old20, scale = FALSE) + (1 + condition | subject) + (1 | item)
  (Crossed random effects for subjects and items guard against the language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). The matched dimensions enter as centred covariates, computed from the stimuli file's own columns, because matching leaves residual differences that the analysis can adjust for (Sassenhagen & Alday, 2016). Begin with random slopes for condition, the manipulated factor, by subject and, where it varies within items, by item (Barr et al., 2013); the matched covariates enter as fixed effects only. If the model is singular or fails to converge, simplify it as Matuschek et al. (2017) describe. The formula is lme4 syntax, for lme4 in R or pymer4 in Python; statsmodels MixedLM cannot take it directly and needs the random effects restated in its own arguments. The equivalence tests in the realised control are post-selection diagnostics on deterministically selected items, not inferential tests over a sample.)
- Inference criteria:
- Treatment of items (e.g. items as a random factor):

