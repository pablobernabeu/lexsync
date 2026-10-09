# Materials datasheet — en_richdim (english)

*lexsync datasheet v1.2; python engine.*

## Provenance

- **Paradigm:** factorial  |  **Item source:** corpus
- **Description:** High versus low frequency English words, matched on length, syllable count and bigram frequency (a phonotactic-probability proxy).
- **Materials source:** `corpora/derived/en_v2.csv` (sha256 `46815cd56ac036cb…`)
- **Excluded words:** `config/exclude_en_demo.txt` (53 words, 53 removed, sha256 `cac9f88fb86fa6d0…`)
- **Selection:** standardised_euclidean
- **Cross-engine determinism:** byte-identical
- **Counterbalancing:** factorial, 1 list(s)
- **Items:** 120 rows across 2 conditions (low_frequency, high_frequency)
- **Seed:** 2026  |  **Versions:** engine python, lexsync 0.1.1, python 3.13.7, pandas 2.3.2, numpy 2.3.2, scipy 1.17.1, rapidfuzz 3.14.5, pyyaml 6.0.3, os Windows AMD64

## Counterbalanced lists

| List | Condition | Trials |
|---|---|---|
| 1 | high_frequency | 60 |
| 1 | low_frequency | 60 |

## Selection transparency

- **Candidate pool** (items satisfying each condition's window before matching): high_frequency: 453, low_frequency: 6051.
- Selection is a deterministic function of the materials source, the design and the schema, blind to any outcome measure, and does not depend on the seed, which fixes the trial order. Exact ties between equally close candidates are broken by a keyed hash of each word (salt lexsync-tie-v1), so no part of the alphabet is favoured. Automating the choice removes the experimenter's discretion that Forster (2000) showed can bias item selection.

## Realised control

Each row compares a condition with its reference. The raw difference and Cohen's d are the reference mean minus the condition mean, and the variance ratio is the condition's variance over the reference's.

| Condition | Reference | Dimension | Role | Raw difference | Cohen's d | 90% CI | Var ratio | TOST p | Equivalent |
|---|---|---|---|---|---|---|---|---|---|
| low_frequency | high_frequency | length | controlled | 0.000 | 0.00 | [-0.30, 0.30] | 1.00 | 0.0036 | True |
| low_frequency | high_frequency | frequency | manipulated | 1.681 | 5.56 | [4.89, 6.22] | 0.59 | 1.0000 | False |
| low_frequency | high_frequency | n_density | uncontrolled | -0.567 | -0.13 | [-0.43, 0.17] | 1.74 | 0.0221 | True |
| low_frequency | high_frequency | old20 | uncontrolled | -0.042 | -0.07 | [-0.37, 0.23] | 1.24 | 0.0101 | True |
| low_frequency | high_frequency | n_syllables | controlled | 0.017 | 0.02 | [-0.28, 0.32] | 0.91 | 0.0050 | True |
| low_frequency | high_frequency | bigram_freq | controlled | 0.000 | 0.02 | [-0.28, 0.33] | 0.90 | 0.0052 | True |

## Suggested analysis

- **Model:** `response ~ condition + scale(length, scale = FALSE) + scale(n_syllables, scale = FALSE) + scale(bigram_freq, scale = FALSE) + (1 + condition | subject) + (1 | item)` — where the response is reaction time from the onset of `{word}`; responses collected for 2500 ms; a response ends the trial.
- Crossed random effects for subjects and items guard against the language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). The matched dimensions enter as centred covariates, computed from the stimuli file's own columns, because matching leaves residual differences that the analysis can adjust for (Sassenhagen & Alday, 2016). Begin with random slopes for condition, the manipulated factor, by subject and, where it varies within items, by item (Barr et al., 2013); the matched covariates enter as fixed effects only. If the model is singular or fails to converge, simplify it as Matuschek et al. (2017) describe. The formula is lme4 syntax, for lme4 in R or pymer4 in Python; statsmodels MixedLM cannot take it directly and needs the random effects restated in its own arguments. The equivalence tests in the realised control are post-selection diagnostics on deterministically selected items, not inferential tests over a sample.

## Methods paragraph

60 items per condition were selected from the English lexicon (wordfreq (Speer, 2022) screened against SUBTLEX-US (Brysbaert & New, 2009), data CC BY-SA 4.0; forms absent from SUBTLEX-US or beginning with a lower-case letter in under 10% of their uses are marked nonstandard, and N and OLD20 count only the unmarked forms; full corpus licence and citation at https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md) and matched item by item on length, n_syllables, bigram_freq using lexsync's standardised_euclidean matcher. The largest difference on a matched dimension was under 0.001 mean bigram probability in bigram_freq (high_frequency against low_frequency; d = 0.02, 90% CI [-0.28, 0.33]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) supported equivalence on 3 of 3 matched comparisons. No uncontrolled dimension differed by more than 0.5 SD. An exclusion list (exclude_en_demo.txt) removed 53 words from the candidates before selection. The smallest condition was selected from 453 eligible candidates, and the selection was deterministic and blind to any outcome measure. Materials were counterbalanced into 1 list(s) (a factorial split) and generated for PsychoPy, OpenSesame and jsPsych. Responses were collected from target onset until 2500 ms after it, and a response ended the trial. The selection is deterministic and reproducible (lexsync 0.1.1), and the seed (2026) fixes the trial order.

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
60 items per condition were selected from the English lexicon (wordfreq (Speer, 2022) screened against SUBTLEX-US (Brysbaert & New, 2009), data CC BY-SA 4.0; forms absent from SUBTLEX-US or beginning with a lower-case letter in under 10% of their uses are marked nonstandard, and N and OLD20 count only the unmarked forms; full corpus licence and citation at https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md) and matched item by item on length, n_syllables, bigram_freq using lexsync's standardised_euclidean matcher. The largest difference on a matched dimension was under 0.001 mean bigram probability in bigram_freq (high_frequency against low_frequency; d = 0.02, 90% CI [-0.28, 0.33]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) supported equivalence on 3 of 3 matched comparisons. No uncontrolled dimension differed by more than 0.5 SD. An exclusion list (exclude_en_demo.txt) removed 53 words from the candidates before selection. The smallest condition was selected from 453 eligible candidates, and the selection was deterministic and blind to any outcome measure. Materials were counterbalanced into 1 list(s) (a factorial split) and generated for PsychoPy, OpenSesame and jsPsych. Responses were collected from target onset until 2500 ms after it, and a response ended the trial. The selection is deterministic and reproducible (lexsync 0.1.1), and the seed (2026) fixes the trial order.

### Sampling plan
- Sample size and justification:
- Stopping rule:

### Analysis plan
- Statistical model: response ~ condition + scale(length, scale = FALSE) + scale(n_syllables, scale = FALSE) + scale(bigram_freq, scale = FALSE) + (1 + condition | subject) + (1 | item)
  (Crossed random effects for subjects and items guard against the language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). The matched dimensions enter as centred covariates, computed from the stimuli file's own columns, because matching leaves residual differences that the analysis can adjust for (Sassenhagen & Alday, 2016). Begin with random slopes for condition, the manipulated factor, by subject and, where it varies within items, by item (Barr et al., 2013); the matched covariates enter as fixed effects only. If the model is singular or fails to converge, simplify it as Matuschek et al. (2017) describe. The formula is lme4 syntax, for lme4 in R or pymer4 in Python; statsmodels MixedLM cannot take it directly and needs the random effects restated in its own arguments. The equivalence tests in the realised control are post-selection diagnostics on deterministically selected items, not inferential tests over a sample.)
- Inference criteria:
- Treatment of items (e.g. items as a random factor):

