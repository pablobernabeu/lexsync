# lexsync run log: en_lexdec

- Engine: R 4.6.1
- Started: 2026-10-02 20:38:48.146018
- Finished: 2026-10-02 20:40:22.418743

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-10-02 20:38:48.162754**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-02 20:38:55.077493**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-02 20:38:55.265**: pool after filters: 8177 words
    - pool: 8177
- **2026-10-02 20:39:03.31483**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-10-02 20:39:03.598033**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-10-02 20:39:14.664861**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: d99b79dee80a0803d326cce5157ad553
- **2026-10-02 20:39:15.95633**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 2
    - md5: f26ab1271c06e35b089d78a806602d3e
- **2026-10-02 20:39:17.643109**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 1
    - md5: 08fc5207d0e20aa470e1b3cf332e5830
- **2026-10-02 20:40:16.646213**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: f9e9b82991e8ffb552fe92ba01b86e58
- **2026-10-02 20:40:17.463273**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: 14dc876a96ac2b3b5e755d8e5353c5f8
- **2026-10-02 20:40:17.839113**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: 05d63ae6ec738c055aea3769358ef22a
- **2026-10-02 20:40:21.880743**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: 6f06aac5002d611b6ac92042b820f54d
- **2026-10-02 20:40:22.221235**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: dfa8b1c650549bdc5d42f8fff286be80
