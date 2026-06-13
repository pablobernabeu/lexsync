# lexsync run log: en_lexdec

- Engine: R 4.5.1
- Started: 2026-06-13 18:21:16.207023
- Finished: 2026-06-13 18:21:17.247959

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026

## Steps

- **2026-06-13 18:21:16.207569** -- loading lexicon 'corpora/derived/en.csv'
- **2026-06-13 18:21:16.295189** -- lexicon loaded: 30000 words
    - words: 30000
- **2026-06-13 18:21:16.300564** -- pool after filters: 8177 words
    - pool: 8177
- **2026-06-13 18:21:17.082727** -- generated 120 items (words + pseudowords)
    - conditions: word, pseudoword
- **2026-06-13 18:21:17.085719** -- equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-06-13 18:21:17.124823** -- wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: f1c1159431d7d91972e84aab3bf876ab
- **2026-06-13 18:21:17.135369** -- wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 2
    - md5: 32ec1c8e337acb192cefd6fca36f949f
- **2026-06-13 18:21:17.14733** -- wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 1
    - md5: 326701be50b673b6b9dc2bb6de64ba97
- **2026-06-13 18:21:17.23326** -- wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: 59aa5ade834c4d2ec8282d7ab0f715c7
- **2026-06-13 18:21:17.239291** -- wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: 5855ff2a6f113ad7daa74849cc066082
