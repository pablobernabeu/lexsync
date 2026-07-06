# lexsync run log: en_lexdec

- Engine: R 4.6.0
- Started: 2026-07-06 10:27:18.258282
- Finished: 2026-07-06 10:27:20.462919

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-07-06 10:27:18.278072**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-06 10:27:18.898459**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-06 10:27:18.923887**: pool after filters: 8177 words
    - pool: 8177
- **2026-07-06 10:27:20.08805**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-07-06 10:27:20.101654**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-07-06 10:27:20.143208**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: f1c1159431d7d91972e84aab3bf876ab
- **2026-07-06 10:27:20.163232**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 2
    - md5: 32ec1c8e337acb192cefd6fca36f949f
- **2026-07-06 10:27:20.181469**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 1
    - md5: 08fc5207d0e20aa470e1b3cf332e5830
- **2026-07-06 10:27:20.303786**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: 469dd81110060f9eccf3a4e7237fa432
- **2026-07-06 10:27:20.317458**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: 5855ff2a6f113ad7daa74849cc066082
- **2026-07-06 10:27:20.32968**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: c821ef1cd8d72dbecca9e658e3073ced
- **2026-07-06 10:27:20.438783**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: c73261969d16352d3ea23fed32aeb7d4
- **2026-07-06 10:27:20.450098**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: 3db244ed61c683537a4f37d52021ab87
