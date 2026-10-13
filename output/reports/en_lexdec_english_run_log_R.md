# lexsync run log: en_lexdec

- Engine: R 4.6.1
- Started: 2026-10-13 11:09:55.782767
- Finished: 2026-10-13 11:10:23.106759

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13 11:09:55.798264**: loading lexicon 'corpora/derived/en_v2.csv'
- **2026-10-13 11:09:58.084151**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-13 11:09:58.125042**: exclude_words: removed 53 of the 53 listed word(s) from the candidates (config/exclude_en_demo.txt)
    - exclude_words: config/exclude_en_demo.txt
    - sha256: cac9f88fb86fa6d0e6dbabc287c9ebb782100d071eeded13eb812584b9d41e9f
    - n_removed: 53
- **2026-10-13 11:09:58.197028**: pool after filters: 6767 words
    - pool: 6767
- **2026-10-13 11:09:59.58031**: pseudowords checked against 289023 known word form(s) from 'corpora/derived/en_known_forms.txt'
    - exclude: corpora/derived/en_known_forms.txt
    - sha256: 31fa1bfbf347a94ca31dcdc0fe69be459b5829621b9b194469c725ab64e5e2b4
- **2026-10-13 11:10:06.171402**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-10-13 11:10:14.145798**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-10-13 11:10:14.160852**: equivalence pseudoword vs word on 'bigram_freq': d = -0.97 [-1.29, -0.65], TOST p = 0.994 (not shown equivalent)
- **2026-10-13 11:10:14.175509**: equivalence pseudoword vs word on 'n_density': d = 0.00 [-0.30, 0.31], TOST p = 0.004 (equivalent)
- **2026-10-13 11:10:14.204097**: equivalence pseudoword vs word on 'old20': d = -0.04 [-0.34, 0.26], TOST p = 0.006 (equivalent)
- **2026-10-13 11:10:15.456697**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: 904a03751c491ba9979823cf6ad1aca4
- **2026-10-13 11:10:15.585404**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 8
    - md5: f703a5d9fc95ab14d7c8b7b81238ee62
- **2026-10-13 11:10:15.853213**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 4
    - md5: 1351a5c0c730e41e247d8ee90369ac23
- **2026-10-13 11:10:21.765504**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: a9c90173d7b34b6b6c1a914fa5132f57
- **2026-10-13 11:10:21.830647**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: 694c11f70ca325181628b5da1922e729
- **2026-10-13 11:10:21.86163**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: 70134e5b9b45c4bc328a61bd5c6dd9a3
- **2026-10-13 11:10:21.91092**: wrote 'en_lexdec_english_psychopy.csv'
    - path: output/experiments/en_lexdec_english_psychopy.csv
    - rows: NA
    - md5: aad3bb5683f8fb1e73bf40f5953e9d01
- **2026-10-13 11:10:21.953575**: wrote 'en_lexdec_english_opensesame.csv'
    - path: output/experiments/en_lexdec_english_opensesame.csv
    - rows: NA
    - md5: d0ffb15c8bb700fa775f65d16d8ae164
- **2026-10-13 11:10:22.002503**: wrote 'en_lexdec_english_opensesame_text.csv'
    - path: output/experiments/en_lexdec_english_opensesame_text.csv
    - rows: NA
    - md5: 8863142b1722e0e7c3971220bad528c6
- **2026-10-13 11:10:22.966013**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: 07f626ca25568c9bc514e060d5b65909
- **2026-10-13 11:10:23.028864**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: da555e54e1257d60d0dc64c055df6e69
