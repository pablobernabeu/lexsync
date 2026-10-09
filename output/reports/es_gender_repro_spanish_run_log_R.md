# lexsync run log: es_gender_repro

- Engine: R 4.6.1
- Started: 2026-10-09 07:51:06.846641
- Finished: 2026-10-09 07:51:08.011761

## Run metadata

- design: es_gender_repro
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09 07:51:06.852196**: loading lexicon 'corpora/derived/es_gender.csv'
- **2026-10-09 07:51:07.146371**: lexicon loaded: 10185 words
    - words: 10185
- **2026-10-09 07:51:07.154662**: pool after filters: 9294 words
    - pool: 9294
- **2026-10-09 07:51:07.265132**: matched 96 items across 2 conditions
    - conditions: feminine, masculine
- **2026-10-09 07:51:07.394849**: equivalence masculine vs feminine on 'length': d = 0.00 [-0.34, 0.34], TOST p = 0.008 (equivalent)
- **2026-10-09 07:51:07.399943**: equivalence masculine vs feminine on 'frequency': d = 0.02 [-0.32, 0.36], TOST p = 0.010 (equivalent)
- **2026-10-09 07:51:07.40401**: equivalence masculine vs feminine on 'n_density': d = 0.20 [-0.14, 0.54], TOST p = 0.070 (not shown equivalent)
- **2026-10-09 07:51:07.407488**: equivalence masculine vs feminine on 'old20': d = -0.08 [-0.42, 0.26], TOST p = 0.022 (equivalent)
- **2026-10-09 07:51:07.41125**: equivalence masculine vs feminine on 'n_syllables': d = 0.10 [-0.24, 0.44], TOST p = 0.027 (equivalent)
- **2026-10-09 07:51:07.414782**: equivalence masculine vs feminine on 'bigram_freq': d = 0.22 [-0.12, 0.56], TOST p = 0.084 (not shown equivalent)
- **2026-10-09 07:51:07.447522**: wrote 'es_gender_repro_spanish_stimuli_R.csv'
    - path: output/stimuli/es_gender_repro_spanish_stimuli_R.csv
    - rows: 96
    - md5: b415e828f6a2dcff9ef0563c8cdc8cb0
- **2026-10-09 07:51:07.463403**: wrote 'es_gender_repro_spanish_descriptives_R.csv'
    - path: output/reports/es_gender_repro_spanish_descriptives_R.csv
    - rows: 12
    - md5: 3f492b562b890d6de54f8080a0d1e014
- **2026-10-09 07:51:07.476914**: wrote 'es_gender_repro_spanish_comparisons_R.csv'
    - path: output/reports/es_gender_repro_spanish_comparisons_R.csv
    - rows: 6
    - md5: 778b0d566053e6b6aa7c2a41b609451c
- **2026-10-09 07:51:07.717856**: wrote 'es_gender_repro_spanish_psychopy.py'
    - path: output/experiments/es_gender_repro_spanish_psychopy.py
    - rows: NA
    - md5: bbf6d33f78dd86bb674cd4a56c83b523
- **2026-10-09 07:51:07.737835**: wrote 'es_gender_repro_spanish.osexp'
    - path: output/experiments/es_gender_repro_spanish.osexp
    - rows: NA
    - md5: 27783330583f1bce440e91e202377908
- **2026-10-09 07:51:07.750969**: wrote 'es_gender_repro_spanish.html'
    - path: output/experiments/es_gender_repro_spanish.html
    - rows: NA
    - md5: 5b7525052e5edf0c002ed324b14703a3
- **2026-10-09 07:51:07.767462**: wrote 'es_gender_repro_spanish_psychopy.csv'
    - path: output/experiments/es_gender_repro_spanish_psychopy.csv
    - rows: NA
    - md5: cd45866303f43f56da2d18ffd8d1cab9
- **2026-10-09 07:51:07.778236**: wrote 'es_gender_repro_spanish_opensesame.csv'
    - path: output/experiments/es_gender_repro_spanish_opensesame.csv
    - rows: NA
    - md5: 84fe9dd521f4209376f827234a0b89d1
- **2026-10-09 07:51:07.789996**: wrote 'es_gender_repro_spanish_opensesame_text.csv'
    - path: output/experiments/es_gender_repro_spanish_opensesame_text.csv
    - rows: NA
    - md5: 0b036507adb99c2f18095ebcfb384c4b
- **2026-10-09 07:51:07.988547**: wrote 'es_gender_repro_spanish_datasheet_R.json'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.json
    - rows: NA
    - md5: c65ac133ae0c8fe510f57538faca1315
- **2026-10-09 07:51:08.000762**: wrote 'es_gender_repro_spanish_datasheet_R.md'
    - path: output/reports/es_gender_repro_spanish_datasheet_R.md
    - rows: NA
    - md5: 3520a70eca159a6259fbb03530608bba
