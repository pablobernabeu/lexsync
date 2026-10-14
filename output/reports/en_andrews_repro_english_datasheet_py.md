# Materials datasheet — en_andrews_repro (english)

*lexsync datasheet v1.2; python engine.*

## Provenance

- **Paradigm:** factorial  |  **Item source:** corpus
- **Description:** Reproducing Andrews (1989): frequency x orthographic neighbourhood size (Coltheart's N), a 2x2 of words with every cell matched on length, in a lexical decision with one interleaved pseudoword per word.
- **Materials source:** `corpora/derived/en_v2.csv` (sha256 `46815cd56ac036cb…`)
- **Excluded words:** `config/exclude_en_demo.txt` (53 words, 53 removed, sha256 `cac9f88fb86fa6d0…`)
- **Selection:** standardised_euclidean
- **Cross-engine determinism:** byte-identical
- **Counterbalancing:** factorial, 1 list(s)
- **Items:** 72 rows across 4 conditions (HF_smallN, HF_largeN, LF_largeN, LF_smallN)
- **Seed:** 2026  |  **Versions:** engine python, lexsync 0.1.1, python 3.13.7, pandas 2.3.2, numpy 2.3.2, scipy 1.17.1, rapidfuzz 3.14.5, pyyaml 6.0.3, os Windows AMD64

## Counterbalanced lists

| List | Condition | Trials |
|---|---|---|
| 1 | HF_largeN | 18 |
| 1 | HF_smallN | 18 |
| 1 | LF_largeN | 18 |
| 1 | LF_smallN | 18 |

## Selection transparency

- **Candidate pool** (items satisfying each condition's window before matching): HF_largeN: 201, HF_smallN: 280, LF_largeN: 794, LF_smallN: 2231.
- Selection is a deterministic function of the materials source, the design and the schema, blind to any outcome measure, and does not depend on the seed, which fixes the trial order. Exact ties between equally close candidates are broken by a keyed hash of each word (salt lexsync-tie-v1), so no part of the alphabet is favoured. Automating the choice removes the experimenter's discretion that Forster (2000) showed can bias item selection.

## Realised control

Each row compares a condition with its reference. The raw difference and Cohen's d are the reference mean minus the condition mean, and the variance ratio is the condition's variance over the reference's.

| Condition | Reference | Dimension | Role | Raw difference | Cohen's d | 90% CI | Var ratio | TOST p | Equivalent |
|---|---|---|---|---|---|---|---|---|---|
| HF_smallN | HF_largeN | length | controlled | 0.111 | 0.18 | [-0.38, 0.75] | 0.50 | 0.1728 | False |
| HF_smallN | HF_largeN | frequency | uncontrolled | -0.233 | -0.45 | [-1.02, 0.12] | 1.24 | 0.4417 | False |
| HF_smallN | HF_largeN | n_density | manipulated | 13.056 | 3.20 | [2.35, 4.05] | 0.09 | 1.0000 | False |
| HF_smallN | HF_largeN | old20 | uncontrolled | -0.503 | -2.50 | [-3.25, -1.75] | 2.44 | 1.0000 | False |
| HF_smallN | HF_largeN | n_syllables | uncontrolled | -0.167 | -0.38 | [-0.95, 0.19] | 1.60 | 0.3619 | False |
| HF_smallN | HF_largeN | bigram_freq | uncontrolled | 0.002 | 0.51 | [-0.06, 1.08] | 1.15 | 0.5115 | False |
| LF_largeN | HF_largeN | length | controlled | 0.111 | 0.18 | [-0.38, 0.75] | 0.50 | 0.1728 | False |
| LF_largeN | HF_largeN | frequency | manipulated | 1.964 | 4.63 | [3.55, 5.71] | 0.51 | 1.0000 | False |
| LF_largeN | HF_largeN | n_density | uncontrolled | 2.278 | 0.46 | [-0.12, 1.03] | 0.63 | 0.4479 | False |
| LF_largeN | HF_largeN | old20 | uncontrolled | -0.111 | -0.71 | [-1.29, -0.13] | 1.08 | 0.7341 | False |
| LF_largeN | HF_largeN | n_syllables | uncontrolled | 0.111 | 0.35 | [-0.22, 0.92] | 0.38 | 0.3268 | False |
| LF_largeN | HF_largeN | bigram_freq | uncontrolled | 0.000 | -0.02 | [-0.58, 0.54] | 2.28 | 0.0795 | False |
| LF_smallN | HF_largeN | length | controlled | 0.111 | 0.18 | [-0.38, 0.75] | 0.50 | 0.1728 | False |
| LF_smallN | HF_largeN | frequency | manipulated | 1.989 | 4.54 | [3.48, 5.61] | 0.61 | 1.0000 | False |
| LF_smallN | HF_largeN | n_density | manipulated | 12.389 | 3.05 | [2.22, 3.88] | 0.08 | 1.0000 | False |
| LF_smallN | HF_largeN | old20 | uncontrolled | -0.542 | -3.46 | [-4.35, -2.57] | 1.08 | 1.0000 | False |
| LF_smallN | HF_largeN | n_syllables | uncontrolled | 0.111 | 0.28 | [-0.29, 0.84] | 1.18 | 0.2546 | False |
| LF_smallN | HF_largeN | bigram_freq | uncontrolled | 0.002 | 0.71 | [0.13, 1.29] | 0.87 | 0.7329 | False |
| LF_largeN | HF_smallN | length | controlled | 0.000 | 0.00 | [-0.56, 0.56] | 1.00 | 0.0714 | False |
| LF_largeN | HF_smallN | frequency | manipulated | 2.197 | 4.81 | [3.70, 5.92] | 0.41 | 1.0000 | False |
| LF_largeN | HF_smallN | n_density | manipulated | -10.778 | -3.26 | [-4.12, -2.40] | 7.27 | 1.0000 | False |
| LF_largeN | HF_smallN | old20 | uncontrolled | 0.392 | 1.93 | [1.24, 2.61] | 0.44 | 0.9999 | False |
| LF_largeN | HF_smallN | n_syllables | uncontrolled | 0.278 | 0.73 | [0.15, 1.31] | 0.24 | 0.7511 | False |
| LF_largeN | HF_smallN | bigram_freq | uncontrolled | -0.002 | -0.42 | [-0.99, 0.15] | 1.98 | 0.4095 | False |
| LF_smallN | HF_smallN | length | controlled | 0.000 | 0.00 | [-0.56, 0.56] | 1.00 | 0.0714 | False |
| LF_smallN | HF_smallN | frequency | manipulated | 2.222 | 4.73 | [3.63, 5.83] | 0.49 | 1.0000 | False |
| LF_smallN | HF_smallN | n_density | uncontrolled | -0.667 | -0.42 | [-0.99, 0.15] | 0.88 | 0.4091 | False |
| LF_smallN | HF_smallN | old20 | uncontrolled | -0.039 | -0.19 | [-0.76, 0.37] | 0.44 | 0.1803 | False |
| LF_smallN | HF_smallN | n_syllables | uncontrolled | 0.278 | 0.62 | [0.04, 1.19] | 0.74 | 0.6335 | False |
| LF_smallN | HF_smallN | bigram_freq | uncontrolled | 0.000 | 0.16 | [-0.41, 0.72] | 0.76 | 0.1550 | False |
| LF_smallN | LF_largeN | length | controlled | 0.000 | 0.00 | [-0.56, 0.56] | 1.00 | 0.0714 | False |
| LF_smallN | LF_largeN | frequency | uncontrolled | 0.024 | 0.07 | [-0.50, 0.63] | 1.19 | 0.1013 | False |
| LF_smallN | LF_largeN | n_density | manipulated | 10.111 | 3.08 | [2.25, 3.92] | 0.12 | 1.0000 | False |
| LF_smallN | LF_largeN | old20 | uncontrolled | -0.431 | -2.70 | [-3.48, -1.92] | 1.00 | 1.0000 | False |
| LF_smallN | LF_largeN | n_syllables | uncontrolled | 0.000 | 0.00 | [-0.56, 0.56] | 3.12 | 0.0714 | False |
| LF_smallN | LF_largeN | bigram_freq | uncontrolled | 0.002 | 0.57 | [-0.01, 1.14] | 0.38 | 0.5791 | False |

## Suggested analysis

- **Model:** `response ~ condition + scale(length, scale = FALSE) + (1 + condition | subject) + (1 | item)` — where the response is reaction time from the onset of `{word}`; responses collected for 2500 ms; a response ends the trial.
- Crossed random effects for subjects and items guard against the language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). The matched dimensions enter as centred covariates, computed from the stimuli file's own columns, because matching leaves residual differences that the analysis can adjust for (Sassenhagen & Alday, 2016). Begin with random slopes for condition, the manipulated factor, by subject and, where it varies within items, by item (Barr et al., 2013); the matched covariates enter as fixed effects only. If the model is singular or fails to converge, simplify it as Matuschek et al. (2017) describe. If the conditions cross two or more factors, recode condition into those factors (for example frequency * neighbourhood) with sum coding. The formula is lme4 syntax, for lme4 in R or pymer4 in Python; statsmodels MixedLM cannot take it directly and needs the random effects restated in its own arguments. The equivalence tests in the realised control are post-selection diagnostics on deterministically selected items, not inferential tests over a sample.

## Methods paragraph

18 items per condition were selected from the English lexicon (wordfreq (Speer, 2022) screened against SUBTLEX-US (Brysbaert & New, 2009), data CC BY-SA 4.0; forms absent from SUBTLEX-US or beginning with a lower-case letter in under 10% of their uses are marked nonstandard, and N and OLD20 count only the unmarked forms; full corpus licence and citation at https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md) and matched item by item on length using lexsync's standardised_euclidean matcher. The largest difference on a matched dimension was 0.111 characters in length (HF_largeN against HF_smallN; d = 0.18, 90% CI [-0.38, 0.75]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) supported equivalence on 0 of 6 matched comparisons; with 18 items per condition no dimension that varies can pass this test, however well matched. Dimensions the design did not control differed: old20 (HF_largeN against LF_smallN: -0.542 mean Levenshtein distance; d = -3.46, 90% CI [-4.35, -2.57]), old20 (LF_largeN against LF_smallN: -0.431 mean Levenshtein distance; d = -2.70, 90% CI [-3.48, -1.92]), old20 (HF_largeN against HF_smallN: -0.503 mean Levenshtein distance; d = -2.50, 90% CI [-3.25, -1.75]), old20 (HF_smallN against LF_largeN: 0.392 mean Levenshtein distance; d = 1.93, 90% CI [1.24, 2.61]) and n_syllables (HF_smallN against LF_largeN: 0.278 syllables; d = 0.73, 90% CI [0.15, 1.31]), and 5 more in the realised-control table. An exclusion list (exclude_en_demo.txt) removed 53 words from the candidates before selection. The smallest condition was selected from 201 eligible candidates, and the selection was deterministic and blind to any outcome measure. Materials were counterbalanced into 1 list(s) (a factorial split) and generated for PsychoPy, OpenSesame and jsPsych. Responses were collected from target onset until 2500 ms after it, and a response ended the trial. Participants pressed the left arrow key for HF_largeN, HF_smallN, LF_largeN and LF_smallN trials. The selection is deterministic and reproducible (lexsync 0.1.1), and the seed (2026) fixes the trial order.

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
18 items per condition were selected from the English lexicon (wordfreq (Speer, 2022) screened against SUBTLEX-US (Brysbaert & New, 2009), data CC BY-SA 4.0; forms absent from SUBTLEX-US or beginning with a lower-case letter in under 10% of their uses are marked nonstandard, and N and OLD20 count only the unmarked forms; full corpus licence and citation at https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md) and matched item by item on length using lexsync's standardised_euclidean matcher. The largest difference on a matched dimension was 0.111 characters in length (HF_largeN against HF_smallN; d = 0.18, 90% CI [-0.38, 0.75]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) supported equivalence on 0 of 6 matched comparisons; with 18 items per condition no dimension that varies can pass this test, however well matched. Dimensions the design did not control differed: old20 (HF_largeN against LF_smallN: -0.542 mean Levenshtein distance; d = -3.46, 90% CI [-4.35, -2.57]), old20 (LF_largeN against LF_smallN: -0.431 mean Levenshtein distance; d = -2.70, 90% CI [-3.48, -1.92]), old20 (HF_largeN against HF_smallN: -0.503 mean Levenshtein distance; d = -2.50, 90% CI [-3.25, -1.75]), old20 (HF_smallN against LF_largeN: 0.392 mean Levenshtein distance; d = 1.93, 90% CI [1.24, 2.61]) and n_syllables (HF_smallN against LF_largeN: 0.278 syllables; d = 0.73, 90% CI [0.15, 1.31]), and 5 more in the realised-control table. An exclusion list (exclude_en_demo.txt) removed 53 words from the candidates before selection. The smallest condition was selected from 201 eligible candidates, and the selection was deterministic and blind to any outcome measure. Materials were counterbalanced into 1 list(s) (a factorial split) and generated for PsychoPy, OpenSesame and jsPsych. Responses were collected from target onset until 2500 ms after it, and a response ended the trial. Participants pressed the left arrow key for HF_largeN, HF_smallN, LF_largeN and LF_smallN trials. The selection is deterministic and reproducible (lexsync 0.1.1), and the seed (2026) fixes the trial order.

### Sampling plan
- Sample size and justification:
- Stopping rule:

### Analysis plan
- Statistical model: response ~ condition + scale(length, scale = FALSE) + (1 + condition | subject) + (1 | item)
  (Crossed random effects for subjects and items guard against the language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). The matched dimensions enter as centred covariates, computed from the stimuli file's own columns, because matching leaves residual differences that the analysis can adjust for (Sassenhagen & Alday, 2016). Begin with random slopes for condition, the manipulated factor, by subject and, where it varies within items, by item (Barr et al., 2013); the matched covariates enter as fixed effects only. If the model is singular or fails to converge, simplify it as Matuschek et al. (2017) describe. If the conditions cross two or more factors, recode condition into those factors (for example frequency * neighbourhood) with sum coding. The formula is lme4 syntax, for lme4 in R or pymer4 in Python; statsmodels MixedLM cannot take it directly and needs the random effects restated in its own arguments. The equivalence tests in the realised control are post-selection diagnostics on deterministically selected items, not inferential tests over a sample.)
- Inference criteria:
- Treatment of items (e.g. items as a random factor):

