# Materials datasheet -- en_balanced_lists (english)

*lexsync datasheet v1.2; R engine.*

## Provenance

- **Paradigm:** factorial  |  **Item source:** corpus
- **Description:** High versus low frequency English words, matched on length, neighbourhood density and OLD20, dealt into four counterbalancing lists that are themselves equated on those dimensions.
- **Materials source:** `corpora/derived/en_v2.csv` (sha256 `46815cd56ac036cb...`)
- **Excluded words:** `config/exclude_en_demo.txt` (53 words, 53 removed, sha256 `cac9f88fb86fa6d0...`)
- **Selection:** standardised_euclidean
- **Cross-engine determinism:** byte-identical
- **Counterbalancing:** factorial, 4 list(s)
- **Presentation versions:** 4, assigned as version = ((participant - 1) mod 4) + 1 unless a version is given at launch
- **Items:** 80 rows across 2 conditions (high_frequency, low_frequency)
- **Seed:** 2026  |  **Versions:** engine R, lexsync 0.1.1, R 4.6.1, readr 2.2.0, stringdist 0.9.17, jsonlite 2.0.0, digest 0.6.39, yaml 2.3.12, stringi 1.8.7, os Windows x86-64

## Balanced list assignment

- **Balanced on:** length, n_density, old20, frequency
- **Imbalance:** 1808620 before, 73660 after, in 11 swap(s)
- **Cost unit:** summed absolute deviation of each list's dimension total from its fair share, in milli-units of the dimension's mean, scaled by the number of item sets
- The search ran to a local optimum: no single exchange of two item sets between lists would reduce the imbalance further.
- The search is a deterministic integer descent with a keyed-hash tie-break, so it uses no random number generator and the R and Python engines produce the same assignment.

## Counterbalanced lists

| List | Condition | Trials |
|---|---|---|
| 1 | high_frequency | 10 |
| 1 | low_frequency | 10 |
| 2 | high_frequency | 10 |
| 2 | low_frequency | 10 |
| 3 | high_frequency | 10 |
| 3 | low_frequency | 10 |
| 4 | high_frequency | 10 |
| 4 | low_frequency | 10 |

## Selection transparency

- **Candidate pool** (items satisfying each condition's window before matching): high_frequency: 534, low_frequency: 3583.
- Selection is a deterministic function of the materials source, the design and the schema, blind to any outcome measure, and does not depend on the seed, which fixes the trial order. Exact ties between equally close candidates are broken by a keyed hash of each word (salt lexsync-tie-v1), so no part of the alphabet is favoured. Automating the choice removes the experimenter's discretion that Forster (2000) showed can bias item selection.

## Realised control

Each row compares a condition with its reference. The raw difference and Cohen's d are the reference mean minus the condition mean, and the variance ratio is the condition's variance over the reference's.

| Condition | Reference | Dimension | Role | Raw difference | Cohen's d | 90% CI | Var ratio | TOST p | Equivalent |
|---|---|---|---|---|---|---|---|---|---|
| low_frequency | high_frequency | length | controlled | 0.025 | 0.02 | [-0.35, 0.39] | 0.92 | 0.0173 | TRUE |
| low_frequency | high_frequency | frequency | manipulated | 1.507 | 5.00 | [4.25, 5.76] | 0.17 | 1.0000 | FALSE |
| low_frequency | high_frequency | n_density | controlled | 0.100 | 0.02 | [-0.36, 0.39] | 0.93 | 0.0168 | TRUE |
| low_frequency | high_frequency | old20 | controlled | 0.025 | 0.05 | [-0.32, 0.42] | 0.79 | 0.0237 | TRUE |
| low_frequency | high_frequency | n_syllables | uncontrolled | 0.025 | 0.04 | [-0.34, 0.41] | 1.01 | 0.0208 | TRUE |
| low_frequency | high_frequency | bigram_freq | uncontrolled | -0.001 | -0.15 | [-0.52, 0.23] | 1.50 | 0.0588 | FALSE |

## Suggested analysis

- **Model:** `response ~ condition + scale(length, scale = FALSE) + scale(n_density, scale = FALSE) + scale(old20, scale = FALSE) + (1 + condition | subject) + (1 | item)` -- where the response is reaction time from the onset of `{word}`; responses collected for 2500 ms; a response ends the trial.
- Crossed random effects for subjects and items guard against the language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). The matched dimensions enter as centred covariates, computed from the stimuli file's own columns, because matching leaves residual differences that the analysis can adjust for (Sassenhagen & Alday, 2016). Begin with random slopes for condition, the manipulated factor, by subject and, where it varies within items, by item (Barr et al., 2013); the matched covariates enter as fixed effects only. If the model is singular or fails to converge, simplify it as Matuschek et al. (2017) describe. The formula is lme4 syntax, for lme4 in R or pymer4 in Python; statsmodels MixedLM cannot take it directly and needs the random effects restated in its own arguments. The equivalence tests in the realised control are post-selection diagnostics on deterministically selected items, not inferential tests over a sample.

## Methods paragraph

40 items per condition were selected from the English lexicon (wordfreq (Speer, 2022) screened against SUBTLEX-US (Brysbaert & New, 2009), data CC BY-SA 4.0; forms absent from SUBTLEX-US or beginning with a lower-case letter in under 10% of their uses are marked nonstandard, and N and OLD20 count only the unmarked forms; full corpus licence and citation at https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md) and matched item by item on length, n_density, old20 using lexsync's standardised_euclidean matcher. The largest difference on a matched dimension was 0.025 mean Levenshtein distance in old20 (high_frequency against low_frequency; d = 0.05, 90% CI [-0.32, 0.42]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) supported equivalence on 3 of 3 matched comparisons. No uncontrolled dimension differed by more than 0.5 SD. An exclusion list (exclude_en_demo.txt) removed 53 words from the candidates before selection. The smallest condition was selected from 534 eligible candidates, and the selection was deterministic and blind to any outcome measure. Item sets were assigned to lists so as to equate the lists on length, n_density, old20, frequency rather than by an arbitrary deal, by a deterministic integer search (11 swap(s); imbalance reduced from 1808620 to 73660). Materials were counterbalanced into 4 list(s) (a factorial split) and generated for PsychoPy, OpenSesame and jsPsych. Each participant was presented one of the 4 lists, assigned in rotation by participant number. Responses were collected from target onset until 2500 ms after it, and a response ended the trial. The selection is deterministic and reproducible (lexsync 0.1.1), and the seed (2026) fixes the trial order.

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
40 items per condition were selected from the English lexicon (wordfreq (Speer, 2022) screened against SUBTLEX-US (Brysbaert & New, 2009), data CC BY-SA 4.0; forms absent from SUBTLEX-US or beginning with a lower-case letter in under 10% of their uses are marked nonstandard, and N and OLD20 count only the unmarked forms; full corpus licence and citation at https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md) and matched item by item on length, n_density, old20 using lexsync's standardised_euclidean matcher. The largest difference on a matched dimension was 0.025 mean Levenshtein distance in old20 (high_frequency against low_frequency; d = 0.05, 90% CI [-0.32, 0.42]). Two one-sided tests at a bound of 0.5 SD (alpha 0.05) supported equivalence on 3 of 3 matched comparisons. No uncontrolled dimension differed by more than 0.5 SD. An exclusion list (exclude_en_demo.txt) removed 53 words from the candidates before selection. The smallest condition was selected from 534 eligible candidates, and the selection was deterministic and blind to any outcome measure. Item sets were assigned to lists so as to equate the lists on length, n_density, old20, frequency rather than by an arbitrary deal, by a deterministic integer search (11 swap(s); imbalance reduced from 1808620 to 73660). Materials were counterbalanced into 4 list(s) (a factorial split) and generated for PsychoPy, OpenSesame and jsPsych. Each participant was presented one of the 4 lists, assigned in rotation by participant number. Responses were collected from target onset until 2500 ms after it, and a response ended the trial. The selection is deterministic and reproducible (lexsync 0.1.1), and the seed (2026) fixes the trial order.

### Sampling plan
- Sample size and justification:
- Stopping rule:

### Analysis plan
- Statistical model: response ~ condition + scale(length, scale = FALSE) + scale(n_density, scale = FALSE) + scale(old20, scale = FALSE) + (1 + condition | subject) + (1 | item)
  (Crossed random effects for subjects and items guard against the language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). The matched dimensions enter as centred covariates, computed from the stimuli file's own columns, because matching leaves residual differences that the analysis can adjust for (Sassenhagen & Alday, 2016). Begin with random slopes for condition, the manipulated factor, by subject and, where it varies within items, by item (Barr et al., 2013); the matched covariates enter as fixed effects only. If the model is singular or fails to converge, simplify it as Matuschek et al. (2017) describe. The formula is lme4 syntax, for lme4 in R or pymer4 in Python; statsmodels MixedLM cannot take it directly and needs the random effects restated in its own arguments. The equivalence tests in the realised control are post-selection diagnostics on deterministically selected items, not inferential tests over a sample.)
- Inference criteria:
- Treatment of items (e.g. items as a random factor):

