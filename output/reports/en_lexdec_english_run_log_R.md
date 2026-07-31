# lexsync run log: en_lexdec

- Engine: R 4.6.1
- Started: 2026-07-31 21:48:15.092803
- Finished: 2026-07-31 21:48:16.456232

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-07-31 21:48:15.096355**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-31 21:48:15.487548**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-31 21:48:15.502079**: pool after filters: 8177 words
    - pool: 8177
- **2026-07-31 21:48:16.176295**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-07-31 21:48:16.1839**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-07-31 21:48:16.220237**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: d99b79dee80a0803d326cce5157ad553
- **2026-07-31 21:48:16.236013**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 2
    - md5: f26ab1271c06e35b089d78a806602d3e
- **2026-07-31 21:48:16.250872**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 1
    - md5: 08fc5207d0e20aa470e1b3cf332e5830
- **2026-07-31 21:48:16.343482**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: f9e9b82991e8ffb552fe92ba01b86e58
- **2026-07-31 21:48:16.352885**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: a1718c27604d642b875fc1b6057bc76c
- **2026-07-31 21:48:16.359918**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: 0637039be99081011c51984176d531c7
- **2026-07-31 21:48:16.44125**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: 935c9df20e10e44e5dd091e387ca8f32
- **2026-07-31 21:48:16.449572**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: a88767b2ecf499c79cd6100ee6684032
