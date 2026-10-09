# lexsync run log: en_lexdec

- Engine: R 4.6.1
- Started: 2026-10-09 07:50:33.740183
- Finished: 2026-10-09 07:50:36.604116

## Run metadata

- design: en_lexdec
- language: english
- paradigm: lexical_decision
- source: generate
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 07:50:33.744397**: loading lexicon 'corpora/derived/en.csv'
- **2026-10-09 07:50:34.302697**: lexicon loaded: 30000 words
    - words: 30000
- **2026-10-09 07:50:34.31474**: pool after filters: 8177 words
    - pool: 8177
- **2026-10-09 07:50:35.148248**: generated 120 items (words + pseudowords, letter_substitution)
    - conditions: word, pseudoword
- **2026-10-09 07:50:36.014213**: equivalence pseudoword vs word on 'length': d = 0.00 [-0.30, 0.30], TOST p = 0.004 (equivalent)
- **2026-10-09 07:50:36.018915**: equivalence pseudoword vs word on 'bigram_freq': d = -1.47 [-1.81, -1.13], TOST p = 1.000 (not shown equivalent)
- **2026-10-09 07:50:36.023458**: equivalence pseudoword vs word on 'n_density': d = -0.28 [-0.59, 0.02], TOST p = 0.117 (not shown equivalent)
- **2026-10-09 07:50:36.027517**: equivalence pseudoword vs word on 'old20': d = 0.17 [-0.13, 0.47], TOST p = 0.037 (equivalent)
- **2026-10-09 07:50:36.067238**: wrote 'en_lexdec_english_stimuli_R.csv'
    - path: output/stimuli/en_lexdec_english_stimuli_R.csv
    - rows: 120
    - md5: bc7c16452b7fd7cbabe8fafc8bb28287
- **2026-10-09 07:50:36.083601**: wrote 'en_lexdec_english_descriptives_R.csv'
    - path: output/reports/en_lexdec_english_descriptives_R.csv
    - rows: 8
    - md5: bee90fb07b347d3fe262803a6f342ade
- **2026-10-09 07:50:36.096764**: wrote 'en_lexdec_english_comparisons_R.csv'
    - path: output/reports/en_lexdec_english_comparisons_R.csv
    - rows: 4
    - md5: 9464b3452793472e9abce17609e3d369
- **2026-10-09 07:50:36.370126**: wrote 'en_lexdec_english_psychopy.py'
    - path: output/experiments/en_lexdec_english_psychopy.py
    - rows: NA
    - md5: a9c90173d7b34b6b6c1a914fa5132f57
- **2026-10-09 07:50:36.380238**: wrote 'en_lexdec_english.osexp'
    - path: output/experiments/en_lexdec_english.osexp
    - rows: NA
    - md5: 694c11f70ca325181628b5da1922e729
- **2026-10-09 07:50:36.388609**: wrote 'en_lexdec_english.html'
    - path: output/experiments/en_lexdec_english.html
    - rows: NA
    - md5: 3307ed89b9e2aaa71ac5dfcff505306d
- **2026-10-09 07:50:36.402933**: wrote 'en_lexdec_english_psychopy.csv'
    - path: output/experiments/en_lexdec_english_psychopy.csv
    - rows: NA
    - md5: 1fe32d4aaed880e77a845f82eb6df4a6
- **2026-10-09 07:50:36.410499**: wrote 'en_lexdec_english_opensesame.csv'
    - path: output/experiments/en_lexdec_english_opensesame.csv
    - rows: NA
    - md5: d0ffb15c8bb700fa775f65d16d8ae164
- **2026-10-09 07:50:36.416938**: wrote 'en_lexdec_english_opensesame_text.csv'
    - path: output/experiments/en_lexdec_english_opensesame_text.csv
    - rows: NA
    - md5: 706132481e716f2a1ada15a83b56c292
- **2026-10-09 07:50:36.586107**: wrote 'en_lexdec_english_datasheet_R.json'
    - path: output/reports/en_lexdec_english_datasheet_R.json
    - rows: NA
    - md5: 40bd565756fbfa22be29bdbd2bcc7b85
- **2026-10-09 07:50:36.596401**: wrote 'en_lexdec_english_datasheet_R.md'
    - path: output/reports/en_lexdec_english_datasheet_R.md
    - rows: NA
    - md5: 4461dab130664205c4bcdfab95714210
