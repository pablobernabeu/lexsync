# lexsync run log: en_lexdec

- Engine: R 4.6.1
- Started: 2026-07-17 01:38:36.288854
- Finished: 2026-07-17 01:38:38.503193

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-07-17 01:38:36.295069**: loading lexicon 'corpora/derived/en.csv'
- **2026-07-17 01:38:36.874304**: lexicon loaded: 30000 words
    - words: 30000
- **2026-07-17 01:38:36.891768**: pool after filters: 8177 words
    - pool: 8177
- **2026-07-17 01:38:38.017617**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-07-17 01:38:38.026409**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-07-17 01:38:38.066216**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: d99b79dee80a0803d326cce5157ad553
- **2026-07-17 01:38:38.094313**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 2
    - md5: f26ab1271c06e35b089d78a806602d3e
- **2026-07-17 01:38:38.122615**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 1
    - md5: 08fc5207d0e20aa470e1b3cf332e5830
- **2026-07-17 01:38:38.297967**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: 0c50909a0211eca881dcdd5a7ad09822
- **2026-07-17 01:38:38.315778**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: a1718c27604d642b875fc1b6057bc76c
- **2026-07-17 01:38:38.331374**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: 5ace7105c9418a6a3f724e09d9e19b11
- **2026-07-17 01:38:38.467637**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: a7e2ec1a637d22d5762311c1b9fb2fe0
- **2026-07-17 01:38:38.486122**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: beaac662bd475017aca2ab958459a367
