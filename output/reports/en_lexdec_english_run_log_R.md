# lexsync run log: en_lexdec

- Engine: R 4.6.1
- Started: 2026-07-15 10:09:43.907696
- Finished: 2026-07-15 10:09:45.618834

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-07-15 10:09:43.912047**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-15 10:09:44.400125**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-15 10:09:44.411811**: pool after filters: 8177 words
    - pool: 8177
- **2026-07-15 10:09:45.272947**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-07-15 10:09:45.283279**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-07-15 10:09:45.318824**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: f1c1159431d7d91972e84aab3bf876ab
- **2026-07-15 10:09:45.338965**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 2
    - md5: 32ec1c8e337acb192cefd6fca36f949f
- **2026-07-15 10:09:45.356167**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 1
    - md5: 08fc5207d0e20aa470e1b3cf332e5830
- **2026-07-15 10:09:45.456433**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: 469dd81110060f9eccf3a4e7237fa432
- **2026-07-15 10:09:45.4669**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: 5855ff2a6f113ad7daa74849cc066082
- **2026-07-15 10:09:45.476706**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: c821ef1cd8d72dbecca9e658e3073ced
- **2026-07-15 10:09:45.581348**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: 907fa4e197c5fdf6b7a711e8488f4c73
- **2026-07-15 10:09:45.600163**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: beaac662bd475017aca2ab958459a367
