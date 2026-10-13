# lexsync run log: es_gender_repro

- Engine: R 4.6.1
- Started: 2026-10-13 11:12:22.847779
- Finished: 2026-10-13 11:12:29.630783

## Run metadata

- design: es_gender_repro
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-13 11:12:22.875215**: loading lexicon 'corpora/derived/es_gender.csv'
- **2026-10-13 11:12:23.748894**: lexicon loaded: 10185 words
    - words: 10185
- **2026-10-13 11:12:23.778394**: pool after filters: 9294 words
    - pool: 9294
- **2026-10-13 11:12:24.161756**: matched 96 items across 2 conditions
    - conditions: feminine, masculine
- **2026-10-13 11:12:24.561827**: equivalence masculine vs feminine on 'length': d = 0.00 [-0.34, 0.34], TOST p = 0.008 (equivalent)
- **2026-10-13 11:12:24.580615**: equivalence masculine vs feminine on 'frequency': d = 0.02 [-0.32, 0.36], TOST p = 0.010 (equivalent)
- **2026-10-13 11:12:24.615693**: equivalence masculine vs feminine on 'n_density': d = 0.15 [-0.19, 0.49], TOST p = 0.043 (equivalent)
- **2026-10-13 11:12:24.64694**: equivalence masculine vs feminine on 'old20': d = -0.01 [-0.35, 0.32], TOST p = 0.010 (equivalent)
- **2026-10-13 11:12:24.666023**: equivalence masculine vs feminine on 'n_syllables': d = 0.13 [-0.21, 0.47], TOST p = 0.036 (equivalent)
- **2026-10-13 11:12:24.682349**: equivalence masculine vs feminine on 'bigram_freq': d = 0.23 [-0.10, 0.57], TOST p = 0.099 (not shown equivalent)
- **2026-10-13 11:12:24.91818**: wrote 'es_gender_repro_spanish_stimuli_R.csv'
    - path: output/stimuli/es_gender_repro_spanish_stimuli_R.csv
    - rows: 96
    - md5: fb913d59159b8ff0f28e2500e37293cc
- **2026-10-13 11:12:25.015299**: wrote 'es_gender_repro_spanish_descriptives_R.csv'
    - path: output/reports/es_gender_repro_spanish_descriptives_R.csv
    - rows: 12
    - md5: 6a7606491f66d8e7edc9d01c9c68d60c
- **2026-10-13 11:12:25.075696**: wrote 'es_gender_repro_spanish_comparisons_R.csv'
    - path: output/reports/es_gender_repro_spanish_comparisons_R.csv
    - rows: 6
    - md5: 616802681caa63a66084ad9584dbc44c
- **2026-10-13 11:12:27.519177**: wrote 'es_gender_repro_spanish_psychopy.py'
    - path: output/experiments/es_gender_repro_spanish_psychopy.py
    - rows: NA
    - md5: bbf6d33f78dd86bb674cd4a56c83b523
- **2026-10-13 11:12:27.596796**: wrote 'es_gender_repro_spanish.osexp'
    - path: output/experiments/es_gender_repro_spanish.osexp
    - rows: NA
    - md5: 27783330583f1bce440e91e202377908
- **2026-10-13 11:12:27.681427**: wrote 'es_gender_repro_spanish.html'
    - path: output/experiments/es_gender_repro_spanish.html
    - rows: NA
    - md5: 7b35e208c9e557473e78e2b41ce73c30
- **2026-10-13 11:12:27.759587**: wrote 'es_gender_repro_spanish_psychopy.csv'
    - path: output/experiments/es_gender_repro_spanish_psychopy.csv
    - rows: NA
    - md5: 0eb63319194528c0c179c3b153236aa8
- **2026-10-13 11:12:27.841111**: wrote 'es_gender_repro_spanish_opensesame.csv'
    - path: output/experiments/es_gender_repro_spanish_opensesame.csv
    - rows: NA
    - md5: 84fe9dd521f4209376f827234a0b89d1
- **2026-10-13 11:12:27.906691**: wrote 'es_gender_repro_spanish_opensesame_text.csv'
    - path: output/experiments/es_gender_repro_spanish_opensesame_text.csv
    - rows: NA
    - md5: 6e3f3663c8f25af2fba15f45cb5c3ccc
- **2026-10-13 11:12:29.512321**: wrote 'es_gender_repro_spanish_datasheet_R.json'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.json
    - rows: NA
    - md5: 5a4e9858c5c672c9795ba87d64eed56a
- **2026-10-13 11:12:29.579684**: wrote 'es_gender_repro_spanish_datasheet_R.md'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.md
    - rows: NA
    - md5: d88b234afee65401295bde269d91e4ed
