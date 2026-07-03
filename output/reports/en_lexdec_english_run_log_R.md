# lexsync run log: en_lexdec

- Engine: R 4.6.0
- Started: 2026-07-03 08:07:49.430943
- Finished: 2026-07-03 08:07:50.552574

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026

## Steps

- **2026-07-03 08:07:49.434683**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-03 08:07:49.738683**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-03 08:07:49.750003**: pool after filters: 8177 words
    - pool: 8177
- **2026-07-03 08:07:50.291805**: generated 120 items (words + pseudowords)
    - conditions: word, pseudoword
- **2026-07-03 08:07:50.30188**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-07-03 08:07:50.331104**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: f1c1159431d7d91972e84aab3bf876ab
- **2026-07-03 08:07:50.351635**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 2
    - md5: 32ec1c8e337acb192cefd6fca36f949f
- **2026-07-03 08:07:50.368618**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 1
    - md5: 326701be50b673b6b9dc2bb6de64ba97
- **2026-07-03 08:07:50.453481**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: 469dd81110060f9eccf3a4e7237fa432
- **2026-07-03 08:07:50.464835**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: 5855ff2a6f113ad7daa74849cc066082
- **2026-07-03 08:07:50.473497**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: c821ef1cd8d72dbecca9e658e3073ced
- **2026-07-03 08:07:50.535567**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: ed550daabaf770c2054f68874f107ecd
- **2026-07-03 08:07:50.543903**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: 06ddb3ae71b6a0219c984fbd1dd3edb6
