# lexsync run log: es_gender_repro

- Engine: R 4.6.1
- Started: 2026-10-14 01:25:29.099848
- Finished: 2026-10-14 01:25:30.454946

## Run metadata

- design: es_gender_repro
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-14 01:25:29.106289**: lexsync: the design gives no `instructions` and its language is 'spanish', so the experiments show lexsync's instructions in English; give `instructions` in the participants' language.
- **2026-10-14 01:25:29.111222**: lexsync: the design gives no `instructions`, and lexsync cannot tell what the response keys of a factorial design mean, so the experiments only name the keys; give `instructions` that say what each key means.
- **2026-10-14 01:25:29.117543**: loading lexicon 'corpora/derived/es_gender.csv'
- **2026-10-14 01:25:29.383455**: lexicon loaded: 10185 words
    - words: 10185
- **2026-10-14 01:25:29.396779**: pool after filters: 9294 words
    - pool: 9294
- **2026-10-14 01:25:29.486448**: matched 96 items across 2 conditions
    - conditions: feminine, masculine
- **2026-10-14 01:25:29.661661**: equivalence masculine vs feminine on 'length': d = 0.00 [-0.34, 0.34], TOST p = 0.008 (equivalent)
- **2026-10-14 01:25:29.754716**: equivalence masculine vs feminine on 'frequency': d = 0.02 [-0.32, 0.36], TOST p = 0.010 (equivalent)
- **2026-10-14 01:25:29.765807**: equivalence masculine vs feminine on 'n_density': d = 0.15 [-0.19, 0.49], TOST p = 0.043 (equivalent)
- **2026-10-14 01:25:29.77922**: equivalence masculine vs feminine on 'old20': d = -0.01 [-0.35, 0.32], TOST p = 0.010 (equivalent)
- **2026-10-14 01:25:29.785104**: equivalence masculine vs feminine on 'n_syllables': d = 0.13 [-0.21, 0.47], TOST p = 0.036 (equivalent)
- **2026-10-14 01:25:29.794001**: equivalence masculine vs feminine on 'bigram_freq': d = 0.23 [-0.10, 0.57], TOST p = 0.099 (not shown equivalent)
- **2026-10-14 01:25:29.829124**: wrote 'es_gender_repro_spanish_stimuli_R.csv'
    - path: output/stimuli/es_gender_repro_spanish_stimuli_R.csv
    - rows: 96
    - md5: fb913d59159b8ff0f28e2500e37293cc
- **2026-10-14 01:25:29.848879**: wrote 'es_gender_repro_spanish_descriptives_R.csv'
    - path: output/reports/es_gender_repro_spanish_descriptives_R.csv
    - rows: 12
    - md5: 6a7606491f66d8e7edc9d01c9c68d60c
- **2026-10-14 01:25:29.87001**: wrote 'es_gender_repro_spanish_comparisons_R.csv'
    - path: output/reports/es_gender_repro_spanish_comparisons_R.csv
    - rows: 6
    - md5: 616802681caa63a66084ad9584dbc44c
- **2026-10-14 01:25:30.126764**: wrote 'es_gender_repro_spanish_psychopy.py'
    - path: output/experiments/es_gender_repro_spanish_psychopy.py
    - rows: NA
    - md5: 454c7dc3109f1f696dff83e552a55563
- **2026-10-14 01:25:30.138957**: wrote 'es_gender_repro_spanish.osexp'
    - path: output/experiments/es_gender_repro_spanish.osexp
    - rows: NA
    - md5: 756d79875c16731491313da0524ce791
- **2026-10-14 01:25:30.150742**: wrote 'es_gender_repro_spanish.html'
    - path: output/experiments/es_gender_repro_spanish.html
    - rows: NA
    - md5: e6602532589f28e6cc159ae07a169b80
- **2026-10-14 01:25:30.166684**: wrote 'es_gender_repro_spanish_psychopy.csv'
    - path: output/experiments/es_gender_repro_spanish_psychopy.csv
    - rows: NA
    - md5: 0eb63319194528c0c179c3b153236aa8
- **2026-10-14 01:25:30.176355**: wrote 'es_gender_repro_spanish_opensesame.csv'
    - path: output/experiments/es_gender_repro_spanish_opensesame.csv
    - rows: NA
    - md5: 84fe9dd521f4209376f827234a0b89d1
- **2026-10-14 01:25:30.189327**: wrote 'es_gender_repro_spanish_opensesame_text.csv'
    - path: output/experiments/es_gender_repro_spanish_opensesame_text.csv
    - rows: NA
    - md5: 6e3f3663c8f25af2fba15f45cb5c3ccc
- **2026-10-14 01:25:30.425938**: wrote 'es_gender_repro_spanish_datasheet_R.json'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.json
    - rows: NA
    - md5: 8eea57f945f9e4427db2bf032500f8cf
- **2026-10-14 01:25:30.441813**: wrote 'es_gender_repro_spanish_datasheet_R.md'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.md
    - rows: NA
    - md5: d88b234afee65401295bde269d91e4ed
