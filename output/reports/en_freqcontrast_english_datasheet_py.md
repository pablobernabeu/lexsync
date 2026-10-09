# Materials datasheet — en_freqcontrast (english)

*lexsync datasheet v1.2; python engine.*

## Provenance

- **Paradigm:** factorial  |  **Item source:** corpus
- **Description:** High versus low frequency English words, matched on length, neighbourhood density and OLD20.
- **Materials source:** `corpora/derived/en_v2.csv` (sha256 `46815cd56ac036cb…`)
- **Excluded words:** `config/exclude_en_demo.txt` (53 words, 53 removed, sha256 `cac9f88fb86fa6d0…`)
- **Selection:** standardised_euclidean
- **Cross-engine determinism:** byte-identical
- **Counterbalancing:** factorial, 1 list(s)
- **Items:** 160 rows across 2 conditions (low_frequency, high_frequency)
- **Seed:** 2026  |  **Versions:** engine python, lexsync 0.1.1, python 3.13.7, pandas 2.3.2, numpy 2.3.2, scipy 1.17.1, rapidfuzz 3.14.5, pyyaml 6.0.3, os Windows AMD64

## Counterbalanced lists

| List | Condition | Trials |
|---|---|---|
| 1 | high_frequency | 80 |
| 1 | low_frequency | 80 |

## Selection transparency

- **Candidate pool** (items satisfying each condition's window before matching): high_frequency: 534, low_frequency: 3583.
- Selection is a deterministic function of the materials source, the design and the schema, blind to any outcome measure, and does not depend on the seed, which fixes the trial order. Exact ties between equally close candidates are broken by a keyed hash of each word (salt lexsync-tie-v1), so no part of the alphabet is favoured. Automating the choice removes the experimenter's discretion that Forster (2000) showed can bias item selection.

## Realised control

Each row compares a condition with its reference. The raw difference and Cohen's d are the reference mean minus the condition mean, and the variance ratio is the condition's variance over the reference's.

| Condition | Reference | Dimension | Role | Raw difference | Cohen's d | 90% CI | Var ratio | TOST p | Equivalent |
|---|---|---|---|---|---|---|---|---|---|
| low_frequency | high_frequency | length | controlled | 0.037 | 0.03 | [-0.23, 0.29] | 0.88 | 0.0017 | True |
| low_frequency | high_frequency | frequency | manipulated | 1.513 | 5.29 | [4.74, 5.85] | 0.19 | 1.0000 | False |
| low_frequency | high_frequency | n_density | controlled | 0.325 | 0.06 | [-0.21, 0.32] | 0.75 | 0.0028 | True |
| low_frequency | high_frequency | old20 | controlled | 0.011 | 0.02 | [-0.24, 0.28] | 0.82 | 0.0015 | True |
| low_frequency | high_frequency | n_syllables | uncontrolled | -0.012 | -0.02 | [-0.28, 0.24] | 1.29 | 0.0014 | True |
| low_frequency | high_frequency | bigram_freq | uncontrolled | 0.000 | 0.01 | [-0.25, 0.27] | 1.39 | 0.0011 | True |

## Suggested analysis

- **Model:** `response ~ condition + scale(length, scale = FALSE) + scale(n_density, scale = FALSE) + scale(old20, scale = FALSE) + (1 + condition | subject) + (1 | item)` — where the response is reaction time from the onset of `{word}`; responses collected for 2500 ms; a response ends the trial.
- Crossed random effects for subjects and items guard against the language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). The matched dimensions enter as centred covariates, computed from the stimuli file's own columns, because matching leaves residual differences that the analysis can adjust for (Sassenhagen & Alday, 2016). Begin with random slopes for condition, the manipulated factor, by subject and, where it varies within items, by item (Barr et al., 2013); the matched covariates enter as fixed effects only. If the model is singular or fails to converge, simplify it as Matuschek et al. (2017) describe. The formula is lme4 syntax, for lme4 in R or pymer4 in Python; statsmodels MixedLM cannot take it directly and needs the random effects restated in its own arguments. The equivalence tests in the realised control are post-selection diagnostics on deterministically selected items, not inferential tests over a sample.

## Methods paragraph

80 items per condition were selected from the English lexicon (wordfreq (Speer, 2022) screened against SUBTLEX-US (Brysbaert & New, 2009), data CC BY-SA 4.0; forms absent from SUBTLEX-US or beginning with a lower-case letter in under 10% of their uses are marked nonstandard, and N and OLD20 count only the unmarked forms; full corpus licence and citation at https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md) and matched item by item on length, n_density, old20 using lexsync's standardised_euclidean matcher. The largest difference on a matched dimension was 0.325 neighbours in n_density (high_frequency against low_frequency; d = 0.06, 90% CI [-0.21, 0.32]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) supported equivalence on 3 of 3 matched comparisons. No uncontrolled dimension differed by more than 0.5 SD. An exclusion list (exclude_en_demo.txt) removed 53 words from the candidates before selection. The smallest condition was selected from 534 eligible candidates, and the selection was deterministic and blind to any outcome measure. Materials were counterbalanced into 1 list(s) (a factorial split) and generated for PsychoPy, OpenSesame and jsPsych. Responses were collected from target onset until 2500 ms after it, and a response ended the trial. The selection is deterministic and reproducible (lexsync 0.1.1), and the seed (2026) fixes the trial order.

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
80 items per condition were selected from the English lexicon (wordfreq (Speer, 2022) screened against SUBTLEX-US (Brysbaert & New, 2009), data CC BY-SA 4.0; forms absent from SUBTLEX-US or beginning with a lower-case letter in under 10% of their uses are marked nonstandard, and N and OLD20 count only the unmarked forms; full corpus licence and citation at https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md) and matched item by item on length, n_density, old20 using lexsync's standardised_euclidean matcher. The largest difference on a matched dimension was 0.325 neighbours in n_density (high_frequency against low_frequency; d = 0.06, 90% CI [-0.21, 0.32]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) supported equivalence on 3 of 3 matched comparisons. No uncontrolled dimension differed by more than 0.5 SD. An exclusion list (exclude_en_demo.txt) removed 53 words from the candidates before selection. The smallest condition was selected from 534 eligible candidates, and the selection was deterministic and blind to any outcome measure. Materials were counterbalanced into 1 list(s) (a factorial split) and generated for PsychoPy, OpenSesame and jsPsych. Responses were collected from target onset until 2500 ms after it, and a response ended the trial. The selection is deterministic and reproducible (lexsync 0.1.1), and the seed (2026) fixes the trial order.

### Sampling plan
- Sample size and justification:
- Stopping rule:

### Analysis plan
- Statistical model: response ~ condition + scale(length, scale = FALSE) + scale(n_density, scale = FALSE) + scale(old20, scale = FALSE) + (1 + condition | subject) + (1 | item)
  (Crossed random effects for subjects and items guard against the language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). The matched dimensions enter as centred covariates, computed from the stimuli file's own columns, because matching leaves residual differences that the analysis can adjust for (Sassenhagen & Alday, 2016). Begin with random slopes for condition, the manipulated factor, by subject and, where it varies within items, by item (Barr et al., 2013); the matched covariates enter as fixed effects only. If the model is singular or fails to converge, simplify it as Matuschek et al. (2017) describe. The formula is lme4 syntax, for lme4 in R or pymer4 in Python; statsmodels MixedLM cannot take it directly and needs the random effects restated in its own arguments. The equivalence tests in the realised control are post-selection diagnostics on deterministically selected items, not inferential tests over a sample.)
- Inference criteria:
- Treatment of items (e.g. items as a random factor):

