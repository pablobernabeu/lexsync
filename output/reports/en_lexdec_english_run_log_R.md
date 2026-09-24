# lexsync run log: en_lexdec

- Engine: R 4.6.1
- Started: 2026-09-24 16:59:49.995508
- Finished: 2026-09-24 16:59:53.471054

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-09-24 16:59:50.002705**: loading lexicon 'corpora/derived/en.csv'
- **2026-09-24 16:59:50.803151**: lexicon loaded: 30000 words
    - words: 30000
- **2026-09-24 16:59:50.820909**: pool after filters: 8177 words
    - pool: 8177
- **2026-09-24 16:59:52.946637**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-09-24 16:59:52.964204**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-09-24 16:59:53.028536**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: d99b79dee80a0803d326cce5157ad553
- **2026-09-24 16:59:53.052603**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 2
    - md5: f26ab1271c06e35b089d78a806602d3e
- **2026-09-24 16:59:53.078629**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 1
    - md5: 08fc5207d0e20aa470e1b3cf332e5830
- **2026-09-24 16:59:53.242312**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: f9e9b82991e8ffb552fe92ba01b86e58
- **2026-09-24 16:59:53.2561**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: a1718c27604d642b875fc1b6057bc76c
- **2026-09-24 16:59:53.266603**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: 05d63ae6ec738c055aea3769358ef22a
- **2026-09-24 16:59:53.413854**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: ee1e8a23fc2feff93c4bd8e3bb56d2dd
- **2026-09-24 16:59:53.43476**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: 8b125ae607d5d636162d86e4da01645a
