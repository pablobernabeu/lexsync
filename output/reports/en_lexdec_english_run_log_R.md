# lexsync run log: en_lexdec

- Engine: R 4.6.1
- Started: 2026-10-03 00:29:07.229818
- Finished: 2026-10-03 00:30:01.062596

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions

## Steps

- **2026-10-03 00:29:07.238248**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-03 00:29:12.343097**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-03 00:29:12.83347**: pool after filters: 8177 words
    - pool: 8177
- **2026-10-03 00:29:21.11538**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-10-03 00:29:21.459918**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-10-03 00:29:23.782559**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: d99b79dee80a0803d326cce5157ad553
- **2026-10-03 00:29:24.553159**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 2
    - md5: f26ab1271c06e35b089d78a806602d3e
- **2026-10-03 00:29:24.935167**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 1
    - md5: 08fc5207d0e20aa470e1b3cf332e5830
- **2026-10-03 00:29:58.343711**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: f9e9b82991e8ffb552fe92ba01b86e58
- **2026-10-03 00:29:58.54616**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: 14dc876a96ac2b3b5e755d8e5353c5f8
- **2026-10-03 00:29:58.720972**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: 05d63ae6ec738c055aea3769358ef22a
- **2026-10-03 00:30:00.420318**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: 4ad453e62ea9b1c41121135142338c69
- **2026-10-03 00:30:00.618356**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: dfa8b1c650549bdc5d42f8fff286be80
