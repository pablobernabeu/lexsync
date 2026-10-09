# Materials datasheet — en_andrews_repro (english)

*lexsync datasheet v1.2; python engine.*

## Provenance

- **Paradigm:** factorial  |  **Item source:** corpus
- **Description:** Reproducing the item selection of Andrews (1989): frequency x orthographic neighbourhood size (Coltheart's N), a 2x2 of words with every cell matched on length; no nonwords or response mapping, so not a lexical-decision task.
- **Materials source:** `corpora/derived/en.csv` (sha256 `575833489e04d6a4…`)
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

- **Candidate pool** (items satisfying each condition's window before matching): HF_largeN: 251, HF_smallN: 258, LF_largeN: 1875, LF_smallN: 3462.
- Selection is a deterministic function of the materials source, the design and the schema, blind to any outcome measure, and does not depend on the seed, which fixes the trial order. Exact ties between equally close candidates are broken by spelling, in byte order, as lexsync 0.1 did, so every tie goes to the spelling that sorts first. Automating the choice removes the experimenter's discretion that Forster (2000) showed can bias item selection.

## Realised control

| Dimension | Role | Cohen's d | 90% CI | Var ratio | TOST p | Equivalent |
|---|---|---|---|---|---|---|
| length | controlled | -0.21 | [-0.77, 0.36] | 0.57 | 0.1920 | False |
| frequency | uncontrolled | -0.11 | [-0.67, 0.46] | 1.07 | 0.1238 | False |
| n_density | manipulated | 3.19 | [2.34, 4.04] | 0.04 | 1.0000 | False |
| old20 | uncontrolled | -5.76 | [-7.03, -4.48] | 1.13 | 1.0000 | False |
| n_syllables | uncontrolled | -0.59 | [-1.16, -0.01] | 1.45 | 0.6023 | False |
| bigram_freq | uncontrolled | 0.82 | [0.23, 1.41] | 0.98 | 0.8291 | False |
| length | controlled | 0.10 | [-0.47, 0.66] | 0.71 | 0.1186 | False |
| frequency | manipulated | 4.71 | [3.62, 5.81] | 0.50 | 1.0000 | False |
| n_density | uncontrolled | 0.10 | [-0.46, 0.67] | 0.64 | 0.1208 | False |
| old20 | uncontrolled | 0.10 | [-0.46, 0.67] | 1.02 | 0.1218 | False |
| n_syllables | uncontrolled | -0.59 | [-1.16, -0.01] | 1.45 | 0.6023 | False |
| bigram_freq | uncontrolled | 0.43 | [-0.14, 1.00] | 1.23 | 0.4174 | False |
| length | controlled | 0.10 | [-0.47, 0.66] | 0.71 | 0.1186 | False |
| frequency | manipulated | 5.19 | [4.01, 6.36] | 0.39 | 1.0000 | False |
| n_density | manipulated | 3.29 | [2.42, 4.15] | 0.05 | 1.0000 | False |
| old20 | uncontrolled | -5.91 | [-7.22, -4.61] | 1.22 | 1.0000 | False |
| n_syllables | uncontrolled | 0.00 | [-0.56, 0.56] | 4.21 | 0.0714 | False |
| bigram_freq | uncontrolled | 1.08 | [0.48, 1.69] | 0.86 | 0.9557 | False |
| length | controlled | 0.34 | [-0.23, 0.91] | 1.23 | 0.3197 | False |
| frequency | manipulated | 4.73 | [3.63, 5.83] | 0.47 | 1.0000 | False |
| n_density | manipulated | -3.78 | [-4.72, -2.84] | 15.79 | 1.0000 | False |
| old20 | uncontrolled | 5.83 | [4.54, 7.12] | 0.91 | 1.0000 | False |
| n_syllables | uncontrolled | 0.00 | [-0.56, 0.56] | 1.00 | 0.0714 | False |
| bigram_freq | uncontrolled | -0.35 | [-0.91, 0.22] | 1.25 | 0.3228 | False |
| length | controlled | 0.34 | [-0.23, 0.91] | 1.23 | 0.3197 | False |
| frequency | manipulated | 5.18 | [4.01, 6.36] | 0.36 | 1.0000 | False |
| n_density | uncontrolled | 0.39 | [-0.18, 0.96] | 1.29 | 0.3742 | False |
| old20 | uncontrolled | -0.27 | [-0.83, 0.30] | 1.08 | 0.2445 | False |
| n_syllables | uncontrolled | 0.39 | [-0.18, 0.96] | 2.91 | 0.3672 | False |
| bigram_freq | uncontrolled | 0.24 | [-0.33, 0.80] | 0.88 | 0.2183 | False |
| length | controlled | 0.00 | [-0.56, 0.56] | 1.00 | 0.0714 | False |
| frequency | uncontrolled | 0.35 | [-0.22, 0.92] | 0.77 | 0.3253 | False |
| n_density | manipulated | 3.89 | [2.93, 4.85] | 0.08 | 1.0000 | False |
| old20 | uncontrolled | -5.98 | [-7.30, -4.66] | 1.19 | 1.0000 | False |
| n_syllables | uncontrolled | 0.39 | [-0.18, 0.96] | 2.91 | 0.3672 | False |
| bigram_freq | uncontrolled | 0.58 | [0.00, 1.15] | 0.70 | 0.5919 | False |

## Suggested analysis

- **Model:** `response ~ condition + (1 + condition | subject) + (1 | item)` — where the response is reaction time from the onset of `{word}`; responses collected for 2500 ms; a response ends the trial.
- Crossed random effects for subjects and items guard against the language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). Begin with this maximal structure (Barr et al., 2013) and reduce it if the model does not converge (Matuschek et al., 2017). The formula is lme4 syntax, for lme4 in R or pymer4 in Python; statsmodels MixedLM cannot take it directly and needs the random effects restated in its own arguments. The equivalence tests in the realised control are post-selection diagnostics on deterministically selected items, not inferential tests over a sample.

## Methods paragraph

18 items per condition were selected from the English lexicon (wordfreq (Speer, 2022), data CC BY-SA 4.0; full corpus licence and citation at https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md) and matched item by item on length using lexsync's standardised_euclidean matcher. Equivalence was not confirmed on every matched dimension; the per-dimension differences are reported in the realised-control table. The smallest condition was selected from 251 eligible candidates, and the selection was deterministic and blind to any outcome measure. Materials were counterbalanced into 1 list(s) (a factorial split) and generated for PsychoPy, OpenSesame and jsPsych. Responses were collected from target onset until 2500 ms after it, and a response ended the trial. The selection is deterministic and reproducible (lexsync 0.1.1), and the seed (2026) fixes the trial order.

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
18 items per condition were selected from the English lexicon (wordfreq (Speer, 2022), data CC BY-SA 4.0; full corpus licence and citation at https://github.com/pablobernabeu/lexsync/blob/main/corpora/ATTRIBUTION.md) and matched item by item on length using lexsync's standardised_euclidean matcher. Equivalence was not confirmed on every matched dimension; the per-dimension differences are reported in the realised-control table. The smallest condition was selected from 251 eligible candidates, and the selection was deterministic and blind to any outcome measure. Materials were counterbalanced into 1 list(s) (a factorial split) and generated for PsychoPy, OpenSesame and jsPsych. Responses were collected from target onset until 2500 ms after it, and a response ended the trial. The selection is deterministic and reproducible (lexsync 0.1.1), and the seed (2026) fixes the trial order.

### Sampling plan
- Sample size and justification:
- Stopping rule:

### Analysis plan
- Statistical model: response ~ condition + (1 + condition | subject) + (1 | item)
  (Crossed random effects for subjects and items guard against the language-as-fixed-effect fallacy (Clark, 1973; Baayen et al., 2008). Begin with this maximal structure (Barr et al., 2013) and reduce it if the model does not converge (Matuschek et al., 2017). The formula is lme4 syntax, for lme4 in R or pymer4 in Python; statsmodels MixedLM cannot take it directly and needs the random effects restated in its own arguments. The equivalence tests in the realised control are post-selection diagnostics on deterministically selected items, not inferential tests over a sample.)
- Inference criteria:
- Treatment of items (e.g. items as a random factor):

