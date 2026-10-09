# lexsync run log: es_gender_repro

- Engine: Python 3.13.7
- Started: 2026-10-09T07:51:45
- Finished: 2026-10-09T07:51:46

## Run metadata

- design: es_gender_repro
- language: spanish
- paradigm: factorial
- source: corpus
- seed: 2026
- mode: conditions
- schema_path: config/schema.yaml

## Steps

- **2026-10-09T07:51:45**: loading lexicon 'corpora/derived/es_gender.csv'
- **2026-10-09T07:51:45**: lexicon loaded: 10185 words
    - words: 10185
- **2026-10-09T07:51:45**: pool after filters: 9294 words
    - pool: 9294
- **2026-10-09T07:51:45**: matched 96 items across 2 conditions
    - conditions: feminine, masculine
- **2026-10-09T07:51:45**: equivalence masculine vs feminine on 'length': d = 0.00 [-0.34, 0.34], TOST p = 0.0081 (equivalent)
- **2026-10-09T07:51:45**: equivalence masculine vs feminine on 'frequency': d = 0.02 [-0.32, 0.36], TOST p = 0.0105 (equivalent)
- **2026-10-09T07:51:45**: equivalence masculine vs feminine on 'n_density': d = 0.20 [-0.14, 0.54], TOST p = 0.0697 (not shown equivalent)
- **2026-10-09T07:51:45**: equivalence masculine vs feminine on 'old20': d = -0.08 [-0.42, 0.26], TOST p = 0.0218 (equivalent)
- **2026-10-09T07:51:45**: equivalence masculine vs feminine on 'n_syllables': d = 0.10 [-0.24, 0.44], TOST p = 0.0271 (equivalent)
- **2026-10-09T07:51:45**: equivalence masculine vs feminine on 'bigram_freq': d = 0.22 [-0.12, 0.56], TOST p = 0.0838 (not shown equivalent)
- **2026-10-09T07:51:45**: wrote 'es_gender_repro_spanish_stimuli_py.csv'
    - path: output\stimuli\es_gender_repro_spanish_stimuli_py.csv
    - rows: 96
    - md5: b415e828f6a2dcff9ef0563c8cdc8cb0
- **2026-10-09T07:51:45**: wrote 'es_gender_repro_spanish_descriptives_py.csv'
    - path: output\reports\es_gender_repro_spanish_descriptives_py.csv
    - rows: 12
    - md5: 3f492b562b890d6de54f8080a0d1e014
- **2026-10-09T07:51:45**: wrote 'es_gender_repro_spanish_comparisons_py.csv'
    - path: output\reports\es_gender_repro_spanish_comparisons_py.csv
    - rows: 6
    - md5: 778b0d566053e6b6aa7c2a41b609451c
- **2026-10-09T07:51:45**: wrote 'es_gender_repro_spanish_psychopy.py'
    - path: output\experiments\es_gender_repro_spanish_psychopy.py
    - rows: None
    - md5: bbf6d33f78dd86bb674cd4a56c83b523
- **2026-10-09T07:51:45**: wrote 'es_gender_repro_spanish.osexp'
    - path: output\experiments\es_gender_repro_spanish.osexp
    - rows: None
    - md5: 27783330583f1bce440e91e202377908
- **2026-10-09T07:51:45**: wrote 'es_gender_repro_spanish.html'
    - path: output\experiments\es_gender_repro_spanish.html
    - rows: None
    - md5: 5b7525052e5edf0c002ed324b14703a3
- **2026-10-09T07:51:45**: wrote 'es_gender_repro_spanish_psychopy.csv'
    - path: output\experiments\es_gender_repro_spanish_psychopy.csv
    - rows: None
    - md5: cd45866303f43f56da2d18ffd8d1cab9
- **2026-10-09T07:51:45**: wrote 'es_gender_repro_spanish_opensesame.csv'
    - path: output\experiments\es_gender_repro_spanish_opensesame.csv
    - rows: None
    - md5: 84fe9dd521f4209376f827234a0b89d1
- **2026-10-09T07:51:45**: wrote 'es_gender_repro_spanish_opensesame_text.csv'
    - path: output\experiments\es_gender_repro_spanish_opensesame_text.csv
    - rows: None
    - md5: 0b036507adb99c2f18095ebcfb384c4b
- **2026-10-09T07:51:45**: wrote 'es_gender_repro_spanish_datasheet_py.json'
    - path: output\reports\es_gender_repro_spanish_datasheet_py.json
    - rows: None
    - md5: f3f1d6cd1a77cb0575d8ffb47c8c13e5
- **2026-10-09T07:51:46**: wrote 'es_gender_repro_spanish_datasheet_py.md'
    - path: output\reports\es_gender_repro_spanish_datasheet_py.md
    - rows: None
    - md5: 391ec8633945aa285c0c013cd927cb65
